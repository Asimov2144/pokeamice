import os
import cv2
import numpy as np

ARCHIVE_DIR = r"E:\Pokeamice\scan\DREAM 2011.1_prepared\archive"
CROP_DIR = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334\scratch\2011_1_crops"
os.makedirs(CROP_DIR, exist_ok=True)

# Pages to crop
PAGES = [
    # Feature 1: P6 to P17
    "p006_bw_special_intro.jpg",
    "p007_bw_pokemon_making_intro.jpg",
    "p008_bw_pokemon_design_process.jpg",
    "p009_bw_pokemon_reshiram_zekrom.jpg",
    "p010_bw_pokemon_snivy_tepig.jpg",
    "p011_bw_pokemon_emboar_oshawott_samurott.jpg",
    "p012_bw_pokemon_zoroark_victini_audino.jpg",
    "p013_bw_pokemon_emolga_musharna_monkeys.jpg",
    "p014_bw_pokemon_accelgor_escavalier_conkeldurr.jpg",
    "p015_bw_characters_protagonists_juniper.jpg",
    "p016_bw_characters_cheren_bianca_n_ghetsis.jpg",
    "p017_bw_characters_gym_leaders_cilan_elesa_skyla.jpg",
    # Feature 2: P18 to P21
    "p018_bw_sound_interview_kageyama.jpg",
    "p019_bw_sound_roundtable_masuda_ichinose_sato_kageyama.jpg",
    "p020_bw_sound_pokemon_cries_interactive.jpg",
    "p021_bw_art_director_masuda_aesthetic.jpg",
    # Feature 3: P22 to P23
    "p022_bw_special_dialogue_sugimori_masuda_part1.jpg",
    "p023_bw_special_dialogue_sugimori_masuda_part2.jpg",
    # Feature 4: P72 to P75
    "p072_memorial_200_sakurai_masahiro_dialogue_part1.jpg",
    "p073_memorial_200_sakurai_masahiro_dialogue_part2.jpg",
    "p074_memorial_200_sakurai_masahiro_dialogue_part3.jpg",
    "p075_memorial_200_sakurai_masahiro_dialogue_part4.jpg"
]

def imread_unicode(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)

def imwrite_unicode(path, img, quality=90):
    ext = os.path.splitext(path)[1]
    ret, buf = cv2.imencode(ext, img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if ret:
        buf.tofile(path)
        return True
    return False

for filename in PAGES:
    in_path = os.path.join(ARCHIVE_DIR, filename)
    if not os.path.exists(in_path):
        print(f"Warning: {filename} not found!")
        continue
    img = imread_unicode(in_path)
    h, w = img.shape[:2]
    
    # top half (0 to 55%)
    top_h = int(h * 0.55)
    top_img = img[0:top_h, :]
    
    # bottom half (45% to end)
    btm_y = int(h * 0.45)
    btm_img = img[btm_y:h, :]
    
    base_name = os.path.splitext(filename)[0]
    out_top = os.path.join(CROP_DIR, f"{base_name}_top.jpg")
    out_btm = os.path.join(CROP_DIR, f"{base_name}_btm.jpg")
    
    imwrite_unicode(out_top, top_img, quality=90)
    imwrite_unicode(out_btm, btm_img, quality=90)
    print(f"Cropped {filename} -> top & btm ({w}x{top_h}, {w}x{h-btm_y})")

print("All crops generated successfully!")
