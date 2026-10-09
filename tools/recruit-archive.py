"""The GAME FREAK recruit site as a versioned archive.

The recruit pages at gamefreak.co.jp/recruit/ reuse their addresses: the same cross-talk URL has
carried different people and a different text in different years, a person's page gets edited,
cards come and go on the index. This tool reads the Wayback Machine's copies of every page and
keeps the history as data, so a post can say which version of which page it translates and the
archive page (/keys/gamefreak-recruit-archive/) can draw the whole thing.

    python tools/recruit-archive.py fetch [page ...]   # list + download the captures (cached), all pages by default
    python tools/recruit-archive.py build              # -> _data/recruit_archive.yml
    python tools/recruit-archive.py check              # posts carrying `recruit:` against the page text they cite

The pages and their labels are in design/recruit-archive/pages.yml (hand-kept). Captures are cached
under data/cache_web/recruit-wayback/ (not in git; fetch rebuilds it). The CDX API answers
"Temporarily Offline" when it is pressed: that is retried, never read as "no captures".

A version is a run of captures with the same body text. A version ends when the people change or
less than 85 % of the text survives; smaller edits stay inside the version as `edits`.
`check` fails a post when fewer than 85 % of its Japanese paragraphs are found verbatim
(normalised) in the version it names - the test the ten invented "originals" of 2026-09 fail.
"""
import difflib
import hashlib
import html as htmlmod
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "cache_web" / "recruit-wayback"
PAGES_FILE = ROOT / "design" / "recruit-archive" / "pages.yml"
OUT = ROOT / "_data" / "recruit_archive.yml"
POSTS = ROOT / "_posts"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) pokeamice-docs archive (recruit pages)"}
KEEP_RATIO = 0.85
# the library writes these names as people.yml does
NAME_FIX = {"渡辺哲也": "渡边哲也", "増田順一": "增田顺一"}


# ---------------------------------------------------------------- fetching
def http(url, binary=False, tries=4):
    for i in range(tries):
        try:
            b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
            if binary:
                return b
            t = decode(b)
            if "Temporarily Offline" in t[:3000] and "web.archive.org" in url:
                raise IOError("wayback temporarily offline")
            return t
        except Exception as exc:  # noqa: BLE001 - every failure is retried the same way
            wait = 20 * (i + 1)
            print(f"    {exc} - retry in {wait}s", file=sys.stderr, flush=True)
            time.sleep(wait)
    raise IOError(f"gave up on {url}")


def decode(b):
    head = b[:2000].decode("ascii", "replace").lower()
    m = re.search(r'charset=["\']?([a-z0-9_-]+)', head)
    encs = ([m.group(1)] if m else []) + ["utf-8", "cp932", "euc_jp"]
    for enc in encs:
        try:
            return b.decode({"shift_jis": "cp932", "x-sjis": "cp932"}.get(enc, enc))
        except (LookupError, UnicodeDecodeError):
            continue
    return b.decode("utf-8", "replace")


def page_url(page):
    host = page.get("host", "www.gamefreak.co.jp")
    return f"https://{host}{page['path']}"


def cache_name(page_id, ts):
    return CACHE / "raw" / f"{page_id.replace('/', '__')}-{ts}.html"


def captures(page):
    """Distinct captures (by digest) of one page, oldest first: [(timestamp, digest)]."""
    url = page_url(page).split("://", 1)[1]
    q = f"https://web.archive.org/cdx/search/cdx?url={urllib.parse.quote(url)}&fl=timestamp,statuscode,digest&collapse=digest"
    rows = []
    for line in http(q).splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] == "200" and parts[0].isdigit():
            rows.append((parts[0], parts[2]))
    return rows


def fetch_capture(page, ts):
    p = cache_name(page["id"], ts)
    if p.exists() and p.stat().st_size > 1500:
        return p.read_text("utf-8")
    t = http(f"https://web.archive.org/web/{ts}id_/{page_url(page)}")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(t, "utf-8")
    time.sleep(1.5)
    return t


def cached_captures(page_id):
    pre = page_id.replace("/", "__") + "-"
    return sorted(p.stem[len(pre):] for p in (CACHE / "raw").glob(pre + "*.html") if p.stem[len(pre):].isdigit())


def cmd_fetch(ids):
    pages = load_pages()["pages"] + [{"id": "index", "path": "/recruit/"}]
    index = {}
    idx_file = CACHE / "captures.json"
    if idx_file.exists():
        index = json.loads(idx_file.read_text("utf-8"))
    for page in pages:
        if ids and page["id"] not in ids:
            continue
        try:
            caps = [ts for ts, _ in captures(page)]
        except IOError as exc:
            # the archive is refusing for now: keep what an earlier run listed, or what is cached
            caps = index.get(page["id"]) or cached_captures(page["id"])
            print(f"== {page['id']}: capture list unavailable ({exc}); using {len(caps)} known", flush=True)
        else:
            print(f"== {page['id']}: {len(caps)} captures", flush=True)
        for ts in caps:
            if page["id"] == "index" and ts < "20130101":
                continue
            try:
                fetch_capture(page, ts)
            except IOError as exc:
                print(f"   {ts}: {exc}", flush=True)
        index[page["id"]] = sorted(set(caps) | set(index.get(page["id"], [])))
        idx_file.write_text(json.dumps(index, indent=1), "utf-8")


# ---------------------------------------------------------------- reading a capture
def plain(fragment):
    f = re.sub(r"(?s)<(script|style|noscript)[^>]*>.*?</\1>", "", fragment)
    f = re.sub(r"(?i)<br\s*/?>", "", f)
    f = re.sub(r"(?i)</(p|h\d|li|dt|dd|div|figcaption|tr|section)>", "\n", f)
    f = re.sub(r"<[^>]+>", "", f)
    f = htmlmod.unescape(f)
    lines = [re.sub(r"[ \t　]+", " ", ln).strip() for ln in f.splitlines()]
    return [ln for ln in lines if ln]


def body_of(html, family):
    """(member lines, body lines) of a capture, without the site's furniture."""
    if family == "cms":
        start = html.find('class="st-contents')
        end = len(html)
        for mark in ('class="cp-projectstory', 'class="cp-people', 'class="cp-crosstalk', 'class="entries', "<footer"):
            i = html.find(mark, start + 1)
            if i > 0:
                end = min(end, i)
        main = html[start:end] if start >= 0 else html
        m0, c0 = main.find('class="member'), main.find('class="contents')
        if 0 <= m0 < c0:
            return plain(main[m0:c0]), plain(main[c0:])
        i0 = main.find('class="info')
        if 0 <= i0 < c0:
            return plain(main[i0:c0]), plain(main[c0:])
        return [], plain(main)
    if family == "gen1":
        start = html.find('class="content_inner')
        end = html.find('id="footer"')
        return [], plain(html[start:end if end > 0 else len(html)])
    # career2009 and anything else: the whole page minus its menus
    return [], [ln for ln in plain(html) if len(ln) > 8]


def initials(lines):
    return sorted(set(re.findall(r"(?<![A-Za-z])([A-Z]\.[A-Z]\.)", " ".join(lines))))


def norm(s):
    """Text for comparing: full-width and half-width forms folded, punctuation and spaces dropped."""
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s「」『』()、。,.・!?:“”\"'…―ー〜~®&]+", "", s)


def sha(lines):
    return hashlib.sha1("\n".join(lines).encode("utf-8")).hexdigest()[:10]


def stamp(ts):
    return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"


# ---------------------------------------------------------------- build
def load_pages():
    return yaml.safe_load(PAGES_FILE.read_text("utf-8"))


def text_ratio(a, b):
    """How much of the text survives, by characters (a reworded line is not a lost line)."""
    return difflib.SequenceMatcher(None, norm("".join(a)), norm("".join(b))).ratio()


def versions_of(page, caps):
    """Group a page's captures into versions (see the module note)."""
    fam = page.get("family", "cms")
    runs = []      # consecutive captures with identical body
    for ts in caps:
        p = cache_name(page["id"], ts)
        if not p.exists():
            continue
        html = p.read_text("utf-8")
        if len(html) < 1500:
            continue
        member, body = body_of(html, fam)
        named = [NAME_FIX.get(n, n) for n in (re.sub(r"\s+", "", htmlmod.unescape(x)) for x in re.findall(r'class="(?:member__list__name|info__name)">([^<]+)<', html))]
        people = (named if named and not all(re.fullmatch(r"[A-Z]\.[A-Z]\.", n) for n in named) else None)             or page.get("members") or initials(member or body[:12])
        assets = sorted(set(re.findall(r"\?(20\d{6})=", html)))
        h = sha(body)
        if runs and runs[-1]["sha"] == h:
            runs[-1]["last"] = ts
            runs[-1]["captures"] += 1
            continue
        runs.append({"sha": h, "first": ts, "last": ts, "captures": 1, "members": people, "assets": assets, "body": body})
    versions = []
    for r in runs:
        if versions:
            v = versions[-1]
            ratio = text_ratio(v["_body"], r["body"])
            same_people = r["members"] == v["members"]
            if same_people and ratio >= KEEP_RATIO:
                v["last"] = stamp(r["last"])
                v["captures"] += r["captures"]
                v["edits"].append({"at": stamp(r["first"]), "kept": round(ratio, 2)})
                v["_body"] = r["body"]
                v["_last_capture"] = r["last"]
                continue
            gone = set(v["members"]) - set(r["members"])
            if not set(v["members"]) & set(r["members"]) or ratio < 0.3:
                change = "replaced"
            elif gone and not set(r["members"]) - set(v["members"]):
                change = "members_removed"
            else:
                change = "rewritten"
        else:
            ratio, change = None, None
        versions.append({"id": stamp(r["first"]), "first": stamp(r["first"]), "last": stamp(r["last"]),
                         "captures": r["captures"], "members": r["members"], "change": change,
                         "kept": round(ratio, 2) if ratio is not None else None,
                         "assets": r["assets"][-1] if r["assets"] else None, "edits": [],
                         "wayback": r["first"], "_body": r["body"], "_last_capture": r["last"]})
    for v in versions:
        v["wayback_last"] = v.pop("_last_capture")
        v.pop("_body")
        if not v["edits"]:
            v.pop("edits")
        for k in ("change", "kept", "assets"):
            if v.get(k) is None:
                v.pop(k)
    return versions


def index_periods(caps):
    """The cards and the talks the recruit index links, as periods of identical sets."""
    out = []
    for ts in caps:
        p = cache_name("index", ts)
        if not p.exists():
            continue
        html = p.read_text("utf-8")
        cards, talks = [], []
        for h in re.findall(r'href="([^"]+)"', html):
            m = re.search(r"/recruit/(interview-[a-z]+-[a-z]+)", h) or re.search(r"(?:^|/recruit/)(interview_\d+)\.html", h)
            if m and m.group(1) not in cards:
                cards.append(m.group(1))
            m = re.search(r"/recruit/((?:crosstalk|projectstory)-[a-z-]+?)/?$", h)
            if m and m.group(1) not in talks:
                talks.append(m.group(1))
        if not cards:
            continue
        key = (tuple(sorted(cards)), tuple(talks))
        if out and out[-1]["_key"] == key:
            out[-1]["last"] = stamp(ts)
            out[-1]["snapshots"] += 1
            continue
        out.append({"_key": key, "first": stamp(ts), "last": stamp(ts), "snapshots": 1, "cards": cards, "talks": talks})
    for o in out:
        o.pop("_key")
    return out


def posts_with_recruit():
    found = {}
    for p in sorted(POSTS.glob("*.md")):
        t = p.read_text("utf-8", errors="replace")
        if "\nrecruit:" not in t[:6000]:
            continue
        fm = yaml.safe_load(t.split("\n---", 1)[0].lstrip("-﻿\n"))
        r = fm.get("recruit") or {}
        if r.get("page"):
            found.setdefault(r["page"], {})[str(r.get("version"))] = p.stem
    return found


def cmd_build():
    pages = load_pages()
    caps = json.loads((CACHE / "captures.json").read_text("utf-8")) if (CACHE / "captures.json").exists() else {}
    for pid in [p["id"] for p in pages["pages"]] + ["index"]:
        caps[pid] = sorted(set(caps.get(pid, [])) | set(cached_captures(pid)))
    linked = posts_with_recruit()
    out_pages = []
    for page in pages["pages"]:
        vs = versions_of(page, caps.get(page["id"], []))
        for v in vs:
            stem = linked.get(page["id"], {}).get(v["id"]) or (page.get("version_posts") or {}).get(v["id"])
            if stem:
                v["post"] = stem
        for k, note in (page.get("version_notes") or {}).items():
            for v in vs:
                if v["id"] == k:
                    v["note"] = note
        entry = {k: page[k] for k in ("id", "kind", "group", "label", "label_ja", "era", "note") if page.get(k)}
        entry["url"] = page_url(page)
        entry["status"] = page.get("status") or "live"
        entry["versions"] = vs
        out_pages.append(entry)
        print(f"{page['id']:<34} {len(vs)} version(s): " + " | ".join(f"{v['id']} {','.join(v['members'])}{' ->' + v['post'][:10] if v.get('post') else ''}" for v in vs))
    data = {
        "_comment": "generated by tools/recruit-archive.py build from Wayback captures + design/recruit-archive/pages.yml - do not edit",
        "updated": time.strftime("%Y-%m-%d"),
        "index": index_periods(caps.get("index", [])),
        "pages": out_pages,
    }
    OUT.write_text("# " + data.pop("_comment") + "\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=200), "utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


# ---------------------------------------------------------------- check
def post_originals(fm):
    out = []
    for it in fm.get("parallel_items") or []:
        if it.get("type") == "image" or not isinstance(it.get("original"), str):
            continue
        if it.get("source") == "editor" or it.get("from_capture"):   # the editor's line / another version's (checked on its own)
            continue
        for piece in re.split(r"\n\s*\n", it["original"].replace("\\n", "\n")):
            if len(norm(piece)) >= 12:
                out.append(piece.strip())
    return out


def cmd_check():
    pages = {p["id"]: p for p in load_pages()["pages"]}
    data = yaml.safe_load(OUT.read_text("utf-8"))
    vers = {p["id"]: {v["id"]: v for v in p["versions"]} for p in data["pages"]}
    bad = 0
    for p in sorted(POSTS.glob("*.md")):
        t = p.read_text("utf-8", errors="replace")
        if "\nrecruit:" not in t[:6000]:
            continue
        fm = yaml.safe_load(t.split("\n---", 1)[0].lstrip("-﻿\n"))
        r = fm["recruit"]
        page, v = pages.get(r["page"]), vers.get(r["page"], {}).get(str(r.get("version")))
        if not page or not v:
            print(f"FAIL {p.stem}: no page/version {r}")
            bad += 1
            continue
        ts = str(r.get("capture") or v["wayback_last"])
        cp = cache_name(page["id"], ts)
        if not cp.exists():
            print(f"FAIL {p.stem}: capture {ts} not cached (run fetch)")
            bad += 1
            continue
        html = cp.read_text("utf-8")
        member, body = body_of(html, page.get("family", "cms"))
        # the check reads the whole main column: the title block and a story's theme sit before the members
        start = html.find('class="st-contents')
        text = norm("".join(member + body + plain(html[start:] if start >= 0 else html)))
        origs = post_originals(fm)
        hit = sum(norm(o) in text for o in origs)
        # paragraphs carried over from an earlier version are read against that version's capture
        for it in fm.get("parallel_items") or []:
            fc = it.get("from_capture")
            if fc and isinstance(it.get("original"), str):
                ep = cache_name(page["id"], str(fc))
                etext = norm("".join(plain(ep.read_text("utf-8")))) if ep.exists() else ""
                if norm(it["original"]) not in etext:
                    print(f"FAIL {p.stem}: carried-over paragraph not in {fc}: {it['original'][:60]}")
                    bad += 1
        share = hit / max(1, len(origs))
        flag = "ok  " if share >= KEEP_RATIO else "FAIL"
        if share < KEEP_RATIO:
            bad += 1
        print(f"{flag} {p.stem:<64} {hit}/{len(origs)} ({share:.0%}) vs {page['id']}@{ts}")
        if share < KEEP_RATIO:
            for o in origs:
                if norm(o) not in text:
                    print(f"       not on the page: {o[:90]}")
    print("ALL OK" if not bad else f"{bad} post(s) fail")
    return 1 if bad else 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "fetch":
        cmd_fetch(sys.argv[2:])
    elif cmd == "build":
        cmd_build()
    elif cmd == "check":
        sys.exit(cmd_check())
    else:
        print(__doc__)
