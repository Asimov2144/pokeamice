# -*- coding: utf-8 -*-
import os
import cv2
import json

src_dir = r"E:\Pokeamice\scan\Continue Vol.32"
files = sorted([f for f in os.listdir(src_dir) if f.endswith('.jpg')])

print(f"Total raw scan files in {src_dir}: {len(files)}")
for f in files:
    fp = os.path.join(src_dir, f)
    img = cv2.imread(fp)
    if img is None:
        print(f"{f}: Failed to read")
        continue
    h, w = img.shape[:2]
    aspect = w / float(h)
    page_type = "Spread (Double-page)" if aspect > 1.1 else "Single page"
    print(f"{f:14s} | {w:4d}x{h:4d} | aspect: {aspect:.2f} | {page_type}")
