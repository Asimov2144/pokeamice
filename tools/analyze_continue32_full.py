# -*- coding: utf-8 -*-
import os
import cv2
import json

src_dir = r"E:\Pokeamice\scan\Continue Vol.32"
files = sorted([f for f in os.listdir(src_dir) if f.endswith('.jpg')])

out_dir = r"p:\WEBSITE\pokeamice-main (1)\pokeamice-main\scan-prepared\continue32_debug"
os.makedirs(out_dir, exist_ok=True)

from rapidocr_onnxruntime import RapidOCR
engine = RapidOCR()

page_list = []

for f in files:
    fp = os.path.join(src_dir, f)
    img = cv2.imread(fp)
    h, w = img.shape[:2]
    aspect = w / float(h)
    
    if aspect > 1.1:
        # Spread
        # Japanese right-binding: right half is Page N, left half is Page N+1
        mid = w // 2
        right_half = img[:, mid:]
        left_half = img[:, :mid]
        
        page_list.append((f, "right", right_half))
        page_list.append((f, "left", left_half))
    else:
        page_list.append((f, "single", img))

print(f"Total split pages: {len(page_list)}")

results = []
for idx, (src_file, side, pimg) in enumerate(page_list, 1):
    h, w = pimg.shape[:2]
    # Resize for OCR
    scale = 2048.0 / h
    nw, nh = int(round(w * scale)), 2048
    resized = cv2.resize(pimg, (nw, nh), interpolation=cv2.INTER_AREA)
    
    # Save debug web image
    out_name = f"page_{idx:02d}_{src_file.replace('.jpg', '')}_{side}.jpg"
    out_path = os.path.join(out_dir, out_name)
    cv2.imwrite(out_path, resized)
    
    ocr_res, _ = engine(resized)
    boxes = []
    if ocr_res:
        for box, text, score in ocr_res:
            if score > 0.4:
                boxes.append((box, text, score))
    
    texts = [b[1] for b in boxes]
    
    # Detect folio / page number from text
    folio = None
    for t in texts:
        t_clean = t.strip()
        if t_clean.isdigit() and 90 <= int(t_clean) <= 130:
            folio = int(t_clean)
            break
    
    # Header / title
    header = " | ".join(texts[:5]) if texts else "NO TEXT"
    
    results.append({
        "idx": idx,
        "src_file": src_file,
        "side": side,
        "width": w,
        "height": h,
        "folio": folio,
        "box_count": len(boxes),
        "sample_text": texts[:8],
        "image_file": out_name
    })
    print(f"[{idx:02d}/16] {src_file:12s} ({side:6s}) -> folio: {str(folio):4s} | boxes: {len(boxes):3d} | {header[:60]}")

with open(os.path.join(out_dir, "pages_summary.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Done full analysis!")
