"""Inspect all empty or untranslated items across interview posts.
"""
import sys
import re
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

POSTS_DIR = Path("_posts")

def check_untranslated():
    posts = sorted(POSTS_DIR.glob("*interview*.md"))
    print("=== INSPECTING UNTRANSLATED AND EMPTY TRANSLATIONS ===\n")
    for p in posts:
        parts = p.read_text(encoding="utf-8").split("---", 2)
        if len(parts) < 3:
            continue
        fm = yaml.safe_load(parts[1])
        items = fm.get("parallel_items", [])
        for idx, it in enumerate(items):
            if not isinstance(it, dict):
                continue
            orig = str(it.get("original", "")).strip()
            trans = str(it.get("translation", "")).strip()
            sp = it.get("speaker", "")
            
            # Empty translation
            if orig and not trans:
                print(f"[{p.name}#item{idx}] EMPTY TRANSLATION (speaker: {sp})")
                print(f"   orig : {repr(orig)}")
                print()
            
            # Untranslated block
            if orig == trans and len(orig) > 25 and not re.search(r"[\u4e00-\u9fa5]", orig):
                print(f"[{p.name}#item{idx}] UNTRANSLATED BLOCK (speaker: {sp})")
                print(f"   orig : {repr(orig)}")
                print()

if __name__ == "__main__":
    check_untranslated()
