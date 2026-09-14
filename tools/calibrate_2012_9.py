# -*- coding: utf-8 -*-
import cv2
import os
import glob
import numpy as np

RAW_DIR = r"E:\Pokeamice\scan\DREAM 2012.9"
SCRATCH_DIR = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334\scratch"

# Definitions: (filename, stem, page_num, parity)
PAGES = [
    ("page001.jpg", "p001_cover", 1, "single"),
    ("page003.jpg", "p003_contents", 3, "odd"),
    ("page004.jpg", "p012_b2w2_interview_intro", 12, "even"),
    ("page006.jpg", "p013_b2w2_interview_unno", 13, "odd"),
    ("page008.jpg", "p014_b2w2_interview_masuda", 14, "even"),
    ("page009.jpg", "p015_b2w2_interview_legendary", 15, "odd"),
    ("page010.jpg", "p016_b2w2_interview_sound", 16, "even"),
    ("page012.jpg", "p017_b2w2_guide_new_elements", 17, "odd"),
    ("page013.jpg", "p054_palutena_special_intro", 54, "even"),
    ("page014.jpg", "p055_palutena_questionnaire_1", 55, "odd"),
    ("page015.jpg", "p056_palutena_questionnaire_2", 56, "even"),
    ("page017.jpg", "p057_palutena_qa_1", 57, "odd"),
    ("page018.jpg", "p058_palutena_qa_2", 58, "even"),
    ("page019.jpg", "p059_palutena_qa_3", 59, "odd"),
    ("page020.jpg", "p060_palutena_dialogue_sakurai_hirabayashi_1", 60, "even"),
    ("page021.jpg", "p061_palutena_dialogue_sakurai_hirabayashi_2", 61, "odd"),
    ("page022.jpg", "p062_palutena_dialogue_sakurai_hirabayashi_3", 62, "even"),
    ("page023.jpg", "p063_palutena_dialogue_sakurai_hirabayashi_4", 63, "odd"),
    ("page024.jpg", "p064_gakkyoku_damashii_palutena_1", 64, "even"),
    ("page025.jpg", "p065_gakkyoku_damashii_palutena_2", 65, "odd"),
    ("page026.jpg", "p072_pokemon_next_genesect", 72, "even"),
    ("page027.jpg", "p073_pokemon_next_tetta", 73, "odd"),
    ("page028.jpg", "p126_sales_ranking", 126, "even"),
    ("page029.jpg", "p999_back_cover", 999, "single"),
]

# Let's calibrate crops at 300 DPI (downsampled 2x from 600 DPI)
# Target height standard: ~3072px.
# Odd pages: crop spine from left (~90..115px), keep right to w3 - 10px.
# Even pages: keep left (x1 ~ 15..20px), crop spine from right (~w3 - 90..115px).
# Single pages (cover / back cover): crop 15px margins.

crops = {}

for fname, stem, pnum, ptype in PAGES:
    p = os.path.join(RAW_DIR, fname)
    im = cv2.imread(p)
    h_raw, w_raw = im.shape[:2]
    w3, h3 = w_raw // 2, h_raw // 2
    
    # Defaults
    y1 = 6
    y2 = h3 - 6
    
    # Specific height calibrations for extended scans:
    if fname == "page001.jpg": # 2487x3120
        y1, y2 = 22, 3094 # H=3072
        x1, x2 = 18, 2465
    elif fname == "page013.jpg": # 2413x3149
        y1, y2 = 58, 3130 # H=3072
        x1, x2 = 18, 2330
    elif fname == "page015.jpg": # 2422x3214
        y1, y2 = 82, 3154 # H=3072
        x1, x2 = 18, 2330
    elif fname == "page017.jpg": # 2372x3140
        y1, y2 = 52, 3124 # H=3072
        x1, x2 = 100, 2360
    elif fname == "page028.jpg": # 2412x3286
        y1, y2 = 60, 3135 # H=3075
        x1, x2 = 18, 2330
    elif ptype == "single":
        x1 = 18
        x2 = w3 - 18
        # adjust y to 3072 if needed
        if h3 > 3080:
            diff = h3 - 3072
            y1 = diff // 2
            y2 = y1 + 3072
        else:
            y1 = 4
            y2 = h3 - 4
    elif ptype == "odd":
        # Spine is on LEFT
        x1 = 110 # remove spine gutter
        x2 = w3 - 12
        if h3 > 3080:
            diff = h3 - 3072
            y1 = diff // 2
            y2 = y1 + 3072
        else:
            y1 = 4
            y2 = h3 - 4
    elif ptype == "even":
        # Spine is on RIGHT
        x1 = 18
        x2 = w3 - 110 # remove spine gutter
        if h3 > 3080:
            diff = h3 - 3072
            y1 = diff // 2
            y2 = y1 + 3072
        else:
            y1 = 4
            y2 = h3 - 4
            
    crops[fname] = [x1, y1, x2, y2]
    ch = y2 - y1
    cw = x2 - x1
    print(f"{fname:12s} ({stem:35s}): crop=[{x1}, {y1}, {x2}, {y2}] -> {cw}x{ch}")
