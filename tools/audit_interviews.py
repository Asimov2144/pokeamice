"""Comprehensive audit of interview posts in _posts/.
Analyzes:
1. Ads, navigation, crawl noise, and unrelated game articles
2. Speaker identification coverage, inconsistencies, and patterns
3. Formatting issues: bad line breaks, raw newlines, irregular whitespace
4. Translation quality: untranslated blocks, terminology consistency, missing translations
5. Duplicate / redundant post files
"""

from __future__ import annotations
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

POSTS_DIR = Path("_posts")

# Known noise keywords
NOISE_KEYWORDS = [
    "tweet", "share", "facebook", "twitter", "instagram", "youtube", "twitch",
    "discussion thread", "skip to main content", "alexa internet", "alexa crawls",
    "top of page", "トップへ", "メニューへ", "バックナンバー",
    "mega man", "showa american", "ace combat", "total war", "warhammer",
    "no rest for the wicked", "dawnwalker", "onimusha",
    "check out our review", "popular content"
]

def audit():
    interview_files = sorted(POSTS_DIR.glob("*interview*.md"))
    print(f"Auditing {len(interview_files)} interview files in {POSTS_DIR}...\n")

    files_data = []
    title_to_files = defaultdict(list)
    speaker_counts = Counter()
    unattributed_dialogue_candidates = []
    noise_items_found = []
    formatting_issues = []
    translation_quality_issues = []

    for path in interview_files:
        content = path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            print(f"Skipping malformed frontmatter: {path.name}")
            continue

        try:
            fm = yaml.safe_load(parts[1])
        except Exception as e:
            print(f"YAML parse error in {path.name}: {e}")
            continue

        title = fm.get("title", "")
        title_to_files[title].append(path.name)
        items = fm.get("parallel_items", [])
        body_md = parts[2]

        file_stat = {
            "path": path,
            "filename": path.name,
            "title": title,
            "item_count": len(items),
            "speakers": set(),
            "has_body_text": len(body_md.strip()) > 0,
            "speaker_items": 0,
            "unattributed_count": 0,
        }

        prev_speaker = None
        for idx, it in enumerate(items):
            if not isinstance(it, dict):
                continue

            orig = str(it.get("original", ""))
            trans = str(it.get("translation", ""))
            sp = str(it.get("speaker", "")).strip()
            itype = it.get("type", "")

            if sp:
                speaker_counts[sp] += 1
                file_stat["speakers"].add(sp)
                file_stat["speaker_items"] += 1
            else:
                file_stat["unattributed_count"] += 1

            # 1. Noise check
            lower_orig = orig.lower()
            lower_trans = trans.lower()
            for kw in NOISE_KEYWORDS:
                if kw in lower_orig or kw in lower_trans:
                    noise_items_found.append({
                        "file": path.name,
                        "idx": idx,
                        "kw": kw,
                        "original": orig[:100],
                        "translation": trans[:100],
                        "speaker": sp
                    })
                    break

            # Check for URL or nav strings
            if re.search(r"https?://(www\.)?(gameinformer|ign|eurogamer|famitsu|4gamer)\.com/?\s*$", orig):
                noise_items_found.append({
                    "file": path.name,
                    "idx": idx,
                    "kw": "raw_url",
                    "original": orig[:100],
                    "translation": trans[:100],
                    "speaker": sp
                })

            # 2. Formatting / Bad line breaks
            # Check internal newlines in original or translation
            if "\n" in orig.strip() or "\r" in orig:
                formatting_issues.append({
                    "file": path.name,
                    "idx": idx,
                    "type": "internal_newline_orig",
                    "sample": repr(orig[:80])
                })
            if "\n" in trans.strip() or "\r" in trans:
                formatting_issues.append({
                    "file": path.name,
                    "idx": idx,
                    "type": "internal_newline_trans",
                    "sample": repr(trans[:80])
                })
            if "　" in orig and len(orig.split("　")) > 3: # many fullwidth spaces
                formatting_issues.append({
                    "file": path.name,
                    "idx": idx,
                    "type": "excessive_fullwidth_space",
                    "sample": orig[:60]
                })

            # 3. Speaker detection candidates (where speaker is missing but text looks like dialogue)
            if not sp and itype == "paragraph":
                # Look for leading patterns: "増田：", "Q:", "杉森：", "田尻: ", "Masuda: ", "IGN: ", etc.
                m = re.match(r"^([A-Za-z\u4e00-\u9fa5\u3040-\u30ff\.\s]{1,20})[:：>>＞＞\-\–\—]\s*(.*)", orig)
                m2 = re.match(r"^([A-Za-z\u4e00-\u9fa5\.\s]{1,15})[:：\-\–\—]\s*(.*)", trans)
                if m or m2:
                    lead = (m.group(1) if m else m2.group(1)).strip()
                    # Filter out False Positives like "Chapter 1", "注", "http", "第1回"
                    if not any(lead.startswith(x) for x in ["http", "Chapter", "Vol", "第", "Part", "P."]):
                        unattributed_dialogue_candidates.append({
                            "file": path.name,
                            "idx": idx,
                            "lead": lead,
                            "orig_sample": orig[:70],
                            "trans_sample": trans[:70]
                        })

            # 4. Translation Quality
            # Check if translation is empty while original is non-empty
            if orig.strip() and not trans.strip():
                translation_quality_issues.append({
                    "file": path.name,
                    "idx": idx,
                    "type": "missing_translation",
                    "orig": orig[:80]
                })
            # Check if translation is identical to original (untranslated non-English/non-symbols)
            elif orig.strip() == trans.strip() and len(orig.strip()) > 30 and re.search(r"[a-zA-Z\u3040-\u30ff]", orig):
                # Only flag if it doesn't look like code or standard quote
                if not re.search(r"[\u4e00-\u9fa5]", orig): # contains no Chinese at all
                    translation_quality_issues.append({
                        "file": path.name,
                        "idx": idx,
                        "type": "untranslated_block",
                        "orig": orig[:80]
                    })
            # Check for placeholder markers like [TODO], [翻译中], etc.
            if any(marker in trans for marker in ["[TODO]", "TODO:", "【待翻译】", "待翻译"]):
                translation_quality_issues.append({
                    "file": path.name,
                    "idx": idx,
                    "type": "todo_marker",
                    "trans": trans[:80]
                })

        files_data.append(file_stat)

    print("=" * 60)
    print("1. DUPLICATE POSTS REPORT")
    print("=" * 60)
    dup_count = 0
    for t, fnames in title_to_files.items():
        if len(fnames) > 1:
            dup_count += 1
            print(f"Title: '{t}'")
            for fn in fnames:
                print(f"   -> {fn}")
    print(f"Total duplicate title clusters: {dup_count}\n")

    print("=" * 60)
    print("2. NOISE & ADS ITEMS FOUND")
    print("=" * 60)
    print(f"Total noise matches: {len(noise_items_found)}")
    # Group by file
    noise_by_file = defaultdict(list)
    for n in noise_items_found:
        noise_by_file[n["file"]].append(n)
    for fn, items_list in sorted(noise_by_file.items(), key=lambda x: -len(x[1]))[:15]:
        print(f"  {fn}: {len(items_list)} noise items (e.g. keywords: {[x['kw'] for x in items_list[:5]]})")
        for sample in items_list[:2]:
            print(f"     [item {sample['idx']}] orig: {sample['original']}")
            print(f"                         trans: {sample['translation']}")
    print()

    print("=" * 60)
    print("3. FORMATTING & AWKWARD LINE BREAKS")
    print("=" * 60)
    print(f"Total internal newline issues: {len(formatting_issues)}")
    fmt_by_file = defaultdict(list)
    for f in formatting_issues:
        fmt_by_file[f["file"]].append(f)
    for fn, items_list in sorted(fmt_by_file.items(), key=lambda x: -len(x[1]))[:15]:
        print(f"  {fn}: {len(items_list)} formatting issues")
        for s in items_list[:2]:
            print(f"     [{s['type']}] {s['sample']}")
    print()

    print("=" * 60)
    print("4. SPEAKER IDENTIFICATION & ATTRIBUTION")
    print("=" * 60)
    print(f"Top 25 Identified Speakers across posts:")
    for sp, cnt in speaker_counts.most_common(25):
        print(f"  {sp:<20}: {cnt} turns")
    print(f"\nPotential unlabelled dialogue items with speaker prefix: {len(unattributed_dialogue_candidates)}")
    lead_counts = Counter(x["lead"] for x in unattributed_dialogue_candidates)
    print("Most common unparsed speaker prefixes:")
    for lead, cnt in lead_counts.most_common(20):
        print(f"  '{lead}': {cnt} times")
    print("\nSample unattributed items:")
    for sample in unattributed_dialogue_candidates[:8]:
        print(f"  [{sample['file']}:idx {sample['idx']}] lead: '{sample['lead']}' | trans: {sample['trans_sample']}")
    print()

    print("=" * 60)
    print("5. TRANSLATION QUALITY ISSUES")
    print("=" * 60)
    print(f"Total translation quality issues flagged: {len(translation_quality_issues)}")
    tq_by_type = Counter(x["type"] for x in translation_quality_issues)
    for typ, cnt in tq_by_type.items():
        print(f"  {typ}: {cnt}")
    for sample in translation_quality_issues[:10]:
        print(f"  [{sample['file']}:idx {sample['idx']}] {sample['type']}: {sample.get('orig', sample.get('trans'))}")
    print()

if __name__ == "__main__":
    audit()
