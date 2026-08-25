import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def iter_images(path: Path):
    if path.is_file():
        yield path
        return
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.tif", "*.tiff"):
        yield from sorted(path.glob(ext))


def smooth(values, window):
    if window <= 1:
        return values
    kernel = np.ones(window, dtype=np.float32) / window
    return np.convolve(values, kernel, mode="same")


def find_body_bbox(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    mask = gray < 238
    row_density = smooth(mask.mean(axis=1), max(25, image.height // 120))
    col_density = smooth(mask.mean(axis=0), max(25, image.width // 120))

    rows = np.where(row_density > 0.015)[0]
    cols = np.where(col_density > 0.01)[0]
    if not len(rows) or not len(cols):
        return 0, 0, image.width, image.height

    x1, x2 = int(cols[0]), int(cols[-1])
    y1, y2 = int(rows[0]), int(rows[-1])
    return x1, y1, x2 + 1, y2 + 1


def threshold_text_mask(crop):
    rgb = np.array(crop)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    adaptive = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        51,
        18,
    )
    # Suppress the very light paper texture but keep black/orange/green text.
    dark = gray < 205
    mask = (adaptive > 0) & dark

    # Remove long page borders, screenshots, and artwork so they do not become
    # fake text columns.
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask.astype(np.uint8), connectivity=8
    )
    clean = np.zeros_like(mask, dtype=np.uint8)
    area_limit = crop.width * crop.height * 0.035
    for label in range(1, num_labels):
        x, y, w, h, area = stats[label]
        if area < 4:
            continue
        if area > area_limit:
            continue
        if h > crop.height * 0.35 and w > crop.width * 0.02:
            continue
        clean[labels == label] = 1
    return clean.astype(bool)


def find_column_cuts(mask, columns):
    density = smooth(mask.mean(axis=0), max(15, mask.shape[1] // 80))
    active = np.where(density > max(0.003, density.max() * 0.08))[0]
    if not len(active):
        return [0, mask.shape[1]]

    left, right = int(active[0]), int(active[-1])
    cuts = [left]
    current_left = left
    for remaining in range(columns, 1, -1):
        span = right - current_left
        expected = current_left + span / remaining
        lo = int(max(current_left + span * 0.22 / remaining, expected - span * 0.18))
        hi = int(min(right - span * 0.12, expected + span * 0.18))
        if hi <= lo:
            cut = int(expected)
        else:
            valley = density[lo:hi]
            min_value = valley.min()
            candidates = np.where(valley <= min_value + max(0.001, density.max() * 0.03))[0]
            cut = lo + int(candidates[len(candidates) // 2])
        cuts.append(cut)
        current_left = cut
    cuts.append(right)
    return sorted(set(cuts))


def box_metrics(poly):
    xs = [point[0] for point in poly]
    ys = [point[1] for point in poly]
    return min(xs), min(ys), max(xs), max(ys), max(xs) - min(xs), max(ys) - min(ys)


def load_ocr_rows(json_path, image_width, image_height, min_score, min_height):
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    payload = data[0].get("res", data[0]) if isinstance(data, list) else data.get("res", data)
    texts = payload.get("rec_texts", [])
    scores = payload.get("rec_scores", [])
    polys = payload.get("rec_polys") or payload.get("dt_polys") or []
    rows = []
    for text, score, poly in zip(texts, scores, polys):
        if not str(text).strip() or score < min_score:
            continue
        x1, y1, x2, y2, width, height = box_metrics(poly)
        if height < min_height or width < 28:
            continue
        if y1 < image_height * 0.05 or y2 > image_height * 0.93:
            continue
        # Edge fragments are usually neighboring page bleed, not the active page.
        if x2 < image_width * 0.08 or x1 > image_width * 0.96:
            continue
        rows.append(
            {
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2),
                "center": (float(x1) + float(x2)) / 2,
                "text": str(text).strip(),
                "score": float(score),
            }
        )
    return rows


def find_column_boxes_from_rows(rows, image_width, image_height, columns, pad):
    coverage = np.zeros(image_width, dtype=np.float32)
    for row in rows:
        coverage[max(0, row["x1"]): min(image_width, row["x2"] + 1)] += 1
    coverage = smooth(coverage, max(15, image_width // 140))
    threshold = max(1.0, coverage.max() * 0.16)
    active = np.where(coverage >= threshold)[0]
    if not len(active):
        return []

    raw_segments = []
    start = int(active[0])
    previous = int(active[0])
    for value in active[1:]:
        value = int(value)
        if value > previous + 1:
            raw_segments.append((start, previous))
            start = value
        previous = value
    raw_segments.append((start, previous))

    scored = []
    for x1, x2 in raw_segments:
        members = [
            row for row in rows if not (row["x2"] < x1 or row["x1"] > x2)
        ]
        if len(members) < 4:
            continue
        score = float(coverage[x1:x2 + 1].sum()) + len(members) * 200
        scored.append((score, x1, x2, members))

    selected = sorted(scored, reverse=True)[:columns]
    boxes = []
    for _, _, _, members in selected:
        x1 = min(row["x1"] for row in members)
        y1 = min(row["y1"] for row in members)
        x2 = max(row["x2"] for row in members)
        y2 = max(row["y2"] for row in members)
        boxes.append(
            (
                max(0, x1 - pad),
                max(0, y1 - pad),
                min(image_width, x2 + pad),
                min(image_height, y2 + pad),
            )
        )
    return sorted(boxes, key=lambda box: box[0])


def crop_columns(image_path, out_dir, columns, top, bottom, pad, debug):
    image = Image.open(image_path).convert("RGB")
    body_x1, body_y1, body_x2, body_y2 = find_body_bbox(image)
    body_y1 = max(body_y1, int(image.height * top))
    body_y2 = min(body_y2, int(image.height * bottom))
    body = image.crop((body_x1, body_y1, body_x2, body_y2))
    mask = threshold_text_mask(body)
    cuts = find_column_cuts(mask, columns)

    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    metadata = {
        "source": str(image_path),
        "image_size": [image.width, image.height],
        "body_bbox": [body_x1, body_y1, body_x2, body_y2],
        "columns": [],
    }

    for index, (x1, x2) in enumerate(zip(cuts, cuts[1:]), 1):
        if x2 - x1 < image.width * 0.08:
            continue
        crop_box = (
            max(0, body_x1 + x1 - pad),
            max(0, body_y1 - pad),
            min(image.width, body_x1 + x2 + pad),
            min(image.height, body_y2 + pad),
        )
        column = image.crop(crop_box)
        out_path = out_dir / f"{image_path.stem}_col{index:02d}{image_path.suffix.lower()}"
        column.save(out_path, quality=95)
        saved.append(out_path)
        metadata["columns"].append(
            {"index": index, "bbox": list(crop_box), "path": str(out_path)}
        )

    meta_path = out_dir / f"{image_path.stem}_columns.json"
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    if debug:
        overlay = np.array(image).copy()
        for column in metadata["columns"]:
            x1, y1, x2, y2 = column["bbox"]
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 0, 0), max(2, image.width // 900))
        Image.fromarray(overlay).save(out_dir / f"{image_path.stem}_debug.jpg", quality=92)

    return saved, meta_path


def crop_columns_from_ocr(image_path, json_path, out_dir, columns, pad, min_score, min_height, debug):
    image = Image.open(image_path).convert("RGB")
    rows = load_ocr_rows(json_path, image.width, image.height, min_score, min_height)
    boxes = find_column_boxes_from_rows(rows, image.width, image.height, columns, pad)
    if not boxes:
        raise SystemExit(f"No column boxes detected from {json_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    metadata = {
        "source": str(image_path),
        "ocr_json": str(json_path),
        "image_size": [image.width, image.height],
        "columns": [],
    }

    for index, crop_box in enumerate(boxes, 1):
        column = image.crop(crop_box)
        out_path = out_dir / f"{image_path.stem}_col{index:02d}{image_path.suffix.lower()}"
        column.save(out_path, quality=95)
        saved.append(out_path)
        metadata["columns"].append(
            {"index": index, "bbox": list(crop_box), "path": str(out_path)}
        )

    meta_path = out_dir / f"{image_path.stem}_columns.json"
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    if debug:
        overlay = np.array(image).copy()
        for column in metadata["columns"]:
            x1, y1, x2, y2 = column["bbox"]
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 180, 255), max(2, image.width // 900))
        Image.fromarray(overlay).save(out_dir / f"{image_path.stem}_debug.jpg", quality=92)

    return saved, meta_path


def main():
    parser = argparse.ArgumentParser(description="Split magazine scans into reading columns before OCR.")
    parser.add_argument("input", help="Image file or folder.")
    parser.add_argument("--out", default="test/magazine-columns")
    parser.add_argument("--columns", type=int, default=2)
    parser.add_argument("--top", type=float, default=0.055, help="Ignore page area above this ratio.")
    parser.add_argument("--bottom", type=float, default=0.92, help="Ignore page area below this ratio.")
    parser.add_argument("--pad", type=int, default=28)
    parser.add_argument("--ocr-json", default="", help="Use PaddleOCR JSON boxes to infer columns.")
    parser.add_argument("--min-score", type=float, default=0.78)
    parser.add_argument("--min-height", type=float, default=20)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    out_dir = Path(args.out).resolve()
    for image_path in iter_images(input_path):
        if args.ocr_json:
            ocr_json = Path(args.ocr_json).resolve()
            if ocr_json.is_dir():
                ocr_json = ocr_json / f"{image_path.stem}.json"
            if not ocr_json.exists():
                raise SystemExit(f"OCR JSON not found for {image_path.name}: {ocr_json}")
            saved, meta_path = crop_columns_from_ocr(
                image_path,
                ocr_json,
                out_dir,
                args.columns,
                args.pad,
                args.min_score,
                args.min_height,
                args.debug,
            )
        else:
            saved, meta_path = crop_columns(
                image_path, out_dir, args.columns, args.top, args.bottom, args.pad, args.debug
            )
        print(f"{image_path.name}: {len(saved)} columns")
        print(meta_path)
        for path in saved:
            print(path)


if __name__ == "__main__":
    main()
