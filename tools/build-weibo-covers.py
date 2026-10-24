#!/usr/bin/env python3
"""Extract the covers the home page's 随手发的东西 card draws from: every fragment with its stickers.

    python tools/build-weibo-covers.py

Input : _pages/notes-weibo/index.md (written by tools/build-weibo-notes.py, which runs this at the end)
Output: assets/data/weibo-covers.json, read by assets/js/home-notes-covers.js

Compact on purpose (the home page fetches it): "c" lists [category, colour], "s" lists the
stickers once as [kind, name, short src], and each post in "p" is [date, category index,
excerpt, sticker index...]. Short src: "p:" is under
https://gallery.pokeamice.com/pokemon-assets/, "w:" under /assets/img/works/.
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_pages" / "notes-weibo" / "index.md"
OUT = ROOT / "assets" / "data" / "weibo-covers.json"

PREFIX = {"p:": "https://gallery.pokeamice.com/pokemon-assets/", "w:": "/assets/img/works/"}

ART = re.compile(r'<article class="fr ([^"]*)" id="f-([0-9a-f]+)" data-d="([\d-]+)" data-c="([^"]*)"[^>]*?'
                 r'style="--c:(#[0-9a-fA-F]{3,6})[^"]*">(.*?)</article>', re.S)
STK = re.compile(r'<span class="stk [^"]*\bst-(p|w)\b[^"]*" title="([^"]*)"[^>]*><img src="([^"]+)"')
TEXT = re.compile(r'<div class="fr-text">(.*?)</div>', re.S)
CAP = re.compile(r'<p class="fr-cap">(.*?)</p>', re.S)


def plain(s):
    s = re.sub(r"<a [^>]*>.*?</a>", " ", s, flags=re.S)   # hashtags, places, the long-article link
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\[[^\[\]]{1,8}\]", "", s)                # [兔子] - Weibo's emoji codes
    s = re.sub(r"https?://\S+", "", s)
    return re.sub(r"\s+", " ", s).strip()


def short(src):
    for k, v in PREFIX.items():
        if src.startswith(v):
            return k + src[len(v):]
    return src


def excerpt(s, n=22):
    return s if len(s) <= n else s[:n].rstrip() + "…"


def main():
    page = SRC.read_text(encoding="utf-8")
    cats, stickers, sidx, posts = [], [], {}, []
    for m in ART.finditer(page):
        _, _, d, cat, color, body = m.groups()
        t = TEXT.search(body)
        text = plain(t.group(1)) if t else ""
        if not text:
            c = CAP.search(body)
            text = plain(c.group(1)) if c else ""
        ks = []
        for kind, name, src in STK.findall(body):
            key = (kind, html.unescape(name), short(src))
            if key not in sidx:
                sidx[key] = len(stickers)
                stickers.append(list(key))
            if sidx[key] not in ks:
                ks.append(sidx[key])
        if not text and not ks:
            continue
        ck = [cat, color.lower()]
        if ck not in cats:
            cats.append(ck)
        posts.append([d, cats.index(ck), excerpt(text)] + ks)
    data = {"c": cats, "s": stickers, "p": posts}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"{OUT.relative_to(ROOT)}: {len(posts)} posts, {sum(1 for p in posts if len(p) > 3)} with stickers, "
          f"{len(stickers)} stickers, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
