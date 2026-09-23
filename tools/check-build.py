#!/usr/bin/env python3
"""What a built site must contain before the push — the navigation layer and the article index.

    python tools/check-build.py <site dir>          # e.g. a git-archive export's _site

Prints one line per check and exits non-zero if any failed. Meant to run against a build
made from the git index, not from the working tree (see the memory note
verify-against-git-index-not-disk): a local build being green says nothing about what a
push would deploy.

This replaces a scratchpad script whose checks were lost when the scratchpad was cleared;
it lives in the repo now so the net survives. It covers what the navigation and the lore
work added - the trail on every kind of page, the tooltip data, the 「本篇提到」 column -
plus the two things that break silently: a crumb pointing at a page that was never built,
and a paragraph anchor that does not exist on the page it claims.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path

from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ok = True


def check(cond, msg: str) -> None:
    global ok
    print(("  ok  " if cond else "  !!  ") + msg)
    ok = ok and bool(cond)


def read(path: Path) -> BeautifulSoup | None:
    return BeautifulSoup(io.open(path, encoding="utf-8", errors="replace").read(), "html.parser") if path.exists() else None


def find_page(site: Path, tail: str) -> Path | None:
    """一篇文章的产物：URL 里带分类路径，按目录名找"""
    hits = [p for p in site.glob("**/index.html") if p.parent.name == tail]
    return hits[0] if hits else None


def exists(site: Path, href: str) -> bool:
    if not href or href.startswith(("http://", "https://", "#", "mailto:")):
        return True
    path = urllib.parse.unquote(href.split("#")[0].split("?")[0])
    if path.startswith("/search/"):
        path = "/search/"
    full = site / path.lstrip("/")
    return full.exists() or (site / (path.strip("/") + "/index.html")).exists()


def trail(page: BeautifulSoup) -> list:
    nav = page.select_one("nav.crumbs") if page else None
    return [(li.get_text(" ", strip=True), (li.find("a") or {}).get("href")) for li in nav.select("li")] if nav else []


def main() -> int:
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    if not (site / "index.html").exists():
        print(f"no build at {site}")
        return 2

    # ---- the trail ------------------------------------------------------
    home = read(site / "index.html")
    check(home.select_one("nav.crumbs") is None, "crumbs: none on the home page")

    pages = {
        "interview": find_page(site, "interview-wedge-ishihara-pokemon-disney"),
        "scan": find_page(site, "scan-ndream-2011-01-bw-design-secrets"),
        "blog": site / "gamefreak-director" / "entry-001" / "index.html",
        "person": site / "people" / "ishihara-tsunekazu" / "index.html",
        "credits": site / "credits" / "red-green" / "index.html",
        "category": site / "categories" / "访谈翻译" / "index.html",
        "timeline": site / "timeline" / "2013" / "index.html",
        "library": site / "keys" / "index.html",
        "search": site / "search" / "index.html",
    }
    for name, path in pages.items():
        page = read(path) if path else None
        rows = trail(page)
        dead = [h for _, h in rows if h and not exists(site, h)]
        check(page is not None and len(rows) >= 2 and rows[0][0] == "首页" and not dead,
              f"crumbs: {name} -> {[n for n, _ in rows]} dead={dead}")

    article = read(pages["interview"])
    ld = [s for s in article.select('script[type="application/ld+json"]') if "BreadcrumbList" in s.get_text()]
    positions = [x["position"] for x in json.loads(ld[0].get_text())["itemListElement"]] if ld else []
    check(positions == list(range(1, len(positions) + 1)) and len(positions) >= 3,
          f"crumbs: BreadcrumbList numbered 1..{len(positions)}")

    # ---- the tooltips ---------------------------------------------------
    tips_path = site / "assets" / "js" / "tips.json"
    tips = json.load(io.open(tips_path, encoding="utf-8")) if tips_path.exists() else {}
    check(len(tips.get("people", {})) >= 700 and len(tips.get("works", {})) >= 90,
          f"tips: {len(tips.get('people', {}))} people, {len(tips.get('works', {}))} works in tips.json")
    check(all("[" not in v.get("s", "") for v in tips.get("people", {}).values()),
          "tips: no citation marks left in the summaries")
    check((site / "assets" / "js" / "tip.js").exists()
          and all("assets/js/tip.js" in io.open(p, encoding="utf-8", errors="replace").read()
                  for p in (site / "index.html", pages["person"], pages["interview"])),
          "tips: tip.js loaded on the home page, a person page and an article")
    check(len(article.select("[data-tip]")) >= 6, f"tips: the reader carries {len(article.select('[data-tip]'))} hints")

    # ---- 本篇提到 --------------------------------------------------------
    lore_pages = [p for p in (pages["interview"], pages["scan"], pages["blog"]) if p]
    with_lore = [read(p) for p in lore_pages]
    with_lore = [d for d in with_lore if d and d.select_one("section.lore")]
    check(with_lore, f"lore: the column is on {len(with_lore)} of the sample articles")
    for page, path in zip(with_lore, lore_pages):
        sec = page.select_one("section.lore")
        bad_anchor = [a.get_text(strip=True) for a in sec.select(".lore__seg")
                      if not page.select_one("#segment-" + a.get_text(strip=True).lstrip("§"))]
        dead = [a["href"] for a in sec.select("a[href^='/']") if not exists(site, a["href"])]
        rows = [r.select_one("dt").get_text(" ", strip=True).split()[0] for r in sec.select(".lore__row")]
        check(not bad_anchor and not dead and rows,
              f"lore: {os.path.basename(os.path.dirname(path))} rows {rows}, bad anchors {bad_anchor}, dead {dead}")

    css = io.open(next(iter(site.glob("assets/css/main.css"))), encoding="utf-8", errors="replace").read()
    check(".crumbs__list" in css and ".tip__card" in css and ".lore__facets" in css,
          "the stylesheet carries the trail, the tip and the column")

    # ---- nothing leaked -------------------------------------------------
    leaks = []
    code = re.compile(r"<(code|pre)\b.*?</\1>", re.S | re.I)
    for path in list(site.glob("**/index.html"))[:4000]:
        text = io.open(path, encoding="utf-8", errors="replace").read()
        # 文档页会把 Liquid 写在 <code> 里当例子（{% raw %} 包着），那不算漏渲染
        text = code.sub(" ", text)
        if "Liquid Exception" in text or "{% include" in text or "{{ page." in text:
            leaks.append(str(path.relative_to(site)))
    check(not leaks, f"pages: no unrendered Liquid left ({leaks[:3]})")

    print("ALL OK" if ok else "PROBLEMS")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
