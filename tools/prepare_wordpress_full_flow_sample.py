"""Prepare one preserved layout page for an end-to-end publishing test.

The scan-library regression fixtures keep lossless-enough region crops even when
the original external scan drive is unavailable.  This helper selects one page,
copies its crops into a self-contained test folder, and reconstructs a visual
comparison sheet at the original layout coordinates.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from PIL import Image


def inner_crop(image: Image.Image, expected_width: int, expected_height: int) -> Image.Image:
    """Remove the annotator's even padding before fitting a crop to its box."""
    if image.width > expected_width and image.height > expected_height:
        extra_x = image.width - expected_width
        extra_y = image.height - expected_height
        image = image.crop(
            (
                extra_x // 2,
                extra_y // 2,
                image.width - (extra_x - extra_x // 2),
                image.height - (extra_y - extra_y // 2),
            )
        )
    return image.resize((expected_width, expected_height), Image.Resampling.LANCZOS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a preserved page for a WordPress full-flow test.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--page-index", type=int, default=0)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--merge-region-ids",
        default="",
        help="Comma-separated region ids that form one continuous reading segment.",
    )
    args = parser.parse_args()

    source_manifest = Path(args.manifest).resolve()
    out_dir = Path(args.out).resolve()
    crops_dir = out_dir / "crops"
    figures_dir = out_dir / "figures"
    crops_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    rows = json.loads(source_manifest.read_text(encoding="utf-8"))
    selected = [row for row in rows if int(row.get("page_index", -1)) == args.page_index]
    if not selected:
        raise SystemExit(f"No page_index={args.page_index} in {source_manifest}")

    merge_ids = {value.strip() for value in args.merge_region_ids.split(",") if value.strip()}
    merge_group = "continuous-" + "-".join(sorted(merge_ids)) if merge_ids else ""

    canvas_width = max(int(row["box"][2]) for row in selected) + 80
    canvas_height = max(int(row["box"][3]) for row in selected) + 80
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    self_contained = []

    for row in sorted(selected, key=lambda item: int(item.get("order", 0))):
        source_crop = Path(row["crop"])
        target_dir = figures_dir if row.get("type") == "image" else crops_dir
        target_crop = target_dir / source_crop.name
        shutil.copy2(source_crop, target_crop)

        x1, y1, x2, y2 = [int(value) for value in row["box"]]
        with Image.open(source_crop) as opened:
            crop = inner_crop(opened.convert("RGB"), x2 - x1, y2 - y1)
        canvas.paste(crop, (x1, y1))

        copied = dict(row)
        if copied.get("region_id") in merge_ids:
            copied["group_id"] = merge_group
        copied["crop"] = str(target_crop.resolve())
        copied["source_image"] = str((out_dir / "reconstructed-page041.jpg").resolve())
        self_contained.append(copied)

    reconstructed = out_dir / "reconstructed-page041.jpg"
    canvas.save(reconstructed, quality=92, optimize=True)
    (out_dir / "region-manifest.json").write_text(
        json.dumps(self_contained, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "SOURCE-NOTE.md").write_text(
        "# Source note\n\n"
        "`reconstructed-page041.jpg` is a coordinate-based comparison sheet rebuilt "
        "from preserved region crops because the external scan drive was offline. "
        "It is suitable for workflow and layout QA, but must not replace the original "
        "scan for final publication.\n",
        encoding="utf-8",
    )
    print(f"Prepared {len(self_contained)} regions: {out_dir}")
    print(f"Reconstructed comparison sheet: {reconstructed}")


if __name__ == "__main__":
    main()
