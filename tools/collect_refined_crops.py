import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageOps

SOURCE_DIR = Path(r"E:\Pokeamice\scan\DREAM 2014.1")
TARGET_DIR = Path(r"E:\Pokeamice\scan\DREAM 2014.1_prepared")

with open(TARGET_DIR / "scan-manifest.json", encoding="utf-8") as f:
    manifest = json.load(f)

# Collect refined bounds
refined_crops = []

for p in manifest["pages"]:
    src = SOURCE_DIR / p["source_file"]
    raw_img = Image.open(src)
    raw_img = ImageOps.exif_transpose(raw_img).convert("RGB")
    arr = np.asarray(raw_img)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape
    side = p["spread_side"]

    # 1. Left/Right from current (which user praised as very perfect)
    left = p["crop_box"]["left"]
    right = p["crop_box"]["right"]

    # 2. Top & Bottom detection with 3070px physical constraint
    sobel_y_top = np.abs(cv2.Sobel(gray[0:450, 40:w-40], cv2.CV_32F, 0, 1, ksize=3))
    top_score = np.percentile(sobel_y_top, 90, axis=1) * 0.5 + np.mean(sobel_y_top, axis=1) * 0.5

    top_cands = []
    for y in range(60, 400):
        if top_score[y] > 15.0 and top_score[y] == max(top_score[max(0, y-8):min(len(top_score), y+9)]):
            top_cands.append((y, float(top_score[y])))
    top_cands.sort(key=lambda x: x[1], reverse=True)

    sobel_y_btm = np.abs(cv2.Sobel(gray[2950:3480, 40:w-40], cv2.CV_32F, 0, 1, ksize=3))
    btm_score = np.percentile(sobel_y_btm, 90, axis=1) * 0.5 + np.mean(sobel_y_btm, axis=1) * 0.5

    btm_cands = []
    for y_rel in range(20, len(btm_score) - 20):
        y_abs = 2950 + y_rel
        if btm_score[y_rel] > 15.0 and btm_score[y_rel] == max(btm_score[max(0, y_rel-8):min(len(btm_score), y_rel+9)]):
            btm_cands.append((y_abs, float(btm_score[y_rel])))
    btm_cands.sort(key=lambda x: x[1], reverse=True)

    best_pair = None
    best_err = 9999
    for ty, _ in top_cands:
        for by, _ in btm_cands:
            diff = by - ty
            if 3055 <= diff <= 3085:
                err = abs(diff - 3070)
                if err < best_err:
                    best_err = err
                    best_pair = (ty, by)

    if best_pair is not None:
        final_top, final_btm = best_pair
    else:
        # Fallback if pair not found: if top exists, btm = top + 3070; if btm exists, top = btm - 3070
        if top_cands:
            final_top = top_cands[0][0]
            final_btm = final_top + 3070
        elif btm_cands:
            final_btm = btm_cands[0][0]
            final_top = final_btm - 3070
        else:
            final_top = 210
            final_btm = 210 + 3070

    refined_crops.append({
        "stem": p["stem"],
        "src": p["source_file"],
        "page_no": p["magazine_page"],
        "side": side,
        "top": final_top,
        "bottom": final_btm,
        "left": left,
        "right": right,
        "height": final_btm - final_top,
        "width": right - left
    })

print(f"{'Stem':<18} {'Top':<6} {'Btm':<6} {'Height':<8} {'Left':<6} {'Right':<6}")
for rc in refined_crops:
    print(f"{rc['stem']:<18} {rc['top']:<6} {rc['bottom']:<6} {rc['height']:<8} {rc['left']:<6} {rc['right']:<6}")
