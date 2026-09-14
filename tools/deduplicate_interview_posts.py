import sys
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

POSTS_DIR = Path("_posts")

# Each tuple: (keep_file, remove_file, era_skin_to_ensure, source_url_to_ensure)
DEDUP_ACTIONS = [
    (
        "2004-05-13-interview-2004-05-13-ign-e3-2004-pokemon-creators.md",
        "2004-05-13-interview-ign-e3-2004-pokemon-creators-speak.md",
        "2003",
        "https://www.ign.com/articles/2004/05/13/e3-2004-the-pokemon-creators-speak"
    ),
    (
        "2011-03-01-interview-nintendo-power-bw-masuda-sugimori.md",
        "2011-03-01-interview-nintendopower-bw-masuda-sugimori.md",
        "2011",
        "https://lavacutcontent.com/masuda-sugimori-gen-5/"
    ),
    (
        "2014-02-14-interview-gameinformer-masuda-afterwords-xy.md",
        "2014-02-14-interview-gameinformer-xy-afterwords-masuda.md",
        "2014",
        "https://www.gameinformer.com/b/features/archive/2014/02/14/afterwords-unabridged-pokemon-x-and-y.aspx"
    ),
    (
        "2014-11-01-interview-elpais-oras-masuda-ohmori.md",
        "2014-11-01-interview-elpais-masuda-ohmori-barcelona.md",
        "2014",
        "https://elpais.com/cultura/2014/11/01/actualidad/1414798048_551223.html"
    ),
    (
        "2016-05-12-interview-inside-pokken-tournament-developers.md",
        "2016-05-12-interview-pokken-tournament-inside.md",
        "2014",
        "https://www.inside-games.jp/article/2016/05/12/98566_2.html"
    ),
    (
        "2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline.md",
        "2017-07-10-interview-cgworld-sun-moon-3d-pipeline-creatures-gamefreak.md",
        "2019",
        "https://cgworld.jp/feature/201707-cgw227GG-pokemon.html"
    ),
    (
        "2017-08-10-interview-game-informer-how-game-freak-designs-pokemon-creatures.md",
        "2017-08-10-interview-gameinformer-how-gf-designs-pokemon.md",
        "2014",
        "https://gameinformer.com/b/features/archive/2017/08/10/heres-how-game-freak-designs-pokemon-creatures.aspx"
    ),
]

print("=== Starting Deduplication & Consolidation ===")
removed_count = 0

for keep_name, remove_name, era, source_url in DEDUP_ACTIONS:
    keep_path = POSTS_DIR / keep_name
    remove_path = POSTS_DIR / remove_name

    if not keep_path.exists():
        print(f"Warning: Keep target does not exist: {keep_name}")
        continue

    # Read keep file and enrich if needed
    raw_keep = keep_path.read_text(encoding="utf-8")
    parts = raw_keep.split("---", 2)
    if len(parts) >= 3:
        fm = yaml.safe_load(parts[1]) or {}
        modified = False
        if not fm.get("era_skin") and era:
            fm["era_skin"] = era
            modified = True
        if not fm.get("source") and source_url:
            fm["source"] = {
                "title": fm.get("title", ""),
                "url": source_url,
                "source_type": "web_interview"
            }
            modified = True
        elif isinstance(fm.get("source"), str) and source_url:
            fm["source"] = {
                "title": fm.get("title", ""),
                "url": source_url,
                "source_type": "web_interview"
            }
            modified = True

        if modified:
            new_fm_text = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
            keep_path.write_text(f"---\n{new_fm_text}---\n{parts[2]}", encoding="utf-8")
            print(f"Updated metadata on: {keep_name} (era_skin: {fm.get('era_skin')})")

    # Remove redundant file
    if remove_path.exists():
        remove_path.unlink()
        print(f"Deleted duplicate: {remove_name}")
        removed_count += 1
    else:
        print(f"Already removed or not found: {remove_name}")

print(f"\nDeduplication complete! Total duplicate posts removed: {removed_count}")
