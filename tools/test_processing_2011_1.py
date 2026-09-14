# -*- coding: utf-8 -*-
import cv2
import numpy as np

def load_img(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)

def save_img(path, img, quality=92):
    ext = os.path.splitext(path)[1]
    ret, buf = cv2.imencode(ext, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if ret:
        with open(path, "wb") as f:
            f.write(buf)

import os
scratch_dir = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334\scratch\2011_1_test"
os.makedirs(scratch_dir, exist_ok=True)

test_files = [
    r"E:\Pokeamice\scan\DREAM 2011.1改\DREAM 2011.1改\page001.jpg",
    r"E:\Pokeamice\scan\DREAM 2011.1改\DREAM 2011.1改\page007.jpg",
    r"E:\Pokeamice\scan\DREAM 2011.1改\DREAM 2011.1改\page023.jpg",
]

for f in test_files:
    fname = os.path.basename(f)
    img = load_img(f)
    h, w = img.shape[:2]
    
    # color stretch
    p_low = np.percentile(img, 0.4)
    p_high = np.percentile(img, 99.2)
    stretched = np.clip((img.astype(np.float32) - p_low) * (255.0 / max(1.0, p_high - p_low)), 0, 255).astype(np.uint8)
    
    # unsharp mask
    blur = cv2.GaussianBlur(stretched, (0, 0), 1.2)
    sharpened = cv2.addWeighted(stretched, 1.15, blur, -0.15, 0)
    
    out_p = os.path.join(scratch_dir, fname)
    save_img(out_p, sharpened, 92)
    print(f"Processed {fname} -> {out_p}")
