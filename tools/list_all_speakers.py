"""List all speakers across all posts.
"""
from collections import Counter
from pathlib import Path
import yaml, sys

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

posts = sorted(Path("_posts").glob("*interview*.md"))
counts = Counter()
for p in posts:
    parts = p.read_text(encoding="utf-8").split("---", 2)
    if len(parts) < 3: continue
    fm = yaml.safe_load(parts[1])
    for it in fm.get("parallel_items", []):
        if isinstance(it, dict) and it.get("speaker"):
            counts[it["speaker"].strip()] += 1

print(f"Total unique speakers: {len(counts)}")
for sp, c in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {sp:<25}: {c}")
