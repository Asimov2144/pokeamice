"""Remove coordinate prefixes from already generated OCR JSON/TXT/Markdown files."""

import argparse
import json
from pathlib import Path

from vlm_api_ocr_regions import quality_warnings, strip_coordinate_prefixes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ocr-dir", required=True)
    args = parser.parse_args()
    ocr_dir = Path(args.ocr_dir).resolve()
    repaired = []
    for json_path in sorted(ocr_dir.glob("*.json")):
        if json_path.name.startswith("_"):
            continue
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        cleaned, detail = strip_coordinate_prefixes(data.get("text") or "")
        if not detail:
            continue
        data["text"] = cleaned
        data["quality_warnings"] = quality_warnings(cleaned)
        previous = data.get("postprocessing") or {}
        data["postprocessing"] = {
            **detail,
            **({"followed_by": previous} if previous else {}),
        }
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for suffix in (".txt", ".md"):
            json_path.with_suffix(suffix).write_text(cleaned + "\n", encoding="utf-8")
        repaired.append(json_path.stem)
    print(json.dumps({"repaired": len(repaired), "items": repaired}, ensure_ascii=False))


if __name__ == "__main__":
    main()
