"""The size of every card cover, so the catalogue can lay a wide picture across the top of
its card and a tall one down the side, and know each card's height before the picture
arrives. Reads the cover of each post the way entry-card.html / catalogue-seed.html pick
it (image, else featured_image, else a scan's first plate, else a web interview's first
picture), measures it - a repo file from disk, a remote one over http - and writes
_data/covers.yml as  cover path -> [width, height].

    python tools/build-cover-dims.py            # measure the covers not yet in the file
    python tools/build-cover-dims.py --force    # measure them all again
    python tools/build-cover-dims.py --also /assets/img/x.jpg   # this path too (a cover the
                                                # committed post names while the working copy differs)
Covers once measured stay in the file, so a post whose cover changes keeps both known.
"""
import io
import re
import sys
import time
import urllib.request
from pathlib import Path

import yaml
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_data" / "covers.yml"
UA = {"User-Agent": "pokeamice-docs/1.0 (docs.pokeamice.com; cover sizes)"}
FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)


def front_matter(path):
    text = io.open(path, encoding="utf-8", errors="replace").read()
    m = FRONT.match(text)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        print(f"  ?? {path.name}: front matter does not parse ({str(e).splitlines()[0]})")
        return None


def first_image(items):
    for it in items or []:
        if isinstance(it, dict) and it.get("type") == "image" and it.get("image"):
            return it["image"]
    return None


def cover_of(fm):
    cover = fm.get("image") or fm.get("featured_image") or ""
    if isinstance(cover, dict):        # minimal-mistakes' header image object
        cover = cover.get("path") or cover.get("image") or ""
    if fm.get("translation_segments"):
        cover = first_image(fm["translation_segments"]) or cover
    elif not cover and fm.get("parallel_items"):
        cover = first_image(fm["parallel_items"]) or cover
    return cover if isinstance(cover, str) else ""


def measure(cover):
    if cover.startswith("http://") or cover.startswith("https://"):
        raw = urllib.request.urlopen(urllib.request.Request(cover, headers=UA), timeout=60).read()
        im = Image.open(io.BytesIO(raw))
    else:
        f = ROOT / cover.lstrip("/")
        if not f.exists():
            raise FileNotFoundError(cover)
        im = Image.open(f)
    return [im.width, im.height]


def main():
    force = "--force" in sys.argv
    known = {}
    if OUT.exists() and not force:
        known = yaml.safe_load(io.open(OUT, encoding="utf-8")) or {}
    covers = []
    for post in sorted((ROOT / "_posts").glob("*.md")):
        fm = front_matter(post)
        if not fm or fm.get("search") is False:
            continue
        c = cover_of(fm)
        if c and c not in covers:
            covers.append(c)
    for i, a in enumerate(sys.argv):
        if a == "--also" and i + 1 < len(sys.argv) and sys.argv[i + 1] not in covers:
            covers.append(sys.argv[i + 1])
    sizes = dict(known)          # what was measured before stays
    failed = []
    for c in covers:
        if c in known:
            sizes[c] = known[c]
            continue
        try:
            sizes[c] = measure(c)
            print(f"  {sizes[c][0]:5d} x {sizes[c][1]:<5d} {c[:96]}")
            if c.startswith("http"):
                time.sleep(0.2)
        except Exception as e:
            failed.append(c)
            print(f"  !! {c[:96]}: {e}")
    lines = [
        "# 卡片封面的尺寸：封面路径 -> [宽, 高]，由 tools/build-cover-dims.py 量出（导入带图的新帖后重跑一次）。",
        "# entry-card.html / catalogue-seed.html 用它决定横图铺在卡片上方、竖图立在左侧，并预先占好高度。",
    ]
    for c in sorted(sizes):
        w, h = sizes[c]
        lines.append(f"{yaml.safe_dump(c, allow_unicode=True, default_style=chr(34)).strip()}: [{w}, {h}]")
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    wide = sum(1 for w, h in sizes.values() if w > h * 1.15)
    print(f"covers.yml: {len(sizes)} covers ({wide} wide, {len(sizes) - wide} tall), {len(failed)} not measured")


if __name__ == "__main__":
    main()
