"""Normalize recurring GAME FREAK Staff Blog names across Chinese translations.

The archive keeps the original Japanese nickname visible and adds the archive's
Chinese editorial rendering only at the first visible occurrence in each
article, for example ``カニ子（蟹子）``. Later occurrences remain ``カニ子``.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "archive" / "gamefreak-staff" / "staff-names.yml"
DEFAULT_CONTENT = ROOT / "archive" / "gamefreak-staff" / "content"
DEFAULT_TRANSLATIONS = ROOT / "archive" / "gamefreak-staff" / "translations" / "zh-CN"
DEFAULT_REPORT = ROOT / "archive" / "gamefreak-staff" / "reports" / "name-consistency.yml"

# These regions are structural rather than reader-visible prose. Markdown link
# labels stay editable, while their destinations are protected.
PROTECTED_RE = re.compile(
    r"(\{%.*?%\}|\{\{.*?\}\}|`[^`]*`|\]\([^\n)]*\)|<[^>]+>)",
    re.DOTALL,
)


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
    front = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=1000).strip()
    path.write_text(f"---\n{front}\n---\n\n{body.strip()}\n", encoding="utf-8")


def load_policy(path: Path = DEFAULT_POLICY) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw_names = data.get("names") or []
    names: list[dict[str, Any]] = []
    for raw in raw_names:
        source_terms = [str(value).strip() for value in raw.get("source_terms", []) if str(value).strip()]
        target = str(raw.get("target") or "").strip()
        if not source_terms or not target:
            continue
        variants = [str(value).strip() for value in raw.get("variants", []) if str(value).strip()]
        names.append(
            {
                "source_terms": source_terms,
                "source": source_terms[0],
                "target": target,
                "variants": list(dict.fromkeys(source_terms + variants)),
                "editorial_variants": variants,
                "exclude_articles": {int(value) for value in raw.get("exclude_articles", [])},
                "exclude_source_prefixes": [str(value) for value in raw.get("exclude_source_prefixes", [])],
                "exclude_source_suffixes": [str(value) for value in raw.get("exclude_source_suffixes", [])],
                "exclude_variant_suffixes": [str(value) for value in raw.get("exclude_variant_suffixes", [])],
            }
        )
    return names


def visible_segments(text: str) -> list[str]:
    return [part for index, part in enumerate(PROTECTED_RE.split(text)) if index % 2 == 0]


def visible_text(text: str) -> str:
    return "".join(visible_segments(text))


def _blocked_suffix(text: str, end: int, suffixes: list[str]) -> bool:
    return any(text.startswith(suffix, end) for suffix in suffixes)


def _char_kind(char: str) -> str:
    if not char:
        return "none"
    if "\u30a0" <= char <= "\u30ff" or char == "ー":
        return "katakana"
    if "\u3040" <= char <= "\u309f":
        return "hiragana"
    if char.isascii() and char.isalnum():
        return "latin"
    return "other"


def _valid_occurrence(
    text: str,
    start: int,
    end: int,
    term: str,
    suffixes: list[str],
    prefixes: list[str] | None = None,
) -> bool:
    if _blocked_suffix(text, end, suffixes):
        return False
    if any(text[:start].endswith(prefix) for prefix in prefixes or []):
        return False
    kinds = {_char_kind(char) for char in term}
    before = _char_kind(text[start - 1]) if start else "none"
    after = _char_kind(text[end]) if end < len(text) else "none"
    if kinds <= {"katakana"} and (before == "katakana" or after == "katakana"):
        return False
    if kinds <= {"latin"} and (before == "latin" or after == "latin"):
        return False
    return True


def _find_valid(
    text: str,
    term: str,
    suffixes: list[str],
    start_at: int = 0,
    prefixes: list[str] | None = None,
) -> int:
    start = text.find(term, start_at)
    while start >= 0:
        end = start + len(term)
        if _valid_occurrence(text, start, end, term, suffixes, prefixes):
            return start
        start = text.find(term, start + 1)
    return -1


def source_mentions(source_body: str, entry: dict[str, Any]) -> bool:
    text = visible_text(source_body)
    for term in sorted(entry["source_terms"], key=len, reverse=True):
        if _find_valid(
            text,
            term,
            entry["exclude_source_suffixes"],
            prefixes=entry["exclude_source_prefixes"],
        ) >= 0:
            return True
    return False


def name_context(entries: list[dict[str, Any]]) -> str:
    lines = [
        "人物昵称采用‘保留日文名，首次出现补充中文编辑译名’的格式；",
        "同一人物在同一篇正文中只有第一次写作 日文名（中文译名），后续只写日文名。",
    ]
    lines.extend(f"- {'／'.join(entry['source_terms'])} → {entry['source']}（{entry['target']}）" for entry in entries)
    return "\n".join(lines)


def applicable_names(
    source_body: str,
    entries: list[dict[str, Any]],
    article_id: int | None = None,
) -> list[dict[str, Any]]:
    return [
        entry
        for entry in entries
        if article_id not in entry["exclude_articles"] and source_mentions(source_body, entry)
    ]


def _replace_variants(text: str, entry: dict[str, Any]) -> str:
    source = entry["source"]
    target = entry["target"]
    variants = sorted(set(entry["variants"]), key=len, reverse=True)
    alternatives = "|".join(re.escape(value) for value in variants)
    if not alternatives:
        return text

    # Collapse an existing annotation first so the operation is idempotent.
    annotation_re = re.compile(rf"(?:{alternatives})\s*[（(]\s*{re.escape(target)}\s*[）)]")
    text = annotation_re.sub(source, text)
    variant_re = re.compile(alternatives)

    def replace(match: re.Match[str]) -> str:
        value = match.group(0)
        suffixes = entry["exclude_source_suffixes"] if value in entry["source_terms"] else entry["exclude_variant_suffixes"]
        prefixes = entry["exclude_source_prefixes"] if value in entry["source_terms"] else []
        if not _valid_occurrence(text, match.start(), match.end(), value, suffixes, prefixes):
            return value
        return source

    return variant_re.sub(replace, text)


def normalize_plain(text: str, entries: list[dict[str, Any]]) -> str:
    for entry in entries:
        text = _replace_variants(text, entry)
    return text


def normalize_card_text(text: str, entries: list[dict[str, Any]]) -> str:
    """Keep search titles and summaries Chinese-only while unifying names."""
    for entry in entries:
        variants = sorted(set(entry["variants"]), key=len, reverse=True)
        if not variants:
            continue
        alternatives = "|".join(re.escape(value) for value in variants)
        variant_re = re.compile(alternatives)

        def replace(match: re.Match[str]) -> str:
            value = match.group(0)
            suffixes = entry["exclude_source_suffixes"] if value in entry["source_terms"] else entry["exclude_variant_suffixes"]
            prefixes = entry["exclude_source_prefixes"] if value in entry["source_terms"] else []
            if not _valid_occurrence(text, match.start(), match.end(), value, suffixes, prefixes):
                return value
            return entry["target"]

        text = variant_re.sub(replace, text)
    return text


def normalize_body(
    source_body: str,
    translation_body: str,
    entries: list[dict[str, Any]],
    article_id: int | None = None,
) -> tuple[str, list[dict[str, str]]]:
    applicable = applicable_names(source_body, entries, article_id)
    parts = PROTECTED_RE.split(translation_body)
    # Remove annotations from an earlier run before recalculating applicability.
    # This also repairs annotations accidentally inserted inside longer names.
    known_annotation_values = sorted(
        {value for entry in entries for value in (entry["source"], entry["target"])},
        key=len,
        reverse=True,
    )
    annotation_value_re = "|".join(re.escape(value) for value in known_annotation_values)
    for entry in entries:
        for source_term in sorted(entry["source_terms"], key=len, reverse=True):
            chained_annotation_re = re.compile(
                rf"{re.escape(source_term)}(?:\s*[（(]\s*(?:{annotation_value_re})\s*[）)])+"
            )
            for index in range(0, len(parts), 2):
                parts[index] = chained_annotation_re.sub(source_term, parts[index])
    for entry in entries:
        endings = "|".join(re.escape(value) for value in {entry["target"], entry["source"]})
        for source_term in sorted(entry["source_terms"], key=len, reverse=True):
            annotation_re = re.compile(rf"{re.escape(source_term)}\s*[（(]\s*(?:{endings})\s*[）)]")
            for index in range(0, len(parts), 2):
                parts[index] = annotation_re.sub(source_term, parts[index])
    for entry in applicable:
        for index in range(0, len(parts), 2):
            parts[index] = _replace_variants(parts[index], entry)

        annotation = f"{entry['source']}（{entry['target']}）"
        annotated = False
        for index in range(0, len(parts), 2):
            if annotated:
                break
            segment = parts[index]
            start = _find_valid(
                segment,
                entry["source"],
                entry["exclude_source_suffixes"],
                prefixes=entry["exclude_source_prefixes"],
            )
            if start >= 0:
                end = start + len(entry["source"])
                parts[index] = segment[:start] + annotation + segment[end:]
                annotated = True

    annotations = [{"source": entry["source"], "target": entry["target"]} for entry in applicable]
    return "".join(parts).strip(), annotations


def audit_body(
    source_body: str,
    translation_body: str,
    entries: list[dict[str, Any]],
    article_id: int | None = None,
) -> list[dict[str, Any]]:
    prose = visible_text(translation_body)
    issues: list[dict[str, Any]] = []
    for entry in applicable_names(source_body, entries, article_id):
        annotation = f"{entry['source']}（{entry['target']}）"
        annotation_count = prose.count(annotation)
        source_count = prose.count(entry["source"])
        prose_without_annotation = prose.replace(annotation, entry["source"])
        remaining_variants = sorted(value for value in set(entry["editorial_variants"]) if value in prose_without_annotation)
        if source_count == 0:
            issues.append({"name": entry["source"], "issue": "missing-name-in-translation"})
        elif annotation_count != 1:
            issues.append(
                {
                    "name": entry["source"],
                    "issue": "annotation-count",
                    "expected": 1,
                    "actual": annotation_count,
                }
            )
        if remaining_variants:
            issues.append(
                {
                    "name": entry["source"],
                    "issue": "remaining-variants",
                    "variants": remaining_variants,
                }
            )
    return issues


def process_file(
    source_path: Path,
    translation_path: Path,
    entries: list[dict[str, Any]],
    fix: bool,
) -> tuple[bool, list[dict[str, Any]]]:
    _source_metadata, source_body = read_markdown(source_path)
    metadata, translation_body = read_markdown(translation_path)
    article_id = int(translation_path.stem)
    normalized_body, annotations = normalize_body(source_body, translation_body, entries, article_id)
    applicable = applicable_names(source_body, entries, article_id)

    normalized_metadata = dict(metadata)
    for field in ("translation_title", "translation_summary"):
        if isinstance(normalized_metadata.get(field), str):
            normalized_metadata[field] = normalize_card_text(normalized_metadata[field], applicable)
    if annotations:
        normalized_metadata["staff_name_policy"] = "kana-first; first occurrence annotated"
        normalized_metadata["staff_name_annotations"] = annotations
    else:
        normalized_metadata.pop("staff_name_policy", None)
        normalized_metadata.pop("staff_name_annotations", None)

    changed = normalized_body != translation_body or normalized_metadata != metadata
    if fix and changed:
        write_markdown(translation_path, normalized_metadata, normalized_body)
    body_to_audit = normalized_body if fix else translation_body
    return changed, audit_body(source_body, body_to_audit, entries, article_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit and normalize Staff Blog names across Chinese translations.")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--content", type=Path, default=DEFAULT_CONTENT)
    parser.add_argument("--translations", type=Path, default=DEFAULT_TRANSLATIONS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--only", type=int, nargs="*")
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    entries = load_policy(args.policy)
    selected = sorted(args.translations.glob("*.md"), key=lambda path: int(path.stem))
    if args.only:
        wanted = set(args.only)
        selected = [path for path in selected if int(path.stem) in wanted]

    changed_files: list[str] = []
    report_issues: list[dict[str, Any]] = []
    for translation_path in selected:
        source_path = args.content / translation_path.stem / "ja.md"
        if not source_path.exists():
            report_issues.append({"article": int(translation_path.stem), "issues": [{"issue": "missing-source"}]})
            continue
        changed, issues = process_file(source_path, translation_path, entries, args.fix)
        if changed:
            changed_files.append(translation_path.name)
        if issues:
            report_issues.append({"article": int(translation_path.stem), "issues": issues})

    report = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "policy": args.policy.relative_to(ROOT).as_posix() if args.policy.is_relative_to(ROOT) else str(args.policy),
        "files_checked": len(selected),
        "files_changed": len(changed_files) if args.fix else 0,
        "would_change": len(changed_files),
        "changed_files": changed_files,
        "issue_articles": len(report_issues),
        "issues": report_issues,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(yaml.safe_dump(report, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")
    action = "fixed" if args.fix else "would change"
    print(f"staff names: checked {len(selected)}; {action} {len(changed_files)}; issue articles {len(report_issues)}")
    if args.check and report_issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
