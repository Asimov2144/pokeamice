"""Audit region crops for direction conflicts and physical multi-column structure."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path


def load_ocr_module():
    path = Path(__file__).with_name("vlm_api_ocr_regions.py")
    spec = importlib.util.spec_from_file_location("vlm_api_ocr_regions", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit physical columns in a region manifest.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-columns", type=int, default=16)
    args = parser.parse_args()

    module = load_ocr_module()
    manifest_path = Path(args.manifest).resolve()
    rows = json.loads(manifest_path.read_text(encoding="utf-8"))
    audit = []
    for item in rows:
        if item.get("type") == "image":
            continue
        crop = Path(item.get("crop") or "")
        orientation = module.detect_text_orientation(crop)
        declared = str(item.get("writing_direction") or "auto").lower()
        detected = orientation.get("direction") or "unknown"
        confidence = float(orientation.get("confidence") or 0)
        effective = detected if detected in {"horizontal", "vertical"} and confidence >= 0.6 else declared
        columns = module.detect_physical_columns(crop, effective, args.max_columns)
        audit.append({
            "page_name": item.get("page_name"),
            "region_id": item.get("region_id"),
            "speaker": item.get("speaker"),
            "crop_name": item.get("crop_name"),
            "declared_direction": declared,
            "detected_direction": detected,
            "direction_confidence": confidence,
            "direction_conflict": detected in {"horizontal", "vertical"} and declared in {"horizontal", "vertical"} and detected != declared and confidence >= 0.6,
            "effective_direction": effective,
            "detected_column_count": int(columns.get("detected_column_count") or 0),
            "auto_split_eligible": len(columns.get("columns") or []) >= 2,
            "too_many_columns": bool(columns.get("too_many_columns")),
        })

    counts = Counter()
    for item in audit:
        counts["direction_conflicts"] += int(item["direction_conflict"])
        counts["multi_column_regions"] += int(item["detected_column_count"] >= 2)
        counts["auto_split_eligible"] += int(item["auto_split_eligible"])
        counts["too_many_columns"] += int(item["too_many_columns"])
    result = {
        "manifest": str(manifest_path),
        "summary": {
            "text_regions": len(audit),
            **dict(counts),
        },
        "regions": audit,
    }
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
