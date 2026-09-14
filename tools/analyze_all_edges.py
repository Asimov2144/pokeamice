import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageOps

SOURCE_DIR = Path(r"E:\Pokeamice\scan\DREAM 2014.1")
TARGET_DIR = Path(r"E:\Pokeamice\scan\DREAM 2014.1_prepared")

with open(TARGET_DIR / "scan-manifest.json", encoding="utf-8") as f:
    manifest = json.load(f)

print(f"{'Stem':<18} {'Src':<12} {'CurrTop':<8} {'CurrBtm':<8} {'CurrH':<8} {'TopPeaks':<25} {'BtmPeaks':<25}")

for p in manifest["pages"]:
    src = SOURCE_DIR / p["source_file"]
    raw_img = Image.open(src)
    raw_img = ImageOps.exif_transpose(raw_img).convert("RGB")
    arr = np.asarray(raw_img)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape

    # Check top
    top_zone = gray[0:450, int(w * 0.05):int(w * 0.95)]
    top_sobel = np.abs(cv2.Sobel(top_zone, cv2.CV_32F, 0, 1, ksize=3))
    row_top = np.mean(top_sobel, axis=1)

    # find prominent peaks in top_zone
    top_peaks = []
    for y in range(40, 420):
        if row_top[y] > 5.0 and row_top[y] == max(row_top[max(0, y-10):min(len(row_top), y+11)]):
            top_peaks.append((y, float(row_top[y])))
    top_peaks.sort(key=lambda x: x[1], reverse=True)

    # Check bottom
    btm_zone = gray[h-600:h, int(w * 0.05):int(w * 0.95)]
    btm_sobel = np.abs(cv2.Sobel(btm_zone, cv2.CV_32F, 0, 1, ksize=3))
    row_btm = np.mean(btm_sobel, axis=1)

    btm_peaks = []
    for y_rel in range(20, 580):
        y_abs = h - 600 + y_rel
        if row_btm[y_rel] > 5.0 and row_btm[y_rel] == max(row_btm[max(0, y_rel-10):min(len(row_btm), y_rel+11)]):
            btm_peaks.append((y_abs, float(row_btm[y_rel])))
    btm_peaks.sort(key=lambda x: x[1], reverse=True)

    cur_t = p["crop_box"]["top"]
    cur_b = p["crop_box"]["bottom"]
    cur_h = p["crop_box"]["cropped_height"]

    top_str = str([(y, round(v, 1)) for y, v in top_peaks[:3]])
    btm_str = str([(y, round(v, 1)) for y, v in btm_peaks[:3]])

    print(f"{p['stem']:<18} {p['source_file']:<12} {cur_t:<8} {cur_b:<8} {cur_h:<8} {top_str:<25} {btm_str:<25}")
