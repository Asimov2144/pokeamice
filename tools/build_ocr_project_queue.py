"""Build a semi-automatic review queue from a region OCR output folder."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

try:
    from ocr_rework_loop import build_repair_proposal, text_health
except ModuleNotFoundError:  # Imported by tests/tools as a module from the repo root.
    from tools.ocr_rework_loop import build_repair_proposal, text_health


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


KANA_LINE = re.compile(r"^[\u3040-\u30ff\u31f0-\u31ffー・\s]{1,28}[?？!！、。]?$")
KANJI = re.compile(r"[\u3400-\u9fff]")
KANA = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff]")


def public_output_file(out_dir: Path, subdir: str, filename: str) -> str:
    try:
        public_root = out_dir.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        public_root = out_dir.name
    return f"/{public_root}/{subdir}/{filename}"


def furigana_contamination(text: str) -> dict | None:
    lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
    if len(lines) < 6:
        return None
    kana_lines = [line for line in lines if KANA_LINE.fullmatch(line) and not KANJI.search(line)]
    ratio = len(kana_lines) / len(lines)
    if len(kana_lines) >= 3 and ratio >= 0.14:
        return {
            "code": "furigana_contamination",
            "label": "振假名污染严重",
            "severity": "high" if ratio >= 0.28 else "medium",
            "detail": f"{len(kana_lines)}/{len(lines)} 行疑似为脱离正文的振假名",
            "score": round(ratio, 3),
        }
    return None


def normalize_flags(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip().lower() for item in value if str(item).strip()]
    return [item.strip().lower() for item in str(value or "").split(",") if item.strip()]


def review_reasons(item: dict, ocr_result: dict, text: str) -> list[dict]:
    if item.get("type") == "image":
        return []
    reasons: list[dict] = []
    direction = str(item.get("writing_direction") or "auto").lower()
    layout_flags = normalize_flags(item.get("review_flags"))
    if direction not in {"horizontal", "vertical"} or "direction_uncertain" in layout_flags:
        reasons.append({
            "code": "direction_uncertain",
            "label": "文字方向待确认",
            "severity": "high",
            "detail": "分区模型主动标记了方向疑问" if "direction_uncertain" in layout_flags else "分区没有可靠的横排或竖排标记",
        })

    confidence = item.get("confidence")
    if confidence is not None:
        try:
            value = float(confidence)
            if value < 0.72:
                reasons.append({
                    "code": "low_layout_confidence",
                    "label": "分区置信度偏低",
                    "severity": "medium",
                    "detail": f"自动分区置信度 {value:.2f}",
                    "score": round(value, 3),
                })
        except (TypeError, ValueError):
            pass

    content_mix = str(item.get("content_mix") or "").lower()
    if content_mix in {"mixed", "uncertain"} or any(flag in {"mixed_content", "image_text_mixed"} for flag in layout_flags):
        reasons.append({
            "code": "image_text_mixed",
            "label": "图片与文字可能混框",
            "severity": "high",
            "detail": "建议回到分区工具拆开图片与正文",
        })
    if "boundary_uncertain" in layout_flags:
        reasons.append({
            "code": "boundary_uncertain",
            "label": "选框边界待确认",
            "severity": "medium",
            "detail": "自动分区认为当前区域的边界不够可靠",
        })
    if "page_rotation_uncertain" in layout_flags:
        reasons.append({
            "code": "page_rotation_uncertain",
            "label": "页面方向待确认",
            "severity": "high",
            "detail": "页面预检无法可靠判断 0°/90°/180°/270°，短文字不能自动放行",
        })

    warnings = [str(value) for value in ocr_result.get("quality_warnings") or []]
    recovery = ocr_result.get("recovery") or {}
    coordinate_seen = any(value.startswith("coordinate_dump") for value in warnings)
    coordinate_seen = coordinate_seen or recovery.get("reason") == "coordinate_dump"
    if coordinate_seen:
        recovered = bool(recovery.get("succeeded"))
        reasons.append({
            "code": "coordinate_dump",
            "label": "OCR 曾输出坐标",
            "severity": "medium" if recovered else "high",
            "detail": "已自动恢复，仍建议快速核对" if recovered else "自动恢复未成功，需要重跑 OCR",
        })

    preprocessing = ocr_result.get("preprocessing") or {}
    postprocessing = ocr_result.get("postprocessing") or {}
    original_size = preprocessing.get("original_size") or [0, 0]
    column_count = postprocessing.get("column_count")
    split_succeeded = preprocessing.get("strategy") == "physical_column_split" and int(column_count or 0) >= 2
    if preprocessing.get("too_many_columns") and not preprocessing.get("whole_block_selected"):
        reasons.append({
            "code": "multicolumn_exceeds_limit",
            "label": "多栏数量超过自动拆分上限",
            "severity": "high",
            "detail": f"检测到 {int(preprocessing.get('detected_column_count') or 0)} 栏，需要重新划成较小区域",
        })
    if preprocessing.get("direction_overridden") and not split_succeeded:
        reasons.append({
            "code": "direction_conflict",
            "label": "标注方向与图像结构冲突",
            "severity": "high",
            "detail": f"标注为 {preprocessing.get('declared_direction')}，图像结构更接近 {preprocessing.get('effective_direction')}",
        })
    if preprocessing.get("direction_override_suppressed"):
        reasons.append({
            "code": "direction_conflict_suppressed",
            "label": "方向冲突已由仲裁器拦截",
            "severity": "medium",
            "detail": f"图像结构倾向 {preprocessing.get('orientation', {}).get('direction')}，但高置信度布局与区域长宽比支持 {preprocessing.get('declared_direction')}，未自动覆盖",
        })
    column_lengths = postprocessing.get("column_text_lengths_visual_left_to_right") or []
    if split_succeeded and any(int(value or 0) <= 0 for value in column_lengths):
        reasons.append({
            "code": "column_ocr_incomplete",
            "label": "逐栏 OCR 有空结果",
            "severity": "high",
            "detail": "至少一个物理栏没有返回文字，需要单独重跑",
        })
    column_boxes = preprocessing.get("columns") or []
    if split_succeeded and preprocessing.get("effective_direction") == "vertical" and len(column_boxes) >= 2:
        widths = [max(0, int(box[2]) - int(box[0])) for box in column_boxes if isinstance(box, list) and len(box) == 4]
        useful_widths = [value for value in widths if value > 0]
        if useful_widths and max(useful_widths) / max(min(useful_widths), 1) >= 1.8:
            reasons.append({
                "code": "heterogeneous_vertical_columns",
                "label": "竖排栏宽差异较大",
                "severity": "medium",
                "detail": "同一选框可能混入大标题、边缘残列或不同字号正文，建议快速核对边界与阅读顺序",
            })
    if (
        direction == "vertical"
        and preprocessing.get("strategy") in {"vertical_long_strip_square_padding", "column_detection"}
        and (
            (len(original_size) >= 2 and int(original_size[0] or 0) >= 100)
            or int(preprocessing.get("detected_column_count") or 0) >= 2
        )
        and column_count is not None
        and int(column_count) <= 1
    ):
        reasons.append({
            "code": "vertical_columns_unstructured",
            "label": "竖排多列未正确拆分",
            "severity": "high",
            "detail": "选框宽度足以容纳多列，但 OCR 只返回一行，需检查列序或重新划区",
        })

    if ocr_result.get("error") or not str(text or "").strip() or str(text).startswith("待校对（VLM API 请求失败"):
        reasons.append({
            "code": "ocr_failed",
            "label": "OCR 失败或为空",
            "severity": "high",
            "detail": str(ocr_result.get("error") or "没有得到可用正文"),
        })

    if any(
        value.startswith("severe_line_repetition")
        or value in {"repeated_text_block", "repeated_line_sequence"}
        for value in warnings
    ):
        reasons.append({
            "code": "repeated_ocr_text",
            "label": "OCR 文字重复",
            "severity": "high",
            "detail": "检测到大段或多行重复文字",
        })
    if "whole_block_column_fragments" in warnings:
        reasons.append({
            "code": "whole_block_column_fragments",
            "label": "整块竖排阅读顺序不可靠",
            "severity": "high",
            "detail": "模型按视觉列片段返回，自动子区返工仍未通过覆盖率检查。",
        })
    disagreement = next((value for value in warnings if value.startswith("dual_ocr_disagreement")), "")
    if disagreement:
        score = disagreement.partition(":")[2]
        reasons.append({
            "code": "dual_ocr_disagreement",
            "label": "两次 OCR 结果不一致",
            "severity": "high",
            "detail": f"同一区域重复识别的一致度仅 {score or '未知'}，不能自动进入翻译。",
            **({"score": float(score)} if score else {}),
        })

    health = text_health(text)
    if any(code in {"repeated_block", "repeated_lines", "repeated_glyph_pattern"} for code in health.get("blockers") or []):
        reasons.append({
            "code": "ocr_text_repetition",
            "label": "OCR 文本存在机械重复",
            "severity": "high",
            "detail": "字符、短语或整行出现不符合正文的重复，禁止进入翻译。",
            "score": health.get("score"),
        })
    compact = re.sub(r"\s+", "", str(text or ""))
    if item.get("type") == "body" and len(compact) >= 60:
        kana_ratio = len(KANA.findall(compact)) / max(len(compact), 1)
        kanji_ratio = len(KANJI.findall(compact)) / max(len(compact), 1)
        if kana_ratio < 0.018 and kanji_ratio >= 0.12:
            reasons.append({
                "code": "japanese_text_implausible",
                "label": "正文不像连续日文",
                "severity": "high",
                "detail": f"长正文的假名比例仅 {kana_ratio:.1%}，可能是乱码、坐标或错误方向识别。",
                "score": round(kana_ratio, 4),
            })

    furigana = furigana_contamination(text)
    if furigana:
        reasons.append(furigana)
    return reasons


def load_ocr_result(ocr_dir: Path, crop_name: str) -> dict:
    path = ocr_dir / f"{crop_name}.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"error": "OCR 结果 JSON 无法读取"}


def load_ocr_text(ocr_dir: Path, crop_name: str, ocr_result: dict) -> str:
    if ocr_result.get("text") is not None:
        return str(ocr_result.get("text") or "").strip()
    path = ocr_dir / f"{crop_name}.txt"
    return path.read_text(encoding="utf-8", errors="replace").strip() if path.exists() else ""


def build_segment(item: dict, text: str, out_dir: Path) -> dict:
    kind = "image" if item.get("type") == "image" else "caption" if item.get("type") == "caption" else "text"
    segment = {
        "speaker": item.get("speaker") or "未命名区域",
        "kind": kind,
        "scan_page": int(item.get("page_index") or 0),
        "page_name": item.get("page_name") or "",
        "source_image": item.get("source_image") or "",
        "region_type": item.get("type") or "body",
        "order": int(item.get("order") or 0),
        "region_id": item.get("region_id") or "",
        "scan_box": item.get("box") or [],
        "angle": item.get("angle") or 0,
        "writing_direction": item.get("writing_direction") or "auto",
        "annotation_note": item.get("note") or "",
    }
    if item.get("image_ref"):
        segment["caption_for"] = item["image_ref"]
    if item.get("exclusions"):
        segment["exclusions"] = item["exclusions"]
    if kind == "image":
        segment["image"] = public_output_file(out_dir, "figures", Path(item.get("crop") or "image.jpg").name)
        segment["alt"] = segment["speaker"]
    else:
        segment["original"] = text or "待校对"
        segment["translation"] = "待翻译"
    return segment


def build_queue(out_dir: Path, ocr_dir: Path | None = None) -> dict:
    manifest_path = out_dir / "region-manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing region manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    ocr_dir = ocr_dir or out_dir / "ocr-vlm-api"
    regions = []
    overrides_path = out_dir / "ocr-rework-overrides.json"
    try:
        overrides = json.loads(overrides_path.read_text(encoding="utf-8")) if overrides_path.exists() else {}
    except (OSError, json.JSONDecodeError):
        overrides = {}
    for item in sorted(manifest, key=lambda row: (int(row.get("page_index") or 0), int(row.get("order") or 0))):
        crop_name = str(item.get("crop_name") or "")
        ocr_result = {} if item.get("type") == "image" else load_ocr_result(ocr_dir, crop_name)
        text = "" if item.get("type") == "image" else load_ocr_text(ocr_dir, crop_name, ocr_result)
        override = overrides.get(crop_name) if isinstance(overrides, dict) else None
        if isinstance(override, dict) and str(override.get("text") or "").strip():
            text = str(override["text"]).strip()
            ocr_result = {**ocr_result, "text": text, "rework_override": override, "quality_warnings": []}
        reasons = review_reasons(item, ocr_result, text)
        if isinstance(override, dict):
            resolved_codes = set(override.get("resolved_reason_codes") or [reason.get("code") for reason in reasons])
            reasons = [reason for reason in reasons if reason.get("code") not in resolved_codes]
        segment = build_segment(item, text, out_dir)
        preprocessing = ocr_result.get("preprocessing") or {}
        postprocessing = ocr_result.get("postprocessing") or {}
        automation = {
            "column_split": preprocessing.get("strategy") == "physical_column_split",
            "column_count": int(postprocessing.get("column_count") or preprocessing.get("detected_column_count") or 0),
            "direction_corrected": bool(preprocessing.get("direction_overridden")),
            "direction_arbitrated": bool(preprocessing.get("direction_override_suppressed")),
            "effective_direction": preprocessing.get("effective_direction") or item.get("writing_direction") or "auto",
        }
        if automation["direction_corrected"]:
            segment["writing_direction"] = automation["effective_direction"]
            segment["annotation_note"] = (
                f"{segment.get('annotation_note') or ''} / 图像结构自动修正方向：{automation['effective_direction']}"
            ).strip(" /")
        proposal = build_repair_proposal(item, ocr_result, reasons) if reasons else None
        region = {
            "key": f"{item.get('page_name') or ''}::{item.get('region_id') or crop_name}",
            "status": "review" if reasons else "ready",
            "route": "rework" if reasons else "translation",
            "reasons": reasons,
            "page_index": int(item.get("page_index") or 0),
            "page_name": item.get("page_name") or "",
            "region_id": item.get("region_id") or "",
            "speaker": item.get("speaker") or "未命名区域",
            "kind": segment["kind"],
            "crop": public_output_file(out_dir, "figures" if item.get("type") == "image" else "crops", Path(item.get("crop") or "").name),
            "quality_warnings": ocr_result.get("quality_warnings") or [],
            "crop_name": crop_name,
            "repair_proposal": proposal,
            "files": {
                "ocr_json": str((ocr_dir / f"{crop_name}.json").resolve()),
                "ocr_text": str((ocr_dir / f"{crop_name}.txt").resolve()),
                "overrides": str(overrides_path.resolve()),
            },
            "automation": automation,
            "segment": segment,
        }
        if isinstance(override, dict):
            region["rework"] = {
                "state": "auto_replaced" if override.get("source") == "automatic" else "manually_accepted",
                "accepted_at": override.get("accepted_at"),
                "old_text": override.get("previous_text") or "",
                "evaluation": override.get("evaluation") or {},
            }
        regions.append(region)

    counts = Counter(item["status"] for item in regions)
    kinds = Counter(item["kind"] for item in regions)
    reason_counts = Counter(reason["code"] for item in regions for reason in item["reasons"])
    automated_column_splits = sum(1 for item in regions if item["automation"]["column_split"])
    corrected_directions = sum(1 for item in regions if item["automation"]["direction_corrected"])
    arbitrated_directions = sum(1 for item in regions if item["automation"]["direction_arbitrated"])
    auto_replaced = sum(1 for item in regions if item.get("rework", {}).get("state") == "auto_replaced")
    source_images = [item.get("source_image") for item in manifest if item.get("source_image")]
    if out_dir.name.lower() in {"output", "output-v2"}:
        project_title = out_dir.parent.name
    elif out_dir.name == "baseline-whole-region":
        project_title = f"{out_dir.parent.name} · 整框基线"
    elif out_dir.name == "enhanced-column-split":
        project_title = f"{out_dir.parent.name} · V3逐栏"
    else:
        project_title = out_dir.name
    return {
        "version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project": {
            "id": f"{out_dir.parent.name}-{out_dir.name}",
            "title": project_title,
            "output_dir": str(out_dir.resolve()),
            "queue_file": str((out_dir / "project-queue.json").resolve()),
            "source_folder": str(Path(source_images[0]).parent) if source_images else "",
        },
        "summary": {
            "total": len(regions),
            "ready": counts["ready"],
            "review": counts["review"],
            "text": kinds["text"],
            "caption": kinds["caption"],
            "image": kinds["image"],
            "auto_column_split": automated_column_splits,
            "direction_corrected": corrected_directions,
            "direction_arbitrated": arbitrated_directions,
            "auto_replaced": auto_replaced,
            "reason_counts": dict(reason_counts),
        },
        "regions": regions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a semi-automatic OCR project review queue.")
    parser.add_argument("--out", required=True, help="Region OCR output folder containing region-manifest.json")
    parser.add_argument("--ocr-dir", default="", help="OCR JSON/TXT folder; defaults to <out>/ocr-vlm-api")
    args = parser.parse_args()

    out_dir = Path(args.out).resolve()
    queue = build_queue(out_dir, Path(args.ocr_dir).resolve() if args.ocr_dir else None)
    queue_path = out_dir / "project-queue.json"
    queue_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"queue": str(queue_path), **queue["summary"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
