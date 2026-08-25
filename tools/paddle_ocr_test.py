import argparse
import json
import os
import sys
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
os.environ["HOME"] = str(ROOT / ".ocr-home")
os.environ["USERPROFILE"] = str(ROOT / ".ocr-home")
os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(ROOT / ".paddlex-cache"))
os.environ.setdefault("PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT", "False")
os.environ.setdefault("FLAGS_use_mkldnn", "false")


def make_sample(path: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 820), "#f8f6f0")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype("C:/Windows/Fonts/YuGothB.ttc", 44)
    body_font = ImageFont.truetype("C:/Windows/Fonts/yumin.ttf", 32)
    small_font = ImageFont.truetype("C:/Windows/Fonts/YuGothM.ttc", 24)

    draw.text((70, 55), "開発者インタビュー", fill="#111111", font=title_font)
    draw.text((70, 125), "ポケットモンスターの世界を作る", fill="#444444", font=small_font)

    left = [
        "聞き手：まず、今回の作品で",
        "もっとも大切にしたことを",
        "教えてください。",
        "",
        "開発者：プレイヤーが自分の",
        "ペースで冒険できることです。",
        "街の表情や人々の会話から、",
        "世界の広がりを感じられるよう",
        "意識しました。",
    ]
    right = [
        "聞き手：制作中に印象的だった",
        "出来事はありますか。",
        "",
        "開発者：小さな演出を何度も",
        "調整したことです。画面の端に",
        "映る看板やポスターにも、",
        "物語の手がかりを入れています。",
    ]
    y = 205
    for line in left:
        draw.text((75, y), line, fill="#161616", font=body_font)
        y += 46
    y = 205
    for line in right:
        draw.text((645, y), line, fill="#161616", font=body_font)
        y += 46

    draw.line((600, 190, 600, 680), fill="#d2ccc1", width=2)
    draw.text((70, 730), "サンプル画像：OCR テスト用", fill="#666666", font=small_font)
    image.save(path, quality=95)


def iter_images(input_path: Path):
    if input_path.is_file():
        yield input_path
        return
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.tif", "*.tiff", "*.pdf"):
        for path in sorted(input_path.glob(ext)):
            if path.stem.endswith("_debug"):
                continue
            yield path


def dump_result_objects(results, out_dir: Path, stem: str) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    text_lines = []
    serializable = []

    for idx, result in enumerate(results):
        if hasattr(result, "json"):
            data = result.json
        elif isinstance(result, dict):
            data = result
        else:
            data = {"repr": repr(result)}
        serializable.append(data)

        payload = data.get("res", data)
        rec_texts = payload.get("rec_texts") or payload.get("texts") or []
        rec_scores = payload.get("rec_scores") or []
        for i, text in enumerate(rec_texts):
            score = rec_scores[i] if i < len(rec_scores) else None
            prefix = f"[{score:.3f}] " if isinstance(score, (int, float)) else ""
            text_lines.append(prefix + str(text))

        markdown = payload.get("markdown") or payload.get("md")
        if markdown:
            md_path = out_dir / f"{stem}_{idx + 1}.md"
            md_path.write_text(str(markdown), encoding="utf-8")

        parsing_blocks = payload.get("parsing_res_list") or []
        if parsing_blocks:
            md_lines = []
            def block_order(item):
                order = item.get("block_order")
                return order if isinstance(order, int) else 999999

            for block in sorted(parsing_blocks, key=block_order):
                label = block.get("block_label", "block")
                order = block.get("block_order", "?")
                bbox = block.get("block_bbox", [])
                content = str(block.get("block_content", "")).strip()
                if not content:
                    continue
                marker = f"[{order}] {label} {bbox}"
                text_lines.append(marker)
                text_lines.append(content)
                text_lines.append("")
                if label in {"paragraph_title", "title"}:
                    md_lines.append(f"## {content}")
                else:
                    md_lines.append(content)
                    md_lines.append("")
            if md_lines:
                md_path = out_dir / f"{stem}_structure.md"
                md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")

    (out_dir / f"{stem}.json").write_text(
        json.dumps(serializable, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    text = "\n".join(text_lines).strip()
    (out_dir / f"{stem}.txt").write_text(text + ("\n" if text else ""), encoding="utf-8")
    return text


def run_ocr(
    paths,
    out_dir: Path,
    lang: str,
    structure: bool,
    fast: bool,
    quality_rec: bool,
    japan_rec: bool,
    device: str,
    restart_each: bool,
    continue_on_error: bool,
) -> None:
    def create_engine():
        if structure:
            from paddleocr import PPStructureV3

            kwargs = {}
            if fast:
                kwargs.update(
                    {
                        "layout_detection_model_name": "PP-DocLayout-S",
                        "text_detection_model_name": "PP-OCRv5_mobile_det",
                        "text_recognition_model_name": "PP-OCRv5_server_rec"
                        if quality_rec
                        else "japan_PP-OCRv3_mobile_rec",
                    }
                )
            elif japan_rec:
                kwargs.update({"text_recognition_model_name": "japan_PP-OCRv3_mobile_rec"})
            return PPStructureV3(
                lang=lang,
                device=device,
                use_doc_orientation_classify=not fast,
                use_doc_unwarping=False,
                use_textline_orientation=not fast,
                use_table_recognition=False,
                use_formula_recognition=False,
                use_chart_recognition=False,
                **kwargs,
            )

        from paddleocr import PaddleOCR

        kwargs = {}
        if fast:
            kwargs.update(
                {
                    "text_detection_model_name": "PP-OCRv5_mobile_det",
                    "text_recognition_model_name": "PP-OCRv5_server_rec"
                    if quality_rec
                    else "japan_PP-OCRv3_mobile_rec",
                }
            )
        elif japan_rec:
            kwargs.update({"text_recognition_model_name": "japan_PP-OCRv3_mobile_rec"})
        return PaddleOCR(
            lang=lang,
            device=device,
            use_doc_orientation_classify=not fast,
            use_doc_unwarping=False,
            use_textline_orientation=not fast,
            **kwargs,
        )

    engine = None if restart_each else create_engine()
    failures = []
    total = len(paths)
    for index, path in enumerate(paths, start=1):
        print(f"OCR [{index}/{total}]: {path}", flush=True)
        try:
            if restart_each:
                engine = create_engine()
            results = engine.predict(str(path))
            text = dump_result_objects(results, out_dir, path.stem)
            preview = text[:600].replace("\n", " / ")
            print(f"Saved: {out_dir / (path.stem + '.txt')}", flush=True)
            if preview:
                safe_preview = preview.encode("utf-8", errors="replace").decode("utf-8")
                print(f"Preview: {safe_preview}", flush=True)
            if restart_each:
                del engine
                engine = None
        except Exception as exc:
            failures.append((path, exc))
            print(f"FAILED: {path}", flush=True)
            traceback.print_exc()
            if not continue_on_error:
                raise

    if failures:
        print("Failures:", flush=True)
        for path, exc in failures:
            print(f"- {path}: {exc}", flush=True)
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local PaddleOCR Japanese OCR tests.")
    parser.add_argument("input", nargs="?", help="Image/PDF file or folder. If omitted, creates a Japanese sample image.")
    parser.add_argument("--out", default="ocr-output", help="Output folder.")
    parser.add_argument("--lang", default="japan", help="PaddleOCR language code, e.g. japan.")
    parser.add_argument("--structure", action="store_true", help="Use PP-StructureV3 document parsing pipeline.")
    parser.add_argument("--fast", action="store_true", help="Use lighter OCR models and skip orientation classifiers.")
    parser.add_argument("--quality-rec", action="store_true", help="Use mobile detection with PP-OCRv5 server recognition.")
    parser.add_argument("--japan-rec", action="store_true", help="Use Japanese-specific recognition model.")
    parser.add_argument("--device", default="cpu", help="Paddle device, e.g. cpu or gpu:0.")
    parser.add_argument("--start", type=int, default=1, help="1-based first image index to process.")
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of images to process. 0 means all.")
    parser.add_argument("--restart-each", action="store_true", help="Recreate OCR engine for every image.")
    parser.add_argument("--continue-on-error", action="store_true", help="Continue batch after a Python-level OCR error.")
    args = parser.parse_args()

    out_dir = ROOT / args.out
    if args.input:
        input_path = Path(args.input).resolve()
    else:
        input_path = ROOT / "test" / "ocr-japanese-sample.jpg"
        make_sample(input_path)
        print(f"Created sample: {input_path}")

    paths = list(iter_images(input_path))
    if not paths:
        raise SystemExit(f"No supported image/PDF files found: {input_path}")
    paths = paths[max(args.start, 1) - 1 :]
    if args.limit > 0:
        paths = paths[: args.limit]
    print(f"Queued {len(paths)} file(s).", flush=True)
    run_ocr(
        paths,
        out_dir,
        args.lang,
        args.structure,
        args.fast,
        args.quality_rec,
        args.japan_rec,
        args.device,
        args.restart_each,
        args.continue_on_error,
    )


if __name__ == "__main__":
    main()
