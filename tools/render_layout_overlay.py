import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


COLORS = {
    "heading": "#ff3b30",
    "interview_body": "#007aff",
    "caption": "#34c759",
    "callout": "#ff9500",
    "footer": "#af52de",
    "screenshot": "#5ac8fa",
    "photo": "#ff2d55",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Render normalized layout regions over an image.")
    parser.add_argument("image")
    parser.add_argument("layout_json")
    parser.add_argument("output")
    parser.add_argument("--max-width", type=int, default=1600)
    args = parser.parse_args()

    image = Image.open(args.image).convert("RGB")
    original_width, original_height = image.size
    if image.width > args.max_width:
        scale = args.max_width / image.width
        image = image.resize((args.max_width, round(image.height * scale)), Image.Resampling.LANCZOS)

    raw = Path(args.layout_json).read_text(encoding="utf-8").strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    layout = json.loads(raw)

    draw = ImageDraw.Draw(image, "RGBA")
    font = ImageFont.load_default()
    for region in layout.get("regions", []):
        left, top, right, bottom = region["bbox"]
        box = (
            round(left / 1000 * image.width),
            round(top / 1000 * image.height),
            round(right / 1000 * image.width),
            round(bottom / 1000 * image.height),
        )
        color = COLORS.get(region.get("type"), "#ffffff")
        rgb = tuple(int(color[index : index + 2], 16) for index in (1, 3, 5))
        draw.rectangle(box, fill=(*rgb, 35), outline=(*rgb, 255), width=5)
        label = f"{region.get('order', '?')} {region.get('id', '')} {region.get('type', '')}"
        label_box = draw.textbbox((box[0] + 5, box[1] + 5), label, font=font)
        draw.rectangle((label_box[0] - 3, label_box[1] - 2, label_box[2] + 3, label_box[3] + 2), fill=(0, 0, 0, 210))
        draw.text((box[0] + 5, box[1] + 5), label, fill=(255, 255, 255, 255), font=font)

    image.save(args.output)
    print(
        json.dumps(
            {
                "source_size": [original_width, original_height],
                "render_size": list(image.size),
                "regions": len(layout.get("regions", [])),
                "output": str(Path(args.output).resolve()),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
