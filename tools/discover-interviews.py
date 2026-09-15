"""Find interviews on the open web, one query at a time, and keep what comes back.

    python tools/discover-interviews.py queries.txt out.json      # run every query
    python tools/discover-interviews.py --probe out.json          # then check each hit is alive

Search is Bing's HTML results page: no key, no JavaScript, one request
a query, a pause between. (DuckDuckGo's HTML endpoint was tried first and
answers a script with a challenge after a handful of queries.) Each query line in the file is either a
bare query or `label<TAB>query`; the label travels with the hits so a
batch can be read back by what it was looking for. Hits are de-duplicated
by URL across the whole run and kept with the title the engine printed,
which is usually the article's own.

--probe fetches every hit with a browser User-Agent and records the status,
so a list can be sorted into live, dead, and paywalled before anyone reads
it. Nothing here writes to _posts.
"""
import html
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept-Language": "ja,en;q=0.8,zh;q=0.6"}


def bing(query, n=10):
    """Bing's HTML results. DuckDuckGo's HTML endpoint answers a script with
    a duck-picking challenge after a few queries; Bing keeps answering."""
    url = "https://www.bing.com/search?q=" + urllib.parse.quote(query) + "&count=10"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        page = r.read().decode("utf-8", "replace")
    hits = []
    for block in re.findall(r'<li class="b_algo".*?</li>', page, re.S):
        a = re.search(r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, re.S)
        if not a:
            continue
        title = html.unescape(re.sub(r"<[^>]+>", "", a.group(2))).strip()
        snip = re.search(r'<p[^>]*class="b_lineclamp\d"[^>]*>(.*?)</p>|<div class="b_caption">.*?<p[^>]*>(.*?)</p>', block, re.S)
        snippet = html.unescape(re.sub(r"<[^>]+>", "", (snip.group(1) or snip.group(2) or ""))).strip() if snip else ""
        hits.append({"title": title, "url": html.unescape(a.group(1)), "snippet": snippet[:300]})
    return hits[:n]


ddg = bing


def run(queries_path, out_path):
    seen = {}
    lines = [l.rstrip("\n") for l in io.open(queries_path, encoding="utf-8") if l.strip() and not l.startswith("#")]
    for i, line in enumerate(lines, 1):
        label, _, query = line.partition("\t")
        if not query:
            label, query = "", label
        try:
            hits = ddg(query)
        except Exception as exc:
            print(f"[{i}/{len(lines)}] {query[:50]}  ERR {str(exc)[:60]}")
            time.sleep(8)
            continue
        new = 0
        for h in hits:
            key = re.sub(r"^https?://(www\.)?", "", h["url"]).rstrip("/")
            if key in seen:
                seen[key]["queries"].append(query)
                continue
            seen[key] = {**h, "label": label, "queries": [query]}
            new += 1
        print(f"[{i}/{len(lines)}] {query[:50]}  {len(hits)} hits, {new} new")
        io.open(out_path, "w", encoding="utf-8", newline="\n").write(json.dumps(list(seen.values()), ensure_ascii=False, indent=1))
        time.sleep(3.5)
    print(f"{len(seen)} distinct urls -> {out_path}")


def probe(out_path):
    rows = json.load(io.open(out_path, encoding="utf-8"))
    for i, r in enumerate(rows, 1):
        if r.get("status") is not None:
            continue
        try:
            req = urllib.request.Request(r["url"], headers=UA)
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read(300000).decode("utf-8", "replace")
                r["status"] = resp.status
                t = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
                r["page_title"] = html.unescape(t.group(1)).strip()[:160] if t else ""
        except urllib.error.HTTPError as exc:
            r["status"] = exc.code
        except Exception as exc:
            r["status"] = "ERR"
            r["error"] = str(exc)[:80]
        print(f"[{i}/{len(rows)}] {r['status']}  {r['url'][:80]}")
        io.open(out_path, "w", encoding="utf-8", newline="\n").write(json.dumps(rows, ensure_ascii=False, indent=1))
        time.sleep(0.8)


if __name__ == "__main__":
    if sys.argv[1] == "--probe":
        probe(sys.argv[2])
    else:
        run(sys.argv[1], sys.argv[2])
