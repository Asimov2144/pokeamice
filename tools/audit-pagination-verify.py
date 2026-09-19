"""For the posts audit-pagination.py flags: is the continuation actually missing?

Each later page of the article is fetched (cached under data/cache_web/audit/<stem>_pN.html,
through Wayback when the post's source is a Wayback copy), its paragraphs cut out the way
import-web.py cuts them, and held against the post's `original` column. A page whose
paragraphs are mostly absent from the post is a page the import never took.

    python tools/audit-pagination-verify.py                 # the flagged posts
    python tools/audit-pagination-verify.py --only dengeki  # by file name
"""
import glob
import importlib.util
import io
import re
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

import yaml
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache_web" / "audit"
FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "ja,en;q=0.8,zh;q=0.6"}

_spec = importlib.util.spec_from_file_location("importweb", ROOT / "tools" / "import-web.py")
iw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(iw)
_spec = importlib.util.spec_from_file_location("ap", ROOT / "tools" / "audit-pagination.py")
ap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ap)

# the chapter list of an Iwata Asks page is not a pager; a site menu is not either
SKIP = re.compile(r"iwata-asks|cit-kensaku|corocoro-coco")


def norm(s):
    return re.sub(r"[\s　]+", "", s).replace("，", ",").replace("（", "(").replace("）", ")").lower()


def probe(p):
    """The piece of a paragraph looked for in the post: past any speaker prefix, forty characters in."""
    p = re.sub(r"^[^：:]{1,30}[：:]\s*", "", p.strip())
    n = norm(p)
    return n[8:48] if len(n) > 56 else n[:40]


def found(p, post):
    """Whether a page paragraph is in the post: its probe, or, past a speaker written with a
    space (NewsPicks' 今村 …), any of three 24-character windows."""
    if probe(p) in post:
        return True
    n = norm(re.sub(r"^[^\s　]{1,12}[\s　]", "", p.strip()))
    if len(n) < 30:
        return n in post
    wins = [n[:24], n[len(n) // 2 - 12:len(n) // 2 + 12], n[-24:]]
    return sum(1 for w in wins if w in post) >= 2


def fidelity(html, target, post):
    """(share of the page's text found in the post, paragraphs, chars, missing paragraphs)."""
    paras = paragraphs(html, target)
    chars = sum(len(p) for p in paras)
    miss = [p for p in paras if not found(p, post)]
    share = 1 - sum(len(p) for p in miss) / chars if chars else 0
    return share, paras, chars, miss


def fetch(url, dest):
    if dest.exists() and dest.stat().st_size > 1000:
        return dest.read_text(encoding="utf-8", errors="replace")
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={**UA, "Accept-Encoding": "gzip"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    import gzip
                    data = gzip.decompress(data)
            soup = BeautifulSoup(data, "html.parser")
            text = str(soup)
            dest.write_text(text, encoding="utf-8", newline="\n")
            time.sleep(1)
            return text
        except Exception as exc:
            err = exc
            time.sleep(5 * (attempt + 1))
    print(f"      fetch failed: {url[-70:]}: {err}")
    return None


def page_links(html, url):
    soup = BeautifulSoup(html, "html.parser")
    out = {}
    for a in soup.find_all("a", href=True):
        n = ap.same_article_page(a["href"], url)
        if n and n >= 2:
            href = a["href"]
            if not href.startswith("http"):
                href = urljoin(url, href)
            out.setdefault(n, href)
    return out


def paragraphs(html, target):
    soup = iw.parse(html)
    iw.strip_noise(soup)
    container = iw.find_container(soup, target or {})
    blocks = iw.extract_blocks(container, join_br=bool((target or {}).get("join_br")))
    return [b["x"] for b in blocks if b["t"] == "text" and len(b["x"]) >= 20]


def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    everything = "--all" in sys.argv
    rows = []
    for f in sorted(glob.glob(str(ROOT / "_posts" / "*.md"))):
        stem = Path(f).stem
        if only and only not in stem:
            continue
        if SKIP.search(stem):
            continue
        t = io.open(f, encoding="utf-8", errors="replace").read()
        m = FRONT.match(t)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        src = fm.get("source")
        url = fm.get("source_url") or (src.get("url") if isinstance(src, dict) else None) or fm.get("original_link") or fm.get("original_url")
        if not url or not str(url).startswith("http"):
            continue
        url = str(url)
        cf = ap.cache_file(stem, url)
        if not cf:
            continue
        html = io.open(cf, encoding="utf-8", errors="replace").read()
        items = fm.get("parallel_items") or fm.get("translation_segments") or []
        post = norm(" ".join(str(x.get("original") or "") + " " + str(x.get("caption") or "") for x in items if isinstance(x, dict)))
        target = ap.target_of(stem)
        if everything:
            # the source page itself: how much of its text the post carries, and the reverse
            share, paras, chars, miss = fidelity(html, target, post)
            if chars >= 400 and not re.search(r"[�]", html[:20000]):
                rows.append((share, len(post), chars, stem, miss))
            continue
        pages, ev = ap.pagination(html, url)
        links = page_links(html, url)
        if not links:
            continue
        print(f"== {stem}  ({len(links) + 1} pages; post {len(post)} chars)")
        for n in sorted(links):
            href = links[n]
            dest = CACHE / f"{stem[11:][:70]}_p{n}.html"
            ph = fetch(href, dest)
            if ph is None:
                continue
            paras = paragraphs(ph, target)
            if not paras:
                print(f"   p{n}: no paragraphs read ({href[-60:]})")
                continue
            share, paras, chars, miss = fidelity(ph, target, post)
            state = "in the post" if share >= 0.7 else ("PARTLY missing" if share >= 0.3 else "MISSING")
            print(f"   p{n}: {len(paras)} paragraphs / {chars} chars, {share:.0%} in the post -> {state}   {href[-70:]}")
            if share < 0.7:
                for p in miss[:2]:
                    print("        · " + p[:80])


    if everything:
        print(f"{len(rows)} posts held against their own page (garbled caches and pages under 400 chars left out)"); print()
        for share, pl, chars, stem, miss in sorted(rows):
            if share >= 0.85:
                continue
            kind = "post much shorter" if pl < chars * 0.7 else "wording differs (rewritten original?)"
            print(f"  {share:4.0%}  post {pl:6d} / page {chars:6d}  {stem[:66]}   {kind}")
            for p in miss[:2]:
                print("           · " + p[:90])
        print(); print(f"{sum(1 for r in rows if r[0] >= 0.85)} at 85% or better, {sum(1 for r in rows if 0.6 <= r[0] < 0.85)} between 60% and 85%, {sum(1 for r in rows if r[0] < 0.6)} under 60%")


if __name__ == "__main__":
    main()
