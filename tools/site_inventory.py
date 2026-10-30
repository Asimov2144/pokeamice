"""站点清单：首页、资料窗口（/keys/）、英文层（/en/）和 sitemap 上的数字只在这里数一次。

    python tools/site_inventory.py build              # 读 _posts / _ja / _pages / _data，写 _data/site_inventory.json
    python tools/site_inventory.py show               # 打印每个数字和它的口径
    python tools/site_inventory.py check --site _site # 构建后：页面上印的数、sitemap 里的网址，都要和清单对上

每篇帖子在这里只归一类（kind，互斥，加起来就是总量）、一个扫描类型（scan_type，只有扫描才有）、
一个原文语言、两个公开状态（listed：进目录和检索；indexed：进 sitemap）。_plugins/site_inventory.rb
把这一行交给 Jekyll 的帖子（post.inv_kind 等），模板按它筛，不再各写一套条件；数字用
_includes/inv.html 印出来，带上口径（title）和 data-inv，check 就按 data-inv 逐个核对。

只用标准库和 PyYAML（部署流程里已装 pyyaml==6.0.2）。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_data" / "site_inventory.json"
PUBLIC = "assets/data/site-inventory.json"       # 构建出来的公开副本（assets/data/site-inventory.json 模板）
IN_ACTIONS = os.environ.get("GITHUB_ACTIONS") == "true"
FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---", re.S)
DATED = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-")

GF_BLOGS = {"gamefreak_director_column", "gamefreak_masuda_lineblog", "gamefreak_legacy_blog"}
INTERVIEW_LAYOUTS = {"interview-editorial", "parallel-translation"}

# 类型：从上往下第一条命中的就是它的类，所以各类互斥、加起来等于总量。
# 检索中心的「内容类型」筛选（catalogue-seed.html）用 type_label，同样由这里决定。
KINDS = [
    # key, 中文名, English, 检索中心类型, 口径
    ("long", "长文分析", "Long-form analyses", "文章",
     "分类含「长文分析」的站主原创长文。", "Original long-form analyses (category 长文分析)."),
    ("scan", "扫描翻译", "Magazine scans", "扫描翻译",
     "archive_type 为 scan_translation，或分类含「扫描存档」的整页扫描转写翻译（不再计入访谈）。",
     "Page scans with transcription and translation (archive_type scan_translation or category 扫描存档); not counted as interviews."),
    ("feature", "媒体专题", "Media features", "媒体专题",
     "archive_type 为 media_feature 的视频 / 媒体专题。", "Video and media features (archive_type media_feature)."),
    ("interview", "访谈翻译", "Interviews", "访谈翻译",
     "版式为 interview-editorial / parallel-translation，或 archive_type 为 interview_translation，或分类含「访谈翻译」，且不属于以上三类。",
     "Interview layouts, archive_type interview_translation or category 访谈翻译, excluding scans, features and long-form analyses."),
    ("blog", "Game Freak 博客", "Game Freak blogs", "Game Freak 博客",
     "archive_type 为部长专栏、增田 LINE BLOG 或旧员工 / 美术博客的复原帖。",
     "Reconstructed Game Freak director columns, Masuda's LINE BLOG and legacy staff / art blogs."),
    ("topic", "官方专题报道", "Official topics", "文章",
     "分类含「专题报道」的官方专题。", "Official topic reports (category 专题报道)."),
    ("doc", "站点文档", "Site documents", "文档",
     "分类含「文档」的建站纪事与说明。", "Site documents (category 文档)."),
    ("other", "其他文章", "Other articles", "文章",
     "不属于以上任何一类的整理与译文。", "Everything not in the classes above."),
]
SCAN_TYPES = {
    "magazine_interview": ("杂志访谈", "Magazine interviews"),
    "magazine_feature": ("杂志特辑", "Magazine features"),
    "unspecified": ("未标注", "Unspecified"),
}
LANG_NAMES = {"ja": ("日语", "Japanese"), "en": ("英语", "English"), "zh": ("中文", "Chinese"),
              "ko": ("韩语", "Korean"), "fr": ("法语", "French"), "de": ("德语", "German"),
              "es": ("西班牙语", "Spanish"), "it": ("意大利语", "Italian"), "unknown": ("未标注", "Unspecified")}
LANG_ALIASES = {"english": "en", "英语": "en", "英文": "en", "en-us": "en", "en-gb": "en",
                "japanese": "ja", "日语": "ja", "日文": "ja", "ja-jp": "ja",
                "chinese": "zh", "中文": "zh", "zh-cn": "zh", "zh-hans": "zh", "zh-tw": "zh"}

# 这些数字必须在这些页面上印出来，并且等于清单（check 会逐页核对）
REQUIRED = {
    "index.html": ["total", "kind_interview", "kind_scan", "people"],
    "keys/index.html": ["total", "kind_interview", "kind_scan", "kind_blog", "people"],
    "en/index.html": ["total", "kind_interview", "kind_scan", "lang_ja"],
    "en/interviews/index.html": ["kind_interview"],
    "en/archive/index.html": ["kind_scan"],
    "en/people/index.html": ["people"],
    "en/credits/index.html": ["credits_games"],
}


def as_list(value) -> list:
    if value is None:
        return []
    return [value] if isinstance(value, (str, int)) else list(value)


def front_matter(path: Path) -> dict:
    m = FRONT.match(path.read_text(encoding="utf-8", errors="replace"))
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def post_date(fm: dict, path: Path) -> dt.datetime | None:
    value = fm.get("date")
    if isinstance(value, dt.datetime):
        return value.replace(tzinfo=None) if value.tzinfo is None else value.astimezone(dt.timezone.utc).replace(tzinfo=None)
    if isinstance(value, dt.date):
        return dt.datetime(value.year, value.month, value.day)
    m = DATED.match(path.name)
    return dt.datetime(int(m[1]), int(m[2]), int(m[3])) if m else None


def classify(fm: dict) -> str:
    cats = {str(c) for c in as_list(fm.get("categories"))}
    archive = str(fm.get("archive_type") or fm.get("resource_type") or "")
    if "长文分析" in cats:
        return "long"
    if archive == "scan_translation" or "扫描存档" in cats:
        return "scan"
    if archive == "media_feature":
        return "feature"
    if fm.get("layout") in INTERVIEW_LAYOUTS or archive == "interview_translation" or "访谈翻译" in cats:
        return "interview"
    if archive in GF_BLOGS:
        return "blog"
    if "专题报道" in cats:
        return "topic"
    if "文档" in cats:
        return "doc"
    return "other"


def source_lang(fm: dict) -> str:
    source = fm.get("source") if isinstance(fm.get("source"), dict) else {}
    raw = fm.get("original_lang") or fm.get("original_language") or source.get("language") or fm.get("source_language")
    value = str(raw or "").strip().lower()
    value = LANG_ALIASES.get(value, value.split("-")[0] if value else "unknown")
    return value if value in LANG_NAMES else "unknown"


def metric(value: int, label: str, label_en: str, definition: str, definition_en: str, group: str) -> dict:
    return {"value": value, "label": label, "label_en": label_en, "group": group,
            "definition": definition, "definition_en": definition_en}


def page_url(path: Path, fm: dict) -> str:
    link = str(fm.get("permalink") or "")
    if link:
        return link if link.startswith("/") else "/" + link
    rel = path.relative_to(ROOT / "_pages").with_suffix("")
    rel = rel.parent if rel.name == "index" else rel
    return "/" + rel.as_posix().strip("/.") + "/"


def build_inventory(now: dt.datetime | None = None) -> dict:
    now = now or dt.datetime.now()
    posts, rows = [], {}
    for path in sorted((ROOT / "_posts").rglob("*")):
        if path.suffix not in (".md", ".markdown", ".html") or not path.is_file():
            continue
        fm = front_matter(path)
        date = post_date(fm, path)
        # Jekyll 不输出 published: false 和日期在未来的帖子（_config.yml 没开 future）
        if fm.get("published") is False or (date and date > now):
            continue
        cats = {str(c) for c in as_list(fm.get("categories"))}
        kind = classify(fm)
        listed = fm.get("search") is not False
        row = {
            "kind": kind,
            "type_label": next(k[3] for k in KINDS if k[0] == kind),
            "listed": listed,
            "indexed": fm.get("sitemap") is not False and "Sites" not in cats,
            "source_lang": source_lang(fm),
            "year": date.year if date else None,
        }
        if kind == "scan":
            row["scan_type"] = str(fm.get("source_kind") or "unspecified")
        rows[path.relative_to(ROOT).as_posix()] = row
        posts.append((fm, row))

    listed = [(fm, row) for fm, row in posts if row["listed"]]
    kinds = Counter(row["kind"] for _, row in listed)
    scans = Counter(row["scan_type"] for _, row in listed if row["kind"] == "scan")
    langs = Counter(row["source_lang"] for _, row in listed)
    years = sorted(row["year"] for _, row in listed if row["year"])

    ja_docs = [p for p in sorted((ROOT / "_ja").rglob("*.md")) if front_matter(p).get("published") is not False]
    pages = []
    for path in sorted((ROOT / "_pages").rglob("*")):
        if path.suffix in (".md", ".html") and path.is_file():
            fm = front_matter(path)
            if fm.get("published") is not False:
                pages.append((page_url(path, fm), fm))
    en_pages = [(u, fm) for u, fm in pages if fm.get("layout") == "english-discovery"]

    def section_pages(name: str) -> int:
        return sum(1 for u, fm in pages if u.split("/")[1:2] == [name] and fm.get("sitemap") is not False)

    data = ROOT / "_data"
    people = yaml.safe_load((data / "people.yml").read_text(encoding="utf-8")) or []
    named = set()
    for fm, _ in posts:
        entities = fm.get("entities") if isinstance(fm.get("entities"), dict) else {}
        named.update(str(n) for n in as_list(entities.get("people")))
    library = [p for p in people if p.get("kind") not in ("character", "figure", "staff") and p.get("name") in named]
    works = yaml.safe_load((data / "works.yml").read_text(encoding="utf-8")) or []
    games = yaml.safe_load((data / "credits_games.yml").read_text(encoding="utf-8")) or []

    total = len(listed)
    m = {}
    m["total"] = metric(total, "条目", "records",
                        "公开条目：Jekyll 输出的全部帖子中没有标 search: false 的，即首页、检索中心和资料窗口列出的条目；下面各类加起来等于它。",
                        "Public records: every published post not marked search: false. The classes below add up to this.", "total")
    m["unlisted"] = metric(len(posts) - total, "未列出", "unlisted",
                           "已发布但标了 search: false、不进目录和检索的帖子，不计入条目。",
                           "Published posts marked search: false; not counted as records.", "public")
    for key, label, label_en, _, definition, definition_en in KINDS:
        m[f"kind_{key}"] = metric(kinds.get(key, 0), label, label_en, definition, definition_en, "kind")
    m["interview_shelf"] = metric(kinds.get("interview", 0) + kinds.get("scan", 0), "访谈与杂志扫描", "interviews and scans",
                                  "首页「访谈翻译」栏目列出的条目 = 访谈翻译 + 扫描翻译。",
                                  "The home page's interview tab: interviews plus magazine scans.", "kind")
    for key in sorted(set(scans) | {"magazine_interview", "magazine_feature"}):
        label, label_en = SCAN_TYPES.get(key, (key, key))
        m[f"scan_{key}"] = metric(scans.get(key, 0), label, label_en,
                                  ("扫描翻译中没写 source_kind 的条目" if key == "unspecified" else f"扫描翻译中 source_kind 为 {key} 的条目") + "；各扫描类型加起来等于扫描翻译。",
                                  ("Scans without a source_kind" if key == "unspecified" else f"Scans whose source_kind is {key}") + "; scan types add up to all scans.", "scan")
    m["lang_zh"] = metric(total, "中文版", "Chinese pages",
                          "每个公开条目有一个中文页面，所以等于条目数。", "Each public record has one Chinese page.", "lang")
    m["lang_ja"] = metric(len(ja_docs), "日文版", "Japanese editions",
                          "_ja 集合中已发布的日文译本（/ja/<slug>/），不含 /ja/ 首页。",
                          "Published Japanese editions in the _ja collection (/ja/<slug>/), not counting /ja/ itself.", "lang")
    m["lang_en"] = metric(len(en_pages), "英文入口", "English pages",
                          "版式为 english-discovery 的英文研究入口页（/en/ 及其子页）。",
                          "English research pages (layout english-discovery, /en/ and its subpages).", "lang")
    for key in sorted(langs):
        label, label_en = LANG_NAMES[key]
        m[f"source_lang_{key}"] = metric(langs[key], f"原文{label}", f"{label_en} sources",
                                         "公开条目按原文语言（original_lang / source.language）分；各语言加起来等于条目数。",
                                         "Public records by source language; languages add up to all records.", "source_lang")
    indexed = sum(1 for _, row in posts if row["indexed"])
    m["indexed"] = metric(indexed, "提交收录", "submitted to search engines",
                          "写进 sitemap 的帖子：没有标 sitemap: false，且分类不含 Sites（站务帖）。",
                          "Posts in the sitemap: not sitemap: false and not in category Sites.", "public")
    m["not_indexed"] = metric(len(posts) - indexed, "不提交收录", "not submitted",
                              "已发布但不写进 sitemap 的帖子（sitemap: false 或站务帖）。",
                              "Published posts left out of the sitemap (sitemap: false or category Sites).", "public")
    m["people"] = metric(len(library), "人物", "people",
                         "人物库（/people/）列出的人：_data/people.yml 中排除角色、雕像与只在制作名单出现的 staff，且至少有一篇帖子的 entities.people 写了他。",
                         "People in the people library: no characters, figures or credits-only staff, and named in at least one post's entities.", "entity")
    m["works"] = metric(sum(1 for w in works if w.get("placeholder") is None), "作品", "works",
                        "_data/works.yml 中不是占位的作品。", "Works in _data/works.yml that are not placeholders.", "entity")
    m["credits_games"] = metric(len(games), "制作名单", "staff rolls",
                                "_data/credits_games.yml 收录了制作名单的游戏数，每作一页 /credits/<slug>/。",
                                "Games with an indexed staff roll, one page each at /credits/<slug>/.", "entity")
    sitemap = {
        "home": (1, "首页", "home page", "首页 /。", "The home page /."),
        "posts": (indexed, "帖子", "posts", "等于「提交收录」。", "Equals the posts submitted to search engines."),
        "people": (section_pages("people"), "人物页", "people pages",
                   "/people/ 下没有标 sitemap: false 的页面（_pages/people/）。", "Pages under /people/ not marked sitemap: false."),
        "credits": (section_pages("credits"), "制作名单页", "credits pages",
                    "/credits/ 下没有标 sitemap: false 的页面（含 /credits/ 本身）。", "Pages under /credits/ not marked sitemap: false."),
        "en": (sum(1 for _, fm in en_pages if fm.get("sitemap") is not False), "英文入口", "English pages",
               "english-discovery 版式的页面。", "Pages with the english-discovery layout."),
        "ja": (len(ja_docs) + 1, "日文版", "Japanese pages", "日文译本各篇加 /ja/ 首页。", "Japanese editions plus /ja/."),
    }
    for key, (value, label, label_en, definition, definition_en) in sitemap.items():
        m[f"sitemap_{key}"] = metric(value, f"sitemap · {label}", f"sitemap · {label_en}", definition, definition_en, "sitemap")
    m["sitemap_total"] = metric(sum(v[0] for v in sitemap.values()), "sitemap 网址", "sitemap URLs",
                                "sitemap.xml 中的网址总数 = 以上六类之和。", "All URLs in sitemap.xml: the six parts above.", "sitemap")
    return {
        "version": 1,
        "years": [years[0], years[-1]] if years else [],
        "groups": [["total", "总量", "Total"], ["kind", "类型", "Types"], ["scan", "扫描类型", "Scan types"],
                   ["lang", "语言版本", "Language versions"], ["source_lang", "原文语言", "Source languages"],
                   ["public", "公开状态", "Public status"], ["entity", "人物与作品", "People and works"],
                   ["sitemap", "sitemap", "Sitemap"]],
        "metrics": m,
        "posts": rows,
    }


def invariants(inv: dict) -> list[str]:
    """清单自己的账要平：各类、各扫描类型、各原文语言加起来都等于总数。"""
    m = {k: v["value"] for k, v in inv["metrics"].items()}
    errors = []
    sums = {
        "类型之和 = 条目": (sum(v for k, v in m.items() if k.startswith("kind_")), m["total"]),
        "扫描类型之和 = 扫描翻译": (sum(v for k, v in m.items() if k.startswith("scan_")), m["kind_scan"]),
        "原文语言之和 = 条目": (sum(v for k, v in m.items() if k.startswith("source_lang_")), m["total"]),
        "中文版 = 条目": (m["lang_zh"], m["total"]),
        "收录 + 不收录 = 全部已发布": (m["indexed"] + m["not_indexed"], m["total"] + m["unlisted"]),
        "sitemap 帖子 = 提交收录": (m["sitemap_posts"], m["indexed"]),
        "sitemap 日文 = 日文版 + 1": (m["sitemap_ja"], m["lang_ja"] + 1),
        "sitemap 英文 = 英文入口": (m["sitemap_en"], m["lang_en"]),
    }
    for name, (got, want) in sums.items():
        if got != want:
            errors.append(f"{name}：{got} ≠ {want}")
    return errors


def dumps(inv: dict) -> str:
    """数字和口径缩进好读；每篇帖子一行，新增一篇 diff 就是一行。"""
    head = json.dumps({k: v for k, v in inv.items() if k != "posts"}, ensure_ascii=False, indent=1)
    rows = ",\n".join(f"  {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}" for k, v in inv["posts"].items())
    return head[:-2] + ',\n "posts": {\n' + rows + "\n }\n}\n"


# ---------------------------------------------------------------- check

class Numbers(HTMLParser):
    """收集带 data-inv 的元素：键、印出来的数字、口径（title）。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found, self.stack = [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "data-inv" in attrs:
            self.stack.append([attrs["data-inv"], attrs.get("title") or "", ""])
        elif self.stack:
            self.stack.append(None)

    def handle_endtag(self, tag):
        if self.stack:
            item = self.stack.pop()
            if item is not None:
                self.found.append((item[0], item[2].strip(), item[1]))

    def handle_data(self, data):
        for item in self.stack:
            if item is not None:
                item[2] += data


def sitemap_parts(path: Path, base: str) -> Counter:
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    parts = Counter()
    for loc in ET.parse(path).getroot().findall("s:url/s:loc", ns):
        url = unquote(urlsplit(loc.text.strip()).path)
        url = url[len(base):] if base and url.startswith(base) else url
        seg = url.split("/")[1] if url.count("/") > 1 else ""
        if url == "/":
            parts["home"] += 1
        elif seg in ("people", "credits", "en", "ja"):
            parts[seg] += 1
        else:
            parts["posts"] += 1
    return parts


def say(level: str, msg: str) -> None:
    print(f"::{level} title=站点清单::{msg}" if IN_ACTIONS else f"[{level}] {msg}")


def check(site: Path, baseurl: str = "") -> int:
    errors = []
    public = site / PUBLIC
    if not public.exists():
        say("error", f"{PUBLIC} 没有构建出来")
        return 1
    built = json.loads(public.read_text(encoding="utf-8"))
    fresh = build_inventory()
    want = {k: v["value"] for k, v in fresh["metrics"].items()}
    got = {k: v["value"] for k, v in built["metrics"].items()}
    # 1. Jekyll 用的清单和现在的源文件重算出来的一致（_data/site_inventory.json 不是旧的）
    for key in sorted(set(want) | set(got)):
        if want.get(key) != got.get(key):
            errors.append(f"清单过期：{key} 构建时 {got.get(key)}，按源文件重算 {want.get(key)}（先跑 build）")
    coverage = built.get("coverage") or {}
    if coverage.get("missing"):
        errors.append(f"{len(coverage['missing'])} 篇帖子不在清单里，例如 {coverage['missing'][:3]}")
    if coverage.get("stale"):
        errors.append(f"清单里有 {len(coverage['stale'])} 篇 Jekyll 没输出的帖子，例如 {coverage['stale'][:3]}")
    if coverage.get("posts_seen") is not None and coverage["posts_seen"] != got["total"] + got["unlisted"]:
        errors.append(f"Jekyll 输出 {coverage['posts_seen']} 篇帖子，清单是 {got['total'] + got['unlisted']} 篇")
    if built.get("ja_seen") is not None and built["ja_seen"] != got["lang_ja"]:
        errors.append(f"Jekyll 输出 {built['ja_seen']} 篇日文版，清单是 {got['lang_ja']} 篇")
    errors += invariants(fresh)
    # 2. 每个入口印出来的数等于清单，并且带口径
    shown = 0
    for page, required in REQUIRED.items():
        path = site / page
        if not path.exists():
            errors.append(f"{page} 没有构建出来")
            continue
        parser = Numbers()
        parser.feed(path.read_text(encoding="utf-8"))
        keys = set()
        for key, text, title in parser.found:
            keys.add(key)
            shown += 1
            if key not in got:
                errors.append(f"{page}：data-inv=\"{key}\" 不是清单里的数字")
                continue
            number = re.sub(r"[,\s]", "", text)
            if number != str(got[key]):
                errors.append(f"{page}：{key} 印的是「{text}」，清单是 {got[key]}")
            if not title.strip():
                errors.append(f"{page}：{key} 没有口径（title）")
        for key in required:
            if key not in keys:
                errors.append(f"{page}：没印 {key}（{got.get(key)}）")
    # 3. sitemap 里的网址按类数，等于清单
    sitemap = site / "sitemap.xml"
    if sitemap.exists():
        parts = sitemap_parts(sitemap, baseurl)
        for key in ("home", "posts", "people", "credits", "en", "ja"):
            if parts.get(key, 0) != got[f"sitemap_{key}"]:
                errors.append(f"sitemap.xml：{key} 有 {parts.get(key, 0)} 个网址，清单是 {got[f'sitemap_{key}']}")
        if sum(parts.values()) != got["sitemap_total"]:
            errors.append(f"sitemap.xml：共 {sum(parts.values())} 个网址，清单是 {got['sitemap_total']}")
    else:
        errors.append("sitemap.xml 没有构建出来")
    for error in errors:
        say("error", error)
    if not errors:
        print(f"站点清单一致：{got['total']} 条目，{shown} 处数字，sitemap {got['sitemap_total']} 个网址")
    return 1 if errors else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    sub.add_parser("show")
    c = sub.add_parser("check")
    c.add_argument("--site", type=Path, default=ROOT / "_site")
    c.add_argument("--baseurl", default="")
    args = ap.parse_args()
    if args.cmd == "check":
        return check(args.site, args.baseurl)
    inv = build_inventory()
    problems = invariants(inv)
    for problem in problems:
        say("error", problem)
    if args.cmd == "build":
        tmp = OUT.with_suffix(".json.tmp")
        tmp.write_text(dumps(inv), encoding="utf-8")
        os.replace(tmp, OUT)
        print(f"写入 {OUT.relative_to(ROOT)}：{inv['metrics']['total']['value']} 条目，{len(inv['posts'])} 篇帖子")
    else:
        for key, item in inv["metrics"].items():
            print(f"{item['group']:<12} {key:<28} {item['value']:>6}  {item['label']}：{item['definition']}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
