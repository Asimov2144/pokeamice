"""Merge the reviewed Game Freak translation layer into zh-CN translations.

Only proofread outputs are merged.  The Japanese source is never touched, and
the proofread layer remains available as an audit copy.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION_DIR = ROOT / "archive" / "gamefreak-director" / "translations" / "zh-CN"
PROOFREAD_DIR = ROOT / "archive" / "gamefreak-director" / "translations" / "zh-CN-proofread"


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
    path.write_text(f"---\n{frontmatter}\n---\n\n{body.strip()}\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge Game Freak proofread translations into zh-CN.")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    proofread_files = sorted(PROOFREAD_DIR.glob("*.md"))
    if not proofread_files:
        raise SystemExit(f"No proofread files found: {PROOFREAD_DIR}")
    merged = 0
    skipped = []
    for proofread_path in proofread_files:
        number = int(proofread_path.stem)
        if number < args.start or (args.end and number > args.end):
            continue
        translation_path = TRANSLATION_DIR / proofread_path.name
        if not translation_path.exists():
            skipped.append(f"{number:03d}: translation missing")
            continue
        proofread_metadata, proofread_body = read_markdown(proofread_path)
        translation_metadata, _translation_body = read_markdown(translation_path)
        if proofread_metadata.get("proofread_status") != "machine-proofread" or not proofread_body.strip():
            skipped.append(f"{number:03d}: proofread output is incomplete")
            continue
        translation_metadata.update(
            {
                "translation_status": "proofread",
                "proofreader": proofread_metadata.get("proofreader"),
                "proofread_at": proofread_metadata.get("proofread_at"),
                "proofread_confidence": proofread_metadata.get("confidence"),
                "proofread_issues": proofread_metadata.get("issues") or [],
                "glossary_source": proofread_metadata.get("glossary_source"),
                "glossary_match_count": proofread_metadata.get("glossary_match_count", 0),
                "glossary_missing_targets": proofread_metadata.get("glossary_missing_targets") or [],
                "proofread_source": f"../zh-CN-proofread/{proofread_path.name}",
            }
        )
        if not args.dry_run:
            write_markdown(translation_path, translation_metadata, proofread_body)
        merged += 1
    print(f"Merged {merged} proofread translation(s) into {TRANSLATION_DIR}")
    if skipped:
        print("Skipped:")
        print("\n".join(skipped))
        if not args.dry_run:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
