#!/usr/bin/env python3
"""把站内的访谈、人物、作品、名单、关系、术语与专题归一化，导出给 PokeAmice App（v2）。

产物默认写到本仓库 `assets/data/app/`，随 GitHub Pages 一起发布，App 直接从
`https://docs.pokeamice.com/assets/data/app/` 读——不经过服务器，不需要部署。

读：_posts/*.md                          front matter + 正文（parallel_items / translation_segments / markdown）
    _data/people.yml                     人物库：名字、别名、分年肖像
    _data/credits_people.yml             人物 slug → 历作职务（build-credits-site.py 生成）
    _data/credits_games.yml              staff 名单收录的作品
    _data/credits/<slug>.yml             单作完整名单
    _data/works.yml                      作品图标与版本色
    _data/credits_relations.yml          作品关系（前作 / 复刻 / 并行 / 谱系）
    _data/credits_eras.yml               Experience cohort 分段
    design/glossary-site.json            术语表
    design/credits-analysis/*.md         专题分析

写：manifest.json          schema_version / docs_commit / generated_at / counts —— App 用 docs_commit 做缓存版本键
    index.json             1,062 篇的摘要（正文不在这里）
    posts/<id>.json        单篇：完整元数据 + 正文（segments 或 markdown）
    speakers/<slug>.json   某人在所有访谈里的发言段索引（「他说过的」）
    people.json            人物，按 slug
    works.json             作品，按站内名
    credits/<slug>.json    单作名单：解析过的团队 + 原始层级
    relations.json         作品关系；eras.json 时代分段
    glossary.json          术语表
    topics/index.json + topics/<slug>.json   专题长文

join 键（都核对过，别改）：
    people.yml[].slug           == credits_people.yml 的键                 616/616
    post.entities.people[]      == people.yml[].name 或 aliases[]          约 82% 命中
    post.entities.works[]       == works.yml[].name == credits_games[].work  约 76% 命中
    segment.speaker             == people.yml[].name / aliases（去掉括号注释后再试一次）

没命中的名字原样带出去（slug 为 null），不丢；App 显示成纯文字即可。

访谈页 URL：front matter 有 permalink 就用它；没有就按 _config 的 /:categories/:title/ 拼——
分类里的 ASCII 转小写、中文原样（百分号编码），:title 是文件名去掉日期与括号、保留大小写。
全部 1,062 篇对着线上核过。等 docs 站给了稳定短链，只改 canonical_url() 一处；记录里同时带 id。

用法：
    python tools/export-docs-archive.py                 # 写到 assets/data/app
    python tools/export-docs-archive.py --out <目录>
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://docs.pokeamice.com"
DEFAULT_OUT = ROOT / "assets" / "data" / "app"
SCHEMA_VERSION = 3

FRONT = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")
BRACKETS = re.compile(r"[\[\]\(\)（）【】]")
# 官方博客的 layout；和 build-people-profiles.py 的分类保持一致
BLOG_LAYOUTS = {"gamefreak-director", "gamefreak-legacy-blog", "gamefreak-lineblog"}
NAME_SPLIT = re.compile(r"\s*[、，,/／]\s*|\s+[×x]\s+")
# 发言人名后面的括号注释：「皮卡丘（记者）」「田尻智（社长）」
SPEAKER_NOTE = re.compile(r"\s*[（(][^（）()]*[）)]\s*$")
DETAILS_JA = re.compile(r"<details class=\"gf-director-language\">(.*?)</details>", re.S)
SUMMARY = re.compile(r"<summary>.*?</summary>\s*", re.S)
ASIDE = re.compile(r"<aside class=\"gf-director-translation-note\">.*?</aside>\s*", re.S)
ZH_HEADING = re.compile(r"^##\s*中文译文\s*$", re.M)

# 专题：design/credits-analysis 里适合当长文读的那几份（timeline / transitions 是工作表，不导）
TOPICS = [
    ("narrative-era-1", "narrative-era-1-1996-2009.md", "第一时代 1996–2009"),
    ("narrative-era-2", "narrative-era-2-2010-2017.md", "第二时代 2010–2017"),
    ("narrative-era-3", "narrative-era-3-2018-2026.md", "第三时代 2018–2026"),
    ("era-1", "era-1-1996-2009.md", "第一时代 · 数据"),
    ("era-2", "era-2-2010-2017.md", "第二时代 · 数据"),
    ("era-3", "era-3-2018-2026.md", "第三时代 · 数据"),
    ("atlas-summary", "atlas-summary.md", "版图总览"),
    ("synthesis", "synthesis.md", "综合"),
    ("domains", "domains.md", "领域"),
    ("absences", "absences.md", "缺席"),
]

# ---- v3：首页目录需要的字段，规则逐条照抄网页端（_includes/entry-card.html / catalogue-seed.html /
# cover-fallback.html / era-skin.html），App 才能画出和网页一样的卡片与年代模版。
INTERVIEW_LAYOUTS = {"interview-editorial", "parallel-translation"}
GF_BLOG_ARCHIVES = {"gamefreak_director_column", "gamefreak_masuda_lineblog", "gamefreak_legacy_blog"}
ERA_KEYS = {"1999", "2003", "2007", "2011", "2014", "2019", "2026"}
INLINE_IMG = re.compile(r"<img[^>]+src=\"([^\"]+)\"|!\[[^\]]*\]\(([^)\s]+)")
MD_STRIP = [
    (re.compile(r"<[^>]+>"), " "),
    (re.compile(r"!\[[^\]]*\]\([^)]*\)"), " "),
    (re.compile(r"\[([^\]]*)\]\([^)]*\)"), r"\1"),
    (re.compile(r"^[#>*\-\s|]+", re.M), ""),
    (re.compile(r"[`*_]{1,3}"), ""),
    (re.compile(r"\s+"), " "),
]
SEARCH_TEXT_CHARS = 1200
# 刊物 → 专题图（assets/img/topics/<tile>.jpg）；顺序就是网页端 cover-fallback 的判断顺序
TILE_RULES = [
    (("社長が訊く", "社长问"), "iwata"),
    (("Nintendo DREAM",), "ndream"),
    (("ファミ通", "Fami通"), "famitsu"),
    (("電撃", "电击"), "dengeki"),
    (("Game Informer",), "gi"),
    (("CEDEC",), "cedec"),
]
# 制作名单首页的「研究札记」：网页端写死在 _layouts/credits-index.html，这里同步一份给 App
CREDITS_NOTES = [
    "从 12 人到两个企划团队。红·绿的 Game Freak 本体只有 12 人、没有任何中层头衔；2002 红宝石·蓝宝石一次性建立 Art Director / Battle Director / Main Programmer 层；2016 太阳·月亮引入 Section Director 制；2022 起阿尔宙斯与朱·紫两支企划团队并行，共享 CG 技术部和宝可梦模型团队。",
    "一批人同时缺席、又同时回归，中间一定有另一部作品。2004 火红·叶绿与绿宝石是两支队伍；2014 缺席 ORAS 的 67 人正是太阳·月亮的领导核心；2016 缺席太阳·月亮的 85 人分成 Let's Go 组和剑·盾组——2017 年 GF 同时运转三条线。",
    "总监交接有迹可循。田尻智 → 増田順一（金·银 Sub Director → 水晶 Director）→ 大森滋（X·Y Planning Director → ORAS Director）→ 岩尾和昌（日月 Section Director → 究极日月 Director → 阿尔宙斯 Director）；每位新总监的第一部 Director 作品都是姊妹作。",
    "Z-A 继承阿尔宙斯线，Pokopia 接走了朱·紫线的一组人。零之秘宝（2023）完成后，朱·紫线的 Field Planning、3D 地图和游戏程序整组没有进 Z-A、Pokopia 或 Champions——约五十人同时消失，比个人离开更像是在做一部尚未公布的作品。",
    "「没上 Champions」不是离职信号。Champions 只有 339 条署名且多为 TPC / ILCA 方；判断去向要看 Z-A、Pokopia 与外传，名单页里每个人的最后一次署名都能点开核对。",
]


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def clean(value) -> str:
    return str(value).strip() if value not in (None, "") else ""


def abs_url(path) -> str:
    """站内相对路径 → 绝对地址。已经是 http(s) 的原样返回。图片现阶段直接热链 docs 站。"""
    s = clean(path)
    if not s:
        return ""
    if s.startswith(("http://", "https://")):
        return s
    return SITE + (s if s.startswith("/") else "/" + s)


def jekyll_title_slug(stem: str) -> str:
    """Jekyll 给 :title 的处理，按 _site 实际产物反推：去掉括号、保留大小写与连字符。"""
    return re.sub(r"-{2,}", "-", BRACKETS.sub("", stem)).strip("-")


def canonical_url(fm: dict, slug: str) -> str:
    explicit = clean(fm.get("permalink"))
    if explicit:
        return SITE + (explicit if explicit.startswith("/") else "/" + explicit)
    cats = [clean(c).lower() for c in as_list(fm.get("categories")) if clean(c)]
    return SITE + "/" + "/".join(urllib.parse.quote(c) for c in cats) + "/" + urllib.parse.quote(jekyll_title_slug(slug)) + "/"


def kind_of(fm: dict) -> str:
    cats = [clean(c) for c in as_list(fm.get("categories"))]
    if fm.get("layout") in BLOG_LAYOUTS or "官方博客" in cats:
        return "blog"
    if fm.get("translation_segments") or "扫描存档" in cats or "扫描翻译" in cats:
        return "scan"
    if clean(fm.get("archive_type")) == "article":
        return "article"
    return "interview"


def type_label(fm: dict, kind: str) -> str:
    """网页端目录的「内容类型」：扫描翻译 / 访谈翻译 / Game Freak 博客 / 文档 / 文章（catalogue-seed.html）。"""
    cats = [clean(c) for c in as_list(fm.get("categories"))]
    archive = clean(fm.get("archive_type") or fm.get("resource_type"))
    if archive == "scan_translation" or kind == "scan":
        return "扫描翻译"
    if fm.get("layout") in INTERVIEW_LAYOUTS or archive == "interview_translation" or "访谈翻译" in cats:
        return "访谈翻译"
    if archive in GF_BLOG_ARCHIVES or kind == "blog":
        return "Game Freak 博客"
    if "文档" in cats:
        return "文档"
    return "文章"


def card_kind(fm: dict, kind: str) -> str:
    """卡片封面的样式：扫描件带页边、杂志特辑同样；博客 / 访谈 / 文章各一种（entry-card.html）。"""
    if "杂志特辑" in [clean(c) for c in as_list(fm.get("categories"))]:
        return "feature"
    return {"scan": "scan", "blog": "blog", "article": "article"}.get(kind, "interview")


def era_skin(fm: dict, kind: str, year: int | None) -> str | None:
    """访谈 / 扫描件按年代套模版（era-skin.html）：front matter 写了合法的 era_skin 就用它，否则按年份。"""
    if kind not in ("interview", "scan"):
        return None
    explicit = clean(fm.get("era_skin"))
    if explicit in ERA_KEYS:
        return explicit
    if not year:
        return "2026"
    if 1980 < year <= 2001:
        return "1999"
    if year <= 2005:
        return "2003"
    if year <= 2009:
        return "2007"
    if year <= 2012:
        return "2011"
    if year <= 2016:
        return "2014"
    if year <= 2021:
        return "2019"
    return "2026"


def proof_label(fm: dict) -> str | None:
    wf = fm.get("workflow") if isinstance(fm.get("workflow"), dict) else {}
    v = clean(wf.get("proofreading"))
    if not v:
        return None
    if re.search(r"pending|machine|deepseek|draft", v):
        return "初译待校"
    if re.search(r"master|professional|manual|verified|done", v):
        return "已校对"
    return None


def first_inline_image(body_md: str) -> str:
    m = INLINE_IMG.search(body_md)
    return abs_url(m.group(1) or m.group(2)) if m else ""


def strip_markdown(text: str) -> str:
    for pattern, repl in MD_STRIP:
        text = pattern.sub(repl, text)
    return text.strip()


def portrait_for_entry(person: dict, slug: str, year: int | None) -> str:
    """网页端 person-avatar.html：为这篇拍的肖像优先，其次 5 年内最近的一张，最后主头像。"""
    src = person.get("avatar") or ""
    gap = 6
    for ph in person.get("portraits") or []:
        if ph.get("post") and ph["post"] in slug:
            return ph["image"] or src
        if ph.get("year") and year:
            d = abs(int(ph["year"]) - year)
            if d < gap:
                gap = d
                src = ph["image"] or src
    return src


def cover_fallback(fm: dict, kind: str, body_md: str, cover: str, people: list[dict], people_by_slug: dict, slug: str, year: int | None):
    """没有自己封面的条目借一张：博客用正文第一张图或栏目图，访谈按刊物用专题图，再不然用第一位受访者的肖像。
    返回 (cover, cover_kind, size)；cover_kind ∈ own / tile / portrait / ""。"""
    if cover:
        return cover, "own", None
    layout = clean(fm.get("layout"))
    tile = ""
    if kind == "blog" or layout in BLOG_LAYOUTS:
        inline = first_inline_image(body_md)
        if inline:
            return inline, "own", None
        tile = "director" if layout in ("gamefreak-director", "gamefreak-lineblog") else "art" if clean(fm.get("gf_legacy_blog")) == "art" else "staff"
    elif layout in INTERVIEW_LAYOUTS or kind == "interview":
        source = fm.get("source") if isinstance(fm.get("source"), dict) else {}
        pub = " ".join([clean(fm.get("publication")) or clean(source.get("publication")), clean(source.get("title")), clean(fm.get("title"))])
        tags = [clean(t) for t in as_list(fm.get("tags"))]
        cats = [clean(c) for c in as_list(fm.get("categories"))]
        if "首藤刚志手记" in cats:
            tile = "shudo"
        else:
            for needles, name in TILE_RULES:
                if any(n in pub for n in needles):
                    tile = name
                    break
            if not tile and "N.O.M" in tags:
                tile = "nom"
            if not tile and "招聘访谈" in tags:
                tile = "recruit"
            if not tile and (clean(fm.get("source_kind")) == "technical_report" or clean(fm.get("article_kind")) == "technical_feature"):
                tile = "tech"
        if not tile:
            for p in people:
                person = people_by_slug.get(p.get("slug") or "")
                if person and person.get("kind") not in ("character", "figure"):
                    src = portrait_for_entry(person, slug, year)
                    if src:
                        return src, "portrait", None
                break
    if tile:
        return f"{SITE}/assets/img/topics/{tile}.jpg", "tile", [336, 192]
    return "", "", None


def split_names(value) -> list[str]:
    s = clean(value)
    return [n for n in (x.strip() for x in NAME_SPLIT.split(s)) if n] if s else []


def git_head(path: Path) -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=path, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return ""


def dump(path: Path, obj) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    path.write_text(text, encoding="utf-8")
    return len(text.encode("utf-8"))


# ---------------------------------------------------------------- people

def build_people(people_raw: list, credits_people: dict, profiles: dict):
    by_slug: dict[str, dict] = {}
    name_to_slug: dict[str, str] = {}
    for p in people_raw:
        slug = clean(p.get("slug"))
        if not slug:
            continue
        cp = credits_people.get(slug)
        pf = profiles.get(slug)
        record = {
            "slug": slug,
            "name": clean(p.get("name")),
            "aliases": [clean(a) for a in as_list(p.get("aliases")) if clean(a)],
            "kind": clean(p.get("kind")) or None,
            "role": clean(p.get("role")) or None,
            "org": clean(p.get("org")) or None,
            "avatar": abs_url(p.get("avatar")) or None,
            "avatar_source": clean(p.get("avatar_source")) or None,
            "portraits": [
                {"image": abs_url(pt.get("image")), "year": pt.get("year"), "source": clean(pt.get("source")) or None, "post": clean(pt.get("post")) or None}
                for pt in as_list(p.get("portraits")) if isinstance(pt, dict) and pt.get("image")
            ],
            "credits": None,
            # 人物页的「开发专长」（tools/build-people-profiles.py）：专长 chips、署名一句话、摘要与出处
            "profile": None if not isinstance(pf, dict) else {
                "expertise": [clean(e) for e in as_list((pf.get("credits") or {}).get("expertise")) if clean(e)],
                "credits_line": clean((pf.get("credits") or {}).get("line")) or None,
                "categories": [{"cat": clean(c.get("cat")), "games": c.get("games") or 0} for c in as_list((pf.get("credits") or {}).get("categories")) if isinstance(c, dict)],
                "interviews": pf.get("interviews") if isinstance(pf.get("interviews"), dict) else None,
                "summary": clean(pf.get("summary")) or None,
                "citations": [
                    {"n": c.get("n"), "post": jekyll_title_slug(DATE_PREFIX.sub("", clean(c.get("post")))), "title": clean(c.get("title")) or None,
                     "date": clean(c.get("date")) or None, "publication": clean(c.get("publication")) or None, "detail": clean(c.get("detail")) or None}
                    for c in as_list(pf.get("citations")) if isinstance(c, dict)
                ],
            },
            "interview_count": 0,
            "mention_count": 0,
            "spoken_segments": 0,
        }
        if cp:
            record["credits"] = {
                "name_en": clean(cp.get("name")),
                "kanji": clean(cp.get("kanji")) or None,
                "kana": clean(cp.get("kana")) or None,
                "games": cp.get("games") or 0,
                "core_games": cp.get("core_games") or 0,
                "first": cp.get("first"),
                "last": cp.get("last"),
                "latest_role": clean(cp.get("latest_role")) or None,
                "latest_game": clean(cp.get("latest_game")) or None,
                "roles": [
                    {"game": clean(c.get("game")), "year": c.get("year"), "role": clean(c.get("role")), "role_ja": clean(c.get("role_ja")) or None, "role_zh": clean(c.get("role_zh")) or None}
                    for c in as_list(cp.get("credits")) if isinstance(c, dict)
                ],
            }
        by_slug[slug] = record
        for alias in [record["name"], *record["aliases"]]:
            name_to_slug.setdefault(alias, slug)
        if record["credits"]:
            for alias in (record["credits"]["name_en"], record["credits"]["kanji"]):
                if alias:
                    name_to_slug.setdefault(alias, slug)
    return by_slug, name_to_slug


def resolve_person(name: str, name_to_slug: dict) -> str | None:
    s = clean(name)
    if not s:
        return None
    if s in name_to_slug:
        return name_to_slug[s]
    # 「皮卡丘（记者）」→「皮卡丘」；「田尻 智」→「田尻智」
    base = SPEAKER_NOTE.sub("", s).replace(" ", "")
    return name_to_slug.get(base) or name_to_slug.get(SPEAKER_NOTE.sub("", s))


# ---------------------------------------------------------------- works

def build_works(works_raw: list, games_raw: list):
    games_by_work = {clean(g.get("work")): g for g in games_raw if clean(g.get("work"))}
    by_name: dict[str, dict] = {}
    for w in works_raw:
        if not isinstance(w, dict) or not clean(w.get("name")):
            continue
        name = clean(w["name"])
        g = games_by_work.get(name)
        by_name[name] = {
            "name": name,
            "credits_slug": clean(g.get("slug")) if g else None,
            "title": clean(g.get("title")) if g else None,
            "title_zh": clean(g.get("title_zh")) if g else None,
            "year": g.get("year") if g else None,
            "developer": clean(g.get("developer")) if g else None,
            "core": bool(g.get("core")) if g else None,
            "staff_count": g.get("count") if g else None,
            "gf_count": g.get("gf_count") if g else None,
            "note": clean(g.get("note")) if g else None,
            "color": clean(w.get("color")) or None,
            "color2": clean(w.get("color2")) or None,
            "icon": abs_url(w.get("icon")) or (abs_url(g.get("icon")) if g else "") or None,
            "icon2": abs_url(w.get("icon2")) or (abs_url(g.get("icon2")) if g else "") or None,
            "mascot": abs_url(w.get("mascot")) or None,
            "interview_count": 0,
        }
    for g in games_raw:
        name = clean(g.get("work")) or clean(g.get("title_zh")) or clean(g.get("title"))
        if name and name not in by_name:
            # 名单页可以借另一部作品的图标（area-zero 借朱·紫的）
            borrowed = by_name.get(clean(g.get("icon_work")), {})
            by_name[name] = {
                "name": name, "credits_slug": clean(g.get("slug")), "title": clean(g.get("title")) or None,
                "title_zh": clean(g.get("title_zh")) or None, "year": g.get("year"), "developer": clean(g.get("developer")) or None,
                "core": bool(g.get("core")), "staff_count": g.get("count"), "gf_count": g.get("gf_count"), "note": clean(g.get("note")) or None,
                "color": borrowed.get("color"), "color2": borrowed.get("color2"),
                "icon": abs_url(g.get("icon")) or borrowed.get("icon"), "icon2": abs_url(g.get("icon2")) or borrowed.get("icon2"),
                "mascot": borrowed.get("mascot"), "interview_count": 0,
            }
    return by_name


# ---------------------------------------------------------------- bodies

SEGMENT_TYPES = {"heading": "heading", "header": "heading", "paragraph": "paragraph", "text": "paragraph", "narrative": "paragraph", "dialogue": "dialogue", "image": "image"}


def normalize_parallel(items: list, name_to_slug: dict) -> list[dict]:
    """访谈的 parallel_items → 统一的 segments。"""
    out = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        speaker = clean(raw.get("speaker"))
        kind = SEGMENT_TYPES.get(clean(raw.get("type")))
        if not kind:
            kind = "dialogue" if speaker else "paragraph"
        seg = {"n": len(out), "type": kind}
        if kind == "heading":
            seg["level"] = int(raw.get("level") or 2)
        if speaker:
            seg["speaker"] = speaker
            slug = resolve_person(speaker, name_to_slug)
            if slug:
                seg["speaker_slug"] = slug
            orig = clean(raw.get("speaker_orig") or raw.get("speaker_ja"))
            if orig:
                seg["speaker_orig"] = orig
        for key in ("role", "note", "caption", "alt"):
            if clean(raw.get(key)):
                seg[key] = clean(raw.get(key))
        image = abs_url(raw.get("image") or raw.get("src"))
        if image:
            seg["image"] = image
        if clean(raw.get("original")):
            seg["original"] = clean(raw.get("original"))
        if clean(raw.get("translation")):
            seg["translation"] = clean(raw.get("translation"))
        if kind == "image" and not image:
            continue  # 没图的图片段没有意义
        if kind != "image" and not seg.get("original") and not seg.get("translation"):
            continue  # 空段落
        out.append(seg)
    return out


def normalize_scan(items: list, name_to_slug: dict) -> list[dict]:
    """扫描件的 translation_segments → 统一的 segments，保留页号与区域 id 给页图高亮用。"""
    out = []
    for raw in sorted((it for it in items if isinstance(it, dict)), key=lambda it: (it.get("scan_page") or 0, it.get("order") or 0)):
        t = clean(raw.get("type"))
        kind = "image" if t == "image" else "heading" if t == "heading" else "paragraph"
        speaker = clean(raw.get("speaker"))
        if speaker in ("image", "body", "caption", "note", "heading"):
            speaker = ""
        if speaker and kind == "paragraph":
            kind = "dialogue"
        seg = {"n": len(out), "type": kind}
        if kind == "heading":
            seg["level"] = int(raw.get("heading_level") or 2)
        if speaker:
            seg["speaker"] = speaker
            slug = resolve_person(speaker, name_to_slug)
            if slug:
                seg["speaker_slug"] = slug
        if raw.get("scan_page") is not None:
            seg["scan_page"] = raw.get("scan_page")
        if clean(raw.get("region_id")):
            seg["region_id"] = clean(raw.get("region_id"))
        image = abs_url(raw.get("image"))
        if image:
            seg["image"] = image
        if clean(raw.get("alt")):
            seg["alt"] = clean(raw.get("alt"))
        if clean(raw.get("original")):
            seg["original"] = clean(raw.get("original"))
        if clean(raw.get("translation")):
            seg["translation"] = clean(raw.get("translation"))
        if kind == "image" and not image:
            continue
        if kind != "image" and not seg.get("original") and not seg.get("translation"):
            continue
        out.append(seg)
    return out


def split_blog(body: str) -> dict:
    """官方博客正文：中文译文与折叠的日文原文拆开。三种来源的结构：
    lineblog：中文 … <details class="gf-director-language"><summary>…</summary> 日文 </details>
    部长专栏：<aside 校对说明/> ## 中文译文 … <details …> 日文 </details>
    旧博客：只有中文，没有结构。"""
    text = ASIDE.sub("", body)
    ja = None
    m = DETAILS_JA.search(text)
    if m:
        ja = SUMMARY.sub("", m.group(1)).strip() or None
        text = text[: m.start()] + text[m.end():]
    zh = ZH_HEADING.sub("", text).strip()
    return {"kind": "markdown", "markdown_zh": zh, "markdown_ja": ja}


# ---------------------------------------------------------------- posts

def build_posts(people_by_slug: dict, people_by_name: dict, works_by_name: dict, covers: dict, out: Path):
    index = []
    speakers: dict[str, list] = collections.defaultdict(list)
    search_text: dict[str, str] = {}
    (out / "posts").mkdir(parents=True, exist_ok=True)
    sizes = []
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
        slug = jekyll_title_slug(DATE_PREFIX.sub("", f.stem))
        body_md = text[m.end():]
        kind = kind_of(fm)
        source = fm.get("source") if isinstance(fm.get("source"), dict) else {}
        ent = fm.get("entities") if isinstance(fm.get("entities"), dict) else {}
        people = [{"name": clean(n), "slug": people_by_name.get(clean(n)) or resolve_person(n, people_by_name)} for n in as_list(ent.get("people")) if clean(n)]
        works = [{"name": clean(n), "slug": works_by_name.get(clean(n), {}).get("credits_slug")} for n in as_list(ent.get("works")) if clean(n)]
        date = clean(fm.get("date"))[:10] or f.stem[:10]

        if fm.get("parallel_items"):
            body = {"kind": "segments", "segments": normalize_parallel(as_list(fm.get("parallel_items")), people_by_name)}
        elif fm.get("translation_segments"):
            body = {"kind": "segments", "segments": normalize_scan(as_list(fm.get("translation_segments")), people_by_name)}
        else:
            body = split_blog(body_md)

        segments = body.get("segments") or []
        year = int(date[:4]) if date[:4].isdigit() else None
        first_work = works[0] if works else None
        for seg in segments:
            if seg.get("speaker_slug"):
                speakers[seg["speaker_slug"]].append({"post": slug, "n": seg["n"], "year": year, **({"work": first_work["name"]} if first_work else {})})

        # 封面：自己的图（front matter image / 扫描件第一页 / 访谈第一张图），没有就按网页规则借一张
        own = abs_url(fm.get("image") or fm.get("featured_image")) or next((s["image"] for s in segments if s.get("image")), "")
        cover, cover_kind, size = cover_fallback(fm, kind, body_md, own, people, people_by_slug, slug, year)
        if cover and size is None:
            size = covers.get(cover.replace(SITE, "", 1))
        mentions = fm.get("mentions") if isinstance(fm.get("mentions"), dict) else {}
        mention_slugs = []
        for n in as_list(mentions.get("people")):
            s = people_by_name.get(clean(n)) or resolve_person(n, people_by_name)
            if s and s not in mention_slugs:
                mention_slugs.append(s)
        excerpt = strip_markdown(clean(fm.get("gf_translation_summary") or fm.get("summary") or fm.get("description") or fm.get("dek")))[:180] or None

        summary_item = {
            "id": slug,
            "kind": kind,
            "type": type_label(fm, kind),
            "card": card_kind(fm, kind),
            "title": clean(fm.get("title")) or slug,
            "display_title": clean(fm.get("display_title")) or None,
            "dek": clean(fm.get("dek")) or None,
            "excerpt": excerpt,
            "date": date,
            "publication": clean(fm.get("publication")) or clean(source.get("title")) or None,
            "source": clean(source.get("title")) or clean(fm.get("publication")) or clean(source.get("publication")) or None,
            "issue": clean(fm.get("issue")) or None,
            "interviewee": split_names(fm.get("interviewee")),
            "people": people,
            "mentions": mention_slugs,
            "works": works,
            "tags": [clean(t) for t in as_list(fm.get("tags")) if clean(t)],
            "categories": [clean(c) for c in as_list(fm.get("categories")) if clean(c)],
            "topics": [clean(t) for t in as_list(fm.get("topics")) if clean(t)],
            "era": era_skin(fm, kind, year),
            "url": canonical_url(fm, slug),
            "body_kind": body["kind"],
            "segment_count": len(segments) if segments else None,
            "pages": sum(1 for s in segments if s.get("type") == "image") if kind == "scan" else 0,
            "proof": proof_label(fm),
            "cover": cover or None,
            "cover_kind": cover_kind,
            "size": size,
        }
        index.append(summary_item)
        # 全文检索用的正文（译文优先），单独一个文件，App 第一次搜正文时才拉
        if segments:
            text = " ".join(s.get("translation") or s.get("original") or "" for s in segments)
        else:
            text = body.get("markdown_zh") or ""
        text = re.sub(r"\s+", " ", strip_markdown(text)).strip()
        if text:
            search_text[slug] = text[:SEARCH_TEXT_CHARS]

        post = {
            **summary_item,
            "archive_type": clean(fm.get("archive_type")) or None,
            "summary": clean(fm.get("summary") or fm.get("description")) or None,
            "interviewer": clean(fm.get("interviewer")) or None,
            "translator": clean(fm.get("translator")) or None,
            "tags": [clean(t) for t in as_list(fm.get("tags")) if clean(t)],
            "original_lang": clean(fm.get("original_lang")) or None,
            "translation_status": clean(fm.get("translation_status")) or None,
            "source": {
                "title": clean(source.get("title")) or None,
                "url": clean(source.get("url") or fm.get("original_link")) or None,
                "archive_url": clean(source.get("archive_url")) or None,
                "type": clean(source.get("source_type") or fm.get("source_kind")) or None,
            },
            "body": body,
        }
        sizes.append(dump(out / "posts" / f"{slug}.json", post))

    index.sort(key=lambda x: (x["date"], x["id"]), reverse=True)
    return index, speakers, sizes, search_text


# ---------------------------------------------------------------- credits

def build_credits(games_raw: list, credits_people: dict, out: Path) -> int:
    team_by_game: dict[str, list] = collections.defaultdict(list)
    slug_by_en: dict[str, str] = {}
    for slug, cp in credits_people.items():
        slug_by_en.setdefault(clean(cp.get("name")), slug)
        for c in as_list(cp.get("credits")):
            if isinstance(c, dict) and clean(c.get("game")):
                team_by_game[clean(c["game"])].append({
                    "slug": slug, "name": clean(cp.get("name")), "kanji": clean(cp.get("kanji")) or None,
                    "role": clean(c.get("role")), "role_ja": clean(c.get("role_ja")) or None, "role_zh": clean(c.get("role_zh")) or None,
                })
    written = 0
    for g in games_raw:
        slug = clean(g.get("slug"))
        src = ROOT / "_data" / "credits" / f"{slug}.yml"
        if not slug or not src.exists():
            continue
        d = load_yaml(src)
        roll = []
        for s in as_list(d.get("sections")):
            if not isinstance(s, dict):
                continue
            roll.append({
                "path": [clean(p) for p in as_list(s.get("path"))],
                "role_ja": clean(s.get("ja_role")) or None,
                "names": [
                    {
                        "name": clean(n.get("name")), "ja": clean(n.get("ja")) or None, "kanji": clean(n.get("kanji")) or None,
                        "slug": slug_by_en.get(clean(n.get("name"))),
                        **({"lead": True} if n.get("lead") else {}),
                        **({"kind": clean(n.get("kind"))} if clean(n.get("kind")) else {}),
                    }
                    for n in as_list(s.get("names")) if isinstance(n, dict) and clean(n.get("name"))
                ],
            })
        dump(out / "credits" / f"{slug}.json", {
            "slug": slug, "work": clean(g.get("work")) or None, "title": clean(g.get("title")) or None,
            "title_zh": clean(g.get("title_zh")) or None, "year": g.get("year"), "developer": clean(g.get("developer")) or None,
            "core": bool(g.get("core")), "count": g.get("count"), "source": clean(g.get("source")) or None,
            "source_ja": clean(g.get("source_ja")) or None,
            "team": sorted(team_by_game.get(slug, []), key=lambda t: t["name"]),
            "roll": roll,
        })
        written += 1
    return written


def build_credits_index(games_raw: list, works: dict, out: Path) -> int:
    """制作名单首页：核心作 / 外传两组，带图标与 Game Freak 成员数，加研究札记。"""
    by_slug = {w["credits_slug"]: w for w in works.values() if w.get("credits_slug")}
    games = []
    for g in games_raw:
        slug = clean(g.get("slug"))
        if not slug:
            continue
        w = by_slug.get(slug, {})
        games.append({
            "slug": slug, "work": clean(g.get("work")) or None, "title": clean(g.get("title")) or None, "title_zh": clean(g.get("title_zh")) or None,
            "year": g.get("year"), "developer": clean(g.get("developer")) or None, "core": bool(g.get("core")), "count": g.get("count") or 0,
            "gf_count": g.get("gf_count"), "note": clean(g.get("note")) or None,
            "icon": w.get("icon") or abs_url(g.get("icon")) or None, "icon2": w.get("icon2") or None, "color": w.get("color"), "color2": w.get("color2"),
            "has_atlas": (ROOT / "assets" / "data" / "credits-profile" / f"{slug}.json").exists(),
        })
    dump(out / "credits" / "index.json", {"games": games, "total": sum(x["count"] for x in games), "notes": CREDITS_NOTES})
    return len(games)


def build_atlas(out: Path) -> int:
    """团队画像（tools/build-atlas.py 的 credits-profile/<slug>.json）原样带过去，再补上 credits-relations 里这一作的数字关系。"""
    src_dir = ROOT / "assets" / "data" / "credits-profile"
    rel_path = ROOT / "assets" / "data" / "credits-relations.json"
    relations = json.loads(rel_path.read_text(encoding="utf-8")) if rel_path.exists() else []
    (out / "atlas").mkdir(parents=True, exist_ok=True)
    written = 0
    for f in sorted(src_dir.glob("*.json")) if src_dir.exists() else []:
        profile = json.loads(f.read_text(encoding="utf-8"))
        slug = clean(profile.get("slug")) or f.stem
        stats = []
        for r in relations:
            if not isinstance(r, dict) or slug not in (r.get("source"), r.get("target")):
                continue
            other = r["b"] if r.get("source") == slug else r["a"]
            stats.append({
                "other": other.get("slug"), "title": other.get("title"), "year": other.get("year"), "type": r.get("type"), "status": r.get("status"),
                "direction": "next" if r.get("source") == slug else "prev", "shared": r.get("shared"), "retention": r.get("retention"),
                "inheritance": r.get("inheritance"), "jaccard": r.get("jaccard"), "note": r.get("note"),
            })
        profile["relation_stats"] = stats
        dump(out / "atlas" / f"{slug}.json", profile)
        written += 1
    return written


def build_staff(out: Path) -> int:
    """历作 staff 总表（credits-staff.json）：3,600 人 × 29 作的矩阵，图标改成绝对地址。"""
    src = ROOT / "assets" / "data" / "credits-staff.json"
    if not src.exists():
        return 0
    data = json.loads(src.read_text(encoding="utf-8"))
    for g in data.get("games", []):
        if g.get("icon"):
            g["icon"] = abs_url(g["icon"])
    for p in data.get("people", []):
        if p.get("a"):
            p["a"] = abs_url(p["a"])
    dump(out / "credits" / "staff.json", data)
    return len(data.get("people", []))


# ---------------------------------------------------------------- topics

def build_topics(people: dict, works: dict, out: Path) -> list[dict]:
    listing = []
    names_people = sorted(((p["name"], p["slug"]) for p in people.values() if len(p["name"]) >= 2), key=lambda x: -len(x[0]))
    names_works = sorted(((w["name"], w["credits_slug"]) for w in works.values()), key=lambda x: -len(x[0]))
    for slug, filename, title in TOPICS:
        src = ROOT / "design" / "credits-analysis" / filename
        if not src.exists():
            continue
        md = src.read_text(encoding="utf-8")
        h1 = re.search(r"^#\s+(.+)$", md, re.M)
        mentioned_people = [{"name": n, "slug": s} for n, s in names_people if n in md][:60]
        mentioned_works = [{"name": n, "slug": s} for n, s in names_works if n in md][:60]
        size = dump(out / "topics" / f"{slug}.json", {
            "slug": slug, "title": title, "heading": h1.group(1).strip() if h1 else title,
            "source_path": f"design/credits-analysis/{filename}", "markdown": md,
            "people": mentioned_people, "works": mentioned_works,
        })
        listing.append({"slug": slug, "title": title, "bytes": size, "people": len(mentioned_people), "works": len(mentioned_works)})
    dump(out / "topics" / "index.json", {"items": listing})
    return listing


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)

    people_raw = load_yaml(ROOT / "_data" / "people.yml")
    credits_people = load_yaml(ROOT / "_data" / "credits_people.yml")
    games_raw = load_yaml(ROOT / "_data" / "credits_games.yml")
    works_raw = load_yaml(ROOT / "_data" / "works.yml")
    relations_raw = load_yaml(ROOT / "_data" / "credits_relations.yml")
    eras_raw = load_yaml(ROOT / "_data" / "credits_eras.yml")
    glossary_raw = json.loads((ROOT / "design" / "glossary-site.json").read_text(encoding="utf-8"))
    profiles_raw = load_yaml(ROOT / "_data" / "people_profiles.yml") if (ROOT / "_data" / "people_profiles.yml").exists() else []
    profiles = {clean(p.get("slug")): p for p in profiles_raw if isinstance(p, dict) and clean(p.get("slug"))}
    covers = load_yaml(ROOT / "_data" / "covers.yml") if (ROOT / "_data" / "covers.yml").exists() else {}

    people, people_by_name = build_people(people_raw, credits_people, profiles)
    works = build_works(works_raw, games_raw)
    index, speakers, post_sizes, search_text = build_posts(people, people_by_name, works, covers, out)

    for it in index:
        for p in it["people"]:
            if p["slug"] in people:
                people[p["slug"]]["interview_count"] += 1
        for s in it["mentions"]:
            if s in people:
                people[s]["mention_count"] += 1
        for w in it["works"]:
            if w["name"] in works:
                works[w["name"]]["interview_count"] += 1
    for slug, items in speakers.items():
        if slug in people:
            people[slug]["spoken_segments"] = len(items)
        dump(out / "speakers" / f"{slug}.json", {"slug": slug, "name": people.get(slug, {}).get("name") or slug, "items": items})

    credits_written = build_credits(games_raw, credits_people, out)
    credits_indexed = build_credits_index(games_raw, works, out)
    atlas_written = build_atlas(out)
    staff_rows = build_staff(out)
    topics = build_topics(people, works, out)

    dump(out / "index.json", {"items": index})
    search_bytes = dump(out / "search.json", {"items": search_text})
    dump(out / "people.json", {"items": list(people.values())})
    dump(out / "works.json", {"items": list(works.values())})
    dump(out / "relations.json", {"items": [
        {"source": clean(r.get("source")), "target": clean(r.get("target")), "type": clean(r.get("type")), "status": clean(r.get("status")),
         **({"note": clean(r.get("note"))} if clean(r.get("note")) else {}),
         **({"evidence": [clean(e) for e in as_list(r.get("evidence"))]} if r.get("evidence") else {})}
        for r in relations_raw if isinstance(r, dict)
    ]})
    dump(out / "eras.json", {"items": [e for e in eras_raw if isinstance(e, dict)]})
    dump(out / "glossary.json", {"items": [
        {"category": clean(e.get("category")) or None, "target": clean(e.get("target")), "terms": [clean(t) for t in as_list(e.get("terms")) if clean(t)],
         "variants": [clean(t) for t in as_list(e.get("variants")) if clean(t)], "note": clean(e.get("note")) or None}
        for e in (glossary_raw.get("entries") if isinstance(glossary_raw, dict) else glossary_raw) if isinstance(e, dict) and clean(e.get("target"))
    ]})

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "docs_commit": git_head(ROOT),
        "site": SITE,
        "base": f"{SITE}/assets/data/app",
        "counts": {
            "posts": len(index),
            "by_kind": dict(collections.Counter(it["kind"] for it in index)),
            "by_body": dict(collections.Counter(it["body_kind"] for it in index)),
            "segments": sum(it["segment_count"] or 0 for it in index),
            "people": len(people),
            "people_with_credits": sum(1 for p in people.values() if p["credits"]),
            "speakers": len(speakers),
            "works": len(works),
            "credits_games": credits_written,
            "credits_indexed": credits_indexed,
            "atlas": atlas_written,
            "staff_rows": staff_rows,
            "search_bytes": search_bytes,
            "covers": dict(collections.Counter(it["cover_kind"] or "none" for it in index)),
            "eras": dict(collections.Counter(it["era"] or "none" for it in index)),
            "relations": len(relations_raw),
            "glossary": len(glossary_raw.get("entries", []) if isinstance(glossary_raw, dict) else glossary_raw),
            "topics": len(topics),
            "unresolved_people_mentions": sum(1 for it in index for p in it["people"] if not p["slug"]),
            "duplicate_ids": len(index) - len({it["id"] for it in index}),
            "posts_bytes": sum(post_sizes),
        },
    }
    dump(out / "manifest.json", manifest)

    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=1))
    print("→", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
