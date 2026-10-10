"""Validate actual production HTML, entity IDs, visible facts and random samples.

Run after a production build. The manifest written by the verification build is
optional; it adds source-grounded checks for interview participants and language.
Reports are saved in the ignored ._site-seo-checks directory.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import random
import re
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import yaml


BASE = "https://docs.pokeamice.com"
ENTITY_TYPES = {"Person", "VideoGame", "Article", "Organization", "CreativeWork", "ProfilePage", "CollectionPage"}


def normalized(value):
    return re.sub(r"\s+", " ", unescape(str(value))).strip()


def folded(value):
    return re.sub(r"[\s・·]", "", str(value).lower())


def absolute(value):
    value = value if value.startswith(("https://", "http://")) else BASE + "/" + value.lstrip("/")
    return quote(value, safe="%:/?#[]@!$&'()*+,;=-._~")


def file_for(site, address):
    path = unquote(urlsplit(address).path).lstrip("/")
    return site / path / "index.html" if not path or path.endswith("/") else site / path


class Rendered(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.body = False
        self.ignored = []
        self.texts, self.links, self.images, self.languages = [], [], [], []
        self.h1, self.heading_parts, self.in_heading = [], [], False
        self.canonicals, self.lang, self.itemscopes = [], None, []
        self.feed(html)
        self.text = normalized(" ".join(self.texts))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(absolute(attrs["href"]))
        if tag == "body":
            self.body = True
        if not self.body:
            return
        if tag in {"script", "style"}:
            self.ignored.append(tag)
        if self.ignored:
            return
        if tag == "h1":
            self.in_heading, self.heading_parts = True, []
        if tag == "a" and attrs.get("href"):
            self.links.append(absolute(attrs["href"]))
        if tag == "img" and attrs.get("src"):
            self.images.append(absolute(attrs["src"]))
        if attrs.get("lang"):
            self.languages.append(attrs["lang"])
        main_article = tag == "article" and set(attrs.get("class", "").split()) & {"page", "ed-article", "parallel-translation__article"}
        if main_article and attrs.get("itemtype") in {"https://schema.org/Article", "https://schema.org/CreativeWork"}:
            self.itemscopes.append(attrs["itemtype"])

    def handle_endtag(self, tag):
        if self.ignored:
            if tag == self.ignored[-1]:
                self.ignored.pop()
            return
        if tag == "body":
            self.body = False
        if tag == "h1" and self.in_heading:
            self.h1.append(normalized(" ".join(self.heading_parts)))
            self.in_heading = False

    def handle_data(self, data):
        if self.body and not self.ignored:
            self.texts.append(data)
            if self.in_heading:
                self.heading_parts.append(data)

    def shows(self, value):
        return bool(normalized(value)) and normalized(value).lower() in self.text.lower()


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def read_yaml(root, path):
    return yaml.load((root / path).read_text(encoding="utf-8-sig"), Loader=yaml.CSafeLoader)


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--site", type=Path)
    cli.add_argument("--seed", type=int, default=20261010)
    args = cli.parse_args()
    root = Path(__file__).resolve().parents[1]
    site = args.site or root / "_site"
    artifacts = root / "._site-seo-checks"
    artifacts.mkdir(exist_ok=True)
    people = {row["slug"]: row for row in read_yaml(root, "_data/people.yml") if row.get("kind") not in {"character", "figure"}}
    games = {row["slug"]: row for row in read_yaml(root, "_data/credits_games.yml")}
    credits = read_yaml(root, "_data/credits_people.yml")
    social = read_yaml(root, "_data/people_social.yml")
    manifest_path = artifacts / "entity-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    documents = {absolute(doc["url"]): doc for doc in manifest}
    person_names = {}
    for slug, person in people.items():
        credit = credits.get(slug, {})
        for name in [person["name"], *person.get("aliases", []), credit.get("name"), credit.get("kanji"), credit.get("kana")]:
            if name:
                person_names.setdefault(folded(name), slug)
    errors, stats, pages, identity_ids = [], Counter(), {}, defaultdict(set)
    reference_edges, max_person_bytes, max_subjects = 0, 0, 0

    def require(condition, address, message):
        if not condition:
            errors.append(f"{address}: {message}")

    def participant_ids(data):
        names = data.get("answerers") or re.split(r"[,，、;；]", str(data.get("interviewee") or ""))
        answerers = set()
        for name in names:
            name = (data.get("speaker_zh") or {}).get(name, name)
            slug = person_names.get(folded(name))
            if slug:
                answerers.add(f"{BASE}/people/{slug}/#person")
        return answerers

    for path in sorted(site.rglob("*.html")):
        stats["html_files"] += 1
        html = path.read_text(encoding="utf-8")
        scripts = re.findall(r"<script\b([^>]*)>(.*?)</script\s*>", html, re.I | re.S)
        schemas = []
        for attrs, content in scripts:
            if not re.search(r"\btype\s*=\s*['\"]application/ld\+json['\"]", attrs, re.I):
                continue
            stats["json_ld_scripts"] += 1
            try:
                schemas.append(json.loads(content))
            except (json.JSONDecodeError, ValueError) as exc:
                errors.append(f"{path.relative_to(site)}: invalid JSON-LD: {exc}")
        if "POKEAMICE_ENTITY_GRAPH" in html:
            errors.append(f"{path.relative_to(site)}: unrendered schema placeholder")
        if not schemas:
            continue
        definitions = [node for schema in schemas for node in objects(schema) if node.get("@id") and node.get("@type")]
        ids = [node["@id"] for node in definitions]
        require(len(ids) == len(set(ids)), str(path.relative_to(site)), "repeated @id definitions")
        graph = [node for schema in schemas for node in schema.get("@graph", [])] if all(isinstance(s, dict) for s in schemas) else []
        primary = next((node for node in graph if node.get("@type") in {"Person", "VideoGame", "Article"}), None)
        for schema in schemas:
            for node in objects(schema):
                for key in ("@id", "url", "image", "sameAs"):
                    values = node.get(key, [])
                    if isinstance(values, str):
                        values = [values]
                    if isinstance(values, list):
                        for value in values:
                            if isinstance(value, str):
                                require(value.startswith(("https://", "http://")), str(path.relative_to(site)), f"relative {key}: {value}")
                if node.keys() == {"@id"}:
                    reference_edges += 1
                    parsed = urlsplit(node["@id"])
                    if parsed.netloc == "docs.pokeamice.com" and parsed.fragment in {"person", "game", "article"}:
                        require(file_for(site, node["@id"]).is_file(), str(path.relative_to(site)), f"missing entity target {node['@id']}")
        for node in definitions:
            if node.get("@type") in ENTITY_TYPES and node.get("url"):
                identity_ids[(node["@type"], absolute(node["url"]))].add(node["@id"])
        if not primary:
            continue
        address, kind = primary["url"], primary["@type"]
        stats[kind] += 1
        require(address not in pages, address, "multiple rendered pages define the same canonical primary entity")
        body = Rendered(html)
        require(body.canonicals == [address], address, "entity URL differs from head canonical")
        require(len([node for node in graph if node.get("@type") == kind]) == 1, address, f"duplicate {kind}")
        for node in graph:
            for key in ("name", "headline", "description", "jobTitle", "creditText"):
                if node.get(key):
                    require(body.shows(node[key]), address, f"invisible {node.get('@type')}.{key}: {node[key]}")
            for name in node.get("alternateName", []):
                require(body.shows(name), address, f"invisible alternateName: {name}")
        if kind == "Person":
            slug = urlsplit(address).path.rstrip("/").split("/")[-1]
            require(slug in people, address, "Person not in human registry")
            record = social.get(slug, {})
            verified = {row["url"] for row in record.get("accounts", [])}
            for account in primary.get("sameAs", []):
                require(record.get("checked") and record.get("found_via") and account in verified and account in body.links, address, f"unverified/invisible sameAs {account}")
            if primary.get("image"):
                require(primary["image"] in body.images, address, "image absent from visible body")
            require(not primary.get("worksFor"), address, "inferred employer")
            if primary.get("jobTitle"):
                require(primary["jobTitle"] == people.get(slug, {}).get("role"), address, "jobTitle not an explicit registry role")
            subjects = primary.get("subjectOf", [])
            max_subjects = max(max_subjects, len(subjects))
            require(len(subjects) <= 8 and all(set(item) == {"@id"} for item in subjects), address, "unbounded/nested interview objects")
            for item in subjects:
                target = item["@id"].split("#", 1)[0]
                require(target in body.links, address, "subjectOf interview not linked in body")
                if target in documents:
                    require(primary["@id"] in participant_ids(documents[target]["data"]), address, "subjectOf incorrectly labels a mentioned person as interviewee")
            max_person_bytes = max(max_person_bytes, len(json.dumps(graph, ensure_ascii=False, separators=(",", ":")).encode("utf-8")))
        elif kind == "VideoGame":
            slug = urlsplit(address).path.rstrip("/").split("/")[-1]
            game = games.get(slug, {})
            require(bool(game), address, "game absent from source registry")
            if primary.get("datePublished"):
                require(primary["datePublished"] == str(game.get("year")) and len(primary["datePublished"]) == 4, address, "invented release day/year")
            rolls = [node for node in graph if node.get("@type") == "ItemList"]
            require(len(rolls) == 1 and rolls[0]["numberOfItems"] == game.get("count"), address, "credits count differs from data")
            for prop, pattern in {"director": r"(?:Director|Directors|Game Director)", "musicBy": r"(?:Music|Music Composition|Composers?|Original Music)"}.items():
                for person in primary.get(prop, []):
                    person_slug = urlsplit(person["@id"]).path.rstrip("/").split("/")[-1]
                    valid = any(row["game"] == slug and re.fullmatch(pattern, row.get("role", "").split(" / ")[-1], flags=re.I) for row in credits.get(person_slug, {}).get("credits", []))
                    require(valid and person["@id"].split("#")[0] in body.links, address, f"unsupported/invisible {prop}")
            company_names = [node["name"] for node in graph if node.get("@type") == "Organization"]
            require(not any(name in {"Inc.", "Ltd.", "Inc", "Ltd"} or " × " in name for name in company_names), address, "phantom organization from developer splitting")
        else:
            require(not body.itemscopes, address, "competing anonymous Article/CreativeWork microdata")
            compatible = primary["inLanguage"] == body.lang or {primary["inLanguage"].lower(), (body.lang or "").lower()} <= {"zh-cn", "zh-hans"}
            require(compatible, address, "article language conflicts with HTML lang")
            data = documents.get(address, {}).get("data", {})
            if data:
                actual_people = {item["@id"] for item in primary.get("about", []) if item["@id"].endswith("#person")}
                expected = participant_ids(data)
                if expected:
                    require(actual_people <= expected, address, "about includes a non-interviewee")
                require(not (set(item["@id"] for item in primary.get("about", [])) & set(item["@id"] for item in primary.get("mentions", []))), address, "about and mentions duplicate the same entity")
                for key in ("translationOfWork", "isBasedOn", "citation"):
                    original_id = primary.get(key, {}).get("@id")
                    if not original_id:
                        continue
                    original = next((node for node in graph if node.get("@id") == original_id), None)
                    require(bool(original), address, "undefined original work")
                    if original and original.get("url"):
                        require(original["url"] in body.links, address, "original URL absent from visible source links")
                    if original and original.get("inLanguage"):
                        source = data.get("source") if isinstance(data.get("source"), dict) else {}
                        stated = data.get("original_lang") or data.get("original_language") or source.get("language") or data.get("source_language")
                        require(original["inLanguage"] == stated, address, "guessed original language")
                    if original and (data.get("recruit") or {}).get("date_basis"):
                        require(not original.get("datePublished"), address, "approximate source date expressed as an exact day")
        pages[address] = {"url": address, "kind": kind, "h1": body.h1[:1], "graph": graph, "file": str(path.resolve()), "json_bytes": len(json.dumps(graph, ensure_ascii=False).encode("utf-8"))}

    for (kind, address), ids in identity_ids.items():
        require(len(ids) == 1, address, f"multiple canonical {kind} entity IDs: {sorted(ids)}")
    for slug in people:
        require(BASE + f"/people/{slug}/" in pages, f"/people/{slug}/", "missing Person graph")
    for slug in games:
        require(BASE + f"/credits/{slug}/" in pages, f"/credits/{slug}/", "missing VideoGame graph")
    randomizer = random.Random(args.seed)
    sample = []
    for kind, count in [("Person", 5), ("VideoGame", 3), ("Article", 5)]:
        candidates = sorted(address for address, page in pages.items() if page["kind"] == kind and (
            kind != "Article" or documents.get(address, {}).get("interview") or (
                not documents and re.search(r"访谈|采访|interview|インタビュー", " ".join(page["h1"]), re.I)
            )
        ))
        require(len(candidates) >= count, kind, "insufficient sample population")
        sample.extend(randomizer.sample(candidates, min(count, len(candidates))))
    controls = [BASE + "/people/masuda-junichi/", BASE + "/people/ohmori-shigeru/", BASE + "/credits/x-y/"]
    report = {"seed": args.seed, "source_manifest_documents": len(documents), "stats": dict(stats), "reference_edges": reference_edges, "max_person_graph_bytes": max_person_bytes, "max_interview_references_per_person": max_subjects,
              "canonical_entity_conflicts": sum(len(ids) > 1 for ids in identity_ids.values()), "errors": errors, "samples": [pages[address] for address in sample], "controls": [pages[address] for address in controls if address in pages]}
    (artifacts / "entity-verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Structured data 构建验证", "", f"随机种子：{args.seed}；错误：{len(errors)}。", "",
             f"扫描 {stats['html_files']} 个 HTML，解析 {stats['json_ld_scripts']} 个 JSON-LD。人物 {stats['Person']}、作品 {stats['VideoGame']}、文章 {stats['Article']}。", "",
             f"canonical 实体 ID 冲突：{report['canonical_entity_conflicts']}。人物页最大实体图 {max_person_bytes:,} 字节；最多 {max_subjects} 个轻量访谈引用。", "",
             "页面事实来自可见正文。SEO head 文案不进入实体图。没有凭 Special Thanks 推断开发职位或雇佣关系。", "",
             "## 生成规则", "",
             "- Person：姓名与别名、头像、已有明确职务，以及核实且可见的个人账号；subjectOf 只引用实际受访且在人物页链接的条目，最多 8 篇。人物档案页关联可见的作品名单。",
             "- VideoGame：数据源中的中英名称、已呈现的日文名单名、年份、开发组织；director / musicBy 只来自明确署名角色。CollectionPage 和 ItemList 记录页面及名单数量，Atlas 概况复用可见统计。",
             "- Article：受访者和主要作品进入 about；其余人物、组织、作品进入 mentions。译文通过 translationOfWork 关联原文；原文记录已呈现的来源 URL、语言、名称和出版信息。",
             "- 全部内部实体使用 canonical URL 加固定片段 ID。重定向副本不另建目标实体；正文中原有匿名文章 microdata 已去除，保留引用卡片等独立作品标记。",
             "- 组织别名仅用于对齐 ID，未在正文呈现的别名不会进入 JSON-LD。核心组织映射附官网来源：[Game Freak](https://www.gamefreak.co.jp/company/)、[Nintendo](https://www.nintendo.co.jp/corporate/outline/index.html)、[Creatures](https://www.creatures.co.jp/company/)、[The Pokémon Company](https://corporate.pokemon.co.jp/aboutus/company/)。", "",
             "## 修改文件", "",
             "- `_plugins/entity_graph.rb`：统一实体图 helper 和构建钩子。",
             "- `_data/structured_entities.yml`：有来源的组织别名映射。",
             "- `_includes/entity-schema.html`、`_includes/article-schema.html`、`_includes/seo.html`：统一 JSON-LD 输出入口。",
             "- `_layouts/credits-game.html`：呈现来源中明确提供的日文名单名。",
             "- `_layouts/interview-editorial.html`、`_layouts/parallel-translation.html`、`_layouts/single.html`：消除同一文章的匿名 microdata 副本。",
             "- `_plugins/search_metadata.rb`：英文搜索 metadata 不再兼任实体事实生成。",
             "- `tools/tests/test_entity_graph.rb`、`tools/tests/test_search_metadata.rb`、`tools/check_entity_graph.py`：回归测试与构建产物验证。", "",
             "## 随机抽样与固定回归页面", "", "| 类型 | 页面 | 可见 H1 | 图大小 |", "| --- | --- | --- | ---: |"]
    for page in report["samples"] + report["controls"]:
        heading = (page["h1"] or [""])[0].replace("|", "&#124;")
        lines.append(f"| {page['kind']} | [{urlsplit(page['url']).path}]({page['url']}) | {heading} | {page['json_bytes']:,} B |")
    lines += ["", "## 完整 JSON-LD 证据", ""]
    for page in report["samples"] + report["controls"]:
        lines += [f"### {page['url']}", "", f"最终 HTML：`{page['file']}`", "", "```json", json.dumps({"@context": "https://schema.org", "@graph": page["graph"]}, ensure_ascii=False, indent=2), "```", ""]
    if errors:
        lines += ["## 错误", ""] + [f"- {error}" for error in errors]
    (artifacts / "entity-verification.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key not in {"samples", "controls"}}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
