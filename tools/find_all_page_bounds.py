import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageOps

SOURCE_DIR = Path(r"E:\Pokeamice\scan\DREAM 2014.1")
TARGET_DIR = Path(r"E:\Pokeamice\scan\DREAM 2014.1_prepared")

with open(TARGET_DIR / "scan-manifest.json", encoding="utf-8") as f:
    manifest = json.load(f)

print(f"{'Page':<18} {'Src':<12} {'Top_Sobel':<10} {'Btm_Sobel':<10} {'Diff':<8} {'Top_L/R':<10} {'Btm_L/R':<10}")

for p in manifest["pages"]:
    src = SOURCE_DIR / p["source_file"]
    raw_img = Image.open(src)
    raw_img = ImageOps.exif_transpose(raw_img).convert("RGB")
    arr = np.asarray(raw_img)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape

    # 1. Top edge detection:
    # Page paper starts somewhere between y=50 and y=420.
    # Across full width (excluding extreme 20px margins):
    # The scanner platen above the page is either dark or white, but there is a horizontal cut line across the page!
    # Let's compute horizontal gradient using Sobel on y
    sobel_y_top = np.abs(cv2.Sobel(gray[0:450, 40:w-40], cv2.CV_32F, 0, 1, ksize=3))
    # Look at row-wise gradient:
    # We can look at mean across columns, but also 90th percentile to catch edges that are distinct on either left, mid or right
    top_p90 = np.percentile(sobel_y_top, 90, axis=1)
    top_mean = np.mean(sobel_y_top, axis=1)
    # Combined score
    top_score = top_p90 * 0.5 + top_mean * 0.5

    # Filter top candidate range: y in [60, 400]
    top_candidates = []
    for y in range(60, 400):
        if top_score[y] > 15.0 and top_score[y] == max(top_score[max(0, y-8):min(len(top_score), y+9)]):
            top_candidates.append((y, top_score[y]))
    top_candidates.sort(key=lambda x: x[1], reverse=True)

    # 2. Bottom edge detection:
    # Page paper ends somewhere between y=2980 and y=3450.
    sobel_y_btm = np.abs(cv2.Sobel(gray[2950:3480, 40:w-40], cv2.CV_32F, 0, 1, ksize=3))
    btm_p90 = np.percentile(sobel_y_btm, 90, axis=1)
    btm_mean = np.mean(sobel_y_btm, axis=1)
    btm_score = btm_p90 * 0.5 + btm_mean * 0.5

    btm_candidates = []
    for y_rel in range(20, len(btm_score) - 20):
        y_abs = 2950 + y_rel
        if btm_score[y_rel] > 15.0 and btm_score[y_rel] == max(btm_score[max(0, y_rel-8):min(len(btm_score), y_rel+9)]):
            btm_candidates.append((y_abs, btm_score[y_rel]))
    btm_candidates.sort(key=lambda x: x[1], reverse=True)

    best_pair = None
    best_diff_error = 9999
    # Let's search pairs where B - T is close to 3070 (e.g. 3060 to 3080)
    for ty, tscore in top_candidates:
        for by, bscore in btm_candidates:
            diff = by - ty
            if 3055 <= diff <= 3085:
                err = abs(diff - 3070)
                if err < best_diff_error:
                    best_diff_error = err
                    best_pair = (ty, by, diff)

    top_cand_str = f"{top_candidates[0][0]}" if top_candidates else "None"
    btm_cand_str = f"{btm_candidates[0][0]}" if btm_candidates else "None"
    pair_str = f"T={best_pair[0]}, B={best_pair[1]}, H={best_pair[2]}" if best_pair else "NO PAIR"

    print(f"{p['stem']:<18} {p['source_file']:<12} {pair_str:<25} (Top={top_cand_str}, Btm={btm_cand_str})")
