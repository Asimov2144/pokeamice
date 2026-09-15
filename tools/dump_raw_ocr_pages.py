# -*- coding: utf-8 -*-
import json
import os

json_p = r"p:\WEBSITE\pokeamice-main (1)\pokeamice-main\scan-prepared\continue-vol32-full-20260829\ocr_transcriptions\continue32_ocr_extracted.json"
out_txt = r"p:\WEBSITE\pokeamice-main (1)\pokeamice-main\scan-prepared\continue-vol32-full-20260829\ocr_transcriptions\raw_ocr_pages.txt"

with open(json_p, "r", encoding="utf-8") as f:
    pages = json.load(f)

with open(out_txt, "w", encoding="utf-8") as out:
    for p in pages:
        folio = p["folio"]
        fn = p["filename"]
        desc = p["description"]
        out.write(f"\n\n{'='*30} Page {folio}: {fn} {'='*30}\n")
        out.write(f"Description: {desc}\n\n")
        for b in p["boxes"]:
            rect = [int(x) for x in b["rect"]]
            out.write(f"[{rect[0]:4d},{rect[1]:4d} - {rect[2]:4d},{rect[3]:4d}] {b['text']}\n")

print(f"Dumped text to {out_txt}")
