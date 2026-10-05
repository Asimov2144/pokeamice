"""The numbers and the picks the timeline pages draw from.

    python tools/build-timeline.py

Reads the tracked posts' front matter (git ls-files - a post that is not committed is not on
the site, so it is not on the timeline), the eras and the games with a staff roll
(_data/credits_eras.yml, credits_games.yml), the version colours and icons (works.yml) and the
people registry, and writes

    _data/timeline.yml                      the year-by-year tally, the eras, the picks
    _pages/generated/timeline/<year>.md     one stub page per year that has entries; the page
                                            itself is _includes/timeline-year.html

_pages/timeline.md (the overview) is hand-written Liquid over _data/timeline.yml. The Ruby
resource-index builder used to write both pages as bare lists; it no longer does.

What counts as what: a *document* is a translated interview, a magazine scan, an official
topic (corporate.pokemon.co.jp) or an article; the Game Freak blogs - the director's column,
Masuda's LINE blog, the staff blog, Sugimori's - are a *stream*: hundreds of short entries
that would bury the documents, so they are tallied apart and listed folded on the year page.
"""
import collections
import importlib.util
import io
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
L = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
CUT = re.compile(r"^(parallel_items|translation_segments):", re.M)

spec = importlib.util.spec_from_file_location("xp", ROOT / "tools" / "export-docs-archive.py")
xp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xp)

STREAMS = {  # archive_type -> (key, name, index page)
    "gamefreak_director_column": ("director", "部长专栏", "/gamefreak-director/"),
    "gamefreak_masuda_lineblog": ("line", "增田顺一 LINE 博客", ""),
    "gamefreak_legacy_blog": ("staff", "员工博客《晴时偶有阴》", "/gamefreak-staff/"),
}
DOC_KINDS = ("interview", "scan", "topic", "article")


def git_files():
    """The posts of the last commit: what is on the site. A working copy another session is in the middle of editing is not read."""
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", "-z", "HEAD", "--", "_posts"], cwd=ROOT, capture_output=True).stdout
    return [f for f in out.decode("utf-8").split(chr(0)) if f.endswith(".md")]


_BLOBS = {}


def load_head(files):
    proc = subprocess.Popen(["git", "cat-file", "--batch"], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for f in files:
        proc.stdin.write((f"HEAD:{f}" + chr(10)).encode("utf-8"))
        proc.stdin.flush()
        size = int(proc.stdout.readline().split()[2])
        _BLOBS[f] = proc.stdout.read(size).decode("utf-8", "replace")
        proc.stdout.read(1)
    proc.stdin.close()
    proc.wait()


def read_post(rel, full=False):
    text = _BLOBS[rel]
    text = text.replace("\r\r\n", "\n").replace("\r\n", "\n")
    m = re.match(r"﻿?---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    head = m.group(1)
    if not full:
        cut = CUT.search(head)
        if cut:
            head = head[:cut.start()]
    try:
        return yaml.load(head, Loader=L) or {}
    except Exception:
        return None


def plain(value, limit=96):
    text = re.sub(r"<[^>]+>", "", str(value or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[:limit].rstrip("，、；：,;: ") + "…"


def clean_title(value, limit=60):
    """A title without the [访谈翻译] / 【…】 tags in front of it."""
    text = plain(value, 300)
    text = re.sub(r"^(?:\s*[\[［【][^\]］】]{1,14}[\]］】])+\s*", "", text)
    return text if len(text) <= limit else text[:limit].rstrip("，、；：,;: ") + "…"


def kind_of(fm):
    at = fm.get("archive_type") or ""
    cats = [str(c) for c in (fm.get("categories") or [])]
    if at in STREAMS:
        return "stream"
    if at == "scan_translation":
        return "scan"
    if "专题报道" in cats:
        return "topic"
    if fm.get("layout") in ("interview-editorial", "parallel-translation") or at.startswith("interview") or at == "media_feature":
        return "interview"
    return "article"


def cover_of(fm):
    """The card's picture by the rule of entry-card.html: image, featured_image, a scan's first plate, a web interview's first picture."""
    pic = fm.get("image") or fm.get("featured_image") or ""
    if not pic:
        for seg in fm.get("translation_segments") or []:
            if isinstance(seg, dict) and seg.get("type") == "image" and (seg.get("image") or seg.get("src")):
                return seg.get("image") or seg.get("src")
        for row in fm.get("parallel_items") or []:
            if isinstance(row, dict) and row.get("type") == "image" and (row.get("image") or row.get("src")):
                return row.get("image") or row.get("src")
    return pic


def main():
    eras = yaml.safe_load(io.open(ROOT / "_data" / "credits_eras.yml", encoding="utf-8"))
    games = yaml.safe_load(io.open(ROOT / "_data" / "credits_games.yml", encoding="utf-8"))
    works = {w["name"]: w for w in yaml.safe_load(io.open(ROOT / "_data" / "works.yml", encoding="utf-8"))}
    people = yaml.safe_load(io.open(ROOT / "_data" / "people.yml", encoding="utf-8"))
    slug_of = {p["name"]: p["slug"] for p in people if p.get("slug") and p.get("kind") not in ("character", "figure")}
    covers = yaml.load(io.open(ROOT / "_data" / "covers.yml", encoding="utf-8").read(), Loader=L) or {}

    posts = []
    files = git_files()
    load_head(files)
    for rel in files:
        fm = read_post(rel)
        if fm is None or fm.get("date") is None or fm.get("search") is False and fm.get("archive_type") not in STREAMS:
            continue
        stem = Path(rel).name[:-3]
        date = str(fm["date"])[:10]
        kind = kind_of(fm)
        ent = fm.get("entities") or {}
        posts.append({
            "rel": rel, "stem": stem, "id": re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem), "fm": fm, "date": date, "year": int(date[:4]),
            "kind": kind, "stream": STREAMS.get(fm.get("archive_type"), ("", "", ""))[0],
            "people": [p for p in (ent.get("people") or []) if isinstance(p, str)],
            "works": [w for w in (ent.get("works") or []) if isinstance(w, str)],
        })
    print(len(posts), "tracked posts on the timeline")

    def work_chip(name):
        w = works.get(name) or {}
        chip = {"name": name}
        for k in ("icon", "icon2", "color", "color2"):
            if w.get(k):
                chip[k] = w[k]
        return chip

    def game_icons(g):
        """a staff-roll game's icon: its work's, or the one credits_games.yml carries for a game works.yml lacks"""
        if g.get("work"):
            return {k: v for k, v in work_chip(g["work"]).items() if k != "name"}
        return {k: g[k] for k in ("icon", "icon2") if g.get(k)}

    by_year = collections.defaultdict(list)
    for p in posts:
        by_year[p["year"]].append(p)

    years = []
    for year in range(min(by_year), max(by_year) + 1):
        ps = by_year.get(year, [])
        docs = [p for p in ps if p["kind"] != "stream"]
        kinds = {k: sum(1 for p in docs if p["kind"] == k) for k in DOC_KINDS}
        stream = {}
        for p in ps:
            if p["kind"] == "stream":
                stream[p["stream"]] = stream.get(p["stream"], 0) + 1
        pc = collections.Counter(n for p in docs for n in set(p["people"]) if n in slug_of)
        wc = collections.Counter(n for p in docs for n in set(p["works"]))
        # the picks: a document with a picture, from a named source, with people in it; not three of one kind
        def series_key(fm):
            return re.sub(r"\s+", "", plain(fm.get("publication") or fm.get("display_title") or fm.get("title"), 200))[:11]

        freq = collections.Counter(series_key(p["fm"]) for p in docs)
        scored = []
        for p in docs:
            fm = p["fm"]
            s = (2 if fm.get("image") or fm.get("featured_image") else 0) + (1 if fm.get("publication") else 0) + min(2, len(p["people"])) + (1 if fm.get("summary") else 0)
            s += {"interview": 1, "scan": 1, "topic": 0, "article": 0}[p["kind"]]
            s -= min(3, freq[series_key(fm)] - 1)     # a column of forty entries does not stand for the year
            scored.append((s, p["date"], p))
        scored.sort(key=lambda t: (-t[0], t[1]))
        picks, taken, seen = [], collections.Counter(), set()
        for strict in (True, False):
            for s, d, p in scored:
                if p in picks or len(picks) == 3:
                    continue
                fm = p["fm"]
                # one run of a column or a magazine per year first: the pick shows the year's range, not one series three times
                key = series_key(fm)
                if strict and (key in seen or taken[p["kind"]] >= 2 and len(docs) > 3):
                    continue
                picks.append(p)
                seen.add(key)
                taken[p["kind"]] += 1
        pick_rows = []
        for p in picks:
            fm = read_post(p["rel"], full=True) or p["fm"]
            cover = cover_of(fm)
            row = {
                "title": clean_title(fm.get("display_title") or fm.get("title")),
                "kind": p["kind"],
                "pub": plain(fm.get("publication"), 40),
                "date": p["date"],
                "url": xp.canonical_url(p["fm"], p["id"]).replace(xp.SITE, ""),
            }
            if fm.get("summary") or fm.get("dek"):
                row["blurb"] = plain(fm.get("dek") or fm.get("summary"), 88)
            if cover:
                row["cover"] = cover
                if covers.get(cover):
                    row["cover_size"] = list(covers[cover])
            pick_rows.append(row)
        rel_games = [g for g in games if g.get("year") == year]
        years.append({
            "year": year,
            "docs": len(docs),
            "stream": sum(stream.values()),
            "kinds": kinds,
            "streams": stream,
            "games": [{"slug": g["slug"], "title": g.get("title_zh") or g["title"], "core": bool(g.get("core")), **game_icons(g)} for g in rel_games],
            "people": [{"name": n, "slug": slug_of[n], "n": c} for n, c in pc.most_common(6)],
            "works": [dict(work_chip(n), n=c) for n, c in wc.most_common(5)],
            "picks": pick_rows,
        })

    era_rows = []
    for i, e in enumerate(eras):
        ys = [y for y in years if e["from"] <= y["year"] <= e["to"]]
        core = [g for g in games if e["from"] <= g.get("year", 0) <= e["to"] and g.get("core")]
        pc = collections.Counter()
        for p in posts:
            if e["from"] <= p["year"] <= e["to"] and p["kind"] != "stream":
                pc.update(n for n in set(p["people"]) if n in slug_of)
        era_rows.append({
            "label": e["label"], "from": e["from"], "to": min(e["to"], years[-1]["year"]),
            "docs": sum(y["docs"] for y in ys), "stream": sum(y["stream"] for y in ys),
            "games": [{"slug": g["slug"], "title": g.get("title_zh") or g["title"], "year": g["year"], **game_icons(g)} for g in core][:10],
            "people": [{"name": n, "slug": slug_of[n], "n": c} for n, c in pc.most_common(5)],
        })

    totals = {k: sum(y["kinds"][k] for y in years) for k in DOC_KINDS}
    totals["stream"] = sum(y["stream"] for y in years)
    totals["docs"] = sum(y["docs"] for y in years)
    totals["max_docs"] = max(y["docs"] for y in years)
    totals["max_stream"] = max(y["stream"] for y in years)
    out = {"span": [years[0]["year"], years[-1]["year"]], "totals": totals, "eras": era_rows, "years": years,
           "streams": [{"key": k, "name": n, "url": u} for k, n, u in STREAMS.values()]}
    text = "# 由 tools/build-timeline.py 生成：资料时间线（/timeline/）的逐年数字、时代分段和每年的推荐。\n" + yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=1000)
    io.open(ROOT / "_data" / "timeline.yml", "w", encoding="utf-8", newline="\n").write(text)

    stubs = ROOT / "_pages" / "generated" / "timeline"
    stubs.mkdir(parents=True, exist_ok=True)
    want = set()
    for y in years:
        if not (y["docs"] or y["stream"]):
            continue
        want.add(f"{y['year']}.md")
        body = (f'---\nlayout: timeline\ntitle: "{y["year"]} - 资料时间线"\npermalink: "/timeline/{y["year"]}/"\ntimeline_year: {y["year"]}\nsearch: false\n---\n'
                "{% include timeline-year.html %}\n")
        io.open(stubs / f"{y['year']}.md", "w", encoding="utf-8", newline="\n").write(body)
    for old in stubs.glob("*.md"):
        if old.name not in want:
            old.unlink()
    print("timeline.yml:", totals, "|", len(want), "year pages")


if __name__ == "__main__":
    main()
