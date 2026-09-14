# -*- coding: utf-8 -*-
import os
import json

ocr_dir = r"E:\Pokeamice\scan\DREAM 2010.11_prepared\ocr_transcriptions"
out_txt = os.path.join(ocr_dir, "all_guide_raw_ocr.txt")

pages = [
    "p001_cover",
    "p002_foldout_poster",
    "p004_contents",
    "p069_5regions_guide_intro",
    "p070_unova_region_part1",
    "p071_unova_region_part2",
    "p072_kanto_region_part1",
    "p073_kanto_region_part2",
    "p074_johto_region_part1",
    "p075_johto_region_part2",
    "p076_hoenn_region_part1",
    "p077_hoenn_region_part2",
    "p078_sinnoh_region_part1",
    "p079_sinnoh_region_part2",
    "p080_best3_mountains_routes_buildings",
    "p081_best3_views_dangers_gourmet",
    "p082_best3_hotsprings_ruins_resorts",
    "p083_best3_transport_battle_halls",
    "p148_back_cover"
]

with open(out_txt, "w", encoding="utf-8") as out:
    for pid in pages:
        fp = os.path.join(ocr_dir, f"{pid}_ocr.json")
        if not os.path.exists(fp):
            continue
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
        page_num = data.get("book_page")
        desc = data.get("description", "")
        out.write(f"\n\n{'='*30} {pid} (P.{page_num}) {'='*30}\n")
        out.write(f"Description: {desc}\n\n")
        boxes = sorted(data["boxes"], key=lambda b: (b["box"][0][1], b["box"][0][0]))
        for b in boxes:
            if b["score"] > 0.4:
                out.write(f"[{b['score']:.2f}] {b['text']}\n")

print(f"Saved all raw OCR text to {out_txt}")
