# -*- coding: utf-8 -*-
"""
High-precision OCR extraction script for core lore and historical sections of:
『ポケットモンスター図鑑』（Aspect / Creatures, 1996）
"""

import os
import sys
import re
import json
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

SRC_DIR = r"E:\Pokeamice\scan\初代攻略本"
OUT_BASE = r"E:\Pokeamice\scan\初代攻略本_prepared"
OCR_DIR = os.path.join(OUT_BASE, "ocr_transcriptions")
os.makedirs(OCR_DIR, exist_ok=True)

def cv2_imread(path):
    with open(path, "rb") as f:
        return cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)

# Map files by index
raw_files = [f for f in os.listdir(SRC_DIR) if f.lower().endswith(".jpg")]
page_map = {}
for f in raw_files:
    m = re.search(r'_(\d{3})_', f)
    if m:
        p_idx = int(m.group(1))
        page_map[p_idx] = f

# Target pages for OCR extraction
# Olympic & Contents: 4, 5, 6, 7, 8
# Mew Special: 54
# Ch5 Pokemon Journal: 131, 132, 133, 134, 135, 136
# Ch6 Staff Interview: 137, 138, 139, 140, 141, 142, 143, 144, 145
# Colophon: 146
target_indices = [4, 5, 6, 7, 8, 54, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146]

engine = RapidOCR()

for idx in target_indices:
    raw_name = page_map[idx]
    file_path = os.path.join(SRC_DIR, raw_name)
    book_page = idx - 2
    out_json_name = f"page_{idx:03d}_p{book_page:03d}_ocr.json"
    out_json_path = os.path.join(OCR_DIR, out_json_name)

    print(f"Running OCR on File {idx:03d} (Book P.{book_page:03d})...")
    img = cv2_imread(file_path)
    if img is None:
        print(f"Failed to read {file_path}")
        continue

    results, elapse = engine(img)
    ocr_data = {
        "file_index": idx,
        "raw_file": raw_name,
        "book_page": book_page,
        "elapse": elapse,
        "boxes": []
    }
    if results:
        for box, text, score in results:
            ocr_data["boxes"].append({
                "box": [list(pt) for pt in box],
                "text": text,
                "score": float(score)
            })

    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(ocr_data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(ocr_data['boxes'])} text lines to {out_json_name}")

print("All target pages OCR extraction complete!")
