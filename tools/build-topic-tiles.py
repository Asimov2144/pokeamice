"""The home page's collection shelf: one 336x192 picture per collection in assets/img/topics.

    python tools/build-topic-tiles.py            # write the missing ones
    python tools/build-topic-tiles.py --force    # redo them all

Each collection gets a picture the site already has - a scan's cover, the director
blog's page header, a 社長が訊く photograph, a CEDEC slide - cut to 7:4 and saved
small (20-40 KB), so the shelf reads at a glance and costs the page little. The
people and works tiles are mosaics of portraits and HOME icons; the timeline and
graph tiles are drawn. _includes/home-topics.html names the file for each entry.
"""
import io
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "img" / "topics"
W, H = 336, 192
UA = {"User-Agent": "pokeamice-docs/1.0 (docs.pokeamice.com; topic tiles)"}
CDN = "https://gallery.pokeamice.com/scan-archive/"
ICON = "https://pokeamice.com/game_gallery/icon/HOME_{}_icon.png"

# key -> source, and where in the picture to look (a focus point, 0-1) when it is cut to 7:4
TILES = {
    "director": ("assets/images/gamefreak-director/original/header-photo.png", (0.5, 0.5)),
    "staff": ("assets/images/gamefreak-legacy/staff/199/nyoro100917_01-09ebe8bb.jpg", (0.5, 0.45)),
    "art": ("assets/images/gamefreak-legacy/art/226/dred-240555b0.jpg", (0.5, 0.4)),
    "iwata": ("assets/img/interviews/2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-1/photo4.jpg", (0.55, 0.4)),
    "shudo": ("portrait:assets/img/people/shudo-takeshi.jpg", (0.5, 0.35)),
    "scan": (CDN + "shodai-zukan-1996-staff-interview/pages/p001_cover.jpg", (0.5, 0.3)),
    "ndream": (CDN + "ndream-2012-09-b2w2-developer-interview/pages/p001_cover.jpg", (0.5, 0.25)),
    "famitsu": ("assets/img/interviews/2019-06-13-interview-famitsu-e3-2019-pokemon-sword-shield-masuda-ohmori/001_5d0152e94fc60.jpg", (0.5, 0.4)),
    "dengeki": (CDN + "dengeki-games-vol14-bw-gamefreak-interview/pages/p001_cover.jpg", (0.5, 0.3)),
    "nom": ("sprite:assets/img/interviews/2000-07-01-interview-nom-gamefreak-roundtable-vol1-red-green/mew.png", (0.5, 0.5)),
    "gi": ("assets/img/interviews/2019-10-01-interview-gi-2019-dexit/001.webp", (0.5, 0.4)),
    "cedec": ("assets/img/interviews/2026-07-22-interview-cedec-2026-battle-system-deck/slide-06.jpg", (0.5, 0.5), (0.03, 0.02, 0.57, 0.36)),
    "tech": ("assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-01.jpg", (0.5, 0.5)),
    "recruit": ("assets/img/interviews/2017-tpc-recruit-passion/entry1.jpg", (0.5, 0.4)),
}
PEOPLE_MOSAIC = ["masuda-junichi", "sugimori-ken", "ishihara-tsunekazu", "tajiri-satoshi", "ohmori-shigeru", "unno-takao", "morimoto-shigeki", "kubo-masakazu"]
WORKS_MOSAIC = ["ball-red-green", "ball-gold-silver", "ball-ruby-sapphire", "ball-diamond-pearl", "black-white", "home-x", "home-sword", "home-scarlet"]   # assets/img/works (tools/build-work-icons.py)


def load(src):
    if src.startswith("http"):
        raw = urllib.request.urlopen(urllib.request.Request(src, headers=UA), timeout=120).read()
        return Image.open(io.BytesIO(raw)).convert("RGB")
    return Image.open(ROOT / src).convert("RGB")


def portrait(im):
    """A face on its own blurred, darkened enlargement - for a collection that is a person."""
    bg = im.resize((W, W), Image.LANCZOS).crop((0, (W - H) // 2, W, (W - H) // 2 + H)).filter(ImageFilter.GaussianBlur(14))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (20, 26, 34)), 0.55)
    face = im.resize((150, 150), Image.LANCZOS)
    mask = Image.new("L", (150, 150), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 149, 149), fill=255)
    bg.paste(face, (28, (H - 150) // 2), mask)
    return bg


def sprite(im, colour=(24, 38, 66)):
    """A transparent picture (a sprite, a logo) centred on a dark ground."""
    im = Image.open(im) if isinstance(im, str) else im
    im = im.convert("RGBA")
    im.thumbnail((W - 40, H - 24), Image.LANCZOS)
    bg = Image.new("RGB", (W, H), colour)
    d = ImageDraw.Draw(bg)
    for i in range(0, W, 24):
        d.line((i, 0, i, H), fill=(colour[0] + 8, colour[1] + 8, colour[2] + 10))
    bg.paste(im, ((W - im.width) // 2, (H - im.height) // 2), im)
    return bg


def cut(im, focus, box=None):
    """The 7:4 window of the picture around the focus point, scaled to the tile;
    `box` (fractions of the picture) restricts the search to part of it first."""
    if box:
        w, h = im.size
        im = im.crop((int(w * box[0]), int(h * box[1]), int(w * box[2]), int(h * box[3])))
    w, h = im.size
    if w / h > W / H:
        nh, nw = h, int(h * W / H)
    else:
        nw, nh = w, int(w * H / W)
    x0 = min(max(int(w * focus[0] - nw / 2), 0), w - nw)
    y0 = min(max(int(h * focus[1] - nh / 2), 0), h - nh)
    return im.crop((x0, y0, x0 + nw, y0 + nh)).resize((W, H), Image.LANCZOS)


def mosaic(images, cols=4):
    """A grid of squares filling the tile, softened so the title stays readable."""
    tile = Image.new("RGB", (W, H), (36, 44, 52))
    side = W // cols
    rows = (len(images) + cols - 1) // cols
    top = (H - rows * side) // 2
    for i, im in enumerate(images):
        sq = im.resize((side, side), Image.LANCZOS)
        tile.paste(sq, ((i % cols) * side, top + (i // cols) * side))
    return tile


def drawn(kind):
    tile = Image.new("RGB", (W, H), (30, 41, 59))
    d = ImageDraw.Draw(tile)
    if kind == "credits":
        # the staff matrix as it looks on /credits/staff/: rows of people, a column per game, a mark
        # coloured by department; columns fill in over the years the way the credits grew
        cols, rows = 14, 9
        cw, rh = W // cols, H // rows
        pal = [(246, 213, 213), (253, 233, 196), (214, 228, 247), (220, 239, 214), (232, 220, 245), (226, 232, 236)]
        for r in range(rows):
            for c in range(cols):
                # a deterministic scatter: more marks to the right (later games), fewer at the top-left
                v = ((r * 31 + c * 17) % 23) / 23
                if v > 0.25 + 0.45 * (1 - c / cols):
                    col = pal[(r * 5 + c * 3) % len(pal)]
                    d.rounded_rectangle((c * cw + 3, r * rh + 3, (c + 1) * cw - 3, (r + 1) * rh - 3), radius=3, fill=col)
        for c in range(cols):  # a faint column tint every other generation, like the table
            if (c // 2) % 2:
                d.rectangle((c * cw, 0, (c + 1) * cw, H), fill=None, outline=(38, 50, 70))
        return tile
    if kind == "timeline":
        import random
        random.seed(7)
        n = 24
        bw = W // n
        for i in range(n):
            bh = 20 + int(140 * (0.25 + 0.75 * abs(((i * 7) % 11) / 11 - 0.5) * 2) * (0.5 + random.random() / 2))
            d.rectangle((i * bw + 2, H - bh, (i + 1) * bw - 2, H), fill=(93 + i * 4, 140 + i * 3, 190))
    else:
        import math
        pts = [(W * (0.15 + 0.7 * ((i * 37) % 13) / 13), H * (0.18 + 0.64 * ((i * 53) % 11) / 11)) for i in range(14)]
        for i, a in enumerate(pts):
            for b in pts[i + 1:]:
                if math.dist(a, b) < 105:
                    d.line((a, b), fill=(84, 104, 126), width=2)
        for i, (x, y) in enumerate(pts):
            r = 5 + (i % 3) * 3
            d.ellipse((x - r, y - r, x + r, y + r), fill=(159, 215, 255) if i % 4 else (255, 196, 92))
    return tile


def save(tile, key):
    OUT.mkdir(parents=True, exist_ok=True)
    tile.save(OUT / f"{key}.jpg", quality=78, optimize=True, progressive=True)


def main():
    force = "--force" in sys.argv
    for key, spec in TILES.items():
        src, focus = spec[0], spec[1]
        box = spec[2] if len(spec) > 2 else None
        out = OUT / f"{key}.jpg"
        if out.exists() and not force:
            continue
        try:
            if src.startswith("portrait:"):
                tile = portrait(load(src[9:]))
            elif src.startswith("sprite:"):
                tile = sprite(str(ROOT / src[7:]))
            else:
                tile = cut(load(src), focus, box)
            save(tile, key)
            print(f"  {key:10s} <- {src[-60:]}")
        except Exception as exc:
            print(f"  !! {key}: {exc}")
    if force or not (OUT / "people.jpg").exists():
        ims = [Image.open(ROOT / "assets" / "img" / "people" / f"{s}.jpg").convert("RGB") for s in PEOPLE_MOSAIC if (ROOT / "assets" / "img" / "people" / f"{s}.jpg").exists()]
        save(mosaic(ims), "people"); print("  people     <- portraits")
    if force or not (OUT / "works.jpg").exists():
        ims = []
        for g in WORKS_MOSAIC:
            f = ROOT / "assets" / "img" / "works" / f"{g}.png"
            if f.exists():
                ims.append(Image.open(f).convert("RGBA").resize((76, 76), Image.LANCZOS))
        bg = Image.new("RGB", (W, H), (36, 44, 52))
        for i, im in enumerate(ims):
            bg.paste(im, (i % 4 * 84 + 4, (i // 4) * 84 + 16), im)
        save(bg, "works"); print("  works      <- the work icons")
    for key in ("timeline", "graph", "credits"):
        if force or not (OUT / f"{key}.jpg").exists():
            save(drawn(key), key); print(f"  {key:10s} <- drawn")
    print("tiles:", sorted(p.name for p in OUT.glob("*.jpg")))


if __name__ == "__main__":
    main()
