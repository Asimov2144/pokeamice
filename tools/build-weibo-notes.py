#!/usr/bin/env python3
"""Build the fragments page: every original short Weibo post by 2144jx, as scraps.

    python tools/build-weibo-notes.py

Input : P:/weibo/_work/dataset.json (posts) + analysis.jsonl (model-made category / topics /
        caption / OCR per post; optional - posts without a record show as plain scraps)
Output: _pages/notes-weibo/index.md  -> /notes/weibo/   (noindex, not in navigation)

The long articles are not here: they are regular posts (tools/build-weibo-posts.py).
An announcement post for one of them links to that post instead.
Re-running rewrites the whole _pages/notes-weibo directory; do not hand-edit it.
"""
import hashlib, html, importlib.util, json, re, shutil, sys
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from weibo_common import WORK, esc_liquid, img_url  # noqa: E402
import weibo_mentions  # noqa: E402

SPECIES_BASE = "https://gallery.pokeamice.com/pokemon-assets/"
USED_W, USED_S = {}, {}

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_pages" / "notes-weibo"

spec = importlib.util.spec_from_file_location("bwp", ROOT / "tools" / "build-weibo-posts.py")
bwp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bwp)

CATS = OrderedDict([
    ("考据观察", "#b5532f"), ("情报新闻", "#2f6fb5"), ("人物与制作", "#7a4fa3"), ("原型与现实", "#3a8a5a"),
    ("资料与扫描", "#8a7a2f"), ("随想吐槽", "#c0577f"), ("对战与卡牌", "#c0892f"), ("日常杂项", "#777777"),
    ("周边与展会", "#2f8a8a"), ("同人与创作", "#a3504f"),
])

data = json.load(open(WORK / "dataset.json", encoding="utf-8"))
posts = sorted(data["posts"], key=lambda p: p["d"], reverse=True)
ana = {}
if (WORK / "analysis.jsonl").exists():
    for line in (WORK / "analysis.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            o = json.loads(line)
            if "_err" not in o:
                ana[o["id"]] = o

# announcement posts -> the article post they announce
first = {}
for a in json.load(open(WORK / "articles.json", encoding="utf-8")):
    first[a["id"]] = min(first.get(a["id"], "9"), a["d"])
mid_to_art = {a["post"]: a["id"] for a in json.load(open(WORK / "articles.json", encoding="utf-8"))}


def article_post_name(aid):
    if aid == bwp.EXISTING:
        return "2024-10-24-[长文]-拨云见日-从百代市到水脉图书馆"
    return f"{first[aid][:10]}-{bwp.SLUGS[aid]}"


LINK = re.compile(r"\[([^\]\n]+)\]\((https?://[^)\s]+)\)")


def render_text(p):
    t = p["text"]
    if p["src"] == "md":
        t = html.unescape(t)
    t = html.escape(t, quote=False)
    t = LINK.sub(lambda m: f'<a href="{html.escape(html.unescape(m.group(2)))}" rel="nofollow noopener" target="_blank">{m.group(1)}</a>', t)
    t = t.replace("\n", "<br>\n")
    return esc_liquid(t)


def jitter(pid, lo, hi, salt):
    h = int(hashlib.md5((pid + salt).encode()).hexdigest()[:6], 16) / 0xFFFFFF
    return lo + (hi - lo) * h


def esc_attr(s):
    return html.escape(esc_liquid(s), quote=True)


def card(p):
    o = ana.get(p["id"], {})
    cat = o.get("category") if o.get("category") in CATS else ""
    topics = [t for t in (o.get("topics") or []) if isinstance(t, str)][:3]
    ocr = (o.get("ocr") or "").strip() if isinstance(o.get("ocr"), str) else ""
    cap = (o.get("caption") or "").strip() if isinstance(o.get("caption"), str) else ""
    rs = o.get("research") if isinstance(o.get("research"), int) else 0
    n = len(p["imgs"])
    ws, sp = weibo_mentions.find(p["text"], " ".join(topics), cap, ocr)
    for w in ws:
        USED_W[w["key"]] = USED_W.get(w["key"], 0) + 1
    for x in sp:
        USED_S[x["id"]] = USED_S.get(x["id"], 0) + 1
    ktok = " ".join([w["key"] for w in ws] + [f"p{x['id']}" for x in sp])
    rot = jitter(p["id"], -1.4, 1.4, "r")
    dy = jitter(p["id"], 0, 14, "y")
    kind = "pic" if (n and len(p["text"]) < 40) else ("note" if not n else "mix")
    if kind == "note" and len(p["text"]) > 120:
        kind = "long"
    search = " ".join([p["text"], cap, ocr, " ".join(topics)])
    attrs = (f'class="fr fr-k-{kind}" id="f-{p["id"]}" data-d="{p["d"][:10]}" data-c="{cat}" data-r="{rs}" data-i="{1 if n else 0}" data-k="{ktok}" '
             f'data-s="{esc_attr(search.lower())}" style="--c:{CATS.get(cat, "#999")};--rot:{rot:.2f}deg;--dy:{dy:.0f}px"')
    h = [f"<article {attrs}>"]
    meta = f'<time>{p["d"][5:16].replace("-", "·", 1)}</time>'
    if cat:
        meta += f'<b class="fr-cat">{cat}</b>'
    h.append(f'<header class="fr-meta">{meta}</header>')
    text = render_text(p)
    mid = p.get("mid")
    if mid in mid_to_art:
        text += f'<br><a class="fr-art" href="{{% post_url {article_post_name(mid_to_art[mid])} %}}">→ 这条的长文已收入站内文章</a>'
    h.append(f'<div class="fr-text">{text}</div>')
    if n:
        shown = p["imgs"][:4]
        h.append(f'<div class="fr-imgs fr-imgs-{len(shown)}">')
        for rel in shown:
            u = img_url(rel)
            h.append(f'<a href="{u}" target="_blank" rel="noopener"><img loading="lazy" decoding="async" src="{u}" alt=""></a>')
        if n > 4:
            h.append(f'<span class="fr-more">+{n - 4}</span>')
        h.append("</div>")
        if cap:
            h.append(f'<p class="fr-cap">{html.escape(esc_liquid(cap), quote=False)}</p>')
        if len(ocr) >= 6:
            snip = re.sub(r"\s+", " ", ocr)[:60]
            h.append(f'<p class="fr-ocr" title="模型转写的图中文字">▤ {html.escape(esc_liquid(snip), quote=False)}</p>')
    if topics:
        h.append('<p class="fr-topics">' + " ".join(f"#{html.escape(esc_liquid(t), quote=False)}" for t in topics) + "</p>")
    if p.get("video"):
        h.append('<p class="fr-vnote">（原帖含视频，存档未收录）</p>')
    link = f' · <a href="https://m.weibo.cn/detail/{mid}" rel="nofollow noopener" target="_blank">原微博</a>' if mid else ""
    h.append(f'<footer class="fr-foot">♥ {p["likes"]}{link}</footer>')
    stk = []
    for w in ws[:3]:
        r = jitter(p["id"] + w["key"], -9, 9, "s")
        imgs = "".join(f'<img src="{i}" alt="" loading="lazy">' for i in w["icons"][:2])
        stk.append(f'<span class="st st-w" title="{html.escape(w["name"])}" style="--sr:{r:.0f}deg">{imgs}</span>')
    for x in sp[:3]:
        r = jitter(p["id"] + str(x["id"]), -12, 12, "s")
        stk.append(f'<span class="st st-p" title="{html.escape(x["zh"])}" style="--sr:{r:.0f}deg"><img src="{SPECIES_BASE}{x["img"]}" alt="" loading="lazy"></span>')
    extra = len(ws) + len(sp) - len(stk)
    if stk:
        h.append('<div class="fr-stk">' + "".join(stk) + (f'<span class="st-more">+{extra}</span>' if extra > 0 else "") + "</div>")
    h.append("</article>")
    return "\n".join(h)


months = OrderedDict()
for p in posts:
    months.setdefault(p["d"][:7], []).append(p)

counts = {c: sum(1 for p in posts if ana.get(p["id"], {}).get("category") == c) for c in CATS}
chips = "".join(f'<button type="button" class="fr-chip" data-c="{c}" style="--c:{col}">{c}<i>{counts[c]}</i></button>' for c, col in CATS.items())
years = sorted({p["d"][:4] for p in posts}, reverse=True)
yopts = "".join(f'<option value="{y}">{y}</option>' for y in years)

cards_html = {p["id"]: card(p) for p in posts}


def sticker_bar():
    ws = sorted((w for w in weibo_mentions.works() if USED_W.get(w["key"], 0) >= 2), key=lambda w: -USED_W[w["key"]])[:18]
    spx = {sp["id"]: sp for _, sp in weibo_mentions.species()["zh"]}
    top = sorted((i for i, c in USED_S.items() if c >= 3), key=lambda i: -USED_S[i])[:26]
    out = ['<div class="st-bar"><span class="lab">作品</span>']
    for w in ws:
        imgs = "".join(f'<img src="{i}" alt="">' for i in w["icons"][:1])
        out.append(f'<button type="button" class="st-b st-bw" data-k="{w["key"]}" title="{html.escape(w["name"])} · {USED_W[w["key"]]}">{imgs}<i>{USED_W[w["key"]]}</i></button>')
    out.append('</div><div class="st-bar"><span class="lab">宝可梦</span>')
    for i in top:
        x = spx.get(i)
        if not x:
            continue
        out.append(f'<button type="button" class="st-b st-bp" data-k="p{i}" title="{html.escape(x["zh"])} · {USED_S[i]}"><img src="{SPECIES_BASE}{x["img"]}" alt=""><i>{USED_S[i]}</i></button>')
    out.append("</div>")
    return "".join(out)


body = [
    '<h1 class="fr-title">碎片 <small>· 2144jx 的微博 2021—2026</small></h1>',
    '<p class="fr-lead">这里是随手发的东西：一句观察、一张截图、半截猜想、几句吐槽。它们不是资料，也不都站得住，只是当时的碎片，按时间摊开。'
    '长文已经单独收进站内文章（分类「站主原创」）。<br><span class="fr-ai">分类、图注与图中文字由模型（Qwen）生成，可能有误；每条的「原微博」链接可对照原帖。</span></p>',
    '<div class="fr-tools">',
    f'<input id="fr-q" type="search" placeholder="搜文字、图中字、话题…" autocomplete="off">',
    f'<select id="fr-y"><option value="">全部年份</option>{yopts}</select>',
    '<label><input id="fr-img" type="checkbox"> 只看有图</label>',
    '<label><input id="fr-r" type="checkbox"> 只看有依据的</label>',
    '<span id="fr-n"></span>',
    "</div>",
    f'<div class="fr-chips">{chips}</div>',
    sticker_bar(),
    '<div id="fr-wall" class="fr-wall">',
]
for ym, ps in months.items():
    body.append(f'<h2 class="fr-month" data-m="{ym}"><span>{ym[:4]}</span>{ym[5:]}</h2>')
    body.append(f'<section class="fr-group" data-m="{ym}">')
    body += [cards_html[p["id"]] for p in ps]
    body.append("</section>")
body += ["</div>", '<p id="fr-empty" class="fr-empty" hidden>没有符合的碎片。</p>',
         '<script src="/assets/js/notes-fragments.js" defer></script>']

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)
front = """---
layout: notes-archive
title: "碎片 · 2144jx 的微博"
permalink: /notes/weibo/
shell_class: wbn-wide
noindex: true
sitemap: false
search: false
hidden: true
---
"""
(OUT / "index.md").write_text(front + "\n" + "\n".join(body) + "\n", encoding="utf-8", newline="\n")
print(f"{len(posts)} fragments, {len(ana)} analysed, {len(months)} months -> {OUT / 'index.md'}")
