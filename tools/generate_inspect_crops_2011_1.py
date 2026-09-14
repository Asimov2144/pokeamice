# -*- coding: utf-8 -*-
import os
import glob
from PIL import Image

folder = r"E:\Pokeamice\scan\DREAM 2011.1改\DREAM 2011.1改"
files = sorted(glob.glob(os.path.join(folder, "*.jpg")))

scratch_dir = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334\scratch\2011_1_inspect"
os.makedirs(scratch_dir, exist_ok=True)

# Generate small contact thumbnails (e.g. 400px width)
for f in files:
    fname = os.path.basename(f)
    with Image.open(f) as img:
        w, h = img.size
        # header crop
        hdr = img.crop((0, 0, w, int(h * 0.15)))
        hdr.save(os.path.join(scratch_dir, f"{os.path.splitext(fname)[0]}_hdr.jpg"), quality=80)
        # footer crop
        ftr = img.crop((0, int(h * 0.85), w, h))
        ftr.save(os.path.join(scratch_dir, f"{os.path.splitext(fname)[0]}_ftr.jpg"), quality=80)
        # thumbnail
        thumb = img.resize((400, int(400 * h / w)), Image.Resampling.LANCZOS)
        thumb.save(os.path.join(scratch_dir, f"{os.path.splitext(fname)[0]}_thumb.jpg"), quality=80)

print(f"Generated inspection crops in {scratch_dir}")
