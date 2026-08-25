import argparse
import json
import re
import sys
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


COLUMN_RE = re.compile(r"_col(\d+)$")


def box_metrics(poly):
    xs = [point[0] for point in poly]
    ys = [point[1] for point in poly]
    return min(xs), min(ys), max(xs), max(ys), max(xs) - min(xs), max(ys) - min(ys)


def column_number(path):
    match = COLUMN_RE.search(path.stem)
    if not match:
        return 9999
    return int(match.group(1))


def yaml_block(value, indent):
    prefix = " " * indent
    text = str(value or "").strip()
    if not text:
        return f"{prefix}|-\n{prefix}  "
    lines = text.splitlines()
    return f"{prefix}|-\n" + "\n".join(f"{prefix}  {line}" for line in lines)


def read_column_offsets(metadata_path):
    if not metadata_path:
        return {}
    data = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    offsets = {}
    for column in data.get("columns", []):
        path = Path(column.get("path", ""))
        bbox = column.get("bbox", [0, 0, 0, 0])
        if len(bbox) == 4:
            offsets[path.stem] = {"x": int(bbox[0]), "y": int(bbox[1]), "bbox": bbox}
    return offsets


def read_rows(json_path, min_score, min_height):
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    payload = data[0].get("res", data[0]) if isinstance(data, list) else data.get("res", data)
    texts = payload.get("rec_texts", [])
    scores = payload.get("rec_scores", [])
    polys = payload.get("rec_polys") or payload.get("dt_polys") or []

    rows = []
    for text, score, poly in zip(texts, scores, polys):
        text = str(text).strip()
        if not text or score < min_score:
            continue
        x1, y1, x2, y2, width, height = box_metrics(poly)
        if height < min_height:
            continue
        rows.append(
            {
                "text": text,
                "score": score,
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2),
                "height": int(height),
            }
        )
    return sorted(rows, key=lambda row: (row["y1"], row["x1"]))


def group_rows(rows, gap_ratio, min_gap, speaker_names):
    if not rows:
        return []
    median_height = sorted(row["height"] for row in rows)[len(rows) // 2]
    gap_limit = max(min_gap, median_height * gap_ratio)
    groups = [[rows[0]]]
    previous = rows[0]

    for row in rows[1:]:
        gap = row["y1"] - previous["y2"]
        starts_speaker = row["text"] in speaker_names
        if gap > gap_limit or starts_speaker:
            groups.append([row])
        else:
            groups[-1].append(row)
        previous = row
    return groups


def group_to_segment(group, offset, pad):
    x1 = min(row["x1"] for row in group) + offset["x"] - pad
    y1 = min(row["y1"] for row in group) + offset["y"] - pad
    x2 = max(row["x2"] for row in group) + offset["x"] + pad
    y2 = max(row["y2"] for row in group) + offset["y"] + pad
    text = "\n".join(row["text"] for row in group)
    return {
        "box": [max(0, x1), max(0, y1), max(0, x2), max(0, y2)],
        "text": text,
    }


def render_segments(segments, scan_page, placeholder, include_comments):
    lines = []
    for segment in segments:
        lines.append("  - speaker: \"\"")
        lines.append(f"    scan_page: {scan_page}")
        lines.append(f"    scan_box: [{', '.join(str(value) for value in segment['box'])}]")
        lines.append("    original: " + yaml_block(segment["text"], 4).lstrip())
        lines.append("    translation: " + yaml_block(placeholder, 4).lstrip())
        if include_comments:
            lines.append("    comment: \"OCR 自动生成坐标，需人工校对段落范围与识别文本。\"")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate scan-translation segments with scan_box from PaddleOCR JSON.")
    parser.add_argument("input", help="Folder containing *_colNN.json files, or a single JSON file.")
    parser.add_argument("--columns-meta", default="", help="Column metadata JSON from split_magazine_columns.py.")
    parser.add_argument("--out", default="")
    parser.add_argument("--scan-page", type=int, default=0)
    parser.add_argument("--min-score", type=float, default=0.80)
    parser.add_argument("--min-height", type=float, default=24)
    parser.add_argument("--gap-ratio", type=float, default=1.4)
    parser.add_argument("--min-gap", type=float, default=18)
    parser.add_argument("--pad", type=int, default=8)
    parser.add_argument("--speaker", action="append", default=["増田", "增田", "西野"])
    parser.add_argument("--placeholder", default="待翻译。")
    parser.add_argument("--comments", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.is_dir():
        paths = sorted(input_path.glob("*_col*.json"), key=column_number)
    else:
        paths = [input_path]
    if not paths:
        raise SystemExit(f"No OCR JSON found: {input_path}")

    offsets = read_column_offsets(args.columns_meta)
    segments = []
    for path in paths:
        if path.stem.endswith("_debug"):
            continue
        offset = offsets.get(path.stem, {"x": 0, "y": 0, "bbox": [0, 0, 0, 0]})
        rows = read_rows(path, args.min_score, args.min_height)
        for group in group_rows(rows, args.gap_ratio, args.min_gap, set(args.speaker)):
            if len(group) == 1 and len(group[0]["text"]) <= 2:
                continue
            segments.append(group_to_segment(group, offset, args.pad))

    text = render_segments(segments, args.scan_page, args.placeholder, args.comments)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text[:2400])
    if args.out:
        print(f"\nSaved: {args.out}")


if __name__ == "__main__":
    main()
