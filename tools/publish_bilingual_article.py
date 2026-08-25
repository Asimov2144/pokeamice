"""Publish one bilingual magazine article to both channels from a single source.

Reads the corrected OCR (`llm-corrections.json`) plus an article metadata file
and renders each channel from the same entries:

    docs      -> _posts/<date>-<slug>.md   (Jekyll, bilingual segments)
    wordpress -> /wp/v2/posts              (draft, bilingual HTML + media)

Each channel keeps its own content hash and sync record under `.publish-state/`,
so a change that only affects one channel does not dirty the other and a repeat
run with unchanged content is a no-op. WordPress updates stop rather than
overwrite when the remote post was edited outside this tool.

Credentials come from the environment and are never written to disk or logs:

    WP_BASE_URL       https://pokeamice.com
    WP_USER           the publishing account's login
    WP_APP_PASSWORD   an Application Password created in WordPress
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml
from PIL import Image

from export_wordpress_bilingual import SCRIPT, STYLE, esc, utterances

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / ".publish-state"
USER_AGENT = "pokeamice-publisher/1"


# --------------------------------------------------------------------------- #
# Source model
# --------------------------------------------------------------------------- #

def load_entries(corrections: Path) -> list[dict]:
    """Return publishable entries in reading order, dropping empty ones."""
    entries = json.loads(corrections.read_text(encoding="utf-8"))
    entries.sort(key=lambda item: (item.get("order") or 0, item.get("region_id") or ""))
    kept = []
    for item in entries:
        if item.get("type") == "image":
            kept.append(item)
            continue
        if not (item.get("original_corrected") or item.get("original_raw") or "").strip():
            continue
        kept.append(item)
    return kept


def entry_kind(item: dict) -> str:
    kind = item.get("type")
    if kind == "image":
        return "image"
    if kind == "caption":
        return "caption"
    return "text"


def original_of(item: dict) -> str:
    return (item.get("original_corrected") or item.get("original_raw") or "").strip()


def translation_of(item: dict) -> str:
    return (item.get("translation") or "").strip()


def content_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def preflight(entries: list[dict], meta: dict) -> list[str]:
    """Collect blocking problems; an empty list means the article may publish."""
    problems = []
    for field in ("article_id", "slug", "date", "title"):
        if not meta.get(field):
            problems.append(f"metadata is missing required field: {field}")
    if not entries:
        problems.append("no publishable entries found in the corrections file")
    for item in entries:
        if entry_kind(item) == "image":
            continue
        region = item.get("region_id") or f"order {item.get('order')}"
        if not translation_of(item):
            problems.append(f"region {region} has no translation")
        for warning in item.get("reliability_warnings") or []:
            problems.append(f"region {region} carries a reliability warning: {warning}")
        for flag in item.get("review_flags") or []:
            problems.append(f"region {region} carries an unresolved review flag: {flag}")
    return problems


# --------------------------------------------------------------------------- #
# docs channel
# --------------------------------------------------------------------------- #

def _block_scalar(dumper, value):
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


class _FrontMatterDumper(yaml.SafeDumper):
    pass


class FlowList(list):
    """A list rendered inline, matching how hand-written posts write boxes."""


_FrontMatterDumper.add_representer(str, _block_scalar)
_FrontMatterDumper.add_representer(
    FlowList,
    lambda dumper, value: dumper.represent_sequence("tag:yaml.org,2002:seq", value, flow_style=True),
)


def docs_segments(entries: list[dict], figures: dict[str, str]) -> list[dict]:
    """Build segments both docs layouts understand.

    scan-translation dispatches on `kind`/`region_type` while
    parallel-translation dispatches on `type`, so every segment carries all
    three. Image regions are only emitted when the metadata maps them to a
    published asset; otherwise the docs page stays text-only, which is what the
    static archive is for.
    """
    segments = []
    for item in entries:
        kind = entry_kind(item)
        region_id = item.get("region_id") or ""
        if kind == "image" and not figures.get(region_id):
            continue
        segment = {
            "speaker": item.get("speaker") or item.get("type") or "正文",
            "type": "image" if kind == "image" else "paragraph",
            "kind": kind,
            "region_type": item.get("type") or "body",
            "region_id": region_id,
            "order": item.get("order") or len(segments) + 1,
            "scan_page": item.get("page_index") or 0,
        }
        box = item.get("box")
        if isinstance(box, list) and len(box) == 4:
            segment["scan_box"] = FlowList(int(round(value)) for value in box)
        if item.get("writing_direction"):
            segment["writing_direction"] = item["writing_direction"]
        if item.get("image_ref") and figures.get(item["image_ref"]):
            segment["caption_for"] = item["image_ref"]
        if kind == "image":
            segment["image"] = figures[region_id]
            segment["alt"] = item.get("note") or "杂志内页图片"
        else:
            segment["original"] = original_of(item)
            segment["translation"] = translation_of(item)
        note = item.get("correction_note") or item.get("note")
        if note:
            segment["comment"] = note
        segments.append(segment)
    return segments


def render_docs_markdown(entries: list[dict], meta: dict) -> str:
    docs_meta = meta.get("docs") or {}
    front: dict = {
        "layout": docs_meta.get("layout", "parallel-translation"),
        "title": meta["title"],
        "date": str(meta["date"]),
        "categories": meta.get("categories") or ["访谈翻译", "扫描存档"],
        "tags": meta.get("tags") or [],
        "archive_type": "scan_translation",
        "source": {
            "title": meta.get("source_title") or f"{meta.get('publication', '')} {meta.get('issue', '')}".strip(),
            "language": meta.get("original_lang", "ja"),
            "source_type": "magazine",
        },
        "workflow": {
            "scan": "done",
            "preprocess": "done",
            "ocr": "done",
            "translation": "draft",
            "proofreading": "pending",
            "published": "draft",
        },
        "original_lang": meta.get("original_lang", "ja"),
        "translation_lang": meta.get("translation_lang", "zh-CN"),
    }
    for key in ("kicker", "publication", "issue", "interviewee", "translator", "summary"):
        if meta.get(key):
            front[key] = meta[key]
    if meta.get("title_ja"):
        front["title_ja"] = meta["title_ja"]
    if meta.get("source_pages"):
        front["source_pages"] = meta["source_pages"]

    scan_image = docs_meta.get("scan_image")
    if scan_image:
        front["scan_pages"] = [{
            "image": scan_image,
            "label": docs_meta.get("scan_label") or "原刊页",
            "caption": docs_meta.get("scan_caption") or "",
        }]
        front["box_editor"] = False
    front["translation_segments"] = docs_segments(entries, docs_meta.get("figures") or {})

    body = docs_meta.get("note") or (
        "本文由本地 OCR 与翻译流水线生成，正文与主站版本同源。"
    )
    front_matter = yaml.dump(
        front,
        Dumper=_FrontMatterDumper,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=4096,
    )
    return f"---\n{front_matter}---\n\n{body}\n"


def docs_post_path(meta: dict) -> Path:
    return ROOT / "_posts" / f"{meta['date']}-{meta['slug']}.md"


# --------------------------------------------------------------------------- #
# WordPress channel
# --------------------------------------------------------------------------- #

def paired_rows(item: dict) -> str:
    originals = utterances(original_of(item), "ja")
    translations = utterances(translation_of(item), "zh")
    rows = []
    for index in range(max(len(originals), len(translations), 1)):
        original = originals[index] if index < len(originals) else ""
        translation = translations[index] if index < len(translations) else ""
        rows.append(
            '<div class="pm-line">'
            f'<div class="pm-cell" lang="ja"><span class="pm-tag">日本語</span><p>{esc(original)}</p></div>'
            f'<div class="pm-cell" lang="zh-CN"><span class="pm-tag">中文</span><p>{esc(translation)}</p></div>'
            "</div>"
        )
    return "\n".join(rows)


def normalized_boxes(item: dict, width: int, height: int) -> list[list[float]]:
    result = []
    for member in item.get("members") or [item]:
        box = member.get("box") or []
        if len(box) != 4 or not width or not height:
            continue
        result.append([
            round(box[0] / width, 5),
            round(box[1] / height, 5),
            round(box[2] / width, 5),
            round(box[3] / height, 5),
        ])
    return result


SEGMENT_LABELS = {
    "body": "访谈正文",
    "lead": "导语",
    "note": "补充说明",
    "caption": "图注",
    "title": "标题",
}


def wp_segment(item: dict, index: int, width: int, height: int) -> str:
    label = SEGMENT_LABELS.get(str(item.get("type")), item.get("speaker") or "正文")
    return (
        f'<section class="pm-segment" tabindex="0" data-boxes="{esc(json.dumps(normalized_boxes(item, width, height)))}">\n'
        f'  <div class="pm-segment-head"><span class="pm-order">{index}</span>'
        f'<span class="pm-label">{esc(label)}</span></div>\n'
        f"  {paired_rows(item)}\n"
        "</section>"
    )


def wp_figure(item: dict, captions: list[dict], index: int, src: str, width: int, height: int) -> str:
    pairs = []
    for caption in captions:
        pairs.append(
            '<div class="pm-caption">'
            f'<div lang="ja"><span class="pm-tag">图注原文</span>{esc(original_of(caption))}</div>'
            f'<div lang="zh-CN"><span class="pm-tag">图注译文</span>{esc(translation_of(caption))}</div>'
            "</div>"
        )
    return (
        f'<section class="pm-segment" tabindex="0" data-boxes="{esc(json.dumps(normalized_boxes(item, width, height)))}">\n'
        f'  <div class="pm-segment-head"><span class="pm-order">{index}</span>'
        '<span class="pm-label">杂志图片与图注</span></div>\n'
        f'  <figure class="pm-figure"><img src="{esc(src)}" alt="{esc(item.get("note") or "杂志内页图片")}" loading="lazy">'
        + "".join(pairs)
        + "</figure>\n</section>"
    )


def render_wordpress_html(entries: list[dict], meta: dict, scan_src: str,
                          scan_size: tuple[int, int], figure_urls: dict[str, str]) -> str:
    width, height = scan_size
    captions_by_image: dict[str, list[dict]] = {}
    for item in entries:
        if entry_kind(item) == "caption" and item.get("image_ref"):
            captions_by_image.setdefault(item["image_ref"], []).append(item)
    consumed = {id(caption) for group in captions_by_image.values() for caption in group}

    blocks = []
    number = 1
    for item in entries:
        if id(item) in consumed:
            continue
        if entry_kind(item) == "image":
            src = figure_urls.get(item.get("region_id") or "", "")
            if not src:
                continue
            blocks.append(wp_figure(item, captions_by_image.get(item.get("region_id"), []),
                                    number, src, width, height))
        else:
            blocks.append(wp_segment(item, number, width, height))
        number += 1

    header_meta = " · ".join(part for part in [
        meta.get("publication"), meta.get("issue"), meta.get("translator"),
    ] if part)
    source_line = "来源：{} {}{}。{}".format(
        meta.get("publication", ""),
        meta.get("issue", ""),
        f"，页 {meta['source_pages']}" if meta.get("source_pages") else "",
        meta.get("pipeline_note", "OCR 与初译由本地流水线生成，发布前经人工复核。"),
    )
    scan_pane = ""
    if scan_src:
        scan_pane = (
            '<aside class="pm-scan"><div class="pm-scan-stage">'
            f'<img src="{esc(scan_src)}" alt="{esc(meta["title"])}原刊扫描页">'
            '</div><p class="pm-scan-note">点击右侧段落可在原扫描页上定位对应文字区域。</p></aside>'
        )
    return f"""
<article class="pm-interview">
  <header class="pm-header">
    <div><div class="pm-kicker">{esc(meta.get('kicker', 'SCAN ARCHIVE · INTERVIEW'))}</div>
    <h1>{esc(meta.get('title_ja') or meta['title'])}</h1>
    <div class="pm-meta">{esc(header_meta)}</div></div>
  </header>
  <p class="pm-summary">{esc(meta.get('summary', ''))}</p>
  <nav class="pm-tools" aria-label="阅读显示"><span class="pm-label">阅读方式</span>\
<button type="button" data-view="both" aria-pressed="true">日中对照</button>\
<button type="button" data-view="ja" aria-pressed="false">只看日文</button>\
<button type="button" data-view="zh" aria-pressed="false">只看中文</button></nav>
  <div class="pm-layout">
    {scan_pane}
    <main class="pm-reading">{"".join(blocks)}
    <p class="pm-source-meta">{esc(source_line)}</p></main>
  </div>
</article>
""".strip()


# --------------------------------------------------------------------------- #
# WordPress REST client
# --------------------------------------------------------------------------- #

class WordPressError(RuntimeError):
    pass


class WordPress:
    def __init__(self, base_url: str, user: str, app_password: str) -> None:
        self.base = base_url.rstrip("/") + "/wp-json/wp/v2"
        token = base64.b64encode(f"{user}:{app_password}".encode("utf-8")).decode("ascii")
        self.auth = f"Basic {token}"

    def _request(self, method: str, path: str, *, data: bytes | None = None,
                 headers: dict | None = None) -> dict:
        request = urllib.request.Request(
            self.base + path,
            data=data,
            method=method,
            headers={
                "Authorization": self.auth,
                "User-Agent": USER_AGENT,
                **(headers or {}),
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:400]
            raise WordPressError(f"{method} {path} -> HTTP {exc.code}: {detail}") from None
        except urllib.error.URLError as exc:
            raise WordPressError(f"{method} {path} -> {exc.reason}") from None
        return json.loads(body) if body else {}

    def get_json(self, path: str) -> dict:
        return self._request("GET", path)

    def post_json(self, path: str, payload: dict) -> dict:
        return self._request(
            "POST", path,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
        )

    def upload_media(self, file: Path, title: str, alt_text: str) -> dict:
        mime = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
        created = self._request(
            "POST", "/media",
            data=file.read_bytes(),
            headers={
                "Content-Type": mime,
                "Content-Disposition": f'attachment; filename="{file.name}"',
            },
        )
        if title or alt_text:
            self.post_json(f"/media/{created['id']}", {"title": title, "alt_text": alt_text})
        return created

    def whoami(self) -> dict:
        return self.get_json("/users/me?context=edit")


def ensure_media(client: WordPress, file: Path, state: dict, title: str,
                 alt_text: str, dry_run: bool) -> str:
    """Upload a file once; reuse the remote URL while its bytes are unchanged."""
    digest = file_hash(file)
    known = state.setdefault("media", {}).get(digest)
    if known:
        return known["url"]
    if dry_run:
        return f"(would upload {file.name})"
    created = client.upload_media(file, title, alt_text)
    record = {"id": created["id"], "url": created["source_url"], "file": file.name}
    state["media"][digest] = record
    return record["url"]


# --------------------------------------------------------------------------- #
# Publication state
# --------------------------------------------------------------------------- #

def load_state(article_id: str) -> dict:
    path = STATE_DIR / f"{article_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"article_id": article_id, "targets": {}, "media": {}}


def save_state(state: dict) -> Path:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = STATE_DIR / f"{state['article_id']}.json"
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# Channels
# --------------------------------------------------------------------------- #

def publish_docs(entries: list[dict], meta: dict, state: dict, args) -> dict:
    markdown = render_docs_markdown(entries, meta)
    digest = content_hash(markdown)
    record = state["targets"].setdefault("docs", {"status": "not-published"})
    path = docs_post_path(meta)
    if record.get("content_hash") == digest and path.exists() and not args.force:
        print(f"docs      unchanged (hash {digest[:12]}), skipping")
        return record
    if args.dry_run:
        print(f"docs      would write {path.relative_to(ROOT)} ({len(markdown)} bytes)")
        return record
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    record.update({
        "status": "built",
        "content_hash": digest,
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "built_at": now(),
    })
    print(f"docs      wrote {record['path']} (hash {digest[:12]})")
    return record


def git_publish_docs(record: dict, meta: dict, args) -> None:
    path = record.get("path")
    if not path:
        return
    changed = subprocess.run(["git", "status", "--porcelain", "--", path],
                             cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if not changed:
        print("docs      no git change to commit")
        return
    if args.dry_run:
        print(f"docs      would commit and push {path}")
        return
    message = f"publish(docs): {meta['slug']} at content {record['content_hash'][:12]}"
    subprocess.run(["git", "add", "--", path], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "-q", "origin", "HEAD"], cwd=ROOT, check=True)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    record.update({"status": "published", "commit": sha, "published_at": now()})
    print(f"docs      pushed {sha[:8]}")


def write_wordpress_preview(entries: list[dict], meta: dict, out: Path, scan_image: str) -> None:
    """Render the WordPress fragment locally so it can be reviewed before upload.

    Media points at the local files rather than the media library, so this is a
    faithful preview of layout and text but not of the final asset URLs.
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    scan_size = (0, 0)
    scan_src = ""
    if scan_image:
        path = Path(scan_image).resolve()
        if path.exists():
            with Image.open(path) as image:
                scan_size = image.size
            scan_src = path.as_uri()
    figure_urls = {}
    for item in entries:
        if entry_kind(item) != "image":
            continue
        crop = Path(str(item.get("crop") or ""))
        if crop.exists():
            figure_urls[item.get("region_id") or ""] = crop.resolve().as_uri()
    article = render_wordpress_html(entries, meta, scan_src, scan_size, figure_urls)
    out.write_text(
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{esc(meta['title'])}｜WordPress 预览</title>{STYLE}</head><body>"
        f"{article}{SCRIPT}</body></html>",
        encoding="utf-8",
    )
    print(f"wordpress preview written to {out}")


def publish_wordpress(entries: list[dict], meta: dict, state: dict, args) -> dict:
    record = state["targets"].setdefault("wordpress", {"status": "not-published"})
    wp_meta = meta.get("wordpress") or {}

    base_url = os.getenv("WP_BASE_URL", "").strip()
    user = os.getenv("WP_USER", "").strip()
    password = os.getenv("WP_APP_PASSWORD", "").strip()
    if not (base_url and user and password):
        raise WordPressError(
            "set WP_BASE_URL, WP_USER and WP_APP_PASSWORD before publishing to WordPress"
        )
    client = WordPress(base_url, user, password)

    scan_image = Path(args.scan_image).resolve() if args.scan_image else None
    scan_size = (0, 0)
    scan_src = ""
    if scan_image and scan_image.exists():
        with Image.open(scan_image) as image:
            scan_size = image.size
        scan_src = ensure_media(client, scan_image, state,
                                f"{meta['title']} 原刊扫描页", meta["title"], args.dry_run)

    figure_urls = {}
    for item in entries:
        if entry_kind(item) != "image":
            continue
        crop = Path(str(item.get("crop") or ""))
        if not crop.exists():
            print(f"wordpress figure for region {item.get('region_id')} is missing: {crop}")
            continue
        figure_urls[item.get("region_id") or ""] = ensure_media(
            client, crop, state, item.get("note") or meta["title"],
            item.get("note") or meta["title"], args.dry_run,
        )

    html_body = STYLE + "\n" + render_wordpress_html(
        entries, meta, scan_src, scan_size, figure_urls) + "\n" + SCRIPT
    digest = content_hash(html_body)

    if record.get("content_hash") == digest and record.get("remote_id") and not args.force:
        print(f"wordpress unchanged (hash {digest[:12]}), skipping")
        return record

    payload = {
        "title": meta["title"],
        "slug": meta["slug"],
        "content": html_body,
        "status": args.wp_status,
        "excerpt": meta.get("summary", ""),
    }
    if wp_meta.get("category_ids"):
        payload["categories"] = wp_meta["category_ids"]
    if wp_meta.get("tag_ids"):
        payload["tags"] = wp_meta["tag_ids"]

    remote_id = record.get("remote_id")
    if remote_id:
        current = client.get_json(f"/posts/{remote_id}?context=edit&_fields=id,modified_gmt,link,status")
        if record.get("remote_modified_gmt") and current.get("modified_gmt") != record["remote_modified_gmt"]:
            record.update({
                "status": "conflict",
                "last_error": (
                    f"remote post {remote_id} was modified at {current.get('modified_gmt')} "
                    f"but this tool last saw {record['remote_modified_gmt']}"
                ),
                "last_attempt_at": now(),
            })
            print(f"wordpress CONFLICT: post {remote_id} changed on the server; not overwriting")
            return record

    if args.dry_run:
        action = f"update post {remote_id}" if remote_id else "create a new draft"
        print(f"wordpress would {action} ({len(html_body)} bytes, hash {digest[:12]})")
        return record

    result = client.post_json(f"/posts/{remote_id}" if remote_id else "/posts", payload)
    record.update({
        "status": "published" if result.get("status") == "publish" else "draft-synced",
        "content_hash": digest,
        "remote_id": result["id"],
        "remote_url": result.get("link", ""),
        "remote_modified_gmt": result.get("modified_gmt"),
        "remote_status": result.get("status"),
        "published_at": now(),
        "last_error": None,
    })
    preview = f"{base_url.rstrip('/')}/?p={result['id']}&preview=true"
    print(f"wordpress {record['status']} post {result['id']} -> {preview}")
    return record


# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--corrections", required=True, help="llm-corrections.json from the OCR pipeline.")
    parser.add_argument("--meta", required=True, help="Article metadata YAML.")
    parser.add_argument("--targets", default="docs,wordpress", help="Comma separated: docs, wordpress.")
    parser.add_argument("--scan-image", default="", help="Original scan page for the WordPress reading pane.")
    parser.add_argument("--wp-status", default="draft", choices=["draft", "publish"],
                        help="WordPress post status; stays draft unless asked otherwise.")
    parser.add_argument("--git-push", action="store_true", help="Commit and push the docs post after writing it.")
    parser.add_argument("--dry-run", action="store_true", help="Render and report without writing or uploading.")
    parser.add_argument("--force", action="store_true", help="Republish even when the content hash is unchanged.")
    parser.add_argument("--skip-preflight", action="store_true", help="Publish despite preflight problems.")
    parser.add_argument("--wp-preview", default="",
                        help="Render the WordPress fragment to this file and exit; needs no credentials.")
    args = parser.parse_args()

    meta = yaml.safe_load(Path(args.meta).read_text(encoding="utf-8"))
    entries = load_entries(Path(args.corrections).resolve())
    targets = {part.strip() for part in args.targets.split(",") if part.strip()}

    problems = preflight(entries, meta)
    if problems:
        print(f"preflight found {len(problems)} problem(s):")
        for problem in problems:
            print(f"  - {problem}")
        if not args.skip_preflight:
            print("refusing to publish; fix these or pass --skip-preflight")
            return 1
        print("continuing anyway because --skip-preflight was given")
    else:
        print(f"preflight ok: {len(entries)} entries ready")

    if args.wp_preview:
        write_wordpress_preview(entries, meta, Path(args.wp_preview), args.scan_image)
        return 0

    state = load_state(meta["article_id"])
    failures = []

    if "docs" in targets:
        record = publish_docs(entries, meta, state, args)
        if args.git_push:
            try:
                git_publish_docs(record, meta, args)
            except subprocess.CalledProcessError as exc:
                record.update({"status": "failed", "last_error": str(exc), "last_attempt_at": now()})
                failures.append(f"docs: {exc}")

    if "wordpress" in targets:
        try:
            publish_wordpress(entries, meta, state, args)
        except WordPressError as exc:
            state["targets"].setdefault("wordpress", {}).update({
                "status": "failed", "last_error": str(exc), "last_attempt_at": now(),
            })
            failures.append(f"wordpress: {exc}")

    if not args.dry_run:
        print(f"state     {save_state(state).relative_to(ROOT)}")

    for failure in failures:
        print(f"FAILED    {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
