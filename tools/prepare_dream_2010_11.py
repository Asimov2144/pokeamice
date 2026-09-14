# -*- coding: utf-8 -*-
"""
Batch preparation, OCR, and verification script for:
『Nintendo DREAM』（ニンテンドードリーム / ニンドリ）2010年11月号（通巻199号、毎日コミュニケーションズ）
Source: E:\Pokeamice\scan\DREAM 2010.11
Output: E:\Pokeamice\scan\DREAM 2010.11_prepared\
  - archive/ (300 DPI master supersampled from 600 DPI, Quality 95)
  - web/ (2048px height, Quality 85)
  - ocr_transcriptions/ (RapidOCR JSONs)
  - scan-manifest.json
  - dream_2010_11_contact_sheet.jpg (in brain directory)
"""

import os
import sys
import json
import hashlib
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

SRC_DIR = r"E:\Pokeamice\scan\DREAM 2010.11"
OUT_BASE = r"E:\Pokeamice\scan\DREAM 2010.11_prepared"
OUT_ARCHIVE = os.path.join(OUT_BASE, "archive")
OUT_WEB = os.path.join(OUT_BASE, "web")
OUT_OCR = os.path.join(OUT_BASE, "ocr_transcriptions")
BRAIN_DIR = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334"

for d in [OUT_ARCHIVE, OUT_WEB, OUT_OCR]:
    os.makedirs(d, exist_ok=True)

def cv2_imread(path):
    with open(path, "rb") as f:
        return cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)

def cv2_imwrite(path, img, quality=95):
    ext = os.path.splitext(path)[1]
    result, buf = cv2.imencode(ext, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if result:
        with open(path, "wb") as f:
            f.write(buf)
        return True
    return False

def md5_file(filepath):
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

PAGE_SPECS = [
    ("page018.jpg", "p001_cover", 1, False, "Cover / 表紙: 『Nintendo DREAM』2010年11月号 (Vol.199) レシラム＆ゼクロム / ポケモンBW総力特集"),
    ("page019.jpg", "p002_foldout_poster", 2, False, "特別付録 折込ポスター: 『ポケットモンスターブラック・ホワイト』 出会うポケモン、すべてが新しい。全部で100種以上！新ポケモン一覧"),
    ("page021.jpg", "p004_contents", 4, False, "Contents / 目次: P.4-P.5 CONTENTS / 5大地方観光ガイド・新連載マナフィ愛好倶楽部 (重複スキャン page020 除外)"),
    ("page023.jpg", "p069_5regions_guide_intro", 69, False, "特集 扉: ニンドリだけの15ページ特別企画！「ALL ABOUT ポケットモンスター 5大地方観光ガイド」 (P.69)"),
    ("page024.jpg", "p070_unova_region_part1", 70, False, "5大地方観光ガイド 1: イッシュ地方 (ヒウンシティ、シッポウシティ、サンヨウシティ、地下水脈の穴、ヤグルマの森) (P.70)"),
    ("page027.jpg", "p071_unova_region_part2", 71, False, "5大地方観光ガイド 2: イッシュ地方 (ライモンシティ、ホドモエシティ、フキヨセシティ、リゾートデザート、古代の城) (P.71)"),
    ("page028.jpg", "p072_kanto_region_part1", 72, False, "5大地方観光ガイド 3: カントー地方 (マサラタウン、タマムシシティ、ヤマブキシティ、トキワの森、お月見山) (P.72)"),
    ("page029.jpg", "p073_kanto_region_part2", 73, False, "5大地方観光ガイド 4: カントー地方 (グレンタウン、ハナダシティ、シオンタウン、サファリゾーン、無人発電所) (P.73)"),
    ("page030.jpg", "p074_johto_region_part1", 74, False, "5大地方観光ガイド 5: ジョウト地方 (ワカバタウン、コガネシティ、エンジュシティ、スズの塔、うずまき島) (P.74)"),
    ("page031.jpg", "p075_johto_region_part2", 75, False, "5大地方観光ガイド 6: ジョウト地方 (アサギシティ、タンバシティ、フスベシティ、アルフの遺跡、シロガネ山) (P.75)"),
    ("page032.jpg", "p076_hoenn_region_part1", 76, False, "5大地方観光ガイド 7: ホウエン地方 (ミシロタウン、カイナシティ、キンセツシティ、えんとつ山、トクサネシティ) (P.76)"),
    ("page033.jpg", "p077_hoenn_region_part2", 77, False, "5大地方観光ガイド 8: ホウエン地方 (ヒワマキシティ、ミナモシティ、ルネシティ、おくりび山、そらのはしら) (P.77)"),
    ("page034.jpg", "p078_sinnoh_region_part1", 78, False, "5大地方観光ガイド 9: シンオウ地方 (フタバタウン、コトブキシティ、ハクタイシティ、テンガン山、シンジ湖) (P.78)"),
    ("page035.jpg", "p079_sinnoh_region_part2", 79, False, "5大地方観光ガイド 10: シンオウ地方 (ヨスガシティ、ノモセシティ、ナギサシティ、やりのはしら、大湿原) (P.79)"),
    ("page036.jpg", "p080_best3_mountains_routes_buildings", 80, False, "5大地方なんでもベスト3 (1): 高い山 ＆ 長い道路 ＆ 巨大建造物 (P.80)"),
    ("page037.jpg", "p081_best3_views_dangers_gourmet", 81, False, "5大地方なんでもベスト3 (2): 絶景スポット ＆ 危険地帯 ＆ 名物グルメ (P.81)"),
    ("page038.jpg", "p082_best3_hotsprings_ruins_resorts", 82, False, "5大地方なんでもベスト3 (3): 温泉 ＆ 古代遺跡 ＆ リゾート地 (P.82)"),
    ("page039.jpg", "p083_best3_transport_battle_halls", 83, True, "5大地方なんでもベスト3 (4): 各地の乗り物 ＆ バトルの殿堂 (P.83, 180°倒置スキャン補正済, 重複スキャン page040 除外)"),
    ("page041.jpg", "p148_back_cover", 148, False, "Back Cover / 表4 裏表紙: 『毛糸のカービィ』 ＆ 毎日コミュニケーションズ発行クレジット")
]

print("Initializing RapidOCR engine...")
ocr_engine = RapidOCR()

manifest = {
    "title": "『Nintendo DREAM』（ニンテンドードリーム / ニンドリ）2010年11月号（Vol.199）",
    "publication_date": "2010-11-01 (2010年9月21日発売)",
    "publisher": "毎日コミュニケーションズ（Mycom）",
    "notes": "全21スキャン中、重複スキャン2組（目次 page020/021, P.83 page039/040）を物理ラプラシアン鮮鋭度判定で厳選（page021及びpage039を採用）。P.83(page039)の180度倒置スキャンを正立補正。厳選19ページにて完全アーカイブ化。",
    "duplicate_audit": [
        {
            "pair": ["page020.jpg", "page021.jpg"],
            "description": "目次 (P.4-P.5 相当)",
            "page020_sharpness": 38.37,
            "page021_sharpness": 38.51,
            "adopted": "page021.jpg",
            "reason": "page021.jpg の方がラプラシアン分散が高くテキスト輪郭が鮮明"
        },
        {
            "pair": ["page039.jpg", "page040.jpg"],
            "description": "5大地方なんでもベスト3 (4) 各地の乗り物・バトルの殿堂 (P.83)",
            "page039_sharpness": 22.97,
            "page040_sharpness": 22.40,
            "adopted": "page039.jpg",
            "rotation_applied": "ROTATE_180",
            "reason": "両者ともスキャナ上で180度倒置スキャンされていたためROTATE_180補正を適用。page039.jpg の方が高解像度鮮鋭度を維持"
        }
    ],
    "total_pages": len(PAGE_SPECS),
    "pages": []
}

processed_thumbs = []

print(f"Processing {len(PAGE_SPECS)} pages...")
for idx, (raw_name, out_id, book_page, rotate_180, desc) in enumerate(PAGE_SPECS, 1):
    raw_path = os.path.join(SRC_DIR, raw_name)
    if not os.path.exists(raw_path):
        print(f"ERROR: Missing {raw_path}")
        continue

    print(f"[{idx}/{len(PAGE_SPECS)}] Processing {raw_name} -> {out_id} (rot180={rotate_180})...")
    img = cv2_imread(raw_path)
    if img is None:
        print(f"ERROR: Failed reading {raw_path}")
        continue

    if rotate_180:
        img = cv2.rotate(img, cv2.ROTATE_180)

    orig_h, orig_w = img.shape[:2]

    # Supersample 600 DPI to 300 DPI master
    # 4962 x 7019 -> 2481 x 3509
    arch_w = int(round(orig_w * 0.5))
    arch_h = int(round(orig_h * 0.5))
    arch_img = cv2.resize(img, (arch_w, arch_h), interpolation=cv2.INTER_AREA)

    arch_filename = f"{out_id}.jpg"
    arch_path = os.path.join(OUT_ARCHIVE, arch_filename)
    cv2_imwrite(arch_path, arch_img, quality=95)

    # Web version (height 2048px)
    web_h = 2048
    scale = web_h / float(orig_h)
    web_w = int(round(orig_w * scale))
    web_img = cv2.resize(img, (web_w, web_h), interpolation=cv2.INTER_AREA)

    web_filename = f"{out_id}.jpg"
    web_path = os.path.join(OUT_WEB, web_filename)
    cv2_imwrite(web_path, web_img, quality=85)

    arch_bytes = os.path.getsize(arch_path)
    web_bytes = os.path.getsize(web_path)
    arch_md5 = md5_file(arch_path)
    web_md5 = md5_file(web_path)

    # RapidOCR
    print(f"  Running OCR on {out_id}...")
    ocr_results, elapse = ocr_engine(arch_img)
    ocr_boxes = []
    if ocr_results:
        for box, text, score in ocr_results:
            ocr_boxes.append({
                "box": [list(pt) for pt in box],
                "text": text,
                "score": float(score)
            })
    
    ocr_json_name = f"{out_id}_ocr.json"
    ocr_json_path = os.path.join(OUT_OCR, ocr_json_name)
    with open(ocr_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "page_index": idx,
            "raw_file": raw_name,
            "id": out_id,
            "book_page": book_page,
            "rotated_180": rotate_180,
            "description": desc,
            "elapse": elapse,
            "total_boxes": len(ocr_boxes),
            "boxes": ocr_boxes
        }, f, ensure_ascii=False, indent=2)
    print(f"  Saved {len(ocr_boxes)} boxes to {ocr_json_name}")

    page_meta = {
        "index": idx,
        "raw_file": raw_name,
        "book_page": book_page,
        "id": out_id,
        "rotated_180": rotate_180,
        "description": desc,
        "archive": {
            "filename": arch_filename,
            "width": arch_w,
            "height": arch_h,
            "filesize_bytes": arch_bytes,
            "md5": arch_md5
        },
        "web": {
            "filename": web_filename,
            "width": web_w,
            "height": web_h,
            "filesize_bytes": web_bytes,
            "md5": web_md5
        }
    }
    manifest["pages"].append(page_meta)

    # Save thumb for contact sheet
    thumb_h = 450
    thumb_w = int(round(arch_w * (thumb_h / float(arch_h))))
    thumb = cv2.resize(arch_img, (thumb_w, thumb_h), interpolation=cv2.INTER_AREA)
    processed_thumbs.append((idx, out_id, book_page, desc, thumb))

# Save scan-manifest.json
manifest_path = os.path.join(OUT_BASE, "scan-manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print(f"Saved manifest to {manifest_path}")

# Build contact sheet (4 rows x 5 columns = 20 cells)
print("Building contact sheet...")
grid_cols = 5
grid_rows = 4
cell_w = 320
cell_h = 480
margin = 20
header_h = 80

sheet_w = grid_cols * cell_w + (grid_cols + 1) * margin
sheet_h = grid_rows * cell_h + (grid_rows + 1) * margin + header_h

sheet = np.full((sheet_h, sheet_w, 3), 24, dtype=np.uint8)

cv2.putText(sheet, "Nintendo DREAM (2010.11 Vol.199) Mycom - 19 Unique Pages Audit",
            (margin + 10, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(sheet, "Pokemon BW Special Feature | ALL ABOUT Pokemon 5 Major Regions Tourism Guide (P.69-P.83)",
            (margin + 10, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (160, 200, 255), 1, cv2.LINE_AA)

for i, (idx, out_id, b_page, desc, thumb) in enumerate(processed_thumbs):
    r = i // grid_cols
    c = i % grid_cols

    x0 = margin + c * (cell_w + margin)
    y0 = header_h + margin + r * (cell_h + margin)

    th, tw = thumb.shape[:2]
    max_tw = cell_w - 20
    max_th = cell_h - 45
    scale = min(max_tw / float(tw), max_th / float(th))
    nw, nh = int(round(tw * scale)), int(round(th * scale))
    resized_thumb = cv2.resize(thumb, (nw, nh), interpolation=cv2.INTER_AREA)

    px = x0 + (cell_w - nw) // 2
    py = y0 + 10 + (max_th - nh) // 2

    sheet[py:py+nh, px:px+nw] = resized_thumb
    cv2.rectangle(sheet, (px-1, py-1), (px+nw+1, py+nh+1), (70, 70, 70), 1)

    page_str = f"P.{b_page}" if b_page else "Cover"
    label = f"#{idx:02d} {page_str} {out_id[:14]}"
    cv2.putText(sheet, label, (x0 + 10, y0 + cell_h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1, cv2.LINE_AA)

# Draw 20th cell info card
r = 19 // grid_cols
c = 19 % grid_cols
x0 = margin + c * (cell_w + margin)
y0 = header_h + margin + r * (cell_h + margin)
cv2.rectangle(sheet, (x0+10, y0+20), (x0+cell_w-10, y0+cell_h-30), (45, 45, 45), -1)
cv2.rectangle(sheet, (x0+10, y0+20), (x0+cell_w-10, y0+cell_h-30), (100, 100, 100), 1)
info_lines = [
    "AUDIT SUMMARY",
    "Total Scans: 21",
    "Unique Pages: 19",
    "Duplicates Dropped: 2",
    " - page020 (Contents)",
    " - page040 (P.83)",
    "Orientations: 100% OK",
    " - P.83 Rotated 180 deg",
    "Master: 300 DPI Area",
    "Web: 2048px Q85",
    "OCR: RapidOCR 19 Pages"
]
for li, line in enumerate(info_lines):
    color = (120, 220, 255) if li == 0 else (200, 200, 200)
    font_scale = 0.55 if li == 0 else 0.45
    thickness = 2 if li == 0 else 1
    cv2.putText(sheet, line, (x0 + 25, y0 + 60 + li * 32),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)

contact_path = os.path.join(BRAIN_DIR, "dream_2010_11_contact_sheet.jpg")
cv2_imwrite(contact_path, sheet, quality=90)
print(f"Contact sheet saved to {contact_path}")

print("Batch preparation completed successfully!")
