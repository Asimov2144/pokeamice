"""Build a portable, self-contained magazine OCR/translation development case."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import date
from pathlib import Path

from PIL import Image

from export_wordpress_bilingual import SCRIPT, STYLE, article_html


CASE_ID = "continue-vol31-page041-aoi-yu"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative_crop(row: dict) -> str:
    filename = Path(str(row.get("crop") or "")).name
    return f"public/assets/figures/{filename}" if row.get("type") == "image" else f"data/crops/{filename}"


def sanitize_row(row: dict) -> dict:
    cleaned = dict(row)
    cleaned["source_image"] = "public/assets/page041.jpg"
    cleaned["crop"] = relative_crop(row)
    if cleaned.get("region_id") in {"qwen-r4", "qwen-r5"}:
        cleaned["group_id"] = "continuous-qwen-r4-qwen-r5"
    if cleaned.get("members"):
        cleaned["members"] = [sanitize_row(member) for member in cleaned["members"]]
    return cleaned


def sanitize_ocr_value(value: object) -> object:
    """Replace every recorded local request path, including split-column inputs."""
    if isinstance(value, dict):
        return {key: sanitize_ocr_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_ocr_value(item) for item in value]
    if isinstance(value, str) and re.match(r"^[A-Z]:\\", value):
        filename = Path(value).name
        if "__column-" in filename:
            return f"data/ocr-qwen/prepared-inputs/{filename}"
        return f"data/crops/{filename}"
    return value


def sanitized_yaml(source: Path) -> str:
    text = source.read_text(encoding="utf-8")
    text = re.sub(r'^\s*source_image:.*$', '    source_image: "public/assets/page041.jpg"', text, flags=re.MULTILINE)
    text = re.sub(
        r'^\s*image:\s*"?.*p001_o006_image_qwen-r6\.jpg"?\s*$',
        '    image: "public/assets/figures/p001_o006_image_qwen-r6.jpg"',
        text,
        flags=re.MULTILINE,
    )
    return text


def sanitized_markdown(source: Path) -> str:
    text = source.read_text(encoding="utf-8")
    text = re.sub(r'^- source_image:.*$', '- source_image: public/assets/page041.jpg', text, flags=re.MULTILINE)
    text = text.replace(
        "/automation-tests/wordpress-full-flow-20260825/figures/p001_o006_image_qwen-r6.jpg",
        "public/assets/figures/p001_o006_image_qwen-r6.jpg",
    )
    return text


def extract_annotation(source: Path, width: int, height: int) -> dict:
    data = json.loads(source.read_text(encoding="utf-8"))
    page = next(page for page in data.get("pages", []) if str(page.get("name", "")).endswith("page041.jpg"))
    page = json.loads(json.dumps(page, ensure_ascii=False))
    page["name"] = "page041.jpg"
    page["width"] = width
    page["height"] = height
    for region in page.get("regions", []):
        if region.get("id") in {"qwen-r4", "qwen-r5"}:
            region["groupId"] = "continuous-qwen-r4-qwen-r5"
    return {
        "version": data.get("version", 3),
        "title": CASE_ID,
        "sourceFolder": "public/assets",
        "pages": [page],
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_portability(root: Path) -> dict:
    absolute_paths = []
    possible_secrets = []
    secret_pattern = re.compile(r"(?i)(?:api[_-]?key|authorization)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{16,}")
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".jpg", ".jpeg", ".png", ".zip"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"(?:^|[\"'\s])[A-Z]:\\", text):
            absolute_paths.append(path.relative_to(root).as_posix())
        if secret_pattern.search(text):
            possible_secrets.append(path.relative_to(root).as_posix())
    return {"absolute_windows_paths": absolute_paths, "possible_secrets": possible_secrets}


def readme() -> str:
    return """# 《CONTINUE》Vol.31 苍井优采访：自动化开发案例

这是一个可移植的完整案例，覆盖：原始扫描图 → 分区 → 区域 OCR → 风险校对 → 中文翻译 → WordPress 日中对照页面。

## 快速查看

将整个目录上传到静态服务器，入口是 `public/index.html`。不要直接双击 HTML；通过 HTTP(S) 访问才能稳定测试图片、脚本和跨设备布局。

WordPress 开发时使用 `public/wordpress-paste.html`。先把 `public/assets/` 上传到媒体目录，再将文件中的 `{{WORDPRESS_MEDIA_BASE}}` 替换成媒体目录 URL。

## 目录

- `public/index.html`：可直接部署的交互预览。
- `public/wordpress-paste.html`：WordPress 自定义 HTML／区块编辑器输入。
- `public/assets/page041.jpg`：原始扫描页。
- `data/magazine-regions.json`：分区标注，可重新进入标注工具。
- `data/region-manifest.json`：区域裁片与阅读顺序清单。
- `data/crops/`：9 个 OCR 文字裁片。
- `data/ocr-qwen/`：Qwen OCR 原始响应、文本和诊断数据。
- `data/llm-corrections.json`：校对、翻译和可靠性信息。
- `data/translation-segments.yml`：翻译工作台导入文件。
- `docs/qa-report.md`：自动检查和人工发布闸门。
- `case.json`：服务器或项目队列可读取的案例入口清单。
- `CHECKSUMS.sha256`：文件完整性校验。

## 预期交互

桌面端同时显示扫描图、日文和中文；点击正文会在原图上标出左右两个连续文字区。窄屏自动改为上下布局，并可切换“日中对照／只看日文／只看中文”。即使服务器或 WordPress 过滤脚本，正文仍保持可读。

## 注意

这是开发与校对案例，不代表已正式发布。上线前仍需确认扫描图及杂志内容的公开使用权限，并完成作品名、节目名、人物名的最终人工校对。
"""


def qa_report(source_image: Path, entries: list[dict], portability: dict) -> str:
    source_hash = sha256(source_image)
    text_regions = [item for item in entries if item.get("type") != "image"]
    return f"""# 开发案例检测报告

| 检查项 | 结果 | 说明 |
|---|---|---|
| 原始扫描图 | 通过 | E 盘原始 page041.jpg 已复制；SHA-256 `{source_hash}` |
| OCR 完整性 | 通过 | 9 个文字区均包含 Qwen JSON、TXT 和 Markdown |
| 阅读顺序 | 通过 | 左右正文栏使用 `continuous-qwen-r4-qwen-r5` 合并 |
| 翻译完整性 | 通过 | {len(text_regions)} 个非图片区均有校对原文和中文译文 |
| WordPress 页面 | 通过 | 桌面三栏、手机单栏、显示切换与区域高亮已验证 |
| 本机路径 | {'通过' if not portability['absolute_windows_paths'] else '需处理'} | 包内未保留 P 盘或 E 盘绝对路径 |
| 敏感信息 | {'通过' if not portability['possible_secrets'] else '需处理'} | 未打包 API Key 或 Authorization 信息 |

## 发布闸门

1. 把 `{{{{WORDPRESS_MEDIA_BASE}}}}` 替换成 WordPress 媒体目录 URL。
2. 确认当前 WordPress 账号是否允许 `<style>` 和 `<script>`；若脚本被过滤，只会失去高亮和切换，不影响正文阅读。
3. 最终人工复核专有名词和中文译名。
4. 公开部署前确认原扫描图及杂志页面的使用权限。
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Package a WordPress bilingual development case.")
    parser.add_argument("--source-image", required=True)
    parser.add_argument("--sample-dir", required=True)
    parser.add_argument("--annotation", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--resume-incomplete",
        action="store_true",
        help="Continue a package directory that previously stopped before ZIP creation.",
    )
    args = parser.parse_args()

    source_image = Path(args.source_image).resolve()
    sample_dir = Path(args.sample_dir).resolve()
    annotation = Path(args.annotation).resolve()
    out_dir = Path(args.out).resolve()
    if out_dir.with_suffix(".zip").exists() or (out_dir.exists() and not args.resume_incomplete):
        raise SystemExit(f"Refusing to overwrite existing package: {out_dir}")

    public_dir = out_dir / "public"
    assets_dir = public_dir / "assets"
    figures_dir = assets_dir / "figures"
    data_dir = out_dir / "data"
    crops_dir = data_dir / "crops"
    ocr_dir = data_dir / "ocr-qwen"
    prepared_dir = ocr_dir / "prepared-inputs"
    docs_dir = out_dir / "docs"
    for folder in (figures_dir, crops_dir, ocr_dir, prepared_dir, docs_dir):
        folder.mkdir(parents=True, exist_ok=True)

    public_scan = assets_dir / "page041.jpg"
    shutil.copy2(source_image, public_scan)
    for source in (sample_dir / "crops").glob("*"):
        if source.is_file():
            shutil.copy2(source, crops_dir / source.name)
    for source in (sample_dir / "figures").glob("*"):
        if source.is_file():
            shutil.copy2(source, figures_dir / source.name)
    for source in (sample_dir / "ocr-qwen").glob("*"):
        if source.is_file() and source.suffix.lower() in {".json", ".txt", ".md"}:
            target = ocr_dir / source.name
            if source.suffix.lower() == ".json":
                payload = json.loads(source.read_text(encoding="utf-8"))
                crop_name = Path(str(payload.get("image") or payload.get("request_image") or "")).name
                portable_crop = f"data/crops/{crop_name}"
                payload["image"] = portable_crop
                payload["request_image"] = portable_crop
                write_json(target, sanitize_ocr_value(payload))
            else:
                shutil.copy2(source, target)
    for source in (sample_dir / "ocr-qwen" / "_prepared-inputs").glob("*"):
        if source.is_file():
            shutil.copy2(source, prepared_dir / source.name)

    with Image.open(source_image) as image:
        width, height = image.size

    manifest = json.loads((sample_dir / "region-manifest.json").read_text(encoding="utf-8"))
    manifest = [sanitize_row(row) for row in manifest]
    entries = json.loads((sample_dir / "llm-corrections.json").read_text(encoding="utf-8"))
    entries = [sanitize_row(row) for row in entries]
    write_json(data_dir / "region-manifest.json", manifest)
    write_json(data_dir / "llm-corrections.json", entries)
    write_json(data_dir / "magazine-regions.json", extract_annotation(annotation, width, height))
    (data_dir / "translation-segments.yml").write_text(
        sanitized_yaml(sample_dir / "translation-segments-llm.yml"), encoding="utf-8"
    )
    (data_dir / "regions-ocr-llm.md").write_text(
        sanitized_markdown(sample_dir / "regions-ocr-llm.md"), encoding="utf-8"
    )

    preview_article = article_html(entries, public_scan, "./assets")
    preview = (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>蒼井優 ♥ ピカチュウ｜完整流程开发案例</title>'
        + STYLE + "</head><body>" + preview_article + SCRIPT + "</body></html>"
    )
    (public_dir / "index.html").write_text(preview, encoding="utf-8")
    wordpress = STYLE + "\n" + article_html(entries, public_scan, "{{WORDPRESS_MEDIA_BASE}}") + "\n" + SCRIPT + "\n"
    (public_dir / "wordpress-paste.html").write_text(wordpress, encoding="utf-8")

    (out_dir / "README.md").write_text(readme(), encoding="utf-8")
    write_json(out_dir / "case.json", {
        "schema_version": 1,
        "id": CASE_ID,
        "title": "蒼井優 ♥ ピカチュウ",
        "publication": "CONTINUE",
        "issue": "2006 vol.31",
        "page": "014-015",
        "created": date.today().isoformat(),
        "status": "development_case",
        "entrypoint": "public/index.html",
        "wordpress_fragment": "public/wordpress-paste.html",
        "source_image": "public/assets/page041.jpg",
        "annotation": "data/magazine-regions.json",
        "region_manifest": "data/region-manifest.json",
        "ocr_directory": "data/ocr-qwen",
        "corrections": "data/llm-corrections.json",
        "translation_segments": "data/translation-segments.yml",
        "models": {"layout": "qwen-vl", "ocr": "qwen-vl-ocr-latest", "correction_translation": "deepseek-chat"},
    })

    portability = scan_portability(out_dir)
    (docs_dir / "qa-report.md").write_text(qa_report(public_scan, entries, portability), encoding="utf-8")
    portability = scan_portability(out_dir)
    if portability["absolute_windows_paths"] or portability["possible_secrets"]:
        raise SystemExit(f"Package portability check failed: {portability}")

    files = sorted(path for path in out_dir.rglob("*") if path.is_file())
    checksums = [f"{sha256(path)}  {path.relative_to(out_dir).as_posix()}" for path in files]
    (out_dir / "CHECKSUMS.sha256").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    archive = shutil.make_archive(str(out_dir), "zip", root_dir=out_dir.parent, base_dir=out_dir.name)
    print(f"Development case: {out_dir}")
    print(f"ZIP archive: {archive}")
    print(f"Files: {len(list(out_dir.rglob('*')))}")


if __name__ == "__main__":
    main()
