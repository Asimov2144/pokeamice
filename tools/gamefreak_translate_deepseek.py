"""Translate the Game Freak Director archive locally with the DeepSeek API.

The source layer is never modified.  Each translated article is written to
archive/gamefreak-director/translations/zh-CN/NNN.md and can be reviewed before
it is copied into the public Jekyll post.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - gives a useful CLI error
    raise SystemExit("PyYAML is required; run .venv-ocr/Scripts/python.exe -m pip install -r tools/requirements.txt") from exc


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "archive" / "gamefreak-director" / "content"
TRANSLATION_DIR = ROOT / "archive" / "gamefreak-director" / "translations" / "zh-CN"
STUB_RE = re.compile(r"中文翻译待完成|translation_status:\s*missing")
MARKER_RE = re.compile(r"\{%\s*(?:image\b[^%]*|spacer\s*)%\}")
URL_RE = re.compile(r"https?://[^)\s]+")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_markdown(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text.strip()
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid front matter: {path}")
    metadata = yaml.safe_load(parts[1]) or {}
    return metadata, parts[2].strip()


def write_yaml_frontmatter(metadata: dict[str, Any], body: str, path: Path) -> None:
    frontmatter = yaml.safe_dump(
        metadata,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    ).strip()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body.strip()}\n", encoding="utf-8")


def source_articles() -> list[tuple[int, Path, dict[str, Any], str]]:
    articles = []
    for path in sorted(CONTENT_DIR.glob("*/ja.md")):
        metadata, body = read_markdown(path)
        number = int(metadata.get("number") or path.parent.name)
        articles.append((number, path, metadata, body))
    return sorted(articles, key=lambda item: item[0])


def marker_signature(text: str) -> list[str]:
    return MARKER_RE.findall(text)


def url_signature(text: str) -> list[str]:
    return URL_RE.findall(text)


def clean_translation(text: str) -> str:
    text = text.strip()
    if text.startswith("```") and text.endswith("```"):
        text = re.sub(r"^```(?:markdown|md)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```$", "", text)
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            text = parts[2].strip()
    return text


def parse_json_response(content: str) -> dict[str, Any]:
    """Accept strict JSON and the occasional literal-newline JSON string."""
    candidate = content.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*", "", candidate, flags=re.I)
        candidate = re.sub(r"\s*```$", "", candidate)
    if "{" in candidate and not candidate.startswith("{"):
        candidate = candidate[candidate.find("{") : candidate.rfind("}") + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # Some compatible endpoints emit newlines directly inside the JSON
        # string despite response_format=json_object.  Python's non-strict
        # decoder can safely read that response without changing the text.
        return json.loads(candidate, strict=False)


def build_prompt(number: int, source_metadata: dict[str, Any], body: str) -> str:
    return f"""你是资深日中翻译与游戏史料编辑，正在整理 GAME FREAK 的「増田部長のめざめるパワー」博客。

请把下面第 {number} 回的日文原文翻译成自然、准确、克制的简体中文，供中文读者阅读和人工校对。

必须遵守：
1. 只翻译当前正文，不补写背景，不删去句子，不总结。
2. 保留原文的段落数量、空行、换行节奏和内容顺序；原文一行一行短句时，中文也保持相同的分行感。
3. 原文中的 Markdown 链接、URL、`{{% image ... %}}`、`{{% spacer %}}` 等标记必须原样保留，位置不能移动；不要翻译 URL 或标记内部内容。
4. 专有名词统一使用官方中文或通行译名；不确定时宁可保留日文并在译文中保持准确，不要臆造。
5. 保留全角标点所表达的语气，但中文句末标点按中文习惯处理。
6. 只输出严格 JSON：`{{"translation_markdown":"翻译后的 Markdown 正文"}}`。不要输出 front matter、解释或代码围栏；正文放在 JSON 的 `translation_markdown` 字段中。

文章元数据：
- 日期：{source_metadata.get('date_display') or source_metadata.get('date') or ''}
- 原文分类：{', '.join(source_metadata.get('categories') or [])}
- 原文导语：{source_metadata.get('lead') or ''}

日文原文：
{body}
""".strip()


def call_deepseek(
    prompt: str,
    api_key: str,
    base_url: str,
    model: str,
    temperature: float,
    retries: int,
) -> str:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是严谨的日中翻译编辑。输出必须是严格 JSON。",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        content = ""
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                data = json.loads(response.read().decode("utf-8"))
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            result = parse_json_response(content)
            translation = result.get("translation_markdown") or result.get("translation")
            if not isinstance(translation, str) or not translation.strip():
                raise ValueError("DeepSeek returned no translation_markdown")
            return clean_translation(translation)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            if isinstance(exc, json.JSONDecodeError):
                last_error = ValueError(f"{exc}; response_prefix={content[:160]!r}")
            else:
                last_error = exc
            if attempt < retries:
                time.sleep(2 + attempt * 2)
    raise RuntimeError(f"DeepSeek request failed: {last_error}")


def validate_translation(source: str, translation: str) -> list[str]:
    warnings = []
    if not translation.strip():
        warnings.append("empty_translation")
    if marker_signature(source) != marker_signature(translation):
        warnings.append("marker_signature_changed")
    if url_signature(source) != url_signature(translation):
        warnings.append("url_signature_changed")
    if "```" in translation:
        warnings.append("code_fence_added")
    source_lines = [line for line in source.splitlines() if line.strip()]
    translated_lines = [line for line in translation.splitlines() if line.strip()]
    if source_lines and len(translated_lines) > max(len(source_lines) * 1.35, len(source_lines) + 10):
        warnings.append(f"line_count_expanded:{len(source_lines)}->{len(translated_lines)}")
    return warnings


def existing_translation(path: Path) -> tuple[dict[str, Any], str] | None:
    if not path.exists():
        return None
    metadata, body = read_markdown(path)
    if metadata.get("translation_status") in {"translated", "machine-translated", "reviewed"} and not STUB_RE.search(body):
        return metadata, body
    return None


def make_translation_metadata(number: int, source: dict[str, Any], model: str, warnings: list[str]) -> dict[str, Any]:
    return {
        "article_id": f"masuda-{number:03d}",
        "number": number,
        "lang": "zh-CN",
        "source_language": "ja",
        "translation_status": "machine-translated",
        "translator": f"DeepSeek {model}",
        "reviewer": None,
        "translated_at": utc_now(),
        "source_date": source.get("date_display") or source.get("date"),
        "translation_warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Translate Game Freak Director archive articles with DeepSeek.")
    parser.add_argument("--start", type=int, default=1, help="First article number (inclusive).")
    parser.add_argument("--end", type=int, default=0, help="Last article number (inclusive); 0 means no upper bound.")
    parser.add_argument("--limit", type=int, default=0, help="Translate at most this many selected articles.")
    parser.add_argument("--only", type=int, nargs="*", help="Translate only these article numbers.")
    parser.add_argument("--model", default=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
    parser.add_argument("--base-url", default=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
    parser.add_argument("--api-key", default=os.getenv("DEEPSEEK_API_KEY", ""))
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--delay", type=float, default=0.5, help="Seconds between successful API calls.")
    parser.add_argument("--reuse-existing", action="store_true", help="Skip already translated files.")
    parser.add_argument("--dry-run", action="store_true", help="Print the selected articles without calling the API.")
    args = parser.parse_args()

    if not args.api_key and not args.dry_run:
        raise SystemExit("Missing DEEPSEEK_API_KEY. Set it in PowerShell before running.")

    selected = []
    only = set(args.only or [])
    for number, path, metadata, body in source_articles():
        if number < args.start or (args.end and number > args.end):
            continue
        if only and number not in only:
            continue
        selected.append((number, path, metadata, body))
    if args.limit > 0:
        selected = selected[: args.limit]
    print(f"Selected {len(selected)} article(s); output={TRANSLATION_DIR}")

    for index, (number, _path, source_metadata, source_body) in enumerate(selected, start=1):
        output = TRANSLATION_DIR / f"{number:03d}.md"
        if args.reuse_existing and existing_translation(output):
            print(f"Reuse [{index}/{len(selected)}] {number:03d}")
            continue
        if args.dry_run:
            print(f"Would translate [{index}/{len(selected)}] {number:03d}")
            continue
        print(f"DeepSeek [{index}/{len(selected)}] {number:03d}")
        translation = call_deepseek(
            build_prompt(number, source_metadata, source_body),
            args.api_key,
            args.base_url,
            args.model,
            args.temperature,
            args.retries,
        )
        warnings = validate_translation(source_body, translation)
        if warnings:
            print(f"  warning: {', '.join(warnings)}")
        write_yaml_frontmatter(make_translation_metadata(number, source_metadata, args.model, warnings), translation, output)
        time.sleep(max(args.delay, 0))


if __name__ == "__main__":
    main()
