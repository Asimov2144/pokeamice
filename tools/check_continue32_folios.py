# -*- coding: utf-8 -*-
import os
import cv2
from rapidocr_onnxruntime import RapidOCR

engine = RapidOCR()
src_dir = r"E:\Pokeamice\scan\Continue Vol.32"
files = sorted([f for f in os.listdir(src_dir) if f.endswith('.jpg')])

print("Scanning headers/footers for page numbers and titles...")
for f in files:
    fp = os.path.join(src_dir, f)
    img = cv2.imread(fp)
    h, w = img.shape[:2]
    
    # Bottom margin (bottom 10%)
    bottom = img[int(h*0.92):, :]
    # Top margin (top 8%)
    top = img[:int(h*0.08), :]
    
    res_b, _ = engine(cv2.resize(bottom, (1200, int(bottom.shape[0] * 1200 / w))))
    res_t, _ = engine(cv2.resize(top, (1200, int(top.shape[0] * 1200 / w))))
    
    texts_b = [r[1] for r in res_b if r[2] > 0.4] if res_b else []
    texts_t = [r[1] for r in res_t if r[2] > 0.4] if res_t else []
    
    print(f"=== {f} ({w}x{h}) ===")
    print("  TOP:   ", " | ".join(texts_t))
    print("  BOTTOM:", " | ".join(texts_b))
