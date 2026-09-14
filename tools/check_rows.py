import cv2
import numpy as np
from PIL import Image, ImageOps
from pathlib import Path

SOURCE_DIR = Path(r"E:\Pokeamice\scan\DREAM 2014.1")

for stem, src_name, expected_t in [("p010", "page010.jpg", 164), ("p020", "page022.jpg", 160), ("p006", "page004.jpg", 224)]:
    raw_img = Image.open(SOURCE_DIR / src_name)
    raw_img = ImageOps.exif_transpose(raw_img).convert("RGB")
    arr = np.asarray(raw_img)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape

    # Let's inspect rows from 3200 to 3350
    # Check left 200px, middle 200px, right 200px
    print(f"\n=== {stem} ({src_name}) ===")
    for y in range(3210, 3260, 5):
        row_l = np.mean(gray[y, 50:250])
        row_m = np.mean(gray[y, int(w*0.4):int(w*0.6)])
        row_r = np.mean(gray[y, w-250:w-50])
        print(f"y={y}: left={row_l:.1f}, mid={row_m:.1f}, right={row_r:.1f}")
