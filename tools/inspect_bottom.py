from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageOps

SOURCE_DIR = Path(r"E:\Pokeamice\scan\DREAM 2014.1")
OUT_DIR = Path(r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334\crop_tests\btm_inspect")
OUT_DIR.mkdir(parents=True, exist_ok=True)

test_files = [
    ("page004.jpg", "p006_mega"),
    ("page010.jpg", "p010_mega"),
    ("page011.jpg", "p011_walkthrough"),
    ("page016.jpg", "p016_lumiose"),
    ("page022.jpg", "p020_interview"),
    ("page024.jpg", "p022_interview"),
    ("page030.jpg", "p126_ranking"),
]

for src_name, stem in test_files:
    raw_img = Image.open(SOURCE_DIR / src_name)
    raw_img = ImageOps.exif_transpose(raw_img).convert("RGB")
    arr = np.asarray(raw_img)
    h, w, _ = arr.shape

    # Save a strip of the bottom 600px, width middle 800px
    strip = arr[h - 600:h, int(w * 0.3):int(w * 0.7)]
    # Let's also draw horizontal grid lines every 50px with y coordinate labels
    annotated = strip.copy()
    for y_offset in range(0, 600, 50):
        y_abs = h - 600 + y_offset
        cv2.line(annotated, (0, y_offset), (annotated.shape[1], y_offset), (255, 0, 0), 1)
        cv2.putText(annotated, f"y={y_abs}", (10, y_offset - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    Image.fromarray(annotated).save(OUT_DIR / f"{stem}_btm_strip.jpg", quality=85)
    print(f"Saved {stem}_btm_strip.jpg")
