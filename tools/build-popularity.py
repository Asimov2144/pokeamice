"""The click weight of the front desk's feed: _data/popularity.yml, url -> hits, read from
an analytics export. docs.pokeamice.com has no counter of its own yet (analytics.provider
is false), so the file is empty until one is switched on; any export with a path column
and a count column does (GoatCounter / Umami / Cloudflare / Plausible CSV, or a JSON list
of {path, hits}). Paths are kept only when they are a post's url.

    python tools/build-popularity.py data/hits.csv
    python tools/build-popularity.py data/hits.json
"""
import csv
import io
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_data" / "popularity.yml"
PATH_KEYS = ("path", "pathname", "url", "page", "page_path")
HIT_KEYS = ("hits", "count", "views", "pageviews", "visitors", "unique", "visits")
FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)


def post_urls():
    """The url of every post, as Jekyll builds it: the permalink in the front matter, else
    the default date/title pattern is not reproduced here - the built catalogue is used."""
    built = ROOT / "_site" / "assets" / "js" / "catalogue.json"
    if built.exists():
        return {it["url"] for it in json.load(io.open(built, encoding="utf-8"))}
    return None


def rows_of(path):
    text = io.open(path, encoding="utf-8-sig").read()
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("hits") or data.get("data") or data.get("results") or []
        return [dict(r) for r in data if isinstance(r, dict)]
    return list(csv.DictReader(io.StringIO(text)))


def pick(row, keys):
    for k in row:
        if k and k.strip().lower() in keys:
            return row[k]
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    src = Path(sys.argv[1])
    urls = post_urls()
    hits = {}
    for row in rows_of(src):
        p, n = pick(row, PATH_KEYS), pick(row, HIT_KEYS)
        if not p or n in (None, ""):
            continue
        p = urlsplit(str(p).strip()).path or "/"
        if not p.endswith("/") and "." not in p.rsplit("/", 1)[-1]:
            p += "/"
        try:
            n = int(float(n))
        except ValueError:
            continue
        if urls is not None and p not in urls:
            continue
        hits[p] = hits.get(p, 0) + n
    lines = [
        "# 首页综合推荐里的点击权重：帖子 url -> 点击数，由 tools/build-popularity.py 从统计导出文件生成。",
        "# 站点目前没有接统计（_config.yml analytics.provider: false），接上后导出 path,count 的 CSV 重跑即可。",
    ]
    if not hits:
        lines.append("{}")
    for p in sorted(hits, key=lambda k: -hits[k]):
        lines.append(f"{json.dumps(p, ensure_ascii=False)}: {hits[p]}")
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print(f"popularity.yml: {len(hits)} urls" + ("" if urls is not None else " (no _site build to check the urls against)"))


if __name__ == "__main__":
    main()
