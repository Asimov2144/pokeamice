"""Translate Game Freak Director archive articles with the OpenAI API.

This is a comparison pipeline: it writes to a separate OpenAI translation
layer and never overwrites the DeepSeek or published zh-CN translations.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from gamefreak_translate_deepseek import (
    DEFAULT_GLOSSARY_CANDIDATES,
    build_prompt,
    clean_card_text,
    glossary_checks,
    glossary_context,
    glossary_matches,
    load_glossary,
    parse_json_response,
    source_articles,
    utc_now,
    validate_translation,
)


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION_DIR = ROOT / "archive" / "gamefreak-director" / "translations" / "zh-CN-openai"


def write_markdown(path: Path, metadata: dict[str, Any], body: str) -> None:
    import yaml

    frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).strip()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body.strip()}\n", encoding="utf-8")


def call_openai(
    prompt: str,
    api_key: str,
    base_url: str,
    model: str,
    temperature: float,
    retries: int,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是严谨但注重中文可读性的日中翻译编辑。输出必须是严格 JSON。",
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }
    # Some reasoning models reject an explicit temperature parameter; their
    # default sampling behavior is used instead.
    if not model.lower().startswith(("gpt-5", "o1", "o3", "o4")):
        payload["temperature"] = temperature
    endpoint = base_url.rstrip("/")
    if not endpoint.endswith("/chat/completions"):
        endpoint += "/chat/completions"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        content = ""
        try:
            with urllib.request.urlopen(request, timeout=240) as response:
                data = json.loads(response.read().decode("utf-8"))
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            result = parse_json_response(content)
            translation = result.get("translation_markdown") or result.get("translation")
            if not isinstance(translation, str) or not translation.strip():
                raise ValueError("OpenAI returned no translation_markdown")
            return {
                "translation_markdown": translation.strip(),
                "translation_title": result.get("translation_title") or "",
                "translation_summary": result.get("translation_summary") or "",
            }
        except urllib.error.HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8", errors="replace")[:1200]
            except Exception:
                detail = ""
            last_error = ValueError(f"HTTP {exc.code}: {detail or exc.reason}")
            if attempt < retries:
                time.sleep(2 + attempt * 2)
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            if isinstance(exc, json.JSONDecodeError):
                last_error = ValueError(f"{exc}; response_prefix={content[:160]!r}")
            else:
                last_error = exc
            if attempt < retries:
                time.sleep(2 + attempt * 2)
    raise RuntimeError(f"OpenAI request failed: {last_error}")


def make_metadata(
    number: int,
    source: dict[str, Any],
    model: str,
    warnings: list[str],
    glossary_path: Path,
    matches: list[dict[str, Any]],
    checks: list[dict[str, Any]],
    title: str,
    summary: str,
) -> dict[str, Any]:
    return {
        "article_id": f"masuda-{number:03d}",
        "number": number,
        "lang": "zh-CN",
        "source_language": "ja",
        "translation_status": "openai-machine-translated",
        "translator": f"OpenAI {model}",
        "provider": "openai",
        "reviewer": None,
        "translated_at": utc_now(),
        "source_date": source.get("date_display") or source.get("date"),
        "translation_warnings": warnings,
        "translation_title": title,
        "translation_summary": summary,
        "glossary_source": glossary_path.name,
        "glossary_match_count": len(matches),
        "glossary_missing_targets": [check["target"] for check in checks if check["status"] == "missing-target"],
        "glossary_checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a separate OpenAI comparison translation layer.")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--only", type=int, nargs="*")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4.1"))
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""))
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--glossary", default=os.getenv("GAMEFREAK_GLOSSARY_PATH", ""))
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.api_key and not args.dry_run:
        raise SystemExit("Missing OPENAI_API_KEY. Set it in PowerShell before running.")
    glossary_path = Path(args.glossary).expanduser() if args.glossary else next(
        (path for path in DEFAULT_GLOSSARY_CANDIDATES if path.exists()), None
    )
    if glossary_path is None or not glossary_path.exists():
        raise SystemExit("Glossary Master JSON was not found. Pass --glossary path/to/glossary-master.json.")
    glossary = load_glossary(glossary_path)
    print(f"Glossary: {glossary_path} ({len(glossary)} usable entries)")

    only = set(args.only or [])
    selected = [
        item for item in source_articles()
        if item[0] >= args.start and (not args.end or item[0] <= args.end) and (not only or item[0] in only)
    ]
    if args.limit > 0:
        selected = selected[: args.limit]
    print(f"Selected {len(selected)} article(s); output={TRANSLATION_DIR}")

    for index, (number, _path, source_metadata, source_body) in enumerate(selected, start=1):
        output = TRANSLATION_DIR / f"{number:03d}.md"
        if args.reuse_existing and output.exists():
            print(f"Reuse [{index}/{len(selected)}] {number:03d}")
            continue
        matches = glossary_matches(source_body, glossary)
        if args.dry_run:
            print(f"Would translate [{index}/{len(selected)}] {number:03d} (glossary matches: {len(matches)})")
            continue
        print(f"OpenAI [{index}/{len(selected)}] {number:03d}")
        result = call_openai(
            build_prompt(number, source_metadata, source_body, glossary_context(matches)),
            args.api_key,
            args.base_url,
            args.model,
            args.temperature,
            args.retries,
        )
        translation = result["translation_markdown"]
        title = clean_card_text(result.get("translation_title"), 8, 30) or f"【博客】{str(source_metadata.get('date', ''))[:4]}年第{number}回"
        summary = clean_card_text(result.get("translation_summary"), 30, 60)
        if not summary:
            summary = " ".join(translation.split())[:60]
        warnings = validate_translation(source_body, translation)
        checks = glossary_checks(matches, translation)
        missing = [check["target"] for check in checks if check["status"] == "missing-target"]
        if missing:
            warnings.append("missing_glossary_targets: " + ", ".join(missing[:12]))
        write_markdown(output, make_metadata(number, source_metadata, args.model, warnings, glossary_path, matches, checks, title, summary), translation)
        time.sleep(max(args.delay, 0))


if __name__ == "__main__":
    main()
