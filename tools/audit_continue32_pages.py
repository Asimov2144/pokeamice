# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

engine = RapidOCR()
src_dir = r"E:\Pokeamice\scan\Continue Vol.32"
files = sorted([f for f in os.listdir(src_dir) if f.endswith('.jpg')])

out_txt = r"p:\WEBSITE\pokeamice-main (1)\pokeamice-main\continue32_audit_ocr.txt"

with open(out_txt, "w", encoding="utf-8") as out:
    for f in files:
        fp = os.path.join(src_dir, f)
        img = cv2.imread(fp)
        h, w = img.shape[:2]
        aspect = w / float(h)
        
        if aspect > 1.1:
            # Spread: in Japanese right-binding, right half is the earlier page, left half is the later page
            # Let's inspect right half and left half separately
            mid = w // 2
            right_half = img[:, mid:]
            left_half = img[:, :mid]
            
            # Right half
            res_r, _ = engine(cv2.resize(right_half, (1200, int(h * 1200 / (w - mid)))))
            texts_r = [r[1] for r in res_r if r[2] > 0.4] if res_r else []
            
            # Left half
            res_l, _ = engine(cv2.resize(left_half, (1200, int(h * 1200 / mid))))
            texts_l = [r[1] for r in res_l if r[2] > 0.4] if res_l else []
            
            out.write(f"\n{'='*30} {f} RIGHT HALF {'='*30}\n")
            out.write(" | ".join(texts_r[:25]) + "\n")
            
            out.write(f"\n{'='*30} {f} LEFT HALF {'='*30}\n")
            out.write(" | ".join(texts_l[:25]) + "\n")
        else:
            res, _ = engine(cv2.resize(img, (1200, int(h * 1200 / w))))
            texts = [r[1] for r in res if r[2] > 0.4] if res else []
            out.write(f"\n{'='*30} {f} SINGLE PAGE {'='*30}\n")
            out.write(" | ".join(texts[:25]) + "\n")

print(f"Saved audit OCR to {out_txt}")
