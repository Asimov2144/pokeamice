"""Recompress the interview pictures in place: same path, same format, same pixel size.

    python tools/compress-images.py            # dry run: what would change and by how much
    python tools/compress-images.py --write    # rewrite the files that pass

Why the size must not change: the people library cuts portraits out of these pictures by pixel boxes
(tools/build-people.py PORTRAITS), and the scan reader's boxes are relative to the picture; the App reads the same
files by the same paths. So nothing is resized or renamed - a PNG photograph stays a PNG (only lossless here).

  JPEG  re-encoded at QUALITY (progressive, optimised; the ICC profile and EXIF - orientation included - kept),
        only when the original is bigger than MIN_BYTES and the new file is at least MIN_SAVING smaller. A picture
        already saved at about QUALITY or below gains little and would only lose a generation, so the saving
        threshold leaves it alone.
  PNG   re-saved losslessly with optimize=True, kept only if smaller by MIN_SAVING. Palette and alpha untouched.

The originals stay in git history (git show <commit>^:<path> brings one back).
"""
import argparse
import io
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DIRS = [ROOT / "assets" / "img" / "interviews"]
QUALITY = 82
MIN_BYTES = 200_000
MIN_SAVING = 0.20


def recompress(path):
    path = Path(path)
    old = path.stat().st_size
    if old < MIN_BYTES:
        return None
    try:
        im = Image.open(path)
        fmt = im.format
        info = dict(im.info)
        size = im.size
        buf = io.BytesIO()
        if fmt == "JPEG":
            if im.mode not in ("RGB", "L", "CMYK"):
                return (str(path), old, old, "skip-mode-" + im.mode)
            kw = {"quality": QUALITY, "optimize": True, "progressive": True}
            if info.get("icc_profile"):
                kw["icc_profile"] = info["icc_profile"]
            if info.get("exif"):
                kw["exif"] = info["exif"]
            im.save(buf, "JPEG", **kw)
        elif fmt == "PNG":
            if getattr(im, "is_animated", False):
                return (str(path), old, old, "skip-animated")
            kw = {"optimize": True}
            for k in ("transparency", "icc_profile", "dpi"):
                if k in info:
                    kw[k] = info[k]
            im.save(buf, "PNG", **kw)
        else:
            return (str(path), old, old, "skip-" + str(fmt))
        new = buf.tell()
        if new > old * (1 - MIN_SAVING):
            return (str(path), old, new, "keep")
        check = Image.open(io.BytesIO(buf.getvalue()))
        if check.size != size:
            return (str(path), old, new, "size-changed")
        return (str(path), old, new, "write", buf.getvalue())
    except Exception as e:  # noqa: BLE001 - a broken file is reported, not fatal
        return (str(path), old, old, "error " + str(e)[:60])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    files = [p for d in DIRS for p in d.rglob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png") and p.is_file()]
    stats = {}
    old_all = new_all = 0
    written = 0
    with ProcessPoolExecutor(max(1, (os.cpu_count() or 2) - 2)) as ex:
        for r in ex.map(recompress, files, chunksize=8):
            if r is None:
                continue
            path, old, new, what = r[:4]
            key = (Path(path).suffix.lower().replace(".jpeg", ".jpg"), what.split(" ")[0])
            s = stats.setdefault(key, [0, 0, 0])
            s[0] += 1
            s[1] += old
            s[2] += new
            if what == "write":
                old_all += old
                new_all += new
                if args.write:
                    tmp = Path(path + ".tmp")
                    tmp.write_bytes(r[4])
                    os.replace(tmp, path)
                    written += 1
            elif what.startswith(("error", "size")):
                print("  !", what, path)
    for (ext, what), (n, o, nw) in sorted(stats.items()):
        print(f"  {ext:5s} {what:12s} {n:5d} files  {o / 1e6:7.1f} MB -> {nw / 1e6:7.1f} MB")
    print(f"{'wrote' if args.write else 'would write'} {written if args.write else sum(v[0] for k, v in stats.items() if k[1] == 'write')} files: "
          f"{old_all / 1e6:.1f} MB -> {new_all / 1e6:.1f} MB (saves {(old_all - new_all) / 1e6:.1f} MB)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
