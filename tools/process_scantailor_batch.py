import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image

from split_magazine_columns import crop_columns, iter_images


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def resolve_root():
    return Path(__file__).resolve().parents[1]


def resize_image(source, out_dir, long_side):
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{source.stem}_long{long_side}.jpg"
    image = Image.open(source).convert("RGB")
    width, height = image.size
    scale = long_side / max(width, height)
    resized = image.resize((round(width * scale), round(height * scale)), Image.LANCZOS)
    resized.save(out_path, quality=94)
    return out_path


def run_command(command, env):
    print(" ".join(str(part) for part in command))
    subprocess.run(command, check=True, env=env)


def ocr_columns(root, columns_dir, ocr_dir, lang, device, fast, quality_rec, gpu_env):
    venv_name = ".venv-ocr-gpu" if gpu_env else ".venv-ocr"
    python = root / venv_name / "Scripts" / "python.exe"
    script = root / "tools" / "paddle_ocr_test.py"
    command = [
        str(python),
        str(script),
        str(columns_dir),
        "--out",
        str(ocr_dir),
        "--lang",
        lang,
        "--device",
        device,
    ]
    if fast:
        command.append("--fast")
    if quality_rec:
        command.append("--quality-rec")

    env = os.environ.copy()
    env["HOME"] = str(root / ".ocr-home")
    env["USERPROFILE"] = str(root / ".ocr-home")
    env["PADDLE_PDX_CACHE_HOME"] = str(root / ".paddlex-cache")
    env["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "False"
    env["FLAGS_use_mkldnn"] = "false"
    run_command(command, env)


def merge_columns(root, ocr_dir, out_path, direction, min_score, min_height):
    python = root / ".venv-ocr-gpu" / "Scripts" / "python.exe"
    if not python.exists():
        python = root / ".venv-ocr" / "Scripts" / "python.exe"
    script = root / "tools" / "merge_paddle_column_text.py"
    command = [
        str(python),
        str(script),
        str(ocr_dir),
        "--out",
        str(out_path),
        "--direction",
        direction,
        "--min-score",
        str(min_score),
        "--min-height",
        str(min_height),
        "--keep-markers",
    ]
    run_command(command, os.environ.copy())


def main():
    parser = argparse.ArgumentParser(
        description="Process ScanTailor output into resized pages, column crops, OCR JSON/TXT, and merged Markdown."
    )
    parser.add_argument("input", help="ScanTailor output file or folder.")
    parser.add_argument("--out", default="ocr-output-scantailor-batch")
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--long-side", type=int, default=3200)
    parser.add_argument("--top", type=float, default=0.055)
    parser.add_argument("--bottom", type=float, default=0.94)
    parser.add_argument("--pad", type=int, default=28)
    parser.add_argument("--direction", choices=("ltr", "rtl"), default="rtl")
    parser.add_argument("--lang", default="japan")
    parser.add_argument("--device", default="gpu:0")
    parser.add_argument("--cpu", action="store_true", help="Use the CPU OCR environment instead of GPU.")
    parser.add_argument("--no-fast", action="store_true")
    parser.add_argument("--no-quality-rec", action="store_true")
    parser.add_argument("--min-score", type=float, default=0.80)
    parser.add_argument("--min-height", type=float, default=24)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    root = resolve_root()
    input_path = Path(args.input).resolve()
    out_root = (root / args.out).resolve()
    resized_dir = out_root / "resized"
    columns_root = out_root / "columns"
    ocr_root = out_root / "ocr"
    merged_root = out_root / "merged"
    merged_root.mkdir(parents=True, exist_ok=True)

    images = list(iter_images(input_path))
    if args.limit:
        images = images[: args.limit]
    if not images:
        raise SystemExit(f"No images found in {input_path}")

    summary = {
        "source": str(input_path),
        "out": str(out_root),
        "columns": args.columns,
        "long_side": args.long_side,
        "direction": args.direction,
        "pages": [],
    }

    for index, source in enumerate(images, 1):
        print(f"\n[{index}/{len(images)}] {source.name}")
        resized = resize_image(source, resized_dir, args.long_side)
        page_columns_dir = columns_root / resized.stem
        saved_columns, meta_path = crop_columns(
            resized,
            page_columns_dir,
            args.columns,
            args.top,
            args.bottom,
            args.pad,
            args.debug,
        )
        page_ocr_dir = ocr_root / resized.stem
        ocr_columns(
            root,
            page_columns_dir,
            page_ocr_dir,
            args.lang,
            "cpu" if args.cpu else args.device,
            not args.no_fast,
            not args.no_quality_rec,
            not args.cpu,
        )
        merged_path = merged_root / f"{source.stem}.md"
        merge_columns(root, page_ocr_dir, merged_path, args.direction, args.min_score, args.min_height)
        summary["pages"].append(
            {
                "source": str(source),
                "resized": str(resized),
                "columns": [str(path) for path in saved_columns],
                "columns_meta": str(meta_path),
                "ocr": str(page_ocr_dir),
                "merged": str(merged_path),
            }
        )

    summary_path = out_root / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDone: {summary_path}")


if __name__ == "__main__":
    main()
