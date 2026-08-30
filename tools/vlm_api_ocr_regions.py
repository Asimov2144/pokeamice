import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

try:
    from PIL import Image, ImageOps
except Exception:
    Image = None
    ImageOps = None

try:
    import numpy as np
except Exception:
    np = None

try:
    import cv2
except Exception:
    cv2 = None

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    import httpx
except Exception:
    httpx = None


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_PROMPT = """あなたは日本語雑誌スキャン専用のOCRエンジンです。
対象はポケットモンスター、任天堂、ゲーム関連の記事・インタビュー・図版キャプションです。
画像内に見える文字を、原文の文字種をできるだけ保って転写してください。
日本語は日本語のまま出力し、英字・数字・記号・商品名・ゲーム名は原文どおり保持してください。
「ポケモン」「ピカチュウ」「ニンテンドーDS」「Wi-Fi」「GAME FREAK」などの固有名詞は文脈に合わせて自然な表記を優先してください。
翻訳、要約、解説、画像説明はしないでください。
読み順に沿って出力し、必要な改行は保ってください。
判読不能な文字は推測で補わず、〔?〕で示してください。"""


VERTICAL_LONG_STRIP_PROMPT = """Read only the visible Japanese text in this image.
The image contains one or more physical vertical text columns. Read every column from top to bottom.
Output exactly one line per physical column, ordered by its visual position from left to right.
Do not join columns, translate, explain, infer missing text, or repeat text.
Output only the transcription."""


SINGLE_VERTICAL_COLUMN_PROMPT = """Transcribe only the visible Japanese text in this single vertical column.
Read from top to bottom. Do not output coordinates, explanations, image descriptions, or repeated text.
Output only the transcription."""


HORIZONTAL_LAYOUT_COLUMN_PROMPT = """Transcribe only the visible Japanese text in this single horizontal-writing layout column.
Read lines from left to right and from top to bottom. Do not output coordinates, explanations, image descriptions, or repeated text.
Preserve useful line breaks and output only the transcription."""


OCR_RECOVERY_PROMPT = """Transcribe all Japanese text actually visible in this crop as plain text.
First determine the real writing direction from the glyphs and text lines; do not infer it from the crop's tall or wide shape.
Use the natural Japanese reading order. Do not output bounding boxes, coordinates, confidence values, explanations, or image descriptions.
Do not invent or repeat text. Output only the transcription."""


COORDINATE_PREFIX = re.compile(r"^\s*\d{1,4}(?:\s*,\s*\d{1,4}){4,}\s*,?\s*")


def load_region_hints(path: str) -> dict[str, dict]:
    if not path:
        return {}
    manifest_path = Path(path).resolve()
    if not manifest_path.exists():
        return {}
    rows = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {str(row.get("crop_name") or ""): row for row in rows if row.get("crop_name")}


def prompt_with_region_hint(prompt: str, item: dict | None, vertical_long_strip: bool = False) -> str:
    direction = str((item or {}).get("writing_direction") or "auto").lower()
    if vertical_long_strip:
        return VERTICAL_LONG_STRIP_PROMPT
    if direction == "vertical":
        hint = "この領域は日本語の縦書きです。各列は上から下へ、列は右から左の順で転写してください。列順を入れ替えないでください。"
    elif direction == "horizontal":
        hint = "この領域は横書きです。行は左から右、上から下の順で転写してください。"
    else:
        hint = "文字方向は未指定です。画像から横書き・縦書きを判断し、自然な読書順で転写してください。"
    return f"{prompt.rstrip()}\n\n領域指定：{hint}"


def encode_image(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:markdown|text)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def normalized_ocr_similarity(left: str, right: str) -> float:
    left_compact = re.sub(r"\s+", "", str(left or ""))
    right_compact = re.sub(r"\s+", "", str(right or ""))
    if not left_compact and not right_compact:
        return 1.0
    if not left_compact or not right_compact:
        return 0.0
    return SequenceMatcher(None, left_compact, right_compact).ratio()


def quality_warnings(text: str) -> list[str]:
    warnings = []
    if not text.strip():
        return ["empty_output"]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) >= 20:
        unique_ratio = len(set(lines)) / len(lines)
        if unique_ratio < 0.35:
            warnings.append(f"severe_line_repetition:{unique_ratio:.2f}")
    if len(lines) >= 6:
        pairs = list(zip(lines, lines[1:]))
        if len(set(pairs)) < len(pairs):
            warnings.append("repeated_line_sequence")
    if re.search(r"(.{24,160}?)(?:\s*\1){2,}", text, flags=re.DOTALL):
        warnings.append("repeated_text_block")
    coordinate_lines = [line for line in lines if COORDINATE_PREFIX.match(line)]
    coordinate_ratio = len(coordinate_lines) / max(1, len(lines))
    if (len(coordinate_lines) >= 3 and coordinate_ratio >= 0.45) or (
        len(coordinate_lines) >= 1 and len(lines) <= 3 and coordinate_ratio >= 0.5
    ):
        warnings.append(f"coordinate_dump:{coordinate_ratio:.2f}")
    return warnings


def strip_coordinate_prefixes(text: str) -> tuple[str, dict]:
    lines = str(text or "").splitlines()
    nonempty = [line for line in lines if line.strip()]
    prefixed = [line for line in nonempty if COORDINATE_PREFIX.match(line)]
    ratio = len(prefixed) / max(1, len(nonempty))
    short_coordinate_output = len(prefixed) >= 1 and len(nonempty) <= 3 and ratio >= 0.5
    if not short_coordinate_output and (len(prefixed) < 3 or ratio < 0.35):
        return str(text or "").strip(), {}
    cleaned = [COORDINATE_PREFIX.sub("", line).strip() for line in lines]
    cleaned = [line for line in cleaned if line]
    return "\n".join(cleaned).strip(), {
        "strategy": "coordinate_prefix_strip",
        "affected_lines": len(prefixed),
        "line_ratio": round(ratio, 3),
    }


def _merge_intervals(intervals: list[tuple[int, int]], gap: int = 0) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if end <= start:
            continue
        if merged and start <= merged[-1][1] + gap:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


IMAGE_ANALYSIS_PACKAGES = (("numpy", "numpy"), ("cv2", "opencv-python-headless"))


def warn(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr, flush=True)


def missing_image_analysis_packages() -> list[str]:
    """Report which page-structure dependencies could not be imported."""
    available = {"numpy": np, "cv2": cv2}
    return [package for module, package in IMAGE_ANALYSIS_PACKAGES if available[module] is None]


def require_image_analysis(feature: str) -> None:
    """Fail loudly. Degrading here costs vertical pages their column splitting in silence."""
    missing = missing_image_analysis_packages()
    if not missing:
        return
    raise RuntimeError(
        f"{feature} requires {' and '.join(missing)}, which could not be imported. "
        "Install with: .venv-ocr/Scripts/python.exe -m pip install -r tools/requirements.txt "
        "(or pass --disable-auto-column-split to run OCR without direction detection "
        "and physical column splitting)."
    )


def _analysis_binary(image_path: Path) -> tuple[object, dict]:
    """Return a compact foreground mask plus glyph-size diagnostics."""
    require_image_analysis("Page structure analysis")
    try:
        encoded = np.fromfile(str(image_path), dtype=np.uint8)
        gray = cv2.imdecode(encoded, cv2.IMREAD_GRAYSCALE)
    except (OSError, ValueError):
        gray = None
    if gray is None:
        warn(
            f"{image_path} could not be decoded for page structure analysis; "
            "direction detection and column splitting are skipped for this crop."
        )
        return None, {}
    height, width = gray.shape[:2]
    scale = min(1.0, 1400.0 / max(width, height, 1))
    if scale < 1.0:
        gray = cv2.resize(gray, (max(1, round(width * scale)), max(1, round(height * scale))), interpolation=cv2.INTER_AREA)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    count, _, stats, _ = cv2.connectedComponentsWithStats(binary, 8)
    components = []
    image_area = binary.shape[0] * binary.shape[1]
    for index in range(1, count):
        x, y, component_width, component_height, area = [int(value) for value in stats[index]]
        if area < 4 or area > image_area * 0.015:
            continue
        if component_width < 2 or component_height < 2:
            continue
        ratio = component_width / max(component_height, 1)
        if 0.15 <= ratio <= 6.5:
            components.append((x, y, component_width, component_height, area))
    if components:
        glyph_width = int(np.median([row[2] for row in components]))
        glyph_height = int(np.median([row[3] for row in components]))
    else:
        glyph_width = max(3, binary.shape[1] // 60)
        glyph_height = max(3, binary.shape[0] // 60)
    return binary, {
        "source_size": [width, height],
        "analysis_size": [int(binary.shape[1]), int(binary.shape[0])],
        "analysis_scale": round(scale, 5),
        "glyph_size": [max(3, glyph_width), max(3, glyph_height)],
        "component_count": len(components),
    }


def detect_text_orientation(image_path: Path) -> dict:
    """Estimate whether a dense crop is arranged as vertical columns or horizontal lines."""
    require_image_analysis("Writing direction detection")
    binary, diagnostics = _analysis_binary(image_path)
    if binary is None or not diagnostics:
        return {"direction": "unknown", "confidence": 0.0, "reason": "unreadable_image"}
    width, height = diagnostics["analysis_size"]
    glyph_width, glyph_height = diagnostics["glyph_size"]
    vertical_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (max(1, glyph_width // 3), max(5, round(glyph_height * 2.2))),
    )
    horizontal_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (max(5, round(glyph_width * 2.2)), max(1, glyph_height // 3)),
    )
    vertical = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, vertical_kernel)
    horizontal = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, horizontal_kernel)

    def line_score(mask, direction: str) -> tuple[float, int]:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        score = 0.0
        lines = 0
        for contour in contours:
            x, y, item_width, item_height = cv2.boundingRect(contour)
            if direction == "vertical":
                if item_height < max(glyph_height * 3, height * 0.08) or item_height < item_width * 2.0:
                    continue
                score += item_height / max(height, 1)
            else:
                if item_width < max(glyph_width * 3, width * 0.08) or item_width < item_height * 2.0:
                    continue
                score += item_width / max(width, 1)
            lines += 1
        return score, lines

    vertical_score, vertical_lines = line_score(vertical, "vertical")
    horizontal_score, horizontal_lines = line_score(horizontal, "horizontal")
    total = vertical_score + horizontal_score
    raw_confidence = abs(vertical_score - horizontal_score) / max(total, 0.001) if total else 0.0
    if total < 0.45 or max(vertical_lines, horizontal_lines) < 2 or raw_confidence < 0.55:
        direction = "unknown"
        confidence = 0.0
    else:
        direction = "vertical" if vertical_score >= horizontal_score else "horizontal"
        confidence = raw_confidence
    return {
        "direction": direction,
        "confidence": round(float(confidence), 3),
        "vertical_score": round(float(vertical_score), 3),
        "horizontal_score": round(float(horizontal_score), 3),
        "vertical_lines": vertical_lines,
        "horizontal_lines": horizontal_lines,
        **diagnostics,
    }


def detect_physical_columns(image_path: Path, direction: str, max_columns: int = 16) -> dict:
    """Find physical reading columns without asking the OCR model to infer their order."""
    require_image_analysis("Physical column detection")
    binary, diagnostics = _analysis_binary(image_path)
    if binary is None or not diagnostics or direction not in {"vertical", "horizontal"}:
        return {"direction": direction, "columns": [], **diagnostics}
    analysis_width, analysis_height = diagnostics["analysis_size"]
    source_width, source_height = diagnostics["source_size"]
    glyph_width, glyph_height = diagnostics["glyph_size"]
    scale_x = source_width / max(analysis_width, 1)
    scale_y = source_height / max(analysis_height, 1)
    boxes: list[tuple[int, int, int, int]] = []

    if direction == "vertical":
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (max(1, glyph_width // 3), max(5, round(glyph_height * 2.4))),
        )
        joined = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(joined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates = []
        for contour in contours:
            x, y, item_width, item_height = cv2.boundingRect(contour)
            if item_height < max(glyph_height * 3, analysis_height * 0.07):
                continue
            if item_width > max(glyph_width * 3.6, analysis_width * 0.28):
                continue
            if item_height < item_width * 2.0:
                continue
            candidates.append((x, y, x + item_width, y + item_height))
        x_intervals = _merge_intervals([(row[0], row[2]) for row in candidates], gap=max(1, glyph_width // 3))
        for x1, x2 in x_intervals:
            members = [row for row in candidates if min(x2, row[2]) > max(x1, row[0])]
            if not members:
                continue
            y1 = min(row[1] for row in members)
            y2 = max(row[3] for row in members)
            pad_x = max(2, glyph_width // 2)
            pad_y = max(2, glyph_height // 2)
            boxes.append((max(0, x1 - pad_x), max(0, y1 - pad_y), min(analysis_width, x2 + pad_x), min(analysis_height, y2 + pad_y)))
    else:
        foreground = (binary > 0).astype(np.float32)
        projection = foreground.mean(axis=0)
        smooth_width = max(3, glyph_width // 2 * 2 + 1)
        projection = np.convolve(projection, np.ones(smooth_width) / smooth_width, mode="same")
        blank = projection < max(0.0025, float(np.quantile(projection, 0.12)) * 0.45)
        blank_runs = []
        start = None
        for index, value in enumerate(blank.tolist() + [False]):
            if value and start is None:
                start = index
            elif not value and start is not None:
                if index - start >= max(glyph_width, round(analysis_width * 0.012)):
                    blank_runs.append((start, index))
                start = None
        cuts = [0]
        for start, end in blank_runs:
            center = (start + end) // 2
            if analysis_width * 0.04 < center < analysis_width * 0.96:
                cuts.append(center)
        cuts.append(analysis_width)
        cuts = sorted(set(cuts))
        for x1, x2 in zip(cuts, cuts[1:]):
            if x2 - x1 < max(glyph_width * 5, analysis_width * 0.09):
                continue
            segment = foreground[:, x1:x2]
            if segment.mean() < 0.006:
                continue
            ys, xs = np.where(segment > 0)
            if not len(xs):
                continue
            pad_x = max(2, glyph_width)
            pad_y = max(2, glyph_height)
            boxes.append((max(0, x1 - pad_x), max(0, int(ys.min()) - pad_y), min(analysis_width, x2 + pad_x), min(analysis_height, int(ys.max()) + 1 + pad_y)))

    boxes = sorted(boxes, key=lambda row: row[0])
    source_boxes = [
        [
            max(0, round(x1 * scale_x)),
            max(0, round(y1 * scale_y)),
            min(source_width, round(x2 * scale_x)),
            min(source_height, round(y2 * scale_y)),
        ]
        for x1, y1, x2, y2 in boxes
    ]
    return {
        "direction": direction,
        "column_count": len(source_boxes),
        "columns": source_boxes if len(source_boxes) <= max_columns else [],
        "detected_columns": source_boxes,
        "detected_column_count": len(source_boxes),
        "too_many_columns": len(source_boxes) > max_columns,
        "reading_order": "right_to_left" if direction == "vertical" else "left_to_right",
        **diagnostics,
    }


def prepare_column_crops(
    image_path: Path,
    item: dict | None,
    model: str,
    prepared_dir: Path,
    max_columns: int = 16,
    disabled: bool = False,
) -> tuple[list[Path], dict]:
    if disabled or "qwen-vl-ocr" not in model.lower():
        return [], {}
    if Image is None:
        warn(
            f"Pillow is unavailable, so {image_path} is sent to OCR without physical column splitting. "
            "Install with: .venv-ocr/Scripts/python.exe -m pip install -r tools/requirements.txt"
        )
        return [], {}
    declared = str((item or {}).get("writing_direction") or "auto").lower()
    orientation = detect_text_orientation(image_path)
    detected = orientation.get("direction") or "unknown"
    confidence = float(orientation.get("confidence") or 0)
    effective = declared if declared in {"horizontal", "vertical"} else detected
    direction_overridden = False
    direction_override_suppressed = False
    if detected in {"horizontal", "vertical"} and detected != declared and confidence >= 0.6:
        source_width, source_height = (orientation.get("source_size") or [0, 0])[:2]
        layout_confidence = float((item or {}).get("confidence") or 0)
        aspect_supports_declared = (
            declared == "horizontal" and source_width >= source_height * 2.4
        ) or (
            declared == "vertical" and source_height >= source_width * 2.4
        )
        if declared in {"horizontal", "vertical"} and layout_confidence >= 0.85 and aspect_supports_declared:
            direction_override_suppressed = True
        else:
            effective = detected
            direction_overridden = declared in {"horizontal", "vertical"}
    if effective not in {"horizontal", "vertical"}:
        return [], {"strategy": "column_detection", "declared_direction": declared, "orientation": orientation, "column_count": 0}
    source_width, source_height = (orientation.get("source_size") or [0, 0])[:2]
    if effective == "vertical" and source_width > 0 and source_height >= source_width * 4.5:
        # A very narrow vertical strip is already one physical text column.
        # Running gutter detection on individual glyph strokes can invent 2-4
        # fake columns and scramble their reading order.
        box = [0, 0, int(source_width), int(source_height)]
        return [], {
            "strategy": "column_detection",
            "declared_direction": declared,
            "effective_direction": effective,
            "direction_overridden": direction_overridden,
            "direction_override_suppressed": direction_override_suppressed,
            "orientation": orientation,
            "direction": "vertical",
            "column_count": 1,
            "columns": [box],
            "detected_columns": [box],
            "detected_column_count": 1,
            "too_many_columns": False,
            "reading_order": "top_to_bottom",
            "forced_single_column": True,
            "source_size": [int(source_width), int(source_height)],
        }
    columns = detect_physical_columns(image_path, effective, max_columns)
    if effective == "vertical":
        glyph_width = int((columns.get("glyph_size") or [0, 0])[0] or 0)
        minimum_column_width = max(8, round(glyph_width * 1.15))
        filtered_boxes = [
            box
            for box in (columns.get("detected_columns") or [])
            if int(box[2]) - int(box[0]) >= minimum_column_width
        ]
        if len(filtered_boxes) >= 2:
            columns = {
                **columns,
                "columns": filtered_boxes if len(filtered_boxes) <= max_columns else [],
                "detected_columns": filtered_boxes,
                "detected_column_count": len(filtered_boxes),
                "column_count": len(filtered_boxes),
                "too_many_columns": len(filtered_boxes) > max_columns,
                "edge_artifacts_filtered": True,
            }
    detected_boxes = columns.get("detected_columns") or columns.get("columns") or []
    if (
        effective == "vertical"
        and len(detected_boxes) >= 2
        and source_width > 0
        and source_height > 0
        and source_width >= source_height * 0.55
    ):
        # Qwen OCR preserves the reading order of a complete horizontal band
        # much better than independently OCRing 10-20 narrow physical columns.
        # Keep the column detector as diagnostics and verify the whole-band OCR
        # with a second request below.
        return [], {
            "strategy": "whole_vertical_block",
            "whole_block_selected": True,
            "declared_direction": declared,
            "effective_direction": effective,
            "direction_overridden": direction_overridden,
            "direction_override_suppressed": direction_override_suppressed,
            "orientation": orientation,
            **columns,
        }
    boxes = columns.get("columns") or []
    if len(boxes) <= 1:
        return [], {
            "strategy": "column_detection",
            "declared_direction": declared,
            "effective_direction": effective,
            "direction_overridden": direction_overridden,
            "direction_override_suppressed": direction_override_suppressed,
            "orientation": orientation,
            **columns,
        }

    prepared_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    with Image.open(image_path) as opened:
        source = ImageOps.exif_transpose(opened).convert("RGB") if ImageOps is not None else opened.convert("RGB")
        for index, box in enumerate(boxes, start=1):
            crop = source.crop(tuple(box))
            if effective == "vertical":
                side = int(((max(crop.width, crop.height) * 1.05 + 31) // 32) * 32)
                canvas = Image.new("RGB", (side, side), "white")
                offset = ((side - crop.width) // 2, (side - crop.height) // 2)
                canvas.paste(crop, offset)
                crop = canvas
            path = prepared_dir / f"{image_path.stem}__column-{index:02d}.png"
            crop.save(path, optimize=True)
            paths.append(path)
    return paths, {
        "strategy": "physical_column_split",
        "declared_direction": declared,
        "effective_direction": effective,
        "direction_overridden": direction_overridden,
        "direction_override_suppressed": direction_override_suppressed,
        "orientation": orientation,
        **columns,
    }


def join_column_texts(texts: list[str], direction: str) -> tuple[str, dict]:
    visual_order = [str(text or "").strip() for text in texts]
    reading_order = list(reversed(visual_order)) if direction == "vertical" else visual_order
    separator = "" if direction == "vertical" else "\n"
    return separator.join(value for value in reading_order if value).strip(), {
        "strategy": "physical_column_reading_order",
        "column_count": len(visual_order),
        "model_order": "visual_left_to_right",
        "reading_order": "right_to_left" if direction == "vertical" else "left_to_right",
        "column_text_lengths_visual_left_to_right": [len(value) for value in visual_order],
    }


def prepare_vertical_subblock_crops(
    image_path: Path,
    detected_columns: list,
    prepared_dir: Path,
    columns_per_block: int = 3,
) -> list[Path]:
    if Image is None or ImageOps is None:
        return []
    boxes = [
        [int(value) for value in box]
        for box in detected_columns
        if isinstance(box, (list, tuple)) and len(box) == 4
    ]
    boxes = sorted(boxes, key=lambda box: box[0])
    if len(boxes) < 2:
        return []
    prepared_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    with Image.open(image_path) as opened:
        source = ImageOps.exif_transpose(opened).convert("RGB")
        group_count = max(2, (len(boxes) + max(2, columns_per_block) - 1) // max(2, columns_per_block))
        boundaries = [0]
        ink = None
        if np is not None:
            grayscale = np.asarray(source.convert("L"))
            ink = (grayscale < 220).mean(axis=0)
        for group_index in range(1, group_count):
            ideal = round(source.width * group_index / group_count)
            search_radius = max(12, round(source.width / group_count * 0.16))
            low = max(boundaries[-1] + 24, ideal - search_radius)
            high = min(source.width - 24, ideal + search_radius)
            boundary = ideal
            if ink is not None and high > low:
                boundary = min(range(low, high + 1), key=lambda x: float(ink[max(0, x - 2) : x + 3].sum()))
            boundaries.append(boundary)
        boundaries.append(source.width)
        for index, (left, right) in enumerate(zip(boundaries, boundaries[1:]), start=1):
            top = 0
            bottom = source.height
            if right <= left or bottom <= top:
                continue
            path = prepared_dir / f"{image_path.stem}__subblock-{index:02d}.png"
            source.crop((left, top, right, bottom)).save(path, optimize=True)
            paths.append(path)
    return paths


def prepare_vertical_long_strip(
    image_path: Path,
    item: dict | None,
    model: str,
    prepared_dir: Path,
    ratio_threshold: float,
    disabled: bool,
) -> tuple[Path, dict]:
    direction = str((item or {}).get("writing_direction") or "auto").lower()
    if disabled or direction != "vertical" or "qwen-vl-ocr" not in model.lower():
        return image_path, {}
    if Image is None or ImageOps is None:
        raise RuntimeError("Pillow is required for vertical long-strip OCR preprocessing.")

    with Image.open(image_path) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        width, height = image.size
        aspect_ratio = height / max(width, 1)
        if height <= width or aspect_ratio < ratio_threshold:
            return image_path, {}

        # Preserve every source pixel. Padding changes only the request canvas so
        # the vision encoder does not receive an extreme long-strip aspect ratio.
        side = max(width, height)
        side = int(((side * 1.05 + 31) // 32) * 32)
        canvas = Image.new("RGB", (side, side), "white")
        offset = ((side - width) // 2, (side - height) // 2)
        canvas.paste(image, offset)

        prepared_dir.mkdir(parents=True, exist_ok=True)
        prepared_path = prepared_dir / f"{image_path.stem}__vertical-padded.png"
        canvas.save(prepared_path, optimize=True)

    return prepared_path, {
        "strategy": "vertical_long_strip_square_padding",
        "original_size": [width, height],
        "request_size": [side, side],
        "aspect_ratio": round(aspect_ratio, 3),
        "padding_offset": list(offset),
        "column_output_order": "visual_left_to_right",
    }


def reverse_vertical_column_order(text: str, enabled: bool, reverse: bool = True) -> tuple[str, dict]:
    if not enabled:
        return text, {}
    columns = [line.strip() for line in text.splitlines() if line.strip()]
    if len(columns) <= 1:
        return text.strip(), {
            "strategy": "vertical_column_order",
            "column_count": len(columns),
            "reversed": False,
        }
    ordered = list(reversed(columns)) if reverse else columns
    return "".join(ordered), {
        "strategy": "vertical_column_order",
        "column_count": len(columns),
        "reversed": reverse,
        "model_order": "visual_left_to_right" if reverse else "top_to_bottom_chunks",
        "reading_order": "right_to_left" if reverse else "top_to_bottom",
    }


def call_vlm_api(
    image_path: Path,
    api_url: str,
    api_key: str,
    model: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    retries: int,
    retry_delay: float,
    enable_thinking: bool,
    thinking_budget: int,
    image_detail: str,
    disable_thinking: bool,
) -> str:
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": encode_image(image_path),
                        "detail": image_detail,
                    },
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if "qwen3" in model.lower():
        payload["enable_thinking"] = enable_thinking
        if enable_thinking and thinking_budget > 0:
            payload["thinking_budget"] = thinking_budget
    if "deepseek" in model.lower() and disable_thinking:
        payload["thinking"] = {"type": "disabled"}

    if OpenAI is not None:
        last_error = None
        for attempt in range(retries + 1):
            try:
                client = OpenAI(api_key=api_key, base_url=api_url.rstrip("/"))
                extra_body = {}
                if "qwen3" in model.lower():
                    extra_body["enable_thinking"] = enable_thinking
                    if enable_thinking and thinking_budget > 0:
                        extra_body["thinking_budget"] = thinking_budget
                if "deepseek" in model.lower() and disable_thinking:
                    extra_body["thinking"] = {"type": "disabled"}
                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_body=extra_body or None,
                    timeout=180,
                )
                content = clean_text(completion.choices[0].message.content or "")
                if not content and getattr(completion.choices[0].message, "reasoning_content", None):
                    raise RuntimeError("Model returned reasoning only. Disable thinking or increase max tokens.")
                return content
            except Exception as exc:
                last_error = exc
                if attempt < retries:
                    time.sleep(retry_delay + attempt * retry_delay)
        raise RuntimeError(f"VLM API request failed for {image_path.name}: {last_error}")

    endpoint = api_url.rstrip("/") + "/chat/completions"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    if httpx is not None:
        last_error = None
        for attempt in range(retries + 1):
            try:
                with httpx.Client(timeout=180, http2=False, follow_redirects=True) as client:
                    response = client.post(endpoint, content=body, headers=headers)
                if response.status_code >= 400:
                    raise RuntimeError(f"HTTP {response.status_code}: {response.text}")
                data = response.json()
                message = data.get("choices", [{}])[0].get("message", {})
                content = clean_text(message.get("content", ""))
                if not content and message.get("reasoning_content"):
                    raise RuntimeError("Model returned reasoning only. Disable thinking or increase max tokens.")
                return content
            except Exception as exc:
                last_error = exc
                if attempt < retries:
                    time.sleep(retry_delay + attempt * retry_delay)
        raise RuntimeError(f"VLM API request failed for {image_path.name}: {last_error}")

    request = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")

    last_error = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                data = json.loads(response.read().decode("utf-8"))
            message = data.get("choices", [{}])[0].get("message", {})
            content = clean_text(message.get("content", ""))
            if not content and message.get("reasoning_content"):
                raise RuntimeError("Model returned reasoning only. Disable thinking or increase max tokens.")
            return content
        except urllib.error.HTTPError as exc:
            try:
                error_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                error_body = ""
            last_error = f"HTTP {exc.code}: {error_body or exc.reason}"
            if attempt < retries:
                time.sleep(retry_delay + attempt * retry_delay)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(retry_delay + attempt * retry_delay)
    raise RuntimeError(f"VLM API request failed for {image_path.name}: {last_error}")


def iter_images(input_path: Path):
    if input_path.is_file():
        yield input_path
        return
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.tif", "*.tiff"):
        yield from sorted(input_path.glob(ext))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run OpenAI-compatible VLM OCR for cropped regions.")
    parser.add_argument("input", help="Cropped image file or folder.")
    parser.add_argument("--out", required=True, help="Output folder for txt/json/md files.")
    parser.add_argument("--api-url", default=os.getenv("VLM_OCR_API_URL", ""))
    parser.add_argument(
        "--api-key",
        default="",
    )
    parser.add_argument("--model", default=os.getenv("VLM_OCR_MODEL", "allenai/olmOCR-2-7B-1025"))
    parser.add_argument("--prompt", default=os.getenv("VLM_OCR_PROMPT", DEFAULT_PROMPT))
    parser.add_argument("--manifest", default="", help="Region manifest used to add per-crop vertical/horizontal OCR instructions.")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=768)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--retry-delay", type=float, default=4.0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--enable-thinking", action="store_true")
    parser.add_argument("--thinking-budget", type=int, default=0)
    parser.add_argument(
        "--disable-thinking",
        action="store_true",
        help="Disable DeepSeek reasoning so OCR tokens are reserved for the final transcription.",
    )
    parser.add_argument(
        "--image-detail",
        choices=("auto", "low", "high", "original"),
        default=os.getenv("VLM_OCR_IMAGE_DETAIL", "auto"),
        help="Vision input resolution. DeepSeek supports low/high/original; use original for dense magazine pages.",
    )
    parser.add_argument(
        "--vertical-long-strip-ratio",
        type=float,
        default=float(os.getenv("VLM_OCR_VERTICAL_LONG_STRIP_RATIO", "3.0")),
        help="Pad Qwen OCR inputs marked vertical when height/width reaches this ratio.",
    )
    parser.add_argument(
        "--disable-vertical-long-strip-padding",
        action="store_true",
        help="Disable automatic square padding and vertical column-order correction.",
    )
    parser.add_argument(
        "--disable-auto-column-split",
        action="store_true",
        help="Disable image-based direction verification and physical multi-column OCR splitting.",
    )
    parser.add_argument(
        "--max-auto-columns",
        type=int,
        default=int(os.getenv("VLM_OCR_MAX_AUTO_COLUMNS", "16")),
        help="Maximum number of physical columns that may be split into separate OCR requests.",
    )
    args = parser.parse_args()

    is_deepseek = "deepseek" in args.model.lower()
    if not args.api_key and is_deepseek:
        args.api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not args.api_key and not is_deepseek:
        args.api_key = (
            os.getenv("VLM_OCR_API_KEY")
            or os.getenv("DASHSCOPE_API_KEY")
            or os.getenv("QWEN_API_KEY")
            or ""
        )
    if not args.api_url and "deepseek" in args.model.lower():
        args.api_url = "https://api.deepseek.com"
    if not args.api_url and "qwen" in args.model.lower():
        args.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    if not args.api_url:
        raise SystemExit("Missing --api-url or VLM_OCR_API_URL.")
    if "dashscope.aliyuncs.com" in args.api_url and not args.api_key:
        raise SystemExit("Missing API key. Set DASHSCOPE_API_KEY or VLM_OCR_API_KEY before running Qwen OCR.")
    if "api.deepseek.com" in args.api_url and not args.api_key:
        raise SystemExit("Missing API key. Set DEEPSEEK_API_KEY before running DeepSeek Vision OCR.")

    if not args.disable_auto_column_split and "qwen-vl-ocr" in args.model.lower():
        require_image_analysis("Automatic column splitting")

    input_path = Path(args.input).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    images = list(iter_images(input_path))
    region_hints = load_region_hints(args.manifest)
    if args.limit > 0:
        images = images[: args.limit]
    if not images:
        raise SystemExit(f"No images found: {input_path}")

    log_path = out_dir / "_vlm-api-log.txt"
    log_path.write_text(f"VLM API OCR started: {time.strftime('%Y-%m-%dT%H:%M:%S')}\n", encoding="utf-8")
    prepared_dir = out_dir / "_prepared-inputs"

    for index, image_path in enumerate(images, start=1):
        txt_path = out_dir / f"{image_path.stem}.txt"
        if args.skip_existing and txt_path.exists():
            print(f"Skip [{index}/{len(images)}]: {image_path.name}", flush=True)
            continue

        print(f"VLM OCR [{index}/{len(images)}]: {image_path}", flush=True)
        started = time.monotonic()
        try:
            region_hint = region_hints.get(image_path.stem)
            column_paths, column_preprocessing = prepare_column_crops(
                image_path,
                region_hint,
                args.model,
                prepared_dir,
                max(2, args.max_auto_columns),
                args.disable_auto_column_split,
            )
            request_images = []
            column_split_used = len(column_paths) > 1
            recovery = {}
            postprocessing = {}
            consistency = {}
            if column_split_used:
                effective_direction = column_preprocessing.get("effective_direction") or "horizontal"
                column_prompt = SINGLE_VERTICAL_COLUMN_PROMPT if effective_direction == "vertical" else HORIZONTAL_LAYOUT_COLUMN_PROMPT
                column_texts = []
                column_warnings = []
                column_recoveries = []
                for column_index, column_path in enumerate(column_paths, start=1):
                    request_images.append(str(column_path))
                    column_text = call_vlm_api(
                        column_path,
                        args.api_url,
                        args.api_key,
                        args.model,
                        column_prompt,
                        args.temperature,
                        args.max_tokens,
                        args.retries,
                        args.retry_delay,
                        args.enable_thinking,
                        args.thinking_budget,
                        args.image_detail,
                        args.disable_thinking,
                    )
                    warnings_for_column = quality_warnings(column_text)
                    coordinate_seen_for_column = any(
                        warning.startswith("coordinate_dump") for warning in warnings_for_column
                    )
                    api_retry_succeeded = None
                    if any(warning.startswith("coordinate_dump") for warning in warnings_for_column):
                        recovered = call_vlm_api(
                            column_path,
                            args.api_url,
                            args.api_key,
                            args.model,
                            column_prompt,
                            args.temperature,
                            args.max_tokens,
                            args.retries,
                            args.retry_delay,
                            args.enable_thinking,
                            args.thinking_budget,
                            args.image_detail,
                            args.disable_thinking,
                        )
                        recovered, cleanup = strip_coordinate_prefixes(recovered)
                        succeeded = bool(recovered.strip()) and not any(
                            warning.startswith("coordinate_dump") for warning in quality_warnings(recovered)
                        )
                        api_retry_succeeded = succeeded
                        if succeeded:
                            column_text = recovered
                    column_text, cleanup = strip_coordinate_prefixes(column_text)
                    if coordinate_seen_for_column or cleanup:
                        final_succeeded = bool(column_text.strip()) and not any(
                            warning.startswith("coordinate_dump") for warning in quality_warnings(column_text)
                        )
                        column_recoveries.append({
                            "column": column_index,
                            "reason": "coordinate_dump",
                            "succeeded": final_succeeded,
                            **({"api_retry_succeeded": api_retry_succeeded} if api_retry_succeeded is not None else {}),
                            **({"cleanup": cleanup} if cleanup else {}),
                        })
                    column_warnings.extend(warnings_for_column)
                    column_texts.append(column_text)
                raw_text, postprocessing = join_column_texts(column_texts, effective_direction)
                preprocessing = column_preprocessing
                request_image_path = image_path
                initial_warnings = list(dict.fromkeys(column_warnings + quality_warnings(raw_text)))
                if column_recoveries:
                    recovery = {
                        "strategy": "per_column_plain_text_retry",
                        "reason": "coordinate_dump",
                        "succeeded": all(item.get("succeeded") for item in column_recoveries),
                        "columns": column_recoveries,
                    }
                use_vertical_postprocessing = False
            else:
                request_image_path, vertical_preprocessing = prepare_vertical_long_strip(
                    image_path,
                    region_hint,
                    args.model,
                    prepared_dir,
                    args.vertical_long_strip_ratio,
                    args.disable_vertical_long_strip_padding,
                )
                preprocessing = {**column_preprocessing, **vertical_preprocessing}
                if column_preprocessing and vertical_preprocessing:
                    preprocessing["column_detection"] = column_preprocessing
                raw_text = call_vlm_api(
                    request_image_path,
                    args.api_url,
                    args.api_key,
                    args.model,
                    prompt_with_region_hint(args.prompt, region_hint, bool(vertical_preprocessing)),
                    args.temperature,
                    args.max_tokens,
                    args.retries,
                    args.retry_delay,
                    args.enable_thinking,
                    args.thinking_budget,
                    args.image_detail,
                    args.disable_thinking,
                )
                initial_warnings = quality_warnings(raw_text)
                if column_preprocessing.get("whole_block_selected"):
                    second_text = call_vlm_api(
                        request_image_path,
                        args.api_url,
                        args.api_key,
                        args.model,
                        prompt_with_region_hint(args.prompt, region_hint, False),
                        args.temperature,
                        args.max_tokens,
                        args.retries,
                        args.retry_delay,
                        args.enable_thinking,
                        args.thinking_budget,
                        args.image_detail,
                        args.disable_thinking,
                    )
                    similarity = normalized_ocr_similarity(raw_text, second_text)
                    consistency = {
                        "strategy": "dual_whole_block",
                        "similarity": round(similarity, 4),
                        "second_text": second_text,
                    }
                    whole_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
                    whole_line_lengths = sorted(len(re.sub(r"\s+", "", line)) for line in whole_lines)
                    median_line_length = (
                        whole_line_lengths[len(whole_line_lengths) // 2] if whole_line_lengths else 0
                    )
                    detected_column_count = int(column_preprocessing.get("detected_column_count") or 0)
                    fragmented_column_output = (
                        len(whole_lines) >= max(6, round(detected_column_count * 0.6))
                        and median_line_length <= 28
                    )
                    whole_warnings = list(
                        dict.fromkeys(quality_warnings(raw_text) + quality_warnings(second_text))
                    )
                    fallback_needed = (
                        similarity < 0.9
                        or fragmented_column_output
                        or any(
                            value.startswith("coordinate_dump")
                            or value.startswith("severe_line_repetition")
                            or value in {"repeated_text_block", "repeated_line_sequence"}
                            for value in whole_warnings
                        )
                    )
                    if fallback_needed:
                        subblock_paths = prepare_vertical_subblock_crops(
                            image_path,
                            column_preprocessing.get("detected_columns") or [],
                            prepared_dir,
                        )
                        subblock_texts = []
                        subblock_checks = []
                        subblock_warnings = []
                        block_prompt = prompt_with_region_hint(OCR_RECOVERY_PROMPT, region_hint, False)
                        for subblock_index, subblock_path in enumerate(subblock_paths, start=1):
                            request_images.append(str(subblock_path))
                            first_subblock = call_vlm_api(
                                subblock_path,
                                args.api_url,
                                args.api_key,
                                args.model,
                                block_prompt,
                                args.temperature,
                                args.max_tokens,
                                args.retries,
                                args.retry_delay,
                                args.enable_thinking,
                                args.thinking_budget,
                                args.image_detail,
                                args.disable_thinking,
                            )
                            second_subblock = call_vlm_api(
                                subblock_path,
                                args.api_url,
                                args.api_key,
                                args.model,
                                block_prompt,
                                args.temperature,
                                args.max_tokens,
                                args.retries,
                                args.retry_delay,
                                args.enable_thinking,
                                args.thinking_budget,
                                args.image_detail,
                                args.disable_thinking,
                            )
                            first_subblock, first_cleanup = strip_coordinate_prefixes(first_subblock)
                            second_subblock, second_cleanup = strip_coordinate_prefixes(second_subblock)
                            first_ordering = {"strategy": "model_natural_vertical_order"}
                            second_ordering = {"strategy": "model_natural_vertical_order"}
                            subblock_orientation = detect_text_orientation(subblock_path)
                            component_count = int(subblock_orientation.get("component_count") or 0)
                            compact_length = len(re.sub(r"\s+", "", first_subblock))
                            component_coverage = compact_length / max(component_count, 1)
                            tertiary_rework = {}
                            if (
                                subblock_index == 1
                                or
                                not first_subblock.strip()
                                or not second_subblock.strip()
                                or (component_count >= 40 and component_coverage < 0.24)
                            ):
                                single_paths, single_metadata = prepare_column_crops(
                                    subblock_path,
                                    {"writing_direction": "vertical", "confidence": 1.0},
                                    args.model,
                                    prepared_dir / "single-columns",
                                    8,
                                    False,
                                )
                                first_columns = []
                                second_columns = []
                                column_checks = []
                                for single_index, single_path in enumerate(single_paths, start=1):
                                    request_images.append(str(single_path))
                                    first_column = call_vlm_api(
                                        single_path,
                                        args.api_url,
                                        args.api_key,
                                        args.model,
                                        SINGLE_VERTICAL_COLUMN_PROMPT,
                                        args.temperature,
                                        args.max_tokens,
                                        args.retries,
                                        args.retry_delay,
                                        args.enable_thinking,
                                        args.thinking_budget,
                                        args.image_detail,
                                        args.disable_thinking,
                                    )
                                    second_column = call_vlm_api(
                                        single_path,
                                        args.api_url,
                                        args.api_key,
                                        args.model,
                                        SINGLE_VERTICAL_COLUMN_PROMPT,
                                        args.temperature,
                                        args.max_tokens,
                                        args.retries,
                                        args.retry_delay,
                                        args.enable_thinking,
                                        args.thinking_budget,
                                        args.image_detail,
                                        args.disable_thinking,
                                    )
                                    first_column, _ = strip_coordinate_prefixes(first_column)
                                    second_column, _ = strip_coordinate_prefixes(second_column)
                                    column_similarity = normalized_ocr_similarity(first_column, second_column)
                                    first_columns.append(first_column)
                                    second_columns.append(second_column)
                                    column_checks.append({
                                        "index": single_index,
                                        "similarity": round(column_similarity, 4),
                                        "first_length": len(re.sub(r"\s+", "", first_column)),
                                        "second_text": second_column,
                                    })
                                rebuilt_first, rebuilt_first_order = join_column_texts(first_columns, "vertical")
                                rebuilt_second, rebuilt_second_order = join_column_texts(second_columns, "vertical")
                                tertiary_succeeded = (
                                    len(single_paths) >= 2
                                    and all(item.get("first_length", 0) > 0 for item in column_checks)
                                    and all(item.get("second_text", "").strip() for item in column_checks)
                                    and all(float(item.get("similarity") or 0) >= 0.9 for item in column_checks)
                                )
                                tertiary_rework = {
                                    "strategy": "single_vertical_column_rework",
                                    "succeeded": tertiary_succeeded,
                                    "column_detection": single_metadata,
                                    "columns": column_checks,
                                }
                                if tertiary_succeeded:
                                    first_subblock = rebuilt_first
                                    second_subblock = rebuilt_second
                                    first_ordering = rebuilt_first_order
                                    second_ordering = rebuilt_second_order
                                    compact_length = len(re.sub(r"\s+", "", first_subblock))
                                    component_coverage = compact_length / max(component_count, 1)
                            subblock_similarity = normalized_ocr_similarity(first_subblock, second_subblock)
                            check = {
                                "index": subblock_index,
                                "image": str(subblock_path),
                                "similarity": round(subblock_similarity, 4),
                                "component_coverage": round(component_coverage, 4),
                                "second_text": second_subblock,
                                "column_ordering": first_ordering,
                            }
                            if first_ordering != second_ordering:
                                check["second_column_ordering"] = second_ordering
                            if tertiary_rework:
                                check["tertiary_rework"] = tertiary_rework
                            if first_cleanup or second_cleanup:
                                check["coordinate_cleanup"] = {
                                    "first": first_cleanup,
                                    "second": second_cleanup,
                                }
                            subblock_checks.append(check)
                            subblock_texts.append(first_subblock)
                            subblock_warnings.extend(quality_warnings(first_subblock))
                            subblock_warnings.extend(quality_warnings(second_subblock))
                            if not first_subblock.strip() or not second_subblock.strip():
                                subblock_warnings.append(f"subblock_ocr_empty:{subblock_index}")
                            if component_count >= 40 and component_coverage < 0.24:
                                subblock_warnings.append(
                                    f"subblock_ocr_low_coverage_{subblock_index}:{component_coverage:.3f}"
                                )
                            if subblock_similarity < 0.9:
                                subblock_warnings.append(
                                    f"dual_ocr_disagreement_subblock_{subblock_index}:{subblock_similarity:.3f}"
                                )
                        rebuilt_text, rebuilt_order = join_column_texts(subblock_texts, "vertical")
                        subblock_warnings.extend(quality_warnings(rebuilt_text))
                        subblock_warnings = list(dict.fromkeys(subblock_warnings))
                        fallback_succeeded = (
                            len(subblock_paths) >= 2
                            and bool(rebuilt_text.strip())
                            and not any(value.startswith("dual_ocr_disagreement") for value in subblock_warnings)
                            and not any(value.startswith("coordinate_dump") for value in subblock_warnings)
                            and not any(value.startswith("subblock_ocr_empty") for value in subblock_warnings)
                            and not any(value.startswith("subblock_ocr_low_coverage") for value in subblock_warnings)
                            and "empty_output" not in subblock_warnings
                        )
                        consistency["subblocks"] = subblock_checks
                        recovery = {
                            "strategy": "vertical_subblock_rework",
                            "reason": (
                                "dual_ocr_disagreement"
                                if similarity < 0.9
                                else "whole_block_column_fragments"
                                if fragmented_column_output
                                else "whole_block_quality_warning"
                            ),
                            "succeeded": fallback_succeeded,
                            "initial_similarity": round(similarity, 4),
                            "subblock_count": len(subblock_paths),
                        }
                        if fallback_succeeded:
                            raw_text = rebuilt_text
                            initial_warnings = subblock_warnings
                            preprocessing["fallback_strategy"] = "vertical_subblock_rework"
                            preprocessing["subblock_count"] = len(subblock_paths)
                            postprocessing = rebuilt_order
                        else:
                            if similarity < 0.9:
                                initial_warnings.append(f"dual_ocr_disagreement:{similarity:.3f}")
                            if fragmented_column_output:
                                initial_warnings.append("whole_block_column_fragments")
                            initial_warnings.extend(whole_warnings)
                            initial_warnings.extend(subblock_warnings)
                use_vertical_postprocessing = bool(vertical_preprocessing)
            if not column_split_used and any(warning.startswith("coordinate_dump") for warning in initial_warnings):
                recovered_text = call_vlm_api(
                    image_path,
                    args.api_url,
                    args.api_key,
                    args.model,
                    OCR_RECOVERY_PROMPT,
                    args.temperature,
                    args.max_tokens,
                    args.retries,
                    args.retry_delay,
                    args.enable_thinking,
                    args.thinking_budget,
                    args.image_detail,
                    args.disable_thinking,
                )
                recovered_text, recovery_cleanup = strip_coordinate_prefixes(recovered_text)
                recovered_warnings = quality_warnings(recovered_text)
                recovery_succeeded = bool(recovered_text.strip()) and not any(
                    warning.startswith("coordinate_dump") for warning in recovered_warnings
                )
                recovery = {
                    "strategy": "direction_agnostic_plain_text_retry",
                    "reason": "coordinate_dump",
                    "succeeded": recovery_succeeded,
                    "initial_warnings": initial_warnings,
                    "initial_text_excerpt": raw_text[:500],
                    "recovered_warnings": recovered_warnings,
                    **({"cleanup": recovery_cleanup} if recovery_cleanup else {}),
                }
                if recovery_succeeded:
                    raw_text = recovered_text
                    request_image_path = image_path
                    use_vertical_postprocessing = False

            raw_text, coordinate_cleanup = strip_coordinate_prefixes(raw_text)
            if column_split_used:
                text = raw_text.strip()
            else:
                detected_columns = int(preprocessing.get("detected_column_count") or 0)
                reverse_chunks = detected_columns > 1
                text, vertical_postprocessing = reverse_vertical_column_order(
                    raw_text,
                    use_vertical_postprocessing,
                    reverse=reverse_chunks,
                )
                if vertical_postprocessing:
                    postprocessing = vertical_postprocessing
            if coordinate_cleanup:
                postprocessing = {
                    **coordinate_cleanup,
                    **({"followed_by": postprocessing} if postprocessing else {}),
                }
            if not text:
                raise RuntimeError("Model returned an empty OCR result.")
            warnings = list(dict.fromkeys(initial_warnings + quality_warnings(raw_text) + quality_warnings(text)))
            elapsed = int(time.monotonic() - started)
            txt_path.write_text(text + ("\n" if text else ""), encoding="utf-8")
            (out_dir / f"{image_path.stem}.md").write_text(text + ("\n" if text else ""), encoding="utf-8")
            (out_dir / f"{image_path.stem}.json").write_text(
                json.dumps(
                    {
                        "image": str(image_path),
                        "request_image": str(request_image_path),
                        **({"request_images": request_images} if request_images else {}),
                        "model": args.model,
                        "image_detail": args.image_detail,
                        "text": text,
                        **({"raw_text": raw_text} if raw_text != text else {}),
                        **({"preprocessing": preprocessing} if preprocessing else {}),
                        **({"postprocessing": postprocessing} if postprocessing else {}),
                        **({"recovery": recovery} if recovery else {}),
                        **({"consistency": consistency} if consistency else {}),
                        "quality_warnings": warnings,
                        "elapsed_seconds": elapsed,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            with log_path.open("a", encoding="utf-8") as log:
                warning_text = ",".join(warnings) if warnings else "none"
                preprocessing_text = preprocessing.get("strategy", "none") if preprocessing else "none"
                recovery_text = recovery.get("strategy", "none") if recovery else "none"
                log.write(
                    f"OK {image_path.name} {elapsed}s preprocessing={preprocessing_text} recovery={recovery_text} warnings={warning_text}\n"
                )
            if warnings:
                print(f"WARNING: {image_path.name}: {', '.join(warnings)}", flush=True)
            print(f"Saved: {txt_path}", flush=True)
        except Exception as exc:
            with log_path.open("a", encoding="utf-8") as log:
                log.write(f"FAILED {image_path.name}: {exc}\n")
            print(f"FAILED: {image_path.name}: {exc}", flush=True)
            if not args.continue_on_error:
                raise
            elapsed = int(time.monotonic() - started)
            placeholder = f"待校对（VLM API 请求失败：{exc}）"
            txt_path.write_text(placeholder + "\n", encoding="utf-8")
            (out_dir / f"{image_path.stem}.md").write_text(placeholder + "\n", encoding="utf-8")
            (out_dir / f"{image_path.stem}.json").write_text(
                json.dumps(
                    {
                        "image": str(image_path),
                        "model": args.model,
                        "image_detail": args.image_detail,
                        "text": "",
                        "error": str(exc),
                        "elapsed_seconds": elapsed,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            print(f"Continued with placeholder: {txt_path}", flush=True)


if __name__ == "__main__":
    main()
