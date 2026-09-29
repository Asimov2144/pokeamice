#!/usr/bin/env python3
"""What each article is about, in a form the App's dex machine can act on.

    python tools/build-post-lore.py --pilot 50        # the pilot set: 50 entries across the kinds
    python tools/build-post-lore.py --only interview-wedge-ishihara-pokemon-disney
    python tools/build-post-lore.py --all             # every post
    python tools/build-post-lore.py --no-llm          # the rule pass only (free, no model)
    python tools/build-post-lore.py --relations       # stage two: the links between articles
    python tools/build-post-lore.py --concepts        # stage three: the concept pass (rules only, free)
    python tools/build-post-lore.py --force           # ignore the cache

Same shape as the travel map's dex-lore: one record per subject, machine-written but
carrying where it came from, editable by hand, and re-run only where the input changed.

Writes data/post_lore/<id>.json - one file per article, the record itself:

  facets        the Pokémon, works, places and people the article actually names, each
                with the paragraph numbers where it is named. The numbers are the
                exporter's own segment numbers (this script calls its normalizer), so
                `docs:post/<id>?s=<n>` lands on that paragraph in the App's reader.
                Pokémon carry the national dex number, works and people their slug,
                places the travel map's place id when the gazetteer has it.
  observations  one or two concrete things the article says, each pinned to the paragraph
                that says it - what the dex machine quotes, and what a reader's excerpt
                from that paragraph can be answered with.
  relations     the articles this one is definitely tied to: the same occasion told
                twice, a later piece that answers or corrects this one, the interview a
                column refers to. Candidates come from shared people, works and dates;
                the model only keeps the ones it can say why about.
  sources       which table version and which model produced it, and whether a person
                has since edited it (`edited: true` is never overwritten).

and collects them into _data/post_lore.yml, keyed by the post's file stem, for the
article page's 「本篇提到」 column; tools/export-docs-archive.py merges the same records
into assets/data/app/posts/<id>.json and index.json for the App.

The model is DeepSeek, as in build-people-profiles.py, and every answer is cached in
data/cache_lore/<id>.json against a hash of exactly what it was shown, so a re-run costs
nothing for articles whose text did not change.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
LORE = ROOT / "data" / "post_lore"
CACHE = ROOT / "data" / "cache_lore"
TABLES = ROOT / "data" / "lore_tables"
OUT_YML = ROOT / "_data" / "post_lore.yml"
FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)
REV = 1


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


xp = _load("export_docs_archive", ROOT / "tools" / "export-docs-archive.py")
nom = _load("import_nom", ROOT / "tools" / "import-nom.py")

MAX_SEG_CHARS = 200          # per paragraph, in what the model is shown
MAX_PROMPT_CHARS = 9000      # the whole body it is shown
MAX_CANDIDATES = 8           # related-article candidates per post
SYSTEM = ("你是宝可梦开发史料库的编辑，为每篇文章写「图鉴条目」：这篇点名提到了什么，以及一两条能在指定段落里核对的具体观察。"
          "只依据给出的段落，不补充材料之外的事实，不评价，不使用感叹号；人名、作品名、地名照原文的写法；只输出合法 JSON。")

# ---------------------------------------------------------------- the tables


def load_tables() -> dict:
    out = {}
    for name in ("pokemon_names", "tour_places"):
        path = TABLES / f"{name}.json"
        if not path.exists():
            raise SystemExit(f"{path} is missing - run tools/sync-lore-tables.py first")
        out[name] = json.load(io.open(path, encoding="utf-8"))
    return out


HAN = re.compile(r"[㐀-鿿぀-ヿ]")
ASCII_ONLY = re.compile(r"^[\x20-\x7e]+$")


def pokemon_matcher(table: dict):
    """名字 -> 图鉴号。中日文写法三个字起（「梦幻」「波波」是常用词，两个字的只认标签里的原样命中）；
    英文名要词边界，五个字母起（Ho-Oh / Mew 在中文正文里几乎只会误中）。"""
    names = table["names"]
    cjk = sorted((n for n in names if not ASCII_ONLY.match(n) and len([*n]) >= 3), key=len, reverse=True)
    latin = sorted((n for n in names if ASCII_ONLY.match(n) and len(n) >= 5), key=len, reverse=True)
    cjk_re = re.compile("|".join(re.escape(n) for n in cjk))
    latin_re = re.compile(r"(?<![A-Za-z])(" + "|".join(re.escape(n) for n in latin) + r")(?![A-Za-z])")
    return cjk_re, latin_re


BRACKET = re.compile(r"[（(].*?[)）]")
#  行政区划与国家：文章里的「东京」「日本」「纽约」是背景，不是能去的一处地方。
#  名字带这些尾字的算区划；此外这张表补上外国城市与国名（模型最常写的那些）。
ADMIN_TAIL = re.compile(r"[市区町村県府都州省郡島県]$")
ADMIN_NAMES = {
    "日本", "美国", "中国", "韩国", "法国", "德国", "英国", "意大利", "西班牙", "加拿大", "澳大利亚", "台湾", "香港",
    "欧洲", "亚洲", "北美", "海外", "关东", "关西", "九州", "四国", "北海道", "东北", "冲绳",
    "东京", "大阪", "京都", "名古屋", "横滨", "神户", "札幌", "福冈", "广岛", "仙台", "千叶", "埼玉", "神奈川",
    "纽约", "洛杉矶", "旧金山", "西雅图", "芝加哥", "波士顿", "华盛顿", "拉斯维加斯", "圣迭戈", "奥兰多", "夏威夷",
    "伦敦", "巴黎", "柏林", "米兰", "罗马", "阿姆斯特丹", "首尔", "上海", "北京", "台北", "曼哈顿", "布鲁克林",
    "涩谷", "涉谷", "新宿", "池袋", "秋叶原", "银座", "台场", "六本木", "原宿", "中野", "吉祥寺",
    "小田原", "金泽", "熊本", "马德里", "阿纳海姆", "西雅图", "温哥华", "多伦多", "墨尔本", "悉尼",
    "关岛", "夏威夷州", "加州", "德州", "佛罗里达", "内华达", "俄亥俄", "新泽西", "长野", "静冈",
    "奈良", "和歌山", "鹿儿岛", "宫城", "岩手", "福岛", "石川", "富山", "新潟", "群马", "栃木",
}


def dated(rec: dict, year: str) -> dict:
    """手写补充里分了时期的（GAME FREAK 的办公室搬过两次），按文章年份取那一段。"""
    periods = rec.get("by_year")
    if not periods or not year.isdigit():
        return rec
    y = int(year)
    for period in periods:
        frm, to = period.get("from"), period.get("to")
        if (frm is None or y >= int(frm)) and (to is None or y <= int(to)):
            return {**rec, **{k: v for k, v in period.items() if k not in ("from", "to")},
                    "id": period.get("place", rec.get("id")), "by_year": None}
    return rec


def when_of(rec: dict, year: str) -> str:
    """文章的年份对着这一处的营业期：文章更早是 before，更晚是 after，在期内是空。

    旅图只收了「宝可梦中心横滨」2018 年起的那一处，而 2016 年的博客也在说这家店——
    连过去仍然有用（今天要去就是去那儿），但不能让读的人以为文章当年说的就是这一处。"""
    if not year.isdigit():
        return ""
    frm, to = (rec.get("from") or "")[:4], (rec.get("to") or "")[:4]
    if frm and year < frm:
        return "before"
    if to and year > to:
        return "after"
    return ""


def scale_of(name: str) -> str:
    """一处地方还是一片地区"""
    return "area" if name in ADMIN_NAMES or ADMIN_TAIL.search(name) else "spot"


def load_extra() -> list:
    """手写的地名补充（data/lore_tables/places_extra.yml）。没有这张表也照跑。"""
    path = TABLES / "places_extra.yml"
    rows = yaml.safe_load(io.open(path, encoding="utf-8")) if path.exists() else []
    return [r for r in (rows or []) if isinstance(r, dict) and r.get("name")]


def place_matcher(table: dict):
    """地名 -> 旅图地点。三个字起，同一个写法对上好几处时取还开着的、名字里没有括号注记的那一条。

    店址与店分两层，和 App 那张对照表一致：「宝可梦中心 东京（日本桥初代店址）」是一处店址（id），
    而文章里写的「宝可梦中心东京」说的是这家店本身——那给 entity（pokemon_center_tokyo），id 留空，
    由 App 按文章日期落到当时的那一处。"""
    def rank(p: dict) -> tuple:
        return (0 if p.get("status") == "current" else 1, 0 if "（" not in p["name"] else 1, p["id"])

    index: dict[str, dict] = {}

    def reg(spelling: str, rec: dict) -> None:
        if len([*spelling]) >= 3:
            index.setdefault(spelling, rec)

    for p in sorted(table["places"], key=rank):
        spot = {"id": p["id"], "entity": p.get("entity"), "category": p.get("category"),
                "from": p.get("from"), "to": p.get("to")}
        shop = {"id": None, "entity": p.get("entity"), "category": p.get("category")}
        for spelling in [p["name"], *p.get("aliases", [])]:
            #  「宝可梦中心 名古屋（松坂屋二代店址）」说的是那一处店址；不带括号的「宝可梦中心名古屋」
            #  说的是这家店本身——2012 年的文章写它，指的是当时那一处，不是 2024 年的新址。
            #  所以有店址沿革的，只有带括号的写法给 id，其余给 entity，由 App 按日期落。
            bracketed = "（" in spelling or "(" in spelling
            reg(spelling, spot if (not p.get("entity") or bracketed) else shop)
    for p in table["places"]:
        if not p.get("entity"):
            continue
        plain = BRACKET.sub("", p["name"]).strip()
        rec = {"id": None, "entity": p["entity"], "category": p.get("category")}
        reg(plain, rec)
        reg(re.sub(r"\s", "", plain), rec)
    #  手写的补充最后登记，但用 dict 的 setdefault 规则它只填空位——旅图已有的写法不被顶掉
    unscanned = set()
    for extra in load_extra():
        rec = {"id": extra.get("place"), "entity": extra.get("entity"), "category": extra.get("category"),
               "area": extra.get("area"), "what": extra.get("what"), "scale": extra.get("scale"),
               "by_year": extra.get("by_year"), "canon": extra["name"], "via": "extra"}
        for spelling in [extra["name"], *(extra.get("aliases") or [])]:
            spelling = str(spelling)
            reg(spelling, rec)
            if extra.get("scan") is False:
                unscanned.add(spelling)
    #  scan: false 的写法（公司名、「宝可梦中心」这种泛称）不进扫正文的那条正则：
    #  满篇都是的词，每出现一次就算「提到一个地方」是错的；模型把它点成地点时才认
    keys = sorted((k for k in index if k not in unscanned), key=len, reverse=True)
    return re.compile("|".join(re.escape(k) for k in keys)), index


# ---------------------------------------------------------------- the library


def people_index() -> tuple[dict, dict]:
    """名字（含别名）-> slug，以及 slug -> kind。

    kind 要带出去：动画角色（character）与只被引述的人物（figure，黑泽明、华特·迪士尼）
    在人物库里有 slug，却没有人物页——tools/build-people.py 不给它们建页。文章页照着 kind
    决定要不要做成链接，不然「黑泽明」会连到一个 404。"""
    rows = yaml.safe_load(io.open(ROOT / "_data" / "people.yml", encoding="utf-8")) or []
    by_name, kinds = {}, {}
    for p in rows:
        slug = (p.get("slug") or "").strip()
        if not slug:
            continue
        kinds[slug] = (p.get("kind") or "person").strip()
        for name in [p.get("name"), *(p.get("aliases") or [])]:
            name = (name or "").strip()
            if name:
                by_name.setdefault(name, slug)
    return by_name, kinds


def works_index() -> dict:
    works = yaml.safe_load(io.open(ROOT / "_data" / "works.yml", encoding="utf-8")) or []
    games = yaml.safe_load(io.open(ROOT / "_data" / "credits_games.yml", encoding="utf-8")) or []
    slug_of = {g.get("work"): g.get("slug") for g in games if g.get("work")}
    return {w["name"]: {"name": w["name"], "slug": slug_of.get(w["name"])} for w in works if w.get("name")}


def as_list(value) -> list:
    if value is None:
        return []
    return [v for v in (value if isinstance(value, list) else [value]) if v]


def anchor_map(items: list) -> list:
    """段号 -> 文章页上的锚点号。

    导出用的段号是过滤后的序号（空段、没有图的图片段都不算），文章页的 id="segment-N" 用的是
    parallel_items 的原序号（从 1 起，什么都不跳）。两者多数时候只差一，但不保证——所以照
    normalize_parallel 的取舍再走一遍，记下每个留下来的段落原来排第几。扫描件的版面是按页重排的，
    对不上这套编号，不给锚点。"""
    out = []
    for i, raw in enumerate(items, 1):
        if not isinstance(raw, dict):
            continue
        kind = xp.SEGMENT_TYPES.get(xp.clean(raw.get("type"))) or ("dialogue" if xp.clean(raw.get("speaker")) else "paragraph")
        image = xp.abs_url(raw.get("image") or raw.get("src"))
        if kind == "image" and not image:
            continue
        if kind != "image" and not xp.clean(raw.get("original")) and not xp.clean(raw.get("translation")):
            continue
        out.append(i)
    return out


def blog_author() -> dict:
    """博客的作者写在博客的资料里，不在每篇的前言里：部长专栏与 LINE BLOG 是增田顺一，
    复刻的旧博客按 gf_legacy_blog 分（绘画日和是杉森建，员工博客是 GAME FREAK 员工）。"""
    out = {}
    for key, path in (("gamefreak_director_column", "gamefreak_director.yml"),
                      ("gamefreak_masuda_lineblog", "gamefreak_lineblog.yml")):
        data = yaml.safe_load(io.open(ROOT / "_data" / path, encoding="utf-8")) or {}
        who = data.get("author") or {}
        out[key] = who.get("name_zh") or who.get("name") or ""
    blogs = yaml.safe_load(io.open(ROOT / "_data" / "gamefreak_legacy_blogs.yml", encoding="utf-8")) or {}
    for slug, blog in blogs.items():
        out["legacy:" + str(slug)] = blog.get("author_zh") or blog.get("author") or ""
    return out


def load_posts() -> list[dict]:
    """front matter + the exporter's own segments, so the paragraph numbers are the App's."""
    authors = blog_author()
    out = []
    for f in sorted((ROOT / "_posts").glob("*.md")):
        text = io.open(f, encoding="utf-8", errors="replace").read()
        m = FRONT.match(text)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        if fm.get("published") is False:
            continue
        body_md = text[m.end():]
        stem = f.stem
        post_id = xp.jekyll_title_slug(xp.DATE_PREFIX.sub("", stem))
        kind = xp.kind_of(fm)
        anchors = []
        if fm.get("parallel_items"):
            segs = xp.normalize_parallel(fm["parallel_items"], {})
            anchors = anchor_map(as_list(fm.get("parallel_items")))
            body_kind = "segments"
        elif fm.get("translation_segments"):
            segs = xp.normalize_scan(fm["translation_segments"], {})
            body_kind = "segments"
        else:
            zh = xp.split_blog(body_md)["markdown_zh"]
            blocks = [b.strip() for b in re.split(r"\n\s*\n", zh) if b.strip()]
            segs = [{"n": i, "type": "paragraph", "translation": re.sub(r"\s+", " ", re.sub(r"[#>*_`]|!?\[[^\]]*\]\([^)]*\)", " ", b)).strip()}
                    for i, b in enumerate(blocks)]
            segs = [s for s in segs if s["translation"]]
            body_kind = "markdown"
        legacy = fm.get("gf_legacy_blog") or fm.get("gf_blog") or ""
        author = str(fm.get("author") or "").strip() or authors.get(str(fm.get("archive_type") or "").strip()) or authors.get("legacy:" + str(legacy)) or ""
        out.append({"stem": stem, "id": post_id, "fm": fm, "kind": kind, "segs": segs, "anchors": anchors, "body_kind": body_kind, "author": author,
                    "title": (fm.get("display_title") or fm.get("title") or "").strip(),
                    "date": str(fm.get("date") or stem[:10])[:10],
                    "publication": (fm.get("publication") or (fm.get("source") or {}).get("title") if isinstance(fm.get("source"), dict) else fm.get("publication")) or ""})
    return out


def seg_text(seg: dict) -> str:
    return (seg.get("translation") or seg.get("original") or seg.get("caption") or "").strip()


# ---------------------------------------------------------------- the rule pass


def hits(pattern: re.Pattern, segs: list, group: bool = False) -> dict:
    """匹配到的写法 -> 出现的段号（最多记 6 段）"""
    found: dict[str, list] = {}
    for seg in segs:
        text = seg_text(seg)
        if not text:
            continue
        for m in pattern.finditer(text):
            word = m.group(1) if group else m.group(0)
            spots = found.setdefault(word, [])
            if seg["n"] not in spots and len(spots) < 6:
                spots.append(seg["n"])
    return found


def rule_facets(post: dict, tables: dict, matchers: dict, people_by_name: dict, kinds: dict, works: dict) -> dict:
    fm = post["fm"]
    segs = post["segs"]
    ents = fm.get("entities") or {}
    tags = [str(t).strip() for t in as_list(fm.get("tags"))]
    names, zh = tables["pokemon_names"]["names"], tables["pokemon_names"]["zh"]

    # --- 宝可梦：标签原样命中最可靠，正文按写法表命中
    poke: dict[int, dict] = {}

    def add_poke(spelling: str, spots: list, via: str):
        ndex = names.get(spelling)
        if not ndex:
            return
        # 写法表里一个图鉴号下有通常与地方形态，zh 表给的未必是通常形态（571 给的是洗翠索罗亚克）：
        # 中文写法照原文留着，只有日文 / 英文写法才换成 zh 表的名字
        name = spelling if HAN.search(spelling) else (zh.get(str(ndex)) or spelling)
        rec = poke.setdefault(ndex, {"name": name, "ndex": ndex, "seg": [], "as": [], "via": via})
        if spelling not in rec["as"]:
            rec["as"].append(spelling)
        for n in spots:
            if n not in rec["seg"]:
                rec["seg"].append(n)

    for tag in tags:
        if tag in names:
            add_poke(tag, [], "tag")
    for spelling, spots in hits(matchers["poke_cjk"], segs).items():
        add_poke(spelling, spots, "body")
    for spelling, spots in hits(matchers["poke_latin"], segs, group=True).items():
        add_poke(spelling, spots, "body")
    for spelling in names:
        if len([*spelling]) >= 3 and spelling in post["title"]:
            add_poke(spelling, [], "title")

    # --- 作品：前言里的 entities.works 是编者写的，正文里再找出现处
    work_out = []
    for name in as_list(ents.get("works")):
        name = str(name).strip()
        spots = []
        for seg in segs:
            if name and name in seg_text(seg):
                spots.append(seg["n"])
            if len(spots) >= 6:
                break
        known = works.get(name) or {}
        work_out.append({"name": name, "slug": known.get("slug"), "seg": spots, "via": "entities"})

    # --- 人：发言人 + entities.people
    # 扫描件的 speaker 字段里混着版面标题与图注小标（「全面解析 ALL ABOUT 宝可梦 黑」「颜色数量少令人恐惧」），
    # 不是人名：人物库认得出的一律留；认不出的要短、干净，而且至少开口两次——标题只出现一次
    said = collections.Counter((seg.get("speaker") or "").strip() for seg in segs)
    speakers = []
    for seg in segs:
        who = (seg.get("speaker") or "").strip()
        if not who or who in speakers:
            continue
        if not people_by_name.get(who) and (said[who] < 2 or len([*who]) > 8 or re.search(r"[\s　！？。、，,!?]|^[—―─–-]+$", who)):
            continue
        speakers.append(who)
    people_out = []
    seen_people = set()
    for name in speakers + [str(p).strip() for p in as_list(ents.get("people"))]:
        if not name or name in seen_people:
            continue
        seen_people.add(name)
        spots = [seg["n"] for seg in segs if (seg.get("speaker") or "").strip() == name][:6]
        if not spots:
            spots = [seg["n"] for seg in segs if name in seg_text(seg)][:6]
        slug = people_by_name.get(name)
        row = {"name": name, "slug": slug, "role": "speaker" if name in speakers else "mentioned", "seg": spots}
        if slug and kinds.get(slug, "person") != "person":
            row["kind"] = kinds[slug]          # character / figure：有 slug，没有人物页
        people_out.append(row)

    # --- 地点：旅图 gazetteer 命中的
    place_out = []
    seen_spots = set()
    for spelling, spots in hits(matchers["place"], segs).items():
        p = dated(matchers["place_index"][spelling], post["date"][:4])
        #  同一处地方的几种写法（六本木新城 / Roppongi Hills / 六本木ヒルズ）只算一处，
        #  段号并到先出现的那个写法上
        key = p.get("canon") or p.get("id") or p.get("entity")
        if key and key in seen_spots:
            same = next(r for r in place_out if r.get("_key") == key)
            same["seg"] = (same["seg"] + [n for n in spots if n not in same["seg"]])[:6]
            continue
        if key:
            seen_spots.add(key)
        row = {"name": spelling, "id": p["id"], "entity": p.get("entity"), "category": p.get("category"),
               "world": "real", "scale": p.get("scale") or scale_of(spelling), "seg": spots,
               "via": p.get("via") or "gazetteer"}
        for field in ("area", "category_link", "what"):
            if p.get(field):
                row[field] = p[field]
        if p.get("via") == "extra" and p.get("category"):
            row["category_link"] = p["category"]      # App 对照表里的那一类（categories.pc）
        when = when_of(p, post["date"][:4]) if p.get("id") else ""
        if when:
            row["when"] = when
        if key:
            row["_key"] = key
        place_out.append(row)
    for row in place_out:
        row.pop("_key", None)
    return {"pokemon": sorted(poke.values(), key=lambda r: r["ndex"]), "works": work_out,
            "people": people_out, "places": place_out}


# ---------------------------------------------------------------- the model pass


def body_for_model(post: dict) -> str:
    rows = []
    for seg in post["segs"]:
        text = seg_text(seg)
        if not text:
            continue
        if len(text) > MAX_SEG_CHARS:
            text = text[:MAX_SEG_CHARS] + "…"
        who = (seg.get("speaker") or "").strip()
        rows.append((seg["n"], f"[{seg['n']}] {who + '：' if who else ''}{text}"))
    total = sum(len(r[1]) for r in rows)
    if total > MAX_PROMPT_CHARS and len(rows) > 6:
        # 均匀取样，段号照旧，跳过处写省略号——段号必须还是真的，App 要用它跳转
        keep = max(6, int(len(rows) * MAX_PROMPT_CHARS / total))
        step = len(rows) / keep
        picked = [rows[int(i * step)] for i in range(keep)]
        lines, last = [], None
        for n, line in picked:
            if last is not None and n > last + 1:
                lines.append("…")
            lines.append(line)
            last = n
        return "\n".join(lines)
    return "\n".join(line for _, line in rows)


def parse_json(raw: str):
    """模型的回答读成 JSON。偶尔会在字符串里漏个引号或者在末尾多写一句话——
    先整份读，不行就截出最外层的大括号再读一次。都不行返回 None，由调用方决定重问。"""
    inner = re.search(r"\{.*\}", raw or "", re.S)
    for text in (raw, inner.group(0) if inner else None):
        if not text:
            continue
        try:
            got = json.loads(text)
        except ValueError:
            continue
        if isinstance(got, dict):
            return got
    return None


def ask_lore(post: dict, facets: dict) -> dict:
    known_people = "、".join(p["name"] for p in facets["people"][:8]) or "（未记）"
    known_works = "、".join(w["name"] for w in facets["works"][:8]) or "（未记）"
    prompt = (f"文章：《{post['title']}》\n"
              f"出处：{post['publication'] or '未记'}　{post['date']}　（{post['kind']}）\n"
              + (f"作者：{post['author']}——正文里的「我」就是他，观察里写他的名字，不要写「作者」\n" if post.get("author") else "")
              + f"已知人物：{known_people}\n已知作品：{known_works}\n\n"
              f"正文按段编号，[n] 是段号：\n\n{body_for_model(post)}\n\n"
              "请输出 JSON：\n"
              '{"observations":[{"seg":0,"text":"…"}],"pokemon":[{"name":"…","seg":0}],'
              '"places":[{"name":"…","seg":0,"what":"…"}],"works":[{"name":"…","seg":0}],"people":[{"name":"…","seg":0}]}\n\n'
              "observations：1–2 条，每条 ≤48 字，写那一段里具体说了什么——一个事实、数字、决定或理由，"
              "要能在该段文字里核对；seg 必须是上面出现过的段号。不要概括全文，不要评价，不要写「本文介绍了」。\n"
              "pokemon：规则已经按写法表扫过一遍，这里只补规则漏掉的（别称、旧译名），最多 8 个，写中文名。\n"
              "places：正文点名的具体地点，最多 8 个，挑这篇里真正要紧的。what 写 8 字以内说明它在这篇里是什么"
              "（如「宝可梦公司总部」）；world 写 real（现实地点，如「六本木新城」「宝可梦中心东京」）"
              "或 game（游戏与动画里的地方，如「合众地区」「真新镇」）；泛指的国家与地区（日本、海外、欧美）不写。\n"
              "works：正文点名的作品；people：正文点名的人。都写出现处的段号。\n"
              "拿不准的不写。")
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}]
    got = parse_json(nom.deepseek(messages, max_tokens=1800))
    if got is None:
        #  再问一次，把「只要 JSON」说死；两次都不成才算这篇失败
        got = parse_json(nom.deepseek(messages + [{"role": "user", "content": "上一次的回答不是合法 JSON。只输出那一个 JSON 对象，不要任何解释文字。"}], max_tokens=1800))
    if got is None:
        raise ValueError("bad answer")
    return got


def lore_key(post: dict) -> str:
    h = hashlib.sha1()
    h.update(f"{REV}|{post['title']}|{post['date']}|{post['publication']}|{post.get('author') or ''}".encode("utf-8"))
    h.update(body_for_model(post).encode("utf-8"))
    return h.hexdigest()[:16]


def merge_model(facets: dict, got: dict, post: dict, tables: dict, matchers: dict, people_by_name: dict, kinds: dict, works: dict) -> list:
    """模型点出来的名字，能对上表的对上，对不上的按名字留着（id 为 null，App 显示成纯文字）"""
    valid = {seg["n"] for seg in post["segs"]}
    names, zh = tables["pokemon_names"]["names"], tables["pokemon_names"]["zh"]

    def seg_of(row) -> list:
        n = row.get("seg")
        return [n] if isinstance(n, int) and n in valid else []

    for row in got.get("pokemon") or []:
        name = str(row.get("name") or "").strip()
        ndex = names.get(name)
        if not ndex:
            continue
        rec = next((p for p in facets["pokemon"] if p["ndex"] == ndex), None)
        if rec is None:
            facets["pokemon"].append({"name": zh.get(str(ndex)) or name, "ndex": ndex, "seg": seg_of(row), "as": [name], "via": "llm"})
        else:
            for n in seg_of(row):
                if n not in rec["seg"]:
                    rec["seg"].append(n)
    for row in (got.get("places") or [])[:10]:
        name = str(row.get("name") or "").strip()
        if not name or len([*name]) < 2:
            continue
        if any(p["name"] == name for p in facets["places"]):
            continue
        canon = (matchers["place_index"].get(name) or {}).get("canon")
        if canon and any((matchers["place_index"].get(q["name"]) or {}).get("canon") == canon for q in facets["places"]):
            continue                      # 「六本木新城」和「Roppongi Hills」是同一处，只留先出现的那个写法
        p = dated(matchers["place_index"].get(name) or matchers["place_index"].get(re.sub(r"\s", "", name)) or {}, post["date"][:4])
        world = "game" if str(row.get("world") or "").strip() == "game" else "real"
        out_row = {"name": name, "id": p.get("id"), "entity": p.get("entity"), "category": p.get("category"),
                   "world": world, "scale": p.get("scale") or scale_of(name), "seg": seg_of(row),
                   "what": str(row.get("what") or "").strip() or p.get("what") or None, "via": p.get("via") or "llm"}
        if p.get("area"):
            out_row["area"] = p["area"]
        if p.get("via") == "extra" and p.get("category"):
            out_row["category_link"] = p["category"]
        when = when_of(p, post["date"][:4]) if p.get("id") else ""
        if when:
            out_row["when"] = when
        facets["places"].append(out_row)
    #  榜单一类的文章会点出二十个地名。先是连得上旅图的，再是具体的一处，再是写了段号的；
    #  「东京」「日本」这种背景地区排最后，最多留十个
    facets["places"].sort(key=lambda p: (0 if (p.get("id") or p.get("entity") or p.get("area") or p.get("category_link")) else 1,
                                         0 if p.get("scale") == "spot" else 1,
                                         0 if p.get("seg") else 1))
    del facets["places"][10:]
    for row in got.get("works") or []:
        name = str(row.get("name") or "").strip()
        if not name or any(w["name"] == name for w in facets["works"]):
            continue
        facets["works"].append({"name": name, "slug": (works.get(name) or {}).get("slug"), "seg": seg_of(row), "via": "llm"})
    for row in got.get("people") or []:
        name = str(row.get("name") or "").strip()
        if not name or any(p["name"] == name for p in facets["people"]):
            continue
        slug = people_by_name.get(name)
        row_out = {"name": name, "slug": slug, "role": "mentioned", "seg": seg_of(row), "via": "llm"}
        if slug and kinds.get(slug, "person") != "person":
            row_out["kind"] = kinds[slug]
        facets["people"].append(row_out)

    obs = []
    for row in got.get("observations") or []:
        text = str(row.get("text") or "").strip()
        n = row.get("seg")
        if not text or not isinstance(n, int) or n not in valid:
            continue
        row = {"seg": n, "text": text[:60]}
        #  文章页只给问答与段落写 id="segment-N"：小标题是 id="section-N"，图片没有 id。
        #  钉在小标题或图片上的观察就不给锚点，免得连到一个页面上不存在的位置。
        kind = (post["segs"][n].get("type") if n < len(post["segs"]) else "") or ""
        anchor = post["anchors"][n] if (kind in ("paragraph", "dialogue") and n < len(post.get("anchors") or [])) else None
        if anchor:
            row["anchor"] = anchor          # 文章页 #segment-N 用的号，和 App 的段号不是一回事
        obs.append(row)
        if len(obs) >= 2:
            break
    return obs


# ---------------------------------------------------------------- stage two: the links


def candidates(post: dict, facets: dict, all_posts: list, lore_by_id: dict) -> list:
    """同人、同作品、同出处、日期相近的几篇——只当候选，由模型判定有没有真的关系"""
    mine_people = {p["slug"] for p in facets["people"] if p.get("slug")}
    mine_works = {w["slug"] or w["name"] for w in facets["works"]}
    mine_year = int(post["date"][:4] or 0)
    scored = []
    for other in all_posts:
        if other["id"] == post["id"]:
            continue
        of = (lore_by_id.get(other["id"]) or {}).get("facets") or {}
        people = {p["slug"] for p in of.get("people", []) if p.get("slug")} or {
            str(x).strip() for x in as_list((other["fm"].get("entities") or {}).get("people"))}
        works = {w.get("slug") or w.get("name") for w in of.get("works", [])} or {
            str(x).strip() for x in as_list((other["fm"].get("entities") or {}).get("works"))}
        score = 2 * len(mine_people & people) + 2 * len(mine_works & works)
        if other["publication"] and other["publication"] == post["publication"]:
            score += 2
        try:
            gap = abs(int(other["date"][:4]) - mine_year)
        except ValueError:
            gap = 99
        if gap == 0:
            score += 3
        elif gap <= 2:
            score += 1
        if score >= 5:
            scored.append((score, other))
    scored.sort(key=lambda s: (-s[0], s[1]["date"]))
    return [o for _, o in scored[:MAX_CANDIDATES]]


KINDS = {"same-occasion": "同一件事的另一种说法", "responds": "后来回应了这篇", "corrects": "更正了这篇的说法",
         "continues": "同一系列的前后篇", "background": "为这篇提供背景"}
PREFIXES = ("[访谈翻译] ", "[扫描访谈] ", "[专栏翻译] ", "[GameFreak部长专栏] ")


def short_title(post: dict) -> str:
    """列表里写的那个标题：副题优先，去掉方括号里的类别前缀"""
    title = str(post["fm"].get("display_title") or post["fm"].get("title") or post["id"]).strip()
    for prefix in PREFIXES:
        title = title.replace(prefix, "")
    return title.strip()


def site_path(post: dict) -> str:
    """站内地址（根相对）。照导出器的 canonical_url 算，省得文章页为了每条关系去扫一遍 site.posts。"""
    return xp.canonical_url(post["fm"], post["id"]).replace(xp.SITE, "")


def ask_relations(post: dict, facets: dict, cands: list, lore_by_id: dict) -> list:
    def brief(p) -> str:
        lore = lore_by_id.get(p["id"]) or {}
        obs = "；".join(o["text"] for o in (lore.get("observations") or [])[:2])
        summary = str(p["fm"].get("summary") or p["fm"].get("dek") or "").strip()[:160]
        return f"《{p['title']}》（{p['publication'] or '出处未记'}，{p['date']}）：{summary}{'　观察：' + obs if obs else ''}"

    mine = lore_by_id.get(post["id"]) or {}
    listing = "\n".join(f"[{i + 1}] {brief(p)}" for i, p in enumerate(cands))
    prompt = (f"这一篇：{brief(post)}\n"
              f"本篇的观察：{'；'.join(o['text'] for o in (mine.get('observations') or [])) or '（无）'}\n\n"
              f"候选文章：\n{listing}\n\n"
              "哪几篇与这一篇有明确关系？关系只用这五种：\n"
              "same-occasion（同一场访谈/发布会/讲演的另一篇报道）、continues（同一系列或同一篇的前后篇）、"
              "responds（后来的那篇回应、补充了这一篇说的事）、corrects（后来的那篇更正了这一篇的说法）、"
              "background（这一篇要读懂需要那一篇给的背景）。\n"
              '输出 {"relations":[{"i":1,"kind":"same-occasion","why":"…"}]}，why ≤30 字，写出具体是哪件事对上了。\n'
              "只写材料里看得出来的；同一个人谈过同一个作品不算关系。没有就给空数组。")
    got = parse_json(nom.deepseek([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], max_tokens=700)) or {}
    out = []
    for row in (got.get("relations") or []) if isinstance(got, dict) else []:
        i, kind = row.get("i"), str(row.get("kind") or "").strip()
        if not isinstance(i, int) or not 1 <= i <= len(cands) or kind not in KINDS:
            continue
        other = cands[i - 1]
        out.append({"id": other["id"], "kind": kind, "label": KINDS[kind],
                    "title": short_title(other), "url": site_path(other),
                    "why": str(row.get("why") or "").strip()[:40]})
    return out[:4]


# ---------------------------------------------------------------- 概念：人写的词表，逐段命中

_CONCEPTS_VERSION = None
CONCEPTS_YML = TABLES / "concepts.yml"
CONCEPTS_REVIEW = TABLES / "concepts.review.json"
EVIDENCE = ROOT / "design" / "concepts-evidence.json"
LATIN = re.compile(r"\A[\x20-\x7e]+\Z")


def alias_re(aliases: list):
    """写法表 -> 一个正则。中日文按子串（长的先试），拉丁字母要词边界。"""
    cjk = sorted({a for a in aliases if a and not LATIN.match(a)}, key=len, reverse=True)
    lat = sorted({a for a in aliases if a and LATIN.match(a)}, key=len, reverse=True)
    parts = []
    if cjk:
        parts.append("|".join(re.escape(a) for a in cjk))
    if lat:
        parts.append(r"(?<![A-Za-z0-9])(?:" + "|".join(re.escape(a) for a in lat) + r")(?![A-Za-z0-9])")
    return re.compile("|".join(parts)) if parts else None


def concepts_version() -> str:
    global _CONCEPTS_VERSION
    if _CONCEPTS_VERSION is None:
        raw = yaml.safe_load(io.open(CONCEPTS_YML, encoding="utf-8")) or {}
        _CONCEPTS_VERSION = str(raw.get("version") or "")
    return _CONCEPTS_VERSION


def load_concepts() -> list:
    """词表 data/lore_tables/concepts.yml + 人审的裁定 concepts.review.json。

    裁定单独放一个文件：审核工具（Pokeamice_app/tools/lore-review 的「概念词表」队列）只往那里写，
    词表本身保持人手写的样子。裁定按 id 覆盖 status 与改过的字段，approved 的才算人审过。"""
    if not CONCEPTS_YML.exists():
        raise SystemExit(f"{CONCEPTS_YML} is missing")
    raw = yaml.safe_load(io.open(CONCEPTS_YML, encoding="utf-8")) or {}
    review = {}
    if CONCEPTS_REVIEW.exists():
        blob = json.load(io.open(CONCEPTS_REVIEW, encoding="utf-8"))
        review = blob.get("verdicts") or {k: v for k, v in blob.items() if isinstance(v, dict) and not k.startswith("_")}
    facets = raw.get("facets") or {}
    out = []
    for ent in raw.get("concepts") or []:
        if not isinstance(ent, dict) or not ent.get("id"):
            continue
        ent = dict(ent)
        said = review.get(ent["id"]) or {}
        for field in ("name", "facet", "gloss", "aliases", "with", "avoid", "note"):
            if said.get(field):
                ent[field] = said[field]
        verdict = said.get("verdict") or ""
        if verdict in ("approve", "approved", "keep"):
            ent["status"] = "approved"
        elif verdict in ("drop", "reject", "rejected"):
            ent["status"] = "rejected"
        if ent.get("status") == "rejected":
            continue
        pattern = alias_re(as_list(ent.get("aliases")))
        if pattern is None:
            print(f"  concept {ent['id']} has no aliases; left out")
            continue
        out.append({"id": ent["id"], "name": ent.get("name") or ent["id"], "facet": ent.get("facet") or "",
                    "facet_name": facets.get(ent.get("facet")) or "", "gloss": ent.get("gloss") or "",
                    "approved": ent.get("status") == "approved", "re": pattern,
                    "with": [w for w in as_list(ent.get("with")) if w], "avoid": [a for a in as_list(ent.get("avoid")) if a],
                    "aliases": as_list(ent.get("aliases"))})
    return out


def _in_avoid(text: str, span: tuple, avoid: list) -> bool:
    """命中处正落在「不算」的写法里（「平衡」撞上「生态平衡」）"""
    for bad in avoid:
        start = 0
        while True:
            at = text.find(bad, start)
            if at < 0:
                break
            if at <= span[0] and span[1] <= at + len(bad):
                return True
            start = at + 1
    return False


def concept_hits(post: dict, vocab: list) -> list:
    """这一篇谈到的概念，每个带段号。

    正文命中是主的（via: body）；正文里没有、但标签或标题写着的也算，那是编者写的
    （via: tag / title），只是没有段号。"""
    texts = [(s["n"], seg_text(s)) for s in post["segs"]]
    texts = [(n, t) for n, t in texts if t]
    tagtext = " / ".join(str(t).strip() for t in as_list(post["fm"].get("tags")))
    #  标题开头的体裁标记（「[访谈翻译] 」「[扫描访谈] 」）是站内的分类，不是这篇谈的事——
    #  不去掉的话「翻译」会把几百篇都收进「本地化」
    title = re.sub(r"\A\s*(\[[^\]]*\]\s*)+", "", post["title"] or "")
    out = []
    for ent in vocab:
        spots: list = []
        forms: list = []
        for n, text in texts:
            if ent["with"] and not any(w in text for w in ent["with"]):
                continue
            for m in ent["re"].finditer(text):
                if ent["avoid"] and _in_avoid(text, m.span(), ent["avoid"]):
                    continue
                if n not in spots and len(spots) < 6:
                    spots.append(n)
                if m.group(0) not in forms and len(forms) < 4:
                    forms.append(m.group(0))
                break                                      # 一段记一次就够
        via = "body" if spots else ""
        if not via:
            for where, source in (("tag", tagtext), ("title", title)):
                for m in (ent["re"].finditer(source) if source else []):
                    if ent["avoid"] and _in_avoid(source, m.span(), ent["avoid"]):
                        continue
                    via, forms = where, [m.group(0)]
                    break
                if via:
                    break
        if not via:
            continue
        row = {"id": ent["id"], "name": ent["name"], "facet": ent["facet"], "seg": spots, "as": forms, "via": via}
        if ent["approved"]:
            row["reviewed"] = True
        out.append(row)
    out.sort(key=lambda r: (r["seg"][0] if r["seg"] else 10 ** 6, r["id"]))
    return out


def annotate_concepts(posts: list, vocab: list, only: set) -> int:
    """给已有的记录补上 facets.concepts，并写出人审要看的证据 design/concepts-evidence.json"""
    seen = {ent["id"]: {"id": ent["id"], "name": ent["name"], "facet": ent["facet"], "facet_name": ent["facet_name"],
                        "gloss": ent["gloss"], "approved": ent["approved"], "aliases": ent["aliases"],
                        "with": ent["with"], "avoid": ent["avoid"],
                        "docs": 0, "segs": 0, "forms": collections.Counter(), "by_kind": collections.Counter(),
                        "samples": []} for ent in vocab}
    per_post = collections.Counter()
    touched = 0
    for post in posts:
        rec = read_record(post["id"])
        if not rec:
            continue
        if only and post["id"] not in only:
            continue
        rows = concept_hits(post, vocab)
        if rec.get("edited") and (rec.get("facets") or {}).get("concepts"):
            rows = rec["facets"]["concepts"]                # 人改过的不动
        else:
            rec.setdefault("facets", {})["concepts"] = rows
            rec.setdefault("sources", {})["concepts"] = concepts_version()
            write_record(rec)
            touched += 1
        per_post[len(rows)] += 1
        texts = {s["n"]: seg_text(s) for s in post["segs"]}
        for row in rows:
            got = seen.get(row["id"])
            if not got:
                continue
            got["docs"] += 1
            got["segs"] += len(row["seg"])
            got["by_kind"][post["kind"]] += 1
            for form in row.get("as") or []:
                got["forms"][form] += 1
            if len(got["samples"]) < 4 and row["seg"]:
                text = texts.get(row["seg"][0]) or ""
                got["samples"].append({"post": post["id"], "title": post["title"][:60], "seg": row["seg"][0],
                                       "via": row["via"], "text": text[:160]})
    rows = []
    for got in seen.values():
        got["forms"] = [f"{w}×{c}" for w, c in got["forms"].most_common(6)]
        got["by_kind"] = dict(got["by_kind"])
        rows.append(got)
    rows.sort(key=lambda r: (-r["docs"], r["id"]))
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    payload = {"generated": date.today().isoformat(), "table": str(CONCEPTS_YML.relative_to(ROOT)).replace("\\", "/"),
               "counts": {"concepts": len(rows), "matched": sum(1 for r in rows if r["docs"]),
                          "unused": [r["id"] for r in rows if not r["docs"]],
                          "posts_with": sum(c for n, c in per_post.items() if n), "posts": sum(per_post.values()),
                          "per_post": {str(n): c for n, c in sorted(per_post.items())}},
               "concepts": rows}
    io.open(EVIDENCE, "w", encoding="utf-8", newline="\n").write(json.dumps(payload, ensure_ascii=False, indent=1) + "\n")
    return touched


# ---------------------------------------------------------------- files


def read_record(post_id: str) -> dict:
    path = LORE / f"{post_id}.json"
    return json.load(io.open(path, encoding="utf-8")) if path.exists() else {}


def write_record(rec: dict) -> None:
    """一篇的记录写回去。先写同目录的临时文件再改名——1160 个文件连着写，
    偶尔会撞上杀毒软件或同步客户端正拿着那一个文件（Windows 报 Errno 22），
    整轮就此中断太亏；改名是原子的，撞上了等一下再试。"""
    LORE.mkdir(parents=True, exist_ok=True)
    path = LORE / f"{rec['id']}.json"
    text = json.dumps(rec, ensure_ascii=False, indent=1) + "\n"
    tmp = path.with_suffix(".json.tmp")
    for attempt in range(4):
        try:
            io.open(tmp, "w", encoding="utf-8", newline="\n").write(text)
            os.replace(tmp, path)
            return
        except OSError:
            if attempt == 3:
                raise
            time.sleep(0.4 * (attempt + 1))


def for_site(rec: dict) -> dict:
    """文章页那一栏要的那些字段。

    单篇的原件（data/post_lore/<id>.json）是完整的，导出给 App 的也是完整的；
    _data/post_lore.yml 只是网页端的读物，Jekyll 每次构建都要把它整份读进内存，
    所以这里只留页面画得出来的东西——每处提及的段号、写法列表、来源标记都不带。"""
    facets = rec.get("facets") or {}
    keep = {
        "id": rec["id"],
        "facets": {
            "pokemon": [{"name": k["name"], "ndex": k["ndex"]} for k in facets.get("pokemon", [])],
            "works": [{"name": w["name"], "slug": w.get("slug")} for w in facets.get("works", [])],
            "people": [{k: p[k] for k in ("name", "slug", "role", "kind") if p.get(k)} for p in facets.get("people", [])],
            "places": [{k: s[k] for k in ("name", "what", "world", "id", "entity") if s.get(k)} for s in facets.get("places", [])],
        },
        "observations": [{k: o[k] for k in ("text", "anchor", "seg") if k in o} for o in rec.get("observations") or []],
    }
    rels = [{k: r[k] for k in ("label", "title", "url", "why", "id", "kind") if r.get(k)} for r in rec.get("relations") or []]
    if rels:
        keep["relations"] = rels
    return keep


def published() -> set:
    """git 已经跟踪的那些帖子的 id。

    记录是照工作区里的 _posts 写的，里面可能有还没提交的帖子（并行的另一个会话正在加）。
    网页端的那一份只留连得上的关系——指向一篇还没进仓库的文章，部署出去就是死链。
    等那些帖子提交了，重跑一次 --collect 就会自动补回来。git 不可用时不过滤。"""
    try:
        out = subprocess.run(["git", "ls-files", "_posts"], cwd=ROOT, capture_output=True, text=True, check=True, encoding="utf-8")
    except Exception:                                                  # noqa: BLE001
        return set()
    ids = set()
    for line in out.stdout.splitlines():
        name = line.strip().rsplit("/", 1)[-1]
        if name.endswith(".md"):
            ids.add(xp.jekyll_title_slug(xp.DATE_PREFIX.sub("", name[:-3])))
    return ids


def collect(tables: dict) -> int:
    """把每篇的记录汇成 _data/post_lore.yml（按文件名 stem 索引，文章页直接查）"""
    out = {}
    live = published()
    dropped = 0
    for path in sorted(LORE.glob("*.json")):
        rec = json.load(io.open(path, encoding="utf-8"))
        if live:
            keep = [r for r in rec.get("relations") or [] if r.get("id") in live]
            dropped += len(rec.get("relations") or []) - len(keep)
            rec = {**rec, "relations": keep}
        out[rec["stem"]] = for_site(rec)
    if dropped:
        print(f"  {dropped} relations point at posts git does not track yet; left out of the site's copy")
    OUT_YML.parent.mkdir(parents=True, exist_ok=True)
    head = ("# 每篇文章的图鉴条目：提到的宝可梦 / 作品 / 地点 / 人（带段号），一两条带段号的观察，与别的文章的关系。\n"
            "# 由 tools/build-post-lore.py 生成（规则 + DeepSeek，data/post_lore/<id>.json 是单篇的原件，可手改）。\n"
            f"# 表：宝可梦写法 {tables['pokemon_names']['synced']} / 旅图地点 {tables['tour_places']['synced']}\n")
    io.open(OUT_YML, "w", encoding="utf-8", newline="\n").write(head + yaml.safe_dump(out, allow_unicode=True, sort_keys=True, width=1000))
    return len(out)


def pilot(posts: list, n: int) -> list:
    """各类文章都挑上：访谈、扫描、博客、站内长文，按年份铺开，取样固定（按 id 排序后等距取）"""
    groups = collections.OrderedDict()
    for p in posts:
        groups.setdefault(p["kind"], []).append(p)
    quota = {"interview": int(n * 0.6), "scan": max(2, int(n * 0.1)), "blog": max(2, int(n * 0.24)), "article": max(1, int(n * 0.06))}
    out = []
    for kind, rows in groups.items():
        want = quota.get(kind, 0)
        if want <= 0 or not rows:
            continue
        rows = sorted(rows, key=lambda p: (p["date"], p["id"]))
        step = max(1, len(rows) // want)
        out.extend(rows[::step][:want])
    return sorted(out, key=lambda p: (p["date"], p["id"]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--pilot", type=int, default=0)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--relations", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    #  只把已有的记录重新汇成 _data/post_lore.yml，不碰模型也不重跑规则
    ap.add_argument("--collect", action="store_true")
    #  概念这一轮：照 data/lore_tables/concepts.yml 逐段标注，不花钱、不碰别的字段
    ap.add_argument("--concepts", action="store_true")
    args = ap.parse_args()

    if args.collect:
        n = collect(load_tables())
        print(f"_data/post_lore.yml has {n} records")
        return 0

    if args.concepts:
        vocab = load_concepts()
        posts = load_posts()
        if args.limit:
            posts = posts[:args.limit]
        touched = annotate_concepts(posts, vocab, set(args.only))
        ev = json.load(io.open(EVIDENCE, encoding="utf-8"))["counts"]
        print(f"{len(vocab)} concepts in the table ({sum(1 for v in vocab if v['approved'])} reviewed), "
              f"{ev['matched']} of them match something; {touched} records written")
        print(f"  {ev['posts_with']} / {ev['posts']} posts carry at least one; unused: {len(ev['unused'])}")
        print(f"  → {EVIDENCE.relative_to(ROOT)}")
        return 0

    tables = load_tables()
    poke_cjk, poke_latin = pokemon_matcher(tables["pokemon_names"])
    place_re, place_index = place_matcher(tables["tour_places"])
    matchers = {"poke_cjk": poke_cjk, "poke_latin": poke_latin, "place": place_re, "place_index": place_index}
    people_by_name, kinds = people_index()
    works = works_index()

    posts = load_posts()
    by_id = {p["id"]: p for p in posts}
    if args.only:
        chosen = [by_id[i] for i in args.only if i in by_id]
        missing = [i for i in args.only if i not in by_id]
        if missing:
            print("  not found:", missing)
    elif args.pilot:
        chosen = pilot(posts, args.pilot)
    elif args.all:
        chosen = posts
    else:
        chosen = [p for p in posts if (LORE / f"{p['id']}.json").exists()]
        if not chosen:
            print("nothing chosen: pass --pilot N, --only <id>… or --all")
            return 2
    if args.limit:
        chosen = chosen[:args.limit]

    CACHE.mkdir(parents=True, exist_ok=True)
    lore_by_id = {p.stem: json.load(io.open(p, encoding="utf-8")) for p in LORE.glob("*.json")} if LORE.exists() else {}

    print(f"{len(chosen)} posts" + ("  (relations)" if args.relations else ""))
    asked = cached = skipped = failed = 0
    for i, post in enumerate(chosen, 1):
        rec = read_record(post["id"])
        if rec.get("edited"):
            print(f"  {i:>3}/{len(chosen)} {post['id'][:48]}  hand-edited, left alone")
            skipped += 1
            continue
        if args.relations:
            facets = (rec.get("facets") or {})
            if not facets:
                print(f"  {i:>3}/{len(chosen)} {post['id'][:48]}  no record yet, run without --relations first")
                skipped += 1
                continue
            cands = candidates(post, facets, posts, lore_by_id)
            if not cands:
                rec["relations"] = []
                write_record(rec)
                continue
            key = hashlib.sha1(("|".join(c["id"] for c in cands) + f"|{REV}").encode("utf-8")).hexdigest()[:16]
            cache = CACHE / f"{post['id']}.rel.json"
            got = None
            if cache.exists() and not args.force:
                blob = json.load(io.open(cache, encoding="utf-8"))
                if blob.get("key") == key:
                    # 缓存里的地址和标题是当时算的；那一篇后来改过分类、标题或换成重导版，
                    # 这里按现在的文章重算，否则关联会连到已经不存在的地址
                    got = [dict(r, url=site_path(by_id[r["id"]]), title=short_title(by_id[r["id"]])) if r.get("id") in by_id else r
                           for r in blob["relations"]]
                    cached += 1
            if got is None:
                try:
                    got = ask_relations(post, facets, cands, lore_by_id)
                    asked += 1
                    io.open(cache, "w", encoding="utf-8", newline="\n").write(json.dumps({"key": key, "relations": got}, ensure_ascii=False))
                    time.sleep(0.3)
                except Exception as exc:                                  # noqa: BLE001 - one bad post must not stop the run
                    print(f"  {i:>3}/{len(chosen)} {post['id'][:48]}  relations failed: {exc}")
                    failed += 1
                    continue
            rec["relations"] = got
            rec.setdefault("sources", {})["relations_model"] = "deepseek-chat"
            write_record(rec)
            lore_by_id[post["id"]] = rec
            print(f"  {i:>3}/{len(chosen)} {post['id'][:48]}  {len(got)} relations of {len(cands)} candidates")
            continue

        facets = rule_facets(post, tables, matchers, people_by_name, kinds, works)
        obs = rec.get("observations") or []
        model = None
        #  --no-llm 是「不花钱」，不是「不要模型写过的东西」：缓存里有就照用，
        #  否则重跑一遍规则会把之前模型认出来的地点、人名全抹掉
        key = lore_key(post)
        cache = CACHE / f"{post['id']}.json"
        if cache.exists() and not args.force:
            blob = json.load(io.open(cache, encoding="utf-8"))
            if blob.get("key") == key:
                model, cached = blob["answer"], cached + 1
        if not args.no_llm:
            if model is None:
                try:
                    model = ask_lore(post, facets)
                    asked += 1
                    io.open(cache, "w", encoding="utf-8", newline="\n").write(json.dumps({"key": key, "answer": model}, ensure_ascii=False))
                    time.sleep(0.3)
                except Exception as exc:                                  # noqa: BLE001
                    print(f"  {i:>3}/{len(chosen)} {post['id'][:48]}  model failed: {exc}")
                    failed += 1
        if model:
            obs = merge_model(facets, model, post, tables, matchers, people_by_name, kinds, works)
        out = {"id": post["id"], "stem": post["stem"], "rev": REV, "built": date.today().isoformat(),
               "kind": post["kind"], "body": {"kind": post["body_kind"], "n": len(post["segs"])},
               "facets": facets, "observations": obs, "relations": rec.get("relations") or [],
               "sources": {"pokemon_names": tables["pokemon_names"]["synced"], "tour_places": tables["tour_places"]["synced"],
                           "model": None if args.no_llm else "deepseek-chat"},
               "edited": False}
        write_record(out)
        lore_by_id[post["id"]] = out
        print(f"  {i:>3}/{len(chosen)} {post['id'][:48]}  "
              f"{len(facets['pokemon'])}宝 {len(facets['works'])}作 {len(facets['places'])}地 {len(facets['people'])}人 {len(obs)}观察")

    n = collect(tables)
    print(f"asked {asked}, cached {cached}, skipped {skipped}, failed {failed}; _data/post_lore.yml has {n} records")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
