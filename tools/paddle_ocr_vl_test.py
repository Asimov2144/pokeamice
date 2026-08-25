import argparse
import json
import os
import sys
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["HOME"] = str(ROOT / ".ocr-home")
os.environ["USERPROFILE"] = str(ROOT / ".ocr-home")
os.environ.setdefault("PADDLE_HOME", str(ROOT / ".ocr-home" / "paddle"))
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".ocr-home" / "cache"))
os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(ROOT / ".paddlex-cache"))
os.environ.setdefault("PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT", "False")
os.environ.setdefault("FLAGS_use_mkldnn", "false")
os.environ.setdefault("FLAGS_allocator_strategy", "auto_growth")
os.environ.setdefault("FLAGS_fraction_of_gpu_memory_to_use", "0.82")


def iter_inputs(input_path: Path):
    if input_path.is_file():
        yield input_path
        return
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.tif", "*.tiff", "*.pdf"):
        for path in sorted(input_path.glob(ext)):
            if not path.stem.endswith("_debug"):
                yield path


def safe_jsonable(value):
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except TypeError:
        if isinstance(value, dict):
            return {str(k): safe_jsonable(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [safe_jsonable(item) for item in value]
        return str(value)


def extract_text_from_result(result) -> str:
    chunks = []
    for attr in ("markdown", "md", "text", "content"):
        value = getattr(result, attr, None)
        if isinstance(value, str) and value.strip():
            chunks.append(value.strip())
    if isinstance(result, dict):
        for key in ("markdown", "md", "text", "content"):
            value = result.get(key)
            if isinstance(value, str) and value.strip():
                chunks.append(value.strip())
    if chunks:
        return "\n\n".join(chunks)
    return str(result)


def save_result(result, out_dir: Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    text = extract_text_from_result(result)
    (out_dir / f"{stem}.md").write_text(text.strip() + "\n", encoding="utf-8")
    (out_dir / f"{stem}.txt").write_text(text.strip() + "\n", encoding="utf-8")

    if hasattr(result, "save_to_json"):
        try:
            result.save_to_json(str(out_dir / f"{stem}.json"))
        except TypeError:
            result.save_to_json(str(out_dir))
        except Exception as exc:
            (out_dir / f"{stem}.json.error.txt").write_text(str(exc), encoding="utf-8")
    else:
        data = result if isinstance(result, dict) else getattr(result, "__dict__", str(result))
        (out_dir / f"{stem}.json").write_text(
            json.dumps(safe_jsonable(data), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    if hasattr(result, "save_to_markdown"):
        try:
            result.save_to_markdown(str(out_dir / f"{stem}_export"))
        except Exception as exc:
            (out_dir / f"{stem}.markdown.error.txt").write_text(str(exc), encoding="utf-8")


def run_with_heartbeat(label: str, interval: int, func):
    started = time.monotonic()
    done = threading.Event()

    def beat():
        while not done.wait(interval):
            elapsed = int(time.monotonic() - started)
            print(f"[PaddleOCR-VL] {label} still running... {elapsed}s", flush=True)

    thread = threading.Thread(target=beat, daemon=True)
    thread.start()
    try:
        return func()
    finally:
        done.set()
        elapsed = int(time.monotonic() - started)
        print(f"[PaddleOCR-VL] {label} finished in {elapsed}s", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PaddleOCR-VL local document VLM OCR.")
    parser.add_argument("input", help="Image/PDF file or folder.")
    parser.add_argument("--out", default="ocr-output-paddle-vl")
    parser.add_argument("--pipeline-version", default="v1.6", choices=("v1", "v1.5", "v1.6"))
    parser.add_argument("--backend", default="native")
    parser.add_argument("--device", default="gpu:0")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--no-layout", action="store_true", help="Disable layout detection for cropped text regions.")
    parser.add_argument("--max-new-tokens", type=int, default=2048)
    parser.add_argument("--max-pixels", type=int, default=1600000)
    parser.add_argument("--flat-output", action="store_true")
    parser.add_argument("--heartbeat-seconds", type=int, default=30)
    args = parser.parse_args()

    from paddleocr import PaddleOCRVL

    inputs = list(iter_inputs(Path(args.input).resolve()))
    if args.limit > 0:
        inputs = inputs[: args.limit]
    if not inputs:
        raise SystemExit(f"No supported input files found: {args.input}")

    print("Creating PaddleOCR-VL engine...", flush=True)
    engine = run_with_heartbeat(
        "engine load",
        args.heartbeat_seconds,
        lambda: PaddleOCRVL(
            pipeline_version=args.pipeline_version,
            vl_rec_backend=args.backend,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_layout_detection=not args.no_layout,
            use_chart_recognition=False,
            use_seal_recognition=False,
            use_ocr_for_image_block=False,
            device=args.device,
        ),
    )

    out_dir = (ROOT / args.out).resolve()
    for index, path in enumerate(inputs, start=1):
        print(f"PaddleOCR-VL [{index}/{len(inputs)}]: {path}", flush=True)
        results = run_with_heartbeat(
            f"predict {path.name}",
            args.heartbeat_seconds,
            lambda: engine.predict(
                str(path),
                max_new_tokens=args.max_new_tokens,
                max_pixels=args.max_pixels,
                use_layout_detection=not args.no_layout,
            ),
        )
        page_dir = out_dir if args.flat_output else out_dir / path.stem
        for result_index, result in enumerate(results, start=1):
            suffix = path.stem if len(results) == 1 else f"{path.stem}_{result_index:03d}"
            save_result(result, page_dir, suffix)
        print(f"Saved: {page_dir}", flush=True)


if __name__ == "__main__":
    main()
