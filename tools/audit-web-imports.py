"""How complete each web-sourced interview is: the original page is fetched (cached under
data/cache_web/audit/), its article cut out the way import-web.py cuts it (the target's
container when the post has a target, else the densest block of paragraphs), and its text
and pictures are held against what the post carries - the `original` of every
parallel_items / translation_segments row, and the image rows. A post whose original text
is well short of the page's is flagged.

    python tools/audit-web-imports.py                 # every interview post with a web source
    python tools/audit-web-imports.py --only gigazine # posts whose file name contains this
    python tools/audit-web-imports.py --refetch       # ignore the cache
    python tools/audit-web-imports.py --only kotaku --detail   # and print the paragraphs a post lacks

Writes design/web_import_audit.json (one row per post) and prints the short ones.
"""
import glob
import io
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, Tag

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache_web" / "audit"
OUT = ROOT / "design" / "web_import_audit.json"
FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "ja,en;q=0.8,zh;q=0.6"}
SHORT = 0.6          # below this share of the page's paragraphs (by length) the post is flagged

sys.path.insert(0, str(ROOT / "tools"))
import importlib.util
_spec = importlib.util.spec_from_file_location("importweb", ROOT / "tools" / "import-web.py")
importweb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(importweb)


def load_targets():
    """slug -> target, from every design/import_web_targets*.json"""
    out = {}
    for f in sorted((ROOT / "design").glob("import_web_targets*.json")):
        try:
            d = json.load(io.open(f, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict) and isinstance(d.get("targets"), list):
            d = d["targets"]                      # import-web.py's files: {"targets": [{key, url, ...}, ...]}
        items = d.items() if isinstance(d, dict) else ((t.get("key") or t.get("slug"), t) for t in d)
        for k, t in items:
            if isinstance(t, dict):
                out[k] = t
                if t.get("slug"):
                    out[t["slug"]] = t
    return out


def posts():
    for f in sorted(glob.glob(str(ROOT / "_posts" / "*.md"))):
        t = io.open(f, encoding="utf-8", errors="replace").read()
        m = FRONT.match(t)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        yield Path(f), fm, t[m.end():]


def source_url(fm):
    src = fm.get("source")
    url = fm.get("source_url") or (src.get("url") if isinstance(src, dict) else None) or fm.get("original_url")
    return str(url) if url and str(url).startswith("http") else None


def squash(s):
    return re.sub(r"[\s\u3000]+", "", s)


def post_text(fm, body):
    """the original-language text the post holds (squashed, one string), and its picture count"""
    rows = fm.get("parallel_items") or fm.get("translation_segments") or []
    parts = []
    images = 0
    for r in rows:
        if not isinstance(r, dict):
            continue
        if r.get("type") == "image" or r.get("image"):
            images += 1
        o = r.get("original")
        if isinstance(o, str):
            parts.append(squash(o))
    if not parts:
        # an older post: the body's blockquotes / the whole body
        parts.append(squash(re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)))
        images += len(re.findall(r"!\[[^\]]*\]\(", body))
    return "".join(parts), images


SPEAKER = re.compile(r"^[^:：」』]{1,40}[:：]")
CHROME = re.compile(r"注目度|PostedBy|Publishedon|newsletter|Signup|関連記事|会員限定|登録会員|転載・複製|Copyright|©|SHARE|シェア|Tweet|ランキング|おすすめ|PR$", re.I)


def held_has(s, held):
    """is this paragraph in the post? the opening of the paragraph, with any speaker label
    the page writes in front of it taken off, at a couple of offsets"""
    core = SPEAKER.sub("", s, count=1)
    for c in (s, core):
        if len(c) >= 24 and (c[:24] in held or c[6:30] in held or c[14:38] in held):
            return True
    return len(core) < 24 and core in held


def missing_paragraphs(html, target, held):
    """the page's paragraphs of some length (>= 40 chars squashed) that the post lacks -
    the chrome of a page is short lines or repeated boilerplate, the article is the rest"""
    soup = importweb.parse(html)
    importweb.strip_noise(soup)
    box = importweb.find_container(soup, target or {})
    seen = set()
    paras, gone = [], []
    for el in box.find_all(["p", "h2", "h3", "h4", "li", "dd", "dt", "blockquote", "div", "td"]):
        if el.name in ("div", "td") and el.find(["p", "div", "li", "td"]):
            continue
        s = squash(el.get_text(" ", strip=True))
        if len(s) < 40 or s in seen or CHROME.search(s):
            continue
        seen.add(s)
        paras.append(s)
        if not held_has(s, held):
            gone.append(s)
    return paras, gone


def _get(url):
    """the page's bytes: urllib, then curl (some sites answer a browser only), then the
    Wayback Machine; a stub (a consent page, a challenge) counts as not readable"""
    import subprocess
    last = None
    for way in ("urllib", "curl", "wayback"):
        try:
            if way == "urllib":
                raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            elif way == "curl":
                raw = subprocess.run(["curl", "-sL", "--max-time", "60", "-A", UA["User-Agent"], "-H", "Accept-Language: ja,en;q=0.8", url], capture_output=True).stdout
            else:
                raw = urllib.request.urlopen(urllib.request.Request("https://web.archive.org/web/2024id_/" + url, headers=UA), timeout=90).read()
            if len(raw) >= 3000:
                return raw
            last = f"{way}: {len(raw)} bytes"
        except Exception as e:
            last = f"{way}: {str(e)[:60]}"
    raise RuntimeError(last or "no answer")


def fetch(url, key, refetch, target_key=None):
    """the page as bytes (its own charset is left to the parser), cached under audit/"""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")[:80] + ".html")
    if f.exists() and not refetch and f.stat().st_size >= 3000:
        return f.read_bytes(), True
    try:
        raw = _get(url)
    except RuntimeError:
        raw = b""
    own = CACHE.parent / f"{target_key}.html" if target_key else None
    if own and own.exists() and len(raw) < 3000:
        raw = own.read_bytes()
    if len(raw) < 3000:
        raise RuntimeError("no readable copy of the page")
    f.write_bytes(raw)
    time.sleep(0.5)
    return raw, False


def page_text(html, target):
    soup = importweb.parse(html)
    importweb.strip_noise(soup)
    box = importweb.find_container(soup, target or {})
    for el in box.find_all(["figcaption"]):
        el.decompose()
    text = box.get_text(" ", strip=True)
    images = [im for im in box.find_all("img") if not re.search(r"(icon|logo|banner|button|avatar|1x1|pixel|emoji|/ad/|sns|share)", (im.get("data-src") or im.get("src") or "") + " " + " ".join(im.get("class") or []), re.I)]
    images = [im for im in images if int(re.sub(r"\D", "", str(im.get("width") or "999")) or 999) >= 120]
    return len(re.sub(r"\s+", "", text)), len(images)


def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else ""
    refetch = "--refetch" in sys.argv
    targets = load_targets()
    rows = []
    for path, fm, body in posts():
        if only and only not in path.name:
            continue
        if fm.get("archive_type") == "scan_translation":
            continue
        if fm.get("layout") not in ("interview-editorial", "parallel-translation") and fm.get("archive_type") != "interview_translation":
            continue
        url = source_url(fm)
        if not url or "web.archive.org" in url and "id_" not in url and False:
            continue
        if re.search(r"gamefreak\.co\.jp|lineblog\.me|style\.fm", url):
            continue            # the blogs and the column have their own pipelines
        slug = path.stem[11:]
        target_key = next((k for k, t in targets.items() if isinstance(t, dict) and (t.get("url") == url or t.get("slug") == slug)), None)
        target = targets.get(target_key) if target_key else None
        held, pimages = post_text(fm, body)
        pchars = len(held)
        row = {"post": path.name, "url": url, "post_chars": pchars, "post_images": pimages}
        try:
            html, cached = fetch(url, slug, refetch, target_key)
            wchars, wimages = page_text(html, target)
            paras, gone = missing_paragraphs(html, target, held)
            if wchars < 1500 or sum(len(p) for p in paras) < 600:
                raise RuntimeError(f"the fetched copy holds no article ({wchars} chars)")
            row.update(page_chars=wchars, page_images=wimages, share=round(pchars / wchars, 2) if wchars else None, cached=cached,
                       paragraphs=len(paras), missing=len(gone), missing_chars=sum(len(g) for g in gone),
                       covered=round(1 - sum(len(g) for g in gone) / max(1, sum(len(p) for p in paras)), 2),
                       missing_sample=[g[:80] for g in gone[:6]])
        except Exception as e:
            row["error"] = str(e)[:160]
        rows.append(row)
        flag = row.get("covered") is not None and row["covered"] < SHORT
        tag = "  !!" if flag else "    "
        print(f"{tag} cover {row.get('covered', '  - ')!s:>5} miss {row.get('missing', 0):3d}/{row.get('paragraphs', 0):<3d} paras  text {pchars:6d}/{row.get('page_chars', 0):<6d} pics {pimages:3d}/{row.get('page_images', 0):<3d} {path.name[:66]}" + (f"  [{row['error']}]" if row.get("error") else ""))
        if "--detail" in sys.argv:
            for g in row.get("missing_sample", []):
                print("         -", g)
    OUT.parent.mkdir(exist_ok=True)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(json.dumps(rows, ensure_ascii=False, indent=1))
    short = [r for r in rows if r.get("covered") is not None and r["covered"] < SHORT]
    errors = [r for r in rows if r.get("error")]
    print(f"\n{len(rows)} posts checked, {len(short)} hold under {int(SHORT * 100)}% of their page's paragraphs, {len(errors)} pages could not be read -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
