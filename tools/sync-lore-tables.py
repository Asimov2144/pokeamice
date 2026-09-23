#!/usr/bin/env python3
"""The two lookup tables build-post-lore.py needs, copied in from the other repos.

    python tools/sync-lore-tables.py                 # refresh both from the local checkouts
    python tools/sync-lore-tables.py --check         # only say whether they are stale

docs has no Pokémon species list and no place registry of its own; the App and the
platform do, and their ids are the join keys the App will link on. So the two tables are
vendored here, each with the file it came from and the day it was taken:

    data/lore_tables/pokemon_names.json   name (zh / ja / en, regional forms too) -> national
                                          dex number, plus the Chinese name per number.
                                          From the App's src/pokemonSprites.ts, which
                                          rebuild_pokemon_engine.mjs generates.
    data/lore_tables/tour_places.json     the places the travel map knows, minus the 489
                                          manhole covers no article talks about: Pokémon
                                          Centers, GAME FREAK's old addresses, event
                                          venues, gyms, shops. id / name / category /
                                          entity (the shop across its addresses) / the
                                          years that address was open / city / tags.
                                          From pokeamice-platform/event/public/tour-places.json.

Neither repo is a dependency of the docs build: if the checkout is not on this machine the
script says so and leaves the vendored copy alone. The lore builder records which version
of each table it matched against, so a stale table shows up in the output rather than
silently changing what an article is said to mention.
"""
import io
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "lore_tables"

SPRITES = Path("P:/WEBSITE/pokeamice/Pokeamice_app/src/pokemonSprites.ts")
PLACES = Path("P:/WEBSITE/pokeamice-platform/event/public/tour-places.json")

# the categories an article can plausibly name; 489 manhole covers are not among them
PLACE_CATEGORIES = {"pc", "gym", "ex", "ps", "venue", "hiking", "game_freak", "default", "restaurant", "prototype", "masuda", "shop", "museum"}


def obj_literal(text: str, name: str) -> dict:
    """the `export const NAME: … = {…};` object literal, read as JSON"""
    i = text.index(f"export const {name}")
    start = text.index("{", i)
    depth, j = 0, start
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    return json.loads(text[start:j + 1])


def build_pokemon() -> dict:
    text = io.open(SPRITES, encoding="utf-8").read()
    names = obj_literal(text, "NAME_TO_DEX")
    zh = obj_literal(text, "DEX_TO_ZH")
    return {"source": "Pokeamice_app/src/pokemonSprites.ts", "synced": date.today().isoformat(),
            "count": len(names), "names": names, "zh": zh}


def aliases_for(name: str, stop: set) -> list:
    """the other ways an article writes this place's name.

    Only two: the name with its spaces closed up (「宝可梦中心 福冈」 is written
    「宝可梦中心福冈」 as often as not), and what stands before the dash (「胡萝卜塔-Game
    Freak」 is the tower). Never what stands before a bracket - that turns 「札幌市（GO
    Fest 2022）」 into 札幌市 and 「宝可梦中心 福冈（キャナルシティ初代店址）」 into the
    name of the shop's other address, so an article that merely says the city or the shop
    would be pinned to one dated venue. A town or prefecture that the gazetteer itself
    names somewhere is dropped for the same reason."""
    out = []
    bare = re.sub(r"[\s·・]", "", name)
    if bare != name:
        out.append(bare)
    head = re.split(r"[-—–]", name)[0].strip()
    if head and head != name and len([*head]) >= 3:
        out.append(head)
        if re.sub(r"\s", "", head) != head:
            out.append(re.sub(r"\s", "", head))
    return sorted({a for a in out if len([*a]) >= 3 and a not in stop and not re.search(r"[市区町村県府都州]$", a)})


def build_places() -> dict:
    rows = json.load(io.open(PLACES, encoding="utf-8"))
    # every town and prefecture the table itself names: an alias must not be one of them
    stop = {str(r.get(k) or "").strip() for r in rows for k in ("cityName", "prefectureName", "regionName", "countryName")} - {""}
    out = []
    for r in rows:
        if r.get("category") not in PLACE_CATEGORIES:
            continue
        out.append({"id": r["id"], "name": r["name"], "category": r.get("category"),
                    "entity": r.get("entityId"), "status": r.get("status"),
                    "from": r.get("validFrom"), "to": r.get("validTo"),
                    "city": r.get("cityName"), "pref": r.get("prefectureName"),
                    "tags": [t for t in (r.get("tags") or []) if t],
                    "aliases": aliases_for(r["name"], stop)})
    out.sort(key=lambda p: p["id"])
    return {"source": "pokeamice-platform/event/public/tour-places.json", "synced": date.today().isoformat(),
            "count": len(out), "of_total": len(rows), "categories": sorted(PLACE_CATEGORIES), "places": out}


def write(path: Path, obj, check: bool) -> bool:
    text = json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False) + "\n"
    old = io.open(path, encoding="utf-8").read() if path.exists() else ""
    same = old and json.loads(old).get("count") == obj.get("count") and json.loads(old).get("names", json.loads(old).get("places")) == obj.get("names", obj.get("places"))
    if check:
        print(f"  {'same' if same else 'STALE'}  {path.relative_to(ROOT)}")
        return not same
    path.parent.mkdir(parents=True, exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)
    print(f"  wrote {path.relative_to(ROOT)}  {obj['count']} rows  {len(text) // 1024} KB")
    return not same


def main() -> int:
    check = "--check" in sys.argv[1:]
    stale = False
    for src, name, build in ((SPRITES, "pokemon_names.json", build_pokemon), (PLACES, "tour_places.json", build_places)):
        if not src.exists():
            print(f"  skip {name}: {src} is not on this machine")
            continue
        stale = write(OUT / name, build(), check) or stale
    return 1 if (check and stale) else 0


if __name__ == "__main__":
    raise SystemExit(main())
