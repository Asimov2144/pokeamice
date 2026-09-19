"""Which web-sourced posts came from a page that continues on another page.

GlitterBerri's article was sixteen pages and the post had one. This looks at the
cached copy of every post's source page (data/cache_web/audit/, written by
audit-web-imports.py; data/cache_web/ for the importer's own copies) for the marks
of a serial: a rel=next link, a pager, "次のページ" / "Page 1 of 3" / "Pages: 1 2 3",
a "/2/" or "?page=2" link to the same article. For each such post it says how many
pages the page announces and whether the post's own front matter names the
continuation pages (a target with `pages`).

    python tools/audit-pagination.py            # every post with a web source
    python tools/audit-pagination.py --detail   # and the links it found

Second part: posts whose `original` column is thin - rows with a translation but
no original (the text was never brought over) - which is the other way an old
import falls short of its page.
"""
import glob
import io
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import yaml
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache_web" / "audit"
CACHE2 = ROOT / "data" / "cache_web"
FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)
NEXT_TEXT = re.compile(r"^(?:次のページ|次へ|次ページ|次の記事|NEXT|Next|Next Page|Next page|続きを読む|続きはこちら|つづき|続き|→|»|>)\s*(?:へ|»|→|>|›)?$")
PAGE_OF = re.compile(r"Page\s*\d+\s*(?:of|/)\s*(\d+)|Pages?:\s*1\s+2\s+3|(\d+)\s*/\s*(\d+)\s*ページ|全(\d+)ページ|(\d+)ページ目", re.I)
PAGER_CLASS = re.compile(r"(?:^|[-_ ])(pager|pagination|paging|page-nav|pagenav|page_nav|pageNav|nextpage|next-page|page-links|pagelink|page-number|pagenation)(?:$|[-_ ])", re.I)


def wayback_strip(u):
    return re.sub(r"^https?://web\.archive\.org/web/\d+[a-z_]*/", "", u or "")


def same_article_page(href, base):
    """A link to page N of the article at `base`: same path with /N/, ?page=N, _N.html, /page/N."""
    h, b = wayback_strip(href), wayback_strip(base)
    if not h.startswith("http"):
        h = urljoin(b, h)
    hp, bp = urlparse(h), urlparse(b)
    if hp.netloc != bp.netloc:
        return None
    bpath = bp.path.rstrip("/")
    bases = [bpath]
    if re.search(r"/\d+$", bpath):                 # the source is itself page N of the article
        bases.append(bpath.rsplit("/", 1)[0])
    if re.search(r"/index[-_]?\d*\.html?$", bpath):
        bases.append(bpath.rsplit("/", 1)[0])
    for b0 in bases:
        for pat in (r"^" + re.escape(b0) + r"/(\d+)/?$", r"^" + re.escape(re.sub(r"\.html?$", "", b0)) + r"[_-](\d+)\.html?$",
                    r"^" + re.escape(b0) + r"/page/(\d+)/?$", r"^" + re.escape(b0) + r"/index[-_](\d+)\.html?$"):
            m = re.match(pat, hp.path.rstrip("/"))
            # under the parent of a numbered path, a small number is a page; a large one is another article
            if m and (b0 == bpath or int(m.group(1)) <= 40):
                return int(m.group(1))
    if hp.path.rstrip("/") in bases or hp.path == bp.path:
        m = re.search(r"(?:^|[?&])(?:page|p|pg|pn|paged|pageindex)=(\d+)", hp.query, re.I)
        if m:
            return int(m.group(1))
    return None


def cache_file(stem, url):
    key = stem[11:] if re.match(r"^\d{4}-\d{2}-\d{2}-", stem) else stem
    f = CACHE / (re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")[:80] + ".html")
    if f.exists():
        return f
    # the importer's own copy, when the post came from a target
    for t in TARGETS.values():
        if t.get("slug") == stem or (t.get("key") and stem.endswith(t["key"])):
            g = CACHE2 / f"{t['key']}.html"
            if g.exists():
                return g
    return None


def load_targets():
    out = {}
    for f in sorted((ROOT / "design").glob("import_web_targets*.json")):
        try:
            d = json.load(io.open(f, encoding="utf-8"))
        except Exception:
            continue
        for t in (d.get("targets") if isinstance(d, dict) else d) or []:
            if isinstance(t, dict) and t.get("key"):
                out[t["key"]] = t
    return out


TARGETS = load_targets()


def target_of(stem):
    for t in TARGETS.values():
        if t.get("slug") == stem or stem.endswith("-" + t["key"]):
            return t
    return None


def pagination(html, url):
    """(pages announced, evidence) from the page's own links and text."""
    soup = BeautifulSoup(html, "html.parser")
    for el in soup.find_all(["script", "style", "noscript"]):
        el.decompose()
    for el in soup.find_all(id=re.compile(r"^wm-ipp|^donato|^playback")):
        el.decompose()
    ev, pages = [], set()
    ln = soup.find("link", rel=lambda v: v and "next" in v)
    if ln and ln.get("href"):
        n = same_article_page(ln["href"], url)
        ev.append(f"rel=next {wayback_strip(ln['href'])[-60:]}")
        if n:
            pages.add(n)
    for a in soup.find_all("a", href=True):
        n = same_article_page(a["href"], url)
        txt = a.get_text(" ", strip=True)
        if n:
            pages.add(n)
            if len(ev) < 6:
                ev.append(f"link p{n} «{txt[:20]}»")
        elif NEXT_TEXT.match(txt) and a.get("rel") and "next" in a.get("rel"):
            ev.append(f"a rel=next «{txt}»")
    for el in soup.find_all(class_=PAGER_CLASS) + soup.find_all(id=PAGER_CLASS):
        nums = [int(x) for x in re.findall(r"\b(\d{1,2})\b", el.get_text(" ", strip=True))]
        nums = [x for x in nums if 1 <= x <= 40]
        if len(nums) >= 2:
            pages.update(nums)
            ev.append(f"pager «{el.get_text(' ', strip=True)[:40]}»")
            break
    body = soup.get_text(" ", strip=True)
    m = PAGE_OF.search(body)
    if m:
        ev.append("text «" + m.group(0)[:30] + "»")
        for g in m.groups():
            if g and g.isdigit():
                pages.add(int(g))
    return (max(pages) if pages else 0), ev


def main():
    detail = "--detail" in sys.argv
    serial, thin = [], []
    n_posts = n_cached = 0
    for f in sorted(glob.glob(str(ROOT / "_posts" / "*.md"))):
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
        stem = Path(f).stem
        n_posts += 1
        items = fm.get("parallel_items") or fm.get("translation_segments") or []
        texts = [x for x in items if isinstance(x, dict) and x.get("type") not in ("image",)]
        empty = [x for x in texts if not str(x.get("original") or "").strip() and str(x.get("translation") or "").strip()]
        if texts and len(empty) >= max(3, len(texts) * 0.15):
            thin.append((stem, len(empty), len(texts)))
        cf = cache_file(stem, str(url))
        if not cf:
            continue
        n_cached += 1
        pages, ev = pagination(io.open(cf, encoding="utf-8", errors="replace").read(), str(url))
        if pages >= 2 or any(e.startswith(("rel=next", "a rel=next")) for e in ev):
            tg = target_of(stem)
            known = len(tg.get("pages") or []) + 1 if tg else 0
            chars = sum(len(str(x.get("original") or "")) for x in texts)
            serial.append((stem, pages, known, chars, ev))
    print(f"{n_posts} posts with a web source, {n_cached} with a cached page\n")
    print(f"== {len(serial)} pages that announce more pages (pages seen / pages the import took / chars in the post)")
    for stem, pages, known, chars, ev in sorted(serial, key=lambda r: (-(r[1] - r[2]), r[0])):
        flag = "  <-- short" if pages > max(known, 1) else ""
        print(f"  {pages:2d} / {known:2d} / {chars:6d}  {stem[:70]}{flag}")
        if detail:
            for e in ev[:6]:
                print("        " + e)
    print(f"\n== {len(thin)} posts whose original column is thin (rows with a translation but no original)")
    for stem, e, n in sorted(thin, key=lambda r: -r[1] / r[2]):
        print(f"  {e:3d} / {n:3d}  {stem[:70]}")


if __name__ == "__main__":
    main()
