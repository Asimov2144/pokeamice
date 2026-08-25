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
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "height": height,
            }
        )
    return sorted(rows, key=lambda row: (row["y1"], row["x1"]))


def column_number(path):
    match = COLUMN_RE.search(path.stem)
    if not match:
        return 9999
    return int(match.group(1))


def main():
    parser = argparse.ArgumentParser(description="Merge per-column PaddleOCR JSON into reading-order Markdown.")
    parser.add_argument("input", help="Folder containing *_colNN.json files.")
    parser.add_argument("--out", default="")
    parser.add_argument("--min-score", type=float, default=0.80)
    parser.add_argument("--min-height", type=float, default=24)
    parser.add_argument(
        "--direction",
        choices=("ltr", "rtl"),
        default="ltr",
        help="Column reading order. Use rtl for Japanese vertical magazine pages.",
    )
    parser.add_argument("--keep-markers", action="store_true")
    args = parser.parse_args()

    input_dir = Path(args.input)
    paths = sorted(input_dir.glob("*_col*.json"), key=column_number)
    if not paths:
        raise SystemExit(f"No *_colNN.json files found in {input_dir}")
    if args.direction == "rtl":
        paths = list(reversed(paths))

    lines = []
    for path in paths:
        if args.keep_markers:
            lines.append(f"<!-- column {column_number(path)}: {path.name} -->")
        for row in read_rows(path, args.min_score, args.min_height):
            lines.append(row["text"])
        lines.append("")

    text = "\n".join(lines).strip() + "\n"
    out_path = Path(args.out) if args.out else input_dir / "merged_columns.md"
    out_path.write_text(text, encoding="utf-8")
    print(out_path)
    print(text[:1600])


if __name__ == "__main__":
    main()
