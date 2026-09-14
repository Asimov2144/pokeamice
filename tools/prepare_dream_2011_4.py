# -*- coding: utf-8 -*-
import cv2
import os
import json
import time
import numpy as np

RAW_DIR = r"E:\Pokeamice\scan\DREAM 2011.4改\DREAM 2011.4改"
OUT_BASE = r"E:\Pokeamice\scan\DREAM 2011.4_prepared"
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

# 16 unique pages (excluding duplicate page010.jpg)
PAGE_DEFS = [
    ("page002.jpg", "p001_cover", 1, "single", [20, 20, 2460, 3085], False),
    ("page004.jpg", "p003_contents", 3, "odd", [95, 10, 2410, 3075], False),
    ("page006.jpg", "p071_bw_interview_part2_intro", 71, "odd", [95, 5, 2375, 3070], False),
    ("page007.jpg", "p072_bw_interview_swords_of_justice", 72, "even", [18, 5, 2315, 3068], True), # un-stretch Y to 3072
    ("page008.jpg", "p073_bw_interview_volcarona_whimsicott_lilligant", 73, "odd", [95, 15, 2395, 3080], False),
    ("page009.jpg", "p074_bw_interview_haxorus_darmanitan_stunfisk", 74, "even", [18, 4, 2305, 3068], False),
    ("page012.jpg", "p075_bw_interview_jellicent_sawsbuck", 75, "odd", [95, 25, 2385, 3090], False),
    ("page013.jpg", "p076_bw_interview_chandelure_seismitoad_klinklang", 76, "even", [18, 20, 2305, 3085], False),
    ("page014.jpg", "p077_bw_interview_crustle_scrafty_cofagrigus_bisharp", 77, "odd", [95, 4, 2335, 3060], False),
    ("page015.jpg", "p078_bw_interview_characters_drayden_iris_brycen", 78, "even", [18, 5, 2305, 3068], False),
    ("page016.jpg", "p079_bw_interview_characters_alder_subway_bosses", 79, "odd", [95, 30, 2355, 3095], False),
    ("page017.jpg", "p080_bw_interview_masuda_bridges_part1", 80, "even", [18, 25, 2285, 3090], False),
    ("page018.jpg", "p081_bw_interview_masuda_bridges_part2", 81, "odd", [95, 10, 2325, 3075], False),
    ("page019.jpg", "p082_bw_interview_masuda_bridges_part3", 82, "even", [18, 4, 2315, 3060], False),
    ("page020.jpg", "p083_bw_interview_masuda_bridges_part4", 83, "odd", [95, 8, 2360, 3072], False),
    ("page022.jpg", "p999_back_cover_ridge_racer_3d", 999, "single", [18, 15, 2450, 3080], False),
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
    "issue": "2011.4",
    "vol": 204,
    "processed_date": time.strftime("%Y-%m-%d"),
    "total_pages": len(PAGE_DEFS),
    "deduplication_notes": "page010.jpg is a narrower duplicate scan of page 75 (jellicent & sawsbuck); page012.jpg with full margin was retained.",
    "geometry_notes": "page007.jpg (P72) raw scan was vertically stretched (height 3638); unstretched vertically to height 3072 to restore true physical 1:1 aspect ratio.",
    "pages": []
}

archive_crops = []

print(f"Starting batch production for {len(PAGE_DEFS)} pages...")

for idx, (raw_name, stem, pnum, ptype, (x1, y1, x2, y2), needs_unstretch) in enumerate(PAGE_DEFS):
    raw_path = os.path.join(RAW_DIR, raw_name)
    raw_img = imread_unicode(raw_path)
    if raw_img is None:
        raise ValueError(f"Could not load image: {raw_path}")
    
    if needs_unstretch:
        # Restore true physical aspect ratio (3638 -> 3072)
        raw_img = cv2.resize(raw_img, (raw_img.shape[1], 3072), interpolation=cv2.INTER_AREA)
    
    # Raw scans in 2011.4 are already ~300 DPI (3070x2400)
    # Crop
    cropped = raw_img[y1:y2, x1:x2]
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
# 1. All overview: 16 pages in 4 rows x 4 columns
thumb_h = 320
thumb_w = 240
grid_thumbs = []
for stem, img in archive_crops:
    t = cv2.resize(img, (thumb_w, thumb_h), interpolation=cv2.INTER_AREA)
    cv2.putText(t, stem, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
    grid_thumbs.append(t)

rows = [np.hstack(grid_thumbs[r*4 : (r+1)*4]) for r in range(4)]
grid_all = np.vstack(rows)
imwrite_unicode(os.path.join(BRAIN_DIR, "dream_2011_4_prepared_all.jpg"), grid_all, [cv2.IMWRITE_JPEG_QUALITY, 85])

# 2. Top headers strip (16 items: 8 in col1, 8 in col2)
header_h = 70
header_w = 800
top_strips = []
for stem, img in archive_crops:
    crop_top = img[:150, :]
    strip = cv2.resize(crop_top, (header_w, header_h), interpolation=cv2.INTER_AREA)
    cv2.putText(strip, stem, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    top_strips.append(strip)

c1 = np.vstack(top_strips[:8])
c2 = np.vstack(top_strips[8:])
top_grid = np.hstack([c1, c2])
imwrite_unicode(os.path.join(BRAIN_DIR, "dream_2011_4_prepared_top.jpg"), top_grid, [cv2.IMWRITE_JPEG_QUALITY, 85])

# 3. Bottom footers strip (16 items: 8 in col1, 8 in col2)
footer_h = 70
footer_w = 800
btm_strips = []
for stem, img in archive_crops:
    crop_btm = img[img.shape[0]-150:, :]
    strip = cv2.resize(crop_btm, (footer_w, footer_h), interpolation=cv2.INTER_AREA)
    cv2.putText(strip, stem, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    btm_strips.append(strip)

b1 = np.vstack(btm_strips[:8])
b2 = np.vstack(btm_strips[8:])
btm_grid = np.hstack([b1, b2])
imwrite_unicode(os.path.join(BRAIN_DIR, "dream_2011_4_prepared_btm.jpg"), btm_grid, [cv2.IMWRITE_JPEG_QUALITY, 85])

print("All contact sheets generated in brain directory!")
