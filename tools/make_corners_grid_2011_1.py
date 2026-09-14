# -*- coding: utf-8 -*-
import os
import glob
from PIL import Image, ImageDraw

scratch_dir = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334\scratch\2011_1_inspect"
corner_files = sorted(glob.glob(os.path.join(scratch_dir, "*_corners.jpg")))

cols = 4
rows = (len(corner_files) + cols - 1) // cols
cell_w = 450
cell_h = 160
grid_img = Image.new("RGB", (cols * cell_w, rows * cell_h), (20, 20, 20))
draw = ImageDraw.Draw(grid_img)

for idx, f in enumerate(corner_files):
    r = idx // cols
    c = idx % cols
    fname = os.path.basename(f).replace("_corners.jpg", "")
    with Image.open(f) as img:
        img_resized = img.resize((cell_w - 20, cell_h - 40), Image.Resampling.LANCZOS)
        grid_img.paste(img_resized, (c * cell_w + 10, r * cell_h + 30))
    draw.text((c * cell_w + 15, r * cell_h + 8), f"[{idx+1:02d}] {fname}", fill=(255, 255, 100))

out_path = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334\dream_2011_1_corners.jpg"
grid_img.save(out_path, quality=85)
print(f"Saved corners contact sheet to {out_path}")
