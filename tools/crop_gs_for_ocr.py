import os
from PIL import Image

prep_dir = r"E:\Pokeamice\scan\金银攻略_prepared\archive"
out_dir = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334\scratch\gs_ocr_crops"
os.makedirs(out_dir, exist_ok=True)

pages = sorted([f for f in os.listdir(prep_dir) if f.endswith('.jpg')])

for p in pages:
    base = os.path.splitext(p)[0]
    in_path = os.path.join(prep_dir, p)
    with Image.open(in_path) as img:
        w, h = img.size
        
        # If P198 or P199 (staff zukan), let's crop top, middle, bottom
        if "198" in p or "199" in p:
            # 3 rows of staff cards
            # Row 1: y=0 to y=int(h*0.42)
            # Row 2: y=int(h*0.35) to y=int(h*0.72)
            # Row 3: y=int(h*0.65) to y=h
            r1 = img.crop((0, 0, w, int(h * 0.42)))
            r2 = img.crop((0, int(h * 0.35), w, int(h * 0.72)))
            r3 = img.crop((0, int(h * 0.65), w, h))
            
            # Resize width to 1600 for sharp vision reading
            for idx, rimg in enumerate([r1, r2, r3]):
                nw = 1600
                nh = int(rimg.height * (nw / rimg.width))
                rc = rimg.resize((nw, nh), Image.Resampling.LANCZOS)
                rc.save(os.path.join(out_dir, f"{base}_row{idx+1}.jpg"), "JPEG", quality=88)
        else:
            # 2 crops: top 55% and bottom 55%
            top_crop = img.crop((0, 0, w, int(h * 0.55)))
            btm_crop = img.crop((0, int(h * 0.45), w, h))
            
            nw = 1600
            for label, cimg in [("top", top_crop), ("btm", btm_crop)]:
                nh = int(cimg.height * (nw / cimg.width))
                rc = cimg.resize((nw, nh), Image.Resampling.LANCZOS)
                rc.save(os.path.join(out_dir, f"{base}_{label}.jpg"), "JPEG", quality=88)

print(f"Generated OCR crops in {out_dir}")
