"""Export the current OCR translation workbench state as a portable case ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

from PIL import Image

from export_wordpress_bilingual import SCRIPT, STYLE, utterances, workbench_article_html


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_box(value: object) -> list[int]:
    if isinstance(value, list) and len(value) == 4:
        return [round(float(part)) for part in value]
    parts = [part.strip() for part in str(value or "").strip("[] ").split(",") if part.strip()]
    if len(parts) != 4:
        return []
    try:
        return [round(float(part)) for part in parts]
    except ValueError:
        return []


def segment_boxes(segment: dict) -> list[list[int]]:
    result = []
    for value in segment.get("scanBoxes") or segment.get("scan_boxes") or []:
        box = parse_box(value)
        if box and box not in result:
            result.append(box)
    primary = parse_box(segment.get("scanBox") or segment.get("scan_box"))
    if primary and primary not in result:
        result.insert(0, primary)
    return result


def entry_from_segment(segment: dict, index: int) -> dict:
    boxes = segment_boxes(segment)
    kind = str(segment.get("kind") or "text")
    region_type = str(segment.get("regionType") or segment.get("region_type") or kind)
    if kind == "image" or region_type == "image":
        entry_type = "image"
    elif kind == "caption" or region_type == "caption":
        entry_type = "caption"
    else:
        entry_type = region_type or "text"
    region_id = str(segment.get("regionId") or segment.get("region_id") or f"segment-{index + 1}")
    members = [
        {
            "box": box,
            "region_id": region_id if member_index == 0 else f"{region_id}-box-{member_index + 1}",
            "page_index": int(segment.get("scanPage") or segment.get("scan_page") or 0),
            "order": int(segment.get("regionOrder") or segment.get("order") or index + 1),
        }
        for member_index, box in enumerate(boxes)
    ]
    return {
        "page_index": int(segment.get("scanPage") or segment.get("scan_page") or 0),
        "page_name": str(segment.get("pageName") or segment.get("page_name") or ""),
        "source_image": "public/assets/scan.jpg",
        "crop": str(segment.get("resolvedImagePath") or segment.get("imagePath") or segment.get("image") or ""),
        "region_id": region_id,
        "group_id": str(segment.get("groupId") or segment.get("group_id") or ""),
        "image_ref": str(segment.get("captionFor") or segment.get("caption_for") or ""),
        "writing_direction": str(segment.get("writingDirection") or segment.get("writing_direction") or "auto"),
        "type": entry_type,
        "region_type": region_type,
        "speaker": str(segment.get("speaker") or f"段落 {index + 1}"),
        "order": int(segment.get("regionOrder") or segment.get("order") or index + 1),
        "box": boxes[0] if boxes else [],
        "members": members or [{"box": [], "region_id": region_id}],
        "original_raw": str(segment.get("original") or ""),
        "original_corrected": str(segment.get("original") or ""),
        "translation": str(segment.get("translation") or ""),
        "correction_note": "\n".join(str(value) for value in (segment.get("comments") or []) if value),
        "status": str(segment.get("status") or "ocr"),
        "alt": str(segment.get("imageAlt") or segment.get("alt") or segment.get("speaker") or "杂志图片"),
    }


def yaml_scalar(value: object) -> str:
    return json.dumps(str(value or ""), ensure_ascii=False)


def block(lines: list[str], key: str, value: object) -> None:
    lines.append(f"    {key}: |-")
    text = str(value or "")
    if not text:
        lines.append("      ")
    else:
        lines.extend(f"      {line}" for line in text.splitlines())


def translation_yaml(entries: list[dict], scan_name: str) -> str:
    lines = ["translation_segments:"]
    for entry in entries:
        lines.extend([
            f"  - speaker: {yaml_scalar(entry['speaker'])}",
            f"    kind: {yaml_scalar('image' if entry['type'] == 'image' else 'caption' if entry['type'] == 'caption' else 'text')}",
            f"    status: {yaml_scalar(entry.get('status'))}",
            f"    scan_page: {entry['page_index']}",
            f"    page_name: {yaml_scalar(entry.get('page_name'))}",
            f"    source_image: {yaml_scalar('public/assets/' + scan_name)}",
            f"    region_type: {yaml_scalar(entry.get('region_type'))}",
            f"    order: {entry['order']}",
            f"    region_id: {yaml_scalar(entry['region_id'])}",
        ])
        if entry.get("group_id"):
            lines.append(f"    group_id: {yaml_scalar(entry['group_id'])}")
        if entry.get("image_ref"):
            lines.append(f"    caption_for: {yaml_scalar(entry['image_ref'])}")
        boxes = [member.get("box") for member in entry.get("members") or [] if len(member.get("box") or []) == 4]
        if len(boxes) > 1:
            lines.append("    scan_boxes:")
            lines.extend(f"      - [{', '.join(str(value) for value in box)}]" for box in boxes)
        elif boxes:
            lines.append(f"    scan_box: [{', '.join(str(value) for value in boxes[0])}]")
        if entry["type"] == "image":
            lines.append(f"    image: {yaml_scalar(entry.get('public_image'))}")
            lines.append(f"    alt: {yaml_scalar(entry.get('alt'))}")
        else:
            block(lines, "original", entry.get("original_corrected"))
            block(lines, "translation", entry.get("translation"))
        if entry.get("correction_note"):
            lines.append(f"    comment: {yaml_scalar(entry['correction_note'])}")
    return "\n".join(lines) + "\n"


def qa(entries: list[dict], scan_path: Path) -> tuple[list[str], dict]:
    issues = []
    text_entries = [entry for entry in entries if entry["type"] not in {"image", "caption"}]
    pending = [entry["region_id"] for entry in text_entries if entry["translation"].strip() in {"", "待翻译"}]
    if pending:
        issues.append(f"仍有 {len(pending)} 段待翻译：{', '.join(pending)}")
    missing_boxes = [entry["region_id"] for entry in text_entries if not segment_boxes({"scanBoxes": [member.get('box') for member in entry.get('members') or []]})]
    if missing_boxes:
        issues.append(f"缺少原图坐标：{', '.join(missing_boxes)}")
    alignment = []
    for entry in text_entries:
        original_text = entry["original_corrected"]
        translation_text = entry["translation"]
        has_interview_turns = bool(
            re.search(r"(?m)^(?:[—―]{2}|蒼井\s+)", original_text)
            and re.search(r"(?m)^(?:[—―]{2}|[苍蒼]井[：:])", translation_text)
        )
        if not has_interview_turns:
            continue
        ja_count = len(utterances(original_text, "ja"))
        zh_count = len(utterances(translation_text, "zh"))
        if translation_text.strip() not in {"", "待翻译"} and ja_count != zh_count:
            alignment.append(f"{entry['region_id']}({ja_count}/{zh_count})")
    if alignment:
        issues.append("日中轮次不一致：" + ", ".join(alignment))
    with Image.open(scan_path) as image:
        size = list(image.size)
    return issues, {
        "segment_count": len(entries),
        "text_count": len(text_entries),
        "image_count": sum(1 for entry in entries if entry["type"] == "image"),
        "caption_count": sum(1 for entry in entries if entry["type"] == "caption"),
        "pending_count": len(pending),
        "alignment_issues": alignment,
        "scan_size": size,
    }


def portability_issues(root: Path) -> list[str]:
    problems = []
    secret = re.compile(r"(?i)(?:api[_-]?key|authorization)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{16,}")
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"(?:^|[\"'\s])[A-Z]:\\", text):
            problems.append(f"本机绝对路径：{path.relative_to(root).as_posix()}")
        if secret.search(text):
            problems.append(f"疑似敏感信息：{path.relative_to(root).as_posix()}")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a workbench WordPress preview and case ZIP.")
    parser.add_argument("--payload", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    payload_path = Path(args.payload).resolve()
    out_dir = Path(args.out).resolve()
    if out_dir.exists() or out_dir.with_suffix(".zip").exists():
        raise SystemExit(f"Refusing to overwrite export: {out_dir}")
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    source_image = Path(str(payload.get("resolvedSourceImage") or "")).resolve()
    if not source_image.is_file():
        raise SystemExit("The original scan image is unavailable; select its folder in the workbench first.")

    public_dir = out_dir / "public"
    assets_dir = public_dir / "assets"
    figures_dir = assets_dir / "figures"
    data_dir = out_dir / "data"
    docs_dir = out_dir / "docs"
    for folder in (figures_dir, data_dir, docs_dir):
        folder.mkdir(parents=True, exist_ok=True)
    scan_name = "scan" + source_image.suffix.lower()
    public_scan = assets_dir / scan_name
    shutil.copy2(source_image, public_scan)

    entries = [entry_from_segment(segment, index) for index, segment in enumerate(payload.get("segments") or [])]
    for entry in entries:
        if entry["type"] != "image":
            continue
        source = Path(str(entry.get("crop") or ""))
        if source.is_file():
            target = figures_dir / source.name
            shutil.copy2(source, target)
            entry["crop"] = str(target)
            entry["public_image"] = f"public/assets/figures/{target.name}"
        else:
            entry["public_image"] = ""

    issues, stats = qa(entries, public_scan)
    workflow = payload.get("workflow") or {}
    portable_payload = {
        "meta": payload.get("meta") or {},
        "segments": payload.get("segments") or [],
        "workflow": {
            "sourceQueue": Path(str(workflow.get("sourceQueue") or "")).name,
            "projectOutput": Path(str(workflow.get("projectOutputDir") or "")).name,
            "exportedAt": workflow.get("exportedAt") or "",
        },
    }
    for segment in portable_payload["segments"]:
        segment.pop("sourceImage", None)
        segment.pop("resolvedImagePath", None)
        if segment.get("kind") == "image":
            filename = Path(str(segment.get("imagePath") or "")).name
            segment["imagePath"] = f"public/assets/figures/{filename}" if filename else ""
    write_json(data_dir / "workbench-export.json", portable_payload)
    portable_entries = json.loads(json.dumps(entries, ensure_ascii=False))
    for entry in portable_entries:
        entry["source_image"] = f"public/assets/{scan_name}"
        if entry["type"] == "image":
            entry["crop"] = entry.get("public_image") or ""
    write_json(data_dir / "translation-entries.json", portable_entries)
    (data_dir / "translation-segments.yml").write_text(translation_yaml(entries, scan_name), encoding="utf-8")

    preview_article = workbench_article_html(payload, entries, public_scan, "./assets")
    preview = (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{payload.get("meta", {}).get("title") or "OCR 日中对照稿"}</title>'
        + STYLE + "</head><body>" + preview_article + SCRIPT + "</body></html>"
    )
    (public_dir / "index.html").write_text(preview, encoding="utf-8")
    wordpress = STYLE + "\n" + workbench_article_html(payload, entries, public_scan, "{{WORDPRESS_MEDIA_BASE}}") + "\n" + SCRIPT + "\n"
    (public_dir / "wordpress-paste.html").write_text(wordpress, encoding="utf-8")

    report = [
        "# WordPress 工作台导出检查", "",
        f"- 结果：{'需要复核' if issues else '通过'}",
        f"- 扫描图：{stats['scan_size'][0]} × {stats['scan_size'][1]}",
        f"- 段落：{stats['segment_count']}；文字 {stats['text_count']}；图片 {stats['image_count']}；图注 {stats['caption_count']}",
        f"- 待翻译：{stats['pending_count']}", "",
        "## 问题", "",
    ]
    report.extend(f"- {issue}" for issue in issues)
    if not issues:
        report.append("- 未发现阻止预览或打包的问题。")
    report.extend(["", "## 上线前", "", "- 替换 WordPress 媒体目录占位符。", "- 人工复核专有名词。", "- 确认扫描页公开使用权限。"])
    (docs_dir / "qa-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    write_json(out_dir / "case.json", {
        "schema_version": 1,
        "title": payload.get("meta", {}).get("title") or "OCR 日中对照稿",
        "status": "review" if issues else "ready_for_final_proofread",
        "entrypoint": "public/index.html",
        "wordpress_fragment": "public/wordpress-paste.html",
        "translation_segments": "data/translation-segments.yml",
        "qa_report": "docs/qa-report.md",
        "stats": stats,
        "issues": issues,
    })
    (out_dir / "README.md").write_text(
        "# OCR 翻译 WordPress 开发案例\n\n上传整个目录后从 `public/index.html` 进入。WordPress 使用 `public/wordpress-paste.html`，并把 `{{WORDPRESS_MEDIA_BASE}}` 替换为媒体目录 URL。\n",
        encoding="utf-8",
    )
    portable_problems = portability_issues(out_dir)
    if portable_problems:
        raise SystemExit("Portability check failed: " + "; ".join(portable_problems))
    checksum_paths = sorted(path for path in out_dir.rglob("*") if path.is_file())
    (out_dir / "CHECKSUMS.sha256").write_text(
        "\n".join(f"{sha256(path)}  {path.relative_to(out_dir).as_posix()}" for path in checksum_paths) + "\n",
        encoding="utf-8",
    )
    archive = shutil.make_archive(str(out_dir), "zip", root_dir=out_dir.parent, base_dir=out_dir.name)
    print(json.dumps({"out": str(out_dir), "zip": archive, "issues": issues, "stats": stats}, ensure_ascii=False))


if __name__ == "__main__":
    main()
