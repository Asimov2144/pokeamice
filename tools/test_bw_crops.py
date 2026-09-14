# -*- coding: utf-8 -*-
"""
Test crop script for 黑白 诞生秘话
"""
import os
import cv2
import numpy as np

SRC_DIR = r"E:\Pokeamice\scan\黑白 诞生秘话"
BRAIN_DIR = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334"

# We test:
# Cover (page004.jpg) - single
# P.3 (page005.jpg) - odd
# P.4 (page006.jpg) - even
# P.5 (page007.jpg) - odd
# P.14 (page016.jpg) - even
# P.15 (page018.jpg) - odd
# P.46 (page049.jpg) - even (Submas & Alder)
# Back (page055.jpg) - single

test_specs = [
    ("page004.jpg", 1,   "single", 246, 3313, "p001_cover"),
    ("page005.jpg", 3,   "odd",    329, 3399, "p003_contents"),
    ("page006.jpg", 4,   "even",   201, 3274, "p004_poll_pokemon_top10_part1"),
    ("page007.jpg", 5,   "odd",    262, 3343, "p005_poll_pokemon_top10_part2"),
    ("page016.jpg", 14,  "even",   197, 3271, "p014_chandelure"),
    ("page018.jpg", 15,  "odd",    182, 3265, "p015_whimsicott_reshiram"),
    ("page049.jpg", 46,  "even",   221, 3292, "p046_submas_alder"),
    ("page055.jpg", 999, "single", 182, 3246, "p999_back_cover"),
]

def enhance_img(cropped):
    p_low = np.percentile(cropped, 0.4)
    p_high = np.percentile(cropped, 99.2)
    stretched = np.clip((cropped.astype(np.float32) - p_low) * (255.0 / max(1.0, p_high - p_low)), 0, 255).astype(np.uint8)
    blur = cv2.GaussianBlur(stretched, (0, 0), 1.0)
    sharpened = cv2.addWeighted(stretched, 1.15, blur, -0.15, 0)
    return sharpened

for src_file, pnum, side, tp, bp, stem in test_specs:
    raw_path = os.path.join(SRC_DIR, src_file)
    raw = cv2.imdecode(np.fromfile(raw_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    h600, w600 = raw.shape[:2]
    im300 = cv2.resize(raw, (int(round(w600 * 0.5)), int(round(h600 * 0.5))), interpolation=cv2.INTER_AREA)
    h300, w300 = im300.shape[:2]
    
    if side == "even":
        left = 18
        right = w300 - 140
    elif side == "odd":
        left = 115
        right = w300 - 18
    else: # single
        left = 18
        right = w300 - 18
        
    cropped = im300[tp:bp, left:right]
    enhanced = enhance_img(cropped)
    
    # Save preview at height 1200
    ch, cw = enhanced.shape[:2]
    prev_w = int(round(cw * (1200 / float(ch))))
    preview = cv2.resize(enhanced, (prev_w, 1200), interpolation=cv2.INTER_AREA)
    
    out_path = os.path.join(BRAIN_DIR, f"preview_calib_{stem}.jpg")
    cv2.imwrite(out_path, preview)
    print(f"{stem}: crop [{left}, {tp}, {right}, {bp}] -> size {cw}x{ch} (prev {prev_w}x1200)")

print("Done generating test calibration previews!")
