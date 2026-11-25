"""Mechanical sweep: fetch each bilingual post's source page, compute per-row 'original' coverage.
python sweep.py fetch   -> caches pages in sweep/pages (untracked)
python sweep.py score   -> writes sweep/scores.json + prints summary"""
import glob, hashlib, html, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import yaml
sys.stdout.reconfigure(encoding="utf-8")
WT = r"P:\WEBSITE\.docs-verify\translation-review"
OUT = os.path.join(WT, "design", "original-check-2026-11-26", "sweep")
PG = os.path.join(OUT, "pages")
os.makedirs(PG, exist_ok=True)
SKIP_HOSTS = ("style.fm",)  # done in the Shudo pass


def posts():
    for p in sorted(glob.glob(os.path.join(WT, "_posts", "*.md"))):
        t = open(p, encoding="utf-8").read().replace("\r\n", "\n")
        if not t.startswith("---"):
            continue
        try:
            fm = yaml.safe_load(t.split("---", 2)[1])
        except Exception:
            continue
        rows = fm.get("parallel_items") or fm.get("translation_segments")
        if not rows:
            continue
        src = fm.get("source") if isinstance(fm.get("source"), dict) else {}
        urls = []
        for u in (src.get("archive_url"), src.get("url"), fm.get("source_url"), fm.get("archive_url"), fm.get("outlet_url")):
            if u and u not in urls and str(u).startswith("http"):
                urls.append(str(u))
        yield os.path.basename(p)[:-3], fm, rows, urls


def cache_path(u):
    return os.path.join(PG, hashlib.md5(u.encode()).hexdigest() + ".bin")


def fetch(u):
    cp = cache_path(u)
    if os.path.exists(cp):
        return u, os.path.getsize(cp)
    try:
        r = subprocess.run(["curl", "-sL", "-m", "45", "--max-filesize", "8000000", "-A", "Mozilla/5.0", "-o", cp, "-w", "%{http_code}", u],
                           capture_output=True, text=True, timeout=60)
        code = r.stdout.strip()
        if code != "200":
            if os.path.exists(cp):
                os.remove(cp)
            return u, -int(code or 0)
        return u, os.path.getsize(cp)
    except Exception:
        if os.path.exists(cp):
            os.remove(cp)
        return u, -1


def decode(b):
    if b[:2] == bytes([31, 139]):
        import gzip
        b = gzip.decompress(b)
    head = b[:4000].decode("ascii", "ignore").lower()
    m = re.search(r"charset=[\"']?([a-z0-9_\-]+)", head)
    encs = ([m.group(1)] if m else []) + ["utf-8", "cp932", "euc-jp"]
    for e in encs:
        try:
            return b.decode(e)
        except Exception:
            pass
    return b.decode("utf-8", "ignore")


def page_text(u):
    cp = cache_path(u)
    if not os.path.exists(cp):
        return None
    t = decode(open(cp, "rb").read())
    t = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return t


def norm(s):
    s = html.unescape(str(s or "")).lower()
    return re.sub(r"[^0-9a-z\u3040-\u30ff\u3400-\u9fff\uff10-\uff5a]+", "", s)


def grams(s, k):
    return {s[i:i + k] for i in range(len(s) - k + 1)}


def k_for(s):
    cjk = len(re.findall(r"[\u3040-\u30ff\u3400-\u9fff]", s))
    return 6 if cjk > len(s) * 0.3 else 12


def all_urls():
    for stem, fm, rows, urls in posts():
        for u in urls:
            if not any(h in u for h in SKIP_HOSTS):
                yield u


if sys.argv[1] == "fetch":
    us = sorted(set(all_urls()))
    print("urls", len(us))
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(fetch, us))
    bad = [(u, c) for u, c in res if c <= 0]
    print("ok", len(res) - len(bad), "bad", len(bad))
    json.dump(bad, open(os.path.join(OUT, "fetch-bad.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
else:
    out = {}
    for stem, fm, rows, urls in posts():
        if any("style.fm" in u for u in urls):
            continue
        txt = None
        for u in urls:
            pt = page_text(u)
            if pt and len(norm(pt)) > 200:
                txt = (txt or "") + pt
        if not txt:
            out[stem] = {"status": "nopage", "urls": urls}
            continue
        N = norm(txt)
        flagged, checked = [], 0
        for i, r in enumerate(rows):
            if r.get("type") == "image":
                continue
            o = norm(r.get("original"))
            if len(o) < 40:
                continue
            k = k_for(str(r.get("original")))
            g = grams(o, k)
            if not g:
                continue
            c = sum(1 for x in g if x in N) / len(g)
            checked += 1
            if c < 0.5:
                flagged.append([i, round(c, 2), r.get("type", ""), str(r.get("original"))[:60]])
        out[stem] = {"status": "ok", "rows": len(rows), "checked": checked, "flagged": flagged, "urls": urls}
    json.dump(out, open(os.path.join(OUT, "scores.json"), "w", encoding="utf-8"), ensure_ascii=False)
    ok = [s for s, v in out.items() if v["status"] == "ok"]
    print("posts", len(out), "scored", len(ok), "nopage", len(out) - len(ok))
    w = sorted(((len(v["flagged"]), s) for s, v in out.items() if v["status"] == "ok" and v["flagged"]), reverse=True)
    print("posts with flagged rows", len(w), "rows", sum(n for n, _ in w))
    for n, s in w[:60]:
        print(n, out[s]["checked"], s)

if sys.argv[1] == "triage":
    d = json.load(open(os.path.join(OUT, "scores.json"), encoding="utf-8"))
    res = []
    for stem, fm, rows, urls in posts():
        v = d.get(stem)
        if not v or v["status"] != "ok" or not v["flagged"] or "-scan-" in stem:
            continue
        txt = "".join(page_text(u) or "" for u in urls)
        N = norm(txt)
        O = "".join(norm(r.get("original")) for r in rows if r.get("type") != "image")
        k = k_for(txt[:3000]) if txt else 6
        gO = grams(O, k)
        gN = grams(N, k)
        # fraction of the post original that the page explains; fraction of the page the post explains
        a = sum(1 for x in gO if x in N) / max(1, len(gO))
        b = len(gN & gO) / max(1, len(gN))
        res.append((stem, len(N), len(O), round(a, 2), round(b, 2), len(v["flagged"]), v["checked"]))
    json.dump(res, open(os.path.join(OUT, "triage.json"), "w", encoding="utf-8"), ensure_ascii=False)
    for r in sorted(res, key=lambda r: r[3]):
        print("pageLen %6d postOrigLen %6d  post->page %.2f page->post %.2f  flagged %d/%d  %s" % (r[1], r[2], r[3], r[4], r[5], r[6], r[0]))

if sys.argv[1] == "refetch":
    todo = []
    for u in sorted(set(all_urls())):
        m = re.match(r"(https?://web\.archive\.org/web/\d+)/(https?://.+)$", u)
        if not m:
            continue
        pt = page_text(u)
        if pt and len(norm(pt)) > 200:
            continue
        todo.append((u, m.group(1) + "id_/" + m.group(2)))
    print("refetch", len(todo))
    def go(x):
        u, v = x
        cp = cache_path(u)
        if os.path.exists(cp):
            os.remove(cp)
        r = subprocess.run(["curl", "-sL", "-m", "60", "-A", "Mozilla/5.0", "-o", cp, "-w", "%{http_code}", v], capture_output=True, text=True)
        code = r.stdout.strip()
        if code != "200" and os.path.exists(cp):
            os.remove(cp)
        return u, code
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(go, todo))
    from collections import Counter
    print(Counter(c for _, c in res))

if sys.argv[1] == "wayback":
    d = json.load(open(os.path.join(OUT, "scores.json"), encoding="utf-8"))
    todo = []
    for s, v in d.items():
        if v["status"] != "nopage" or "-scan-" in s:
            continue
        for u in v["urls"]:
            if "web.archive.org" in u or "archive.org/details" in u:
                continue
            todo.append(u)
    todo = sorted(set(todo))
    print("wayback todo", len(todo))
    def go(u):
        cp = cache_path(u)
        if os.path.exists(cp):
            return u, "cached"
        v = "https://web.archive.org/web/2id_/" + u
        try:
            r = subprocess.run(["curl", "-sL", "-m", "50", "-A", "Mozilla/5.0", "-o", cp, "-w", "%{http_code}", v], capture_output=True, text=True, timeout=70)
            code = r.stdout.strip()
        except Exception:
            code = "000"
        if code != "200" and os.path.exists(cp):
            os.remove(cp)
        return u, code
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(go, todo))
    from collections import Counter
    print(Counter(c for _, c in res))

if sys.argv[1] == "retry":
    d = json.load(open(os.path.join(OUT, "scores.json"), encoding="utf-8"))
    todo = []
    for s, v in d.items():
        if v["status"] != "nopage" or "-scan-" in s:
            continue
        for u in v["urls"]:
            if "archive.org/details" in u:
                continue
            todo.append(u)
    todo = sorted(set(todo))
    print("retry todo", len(todo), flush=True)
    def go(u):
        cp = cache_path(u)
        m = re.match(r"(https?://web\.archive\.org/web/\d+)/(https?://.+)$", u)
        v = (m.group(1) + "id_/" + m.group(2)) if m else "https://web.archive.org/web/2id_/" + u
        for attempt in range(2):
            try:
                r = subprocess.run(["curl", "-sL", "-m", "90", "-A", "Mozilla/5.0", "-o", cp, "-w", "%{http_code}", v], capture_output=True, text=True, timeout=110)
                code = r.stdout.strip()
            except Exception:
                code = "000"
            if code == "200":
                return u, code
            if os.path.exists(cp):
                os.remove(cp)
        return u, code
    with ThreadPoolExecutor(3) as ex:
        res = list(ex.map(go, todo))
    from collections import Counter
    print(Counter(c for _, c in res), flush=True)
