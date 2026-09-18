"""Bring a web-published interview into _posts: a magazine site, an official
site, or a Wayback copy of either.

    python tools/import-web.py --list                     # the targets in design/import_web_targets_2026-09.json
    python tools/import-web.py gi-2019-dexit --dry-run    # fetch, parse, print the turns, write .items.json
    python tools/import-web.py gi-2019-dexit              # + translate + write the post
    python tools/import-web.py --all [--dry-run]
    python tools/import-web.py --targets=design/import_web_targets_2026-09b.json kotaku-2016-popplio
A target may also carry `max_images` (default 10 - a lecture report's slides need more),
`slug` (the post's file stem, to re-import over an existing post), `categories`, and
`stop_at` (a heading regex: the page's own index after the piece is cut there), and
`images_live` (the pictures from their live addresses although the page is a Wayback copy -
a CDN that outlived the site, like Kinja's), `unmarked: question` (a paragraph with no
speaker's name is the interviewer's - a page that labels every answer), and `drop` (a regex:
blocks whose text, alt or address match it are left out).

Where import-nom.py knows one page family, this one has to read whatever
the site did: the article container is found by weight (the element whose
<p> descendants carry the most text, narrowed to the tightest such
element), then walked in document order for headings, paragraphs,
<br>-separated runs, list items, block quotes and photographs. A target can
still pin the container with a `container` selector when the weight picks
the wrong thing.

Speakers are read from the text in the way each language writes an
interview - `――` / `4Gamer：` / `増田氏：` / `増田　` in Japanese, `Masuda:`
/ `GI:` / a bold paragraph in English, `jeuxvideo.com >` in French - and
mapped to the Chinese names the target declares. A paragraph with no
prefix continues the turn before it, but only in a question-and-answer
piece; in a feature or a lecture report it stays narrative.

Translation is DeepSeek with the project glossary, the way import-nom.py
does it; the original is kept from the page, never echoed back through the
model. The model also proposes the Chinese title, dek and summary.
"""
import html as htmlmod
import importlib.util
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, Comment, NavigableString, Tag

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "_posts"
IMG_DIR = ROOT / "assets" / "img" / "interviews"
CACHE = ROOT / "data" / "cache_web"
TARGETS_FILE = ROOT / "design" / "import_web_targets_2026-09.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "ja,en;q=0.8,zh;q=0.6"}

# the N.O.M importer already has the DeepSeek call, the glossary and the era table
_spec = importlib.util.spec_from_file_location("import_nom", ROOT / "tools" / "import-nom.py")
_nom = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_nom)
deepseek, load_glossary, glossary_hits, era_for = _nom.deepseek, _nom.load_glossary, _nom.glossary_hits, _nom.era_for

LANG_NAME = {"ja": "日文", "en": "英文", "fr": "法文", "it": "意大利文", "de": "德文"}
DIALOGUE_KINDS = {"interview"}
ASKERS = {"4gamer", "ファミ通", "週刊ファミ通", "編集部", "記者", "インサイド", "inside", "oricon", "電ファミ", "東洋経済", "cgworld",
          "聞き手", "game informer", "gi", "polygon", "kotaku", "vg247", "nintendo life", "nl", "pokemon.com", "q", "ｑ", "question",
          "jeuxvideo.com", "multiplayer.it", "ーー", "――", "──", "——"}
NOISE_CLASS = re.compile(r"(?:^|[-_ ])(ads?|advert\w*|sponsor\w*|share|social|sns|related|recommend\w*|sidebar|comments?|breadcrumbs?|"
                         r"newsletter|promo\w*|banner|pager|pagination|widget|cta|tags?|taglist|author[-_]?box|profile[-_]?box|"
                         r"outbrain|taboola|popular|ranking|footer|header|nav|menu|modal|cookie|subscribe|amazon|affiliate)(?:$|[-_ ])", re.I)
# where a site keeps the full-size file of the picture it shows small
FULLSIZE = [(r"(/games/\d+/G\d+/\d+/)TN/(\d+\.jpg)$", r"\g<1>SS/\g<2>"),               # 4Gamer
            (r"^(https?://image\.gamer\.ne\.jp/.*/)m/(\d+\.jpg)$", r"\g<1>o/\g<2>")]    # gamer.ne.jp
IMG_NOISE = re.compile(r"(logo|icon|avatar|button|spacer|pixel|1x1|badge|banner|share|ad[-_]|counter|arrow|blank\.gif|loading|dummy|placeholder|hubcoverage)", re.I)
BLOCK_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "li", "dt", "dd", "blockquote", "figure", "figcaption", "img", "pre", "table",
              "div", "section", "article", "main", "td", "tr", "tbody", "ul", "ol", "dl", "center", "font", "span", "body", "header"}


# ---------------------------------------------------------------- targets / fetch
def load_targets(path=None):
    doc = json.loads((path or TARGETS_FILE).read_text(encoding="utf-8"))
    return {t["key"]: t for t in doc["targets"]}


def fetch(target):
    """The page, cached under data/cache_web; the Wayback copy when the target names one."""
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"{target['key']}.html"
    if out.exists() and out.stat().st_size > 2000:
        return out.read_text(encoding="utf-8")
    url = target.get("wayback") or target["url"]
    req = urllib.request.Request(url, headers={**UA, "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            import gzip
            data = gzip.decompress(data)
    m = re.search(rb'charset=["\']?([\w-]+)', data[:4000])
    enc = m.group(1).decode() if m else "utf-8"
    try:
        text = data.decode(enc, "replace")
    except LookupError:
        text = data.decode("utf-8", "replace")
    out.write_text(text, encoding="utf-8", newline="\n")
    return text


def fetch_image(src, page_url, wayback, dest_dir, index, images_live=False):
    """A photograph saved under assets/img/interviews/<slug>/; through the same
    Wayback snapshot (im_) when the page itself came from there."""
    src = re.sub(r"^https?://web\.archive\.org/web/\d+[a-z_]*/", "", src)
    absolute = urllib.parse.urljoin(page_url, src)
    name = urllib.parse.unquote(absolute.split("?")[0].rsplit("/", 1)[-1])
    ext = Path(name).suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        ext = ".jpg"
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / f"{index:03d}{ext}"
    if not out.exists():
        url = absolute
        if wayback and not images_live:
            ts = re.search(r"/web/(\d+)", wayback).group(1)
            url = f"https://web.archive.org/web/{ts}im_/{absolute}"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data = r.read()
            if len(data) < 3000:          # a tracking pixel or a broken thumbnail
                return None
            out.write_bytes(data)
            time.sleep(0.8)
        except Exception as exc:
            print(f"    image {name}: {exc}")
            return None
    return "/" + out.relative_to(ROOT).as_posix()


# ---------------------------------------------------------------- extract
def parse(html):
    """lxml closes the <p> a site forgot to; but on a malformed Wayback page it
    can also lose most of the body, so the plain parser wins when it keeps more."""
    a = BeautifulSoup(html, "lxml")
    b = BeautifulSoup(html, "html.parser")
    return b if len(b.get_text()) > 1.3 * len(a.get_text()) else a


def strip_noise(soup):
    # a nav / footer / aside that wraps the article itself (Kinja put the whole page in a <nav>) stays
    body_w = p_weight(soup.body or soup)
    for sel in ("script", "style", "noscript", "iframe", "svg", "button", "nav", "footer", "aside", "template", "ins", "object", "embed", "video", "audio"):
        for el in soup.find_all(sel):
            if sel in ("nav", "footer", "aside") and body_w and p_weight(el) > body_w * 0.3:
                continue
            el.decompose()
    for el in soup.find_all(id=re.compile(r"^wm-ipp|^donato|^playback")):
        el.decompose()
    for el in list(soup.find_all(True)):
        if not isinstance(el, Tag) or el.decomposed or el.attrs is None:
            continue
        ident = " ".join(el.get("class", []) if isinstance(el.get("class"), list) else [el.get("class", "")]) + " " + (el.get("id") or "")
        if el.name in ("article", "main", "body", "img", "picture", "source", "figure") or not ident.strip():
            continue                                  # media is judged by its address, not its class
        if NOISE_CLASS.search(ident) and not re.search(r"(article|entry|post|body|content|main|text)", ident, re.I):
            if body_w and p_weight(el) > body_w * 0.3:      # it wraps the article
                continue
            el.decompose()


def p_weight(el):
    return sum(len(p.get_text(" ", strip=True)) for p in el.find_all("p"))


def find_container(soup, target):
    if target.get("container"):
        found = soup.select(target["container"])
        if found:
            return max(found, key=p_weight)      # the selector may match a comments widget too
        print(f"    container {target['container']!r} not found, falling back to weight")
    best, best_w = soup.body or soup, p_weight(soup.body or soup)
    if best_w == 0:
        return best
    changed = True
    while changed:
        changed = False
        for child in best.find_all(recursive=False):
            if not isinstance(child, Tag):
                continue
            w = p_weight(child)
            if w >= best_w * 0.85:
                best, best_w, changed = child, w, True
                break
    return best


def split_br(el, join_br=False):
    """The text of an element as paragraphs, a <br> run being a break; each
    part with whether all of its text sits inside <strong>/<b>. A site that
    breaks its lines typographically (ほぼ日 sets every clause on its own
    line) passes join_br, and a <br> is then nothing at all."""
    parts, cur, bold = [], [], []
    for node in el.descendants:
        if isinstance(node, Tag) and node.name == "br":
            if join_br:
                continue
            parts.append(("".join(cur), bool(bold) and all(bold)))
            cur, bold = [], []
        elif isinstance(node, NavigableString) and not isinstance(node, Comment):
            if str(node).strip():
                bold.append(any(a.name in ("strong", "b") for a in node.parents if a is not el and a is not None) or el.name in ("strong", "b"))
            cur.append(str(node))
    parts.append(("".join(cur), bool(bold) and all(bold)))
    return [(re.sub(r"[ \t\r\n\u3000]+", " ", t).strip(), b) for t, b in parts if t.strip()]


def srcset_last(srcset):
    """the last candidate of a srcset - candidates are split at ", " before a URL, never at
    the commas inside a URL (Cloudinary's c_scale,q_80,w_800/...)"""
    cands = [c.strip() for c in re.split(r",\s+(?=(?:https?:)?/)", srcset.strip()) if c.strip()]
    return cands[-1].split()[0] if cands else ""


def extract_blocks(container, join_br=False):
    """Headings, paragraphs and images of the container in reading order."""
    blocks = []

    def emit_text(el, quote=False):
        for t, b in split_br(el, join_br):
            if len(t) >= 2:
                blocks.append({"t": "text", "x": t, "bold": b, "quote": quote})

    def emit_img(el, caption=""):
        src = el.get("data-src") or el.get("data-original") or el.get("src") or ""
        # a lazy picture: the largest <source> of its <picture>, else its srcset's last candidate
        pic = el.find_parent("picture")
        if pic is not None:
            cands = [srcset_last(s.get("data-srcset") or s.get("srcset") or "") for s in pic.find_all("source")]
            cands = [c for c in cands if c]
            if cands:
                src = cands[-1]
        elif (not src or src.startswith("data:")) and (el.get("data-srcset") or el.get("srcset")):
            src = srcset_last(el.get("data-srcset") or el.get("srcset"))
        # the noise words are judged on the file name only: Game Informer keeps its pictures under the
        # article's title ("...Directors Share Their Favorite...") and "share" is not a share button there
        if not src or src.startswith("data:") or IMG_NOISE.search(src.rsplit("/", 1)[-1]):
            return
        # a thumbnail wrapped in a link to its full-size file (WordPress "link to media"), or opening it
        # from an onclick (4Gamer's OVERLAY_SS_open('/SS/002.jpg')), or kept at a sibling address: take the file
        link = el.find_parent("a")
        href = (link.get("href") or "") if link is not None else ""
        if re.search(r"\.(?:jpe?g|png|gif|webp)(?:\?[^#]*)?$", href, re.I) and not IMG_NOISE.search(href):
            src = href
        m_click = re.search(r"['\"]([^'\"]+\.(?:jpe?g|png|webp))['\"]", el.get("onclick") or "", re.I)
        if m_click:
            src = m_click.group(1)
        for pat, rep in FULLSIZE:
            src = re.sub(pat, rep, src)
        try:
            w = int(re.sub(r"\D", "", str(el.get("width") or "0")) or 0)
            h = int(re.sub(r"\D", "", str(el.get("height") or "0")) or 0)
        except ValueError:
            w = h = 0
        if (0 < w < 120) or (0 < h < 120):
            return
        blocks.append({"t": "img", "src": src, "alt": (el.get("alt") or "").strip(), "cap": caption.strip()})

    def walk(el, quote=False):
        if isinstance(el, NavigableString):
            return
        name = el.name
        if name in ("h1", "h2", "h3", "h4", "h5"):
            txt = el.get_text(" ", strip=True)
            if not txt and el.find("img"):        # a heading set as a picture: its alt is the text
                txt = (el.find("img").get("alt") or "").strip()
            if txt:
                blocks.append({"t": "h", "x": re.sub(r"\s+", " ", txt), "level": 2 if name in ("h1", "h2") else 3})
            return
        if name == "img":
            emit_img(el)
            return
        if name == "figure":
            cap = el.find("figcaption")
            cap_t = cap.get_text(" ", strip=True) if cap else ""
            for im in el.find_all("img"):
                emit_img(im, cap_t)
                break
            return
        if name == "figcaption":
            return
        if name == "dl":
            # a definition list as dialogue (ほぼ日): <dt> is the speaker, the <dd>s are the turn;
            # the label is put in front of every <dd> so each paragraph reads like a marked line
            # (a question there runs over several <dd>s, which an unmarked paragraph would not keep)
            label = None
            for k in el.children:
                if not isinstance(k, Tag):
                    continue
                if k.name == "dt":
                    label = k.get_text(" ", strip=True)
                elif k.name == "dd":
                    for im in k.find_all("img"):
                        emit_img(im)
                    for tx, b in split_br(k, join_br):
                        if label:
                            tx = (label + " " + tx) if re.match(r"^[―─—–\-]+$", label) else (label + "：" + tx)
                        if len(tx) >= 2:
                            blocks.append({"t": "text", "x": tx, "bold": b, "quote": quote})
            return
        if name in ("p", "li", "dd", "dt", "pre"):
            for im in el.find_all("img"):
                emit_img(im)
            emit_text(el, quote)
            return
        if name == "blockquote":
            for k in el.children:
                if isinstance(k, Tag):
                    walk(k, True)
                elif str(k).strip():
                    blocks.append({"t": "text", "x": re.sub(r"\s+", " ", str(k)).strip(), "bold": False, "quote": True})
            return
        if name in BLOCK_TAGS or name is None:
            # a container: block children walked, loose inline text gathered as its own paragraphs
            loose = []
            for k in el.children:
                if isinstance(k, Tag) and (k.name in BLOCK_TAGS and k.name not in ("span", "font", "center")):
                    if loose:
                        flush(loose, quote)
                        loose = []
                    walk(k, quote)
                else:
                    loose.append(k)
            if loose:
                flush(loose, quote)

    def flush(nodes, quote):
        wrapper = BeautifulSoup("<div></div>", "lxml").div
        for n in nodes:
            if isinstance(n, Comment):
                continue
            wrapper.append(n.__copy__() if isinstance(n, Tag) else NavigableString(str(n)))
        for im in wrapper.find_all("img"):
            emit_img(im)
        for t, b in split_br(wrapper, join_br):
            if len(t) >= 2:
                blocks.append({"t": "text", "x": t, "bold": b, "quote": quote})

    walk(container)
    return blocks


# ---------------------------------------------------------------- items
DASH_Q = re.compile(r"^\s*(?:[―─—–‐\-]{1,3}|——|――|──)\s*(.+)$")
JA_NAME = re.compile(r"^\s*([^\s：:　（(]{1,12}?)\s*(?:氏|さん|社長|様|先生)?\s*(?:（[^）]{0,20}）)?\s*[：:]\s*(.+)$")
JA_SPACE = re.compile(r"^\s*([一-鿿゠-ヿ]{1,5})[　 ]\s*(\S.+)$")
EN_NAME = re.compile(r"^\s*([A-Z][A-Za-z.'’\- ]{0,30}?)\s*:\s+(.+)$")     # {0,30}: a lone "Q:" counts
FR_Q = re.compile(r"^\s*jeuxvideo\.com\s*>\s*(.+)$", re.I)
FR_NAME = re.compile(r"^\s*([A-Z][A-Za-z\- ]{2,30}?)\s*:\s*(.+)$")


def match_speaker(name, target):
    """The declared Chinese name for a surname / alias the page uses, or None."""
    n = name.strip().rstrip("氏").strip()
    for alias, zh in target["speakers"].items():
        if n == alias or n.lower() == alias.lower() or (len(alias) >= 3 and (n.endswith(alias) or alias.endswith(n)) and len(n) >= 2):
            return zh
    return None


def is_asker(name, target):
    n = name.strip().lower()
    aliases = [a.lower() for a in target.get("asker_aliases", [])]
    return n in ASKERS or n in aliases or n == target.get("asker", "").lower() or n.startswith(target.get("asker", "\0").lower())


SPEAKER_LINE = re.compile(r"^\s*([^\s：:　]{1,12}?)\s*(?:氏|さん|社長)?\s*(?:（[^）]{0,24}）)?\s*[：:]?\s*$")


def to_items(blocks, target, slug, dry):
    """Blocks to parallel_items: role and speaker read from the text."""
    lang, kind = target["lang"], target.get("kind", "interview")
    dialogue = kind in DIALOGUE_KINDS
    solo = list(target["speakers"].values())
    solo = solo[0] if len(set(solo)) == 1 else None
    items, last_role, last_speaker, n_img = [], None, None, 0
    pending, seen_heading, alt_turn = None, False, 0
    wayback = target.get("wayback")
    dest = IMG_DIR / slug
    for b in blocks:
        if b["t"] == "h":
            items.append({"type": "heading", "level": b["level"], "original": b["x"]})
            last_role = last_speaker = pending = None
            seen_heading = True
            continue
        if b["t"] == "img":
            if n_img >= int(target.get("max_images") or 10):
                continue
            n_img += 1
            if dry:
                items.append({"type": "image", "image": b["src"], "caption": b["cap"], "alt": b["alt"]})
                continue
            local = fetch_image(b["src"], target["url"], wayback, dest, n_img, bool(target.get("images_live")))
            if local:
                it = {"type": "image", "image": local, "alt": b["alt"] or target["title"]}
                if b["cap"]:
                    it["caption"] = b["cap"]
                items.append(it)
            continue
        text = b["x"]
        # a speaker's name on a line of its own (Famitsu 2026, Gpara) names the next paragraph
        m = SPEAKER_LINE.match(text)
        if m and len(text) <= 14 and match_speaker(m.group(1), target):
            pending = match_speaker(m.group(1), target)
            # the paragraph before a lone speaker line is the question it answers
            if items and items[-1].get("type") is None and not items[-1].get("_explicit") and dialogue:
                items[-1]["role"], items[-1]["speaker"] = "question", target.get("asker") or ""
            continue
        role, speaker, body = None, None, text
        if pending:
            role, speaker, pending = "answer", pending, None
        elif target.get("all_answers_by") and seen_heading:
            role, speaker, body = "answer", target["all_answers_by"], re.sub(r"^[－―─—–\-]\s*", "", text)
        elif lang == "ja":
            m = DASH_Q.match(text)
            if m:
                role, speaker, body = "question", None, m.group(1)
            else:
                m = JA_NAME.match(text) or None
                if m and (match_speaker(m.group(1), target) or is_asker(m.group(1), target)):
                    zh = match_speaker(m.group(1), target)
                    if zh:
                        role, speaker, body = "answer", zh, m.group(2)
                    else:
                        role, speaker, body = "question", None, m.group(2)
                else:
                    m = JA_SPACE.match(text)
                    if m and match_speaker(m.group(1), target):
                        role, speaker, body = "answer", match_speaker(m.group(1), target), m.group(2)
        elif lang == "fr":
            m = FR_Q.match(text)
            if m:
                role, speaker, body = "question", None, m.group(1)
            else:
                m = FR_NAME.match(text)
                if m and match_speaker(m.group(1), target):
                    role, speaker, body = "answer", match_speaker(m.group(1), target), m.group(2)
        else:  # en / it
            m = EN_NAME.match(text)
            if m and match_speaker(m.group(1), target):
                role, speaker, body = "answer", match_speaker(m.group(1), target), m.group(2)
            elif m and is_asker(m.group(1), target):
                role, speaker, body = "question", None, m.group(2)
            elif dialogue and b["bold"] and len(text) < 400 and target.get("bold_question", True):
                role, speaker, body = "question", None, text      # bold_question: false on a page whose captions are bold too
        explicit = role is not None
        if role is None and target.get("unmarked") == "question" and seen_heading:
            # every answer on the page carries its speaker's name; a bare paragraph is the interviewer (Creatures' SPECIAL TALK)
            role, speaker = "question", None
        if role is None and target.get("alternate") and seen_heading and last_role:
            # question and answer alternate with no marks at all (Multiplayer.it)
            role, speaker = ("answer", solo) if last_role == "question" else ("question", None)
        sentence = len(text) >= 40 or re.search(r"[。！？!?.」)）\"”]$", text)
        if role is None and dialogue and last_role == "question" and solo and sentence:
            role, speaker = "answer", solo          # one interviewee: what follows a question is the answer
        elif role is None and dialogue and last_role and sentence:
            role, speaker = last_role, last_speaker  # a paragraph with no prefix continues the turn before it
        it = {"original": body.strip()}
        if role == "question":
            it["role"] = "question"
            it["speaker"] = target.get("asker") or ""
        elif role == "answer":
            it["role"], it["speaker"] = "answer", speaker
        if b.get("quote") and role is None:
            it["quote"] = True
        if explicit:
            it["_explicit"] = True
        items.append(it)
        last_role, last_speaker = role, speaker
    return items


def tidy(items):
    """Drop the lines a site leaves around an article, merge a heading that
    repeats the title, and give consecutive same-speaker turns their own lines."""
    out = []
    junk = re.compile(r"^(この記事の写真|写真ページを見る|ADの後に|Play$|Unmute$|00:00|Remove Ads|関連記事|Advertisement|Sponsored|Click here|Learn more at|"
                      r"Prefer .* on Google|Suivez-nous|Partager|LEGGI DOPO|SEGUI$|画像集|拡大画像|Image credit|Photo:|Screenshot:|Read more|"
                      r"More Great|Related Reading|©|\(c\)|\d+ 796 vues|Track this|This article|Here is a fact-based summary|Like$|Follow$|Add Us$|BY $|For more on .*(hub|coverage)|head to our hub|"
                      r"^(発売日|希望小売価格|発売|販売|開発|対応機種|ジャンル|価格|プレイ人数|CERO)[：:]|^(information|記事の目次|関連リンク|関連記事一覧|公式サイトはこちら|.*はこちら)$|^www\.|^https?://|^文／|^編集／|^取材・文／|^\[VIDEO)", re.I)
    for it in items:
        if it.get("type") in ("heading",) and len(it["original"]) < 2:
            continue
        if it.get("type") is None and (junk.search(it["original"]) or len(it["original"]) < 4):
            continue
        out.append(it)
    return out


# ---------------------------------------------------------------- translate
SYSTEM = ("你是宝可梦开发史料的译者，把{lang}访谈译成简体中文。译文忠实、平实、可读，不加渲染、不加感叹号、不改写语气；"
          "人名用通行中文译名，游戏名与专有名词优先采用提供的术语表；只输出合法 JSON。")


def translate_items(items, target, glossary):
    lang = LANG_NAME.get(target["lang"], target["lang"])
    text_items = [(i, x) for i, x in enumerate(items) if x.get("type") != "image"]
    full = "\n".join(x["original"] for _, x in text_items)
    hits = glossary_hits(full, glossary)
    gloss = "\n".join(f"- {s} → {t}" for s, t in hits) or "（无）"
    chunk = 10
    system = SYSTEM.format(lang=lang) + f"\n术语表：\n{gloss}"
    for start in range(0, len(text_items), chunk):
        part = text_items[start:start + chunk]
        payload = [{"i": i, "speaker": x.get("speaker", ""), "text": x["original"]} for i, x in part]
        prompt = (f"这是{target['outlet']} {target['date'][:4]}年的文章《{target['title']}》的一段（{lang}）。"
                  f"逐条把 text 译成简体中文，保留条目顺序与编号 i；说话人不用译；标题行照译。"
                  f"note 只在读者很可能不知道的具体事实上给一句（某个人是谁、某部作品或某件当年的事），一般留空字符串；不要解释宝可梦、任天堂这类常识。\n\n"
                  f"输出格式：{{\"items\":[{{\"i\":编号,\"translation\":\"译文\",\"note\":\"\"}}]}}\n\n"
                  f"待译：\n{json.dumps(payload, ensure_ascii=False)}")
        print(f"  translating {start + 1}-{start + len(part)} / {len(text_items)} ...", flush=True)
        got = None
        for attempt in range(3):
            raw = deepseek([{"role": "system", "content": system}, {"role": "user", "content": prompt}])
            try:
                got = {int(r["i"]): r for r in json.loads(raw).get("items", []) if "i" in r}
                break
            except (ValueError, TypeError) as exc:
                print(f"    bad JSON from the model (attempt {attempt + 1}): {exc}", file=sys.stderr)
        if got is None:
            raise RuntimeError("translation chunk failed three times")
        for i, x in part:
            r = got.get(i)
            if not r:
                print(f"    missing translation for item {i}", file=sys.stderr)
                x["translation"] = ""
                continue
            x["translation"] = str(r.get("translation", "")).strip()
            note = str(r.get("note", "") or "").strip()
            if note:
                x["note"] = note
        time.sleep(1)
    return items


def propose_cover(items, target):
    sample = "\n".join(f"{x.get('speaker', '')}: {x.get('translation', '')}" for x in items if x.get("type") != "image")[:6000]
    year = target["date"][:4]
    prompt = (f"下面是{target['outlet_zh']} {year}年的文章《{target['title']}》的中文译文节选。"
              f"给出：title（中文标题，形如「{target['outlet_zh']} {year}：……」，45字以内，写清受访者与主题，不用感叹号）、"
              f"display_title（封面用的一句短标题，20字以内）、dek（一句导语，60字以内）、summary（120字以内的内容提要，平实）。"
              f"输出 JSON：{{\"title\":\"\",\"display_title\":\"\",\"dek\":\"\",\"summary\":\"\"}}\n\n{sample}")
    raw = deepseek([{"role": "system", "content": SYSTEM.format(lang=LANG_NAME.get(target["lang"], ""))}, {"role": "user", "content": prompt}], max_tokens=800)
    return json.loads(raw)


# ---------------------------------------------------------------- write
KIND_SOURCE = {"interview": "media_interview", "interview_feature": "media_feature", "cover_story": "media_feature",
               "lecture_report": "lecture_report", "making": "making_feature", "event_report": "event_report"}


def write_post(target, items, cover, slug):
    year = target["date"][:4]
    official = "pokemon.co" in target["url"] or "nintendo.co" in target["url"]
    people = sorted({x["speaker"] for x in items if x.get("role") == "answer" and x.get("speaker")})
    if not people:
        people = sorted(set(target["speakers"].values()))
    fm = {
        "layout": "interview-editorial",
        "archive_type": "interview_translation",
        "title": cover.get("title") or f"{target['outlet_zh']} {year}：{target['title']}",
        "display_title": cover.get("display_title") or None,
        "dek": cover.get("dek") or None,
        "original_title": target["title"],
        "date": target["date"],
        "era_skin": era_for(year),
        "categories": target.get("categories") or (["访谈翻译", "官方档案"] if official else ["访谈翻译", "翻译", "访谈整理"]),
        "tags": ["访谈", "Game Freak"] + target["tags"],
        "publication": f"{target['outlet_zh']}（{target['date']}）",
        "source_kind": KIND_SOURCE.get(target.get("kind"), "media_interview"),
        "author": target.get("author") or None,
        "interviewer": target.get("author") or target.get("asker") or target["outlet"],
        "interviewee": "、".join(sorted(set(target["speakers"].values()))),
        "translator": "PokeAmice（DeepSeek 初译）",
        "original_lang": target["lang"],
        "translation_lang": "zh-CN",
        "source": {"title": target["title"], "url": target["url"], "language": target["lang"],
                   "source_type": "official_web" if official else "media_interview"},
        "original_link": target["url"],
        "source_url": target.get("wayback") or None,
        "summary": cover.get("summary") or None,
        "entities": {"people": people, "works": target.get("works", [])},
        "workflow": {"fetch": "wayback" if target.get("wayback") else "live", "translation": "deepseek-chat", "proofreading": "pending", "published": "draft"},
        "parallel_items": [{k: v for k, v in x.items() if not k.startswith("_")} for x in items],
    }
    if target.get("series"):
        fm["series"] = target["series"]
        fm["series_part"] = target.get("part")
    fm = {k: v for k, v in fm.items() if v is not None}
    path = POSTS / f"{slug}.md"
    path.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n", encoding="utf-8", newline="\n")
    return path


# ---------------------------------------------------------------- run
flags_limit = 60


def run(key, targets, dry, glossary):
    target = targets[key]
    slug = target.get("slug") or f"{target['date']}-interview-{key}"
    print(f"== {key}: {target['title'][:60]}")
    blocks = []
    for n, url in enumerate([None] + target.get("pages", [])):
        t = target if url is None else {**target, "key": f"{target['key']}_p{n + 1}", "url": url, "wayback": None}
        soup = parse(fetch(t))
        strip_noise(soup)
        container = find_container(soup, target)
        blocks += extract_blocks(container, join_br=bool(target.get("join_br")))
    # what the page carries besides the piece: a date stamp, the next installment's thumbnail
    # the page's own index / navigation after the piece: cut at the heading that opens it
    if target.get("stop_at"):
        stop = re.compile(target["stop_at"])
        for n, b in enumerate(blocks):
            if b["t"] == "h" and stop.search(b.get("x") or ""):
                blocks = blocks[:n]
                break
    if target.get("drop"):
        drop = re.compile(target["drop"])
        blocks = [b for b in blocks if not drop.search(b.get("x") or "") and not drop.search(b.get("alt") or "") and not drop.search(b.get("src") or "")]
    items = tidy(to_items(blocks, target, slug, dry))
    n_q = sum(1 for x in items if x.get("role") == "question")
    n_a = sum(1 for x in items if x.get("role") == "answer")
    n_h = sum(1 for x in items if x.get("type") == "heading")
    n_i = sum(1 for x in items if x.get("type") == "image")
    n_p = len(items) - n_q - n_a - n_h - n_i
    chars = sum(len(x.get("original", "")) for x in items)
    print(f"   container <{container.name} class={container.get('class')} id={container.get('id')}>  items {len(items)}: Q {n_q} / A {n_a} / heading {n_h} / image {n_i} / narrative {n_p}, {chars} chars")
    (CACHE / f"{key}.items.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    if dry:
        for x in items[:int(flags_limit)]:
            tag = x.get("type") or x.get("role") or "-"
            print(f"   [{tag:8}] {x.get('speaker', ''):8} {x.get('original', x.get('image', ''))[:90]}")
        if len(items) > int(flags_limit):
            print(f"   ... {len(items) - int(flags_limit)} more")
        return
    items = translate_items(items, target, glossary)
    cover = propose_cover(items, target)
    path = write_post(target, items, cover, slug)
    print(f"   wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    tf = next((f.split("=", 1)[1] for f in flags if f.startswith("--targets=")), None)
    targets = load_targets(Path(tf) if tf else None)
    if "--list" in flags:
        for k, t in targets.items():
            print(f"{k:32} {t['date']}  {t['lang']}  {t['outlet']:24} {t['title'][:60]}")
        sys.exit()
    keys = list(targets) if "--all" in flags else args
    for f in flags:
        if f.startswith("--limit="):
            flags_limit = int(f.split("=")[1])
    glossary = None if "--dry-run" in flags else load_glossary()
    for k in keys:
        if k not in targets:
            sys.exit(f"unknown target {k}")
        run(k, targets, "--dry-run" in flags, glossary)
