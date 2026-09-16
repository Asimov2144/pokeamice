"""Bring a CEDEC slide deck downloaded from CEDiL into _posts as a technical
report: every slide a figure with its text under it, section slides as
headings, the session's own abstract and speaker profile from the public
CEDiL page, DeepSeek for the Chinese.

    python tools/import-cedil-deck.py 3341 "C:/Users/me/Downloads/deck.pdf"            # write the post
    python tools/import-cedil-deck.py 3341 deck.pdf --dry-run                            # parse only, print the slides

CEDiL (cedil.cesa.or.jp) shows a session's title, date, abstract and speaker
profile to anyone; the PDF itself is behind a free login, so the deck is
handed to this script as a file the person downloaded. Slides are rendered
at 960 px as JPEG under assets/img/interviews/<slug>/, and the slide text
comes from the PDF's own text layer (the decks CEDiL hosts are exported
from PowerPoint or Google Slides and carry it). A slide whose text is only
a section title - the agenda names them - becomes a heading; the title
slide, the agenda and the housekeeping slide are kept as narrative.
"""
import html as htmlmod
import importlib.util
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import pymupdf
import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "_posts"
IMG_DIR = ROOT / "assets" / "img" / "interviews"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}

_spec = importlib.util.spec_from_file_location("import_web", ROOT / "tools" / "import-web.py")
_web = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_web)
deepseek, load_glossary, glossary_hits, era_for, LANG_NAME = _web.deepseek, _web.load_glossary, _web.glossary_hits, _web.era_for, _web.LANG_NAME


# ---------------------------------------------------------------- CEDiL
def session(cedil_id):
    """Title, event, date, abstract, speakers and profile from the public page."""
    url = f"https://cedil.cesa.or.jp/cedil_sessions/view/{cedil_id}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        html = r.read().decode("utf-8", "replace")
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    text = htmlmod.unescape(re.sub(r"\n\s*\n+", "\n", re.sub(r"<[^>]+>", "\n", text)))
    title = htmlmod.unescape(re.search(r"<title>(.*?)\s*\|", html, re.S).group(1).strip())
    date = re.search(r"(\d{4})年(\d{2})月(\d{2})日", text)
    event = re.search(r"\n(CEDEC(?:\+\w+)? \d{4})\n", text.split("セッション詳細", 1)[-1])
    abstract = re.search(r"セッションの内容\n(.+?)\n講演資料", text, re.S)
    prof = text.split("講演者プロフィール", 1)[-1].split("セッション検索", 1)[0]
    speakers = []
    for m in re.finditer(r"\n([^\n]{2,14})\n((?:株式会社|GAME FREAK|Niantic|[^\n]*Inc\.)[^\n]*)\n([^\n]*)\n([^\n]*)\n", prof):
        speakers.append({"name": re.sub(r"\s+", " ", m.group(1)).strip(), "org": m.group(2).strip(), "dept": m.group(3).strip(), "role": m.group(4).strip()})
    return {"id": cedil_id, "url": url, "title": title, "event": event.group(1) if event else "CEDEC",
            "date": f"{date.group(1)}-{date.group(2)}-{date.group(3)}" if date else "",
            "abstract": abstract.group(1).strip() if abstract else "", "speakers": speakers,
            "profile": re.sub(r"\n+", "\n", prof).strip()[:1200]}


# ---------------------------------------------------------------- deck
def slides(pdf_path):
    """Each page's text lines, plus the font size of its largest type and
    whether the page is one full-bleed picture (a notes export: the slide as
    an image with the presenter's script beside it)."""
    doc = pymupdf.open(str(pdf_path))
    out = []
    for i, page in enumerate(doc):
        raw = [l.strip() for l in (page.get_text("text") or "").split("\n") if l.strip()]
        # the page number a deck prints in its corner
        if raw and re.fullmatch(r"\d{1,3}", raw[-1]):
            raw = raw[:-1]
        # a bullet glyph or a list number the text layer puts on a line of its own joins the line after it
        lines = []
        for l in raw:
            if lines and re.fullmatch(r"[●○◆◇■□▶•・]|\d{1,2}[.．)]", lines[-1]):
                lines[-1] = lines[-1] + " " + l
            else:
                lines.append(l)
        sizes = [round(sp["size"]) for b in page.get_text("dict")["blocks"] if b.get("type") == 0
                 for ln in b["lines"] for sp in ln["spans"] if sp["text"].strip()]
        out.append({"n": i + 1, "lines": lines, "top": max(sizes) if sizes else 0, "small": max(sizes) <= 13 if sizes else False})
    # the deck's usual title size: what most pages' largest type is
    tops = [s["top"] for s in out if s["top"]]
    title_size = max(set(tops), key=tops.count) if tops else 0
    notes = sum(1 for s in out if s["small"]) >= 0.6 * max(1, sum(1 for s in out if s["lines"]))
    return doc, out, title_size, notes


def classify(slide, agenda, title_size):
    """heading for a section-divider slide - a lone line set larger than the
    deck's title size, or a lone line the agenda names; a sub-heading when
    a second line names the part; skip for a blank one; else body."""
    lines = slide["lines"]
    if not lines:
        return "skip"
    first = lines[0]
    if len(lines) == 1 and len(first) <= 40 and slide["top"] > title_size:
        return "heading"
    if len(lines) <= 3 and len(" ".join(lines)) <= 70 and any(a and (a in first or first in a) for a in agenda):
        return "heading" if len(lines) == 1 else "subheading"
    return "body"


SCRIPT_HEAD = re.compile(r"^ここからは[、，]?(.+?)(?:について|を)(?:説明|紹介|お話し|ご紹介|見て)")


def script_text(lines):
    """A presenter's script wrapped hard at the notes-pane width: a line that
    does not end a sentence continues on the next one; a stage direction
    (★, ※) stands on its own."""
    out = []
    for l in lines:
        if out and not re.search(r"(?:[。！？!?」』）)】]|です|ます|でした|ました|ません|でしょう)$", out[-1]) and not re.match(r"^[★※●]", l) and not re.match(r"^[★※●]", out[-1]):
            out[-1] += l
        else:
            out.append(l)
    return "\n".join(out)


def slide_markdown(lines):
    """Bullets stay bullets; a run of short fragments (a diagram's labels) is
    folded into one line so it does not read as prose."""
    out, frag = [], []
    for l in lines:
        if re.match(r"^[●○◆◇■□▶•・\-]\s*", l):
            if frag:
                out.append(" ／ ".join(frag)); frag = []
            out.append("- " + re.sub(r"^[●○◆◇■□▶•・\-]\s*", "", l))
        elif len(l) <= 14 and not re.search(r"[。．.！？!?]$", l):
            frag.append(l)
        else:
            if frag:
                out.append(" ／ ".join(frag)); frag = []
            out.append(l)
    if frag:
        out.append(" ／ ".join(frag))
    return "\n".join(out)


def build_items(doc, deck, meta, slug, dry, title_size=0, notes=False):
    agenda = []
    for s in deck[:8]:
        if any(l.startswith("目次") or l == "アジェンダ" or l.lower() == "agenda" or l == "本日の内容" for l in s["lines"]):
            agenda = [re.sub(r"^\d+[.．)]\s*", "", l).strip() for l in s["lines"] if re.match(r"^\d+[.．)]", l)]
            agenda = [re.sub(r"の紹介と課題$|と課題$", "", a) for a in agenda] + agenda
    items, dest = [], IMG_DIR / slug
    for s in deck:
        kind = classify(s, agenda, title_size)
        if notes:
            # a notes export: the page is the slide, the text is what was said over it
            kind = "skip" if not s["lines"] and s["n"] > 1 else "body"
            if kind == "body" and s["lines"]:
                m = SCRIPT_HEAD.match(s["lines"][0])
                if m:
                    items.append({"type": "heading", "level": 2, "original": m.group(1).strip(), "_slide": s["n"]})
        if kind == "skip":
            continue
        text = slide_markdown(s["lines"]) if not notes else script_text(s["lines"])
        if kind == "heading":
            items.append({"type": "heading", "level": 2, "original": s["lines"][0], "_slide": s["n"]})
            continue
        if kind == "subheading":
            # the part's own section head, once, before its first sub-part
            if not any(x.get("type") == "heading" and x["original"] == s["lines"][0] for x in items):
                items.append({"type": "heading", "level": 2, "original": s["lines"][0], "_slide": s["n"]})
            items.append({"type": "heading", "level": 3, "original": " ".join(s["lines"][1:]), "_slide": s["n"]})
            continue
        if not dry:
            dest.mkdir(parents=True, exist_ok=True)
            out = dest / f"slide-{s['n']:02d}.jpg"
            if not out.exists():
                page = doc[s["n"] - 1]
                pix = page.get_pixmap(matrix=pymupdf.Matrix(960 / page.rect.width, 960 / page.rect.width))
                pix.save(str(out), jpg_quality=78)
            items.append({"type": "image", "image": "/" + out.relative_to(ROOT).as_posix(), "alt": f"{meta['title']} - 第{s['n']}页", "_slide": s["n"]})
        else:
            items.append({"type": "image", "image": f"slide-{s['n']:02d}.jpg", "_slide": s["n"]})
        if text.strip():
            items.append({"original": text, "_slide": s["n"]})
    return items


# ---------------------------------------------------------------- translate / write
SYSTEM = ("你是宝可梦开发史料与游戏技术文献的日中译者，正在翻译 CEDEC 讲演幻灯片。译文忠实、平实，保留 Markdown 列表符号与行结构；"
          "技术名词（Kubernetes、Pod、DaemonSet、Windows コンテナ、GitLab Runner、Azure 等）保留英文原名，日文外来语还原为英文；只输出合法 JSON。")


def translate(items, meta, glossary):
    text_items = [(i, x) for i, x in enumerate(items) if x.get("type") != "image"]
    hits = glossary_hits("\n".join(x["original"] for _, x in text_items), glossary)
    gloss = "\n".join(f"- {s} → {t}" for s, t in hits) or "（无）"
    system = SYSTEM + f"\n术语表：\n{gloss}"
    for start in range(0, len(text_items), 8):
        part = text_items[start:start + 8]
        payload = [{"i": i, "text": x["original"]} for i, x in part]
        prompt = (f"这是 {meta['event']} 讲演《{meta['title']}》（{'、'.join(s['name'] for s in meta['speakers'])}）的幻灯片文字。"
                  f"逐条译成简体中文，保留编号 i 与每条内部的换行和「- 」列表符；note 只在读者很可能不知道的具体事实上给一句，一般留空。\n\n"
                  f"输出格式：{{\"items\":[{{\"i\":编号,\"translation\":\"译文\",\"note\":\"\"}}]}}\n\n待译：\n{json.dumps(payload, ensure_ascii=False)}")
        print(f"  translating {start + 1}-{start + len(part)} / {len(text_items)} ...", flush=True)
        got = None
        for attempt in range(3):
            raw = deepseek([{"role": "system", "content": system}, {"role": "user", "content": prompt}])
            try:
                got = {int(r["i"]): r for r in json.loads(raw).get("items", []) if "i" in r}
                break
            except (ValueError, TypeError) as exc:
                print(f"    bad JSON (attempt {attempt + 1}): {exc}", file=sys.stderr)
        if got is None:
            raise RuntimeError("translation failed")
        for i, x in part:
            r = got.get(i) or {}
            x["translation"] = str(r.get("translation", "")).strip()
            if str(r.get("note", "") or "").strip():
                x["note"] = str(r["note"]).strip()
        time.sleep(1)
    return items


def cover(meta, items):
    sample = "\n".join(x.get("translation", "") for x in items if x.get("type") != "image")[:5000]
    prompt = (f"下面是 {meta['event']} 讲演《{meta['title']}》的中文译文节选，讲者 {'、'.join(s['name'] + '（' + s['org'] + '）' for s in meta['speakers'])}。"
              f"讲演摘要（日文）：{meta['abstract']}\n"
              f"给出：title（中文标题，形如「{meta['event']}：……」，45字以内，写清讲者与主题，不用感叹号）、display_title（20字以内）、"
              f"dek（一句导语，60字以内）、summary（150字以内的内容提要，平实，从摘要与内容归纳）、abstract_zh（摘要全文的中文翻译）。"
              f"输出 JSON：{{\"title\":\"\",\"display_title\":\"\",\"dek\":\"\",\"summary\":\"\",\"abstract_zh\":\"\"}}\n\n{sample}")
    return json.loads(deepseek([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], max_tokens=1500))


def write_post(meta, items, cov, slug, pdf_name, notes=False):
    year = meta["date"][:4]
    people = [s["name"].replace(" ", "") for s in meta["speakers"]]
    orgs = sorted({s["org"] for s in meta["speakers"]})
    clean = [{k: v for k, v in x.items() if not k.startswith("_")} for x in items]
    fm = {
        "layout": "interview-editorial",
        "archive_type": "interview_translation",
        "title": cov.get("title") or f"{meta['event']}：{meta['title']}",
        "display_title": cov.get("display_title") or None,
        "dek": cov.get("dek") or None,
        "original_title": meta["title"],
        "date": meta["date"],
        "era_skin": era_for(year),
        "categories": ["访谈翻译", "翻译", "访谈整理"],
        "tags": ["技术专题", meta["event"], "讲演资料", "CEDiL"] + people + orgs,
        "publication": f"{meta['event']} 講演資料（CEDEC Digital Library）",
        "source_kind": "technical_report",
        "article_kind": "slide_deck",
        "author": "、".join(people),
        "interviewer": meta["event"],
        "interviewee": "、".join(people),
        "organization": "、".join(orgs),
        "translator": "PokeAmice（DeepSeek 初译）",
        "original_lang": "ja",
        "translation_lang": "zh-CN",
        "source": {"title": meta["title"], "url": meta["url"], "language": "ja", "source_type": "conference_slides",
                   "file": pdf_name, "access": "CEDiL 免费注册后可下载", "text_is": "讲者备注稿（発表原稿）" if notes else "幻灯片文字"},
        "original_link": meta["url"],
        "summary": cov.get("summary") or None,
        "session_abstract": meta["abstract"],
        "session_abstract_zh": cov.get("abstract_zh") or None,
        "speakers": meta["speakers"],
        "entities": {"people": people, "works": [], "organizations": orgs},
        "workflow": {"fetch": "cedil-pdf", "translation": "deepseek-chat", "proofreading": "pending", "published": "draft"},
        "parallel_items": clean,
    }
    fm = {k: v for k, v in fm.items() if v is not None}
    path = POSTS / f"{slug}.md"
    path.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n", encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    cedil_id, pdf = args[0], Path(args[1])
    meta = session(cedil_id)
    print(f"== CEDiL {cedil_id}: {meta['event']} {meta['date']} | {meta['title']}")
    for s in meta["speakers"]:
        print(f"   {s['name']} ({s['org']} {s['dept']} {s['role']})")
    slug_key = re.sub(r"[^a-z0-9]+", "-", (args[2] if len(args) > 2 else f"cedil-{cedil_id}").lower()).strip("-")
    slug = f"{meta['date']}-interview-{slug_key}"
    doc, deck, title_size, notes = slides(pdf)
    print(f"   title size {title_size}pt; {'notes export - text is the presenter script' if notes else 'slide text'}")
    items = build_items(doc, deck, meta, slug, dry, title_size, notes)
    n_h = sum(1 for x in items if x.get("type") == "heading"); n_i = sum(1 for x in items if x.get("type") == "image")
    print(f"   {len(deck)} slides -> {len(items)} items: {n_h} headings, {n_i} figures, {len(items) - n_h - n_i} text")
    if dry:
        for x in items:
            if x.get("type") == "image":
                continue
            print(f"   [{x.get('type') or 'text':7}] p{x['_slide']:02d} {x['original'][:100].replace(chr(10), ' | ')}")
        sys.exit()
    items = translate(items, meta, load_glossary())
    cov = cover(meta, items)
    print("   wrote", write_post(meta, items, cov, slug, pdf.name, notes).relative_to(ROOT))
