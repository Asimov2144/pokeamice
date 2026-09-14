# -*- coding: utf-8 -*-
"""
Script to analyze the exact paper bounds (top, bottom, left, right)
for all 50 pages of:
『ポケモン誕生秘話 ポケットモンスターブラック・ホワイト 完全総集版』
"""

import os
import glob
import cv2
import numpy as np

SRC_DIR = r"E:\Pokeamice\scan\黑白 诞生秘话"

# 50 unique pages
PAGE_SPECS = [
    ("page004.jpg", 1,   "p001_cover", "Cover"),
    ("page005.jpg", 3,   "p003_contents", "P.3"),
    ("page006.jpg", 4,   "p004_poll_pokemon_top10_part1", "P.4"),
    ("page007.jpg", 5,   "p005_poll_pokemon_top10_part2", "P.5"),
    ("page008.jpg", 6,   "p006_poll_pokemon_11_20", "P.6"),
    ("page009.jpg", 7,   "p007_poll_pokemon_21_50_ranking", "P.7"),
    ("page010.jpg", 8,   "p008_poll_character_top3", "P.8"),
    ("page011.jpg", 9,   "p009_poll_character_4_15_ranking", "P.9"),
    ("page012.jpg", 10,  "p010_reader_postcards_part1", "P.10"),
    ("page013.jpg", 11,  "p011_reader_postcards_part2", "P.11"),
    ("page014.jpg", 12,  "p012_reader_postcards_part3", "P.12"),
    ("page015.jpg", 13,  "p013_reader_postcards_part4", "P.13"),
    ("page016.jpg", 14,  "p014_special_top3_pokemon_chandelure", "P.14"),
    ("page018.jpg", 15,  "p015_special_top3_pokemon_whimsicott_reshiram", "P.15"),
    ("page019.jpg", 16,  "p016_special_top3_character_n", "P.16"),
    ("page020.jpg", 17,  "p017_special_top3_character_subway_masters", "P.17"),
    ("page021.jpg", 18,  "p018_making_pokemon_roundtable_intro", "P.18"),
    ("page022.jpg", 19,  "p019_making_pokemon_snivy_tepig", "P.19"),
    ("page023.jpg", 20,  "p020_making_pokemon_emboar_oshawott_samurott", "P.20"),
    ("page024.jpg", 21,  "p021_making_pokemon_patrat_pidove_monkeys", "P.21"),
    ("page025.jpg", 22,  "p022_making_pokemon_cinccino_munna_karrablast_shelmet", "P.22"),
    ("page026.jpg", 23,  "p023_making_pokemon_audino_whimsicott_lilligant_emolga_sigilyph", "P.23"),
    ("page027.jpg", 24,  "p024_making_pokemon_chandelure_conkeldurr_klinklang", "P.24"),
    ("page028.jpg", 25,  "p025_making_pokemon_garbodor_sawsbuck_beartic", "P.25"),
    ("page029.jpg", 26,  "p026_making_pokemon_bisharp_eelektross_heatmor_durant", "P.26"),
    ("page030.jpg", 27,  "p027_making_pokemon_haxorus_darmanitan_jellicent", "P.27"),
    ("page031.jpg", 28,  "p028_making_pokemon_tympole_stunfisk_cofagrigus_crustle", "P.28"),
    ("page032.jpg", 29,  "p029_making_pokemon_golurk_vanilluxe_basculin", "P.29"),
    ("page033.jpg", 30,  "p030_making_pokemon_volcarona_braviary_mandibuzz", "P.30"),
    ("page034.jpg", 31,  "p031_making_pokemon_amoonguss_ferrothorn_zoroark_scrafty", "P.31"),
    ("page035.jpg", 32,  "p032_making_pokemon_mienshao_hydreigon_victini", "P.32"),
    ("page036.jpg", 33,  "p033_making_pokemon_reshiram_zekrom", "P.33"),
    ("page037.jpg", 34,  "p034_making_pokemon_forces_of_nature_throh_sawk", "P.34"),
    ("page038.jpg", 35,  "p035_making_pokemon_swords_of_justice_favorites", "P.35"),
    ("page039.jpg", 36,  "p036_making_pokemon_summary_favorite_poll", "P.36"),
    ("page040.jpg", 37,  "p037_special_single_illustration_gallery", "P.37"),
    ("page041.jpg", 38,  "p038_making_characters_protagonists_fennel", "P.38"),
    ("page042.jpg", 39,  "p039_making_characters_juniper_cheren_bianca", "P.39"),
    ("page043.jpg", 40,  "p040_making_characters_n_ghetsis_grunts", "P.40"),
    ("page044.jpg", 41,  "p041_making_characters_gym_leaders_cilan_burgh_lenora", "P.41"),
    ("page045.jpg", 42,  "p042_making_characters_gym_leaders_clay_skyla_elesa", "P.42"),
    ("page046.jpg", 43,  "p043_making_characters_gym_leaders_brycen_iris_drayden", "P.43"),
    ("page047.jpg", 44,  "p044_making_characters_elite_four_grimsley_shauntal", "P.44"),
    ("page048.jpg", 45,  "p045_making_characters_elite_four_marshal_caitlin", "P.45"),
    ("page049.jpg", 46,  "p046_making_characters_subway_masters_alder", "P.46"),
    ("page050.jpg", 47,  "p047_pokemon_do_special_movie_distributions", "P.47"),
    ("page051.jpg", 48,  "p048_pokemon_do_special_pgl_pokemon_cafe", "P.48"),
    ("page053.jpg", 49,  "p049_pokemon_do_special_tcg_victini_decks", "P.49"),
    ("page054.jpg", 50,  "p050_pokemon_do_special_tcg_tournament_colophon", "P.50"),
    ("page055.jpg", 999, "p999_back_cover", "Back Cover")
]

def analyze_page(src_file):
    img = cv2.imdecode(np.fromfile(os.path.join(SRC_DIR, src_file), dtype=np.uint8), cv2.IMREAD_COLOR)
    h600, w600 = img.shape[:2]
    # Work at 300 DPI for fast & robust edge detection
    im300 = cv2.resize(img, (int(round(w600 * 0.5)), int(round(h600 * 0.5))), interpolation=cv2.INTER_AREA)
    h300, w300 = im300.shape[:2]
    gray = cv2.cvtColor(im300, cv2.COLOR_BGR2GRAY)
    
    # 1. Top Edge Detection (y in [100..450] at 300 DPI)
    # Sobel vertical gradient
    sobely = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))
    
    # Check horizontal strip in middle 60% of width
    mid_w_start = int(w300 * 0.2)
    mid_w_end = int(w300 * 0.8)
    
    # Scanner bed is white (> 220). The paper boundary has a drop in intensity or a sharp shadow line.
    top_zone = sobely[100:500, mid_w_start:mid_w_end]
    grad_top = (np.percentile(top_zone, 85, axis=1) + np.mean(top_zone, axis=1)) / 2.0
    
    # Also check gray level drop from scanner white
    gray_top = np.mean(gray[100:500, mid_w_start:mid_w_end], axis=1)
    
    # Bottom Edge Detection (y in [3000..h300-50])
    btm_start_y = 2950
    btm_zone = sobely[btm_start_y:h300-30, mid_w_start:mid_w_end]
    grad_btm = (np.percentile(btm_zone, 85, axis=1) + np.mean(btm_zone, axis=1)) / 2.0
    gray_btm = np.mean(gray[btm_start_y:h300-30, mid_w_start:mid_w_end], axis=1)
    
    # Find candidate peaks
    # Filter top peaks where gradient is strong OR gray value transitions from white (>225) to page (<215)
    top_candidates = []
    for y_idx in range(len(grad_top)):
        score = grad_top[y_idx]
        y_abs = y_idx + 100
        # If there's a drop from white
        if y_idx > 5 and gray_top[y_idx-5] > 220 and gray_top[y_idx] < 200:
            score += 30.0
        if score > 15.0:
            top_candidates.append((y_abs, score))
            
    btm_candidates = []
    for y_idx in range(len(grad_btm)):
        score = grad_btm[y_idx]
        y_abs = y_idx + btm_start_y
        if y_idx < len(gray_btm) - 5 and gray_btm[y_idx] < 200 and gray_btm[y_idx+5] > 220:
            score += 30.0
        if score > 15.0:
            btm_candidates.append((y_abs, score))
            
    # Pair search: find (tp, bp) that maximizes score and gives dist close to ~3070 (range 3050..3095)
    best_pair = None
    best_score = -1e9
    for tp, s_top in top_candidates:
        for bp, s_btm in btm_candidates:
            dist = bp - tp
            if 3050 <= dist <= 3100:
                s = s_top + s_btm - abs(dist - 3072) * 0.8
                if s > best_score:
                    best_score = s
                    best_pair = (tp, bp, dist)
                    
    # Left and Right edges:
    # Outer edge vs Gutter edge
    # Let's inspect horizontal gradient (sobelx)
    sobelx = np.abs(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3))
    
    # Check left edge in [10..250]
    grad_left = np.mean(sobelx[500:2500, 10:250], axis=0) + np.percentile(sobelx[500:2500, 10:250], 85, axis=0)
    # Check right edge in [w300-250..w300-10]
    grad_right = np.mean(sobelx[500:2500, w300-250:w300-10], axis=0) + np.percentile(sobelx[500:2500, w300-250:w300-10], 85, axis=0)
    
    best_l = np.argmax(grad_left) + 10 if np.max(grad_left) > 15 else 18
    best_r = w300 - 250 + np.argmax(grad_right) if np.max(grad_right) > 15 else w300 - 18
    
    return best_pair, (best_l, best_r), (h300, w300)

print(f"{'Page':<8} {'File':<14} {'Top':<6} {'Btm':<6} {'Height':<8} {'Left':<6} {'Right':<6} {'Width':<8} {'Status'}")
print("-" * 75)

success_count = 0
results = []
for src_file, mag_p, stem, desc in PAGE_SPECS:
    pair, lr, dims = analyze_page(src_file)
    p_label = f"P.{mag_p:02d}" if mag_p not in [1, 999] else ("Cover" if mag_p==1 else "Back")
    if pair:
        tp, bp, dist = pair
        bl, br = lr
        w = br - bl
        results.append((src_file, mag_p, stem, tp, bp, dist, bl, br, w))
        success_count += 1
        print(f"{p_label:<8} {src_file:<14} {tp:<6} {bp:<6} {dist:<8} {bl:<6} {br:<6} {w:<8} OK")
    else:
        results.append((src_file, mag_p, stem, None, None, None, None, None, None))
        print(f"{p_label:<8} {src_file:<14} {'FAIL':<6} {'FAIL':<6} {'FAIL':<8} {'FAIL':<6} {'FAIL':<6} {'FAIL':<8} NO PAIR")

print("-" * 75)
print(f"Total analyzed: {len(PAGE_SPECS)}, Paired: {success_count}/{len(PAGE_SPECS)}")
