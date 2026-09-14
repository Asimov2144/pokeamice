# -*- coding: utf-8 -*-
import os
import glob
from PIL import Image
import numpy as np

folder = r"E:\Pokeamice\scan\DREAM 2011.1改\DREAM 2011.1改"
files = sorted(glob.glob(os.path.join(folder, "*.jpg")))

print(f"Found {len(files)} files in {folder}")

info_list = []
for f in files:
    fname = os.path.basename(f)
    size_bytes = os.path.getsize(f)
    with Image.open(f) as img:
        w, h = img.size
        dpi = img.info.get('dpi', (None, None))
        aspect = h / w if w > 0 else 0
        info_list.append((fname, w, h, aspect, size_bytes, dpi))

print(f"{'Filename':<12} | {'Width':<6} | {'Height':<6} | {'Aspect':<6} | {'Size(MB)':<8} | {'DPI'}")
print("-" * 65)
for item in info_list:
    fname, w, h, aspect, size_bytes, dpi = item
    print(f"{fname:<12} | {w:<6} | {h:<6} | {aspect:<6.3f} | {size_bytes/(1024*1024):<8.2f} | {dpi}")

# Pairwise similarity comparison
print("\nChecking for duplicates or near-duplicates...")
thumbs = []
for f in files:
    with Image.open(f) as img:
        # thumbnail to 64x64 grayscale
        thumb = img.convert('L').resize((64, 64), Image.Resampling.BILINEAR)
        thumbs.append((os.path.basename(f), np.array(thumb, dtype=np.float32)))

for i in range(len(thumbs)):
    for j in range(i + 1, len(thumbs)):
        name1, arr1 = thumbs[i]
        name2, arr2 = thumbs[j]
        # MSE & MAE
        mae = np.mean(np.abs(arr1 - arr2))
        mse = np.mean((arr1 - arr2) ** 2)
        if mae < 15.0: # high similarity threshold
            print(f"Potential duplicate/variant: {name1} and {name2} (MAE: {mae:.2f}, MSE: {mse:.2f})")
