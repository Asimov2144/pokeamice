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
    #  这一栏铺在上千页上，抽查三篇看不出问题：整站扫一遍，看关系连的页面在不在、
    #  观察指的那一段在不在（小标题的 id 是 section-N，图片没有 id，钉错了就是个跳不到的锚点）
    lore_pages = 0
    dead_links: list = []
    bad_anchors: list = []
    facet_rows = 0
    lore_re = re.compile(r'<section class="lore".*?</section>', re.S)
    href_re = re.compile(r'href="(/[^"#?]*)"')
    anchor_re = re.compile(r'href="#segment-(\d+)"')
    for path in site.glob("**/index.html"):
        text = io.open(path, encoding="utf-8", errors="replace").read()
        found = lore_re.search(text)
        if not found:
            continue
        lore_pages += 1
        column = found.group(0)
        facet_rows += column.count('class="lore__row"')
        here = os.path.basename(os.path.dirname(path))
        for href in href_re.findall(column):
            if not exists(site, href):
                dead_links.append(here + " -> " + urllib.parse.unquote(href))
        for n in anchor_re.findall(column):
            if f'id="segment-{n}"' not in text:
                bad_anchors.append(f"{here} §{n}")
    check(lore_pages > 0, f"lore: the column is on {lore_pages} pages, {facet_rows} facet rows")
    check(not dead_links, f"lore: {len(dead_links)} links point at a page that was not built {dead_links[:3]}")
    check(not bad_anchors, f"lore: {len(bad_anchors)} observations point at a paragraph the page does not have {bad_anchors[:3]}")

    css = io.open(next(iter(site.glob("assets/css/main.css"))), encoding="utf-8", errors="replace").read()
    check(".crumbs__list" in css and ".tip__card" in css and ".lore__facets" in css,
          "the stylesheet carries the trail, the tip and the column")

    # ---- GF 员工博客：早期版本补回的署名 / 分类 / 修正（tools/gamefreak_staff_history.py）----
    staff_pages = sorted(site.glob("gamefreak-staff/entry-*/index.html"))
    bylines = avatars = mojibake = 0
    missing_avatar = []
    for path in staff_pages:
        page = read(path)
        by = page.select_one(".gf-legacy-byline")
        if by:
            bylines += 1
            for img in by.select("img"):
                avatars += 1
                if not exists(site, img.get("src") or ""):
                    missing_avatar.append(img.get("src"))
        body = page.select_one(".gf-legacy-post__body")
        if body and re.search(r"縲|竏|鰀|怩|怐|怺", body.get_text()):
            mojibake += 1
    check(len(staff_pages) >= 209, f"staff blog: {len(staff_pages)} entries built")
    check(bylines >= 190, f"staff blog: {bylines} entries carry the restored byline ({avatars} avatars)")
    check(not missing_avatar, f"staff blog: every avatar resolves ({missing_avatar[:3]})")
    check(mojibake == 0, f"staff blog: no 2013 mojibake left in the entries ({mojibake} pages)")
    staff_home = read(site / "gamefreak-staff" / "index.html")
    writers = staff_home.select(".gf-legacy-writers li") if staff_home else []
    headers = staff_home.select(".gf-legacy-early img") if staff_home else []
    check(len(writers) >= 50 and len(headers) == 3,
          f"staff blog: the writer list ({len(writers)}) and the three early headers ({len(headers)}) are on the front page")
    check(all(exists(site, img.get("src") or "") for img in headers), "staff blog: the early headers resolve")

    # ---- the timeline ---------------------------------------------------
    tl_index = read(site / "timeline" / "index.html")
    cols = tl_index.select("a.tl-col") if tl_index else []
    check(len(cols) >= 25, f"timeline: the overview draws {len(cols)} year columns")
    check(all(exists(site, a.get("href") or "") for a in cols), "timeline: every column links to a built year page")
    picks = tl_index.select("a.tl-pick") if tl_index else []
    check(len(picks) >= 60 and all(exists(site, a.get("href") or "") for a in picks),
          f"timeline: {len(picks)} picks, every one resolves")
    check(len(tl_index.select("section.tl-era")) >= 5 if tl_index else False, "timeline: the eras are there")
    y2010 = read(site / "timeline" / "2010" / "index.html")
    if y2010:
        check(len(y2010.select(".tl-item")) >= 40 and len(y2010.select("details.tl-stream")) >= 1,
              f"timeline: 2010 has {len(y2010.select('.tl-item'))} cards and {len(y2010.select('details.tl-stream'))} folded blogs")
        check([t for t, _ in trail(y2010)][:2] == ["首页", "时间线"], f"timeline: the year sits under 时间线 {trail(y2010)[:3]}")
        check(all(exists(site, a.get("href") or "") for a in y2010.select(".tl-strip a, .tl-head__step, .tl-game")),
              "timeline: the year strip, the neighbours and the game chips resolve")
    else:
        check(False, "timeline: 2010 is built")

    # ---- the two cross-cutting hubs (tools/build-hubs.py) ---------------------
    ov = read(site / "overseas" / "index.html")
    if ov:
        cards = ov.select("a.tl-pick[data-hub-item]")
        check(len(cards) >= 55 and all(exists(site, a.get("href") or "") for a in cards),
              f"overseas: {len(cards)} interviews, every one resolves")
        check(len(ov.select("section.tl-era")) >= 4 and len(ov.select("[data-hub-bar] button")) >= 5,
              f"overseas: {len(ov.select('section.tl-era'))} regions and {len(ov.select('[data-hub-bar] button'))} outlet buttons")
        check([t for t, _ in trail(ov)][:2] == ["首页", "海外媒体专访"], f"overseas: the crumbs are 首页 › 海外媒体专访 {trail(ov)[:3]}")
        check(all(exists(site, a.get("href") or "") for a in ov.select(".hub-who a")), "overseas: the people and game chips resolve")
    else:
        check(False, "overseas: the page is built")
    gm = read(site / "games" / "index.html")
    if gm:
        games = gm.select("article.hub-game")
        picks = gm.select(".hub-game__picks a")
        check(len(games) >= 35 and len(gm.select("section.tl-era")) >= 10, f"games: {len(games)} games in {len(gm.select('section.tl-era'))} groups")
        check(len(picks) >= 90 and all(exists(site, a.get("href") or "") for a in picks), f"games: {len(picks)} picks, every one resolves")
        anchors = {g.get("id") for g in games}
        check(all((a.get("href") or "")[1:] in anchors for a in gm.select(".hub-top a")), "games: the 'most talked about' chips point at cards on the page")
        check(all(exists(site, a.get("href") or "") for a in gm.select(".hub-game__foot a[href*='/credits/']")), "games: the staff-roll links resolve")
    else:
        check(False, "games: the page is built")
    home = read(site / "index.html")
    if home:
        hrefs = {a.get("href") for a in home.select("a.front__tile")}
        check({"/overseas/", "/games/"} <= hrefs, "home: the shelf has the 海外媒体专访 and 按游戏读 tiles")

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
