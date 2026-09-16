"""Bring a prepared magazine scan set onto the site.

A prepared set (E:/Pokeamice/scan/<name>_prepared) is one issue: web/ holds
one 2048px JPEG per selected page, archive/ the 300 dpi masters, and a
scan-manifest.json that names the pages. The transcriptions that came with
the sets are not used - checked against the page images, some of them were
written rather than read (DREAM 2011.1 P18-P23 is a different interview
from the one on the page) - so every page is transcribed again from the
image by a vision model, and that text is what gets translated.

    python tools/import-scan-set.py ocr   <slug>|all [--workers 4]
    python tools/import-scan-set.py pages <slug>            # headings per page, to draw the feature boundaries
    python tools/import-scan-set.py build <slug> [--dry-run] [--only <feature>]

The registry is design/scan_sets_2026-09.json: per set the bibliography,
the page list, and `features` - the articles that become posts, each a
page range with a title, a kind and its people. The page transcriptions are
cached in data/cache_scan/<slug>/<page>.txt and are the raw record.

Post shape follows the CONTINUE scans (archive_type scan_translation,
translation_segments with scan_page / region_type / speaker), so the
interview-editorial layout renders them page by page with the READ /
ARCHIVE views of interview-body-scan.html.
"""
import argparse
import base64
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "design" / "scan_sets_2026-09.json"
CACHE = ROOT / "data" / "cache_scan"
ASSETS = ROOT / "assets" / "images" / "scan-archive"
POSTS = ROOT / "_posts"

# the web importer already knows DeepSeek, the glossary and the house prompt
_spec = importlib.util.spec_from_file_location("import_web", ROOT / "tools" / "import-web.py")
_web = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_web)
deepseek, load_glossary, glossary_hits, SYSTEM = _web.deepseek, _web.load_glossary, _web.glossary_hits, _web.SYSTEM


def registry():
    return json.load(io.open(REGISTRY, encoding="utf-8"))


def save_registry(reg):
    json.dump(reg, io.open(REGISTRY, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def find_set(reg, slug):
    for s in reg["sets"]:
        if s["slug"] == slug:
            return s
    raise SystemExit(f"no set {slug!r} in {REGISTRY.name}")


def page_image(s, page, master=False):
    base = Path(registry_root(s)) / s["dir"]
    if master:
        # the 300 dpi master; its name is the web name with, in some sets, a suffix (dengeki: _master).
        # A set whose archive/ came out small (DREAM 2011.5: 1112x1529) names a master_dir rebuilt from the raw scans.
        for sub in ([s["master_dir"]] if s.get("master_dir") else []) + ["archive"]:
            hits = sorted((base / sub).glob(page["file"] + "*.jpg"))
            if hits:
                return hits[0]
    return base / "web" / (page["file"] + ".jpg")


def registry_root(s):
    return reg_root


reg_root = None


# ---------------------------------------------------------------- ocr
VLM_URL = (os.environ.get("VLM_OCR_API_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1").rstrip("/") + "/chat/completions"
VLM_KEY = os.environ.get("VLM_OCR_API_KEY") or os.environ.get("DASHSCOPE_API_KEY") or ""
VLM_MODEL = "qwen3.8-max"

# Tested on the 電撃GAMES Vol.14 P.252 and P.254 pages against a
# transcription known to be faithful, and on the dense DREAM 2011.1 P.22
# page against the page itself. qwen3.8-max reads them; qwen3.7-plus drops
# words; qwen3.5-ocr scrambles the columns; qwen-vl-ocr returns boxes. At
# the default ~2500 image tokens the dense P.254 still lost names (ラッコ
# became シカ, a question folded into the answer before it); with
# vl_high_resolution_images on the 300 dpi master (~6700 tokens) it is
# verbatim. So: master + high resolution, about 50 s a page.
OCR_PROMPT = (
    "これは日本の雑誌のスキャンページです。ページ上のすべての日本語の文字を、誌面の読み順（縦書きは右の列から左の列へ、各列は上から下へ；横書きは上から下へ）で、一字一句そのまま書き起こしてください。\n"
    "・ルビ（振り仮名）は書かず、本文の漢字だけを書く。\n"
    "・『』「」などの括弧、数字の全角／半角、記号は誌面のとおりにする。\n"
    "・見出し・キャッチコピー・小見出し・本文・写真キャプション・囲み記事・表を、それぞれ空行で区切ったブロックとして出力し、ブロックの先頭行に [見出し] [小見出し] [本文] [キャプション] [囲み] [表] のいずれかを付ける。\n"
    "・インタビューの質問（――で始まる文）と発言者名（例：増田、景山、杉森）は誌面のとおり残す。\n"
    "・ページに無い言葉を補わない、要約しない、言い換えない。読めない文字は〓にする。\n"
    "・ページ番号・柱（雑誌名や号数の小さな表記）は最後に [柱] ブロックとして書く。"
)


def vlm_transcribe(image_path, model=VLM_MODEL, max_tokens=12000):
    data = "data:image/jpeg;base64," + base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
    body = {
        "model": model,
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": data}},
            {"type": "text", "text": OCR_PROMPT},
        ]}],
        "max_tokens": max_tokens,
        "temperature": 0,
        "enable_thinking": False,
        "vl_high_resolution_images": True,
    }
    req = urllib.request.Request(VLM_URL, data=json.dumps(body).encode("utf-8"),
                                 headers={"Authorization": "Bearer " + VLM_KEY, "Content-Type": "application/json"})
    last = None
    for attempt in range(4):
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=900) as r:
                d = json.load(r)
            text = d["choices"][0]["message"]["content"]
            usage = d.get("usage", {})
            return text, {"model": model, "seconds": round(time.time() - t0, 1),
                          "image_tokens": (usage.get("prompt_tokens_details") or {}).get("image_tokens"),
                          "completion_tokens": usage.get("completion_tokens"),
                          "finish": d["choices"][0].get("finish_reason")}
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            last = exc
            body_text = ""
            if isinstance(exc, urllib.error.HTTPError):
                try:
                    body_text = exc.read().decode("utf-8", "replace")[:300]
                except Exception:
                    pass
            print(f"    vlm error (attempt {attempt + 1}): {exc} {body_text}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"vlm failed for {image_path}: {last}")


def ocr_set(s, workers):
    out_dir = CACHE / s["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    wanted = s.get("ocr_pages")  # a set may name the pages worth reading (a guidebook's pokedex is not)
    todo = []
    for p in s["pages"]:
        if wanted and p["file"] not in wanted:
            continue
        txt = out_dir / (p["file"] + ".txt")
        if txt.exists() and txt.stat().st_size > 50:
            continue
        todo.append(p)
    print(f"{s['slug']}: {len(todo)} pages to transcribe ({len(s['pages'])} in set)", flush=True)

    def one(p):
        img = page_image(s, p, master=True)
        text, meta = vlm_transcribe(img)
        meta["file"] = p["file"]
        meta["image_md5"] = hashlib.md5(img.read_bytes()).hexdigest()
        (out_dir / (p["file"] + ".txt")).write_text(text, encoding="utf-8")
        (out_dir / (p["file"] + ".meta.json")).write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        return p["file"], meta

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, p): p for p in todo}
        for f in as_completed(futs):
            p = futs[f]
            try:
                name, meta = f.result()
                print(f"  ok {s['slug']}/{name}  {meta['seconds']}s  out {meta['completion_tokens']}  {meta['finish']}", flush=True)
            except Exception as exc:
                print(f"  FAIL {s['slug']}/{p['file']}: {exc}", file=sys.stderr, flush=True)


# ---------------------------------------------------------------- parse the transcription
BLOCK_TAGS = {"見出し": "heading", "小見出し": "subheading", "本文": "body", "キャプション": "caption",
              "囲み": "note", "表": "table", "柱": "folio"}
# a question opens with the dash of a magazine interview, or the Q of a guidebook's Q&A
Q_RE = re.compile(r"^(?:――|——|―|—|──|--|[QＱ][ 　：:.．])\s*(.+)$")


def question_re(feature):
    """A feature may declare the mark its magazine used for questions (the 1996
    guidebook: ●); it is only honoured there, since ● is a bullet elsewhere."""
    mark = feature.get("question_mark") if feature else None
    if not mark:
        return Q_RE
    return re.compile(r"^(?:――|——|―|—|──|--|[QＱ][ 　：:.．]|" + re.escape(mark) + r")\s*(.+)$")
# 「増田 本文」 / 「増田：本文」 / 「増田順一氏（以下、敬称略） 本文」
SPEAKER_RE = re.compile(r"^([\u4e00-\u9fff\u30a0-\u30ff\u3040-\u309fA-Za-z・]{1,8}(?:氏)?(?:（[^）]{0,20}）)?)[ 　：:]\s*(.+)$")


def parse_page(text):
    """Blocks of one page: [{kind, lines}] in page order."""
    blocks = []
    cur = None
    for raw in text.splitlines():
        line = raw.rstrip()
        m = re.match(r"^\s*\[(見出し|小見出し|本文|キャプション|囲み|表|柱)\]\s*(.*)$", line)
        if m:
            cur = {"kind": BLOCK_TAGS[m.group(1)], "lines": []}
            blocks.append(cur)
            if m.group(2).strip():
                cur["lines"].append(m.group(2).strip())
            continue
        if not line.strip():
            if cur and cur["lines"]:
                cur["lines"].append("")
            continue
        if cur is None:
            cur = {"kind": "body", "lines": []}
            blocks.append(cur)
        cur["lines"].append(line.strip())
    for b in blocks:
        while b["lines"] and not b["lines"][-1]:
            b["lines"].pop()
    return [b for b in blocks if b["lines"]]


def block_paragraphs(block, q_re=Q_RE):
    """A body block is turns and paragraphs; the model separates them with blank lines,
    and a question or a speaker name also starts a new one."""
    paras = []
    cur = []
    for line in block["lines"]:
        starts = (not line) or q_re.match(line) or SPEAKER_RE.match(line)
        if starts and cur:
            paras.append(" ".join(cur) if all(re.search(r"[A-Za-z]$", x) for x in cur) else "".join(cur))
            cur = []
        if line:
            cur.append(line)
    if cur:
        paras.append("".join(cur))
    return [p for p in paras if p.strip()]


def split_runaway_headings(blocks, q_re=Q_RE):
    """The model sometimes keeps writing an interview under a [小見出し] tag: the block then
    holds questions and named turns. Its first line stays the heading; the rest is body."""
    out = []
    for b in blocks:
        lines = b["lines"]
        turn = lambda l: q_re.match(l) or re.match(r"^[一-鿿]{2,4}[ 　：:]", l)
        if b["kind"] in ("heading", "subheading") and len(lines) > 1 and any(turn(l) for l in lines[1:]):
            cut = next(i for i, l in enumerate(lines) if i >= 1 and turn(l))
            out.append({"kind": b["kind"], "lines": lines[:cut]})
            out.append({"kind": "body", "lines": lines[cut:]})
        elif b["kind"] in ("heading", "subheading") and len("".join(lines)) > 120:
            out.append({"kind": "body", "lines": lines})   # a paragraph tagged as a heading
        else:
            out.append(b)
    return out


def to_segments(s, feature, cache_dir, speakers):
    """translation_segments for a feature: per page a plate, then its blocks."""
    segs = []
    order = 0
    # the label printed in the magazine (増田) -> the name the site uses (增田顺一)
    smap = feature.get("speaker_map") or {}
    q_re = question_re(feature)
    names = {n for n in speakers} | set(smap)
    supp = feature.get("supplement") or []
    for idx, page in enumerate(feature_pages(s, feature)):
        order += 1
        if supp and page["file"] == supp[0]:
            # the divider before the pages that are not the interview
            segs.append({"speaker": "附录：同期攻略与资料页", "type": "heading", "kind": "text", "region_type": "heading",
                         "region_id": f"{page['file']}-supplement", "order": order, "scan_page": idx, "heading_level": 2,
                         "review_status": "ready", "original": "", "translation": "",
                         "comment": "以下各页是与访谈同期刊出的攻略、数据页，作为补充收录，不是访谈本体。"})
            order += 1
        segs.append({"speaker": "image", "type": "image", "kind": "image", "region_type": "image",
                     "region_id": f"{page['file']}-fullpage", "order": order, "scan_page": idx,
                     "image": f"{image_base(s)}/{feature['slug']}/pages/{page['file']}.jpg",
                     "alt": f"{s['publication']} {s['issue']} P.{page['page']}" if page.get("page") else s["publication"],
                     "review_status": "ready"})
        if page["file"] in (feature.get("plate_only") or []):
            continue  # a cover or a contents page: the picture is the record, its text is another article's
        txt_path = cache_dir / (page["file"] + ".txt")
        if not txt_path.exists():
            print(f"  ! no transcription for {page['file']}", file=sys.stderr)
            continue
        for b in split_runaway_headings(parse_page(txt_path.read_text(encoding="utf-8")), q_re):
            if b["kind"] == "folio":
                continue
            if b["kind"] in ("heading", "subheading"):
                order += 1
                segs.append({"speaker": "".join(b["lines"]), "type": "heading", "kind": "text", "region_type": "heading",
                             "region_id": f"{page['file']}-h{order}", "order": order, "scan_page": idx,
                             "heading_level": 2 if b["kind"] == "heading" else 3,
                             "review_status": "ready", "original": "", "translation": ""})
                continue
            if b["kind"] == "table":
                order += 1
                segs.append({"speaker": "note", "type": "paragraph", "kind": "text", "region_type": "note",
                             "region_id": f"{page['file']}-t{order}", "order": order, "scan_page": idx,
                             "review_status": "ready", "original": "\n".join(b["lines"]), "translation": ""})
                continue
            kind = {"caption": "caption", "note": "note"}.get(b["kind"], "body")
            for para in block_paragraphs(b, q_re):
                order += 1
                seg = {"speaker": kind, "type": "paragraph", "kind": "text", "region_type": kind,
                       "region_id": f"{page['file']}-r{order}", "order": order, "scan_page": idx,
                       "review_status": "ready", "original": para, "translation": ""}
                q = q_re.match(para)
                if q and kind == "body":
                    seg["speaker"] = "──"
                    seg["original"] = q.group(1).strip()
                else:
                    sp = SPEAKER_RE.match(para)
                    if sp and kind == "body":
                        name = re.sub(r"氏$", "", re.sub(r"（.*?）", "", sp.group(1)).strip())
                        known = name in names or name[:2] in names
                        if known or (len(name) <= 4 and name not in ("全員",) and re.match(r"^[\u4e00-\u9fff]{1,4}$", name)):
                            # 増田順一氏 on first mention, 増田 after; the map may know either
                            seg["speaker"] = smap.get(name) or smap.get(name[:2]) or name
                            seg["original"] = sp.group(2).strip()
                            if not known:
                                seg["_guess"] = (name, para)   # a name nobody declared: kept only if it recurs
                        elif name == "全員":
                            seg["speaker"] = smap.get("全員", "全員")
                            seg["original"] = sp.group(2).strip()
                segs.append(seg)
    # a label seen once that no one declared is a book title or a shop, not a person
    seen = {}
    for x in segs:
        if "_guess" in x:
            seen[x["_guess"][0]] = seen.get(x["_guess"][0], 0) + 1
    for x in segs:
        if "_guess" in x:
            name, para = x.pop("_guess")
            if seen[name] < 2:
                x["speaker"], x["original"] = "body", para
    return segs


def feature_pages(s, feature):
    """The feature's pages in set order, then its supplement - the walkthrough or data
    pages that ran beside the interview and are kept after it, not in it."""
    files = set(feature.get("files") or [])
    supp = set(feature.get("supplement") or [])
    lo, hi = feature.get("pages", [None, None]) if not files else (None, None)
    out = []
    for p in s["pages"]:
        if files:
            if p["file"] in files and p["file"] not in supp:
                out.append(p)
        elif p.get("page") is not None and lo is not None and lo <= p["page"] <= hi and p["file"] not in supp:
            out.append(p)
    out += [p for p in s["pages"] if p["file"] in supp]
    return out


# ---------------------------------------------------------------- translate
def translate_segments(segs, s, feature, glossary):
    text = [(i, x) for i, x in enumerate(segs) if x.get("type") != "image" and (x.get("original") or x.get("type") == "heading")]
    for i, x in text:
        if x.get("type") == "heading":
            x["original"] = x["speaker"]
    full = "\n".join(x["original"] for _, x in text)
    hits = glossary_hits(full, glossary)
    gloss = "\n".join(f"- {a} → {b}" for a, b in hits) or "（无）"
    system = SYSTEM.format(lang="日语") + f"\n术语表：\n{gloss}"
    def run(items, chunk):
        for start in range(0, len(items), chunk):
            part = items[start:start + chunk]
            payload = [{"i": i, "speaker": ("" if x.get("speaker") in ("body", "note", "caption") else x.get("speaker", "")),
                        "kind": x.get("region_type"), "text": x["original"]} for i, x in part]
            prompt = (f"这是{s['publication_zh']} {s['issue']} 的杂志扫描页转写《{feature['title_ja']}》的一段（日语，OCR 转写，可能有个别错字）。"
                      f"逐条把 text 译成简体中文，保留条目顺序与编号 i，每一条都要有译文；kind=heading 的是标题行，照译成简短标题；kind=caption 是图说；kind=table 的按行、按「|」分隔原样保持结构；说话人不用译，译文开头不要加破折号。"
                      f"OCR 明显错字按上下文改正后再译，不要在译文里标注。"
                      f"note 只在读者很可能不知道的具体事实上给一句，一般留空字符串。\n\n"
                      f"输出格式：{{\"items\":[{{\"i\":编号,\"translation\":\"译文\",\"note\":\"\"}}]}}\n\n"
                      f"待译：\n{json.dumps(payload, ensure_ascii=False)}")
            print(f"  translating {start + 1}-{start + len(part)} / {len(items)} ...", flush=True)
            got = None
            for attempt in range(3):
                raw = deepseek([{"role": "system", "content": system}, {"role": "user", "content": prompt}])
                try:
                    got = {int(r["i"]): r for r in json.loads(raw).get("items", []) if "i" in r}
                    break
                except (ValueError, TypeError) as exc:
                    print(f"    bad JSON from the model (attempt {attempt + 1}): {exc}", file=sys.stderr)
            if got is None:
                raise RuntimeError("translation chunk failed three times")
            for i, x in part:
                r = got.get(i)
                x["translation"] = re.sub(r"^[─—－-]{1,2}\s*", "", str((r or {}).get("translation", "")).strip())
                note = str((r or {}).get("note", "") or "").strip()
                if note:
                    x["comment"] = note
            time.sleep(1)

    run(text, 12)
    # the model now and then drops an item from a chunk; those go back in smaller chunks
    for _ in range(2):
        missing = [(i, x) for i, x in text if not x["translation"]]
        if not missing:
            break
        print(f"  {len(missing)} items came back empty, retrying", flush=True)
        run(missing, 4)
    # a heading is shown by its translation (the CONTINUE convention: speaker
    # holds the title); the printed Japanese stays in original, under it
    for _, x in text:
        if x.get("type") == "heading" and x.get("translation"):
            x["speaker"] = x["translation"]
            x["translation"] = ""
    return segs


def cover(segs, s, feature):
    sample = "\n".join(f"{x.get('speaker', '')}: {x.get('translation', '')}" for x in segs if x.get("type") != "image")[:6000]
    year = s["date"][:4]
    prompt = (f"下面是{s['publication_zh']} {s['issue']}（{year} 年）杂志文章《{feature['title_ja']}》的中文译文节选。"
              f"给出：title（中文标题，形如「{s['publication']} {year}：……」，45字以内，写清受访者/主题，不用感叹号）、"
              f"display_title（封面用的一句短标题，20字以内）、dek（一句导语，60字以内）、summary（120字以内的内容提要，平实）。"
              f"输出 JSON：{{\"title\":\"\",\"display_title\":\"\",\"dek\":\"\",\"summary\":\"\"}}\n\n{sample}")
    raw = deepseek([{"role": "system", "content": SYSTEM.format(lang="日语")}, {"role": "user", "content": prompt}], max_tokens=800)
    return json.loads(raw)


# ---------------------------------------------------------------- write
def yaml_str(v):
    v = str(v)
    if v == "" or re.search(r"[:#\[\]{}&*!|>'\"%@`,\n]|^\s|\s$|^[-?]", v) or v.lower() in ("true", "false", "null", "yes", "no") or re.match(r"^[\d.]+$", v):
        return json.dumps(v, ensure_ascii=False)
    return v


def dump_yaml(obj, indent=0):
    pad = "  " * indent
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                out.append(f"{pad}{k}:")
                out.append(dump_yaml(v, indent + 1))
            elif isinstance(v, (dict, list)):
                out.append(f"{pad}{k}: {'{}' if isinstance(v, dict) else '[]'}")
            elif isinstance(v, bool):
                out.append(f"{pad}{k}: {'true' if v else 'false'}")
            elif v is None:
                out.append(f"{pad}{k}: null")
            elif isinstance(v, (int, float)):
                out.append(f"{pad}{k}: {v}")
            else:
                out.append(f"{pad}{k}: {yaml_str(v)}")
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, dict):
                inner = dump_yaml(v, indent + 1).split("\n")
                first = inner[0].lstrip()
                out.append(f"{pad}- {first}")
                out.extend(inner[1:])
            elif isinstance(v, list):
                out.append(f"{pad}- ")
                out.append(dump_yaml(v, indent + 1))
            elif isinstance(v, (int, float)) and not isinstance(v, bool):
                out.append(f"{pad}- {v}")
            else:
                out.append(f"{pad}- {yaml_str(v)}")
    return "\n".join(out)


# ---------------------------------------------------------------- plates
# The page images do not go into the repository: 204 pages are 147 MB, and
# git would carry them forever while every Pages deploy re-uploads them. They
# live in the Tencent COS bucket the app already serves its sprites from
# (gallery.pokeamice.com; see data-center/scripts/upload-cdn-assets.mjs),
# under scan-archive/<feature>/pages/, and the posts point at the CDN URL.
# The bucket credentials come from event/.env and are never printed.
COS_ENV = ROOT.parent.parent / "pokeamice" / "event" / ".env"


def image_base(s):
    return s.get("image_base") or registry().get("image_base") or "/assets/images/scan-archive"


def cos_client():
    from qcloud_cos import CosConfig, CosS3Client
    conf = {}
    for line in COS_ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            conf[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("TENCENT_COS_SECRET_ID", "TENCENT_COS_SECRET_KEY", "TENCENT_COS_BUCKET", "TENCENT_COS_REGION"):
        if not conf.get(k):
            raise SystemExit(f"{COS_ENV} lacks {k}")
    client = CosS3Client(CosConfig(Region=conf["TENCENT_COS_REGION"], SecretId=conf["TENCENT_COS_SECRET_ID"], SecretKey=conf["TENCENT_COS_SECRET_KEY"]))
    return client, conf["TENCENT_COS_BUCKET"]


def upload_set(s, workers=6):
    """Every feature's plates to the bucket; a key that is already there with the same size is skipped."""
    client, bucket = cos_client()
    base = image_base(s)
    prefix = base.split("//", 1)[-1].split("/", 1)[1] if base.startswith("http") else "scan-archive"
    jobs = []
    for feature in s["features"]:
        if feature.get("skip"):
            continue
        for p in feature_pages(s, feature):
            jobs.append((f"{prefix}/{feature['slug']}/pages/{p['file']}.jpg", page_image(s, p)))
    print(f"{s['slug']}: {len(jobs)} plates -> {bucket}/{prefix}/", flush=True)

    def one(key, src):
        size = src.stat().st_size
        try:
            head = client.head_object(Bucket=bucket, Key=key)
            if int(head.get("Content-Length", -1)) == size:
                return key, "kept"
        except Exception:
            pass
        client.put_object(Bucket=bucket, Key=key, Body=src.read_bytes(), ContentType="image/jpeg",
                          CacheControl="public, max-age=31536000, immutable")
        return key, f"up {size // 1024} KB"

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(one, k, src) for k, src in jobs]
        for f in as_completed(futs):
            key, what = f.result()
            print(f"  {what:>12}  {key}", flush=True)


def copy_pages(s, feature, dry):
    """Only when the registry has no CDN base: the CONTINUE-style copy into assets/."""
    if dry or image_base(s).startswith("http"):
        return
    dest = ASSETS / feature["slug"] / "pages"
    dest.mkdir(parents=True, exist_ok=True)
    for p in feature_pages(s, feature):
        src = page_image(s, p)
        dst = dest / (p["file"] + ".jpg")
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copyfile(src, dst)


def tabulate(segs):
    """A [表] block the model wrote as `a | b | c` rows becomes a table: rows_ja / rows_zh
    for the reader, original / translation kept for the record. A block whose rows do not
    line up after translation stays prose."""
    for x in segs:
        if not re.search(r"-t\d+$", str(x.get("region_id", ""))):
            continue
        ja = [l for l in (x.get("original") or "").splitlines() if "|" in l]
        zh = [l for l in (x.get("translation") or "").splitlines() if "|" in l]
        if len(ja) < 2 or len(ja) != len(zh):
            continue
        rows_ja = [[c.strip() for c in l.strip().strip("|").split("|")] for l in ja]
        rows_zh = [[c.strip() for c in l.strip().strip("|").split("|")] for l in zh]
        width = max(len(r) for r in rows_ja)
        if any(len(r) != len(q) for r, q in zip(rows_ja, rows_zh)):
            continue
        x["type"] = "table"
        x["region_type"] = "table"
        x["rows_ja"] = [r + [""] * (width - len(r)) for r in rows_ja]
        x["rows_zh"] = [r + [""] * (width - len(r)) for r in rows_zh]
        lead = [l for l in (x.get("translation") or "").splitlines() if "|" not in l and l.strip()]
        if lead:
            x["table_caption"] = lead[0].strip()
    return segs


def front_matter(text):
    """The YAML between the --- fences."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    return m.group(1)


def post_text(fm):
    return "---" + chr(10) + dump_yaml(fm) + chr(10) + "---" + chr(10)


def write_post(s, feature, segs, cov):
    year = s["date"][:4]
    pages = feature_pages(s, feature)
    plates = set(feature.get("plate_only") or [])
    nums = [p["page"] for p in pages if p.get("page") and p["file"] not in plates]
    span = f"P.{nums[0]}–P.{nums[-1]}" if nums else ""
    people = feature.get("people") or []
    is_interview = feature.get("kind", "interview") in ("interview", "roundtable")
    fm = {
        "archive_type": "scan_translation",
        "layout": "interview-editorial",
        "title": cov.get("title") or f"{s['publication']} {year}：{feature['title_ja']}",
        "display_title": cov.get("display_title", ""),
        "title_ja": feature["title_ja"],
        "date": s["date"],
        "era_skin": int(year),
        "categories": ["访谈翻译", "扫描存档"] if is_interview else ["杂志特辑", "扫描存档"],
        "tags": list(dict.fromkeys([s["publication"], "扫描存档", "日中对照"] + (feature.get("tags") or []))),
        "kicker": "SCAN ARCHIVE · " + ("INTERVIEW" if is_interview else "FEATURE"),
        "publication": s["publication"],
        "issue": s["issue"],
        "publisher": s.get("publisher", ""),
        "interviewee": "、".join(people),
        "interviewer": feature.get("interviewer", s["publication"] + " 編集部"),
        "dek": cov.get("dek", ""),
        "summary": cov.get("summary", ""),
        "source_pages": f"{span}（{len(pages) - len(plates)} 页" + ("，另附封面/目次" if plates else "") + "；2048px 页图）",
        "source": {"title": feature["title_ja"], "source_type": "magazine_scan", "language": "ja",
                   "publication": s["publication"], "issue": s["issue"]},
        "source_kind": "magazine_interview" if is_interview else "magazine_feature",
        "original_lang": "ja",
        "translation_lang": "zh-CN",
        "parallel_view": "translation",
        "published": True,
        "translator": "qwen3.8-max 整页转写 / DeepSeek 初译",
        "workflow": {"scan": "done", "preprocess": "prepared set (dedup, deskew, 2048px web)", "ocr": "qwen3.8-max full-page",
                     "translation": "deepseek-machine", "proofreading": "pending", "published": "online"},
        "review_scope": "整页由视觉模型一次转写、DeepSeek 初译；未经人工逐字校对，读者请以页图为准。" + (" " + s["scan_note"] if s.get("scan_note") else ""),
        "pending_review_regions": sum(1 for x in segs if x.get("type") != "image"),
        "scan_set": s["slug"],
        "entities": {"people": people, "works": feature.get("works") or []},
        "translation_segments": segs,
    }
    for k in ("display_title", "dek", "summary", "publisher"):
        if not fm[k]:
            del fm[k]
    if not people:
        del fm["interviewee"]
    for x in fm["translation_segments"]:
        x["review_status"] = "review" if x.get("type") != "image" else "ready"
    body = "---\n" + dump_yaml(fm) + "\n---\n"
    path = POSTS / f"{s['date']}-scan-{feature['slug']}.md"
    path.write_text(body, encoding="utf-8", newline="\n")
    return path


# ---------------------------------------------------------------- commands
def cmd_pages(s):
    cache_dir = CACHE / s["slug"]
    for p in s["pages"]:
        txt = cache_dir / (p["file"] + ".txt")
        if not txt.exists():
            print(f"{str(p.get('page')):>4} {p['file']:50s} (no ocr)")
            continue
        blocks = parse_page(txt.read_text(encoding="utf-8"))
        heads = [("".join(b["lines"]))[:40] for b in blocks if b["kind"] in ("heading", "subheading")][:3]
        nchar = sum(len("".join(b["lines"])) for b in blocks if b["kind"] == "body")
        speakers = sorted({SPEAKER_RE.match(l).group(1) for b in blocks if b["kind"] == "body" for l in b["lines"] if SPEAKER_RE.match(l)})[:6]
        print(f"{str(p.get('page')):>4} {p['file'][:44]:44s} body {nchar:5d}  {' | '.join(heads)}  {speakers}")


def cmd_build(s, dry, only, glossary):
    cache_dir = CACHE / s["slug"]
    for feature in s["features"]:
        if only and feature["slug"] != only:
            continue
        if feature.get("skip"):
            print(f"-- {feature['slug']}: skipped ({feature['skip']})")
            continue
        pages = feature_pages(s, feature)
        print(f"== {feature['slug']}  {len(pages)} pages  {feature['title_ja'][:50]}")
        segs = to_segments(s, feature, cache_dir, feature.get("people") or [])
        n_text = sum(1 for x in segs if x.get("type") != "image")
        n_q = sum(1 for x in segs if x.get("speaker") == "──")
        n_named = sum(1 for x in segs if x.get("speaker") not in ("──", "image", "body", "note", "caption") and x.get("type") == "paragraph")
        print(f"   segments {len(segs)}  text {n_text}  questions {n_q}  named turns {n_named}")
        if dry:
            for x in segs[:14]:
                if x.get("type") == "image":
                    continue
                print(f"     [{x['region_type']}] {x.get('speaker', '')}: {x['original'][:60]}")
            continue
        copy_pages(s, feature, dry)
        segs = translate_segments(segs, s, feature, glossary)
        cov = cover(segs, s, feature)
        segs = tabulate(segs)
        path = write_post(s, feature, segs, cov)
        print(f"   wrote {path.name}")


def main():
    global reg_root
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["ocr", "pages", "build", "upload", "fix"])
    ap.add_argument("slug")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    reg = registry()
    reg_root = reg["scan_root"]
    sets = reg["sets"] if args.slug == "all" else [find_set(reg, args.slug)]
    if args.cmd == "ocr":
        if not VLM_KEY:
            raise SystemExit("VLM_OCR_API_KEY / DASHSCOPE_API_KEY not set")
        for s in sets:
            ocr_set(s, args.workers)
    elif args.cmd == "fix":
        # a built post, brought up to the current tool without re-translating everything:
        # the items the model dropped are translated, question translations lose the
        # dash the model prefixed, [表] blocks become tables
        import yaml
        glossary = load_glossary()
        for s in sets:
            for feature in s["features"]:
                for path in POSTS.glob(f"*-scan-{feature['slug']}.md"):
                    fm = yaml.safe_load(front_matter(path.read_text(encoding="utf-8")))
                    segs = fm["translation_segments"]
                    missing = [x for x in segs if x.get("type") == "paragraph" and x.get("original") and not x.get("translation")]
                    if missing:
                        translate_segments(missing, s, feature, glossary)
                    for x in segs:
                        if x.get("speaker") == "──" and x.get("translation"):
                            x["translation"] = re.sub(r"^[─—－-]{1,2}\s*", "", x["translation"])
                        # a paragraph the model tagged as a heading (built before split_runaway_headings):
                        # the translation is in speaker, the Japanese in original - make it a body paragraph
                        if x.get("type") == "heading" and len(x.get("original") or "") > 120 and not x.get("translation"):
                            x["type"], x["region_type"], x["kind"] = "paragraph", "body", "text"
                            x["translation"], x["speaker"] = x["speaker"], "body"
                            x.pop("heading_level", None)
                    # a one-off label nobody declared (a book title, a shop name) is not a speaker
                    declared = set(feature.get("people") or []) | set((feature.get("speaker_map") or {}).values()) | {"──", "全体", "全員", "body", "note", "caption", "image"}
                    tally = {}
                    for x in segs:
                        if x.get("type") == "paragraph" and x.get("region_type") == "body":
                            tally[x.get("speaker")] = tally.get(x.get("speaker"), 0) + 1
                    demoted = 0
                    for x in segs:
                        sp = x.get("speaker")
                        if x.get("type") == "paragraph" and x.get("region_type") == "body" and sp not in declared and tally.get(sp, 0) < 2:
                            x["original"] = f"{sp} {x.get('original', '')}"
                            x["translation"] = f"{sp} {x.get('translation', '')}"
                            x["speaker"] = "body"
                            demoted += 1
                    before = sum(1 for x in segs if x.get("type") == "table")
                    fm["translation_segments"] = tabulate(segs)
                    after = sum(1 for x in segs if x.get("type") == "table")
                    path.write_text(post_text(fm), encoding="utf-8", newline="\n")
                    print(f"{path.name}: filled {len(missing)}, demoted {demoted}, tables {before} -> {after}")
    elif args.cmd == "upload":
        for s in sets:
            upload_set(s)
    elif args.cmd == "pages":
        for s in sets:
            print(f"==== {s['slug']}")
            cmd_pages(s)
    else:
        glossary = load_glossary()
        for s in sets:
            cmd_build(s, args.dry_run, args.only, glossary)


if __name__ == "__main__":
    main()
