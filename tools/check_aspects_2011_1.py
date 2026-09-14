# -*- coding: utf-8 -*-
import os
import glob
from PIL import Image

folder = r"E:\Pokeamice\scan\DREAM 2011.1改\DREAM 2011.1改"
files = sorted(glob.glob(os.path.join(folder, "*.jpg")))

print(f"{'Filename':<12} | {'Width':<6} | {'Height':<6} | {'H/W Aspect':<10}")
print("-" * 45)
for f in files:
    fname = os.path.basename(f)
    with Image.open(f) as img:
        w, h = img.size
        print(f"{fname:<12} | {w:<6} | {h:<6} | {h/w:<10.3f}")
