"""Deep-dive script to analyze translation quality, ads/noise, linebreaks, and speaker attribution.
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

def run_analysis():
    posts = sorted(POSTS_DIR.glob("*interview*.md"))
    
    # Trackers
    fami_ad_files = defaultdict(list)
    roblox_ad_files = defaultdict(list)
    sidebar_ad_files = defaultdict(list)
    footer_nav_files = defaultdict(list)
    none_junk_files = defaultdict(list)
    
    newline_files = defaultdict(list)
    
    unidentified_speakers = defaultdict(list)
    spaced_speakers = defaultdict(set)
    all_speakers = Counter()
    
    tq_untranslated = defaultdict(list)
    tq_empty = defaultdict(list)
    tq_suspicious_glossary = defaultdict(list)

    for p in posts:
        parts = p.read_text(encoding="utf-8").split("---", 2)
        if len(parts) < 3:
            continue
        try:
            fm = yaml.safe_load(parts[1])
        except Exception:
            continue

        items = fm.get("parallel_items", [])
        for idx, it in enumerate(items):
            if not isinstance(it, dict):
                continue
            orig = str(it.get("original", ""))
            trans = str(it.get("translation", ""))
            sp = str(it.get("speaker", "")).strip()
            
            # --- 1. ADS & NOISE ---
            if re.search(r"小売希望価格|新品最安値|発売日：20\d\d年", orig + trans):
                fami_ad_files[p.name].append((idx, orig[:60], trans[:60]))
            if "roblox" in (orig + trans).lower():
                roblox_ad_files[p.name].append((idx, orig[:60], trans[:60]))
            if any(g in orig.lower() for g in ["gamescom 2026", "mega man", "review – space for improvement", "popular content", "showa american", "no rest for the wicked"]):
                sidebar_ad_files[p.name].append((idx, orig[:60], trans[:60]))
            if any(f in orig for f in ["Page Tags:", "Website Programming:", "Interactive Affiliates"]):
                footer_nav_files[p.name].append((idx, orig[:60], trans[:60]))
            if "none none" in (orig + trans).lower():
                none_junk_files[p.name].append((idx, orig[:60], trans[:60]))

            # --- 2. AWKWARD LINE BREAKS ---
            if "\n" in orig.strip() or "\n" in trans.strip():
                # Count how many \n
                orig_nl = orig.count("\n")
                trans_nl = trans.count("\n")
                newline_files[p.name].append((idx, orig_nl, trans_nl, orig[:40], trans[:40]))

            # --- 3. SPEAKERS ---
            if sp:
                all_speakers[sp] += 1
                if " " in sp or "　" in sp:
                    spaced_speakers[sp].add(p.name)
            else:
                # Check for speaker pattern in translation or original
                m = re.match(r"^([A-Za-z\u4e00-\u9fa5\u3040-\u30ff]{1,10})[:：](.*)$", trans)
                if m:
                    candidate = m.group(1).strip()
                    if candidate in ["增田", "增田顺一", "杉森", "杉森建", "田尻", "田尻智", "森本", "森本茂树", "大森", "大森滋", "石原", "石原恒和", "海野", "岩田", "问", "记者", "Fami通", "IGN", "提问"]:
                        unidentified_speakers[p.name].append((idx, candidate, trans[:60]))

            # --- 4. TRANSLATION QUALITY ---
            if orig.strip() and not trans.strip():
                tq_empty[p.name].append((idx, orig[:60]))
            if orig.strip() == trans.strip() and len(orig.strip()) > 30:
                if not re.search(r"[\u4e00-\u9fa5]", orig):
                    tq_untranslated[p.name].append((idx, orig[:60]))
            # Suspicious terms
            if any(old_t in trans for old_t in ["口袋妖怪", "宠物小精灵", "神奇宝贝"]):
                tq_suspicious_glossary[p.name].append((idx, trans[:60]))

    print("=== SUMMARY OF FINDINGS ===")
    print(f"Total files audited: {len(posts)}")
    print(f"1. Files with Famitsu store widget ads: {len(fami_ad_files)} files ({sum(len(v) for v in fami_ad_files.values())} items)")
    for fn, items_list in fami_ad_files.items():
        print(f"   - {fn}: {len(items_list)} ads")
    print(f"2. Files with Roblox gift card ads: {len(roblox_ad_files)} files ({sum(len(v) for v in roblox_ad_files.values())} items)")
    for fn, items_list in roblox_ad_files.items():
        print(f"   - {fn}: {len(items_list)} ads")
    print(f"3. Files with unrelated sidebar/game reviews: {len(sidebar_ad_files)} files ({sum(len(v) for v in sidebar_ad_files.values())} items)")
    for fn, items_list in sidebar_ad_files.items():
        print(f"   - {fn}: {len(items_list)} items")
    print(f"4. Files with website footer navigation: {len(footer_nav_files)} files ({sum(len(v) for v in footer_nav_files.values())} items)")
    for fn, items_list in footer_nav_files.items():
        print(f"   - {fn}: {len(items_list)} items")
    print(f"5. Files with 'None None' parser junk: {len(none_junk_files)} files ({sum(len(v) for v in none_junk_files.values())} items)")
    for fn, items_list in none_junk_files.items():
        print(f"   - {fn}: {len(items_list)} items")

    print(f"\n6. Internal newlines/broken line breaks: {len(newline_files)} files ({sum(len(v) for v in newline_files.values())} paragraphs)")
    for fn, items_list in sorted(newline_files.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"   - {fn}: {len(items_list)} paragraphs with internal newlines")

    print(f"\n7. Speaker attribution:")
    print(f"   Total unique speaker strings: {len(all_speakers)}")
    print(f"   Spaced speaker strings to normalize (e.g. '增田 顺一' -> '增田顺一'): {len(spaced_speakers)}")
    for sp, fns in spaced_speakers.items():
        print(f"     '{sp}' across {len(fns)} files")
    print(f"   Unset speaker where text starts with name: {len(unidentified_speakers)} files ({sum(len(v) for v in unidentified_speakers.values())} items)")
    for fn, items_list in unidentified_speakers.items():
        print(f"     - {fn}: {len(items_list)} dialogue items needing speaker extraction")

    print(f"\n8. Translation quality issues:")
    print(f"   Empty translations: {len(tq_empty)} files ({sum(len(v) for v in tq_empty.values())} items)")
    print(f"   Untranslated foreign blocks: {len(tq_untranslated)} files ({sum(len(v) for v in tq_untranslated.values())} items)")
    print(f"   Outdated legacy terms (口袋妖怪/神奇宝贝): {len(tq_suspicious_glossary)} files ({sum(len(v) for v in tq_suspicious_glossary.values())} items)")
    for fn, items_list in tq_suspicious_glossary.items():
        print(f"     - {fn}: {len(items_list)} legacy terms, e.g.: {items_list[0][1]}")

if __name__ == "__main__":
    run_analysis()
