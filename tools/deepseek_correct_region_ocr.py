import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from ocr_regions_from_annotation import grouped_manifest, public_output_file, read_ocr_text, yaml_string


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def build_prompt(item: dict, raw_text: str, context: str) -> str:
    return f"""
你是日文杂志访谈 OCR 校对与中文翻译助手。
任务：根据上下文修正 OCR 识别错误，并翻译成自然中文。

规则：
1. 不要凭空补写原文没有的信息。
2. 只修正常见 OCR 错字、漏字、片假名大小字、浊音半浊音、标点和断行。
3. 如果无法确定，保留原样，并在 correction_note 说明疑点。
4. 人名、作品名、公司名要谨慎。Pokemon / ポケットモンスター 等专有名词可按上下文修正。
5. 输出必须是 JSON，不要 Markdown，不要解释 JSON 之外的内容。
6. 只处理“当前 OCR 原文”。邻近上下文只用于判断词义，绝对不能复制、续写或翻译到结果中。
7. 当前原文如果在词语中途截断，必须保留截断状态，不得从邻区补全。

区域信息：
- page: {item.get("page_name")}
- type: {item.get("type")}
- writing_direction: {item.get("writing_direction") or "auto"}
- speaker: {item.get("speaker")}
- note: {item.get("note") or ""}

邻近上下文：
{context or "无"}

OCR 原文：
{raw_text or "无"}

输出 JSON 格式：
{{
  "original_corrected": "校对后的日文原文",
  "translation": "中文翻译",
  "correction_note": "简短说明修正依据；如果没有明显修正则写：未发现明确 OCR 修正"
}}
""".strip()


def call_deepseek(prompt: str, model: str, api_key: str, base_url: str, temperature: float, retries: int) -> dict:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是谨慎的日文 OCR 校对员和中文译者。你必须输出严格 JSON。",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    last_error = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return json.loads(content)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(2 + attempt * 2)
    raise RuntimeError(f"DeepSeek request failed: {last_error}")


def clean_raw_text(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.strip())


def normalized_text(text: str) -> str:
    return re.sub(r"\s+", "", str(text or ""))


def suspicious_correction(raw_text: str, corrected_text: str, next_text: str = "") -> list[str]:
    """Detect correction results that escaped the current OCR region."""
    raw = normalized_text(raw_text)
    corrected = normalized_text(corrected_text)
    next_raw = normalized_text(next_text)
    warnings = []
    if len(raw) >= 80 and len(corrected) > max(len(raw) + 80, round(len(raw) * 1.28)):
        warnings.append(f"corrected_text_expanded:{len(raw)}->{len(corrected)}")
    next_probe = next_raw[:48]
    if len(next_probe) >= 32 and next_probe in corrected and next_probe not in raw:
        warnings.append("neighbor_context_copied")
    return warnings


def build_context(entries: list[dict], index: int) -> str:
    neighbors = []
    for offset in (-1, 1):
        other_index = index + offset
        if 0 <= other_index < len(entries):
            other = entries[other_index]
            raw = other.get("original_raw", "")
            if raw:
                neighbors.append(f"{other.get('speaker')}: {raw[:500]}")
    return "\n".join(neighbors)


def cache_key(item: dict) -> tuple[str, str, str]:
    return (
        str(item.get("page_name") or ""),
        str(item.get("region_id") or ""),
        str(item.get("original_raw") or ""),
    )


def load_entries(out_dir: Path, ocr_dir: Path) -> list[dict]:
    manifest = json.loads((out_dir / "region-manifest.json").read_text(encoding="utf-8"))
    entries = []
    for item in grouped_manifest(manifest):
        is_image = item.get("type") == "image"
        texts = [] if is_image else [read_ocr_text(ocr_dir, member["crop_name"]) for member in item["members"]]
        raw_text = clean_raw_text("\n".join(part for part in texts if part))
        entry = dict(item)
        entry["original_raw"] = raw_text
        entries.append(entry)
    return entries


def write_outputs(out_dir: Path, entries: list[dict]) -> None:
    corrections_path = out_dir / "llm-corrections.json"
    corrections_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = ["# Region OCR With DeepSeek Correction", ""]
    yaml_lines = ["translation_segments:"]
    for index, item in enumerate(entries, start=1):
        is_image = item.get("type") == "image"
        item_kind = "image" if is_image else "caption" if item.get("type") == "caption" else "text"
        raw = item.get("original_raw") or "待校对"
        corrected = item.get("original_corrected") or raw
        translation = item.get("translation") or "待翻译"
        note = item.get("correction_note") or ""
        public_image = public_output_file(out_dir, "figures", Path(item["crop"]).name) if is_image else ""

        md_lines.extend([
            f"## {index}. {item.get('speaker')}",
            "",
            f"- page: {item.get('page_name')}",
            f"- source_image: {item.get('source_image') or ''}",
            f"- type: {item.get('type')}",
            f"- kind: {item_kind}",
            f"- region_id: {item.get('region_id') or ''}",
            f"- order: {item.get('order') or index}",
        ])
        if item.get("group_id"):
            md_lines.append(f"- group_id: {item['group_id']}")
        if not is_image:
            md_lines.append(f"- writing_direction: {item.get('writing_direction') or 'auto'}")
        if item.get("image_ref"):
            md_lines.append(f"- caption_for: {item['image_ref']}")
        if public_image:
            md_lines.append(f"- image: {public_image}")
        md_lines.extend([
            "",
            f"![{item.get('speaker') or '杂志图片'}]({public_image})" if is_image else "### OCR Raw",
        ])
        if not is_image:
            md_lines.extend([
                "",
                raw,
                "",
                "### Corrected Original",
                "",
                corrected,
                "",
                "### Translation",
                "",
                translation,
                "",
            ])
        if note:
            md_lines.extend(["### Correction Note", "", note, ""])

        yaml_lines.append(f'  - speaker: "{yaml_string(item.get("speaker"))}"')
        yaml_lines.append(f'    kind: "{item_kind}"')
        yaml_lines.append(f"    scan_page: {item.get('page_index', 0)}")
        if item.get("page_name"):
            yaml_lines.append(f'    page_name: "{yaml_string(item.get("page_name"))}"')
        if item.get("source_image"):
            yaml_lines.append(f'    source_image: "{yaml_string(item.get("source_image"))}"')
        yaml_lines.append(f'    region_type: "{yaml_string(item.get("type"))}"')
        yaml_lines.append(f"    order: {item.get('order') or index}")
        if not is_image:
            yaml_lines.append(f'    writing_direction: "{yaml_string(item.get("writing_direction") or "auto")}"')
        if item.get("region_id"):
            yaml_lines.append(f'    region_id: "{yaml_string(item.get("region_id"))}"')
        if item.get("group_id"):
            yaml_lines.append(f'    group_id: "{yaml_string(item.get("group_id"))}"')
        if item.get("image_ref"):
            yaml_lines.append(f'    caption_for: "{yaml_string(item.get("image_ref"))}"')
        members = item.get("members") or [item]
        if len(members) > 1:
            yaml_lines.append("    scan_boxes:")
            for member in members:
                yaml_lines.append(f"      - [{', '.join(str(value) for value in member['box'])}]")
        else:
            yaml_lines.append(f"    scan_box: [{', '.join(str(value) for value in item.get('box', []))}]")
        if is_image:
            yaml_lines.append(f'    image: "{yaml_string(public_image)}"')
            yaml_lines.append(f'    alt: "{yaml_string(item.get("speaker") or "杂志图片")}"')
        else:
            yaml_lines.append("    original_raw: |-")
            for line in raw.splitlines():
                yaml_lines.append(f"      {line}")
            yaml_lines.append("    original: |-")
            for line in corrected.splitlines():
                yaml_lines.append(f"      {line}")
            yaml_lines.append("    translation: |-")
            for line in translation.splitlines():
                yaml_lines.append(f"      {line}")
        if note:
            yaml_lines.append(f'    comment: "{yaml_string(note)}"')

    (out_dir / "regions-ocr-llm.md").write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    (out_dir / "translation-segments-llm.yml").write_text("\n".join(yaml_lines).strip() + "\n", encoding="utf-8")
    print(f"DeepSeek corrections: {corrections_path}")
    print(f"LLM Markdown: {out_dir / 'regions-ocr-llm.md'}")
    print(f"LLM YAML: {out_dir / 'translation-segments-llm.yml'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Correct region OCR text with DeepSeek.")
    parser.add_argument("--out", required=True, help="Region OCR output folder.")
    parser.add_argument("--ocr-dir", required=True, help="PaddleOCR output folder for crops.")
    parser.add_argument("--model", default=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
    parser.add_argument("--base-url", default=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
    parser.add_argument("--api-key", default=os.getenv("DEEPSEEK_API_KEY", ""))
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--reuse-existing",
        action="store_true",
        help="Reuse unchanged entries from llm-corrections.json and only call the API for changed OCR text.",
    )
    args = parser.parse_args()

    if not args.api_key:
        raise SystemExit("Missing DEEPSEEK_API_KEY. Set it in PowerShell before running.")

    out_dir = Path(args.out).resolve()
    ocr_dir = Path(args.ocr_dir).resolve()
    entries = load_entries(out_dir, ocr_dir)
    if args.limit > 0:
        entries = entries[: args.limit]

    cached = {}
    corrections_path = out_dir / "llm-corrections.json"
    if args.reuse_existing and corrections_path.exists():
        try:
            previous = json.loads(corrections_path.read_text(encoding="utf-8"))
            cached = {cache_key(item): item for item in previous}
        except (OSError, json.JSONDecodeError):
            cached = {}

    for index, item in enumerate(entries):
        if item.get("type") == "image":
            item["original_corrected"] = ""
            item["translation"] = ""
            item["correction_note"] = ""
            continue
        raw_text = item.get("original_raw", "")
        if not raw_text:
            item["original_corrected"] = ""
            item["translation"] = ""
            item["correction_note"] = "该区域没有 OCR 文本。"
            continue
        previous = cached.get(cache_key(item))
        if previous and previous.get("translation"):
            item["original_corrected"] = previous.get("original_corrected", raw_text)
            item["translation"] = previous.get("translation", "")
            item["correction_note"] = previous.get("correction_note", "")
            item["reliability_warnings"] = previous.get("reliability_warnings", [])
            print(f"Reuse [{index + 1}/{len(entries)}]: {item.get('speaker')}")
            continue
        print(f"DeepSeek [{index + 1}/{len(entries)}]: {item.get('speaker')}")
        context = build_context(entries, index)
        result = call_deepseek(
            build_prompt(item, raw_text, context),
            args.model,
            args.api_key,
            args.base_url,
            args.temperature,
            args.retries,
        )
        next_text = entries[index + 1].get("original_raw", "") if index + 1 < len(entries) else ""
        warnings = suspicious_correction(raw_text, result.get("original_corrected", raw_text), next_text)
        if warnings:
            print(f"Retry current region only [{index + 1}/{len(entries)}]: {', '.join(warnings)}")
            result = call_deepseek(
                build_prompt(item, raw_text, "无；本次为边界保护重试，只允许当前区域内容。"),
                args.model,
                args.api_key,
                args.base_url,
                args.temperature,
                args.retries,
            )
            warnings = suspicious_correction(raw_text, result.get("original_corrected", raw_text), "")
        item["original_corrected"] = result.get("original_corrected", raw_text)
        item["translation"] = result.get("translation", "")
        item["correction_note"] = result.get("correction_note", "")
        item["reliability_warnings"] = warnings

    write_outputs(out_dir, entries)


if __name__ == "__main__":
    main()
