"""Bring an N.O.M (Nintendo Online Magazine, 1998-2008) interview into _posts.

    python tools/import-nom.py --list                 # the targets this script knows
    python tools/import-nom.py kubo-2000              # fetch, parse, translate, write
    python tools/import-nom.py kubo-2000 --dry-run    # parse only, print the turns

N.O.M is gone from nintendo.co.jp; every page here is read from the
Wayback Machine (the `id_` raw form, Shift_JIS). The pages are of one
family: a question is a line on its own, an answer is `名前>> text`, a
photograph is an <img> whose alt names the person, and the page opens with
the interviewee's title and name. That is parsed into parallel_items with
the roles already set - the question is asked by N.O.M, everything with a
`>>` is an answer - so the post goes straight onto interview-editorial.

Translation is DeepSeek with the project glossary, the way the other
importers do it; the Japanese is kept from the page, never echoed back
through the model. The model also proposes the Chinese title, a one-line
dek and a summary, which are written as display_title / dek / summary.

Targets are declared in TARGETS below, one per interview, with the pages
in reading order and the names as the page abbreviates them.
"""
import html
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "_posts"
IMG_DIR = ROOT / "assets" / "img" / "interviews"
CACHE = ROOT / "data" / "cache_nom"
GLOSSARY = Path("P:/WEBSITE/pokeamice/event/public/glossary-master.json")
UA = {"User-Agent": "Mozilla/5.0"}
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

TARGETS = {
    "kubo-2000": {
        "issue": "0006", "date": "2000-06-01", "no": "No.23",
        "pages": ["04/04c01.html", "04/04c02.html"],
        "title_ja": "ポケモンから広がる世界／「ポケモン大ヒットの秘密をさぐる」小学館 久保雅一さんインタビュー",
        "speakers": {"久保": "久保雅一"},
        "interviewee": "久保雅一",
        "org": "小学馆 / 小学馆Production",
        "works": ["宝可梦 动画系列", "超梦的逆袭", "宝可梦 红·绿"],
        "tags": ["N.O.M", "久保雅一", "小学馆", "动画", "剧场版", "海外展开", "CoroCoro"],
        "slug": "nom-2000-kubo-masakazu-pokemon-hit",
    },
    "ishihara-2001": {
        "issue": "0111", "date": "2001-11-01", "no": "No.40",
        "pages": ["03/index.html"],
        "title_ja": "未来へ広がるポケモンワールド／株式会社ポケモン 代表取締役社長 石原恒和氏インタビュー",
        "speakers": {"石原": "石原恒和"},
        "interviewee": "石原恒和",
        "org": "株式会社ポケモン",
        "works": ["宝可梦集换式卡牌游戏", "宝可梦 金·银", "宝可梦 水晶版"],
        "tags": ["N.O.M", "石原恒和", "株式会社ポケモン", "宝可梦卡牌e", "Pokémon mini"],
        "slug": "nom-2001-ishihara-tsunekazu-pokemon-world",
    },
    "card-e-2001": {
        "issue": "0111", "date": "2001-11-01", "no": "No.40",
        "pages": ["01/page02.html", "01/page03.html"],
        "title_ja": "未来へ広がるポケモンワールド／ポケモンカードe・カードeリーダー開発者インタビュー",
        "speakers": {"赤羽": "赤羽卓美", "入江": "入江胜义", "福田": "福田和彦", "吉野": "吉野元文"},
        "interviewee": "赤羽卓美、入江胜义",
        "org": "Creatures",
        "works": ["宝可梦集换式卡牌游戏"],
        "tags": ["N.O.M", "Creatures", "宝可梦卡牌e", "卡牌e读卡器", "赤羽卓美", "入江胜义"],
        "slug": "nom-2001-pokemon-card-e-creatures",
    },
    "mini-2001": {
        "issue": "0111", "date": "2001-11-01", "no": "No.40",
        "pages": ["02/page02.html"],
        "title_ja": "未来へ広がるポケモンワールド／ポケモンミニソフト開発者インタビュー",
        "speakers": {},
        "interviewee": "",
        "org": "",
        "works": ["Pokémon mini"],
        "tags": ["N.O.M", "Pokémon mini"],
        "slug": "nom-2001-pokemon-mini-developers",
    },
    "dp-2006": {
        "issue": "0610", "date": "2006-10-01", "no": "No.99",
        "pages": ["12/i01.html", "12/i02.html", "12/i03.html", "12/i04.html", "12/i05.html", "12/i06.html", "12/i07.html"],
        "title_ja": "『ポケットモンスター ダイヤモンド・パール』開発スタッフインタビュー",
        "speakers": {"杉森": "杉森建", "増田": "增田顺一", "石原": "石原恒和"},
        "interviewee": "石原恒和、增田顺一、杉森建",
        "org": "株式会社ポケモン / GAME FREAK",
        "works": ["宝可梦 钻石·珍珠", "宝可梦对战革命"],
        "tags": ["N.O.M", "钻石·珍珠", "石原恒和", "增田顺一", "杉森建", "Nintendo DS", "Wi-Fi", "宝可梦对战革命"],
        "slug": "nom-2006-diamond-pearl-ishihara-masuda-sugimori",
    },
    "channel-2003": {
        "issue": "0308", "date": "2003-08-01", "no": "No.61",
        "pages": ["p_inter/index.html", "p_inter/page01/index.html", "p_inter/page02/index.html", "p_inter/page03/index.html"],
        "title_ja": "『ポケモンチャンネル』開発スタッフインタビュー",
        "speakers": {"石原": "石原恒和"},
        "interviewee": "石原恒和",
        "org": "Ambrella",
        "works": ["宝可梦频道"],
        "tags": ["N.O.M", "宝可梦频道", "Ambrella", "GameCube"],
        "slug": "nom-2003-pokemon-channel-staff",
    },
    "rs-2002": {
        "issue": "0211", "date": "2002-11-01", "no": "No.52",
        "pages": ["01/01_05/index.html"],
        "title_ja": "『ポケットモンスタールビー・サファイア』発売記念特集／開発者よりみなさまへのメッセージ（増田順一・杉森建・石原恒和）",
        "speakers": {"増田": "增田顺一", "杉森": "杉森建", "石原": "石原恒和"},
        "sections": ["增田顺一", "杉森建", "石原恒和"],
        "interviewee": "增田顺一、杉森建、石原恒和",
        "org": "GAME FREAK / 株式会社ポケモン",
        "works": ["宝可梦 红宝石·蓝宝石"],
        "tags": ["N.O.M", "红宝石·蓝宝石", "增田顺一", "杉森建", "石原恒和", "Game Boy Advance", "华丽大赛", "秘密基地"],
        "slug": "nom-2002-ruby-sapphire-staff-messages",
    },
    "rs-2002-report": {
        "issue": "0211", "date": "2002-11-01", "no": "No.52",
        "pages": ["01/01_04/index.html"],
        "title_ja": "『ポケットモンスタールビー・サファイア』発売記念特集／対戦＆「ひみつきち」体験！ 株式会社ポケモン潜入取材",
        "speakers": {},
        "narrative": True,
        "interviewee": "",
        "org": "株式会社ポケモン",
        "works": ["宝可梦 红宝石·蓝宝石"],
        "tags": ["N.O.M", "红宝石·蓝宝石", "株式会社ポケモン", "Game Boy Advance", "多人对战", "秘密基地", "报道"],
        "slug": "nom-2002-ruby-sapphire-multi-battle-secret-base-report",
    },
    "colosseum-2003": {
        "issue": "0311", "date": "2003-11-01", "no": "No.64",
        "pages": ["soft/interv.html", "soft/interv01.html", "soft/interv02.html", "soft/interv03.html"],
        "title_ja": "『ポケモンコロシアム』開発スタッフインタビュー",
        "speakers": {"山名": "山名学", "三浦": "三浦昌幸"},
        "interviewee": "山名学、三浦昌幸 等（Genius Sonority 开发团队）",
        "org": "Genius Sonority",
        "works": ["宝可梦圆形竞技场"],
        "tags": ["N.O.M", "宝可梦圆形竞技场", "Genius Sonority", "GameCube"],
        "slug": "nom-2003-pokemon-colosseum-staff",
    },
}


# ---------------------------------------------------------------- fetch
def wayback(issue, page):
    """The raw page from the Wayback Machine, cached under data/cache_nom."""
    CACHE.mkdir(parents=True, exist_ok=True)
    fn = CACHE / f"nom_{issue}_{page.replace('/', '_')}"
    if fn.exists():
        raw = fn.read_bytes()
        meta = fn.with_suffix(fn.suffix + ".meta")
        ts = meta.read_text().strip() if meta.exists() else "2009"
        return raw, ts
    url = f"https://web.archive.org/web/2009id_/http://www.nintendo.co.jp/nom/{issue}/{page}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                raw = r.read()
                m = re.search(r"/web/(\d{14})", r.geturl())
                ts = m.group(1) if m else "2009"
            fn.write_bytes(raw)
            fn.with_suffix(fn.suffix + ".meta").write_text(ts)
            time.sleep(2)
            return raw, ts
        except Exception as exc:
            err = exc
            time.sleep(6 * (attempt + 1))
    raise err


def fetch_image(issue, page, src, ts, dest_dir):
    """A photograph from the same snapshot, saved under assets/img/interviews."""
    base = f"http://www.nintendo.co.jp/nom/{issue}/" + page.rsplit("/", 1)[0] + "/" if "/" in page else f"http://www.nintendo.co.jp/nom/{issue}/"
    src = re.sub(r"^/web/\d+im_/", "", src)
    if src.startswith("http"):
        absolute = src
    elif src.startswith("/"):
        absolute = "http://www.nintendo.co.jp" + src
    else:
        absolute = urllib.parse.urljoin(base, src)
    name = absolute.rsplit("/", 1)[-1]
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / name
    if not out.exists():
        url = f"https://web.archive.org/web/{ts}im_/{absolute}"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                out.write_bytes(r.read())
            time.sleep(1.5)
        except Exception as exc:
            print(f"    image {name}: {exc}")
            return None
    return "/" + out.relative_to(ROOT).as_posix()


# ---------------------------------------------------------------- parse
ANSWER = re.compile(r"^\s*([^\s>＞：:]{1,8})\s*(?:>>|＞＞)\s*(.*)$")


def page_items(raw, target, page, ts):
    """One page -> items. Questions are lines of their own, answers carry
    `名前>>`, the block before the first question is the introduction and
    the credits, a photograph is an image item where it appears."""
    t = raw.decode("shift_jis", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
    # the navigation strip at the top and bottom
    t = re.sub(r"<map.*?</map>", "", t, flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</tr>|</h\d>|</div>", "\n", t, flags=re.I)
    # the 2002 pages write <IMG SRC=...> in capitals
    t = re.sub(r'<img[^>]*src="([^"]+)"[^>]*alt="([^"]*)"[^>]*>', lambda m: f"\n[[img|{m.group(1)}|{m.group(2)}]]\n", t, flags=re.I)
    t = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*src="([^"]+)"[^>]*>', lambda m: f"\n[[img|{m.group(2)}|{m.group(1)}]]\n", t, flags=re.I)
    txt = re.sub(r"<[^>]+>", "", t)
    txt = html.unescape(txt)
    lines = [re.sub(r"[ \t\u3000]+", " ", l).strip() for l in txt.split("\n")]
    # the page's own title, repeated as a banner on every page of a feature:
    # kept once as the heading, never as a turn
    tm = re.search(r"<title>(.*?)</title>", raw.decode("shift_jis", "replace"), re.S | re.I)
    page_title = html.unescape(re.sub(r"\s+", " ", tm.group(1))).strip() if tm else ""
    if page_title:
        lines = ["[[title]]" + page_title] + [l for l in lines if l != page_title]
    if target.get("sections"):
        return section_items(lines, target, page, ts)
    if target.get("narrative"):
        return narrative_items(lines, page, ts)
    items = []
    seen_q = False
    speakers = target["speakers"]
    pending = None   # "石原：" on a line of its own names the speaker of the next line
    # the third house style writes "吉野：text" inline; on such a page a line
    # with no name is the interviewer only if it reads as a question, and a
    # statement continues the answer above
    INLINE = re.compile(r"^([^\s：:>＞、。]{1,4})[：:]\s*(\S.*)$")
    inline_page = any(INLINE.match(l) and not re.match(r"^(Q|Ｑ|N\.O\.M|NOM|ＮＯＭ|http|https)", l) for l in lines)
    # the fourth style: "山名 はい。" - a family name, a space, the answer; and
    # the question as "N.O.M ..." or "■...". A name counts when the page uses
    # it as a prefix more than once, so "また 何か" is not a speaker.
    SPACED = re.compile(r"^([一-鿿゠-ヿ]{1,5})\s+(\S.*)$")
    prefix_count = {}
    for l in lines:
        m4 = SPACED.match(l)
        if m4 and m4.group(1) not in ("また", "ただ", "でも", "つまり", "例えば", "実は", "結局", "特に", "最初", "今回", "今後", "最後", "当時", "現在"):
            prefix_count[m4.group(1)] = prefix_count.get(m4.group(1), 0) + 1
    spaced_names = {n for n, c in prefix_count.items() if c >= 2} | set(speakers)
    spaced_page = bool(spaced_names) and any(re.match(r"^(N\.O\.M|Ｎ\.Ｏ\.Ｍ|■|―|--)", l) for l in lines)
    QUESTION_END = re.compile(r"([？?]|か。|ね。|ください。|でしょう。|ますか。|ですか。|よね。|ますね。)\s*$")
    for line in lines:
        if not line:
            continue
        if line.startswith("[[title]]"):
            if not any(x.get("type") == "heading" for x in items):
                items.append({"type": "heading", "level": 2, "original": line[9:]})
            continue
        if pending:
            items.append({"type": "dialogue", "speaker": pending, "original": line, "role": "answer"})
            pending = None
            seen_q = True
            continue
        qn = re.match(r"^(?:ＮＯＭ|N\.O\.M|NOM|Ｎ\.Ｏ\.Ｍ)[：:]\s*(.+)$", line)
        if qn:
            items.append({"type": "dialogue", "speaker": "N.O.M采访者", "original": qn.group(1).strip(), "role": "question"})
            seen_q = True
            continue
        n = re.match(r"^([^\s：:>＞]{1,6})[：:]\s*$", line)
        if n and not re.match(r"^(Q|Ｑ|N\.O\.M)", n.group(1)):
            pending = speakers.get(n.group(1), n.group(1))
            continue
        if spaced_page:
            q4 = re.match(r"^(?:N\.O\.M|Ｎ\.Ｏ\.Ｍ)\s*(.+)$|^[■―]+\s*(.+)$|^--+\s*(.+)$", line)
            if q4:
                text = next(g for g in q4.groups() if g)
                items.append({"type": "dialogue", "speaker": "N.O.M采访者", "original": text.strip(), "role": "question"})
                seen_q = True
                continue
            m4 = SPACED.match(line)
            if m4 and m4.group(1) in spaced_names:
                items.append({"type": "dialogue", "speaker": speakers.get(m4.group(1), m4.group(1)), "original": m4.group(2).strip(), "role": "answer"})
                seen_q = True
                continue
            if items and items[-1].get("role") == "answer" and not line.startswith("[[img") and not re.match(r"^(★|▲|■|→|←)", line):
                items[-1]["original"] += chr(10) + line
                continue
        if inline_page:
            m3 = INLINE.match(line)
            if m3 and not re.match(r"^(Q|Ｑ|N\.O\.M|NOM|ＮＯＭ|http|https)", m3.group(1)):
                items.append({"type": "dialogue", "speaker": speakers.get(m3.group(1), m3.group(1)), "original": m3.group(2).strip(), "role": "answer"})
                seen_q = True
                continue
            if items and items[-1].get("role") == "answer" and not QUESTION_END.search(line) and not line.startswith("[[img"):
                items[-1]["original"] += chr(10) + line
                continue
        m = re.match(r"\[\[img\|([^|]+)\|([^\]]*)\]\]", line)
        if m:
            src, alt = m.group(1), m.group(2)
            # only the photographs: the layout gifs are frames, bullets and the Q badge
            if re.search(r"\.(jpe?g)$", src, re.I) and not re.search(r"waku|mball|q\.gif|btn|arrow|line|bar", src):
                items.append({"type": "image", "src": src, "alt": alt, "_page": page, "_ts": ts})
            continue
        if re.match(r"^(★|▲|■|→|←|＞＞|<<|>>)?\s*(ページ\s*[１-９1-9]|前のページ|次のページ|サイトマップ|ＴＯＰ|TOP|トップ)", line):
            continue
        if re.match(r"^\[?(Q|Ｑ)\]?$", line) or not re.search(r"[぀-ヿ一-鿿]", line):
            continue   # a divider, a page strip "｜１｜２｜", a bare badge
        a = ANSWER.match(line)
        if a and a.group(2).strip():
            name = speakers.get(a.group(1), a.group(1))
            items.append({"type": "dialogue", "speaker": name, "original": a.group(2).strip(), "role": "answer"})
            continue
        if seen_q or re.search(r"[？?]\s*$", line) or (items and items[-1].get("role") == "answer"):
            # a question, or the interviewer's remark between answers
            seen_q = True
            items.append({"type": "dialogue", "speaker": "N.O.M采访者", "original": line, "role": "question"})
            continue
        # before the first question: page title, section head, introduction, credits
        if re.match(r"^[０-９0-9]+[−\-−．.]", line) or "インタビュー" in line and len(line) < 60 and not items:
            items.append({"type": "heading", "level": 2, "original": line})
        else:
            items.append({"type": "narrative", "original": line})
    return items


def narrative_items(lines, page, ts):
    """A report page with no interview in it (the 2002 play report): every line of prose is a
    paragraph, the numbered line is the heading, a photograph stays where it is."""
    items = []
    for line in lines:
        if not line:
            continue
        if line.startswith("[[title]]"):
            items.append({"type": "heading", "level": 2, "original": line[9:]})
            continue
        m = re.match(r"\[\[img\|([^|]+)\|([^\]]*)\]\]", line)
        if m:
            if re.search(r"\.(jpe?g)$", m.group(1), re.I):
                items.append({"type": "image", "src": m.group(1), "alt": m.group(2), "_page": page, "_ts": ts})
            continue
        if re.match(r"^★[・★]*$|^▲|^(ページ\s*[１-９1-9]|前のページ|次のページ|サイトマップ|ＴＯＰ|TOP|トップ)", line) or not re.search(r"[぀-ヿ一-鿿]", line):
            continue
        if re.match(r"^[０-９0-9]+[−\-−．.]", line):
            items.append({"type": "heading", "level": 2, "original": line})
        else:
            items.append({"type": "narrative", "original": line})
    return items


def section_items(lines, target, page, ts):
    """The fifth house style (the 2002 Ruby/Sapphire staff messages): one page, a section per
    person divided by ★ rules, each opening with the person's title and a profile paragraph,
    then question and answer alternating with no marks at all; the photographs sit in a strip
    at the top, one per section, in the sections' order."""
    items, photos, sec, state, parity = [], [], -1, None, 0
    names = target["sections"]
    for line in lines:
        if not line:
            continue
        if line.startswith("[[title]]"):
            items.append({"type": "heading", "level": 2, "original": line[9:]})
            continue
        m = re.match(r"\[\[img\|([^|]+)\|([^\]]*)\]\]", line)
        if m:
            if re.search(r"\.(jpe?g)$", m.group(1), re.I):
                photos.append({"type": "image", "src": m.group(1), "alt": m.group(2), "_page": page, "_ts": ts})
            continue
        if re.match(r"^★[・★]*$", line):
            sec += 1
            state, parity = "title", 0
            if sec < len(photos):
                items.append(photos[sec])
            continue
        if re.match(r"^▲|^(ページ\s*[１-９1-9]|前のページ|次のページ|サイトマップ|ＴＯＰ|TOP|トップ)", line) or not re.search(r"[぀-ヿ一-鿿]", line):
            continue
        if sec < 0:
            if re.match(r"^[０-９0-9]+[−\-−．.]", line):
                items.append({"type": "heading", "level": 2, "original": line})
            else:
                items.append({"type": "narrative", "original": line})
            continue
        who = names[sec] if sec < len(names) else names[-1]
        if state == "title":
            items.append({"type": "heading", "level": 3, "original": f"{who}：{line}"})
            state = "profile"
        elif state == "profile":
            items.append({"type": "narrative", "original": line})
            state = "turns"
        else:
            if parity % 2 == 0:
                items.append({"type": "dialogue", "speaker": "N.O.M采访者", "original": line, "role": "question"})
            else:
                items.append({"type": "dialogue", "speaker": who, "original": line, "role": "answer"})
            parity += 1
    return items


def tidy(items):
    """What the line rules cannot see: the first question has no question
    mark and comes before any answer, so a narrative line that an answer
    follows is a question; the credits at the top are one block, not five
    paragraphs; a page's repeated feature title is not prose."""
    out = []
    title = None
    for i, x in enumerate(items):
        if x["type"] == "narrative":
            text = x["original"]
            if title is None and "／" in text:
                title = text.rstrip("１２３４５６７８９0123456789 ★")
                out.append({"type": "heading", "level": 2, "original": text})
                continue
            if title and text.startswith(title):
                continue
            nxt = items[i + 1] if i + 1 < len(items) else None
            if nxt and nxt.get("role") == "answer":
                out.append({"type": "dialogue", "speaker": "N.O.M采访者", "original": text, "role": "question"})
                continue
        if x["type"] == "heading" and any(y["type"] == "heading" and y["original"] == x["original"] for y in out):
            continue
        out.append(x)
    # the credits name the people the turns abbreviate: 福田和彦さん -> 福田
    fullnames = {}
    for x in out:
        if x["type"] == "narrative":
            for m in re.finditer(r"([一-鿿]{1,3})\s?([一-鿿]{1,3})(?:さん|氏)", x["original"]):
                fullnames.setdefault(m.group(1), m.group(1) + m.group(2))
    for x in out:
        if x.get("role") == "answer" and x["speaker"] in fullnames:
            x["speaker"] = fullnames[x["speaker"]]
    # the credits: consecutive short narrative lines before the first turn
    merged = []
    for x in out:
        if x["type"] == "narrative" and merged and merged[-1]["type"] == "narrative" and len(x["original"]) <= 40 and len(merged[-1]["original"]) <= 120 and not any(y["type"] == "dialogue" for y in merged):
            merged[-1]["original"] += "／" + x["original"]
        else:
            merged.append(dict(x))
    return merged


def merge_pages(target):
    items = []
    for i, page in enumerate(target["pages"]):
        raw, ts = wayback(target["issue"], page)
        items.extend(page_items(raw, target, page, ts))
    return items if target.get("narrative") else tidy(items)


# ---------------------------------------------------------------- translate
SITE_GLOSSARY = ROOT / "design" / "glossary-site.json"


def load_glossary():
    """the site's own glossary (people, companies, dev jargon - design/glossary-site.json,
    kept by tools/glossary-audit.py) first, then the master glossary of game terms"""
    out = []
    if SITE_GLOSSARY.exists():
        site = json.loads(SITE_GLOSSARY.read_text(encoding="utf-8"))
        out += [{"target": e["target"], "terms": e.get("terms") or [], "site": True} for e in site.get("entries", []) if e.get("target")]
    if GLOSSARY.exists():
        data = json.loads(GLOSSARY.read_text(encoding="utf-8"))
        out += [{"target": e["target"], "terms": e.get("terms") or []} for e in data.get("entries", []) if e.get("target")]
    return out


def glossary_hits(text, glossary):
    hits = {}
    for e in glossary:
        for term in e["terms"]:
            term = term.strip()
            if len(term) >= 2 and not re.match(r"^[A-Za-z0-9 .\-]+$", term) and term in text:
                hits[term] = e["target"]
                break
    # the site's own terms come first when the list is cut
    site_terms = {term for e in glossary if e.get("site") for term in e["terms"]}
    return sorted(hits.items(), key=lambda kv: (kv[0] not in site_terms, -len(kv[0])))[:80]


def deepseek(messages, max_tokens=6000):
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        raise SystemExit("DEEPSEEK_API_KEY is not set")
    payload = {"model": "deepseek-chat", "messages": messages, "max_tokens": max_tokens, "temperature": 0.2,
               "response_format": {"type": "json_object"}}
    req = urllib.request.Request(DEEPSEEK_URL, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode("utf-8"))["choices"][0]["message"]["content"]
        except Exception as exc:
            print(f"    deepseek attempt {attempt + 1}: {exc}", file=sys.stderr)
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("deepseek failed")


SYSTEM = ("你是宝可梦开发史料的日中译者。译文忠实、平实、可读，不加渲染、不加感叹号、不改写语气；"
          "人名用通行中文译名，游戏名与专有名词优先采用提供的术语表；只输出合法 JSON。")


def translate_items(items, target, glossary):
    text_items = [(i, x) for i, x in enumerate(items) if x["type"] != "image"]
    full = "\n".join(x["original"] for _, x in text_items)
    hits = glossary_hits(full, glossary)
    gloss = "\n".join(f"- {s} → {t}" for s, t in hits) or "（无）"
    chunk = 10
    for start in range(0, len(text_items), chunk):
        part = text_items[start:start + chunk]
        payload = [{"i": i, "speaker": x.get("speaker", ""), "text": x["original"]} for i, x in part]
        prompt = (f"这是任天堂官方网络杂志 N.O.M {target['date'][:4]}年的访谈《{target['title_ja']}》的一段。"
                  f"逐条把 text 译成简体中文，保留条目顺序与编号 i；说话人不用译。"
                  f"note 只在读者很可能不知道的具体事实上给一句（某个人是谁、某部作品或某件当年的事），一般留空字符串；不要解释 N.O.M、宝可梦、任天堂这类常识，标题行不加 note。\n\n"
                  f"输出格式：{{\"items\":[{{\"i\":编号,\"translation\":\"译文\",\"note\":\"\"}}]}}\n\n"
                  f"待译：\n{json.dumps(payload, ensure_ascii=False)}")
        print(f"  translating {start + 1}-{start + len(part)} / {len(text_items)} ...", flush=True)
        got = None
        for attempt in range(3):
            raw = deepseek([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}])
            try:
                got = {int(r["i"]): r for r in json.loads(raw).get("items", []) if "i" in r}
                break
            except (ValueError, TypeError) as exc:
                # the model sometimes breaks its own JSON on a long answer; ask again
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
    """Chinese title, dek and summary from the translated turns."""
    sample = "\n".join(f"{x.get('speaker', '')}: {x.get('translation', '')}" for x in items if x["type"] == "dialogue")[:6000]
    prompt = (f"下面是 N.O.M {target['date'][:4]}年的访谈《{target['title_ja']}》的中文译文节选。"
              f"给出：title（中文标题，形如「N.O.M 2000年6月号：……」，40字以内，写清受访者与主题，不用感叹号）、"
              f"display_title（封面用的一句短标题，20字以内）、dek（一句导语，60字以内）、summary（120字以内的内容提要，平实）。"
              f"输出 JSON：{{\"title\":\"\",\"display_title\":\"\",\"dek\":\"\",\"summary\":\"\"}}\n\n{sample}")
    raw = deepseek([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], max_tokens=800)
    return json.loads(raw)


# ---------------------------------------------------------------- write
def era_for(year):
    y = int(year)
    return "1999" if y <= 2001 else "2003" if y <= 2005 else "2007" if y <= 2009 else "2011" if y <= 2012 else "2014" if y <= 2016 else "2019" if y <= 2021 else "2026"


def write_post(key, target, items, cover, ts):
    issue = target["issue"]
    year, month = "19" + issue[:2] if issue[0] == "9" else "20" + issue[:2], int(issue[2:])
    first_page = target["pages"][0]
    original_link = f"https://www.nintendo.co.jp/nom/{issue}/{first_page}"
    people = sorted({x["speaker"] for x in items if x.get("role") == "answer"})
    clean = []
    for x in items:
        y = {k: v for k, v in x.items() if not k.startswith("_")}
        clean.append(y)
    fm = {
        "layout": "interview-editorial",
        "archive_type": "interview_translation",
        "title": cover.get("title") or f"N.O.M {year}年{month}月号：{target['title_ja']}",
        "display_title": cover.get("display_title") or None,
        "dek": cover.get("dek") or None,
        "date": target["date"],
        "era_skin": era_for(year),
        "categories": ["访谈翻译", "官方档案"],
        "tags": target["tags"],
        "publication": f"任天堂官网「N.O.M」{year}年{month}月号（{target['no']}）",
        "source_kind": "official_web_magazine",
        "interviewer": "N.O.M 编辑部",
        "interviewee": target["interviewee"] or "、".join(people),
        "organization": target.get("org") or None,
        "translator": "PokeAmice（DeepSeek 初译）",
        "original_lang": "ja",
        "translation_lang": "zh-CN",
        "source": {"title": f"{target['title_ja']}｜Nintendo Online Magazine {year}年{month}月号",
                   "url": original_link, "language": "ja", "source_type": "official_web_magazine"},
        "original_link": original_link,
        "source_url": f"https://web.archive.org/web/{ts}/{original_link}",
        "summary": cover.get("summary") or None,
        "entities": {"people": people, "works": target["works"]},
        "workflow": {"fetch": "wayback", "translation": "deepseek-chat", "proofreading": "pending", "published": "draft"},
        "parallel_items": clean,
    }
    fm = {k: v for k, v in fm.items() if v is not None}
    path = POSTS / f"{target['date']}-interview-{target['slug']}.md"
    path.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n", encoding="utf-8", newline="\n")
    return path


def run(key, dry):
    target = TARGETS[key]
    print(f"== {key}: N.O.M {target['issue']} {target['title_ja']}")
    items = merge_pages(target)
    _, ts = wayback(target["issue"], target["pages"][0])
    q = sum(1 for x in items if x.get("role") == "question")
    a = sum(1 for x in items if x.get("role") == "answer")
    print(f"  {len(items)} items: {q} questions, {a} answers, {sum(1 for x in items if x['type'] == 'image')} images, {sum(1 for x in items if x['type'] == 'narrative')} narrative")
    if dry:
        for x in items:
            print(f"   [{x['type'][:4]}] {x.get('speaker', '')}: {x.get('original', x.get('alt', ''))[:90]}")
        return
    dest = IMG_DIR / f"nom-{target['issue']}-{key}"
    kept = []
    for x in items:
        if x["type"] == "image":
            rel = fetch_image(target["issue"], x["_page"], x["src"], x["_ts"], dest)
            if rel:
                kept.append({"type": "image", "image": rel, "alt": x["alt"], "caption": x["alt"]})
        else:
            kept.append(x)
    items = kept
    glossary = load_glossary()
    translate_items(items, target, glossary)
    cover = propose_cover(items, target)
    path = write_post(key, target, items, cover, ts)
    print(f"  -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--list" in sys.argv or not args:
        for k, t in TARGETS.items():
            print(f"{k:18s} N.O.M {t['issue']}  {t['title_ja']}")
        sys.exit(0)

    for key in args:
        run(key, "--dry-run" in sys.argv)
