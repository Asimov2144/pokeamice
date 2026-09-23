#!/usr/bin/env python3
"""What each article is about, in a form the App's dex machine can act on.

    python tools/build-post-lore.py --pilot 50        # the pilot set: 50 entries across the kinds
    python tools/build-post-lore.py --only interview-wedge-ishihara-pokemon-disney
    python tools/build-post-lore.py --all             # every post
    python tools/build-post-lore.py --no-llm          # the rule pass only (free, no model)
    python tools/build-post-lore.py --relations       # stage two: the links between articles
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
import re
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
        rec = {"id": p["id"], "entity": p.get("entity"), "category": p.get("category")}
        for spelling in [p["name"], *p.get("aliases", [])]:
            reg(spelling, rec)
    for p in table["places"]:
        if not p.get("entity"):
            continue
        plain = BRACKET.sub("", p["name"]).strip()
        rec = {"id": None, "entity": p["entity"], "category": p.get("category")}
        reg(plain, rec)
        reg(re.sub(r"\s", "", plain), rec)
    keys = sorted(index, key=len, reverse=True)
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
    for spelling, spots in hits(matchers["place"], segs).items():
        p = matchers["place_index"][spelling]
        place_out.append({"name": spelling, "id": p["id"], "entity": p.get("entity"), "category": p.get("category"),
                          "world": "real", "seg": spots, "via": "gazetteer"})
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
    raw = nom.deepseek([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], max_tokens=1800)
    got = json.loads(raw)
    if not isinstance(got, dict):
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
        p = matchers["place_index"].get(name) or matchers["place_index"].get(re.sub(r"\s", "", name))
        world = "game" if str(row.get("world") or "").strip() == "game" else "real"
        facets["places"].append({"name": name, "id": p["id"] if p else None, "entity": (p or {}).get("entity"),
                                 "category": (p or {}).get("category"), "world": world, "seg": seg_of(row),
                                 "what": str(row.get("what") or "").strip() or None, "via": "llm"})
    # 榜单一类的文章会点出二十个地名；留下对得上旅图的、写了段号的，最多十个
    facets["places"].sort(key=lambda p: (0 if (p.get("id") or p.get("entity")) else 1, 0 if p.get("seg") else 1))
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
        anchor = post["anchors"][n] if n < len(post.get("anchors") or []) else None
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
    raw = nom.deepseek([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], max_tokens=700)
    got = json.loads(raw)
    out = []
    for row in (got.get("relations") or []) if isinstance(got, dict) else []:
        i, kind = row.get("i"), str(row.get("kind") or "").strip()
        if not isinstance(i, int) or not 1 <= i <= len(cands) or kind not in KINDS:
            continue
        out.append({"id": cands[i - 1]["id"], "kind": kind, "label": KINDS[kind],
                    "why": str(row.get("why") or "").strip()[:40]})
    return out[:4]


# ---------------------------------------------------------------- files


def read_record(post_id: str) -> dict:
    path = LORE / f"{post_id}.json"
    return json.load(io.open(path, encoding="utf-8")) if path.exists() else {}


def write_record(rec: dict) -> None:
    LORE.mkdir(parents=True, exist_ok=True)
    path = LORE / f"{rec['id']}.json"
    io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(rec, ensure_ascii=False, indent=1) + "\n")


def collect(tables: dict) -> int:
    """把每篇的记录汇成 _data/post_lore.yml（按文件名 stem 索引，文章页直接查）"""
    out = {}
    for path in sorted(LORE.glob("*.json")):
        rec = json.load(io.open(path, encoding="utf-8"))
        out[rec["stem"]] = {k: rec[k] for k in ("id", "facets", "observations", "relations", "sources") if k in rec}
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
    args = ap.parse_args()

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
                    got, cached = blob["relations"], cached + 1
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
        if not args.no_llm:
            key = lore_key(post)
            cache = CACHE / f"{post['id']}.json"
            if cache.exists() and not args.force:
                blob = json.load(io.open(cache, encoding="utf-8"))
                if blob.get("key") == key:
                    model, cached = blob["answer"], cached + 1
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
