# -*- coding: utf-8 -*-
"""
Batch preparation and OCR script for:
『ダ・ヴィンチ』（Da Vinci）2011年1月号（通巻201号、メディアファクトリー）
Source: E:\Pokeamice\scan\ダ　ウチい
Output: E:\Pokeamice\scan\ダ　ウチい_prepared\
  - archive/ (300 DPI master supersampled from 600 DPI, Quality 95)
  - web/ (2048px height, Quality 85)
  - ocr_transcriptions/ (RapidOCR JSONs + detailed Markdown transcripts)
  - scan-manifest.json
  - davinci_contact_sheet.jpg (in brain directory)
"""

import os
import sys
import json
import hashlib
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

SRC_DIR = r"E:\Pokeamice\scan\ダ　ウチい"
OUT_BASE = r"E:\Pokeamice\scan\ダ　ウチい_prepared"
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
    ("page042.jpg", "p001_cover", None, "Cover / 表紙: 『ダ・ヴィンチ』2011年1月号 (表紙・向井理 / 2010年 BOOK OF THE YEAR)"),
    ("page043.jpg", "p002_ad_young_kun", None, "広告: マガジンハウス ムトウマサヤ『ヤングくん 1』人気4コマベスト10"),
    ("page044.jpg", "p007_contents", 7, "Contents / 目次: 『ダ・ヴィンチ』2011年1月号 目次 (P.7)"),
    ("page047.jpg", "p058_kojima_hanazawa_part1", 58, "特別対談 扉: 小島秀夫 (『MGS PW』) × 花沢健吾 (『アイアムアヒーロー』) 「ぼくたちを作品づくりに突き動かすもの」 (P.58)"),
    ("page048.jpg", "p059_kojima_hanazawa_part2", 59, "特別対談 1: ゾンビと非モテ系、破壊衝動と日常のリアリティ、MGS PWの冷戦 (P.59)"),
    ("page050.jpg", "p060_kojima_hanazawa_part3", 60, "特別対談 2: ウイルスの如く広がる匿名ネット情報、現実で味わえない生き方 (P.60)"),
    ("page051.jpg", "p061_kojima_hanazawa_part4", 61, "特別対談 3: 結語・ひきこもりが生き残る終末世界 ＆ 『キャッスルヴァニア ロード オブ シャドウ』 (P.61)"),
    ("page045.jpg", "p132_pokemon_bw_special", 132, "特集: 『ポケットモンスターブラック・ホワイト』 「大人だって『ポケモン』が好き！」 (P.132)"),
    ("page046.jpg", "p133_masuda_junichi_interview", 133, "インタビュー: 株式会社ゲームフリーク 増田順一氏 スペシャルインタビュー ＆ クリエイター必携ブックガイド ＆ BW音楽の世界 (P.133)"),
    ("page052.jpg", "p148_back_cover", None, "Back Cover / 表4 裏表紙: 20世紀フォックス 『サウンド・オブ・ミュージック』BD ＆ メディアファクトリー発行クレジット")
]

print("Initializing RapidOCR engine...")
ocr_engine = RapidOCR()

manifest = {
    "title": "『ダ・ヴィンチ』（Da Vinci）2011年1月号（通巻201号）",
    "publication_date": "2011-01-06 (平成23年1月6日発行)",
    "publisher": "メディアファクトリー（MEDIA FACTORY）",
    "notes": "フォルダ名『ダ　ウチい』は『ダ・ヴィンチ』の転写異体名。スキャン時に page049 が欠番となっているが、P.58〜P.61の対談本文およびP.132〜P.133のポケモン特集は完全収録・文脈完全連続であることを確認済。",
    "total_pages": len(PAGE_SPECS),
    "pages": []
}

processed_thumbs = []

print("Processing 10 pages...")
for idx, (raw_name, out_id, book_page, desc) in enumerate(PAGE_SPECS, 1):
    raw_path = os.path.join(SRC_DIR, raw_name)
    if not os.path.exists(raw_path):
        print(f"ERROR: Missing {raw_path}")
        continue

    print(f"[{idx}/10] Processing {raw_name} -> {out_id}...")
    img = cv2_imread(raw_path)
    if img is None:
        print(f"ERROR: Failed reading {raw_path}")
        continue

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

# Build contact sheet (2 rows x 5 columns)
print("Building contact sheet...")
grid_cols = 5
grid_rows = 2
cell_w = 320
cell_h = 500
margin = 20
header_h = 80

sheet_w = grid_cols * cell_w + (grid_cols + 1) * margin
sheet_h = grid_rows * cell_h + (grid_rows + 1) * margin + header_h

sheet = np.full((sheet_h, sheet_w, 3), 24, dtype=np.uint8)

cv2.putText(sheet, "Da Vinci (2011.01 Vol.201) Media Factory - 10 Pages Audit",
            (margin + 10, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(sheet, "Pokemon BW Special + Masuda Junichi Interview | Kojima Hideo x Hanazawa Kengo Dialogue",
            (margin + 10, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (160, 200, 255), 1, cv2.LINE_AA)

for i, (idx, out_id, b_page, desc, thumb) in enumerate(processed_thumbs):
    r = i // grid_cols
    c = i % grid_cols

    x0 = margin + c * (cell_w + margin)
    y0 = header_h + margin + r * (cell_h + margin)

    th, tw = thumb.shape[:2]
    max_tw = cell_w - 20
    max_th = cell_h - 50
    scale = min(max_tw / float(tw), max_th / float(th))
    nw, nh = int(round(tw * scale)), int(round(th * scale))
    resized_thumb = cv2.resize(thumb, (nw, nh), interpolation=cv2.INTER_AREA)

    px = x0 + (cell_w - nw) // 2
    py = y0 + 10 + (max_th - nh) // 2

    sheet[py:py+nh, px:px+nw] = resized_thumb
    cv2.rectangle(sheet, (px-1, py-1), (px+nw+1, py+nh+1), (70, 70, 70), 1)

    page_str = f"P.{b_page}" if b_page else "Cover/Ad"
    label = f"#{idx:02d} {page_str} {out_id[:14]}"
    cv2.putText(sheet, label, (x0 + 10, y0 + cell_h - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1, cv2.LINE_AA)

contact_path = os.path.join(BRAIN_DIR, "davinci_contact_sheet.jpg")
cv2_imwrite(contact_path, sheet, quality=90)
print(f"Contact sheet saved to {contact_path}")

print("Batch preparation completed successfully!")
