import argparse
import json
import sys
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def box_metrics(poly):
    xs = [point[0] for point in poly]
    ys = [point[1] for point in poly]
    return min(xs), min(ys), max(xs), max(ys), max(xs) - min(xs), max(ys) - min(ys)


def cluster_columns(rows, gap_ratio):
    if not rows:
        return []
    rows_by_x = sorted(rows, key=lambda row: row["x1"])
    page_width = max(row["x2"] for row in rows_by_x) - min(row["x1"] for row in rows_by_x)
    gap_threshold = max(80, page_width * gap_ratio)
    columns = [[rows_by_x[0]]]
    current_right = rows_by_x[0]["x2"]
    for row in rows_by_x[1:]:
        if row["x1"] - current_right > gap_threshold:
            columns.append([row])
            current_right = row["x2"]
        else:
            columns[-1].append(row)
            current_right = max(current_right, row["x2"])
    return columns


def main():
    parser = argparse.ArgumentParser(description="Filter PaddleOCR JSON output for magazine text.")
    parser.add_argument("json_path")
    parser.add_argument("--out", default="")
    parser.add_argument("--min-height", type=float, default=22)
    parser.add_argument("--min-score", type=float, default=0.75)
    parser.add_argument("--gap-ratio", type=float, default=0.08)
    args = parser.parse_args()

    data = json.loads(Path(args.json_path).read_text(encoding="utf-8"))
    payload = data[0].get("res", data[0]) if isinstance(data, list) else data.get("res", data)
    texts = payload.get("rec_texts", [])
    scores = payload.get("rec_scores", [])
    polys = payload.get("rec_polys") or payload.get("dt_polys") or []

    rows = []
    for index, (text, score, poly) in enumerate(zip(texts, scores, polys)):
        if not str(text).strip():
            continue
        x1, y1, x2, y2, width, height = box_metrics(poly)
        if height < args.min_height or score < args.min_score:
            continue
        rows.append(
            {
                "index": index,
                "text": str(text).strip(),
                "score": score,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "height": height,
            }
        )

    columns = cluster_columns(rows, args.gap_ratio)
    lines = []
    for column_index, column in enumerate(columns, 1):
        if len(columns) > 1:
            lines.append(f"<!-- column {column_index} -->")
        for row in sorted(column, key=lambda item: (item["y1"], item["x1"])):
            lines.append(row["text"])
        lines.append("")
    text = "\n".join(lines).strip() + "\n"

    if args.out:
        out_path = Path(args.out)
    else:
        src = Path(args.json_path)
        out_path = src.with_name(src.stem + "_filtered.md")
    out_path.write_text(text, encoding="utf-8")
    print(out_path)
    print(text[:1200])


if __name__ == "__main__":
    main()
