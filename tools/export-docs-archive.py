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
SCHEMA_VERSION = 2

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

def build_people(people_raw: list, credits_people: dict):
    by_slug: dict[str, dict] = {}
    name_to_slug: dict[str, str] = {}
    for p in people_raw:
        slug = clean(p.get("slug"))
        if not slug:
            continue
        cp = credits_people.get(slug)
        record = {
            "slug": slug,
            "name": clean(p.get("name")),
            "aliases": [clean(a) for a in as_list(p.get("aliases")) if clean(a)],
            "kind": clean(p.get("kind")) or None,
            "avatar": abs_url(p.get("avatar")) or None,
            "avatar_source": clean(p.get("avatar_source")) or None,
            "portraits": [
                {"image": abs_url(pt.get("image")), "year": pt.get("year"), "source": clean(pt.get("source")) or None, "post": clean(pt.get("post")) or None}
                for pt in as_list(p.get("portraits")) if isinstance(pt, dict) and pt.get("image")
            ],
            "credits": None,
            "interview_count": 0,
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
            "color": clean(w.get("color")) or None,
            "color2": clean(w.get("color2")) or None,
            "icon": abs_url(w.get("icon")) or None,
            "icon2": abs_url(w.get("icon2")) or None,
            "mascot": abs_url(w.get("mascot")) or None,
            "interview_count": 0,
        }
    for g in games_raw:
        name = clean(g.get("work")) or clean(g.get("title_zh")) or clean(g.get("title"))
        if name and name not in by_name:
            by_name[name] = {
                "name": name, "credits_slug": clean(g.get("slug")), "title": clean(g.get("title")) or None,
                "title_zh": clean(g.get("title_zh")) or None, "year": g.get("year"), "developer": clean(g.get("developer")) or None,
                "core": bool(g.get("core")), "staff_count": g.get("count"), "color": None, "color2": None,
                "icon": None, "icon2": None, "mascot": None, "interview_count": 0,
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

def build_posts(people_by_name: dict, works_by_name: dict, out: Path):
    index = []
    speakers: dict[str, list] = collections.defaultdict(list)
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
        cover = next((s["image"] for s in segments if s.get("image")), None)
        year = int(date[:4]) if date[:4].isdigit() else None
        first_work = works[0] if works else None
        for seg in segments:
            if seg.get("speaker_slug"):
                speakers[seg["speaker_slug"]].append({"post": slug, "n": seg["n"], "year": year, **({"work": first_work["name"]} if first_work else {})})

        summary_item = {
            "id": slug,
            "kind": kind,
            "title": clean(fm.get("title")) or slug,
            "display_title": clean(fm.get("display_title")) or None,
            "dek": clean(fm.get("dek")) or None,
            "date": date,
            "publication": clean(fm.get("publication")) or clean(source.get("title")) or None,
            "issue": clean(fm.get("issue")) or None,
            "interviewee": split_names(fm.get("interviewee")),
            "people": people,
            "works": works,
            "era": clean(fm.get("era_skin")) or None,
            "url": canonical_url(fm, slug),
            "body_kind": body["kind"],
            "segment_count": len(segments) if segments else None,
            "cover": cover,
        }
        index.append(summary_item)

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
    return index, speakers, sizes


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

    people, people_by_name = build_people(people_raw, credits_people)
    works = build_works(works_raw, games_raw)
    index, speakers, post_sizes = build_posts(people_by_name, works, out)

    for it in index:
        for p in it["people"]:
            if p["slug"] in people:
                people[p["slug"]]["interview_count"] += 1
        for w in it["works"]:
            if w["name"] in works:
                works[w["name"]]["interview_count"] += 1
    for slug, items in speakers.items():
        if slug in people:
            people[slug]["spoken_segments"] = len(items)
        dump(out / "speakers" / f"{slug}.json", {"slug": slug, "name": people.get(slug, {}).get("name") or slug, "items": items})

    credits_written = build_credits(games_raw, credits_people, out)
    topics = build_topics(people, works, out)

    dump(out / "index.json", {"items": index})
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
