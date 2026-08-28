#!/usr/bin/env python3
"""Archive Game Freak's Sugimori art and staff diary blogs from Wayback.

The pipeline keeps the same layers as the Masuda archive:

    raw -> assets -> content -> translations -> Jekyll posts

By default it processes a small representative sample. Pass ``--all`` for the
complete five-post art blog and the 209-post staff archive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qs, quote, unquote, urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup, NavigableString, Tag
from PIL import Image, UnidentifiedImageError


REPO_ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
USER_AGENT = (
    "PokeAmice-Digital-Archive/0.2 "
    "(+https://docs.pokeamice.com/; low-rate historical blog preservation)"
)

BLOGS: dict[str, dict[str, Any]] = {
    "art": {
        "slug": "gamefreak-art",
        "root_url": "http://www.gamefreak.co.jp/blog/art/",
        "snapshot": "20130808124032",
        "index_url": "http://www.gamefreak.co.jp/blog/art/",
        "title_ja": "杉森建のお絵かき日和",
        "title_zh": "杉森建的绘画日和",
        "author_ja": "杉森 建",
        "author_zh": "杉森建",
        "expected_count": 5,
        "posts_per_page": 5,
        "sample_ids": [226, 8, 5],
        "theme_css": "http://www.gamefreak.co.jp/blog/art/wp-content/themes/clean-minimal/style.css",
        "header_asset": "http://www.gamefreak.co.jp/blog/art/wp-content/themes/clean-minimal/art_tit.jpg",
        "background_asset": "http://www.gamefreak.co.jp/blog/art/wp-content/themes/clean-minimal/bg.jpg",
    },
    "staff": {
        "slug": "gamefreak-staff",
        "root_url": "http://www.gamefreak.co.jp/blog/staff/",
        "snapshot": "20130808162750",
        "index_url": "http://www.gamefreak.co.jp/blog/staff/?page_id=245",
        "title_ja": "晴れたり時々曇ったり",
        "title_zh": "晴时偶有阴",
        "author_ja": "ゲームフリークスタッフ",
        "author_zh": "GAME FREAK 员工",
        "expected_count": 209,
        "posts_per_page": 10,
        "sample_ids": [243, 201, 3],
        "theme_css": "http://www.gamefreak.co.jp/blog/staff/wp-content/themes/clean-minimal/style.css",
        "header_asset": "http://www.gamefreak.co.jp/blog/staff/wp-content/themes/clean-minimal/title.jpg",
        "background_asset": "http://www.gamefreak.co.jp/blog/staff/wp-content/themes/clean-minimal/bg.jpg",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def write_text(path: Path, text: str) -> None:
    atomic_write(path, text.encode("utf-8"))


def write_yaml(path: Path, data: Any) -> None:
    write_text(path, yaml.safe_dump(data, allow_unicode=True, sort_keys=False))


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def archive_root(blog: dict[str, Any]) -> Path:
    return REPO_ROOT / "archive" / blog["slug"]


def wayback_url(timestamp: str, original_url: str, modifier: str = "id_") -> str:
    return f"https://web.archive.org/web/{timestamp}{modifier}/{original_url}"


def find_cdx_capture(fetcher: "Fetcher", original_url: str, preferred_timestamp: str) -> tuple[requests.Response, str]:
    query = (
        "https://web.archive.org/cdx/search/cdx?"
        f"url={quote(original_url, safe='')}&output=json&filter=statuscode:200&"
        "fl=timestamp,original,statuscode,mimetype&collapse=digest"
    )
    response = fetcher.request(query)
    rows = response.json()
    if len(rows) < 2:
        raise RuntimeError(f"No successful Wayback capture for {original_url}")
    timestamps = [str(row[0]) for row in rows[1:] if row and str(row[0]).isdigit()]
    if not timestamps:
        raise RuntimeError(f"Wayback CDX returned no timestamp for {original_url}")
    preferred = int(preferred_timestamp)
    timestamp = min(timestamps, key=lambda value: abs(int(value[:14]) - preferred))
    return fetcher.request(wayback_url(timestamp, original_url)), timestamp


def unwrap_wayback_url(value: str, base_url: str) -> str:
    resolved = urljoin(base_url, value)
    match = re.match(r"https?://web\.archive\.org/web/\d+(?:[a-z_]+)?/(https?://.*)", resolved)
    return match.group(1) if match else resolved


def safe_filename(url: str, fallback: str = "asset.bin") -> str:
    name = Path(unquote(urlparse(url).path)).name or fallback
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip(".-") or fallback


def is_image_url(url: str) -> bool:
    return Path(urlparse(url).path).suffix.lower() in IMAGE_EXTENSIONS


def post_id_from_url(url: str) -> int | None:
    values = parse_qs(urlparse(url).query).get("p")
    return int(values[0]) if values and values[0].isdigit() else None


@dataclass
class Fetcher:
    delay: float = 0.45
    refresh: bool = False

    def __post_init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "ja"})
        self.network_requests = 0

    def request(self, url: str) -> requests.Response:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=45, allow_redirects=True)
                response.raise_for_status()
                self.network_requests += 1
                if self.delay:
                    time.sleep(self.delay)
                return response
            except requests.RequestException as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"Failed to fetch {url}: {last_error}")

    def capture(self, original_url: str, timestamp: str, body: Path, meta: Path) -> bytes:
        if body.exists() and meta.exists() and not self.refresh:
            return body.read_bytes()
        replay = wayback_url(timestamp, original_url)
        response = self.request(replay)
        payload = response.content
        atomic_write(body, payload)
        write_yaml(
            meta,
            {
                "original_url": original_url,
                "requested_replay_url": replay,
                "final_url": response.url,
                "captured_at": utc_now(),
                "status": response.status_code,
                "content_type": response.headers.get("Content-Type"),
                "bytes": len(payload),
                "sha256": sha256_bytes(payload),
            },
        )
        return payload


def parse_date(post: Tag) -> str:
    left = post.select_one(".left")
    if not left:
        raise ValueError("Post has no .left date block")
    day_node = left.select_one("h5")
    values = [node.get_text(" ", strip=True) for node in left.select("b")]
    if not day_node or len(values) < 2:
        raise ValueError("Post date is incomplete")
    day = int(day_node.get_text(strip=True))
    month_match = re.search(r"(\d+)", values[0])
    year_match = re.search(r"(\d{4})", values[1])
    if not month_match or not year_match:
        raise ValueError(f"Unrecognized post date: {values}")
    return f"{int(year_match.group(1)):04d}-{int(month_match.group(1)):02d}-{day:02d}"


def clean_text(node: Tag | None) -> str:
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True) if node else "").strip()


def parse_post(post: Tag, blog: dict[str, Any], page_url: str) -> dict[str, Any]:
    heading = post.select_one(".right h2 a")
    if not heading:
        raise ValueError("Post has no linked heading")
    permalink = unwrap_wayback_url(str(heading.get("href") or ""), page_url)
    post_id = post_id_from_url(permalink)
    if post_id is None:
        raise ValueError(f"Post heading has no WordPress id: {permalink}")
    tags = [clean_text(tag) for tag in post.select(".tag a, .UTWPrimaryTags a")]
    right = post.select_one(".right")
    lead = ""
    if right:
        for paragraph in right.select("p"):
            candidate = clean_text(paragraph)
            if candidate:
                lead = candidate
                break
    return {
        "id": post_id,
        "archive_id": f"{blog['slug']}-{post_id}",
        "date": parse_date(post),
        "title": clean_text(heading),
        "lead": lead,
        "tags": list(dict.fromkeys(tag for tag in tags if tag)),
        "source_url": permalink,
        "wayback_url": wayback_url(blog["snapshot"], permalink, ""),
        "source_html": str(post),
    }


def discover_one(blog_name: str, args: argparse.Namespace) -> dict[str, Any]:
    blog = BLOGS[blog_name]
    root = archive_root(blog)
    fetcher = Fetcher(args.delay, args.refresh)
    index_path = root / "raw" / "index.html"
    index_meta = root / "raw" / "index.meta.yml"
    index_html = fetcher.capture(blog["index_url"], blog["snapshot"], index_path, index_meta)
    soup = BeautifulSoup(index_html, "html.parser")

    articles: list[dict[str, Any]] = []
    if blog_name == "art":
        for post in soup.select(".post"):
            parsed = parse_post(post, blog, blog["index_url"])
            if args.all or parsed["id"] in blog["sample_ids"]:
                parsed["raw_page"] = index_path.relative_to(REPO_ROOT).as_posix()
                articles.append(parsed)
    else:
        links: dict[int, dict[str, str]] = {}
        for anchor in soup.select('a[href*="?p="]'):
            source_url = unwrap_wayback_url(str(anchor.get("href") or ""), blog["index_url"])
            post_id = post_id_from_url(source_url)
            if post_id is not None:
                links[post_id] = {"source_url": source_url, "title": clean_text(anchor)}
        target_ids = sorted(links, reverse=True) if args.all else blog["sample_ids"]
        for position, post_id in enumerate(target_ids, 1):
            if post_id not in links:
                raise RuntimeError(f"Staff archive index does not contain post {post_id}")
            raw_path = root / "raw" / "posts" / f"{post_id}.html"
            raw_meta = root / "raw" / "posts" / f"{post_id}.meta.yml"
            payload = fetcher.capture(links[post_id]["source_url"], blog["snapshot"], raw_path, raw_meta)
            article_soup = BeautifulSoup(payload, "html.parser")
            post = article_soup.select_one(".post")
            if not post:
                raise RuntimeError(f"Staff post {post_id} has no .post node")
            parsed = parse_post(post, blog, links[post_id]["source_url"])
            parsed["raw_page"] = raw_path.relative_to(REPO_ROOT).as_posix()
            articles.append(parsed)
            if args.all and position % 25 == 0:
                print(f"discover {blog_name}: {position}/{len(target_ids)}")

    articles.sort(key=lambda item: (item["date"], item["id"]))
    manifest = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "mode": "all" if args.all else "samples",
        "blog": {key: value for key, value in blog.items() if key != "sample_ids"},
        "network_requests": fetcher.network_requests,
        "articles": [{key: value for key, value in item.items() if key != "source_html"} for item in articles],
    }
    write_yaml(root / "manifest" / "articles.yml", manifest)
    print(f"discover {blog_name}: {len(articles)} articles, {fetcher.network_requests} requests")
    return manifest


def load_manifest(blog: dict[str, Any]) -> dict[str, Any]:
    path = archive_root(blog) / "manifest" / "articles.yml"
    if not path.exists():
        raise FileNotFoundError(f"Run discover for {blog['slug']} first")
    return load_yaml(path)


def load_article_post(article: dict[str, Any], blog: dict[str, Any]) -> Tag:
    raw_path = REPO_ROOT / article["raw_page"]
    soup = BeautifulSoup(raw_path.read_bytes(), "html.parser")
    matches = []
    for post in soup.select(".post"):
        heading = post.select_one(".right h2 a")
        if heading and post_id_from_url(unwrap_wayback_url(str(heading.get("href") or ""), article["source_url"])) == article["id"]:
            matches.append(post)
    if len(matches) != 1:
        raise RuntimeError(f"Expected one post {article['id']} in {raw_path}, found {len(matches)}")
    return matches[0]


def asset_id(blog: dict[str, Any], url: str) -> str:
    return f"{blog['slug']}-{hashlib.sha1(url.encode('utf-8')).hexdigest()[:12]}"


def unique_asset_name(url: str) -> str:
    name = safe_filename(url)
    stem, suffix = Path(name).stem, Path(name).suffix
    return f"{stem}-{hashlib.sha1(url.encode('utf-8')).hexdigest()[:8]}{suffix}"


def collect_article_assets(post: Tag, blog: dict[str, Any], page_url: str) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}

    def add(url: str, role: str, pair_url: str | None = None) -> None:
        original = unwrap_wayback_url(url, page_url)
        if not is_image_url(original):
            return
        record = records.setdefault(original, {"roles": set(), "pair_url": pair_url})
        record["roles"].add(role)
        if pair_url:
            record["pair_url"] = unwrap_wayback_url(pair_url, page_url)

    for image in post.select(".right img[src]"):
        if image.find_parent(class_="zoom"):
            continue
        source = str(image.get("src") or "")
        parent_link = image.find_parent("a", href=True)
        full_url = str(parent_link.get("href")) if parent_link else None
        if blog["slug"] == "gamefreak-art" and full_url and is_image_url(unwrap_wayback_url(full_url, page_url)):
            add(source, "design-thumbnail", full_url)
            add(full_url, "design-full-resolution", source)
        else:
            add(source, "article-image")
    for link in post.select(".zoom a[href]"):
        full_url = str(link.get("href") or "")
        if is_image_url(unwrap_wayback_url(full_url, page_url)):
            add(full_url, "design-full-resolution")
    return records


def download_asset(
    fetcher: Fetcher,
    blog: dict[str, Any],
    url: str,
    destination: Path,
    roles: Iterable[str],
    article_id: int | None,
    pair_url: str | None = None,
) -> dict[str, Any]:
    meta_path = destination.with_suffix(destination.suffix + ".meta.yml")
    replay = wayback_url(blog["snapshot"], url)
    if destination.exists() and meta_path.exists() and not fetcher.refresh:
        meta = load_yaml(meta_path)
        return {
            "id": asset_id(blog, url),
            "article": article_id,
            "roles": sorted(set(roles)),
            "original_url": url,
            "pair_url": pair_url,
            "local_path": destination.relative_to(REPO_ROOT).as_posix(),
            **meta,
        }
    selected_timestamp = blog["snapshot"]
    capture_source = "internet-archive-fixed-snapshot"
    try:
        response = fetcher.request(replay)
    except RuntimeError:
        response, selected_timestamp = find_cdx_capture(fetcher, url, blog["snapshot"])
        capture_source = "internet-archive-cdx-fallback"
    if "text/html" in (response.headers.get("Content-Type") or "") and is_image_url(url):
        raise RuntimeError(f"Wayback returned HTML for image {url}")
    payload = response.content
    atomic_write(destination, payload)
    width = height = None
    if is_image_url(url):
        try:
            with Image.open(destination) as image:
                width, height = image.size
        except (UnidentifiedImageError, OSError):
            pass
    meta = {
        "captured_at": utc_now(),
        "capture_source": capture_source,
        "wayback_timestamp": selected_timestamp,
        "wayback_url": response.url,
        "status": response.status_code,
        "content_type": response.headers.get("Content-Type"),
        "bytes": len(payload),
        "sha256": sha256_bytes(payload),
        "width": width,
        "height": height,
    }
    write_yaml(meta_path, {"original_url": url, **meta})
    return {
        "id": asset_id(blog, url),
        "article": article_id,
        "roles": sorted(set(roles)),
        "original_url": url,
        "pair_url": pair_url,
        "local_path": destination.relative_to(REPO_ROOT).as_posix(),
        **meta,
    }


def fetch_one(blog_name: str, args: argparse.Namespace) -> dict[str, Any]:
    blog = BLOGS[blog_name]
    root = archive_root(blog)
    manifest = load_manifest(blog)
    fetcher = Fetcher(args.delay, args.refresh)
    assets: dict[str, dict[str, Any]] = {}

    for article in manifest["articles"]:
        post = load_article_post(article, blog)
        discovered = collect_article_assets(post, blog, article["source_url"])
        for url, info in discovered.items():
            destination = root / "assets" / "original" / str(article["id"]) / unique_asset_name(url)
            assets[url] = download_asset(
                fetcher, blog, url, destination, info["roles"], article["id"], info.get("pair_url")
            )

    shared_urls = {
        blog["theme_css"]: {"theme-css"},
        blog["header_asset"]: {"theme-header"},
        blog["background_asset"]: {"theme-background"},
    }
    for url, roles in shared_urls.items():
        destination = root / "assets" / "original" / "shared" / unique_asset_name(url)
        assets[url] = download_asset(fetcher, blog, url, destination, roles, None)

    records = sorted(assets.values(), key=lambda item: (item["article"] or 0, item["original_url"]))
    result = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "network_requests": fetcher.network_requests,
        "assets": records,
    }
    write_yaml(root / "manifest" / "assets.yml", result)
    print(f"fetch {blog_name}: {len(records)} assets, {fetcher.network_requests} requests")
    return result


def inline_markdown(node: Tag | NavigableString, assets: dict[str, dict[str, Any]], page_url: str, blog: dict[str, Any]) -> str:
    parts: list[str] = []

    def walk(current: Tag | NavigableString) -> None:
        if isinstance(current, NavigableString):
            parts.append(re.sub(r"[\t\r\f\v ]+", " ", str(current)))
            return
        if not isinstance(current, Tag):
            return
        if current.name in {"script", "style"} or "zoom" in (current.get("class") or []):
            return
        if current.name == "br":
            parts.append("  \n")
            return
        if current.name == "img":
            source = unwrap_wayback_url(str(current.get("src") or ""), page_url)
            parent = current.find_parent("a", href=True)
            target = unwrap_wayback_url(str(parent.get("href")), page_url) if parent else source
            chosen = target if blog["slug"] == "gamefreak-art" and target in assets and is_image_url(target) else source
            record = assets.get(chosen)
            if record:
                alt = str(current.get("alt") or "").replace('"', "'")
                parts.append(f'{{% legacy_image id="{record["id"]}" alt="{alt}" %}}')
            return
        if current.name == "a":
            image = current.find("img")
            if image:
                walk(image)
                return
            label = clean_text(current)
            href = unwrap_wayback_url(str(current.get("href") or ""), page_url)
            parts.append(f"[{label}]({href})" if label else "")
            return
        if current.name in {"strong", "b"}:
            inner = "".join(inline_markdown(child, assets, page_url, blog) for child in current.children)
            parts.append(f"**{inner.strip()}**")
            return
        for child in current.children:
            walk(child)

    walk(node)
    return re.sub(r" *\n *", "\n", "".join(parts)).strip()


def extract_one(blog_name: str, args: argparse.Namespace) -> dict[str, Any]:
    blog = BLOGS[blog_name]
    root = archive_root(blog)
    manifest = load_manifest(blog)
    asset_manifest = load_yaml(root / "manifest" / "assets.yml")
    assets = {item["original_url"]: item for item in asset_manifest.get("assets", [])}

    for article in manifest["articles"]:
        post = load_article_post(article, blog)
        right = post.select_one(".right")
        if not right:
            raise RuntimeError(f"Post {article['id']} has no content column")
        heading = right.select_one("h2")
        if heading:
            heading.decompose()
        for tag in right.select(".tag"):
            tag.decompose()
        blocks: list[dict[str, Any]] = []
        markdown_parts: list[str] = []
        for child in list(right.children):
            if isinstance(child, NavigableString) and not child.strip():
                continue
            markdown = inline_markdown(child, assets, article["source_url"], blog)
            if not markdown:
                continue
            image_ids = re.findall(r'legacy_image id="([^"]+)"', markdown)
            blocks.append({"type": child.name if isinstance(child, Tag) else "text", "markdown": markdown, "images": image_ids})
            markdown_parts.append(markdown)
        article_dir = root / "content" / str(article["id"])
        front = {
            "article_id": article["archive_id"],
            "post_id": article["id"],
            "lang": "ja",
            "date": article["date"],
            "title": article["title"],
            "source": article["source_url"],
            "status": "source-extracted",
        }
        write_text(
            article_dir / "ja.md",
            "---\n" + yaml.safe_dump(front, allow_unicode=True, sort_keys=False).strip() + "\n---\n\n" + "\n\n".join(markdown_parts).strip() + "\n",
        )
        write_text(article_dir / "source.html", str(post))
        write_text(article_dir / "structure.ja.json", json.dumps({"schema_version": 1, "blocks": blocks}, ensure_ascii=False, indent=2) + "\n")
        article_assets = [item for item in asset_manifest.get("assets", []) if item.get("article") == article["id"]]
        write_yaml(
            article_dir / "metadata.yml",
            {
                "article_id": article["archive_id"],
                "post_id": article["id"],
                "date": article["date"],
                "title": article["title"],
                "tags": article.get("tags", []),
                "author": {"name_ja": blog["author_ja"], "name_zh": blog["author_zh"]},
                "series": {"name_ja": blog["title_ja"], "name_zh": blog["title_zh"]},
                "source": {"url": article["source_url"], "wayback_url": article["wayback_url"], "raw_page": article["raw_page"]},
                "assets": [{key: item.get(key) for key in ("id", "roles", "original_url", "pair_url", "local_path", "sha256", "width", "height", "wayback_url")} for item in article_assets],
                "rights": {"archive_type": "unofficial", "original_copyright": "GAME FREAK inc."},
                "extracted_at": utc_now(),
            },
        )
        translation = root / "translations" / "zh-CN" / f"{article['id']}.md"
        if not translation.exists():
            translation_front = {
                "article_id": article["archive_id"],
                "post_id": article["id"],
                "lang": "zh-CN",
                "source_language": "ja",
                "translation_status": "missing",
                "translation_title": "",
                "translation_summary": "",
                "translator": None,
                "reviewer": None,
            }
            write_text(translation, "---\n" + yaml.safe_dump(translation_front, allow_unicode=True, sort_keys=False).strip() + "\n---\n\n<!-- 中文翻译待完成；请保留段落、换行和图片标记。 -->\n")
    print(f"extract {blog_name}: {len(manifest['articles'])} Japanese documents")
    return {"articles": len(manifest["articles"])}


def content_parts(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    return (yaml.safe_load(parts[1]) or {}, parts[2].lstrip()) if len(parts) == 3 else ({}, text)


def publish_one(blog_name: str, args: argparse.Namespace) -> dict[str, Any]:
    blog = BLOGS[blog_name]
    root = archive_root(blog)
    manifest = load_manifest(blog)
    asset_manifest = load_yaml(root / "manifest" / "assets.yml")
    asset_by_id = {item["id"]: item for item in asset_manifest.get("assets", [])}
    public_root = REPO_ROOT / "assets" / "images" / "gamefreak-legacy" / blog_name

    for item in asset_manifest.get("assets", []):
        source = REPO_ROOT / item["local_path"]
        if not source.exists() or source.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        if item.get("article") is None and "theme-header" in item.get("roles", []):
            relative = Path("shared") / f"header{source.suffix.lower()}"
        elif item.get("article") is None and "theme-background" in item.get("roles", []):
            relative = Path("shared") / f"background{source.suffix.lower()}"
        else:
            relative = Path("shared") / source.name if item.get("article") is None else Path(str(item["article"])) / source.name
        destination = public_root / relative
        if not destination.exists() or sha256_file(destination) != item["sha256"]:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)

    def render(body: str) -> str:
        def replace(match: re.Match[str]) -> str:
            item = asset_by_id.get(match.group(1))
            if not item:
                return ""
            source = Path(item["local_path"])
            relative = Path("shared") / source.name if item.get("article") is None else Path(str(item["article"])) / source.name
            url = f"/assets/images/gamefreak-legacy/{blog_name}/{relative.as_posix()}"
            alt = match.group(2)
            role_class = " gf-legacy-full-art" if "design-full-resolution" in item.get("roles", []) else ""
            return f'<figure class="gf-legacy-image{role_class}"><a href="{url}" target="_blank"><img src="{url}" alt="{alt}" loading="lazy"></a></figure>'
        return re.sub(r'\{%\s*legacy_image\s+id="([^"]+)"\s+alt="([^"]*)"\s*%\}', replace, body).strip()

    for article in manifest["articles"]:
        ja_meta, ja_body = content_parts(root / "content" / str(article["id"]) / "ja.md")
        translation_path = root / "translations" / "zh-CN" / f"{article['id']}.md"
        zh_meta, zh_body = content_parts(translation_path)
        has_translation = zh_meta.get("translation_status") not in {None, "missing"} and zh_body.strip() and "中文翻译待完成" not in zh_body
        post_front = {
            "layout": "gamefreak-legacy-blog",
            "title": zh_meta.get("translation_title") or article["title"],
            "date": article["date"],
            "permalink": f"/{blog['slug']}/entry-{article['id']}/",
            "categories": ["官方博客", "Game Freak", "数字存档"],
            "tags": ["Game Freak", blog["author_zh"], *article.get("tags", [])],
            "archive_type": "gamefreak_legacy_blog",
            "gf_legacy_blog": blog_name,
            "gf_legacy_post_id": article["id"],
            "gf_entry_title": zh_meta.get("translation_title") or article["title"],
            "gf_original_title": article["title"],
            "gf_translation_title": zh_meta.get("translation_title") or "",
            "translation_available": has_translation,
            "summary": zh_meta.get("translation_summary") or article.get("lead") or article["title"],
            "translation_status": zh_meta.get("translation_status", "missing"),
            "search": True,
            "source": {"title": f"{blog['title_ja']} · {article['title']}", "url": article["source_url"], "archive_url": article["wayback_url"], "source_type": "official_blog_wayback"},
        }
        content = (
            "---\n" + yaml.safe_dump(post_front, allow_unicode=True, sort_keys=False).strip() + "\n---\n\n"
            + (f'<div data-gf-language-panel="zh-CN">\n{render(zh_body)}\n</div>\n\n' if has_translation else "")
            + f'<div data-gf-language-panel="ja"{(" hidden" if has_translation else "")}>\n{render(ja_body)}\n</div>\n'
        )
        filename = f"{article['date']}-{blog['slug']}-{article['id']}.md"
        write_text(REPO_ROOT / "_posts" / filename, content)

    page_count = (len(manifest["articles"]) + blog["posts_per_page"] - 1) // blog["posts_per_page"]
    for page_number in range(2, page_count + 1):
        page_front = {
            "layout": "gamefreak-legacy-blog",
            "title": f"{blog['title_ja']} · {page_number}",
            "permalink": f"/{blog['slug']}/page/{page_number}/",
            "gf_mode": "index",
            "gf_blog": blog_name,
            "gf_archive_page": page_number,
            "search": False,
        }
        page_content = "---\n" + yaml.safe_dump(page_front, allow_unicode=True, sort_keys=False).strip() + "\n---\n"
        write_text(REPO_ROOT / "_pages" / f"{blog['slug']}-page-{page_number:02d}.md", page_content)
    print(f"publish {blog_name}: {len(manifest['articles'])} Jekyll posts")
    return {"articles": len(manifest["articles"])}


def validate_one(blog_name: str, args: argparse.Namespace) -> dict[str, Any]:
    blog = BLOGS[blog_name]
    root = archive_root(blog)
    manifest = load_manifest(blog)
    assets_path = root / "manifest" / "assets.yml"
    errors: list[str] = []
    warnings: list[str] = []
    if not assets_path.exists():
        errors.append("asset manifest is missing")
        assets = []
    else:
        assets = load_yaml(assets_path).get("assets", [])
    for article in manifest["articles"]:
        for required in (
            root / "content" / str(article["id"]) / "ja.md",
            root / "content" / str(article["id"]) / "metadata.yml",
            root / "translations" / "zh-CN" / f"{article['id']}.md",
        ):
            if not required.exists():
                errors.append(f"missing {required.relative_to(REPO_ROOT)}")
    for asset in assets:
        path = REPO_ROOT / asset["local_path"]
        if not path.exists():
            errors.append(f"missing asset {asset['local_path']}")
        elif sha256_file(path) != asset.get("sha256"):
            errors.append(f"checksum mismatch {asset['local_path']}")
    full: list[dict[str, Any]] = []
    thumbnails: list[dict[str, Any]] = []
    if blog_name == "art":
        full = [item for item in assets if "design-full-resolution" in item.get("roles", [])]
        thumbnails = [item for item in assets if "design-thumbnail" in item.get("roles", [])]
        if not full:
            errors.append("no full-resolution ZOOM artwork was archived")
        if len(full) < len(thumbnails):
            errors.append(f"ZOOM coverage incomplete: {len(full)} full images for {len(thumbnails)} thumbnails")
    if manifest.get("mode") == "all" and len(manifest["articles"]) != blog["expected_count"]:
        errors.append(f"expected {blog['expected_count']} articles, found {len(manifest['articles'])}")
    result = {
        "generated_at": utc_now(),
        "blog": blog_name,
        "articles": len(manifest["articles"]),
        "assets": len(assets),
        "full_resolution_artworks": len(full),
        "artwork_thumbnails": len(thumbnails),
        "errors": errors,
        "warnings": warnings,
        "status": "PASS" if not errors else "FAIL",
    }
    write_yaml(root / "reports" / "validation.yml", result)
    print(f"validate {blog_name}: {result['status']} — {len(errors)} errors, {len(warnings)} warnings")
    if args.strict and errors:
        raise SystemExit(1)
    return result


def selected_blogs(value: str) -> list[str]:
    return list(BLOGS) if value == "both" else [value]


def run_stage(stage: str, blog_name: str, args: argparse.Namespace) -> None:
    stages = {
        "discover": discover_one,
        "fetch": fetch_one,
        "extract": extract_one,
        "publish": publish_one,
        "validate": validate_one,
    }
    if stage == "all":
        for name in ("discover", "fetch", "extract", "publish", "validate"):
            stages[name](blog_name, args)
    else:
        stages[stage](blog_name, args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["discover", "fetch", "extract", "publish", "validate", "all"])
    parser.add_argument("--blog", choices=["art", "staff", "both"], default="both")
    parser.add_argument("--all", action="store_true", help="Process the complete archive instead of samples")
    parser.add_argument("--refresh", action="store_true", help="Refetch existing raw captures and assets")
    parser.add_argument("--delay", type=float, default=0.45, help="Delay after network requests")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on validation errors")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    for blog_name in selected_blogs(args.blog):
        run_stage(args.stage, blog_name, args)


if __name__ == "__main__":
    main()
