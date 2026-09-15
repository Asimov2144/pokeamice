# -*- coding: utf-8 -*-
import json
import os
import re

json_p = r"p:\WEBSITE\pokeamice-main (1)\pokeamice-main\scan-prepared\continue-vol32-full-20260829\ocr_transcriptions\continue32_ocr_extracted.json"
out_p = r"p:\WEBSITE\pokeamice-main (1)\pokeamice-main\scan-prepared\continue-vol32-full-20260829\ocr_transcriptions\reconstructed_dialogue.txt"

with open(json_p, "r", encoding="utf-8") as f:
    pages = json.load(f)

with open(out_p, "w", encoding="utf-8") as out:
    for p in pages:
        fol = p["folio"]
        fn = p["filename"]
        desc = p["description"]
        boxes = p["boxes"]
        
        out.write(f"\n\n{'='*40}\nPage {fol}: {fn}\n{desc}\n{'='*40}\n\n")
        
        # Group into 3 vertical columns
        cols = {"top": [], "mid": [], "bot": []}
        for b in boxes:
            yc = b["center_y"]
            if yc < 700:
                cols["top"].append(b)
            elif yc < 1300:
                cols["mid"].append(b)
            else:
                cols["bot"].append(b)
        
        # Read from right to left column?
        # In P.101: intro is at top, dialogue starts in bottom column
        # In P.102-P.111: standard 3-column vertical layout.
        # Right-to-left binding: Japanese vertical text reads from Right Column to Left Column!
        # Wait, is Y=100-700 the top column or right column?
        # A page is height 2048, width ~1500.
        # The page is divided into 3 HORIZONTAL BANDS (rows of vertical text):
        # Band 1: Top (Y: 100 to 680)
        # Band 2: Middle (Y: 700 to 1280)
        # Band 3: Bottom (Y: 1300 to 1860)
        # In Japanese vertical magazine layout with 3 horizontal bands:
        # Does reading start at Band 1 (Top) from Right to Left, then Band 2 (Middle) Right to Left, then Band 3 (Bottom) Right to Left?
        # YES! That is standard Japanese multi-column vertical text!
        # Band 1 (Top) -> Band 2 (Middle) -> Band 3 (Bottom)!
        # And within each band, lines are vertical, reading from RIGHT (X: 1500) to LEFT (X: 0)!
        
        for band_name in ["top", "mid", "bot"]:
            b_boxes = cols[band_name]
            if not b_boxes:
                continue
            # Sort within band: right to left (descending X)
            b_sorted = sorted(b_boxes, key=lambda b: -b["center_x"])
            out.write(f"\n--- Band {band_name.upper()} ---\n")
            for b in b_sorted:
                rect = [int(x) for x in b["rect"]]
                out.write(f"[{rect[0]:4d},{rect[1]:4d}] {b['text']}\n")

print(f"Saved reconstructed text to {out_p}")
