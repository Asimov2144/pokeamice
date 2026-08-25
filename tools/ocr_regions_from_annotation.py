import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def slugify(value: str) -> str:
    value = re.sub(r"[^\w\u3040-\u30ff\u3400-\u9fff-]+", "-", value, flags=re.UNICODE)
    return value.strip("-")[:48] or "region"


def yaml_string(value: str) -> str:
    return str(value or "").replace("\\", "\\\\").replace('"', '\\"')


def public_output_file(out_dir: Path, subdir: str, filename: str) -> str:
    try:
        public_root = out_dir.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        public_root = out_dir.name
    return f"/{public_root}/{subdir}/{filename}"


def load_annotation(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("pages"), list):
        raise SystemExit(f"Invalid annotation JSON: {path}")
    return data


def find_image(images_dir: Path, page_name: str) -> Path:
    direct = images_dir / page_name
    if direct.exists():
        return direct
    stem = Path(page_name).stem
    matches = sorted(images_dir.glob(stem + ".*"))
    if matches:
        return matches[0]

    lower_name = page_name.lower()
    lower_stem = stem.lower()
    image_exts = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
    files = [path for path in images_dir.glob("*") if path.is_file() and path.suffix.lower() in image_exts]
    for path in files:
        if path.name.lower() == lower_name or path.stem.lower() == lower_stem:
            return path

    page_number = re.search(r"(\d{3,})", stem)
    if page_number:
        token = page_number.group(1)
        numbered = [path for path in files if token in path.stem]
        if len(numbered) == 1:
            return numbered[0]
        if numbered:
            names = ", ".join(path.name for path in numbered[:8])
            raise FileNotFoundError(
                f"Multiple possible images for {page_name} in {images_dir}: {names}"
            )

    recursive_matches = sorted(images_dir.rglob(stem + ".*"))
    recursive_matches = [path for path in recursive_matches if path.is_file()]
    if recursive_matches:
        return recursive_matches[0]

    sample = ", ".join(path.name for path in files[:12]) or "no supported image files found"
    raise FileNotFoundError(
        f"Cannot find source image for page: {page_name}\n"
        f"Image directory: {images_dir}\n"
        f"Sample files: {sample}"
    )


def normalized_box(box, width: int, height: int, padding: int) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = [float(item) for item in box]
    left = max(0, int(round(min(x1, x2))) - padding)
    top = max(0, int(round(min(y1, y2))) - padding)
    right = min(width, int(round(max(x1, x2))) + padding)
    bottom = min(height, int(round(max(y1, y2))) + padding)
    if right <= left or bottom <= top:
        raise ValueError(f"Invalid crop box: {box}")
    return left, top, right, bottom


def resize_to_max_pixels(image: Image.Image, max_pixels: int) -> Image.Image:
    if max_pixels <= 0:
        return image
    pixels = image.width * image.height
    if pixels <= max_pixels:
        return image
    scale = (max_pixels / pixels) ** 0.5
    new_size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    return image.resize(new_size, Image.LANCZOS)


def deskew_crop(image: Image.Image, angle: float) -> Image.Image:
    """Rotate a crop back toward horizontal before OCR when an annotation has angle."""
    try:
        value = float(angle or 0)
    except (TypeError, ValueError):
        value = 0.0
    if abs(value) < 0.05:
        return image
    resampling = getattr(Image, "Resampling", Image)
    return image.rotate(value, expand=True, fillcolor=(255, 255, 255), resample=resampling.BICUBIC)


def mask_exclusions(crop: Image.Image, exclusions: list, crop_box: tuple[int, int, int, int]) -> Image.Image:
    """Paint manually marked interference ranges white before OCR."""
    if not exclusions:
        return crop
    left, top, right, bottom = crop_box
    draw = ImageDraw.Draw(crop)
    for exclusion in exclusions:
        if not isinstance(exclusion, (list, tuple)) or len(exclusion) != 4:
            continue
        try:
            ex_left, ex_top, ex_right, ex_bottom = [float(value) for value in exclusion]
        except (TypeError, ValueError):
            continue
        x1 = max(left, min(ex_left, ex_right)) - left
        y1 = max(top, min(ex_top, ex_bottom)) - top
        x2 = min(right, max(ex_left, ex_right)) - left
        y2 = min(bottom, max(ex_top, ex_bottom)) - top
        if x2 > x1 and y2 > y1:
            draw.rectangle((round(x1), round(y1), round(x2), round(y2)), fill=(255, 255, 255))
    return crop


def crop_regions(annotation: dict, images_dir: Path, out_dir: Path, padding: int, max_crop_pixels: int = 0) -> list[dict]:
    crops_dir = out_dir / "crops"
    figures_dir = out_dir / "figures"
    crops_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    manifest = []

    for page_index, page in enumerate(annotation["pages"]):
        page_name = page.get("name") or f"page{page_index + 1:03d}"
        source = find_image(images_dir, page_name)
        image = Image.open(source).convert("RGB")
        width, height = image.size
        regions = [
            region for region in page.get("regions", [])
            if region.get("type") != "ignore" and region.get("box")
        ]
        regions.sort(key=lambda item: (int(item.get("order") or 9999), item.get("id") or ""))

        for region_index, region in enumerate(regions, start=1):
            order = int(region.get("order") or region_index)
            region_id = region.get("id") or f"r{region_index:03d}"
            label = region.get("speaker") or region.get("type") or "body"
            filename = f"p{page_index + 1:03d}_o{order:03d}_{slugify(label)}_{slugify(region_id)}.jpg"
            is_image = region.get("type") == "image"
            crop_path = (figures_dir if is_image else crops_dir) / filename
            crop_box = normalized_box(region["box"], width, height, padding)
            angle = float(region.get("angle") or 0)
            crop = image.crop(crop_box)
            crop = mask_exclusions(crop, region.get("exclusions") or region.get("excludeBoxes") or [], crop_box)
            crop = deskew_crop(crop, angle)
            crop = resize_to_max_pixels(crop, max_crop_pixels)
            crop.save(crop_path, quality=95)
            manifest.append({
                "page_index": page_index,
                "page_name": page_name,
                "source_image": str(source.resolve()),
                "crop": str(crop_path),
                "crop_name": crop_path.stem,
                "region_id": region_id,
                "group_id": region.get("groupId") or "",
                "image_ref": region.get("imageRef") or region.get("captionFor") or "",
                "writing_direction": region.get("writingDirection") or region.get("writing_direction") or "auto",
                "confidence": region.get("confidence"),
                "content_mix": region.get("contentMix") or region.get("content_mix") or "",
                "review_flags": region.get("reviewFlags") or region.get("review_flags") or [],
                "type": region.get("type") or "body",
                "speaker": label,
                "order": order,
                "box": region["box"],
                "angle": angle,
                "exclusions": region.get("exclusions") or region.get("excludeBoxes") or [],
                "crop_width": crop.width,
                "crop_height": crop.height,
                "note": region.get("note") or "",
            })

    infer_caption_links(manifest)
    (out_dir / "region-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Cropped {len(manifest)} region(s): {crops_dir}")
    return manifest


def infer_caption_links(manifest: list[dict]) -> None:
    """Pair caption regions with the closest preceding image in reading order."""
    pages = sorted({int(item.get("page_index") or 0) for item in manifest})
    for page_index in pages:
        page_items = sorted(
            [item for item in manifest if int(item.get("page_index") or 0) == page_index],
            key=lambda item: (int(item.get("order") or 0), item.get("region_id") or ""),
        )
        images = [item for item in page_items if item.get("type") == "image"]
        for caption in [item for item in page_items if item.get("type") == "caption"]:
            if caption.get("image_ref") and any(image.get("region_id") == caption["image_ref"] for image in images):
                continue
            preceding = [image for image in images if int(image.get("order") or 0) <= int(caption.get("order") or 0)]
            linked = preceding[-1] if preceding else (images[0] if images else None)
            caption["image_ref"] = linked.get("region_id") if linked else ""


def read_ocr_text(ocr_dir: Path, crop_name: str) -> str:
    txt_path = ocr_dir / f"{crop_name}.txt"
    if not txt_path.exists():
        return ""
    lines = []
    for line in txt_path.read_text(encoding="utf-8", errors="replace").splitlines():
        cleaned = re.sub(r"^\[[0-9.]+\]\s*", "", line).strip()
        if cleaned:
            lines.append(cleaned)
    return "\n".join(lines).strip()


def read_ocr_metadata(ocr_dir: Path, crop_name: str) -> dict:
    path = ocr_dir / f"{crop_name}.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def grouped_manifest(manifest: list[dict]) -> list[dict]:
    emitted = set()
    items = []
    for item in sorted(manifest, key=lambda row: (row["page_index"], row["order"])):
        group_id = item.get("group_id")
        if group_id:
            if group_id in emitted:
                continue
            members = [
                row for row in manifest
                if row.get("group_id") == group_id
            ]
            members.sort(key=lambda row: (row["page_index"], row["order"]))
            emitted.add(group_id)
            merged = dict(item)
            merged["members"] = members
            items.append(merged)
        else:
            merged = dict(item)
            merged["members"] = [item]
            items.append(merged)
    return items


def merge_outputs(out_dir: Path, ocr_dir: Path) -> None:
    manifest_path = out_dir / "region-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    infer_caption_links(manifest)
    grouped = grouped_manifest(manifest)

    md_lines = ["# Region OCR", ""]
    yaml_lines = ["translation_segments:"]
    for index, item in enumerate(grouped, start=1):
        is_image = item.get("type") == "image"
        texts = [] if is_image else [read_ocr_text(ocr_dir, member["crop_name"]) for member in item["members"]]
        ocr_metadata = [] if is_image else [read_ocr_metadata(ocr_dir, member["crop_name"]) for member in item["members"]]
        effective_directions = [
            (metadata.get("preprocessing") or {}).get("effective_direction")
            for metadata in ocr_metadata
            if (metadata.get("preprocessing") or {}).get("direction_overridden")
        ]
        resolved_direction = effective_directions[0] if effective_directions else item.get("writing_direction") or "auto"
        auto_column_counts = [
            int((metadata.get("postprocessing") or {}).get("column_count") or 0)
            for metadata in ocr_metadata
            if (metadata.get("preprocessing") or {}).get("strategy") == "physical_column_split"
        ]
        text = "\n".join(part for part in texts if part).strip()
        box_key = "scan_boxes" if len(item["members"]) > 1 else "scan_box"
        public_image = public_output_file(out_dir, "figures", Path(item["crop"]).name) if is_image else ""

        md_lines.append(f"## {index}. {item['speaker']}")
        md_lines.append("")
        md_lines.append(f"- page: {item['page_name']}")
        md_lines.append(f"- page_index: {item['page_index']}")
        md_lines.append(f"- source_image: {item.get('source_image') or ''}")
        md_lines.append(f"- type: {item['type']}")
        md_lines.append(f"- kind: {'image' if is_image else 'caption' if item.get('type') == 'caption' else 'text'}")
        md_lines.append(f"- speaker: {item['speaker']}")
        md_lines.append(f"- order: {item['order']}")
        if not is_image:
            md_lines.append(f"- writing_direction: {resolved_direction}")
            if auto_column_counts:
                md_lines.append(f"- auto_column_count: {sum(auto_column_counts)}")
        md_lines.append(f"- region_id: {item['region_id']}")
        if item.get("group_id"):
            md_lines.append(f"- group_id: {item['group_id']}")
        md_lines.append(f"- scan_box: {json.dumps(item['box'], ensure_ascii=False)}")
        md_lines.append(f"- angle: {item.get('angle') or 0}")
        md_lines.append(f"- exclusions: {json.dumps(item.get('exclusions') or [], ensure_ascii=False)}")
        if public_image:
            md_lines.append(f"- image: {public_image}")
        if item.get("image_ref"):
            md_lines.append(f"- caption_for: {item['image_ref']}")
        if item.get("note"):
            md_lines.append(f"- note: {item['note']}")
        md_lines.append("")
        md_lines.append(f"![{item['speaker']}]({public_image})" if is_image else (text or "待校对"))
        md_lines.append("")

        yaml_lines.append(f'  - speaker: "{yaml_string(item["speaker"])}"')
        item_kind = "image" if is_image else "caption" if item.get("type") == "caption" else "text"
        yaml_lines.append(f'    kind: "{item_kind}"')
        yaml_lines.append(f"    scan_page: {item['page_index']}")
        yaml_lines.append(f'    page_name: "{yaml_string(item["page_name"])}"')
        if item.get("source_image"):
            yaml_lines.append(f'    source_image: "{yaml_string(item["source_image"])}"')
        yaml_lines.append(f'    region_type: "{yaml_string(item["type"])}"')
        yaml_lines.append(f"    order: {item['order']}")
        if not is_image:
            yaml_lines.append(f'    writing_direction: "{yaml_string(resolved_direction)}"')
            if auto_column_counts:
                yaml_lines.append(f"    auto_column_count: {sum(auto_column_counts)}")
        yaml_lines.append(f'    region_id: "{yaml_string(item["region_id"])}"')
        if item.get("group_id"):
            yaml_lines.append(f'    group_id: "{yaml_string(item["group_id"])}"')
        if item.get("image_ref"):
            yaml_lines.append(f'    caption_for: "{yaml_string(item["image_ref"])}"')
        if item.get("angle"):
            yaml_lines.append(f"    angle: {item['angle']}")
        if item.get("exclusions"):
            yaml_lines.append(f"    exclusions: {json.dumps(item['exclusions'], ensure_ascii=False)}")
        if item.get("note"):
            yaml_lines.append(f'    annotation_note: "{yaml_string(item["note"])}"')
        if box_key == "scan_boxes":
            cross_page = any(member["page_index"] != item["page_index"] for member in item["members"])
            if cross_page:
                yaml_lines.append(f"    scan_box: [{', '.join(str(value) for value in item['box'])}]")
                yaml_lines.append("    scan_targets:")
                for member in item["members"]:
                    yaml_lines.append(f"      - scan_page: {member['page_index']}")
                    yaml_lines.append(f"        scan_box: [{', '.join(str(value) for value in member['box'])}]")
            else:
                yaml_lines.append("    scan_boxes:")
                for member in item["members"]:
                    yaml_lines.append(f"      - [{', '.join(str(value) for value in member['box'])}]")
        else:
            yaml_lines.append(f"    scan_box: [{', '.join(str(value) for value in item['box'])}]")
        if is_image:
            yaml_lines.append(f'    image: "{yaml_string(public_image)}"')
            yaml_lines.append(f'    alt: "{yaml_string(item["speaker"] or "杂志图片")}"')
        else:
            yaml_lines.append("    original: |-")
            for line in (text or "待校对").splitlines():
                yaml_lines.append(f"      {line}")
            yaml_lines.append("    translation: |-")
            yaml_lines.append("      待翻译")
        notes = [member.get("note") for member in item["members"] if member.get("note")]
        if notes:
            yaml_lines.append(f'    comment: "{yaml_string(" / ".join(dict.fromkeys(notes)))}"')

    (out_dir / "regions-ocr.md").write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    (out_dir / "translation-segments.yml").write_text("\n".join(yaml_lines).strip() + "\n", encoding="utf-8")
    print(f"Merged Markdown: {out_dir / 'regions-ocr.md'}")
    print(f"Merged YAML: {out_dir / 'translation-segments.yml'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crop annotation regions and merge PaddleOCR text.")
    parser.add_argument("--annotation", required=True, help="JSON exported from magazine-region-annotator.html.")
    parser.add_argument("--images", required=True, help="Folder containing original page images.")
    parser.add_argument("--out", required=True, help="Output folder.")
    parser.add_argument("--ocr-dir", help="PaddleOCR txt/json output folder for cropped regions.")
    parser.add_argument("--padding", type=int, default=16)
    parser.add_argument("--max-crop-pixels", type=int, default=0, help="Resize cropped region images before OCR. 0 keeps original crop size.")
    parser.add_argument("--merge-only", action="store_true")
    args = parser.parse_args()

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not args.merge_only:
        crop_regions(load_annotation(Path(args.annotation)), Path(args.images), out_dir, args.padding, args.max_crop_pixels)
    if args.ocr_dir:
        merge_outputs(out_dir, Path(args.ocr_dir).resolve())


if __name__ == "__main__":
    main()
