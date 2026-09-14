"""
Crop high-resolution reading segments for:
1. 2000.5 (P82-P85)
2. 2001.4 (P78-P81)
"""

import os
from PIL import Image

scratch = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334\scratch\rumor_ocr_crops"
os.makedirs(scratch, exist_ok=True)

# 2000.5
src_2000_5 = r"E:\Pokeamice\scan\谎言的真相 2000.5_prepared\archive"
for p in ['p082.jpg', 'p083.jpg', 'p084.jpg', 'p085.jpg']:
    im = Image.open(os.path.join(src_2000_5, p))
    w, h = im.size
    im.crop((0, 0, w, int(h * 0.55))).save(os.path.join(scratch, f"2000_5_{p[:-4]}_top.jpg"), quality=95)
    im.crop((0, int(h * 0.45), w, h)).save(os.path.join(scratch, f"2000_5_{p[:-4]}_btm.jpg"), quality=95)
    print(f"2000.5 {p} cropped")

# 2001.4
src_2001_4 = r"E:\Pokeamice\scan\谎言的真相 2001.4_prepared\archive"
for p in ['p078.jpg', 'p079.jpg', 'p080.jpg', 'p081.jpg']:
    im = Image.open(os.path.join(src_2001_4, p))
    w, h = im.size
    im.crop((0, 0, w, int(h * 0.55))).save(os.path.join(scratch, f"2001_4_{p[:-4]}_top.jpg"), quality=95)
    im.crop((0, int(h * 0.45), w, h)).save(os.path.join(scratch, f"2001_4_{p[:-4]}_btm.jpg"), quality=95)
    print(f"2001.4 {p} cropped")

print("All OCR crops generated!")
