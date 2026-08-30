"""Repair proposals and conservative OCR replacement decisions.

This module is deliberately API-agnostic.  The local server performs targeted OCR
runs, while these pure functions explain what to repair and whether two fresh
transcriptions are safe enough to replace the current text.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="strict")


COORDINATE = re.compile(r"^\s*\d{1,4}(?:\s*,\s*\d{1,4}){4,}\s*,?", re.MULTILINE)
JAPANESE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]" )
KANA_ONLY_LINE = re.compile(r"^[\u3040-\u30ff\u31f0-\u31ffー・\s]{1,28}[?？!！、。]?$" )
KANJI = re.compile(r"[\u3400-\u9fff]")


def normalized_text(text: str) -> str:
    return re.sub(r"\s+", "", str(text or "")).strip()


def similarity(left: str, right: str) -> float:
    a, b = normalized_text(left), normalized_text(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return round(SequenceMatcher(None, a, b).ratio(), 4)


def text_health(text: str) -> dict:
    raw = str(text or "").strip()
    compact = normalized_text(raw)
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    blockers: list[str] = []
    warnings: list[str] = []
    score = 1.0
    if not compact or raw.startswith("待校对（VLM API 请求失败"):
        return {"score": 0.0, "characters": len(compact), "blockers": ["empty_or_failed"], "warnings": []}
    if COORDINATE.search(raw):
        blockers.append("coordinate_output")
        score -= 0.55
    if "〔?〕" in raw or "�" in raw:
        ratio = (raw.count("〔?〕") + raw.count("�")) / max(len(compact), 1)
        (blockers if ratio >= 0.04 else warnings).append("unreadable_characters")
        score -= min(0.35, ratio * 5)
    if len(compact) < 4:
        warnings.append("very_short")
        score -= 0.18
    if re.search(r"(.{18,120}?)(?:\s*\1){2,}", raw, re.DOTALL):
        blockers.append("repeated_block")
        score -= 0.55
    if re.search(r"(.)\1{8,}", compact) or re.search(r"(.{2,8})\1{4,}", compact):
        blockers.append("repeated_glyph_pattern")
        score -= 0.55
    if len(lines) >= 8:
        unique_ratio = len(set(lines)) / len(lines)
        if unique_ratio < 0.45:
            blockers.append("repeated_lines")
            score -= 0.45
        tiny_ratio = sum(len(normalized_text(line)) <= 2 for line in lines) / len(lines)
        if tiny_ratio >= 0.55:
            warnings.append("fragmented_lines")
            score -= 0.18
        kana_lines = [line for line in lines if KANA_ONLY_LINE.fullmatch(line) and not KANJI.search(line)]
        if len(kana_lines) >= 3 and len(kana_lines) / len(lines) >= 0.14:
            warnings.append("furigana_pattern")
            score -= min(0.25, len(kana_lines) / len(lines) * 0.6)
    meaningful = [char for char in compact if char.isalnum() or JAPANESE.match(char)]
    if len(compact) >= 12 and len(meaningful) / max(len(compact), 1) < 0.48:
        warnings.append("low_text_character_ratio")
        score -= 0.2
    return {
        "score": round(max(0.0, min(1.0, score)), 3),
        "characters": len(compact),
        "line_count": len(lines),
        "blockers": blockers,
        "warnings": warnings,
    }


def _expand_box(box: list, ratio: float = 0.035) -> list[int]:
    if len(box) != 4:
        return []
    x1, y1, x2, y2 = [int(round(float(value))) for value in box]
    dx, dy = max(8, round((x2 - x1) * ratio)), max(8, round((y2 - y1) * ratio))
    return [max(0, x1 - dx), max(0, y1 - dy), x2 + dx, y2 + dy]


def _column_group_boxes(item: dict, ocr_result: dict, group_size: int = 6) -> list[dict]:
    crop_box = item.get("box") or []
    preprocessing = ocr_result.get("preprocessing") or {}
    raw_columns = preprocessing.get("columns") or preprocessing.get("detected_columns") or []
    columns = [box for box in raw_columns if isinstance(box, list) and len(box) == 4]
    source_size = preprocessing.get("source_size") or []
    if len(crop_box) != 4 or len(source_size) != 2 or len(columns) < 2:
        return []
    cx1, cy1, cx2, cy2 = map(float, crop_box)
    source_width, source_height = map(float, source_size)
    if source_width <= 0 or source_height <= 0:
        return []
    groups = [columns[index:index + group_size] for index in range(0, len(columns), group_size)]
    parts = []
    for index, group in enumerate(groups):
        gx1 = min(float(box[0]) for box in group)
        gy1 = min(float(box[1]) for box in group)
        gx2 = max(float(box[2]) for box in group)
        gy2 = max(float(box[3]) for box in group)
        pad_x = max(4.0, (gx2 - gx1) * 0.04)
        pad_y = max(4.0, (gy2 - gy1) * 0.025)
        mapped = [
            cx1 + max(0.0, gx1 - pad_x) / source_width * (cx2 - cx1),
            cy1 + max(0.0, gy1 - pad_y) / source_height * (cy2 - cy1),
            cx1 + min(source_width, gx2 + pad_x) / source_width * (cx2 - cx1),
            cy1 + min(source_height, gy2 + pad_y) / source_height * (cy2 - cy1),
        ]
        parts.append({"id": f"part-{index + 1}", "scan_box": [round(value) for value in mapped], "visual_index": index})
    direction = str(preprocessing.get("effective_direction") or item.get("writing_direction") or "auto")
    if direction == "vertical":
        parts.reverse()
    for reading_index, part in enumerate(parts, start=1):
        part["reading_order"] = reading_index
    return parts


def build_repair_proposal(item: dict, ocr_result: dict, reasons: list[dict]) -> dict:
    codes = [str(reason.get("code") or "") for reason in reasons]
    direction = str(item.get("writing_direction") or "auto")
    preprocessing = ocr_result.get("preprocessing") or {}
    effective = str(preprocessing.get("effective_direction") or direction)
    base_box = [round(float(value)) for value in item.get("box") or []]
    proposal = {
        "kind": "targeted_rerun",
        "label": "原框定点重跑",
        "detail": "保留当前选框，使用同一模型做两次独立识别并核对一致性。",
        "writing_direction": effective if effective in {"horizontal", "vertical"} else direction,
        "parts": [{"id": "part-1", "scan_box": base_box, "reading_order": 1}],
        "auto_replace_allowed": True,
        "requires_preview": False,
        "risk": "low",
    }
    if "image_text_mixed" in codes:
        proposal.update({
            "kind": "manual_content_split", "label": "拆开图片与文字",
            "detail": "图片与正文的语义边界无法只靠 OCR 可靠决定，请先在分区工具中拆框。",
            "auto_replace_allowed": False, "requires_preview": True, "risk": "high", "parts": [],
        })
    elif "page_rotation_uncertain" in codes:
        proposal.update({
            "kind": "confirm_page_rotation", "label": "确认整页方向后再识别",
            "detail": "需先确认页面应旋转 0°、90°、180° 或 270°；方向未确认前不重跑短文字。",
            "auto_replace_allowed": False, "requires_preview": True, "risk": "high", "parts": [],
        })
    elif "direction_conflict_suppressed" in codes:
        proposal.update({
            "kind": "direction_arbitration", "label": "保留布局方向并人工快看",
            "detail": "结构算法与布局方向冲突；仲裁器已阻止自动覆盖，本次候选只按布局方向识别。",
            "auto_replace_allowed": False, "requires_preview": True, "risk": "medium",
        })
    elif "multicolumn_exceeds_limit" in codes:
        parts = _column_group_boxes(item, ocr_result)
        proposal.update({
            "kind": "split_columns", "label": "按物理栏拆成较小文字块",
            "detail": f"将过宽区域拆为 {len(parts)} 组，分别 OCR 后按阅读顺序合并。" if parts else "需要先人工划出较小的栏组。",
            "parts": parts, "auto_replace_allowed": False, "requires_preview": True,
            "risk": "medium" if parts else "high",
        })
    elif "heterogeneous_vertical_columns" in codes:
        proposal.update({
            "kind": "inspect_column_edges", "label": "隔离异常宽栏或边缘残列",
            "detail": "栏宽差异可能来自标题、残列或字号变化；可定点试跑，但结果只作为人工候选。",
            "auto_replace_allowed": False, "requires_preview": True, "risk": "high",
        })
    elif "boundary_uncertain" in codes:
        proposal.update({
            "kind": "expand_crop", "label": "四周轻微扩框",
            "detail": "向四周扩展约 3.5%，找回可能被裁掉的首尾字符；变化需人工确认。",
            "parts": [{"id": "part-1", "scan_box": _expand_box(base_box), "reading_order": 1}],
            "auto_replace_allowed": False, "requires_preview": True, "risk": "medium",
        })
    elif "direction_conflict" in codes or "direction_uncertain" in codes:
        proposal.update({
            "kind": "direction_fix", "label": f"方向修正为{'竖排' if effective == 'vertical' else '横排'}",
            "detail": "不改变选框，只按图像结构修正阅读方向并重跑。",
            "auto_replace_allowed": effective in {"horizontal", "vertical"}, "risk": "low",
        })
    elif "ocr_failed" in codes:
        proposal.update({
            "kind": "expanded_retry", "label": "轻微扩框后重试",
            "detail": "原结果为空，扩框后做两次独立识别。",
            "parts": [{"id": "part-1", "scan_box": _expand_box(base_box, 0.025), "reading_order": 1}],
            "risk": "medium",
        })
    if not proposal["parts"]:
        proposal["can_run"] = False
    else:
        proposal["can_run"] = True
    proposal["reason_codes"] = codes
    return proposal


def evaluate_replacement(old_text: str, first_text: str, second_text: str, proposal: dict) -> dict:
    old_health, first_health, second_health = map(text_health, [old_text, first_text, second_text])
    agreement = similarity(first_text, second_text)
    chosen_text = first_text if first_health["score"] >= second_health["score"] else second_text
    chosen_health = first_health if chosen_text == first_text else second_health
    old_similarity = similarity(old_text, chosen_text)
    old_len, new_len = max(old_health["characters"], 1), chosen_health["characters"]
    length_delta = abs(new_len - old_health["characters"]) / old_len
    blockers = list(chosen_health["blockers"])
    gates = []
    if not proposal.get("auto_replace_allowed"):
        gates.append("proposal_requires_human")
    if agreement < 0.9:
        gates.append("two_runs_disagree")
    if chosen_health["score"] < 0.86 or blockers:
        gates.append("candidate_quality_low")
    if new_len < 8 and normalized_text(chosen_text) != normalized_text(old_text):
        gates.append("short_text_changed")
    if old_health["score"] >= 0.55 and length_delta > 0.45:
        gates.append("length_changed_too_much")
    if old_health["score"] >= 0.72 and old_similarity < 0.58:
        gates.append("meaningful_change_needs_review")
    improvement = round(chosen_health["score"] - old_health["score"], 3)
    issue_codes = set(proposal.get("reason_codes") or [])
    resolved_by_structure = bool(issue_codes & {"direction_conflict", "direction_uncertain", "column_ocr_incomplete", "vertical_columns_unstructured"})
    if improvement < 0.08 and old_similarity < 0.9 and not resolved_by_structure:
        gates.append("no_clear_improvement")
    auto_replace = not gates
    confidence = 0.48 * chosen_health["score"] + 0.34 * agreement + 0.18 * max(0.0, 1.0 - min(length_delta, 1.0))
    if old_similarity < 0.58 and old_health["score"] >= 0.72:
        confidence -= 0.12
    return {
        "decision": "auto_replace" if auto_replace else "human_review",
        "reliable": auto_replace,
        "confidence": round(max(0.0, min(1.0, confidence)), 3),
        "chosen_text": chosen_text.strip(),
        "old_similarity": old_similarity,
        "two_run_agreement": agreement,
        "length_change_ratio": round(length_delta, 3),
        "quality_improvement": improvement,
        "old_health": old_health,
        "first_health": first_health,
        "second_health": second_health,
        "gates": list(dict.fromkeys(gates)),
        "explanation": "两次结果高度一致，候选文字质量通过全部安全门槛。" if auto_replace else "候选结果已保留，但至少一项安全门槛未通过。",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluate", help="JSON input file for evaluate_replacement")
    args = parser.parse_args()
    if args.evaluate:
        payload = json.loads(Path(args.evaluate).read_text(encoding="utf-8"))
        print(json.dumps(evaluate_replacement(payload.get("old_text", ""), payload.get("first_text", ""), payload.get("second_text", ""), payload.get("proposal") or {}), ensure_ascii=False))


if __name__ == "__main__":
    main()
