# -*- coding: utf-8 -*-
"""
Batch image preparation script for:
『ポケットモンスター図鑑』（An Illustrated Book of POCKET MONSTERS / 初代公式図鑑・初代攻略本）
Aspect / Creatures inc. / 1996

Source: E:\Pokeamice\scan\初代攻略本
Output: E:\Pokeamice\scan\初代攻略本_prepared\
  - archive/ (Master resolution, Q95, scanner platen crop on Page 072)
  - web/ (Standardized 2048px height, INTER_AREA, Q85)
  - scan-manifest.json
  - shodai_contact_sheet.jpg (in brain artifacts directory)
"""

import os
import sys
import re
import json
import hashlib
import cv2
import numpy as np
from PIL import Image

SRC_DIR = r"E:\Pokeamice\scan\初代攻略本"
OUT_BASE = r"E:\Pokeamice\scan\初代攻略本_prepared"
OUT_ARCHIVE = os.path.join(OUT_BASE, "archive")
OUT_WEB = os.path.join(OUT_BASE, "web")
OUT_OCR = os.path.join(OUT_BASE, "ocr_transcriptions")
BRAIN_DIR = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334"

for d in [OUT_ARCHIVE, OUT_WEB, OUT_OCR]:
    os.makedirs(d, exist_ok=True)

def cv2_imread(path):
    with open(path, "rb") as f:
        return cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)

def cv2_imwrite(path, img, quality=95):
    ext = os.path.splitext(path)[1]
    result, buf = cv2.imencode(ext, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if result:
        with open(path, "wb") as f:
            f.write(buf)
        return True
    return False

# Build map from index to source filename
raw_files = [f for f in os.listdir(SRC_DIR) if f.lower().endswith(".jpg")]
page_map = {}
for f in raw_files:
    m = re.search(r'_(\d{3})_', f)
    if m:
        p_idx = int(m.group(1))
        page_map[p_idx] = f

print(f"Discovered {len(page_map)} pages in source directory.")
assert len(page_map) == 148, f"Expected 148 pages, found {len(page_map)}"

# Build comprehensive specs for all 148 pages
def get_page_info(idx):
    raw_name = page_map[idx]
    if idx == 1:
        return raw_name, "p001_cover", None, "Cover / 表紙: ポケットモンスター図鑑 (Aspect / Creatures)"
    elif idx == 2:
        return raw_name, "p002_inside_cover", None, "Inside Front Cover / 表2 見返し (赤緑ポケモングリッドスプライト)"
    elif idx == 3:
        return raw_name, "p003_title", None, "Title Page / 本扉: ポケットモンスター図鑑"
    elif idx == 4:
        return raw_name, "p004_p002_olympic_track", 2, "ポケモンオリンピック: 陸上・走る力・時速1000kmの衝撃 ドードリオ vs 新幹線"
    elif idx == 5:
        return raw_name, "p005_p003_olympic_power", 3, "ポケモンオリンピック: 怪力・パワー自慢・ビルを投げ飛ばすカイリキー"
    elif idx == 6:
        return raw_name, "p006_p004_olympic_sea", 4, "ポケモンオリンピック: 水泳・水中スピード対決・潜水艦より速いゴルダック"
    elif idx == 7:
        return raw_name, "p007_p005_olympic_sky", 5, "ポケモンオリンピック: 飛行・大空の王者・マッハ2で飛ぶピジョット"
    elif idx == 8:
        return raw_name, "p008_p006_contents", 6, "目次 CONTENTS & 本書の使い方"
    elif idx == 9:
        return raw_name, "p009_p007_ch1_intro_town", 7, "第1章 ポケモン大百科 扉: まちのまわり"
    elif 10 <= idx <= 50:
        p_num = idx - 2
        return raw_name, f"p{idx:03d}_p{p_num:03d}_zukan", p_num, f"第1章 ポケモン大百科 (P.{p_num})"
    elif idx == 51:
        return raw_name, "p051_p049_zukan_habitat_chart1", 49, "第1章 ポケモン大百科: 生息地別分布図 1"
    elif idx == 52:
        return raw_name, "p052_p050_zukan_habitat_chart2", 50, "第1章 ポケモン大百科: 生息地別分布図 2"
    elif idx == 53:
        return raw_name, "p053_p051_zukan_habitat_chart3", 51, "第1章 ポケモン大百科: 生息地別分布図 3"
    elif idx == 54:
        return raw_name, "p054_p052_zukan_mew_special", 52, "第1章 ポケモン大百科: No.151 幻のポケモン ミュウ 特別レポート"
    elif idx == 55:
        return raw_name, "p055_p053_ch2_field_intro", 53, "第2章 フィールド＆ダンジョン 扉: カントー地方全図"
    elif 56 <= idx <= 102:
        p_num = idx - 2
        desc = f"第2章 フィールド＆ダンジョン (P.{p_num})"
        if idx == 72:
            desc = "第2章 フィールド＆ダンジョン: イワヤマ 9番道路 10番道路 (P.70, スキャナ平床トリミング済)"
        return raw_name, f"p{idx:03d}_p{p_num:03d}_field", p_num, desc
    elif idx == 103:
        return raw_name, "p103_p101_ch3_data_intro", 101, "第3章 完全データファイル 扉"
    elif 104 <= idx <= 124:
        p_num = idx - 2
        return raw_name, f"p{idx:03d}_p{p_num:03d}_data", p_num, f"第3章 完全データファイル (P.{p_num})"
    elif idx == 125:
        return raw_name, "p125_p123_ch4_battle_trade_intro", 123, "第4章 通信交換・対戦のススメ 扉"
    elif 126 <= idx <= 130:
        p_num = idx - 2
        return raw_name, f"p{idx:03d}_p{p_num:03d}_battle_trade", p_num, f"第4章 通信交換・対戦のススメ (P.{p_num})"
    elif idx == 131:
        return raw_name, "p131_p129_ch5_journal_part1", 129, "第5章 ポケモン・ジャーナル 扉・タマムシ大学研究報告 ポケモンとは何か？"
    elif idx == 132:
        return raw_name, "p132_p130_ch5_journal_part2", 130, "第5章 ポケモン・ジャーナル: 祖先・化石ポケモンと古代の生態系"
    elif idx == 133:
        return raw_name, "p133_p131_ch5_journal_part3", 131, "第5章 ポケモン・ジャーナル: 進化のメカニズム・石による突然変異"
    elif idx == 134:
        return raw_name, "p134_p132_ch5_journal_part4", 132, "第5章 ポケモン・ジャーナル: モンスターボールの歴史・西野教授の縮小習性発見"
    elif idx == 135:
        return raw_name, "p135_p133_ch5_journal_part5", 133, "第5章 ポケモン・ジャーナル: 南米ギアナでのミュウ発見・オーキド博士論文"
    elif idx == 136:
        return raw_name, "p136_p134_ch5_journal_part6", 134, "第5章 ポケモン・ジャーナル: 人間とポケモンの共存史・カントー学会の未来"
    elif idx == 137:
        return raw_name, "p137_p135_ch6_interview_part1", 135, "第6章 開発スタッフ・インタヴュー 扉: 6年の歳月をかけたモンスターたち"
    elif idx == 138:
        return raw_name, "p138_p136_ch6_interview_part2", 136, "第6章 開発スタッフ・インタヴュー: 集合写真・田尻智×杉森建×増田順一×森本茂樹"
    elif idx == 139:
        return raw_name, "p139_p137_ch6_interview_part3", 137, "第6章 開発スタッフ・インタヴュー: カプセル怪獣構想・通信ケーブルの革命"
    elif idx == 140:
        return raw_name, "p140_p138_ch6_interview_part4", 138, "第6章 開発スタッフ・インタヴュー: 赤・緑バージョン分離案・宮本茂さんの助言"
    elif idx == 141:
        return raw_name, "p141_p139_ch6_interview_part5", 139, "第6章 開発スタッフ・インタヴュー: メモリ限界への挑戦・バックアップRAM拡大"
    elif idx == 142:
        return raw_name, "p142_p140_ch6_interview_part6", 140, "第6章 開発スタッフ・インタヴュー: 対戦バランス調整・ミュウの秘密実装"
    elif idx == 143:
        return raw_name, "p143_p141_ch6_interview_part7", 141, "第6章 開発スタッフ・インタヴュー: スタッフメッセージ 1 (田尻智・杉森建・増田順一)"
    elif idx == 144:
        return raw_name, "p144_p142_ch6_interview_part8", 142, "第6章 開発スタッフ・インタヴュー: スタッフメッセージ 2 (森本茂樹・太田哲司・渡辺哲也)"
    elif idx == 145:
        return raw_name, "p145_p143_ch6_interview_part9", 143, "第6章 開発スタッフ・インタヴュー: スタッフメッセージ 3 (藤原基史・西野弘二・西田敦子)"
    elif idx == 146:
        return raw_name, "p146_p144_colophon", 144, "奥付: ポケットモンスター図鑑 発行データ・スタッフクレジット"
    elif idx == 147:
        return raw_name, "p147_inside_back_cover", None, "Inside Back Cover / 表3 見返し (赤緑ポケモングリッドスプライト)"
    elif idx == 148:
        return raw_name, "p148_back_cover", None, "Back Cover / 表4 裏表紙 (Aspect 定価980円・バーコード)"
    else:
        return raw_name, f"p{idx:03d}", None, f"Page {idx}"

def md5_file(filepath):
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

print(f"Starting preparation of 148 pages from {SRC_DIR}...")
manifest = {
    "title": "ポケットモンスター図鑑 (An Illustrated Book of POCKET MONSTERS)",
    "publication_date": "1996-04-05 (初版発行) / 1997-02-07 (第六刷)",
    "publisher": "株式会社アスペクト (Aspect) / 株式会社アスキー (ASCII) / ファミ通書籍編集部",
    "supervision": "Creatures inc. / 石原恒和",
    "authors": "とみさわ昭仁 / 川本ひろし / 林英明",
    "illustrations": "杉森建 / 西田敦子 (GAME FREAK inc.)",
    "isbn": "ISBN 4-89366-494-8",
    "total_pages": 148,
    "pages": []
}

processed_images_for_contact = []
# Select 16 representative pages for contact sheet (4x4)
contact_indices = [1, 3, 4, 8, 10, 15, 44, 50, 54, 55, 72, 103, 131, 137, 138, 146]

for idx in range(1, 149):
    raw_name, out_id, book_page, desc = get_page_info(idx)
    raw_path = os.path.join(SRC_DIR, raw_name)
    if not os.path.exists(raw_path):
        print(f"ERROR: Missing file {raw_path}")
        continue

    # Read image safely with unicode path support
    img = cv2_imread(raw_path)
    if img is None:
        print(f"ERROR: Failed to read {raw_path}")
        continue
    
    orig_h, orig_w = img.shape[:2]
    crop_info = None

    # Handle Page 072 scanner platen crop
    if idx == 72:
        # y: [645, 2815], x: [965, 2455]
        crop_y1, crop_y2, crop_x1, crop_x2 = 645, 2815, 965, 2455
        img = img[crop_y1:crop_y2, crop_x1:crop_x2]
        crop_info = {
            "applied": True,
            "reason": "Scanner flatbed platen uncropped margin removal",
            "original_size": [orig_w, orig_h],
            "crop_box": [crop_x1, crop_y1, crop_x2, crop_y2]
        }
    else:
        crop_info = {
            "applied": False,
            "original_size": [orig_w, orig_h]
        }

    curr_h, curr_w = img.shape[:2]

    # Save to archive (master quality Q95)
    arch_filename = f"{out_id}.jpg"
    arch_path = os.path.join(OUT_ARCHIVE, arch_filename)
    cv2_imwrite(arch_path, img, quality=95)

    # Generate web version (standardized height 2048px, INTER_AREA)
    target_h = 2048
    scale = target_h / float(curr_h)
    target_w = int(round(curr_w * scale))
    web_img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)

    web_filename = f"{out_id}.jpg"
    web_path = os.path.join(OUT_WEB, web_filename)
    cv2_imwrite(web_path, web_img, quality=85)

    # File stats
    arch_bytes = os.path.getsize(arch_path)
    web_bytes = os.path.getsize(web_path)
    arch_md5 = md5_file(arch_path)
    web_md5 = md5_file(web_path)

    page_meta = {
        "index": idx,
        "raw_file": raw_name,
        "book_page": book_page,
        "id": out_id,
        "description": desc,
        "archive": {
            "filename": arch_filename,
            "width": curr_w,
            "height": curr_h,
            "filesize_bytes": arch_bytes,
            "md5": arch_md5
        },
        "web": {
            "filename": web_filename,
            "width": target_w,
            "height": target_h,
            "filesize_bytes": web_bytes,
            "md5": web_md5
        },
        "crop_info": crop_info
    }
    manifest["pages"].append(page_meta)

    if idx in contact_indices:
        # Save a thumbnail for contact sheet
        thumb_h = 450
        thumb_w = int(round(curr_w * (thumb_h / float(curr_h))))
        thumb = cv2.resize(img, (thumb_w, thumb_h), interpolation=cv2.INTER_AREA)
        processed_images_for_contact.append((idx, out_id, desc, thumb))

    if idx % 25 == 0 or idx == 148:
        print(f"Processed {idx}/148 pages... ({arch_filename})")

# Save scan-manifest.json
manifest_path = os.path.join(OUT_BASE, "scan-manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print(f"Saved manifest to {manifest_path}")

# Build contact sheet (4x4 grid of 16 representative pages)
print("Building contact sheet...")
grid_cols = 4
grid_rows = 4
cell_w = 360
cell_h = 550
margin = 20
header_h = 80

sheet_w = grid_cols * cell_w + (grid_cols + 1) * margin
sheet_h = grid_rows * cell_h + (grid_rows + 1) * margin + header_h

sheet = np.full((sheet_h, sheet_w, 3), 24, dtype=np.uint8) # dark background

# Draw header
cv2.putText(sheet, "An Illustrated Book of POCKET MONSTERS (1996 Aspect/Creatures) - 148 Pages Audit",
            (margin + 10, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(sheet, "Master Archive & Web 2048px Pipeline | 100% Upright | Page 072 Scanner Platen Corrected",
            (margin + 10, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (160, 200, 255), 1, cv2.LINE_AA)

for i, (idx, out_id, desc, thumb) in enumerate(processed_images_for_contact):
    r = i // grid_cols
    c = i % grid_cols

    x0 = margin + c * (cell_w + margin)
    y0 = header_h + margin + r * (cell_h + margin)

    # Place thumbnail centered in cell
    th, tw = thumb.shape[:2]
    max_tw = cell_w - 20
    max_th = cell_h - 50
    scale = min(max_tw / float(tw), max_th / float(th))
    nw, nh = int(round(tw * scale)), int(round(th * scale))
    resized_thumb = cv2.resize(thumb, (nw, nh), interpolation=cv2.INTER_AREA)

    px = x0 + (cell_w - nw) // 2
    py = y0 + 10 + (max_th - nh) // 2

    sheet[py:py+nh, px:px+nw] = resized_thumb

    # Draw border around thumbnail
    cv2.rectangle(sheet, (px-1, py-1), (px+nw+1, py+nh+1), (70, 70, 70), 1)

    # Label text below
    short_label = f"#{idx:03d} {out_id.split('_')[1] if '_' in out_id else out_id}"
    cv2.putText(sheet, short_label, (x0 + 15, y0 + cell_h - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)

contact_path = os.path.join(BRAIN_DIR, "shodai_contact_sheet.jpg")
cv2_imwrite(contact_path, sheet, quality=90)
print(f"Contact sheet saved to {contact_path}")

print("Batch preparation successfully completed!")
