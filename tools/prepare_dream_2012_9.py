# -*- coding: utf-8 -*-
import cv2
import os
import json
import time
import numpy as np

RAW_DIR = r"E:\Pokeamice\scan\DREAM 2012.9"
OUT_BASE = r"E:\Pokeamice\scan\DREAM 2012.9_prepared"
OUT_ARCHIVE = os.path.join(OUT_BASE, "archive")
OUT_WEB = os.path.join(OUT_BASE, "web")
BRAIN_DIR = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334"

os.makedirs(OUT_ARCHIVE, exist_ok=True)
os.makedirs(OUT_WEB, exist_ok=True)

PAGE_DEFS = [
    ("page001.jpg", "p001_cover", 1, "single", [18, 22, 2465, 3094]),
    ("page003.jpg", "p003_contents", 3, "odd", [110, 6, 2401, 3078]),
    ("page004.jpg", "p012_b2w2_interview_intro", 12, "even", [18, 6, 2339, 3078]),
    ("page006.jpg", "p013_b2w2_interview_unno", 13, "odd", [110, 4, 2355, 3076]),
    ("page008.jpg", "p014_b2w2_interview_masuda", 14, "even", [18, 4, 2314, 3076]),
    ("page009.jpg", "p015_b2w2_interview_legendary", 15, "odd", [110, 4, 2353, 3076]),
    ("page010.jpg", "p016_b2w2_interview_sound", 16, "even", [18, 4, 2325, 3076]),
    ("page012.jpg", "p017_b2w2_guide_new_elements", 17, "odd", [110, 7, 2375, 3079]),
    ("page013.jpg", "p054_palutena_special_intro", 54, "even", [18, 58, 2330, 3130]),
    ("page014.jpg", "p055_palutena_questionnaire_1", 55, "odd", [110, 4, 2305, 3076]),
    ("page015.jpg", "p056_palutena_questionnaire_2", 56, "even", [18, 82, 2330, 3154]),
    ("page017.jpg", "p057_palutena_qa_1", 57, "odd", [100, 52, 2360, 3124]),
    ("page018.jpg", "p058_palutena_qa_2", 58, "even", [18, 4, 2257, 3069]),
    ("page019.jpg", "p059_palutena_qa_3", 59, "odd", [110, 6, 2286, 3078]),
    ("page020.jpg", "p060_palutena_dialogue_sakurai_hirabayashi_1", 60, "even", [18, 4, 2322, 3075]),
    ("page021.jpg", "p061_palutena_dialogue_sakurai_hirabayashi_2", 61, "odd", [110, 5, 2273, 3077]),
    ("page022.jpg", "p062_palutena_dialogue_sakurai_hirabayashi_3", 62, "even", [18, 4, 2325, 3076]),
    ("page023.jpg", "p063_palutena_dialogue_sakurai_hirabayashi_4", 63, "odd", [110, 4, 2275, 3074]),
    ("page024.jpg", "p064_gakkyoku_damashii_palutena_1", 64, "even", [18, 5, 2265, 3077]),
    ("page025.jpg", "p065_gakkyoku_damashii_palutena_2", 65, "odd", [110, 7, 2269, 3079]),
    ("page026.jpg", "p072_pokemon_next_genesect", 72, "even", [18, 7, 2259, 3079]),
    ("page027.jpg", "p073_pokemon_next_tetta", 73, "odd", [110, 11, 2275, 3083]),
    ("page028.jpg", "p126_sales_ranking", 126, "even", [18, 60, 2330, 3135]),
    ("page029.jpg", "p999_back_cover", 999, "single", [18, 4, 2380, 3075]),
]

def enhance_image(img, p_low=0.4, p_high=99.1):
    out = np.empty_like(img)
    for c in range(3):
        ch = img[:, :, c]
        v_low = np.percentile(ch, p_low)
        v_high = np.percentile(ch, p_high)
        if v_high > v_low:
            scaled = (ch.astype(np.float32) - v_low) * (255.0 / (v_high - v_low))
            out[:, :, c] = np.clip(scaled, 0, 255).astype(np.uint8)
        else:
            out[:, :, c] = ch
            
    # Unsharp mask
    blur = cv2.GaussianBlur(out, (0, 0), sigmaX=1.0)
    enhanced = cv2.addWeighted(out, 1.35, blur, -0.35, 0)
    return enhanced

manifest = {
    "magazine": "Nintendo DREAM",
    "issue": "2012.9",
    "vol": 221,
    "processed_date": time.strftime("%Y-%m-%d"),
    "total_pages": len(PAGE_DEFS),
    "pages": []
}

archive_crops = []

print(f"Starting batch production for {len(PAGE_DEFS)} pages...")

for idx, (raw_name, stem, pnum, ptype, (x1, y1, x2, y2)) in enumerate(PAGE_DEFS):
    raw_path = os.path.join(RAW_DIR, raw_name)
    raw_img = cv2.imread(raw_path)
    h_raw, w_raw = raw_img.shape[:2]
    
    # 2x supersampling to 300 DPI
    img_300 = cv2.resize(raw_img, (w_raw // 2, h_raw // 2), interpolation=cv2.INTER_AREA)
    
    # Crop
    cropped = img_300[y1:y2, x1:x2]
    ch, cw = cropped.shape[:2]
    
    # Color enhancement & unsharp mask
    enhanced = enhance_image(cropped)
    
    # Save archive (300 DPI, Quality 92)
    arc_name = f"{stem}.jpg"
    arc_path = os.path.join(OUT_ARCHIVE, arc_name)
    cv2.imwrite(arc_path, enhanced, [cv2.IMWRITE_JPEG_QUALITY, 92])
    
    # Web scale: target height 2048px
    target_web_h = 2048
    target_web_w = int(round(cw * (target_web_h / float(ch))))
    web_img = cv2.resize(enhanced, (target_web_w, target_web_h), interpolation=cv2.INTER_AREA)
    web_name = f"{stem}.jpg"
    web_path = os.path.join(OUT_WEB, web_name)
    cv2.imwrite(web_path, web_img, [cv2.IMWRITE_JPEG_QUALITY, 84])
    
    manifest["pages"].append({
        "order": idx + 1,
        "magazine_page": pnum,
        "type": ptype,
        "raw_file": raw_name,
        "filename": arc_name,
        "crop_box_300dpi": [x1, y1, x2, y2],
        "archive_size": [cw, ch],
        "web_size": [target_web_w, target_web_h]
    })
    
    archive_crops.append((stem, enhanced))
    print(f"[{idx+1}/{len(PAGE_DEFS)}] {arc_name} done: {cw}x{ch} -> web: {target_web_w}x{target_web_h}")

# Save manifest
with open(os.path.join(OUT_BASE, "scan-manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("scan-manifest.json written!")

# Generate contact sheets
print("Generating contact sheets...")
# 1. All overview: 24 pages in 4 rows x 6 columns
thumb_h = 320
thumb_w = 240
grid_thumbs = []
for stem, img in archive_crops:
    t = cv2.resize(img, (thumb_w, thumb_h), interpolation=cv2.INTER_AREA)
    cv2.putText(t, stem, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    grid_thumbs.append(t)

rows = [np.hstack(grid_thumbs[r*6 : (r+1)*6]) for r in range(4)]
grid_all = np.vstack(rows)
cv2.imwrite(os.path.join(BRAIN_DIR, "dream_2012_9_prepared_all.jpg"), grid_all, [cv2.IMWRITE_JPEG_QUALITY, 85])

# 2. Top headers strip (24 rows, height 70)
header_h = 70
header_w = 800
top_strips = []
for stem, img in archive_crops:
    crop_top = img[:150, :]
    strip = cv2.resize(crop_top, (header_w, header_h), interpolation=cv2.INTER_AREA)
    cv2.putText(strip, stem, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    top_strips.append(strip)

# stack 2 cols of 12
c1 = np.vstack(top_strips[:12])
c2 = np.vstack(top_strips[12:])
top_grid = np.hstack([c1, c2])
cv2.imwrite(os.path.join(BRAIN_DIR, "dream_2012_9_prepared_top.jpg"), top_grid, [cv2.IMWRITE_JPEG_QUALITY, 85])

# 3. Bottom footers strip (24 rows, height 70)
footer_h = 70
footer_w = 800
btm_strips = []
for stem, img in archive_crops:
    crop_btm = img[img.shape[0]-150:, :]
    strip = cv2.resize(crop_btm, (footer_w, footer_h), interpolation=cv2.INTER_AREA)
    cv2.putText(strip, stem, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    btm_strips.append(strip)

b1 = np.vstack(btm_strips[:12])
b2 = np.vstack(btm_strips[12:])
btm_grid = np.hstack([b1, b2])
cv2.imwrite(os.path.join(BRAIN_DIR, "dream_2012_9_prepared_btm.jpg"), btm_grid, [cv2.IMWRITE_JPEG_QUALITY, 85])

print("All contact sheets generated in brain directory!")
