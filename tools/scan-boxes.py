"""Where on the page each transcribed region sits.

The scan posts built by import-scan-set.py carry one segment per region of
the page - heading, body turn, caption, boxed note, table - but no
coordinates: the page was transcribed whole, and the vision model was asked
for the words, not for where they were. Without coordinates the reader
cannot tie a paragraph to its place on the page, a caption to its
photograph, or a column of vertical text to the fact that it is vertical.

This asks the same model, page by page, to locate the regions it already
transcribed: the page image (the 2048px one the site serves, so the
coordinates land on the picture the reader sees) plus the list of regions,
back comes a box for each; a region that spans two bands of columns may
get several boxes. The writing direction is not asked of the model - it called
every narrow horizontal column "vertical" on DREAM 2011.1 P.22 - but read
off the page: RapidOCR's text-line detector finds the lines, and a region
whose lines are tall is vertical, whose lines are wide is horizontal
(ダ・ヴィンチ P.133 came out right that way: vertical interview, horizontal
book guide). A region with no detected line takes the page's majority.

    python tools/scan-boxes.py calibrate <slug> <page-file> [...]   # one page, drawn, to check the coordinate space
    python tools/scan-boxes.py run   <slug>|all [--workers 4] [--only <feature>] [--force]
    python tools/scan-boxes.py apply <slug>|all [--only <feature>]  # cache -> posts, no API
    python tools/scan-boxes.py report <slug>|all                     # coverage per feature

Cache: data/cache_scan/<slug>/<page>.boxes.json (by region id). Page images
downloaded from the CDN and the drawn review sheets go to a work directory
beside the repository (SCAN_WORK, default ../scan-work), not into git.
"""
import argparse
import base64
import importlib.util
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache_scan"
POSTS = ROOT / "_posts"
WORK = Path(os.environ.get("SCAN_WORK") or (ROOT.parent / "scan-work"))

_spec = importlib.util.spec_from_file_location("import_scan_set", ROOT / "tools" / "import-scan-set.py")
_imp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_imp)
registry, find_set, front_matter, post_text = _imp.registry, _imp.find_set, _imp.front_matter, _imp.post_text
VLM_URL, VLM_KEY, VLM_MODEL = _imp.VLM_URL, _imp.VLM_KEY, _imp.VLM_MODEL

KINDS = {"heading": "見出し", "body": "本文", "caption": "キャプション", "note": "囲み", "table": "表"}

PROMPT = (
    "これは日本の雑誌のスキャンページ（{w}×{h} ピクセル）です。下の一覧は、このページから書き起こした各テキスト領域です。"
    "各領域が誌面のどこにあるかを答えてください。座標は画像の幅と高さをそれぞれ 1000 とした相対座標（0〜1000 の整数）で、左上が原点です。\n"
    "・各領域について [x1, y1, x2, y2]（左上と右下）を返す。文字の塊をぴったり囲む。\n"
    "・領域が複数の段組（コラム帯）にまたがる場合は、段組ごとに矩形を分けて boxes に順に入れる（最初の矩形が領域の始まり、最大6個）。ひとつの段組に収まる領域は1つ。\n"
    "・見つからない領域は boxes を null にする。ページに無い領域を作らない。\n"
    "・出力は JSON のみ： {{\"regions\": [{{\"i\": 番号, \"boxes\": [[x1,y1,x2,y2]]}}, ...]}}\n\n"
    "領域一覧：\n{regions}"
)


# ---------------------------------------------------------------- pages and posts
def feature_posts(s, feature):
    return sorted(POSTS.glob(f"*-scan-{feature['slug']}.md"))


def load_post(path):
    import yaml
    return yaml.safe_load(front_matter(path.read_text(encoding="utf-8")))


def page_groups(fm):
    """The post's segments by page: [(page index, plate segment or None, [text segments])]."""
    by = {}
    for seg in fm.get("translation_segments") or []:
        by.setdefault(int(seg.get("scan_page") or 0), []).append(seg)
    out = []
    for idx in sorted(by):
        segs = by[idx]
        plate = next((x for x in segs if x.get("type") == "image" and (str(x.get("region_id", "")).endswith("-fullpage") or "/pages/" in str(x.get("image", "")))), None)
        texts = [x for x in segs if x.get("type") != "image" and (x.get("original") or x.get("speaker"))]
        out.append((idx, plate, texts))
    return out


def page_file_of(plate):
    m = re.search(r"/pages/([^/]+)\.jpg$", plate.get("image", ""))
    if m:
        return m.group(1)
    return re.sub(r"-fullpage$", "", str(plate.get("region_id", "page")))


def fetch_image(url, dest):
    """The page image, from the CDN or from the repository's assets."""
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    if url.startswith("http"):
        req = urllib.request.Request(url, headers={"User-Agent": "pokeamice-scan-boxes/1"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    dest.write_bytes(r.read())
                return dest
            except (urllib.error.URLError, TimeoutError) as exc:
                print(f"    fetch error ({attempt + 1}): {exc}", file=sys.stderr)
                time.sleep(3)
        raise RuntimeError("cannot fetch " + url)
    src = ROOT / url.lstrip("/")
    dest.write_bytes(src.read_bytes())
    return dest


def region_line(i, seg):
    kind = KINDS.get(seg.get("region_type"), seg.get("region_type", ""))
    text = (seg.get("original") or seg.get("speaker") or "").replace("\n", " ")
    if seg.get("type") == "heading" and not seg.get("original"):
        text = seg.get("speaker", "")
    if len(text) > 70:
        text = text[:52] + "……" + text[-14:]
    who = seg.get("speaker", "")
    lead = ""
    if seg.get("region_type") == "body" and who and who not in ("body", "note", "caption"):
        lead = ("――" if who in ("──", "——") else who + "：")
    return f"{i}. [{kind}] {lead}{text}"


# ---------------------------------------------------------------- the model
def ask(image_path, w, h, texts):
    listing = "\n".join(region_line(i + 1, seg) for i, seg in enumerate(texts))
    data = "data:image/jpeg;base64," + base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
    body = {
        "model": VLM_MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": data}},
            {"type": "text", "text": PROMPT.format(w=w, h=h, regions=listing)},
        ]}],
        "max_tokens": 6000,
        "temperature": 0,
        "enable_thinking": False,
        "vl_high_resolution_images": True,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(VLM_URL, data=json.dumps(body).encode("utf-8"),
                                 headers={"Authorization": "Bearer " + VLM_KEY, "Content-Type": "application/json"})
    last = None
    for attempt in range(4):
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.load(r)
            text = d["choices"][0]["message"]["content"]
            m = re.search(r"\{.*\}", text, re.S)
            parsed = json.loads(m.group(0) if m else text)
            usage = d.get("usage", {})
            return parsed, {"model": VLM_MODEL, "seconds": round(time.time() - t0, 1),
                            "image_tokens": (usage.get("prompt_tokens_details") or {}).get("image_tokens"),
                            "completion_tokens": usage.get("completion_tokens"),
                            "finish": d["choices"][0].get("finish_reason")}
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, KeyError, AttributeError) as exc:
            last = exc
            detail = ""
            if isinstance(exc, urllib.error.HTTPError):
                try:
                    detail = exc.read().decode("utf-8", "replace")[:300]
                except Exception:
                    pass
            print(f"    vlm error (attempt {attempt + 1}): {exc} {detail}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"vlm failed for {image_path}: {last}")


_ocr = None


def text_lines(image_path):
    """The text lines on the page as boxes, from RapidOCR's detector (no recognition).
    [] when RapidOCR is not installed."""
    global _ocr
    try:
        import numpy as np
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        return []
    from PIL import Image
    if _ocr is None:
        _ocr = RapidOCR()
    with Image.open(image_path) as im:
        arr = np.asarray(im.convert("RGB"))[:, :, ::-1]
    res, _ = _ocr(arr, use_det=True, use_cls=False, use_rec=False)
    out = []
    for r in res or []:
        pts = np.asarray(r[0] if isinstance(r[0], (list, tuple, np.ndarray)) and len(r[0]) == 4 else r, dtype=float)
        out.append([int(pts[:, 0].min()), int(pts[:, 1].min()), int(pts[:, 0].max()), int(pts[:, 1].max())])
    return out


def line_direction(lines, box=None):
    """vertical / horizontal by the area of tall against wide lines inside the box
    (the whole page when box is None); None when no line is there."""
    v = h = 0.0
    for lx1, ly1, lx2, ly2 in lines:
        lw, lh = lx2 - lx1, ly2 - ly1
        area = lw * lh
        if area <= 0:
            continue
        if box is not None:
            ix = max(0, min(box[2], lx2) - max(box[0], lx1))
            iy = max(0, min(box[3], ly2) - max(box[1], ly1))
            if ix * iy < 0.5 * area:
                continue
        if lh > 1.8 * lw:
            v += area
        elif lw > 1.8 * lh:
            h += area
    if v == 0 and h == 0:
        return None
    return "vertical" if v > h else "horizontal"


def clean_boxes(raw, w, h, scale=(1.0, 1.0)):
    """Boxes clamped to the page, degenerate ones dropped; None when nothing survives."""
    out = []
    for b in raw or []:
        if not isinstance(b, (list, tuple)) or len(b) != 4:
            continue
        try:
            x1, y1, x2, y2 = [float(v) for v in b]
        except (TypeError, ValueError):
            continue
        x1, x2, y1, y2 = x1 * scale[0], x2 * scale[0], y1 * scale[1], y2 * scale[1]
        x1, x2 = sorted((max(0, min(w, x1)), max(0, min(w, x2))))
        y1, y2 = sorted((max(0, min(h, y1)), max(0, min(h, y2))))
        if x2 - x1 < 8 or y2 - y1 < 8:
            continue
        if (x2 - x1) * (y2 - y1) > 0.92 * w * h:
            continue  # the whole page is not a region
        out.append([int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))])
    return out[:6] or None


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua else 0


def locate_page(image_path, texts):
    from PIL import Image
    with Image.open(image_path) as im:
        w, h = im.size
    parsed, meta = ask(image_path, w, h, texts)
    # the model answers in Qwen's grounding convention, both axes 0-1000 (checked on
    # DREAM 2011.1 P.7: the boxes drawn at face value sat in the top-left corner);
    # should it ever answer in pixels, nothing needs scaling
    allv = [float(v) for r in parsed.get("regions") or [] for b in (r.get("boxes") or ([r["bbox_2d"]] if r.get("bbox_2d") else [])) if isinstance(b, (list, tuple)) for v in b if isinstance(v, (int, float))]
    scale = (w / 1000.0, h / 1000.0) if allv and max(allv) <= 1000 else (1.0, 1.0)
    meta["scale"] = "1000" if scale != (1.0, 1.0) else "px"
    lines = text_lines(image_path)
    page_dir = line_direction(lines) or "horizontal"
    found = {}
    for r in parsed.get("regions") or []:
        try:
            i = int(r.get("i"))
        except (TypeError, ValueError):
            continue
        if not 1 <= i <= len(texts):
            continue
        boxes = clean_boxes(r.get("boxes") or ([r["bbox_2d"]] if r.get("bbox_2d") else None), w, h, scale)
        if not boxes:
            continue
        found[i] = {"boxes": boxes, "direction": line_direction(lines, boxes[0]) or page_dir}
    # a box that repeats an earlier one is the model losing its place, not a second region
    seen = []
    for i in sorted(found):
        b = found[i]["boxes"][0]
        if any(iou(b, o) > 0.8 for o in seen):
            found[i]["dup"] = True
        seen.append(b)
    regions = {}
    for i, seg in enumerate(texts, 1):
        rid = seg.get("region_id") or f"i{i}"
        if i in found and not found[i].get("dup"):
            regions[rid] = found[i]
        else:
            regions[rid] = None
    return {"width": w, "height": h, "page_direction": page_dir, "lines": lines, "regions": regions, "meta": meta}


def draw_review(image_path, out_path, texts, regions, max_w=1100):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(image_path).convert("RGB")
    scale = min(1.0, max_w / im.width)
    if scale < 1:
        im = im.resize((int(im.width * scale), int(im.height * scale)))
    dr = ImageDraw.Draw(im, "RGBA")
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
    except OSError:
        font = ImageFont.load_default()
    colours = {"heading": (220, 40, 40), "body": (30, 90, 220), "caption": (20, 150, 60), "note": (200, 120, 0), "table": (140, 40, 160)}
    for i, seg in enumerate(texts, 1):
        r = regions.get(seg.get("region_id") or f"i{i}")
        if not r:
            continue
        c = colours.get(seg.get("region_type"), (80, 80, 80))
        for k, b in enumerate(r["boxes"]):
            x1, y1, x2, y2 = [v * scale for v in b]
            dr.rectangle([x1, y1, x2, y2], outline=c + (255,), width=3, fill=c + (28,))
            tag = f"{i}{'v' if r.get('direction') == 'vertical' else 'h' if r.get('direction') else ''}{'+' if k else ''}"
            dr.rectangle([x1, y1 - 20, x1 + 12 * len(tag) + 6, y1], fill=c + (230,))
            dr.text((x1 + 3, y1 - 20), tag, fill=(255, 255, 255), font=font)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path, quality=82)


# ---------------------------------------------------------------- commands
def sets_for(reg, slug):
    return reg["sets"] if slug == "all" else [find_set(reg, slug)]


def page_jobs(s, only=""):
    """Every (feature, post path, page index, plate, texts, cache path) of a set."""
    jobs = []
    for feature in s.get("features") or []:
        if only and feature["slug"] != only:
            continue
        for path in feature_posts(s, feature):
            fm = load_post(path)
            for idx, plate, texts in page_groups(fm):
                if not plate or not texts:
                    continue
                cache = CACHE / s["slug"] / (page_file_of(plate) + ".boxes.json")
                jobs.append((feature, path, idx, plate, texts, cache))
    return jobs


def dump_cache(rec):
    """One region (and one detected line) per line, so the cache diffs by region and
    does not run to thousands of lines of bare numbers."""
    out = ["{"]
    for k, v in rec.items():
        if k == "regions":
            rows = [json.dumps(rid, ensure_ascii=False) + ": " + json.dumps(r, ensure_ascii=False, separators=(",", ":")) for rid, r in v.items()]
            out.append(' "regions": {\n  ' + ",\n  ".join(rows) + "\n },")
        elif k == "lines":
            out.append(' "lines": [' + ", ".join(json.dumps(l, separators=(",", ":")) for l in v) + "],")
        else:
            out.append(" " + json.dumps(k) + ": " + json.dumps(v, ensure_ascii=False) + ",")
    out[-1] = out[-1].rstrip(",")
    out.append("}")
    return "\n".join(out) + "\n"


def run_job(s, feature, plate, texts, cache, review=True):
    pf = page_file_of(plate)
    img = fetch_image(plate["image"], WORK / "pages" / feature["slug"] / (pf + ".jpg"))
    rec = locate_page(img, texts)
    rec["image"] = plate["image"]
    rec["page_file"] = pf
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(dump_cache(rec), encoding="utf-8")
    if review:
        draw_review(img, WORK / "review" / feature["slug"] / (pf + ".jpg"), texts, rec["regions"])
    return rec


def cmd_run(reg, slug, workers, only, force):
    todo = []
    for s in sets_for(reg, slug):
        for job in page_jobs(s, only):
            feature, path, idx, plate, texts, cache = job
            if cache.exists() and not force:
                # only pages whose region set changed are asked again
                old = json.loads(cache.read_text(encoding="utf-8"))
                ids = [x.get("region_id") for x in texts]
                if all(i in old.get("regions", {}) for i in ids):
                    continue
            todo.append((s, job))
    print(f"{len(todo)} pages to locate", flush=True)

    def one(s, job):
        feature, path, idx, plate, texts, cache = job
        rec = run_job(s, feature, plate, texts, cache)
        got = sum(1 for v in rec["regions"].values() if v)
        return f"{feature['slug']}/{rec['page_file']}", got, len(texts), rec["meta"]

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, s, job): job for s, job in todo}
        for f in as_completed(futs):
            job = futs[f]
            try:
                name, got, n, meta = f.result()
                print(f"  ok {name}  {got}/{n} boxes  {meta['seconds']}s  {meta['finish']}", flush=True)
            except Exception as exc:
                print(f"  FAIL {job[0]['slug']}/{page_file_of(job[3])}: {exc}", file=sys.stderr, flush=True)


def cmd_apply(reg, slug, only):
    import yaml  # noqa: F401  (load_post)
    for s in sets_for(reg, slug):
        for feature in s.get("features") or []:
            if only and feature["slug"] != only:
                continue
            for path in feature_posts(s, feature):
                fm = load_post(path)
                n_box = n_text = 0
                for idx, plate, texts in page_groups(fm):
                    if not plate:
                        continue
                    cache = CACHE / s["slug"] / (page_file_of(plate) + ".boxes.json")
                    if not cache.exists():
                        continue
                    rec = json.loads(cache.read_text(encoding="utf-8"))
                    plate["width"], plate["height"] = rec["width"], rec["height"]
                    for seg in texts:
                        n_text += 1
                        r = rec["regions"].get(seg.get("region_id"))
                        for k in ("scan_box", "scan_boxes", "writing_direction"):
                            seg.pop(k, None)
                        if not r:
                            continue
                        n_box += 1
                        seg["scan_box"] = r["boxes"][0]
                        if len(r["boxes"]) > 1:
                            seg["scan_boxes"] = r["boxes"]
                        if r.get("direction"):
                            seg["writing_direction"] = r["direction"]
                path.write_text(post_text(fm), encoding="utf-8", newline="\n")
                print(f"  {path.name}: {n_box}/{n_text} regions boxed")


def cmd_report(reg, slug):
    for s in sets_for(reg, slug):
        for feature in s.get("features") or []:
            for path in feature_posts(s, feature):
                fm = load_post(path)
                n = sum(1 for x in fm.get("translation_segments") or [] if x.get("type") != "image")
                b = sum(1 for x in fm.get("translation_segments") or [] if x.get("scan_box"))
                v = sum(1 for x in fm.get("translation_segments") or [] if x.get("writing_direction") == "vertical")
                print(f"  {path.name}: {b}/{n} boxed, {v} vertical")


def cmd_calibrate(reg, slug, files):
    s = find_set(reg, slug)
    for job in page_jobs(s):
        feature, path, idx, plate, texts, cache = job
        if page_file_of(plate) not in files:
            continue
        rec = run_job(s, feature, plate, texts, cache)
        got = sum(1 for v in rec["regions"].values() if v)
        print(f"{feature['slug']}/{rec['page_file']}: {got}/{len(texts)} boxes, {rec['width']}x{rec['height']}, {rec['meta']}")
        for i, seg in enumerate(texts, 1):
            r = rec["regions"].get(seg.get("region_id"))
            print(f"   {i:>2} {seg.get('region_type', ''):<8} {str(r['boxes']) if r else '-':<40} {(r or {}).get('direction') or ''}  {(seg.get('original') or seg.get('speaker') or '')[:30]}")
        print("   review:", WORK / "review" / feature["slug"] / (rec["page_file"] + ".jpg"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["calibrate", "run", "apply", "report"])
    ap.add_argument("slug")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    reg = registry()
    if a.cmd == "calibrate":
        cmd_calibrate(reg, a.slug, set(a.files))
    elif a.cmd == "run":
        cmd_run(reg, a.slug, a.workers, a.only, a.force)
    elif a.cmd == "apply":
        cmd_apply(reg, a.slug, a.only)
    else:
        cmd_report(reg, a.slug)


if __name__ == "__main__":
    main()
