"""Publish translated scan-library runs as Jekyll scan-translation posts."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def unique_page_rows(manifest: dict) -> list[dict]:
    rows = []
    for page in manifest.get("pages") or []:
        # A source spread can produce two Web pages (for example page034-a/b).
        # Keep both outputs in exactly the order used by the OCR page_index.
        for web in page.get("outputs") or []:
            if web.get("profile") != "web":
                continue
            file_name = str(web.get("path") or Path(str(web.get("relative_path") or "")).name)
            rows.append({
                "name": file_name,
                "file": str(web.get("relative_path") or f"web/{file_name}"),
            })
    return rows


def copy_pages(prep_dir: Path, asset_dir: Path, manifest: dict) -> tuple[list[dict], dict[str, int]]:
    pages = []
    page_index = {}
    for index, row in enumerate(unique_page_rows(manifest)):
        source = prep_dir / row["file"]
        if not source.exists():
            raise FileNotFoundError(source)
        target = asset_dir / source.name
        shutil.copy2(source, target)
        page = {"image": f"/assets/images/scan-archive/{asset_dir.name}/{target.name}", "label": target.stem}
        pages.append(page)
        page_index[row["name"]] = index
        page_index[target.name] = index
    return pages, page_index


def normalize_id(page_index: int, region_id: object) -> str:
    return f"p{page_index + 1:03d}-{str(region_id or 'region')}"


def build_segments(entries: list[dict], asset_dir: Path, queue_regions: dict[tuple[str, str], dict]) -> list[dict]:
    segments = []
    for item in sorted(entries, key=lambda value: (int(value.get("page_index") or 0), int(value.get("order") or 0))):
        page_index = int(item.get("page_index") or 0)
        region_id = normalize_id(page_index, item.get("region_id"))
        kind = "image" if item.get("type") == "image" else "caption" if item.get("type") == "caption" else "text"
        original = str(item.get("original_corrected") or item.get("original_raw") or "").strip()
        translation = str(item.get("translation") or "").strip()
        warnings = [str(value) for value in item.get("reliability_warnings") or [] if value]
        review_flags = [str(value) for value in item.get("review_flags") or [] if value]
        queue_item = queue_regions.get((str(item.get("page_name") or ""), str(item.get("region_id") or "")), {})
        if queue_item.get("status") == "review":
            warnings.extend(str(reason.get("code")) for reason in queue_item.get("reasons") or [] if reason.get("code"))
        comments = [str(value) for value in (item.get("correction_note"), *warnings, *review_flags) if value]
        if not translation and kind != "image":
            translation = "（待人工复核：暂无可靠译文）"
            comments.append("该区域未生成可靠中文译文，保留在人工返工队列。")
        row = {
            "speaker": str(item.get("speaker") or item.get("type") or "区域"),
            "type": "paragraph" if kind != "image" else "image",
            "kind": kind,
            "region_type": str(item.get("type") or "text"),
            "region_id": region_id,
            "order": int(item.get("order") or 0),
            "scan_page": page_index,
            "scan_box": [int(value) for value in item.get("box") or []],
            "writing_direction": str(item.get("writing_direction") or "auto"),
            "review_status": "review" if queue_item.get("status") == "review" or warnings or review_flags else "ready",
        }
        if item.get("group_id"):
            row["group_id"] = str(item["group_id"])
        if item.get("image_ref"):
            row["caption_for"] = normalize_id(page_index, item["image_ref"])
        if comments:
            row["comment"] = "；".join(dict.fromkeys(comments))
        if kind == "image":
            crop = Path(str(item.get("crop") or ""))
            if crop.exists():
                target = asset_dir / "regions" / f"p{page_index + 1:03d}-{crop.name}"
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(crop, target)
                row["image"] = f"/assets/images/scan-archive/{asset_dir.name}/regions/{target.name}"
                row["alt"] = str(item.get("speaker") or "杂志图片")
        else:
            row["original"] = original
            row["translation"] = translation
        segments.append(row)
    return segments


def write_post(path: Path, metadata: dict) -> None:
    frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, default_flow_style=False).strip()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n", encoding="utf-8")


def publish_one(args: argparse.Namespace) -> None:
    prep_dir = Path(args.prep_dir).resolve()
    ocr_dir = Path(args.ocr_dir).resolve()
    asset_dir = (ROOT / "assets" / "images" / "scan-archive" / args.slug).resolve()
    manifest = json.loads((prep_dir / "scan-manifest.json").read_text(encoding="utf-8"))
    entries = json.loads((ocr_dir / "llm-corrections.json").read_text(encoding="utf-8"))
    queue_path = ocr_dir / "project-queue.json"
    queue_regions = {}
    if queue_path.exists():
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        queue_regions = {
            (str(row.get("page_name") or ""), str(row.get("region_id") or "")): row
            for row in queue.get("regions") or []
        }
    asset_dir.mkdir(parents=True, exist_ok=True)
    segments = build_segments(entries, asset_dir, queue_regions)
    pending = sum(1 for item in segments if item.get("review_status") == "review")
    metadata = {
        # Docs/GitHub Pages uses a lightweight reading view. Full-page scans
        # remain in the local prepared output for the main-site publication.
        "layout": "parallel-translation",
        "title": args.title,
        "title_ja": args.title_ja,
        "date": args.date,
        "categories": ["访谈翻译", "扫描存档"],
        "tags": ["CONTINUE", "扫描存档", "Qwen-VL-OCR", "DeepSeek", "日中对照"],
        "kicker": "SCAN ARCHIVE · INTERVIEW",
        "publication": "CONTINUE",
        "issue": args.issue,
        "interviewee": args.interviewee,
        "translator": "Qwen-VL-OCR 识别 / DeepSeek 校对翻译",
        "summary": args.summary,
        "source_pages": f"{len(manifest.get('pages') or [])} 页（Docs 仅展示插图裁片）",
        "original_lang": "ja",
        "translation_lang": "zh-CN",
        "parallel_view": "translation",
        "published": True,
        "workflow": {
            "scan": "done",
            "preprocess": "done",
            "ocr": "done",
            "translation": "machine-translated",
            "proofreading": "deepseek-proofread",
            "published": "online",
        },
        "review_scope": "机器校对与翻译已完成；风险区域保留人工返工标记。",
        "pending_review_regions": pending,
        "translation_segments": segments,
    }
    write_post(ROOT / "_posts" / args.post_name, metadata)
    image_count = sum(1 for item in segments if item.get("kind") == "image")
    print(json.dumps({"post": str(ROOT / "_posts" / args.post_name), "image_crops": image_count, "segments": len(segments), "pending_review": pending}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prep-dir", required=True)
    parser.add_argument("--ocr-dir", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--post-name", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--title-ja", default="")
    parser.add_argument("--issue", required=True)
    parser.add_argument("--interviewee", default="杂志采访")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--date", default="2026-08-29")
    publish_one(parser.parse_args())


if __name__ == "__main__":
    main()
