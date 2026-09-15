# -*- coding: utf-8 -*-
import json
import os

BASE_DIR = r"p:\WEBSITE\pokeamice-main (1)\pokeamice-main"
POST_P = os.path.join(BASE_DIR, "_posts", "2026-08-29-continue-vol32-scan-archive.md")
REGIONS_P = os.path.join(BASE_DIR, "continue-vol32-regions.json")
MANIFEST_P = os.path.join(BASE_DIR, "scan-prepared", "continue-vol32-full-20260829", "scan-manifest.json")

with open(MANIFEST_P, "r", encoding="utf-8") as f:
    manifest = json.load(f)

# Build a clean regions JSON compatible with magazine-region-annotator and ocr-translation-workbench
annotator_data = {
    "version": "2.0.0",
    "createdAt": "2026-09-15T07:45:00+09:00",
    "publication": "CONTINUE",
    "issue": "Vol.32",
    "title": "スペシャル対談 田尻智×中川翔子",
    "totalPages": len(manifest["pages"]),
    "pages": []
}

for p in manifest["pages"]:
    web_fn = p["web"]["filename"]
    web_rel = f"/assets/images/scan-archive/continue-vol32-20260829/pages/{web_fn}"
    annotator_data["pages"].append({
        "pageIndex": p["order"] - 1,
        "folio": p["folio"],
        "id": p["id"],
        "filename": web_fn,
        "image": web_rel,
        "width": p["web"]["width"],
        "height": p["web"]["height"],
        "description": p["description"],
        "isPhoto": p["is_photo"]
    })

with open(REGIONS_P, "w", encoding="utf-8") as f:
    json.dump(annotator_data, f, ensure_ascii=False, indent=2)

print(f"Updated {REGIONS_P} successfully with 16 pages!")
