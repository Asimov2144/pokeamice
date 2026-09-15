# -*- coding: utf-8 -*-
"""
Image reprocessing and color correction script for CONTINUE Vol.32
(Tajiri Satoshi x Nakagawa Shoko Interview Special)
Source: E:\Pokeamice\scan\Continue Vol.32
Outputs:
  - scan-prepared/continue-vol32-full-20260829/archive/ (300 DPI masters, Q95)
  - scan-prepared/continue-vol32-full-20260829/web/     (2048px height, Q88)
  - assets/images/scan-archive/continue-vol32-20260829/pages/ (for web article reader)
  - scan-manifest.json
"""

import os
import cv2
import numpy as np
import hashlib
import json

SRC_DIR = r"E:\Pokeamice\scan\Continue Vol.32"
BASE_DIR = r"p:\WEBSITE\pokeamice-main (1)\pokeamice-main"

OUT_ARCHIVE = os.path.join(BASE_DIR, "scan-prepared", "continue-vol32-full-20260829", "archive")
OUT_WEB = os.path.join(BASE_DIR, "scan-prepared", "continue-vol32-full-20260829", "web")
OUT_ASSETS = os.path.join(BASE_DIR, "assets", "images", "scan-archive", "continue-vol32-20260829", "pages")
OUT_MANIFEST = os.path.join(BASE_DIR, "scan-prepared", "continue-vol32-full-20260829", "scan-manifest.json")

for d in [OUT_ARCHIVE, OUT_WEB, OUT_ASSETS]:
    os.makedirs(d, exist_ok=True)

def md5_file(filepath):
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def color_correct_page(img, is_color_photo=False):
    """
    White balance and paper tone enhancement:
    - Neutralize paper yellow/green tint
    - Stretch levels so background is clean paper white (around 250-255)
    - Keep black typography solid and crisp
    """
    # Convert to float
    fimg = img.astype(np.float32)
    
    # Analyze paper background using 95th-98th percentile of brighter pixels
    # Sample from margins/non-dark areas
    h, w = img.shape[:2]
    margin_sample = np.concatenate([
        img[:int(h*0.1), :].reshape(-1, 3),
        img[int(h*0.9):, :].reshape(-1, 3),
        img[:, :int(w*0.08)].reshape(-1, 3),
        img[:, int(w*0.92):].reshape(-1, 3)
    ], axis=0)
    
    # Calculate paper white reference
    p95 = np.percentile(margin_sample, 96, axis=0)
    # Target white: [250, 250, 250]
    # Scaling factors per channel (B, G, R)
    scale_b = 250.0 / max(p95[0], 180.0)
    scale_g = 250.0 / max(p95[1], 180.0)
    scale_r = 250.0 / max(p95[2], 180.0)
    
    # Limit extreme scaling to avoid oversaturation
    scale_b = np.clip(scale_b, 0.95, 1.35)
    scale_g = np.clip(scale_g, 0.95, 1.25)
    scale_r = np.clip(scale_r, 0.95, 1.35)
    
    fimg[:, :, 0] *= scale_b
    fimg[:, :, 1] *= scale_g
    fimg[:, :, 2] *= scale_r
    
    # Clip to [0, 255]
    res = np.clip(fimg, 0, 255).astype(np.uint8)
    
    # Contrast curve: slight S-curve to make black text crisper
    if not is_color_photo:
        # For text-heavy pages, increase text blackness slightly
        gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
        # Apply gentle CLAHE or tone mapping
        look_up = np.zeros((256,), dtype=np.uint8)
        for i in range(256):
            if i < 70:
                look_up[i] = int(i * 0.88)
            elif i > 240:
                look_up[i] = min(255, int(240 + (i - 240) * 1.0))
            else:
                look_up[i] = i
        res = cv2.LUT(res, look_up)
    
    return res

PAGES_SPEC = [
    ("page016.jpg", "single", "p016_cover", 16, False, "表紙: 『CONTINUE』Vol.32 (若杉公徳 DMC特別編 / 田尻智×中川翔子 特別対談予告)"),
    ("page019.jpg", "right",  "p100_tajiri_shokotan_title", 100, True, "特輯扉頁: スペシャル対談 田尻智×中川翔子 (下北沢の地で出会ったふたりの大写景)"),
    ("page019.jpg", "left",   "p101_dialogue_p01", 101, False, "対談第1幕: 興奮と歓喜の出会い「神様だ！」・名刺にホウオウ・聖なる灰の仕事"),
    ("page023.jpg", "right",  "p102_dialogue_p02", 102, False, "対談第2幕: ポケモンの聖地・下北沢の青春・ゲームセンターと『ゲームフリーク』同人誌創業期"),
    ("page023.jpg", "left",   "p103_dialogue_p03", 103, False, "対談第3幕: 『ポケットモンスター赤・緑』開発の原点・通信ケーブルのひらめきと交換の魔力"),
    ("page025.jpg", "right",  "p104_photo_shimokitazawa_ds", 104, True, "実景写真大頁: 下北沢の路上でNintendo DSを手にポケモンDPを通信プレイするふたり"),
    ("page025.jpg", "left",   "p105_dialogue_p04", 105, False, "対談第4幕: しょこたんの人生を変えたポケモン・学校のいじめを救ってくれた相棒フシギダネ"),
    ("page026.jpg", "right",  "p106_dialogue_p05", 106, False, "対談第5幕: どく・ゴーストタイプへの偏愛・ゲンガーの怪しげな魅力と深夜の通信対戦"),
    ("page026.jpg", "left",   "p107_dialogue_p06", 107, False, "対談第6幕: 『ダイヤモンド・パール』Wi-Fi世界対戦の衝撃・GTSの地球儀と地下通路の秘密基地"),
    ("page028.jpg", "right",  "p108_dialogue_p07", 108, False, "対談第7幕: ポケモンの命名哲学・カプセルモンスターからポケットモンスターへ"),
    ("page028.jpg", "left",   "p109_dialogue_p08", 109, False, "対談第8幕: 世代を超える対戦の進化・個体値・努力値と開発者が仕掛けた奥深い遊び"),
    ("page029.jpg", "right",  "p110_dialogue_p09", 110, False, "対談第9幕: 親子と世代を繋ぐコミュニケーション・大人になった子どもたちが戻ってくる世界"),
    ("page029.jpg", "left",   "p111_dialogue_p10", 111, False, "対談第10幕 & 結語: ふたりの約束・これからのポケモン・ゲームクリエイター田尻智のまなざし"),
    ("page030.jpg", "right",  "p112_quiz_and_shimokitazawa_walk", 112, True, "特別専欄1: しょこたんのポケモン超難問クイズ ＆ 下北沢聖地散歩ロケ密着写真"),
    ("page030.jpg", "left",   "p113_gamefreak_chronicle_column", 113, False, "特別専欄2: THE VIDEO GAME MAGAZINES CHRONICLE・田尻智の伝説の手作り同人誌『ゲームフリーク』創刊史"),
    ("page032.jpg", "single", "p032_back_cover", 132, False, "表4 (裏表紙): セガ『BLEACH DS 2nd 黒衣ひらめく鎮魂歌』広告 ＆ 太田出版クレジット")
]

manifest = {
    "title": "『CONTINUE』Vol.32（2007年2月発売、太田出版）",
    "feature_title": "スペシャル対談 田尻智 × 中川翔子「ポケモンの生みの親と人生を変えられた少女」",
    "publication_date": "2007-02-24",
    "publisher": "太田出版（Ohta Publishing）",
    "notes": "全9スキャン（7跨页+2单页）严格按日本右开本裁切为16页完整档案，经白平衡色调校正与文字锐化，重建全页高清底本。",
    "total_pages": len(PAGES_SPEC),
    "pages": []
}

print(f"Starting reprocessing of {len(PAGES_SPEC)} pages...")

for idx, (raw_name, side, out_id, folio, is_photo, desc) in enumerate(PAGES_SPEC, 1):
    raw_path = os.path.join(SRC_DIR, raw_name)
    raw_img = cv2.imread(raw_path)
    if raw_img is None:
        print(f"ERROR: Cannot read {raw_path}")
        continue
    
    h, w = raw_img.shape[:2]
    
    if side == "right":
        mid = w // 2
        pimg = raw_img[:, mid:]
    elif side == "left":
        mid = w // 2
        pimg = raw_img[:, :mid]
    else:
        pimg = raw_img
    
    # Color grading
    corrected = color_correct_page(pimg, is_color_photo=is_photo)
    
    # 1. Archive Master (300 DPI equivalent)
    ch, cw = corrected.shape[:2]
    # Set standard master height ~3500px or keep original resolution
    arch_h = min(ch, 3508)
    arch_w = int(round(cw * (arch_h / float(ch))))
    arch_img = cv2.resize(corrected, (arch_w, arch_h), interpolation=cv2.INTER_AREA)
    
    arch_fn = f"{out_id}.jpg"
    arch_path = os.path.join(OUT_ARCHIVE, arch_fn)
    cv2.imwrite(arch_path, arch_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    
    # 2. Web version (2048px height)
    web_h = 2048
    web_w = int(round(cw * (web_h / float(ch))))
    web_img = cv2.resize(corrected, (web_w, web_h), interpolation=cv2.INTER_AREA)
    
    web_fn = f"{out_id}.jpg"
    web_path = os.path.join(OUT_WEB, web_fn)
    cv2.imwrite(web_path, web_img, [cv2.IMWRITE_JPEG_QUALITY, 88])
    
    # Also save to assets directory for web viewer
    asset_path = os.path.join(OUT_ASSETS, web_fn)
    cv2.imwrite(asset_path, web_img, [cv2.IMWRITE_JPEG_QUALITY, 88])
    
    arch_size = os.path.getsize(arch_path)
    web_size = os.path.getsize(web_path)
    arch_md5 = md5_file(arch_path)
    web_md5 = md5_file(web_path)
    
    manifest["pages"].append({
        "order": idx,
        "id": out_id,
        "folio": folio,
        "raw_source": raw_name,
        "side": side,
        "description": desc,
        "is_photo": is_photo,
        "archive": {
            "filename": arch_fn,
            "width": arch_w,
            "height": arch_h,
            "bytes": arch_size,
            "md5": arch_md5
        },
        "web": {
            "filename": web_fn,
            "width": web_w,
            "height": web_h,
            "bytes": web_size,
            "md5": web_md5
        }
    })
    print(f"[{idx:02d}/16] {out_id:34s} (P.{folio:3d}) | web: {web_w}x{web_h} ({web_size//1024} KB) | arch: {arch_w}x{arch_h}")

with open(OUT_MANIFEST, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"Saved manifest to {OUT_MANIFEST}")
print("Image reprocessing completed successfully!")
