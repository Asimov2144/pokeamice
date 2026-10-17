"""Shared helpers for the Weibo archive builders (tools/build-weibo-posts.py,
tools/build-weibo-notes.py).

Long articles come from the logged-in re-capture (fetched/art2_<id>.json: styled HTML with
real link targets). This module turns that HTML into something a Jekyll page can carry:
CDN image URLs, quoted-weibo cards rebuilt as plain quote blocks, near-black/near-white
colours dropped (the site is light grey), videos replaced with a note, Liquid braces escaped.
"""
import html, json, os, re
from pathlib import Path
from bs4 import BeautifulSoup

WORK = Path("P:/weibo/_work")
ART2 = WORK / "fetched"
CDN = "https://gallery.pokeamice.com/weibo-notes/"
COS = set(os.listdir(WORK / "cos")) if (WORK / "cos").is_dir() else set()

NOHREF = re.compile(r'<a(?:\s+href="javascript:;")?\s*>(.*?)</a>')
TAGSPAN = r'<span class="wbn-tag">\1</span>'
CARD_DATE = re.compile(r"\d{4}年\d+月\d+日 \d+:\d+")


def esc_liquid(s):
    # Liquid would try to parse these inside page content.
    return s.replace("{", "&#123;").replace("}", "&#125;")


def img_url(rel):
    return CDN + rel.rsplit("/", 1)[-1]


def normalize_imgs(h):
    """Weibo CDN image URLs -> img_articles/<file> once the file is on COS."""
    def r(m):
        return f'src="img_articles/{m.group(1)}"' if m.group(1) in COS else m.group(0)
    return re.sub(r'src="https?://[^"/]*sinaimg\.cn/[^"/]+/([^"?/]+)"', r, h)


def convert_cards(h):
    """Weibo's article editor embeds quoted posts as header/article/footer div soup whose
    classes were stripped on capture; rebuild each one as a plain quote block."""
    soup = BeautifulSoup(h, "html.parser")
    for head in list(soup.find_all("header")):
        box = head.parent
        art = box.find("article") if box else None
        if art is None:
            continue
        parts = [t for t in head.get_text("|", strip=True).split("|") if t]
        author = parts[0] if parts else ""
        m = CARD_DATE.search(head.get_text(" ", strip=True))
        when = m.group(0) if m else ""
        source = parts[-1] if len(parts) > 3 else ""
        body_div = next((d for d in art.find_all("div") if d.find("span", recursive=False)), None)
        text, cut = [], False
        if body_div is not None:
            for ch in body_div.children:
                name = getattr(ch, "name", None)
                if name == "span":
                    for im in ch.find_all("img"):
                        im.decompose()
                    text.append(ch.decode_contents())
                elif name == "a":
                    if ch.get_text(strip=True) == "全文":
                        cut = True
                    else:
                        for im in ch.find_all("img"):
                            im.decompose()
                        text.append(str(ch))
        imgs = []
        for im in art.find_all("img"):
            src = im.get("src", "")
            if src.startswith("img_articles/") and src not in imgs:
                imgs.append(src)
        vid = art.find("video") is not None
        out = ['<aside class="wbn-quote">',
               f'<p class="wbn-quote-head"><strong>{html.escape(author, quote=False)}</strong> <time>{when}</time>'
               + (f" · 来自 {html.escape(source, quote=False)}" if source else "") + "</p>",
               f'<div class="wbn-quote-body">{NOHREF.sub(TAGSPAN, "".join(text)).strip()}'
               + ("<br>（引用的微博摘要，原帖较长，此处被截断）" if cut else "") + "</div>"]
        if imgs:
            out.append('<div class="wbn-imgs wbn-imgs-%d">' % min(len(imgs), 4) + "".join(f'<img src="{i}" alt="">' for i in imgs) + "</div>")
        if vid:
            out.append('<p class="wbn-note">（含视频，存档未收录）</p>')
        out.append("</aside>")
        new = BeautifulSoup("".join(out), "html.parser")
        outer = box
        while outer.parent is not None and outer.parent.name == "div" and len(outer.parent.find_all(True, recursive=False)) == 1:
            outer = outer.parent
        outer.replace_with(new)
    return str(soup)


def _rgb(v):
    v = v.strip().lower()
    m = re.match(r"#([0-9a-f]{6}|[0-9a-f]{3})$", v)
    if m:
        x = m.group(1)
        x = "".join(c * 2 for c in x) if len(x) == 3 else x
        return tuple(int(x[i:i + 2], 16) for i in (0, 2, 4))
    m = re.match(r"rgba?\(\s*(\d+)[ ,]+(\d+)[ ,]+(\d+)", v)
    return tuple(int(g) for g in m.groups()) if m else None


def tidy_style(style):
    """Keep chromatic colours and layout hints; drop near-black / near-white text and
    backgrounds so the page still reads on the site's light grey."""
    keep = []
    for d in style.split(";"):
        if ":" not in d:
            continue
        k, v = (x.strip() for x in d.split(":", 1))
        if k in ("color", "background-color"):
            c = _rgb(v)
            if c is None or max(c) - min(c) < 40:
                continue
        keep.append(f"{k}:{v}")
    return ";".join(keep)


def finish_article(h):
    soup = BeautifulSoup(h, "html.parser")
    for v in soup.find_all("video"):
        note = soup.new_tag("p")
        note["class"] = "wbn-note"
        note.string = "（原文此处为视频，存档未收录）"
        v.replace_with(note)
    for t in soup.find_all(True):
        if t.get("style") is not None:
            st = tidy_style(t["style"])
            if st:
                t["style"] = st
            else:
                del t["style"]
        if t.name == "font" and t.get("color"):
            c = _rgb(t["color"])
            if c is None or max(c) - min(c) < 40:
                del t["color"]
        if t.name == "a" and t.get("href", "").startswith("http"):
            t["target"] = "_blank"
            t["rel"] = "nofollow noopener"
    return str(soup)


def article_html(a):
    """Final body HTML for one long article record from dataset.json."""
    f2 = ART2 / f"art2_{a['id']}.json"
    src = json.load(open(f2, encoding="utf-8"))["html"] if f2.exists() else a["html"]
    h = finish_article(convert_cards(normalize_imgs(src)))
    h = re.sub(r'src="img_articles/([^"]+)"', lambda m: f'src="{CDN}{m.group(1)}" loading="lazy"', h)
    h = re.sub(r'<img src="https://tvax[^"]*">', "", h).replace('href="javascript:;"', "")
    return esc_liquid(h.replace("\u200b", ""))
