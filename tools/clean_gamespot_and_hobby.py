"""Clean gamespot and hobbyconsolas posts of trailing and header chrome.
"""
from pathlib import Path
import yaml
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

POSTS_DIR = Path("_posts")

def clean_gamespot():
    p = POSTS_DIR / "2018-10-18-interview-gamespot-lgpe-masuda.md"
    if not p.exists(): return
    text = p.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    fm = yaml.safe_load(parts[1])
    items = fm.get("parallel_items", [])
    
    cleaned = []
    for it in items:
        orig = str(it.get("original", "")).strip()
        trans = str(it.get("translation", "")).strip()
        # Skip ad spacer
        if orig.lower() in ["advertisement", "ad"] or trans == "广告":
            continue
        # Stop before author bio / sidebar
        if "About the Authors" in orig or "关于作者" in trans:
            break
        cleaned.append(it)
        
    fm["parallel_items"] = cleaned
    new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    p.write_text(f"---\n{new_yaml}---\n{parts[2].lstrip()}", encoding="utf-8")
    print(f"Cleaned GameSpot LGPE: {len(items)} -> {len(cleaned)} items")

def clean_hobbyconsolas():
    p = POSTS_DIR / "2013-10-11-interview-hobbyconsolas-masuda-xy.md"
    if not p.exists(): return
    text = p.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    fm = yaml.safe_load(parts[1])
    items = fm.get("parallel_items", [])
    
    start_idx = None
    end_idx = None
    for i, it in enumerate(items):
        orig = it.get("original", "")
        if "Un año después de que Hobby Consolas hablara con Junichi Masuda" in orig:
            start_idx = i
        if "Hay muchísimos Pokémon diferentes, es difícil decir el tiempo de creación" in orig:
            end_idx = i + 1
            
    if start_idx is not None and end_idx is not None:
        cleaned = items[start_idx:end_idx]
        fm["parallel_items"] = cleaned
        new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
        p.write_text(f"---\n{new_yaml}---\n{parts[2].lstrip()}", encoding="utf-8")
        print(f"Cleaned HobbyConsolas: {len(items)} -> {len(cleaned)} items")

if __name__ == "__main__":
    clean_gamespot()
    clean_hobbyconsolas()
