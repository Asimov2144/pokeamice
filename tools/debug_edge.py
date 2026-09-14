from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageOps

SOURCE_DIR = Path(r"E:\Pokeamice\scan\DREAM 2014.1")

test_files = [
    ("page001.jpg", "p001_cover"),
    ("page004.jpg", "p006_mega"),
    ("page008.jpg", "p008_mega"),
    ("page010.jpg", "p010_mega"),
    ("page011.jpg", "p011_walkthrough"),
    ("page016.jpg", "p016_lumiose"),
    ("page022.jpg", "p020_interview"),
    ("page024.jpg", "p022_interview"),
    ("page030.jpg", "p126_ranking"),
]

for src_name, stem in test_files:
    src_path = SOURCE_DIR / src_name
    raw_img = Image.open(src_path)
    raw_img = ImageOps.exif_transpose(raw_img).convert("RGB")
    raw_arr = np.asarray(raw_img)
    gray = cv2.cvtColor(raw_arr, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape

    # Let's inspect the entire vertical profile:
    # Look at row means across middle 50%
    mid_strip = gray[:, int(w * 0.3):int(w * 0.7)]
    sobel_y = np.abs(cv2.Sobel(mid_strip, cv2.CV_32F, 0, 1, ksize=3))
    row_grad = np.mean(sobel_y, axis=1)

    # Top search: 50 to 450
    top_candidates = []
    for y in range(50, 450):
        if row_grad[y] > 6.0:
            top_candidates.append((y, row_grad[y]))
    top_candidates.sort(key=lambda x: x[1], reverse=True)

    # Bottom search: h - 500 to h - 50
    btm_candidates = []
    for y in range(h - 500, h - 50):
        if row_grad[y] > 6.0:
            btm_candidates.append((y, row_grad[y]))
    btm_candidates.sort(key=lambda x: x[1], reverse=True)

    top_best = top_candidates[0] if top_candidates else (0, 0)
    btm_best = btm_candidates[0] if btm_candidates else (h - 1, 0)

    print(f"{stem:<18} H={h} Top: {top_best} (top 3: {top_candidates[:3]}), Btm: {btm_best} (top 3: {btm_candidates[:3]})")
