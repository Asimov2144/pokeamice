"""Inspect specific paired files to check differences, duplication, and quality.
"""
from pathlib import Path
import yaml

POSTS_DIR = Path("_posts")

PAIRS = [
    ("1999-11-22-interview-1999-11-22-time-magazine-tajiri.md", "1999-11-22-interview-time-satoshi-tajiri-ultimate-game-freak.md"),
    ("2000-07-01-interview-2000-07-01-nom-gen1-gamefreak.md", "2000-07-01-interview-nom-gamefreak-roundtable-vol1-red-green.md"),
    ("2000-07-01-interview-2000-07-01-nom-gen2-gamefreak.md", "2000-07-01-interview-nom-gamefreak-roundtable-vol2-gold-silver-secrets.md"),
    ("2010-03-19-interview-2010-03-19-game-informer-hgss.md", "2010-03-19-interview-gameinformer-masuda-morimoto-hgss.md"),
    ("2017-08-10-interview-game-informer-how-game-freak-designs-pokemon-creatures.md", "2017-08-10-interview-heres-how-game-freak-designs-pokemo.md"),
    ("2018-06-08-interview-denfaminicogamer-pokemon-go-miracle.md", "2018-06-08-interview-denfaminicogamer-pokemon-go-server-miracle.md"),
    ("2021-04-30-interview-famitsu-new-pokemon-snap-ishihara-suzaki.md", "2021-04-30-interview-new-pokemon-snap-ishihara-suzaki.md"),
]

for f1_name, f2_name in PAIRS:
    p1 = POSTS_DIR / f1_name
    p2 = POSTS_DIR / f2_name
    if not p1.exists() or not p2.exists():
        print(f"Missing one of {f1_name} / {f2_name}")
        continue
    
    fm1 = yaml.safe_load(p1.read_text(encoding="utf-8").split("---", 2)[1])
    fm2 = yaml.safe_load(p2.read_text(encoding="utf-8").split("---", 2)[1])
    
    print(f"=== PAIR ===")
    print(f"1: {f1_name} ({p1.stat().st_size} bytes)")
    print(f"   Title: {fm1.get('title')}")
    print(f"   URL:   {fm1.get('source', {}).get('url')}")
    print(f"   Items: {len(fm1.get('parallel_items', []))}")
    print(f"2: {f2_name} ({p2.stat().st_size} bytes)")
    print(f"   Title: {fm2.get('title')}")
    print(f"   URL:   {fm2.get('source', {}).get('url')}")
    print(f"   Items: {len(fm2.get('parallel_items', []))}")
    print()
