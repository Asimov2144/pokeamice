# -*- coding: utf-8 -*-
import cv2
import os
import json
import time
import numpy as np

RAW_DIR = r"E:\Pokeamice\scan\DREAM 2011.5改\DREAM 2011.5改"
OUT_BASE = r"E:\Pokeamice\scan\DREAM 2011.5_prepared"
OUT_ARCHIVE = os.path.join(OUT_BASE, "archive")
OUT_WEB = os.path.join(OUT_BASE, "web")
BRAIN_DIR = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334"

os.makedirs(OUT_ARCHIVE, exist_ok=True)
os.makedirs(OUT_WEB, exist_ok=True)

def imread_unicode(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)

def imwrite_unicode(path, img, params=None):
    ext = os.path.splitext(path)[1]
    result, nparr = cv2.imencode(ext, img, params)
    if result:
        with open(path, "wb") as f:
            nparr.tofile(f)
        return True
    return False

PAGE_DEFS = [
    ("page001.jpg", "p001_cover", 1, "single", [18, 10, 2380, 3055]),
    ("page003.jpg", "p003_contents", 3, "odd", [100, 20, 2395, 3190]),
    ("page004.jpg", "p006_3ds_launch_akiba_shibuya", 6, "even", [18, 45, 2335, 3117]),
    ("page005.jpg", "p007_3ds_launch_report_muscle", 7, "odd", [95, 100, 2315, 3172]),
    ("page006.jpg", "p064_pokemon_typing_ds_intro", 64, "even", [18, 4, 2270, 3070]),
    ("page007.jpg", "p065_pokemon_typing_ds_details", 65, "odd", [95, 4, 2338, 3068]),
    ("page008.jpg", "p069_bw_special_interview_intro", 69, "odd", [95, 4, 2322, 3050]),
    ("page009.jpg", "p070_bw_interview_elite4_grimsley_shauntal", 70, "even", [18, 4, 2295, 3060]),
    ("page010.jpg", "p071_bw_interview_elite4_marshal_caitlin", 71, "odd", [95, 15, 2346, 3080]),
    ("page011.jpg", "p072_bw_interview_forces_of_nature_mienshao", 72, "even", [18, 4, 2320, 3060]),
    ("page012.jpg", "p073_bw_interview_hydreigon_throh_sawk", 73, "odd", [95, 4, 2323, 3060]),
    ("page013.jpg", "p074_bw_interview_golurk_heatmor_durant", 74, "even", [18, 5, 2315, 3077]),
    ("page015.jpg", "p075_bw_interview_braviary_mandibuzz_eelektross", 75, "odd", [95, 4, 2394, 3065]),
    ("page017.jpg", "p076_bw_interview_amoonguss_ferrothorn_basculin", 76, "even", [18, 15, 2320, 3080]),
    ("page018.jpg", "p077_bw_interview_team_plasma_sages_aftermath", 77, "odd", [95, 4, 2367, 3064]),
    ("page019.jpg", "p078_bw_poll_unova_pokemon_000_054", 78, "even", [18, 20, 2310, 3085]),
    ("page021.jpg", "p079_bw_poll_unova_pokemon_055_108", 79, "odd", [95, 20, 2380, 3090]),
    ("page023.jpg", "p080_bw_poll_unova_pokemon_109_155", 80, "even", [18, 4, 2290, 3055]),
    ("page024.jpg", "p081_bw_poll_characters_01_32", 81, "odd", [95, 8, 2338, 3080]),
    ("page025.jpg", "p082_ohmura_character_making_special_1", 82, "even", [18, 5, 2325, 3077]),
    ("page026.jpg", "p083_ohmura_character_making_special_2", 83, "odd", [95, 4, 2330, 3060]),
    ("page027.jpg", "p084_ohmura_character_making_special_3", 84, "even", [18, 4, 2315, 3064]),
    ("page029.jpg", "p085_pokemon_do_united_tower_movie", 85, "odd", [95, 4, 2382, 3060]),
    ("page030.jpg", "p118_nintendo_paris_report_michael_jackson", 118, "even", [18, 20, 2300, 3095]),
    ("page031.jpg", "p999_back_cover_famista_2011", 999, "single", [18, 4, 2315, 3065]),
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
    "issue": "2011.5",
    "vol": 205,
    "processed_date": time.strftime("%Y-%m-%d"),
    "total_pages": len(PAGE_DEFS),
    "pages": []
}

archive_crops = []

print(f"Starting batch production for {len(PAGE_DEFS)} pages...")

for idx, (raw_name, stem, pnum, ptype, (x1, y1, x2, y2)) in enumerate(PAGE_DEFS):
    raw_path = os.path.join(RAW_DIR, raw_name)
    raw_img = imread_unicode(raw_path)
    if raw_img is None:
        raise ValueError(f"Could not load image: {raw_path}")
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
    imwrite_unicode(arc_path, enhanced, [cv2.IMWRITE_JPEG_QUALITY, 92])
    
    # Web scale: target height 2048px
    target_web_h = 2048
    target_web_w = int(round(cw * (target_web_h / float(ch))))
    web_img = cv2.resize(enhanced, (target_web_w, target_web_h), interpolation=cv2.INTER_AREA)
    web_name = f"{stem}.jpg"
    web_path = os.path.join(OUT_WEB, web_name)
    imwrite_unicode(web_path, web_img, [cv2.IMWRITE_JPEG_QUALITY, 84])
    
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
# 1. All overview: 25 pages in 5 rows x 5 columns
thumb_h = 320
thumb_w = 240
grid_thumbs = []
for stem, img in archive_crops:
    t = cv2.resize(img, (thumb_w, thumb_h), interpolation=cv2.INTER_AREA)
    cv2.putText(t, stem, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
    grid_thumbs.append(t)

rows = [np.hstack(grid_thumbs[r*5 : (r+1)*5]) for r in range(5)]
grid_all = np.vstack(rows)
imwrite_unicode(os.path.join(BRAIN_DIR, "dream_2011_5_prepared_all.jpg"), grid_all, [cv2.IMWRITE_JPEG_QUALITY, 85])

# 2. Top headers strip (25 items: 13 in col1, 12 + 1 blank in col2)
header_h = 70
header_w = 800
top_strips = []
for stem, img in archive_crops:
    crop_top = img[:150, :]
    strip = cv2.resize(crop_top, (header_w, header_h), interpolation=cv2.INTER_AREA)
    cv2.putText(strip, stem, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    top_strips.append(strip)

blank_top = np.zeros((header_h, header_w, 3), dtype=np.uint8)
top_strips_padded = top_strips + [blank_top]
c1 = np.vstack(top_strips_padded[:13])
c2 = np.vstack(top_strips_padded[13:])
top_grid = np.hstack([c1, c2])
imwrite_unicode(os.path.join(BRAIN_DIR, "dream_2011_5_prepared_top.jpg"), top_grid, [cv2.IMWRITE_JPEG_QUALITY, 85])

# 3. Bottom footers strip (25 items: 13 in col1, 12 + 1 blank in col2)
footer_h = 70
footer_w = 800
btm_strips = []
for stem, img in archive_crops:
    crop_btm = img[img.shape[0]-150:, :]
    strip = cv2.resize(crop_btm, (footer_w, footer_h), interpolation=cv2.INTER_AREA)
    cv2.putText(strip, stem, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    btm_strips.append(strip)

blank_btm = np.zeros((footer_h, footer_w, 3), dtype=np.uint8)
btm_strips_padded = btm_strips + [blank_btm]
b1 = np.vstack(btm_strips_padded[:13])
b2 = np.vstack(btm_strips_padded[13:])
btm_grid = np.hstack([b1, b2])
imwrite_unicode(os.path.join(BRAIN_DIR, "dream_2011_5_prepared_btm.jpg"), btm_grid, [cv2.IMWRITE_JPEG_QUALITY, 85])

print("All contact sheets generated in brain directory!")
