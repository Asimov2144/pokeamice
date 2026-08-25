"""Convert Qwen normalized layout JSON files into the local crop annotation format."""

import argparse
import json
import re
from pathlib import Path

from PIL import Image


def local_region_type(value: str) -> str:
    region_type = str(value or "").lower()
    if region_type in {"image", "photo", "illustration", "screenshot", "figure"}:
        return "image"
    if region_type == "caption":
        return "caption"
    if region_type in {"callout", "footer"}:
        return "note"
    return "body"


def parse_layout(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8").strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    data = json.loads(raw)
    if not isinstance(data.get("regions"), list):
        raise ValueError(f"Layout has no regions: {path}")
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--layouts", required=True)
    parser.add_argument("--images", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    layouts_dir = Path(args.layouts)
    images_dir = Path(args.images)
    pages = []
    for layout_path in sorted(layouts_dir.glob("page*.txt")):
        page_name = layout_path.stem + ".jpg"
        image_path = images_dir / page_name
        if not image_path.exists():
            raise SystemExit(f"Missing image for {layout_path.name}: {image_path}")
        with Image.open(image_path) as image:
            width, height = image.size
        layout = parse_layout(layout_path)
        regions = []
        for index, region in enumerate(layout["regions"], start=1):
            bbox = region.get("bbox")
            if not isinstance(bbox, list) or len(bbox) != 4:
                continue
            left, top, right, bottom = [float(value) for value in bbox]
            left, right = sorted((max(0.0, left), min(1000.0, right)))
            top, bottom = sorted((max(0.0, top), min(1000.0, bottom)))
            if right - left < 2 or bottom - top < 2:
                continue
            regions.append(
                {
                    "id": region.get("id") or f"r{index}",
                    "type": local_region_type(region.get("type")),
                    "box": [
                        round(left / 1000 * width),
                        round(top / 1000 * height),
                        round(right / 1000 * width),
                        round(bottom / 1000 * height),
                    ],
                    "order": int(region.get("order") or index),
                    "angle": float(region.get("angle") or 0),
                    "writingDirection": region.get("writing_direction") or "auto",
                    "confidence": region.get("confidence"),
                    "contentMix": region.get("content_mix") or "",
                    "reviewFlags": region.get("review_flags") or [],
                    "imageRef": region.get("caption_for") or "",
                    "note": region.get("note") or "Qwen layout region",
                }
            )
        pages.append(
            {
                "name": page_name,
                "page_type": layout.get("page_type") or "mixed",
                "reading_direction": layout.get("reading_direction") or "left_to_right",
                "regions": regions,
            }
        )

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"pages": pages}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pages": len(pages), "regions": sum(len(page["regions"]) for page in pages), "output": str(output.resolve())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
