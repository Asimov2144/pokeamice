#!/usr/bin/env python3
"""Build the fragments page: every original short Weibo post by 2144jx, as scraps.

    python tools/build-weibo-notes.py

Input : P:/weibo/_work/dataset.json (posts) + analysis.jsonl (model-made category / topics /
        caption / OCR per post; optional - posts without a record show as plain scraps)
Output: _pages/notes-weibo/index.md  -> /notes/weibo/   (noindex, not in navigation)
        assets/data/weibo-covers.json (via tools/build-weibo-covers.py, for the home page card)

The long articles are not here: they are regular posts (tools/build-weibo-posts.py).
An announcement post for one of them links to that post instead.
Re-running rewrites the whole _pages/notes-weibo directory; do not hand-edit it.
"""
import hashlib, html, importlib.util, json, re, shutil, sys
from PIL import Image
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


_dims = {}


def dims(rel):
    """(w, h) of the compressed copy on COS, so the page can keep every picture's own shape."""
    name = rel.rsplit("/", 1)[-1]
    if name not in _dims:
        try:
            with Image.open(WORK / "cos" / name) as im:
                _dims[name] = im.size
        except Exception:
            _dims[name] = (4, 3)
    return _dims[name]


def hv(pid, salt):
    return int(hashlib.md5((pid + salt).encode()).hexdigest()[:6], 16) / 0xFFFFFF


def fig(rel, cls="", style=""):
    w, h = dims(rel)
    u = img_url(rel)
    st = f' style="--ar:{w / h:.3f}{";" + style if style else ""}"'
    return (f'<a class="fr-ph {cls}"{st} href="{u}" target="_blank" rel="noopener">'
            f'<img loading="lazy" decoding="async" width="{w}" height="{h}" src="{u}" alt=""></a>')


def row(rels, cls=""):
    return f'<div class="fr-row {cls}">' + "".join(fig(r) for r in rels) + "</div>"


def paragraphs(p):
    lines = [l for l in p["text"].split("\n") if l.strip()]
    if len(lines) > 4:
        lines = lines[:3] + ["\n".join(lines[3:])]
    return [render_text({**p, "text": l}) for l in lines]


def stickers_for(ws, sp):
    """Every icon is its own sticker (a two-version game gives two), works first."""
    out = []
    for w in ws[:2]:
        for k, ic in enumerate(w["icons"][:2]):
            out.append(("w", w["name"], ic, f"{w['key']}-{k}"))
    for x in sp[:3]:
        out.append(("p", x["zh"], SPECIES_BASE + x["img"], f"p{x['id']}"))
    return out[:6], max(0, len(out) - 6)


def place(p, stks, has_img):
    """Spread the stickers over the card: picture corners first when there are pictures, then
    the card's own corners and edges - the gaps the layout leaves for them."""
    h = hv(p["id"], "slots")
    slots_img = ["i1", "i2", "i3", "i4"]
    slots_card = ["tr", "bl", "br", "tl", "ml", "mr"]
    rot = int(h * len(slots_card))
    slots_card = slots_card[rot:] + slots_card[:rot]
    inside, outside = [], []
    order = (slots_img[:2] + slots_card) if has_img else slots_card
    for i, st in enumerate(stks):
        slot = order[i % len(order)]
        r = jitter(p["id"], -14, 14, f"s{i}")
        kind, name, src, key = st
        size = "st-lg" if kind == "p" else "st-md"
        el = (f'<span class="stk stk-{slot} {size} st-{kind}" title="{html.escape(name)}" style="--sr:{r:.0f}deg">'
              f'<img src="{src}" alt="" loading="lazy"></span>')
        (inside if slot.startswith("i") else outside).append(el)
    return "".join(inside), "".join(outside)


def pick_variant(p, n, L, ars, npar):
    h = hv(p["id"], "var")
    if n == 0:
        return "note"
    if n == 1:
        ar = ars[0]
        if ar > 1.5:
            return "hero"
        if ar < 0.85 and L >= 30:
            return "float"
        return "pol" if h < .34 else ("tape" if h < .67 else "hero")
    if npar >= 2 and L <= 700 and h < .55:
        return "mag"
    if n == 2:
        return "pair" if h < .5 else "overlap"
    if n <= 4:
        return "strip" if h < .5 else ("overlap" if n == 3 else "grid")
    return "mosaic"


SPREAD_USED = set()


def card(p):
    o = ana.get(p["id"], {})
    cat = o.get("category") if o.get("category") in CATS else ""
    topics = [t for t in (o.get("topics") or []) if isinstance(t, str)][:3]
    ocr = (o.get("ocr") or "").strip() if isinstance(o.get("ocr"), str) else ""
    cap = (o.get("caption") or "").strip() if isinstance(o.get("caption"), str) else ""
    rs = o.get("research") if isinstance(o.get("research"), int) else 0
    imgs = p["imgs"]
    n = len(imgs)
    ws, sp = weibo_mentions.find(p["text"], " ".join(topics), cap, ocr)
    for w in ws:
        USED_W[w["key"]] = USED_W.get(w["key"], 0) + 1
    for x in sp:
        USED_S[x["id"]] = USED_S.get(x["id"], 0) + 1
    ktok = " ".join([w["key"] for w in ws] + [f"p{x['id']}" for x in sp])
    L = len(re.sub(r"\s", "", p["text"]))
    shown = imgs[:6]
    ars = [dims(r)[0] / dims(r)[1] for r in shown]
    paras = paragraphs(p) if "\n" in p["text"].strip() else [render_text(p)]
    month = p["d"][:7]
    var = pick_variant(p, n, L, ars, len(paras))
    if month not in SPREAD_USED and rs == 3 and n >= 2 and L >= 80:
        SPREAD_USED.add(month)
        var = "spread"
    rot = jitter(p["id"], -1.3, 1.3, "r")
    dy = jitter(p["id"], 0, 12, "y")
    paper = int(hv(p["id"], "paper") * 4)
    stks, extra = stickers_for(ws, sp)
    inside, outside = place(p, stks, n > 0 and var not in ("mag", "spread"))
    search = " ".join([p["text"], cap, ocr, " ".join(topics)])
    cls = f"fr fr-v-{var}" + (f" fr-p{paper}" if var == "note" else "") + (" has-stk" if stks else "")
    attrs = (f'class="{cls}" id="f-{p["id"]}" '
             f'data-d="{p["d"][:10]}" data-c="{cat}" data-r="{rs}" data-i="{1 if n else 0}" data-k="{ktok}" '
             f'data-s="{esc_attr(search.lower())}" style="--c:{CATS.get(cat, "#999")};--rot:{rot:.2f}deg;--dy:{dy:.0f}px"')
    h = [f"<article {attrs}>"]
    meta = f'<time>{p["d"][5:16].replace("-", "·", 1)}</time>'
    if cat:
        meta += f'<b class="fr-cat">{cat}</b>'
    h.append(f'<header class="fr-meta">{meta}</header>')
    mid = p.get("mid")
    tail = ""
    if mid in mid_to_art:
        tail = f'<br><a class="fr-art" href="{{% post_url {article_post_name(mid_to_art[mid])} %}}">→ 这条的长文已收入站内文章</a>'
    text_html = "<br>\n".join(paras)
    text_div = f'<div class="fr-text">{text_html}{tail}</div>'
    capline = f'<p class="fr-cap">{html.escape(esc_liquid(cap), quote=False)}</p>' if cap else ""
    more = f'<span class="fr-more">+{n - len(shown)}</span>' if n > len(shown) else ""

    def box(inner, c):
        return f'<div class="fr-imgs {c}">{inner}{inside}{more}</div>'

    if var == "note":
        pass
        h.append(text_div)
    elif var == "hero":
        h += [box(fig(shown[0]), "im-hero"), text_div, capline]
    elif var == "float":
        h += [f'<div class="fr-flow">{box(fig(shown[0]), "im-float")}{text_html}{tail}</div>', capline]
    elif var == "pol":
        pc = html.escape(esc_liquid(cap or ""), quote=False)
        h += [text_div, box(f'{fig(shown[0])}<span class="pol-cap">{pc}</span>', "im-pol")]
    elif var == "tape":
        h += [text_div, box(fig(shown[0]), "im-tape"), capline]
    elif var == "pair":
        h += [text_div, box(row(shown[:2]), "im-pair"), capline]
    elif var == "overlap":
        h += [text_div, box("".join(fig(r, "ov") for r in shown[:3]), "im-overlap"), capline]
    elif var == "strip":
        h += [text_div, box(row(shown[:3] if n == 3 else shown[:4]), "im-strip"), capline]
    elif var == "grid":
        h += [text_div, box(row(shown[:2]) + row(shown[2:4]), "im-grid"), capline]
    elif var == "mosaic":
        h += [text_div, box(fig(shown[0]) + row(shown[1:4]) + (row(shown[4:6]) if n > 4 else ""), "im-mosaic"), capline]
    elif var in ("mag", "spread"):
        k = min(len(shown), max(1, len(paras)))
        parts = []
        for i, para in enumerate(paras):
            parts.append(f'<p class="fr-para">{para}</p>')
            if i < k:
                parts.append(f'<div class="fr-figure fr-fig-{i % 2}">{fig(shown[i])}</div>')
        rest = shown[k:]
        body = "".join(parts) + (row(rest) if rest else "")
        if tail:
            body += f'<p class="fr-para">{tail[4:]}</p>'
        wrap = "fr-spread-body" if var == "spread" else "fr-mag"
        h += [f'<div class="{wrap}">{body}</div>', f'<div class="fr-imgs im-inline">{inside}{more}</div>', capline]
    if n and len(ocr) >= 6 and var != "note":
        snip = re.sub(r"\s+", " ", ocr)[:60]
        h.append(f'<p class="fr-ocr" title="模型转写的图中文字">▤ {html.escape(esc_liquid(snip), quote=False)}</p>')
    if topics:
        h.append('<p class="fr-topics">' + " ".join(f"#{html.escape(esc_liquid(t), quote=False)}" for t in topics) + "</p>")
    if p.get("video"):
        h.append('<p class="fr-vnote">（原帖含视频，存档未收录）</p>')
    link = f' · <a href="https://m.weibo.cn/detail/{mid}" rel="nofollow noopener" target="_blank">原微博</a>' if mid else ""
    ex = f' <span class="st-more">+{extra}</span>' if extra else ""
    h.append(f'<footer class="fr-foot">♥ {p["likes"]}{link}{ex}</footer>')
    h.append(outside)
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
    '长文已经单独收进站内文章（<a href="/long-analysis/">专题「长文分析」</a>）。<br><span class="fr-ai">分类、图注与图中文字由模型（Qwen）生成，可能有误；每条的「原微博」链接可对照原帖。</span></p>',
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
    group = [cards_html[p["id"]] for p in ps]
    # the month's feature spread (full width) goes first so the narrow cards fill the columns below it
    group.sort(key=lambda c: 0 if "fr-v-spread" in c.split(">", 1)[0] else 1)
    body += group
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

# the home page's 随手发的东西 card draws its covers from this page's stickers
import subprocess  # noqa: E402
subprocess.run([sys.executable, str(ROOT / "tools" / "build-weibo-covers.py")], check=True)
