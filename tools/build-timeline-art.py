"""The pictures of the timeline (/timeline/): Pokémon HOME renders, kept with their alpha so the
page can use them as masks (a silhouette filled with the generation's colours) and as the small
figures of the today sheet.

    python tools/build-timeline-art.py           # fetch what is missing
    python tools/build-timeline-art.py --force   # fetch everything again

Writes assets/img/timeline/legends/<dex>.png for every legend in _data/timeline_covers.yml and
assets/img/timeline/<name>.png for the extras below: Celebi (the jump-to-year button), the
evolutions that depend on the time of day (Eevee -> Espeon / Umbreon, Rockruff -> Lycanroc in its
three forms) and Deerling in its four seasons. Renders are PokeAPI's HOME sprites (512 px;
the site's own gallery set is smaller and lacks some).
Each is trimmed to its alpha box, fitted to 360 px on the long side and saved as a 128-colour PNG.
"""
import io
import sys
import urllib.request
from pathlib import Path

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "img" / "timeline"
POKEAPI = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/{}.png"
SIDE = 360

EXTRAS = {
    "celebi": POKEAPI.format(251),
    "eevee": POKEAPI.format(133),
    "espeon": POKEAPI.format(196),
    "umbreon": POKEAPI.format(197),
    "rockruff": POKEAPI.format(744),
    "lycanroc-midday": POKEAPI.format(745),
    "lycanroc-midnight": POKEAPI.format(10126),
    "lycanroc-dusk": POKEAPI.format(10152),
    "deerling-spring": POKEAPI.format(585),
    "deerling-summer": POKEAPI.format("585-summer"),
    "deerling-autumn": POKEAPI.format("585-autumn"),
    "deerling-winter": POKEAPI.format("585-winter"),
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (pokeamice docs)"})
    return urllib.request.urlopen(req, timeout=60).read()


def save(url, path, force):
    if path.exists() and not force:
        return False
    im = Image.open(io.BytesIO(fetch(url))).convert("RGBA")
    box = im.getchannel("A").getbbox()
    if box:
        im = im.crop(box)
    im.thumbnail((SIDE, SIDE), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    im = im.quantize(colors=128, method=Image.FASTOCTREE)    # alpha kept; about a third of the size
    im.save(path, optimize=True)
    print(f"  {path.relative_to(ROOT).as_posix():48s} {im.size[0]}x{im.size[1]}  <- {url.rsplit('/', 1)[-1]}")
    return True


def main():
    force = "--force" in sys.argv
    covers = yaml.safe_load(io.open(ROOT / "_data" / "timeline_covers.yml", encoding="utf-8"))
    n = 0
    for g in covers:
        for lg in g["legends"]:
            n += save(POKEAPI.format(lg["dex"]), OUT / "legends" / f"{lg['dex']}.png", force)
    for name, url in EXTRAS.items():
        n += save(url, OUT / f"{name}.png", force)
    print(f"timeline art: {n} written")


if __name__ == "__main__":
    main()
