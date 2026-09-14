"""Detailed investigation script for interview posts, single-pass optimized.
"""
from __future__ import annotations
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

POSTS_DIR = Path("_posts")

def check_duplicates():
    posts = sorted(POSTS_DIR.glob("*interview*.md"))
    url_to_files = defaultdict(list)
    date_to_files = defaultdict(list)
    for p in posts:
        parts = p.read_text(encoding="utf-8").split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            src = fm.get("source", {})
            url = src.get("url", "") if isinstance(src, dict) else ""
            if url:
                url_to_files[url].append((p.name, fm.get("title", ""), p.stat().st_size))
            d = str(fm.get("date", ""))[:10]
            date_to_files[d].append((p.name, fm.get("title", ""), p.stat().st_size))

    print("=== SAME SOURCE URL FILES ===", flush=True)
    for u, fnames in url_to_files.items():
        if len(fnames) > 1:
            print(f"URL: {u}")
            for fn, title, sz in fnames:
                print(f"   -> {fn} ({sz}b) | '{title}'")
    print(flush=True)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "duplicate":
        check_duplicates()
        return
    posts = sorted(POSTS_DIR.glob("*interview*.md"))
    print(f"Auditing {len(posts)} interview files in single pass...\n", flush=True)

    title_to_files = defaultdict(list)
    noise_patterns = [
        (r"小売希望価格|新品最安値|発売日：20\d\d年", "fami_store_ad"),
        (r"Roblox|ギフトカード", "roblox_ad"),
        (r"Page Tags|Website Programming|Interactive Affiliates", "site_footer_nav"),
        (r"gamescom 2026|Mega Man|Review – Space For Improvement|Popular Content", "gameinformer_sidebar"),
        (r"None None", "none_none_junk"),
        (r"▲トップへ|メニュー へ戻る|「砂の碑」トップページ", "nav_top"),
        (r"Post Tweet Email|Twitter Facebook Instagram Twitch YouTube", "social_share"),
        (r"A Special Movie Preview of Pokemon", "unrelated_preview_nav"),
    ]

    total_noise_items = 0
    file_noise_counts = Counter()
    sample_noise = defaultdict(list)

    count_bad_breaks = 0
    files_with_newlines = Counter()
    sample_bad = []

    speaker_counts = Counter()
    missing_speaker_dialogue = []
    inconsistent_speakers = Counter()

    for p in posts:
        parts = p.read_text(encoding="utf-8").split("---", 2)
        if len(parts) < 3:
            continue
        try:
            fm = yaml.safe_load(parts[1])
        except Exception as e:
            print(f"Error parsing {p.name}: {e}", flush=True)
            continue

        title = fm.get("title", "")
        title_to_files[title].append((p.name, p.stat().st_size))
        items = fm.get("parallel_items", [])

        for idx, it in enumerate(items):
            if not isinstance(it, dict):
                continue
            orig = str(it.get("original", ""))
            trans = str(it.get("translation", ""))
            sp = str(it.get("speaker", "")).strip()

            # 1. Noise
            combined = orig + " " + trans
            for pat, label in noise_patterns:
                if re.search(pat, combined, re.IGNORECASE):
                    total_noise_items += 1
                    file_noise_counts[p.name] += 1
                    sample_noise[label].append((p.name, idx, orig[:80], trans[:80]))
                    break

            # 2. Line breaks
            if "\n" in orig.strip() or "\n" in trans.strip():
                count_bad_breaks += 1
                files_with_newlines[p.name] += 1
                if len(sample_bad) < 5:
                    sample_bad.append((p.name, idx, orig, trans))

            # 3. Speaker
            if sp:
                speaker_counts[sp] += 1
                if " " in sp or "　" in sp:
                    inconsistent_speakers[sp] += 1
            else:
                m = re.match(r"^([^\s:：]{1,10})[:：](.*)$", trans)
                if m and not any(m.group(1).startswith(k) for k in ["http", "注", "第"]):
                    missing_speaker_dialogue.append((p.name, idx, m.group(1), trans[:80]))

    print("=== 1. DUPLICATE POSTS ===", flush=True)
    for t, fnames in title_to_files.items():
        if len(fnames) > 1:
            print(f"Title: {t}")
            for fn, sz in fnames:
                print(f"   -> {fn} ({sz} bytes)")
    print()

    print("=== 2. NOISE DETAILS ===", flush=True)
    print(f"Total noise items found: {total_noise_items} across {len(file_noise_counts)} files")
    for label, samples in sample_noise.items():
        print(f"\nPattern: {label} (total: {len(samples)})")
        for fn, idx, orig, trans in samples[:2]:
            print(f"  [{fn}#item{idx}] orig : {repr(orig)}")
            print(f"  [{fn}#item{idx}] trans: {repr(trans)}")
    print()

    print("=== 3. AWKWARD LINE BREAKS / INTERNAL NEWLINES ===", flush=True)
    print(f"Total paragraphs with internal line breaks: {count_bad_breaks} across {len(files_with_newlines)} files")
    print("Files with most newline issues:")
    for fn, c in files_with_newlines.most_common(10):
        print(f"  {fn}: {c} paragraphs")
    print("\nSamples:")
    for fn, idx, orig, trans in sample_bad[:2]:
        print(f"  [{fn}#item{idx}]")
        print(f"    orig : {repr(orig)}")
        print(f"    trans: {repr(trans)}")
    print()

    print("=== 4. SPEAKER AUDIT ===", flush=True)
    print("Inconsistent spacing in speaker names (e.g. '增田 顺一' vs '增田顺一'):")
    for sp, cnt in inconsistent_speakers.most_common(15):
        print(f"  '{sp}': {cnt} times")

    print(f"\nUnset speaker where translation starts with Name: (total: {len(missing_speaker_dialogue)})")
    for fn, idx, lead, sample in missing_speaker_dialogue[:10]:
        print(f"  [{fn}#item{idx}] lead: '{lead}' | text: {sample}")

if __name__ == "__main__":
    main()
