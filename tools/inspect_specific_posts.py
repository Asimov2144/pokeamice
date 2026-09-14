import sys
from pathlib import Path
import yaml

sys.stdout.reconfigure(encoding="utf-8")

posts = [
    "2002-11-01-interview-nom-ruby-sapphire-director-masuda.md",
    "2002-11-01-interview-nom-ruby-sapphire-multi-battle-secret-base.md"
]

for fname in posts:
    p = Path("_posts") / fname
    parts = p.read_text(encoding="utf-8").split("---", 2)
    fm = yaml.safe_load(parts[1])
    items = fm.get("parallel_items", [])
    print(f"=== {fname} ({len(items)} items) ===")
    for i, it in enumerate(items[:6]):
        spk = it.get("speaker")
        orig = repr(it.get("original", "")[:45])
        trans = repr(it.get("translation", "")[:45])
        print(f"  [{i}] spk: {spk} | orig: {orig} | trans: {trans}")
