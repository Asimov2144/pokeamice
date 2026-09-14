# -*- coding: utf-8 -*-
import os
import glob
from PIL import Image

folder = r"E:\Pokeamice\scan\DREAM 2011.1改\DREAM 2011.1改"
files = sorted(glob.glob(os.path.join(folder, "*.jpg")))

scratch_dir = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334\scratch\2011_1_inspect"

# Let's inspect lower left and lower right of each page to find page numbers
ftr_crops = []
for f in files:
    fname = os.path.basename(f)
    base = os.path.splitext(fname)[0]
    with Image.open(f) as img:
        w, h = img.size
        # crop bottom 10%
        # left corner (even pages) and right corner (odd pages)
        ll = img.crop((0, int(h * 0.92), int(w * 0.2), h))
        lr = img.crop((int(w * 0.8), int(h * 0.92), w, h))
        
        # combine ll and lr side by side
        comb = Image.new("RGB", (ll.width + lr.width + 10, max(ll.height, lr.height)), (0, 0, 0))
        comb.paste(ll, (0, 0))
        comb.paste(lr, (ll.width + 10, 0))
        comb.save(os.path.join(scratch_dir, f"{base}_corners.jpg"), quality=85)

print("Saved corner crops.")
