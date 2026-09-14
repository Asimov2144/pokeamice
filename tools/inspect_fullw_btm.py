from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageOps

SOURCE_DIR = Path(r"E:\Pokeamice\scan\DREAM 2014.1")
OUT_DIR = Path(r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334\crop_tests\btm_inspect")

for stem, src_name in [("p010", "page010.jpg"), ("p011", "page011.jpg"), ("p020", "page022.jpg"), ("p022", "page024.jpg")]:
    raw_img = Image.open(SOURCE_DIR / src_name)
    raw_img = ImageOps.exif_transpose(raw_img).convert("RGB")
    arr = np.asarray(raw_img)
    h, w, _ = arr.shape

    # full width, bottom 400px
    strip = arr[h - 400:h, :]
    # Resize width to 1200 for easy viewing
    strip_resized = cv2.resize(strip, (1200, 400))
    # draw lines
    for y_rel in range(0, 400, 50):
        y_abs = h - 400 + y_rel
        cv2.line(strip_resized, (0, y_rel), (1200, y_rel), (255, 0, 0), 1)
        cv2.putText(strip_resized, f"y={y_abs}", (10, y_rel + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    Image.fromarray(strip_resized).save(OUT_DIR / f"{stem}_fullw_btm.jpg", quality=85)
