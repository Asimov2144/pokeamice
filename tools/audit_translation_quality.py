"""Comprehensive translation quality and asset audit tool for Pokeamice.
Audits all posts in _posts/*interview*.md for:
1. Empty translations
2. Untranslated Japanese (high kana ratio)
3. Untranslated English paragraphs
4. Translation length truncation anomalies
5. Placeholder or TODO markers
6. Outdated / forbidden terminology (e.g. 神奇宝贝, 宠物小精灵, 口袋妖怪)
7. Missing local images or empty image assets
8. Frontmatter and YAML parsing errors
"""

from __future__ import annotations
import re
import sys
from collections import defaultdict
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

POSTS_DIR = Path("_posts")
ASSETS_DIR = Path("assets")

KANA_RE = re.compile(r"[\u3040-\u309f\u30a0-\u30ff]")
KANJI_RE = re.compile(r"[\u4e00-\u9fff]")

FORBIDDEN_TERMS = [
    ("宠物小精灵", "宝可梦"),
    ("神奇宝贝", "宝可梦"),
    ("口袋妖怪", "宝可梦"),
    ("口袋魔鬼", "宝可梦"),
]

TODO_MARKERS = ["[TODO]", "TODO:", "【待翻译】", "待翻译", "[TRANSLATE]"]


def audit():
    posts = sorted(POSTS_DIR.glob("*interview*.md"))
    print(f"==================================================")
    print(f"Auditing {len(posts)} interview posts in {POSTS_DIR}...")
    print(f"==================================================\n")

    issues = defaultdict(list)
    stats = {
        "total_posts": len(posts),
        "total_items": 0,
        "total_images": 0,
        "yaml_errors": 0,
    }

    for p in posts:
        text = p.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) < 3:
            issues["broken_frontmatter"].append((p.name, 0, "Missing YAML frontmatter delimiters"))
            stats["yaml_errors"] += 1
            continue

        try:
            fm = yaml.safe_load(parts[1])
        except Exception as e:
            issues["yaml_parse_error"].append((p.name, 0, str(e)))
            stats["yaml_errors"] += 1
            continue

        items = fm.get("parallel_items", [])
        stats["total_items"] += len(items)

        for idx, it in enumerate(items):
            if not isinstance(it, dict):
                continue

            itype = it.get("type", "paragraph")
            orig = str(it.get("original", "")).strip()
            trans = str(it.get("translation", "")).strip()
            src = str(it.get("src", "")).strip()

            # Image asset check
            if itype == "image" or src:
                img_ref = src or orig or trans
                if img_ref and not img_ref.startswith("http"):
                    stats["total_images"] += 1
                    clean_path = img_ref.lstrip("/").split("?")[0]
                    img_file = Path(clean_path)
                    if not img_file.exists():
                        issues["missing_image"].append((p.name, idx, img_ref))
                    elif img_file.stat().st_size == 0:
                        issues["empty_image"].append((p.name, idx, img_ref))
                continue

            if itype == "hr":
                continue

            if not orig:
                continue

            # Check 1: Missing / empty translation
            if not trans:
                issues["empty_translation"].append((p.name, idx, orig[:70]))
                continue

            # Check 2: Untranslated Japanese (High kana ratio in translation)
            kana_count = len(KANA_RE.findall(trans))
            if kana_count > 8 and len(trans) > 15:
                # Discard legitimate citations in parentheses like （原文：...）or（CD...）
                trans_no_quotes = re.sub(r"（[^）]*）|\([^\)]*\)", "", trans)
                kana_count_no_quotes = len(KANA_RE.findall(trans_no_quotes))
                if len(trans_no_quotes) > 15 and (kana_count_no_quotes / len(trans_no_quotes)) > 0.15:
                    issues["untranslated_japanese"].append((p.name, idx, trans[:80]))

            # Check 3: Untranslated English in translation
            orig_en = bool(re.search(r"^[A-Za-z0-9\s\.,\?!\"'-]+$", orig))
            trans_en = bool(re.search(r"^[A-Za-z0-9\s\.,\?!\"'-]+$", trans))
            if orig_en and trans_en and len(trans) > 40:
                if not any(k in trans.lower() for k in ["http", "copyright", "assets", "pokemon.com", "©"]):
                    issues["untranslated_english"].append((p.name, idx, trans[:80]))

            # Check 4: Length truncation anomaly
            if len(orig) > 160 and len(trans) < 25 and not any(k in trans for k in ["http", "图", "表"]):
                issues["truncated_translation"].append(
                    (p.name, idx, f"Orig({len(orig)}): {orig[:35]}... -> Trans({len(trans)}): {trans}")
                )

            # Check 5: TODO markers
            for m in TODO_MARKERS:
                if m in trans:
                    issues["todo_marker"].append((p.name, idx, f"Marker '{m}' in: {trans[:60]}"))

            # Check 6: Forbidden / outdated terminology
            for bad, good in FORBIDDEN_TERMS:
                if bad in trans:
                    # Ignore if explicitly explaining translation history
                    if "旧译" not in trans and "曾译" not in trans and "翻译" not in trans and "Pocket Monsters" not in trans:
                        issues["forbidden_term"].append((p.name, idx, f"Found '{bad}' (suggest '{good}'): {trans[:70]}"))

    print(f"--- AUDIT SUMMARY ---")
    print(f"Total Posts: {stats['total_posts']}")
    print(f"Total Dialogue & Text Items: {stats['total_items']}")
    print(f"Total Local Images Verified: {stats['total_images']}")
    print(f"YAML / Frontmatter Errors: {stats['yaml_errors']}")
    print(f"Total Flagged Issues: {sum(len(v) for v in issues.values())}\n")

    for category, items_list in issues.items():
        print(f"[{category.upper()}] - {len(items_list)} issues:")
        for fn, idx, detail in items_list[:10]:
            print(f"  [{fn} #{idx}] {detail}")
        if len(items_list) > 10:
            print(f"  ... and {len(items_list) - 10} more.")
        print()

    return issues


if __name__ == "__main__":
    audit()
