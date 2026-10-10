"""Verify the rendered English metadata against registry data and a prior build.

Run after a normal production Jekyll build:
    python tools/check_search_metadata.py --baseline PATH_TO_PREVIOUS_SITE
The report stays in the ignored local verification directory.
"""
from __future__ import annotations

import argparse
import collections
from datetime import datetime, timezone
import json
from html import unescape
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

import yaml


PEOPLE = [
    "masuda-junichi", "ohmori-shigeru", "sugimori-ken", "tajiri-satoshi",
    "ishihara-tsunekazu", "morimoto-shigeki", "ichinose-go", "james-turner",
    "shudo-takeshi", "aoki-kaori",
]
GAMES = ["x-y", "red-green", "black-white", "sword-shield", "sun-moon"]


class Head(HTMLParser):
    def __init__(self, html: str):
        super().__init__(convert_charrefs=True)
        self.titles, self.h1, self.schemas = [], [], []
        self.meta, self.links = {}, []
        self.lang, self.active, self.text = None, None, []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "meta":
            self.meta[attrs.get("name") or attrs.get("property")] = attrs.get("content")
        if tag == "link" and attrs.get("rel") in {"canonical", "alternate"}:
            self.links.append(attrs)
        if tag in {"title", "h1"} or (tag == "script" and attrs.get("type") == "application/ld+json"):
            self.active, self.text = tag, []

    def handle_data(self, data):
        if self.active:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag != self.active:
            return
        text = "".join(self.text).strip()
        if tag == "title":
            self.titles.append(text)
        elif tag == "h1":
            self.h1.append(text)
        else:
            self.schemas.append(json.loads(text))
        self.active, self.text = None, []


def output_file(site: Path, url: str) -> Path:
    relative = unquote(url).lstrip("/")
    return site / relative / "index.html" if url.endswith("/") else site / relative


def publication_offset_only(current: str, previous: str) -> bool:
    """Date-only front matter keeps midnight; explicit timestamps keep UTC."""
    try:
        now, old = datetime.fromisoformat(current), datetime.fromisoformat(previous)
    except (ValueError, TypeError):
        return False
    if now.utcoffset() == old.utcoffset():
        return False
    return now.replace(tzinfo=None) == old.replace(tzinfo=None) or now.astimezone(timezone.utc) == old.astimezone(timezone.utc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    artifacts, site = root / "._site-seo-checks", root / "_site"
    generated = json.loads((artifacts / "generated-metadata.json").read_text(encoding="utf-8"))
    registry = yaml.load((root / "_data/credits_people.yml").read_text(encoding="utf-8"), Loader=yaml.CSafeLoader)
    errors, examples, titles = [], [], collections.defaultdict(list)
    wanted = {f"/people/{slug}/" for slug in PEOPLE} | {f"/credits/{slug}/" for slug in GAMES} | {"/", "/people/", "/credits/"}
    for entry in generated:
        url, metadata = entry["url"], entry["metadata"]
        path = output_file(site, url)
        if not path.is_file():
            errors.append(f"Missing HTML: {url}")
            continue
        html = Head(path.read_text(encoding="utf-8"))
        titles[html.titles[0] if html.titles else ""].append(url)
        expected = f"{metadata['title']} | Poke Amice Docs"
        # Existing pagination appends its localized page number.
        title_ok = len(html.titles) == 1 and (html.titles[0] == expected or (entry["layout"] == "home" and html.titles[0].startswith(expected + " - ")))
        if not title_ok:
            errors.append(f"Title mismatch: {url}: {html.titles}")
        if entry["layout"] != "home" and len(expected) > 80:
            errors.append(f"Long title: {url}: {len(expected)}")
        if html.meta.get("description") != metadata["description"] or len(metadata["description"]) > 190:
            errors.append(f"Description mismatch/length: {url}")
        if html.meta.get("og:title") != metadata["title"] or html.meta.get("og:description") != metadata["description"]:
            errors.append(f"Open Graph mismatch: {url}")
        if metadata.get("schema") and metadata["schema"] not in html.schemas:
            errors.append(f"Structured data mismatch: {url}")
        if html.lang != "zh-CN" or "noindex" in html.meta.get("robots", "").lower():
            errors.append(f"Language/indexability changed: {url}")
        canonicals = [link.get("href") for link in html.links if link.get("rel") == "canonical"]
        if canonicals != ["https://docs.pokeamice.com" + url]:
            errors.append(f"Canonical mismatch: {url}: {canonicals}")
        if entry["layout"] == "person":
            slug = url.rstrip("/").split("/")[-1]
            credits = registry.get(slug, {})
            works = {row["game"] for row in credits.get("credits", []) if row.get("game")}
            if works and len(works) != metadata["credited_works_count"]:
                errors.append(f"Credited works mismatch: {url}")
        if entry["layout"] == "credits-game":
            slug = url.rstrip("/").split("/")[-1]
            atlas_path = root / "assets/data/credits-profile" / f"{slug}.json"
            if atlas_path.is_file():
                counts = json.loads(atlas_path.read_text(encoding="utf-8"))["team_size"]
                if metadata["credited_entries_count"] != counts["names"] or metadata["people_count"] != counts["persons"]:
                    errors.append(f"Atlas counts mismatch: {url}")
        if url in wanted:
            if args.baseline and output_file(args.baseline, url).is_file():
                old = Head(output_file(args.baseline, url).read_text(encoding="utf-8"))
                if (old.h1, old.lang, old.links, old.meta.get("og:locale")) != (html.h1, html.lang, html.links, html.meta.get("og:locale")):
                    errors.append(f"Chinese H1/language/canonical/hreflang changed: {url}")
            examples.append({"url": url, "title": html.titles[0], "description": html.meta["description"], "h1": html.h1, **{key: metadata[key] for key in ["interview_count", "credited_works_count", "major_roles", "credited_entries_count", "people_count"] if key in metadata}})
    duplicates = {title: urls for title, urls in titles.items() if len(urls) > 1}
    if duplicates:
        errors.append(f"Duplicate generated titles: {duplicates}")
    missing_samples = wanted - {row["url"] for row in examples}
    if missing_samples:
        errors.append(f"Missing samples: {sorted(missing_samples)}")

    all_titles = collections.defaultdict(list)
    for path in site.rglob("*.html"):
        matches = re.findall(r"<title>(.*?)</title>", path.read_text(encoding="utf-8"), flags=re.S | re.I)
        if matches:
            all_titles[unescape(matches[0]).strip()].append(str(path.relative_to(site)))
    legacy_duplicates = {title: paths for title, paths in all_titles.items() if len(paths) > 1 and title not in titles}
    for title, urls in titles.items():
        if len(all_titles[title]) > 1:
            errors.append(f"Generated title collides elsewhere: {title}: {all_titles[title]}")

    # An English head must not change Japanese pages or paired hreflang links.
    ja_checked, date_offset_differences = 0, 0
    if args.baseline:
        for path in (site / "ja").rglob("*.html"):
            previous = args.baseline / path.relative_to(site)
            if not previous.is_file():
                continue
            current, old = Head(path.read_text(encoding="utf-8")), Head(previous.read_text(encoding="utf-8"))
            current_meta, old_meta = dict(current.meta), dict(old.meta)
            # _config.yml has no timezone. A previous Windows build used +09
            # while this host uses +08; compare the unchanged publication date.
            key = "article:published_time"
            if current_meta.get(key) != old_meta.get(key) and publication_offset_only(current_meta.get(key), old_meta.get(key)):
                current_meta.pop(key, None)
                old_meta.pop(key, None)
                date_offset_differences += 1
            if (current.titles, current_meta, current.lang, current.links) != (old.titles, old_meta, old.lang, old.links):
                errors.append(f"Japanese head changed: {path.relative_to(site)}")
            if current.lang != "ja":
                errors.append(f"Japanese lang invalid: {path.relative_to(site)}")
            ja_checked += 1
    report = {"verified_pages": len(generated), "layouts": dict(collections.Counter(row["layout"] for row in generated)), "duplicate_titles": duplicates, "legacy_duplicate_titles": legacy_duplicates, "total_html_files": sum(map(len, all_titles.values())), "japanese_pages_unchanged": ja_checked, "publication_date_offset_differences": date_offset_differences, "errors": errors, "examples": examples}
    (artifacts / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# English search metadata: rendered HTML verification", "", f"Checked {len(generated)} generated pages; duplicate generated titles: {len(duplicates)}; errors: {len(errors)}; Japanese SEO comparisons: {ja_checked}.", "", f"Scanned {report['total_html_files']} HTML files. Existing unrelated duplicate title groups: {len(legacy_duplicates)}. All generated titles are also checked against the rest of the site.", "", f"Publication-time offset differences from the previous build: {date_offset_differences}. The source has no configured timezone; this host uses +08 while the prior build used +09. The local publication dates, Japanese titles/descriptions, canonical links, hreflang and language are compared separately.", "", "## Actual rendered examples", ""]
    for row in examples:
        lines.extend([f"### `{row['url']}`", "", f"Title: {row['title']}", "", f"Description: {row['description']}", "", f"Visible H1: {' / '.join(row['h1'])}", ""])
    if legacy_duplicates:
        lines.extend(["## Existing unrelated duplicate titles", "", "These pages retain their existing metadata; they are outside the person, credits and primary collection scope.", "", "| Title | Output files |", "| --- | --- |"])
        for title, paths in legacy_duplicates.items():
            lines.append("| " + title.replace("|", r"\|") + " | " + "<br>".join(paths) + " |")
    if errors:
        lines.extend(["## Errors", "", *errors])
    (artifacts / "verification.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key not in {"examples", "legacy_duplicate_titles", "errors"}}, ensure_ascii=False, indent=2))
    print(f"Existing unrelated duplicate title groups: {len(legacy_duplicates)}; errors: {len(errors)}")
    for error in errors[:10]:
        print(error)
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
