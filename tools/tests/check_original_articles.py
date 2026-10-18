#!/usr/bin/env python3
"""Compare every rendered Weibo long article with its preserved source.

Run after tools/preview-pages.rb --layout original-article --limit 25 --css.
Uses the same BeautifulSoup dependency as tools/weibo_common.py, plus PyYAML.
Writes the manifest consumed by check_original_articles.cjs.
"""
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
PREVIEW = ROOT / ".preview-build" / "pages"
OUTPUT = ROOT / ".preview-build" / "longform"


def compact(text):
    return re.sub(r"\s+", "", text)


def main():
    manifest = []
    for post in sorted((ROOT / "_posts").glob("*.md")):
        source = post.read_text(encoding="utf-8")
        if not source.startswith("---\n"):
            continue
        _, header, body = source.split("---\n", 2)
        metadata = yaml.safe_load(header)
        if not metadata.get("weibo_article"):
            continue
        assert metadata["layout"] == "original-article", post.name
        slug = metadata.get("slug", post.stem[11:])
        url = metadata.get("permalink", "/" + "/".join(metadata["categories"]) + "/" + slug + "/")
        rendered = BeautifulSoup((PREVIEW / unquote(url).strip("/") / "index.html").read_text(encoding="utf-8"), "html.parser")
        original = BeautifulSoup(body, "html.parser")
        content = rendered.select_one("[data-original-content]")
        assert content is not None, post.name
        assert compact(content.get_text()) == compact(original.get_text()), f"changed text: {post.name}"
        assert [x.get("src") for x in content.select("img")] == [x.get("src") for x in original.select("img")], f"changed images: {post.name}"
        assert [x.get("href") for x in content.select("a")] == [x.get("href") for x in original.select("a")], f"changed links: {post.name}"
        assert len(rendered.select("[data-original-reader] h1")) == 1, post.name
        canonical = rendered.select_one('link[rel="canonical"]')
        assert unquote(urlsplit(canonical["href"]).path) == url, post.name
        ids = [x["id"] for x in rendered.select("[data-original-reader] [id]")]
        assert len(ids) == len(set(ids)), f"duplicate IDs: {post.name}"
        chapters = rendered.select(".original-toc a")
        for chapter in chapters:
            assert unquote(chapter["href"][1:]) in ids, f"broken chapter: {post.name}"
        manifest.append({"file": post.name, "url": url, "images": len(content.select("img")), "chapters": len(chapters)})
    assert manifest, "No rendered Weibo articles found"
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(manifest)} articles: source text, original image/link order, canonical URLs and {sum(p['chapters'] for p in manifest)} chapter links preserved; {sum(p['images'] for p in manifest)} images.")


if __name__ == "__main__":
    main()
