from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError


ROOT = Path(__file__).resolve().parents[1] / "assets" / "images" / "jleague-pokemon"
SUPPORTED = {".png", ".jpg", ".jpeg"}


def main() -> None:
    converted = 0
    skipped: list[str] = []

    for source in sorted(ROOT.iterdir()):
        if source.suffix.lower() not in SUPPORTED:
            continue

        try:
            with Image.open(source) as raw:
                image = ImageOps.exif_transpose(raw)
                image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
                if "A" in image.getbands():
                    image = image.convert("RGBA")
                else:
                    image = image.convert("RGB")
                image.save(source.with_suffix(".webp"), "WEBP", quality=84, method=6)
                converted += 1
        except (UnidentifiedImageError, OSError):
            skipped.append(source.name)

    print(f"converted={converted}")
    print(f"skipped={','.join(skipped) if skipped else 'none'}")


if __name__ == "__main__":
    main()
