#!/usr/bin/env python3
"""Archive pipeline for Game Freak's Masuda Director's Columns.

The pipeline deliberately separates discovery/raw capture, asset fetching,
normalized extraction, and validation. It defaults to the three sample
articles in gamefreak-archive-samples.yml. Pass --all to discover every month;
that mode is intentionally not used by the sample test run.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import mimetypes
import re
import sys
import time
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote, unquote, urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup, NavigableString, Tag
from PIL import Image, UnidentifiedImageError


REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = REPO_ROOT / "archive" / "gamefreak-director"
DEFAULT_SAMPLE_FILE = REPO_ROOT / "tools" / "gamefreak-archive-samples.yml"
LANGUAGES = {
    "ja": "https://www.gamefreak.co.jp/blog/dir/",
    "en": "https://www.gamefreak.co.jp/blog/dir_english/",
}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
USER_AGENT = (
    "PokeAmice-Digital-Archive/0.1 "
    "(+https://docs.pokeamice.com/gamefreak-director/; low-rate preservation test)"
)
WAYBACK_AVAILABILITY_URL = "https://archive.org/wayback/available"
SOURCE_ASSET_ALIASES = {
    # The Japanese No. 80 page has an extra trailing "1"; the parallel
    # English post and the rest of the ger00x sequence use ger001.jpg.
    "https://www.gamefreak.co.jp/blog/dir/wp-content/uploads/2007/08/ger0011.jpg":
        "https://www.gamefreak.co.jp/blog/dir/wp-content/uploads/2007/08/ger001.jpg",
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
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_bytes(data)
    temp_path.replace(path)


def write_text(path: Path, text: str) -> None:
    atomic_write(path, text.encode("utf-8"))


def write_yaml(path: Path, data: Any) -> None:
    write_text(path, yaml.safe_dump(data, allow_unicode=True, sort_keys=False))


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def normalize_number(text: str) -> int | None:
    normalized = unicodedata.normalize("NFKC", text)
    match = re.search(r"(?:第\s*(\d+)\s*回|No\.?\s*(\d+))", normalized, re.I)
    if not match:
        return None
    return int(match.group(1) or match.group(2))


def normalize_date(text: str, lang: str) -> str | None:
    value = unicodedata.normalize("NFKC", text).strip()
    formats = ["%Y.%m.%d"] if lang == "ja" else ["%m.%d.%Y", "%m.%d.%y"]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def month_from_url(url: str) -> str | None:
    match = re.search(r"/(\d{4})/(\d{2})/", url)
    return f"{match.group(1)}-{match.group(2)}" if match else None


def safe_filename(url: str, fallback: str = "asset.bin") -> str:
    name = Path(unquote(urlparse(url).path)).name or fallback
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip(".-") or fallback
    return name


def is_image_url(url: str) -> bool:
    return Path(urlparse(url).path).suffix.lower() in IMAGE_EXTENSIONS


def resolve_source_url(page_url: str, value: str | None) -> str:
    """Resolve old HTML URLs, including scheme-less absolute host paths."""
    raw = (value or "").strip()
    if raw.startswith("www.gamefreak.co.jp/"):
        return "https://" + raw
    if raw.startswith("gamefreak.sakura.ne.jp/"):
        return "http://" + raw
    resolved = urljoin(page_url, raw)
    parsed = urlparse(resolved)
    if parsed.netloc == "www.gamefreak.co.jp":
        for duplicated_host, scheme in (
            ("/www.gamefreak.co.jp/", "https"),
            ("/gamefreak.sakura.ne.jp/", "http"),
        ):
            if duplicated_host in parsed.path:
                suffix = parsed.path.split(duplicated_host, 1)[1]
                host = duplicated_host.strip("/")
                return f"{scheme}://{host}/{suffix}"
    return resolved


@dataclass
class Fetcher:
    delay: float = 0.8
    refresh: bool = False

    def __post_init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "ja,en;q=0.8"})
        self.network_requests = 0

    def request(self, url: str) -> requests.Response:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=40, allow_redirects=True)
                response.raise_for_status()
                self.network_requests += 1
                if self.delay:
                    time.sleep(self.delay)
                return response
            except requests.RequestException as exc:
                last_error = exc
                response = getattr(exc, "response", None)
                if response is not None and 400 <= response.status_code < 500:
                    if response.status_code not in {408, 429}:
                        break
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"Failed to fetch {url}: {last_error}")

    def capture(self, url: str, body_path: Path, meta_path: Path) -> bytes:
        if body_path.exists() and meta_path.exists() and not self.refresh:
            return body_path.read_bytes()

        response = self.request(url)
        body = response.content
        atomic_write(body_path, body)
        write_yaml(
            meta_path,
            {
                "requested_url": url,
                "final_url": response.url,
                "captured_at": utc_now(),
                "status": response.status_code,
                "content_type": response.headers.get("Content-Type"),
                "content_length": len(body),
                "sha256": sha256_bytes(body),
                "headers": dict(response.headers),
            },
        )
        return body


def find_wayback_capture(
    fetcher: Fetcher, original_url: str
) -> tuple[requests.Response, str, str]:
    availability_url = f"{WAYBACK_AVAILABILITY_URL}?url={quote(original_url, safe='')}"
    availability = fetcher.request(availability_url)
    closest = availability.json().get("archived_snapshots", {}).get("closest", {})
    if not closest.get("available") or str(closest.get("status")) != "200":
        raise RuntimeError(f"No Internet Archive capture available for {original_url}")
    timestamp = str(closest.get("timestamp") or "")
    if not timestamp:
        match = re.search(r"/web/(\d+)/", str(closest.get("url") or ""))
        timestamp = match.group(1) if match else ""
    if not timestamp:
        raise RuntimeError(f"Internet Archive capture has no timestamp for {original_url}")
    raw_url = f"https://web.archive.org/web/{timestamp}id_/{original_url}"
    response = fetcher.request(raw_url)
    if is_image_url(original_url) and "text/html" in response.headers.get("Content-Type", ""):
        raise RuntimeError(f"Internet Archive returned HTML instead of an image: {raw_url}")
    return response, raw_url, timestamp


def raw_archive_paths(lang: str) -> tuple[Path, Path]:
    directory = ARCHIVE_ROOT / "raw" / lang
    return directory / "archive.html", directory / "archive.response.yml"


def raw_root_paths(lang: str) -> tuple[Path, Path]:
    directory = ARCHIVE_ROOT / "raw" / lang
    return directory / "index.html", directory / "index.response.yml"


def raw_month_paths(lang: str, month: str) -> tuple[Path, Path]:
    year, month_number = month.split("-")
    directory = ARCHIVE_ROOT / "raw" / lang / year / month_number
    return directory / "index.html", directory / "response.yml"


def parse_month_links(html: bytes, base_url: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    links: dict[str, str] = {}
    for anchor in soup.select(".main a[href]"):
        url = urljoin(base_url, anchor.get("href"))
        month = month_from_url(url)
        if month:
            links.setdefault(month, url)
    return links


def is_malformed_archive_url(url: str) -> bool:
    """Identify broken placeholder links emitted by the official archive."""
    return ".UNKNOWN" in url.upper()


def missing_japanese_article_numbers(manifest: dict[str, Any]) -> list[int]:
    present = {
        int(article["number"])
        for article in manifest.get("articles", [])
        if "ja" in article.get("languages", {})
    }
    return sorted(set(range(1, 245)) - present)


def parse_articles(html: bytes, lang: str, page_url: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    results: list[dict[str, Any]] = []
    for article in soup.select(".main .article"):
        header = article.select_one(".article-header-title")
        if not header:
            continue
        number = normalize_number(header.get_text(" ", strip=True))
        if number is None:
            continue
        date_node = header.select_one(".article-date")
        date_display = date_node.get_text(" ", strip=True) if date_node else ""
        detail = article.select_one(".article-detail")
        footer = article.select_one(".article-footer")
        categories = [
            item.get_text(" ", strip=True)
            for item in article.select(".article-footer-category-name")
            if item.get_text(" ", strip=True)
        ]
        share = article.select_one(".twitter-share-button[data-url]")
        permalink_reported = urljoin(page_url, share.get("data-url")) if share else None
        permalink_number = (
            normalize_number(unquote(urlparse(permalink_reported).path).replace("-", " "))
            if permalink_reported
            else None
        )
        permalink_validated = permalink_reported is not None and permalink_number == number
        permalink = permalink_reported if permalink_validated else None
        lead = ""
        if detail:
            for paragraph in detail.find_all(["p", "div", "pre"], recursive=False):
                candidate = paragraph.get_text(" ", strip=True)
                if candidate:
                    lead = candidate
                    break
        results.append(
            {
                "number": number,
                "lang": lang,
                "date": normalize_date(date_display, lang),
                "date_display": date_display,
                "page_url": page_url,
                "permalink": permalink,
                "permalink_reported": permalink_reported,
                "permalink_validated": permalink_validated,
                "categories": categories,
                "lead": lead,
                "article_html": str(article),
                "detail_html": str(detail) if detail else "",
                "footer_html": str(footer) if footer else "",
            }
        )
    return results


def load_sample_config(path: Path) -> dict[int, dict[str, Any]]:
    raw = load_yaml(path) or {}
    samples: dict[int, dict[str, Any]] = {}
    for item in raw.get("samples", []):
        item = dict(item)
        item["number"] = int(item["number"])
        samples[item["number"]] = item
    if not samples:
        raise ValueError(f"No samples found in {path}")
    return samples


def discover(args: argparse.Namespace) -> dict[str, Any]:
    sample_config = load_sample_config(args.samples)
    fetcher = Fetcher(delay=args.delay, refresh=args.refresh)
    article_map: dict[int, dict[str, Any]] = {}
    discovered_months: dict[str, dict[str, str]] = {}
    discovery_issues: list[dict[str, Any]] = []

    def merge_article(
        parsed: dict[str, Any], lang: str, month: str, raw_page: str
    ) -> None:
        number = parsed["number"]
        if not args.all and number not in sample_config:
            return
        entry = article_map.setdefault(
            number,
            {
                "id": f"masuda-{number:03d}",
                "number": number,
                "month": month,
                "roles": sample_config.get(number, {}).get("roles", []),
                "expected_languages": sample_config.get(number, {}).get(
                    "expected_languages", ["ja"]
                ),
                "known_missing_languages": sample_config.get(number, {}).get(
                    "known_missing_languages", []
                ),
                "minimum_article_assets": sample_config.get(number, {}).get(
                    "minimum_article_assets", 0
                ),
                "languages": {},
            },
        )
        previous = entry["languages"].get(lang)
        if previous and previous.get("date") != parsed.get("date"):
            discovery_issues.append(
                {
                    "lang": lang,
                    "month": month,
                    "source_url": parsed.get("page_url"),
                    "status": "duplicate-article-number",
                    "article_number": number,
                    "dates": [previous.get("date"), parsed.get("date")],
                    "note": "Both posts remain preserved in the raw monthly capture.",
                }
            )
        language_data = {
            key: value for key, value in parsed.items() if not key.endswith("_html")
        }
        language_data["raw_page"] = raw_page
        entry["languages"][lang] = language_data

    for lang, base_url in LANGUAGES.items():
        archive_url = urljoin(base_url, "archive.html")
        archive_body, archive_meta = raw_archive_paths(lang)
        archive_html = fetcher.capture(archive_url, archive_body, archive_meta)
        month_links = parse_month_links(archive_html, archive_url)
        discovered_months[lang] = month_links

        # Two links in the official English archive contain UNKNOWN
        # placeholders. The root page is also a useful auxiliary source: it
        # includes No. 242, whose 2014-10 month page is inaccessible.
        if args.all and lang == "en":
            root_body, root_meta = raw_root_paths(lang)
            try:
                root_html = fetcher.capture(base_url, root_body, root_meta)
                for parsed in parse_articles(root_html, lang, base_url):
                    existing = article_map.get(parsed["number"])
                    root_month = (
                        existing.get("month")
                        if existing
                        else (parsed.get("date") or "0000-00")[:7]
                    )
                    merge_article(
                        parsed,
                        lang,
                        root_month,
                        "archive/gamefreak-director/raw/en/index.html",
                    )
            except RuntimeError as exc:
                discovery_issues.append(
                    {
                        "lang": lang,
                        "month": None,
                        "source_url": base_url,
                        "status": "fallback-unavailable",
                        "error": str(exc),
                    }
                )

        if args.all:
            target_months = sorted(month_links)
        else:
            target_months = sorted({str(item["month"]) for item in sample_config.values()})

        for month in target_months:
            month_url = month_links.get(month)
            if not month_url:
                continue
            if is_malformed_archive_url(month_url):
                discovery_issues.append(
                    {
                        "lang": lang,
                        "month": month,
                        "source_url": month_url,
                        "status": "malformed-official-link",
                        "error": "The official archive emitted an UNKNOWN placeholder URL.",
                        "fallback_source": base_url if lang == "en" else None,
                    }
                )
                continue
            body_path, meta_path = raw_month_paths(lang, month)
            try:
                month_html = fetcher.capture(month_url, body_path, meta_path)
            except RuntimeError as exc:
                discovery_issues.append(
                    {
                        "lang": lang,
                        "month": month,
                        "source_url": month_url,
                        "status": "fetch-failed",
                        "error": str(exc),
                    }
                )
                continue
            for parsed in parse_articles(month_html, lang, month_url):
                year, month_number = month.split("-")
                merge_article(
                    parsed,
                    lang,
                    month,
                    f"archive/gamefreak-director/raw/{lang}/{year}/{month_number}/index.html",
                )

    articles = [article_map[key] for key in sorted(article_map)]
    manifest = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "mode": "all" if args.all else "samples",
        "source": LANGUAGES,
        "network_requests": fetcher.network_requests,
        "articles": articles,
    }
    manifest_dir = ARCHIVE_ROOT / "manifest"
    write_yaml(manifest_dir / "articles.yml", manifest)
    write_yaml(
        ARCHIVE_ROOT / "reports" / "discovery-issues.yml",
        {"generated_at": utc_now(), "issues": discovery_issues},
    )

    manifest_dir.mkdir(parents=True, exist_ok=True)
    with (manifest_dir / "urls.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["number", "lang", "month", "date", "page_url", "permalink"],
        )
        writer.writeheader()
        for article in articles:
            for lang, language_data in article["languages"].items():
                writer.writerow(
                    {
                        "number": article["number"],
                        "lang": lang,
                        "month": article["month"],
                        "date": language_data.get("date"),
                        "page_url": language_data.get("page_url"),
                        "permalink": language_data.get("permalink"),
                    }
                )

    print(
        f"discover: {len(articles)} articles, {fetcher.network_requests} network requests, "
        f"{len(discovery_issues)} source issues, manifest={manifest_dir / 'articles.yml'}"
    )
    return manifest


def load_manifest() -> dict[str, Any]:
    path = ARCHIVE_ROOT / "manifest" / "articles.yml"
    if not path.exists():
        raise FileNotFoundError("Run discover before this stage")
    return load_yaml(path)


def find_article_in_raw(article: dict[str, Any], lang: str) -> dict[str, Any]:
    language_data = article["languages"][lang]
    raw_path = REPO_ROOT / language_data["raw_page"]
    matches = [
        item
        for item in parse_articles(raw_path.read_bytes(), lang, language_data["page_url"])
        if item["number"] == article["number"]
    ]
    if len(matches) > 1:
        expected_date = language_data.get("date")
        dated_matches = [item for item in matches if item.get("date") == expected_date]
        if len(dated_matches) == 1:
            return dated_matches[0]
        expected_permalink = language_data.get("permalink_reported")
        permalink_matches = [
            item for item in matches if item.get("permalink_reported") == expected_permalink
        ]
        if len(permalink_matches) == 1:
            return permalink_matches[0]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one article {article['number']} in {raw_path}, found {len(matches)}"
        )
    return matches[0]


def collect_article_asset_urls(article_html: str, page_url: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(article_html, "html.parser")
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for image in soup.select("img[src]"):
        url = resolve_source_url(page_url, image.get("src"))
        if url not in seen:
            seen.add(url)
            results.append({"url": url, "role": "inline", "alt": image.get("alt") or ""})
    for anchor in soup.select("a[href]"):
        url = resolve_source_url(page_url, anchor.get("href"))
        if is_image_url(url) and url not in seen:
            seen.add(url)
            results.append({"url": url, "role": "linked-original", "alt": ""})
    return results


def collect_shared_asset_urls(html: bytes, page_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    results: list[str] = []
    for node, attribute in [(item, "href") for item in soup.select("link[href]")] + [
        (item, "src") for item in soup.select("script[src], header img[src], .sidebar img[src]")
    ]:
        url = urljoin(page_url, node.get(attribute))
        parsed = urlparse(url)
        if parsed.netloc == "www.gamefreak.co.jp" and "/themes/default/static/" in parsed.path:
            results.append(url)
    return list(dict.fromkeys(results))


def download_asset(
    fetcher: Fetcher,
    url: str,
    destination: Path,
    *,
    role: str,
    article_number: int | None,
    asset_scope: str,
    languages: Iterable[str],
) -> dict[str, Any]:
    meta_path = destination.with_name(destination.name + ".meta.yml")
    asset_id = (
        f"{article_number:03d}-{asset_scope}-{destination.stem.lower()}"
        if article_number is not None
        else f"shared-{asset_scope}-{destination.stem.lower()}"
    )
    response_headers: dict[str, str] = {}
    wayback_url = None
    wayback_timestamp = None
    substitute_url = None
    if destination.exists() and not fetcher.refresh:
        body = destination.read_bytes()
        existing_meta = load_yaml(meta_path) if meta_path.exists() else {}
        status = int(existing_meta.get("status", 200))
        content_type = existing_meta.get("content_type") or mimetypes.guess_type(destination.name)[0]
        captured_at = existing_meta.get("captured_at") or datetime.fromtimestamp(
            destination.stat().st_mtime, timezone.utc
        ).replace(microsecond=0).isoformat()
        response_headers = existing_meta.get("headers", {})
        capture_source = existing_meta.get("capture_source", "existing-local-file")
        wayback_url = existing_meta.get("wayback_url")
        wayback_timestamp = existing_meta.get("wayback_timestamp")
        substitute_url = existing_meta.get("substitute_url")
    else:
        try:
            response = fetcher.request(url)
            capture_source = "http-response"
        except RuntimeError as original_exc:
            try:
                substitute_url = SOURCE_ASSET_ALIASES.get(url)
                if not substitute_url:
                    raise RuntimeError("No documented source URL correction")
                response = fetcher.request(substitute_url)
                capture_source = "source-url-correction"
            except RuntimeError as alias_exc:
                try:
                    response, wayback_url, wayback_timestamp = find_wayback_capture(fetcher, url)
                    capture_source = "internet-archive"
                except (RuntimeError, requests.RequestException, ValueError) as wayback_exc:
                    exc = RuntimeError(
                        f"{original_exc}; URL correction failed: {alias_exc}; "
                        f"Wayback fallback failed: {wayback_exc}"
                    )
                    captured_at = utc_now()
                    sidecar = {
                        "original_url": url,
                        "captured_at": captured_at,
                        "capture_source": "http-error",
                        "status": "unavailable",
                        "error": str(exc),
                    }
                    write_yaml(meta_path, sidecar)
                    return {
                        "id": asset_id,
                        "article": article_number,
                        "role": role,
                        "languages": sorted(set(languages)),
                        "original_url": url,
                        "local_path": None,
                        "intended_local_path": destination.relative_to(REPO_ROOT).as_posix(),
                        "original_filename": safe_filename(url),
                        "captured_at": captured_at,
                        "status": "unavailable",
                        "content_type": None,
                        "bytes": 0,
                        "sha256": None,
                        "width": None,
                        "height": None,
                        "sidecar": meta_path.relative_to(REPO_ROOT).as_posix(),
                        "error": str(exc),
                    }
        body = response.content
        atomic_write(destination, body)
        status = response.status_code
        content_type = response.headers.get("Content-Type")
        captured_at = utc_now()
        response_headers = dict(response.headers)

    width = None
    height = None
    if is_image_url(url):
        try:
            with Image.open(destination) as image:
                width, height = image.size
        except (UnidentifiedImageError, OSError):
            pass

    sha256 = sha256_bytes(body)
    sidecar = {
        "original_url": url,
        "captured_at": captured_at,
        "capture_source": capture_source,
        "status": status,
        "content_type": content_type,
        "bytes": len(body),
        "sha256": sha256,
        "width": width,
        "height": height,
        "headers": response_headers,
    }
    if capture_source == "internet-archive":
        sidecar["wayback_url"] = wayback_url
        sidecar["wayback_timestamp"] = wayback_timestamp
    if capture_source == "source-url-correction":
        sidecar["substitute_url"] = substitute_url
    write_yaml(meta_path, sidecar)
    return {
        "id": asset_id,
        "article": article_number,
        "role": role,
        "languages": sorted(set(languages)),
        "original_url": url,
        "local_path": destination.relative_to(REPO_ROOT).as_posix(),
        "original_filename": safe_filename(url),
        "captured_at": captured_at,
        "capture_source": capture_source,
        "status": status,
        "content_type": content_type,
        "bytes": len(body),
        "sha256": sha256,
        "width": width,
        "height": height,
        "sidecar": meta_path.relative_to(REPO_ROOT).as_posix(),
        "wayback_url": wayback_url,
        "wayback_timestamp": wayback_timestamp,
        "substitute_url": substitute_url,
    }


def fetch_assets(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_manifest()
    fetcher = Fetcher(delay=args.delay, refresh=args.refresh)
    asset_records: dict[str, dict[str, Any]] = {}
    shared_urls: dict[str, set[str]] = defaultdict(set)

    for article in manifest["articles"]:
        discovered: dict[str, dict[str, Any]] = {}
        for lang in article["languages"]:
            parsed = find_article_in_raw(article, lang)
            for asset in collect_article_asset_urls(parsed["article_html"], parsed["page_url"]):
                record = discovered.setdefault(asset["url"], {"roles": set(), "languages": set()})
                record["roles"].add(asset["role"])
                record["languages"].add(lang)

            language_data = article["languages"][lang]
            raw_path = REPO_ROOT / language_data["raw_page"]
            for url in collect_shared_asset_urls(raw_path.read_bytes(), language_data["page_url"]):
                shared_urls[url].add(lang)

        for url, discovery in discovered.items():
            if url in asset_records:
                asset_records[url]["languages"] = sorted(
                    set(asset_records[url]["languages"]) | set(discovery["languages"])
                )
                continue
            filename = safe_filename(url)
            asset_scope = (
                next(iter(discovery["languages"]))
                if len(discovery["languages"]) == 1
                else "multi"
            )
            destination = (
                ARCHIVE_ROOT
                / "assets"
                / "original"
                / f"{article['number']:03d}"
                / asset_scope
                / filename
            )
            record = download_asset(
                fetcher,
                url,
                destination,
                role="+".join(sorted(discovery["roles"])),
                article_number=article["number"],
                asset_scope=asset_scope,
                languages=discovery["languages"],
            )
            asset_records[url] = record

    for url, languages in shared_urls.items():
        if url in asset_records:
            asset_records[url]["languages"] = sorted(
                set(asset_records[url]["languages"]) | set(languages)
            )
            continue
        filename = safe_filename(url)
        asset_scope = next(iter(languages)) if len(languages) == 1 else "multi"
        destination = (
            ARCHIVE_ROOT / "assets" / "original" / "shared" / asset_scope / filename
        )
        record = download_asset(
            fetcher,
            url,
            destination,
            role="theme-shared",
            article_number=None,
            asset_scope=asset_scope,
            languages=languages,
        )
        asset_records[url] = record

        if record.get("status") != "unavailable" and destination.suffix.lower() == ".css":
            css_text = destination.read_text(encoding="utf-8", errors="replace")
            for match in re.finditer(r"url\((['\"]?)([^)'\"]+)\1\)", css_text):
                dependency = match.group(2).strip()
                if dependency.startswith("data:"):
                    continue
                dependency_url = urljoin(url, dependency)
                parsed = urlparse(dependency_url)
                if parsed.netloc != "www.gamefreak.co.jp":
                    continue
                dependency_name = safe_filename(dependency_url)
                dependency_destination = (
                    ARCHIVE_ROOT
                    / "assets"
                    / "original"
                    / "shared"
                    / asset_scope
                    / dependency_name
                )
                if dependency_url not in asset_records:
                    asset_records[dependency_url] = download_asset(
                        fetcher,
                        dependency_url,
                        dependency_destination,
                        role="theme-shared-css-dependency",
                        article_number=None,
                        asset_scope=asset_scope,
                        languages=languages,
                    )

    assets = sorted(asset_records.values(), key=lambda item: (item["article"] or 0, item["id"]))
    asset_manifest = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "network_requests": fetcher.network_requests,
        "assets": assets,
    }
    write_yaml(ARCHIVE_ROOT / "manifest" / "assets.yml", asset_manifest)
    print(
        f"fetch: {len(assets)} assets, {fetcher.network_requests} network requests, "
        f"manifest={ARCHIVE_ROOT / 'manifest' / 'assets.yml'}"
    )
    return asset_manifest


def inline_to_markdown(node: Tag, asset_by_url: dict[str, dict[str, Any]], page_url: str) -> str:
    parts: list[str] = []

    def walk(current: Tag | NavigableString) -> None:
        if isinstance(current, NavigableString):
            text = re.sub(r"[\t\r\f\v ]+", " ", str(current))
            parts.append(text)
            return
        if not isinstance(current, Tag):
            return
        if current.name == "br":
            parts.append("  \n")
            return
        if current.name == "img":
            url = resolve_source_url(page_url, current.get("src"))
            asset = asset_by_url.get(url)
            marker = asset["id"] if asset else safe_filename(url)
            parts.append(f'{{% image id="{marker}" %}}')
            return
        if current.name == "a":
            image = current.find("img")
            if image:
                walk(image)
                return
            label = current.get_text(" ", strip=True)
            href = urljoin(page_url, current.get("href"))
            parts.append(f"[{label}]({href})" if label else f"<{href}>")
            return
        for child in current.children:
            walk(child)

    walk(node)
    result = "".join(parts)
    result = re.sub(r" *\n *", "\n", result).strip()
    return result


def detail_to_structure(
    detail_html: str, page_url: str, asset_by_url: dict[str, dict[str, Any]]
) -> tuple[list[dict[str, Any]], str]:
    soup = BeautifulSoup(detail_html, "html.parser")
    detail = soup.select_one(".article-detail") or soup
    blocks: list[dict[str, Any]] = []
    markdown_parts: list[str] = []

    children = [child for child in detail.children if isinstance(child, (Tag, NavigableString))]
    for child in children:
        if isinstance(child, NavigableString):
            text = child.strip()
            if not text:
                continue
            blocks.append({"type": "text", "markdown": text})
            markdown_parts.append(text)
            continue
        markdown = inline_to_markdown(child, asset_by_url, page_url)
        if not markdown:
            blocks.append({"type": "spacer"})
            markdown_parts.append('{% spacer %}')
            continue
        block_type = "paragraph" if child.name == "p" else child.name
        image_ids = re.findall(r'image id="([^"]+)"', markdown)
        blocks.append(
            {
                "type": block_type,
                "markdown": markdown,
                "images": image_ids,
                "source_html": str(child),
            }
        )
        markdown_parts.append(markdown)
    return blocks, "\n\n".join(markdown_parts).strip() + "\n"


def extract(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_manifest()
    asset_manifest = load_yaml(ARCHIVE_ROOT / "manifest" / "assets.yml")
    asset_by_url = {item["original_url"]: item for item in asset_manifest.get("assets", [])}
    extracted = 0

    for article in manifest["articles"]:
        number = article["number"]
        article_dir = ARCHIVE_ROOT / "content" / f"{number:03d}"
        article_dir.mkdir(parents=True, exist_ok=True)
        metadata: dict[str, Any] = {
            "id": article["id"],
            "number": number,
            "month": article["month"],
            "roles": article.get("roles", []),
            "author": {"name_ja": "増田 順一", "name_en": "Junichi Masuda"},
            "series": {
                "name_ja": "増田部長のめざめるパワー",
                "name_en": "HIDDEN POWER of masuda",
            },
            "sources": {},
            "languages": {},
            "rights": {
                "archive_type": "unofficial",
                "original_copyright": "GAME FREAK inc.",
            },
            "extracted_at": utc_now(),
        }

        for lang in sorted(article["languages"]):
            parsed = find_article_in_raw(article, lang)
            blocks, markdown_body = detail_to_structure(
                parsed["detail_html"], parsed["page_url"], asset_by_url
            )
            front_matter = {
                "article_id": article["id"],
                "number": number,
                "lang": lang,
                "date": parsed.get("date"),
                "date_display": parsed.get("date_display"),
                "source": parsed.get("page_url"),
                "permalink_source": parsed.get("permalink"),
                "categories": parsed.get("categories", []),
                "status": "source-extracted",
            }
            markdown = (
                "---\n"
                + yaml.safe_dump(front_matter, allow_unicode=True, sort_keys=False).strip()
                + "\n---\n\n"
                + markdown_body
            )
            write_text(article_dir / f"{lang}.md", markdown)
            write_text(article_dir / f"source.{lang}.html", parsed["article_html"])
            write_text(
                article_dir / f"structure.{lang}.json",
                json.dumps(
                    {
                        "schema_version": 1,
                        "article": number,
                        "lang": lang,
                        "blocks": blocks,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
            )
            metadata["sources"][lang] = {
                "page_url": parsed.get("page_url"),
                "permalink": parsed.get("permalink"),
                "permalink_reported": parsed.get("permalink_reported"),
                "permalink_validated": parsed.get("permalink_validated"),
                "date": parsed.get("date"),
                "date_display": parsed.get("date_display"),
                "categories": parsed.get("categories", []),
                "lead": parsed.get("lead"),
                "raw_page": article["languages"][lang]["raw_page"],
            }
            metadata["languages"][lang] = True
            extracted += 1

        article_assets = [
            item for item in asset_manifest.get("assets", []) if item.get("article") == number
        ]
        metadata["assets"] = [
            {
                "id": item["id"],
                "role": item["role"],
                "original_url": item["original_url"],
                "local_path": item["local_path"],
                "sha256": item["sha256"],
                "capture_source": item.get("capture_source"),
                "wayback_url": item.get("wayback_url"),
                "wayback_timestamp": item.get("wayback_timestamp"),
                "substitute_url": item.get("substitute_url"),
            }
            for item in article_assets
        ]
        write_yaml(article_dir / "metadata.yml", metadata)

        translation_path = ARCHIVE_ROOT / "translations" / "zh-CN" / f"{number:03d}.md"
        if not translation_path.exists():
            translation_front_matter = {
                "article_id": article["id"],
                "number": number,
                "lang": "zh-CN",
                "source_language": "ja",
                "translation_status": "missing",
                "translator": None,
                "reviewer": None,
            }
            translation = (
                "---\n"
                + yaml.safe_dump(
                    translation_front_matter, allow_unicode=True, sort_keys=False
                ).strip()
                + "\n---\n\n<!-- 中文翻译待完成；请保留原文的段落、换行和图片标记。 -->\n"
            )
            write_text(translation_path, translation)

    print(f"extract: {extracted} language documents from {len(manifest['articles'])} articles")
    return {"articles": len(manifest["articles"]), "language_documents": extracted}


def _content_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        return parts[2].lstrip() if len(parts) == 3 else text
    return text


def publish_site_pages(args: argparse.Namespace) -> dict[str, Any]:
    """Materialize normalized archive content as searchable Jekyll posts."""
    manifest = load_manifest()
    assets_manifest_path = ARCHIVE_ROOT / "manifest" / "assets.yml"
    assets = load_yaml(assets_manifest_path).get("assets", []) if assets_manifest_path.exists() else []
    asset_by_id = {item["id"]: item for item in assets}
    public_asset_root = REPO_ROOT / "assets" / "images" / "gamefreak-director" / "archive"
    published_assets = 0

    for asset in assets:
        local_path = asset.get("local_path")
        if not local_path or asset.get("status") == "unavailable":
            continue
        source_path = REPO_ROOT / local_path
        if not source_path.exists() or source_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        marker = "archive/gamefreak-director/assets/original/"
        if marker not in local_path:
            continue
        relative = local_path.split(marker, 1)[1]
        destination = public_asset_root / relative
        atomic_write(destination, source_path.read_bytes())
        published_assets += 1

    def render_body(path: Path) -> str:
        body = _content_body(path)

        def replace_marker(match: re.Match[str]) -> str:
            asset = asset_by_id.get(match.group(1))
            if not asset or not asset.get("local_path"):
                return ""
            local_path = asset["local_path"]
            marker = "archive/gamefreak-director/assets/original/"
            if marker not in local_path:
                return ""
            relative = local_path.split(marker, 1)[1]
            public_path = f"/assets/images/gamefreak-director/archive/{relative}"
            return f'<img src="{public_path}" alt="" loading="lazy">'

        body = re.sub(r'\{%\s*image\s+id="([^"]+)"\s*%\}', replace_marker, body)
        body = re.sub(r"\{%\s*spacer\s*%\}", '<p class="gf-director-spacer"></p>', body)
        return body.strip() + "\n"

    generated = 0
    posts_dir = REPO_ROOT / "_posts"
    for article in manifest["articles"]:
        number = int(article["number"])
        ja = article.get("languages", {}).get("ja")
        if not ja:
            continue
        date = ja.get("date") or f"{article['month']}-01"
        categories = list(ja.get("categories") or [])
        front_matter = {
            "layout": "gamefreak-director",
            "title": f"[GameFreak部长专栏] 第{number}回",
            "date": date,
            "permalink": f"/gamefreak-director/entry-{number:03d}/",
            "categories": ["官方博客", "Game Freak", "翻译资料"],
            "tags": ["Game Freak", "增田顺一", "宝可梦", "官方博客"],
            "archive_type": "gamefreak_director_column",
            "gf_entry_no": number,
            "gf_entry_title": ja.get("lead") or "",
            "gf_archive": article.get("month"),
            "gf_categories": categories,
            "summary": "日文原文已归档；中文译稿待校对，官方英文版按原站可用性提供。",
            "search": True,
            "source": {"title": f"増田部長のめざめるパワー 第{number}回", "url": ja.get("page_url"), "source_type": "official_blog"},
            "gf_archive_id": article.get("id"),
        }
        front = yaml.safe_dump(front_matter, allow_unicode=True, sort_keys=False).strip()
        ja_path = ARCHIVE_ROOT / "content" / f"{number:03d}" / "ja.md"
        if not ja_path.exists():
            continue
        body_parts = [
            '<aside class="gf-director-translation-note"><strong>中文翻译待完成</strong><span>以下为保留原始换行与图片位置的日文原文。</span></aside>',
            "## 日文原文",
            render_body(ja_path),
        ]
        en_path = ARCHIVE_ROOT / "content" / f"{number:03d}" / "en.md"
        if en_path.exists():
            body_parts.extend(
                [
                    "<details class=\"gf-director-language\"><summary>查看官方英文版</summary>",
                    render_body(en_path),
                    "</details>",
                ]
            )
        filename = f"{date}-gamefreak-director-{number:03d}.md"
        write_text(posts_dir / filename, f"---\n{front}\n---\n\n" + "\n\n".join(body_parts) + "\n")
        generated += 1

    print(f"publish: {generated} searchable Jekyll posts, {published_assets} public images")
    return {"posts": generated, "assets": published_assets}


def validate(args: argparse.Namespace) -> dict[str, Any]:
    manifest = load_manifest()
    asset_manifest_path = ARCHIVE_ROOT / "manifest" / "assets.yml"
    assets = load_yaml(asset_manifest_path).get("assets", []) if asset_manifest_path.exists() else []
    assets_by_article: dict[int, list[dict[str, Any]]] = defaultdict(list)
    checks: list[dict[str, Any]] = []

    discovery_issues_path = ARCHIVE_ROOT / "reports" / "discovery-issues.yml"
    if discovery_issues_path.exists():
        for issue in (load_yaml(discovery_issues_path) or {}).get("issues", []):
            target_parts = [str(issue.get("lang") or "source")]
            if issue.get("month"):
                target_parts.append(str(issue["month"]))
            if issue.get("article_number") is not None:
                target_parts.append(f"No.{int(issue['article_number'])}")
            checks.append(
                {
                    "check": "discovery-source-anomaly",
                    "target": "/".join(target_parts),
                    "status": "warning",
                    "detail": issue.get("status"),
                }
            )

    for asset in assets:
        if asset.get("status") == "unavailable":
            checks.append(
                {
                    "check": "source-asset-unavailable",
                    "target": asset["id"],
                    "status": "warning",
                    "detail": asset["original_url"],
                }
            )
            continue
        if asset.get("article") is not None:
            assets_by_article[int(asset["article"])].append(asset)
        path = REPO_ROOT / asset["local_path"]
        ok = path.exists() and sha256_file(path) == asset["sha256"]
        checks.append(
            {
                "check": "asset-file-and-hash",
                "target": asset["id"],
                "status": "pass" if ok else "fail",
                "detail": asset["local_path"],
            }
        )

    numbers = [int(article["number"]) for article in manifest["articles"]]
    unique_numbers = len(numbers) == len(set(numbers))
    checks.append(
        {
            "check": "unique-article-numbers",
            "target": "manifest",
            "status": "pass" if unique_numbers else "fail",
            "detail": f"{len(numbers)} records",
        }
    )

    if manifest.get("mode") == "all":
        missing_ja = missing_japanese_article_numbers(manifest)
        checks.append(
            {
                "check": "full-japanese-number-coverage",
                "target": "001-244/ja",
                "status": "pass" if not missing_ja else "fail",
                "detail": (
                    "all 244 article numbers discovered"
                    if not missing_ja
                    else "missing: " + ", ".join(f"{number:03d}" for number in missing_ja)
                ),
            }
        )

    for article in manifest["articles"]:
        number = int(article["number"])
        expected_languages = article.get("expected_languages", ["ja"])
        for lang in expected_languages:
            language_present = lang in article.get("languages", {})
            checks.append(
                {
                    "check": "expected-language-discovered",
                    "target": f"{number:03d}/{lang}",
                    "status": "pass" if language_present else "fail",
                    "detail": article.get("month"),
                }
            )
            content_path = ARCHIVE_ROOT / "content" / f"{number:03d}" / f"{lang}.md"
            structure_path = (
                ARCHIVE_ROOT / "content" / f"{number:03d}" / f"structure.{lang}.json"
            )
            content_ok = content_path.exists() and content_path.stat().st_size > 100
            structure_ok = structure_path.exists() and structure_path.stat().st_size > 100
            checks.append(
                {
                    "check": "normalized-content",
                    "target": f"{number:03d}/{lang}",
                    "status": "pass" if content_ok and structure_ok else "fail",
                    "detail": f"markdown={content_ok}, structure={structure_ok}",
                }
            )
            if content_ok:
                text = content_path.read_text(encoding="utf-8")
                hotlinks = re.findall(r"!\[[^]]*\]\(https?://", text)
                checks.append(
                    {
                        "check": "no-image-hotlinks",
                        "target": f"{number:03d}/{lang}",
                        "status": "pass" if not hotlinks else "fail",
                        "detail": f"{len(hotlinks)} image hotlinks",
                    }
                )

        for lang in article.get("known_missing_languages", []):
            language_absent = lang not in article.get("languages", {})
            checks.append(
                {
                    "check": "known-language-absence",
                    "target": f"{number:03d}/{lang}",
                    "status": "pass" if language_absent else "fail",
                    "detail": "confirmed absent in the official archive month",
                }
            )

        minimum_assets = int(article.get("minimum_article_assets", 0))
        article_asset_count = len(assets_by_article[number])
        checks.append(
            {
                "check": "minimum-article-assets",
                "target": f"{number:03d}",
                "status": "pass" if article_asset_count >= minimum_assets else "fail",
                "detail": f"found {article_asset_count}, expected at least {minimum_assets}",
            }
        )
        translation = ARCHIVE_ROOT / "translations" / "zh-CN" / f"{number:03d}.md"
        checks.append(
            {
                "check": "translation-layer-present",
                "target": f"{number:03d}/zh-CN",
                "status": "pass" if translation.exists() else "fail",
                "detail": "translation stub is allowed in sample mode",
            }
        )

    failed = [item for item in checks if item["status"] == "fail"]
    warnings = [item for item in checks if item["status"] == "warning"]
    available_hashes = {item["sha256"] for item in assets if item.get("sha256")}
    summary = {
        "generated_at": utc_now(),
        "mode": manifest.get("mode"),
        "articles": len(manifest["articles"]),
        "language_documents": sum(len(item.get("languages", {})) for item in manifest["articles"]),
        "assets": len(assets),
        "unique_asset_hashes": len(available_hashes),
        "duplicate_asset_files": sum(bool(item.get("sha256")) for item in assets)
        - len(available_hashes),
        "checks": len(checks),
        "passed": len(checks) - len(failed) - len(warnings),
        "warnings": len(warnings),
        "failed": len(failed),
        "status": "pass" if not failed else "fail",
    }
    report = {"summary": summary, "checks": checks}
    reports_dir = ARCHIVE_ROOT / "reports"
    write_text(reports_dir / "validation.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    lines = [
        "# Game Freak Director Archive Validation",
        "",
        f"- Status: **{summary['status'].upper()}**",
        f"- Articles: {summary['articles']}",
        f"- Language documents: {summary['language_documents']}",
        f"- Assets: {summary['assets']}",
        f"- Unique asset hashes: {summary['unique_asset_hashes']}",
        f"- Duplicate files by hash: {summary['duplicate_asset_files']}",
        f"- Checks: {summary['passed']} passed / {summary['warnings']} warnings / {summary['failed']} failed",
        "",
        "## Checks",
        "",
        "| Status | Check | Target | Detail |",
        "| --- | --- | --- | --- |",
    ]
    for item in checks:
        icon = {"pass": "PASS", "warning": "WARN", "fail": "FAIL"}[item["status"]]
        detail = str(item["detail"]).replace("|", "\\|")
        lines.append(f"| {icon} | {item['check']} | {item['target']} | {detail} |")
    write_text(reports_dir / "validation.md", "\n".join(lines) + "\n")

    print(
        f"validate: {summary['status'].upper()} — {summary['passed']} passed, "
        f"{summary['warnings']} warnings, {summary['failed']} failed, "
        f"report={reports_dir / 'validation.md'}"
    )
    if failed and args.strict:
        raise SystemExit(1)
    return report


def write_archive_readme() -> None:
    readme = """# Game Freak Director Archive Corpus

This directory is excluded from the Jekyll build. It contains preservation
inputs and normalized research data, not the public presentation layer.

Pipeline stages:

1. `discover` captures archive/month pages and builds the article manifest.
2. `fetch` downloads article media and shared theme assets with hashes. The
   live Game Freak host is tried first; missing resources fall back to the
   Internet Archive with their Wayback URL and snapshot timestamp retained.
3. `extract` creates Markdown, source fragments, and ordered structure JSON.
4. `publish` materializes normalized content as searchable Jekyll posts and
   copies archived article images into the public asset layer.
5. `validate` verifies languages, files, hashes, hotlinks, and translation layers.

The sample configuration covers entries 1, 73, and 199. Use `discover --all`
only after reviewing the sample report and crawl scope. WARC packaging is not
part of this first test implementation; raw response bodies and response
metadata are preserved losslessly so WARC export can be added later.

Sample run:

```powershell
python tools/gamefreak_archive_pipeline.py all --strict
```

Full discovery, after reviewing scope and storage:

```powershell
python tools/gamefreak_archive_pipeline.py discover --all
```

Full resumable capture, extraction, and strict validation:

```powershell
python tools/gamefreak_archive_pipeline.py all --all --delay 0.8 --strict
```

Source anomalies are recorded in `reports/discovery-issues.yml`. A resource
that is unavailable from both the live host and Wayback remains in
`manifest/assets.yml` with `status: unavailable`; validation reports it as a
warning rather than silently omitting it.

Documented source-URL typos may use a bilingual counterpart as a correction.
Those records use `capture_source: source-url-correction` and retain both the
broken `original_url` and the working `substitute_url`.
"""
    write_text(ARCHIVE_ROOT / "README.md", readme)


def run_all(args: argparse.Namespace) -> None:
    write_archive_readme()
    discover(args)
    fetch_assets(args)
    extract(args)
    publish_site_pages(args)
    validate(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage", choices=["discover", "fetch", "extract", "publish", "validate", "all"]
    )
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLE_FILE)
    parser.add_argument("--delay", type=float, default=0.8, help="Delay after each network request")
    parser.add_argument("--refresh", action="store_true", help="Refetch existing captures/assets")
    parser.add_argument("--all", action="store_true", help="Discover every archive month")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on validation failure")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.samples = args.samples.resolve()
    write_archive_readme()
    if args.stage == "discover":
        discover(args)
    elif args.stage == "fetch":
        fetch_assets(args)
    elif args.stage == "extract":
        extract(args)
    elif args.stage == "publish":
        publish_site_pages(args)
    elif args.stage == "validate":
        validate(args)
    else:
        run_all(args)


if __name__ == "__main__":
    main()
