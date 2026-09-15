# -*- coding: utf-8 -*-
import json

with open('scan-prepared/continue-vol32-full-20260829/ocr_transcriptions/continue32_ocr_extracted.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data:
    fol = p['folio']
    fn = p['filename']
    boxes = p['boxes']
    print(f"\n{'='*20} Folio {fol}: {fn} ({len(boxes)} boxes) {'='*20}")
    # Sort with Japanese reading order:
    # Most pages have 3 vertical text columns (top column Y:100-680, mid Y:700-1280, bottom Y:1300-1860)
    # Inside each column, text lines are vertical, read from right (large X) to left (small X)
    # Let's group boxes by vertical band (column)
    cols = {"top": [], "mid": [], "bot": [], "other": []}
    for b in boxes:
        y_center = b["center_y"]
        if y_center < 700:
            cols["top"].append(b)
        elif y_center < 1300:
            cols["mid"].append(b)
        elif y_center < 1900:
            cols["bot"].append(b)
        else:
            cols["other"].append(b)
            
    for col_name in ["bot", "mid", "top"]:
        c_boxes = cols[col_name]
        if not c_boxes:
            continue
        # Within column: sort right to left (descending X)
        c_sorted = sorted(c_boxes, key=lambda b: -b["center_x"])
        print(f"--- Column {col_name.upper()} ({len(c_sorted)} boxes) ---")
        line_txts = [b["text"] for b in c_sorted]
        print(" | ".join(line_txts))
