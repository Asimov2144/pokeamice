# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np

BRAIN_DIR = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334"
WEB_DIR = r"p:\WEBSITE\pokeamice-main (1)\pokeamice-main\scan-prepared\continue-vol32-full-20260829\web"

PAGES = [
    ("p016_cover.jpg", "Cover", "P.16"),
    ("p100_tajiri_shokotan_title.jpg", "Title Hero", "P.100"),
    ("p101_dialogue_p01.jpg", "Dialogue 01", "P.101"),
    ("p102_dialogue_p02.jpg", "Dialogue 02", "P.102"),
    ("p103_dialogue_p03.jpg", "Dialogue 03", "P.103"),
    ("p104_photo_shimokitazawa_ds.jpg", "DS Photo", "P.104"),
    ("p105_dialogue_p04.jpg", "Dialogue 04", "P.105"),
    ("p106_dialogue_p05.jpg", "Dialogue 05", "P.106"),
    ("p107_dialogue_p06.jpg", "Dialogue 06", "P.107"),
    ("p108_dialogue_p07.jpg", "Dialogue 07", "P.108"),
    ("p109_dialogue_p08.jpg", "Dialogue 08", "P.109"),
    ("p110_dialogue_p09.jpg", "Dialogue 09", "P.110"),
    ("p111_dialogue_p10.jpg", "Dialogue 10", "P.111"),
    ("p112_quiz_and_shimokitazawa_walk.jpg", "Quiz & Walk", "P.112"),
    ("p113_gamefreak_chronicle_column.jpg", "GF Chronicle", "P.113"),
    ("p032_back_cover.jpg", "Back Cover", "P.132")
]

grid_cols = 4
grid_rows = 4
cell_w = 340
cell_h = 480
margin = 20
header_h = 90

sheet_w = grid_cols * cell_w + (grid_cols + 1) * margin
sheet_h = grid_rows * cell_h + (grid_rows + 1) * margin + header_h

sheet = np.full((sheet_h, sheet_w, 3), 26, dtype=np.uint8)

cv2.putText(sheet, "CONTINUE Vol.32 (2007.02) Ohta Publishing - 16 Pages Audit",
            (margin + 10, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(sheet, "Special Dialogue: Tajiri Satoshi x Nakagawa Shoko in Shimokitazawa (P.100-P.113 Complete)",
            (margin + 10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (160, 210, 255), 1, cv2.LINE_AA)

for i, (fn, title, page_lbl) in enumerate(PAGES):
    r = i // grid_cols
    c = i % grid_cols

    x0 = margin + c * (cell_w + margin)
    y0 = header_h + margin + r * (cell_h + margin)

    img_p = os.path.join(WEB_DIR, fn)
    img = cv2.imread(img_p)
    if img is not None:
        th, tw = img.shape[:2]
        max_tw = cell_w - 20
        max_th = cell_h - 45
        scale = min(max_tw / float(tw), max_th / float(th))
        nw, nh = int(round(tw * scale)), int(round(th * scale))
        resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)

        px = x0 + (cell_w - nw) // 2
        py = y0 + 10 + (max_th - nh) // 2

        sheet[py:py+nh, px:px+nw] = resized
        cv2.rectangle(sheet, (px-1, py-1), (px+nw+1, py+nh+1), (65, 65, 65), 1)

    label = f"#{i+1:02d} {page_lbl} {title}"
    cv2.putText(sheet, label, (x0 + 10, y0 + cell_h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1, cv2.LINE_AA)

out_contact = os.path.join(BRAIN_DIR, "continue_vol32_contact_sheet.jpg")
cv2.imwrite(out_contact, sheet, [cv2.IMWRITE_JPEG_QUALITY, 90])
print(f"Contact sheet saved to {out_contact}")
