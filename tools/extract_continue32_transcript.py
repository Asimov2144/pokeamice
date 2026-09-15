# -*- coding: utf-8 -*-
"""
High-precision column-aware OCR and turn reconstruction for CONTINUE Vol.32
(Tajiri Satoshi x Nakagawa Shoko Interview)
"""

import os
import cv2
import json
import re
from rapidocr_onnxruntime import RapidOCR

WEB_DIR = r"p:\WEBSITE\pokeamice-main (1)\pokeamice-main\scan-prepared\continue-vol32-full-20260829\web"
OUT_DIR = r"p:\WEBSITE\pokeamice-main (1)\pokeamice-main\scan-prepared\continue-vol32-full-20260829\ocr_transcriptions"
os.makedirs(OUT_DIR, exist_ok=True)

engine = RapidOCR()

PAGES = [
    ("p101_dialogue_p01.jpg", 101, "対談第1幕: 興奮と歓喜の出会い「神様だ！」・名刺にホウオウ・聖なる灰の仕事"),
    ("p102_dialogue_p02.jpg", 102, "対談第2幕: ポケモンの聖地・下北沢の青春・ゲームセンターと『ゲームフリーク』同人誌創業期"),
    ("p103_dialogue_p03.jpg", 103, "対談第3幕: 『ポケットモンスター赤・緑』開発の原点・通信ケーブルのひらめきと交換の魔力"),
    ("p104_photo_shimokitazawa_ds.jpg", 104, "実景写真大頁: 下北沢の路上でNintendo DSを手にポケモンDPを通信プレイするふたり"),
    ("p105_dialogue_p04.jpg", 105, "対談第4幕: しょこたんの人生を変えたポケモン・学校のいじめを救ってくれた相棒フシギダネ"),
    ("p106_dialogue_p05.jpg", 106, "対談第5幕: どく・ゴーストタイプへの偏愛・ゲンガーの怪しげな魅力と深夜の通信対戦"),
    ("p107_dialogue_p06.jpg", 107, "対談第6幕: 『ダイヤモンド・パール』Wi-Fi世界対戦の衝撃・GTSの地球儀と地下通路の秘密基地"),
    ("p108_dialogue_p07.jpg", 108, "対談第7幕: ポケモンの命名哲学・カプセルモンスターからポケットモンスターへ"),
    ("p109_dialogue_p08.jpg", 109, "対談第8幕: 世代を超える対戦の進化・個体値・努力値と開発者が仕掛けた奥深い遊び"),
    ("p110_dialogue_p09.jpg", 110, "対談第9幕: 親子と世代を繋ぐコミュニケーション・大人になった子どもたちが戻ってくる世界"),
    ("p111_dialogue_p10.jpg", 111, "対談第10幕 & 結語: ふたりの約束・これからのポケモン・ゲームクリエイター田尻智のまなざし"),
    ("p112_quiz_and_shimokitazawa_walk.jpg", 112, "特別専欄1: しょこたんのポケモン超難問クイズ ＆ 下北沢聖地散歩ロケ密着写真"),
    ("p113_gamefreak_chronicle_column.jpg", 113, "特別専欄2: THE VIDEO GAME MAGAZINES CHRONICLE・田尻智の伝説の手作り同人誌『ゲームフリーク』創刊史")
]

print("Running column-aware OCR extraction...")
all_pages_data = []

for fn, folio, desc in PAGES:
    img_p = os.path.join(WEB_DIR, fn)
    img = cv2.imread(img_p)
    if img is None:
        continue
    
    ocr_results, elapse = engine(img)
    boxes = []
    if ocr_results:
        for box, text, score in ocr_results:
            if score > 0.45:
                # box is [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                xs = [pt[0] for pt in box]
                ys = [pt[1] for pt in box]
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                boxes.append({
                    "box": box,
                    "rect": [min_x, min_y, max_x, max_y],
                    "center_x": (min_x + max_x) / 2.0,
                    "center_y": (min_y + max_y) / 2.0,
                    "text": text,
                    "score": float(score)
                })
    
    # In Japanese vertical text (or vertical columns):
    # Overall reading direction across columns is RIGHT-to-LEFT (large X to small X).
    # Within a column, reading direction is top-to-bottom (small Y to large Y).
    # Let's cluster into columns or sort with right-to-left priority:
    # We sort primarily by X (descending) with some tolerance, but more reliably:
    # Sort by center_x descending
    sorted_boxes = sorted(boxes, key=lambda b: (-b["center_x"], b["center_y"]))
    
    all_pages_data.append({
        "filename": fn,
        "folio": folio,
        "description": desc,
        "boxes": sorted_boxes
    })
    print(f"Page {folio}: {len(sorted_boxes)} boxes extracted.")

out_json = os.path.join(OUT_DIR, "continue32_ocr_extracted.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(all_pages_data, f, ensure_ascii=False, indent=2)

print(f"Saved extracted data to {out_json}")
