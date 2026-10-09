"""Import (or re-import) GAME FREAK recruit pages into _posts from their Wayback captures.

    python tools/import-gf-recruit.py --list
    python tools/import-gf-recruit.py STEM [STEM ...] [--dry]   # --dry: parse + print, no translation, nothing written
    python tools/import-gf-recruit.py --all [--dry]

Targets are in design/recruit-archive/targets.yml. The capture comes from the cache that
tools/recruit-archive.py fetch fills (data/cache_web/recruit-wayback/raw/), and is fetched if it is
missing. Three page families are read, each by its own markup rather than by guessing:

  cms         the 2019 site: mv / member (or info) / contents units, a turn is
              <b class="talker"><span class="talker__name">T.T.</span></b><span class="speak">...</span>
  gen1        interview_0x.html of 2015-2017: lead, a profile list, sections of h2 / h3 questions and
              <dl><dt><img alt="デザイナー J.T."></dt><dd>answer</dd></dl>
  career2009  the 2009 mid-career site: 語り手 / profile / h3 / p

The Japanese is taken from the page as it is - nothing goes through the model but the translation.
A target with `earlier:` (a capture of an earlier version of the same page) gets the paragraphs that
version had and this one does not, after the piece, under an editor's heading; those items carry
`from_capture` so `recruit-archive.py check` reads them against their own capture.

On a re-import (the stem exists) the post keeps the title, tags, entities, topics and the other
fields the library knows it by; the items, summary, dek, date, interviewee and source are new.
"""
import importlib.util
import json
import re
import sys
import time
import urllib.parse
from io import BytesIO
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, NavigableString, Tag

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "_posts"
IMG_ROOT = ROOT / "assets" / "img" / "interviews"
TARGETS = ROOT / "design" / "recruit-archive" / "targets.yml"


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ra = _load("recruit_archive", "recruit-archive.py")
_nom = _load("import_nom", "import-nom.py")
deepseek, load_glossary, glossary_hits = _nom.deepseek, _nom.load_glossary, _nom.glossary_hits

# the page writes names with a space; the library writes them as people.yml does
NAMES = {"大森 滋": "大森滋", "岩尾 和昌": "岩尾和昌", "尾上 将之": "尾上将之", "伊藤 博人": "伊藤博人", "小川 一美": "小川一美",
         "渡辺 哲也": "渡边哲也", "渡辺哲也": "渡边哲也", "増田順一": "增田顺一", "増田 順一": "增田顺一"}
INITIALS = re.compile(r"([A-Z])\.?\s?([A-Z])\.?$")


def who(raw):
    raw = re.sub(r"\s+", " ", (raw or "").strip())
    if raw in NAMES:
        return NAMES[raw]
    m = re.search(r"([A-Z])\.\s?([A-Z])\.?", raw)
    if m:
        return f"{m.group(1)}.{m.group(2)}."
    return raw


def text_of(el, br="\n"):
    """An element's text, <br> as `br`, whitespace tidied, the page's own wording otherwise."""
    if el is None:
        return ""
    el = BeautifulSoup(str(el), "html.parser")
    for b in el.find_all("br"):
        b.replace_with(br)
    t = el.get_text("")
    t = re.sub(r"[ \t\r\f\v]+", " ", t)
    t = re.sub(r" *\n *", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def cls(el):
    return " ".join(el.get("class") or []) if isinstance(el, Tag) else ""


# ---------------------------------------------------------------- parsers
def parse_cms(html, page, target):
    soup = BeautifulSoup(html, "html.parser")
    root = soup.select_one(".st-contents") or soup
    items, seen_img = [], set()
    person = None
    info = root.select_one(".info")
    if info:
        person = who(text_of(info.select_one(".info__name"), " "))
    default_speaker = target.get("speaker") or (person if page.get("group") in ("people", "message") else None)

    def img(el, role=None):
        src = el.get("src") or ""
        if not src or src in seen_img or re.search(r"(logo|icon|arrow|btn|bubble|@sp\.)", src, re.I):
            return
        seen_img.add(src)
        items.append({"type": "image", "_src": src, "_role": role})

    def walk(el):
        for ch in el.children:
            if not isinstance(ch, Tag):
                continue
            c = cls(ch)
            if re.search(r"\b(hdr|tag|bubble|obj|entries|cp-|mv__cp|member__ttl)", c) or ch.name in ("script", "style", "nav"):
                continue
            if "mv" == c.split(" ")[0] or c.startswith("mv "):
                for im in ch.find_all("img")[:1]:
                    img(im, "mv")
                continue
            if c.startswith("info") and ch.select_one(".info__name"):
                name = who(text_of(ch.select_one(".info__name"), " "))
                post = text_of(ch.select_one(".info__post"), "　")
                prof = text_of(ch.select_one(".info__profile"))
                items.append({"type": "profile", "speaker": name, "speaker_orig": text_of(ch.select_one(".info__name"), " "),
                              "role_ja": post, "original": prof, "role": "answer"})
                continue
            if "theme__ttl" in c:
                items.append({"type": "heading", "level": 2, "original": text_of(ch, "")})
                continue
            if "theme__intro" in c:
                items.append({"type": "text", "original": text_of(ch)})
                continue
            if "member__list__unit" in c:
                name_raw = text_of(ch.select_one(".member__list__name"), " ")
                info_l = [text_of(p, " ") for p in ch.select(".member__list__info p")] or [text_of(ch.select_one(".member__list__info"), " ")]
                photo = ch.select_one(".member__list__photo img")
                if photo is not None:
                    img(photo, "member")
                items.append({"type": "profile", "speaker": who(name_raw), "speaker_orig": name_raw,
                              "role_ja": "　".join(x for x in info_l if x), "original": text_of(ch.select_one(".member__list__profile")),
                              "role": "answer", "_avatar": items[-1]["_src"] if photo is not None and items and items[-1]["type"] == "image" else None})
                if photo is not None and items[-2]["type"] == "image":
                    items.pop(-2)      # the photo goes with the profile, not as a picture in the piece
                continue
            if "contents__unit__cp" in c:
                items.append({"type": "heading", "level": 3, "original": text_of(ch, "")})
                continue
            if ch.name == "p":
                talker = ch.select_one(".talker__name")
                speak = ch.select_one(".speak")
                if talker is not None:
                    items.append({"type": "text", "speaker": who(text_of(talker, "")), "speaker_orig": text_of(talker, ""),
                                  "original": text_of(speak if speak is not None else ch), "role": "answer"})
                else:
                    t = text_of(ch)
                    if t:
                        x = {"type": "text", "original": t}
                        if default_speaker:
                            x.update({"speaker": default_speaker, "role": "answer"})
                        items.append(x)
                continue
            if ch.name == "img":
                if "-sp" not in cls(ch.parent) and "is-sp" not in c:
                    img(ch)
                continue
            if ch.name in ("h2", "h3", "h4") and text_of(ch, ""):
                items.append({"type": "heading", "level": 3, "original": text_of(ch, "")})
                continue
            if "contents__unit__img-sp" in c or "is-sp" in c:
                continue
            walk(ch)

    mv = soup.select_one(".mv")
    if mv is not None:
        for im in mv.find_all("img")[:1]:
            img(im, "mv")
    walk(root)
    catch = text_of(soup.select_one(".mv__cp__pc") or soup.select_one(".mv__cp"), "")
    title = text_of(soup.title, " ") if soup.title else ""
    return items, {"catch": catch, "title_ja": re.sub(r"\s*[｜|]\s*GAME FREAK.*$", "", title).strip(), "person": person}


def parse_gen1(html, page, target):
    soup = BeautifulSoup(html, "html.parser")
    root = soup.select_one(".content_inner") or soup
    items = []
    kv = soup.select_one(".keyvisual img")
    if kv is not None:
        items.append({"type": "image", "_src": kv.get("src"), "_role": "mv"})

    def speaker_from_alt(alt):
        m = re.search(r"([A-Z])\.\s?([A-Z])\.?", alt or "")
        return (f"{m.group(1)}.{m.group(2)}." if m else (alt or "").strip()), (alt or "").strip()

    def walk(el):
        for ch in el.children:
            if not isinstance(ch, Tag):
                continue
            c = cls(ch)
            if ch.name == "p" and "lead" in c:
                items.append({"type": "text", "original": text_of(ch)})
            elif ch.name == "p" and "people_double-text" in c:
                items.append({"type": "text", "original": text_of(ch)})
            elif ch.name == "h2":
                items.append({"type": "heading", "level": 2, "original": text_of(ch, "")})
            elif ch.name == "h3":
                items.append({"type": "heading", "level": 3, "original": text_of(ch, ""), "role_hint": "question"})
            elif ch.name == "dl":
                dt, dd = ch.find("dt"), ch.find("dd")
                imgs = dt.find_all("img") if dt is not None else []
                in_profile = ch.find_parent(class_=re.compile(r"\bprofile\b")) is not None
                if dd is None:
                    for im in imgs:      # a profile row of two portraits, its text in a <p> after it
                        sp, alt = speaker_from_alt(im.get("alt"))
                        items.append({"type": "image", "_src": im.get("src"), "_role": "portrait", "caption_ja": alt})
                    continue
                sp, alt = speaker_from_alt(imgs[0].get("alt") if imgs else "")
                body = text_of(dd)
                said = re.search(r"([A-Z]\.[A-Z]\.)です", body)
                if in_profile and said and said.group(1) != sp:
                    # a reused template keeps the old portrait's alt text: the self-introduction decides
                    sp, alt = said.group(1), said.group(1)
                if in_profile:
                    items.append({"type": "profile", "speaker": sp, "speaker_orig": alt, "role_ja": alt.replace(sp.rstrip("."), "").strip(" ."),
                                  "original": body, "role": "answer", "_avatar": imgs[0].get("src") if imgs else None})
                else:
                    items.append({"type": "text", "speaker": sp, "speaker_orig": alt, "original": body, "role": "answer"})
            elif "photo_area" in c:
                for im in ch.find_all("img"):
                    items.append({"type": "image", "_src": im.get("src")})
            else:
                walk(ch)

    walk(root)
    title = text_of(soup.title, " ") if soup.title else ""
    return items, {"catch": kv.get("alt") if kv is not None else "", "title_ja": re.sub(r"\s*[｜|].*$", "", title).strip()}


def parse_career2009(html, page, target):
    soup = BeautifulSoup(html, "html.parser")
    root = soup.select_one("#cont") or soup
    items = []
    prof = root.select_one("#profile")
    speaker = None
    if prof is not None:
        h = prof.find("h3")
        name_raw = text_of(h, "").replace("語り手：", "").strip() if h is not None else ""
        speaker = who(name_raw)
        if h is not None:
            h.extract()
        items.append({"type": "profile", "speaker": speaker, "speaker_orig": name_raw, "role_ja": "語り手",
                      "original": text_of(prof), "role": "answer"})
    for ch in root.children:
        if not isinstance(ch, Tag) or ch.get("id") == "profile":
            continue
        if ch.name == "h3":
            items.append({"type": "heading", "level": 3, "original": text_of(ch, "")})
        elif ch.name == "p":
            for para in [x for x in text_of(ch).split("\n") if x.strip()]:
                items.append({"type": "text", "speaker": speaker, "original": para.strip(), "role": "answer"})
    head = soup.select_one("#main h2 img")
    return items, {"catch": head.get("alt") if head is not None else "", "title_ja": text_of(soup.title, " ") if soup.title else ""}


PARSERS = {"cms": parse_cms, "gen1": parse_gen1, "career2009": parse_career2009}


# ---------------------------------------------------------------- pictures
def picture(src, page, ts, img_dir):
    """The page's picture in the post's picture folder: reused if a file of that name is there."""
    absu = urllib.parse.urljoin(ra.page_url(page), src)
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(urllib.parse.urlparse(absu).path).name) or "img.jpg"
    dest = IMG_ROOT / img_dir / name
    web = f"/assets/img/interviews/{img_dir}/{name}"
    if dest.exists():
        return web
    data = None
    for cap in (ts, ts[:8]):
        try:
            data = ra.http(f"https://web.archive.org/web/{cap}im_/{absu}", binary=True, tries=3)
            if data and len(data) > 300 and not data[:200].lstrip().lower().startswith(b"<"):
                break
            data = None
        except IOError:
            data = None
    if data is None:
        print(f"    picture not in the archive: {absu}", file=sys.stderr)
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
        im = Image.open(BytesIO(data))
        if im.format == "JPEG" and (len(data) > 250_000 or im.width > 1600):
            if im.width > 1600:
                im = im.resize((1600, round(im.height * 1600 / im.width)))
            buf = BytesIO()
            im.convert("RGB").save(buf, "JPEG", quality=82, optimize=True, progressive=True)
            data = buf.getvalue()
    except Exception as exc:  # noqa: BLE001 - keep the bytes as they came
        print(f"    could not re-encode {name}: {exc}", file=sys.stderr)
    dest.write_bytes(data)
    time.sleep(1)
    return web


# ---------------------------------------------------------------- translation
SYSTEM = ("你是宝可梦开发史料的日中译者，把 GAME FREAK 招聘网站上的员工访谈、对谈和寄语译成简体中文。"
          "要求：意思一点不差，不增不减，不加渲染、不加感叹号、不拔高语气；说话的部分译成中文口语里自然的说法，"
          "不要日语直译腔——日语汉字词换成中文的说法（自己責任→自己负责，経営メンバー→管理层，元開発者→开发出身，"
          "職種→岗位/职能，独自エンジン→自研引擎，～現在→截至～，入社→入职），按中文习惯调整语序，长句可以断开；"
          "人名首字母（T.T.、K.I. 等）照写；部门名照通行译法（研究開発部→研究开发部，開発一部→开发一部）；"
          "游戏名与专有名词优先采用术语表；只输出合法 JSON。")


def translate(items, target, glossary):
    todo = [(i, x) for i, x in enumerate(items) if x.get("type") != "image" and x.get("original")]
    full = "\n".join(x["original"] for _, x in todo)
    hits = glossary_hits(full, glossary)
    system = SYSTEM + "\n术语表：\n" + ("\n".join(f"- {s} → {t}" for s, t in hits) or "（无）")
    ctx = f"GAME FREAK 招聘网站 {target['date'][:4]} 年的页面《{target.get('label_ja') or target['page']}》"
    for start in range(0, len(todo), 10):
        part = todo[start:start + 10]
        payload = [{"i": i, "speaker": x.get("speaker", ""), "kind": x["type"], "text": x["original"],
                    **({"role_line": x["role_ja"]} if x.get("role_ja") else {})} for i, x in part]
        prompt = (f"这是{ctx}的一段（日文）。逐条把 text 译成简体中文，有 role_line 的也把它译出来（职种、入社年份这一行）；"
                  "保留编号 i；说话人不用译；标题照译，不加书名号以外的符号。"
                  "note 只在读者很可能不知道的具体事实上给一句，一般留空字符串。\n\n"
                  '输出：{"items":[{"i":编号,"translation":"译文","role_line":"职种行的译文或空","note":""}]}\n\n'
                  f"待译：\n{json.dumps(payload, ensure_ascii=False)}")
        print(f"  translating {start + 1}-{start + len(part)} / {len(todo)}", flush=True)
        got = None
        for attempt in range(3):
            try:
                got = {int(r["i"]): r for r in json.loads(deepseek([{"role": "system", "content": system},
                                                                     {"role": "user", "content": prompt}])).get("items", []) if "i" in r}
                break
            except (ValueError, TypeError) as exc:
                print(f"    bad JSON ({exc}), again", file=sys.stderr)
        if got is None:
            raise RuntimeError("translation failed three times")
        for i, x in part:
            r = got.get(i) or {}
            x["translation"] = str(r.get("translation", "")).strip()
            if x.get("role_ja"):
                x["role_zh"] = str(r.get("role_line", "")).strip()
            note = str(r.get("note") or "").strip()
            if note:
                x["note"] = note
        time.sleep(1)
    missing = [i for i, x in todo if not x.get("translation")]
    if missing:
        raise RuntimeError(f"untranslated items: {missing}")
    return items


def propose(items, target, keep_title, catch=""):
    sample = "\n".join(f"{x.get('speaker', '')}: {x.get('translation', '')}" for x in items if x.get("type") != "image")[:7000]
    if catch:
        sample = f"（页面主标语原文：{catch}）\n" + sample
    year = target["date"][:4]
    ask = ("title（中文标题，照本站同类标题的写法：" + target.get("title_like", "「GAME FREAK 官方对谈 程序员篇：<一句主题>（T.T. × K.I.）」") +
           "，45 字以内，主题取自文中的标题句，不用感叹号）、display_title（封面用的一句短标题：把页面主标语原文译成中文，25 字以内）、") if not keep_title else ""
    prompt = (f"下面是 GAME FREAK 招聘网站 {year} 年页面《{target.get('label_ja') or target['page']}》的中文译文。给出："
              f"{ask}dek（一句导语，60 字以内）、summary（120 字以内的内容提要，平实，只写文中有的事实）。"
              '输出 JSON：{"title":"","display_title":"","dek":"","summary":""}\n\n' + sample)
    return json.loads(deepseek([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], max_tokens=900))


# ---------------------------------------------------------------- assembling the post
FRONT_RE = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)
KEEP = ("title", "display_title", "title_ja", "era", "era_skin", "tags", "categories", "entities", "topics", "mentions",
        "interview_id", "author", "publication", "outlet", "interviewer", "cover", "header", "series", "series_part", "lore")


def old_front(stem):
    """The post as the library has it (git HEAD) - a file this tool wrote earlier is not 'the library's'."""
    import subprocess
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:_posts/{stem}.md"], capture_output=True)
    if r.returncode != 0:
        return None
    m = FRONT_RE.match(r.stdout.decode("utf-8", "replace"))
    return yaml.safe_load(m.group(1)) if m else None


def finish_items(items, page, ts, img_dir, extra=None):
    out = []
    for x in items:
        x = dict(x)
        if x["type"] == "image":
            web = picture(x["_src"], page, ts, img_dir)
            if not web:
                continue
            y = {"type": "image", "src": web}
            if x.get("caption_ja"):
                y["caption"] = x["caption_ja"]
            out.append(y)
            continue
        if x.get("_avatar"):
            av = picture(x["_avatar"], page, ts, img_dir)
            if av:
                x["avatar"] = av
        x.pop("role_hint", None)
        out.append({k: v for k, v in x.items() if not k.startswith("_") and v not in (None, "")})
        if extra:
            out[-1].update(extra)
    return out


def diff_items(main_items, earlier_items):
    have = ra.norm("".join(x.get("original", "") for x in main_items))
    return [x for x in earlier_items if x["type"] in ("text", "profile") and len(ra.norm(x.get("original", ""))) >= 12
            and ra.norm(x["original"]) not in have]


def run(t, pages, glossary, dry):
    page = pages[t["page"]]
    ts = str(t["capture"])
    html = ra.fetch_capture(page, ts)
    items, meta = PARSERS[page.get("family", "cms")](html, page, t)
    earlier = []
    if t.get("earlier"):
        e_html = ra.fetch_capture(page, str(t["earlier"]))
        e_items, _ = PARSERS[page.get("family", "cms")](e_html, page, t)
        earlier = diff_items(items, e_items)
    if t.get("later"):
        # what a later version of the page no longer says (a person taken out, a passage rewritten)
        l_items, _ = PARSERS[page.get("family", "cms")](ra.fetch_capture(page, str(t["later"])), page, t)
        later_text = ra.norm("".join(x.get("original", "") for x in l_items))
        gone = 0
        for x in items:
            if x["type"] in ("text", "profile") and len(ra.norm(x.get("original", ""))) >= 12 and ra.norm(x["original"]) not in later_text:
                x["removed_on"] = ra.stamp(str(t["later"]))
                gone += 1
        print(f"   {gone} item(s) not in the later version {t['later']}")
    speakers = list(dict.fromkeys(x["speaker"] for x in items if x.get("speaker") and x.get("role") == "answer"))
    print(f"== {t['stem']}: {page['id']}@{ts}  {len(items)} items, speakers {speakers}, catch {meta.get('catch', '')[:40]!r}")
    if earlier:
        print(f"   + {len(earlier)} paragraph(s) only in the earlier version {t['earlier']}")
    if dry:
        for x in items + earlier:
            if x["type"] == "image":
                print(f"   [img] {x['_src']}")
            else:
                print(f"   [{x['type']}{'/' + x['speaker'] if x.get('speaker') else ''}] {x['original'][:80]}")
        return None
    old = old_front(t["stem"])
    img_dir = t.get("img_dir") or (old and _old_img_dir(t["stem"])) or t["stem"].split("-", 3)[-1]
    if earlier:
        e_head = {"type": "heading", "level": 2, "source": "editor",
                  "original": "（編者注）この版にない、" + t["earlier_label_ja"] + "の段落",
                  "translation": t["earlier_label"]}
        earlier = [e_head] + earlier
    for x in earlier[1:]:
        x["_from"] = str(t["earlier"])
    translate(items + earlier, t, glossary)
    body = finish_items(items, page, ts, img_dir)
    for x in earlier[1:]:
        x["from_capture"] = x.pop("_from")
    body += finish_items(earlier, page, str(t.get("earlier") or ts), img_dir)
    cover = propose(body, t, keep_title=bool(old) and not t.get("new_title"), catch=meta.get("catch", ""))
    people = [s for s in speakers if s]
    fm = {
        "layout": "interview-editorial",
        "archive_type": "interview_translation",
        "title": cover.get("title"),
        "display_title": cover.get("display_title"),
        "title_ja": t.get("title_ja") or meta.get("title_ja"),
        "date": f"{t['date']} 10:00:00 +0900",
        "era": str(t["date"][:4]),
        "categories": ["developer-interviews", "gamefreak-recruit"],
        "tags": ["Game Freak", "招聘访谈"] + list(t.get("tags") or []),
        "publication": "Game Freak 採用情報",
        "original_link": ra.page_url(page),
        "source_url": f"https://web.archive.org/web/{ts}/{ra.page_url(page)}",
        "source": {"title": t.get("title_ja") or meta.get("title_ja"), "url": ra.page_url(page), "language": "ja",
                   "source_type": "official_interview"},
        "author": "Game Freak 官方",
        "interviewee": "、".join(people),
        "original_lang": "ja",
        "translation_lang": "zh-CN",
        "translator": "PokeAmice（DeepSeek 初译）",
        "summary": cover.get("summary"),
        "dek": cover.get("dek"),
        "entities": {"people": people, "works": list(t.get("works") or []), "organizations": ["株式会社ゲームフリーク"]},
        "recruit": {k: v for k, v in {"page": page["id"], "version": t["version"], "capture": ts,
                                       "date_basis": t.get("date_basis")}.items() if v},
        "parallel_items": body,
    }
    if page.get("family") == "cms":
        fm["era_skin"] = "2019"
    if old:
        for k in KEEP:
            if old.get(k) not in (None, "", [], {}):
                fm[k] = old[k]
        fm["entities"]["people"] = list(dict.fromkeys(people + [p for p in (old.get("entities") or {}).get("people", []) if p in people]))
        cats = list(fm.get("categories") or [])
        if "gamefreak-recruit" not in cats:
            fm["categories"] = cats + ["gamefreak-recruit"]
    for k, v in (t.get("set") or {}).items():
        fm[k] = v
    fm = {k: v for k, v in fm.items() if v not in (None, "", [], {})}
    path = POSTS / f"{t['stem']}.md"
    path.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n", encoding="utf-8", newline="\n")
    print(f"   wrote {path.relative_to(ROOT)} ({len(body)} items)")
    return path


def _old_img_dir(stem):
    import subprocess
    t = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:_posts/{stem}.md"], capture_output=True).stdout.decode("utf-8", "replace")
    m = re.search(r"/assets/img/interviews/([^/\s]+)/", t)
    return m.group(1) if m else None


def append_earlier(t, pages, glossary, dry):
    """A faithful post of the current version gets what the first version said and this one does not -
    appended as YAML text after its last item, so the rest of the file is untouched."""
    page = pages[t["page"]]
    path = POSTS / f"{t['stem']}.md"
    text = path.read_text("utf-8")
    fm = yaml.safe_load(FRONT_RE.match(text).group(1))
    have = ra.norm("".join(x.get("original", "") for x in fm.get("parallel_items") or [] if isinstance(x.get("original"), str)))
    cur, _ = PARSERS[page.get("family", "cms")](ra.fetch_capture(page, str(t["capture"])), page, t)
    have += ra.norm("".join(x.get("original", "") for x in cur))
    e_items, _ = PARSERS[page.get("family", "cms")](ra.fetch_capture(page, str(t["earlier"])), page, t)
    extra = [x for x in e_items if x["type"] in ("text", "profile") and len(ra.norm(x.get("original", ""))) >= 12 and ra.norm(x["original"]) not in have]
    print(f"== {t['stem']}: {len(extra)} paragraph(s) only in {t['earlier']}")
    if dry or not extra:
        for x in extra:
            print(f"   [{x['type']}/{x.get('speaker', '')}] {x['original'][:80]}")
        return
    head = {"type": "heading", "level": 2, "source": "editor", "original": t["earlier_label_ja"], "translation": t["earlier_label"]}
    translate([head] + extra, t, glossary)
    head["translation"] = t["earlier_label"]          # the editor's own wording, not the model's
    out = [head] + finish_items(extra, page, str(t["earlier"]), t.get("img_dir") or _old_img_dir(t["stem"]) or t["stem"],
                                extra={"from_capture": str(t["earlier"])})
    block = yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=1000)
    # the items list ends where the next top-level key begins
    m = re.search(r"^parallel_items:\n(?:(?:- |  ).*\n)+", text, re.M)
    nl = "\r\n" if "\r\n" in text[:2000] else "\n"
    new = text[:m.end()] + block.replace("\n", nl) + text[m.end():]
    path.write_text(new, "utf-8", newline="")
    print(f"   appended {len(out)} item(s) to {path.name}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry" in sys.argv
    conf = yaml.safe_load(TARGETS.read_text("utf-8"))
    targets = {t["stem"]: t for t in conf["targets"]}
    if "--list" in sys.argv:
        for s, t in targets.items():
            print(f"{s:<66} {t['page']}@{t['capture']}  {'re-import' if (POSTS / (s + '.md')).exists() else 'new'}")
        return
    pages = {p["id"]: p for p in ra.load_pages()["pages"]}
    glossary = load_glossary()
    todo = list(targets) if "--all" in sys.argv else args
    for s in todo:
        if targets[s].get("mode") == "append_earlier":
            append_earlier(targets[s], pages, glossary, dry)
        else:
            run(targets[s], pages, glossary, dry)


if __name__ == "__main__":
    main()
