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
DEFAULT_GLOSSARY_CANDIDATES = (
    ROOT / "glossary-master.json",
    ROOT.parent / "glossary-master.json",
    Path("P:/WEBSITE/pokeamice/event/public/glossary-master.json"),
)
STUB_RE = re.compile(r"中文翻译待完成|translation_status:\s*missing")
MARKER_RE = re.compile(r"\{%\s*(?:image\b[^%]*|spacer\s*)%\}")
URL_RE = re.compile(r"https?://[^)\s]+")
JAPANESE_KANA_RE = re.compile(r"[ぁ-んァ-ン]")


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


def clean_card_text(text: Any, minimum: int, maximum: int) -> str:
    """Normalize model-generated card copy without allowing a Japanese-only label."""
    value = re.sub(r"\s+", " ", str(text or "")).strip().strip("「」『』\"'")
    if JAPANESE_KANA_RE.search(value):
        return ""
    if len(value) < minimum or len(value) > maximum:
        return ""
    return value


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


def load_glossary(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("entries") if isinstance(data, dict) else data
    if not isinstance(entries, list):
        raise ValueError(f"Glossary has no entries list: {path}")
    valid = []
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("target"):
            continue
        terms = [str(term).strip() for term in entry.get("terms", []) if str(term).strip()]
        if terms:
            valid.append({
                "category": entry.get("category", ""),
                "target": str(entry["target"]),
                "terms": terms,
                "source": entry.get("source", ""),
            })
    return valid


def glossary_matches(source: str, glossary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find glossary terms in source, avoiding short embedded katakana/kanji hits."""
    def kind(char: str) -> str:
        codepoint = ord(char)
        if "\u3040" <= char <= "\u309f":
            return "hiragana"
        if "\u30a0" <= char <= "\u30ff" or char in "ー・":
            return "katakana"
        if "\u3400" <= char <= "\u9fff":
            return "kanji"
        if char.isalnum() or codepoint > 0x7f and char.isalpha():
            return "latin"
        return "other"

    def standalone_hits(term: str) -> list[str]:
        if len(term) < 2:
            return []
        term_kinds = {kind(char) for char in term}
        hits = []
        start = source.find(term)
        while start >= 0:
            end = start + len(term)
            before = kind(source[start - 1]) if start else "other"
            after = kind(source[end]) if end < len(source) else "other"
            embedded = (
                (term_kinds == {"katakana"} and (before == "katakana" or after == "katakana"))
                or (term_kinds == {"kanji"} and (before == "kanji" or after == "kanji"))
                or (term_kinds == {"latin"} and (before == "latin" or after == "latin"))
                or (term_kinds == {"hiragana"} and len(term) < 4 and (before == "hiragana" or after == "hiragana"))
            )
            if not embedded:
                hits.append(term)
            start = source.find(term, start + 1)
        return hits

    all_candidates = []
    for entry in glossary:
        hits = sorted({term for term in entry["terms"] for _ in standalone_hits(term)}, key=len, reverse=True)
        if hits:
            all_candidates.append({**entry, "hits": hits})
    candidate_terms = [term for entry in all_candidates for term in entry["hits"]]
    matches = {}
    for entry in all_candidates:
        hits = [term for term in entry["hits"] if not any(
            term != other and term in other and len(other) > len(term) for other in candidate_terms
        )]
        if hits:
            key = (entry["target"], tuple(hits))
            matches[key] = {**entry, "hits": hits}
    return sorted(matches.values(), key=lambda item: (-max(map(len, item["hits"])), item["target"]))


def glossary_context(matches: list[dict[str, Any]], limit: int = 120) -> str:
    lines = []
    for entry in matches[:limit]:
        source_terms = "、".join(entry["hits"])
        # 分类仅用于内部审计，不注入提示词，避免模型把括号说明写进正文。
        lines.append(f"- {source_terms} → {entry['target']}")
    if len(matches) > limit:
        lines.append(f"- 其余 {len(matches) - limit} 条命中术语不展开；仍应优先遵循目标译名。")
    return "\n".join(lines) or "本篇原文没有命中术语表中的明确词条。"


def glossary_checks(matches: list[dict[str, Any]], translation: str) -> list[dict[str, Any]]:
    return [
        {
            "source_terms": entry["hits"],
            "target": entry["target"],
            "target_occurrences": translation.count(entry["target"]),
            "status": "present" if translation.count(entry["target"]) else "missing-target",
            "category": entry.get("category", ""),
            "source": entry.get("source", ""),
        }
        for entry in matches
    ]


def build_prompt(number: int, source_metadata: dict[str, Any], body: str, glossary: str) -> str:
    return f"""你是资深日中翻译与宝可梦史料编辑，正在整理 GAME FREAK 的「増田部長のめざめるパワー」博客。

请把下面第 {number} 回的日文原文翻译成自然、准确、亲切的简体中文，供中文宝可梦玩家进行阅读和人工校对。
这是一篇由增田顺一以第一人称写下的旧博客/工作日记，不是新闻稿、说明书或百科条目。译文要像作者在和读者聊天：保留随笔感、现场感、兴奋或自嘲等情绪，让中文读者读起来顺畅亲切，但不要擅自卖萌、网络化或添加原文没有的信息。
最后的 では チャオ！之类的结尾词也请按照信件的语气翻译成中文。

必须遵守：
1. 只翻译当前正文，不补写背景，不删去句子，不总结。
2. 保留原文的段落数量、空行、换行节奏和内容顺序；原文一行一行短句时，中文也保持相同的分行感。
3. 原文中的 Markdown 链接、URL、`{{% image ... %}}`、`{{% spacer %}}` 等标记必须原样保留，位置不能移动；不要翻译 URL 或标记内部内容。
4. 优先保留作者的第一人称和口语语气（如“我”“其实”“终于”“没想到”等）文中出现ますだ时也可以直接翻译成“我”；日文敬体不要机械翻成公文腔，按上下文译成自然的中文叙述。
5. 专有名词必须优先采用下方译名库中的目标译名；同一篇文章保持前后一致。译名库没有覆盖的词，不要臆造，可保留日文或采用通行译名。
6. 保留全角标点所表达的语气，但中文句末标点按中文习惯处理。
7. 不要在中文译文开头重复日文标题、日期、署名、原文导语或任何日文原文；这些内容会在网页后面单独展示。正文中也不要附上整段日文原文。
8. 另外生成一个用于外部卡片的中文标题和摘要。标题优先参考“【分类】+年代+作品/活动/话题+主题”（例如“【开发日记】2008年 宝可梦新作”），但不要机械套模板；请从正文提取真正主题，以自然、顺畅、读起来像中文标题为准，长度大约 10—20 字即可，必要时可略微超出。摘要约 30—60 字。标题和摘要都不得含日文假名。
9. 只输出严格 JSON：`{{"translation_markdown":"翻译后的 Markdown 正文","translation_title":"约10—20字、顺畅的中文标题","translation_summary":"30—60字中文摘要"}}`。不要输出 front matter、解释或代码围栏。

文章元数据：
- 日期：{source_metadata.get('date_display') or source_metadata.get('date') or ''}
- 原文分类：{', '.join(source_metadata.get('categories') or [])}
- 原文导语：{source_metadata.get('lead') or ''}

本篇命中的译名库（原词 → 统一中文译名）：
{glossary}
括号中的分类、来源或备注不属于译文内容；只有当括号本身就是官方译名的一部分时才保留。

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
) -> dict[str, Any]:
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
            return {
                "translation_markdown": clean_translation(translation),
                "translation_title": result.get("translation_title") or "",
                "translation_summary": result.get("translation_summary") or "",
            }
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
    first_content = next((line.strip() for line in translation.splitlines() if line.strip()), "")
    if JAPANESE_KANA_RE.search(first_content):
        warnings.append("japanese_text_at_translation_start")
    source_lines = [line for line in source.splitlines() if line.strip()]
    translated_lines = [line for line in translation.splitlines() if line.strip()]
    if source_lines and len(translated_lines) > max(len(source_lines) * 1.35, len(source_lines) + 10):
        warnings.append(f"line_count_expanded:{len(source_lines)}->{len(translated_lines)}")
    return warnings


def existing_translation(path: Path) -> tuple[dict[str, Any], str] | None:
    if not path.exists():
        return None
    metadata, body = read_markdown(path)
    if metadata.get("translation_status") in {"translated", "machine-translated", "reviewed", "proofread"} and not STUB_RE.search(body):
        return metadata, body
    return None


def make_translation_metadata(
    number: int,
    source: dict[str, Any],
    model: str,
    warnings: list[str],
    glossary_path: Path,
    glossary_matches_found: list[dict[str, Any]],
    glossary_term_checks: list[dict[str, Any]],
    translation_title: str,
    translation_summary: str,
) -> dict[str, Any]:
    missing_targets = [check["target"] for check in glossary_term_checks if check["status"] == "missing-target"]
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
        "translation_title": translation_title,
        "translation_summary": translation_summary,
        "glossary_source": glossary_path.name,
        "glossary_match_count": len(glossary_matches_found),
        "glossary_missing_targets": missing_targets,
        "glossary_checks": glossary_term_checks,
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
    parser.add_argument("--glossary", default=os.getenv("GAMEFREAK_GLOSSARY_PATH", ""), help="Glossary Master JSON path.")
    parser.add_argument("--reuse-existing", action="store_true", help="Skip already translated files.")
    parser.add_argument("--dry-run", action="store_true", help="Print the selected articles without calling the API.")
    args = parser.parse_args()

    if not args.api_key and not args.dry_run:
        raise SystemExit("Missing DEEPSEEK_API_KEY. Set it in PowerShell before running.")

    glossary_path = Path(args.glossary).expanduser() if args.glossary else next(
        (path for path in DEFAULT_GLOSSARY_CANDIDATES if path.exists()), None
    )
    if glossary_path is None or not glossary_path.exists():
        raise SystemExit("Glossary Master JSON was not found. Pass --glossary path/to/glossary-master.json.")
    glossary = load_glossary(glossary_path)
    print(f"Glossary: {glossary_path} ({len(glossary)} usable entries)")

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
            matches = glossary_matches(source_body, glossary)
            print(f"Would translate [{index}/{len(selected)}] {number:03d} (glossary matches: {len(matches)})")
            continue
        print(f"DeepSeek [{index}/{len(selected)}] {number:03d}")
        matches = glossary_matches(source_body, glossary)
        result = call_deepseek(
            build_prompt(number, source_metadata, source_body, glossary_context(matches)),
            args.api_key,
            args.base_url,
            args.model,
            args.temperature,
            args.retries,
        )
        translation = result["translation_markdown"]
        fallback_title = f"【博客】{source_metadata.get('date', '')[:4]}年第{number}回"
        # 标题以顺畅和主题准确为先，允许模型根据文章内容略微调整长度。
        translation_title = clean_card_text(result.get("translation_title"), 8, 30) or fallback_title
        translation_summary = clean_card_text(result.get("translation_summary"), 30, 60)
        if not translation_summary:
            first_paragraph = next((part.strip() for part in re.split(r"\n\s*\n", translation) if part.strip()), "")
            translation_summary = re.sub(r"[*_`#]", "", first_paragraph)
            translation_summary = re.sub(r"\s+", " ", translation_summary).strip()[:60]
        warnings = validate_translation(source_body, translation)
        term_checks = glossary_checks(matches, translation)
        missing_targets = [check["target"] for check in term_checks if check["status"] == "missing-target"]
        if missing_targets:
            warnings.append("missing_glossary_targets: " + ", ".join(missing_targets[:12]))
        if warnings:
            print(f"  warning: {', '.join(warnings)}")
        write_yaml_frontmatter(
            make_translation_metadata(
                number,
                source_metadata,
                args.model,
                warnings,
                glossary_path,
                matches,
                term_checks,
                translation_title,
                translation_summary,
            ),
            translation,
            output,
        )
        time.sleep(max(args.delay, 0))


if __name__ == "__main__":
    main()
