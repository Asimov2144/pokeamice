"""Proofread completed Game Freak Japanese->Chinese translations with DeepSeek.

This command writes a separate review layer and never overwrites the source
translation.  A reviewer can compare the original translation and the
proofread result before publishing it to the Jekyll article.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "archive" / "gamefreak-director" / "content"
TRANSLATION_DIR = ROOT / "archive" / "gamefreak-director" / "translations" / "zh-CN"
REVIEW_DIR = ROOT / "archive" / "gamefreak-director" / "translations" / "zh-CN-proofread"
DEFAULT_GLOSSARY_CANDIDATES = (
    ROOT / "glossary-master.json",
    ROOT.parent / "glossary-master.json",
    Path("P:/WEBSITE/pokeamice/event/public/glossary-master.json"),
)
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
    return yaml.safe_load(parts[1]) or {}, parts[2].strip()


def write_markdown(path: Path, metadata: dict[str, Any], body: str) -> None:
    frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).strip()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}\n---\n\n{body.strip()}\n", encoding="utf-8")


def marker_signature(text: str) -> list[str]:
    return MARKER_RE.findall(text)


def url_signature(text: str) -> list[str]:
    return URL_RE.findall(text)


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
            valid.append({"category": entry.get("category", ""), "target": str(entry["target"]), "terms": terms, "source": entry.get("source", "")})
    return valid


def glossary_matches(source: str, glossary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find source terms in the article, preferring terms of two characters or more."""
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
    matches = {}
    for entry in glossary:
        hits = sorted({term for term in entry["terms"] for _ in standalone_hits(term)}, key=len, reverse=True)
        if hits:
            all_candidates.append({**entry, "hits": hits})
    candidate_terms = [term for entry in all_candidates for term in entry["hits"]]
    for entry in all_candidates:
        hits = [term for term in entry["hits"] if not any(term != other and term in other and len(other) > len(term) for other in candidate_terms)]
        if hits:
            key = (entry["target"], tuple(hits))
            matches[key] = {**entry, "hits": hits}
    return sorted(matches.values(), key=lambda item: (-max(map(len, item["hits"])), item["target"]))


def glossary_context(matches: list[dict[str, Any]], limit: int = 120) -> str:
    lines = []
    for entry in matches[:limit]:
        source_terms = "、".join(entry["hits"])
        category = f"（{entry['category']}）" if entry.get("category") else ""
        lines.append(f"- {source_terms} → {entry['target']}{category}")
    if len(matches) > limit:
        lines.append(f"- 其余 {len(matches) - limit} 条命中术语不展开；仍应优先遵循目标译名。")
    return "\n".join(lines) or "本篇原文没有命中术语表中的明确词条。"


def glossary_checks(matches: list[dict[str, Any]], proofread: str) -> list[dict[str, Any]]:
    checks = []
    for entry in matches:
        target = entry["target"]
        target_hits = proofread.count(target)
        checks.append({
            "source_terms": entry["hits"],
            "target": target,
            "target_occurrences": target_hits,
            "status": "present" if target_hits else "missing-target",
            "category": entry.get("category", ""),
            "source": entry.get("source", ""),
        })
    return checks


def clean_body(text: str) -> str:
    candidate = (text or "").strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:markdown|md)?\s*", "", candidate, flags=re.I)
        candidate = re.sub(r"\s*```$", "", candidate)
    if candidate.startswith("---"):
        parts = candidate.split("---", 2)
        if len(parts) == 3:
            candidate = parts[2].strip()
    return candidate


def parse_json_response(content: str) -> dict[str, Any]:
    candidate = (content or "").strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*", "", candidate, flags=re.I)
        candidate = re.sub(r"\s*```$", "", candidate)
    if "{" in candidate and not candidate.startswith("{"):
        candidate = candidate[candidate.find("{") : candidate.rfind("}") + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return json.loads(candidate, strict=False)


def build_prompt(number: int, source: str, translation: str, glossary: str) -> str:
    return f"""你是负责游戏史料的资深日中译文校对编辑。

请对照第 {number} 回的日文原文和现有中文译文，进行谨慎的最终校对。

校对规则：
1. 只修正误译、漏译、错译、不自然但影响含义的表达、专有名词和明显标点问题；已经准确的句子不要为了换风格而改写。
2. 不增加原文没有的信息，不删减原文信息，不总结，不添加译者说明。
3. 保留中文译文现有的段落数量、空行、换行节奏和顺序。
4. 原文和译文中的 Markdown 链接、URL、`{{% image ... %}}`、`{{% spacer %}}` 等标记必须原样保留，位置不能改变。
5. 术语表中的目标译名是优先译法；若原文命中术语，尽量在对应中文位置使用目标译名，不要擅自创造近义译名。若上下文确实不适用，在 issues 中说明。
6. 专有名词优先使用官方中文或通行译名；不确定时保持原译并在 issues 中说明，不要臆造。
7. 输出严格 JSON：`{{"proofread_markdown":"...","issues":["..."],"confidence":"high|medium|low"}}`。
8. `proofread_markdown` 只放完整中文译文正文，不要 front matter、解释或代码围栏。若没有需要修改，原样返回现有中文译文，issues 返回空数组。

日文原文：
{source}

现有中文译文：
{translation}

本篇命中的 Glossary Master 术语（原词 → 统一中文译名）：
{glossary}
""".strip()


def call_deepseek(prompt: str, api_key: str, base_url: str, model: str, retries: int) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是严谨的日中译文校对编辑，必须输出严格 JSON。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.05,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        content = ""
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                data = json.loads(response.read().decode("utf-8"))
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return parse_json_response(content)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            if isinstance(exc, json.JSONDecodeError):
                last_error = ValueError(f"{exc}; response_prefix={content[:160]!r}")
            else:
                last_error = exc
            if attempt < retries:
                time.sleep(2 + attempt * 2)
    raise RuntimeError(f"DeepSeek request failed: {last_error}")


def validate(source: str, original: str, proofread: str) -> list[str]:
    warnings = []
    if marker_signature(original) != marker_signature(proofread):
        warnings.append("marker_signature_changed")
    if url_signature(original) != url_signature(proofread):
        warnings.append("url_signature_changed")
    if not proofread.strip():
        warnings.append("empty_proofread")
    source_lines = [line for line in source.splitlines() if line.strip()]
    proofread_lines = [line for line in proofread.splitlines() if line.strip()]
    if source_lines and len(proofread_lines) > max(len(source_lines) * 1.35, len(source_lines) + 10):
        warnings.append(f"line_count_expanded:{len(source_lines)}->{len(proofread_lines)}")
    return warnings


def main() -> None:
    parser = argparse.ArgumentParser(description="Proofread Game Freak Chinese translations with DeepSeek.")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--only", type=int, nargs="*")
    parser.add_argument("--model", default=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
    parser.add_argument("--base-url", default=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
    parser.add_argument("--api-key", default=os.getenv("DEEPSEEK_API_KEY", ""))
    parser.add_argument("--glossary", default=os.getenv("GAMEFREAK_GLOSSARY_PATH", ""), help="Glossary Master JSON path.")
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.api_key and not args.dry_run:
        raise SystemExit("Missing DEEPSEEK_API_KEY. Set it in PowerShell before running.")

    glossary_path = Path(args.glossary).expanduser() if args.glossary else next((path for path in DEFAULT_GLOSSARY_CANDIDATES if path.exists()), None)
    if glossary_path is None or not glossary_path.exists():
        raise SystemExit("Glossary Master JSON was not found. Pass --glossary path/to/glossary-master.json.")
    glossary = load_glossary(glossary_path)
    print(f"Glossary: {glossary_path} ({len(glossary)} usable entries)")

    only = set(args.only or [])
    selected = []
    for source_path in sorted(CONTENT_DIR.glob("*/ja.md")):
        source_metadata, source_body = read_markdown(source_path)
        number = int(source_metadata.get("number") or source_path.parent.name)
        if number < args.start or (args.end and number > args.end) or (only and number not in only):
            continue
        translation_path = TRANSLATION_DIR / f"{number:03d}.md"
        if not translation_path.exists():
            print(f"Skip {number:03d}: translation file is missing")
            continue
        translation_metadata, translation_body = read_markdown(translation_path)
        selected.append((number, source_body, translation_metadata, translation_body))
    if args.limit > 0:
        selected = selected[: args.limit]
    print(f"Selected {len(selected)} article(s); output={REVIEW_DIR}")

    for index, (number, source_body, translation_metadata, translation_body) in enumerate(selected, start=1):
        matches = glossary_matches(source_body, glossary)
        output = REVIEW_DIR / f"{number:03d}.md"
        if args.reuse_existing and output.exists():
            print(f"Reuse [{index}/{len(selected)}] {number:03d}")
            continue
        if args.dry_run:
            print(f"Would proofread [{index}/{len(selected)}] {number:03d} (glossary matches: {len(matches)})")
            continue
        print(f"DeepSeek proofread [{index}/{len(selected)}] {number:03d}")
        result = call_deepseek(
            build_prompt(number, source_body, translation_body, glossary_context(matches)),
            args.api_key,
            args.base_url,
            args.model,
            args.retries,
        )
        proofread_body = clean_body(result.get("proofread_markdown") or translation_body)
        model_warnings = result.get("issues") if isinstance(result.get("issues"), list) else []
        warnings = validate(source_body, translation_body, proofread_body)
        term_checks = glossary_checks(matches, proofread_body)
        missing_targets = [check["target"] for check in term_checks if check["status"] == "missing-target"]
        all_issues = [str(issue) for issue in model_warnings] + warnings
        if missing_targets:
            all_issues.append("missing_glossary_targets: " + ", ".join(missing_targets[:12]))
        output_metadata = {
            "article_id": f"masuda-{number:03d}",
            "number": number,
            "lang": "zh-CN",
            "source_language": "ja",
            "proofread_status": "machine-proofread",
            "source_translation": f"../zh-CN/{number:03d}.md",
            "proofreader": f"DeepSeek {args.model}",
            "proofread_at": utc_now(),
            "confidence": str(result.get("confidence") or "medium"),
            "issues": all_issues,
            "glossary_source": glossary_path.name,
            "glossary_match_count": len(matches),
            "glossary_missing_targets": missing_targets,
            "glossary_checks": term_checks,
        }
        write_markdown(output, output_metadata, proofread_body)
        if warnings:
            print(f"  validation warning: {', '.join(warnings)}")
        print(f"  model issues: {len(model_warnings)}")
        time.sleep(max(args.delay, 0))


if __name__ == "__main__":
    main()
