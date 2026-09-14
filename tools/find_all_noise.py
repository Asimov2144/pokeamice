"""Inspect exact noise items across all posts.
"""
import re
import sys
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

POSTS_DIR = Path("_posts")

NOISE_REGEXES = [
    (r"小売希望価格|新品最安値|発売日：20\d\d年", "fami_store_ad"),
    (r"Roblox|ギフトカード", "roblox_ad"),
    (r"Page Tags:|Website Programming:|Interactive Affiliates", "footer_nav"),
    (r"None None", "none_junk"),
    (r"gamescom 2026|Mega Man: Dual Override|The Can't Miss Games|Preview – Mega Man|Review – Space For Improvement|Popular Content|Showa American Story|Ace Combat 8|Total War: Warhammer|No Rest For The Wicked", "unrelated_games"),
    (r"Post Tweet Email|Twitter Facebook Instagram Twitch YouTube|View the discussion thread", "social_share"),
    (r"▲トップへ|メニュー へ戻る|「砂の碑」トップページ", "nav_top"),
    (r"^\{\"\d+\":\[\"\d+\"\]", "raw_json_junk"),
    (r"PlayStation 5/PlayStation 4", "ps5_junk"),
]

def find_all_noise():
    posts = sorted(POSTS_DIR.glob("*interview*.md"))
    results = []
    for p in posts:
        parts = p.read_text(encoding="utf-8").split("---", 2)
        if len(parts) < 3:
            continue
        fm = yaml.safe_load(parts[1])
        items = fm.get("parallel_items", [])
        for idx, it in enumerate(items):
            if not isinstance(it, dict):
                continue
            orig = str(it.get("original", ""))
            trans = str(it.get("translation", ""))
            combined = orig + " " + trans
            for r, label in NOISE_REGEXES:
                if re.search(r, combined, re.IGNORECASE):
                    results.append((p.name, idx, label, orig[:80], trans[:80]))
                    break

    print(f"Total noise items found: {len(results)}")
    by_file = {}
    for fn, idx, label, orig, trans in results:
        by_file.setdefault(fn, []).append((idx, label, orig, trans))
    
    for fn, items in sorted(by_file.items()):
        print(f"\n{fn} ({len(items)} items):")
        for idx, label, orig, trans in items[:5]:
            print(f"  [{label} #idx {idx}]")
            print(f"    orig : {repr(orig)}")
            print(f"    trans: {repr(trans)}")
        if len(items) > 5:
            print(f"    ... and {len(items)-5} more")

if __name__ == "__main__":
    find_all_noise()
