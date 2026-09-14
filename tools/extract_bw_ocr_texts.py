# -*- coding: utf-8 -*-
"""
Run RapidOCR on all prepared web images of Pokemon BW Tanjou Hiwa booklet.
Outputs raw OCR text files to scratch/bw_raw_ocr/
"""

import os
import sys
import json
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

ocr = RapidOCR()

WEB_DIR = r"E:\Pokeamice\scan\黑白 诞生秘话_prepared\web"
SCRATCH_DIR = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334\scratch\bw_raw_ocr"
os.makedirs(SCRATCH_DIR, exist_ok=True)

manifest_file = r"E:\Pokeamice\scan\黑白 诞生秘话_prepared\scan-manifest.json"
with open(manifest_file, "r", encoding="utf-8") as f:
    manifest = json.load(f)

for page in manifest["pages"]:
    basename = page["output_basename"]
    out_txt = os.path.join(SCRATCH_DIR, f"{basename}.txt")
    if os.path.exists(out_txt) and os.path.getsize(out_txt) > 20:
        continue
    
    img_path = os.path.join(WEB_DIR, f"{basename}.jpg")
    img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    
    res, _ = ocr(img)
    lines = []
    if res:
        for box, text, score in res:
            lines.append(text)
    
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Done OCR for {basename} ({len(lines)} lines)")
    sys.stdout.flush()

print("All raw OCR extraction finished.")
