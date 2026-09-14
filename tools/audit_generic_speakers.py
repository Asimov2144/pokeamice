"""Audit files using generic speaker '受访嘉宾' or unclear speakers.
"""
from collections import defaultdict
from pathlib import Path
import yaml

POSTS_DIR = Path("_posts")

def audit_generic_speakers():
    posts = sorted(POSTS_DIR.glob("*interview*.md"))
    generic_in_files = defaultdict(list)
    for p in posts:
        parts = p.read_text(encoding="utf-8").split("---", 2)
        if len(parts) < 3:
            continue
        fm = yaml.safe_load(parts[1])
        items = fm.get("parallel_items", [])
        title = fm.get("title", "")
        interviewee = fm.get("interviewee", "")
        people = fm.get("entities", {}).get("people", [])
        for idx, it in enumerate(items):
            if not isinstance(it, dict):
                continue
            sp = str(it.get("speaker", "")).strip()
            if sp in ["受访嘉宾", "受访者", "答"]:
                generic_in_files[p.name].append({
                    "idx": idx,
                    "title": title,
                    "interviewee": interviewee,
                    "people": people,
                    "orig": it.get("original", "")[:60],
                    "trans": it.get("translation", "")[:60]
                })

    print(f"Files with '受访嘉宾': {len(generic_in_files)}")
    for fn, items in generic_in_files.items():
        print(f"\nFile: {fn} ({len(items)} turns)")
        print(f"  Title: {items[0]['title']}")
        print(f"  Interviewee: {items[0]['interviewee']} | People: {items[0]['people']}")
        for it in items[:2]:
            print(f"    [item {it['idx']}] orig: {it['orig']}")
            print(f"                      trans: {it['trans']}")

if __name__ == "__main__":
    audit_generic_speakers()
