from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageOps

SOURCE_DIR = Path(r"E:\Pokeamice\scan\DREAM 2014.1")
OUT_DIR = Path(r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334\crop_tests\page_verif")
OUT_DIR.mkdir(parents=True, exist_ok=True)

test_crops = [
    ("p001_cover", "page001.jpg", 214, 3286, 18, 2450),
    ("p008_mega", "page008.jpg", 89, 3160, 18, 2350),
    ("p010_mega", "page010.jpg", 160, 3232, 18, 2340),
    ("p016_lumiose", "page016.jpg", 210, 3288, 18, 2340),
    ("p020_interview", "page022.jpg", 156, 3236, 18, 2340),
    ("p022_interview", "page024.jpg", 178, 3249, 18, 2340),
    ("p126_ranking", "page030.jpg", 222, 3282, 18, 2340),
]

for stem, src_name, t, b, l, r in test_crops:
    raw_img = Image.open(SOURCE_DIR / src_name)
    raw_img = ImageOps.exif_transpose(raw_img).convert("RGB")
    arr = np.asarray(raw_img)
    h, w, _ = arr.shape

    # Crop
    cropped = arr[t:b, l:min(r, w)]
    # Resize height to 1200 for review
    scaled = cv2.resize(cropped, (int(cropped.shape[1] * 1200 / cropped.shape[0]), 1200))
    Image.fromarray(scaled).save(OUT_DIR / f"{stem}_verif.jpg", quality=85)
    print(f"Saved {stem}_verif.jpg (size {cropped.shape[1]}x{cropped.shape[0]})")
