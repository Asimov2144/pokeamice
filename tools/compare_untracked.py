"""Compare the 14 untracked files in _posts/ with their tracked counterparts.
"""
import sys
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

POSTS_DIR = Path("_posts")

UNTRACKED = [
    "1999-11-22-interview-time-satoshi-tajiri-ultimate-game-freak.md",
    "2009-05-01-interview-nintendo-power-masuda-kawachimaru-platinum-gens.md",
    "2010-03-19-interview-gameinformer-masuda-morimoto-hgss.md",
    "2011-03-01-interview-eurogamer-masuda-sugimori-black-white-brains.md",
    "2012-08-05-interview-famitsu-b2w2-fanmeeting-masuda-unno.md",
    "2013-11-16-interview-famitsu-xy-music-fanmeeting-masuda-kageyama.md",
    "2017-07-03-interview-denfaminicogamer-ohmori-onoue-gear-project.md",
    "2017-08-10-interview-game-informer-how-game-freak-designs-pokemon-creatures.md",
    "2017-08-14-interview-game-informer-why-ruby-sapphire-most-challenging.md",
    "2018-06-08-interview-denfaminicogamer-pokemon-go-server-miracle.md",
    "2019-10-24-interview-eurogamer-masuda-ohmori-sword-shield-dex-sirfetchd.md",
    "2021-04-30-interview-famitsu-new-pokemon-snap-ishihara-suzaki.md",
    "2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline.md",
    "2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza.md",
]

for fn in UNTRACKED:
    p = POSTS_DIR / fn
    if not p.exists():
        continue
    fm = yaml.safe_load(p.read_text(encoding="utf-8").split("---", 2)[1])
    date_prefix = fn[:10]
    
    # Find any other posts matching this date or topic
    matches = [m.name for m in POSTS_DIR.glob(f"{date_prefix}*interview*.md") if m.name != fn]
    print(f"Untracked: {fn} ({p.stat().st_size}b)")
    print(f"  Title: {fm.get('title')}")
    print(f"  Other posts with date {date_prefix}: {matches}")
    for m in matches:
        mp = POSTS_DIR / m
        mfm = yaml.safe_load(mp.read_text(encoding="utf-8").split("---", 2)[1])
        print(f"    vs {m} ({mp.stat().st_size}b): '{mfm.get('title')}'")
    print()
