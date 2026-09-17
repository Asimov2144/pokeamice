"""Fold one import of a page into another import of the same page.

    python tools/fold-duplicate.py <retired stem> <kept stem> [--title] [--dry-run]

The kept post takes what the retired one had and it lacks: dek, summary, topics, mentions,
title_ja, era, tags and entities (union). With --title the retired post's title replaces the
kept one's (for a kept post whose title is the importer's placeholder). Then a redirect stub
at the retired address, its cards in the baked lists (_pages/generated) removed or, where the
kept post has none on that page, repointed, the retired file and its picture folder gone
(unless a portrait in tools/build-people.py or _data/people.yml is cut from it).
The addresses are the site's permalink rule, /:categories/:title/.
"""
import glob
import io
import os
import re
import sys

import yaml

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)
CARD = r'<article class="resource-network-card">\n(?:(?!</article>).)*?%s(?:(?!</article>).)*?</article>\n\n?'


def load(stem):
    t = io.open(f"{ROOT}/_posts/{stem}.md", encoding="utf-8").read()
    m = FRONT.match(t)
    return t, m, yaml.safe_load(m.group(1))


def url_of(stem, fm):
    cats = fm.get("categories") or []
    if isinstance(cats, str):
        cats = [cats]
    return "/" + "/".join(list(cats) + [stem[11:]]) + "/"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    retired, kept = args
    take_title = "--title" in sys.argv
    dry = "--dry-run" in sys.argv
    kt, km, kfm = load(kept)
    rt, rm, rfm = load(retired)
    kept_url, old_url = url_of(kept, kfm), url_of(retired, rfm)
    head = km.group(1)
    nl = "\r\n" if "\r\n" in head else "\n"
    changes = []

    def set_scalar(key, value):
        nonlocal head
        dumped = yaml.safe_dump({key: value}, allow_unicode=True, sort_keys=False, width=1000).rstrip("\n")
        if re.search(rf"(?m)^{key}:", head):
            head = re.sub(rf"(?ms)^{key}:.*?(?=^\S)", dumped + nl, head + nl, count=1).rstrip("\r\n")
        else:
            head = head + nl + dumped
        changes.append(key)

    if take_title and rfm.get("title"):
        set_scalar("title", rfm["title"])
    for key in ("dek", "summary", "title_ja", "era", "topics", "mentions", "display_title"):
        if rfm.get(key) and not kfm.get(key):
            set_scalar(key, rfm[key])
    tags = list(dict.fromkeys((kfm.get("tags") or []) + [t for t in (rfm.get("tags") or []) if t != "EN"]))
    if tags != (kfm.get("tags") or []):
        set_scalar("tags", tags)
    ke, re_ = kfm.get("entities") or {}, rfm.get("entities") or {}
    ents = dict(ke)
    for k in set(ke) | set(re_):
        merged = list(dict.fromkeys((ke.get(k) or []) + (re_.get(k) or [])))
        if merged:
            ents[k] = merged
    if ents != ke:
        set_scalar("entities", ents)
    new_kt = kt[:km.start(1)] + head + kt[km.end(1):]
    yaml.safe_load(FRONT.match(new_kt).group(1))       # it must still parse
    print(f"kept   {kept}\n       {kept_url}\n       takes: {', '.join(changes) or '(nothing)'}")
    print(f"retire {retired}\n       {old_url}")
    people = io.open(f"{ROOT}/_data/people.yml", encoding="utf-8").read()
    bp = io.open(f"{ROOT}/tools/build-people.py", encoding="utf-8").read()
    folder = f"{ROOT}/assets/img/interviews/{retired}"
    keep_folder = retired in bp or retired in people
    if os.path.isdir(folder):
        print(f"       pictures: {len(os.listdir(folder))} in its folder -> {'kept (a portrait is cut from it)' if keep_folder else 'removed'}")
    if dry:
        return
    io.open(f"{ROOT}/_posts/{kept}.md", "w", encoding="utf-8", newline="").write(new_kt)
    title = yaml.safe_load(FRONT.match(new_kt).group(1))["title"]
    io.open(f"{ROOT}/_pages/redirects/{retired[11:]}.html", "w", encoding="utf-8", newline="\n").write(f"""---
layout: null
permalink: {old_url}
sitemap: false
search: false
---
<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>已合并：{title}</title>
<link rel="canonical" href="{{{{ '{kept_url}' | relative_url }}}}">
<meta http-equiv="refresh" content="0; url={{{{ '{kept_url}' | relative_url }}}}">
<meta name="robots" content="noindex">
</head><body><p>这篇是同一篇文章的另一次导入，已并入：<a href="{{{{ '{kept_url}' | relative_url }}}}">{title}</a></p></body></html>
""")
    src_line = kfm.get("source") if isinstance(kfm.get("source"), str) else (kfm.get("source") or {}).get("title") or kfm.get("source_name") or kfm.get("publication") or ""
    year = str(kfm.get("date"))[:4]
    card = f'''<article class="resource-network-card">
  <p>{year} · interview_translation · {src_line}</p>
  <h3><a href="{kept_url}">{title}</a></h3>
  <span></span>
</article>

'''
    for f in glob.glob(f"{ROOT}/_pages/generated/**/*.md", recursive=True):
        t = io.open(f, encoding="utf-8").read()
        if old_url not in t:
            continue
        rep = "" if kept_url in t else card
        t2, k = re.subn(CARD % re.escape(old_url), rep, t, count=1, flags=re.S)
        if k:
            io.open(f, "w", encoding="utf-8", newline="\n").write(t2)
            print("       card", "removed" if not rep else "repointed", "in", os.path.relpath(f, ROOT))
    os.remove(f"{ROOT}/_posts/{retired}.md")
    if os.path.isdir(folder) and not keep_folder:
        for x in os.listdir(folder):
            os.remove(os.path.join(folder, x))
        os.rmdir(folder)
    print("       done")


if __name__ == "__main__":
    main()
