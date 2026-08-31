#!/usr/bin/env python3
"""Archive Junichi Masuda's former LINE BLOG from Internet Archive.

The workflow mirrors the existing GAME FREAK blog preservation tools:

    raw -> assets -> content -> translations -> Jekyll posts

The default run processes three representative articles. Use ``--all`` to
discover all numeric article URLs recorded by the Wayback CDX index.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import html
import json
import mimetypes
import re
import shutil
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup, NavigableString, Tag
from PIL import Image, ImageOps, UnidentifiedImageError


REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = REPO_ROOT / "archive" / "gamefreak-lineblog"
SAMPLE_FILE = REPO_ROOT / "tools" / "gamefreak-lineblog-samples.yml"
ROOT_URL = "https://lineblog.me/masudajunichi/"
SNAPSHOT = "20180603171931"
EXPECTED_COUNT = 251
IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif", "image/webp": ".webp"}
USER_AGENT = "PokeAmice-Digital-Archive/0.3 (+https://docs.pokeamice.com/gamefreak-director/)"
PUBLIC_IMAGE_LONG_EDGE = 1600
PUBLIC_IMAGE_WEBP_QUALITY = 80


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


def write_text(path: Path, value: str) -> None:
    atomic_write(path, value.encode("utf-8"))


def write_yaml(path: Path, value: Any) -> None:
    write_text(path, yaml.safe_dump(value, allow_unicode=True, sort_keys=False))


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def wayback_url(timestamp: str, original_url: str, modifier: str = "id_") -> str:
    return f"https://web.archive.org/web/{timestamp}{modifier}/{original_url}"


def unwrap_wayback_url(value: str, base_url: str) -> str:
    resolved = urljoin(base_url, value)
    match = re.match(r"https?://web\.archive\.org/web/\d+(?:[a-z_]+)?/(https?://.*)", resolved)
    return match.group(1) if match else resolved


def canonical_source_url(value: str) -> str:
    parsed = urlparse(value)
    host = parsed.hostname or ""
    scheme = "https" if host in {"lineblog.me", "obs.line-scdn.net", "line.blogimg.jp"} else (parsed.scheme or "https")
    port = f":{parsed.port}" if parsed.port and parsed.port not in {80, 443} else ""
    return parsed._replace(scheme=scheme, netloc=f"{host}{port}", fragment="").geturl()


def article_id_from_url(value: str) -> int | None:
    match = re.search(r"/archives/(\d+)\.html(?:[?#].*)?$", value)
    return int(match.group(1)) if match else None


def parse_datetime(value: str) -> str:
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", value)
    if not match:
        raise ValueError(f"Unrecognized LINE BLOG date: {value}")
    return "-".join(match.groups())


def extension_for(response: requests.Response, original_url: str) -> str:
    content_type = response.headers.get("Content-Type", "").split(";", 1)[0].lower()
    if content_type in IMAGE_TYPES:
        return IMAGE_TYPES[content_type]
    suffix = Path(unquote(urlparse(original_url).path)).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    guessed = mimetypes.guess_extension(content_type) or ".bin"
    return ".jpg" if guessed == ".jpe" else guessed


@dataclass
class Fetcher:
    delay: float = 0.45
    refresh: bool = False

    def __post_init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "ja,en;q=0.8"})
        self.network_requests = 0

    def request(self, url: str) -> requests.Response:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=60, allow_redirects=True)
                response.raise_for_status()
                self.network_requests += 1
                if self.delay:
                    time.sleep(self.delay)
                return response
            except requests.RequestException as exc:
                last_error = exc
                response = getattr(exc, "response", None)
                if response is not None and 400 <= response.status_code < 500 and response.status_code not in {408, 429}:
                    break
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"Failed to fetch {url}: {last_error}")

    def cdx(self, original_url: str) -> list[list[str]]:
        response = self.request(
            "https://web.archive.org/cdx/search/cdx?"
            f"url={quote(original_url, safe='')}&output=json&filter=statuscode:200&"
            "filter=mimetype:text/html&fl=timestamp,original,digest&collapse=digest"
        )
        rows = response.json()
        return rows[1:] if rows else []

    def closest_timestamp(self, original_url: str, preferred: str) -> str:
        rows = self.cdx(original_url)
        timestamps = [str(row[0]) for row in rows if row and str(row[0]).isdigit()]
        if not timestamps:
            raise RuntimeError(f"No Wayback capture available for {original_url}")
        preferred_number = int(preferred[:14])
        return min(timestamps, key=lambda item: abs(int(item[:14]) - preferred_number))

    def archived_response(self, original_url: str, timestamp: str, modifier: str = "id_") -> tuple[requests.Response, str]:
        replay = wayback_url(timestamp, original_url, modifier)
        try:
            return self.request(replay), timestamp
        except RuntimeError:
            closest = self.closest_timestamp(original_url, timestamp)
            return self.request(wayback_url(closest, original_url, modifier)), closest

    def capture_page(self, article: dict[str, Any]) -> bytes:
        body = ARCHIVE_ROOT / article["raw_page"]
        meta = body.with_suffix(".response.yml")
        if body.exists() and meta.exists() and not self.refresh:
            return body.read_bytes()
        response, timestamp = self.archived_response(article["source_url"], article["timestamp"])
        atomic_write(body, response.content)
        write_yaml(meta, {
            "original_url": article["source_url"],
            "requested_replay_url": wayback_url(article["timestamp"], article["source_url"]),
            "actual_replay_url": response.url,
            "timestamp": timestamp,
            "captured_at": utc_now(),
            "status": response.status_code,
            "content_type": response.headers.get("Content-Type"),
            "bytes": len(response.content),
            "sha256": sha256_bytes(response.content),
        })
        return response.content


def discover(args: argparse.Namespace) -> dict[str, Any]:
    if args.all:
        fetcher = Fetcher(delay=args.delay, refresh=args.refresh)
        query = (
            "https://web.archive.org/cdx/search/cdx?"
            "url=lineblog.me%2Fmasudajunichi%2F*&output=json&filter=statuscode:200&"
            "filter=mimetype:text%2Fhtml&fl=timestamp,original,digest&collapse=urlkey&from=2016&to=2023"
        )
        rows = fetcher.request(query).json()
        candidates: dict[int, list[dict[str, str]]] = {}
        for row in rows[1:]:
            if len(row) < 2:
                continue
            post_id = article_id_from_url(str(row[1]))
            if post_id is None:
                continue
            candidates.setdefault(post_id, []).append({"timestamp": str(row[0]), "url": canonical_source_url(str(row[1]))})
        articles: list[dict[str, Any]] = []
        for post_id, captures in candidates.items():
            chosen = min(captures, key=lambda item: abs(int(item["timestamp"][:14]) - int(SNAPSHOT)))
            articles.append({
                "archive_id": f"masuda-line-{post_id}", "id": post_id, "date": None, "title": None,
                "source_url": chosen["url"], "timestamp": chosen["timestamp"],
                "raw_page": f"raw/articles/{post_id}.html",
            })
        articles.sort(key=lambda item: item["id"])
        mode = "all"
    else:
        source = load_yaml(SAMPLE_FILE)
        articles = [{
            "archive_id": f"masuda-line-{item['id']}", "id": int(item["id"]),
            "date": item.get("date"), "title": item.get("title"),
            "source_url": canonical_source_url(item["url"]), "timestamp": str(item["timestamp"]),
            "role": item.get("role"), "raw_page": f"raw/articles/{item['id']}.html",
        } for item in source["articles"]]
        mode = "sample"
    manifest = {
        "schema_version": 1, "series": "増田順一 公式ブログ", "platform": "LINE BLOG",
        "source_url": ROOT_URL, "snapshot": SNAPSHOT, "mode": mode,
        "expected_count": EXPECTED_COUNT, "discovered_at": utc_now(), "articles": articles,
    }
    write_yaml(ARCHIVE_ROOT / "manifest" / "articles.yml", manifest)
    print(f"discover: {len(articles)} LINE BLOG article URL(s) ({mode})")
    return manifest


def load_manifest() -> dict[str, Any]:
    path = ARCHIVE_ROOT / "manifest" / "articles.yml"
    if not path.exists():
        raise RuntimeError("Article manifest missing; run discover first")
    return load_yaml(path)


def article_body(page: bytes) -> Tag:
    soup = BeautifulSoup(page, "html.parser")
    body = soup.select_one(".article-body-inner")
    if not body:
        raise ValueError("LINE BLOG page has no .article-body-inner")
    return body


def source_image_url(image: Tag, page_url: str) -> tuple[str, str]:
    shown = canonical_source_url(unwrap_wayback_url(str(image.get("src") or ""), page_url))
    parent = image.find_parent("a", href=True)
    full = canonical_source_url(unwrap_wayback_url(str(parent.get("href")), page_url)) if parent else shown
    if urlparse(full).hostname not in {"obs.line-scdn.net", "line.blogimg.jp"}:
        full = shown
    return shown, full


def collect_assets(page: bytes, article: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for image in article_body(page).select("img[src]"):
        shown, full = source_image_url(image, article["source_url"])
        key = full
        record = result.setdefault(key, {
            "original_url": full, "display_url": shown, "roles": set(),
            "alt": str(image.get("alt") or ""), "article": article["id"],
        })
        record["roles"].add("article-image")
        if full != shown:
            record["roles"].add("full-resolution")
    return result


def fetch_asset(fetcher: Fetcher, article: dict[str, Any], record: dict[str, Any], index: int) -> dict[str, Any]:
    asset_id = f"line-{article['id']}-{index:03d}"
    existing = next((path for path in (ARCHIVE_ROOT / "assets" / str(article["id"])).glob(f"{index:03d}-*.*")), None)
    meta_path = ARCHIVE_ROOT / "assets" / str(article["id"]) / f"{index:03d}.response.yml"
    if existing and meta_path.exists() and not fetcher.refresh:
        meta = load_yaml(meta_path)
        return {**record, **meta.get("asset", {}), "id": asset_id, "local_path": existing.relative_to(REPO_ROOT).as_posix()}
    response: requests.Response | None = None
    method = "live-source"
    capture_timestamp = article["timestamp"]
    try:
        response = fetcher.request(record["original_url"])
        if not response.headers.get("Content-Type", "").lower().startswith("image/"):
            raise RuntimeError("source did not return an image")
    except RuntimeError:
        method = "wayback"
        response, capture_timestamp = fetcher.archived_response(record["original_url"], article["timestamp"], "id_")
    extension = extension_for(response, record["original_url"])
    filename = f"{index:03d}-{sha256_bytes(record['original_url'].encode('utf-8'))[:10]}{extension}"
    path = ARCHIVE_ROOT / "assets" / str(article["id"]) / filename
    atomic_write(path, response.content)
    width = height = None
    try:
        with Image.open(path) as image:
            width, height = image.size
    except (UnidentifiedImageError, OSError):
        pass
    item = {
        **record, "id": asset_id, "roles": sorted(record["roles"]),
        "local_path": path.relative_to(REPO_ROOT).as_posix(), "content_type": response.headers.get("Content-Type"),
        "bytes": len(response.content), "sha256": sha256_bytes(response.content), "width": width, "height": height,
        "retrieval_method": method, "timestamp": capture_timestamp,
        "wayback_url": wayback_url(capture_timestamp, record["original_url"], "id_"),
    }
    write_yaml(meta_path, {"captured_at": utc_now(), "asset": item})
    return item


def capture(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_manifest()
    selected = selected_articles(manifest, args)
    selected_ids = {article["id"] for article in selected}
    existing_manifest = ARCHIVE_ROOT / "manifest" / "assets.yml"
    existing_assets = load_yaml(existing_manifest).get("assets", []) if existing_manifest.exists() else []
    assets: list[dict[str, Any]] = [item for item in existing_assets if item.get("article") not in selected_ids]

    def capture_one(article: dict[str, Any]) -> tuple[int, list[dict[str, Any]]]:
        # requests.Session is not shared across threads.  Article and asset
        # cache paths are disjoint, so every worker can write atomically.
        fetcher = Fetcher(delay=args.delay, refresh=args.refresh)
        page = fetcher.capture_page(article)
        records = collect_assets(page, article)
        article_assets: list[dict[str, Any]] = []
        for index, record in enumerate(records.values(), start=1):
            try:
                article_assets.append(fetch_asset(fetcher, article, record, index))
            except RuntimeError as exc:
                article_assets.append({**record, "id": f"line-{article['id']}-{index:03d}", "roles": sorted(record["roles"]), "status": "missing", "error": str(exc)})
        return article["id"], article_assets

    captured_by_article: dict[int, list[dict[str, Any]]] = {}
    capture_failures: list[dict[str, Any]] = []
    workers = max(1, min(int(getattr(args, "workers", 1)), 8))
    if workers == 1:
        for index, article in enumerate(selected, start=1):
            try:
                article_id, article_assets = capture_one(article)
                captured_by_article[article_id] = article_assets
                print(f"capture [{index}/{len(selected)}] {article_id}: {len(article_assets)} image(s)", flush=True)
            except Exception as exc:
                capture_failures.append({"article": article["id"], "error": str(exc)})
                print(f"capture [{index}/{len(selected)}] {article['id']}: FAILED — {exc}", flush=True)
    else:
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="lineblog-capture") as executor:
            futures = {executor.submit(capture_one, article): article for article in selected}
            for index, future in enumerate(as_completed(futures), start=1):
                article = futures[future]
                try:
                    article_id, article_assets = future.result()
                    captured_by_article[article_id] = article_assets
                    print(f"capture [{index}/{len(selected)}] {article_id}: {len(article_assets)} image(s)", flush=True)
                except Exception as exc:
                    capture_failures.append({"article": article["id"], "error": str(exc)})
                    print(f"capture [{index}/{len(selected)}] {article['id']}: FAILED — {exc}", flush=True)

    for article in selected:
        assets.extend(captured_by_article.get(article["id"], []))
    write_yaml(ARCHIVE_ROOT / "manifest" / "assets.yml", {
        "generated_at": utc_now(), "assets": assets, "capture_failures": capture_failures,
    })
    print(
        f"capture: {len(selected)} pages, {len(assets)} image record(s), "
        f"{len(capture_failures)} page failure(s) in manifest"
    )
    return {"articles": len(selected), "assets": len(assets), "failures": capture_failures}


def inline_html(node: Tag | NavigableString, assets: dict[str, dict[str, Any]], page_url: str) -> str:
    if isinstance(node, NavigableString):
        return html.escape(str(node).replace("\xa0", " "), quote=False)
    if node.name == "br":
        return "<br>\n"
    if node.name == "img":
        _shown, full = source_image_url(node, page_url)
        item = assets.get(full)
        alt = html.escape(str(node.get("alt") or "").replace('"', "'"), quote=False)
        return f'{{% lineblog_image id="{item["id"]}" alt="{alt}" %}}' if item and item.get("status") != "missing" else ""
    if node.name == "a":
        image = node.find("img")
        if image:
            return inline_html(image, assets, page_url)
        inner = "".join(inline_html(child, assets, page_url) for child in node.children).strip()
        href = unwrap_wayback_url(str(node.get("href") or ""), page_url)
        safe_href = html.escape(href, quote=True)
        return f'<a class="gf-lineblog-source-link" href="{safe_href}" target="_blank" rel="noopener">{inner}</a>' if inner else ""
    inner = "".join(inline_html(child, assets, page_url) for child in node.children)
    if node.name in {"strong", "b"}:
        return f"<strong>{inner.strip()}</strong>"
    if node.name in {"em", "i"}:
        return f"<em>{inner.strip()}</em>"
    return inner


def extract_article(page: bytes, article: dict[str, Any], assets: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], str, list[dict[str, Any]]]:
    soup = BeautifulSoup(page, "html.parser")
    title_node = soup.select_one(".article-title")
    time_node = soup.select_one(".article-date time[datetime]")
    body = soup.select_one(".article-body-inner")
    if not title_node or not time_node or not body:
        raise ValueError(f"Incomplete LINE BLOG article {article['id']}")
    title = title_node.get_text(" ", strip=True)
    date = parse_datetime(str(time_node.get("datetime") or time_node.get_text(strip=True)))
    categories = list(dict.fromkeys(node.get_text(" ", strip=True) for node in soup.select(".article-category dd a") if node.get_text(strip=True)))
    tags = list(dict.fromkeys(node.get_text(" ", strip=True) for node in soup.select(".article-tags dd a") if node.get_text(strip=True)))
    blocks: list[dict[str, Any]] = []
    markdown: list[str] = []
    for child in body.children:
        if isinstance(child, NavigableString) and not child.strip():
            continue
        if isinstance(child, Tag) and child.get("id") in {"ad2", "ad1"}:
            continue
        rendered = inline_html(child, assets, article["source_url"]).strip()
        if not rendered:
            continue
        alignment = ""
        if isinstance(child, Tag):
            style = str(child.get("style") or "")
            match = re.search(r"text-align\s*:\s*(center|right|left)", style, re.I)
            alignment = match.group(1).lower() if match else ""
        if alignment:
            rendered = f'<div class="gf-lineblog-line gf-lineblog-line--{alignment}">{rendered}</div>'
        images = re.findall(r'lineblog_image id="([^"]+)"', rendered)
        blocks.append({"type": child.name if isinstance(child, Tag) else "text", "alignment": alignment or None, "markdown": rendered, "images": images})
        markdown.append(rendered)
    metadata = {"title": title, "date": date, "categories": categories, "tags": tags}
    return metadata, "\n".join(markdown).strip(), blocks


def extract(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_manifest()
    asset_path = ARCHIVE_ROOT / "manifest" / "assets.yml"
    all_assets = load_yaml(asset_path).get("assets", []) if asset_path.exists() else []
    extracted = 0
    for article in selected_articles(manifest, args):
        raw_path = ARCHIVE_ROOT / article["raw_page"]
        if not raw_path.exists():
            raise RuntimeError(f"Missing raw page for {article['id']}; run capture first")
        article_assets = {item["original_url"]: item for item in all_assets if item.get("article") == article["id"]}
        metadata, body, blocks = extract_article(raw_path.read_bytes(), article, article_assets)
        article.update({"date": metadata["date"], "title": metadata["title"], "categories": metadata["categories"], "tags": metadata["tags"]})
        root = ARCHIVE_ROOT / "content" / str(article["id"])
        front = {
            "article_id": article["archive_id"], "post_id": article["id"], "lang": "ja",
            "date": metadata["date"], "title": metadata["title"], "categories": metadata["categories"],
            "tags": metadata["tags"], "source": article["source_url"], "status": "source-extracted",
        }
        write_text(root / "ja.md", "---\n" + yaml.safe_dump(front, allow_unicode=True, sort_keys=False).strip() + "\n---\n\n" + body + "\n")
        write_text(root / "structure.ja.json", json.dumps({"schema_version": 1, "blocks": blocks}, ensure_ascii=False, indent=2) + "\n")
        write_yaml(root / "metadata.yml", {
            **front,
            "author": {"name_ja": "増田順一", "name_zh": "增田顺一"},
            "series": {"name_ja": "増田順一 公式ブログ", "name_zh": "增田顺一 LINE BLOG"},
            "source_record": {"url": article["source_url"], "wayback_url": wayback_url(article["timestamp"], article["source_url"]), "raw_page": article["raw_page"]},
            "assets": [{key: item.get(key) for key in ("id", "roles", "original_url", "display_url", "local_path", "sha256", "width", "height", "wayback_url", "retrieval_method")} for item in article_assets.values()],
            "rights": {"archive_type": "unofficial", "original_rights": "Original text and images remain with their respective rights holders; LINE BLOG was operated by LINE."},
            "extracted_at": utc_now(),
        })
        translation = ARCHIVE_ROOT / "translations" / "zh-CN" / f"{article['id']}.md"
        if not translation.exists():
            translation_front = {
                "article_id": article["archive_id"], "post_id": article["id"], "lang": "zh-CN",
                "source_language": "ja", "translation_status": "missing", "translation_title": "",
                "translation_summary": "", "translator": None, "reviewer": None,
            }
            write_text(translation, "---\n" + yaml.safe_dump(translation_front, allow_unicode=True, sort_keys=False).strip() + "\n---\n\n<!-- 中文翻译待完成；请保留每一行、空行和图片标记。 -->\n")
        extracted += 1
    write_yaml(ARCHIVE_ROOT / "manifest" / "articles.yml", manifest)
    print(f"extract: {extracted} Japanese LINE BLOG document(s)")
    return {"articles": extracted}


def markdown_parts(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    return (yaml.safe_load(parts[1]) or {}, parts[2].lstrip()) if len(parts) == 3 else ({}, text)


def publish_image(source: Path, destination_dir: Path) -> tuple[Path, int, int, bool]:
    """Create a compact public copy while keeping the source archive untouched."""
    with Image.open(source) as opened:
        width, height = opened.size
        if source.suffix.lower() == ".gif" and getattr(opened, "is_animated", False):
            destination = destination_dir / source.name
            if not destination.exists() or sha256_file(destination) != sha256_file(source):
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
                return destination, width, height, True
            return destination, width, height, False

        destination = destination_dir / f"{source.stem}.webp"
        if destination.exists():
            try:
                with Image.open(destination) as public_image:
                    public_image.verify()
                with Image.open(destination) as public_image:
                    public_width, public_height = public_image.size
                return destination, public_width, public_height, False
            except (OSError, UnidentifiedImageError):
                pass

        image = ImageOps.exif_transpose(opened)
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        image.thumbnail((PUBLIC_IMAGE_LONG_EDGE, PUBLIC_IMAGE_LONG_EDGE), Image.Resampling.LANCZOS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        image.save(temporary, format="WEBP", quality=PUBLIC_IMAGE_WEBP_QUALITY, method=4)
        temporary.replace(destination)
        return destination, image.width, image.height, True


def publish(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_manifest()
    asset_path = ARCHIVE_ROOT / "manifest" / "assets.yml"
    all_assets = load_yaml(asset_path).get("assets", []) if asset_path.exists() else []
    asset_by_id = {item["id"]: item for item in all_assets if item.get("local_path")}
    public_root = REPO_ROOT / "assets" / "images" / "gamefreak-lineblog"
    copied = 0
    public_assets: dict[str, tuple[Path, int, int]] = {}
    def prepare(item: dict[str, Any]) -> tuple[str, Path, int, int, bool]:
        source = REPO_ROOT / item["local_path"]
        destination, width, height, changed = publish_image(source, public_root / str(item["article"]))
        return item["id"], destination, width, height, changed

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(prepare, item) for item in asset_by_id.values()]
        for future in as_completed(futures):
            asset_id, destination, width, height, changed = future.result()
            public_assets[asset_id] = (destination, width, height)
            if changed:
                copied += 1

    def render(body: str) -> str:
        def replace(match: re.Match[str]) -> str:
            item = asset_by_id.get(match.group(1))
            if not item:
                return ""
            destination, width, height = public_assets[item["id"]]
            url = "/" + destination.relative_to(REPO_ROOT).as_posix()
            alt = match.group(2)
            dimensions = f' width="{width}" height="{height}"'
            return f'<figure class="gf-lineblog-image"><a href="{url}" target="_blank" rel="noopener"><img src="{url}" alt="{alt}" loading="lazy"{dimensions}></a></figure>'
        return re.sub(r'\{%\s*lineblog_image\s+id="([^"]+)"\s+alt="([^"]*)"\s*%\}', replace, body).strip()

    generated = 0
    for article in selected_articles(manifest, args):
        source_path = ARCHIVE_ROOT / "content" / str(article["id"]) / "ja.md"
        if not source_path.exists():
            continue
        ja_meta, ja_body = markdown_parts(source_path)
        translation_path = ARCHIVE_ROOT / "translations" / "zh-CN" / f"{article['id']}.md"
        zh_meta, zh_body = markdown_parts(translation_path) if translation_path.exists() else ({}, "")
        has_translation = zh_meta.get("translation_status") not in {None, "", "missing"} and "中文翻译待完成" not in zh_body
        display_title = zh_meta.get("translation_title") or ja_meta.get("title") or article["title"]
        summary = zh_meta.get("translation_summary") or f"增田顺一在 LINE BLOG 发布的日记《{ja_meta.get('title') or article['title']}》。"
        tags = list(dict.fromkeys(["Game Freak", "增田顺一", "LINE BLOG", *(ja_meta.get("categories") or []), *(ja_meta.get("tags") or [])]))
        front = {
            "layout": "gamefreak-director", "title": display_title, "date": ja_meta["date"],
            "permalink": f"/gamefreak-director/lineblog-{article['id']}/",
            "categories": ["官方博客", "Game Freak", "数字存档"], "tags": tags,
            "archive_type": "gamefreak_masuda_lineblog", "gf_series": "lineblog", "gf_lineblog_id": article["id"],
            "gf_entry_title": display_title, "gf_original_title": ja_meta["title"], "gf_archive": ja_meta["date"][:7],
            "gf_categories": ja_meta.get("categories") or [], "gf_source_tags": ja_meta.get("tags") or [],
            "gf_translation_title": zh_meta.get("translation_title") or "", "translation_available": has_translation,
            "translation_status": zh_meta.get("translation_status", "missing"), "summary": summary, "description": summary, "search": True,
            "source": {"title": f"増田順一 公式ブログ · {ja_meta['title']}", "url": article["source_url"], "archive_url": wayback_url(article["timestamp"], article["source_url"]), "source_type": "official_blog_wayback"},
            "entities": {"people": ["增田顺一"], "organizations": ["Game Freak", "LINE BLOG"]},
        }
        body = []
        if has_translation:
            body.append(render(zh_body))
        else:
            body.append('<p class="gf-director-language-empty">中文译文正在整理，可切换至“日文原文”阅读。</p>')
        body.extend(["<details class=\"gf-director-language\"><summary>查看日文原文</summary>", render(ja_body), "</details>"])
        filename = f"{ja_meta['date']}-gamefreak-lineblog-{article['id']}.md"
        write_text(REPO_ROOT / "_posts" / filename, "---\n" + yaml.safe_dump(front, allow_unicode=True, sort_keys=False).strip() + "\n---\n\n" + "\n\n".join(body) + "\n")
        generated += 1
    print(f"publish: {generated} LINE BLOG post(s), {copied} copied image(s)")
    return {"posts": generated, "assets": copied}


def validate(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_manifest()
    selected = selected_articles(manifest, args)
    asset_path = ARCHIVE_ROOT / "manifest" / "assets.yml"
    assets = load_yaml(asset_path).get("assets", []) if asset_path.exists() else []
    errors: list[str] = []
    warnings: list[str] = []
    for article in selected:
        for path in (
            ARCHIVE_ROOT / article["raw_page"],
            ARCHIVE_ROOT / "content" / str(article["id"]) / "ja.md",
            ARCHIVE_ROOT / "content" / str(article["id"]) / "metadata.yml",
            ARCHIVE_ROOT / "translations" / "zh-CN" / f"{article['id']}.md",
        ):
            if not path.exists():
                errors.append(f"missing {path.relative_to(REPO_ROOT)}")
    for item in assets:
        if item.get("status") == "missing":
            warnings.append(f"missing source image {item.get('original_url')}")
            continue
        path = REPO_ROOT / item["local_path"]
        if not path.exists():
            errors.append(f"missing asset {item['local_path']}")
        elif sha256_file(path) != item.get("sha256"):
            errors.append(f"checksum mismatch {item['local_path']}")
    if manifest.get("mode") == "all" and len(manifest.get("articles", [])) != EXPECTED_COUNT:
        warnings.append(f"expected {EXPECTED_COUNT} numeric article URLs from the Wayback CDX index; discovery found {len(manifest.get('articles', []))}")
    result = {"generated_at": utc_now(), "articles": len(selected), "assets": len(assets), "errors": errors, "warnings": warnings, "status": "PASS" if not errors else "FAIL"}
    write_yaml(ARCHIVE_ROOT / "reports" / "validation.yml", result)
    print(f"validate: {result['status']} — {len(errors)} error(s), {len(warnings)} warning(s)")
    if args.strict and errors:
        raise SystemExit(1)
    return result


def selected_articles(manifest: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    articles = list(manifest.get("articles", []))
    if args.only:
        wanted = set(args.only)
        articles = [item for item in articles if item["id"] in wanted]
    if args.limit:
        articles = articles[:args.limit]
    return articles


def run_all(args: argparse.Namespace) -> None:
    discover(args)
    capture(args)
    extract(args)
    publish(args)
    validate(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Archive Masuda Junichi's LINE BLOG from Wayback.")
    parser.add_argument("command", choices=["all", "discover", "capture", "extract", "publish", "validate"], nargs="?", default="all")
    parser.add_argument("--all", action="store_true", help="Discover every numeric article URL recorded by Wayback CDX.")
    parser.add_argument("--only", type=int, nargs="*", help="Limit later stages to specific LINE BLOG article ids.")
    parser.add_argument("--limit", type=int, default=0, help="Limit later stages after discovery.")
    parser.add_argument("--delay", type=float, default=0.45)
    parser.add_argument("--workers", type=int, default=1, help="Parallel capture workers (1-8; capture stage only).")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--strict", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "all":
        run_all(args)
    else:
        globals()[args.command](args)


if __name__ == "__main__":
    main()
