"""Check a post's `original` text against the source it cites.

The 2026-09 audits found posts whose Japanese "original" was written rather than
read: section headings the magazine never printed, paragraphs expanded with
facts the page does not carry, whole interviews back-generated from an English
summary. A translation cannot be audited until the original is known to be real,
so this tool answers one question per post: **is each original segment actually
present in the cited source?**

    python tools/audit_source_fidelity.py --posts <glob>...    [--json out.json]
    python tools/audit_source_fidelity.py --untracked           # every ?? post
    python tools/audit_source_fidelity.py --posts _posts/2017-09-05-*.md -v

Sources are read from, in order: data/cache_web/ and data/cache_web/audit/ (the
web importer's own page copies), data/cache_scan/<slug>/ (page transcriptions),
data/cache_nom/, then the network (cached under data/cache_audit/). A post whose
source cannot be read is reported as UNVERIFIABLE, which is not the same as
clean - a print magazine with no scan simply cannot be checked this way.

Coverage is measured per segment with character 6-grams over text stripped of
punctuation and whitespace, so OCR spacing and typographic variants do not
matter. Segments shorter than 12 characters are skipped (too common to be
evidence either way). A segment at/above --hit (default 0.55) counts as found.
"""
import argparse
import glob as globmod
import html
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
CACHES = [ROOT / "data" / "cache_web", ROOT / "data" / "cache_web" / "audit",
          ROOT / "data" / "cache_nom", ROOT / "data" / "cache_scan"]
NETCACHE = ROOT / "data" / "cache_audit"
UA = "Mozilla/5.0 (compatible; pokeamice-audit/1.0)"

PUNCT = re.compile(r"[\s　、。，．,\.「」『』（）\(\)【】〔〕《》・:：;；!！?？\-–—…~〜\"'’”“′″*|/\\\[\]#＃＆&%％+＋=]+")


def norm(s):
    return PUNCT.sub("", html.unescape(s or ""))


def grams(s, n=6):
    return {s[i:i + n] for i in range(max(0, len(s) - n + 1))}


def strip_html(raw):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>|</p>|</div>|</td>|</tr>|</li>|</h[1-6]>", "\n", t, flags=re.I)
    alts = " ".join(re.findall(r'alt="([^"]*)"', t))          # N.O.M keeps body text in alt=
    t = re.sub(r"<[^>]+>", " ", t)
    return html.unescape(t + "\n" + alts)


def decode(data):
    m = re.search(rb'charset=["\']?\s*([A-Za-z0-9._-]+)', data[:4096], re.I)
    hint = [m.group(1).decode("ascii", "ignore").lower()] if m else []
    hi_ratio = sum(1 for b in data[:8192] if b >= 0x80) / max(1, min(len(data), 8192))
    order = hint + (["utf-8", "cp1252", "shift_jis", "euc-jp", "cp932"] if hi_ratio < 0.03 else ["utf-8", "shift_jis", "euc-jp", "cp932", "cp1252"])
    for enc in dict.fromkeys(order):
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("utf-8", "replace")


def front_matter(path):
    t = open(path, encoding="utf-8").read().replace("\r", "")
    if not t.startswith("---"):
        return None, "no front matter"
    b = t[4:]
    closed = "\n---\n" in b
    if closed:
        b = b.split("\n---\n", 1)[0]
    try:
        d = yaml.safe_load(b)
    except Exception as exc:
        return None, f"YAML error: {str(exc)[:70]}"
    if not isinstance(d, dict):
        return None, "front matter is not a mapping"
    return d, (None if closed else "front matter has no closing ---")


def cited_urls(d):
    out = []
    src = d.get("source") if isinstance(d.get("source"), dict) else {}
    for v in (d.get("source_url"), d.get("original_link"), d.get("original_url"), src.get("url"), src.get("archive_url")):
        if isinstance(v, str) and v.startswith("http"):
            out.append(v)
    for p in (d.get("pages") or []):
        if isinstance(p, dict) and isinstance(p.get("url"), str) and p["url"].startswith("http"):
            out.append(p["url"])
    # a piece that ran over several pages: every page counts as the source, or the
    # paragraphs on pages 2..n read as missing (`source_pages`, or `pages` under `source`)
    more = d.get("source_pages") or ((d.get("source") or {}).get("pages") if isinstance(d.get("source"), dict) else None)
    for u in (more or []):
        if isinstance(u, str) and u.startswith("http"):
            out.append(u)
    seen, uniq = set(), []
    for u in out:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def local_source_text(d, post_path):
    """Page copies and transcriptions this repo already holds."""
    parts = []
    slug = d.get("scan_set")
    if slug:
        for p in sorted((ROOT / "data" / "cache_scan" / str(slug)).glob("*.txt")):
            parts.append(p.read_text(encoding="utf-8", errors="replace"))
    stem = Path(post_path).stem
    stem = re.sub(r"^\d{4}-\d{2}-\d{2}-(?:interview|scan|research)-", "", stem)
    for base in CACHES:
        if not base.exists():
            continue
        for p in list(base.glob(stem + "*.html")) + list(base.glob(stem + "*.txt")):
            raw = p.read_bytes()
            parts.append(strip_html(decode(raw)) if p.suffix == ".html" else decode(raw))
    return "\n".join(parts)


def fetch(url):
    NETCACHE.mkdir(parents=True, exist_ok=True)
    key = re.sub(r"[^A-Za-z0-9._-]+", "_", url)[:150]
    cached = NETCACHE / (key + ".txt")
    if cached.exists() and cached.stat().st_size > 200:
        return cached.read_text(encoding="utf-8", errors="replace"), "cache"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            raw = r.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        return "", f"fetch failed: {str(exc)[:60]}"
    text = strip_html(decode(raw))
    cached.write_text(text, encoding="utf-8")
    return text, "net"


def segments(d):
    return d.get("translation_segments") or d.get("parallel_items") or []


def audit(path, hit, offline, verbose):
    d, fm_note = front_matter(path)
    rec = {"post": os.path.basename(path), "note": fm_note}
    if d is None:
        rec["verdict"] = "UNPARSEABLE"
        return rec
    wf = d.get("workflow") or {}
    rec["workflow"] = f"{wf.get('translation', '')}/{wf.get('proofreading', '')}/{wf.get('published', '')}"
    segs = [
        x for x in segments(d)
        if isinstance(x, dict)
        and (x.get("original") or "").strip()
        and x.get("type") not in ("image", "hr", "translator_note")
        and x.get("role") not in ("image", "translator_note")
        and x.get("source") != "editor"
        and not str(x.get("original") or "").strip().startswith("/assets/")
    ]
    rec["segments"] = len(segs)
    src = local_source_text(d, path)
    rec["source"] = "local" if norm(src) else ""
    urls = cited_urls(d)
    rec["urls"] = urls
    if len(norm(src)) < 200 and not offline:
        for u in urls:
            t, how = fetch(u)
            if norm(t):
                src += "\n" + t
                rec["source"] = how
            else:
                rec.setdefault("fetch_errors", []).append(f"{u} -> {how}")
    S = grams(norm(src))
    if len(S) < 50:
        rec["verdict"] = "UNVERIFIABLE"
        return rec
    checked, found, misses = 0, 0, []
    for i, x in enumerate(segs):
        o = norm(x.get("original"))
        if len(o) < 12:
            continue
        g = grams(o)
        cov = len(g & S) / max(1, len(g))
        checked += 1
        if cov >= hit:
            found += 1
        else:
            misses.append({"item": i, "cov": round(cov, 2), "type": x.get("type"),
                           "text": (x.get("original") or "")[:90].replace("\n", "/")})
    rec["checked"], rec["found"] = checked, found
    rec["pct"] = round(100 * found / checked, 1) if checked else None
    rec["misses"] = misses if verbose else misses[:6]
    rec["miss_count"] = len(misses)
    if not checked:
        rec["verdict"] = "NOTHING TO CHECK"
    elif rec["pct"] >= 90:
        rec["verdict"] = "OK"
    elif rec["pct"] >= 60:
        rec["verdict"] = "PARTLY NOT IN SOURCE"
    else:
        rec["verdict"] = "NOT IN SOURCE"
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--posts", nargs="*", default=[])
    ap.add_argument("--untracked", action="store_true", help="audit every untracked post")
    ap.add_argument("--hit", type=float, default=0.55)
    ap.add_argument("--offline", action="store_true", help="local page copies only")
    ap.add_argument("--json", default="")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    paths = []
    for pat in args.posts:
        paths += sorted(globmod.glob(pat))
    if args.untracked:
        import subprocess
        out = subprocess.run(["git", "status", "--porcelain", "_posts"], cwd=ROOT,
                             capture_output=True, text=True, encoding="utf-8").stdout
        paths += [str(ROOT / l[3:].strip().strip('"')) for l in out.splitlines() if l.startswith("??")]
    if not paths:
        raise SystemExit("nothing to audit: pass --posts or --untracked")

    recs = []
    for p in dict.fromkeys(paths):
        r = audit(p, args.hit, args.offline, args.verbose)
        recs.append(r)
        pct = "" if r.get("pct") is None else f"{r['pct']:5.1f}%"
        print(f"{r['post'][:60]:62} {r['verdict']:22} {pct:>6} "
              f"{r.get('found', '')}/{r.get('checked', '')} src={r.get('source', '-') or '-'}"
              f"{'  [' + r['note'] + ']' if r.get('note') else ''}", flush=True)
        for m in r.get("misses", [])[:6 if not args.verbose else 100]:
            print(f"     item {m['item']:3} cov {m['cov']:.2f} [{m['type']}] {m['text']}")
    order = {"UNPARSEABLE": 0, "NOT IN SOURCE": 1, "PARTLY NOT IN SOURCE": 2,
             "UNVERIFIABLE": 3, "NOTHING TO CHECK": 4, "OK": 5}
    print("\n--- summary")
    for v in sorted({r["verdict"] for r in recs}, key=lambda v: order.get(v, 9)):
        n = [r for r in recs if r["verdict"] == v]
        print(f"  {v:22} {len(n):3}")
    if args.json:
        Path(args.json).write_text(json.dumps(recs, ensure_ascii=False, indent=1), encoding="utf-8")
        print("wrote", args.json)


if __name__ == "__main__":
    main()
