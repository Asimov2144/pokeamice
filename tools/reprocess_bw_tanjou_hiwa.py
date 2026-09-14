# -*- coding: utf-8 -*-
"""
Reprocessing script for:
『ポケモン誕生秘話 ポケットモンスターブラック・ホワイト 完全総集版』
(Nintendo DREAM 2011年7月号 特別付録 小冊子)

Calibrates exact top/bottom paper boundaries using Sobel edge analysis
to completely remove scanner bed margins while preserving all headers,
footers, page numbers, and spine tabs.
"""

import os
import sys
import json
import hashlib
import time
import cv2
import numpy as np

SRC_DIR = r"E:\Pokeamice\scan\黑白 诞生秘话"
OUT_BASE = r"E:\Pokeamice\scan\黑白 诞生秘话_prepared"
OUT_ARCHIVE = os.path.join(OUT_BASE, "archive")
OUT_WEB = os.path.join(OUT_BASE, "web")
BRAIN_DIR = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334"

os.makedirs(OUT_ARCHIVE, exist_ok=True)
os.makedirs(OUT_WEB, exist_ok=True)

# 50 unique pages definition
# side: "single" (Cover/Back), "even" (outer left, gutter right), "odd" (gutter left, outer right)
PAGE_SPECS = [
    ("page004.jpg", 1,   "single", "p001_cover", "Cover / 表紙: ポケモン誕生秘話 完全総集版"),
    ("page005.jpg", 3,   "odd",    "p003_contents", "Contents / 目次 & はじめに (編集長 マッスル五十嵐)"),
    ("page006.jpg", 4,   "even",   "p004_poll_pokemon_top10_part1", "ポケモン人気投票 結果発表 第1位～第3位 (シャンデラ, エルフーン, レシラム)"),
    ("page007.jpg", 5,   "odd",    "p005_poll_pokemon_top10_part2", "ポケモン人気投票 結果発表 第4位～第10位 (ランクルス, サザンドラ, ジャローダ, ツタージャ, バチュル, ミジュマル, ドレディア)"),
    ("page008.jpg", 6,   "even",   "p006_poll_pokemon_11_20", "ポケモン人気投票 結果発表 第11位～第20位 (ゼクロム, デンチュラ, ヤナップ, ペンドラー, ウルガモス, エモンガ, ゾロアーク, ヒトモシ, ビクティニ, チラーミィ)"),
    ("page009.jpg", 7,   "odd",    "p007_poll_pokemon_21_50_ranking", "ポケモン人気投票 結果発表 第21位～第50位＆イッシュ全ポケモン順位一覧"),
    ("page010.jpg", 8,   "even",   "p008_poll_character_top3", "人物キャラ部門 結果発表 第1位～第3位 (1位 N 366票, 2位 ノボリ 348票, 3位 クダリ 298票)"),
    ("page011.jpg", 9,   "odd",    "p009_poll_character_4_15_ranking", "人物キャラ部門 結果発表 第4位～第15位＆総合順位・編集部コメント"),
    ("page012.jpg", 10,  "even",   "p010_reader_postcards_part1", "みんなのおハガキ大紹介 Part 1 (マッスル五十嵐感謝感激企画)"),
    ("page013.jpg", 11,  "odd",    "p011_reader_postcards_part2", "みんなのおハガキ大紹介 Part 2"),
    ("page014.jpg", 12,  "even",   "p012_reader_postcards_part3", "みんなのおハガキ大紹介 Part 3"),
    ("page015.jpg", 13,  "odd",    "p013_reader_postcards_part4", "みんなのおハガキ大紹介 Part 4 & 読者イラスト"),
    ("page016.jpg", 14,  "even",   "p014_special_top3_pokemon_chandelure", "人気投票TOP3おめでとう企画 ポケモン編: 第1位 シャンデラ徹底特集"),
    ("page018.jpg", 15,  "odd",    "p015_special_top3_pokemon_whimsicott_reshiram", "人気投票TOP3おめでとう企画 ポケモン編: 第2位 エルフーン & 第3位 レシラム特集"),
    ("page019.jpg", 16,  "even",   "p016_special_top3_character_n", "人気投票TOP3おめでとう企画 人物キャラ編: 第1位 プラズマ団の王 N 名場面集"),
    ("page020.jpg", 17,  "odd",    "p017_special_top3_character_subway_masters", "人気投票TOP3おめでとう企画 人物キャラ編: 第2位・第3位 サブウェイマスター ノボリ＆クダリ 名場面集"),
    ("page021.jpg", 18,  "even",   "p018_making_pokemon_roundtable_intro", "ポケモン誕生秘話 総集編 導入・スペシャル会談 (杉森建・海野隆雄・大村祐介)"),
    ("page022.jpg", 19,  "odd",    "p019_making_pokemon_snivy_tepig", "ポケモン誕生秘話: ツタージャ・ジャノビー・ジャローダ / ポカブ・チャオブー"),
    ("page023.jpg", 20,  "even",   "p020_making_pokemon_emboar_oshawott_samurott", "ポケモン誕生秘話: エンブオー / ミジュマル・フタチマル・ダイケンキ"),
    ("page024.jpg", 21,  "odd",    "p021_making_pokemon_patrat_pidove_monkeys", "ポケモン誕生秘話: ミネズミ・ミルホッグ / マメパト・ハトーボー・ケンホロウ / ヤナップ・バオップ・ヒヤップ・進化形"),
    ("page025.jpg", 22,  "even",   "p022_making_pokemon_cinccino_munna_karrablast_shelmet", "ポケモン誕生秘話: チラーミィ・チラチーノ / ムンナ・ムシャーナ / カブルモ・シュバルゴ / チョボマキ・アギルダー"),
    ("page026.jpg", 23,  "odd",    "p023_making_pokemon_audino_whimsicott_lilligant_emolga_sigilyph", "ポケモン誕生秘話: モンメン・エルフーン / チュリネ・ドレディア / タブンネ / エモンガ / シンボラー"),
    ("page027.jpg", 24,  "even",   "p024_making_pokemon_chandelure_conkeldurr_klinklang", "ポケモン誕生秘話: ヒトモシ・ランプラー・シャンデラ / ドッコラー・ドテッコツ・ローブシン / ギアル・ギギアル・ギギギアル"),
    ("page028.jpg", 25,  "odd",    "p025_making_pokemon_garbodor_sawsbuck_beartic", "ポケモン誕生秘話: ヤブクロン・ダストダス / シキジカ・メブキジカ / クマシュン・ツンベアー"),
    ("page029.jpg", 26,  "even",   "p026_making_pokemon_bisharp_eelektross_heatmor_durant", "ポケモン誕生秘話: コマタナ・キリキザン / シビシラス・シビビール・シビルドン / クイタラン / アイアント"),
    ("page030.jpg", 27,  "odd",    "p027_making_pokemon_haxorus_darmanitan_jellicent", "ポケモン誕生秘話: キバゴ・オノンド・オノノクス / ダルマッカ・ヒヒダルマ / プルリル・ブルンゲル"),
    ("page031.jpg", 28,  "even",   "p028_making_pokemon_tympole_stunfisk_cofagrigus_crustle", "ポケモン誕生秘話: オタマロ・ガマガル・ガマゲロゲ / マッギョ / デスマス・デスカーン / イシズマイ・イワパレス"),
    ("page032.jpg", 29,  "odd",    "p029_making_pokemon_golurk_vanilluxe_basculin", "ポケモン誕生秘話: ゴビット・ゴルーグ / バニプッチ・バニリッチ・バイバニラ / バスラオ"),
    ("page033.jpg", 30,  "even",   "p030_making_pokemon_volcarona_braviary_mandibuzz", "ポケモン誕生秘話: メラルバ・ウルガモス / ワシボン・ウォーグル / バルチャイ・バルジーナ"),
    ("page034.jpg", 31,  "odd",    "p031_making_pokemon_amoonguss_ferrothorn_zoroark_scrafty", "ポケモン誕生秘話: タマゲタケ・モロバレル / テッシード・ナットレイ / ゾロア・ゾロアーク / ズルッグ・ズルズキン"),
    ("page035.jpg", 32,  "even",   "p032_making_pokemon_mienshao_hydreigon_victini", "ポケモン誕生秘話: コジョフー・コジョンド / モノズ・ジヘッド・サザンドラ / ビクティニ"),
    ("page036.jpg", 33,  "odd",    "p033_making_pokemon_reshiram_zekrom", "ポケモン誕生秘話: 伝説のポケモン レシラム / ゼクロム"),
    ("page037.jpg", 34,  "even",   "p034_making_pokemon_forces_of_nature_throh_sawk", "ポケモン誕生秘話: コピペロス トルネロス・ボルトロス・ランドロス / ナゲキ・ダゲキ"),
    ("page038.jpg", 35,  "odd",    "p035_making_pokemon_swords_of_justice_favorites", "ポケモン誕生秘話: 聖剣士 コバルオン・テラキオン・ビリジオン / イッシュ地方で一番のお気に入りは？"),
    ("page039.jpg", 36,  "even",   "p036_making_pokemon_summary_favorite_poll", "ポケモン誕生秘話: 開発者インタビュー総括＆お気に入りポケモン談義"),
    ("page040.jpg", 37,  "odd",    "p037_special_single_illustration_gallery", "特別企画「ポケモンB・W」一枚絵ギャラリー (バトルサブウェイ, ミュージカル, ゲーチス, ブラックシティ/ホワイトフォレスト, ヒウンシティ)"),
    ("page041.jpg", 38,  "even",   "p038_making_characters_protagonists_fennel", "29キャラの裏話が満載!! 登場人物編: 主人公 (男の子・女の子) / マコモ"),
    ("page042.jpg", 39,  "odd",    "p039_making_characters_juniper_cheren_bianca", "登場人物編: アララギ博士・アララギパパ / チェレン / ベル"),
    ("page043.jpg", 40,  "even",   "p040_making_characters_n_ghetsis_grunts", "登場人物編: N (エヌ) / ゲーチス / プラズマ団したっぱ (男女)"),
    ("page044.jpg", 41,  "odd",    "p041_making_characters_gym_leaders_cilan_burgh_lenora", "登場人物編 ジムリーダー: ポッド＆デント＆コーン / アーティ / アロエ"),
    ("page045.jpg", 42,  "even",   "p042_making_characters_gym_leaders_clay_skyla_elesa", "登場人物編 ジムリーダー: ヤーコン / フウロ / カミツレ"),
    ("page046.jpg", 43,  "odd",    "p043_making_characters_gym_leaders_brycen_iris_drayden", "登場人物編 ジムリーダー: ハチク / アイリス / シャガ"),
    ("page047.jpg", 44,  "even",   "p044_making_characters_elite_four_grimsley_shauntal", "登場人物編 四天王: ギーマ / シキミ"),
    ("page048.jpg", 45,  "odd",    "p045_making_characters_elite_four_marshal_caitlin", "登場人物編 四天王: レンブ / カトレア (※コクラン解説)"),
    ("page049.jpg", 46,  "even",   "p046_making_characters_subway_masters_alder", "登場人物編: サブウェイマスター クダリ・ノボリ / ポケモンリーグチャンピオン アデク"),
    ("page050.jpg", 47,  "odd",    "p047_pokemon_do_special_movie_distributions", "特別企画「ポケモン堂」出張版: 劇場版プレゼントポケモン (ゼクロム・レシラム)＆前売券ビクティニ"),
    ("page051.jpg", 48,  "even",   "p048_pokemon_do_special_pgl_pokemon_cafe", "特別企画「ポケモン堂」出張版: PGL「ポケモンカフェ」＆ポケモンセンターコラボグッズ"),
    ("page053.jpg", 49,  "odd",    "p049_pokemon_do_special_tcg_victini_decks", "特別企画「ポケモン堂」出張版: ポケモンカードゲームBW バトルテーマデッキ「ビクティニ」＆拡張パック「レッドコレクション」"),
    ("page054.jpg", 50,  "even",   "p050_pokemon_do_special_tcg_tournament_colophon", "特別企画「ポケモン堂」出張版: マッスル五十嵐レポート はじめて大会へGO!! / バトリオV / 奥付 (ニンドリ2011年7月号 附録)"),
    ("page055.jpg", 999, "single", "p999_back_cover", "Back Cover / 表4: ポケモン誕生秘話 完全総集版 (ニンテンドードリーム2011年7月号 別冊付録)")
]

def load_img(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)

def save_img(path, img, quality=92):
    ext = os.path.splitext(path)[1]
    ret, buf = cv2.imencode(ext, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if ret:
        with open(path, "wb") as f:
            f.write(buf)

def calc_md5(path):
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def detect_page_bounds(im300, side):
    h300, w300 = im300.shape[:2]
    gray = cv2.cvtColor(im300, cv2.COLOR_BGR2GRAY)
    sobely = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))
    
    mid_w_start = int(w300 * 0.2)
    mid_w_end = int(w300 * 0.8)
    
    top_zone = sobely[100:500, mid_w_start:mid_w_end]
    grad_top = (np.percentile(top_zone, 85, axis=1) + np.mean(top_zone, axis=1)) / 2.0
    gray_top = np.mean(gray[100:500, mid_w_start:mid_w_end], axis=1)
    
    btm_start_y = 2950
    btm_zone = sobely[btm_start_y:h300-30, mid_w_start:mid_w_end]
    grad_btm = (np.percentile(btm_zone, 85, axis=1) + np.mean(btm_zone, axis=1)) / 2.0
    gray_btm = np.mean(gray[btm_start_y:h300-30, mid_w_start:mid_w_end], axis=1)
    
    top_candidates = []
    for y_idx in range(len(grad_top)):
        score = grad_top[y_idx]
        y_abs = y_idx + 100
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
            
    best_pair = None
    best_score = -1e9
    for tp, s_top in top_candidates:
        for bp, s_btm in btm_candidates:
            dist = bp - tp
            if 3050 <= dist <= 3100:
                s = s_top + s_btm - abs(dist - 3076) * 0.8
                if s > best_score:
                    best_score = s
                    best_pair = (tp, bp, dist)
                    
    if best_pair is None:
        tp, bp = 220, 3296
    else:
        tp, bp, _ = best_pair
        
    # Standardize height to exactly 3076 if difference is small
    target_h = 3076
    cur_h = bp - tp
    diff = target_h - cur_h
    if abs(diff) <= 10:
        bp += diff // 2
        tp -= (diff - diff // 2)
        
    # Horizontal side bounds
    if side == "even":
        left = 18
        right = w300 - 140
    elif side == "odd":
        left = 115
        right = w300 - 18
    else: # single (Cover, Back Cover)
        left = 18
        right = w300 - 18
        
    return left, tp, right, bp

def enhance_img(cropped):
    p_low = np.percentile(cropped, 0.4)
    p_high = np.percentile(cropped, 99.2)
    stretched = np.clip((cropped.astype(np.float32) - p_low) * (255.0 / max(1.0, p_high - p_low)), 0, 255).astype(np.uint8)
    blur = cv2.GaussianBlur(stretched, (0, 0), 1.0)
    sharpened = cv2.addWeighted(stretched, 1.15, blur, -0.15, 0)
    return sharpened

manifest_records = []
overview_thumbs = []
top_strips = []
btm_strips = []

print("Starting calibrated reprocessing for 『ポケモン誕生秘話 完全総集版』 (50 pages)...")

for src_file, mag_p, side, out_base_name, desc in PAGE_SPECS:
    src_path = os.path.join(SRC_DIR, src_file)
    raw = load_img(src_path)
    h600, w600 = raw.shape[:2]
    
    # 2x supersampling to 300 DPI master
    im300 = cv2.resize(raw, (int(round(w600 * 0.5)), int(round(h600 * 0.5))), interpolation=cv2.INTER_AREA)
    
    # Accurate edge bounds
    left, top, right, btm = detect_page_bounds(im300, side)
    
    # Manual fine-tunes if needed (e.g. page009)
    if src_file == "page009.jpg":
        top = 272
        btm = 272 + 3076
        
    cropped = im300[top:btm, left:right]
    crop_h, crop_w = cropped.shape[:2]
    
    enhanced = enhance_img(cropped)
    
    # 1. Archive tier (300 DPI master, Quality 92)
    arch_filename = f"{out_base_name}.jpg"
    arch_path = os.path.join(OUT_ARCHIVE, arch_filename)
    save_img(arch_path, enhanced, quality=92)
    arch_md5 = calc_md5(arch_path)
    
    # 2. Web tier (Height 2048px, Quality 84)
    web_target_h = 2048
    web_target_w = int(round(crop_w * (web_target_h / float(crop_h))))
    web_img = cv2.resize(enhanced, (web_target_w, web_target_h), interpolation=cv2.INTER_AREA)
    web_filename = f"{out_base_name}.jpg"
    web_path = os.path.join(OUT_WEB, web_filename)
    save_img(web_path, web_img, quality=84)
    web_md5 = calc_md5(web_path)
    
    # Contact thumbnail (width 360px)
    thumb_w = 360
    thumb_h = int(round(crop_h * (thumb_w / float(crop_w))))
    thumb_img = cv2.resize(web_img, (thumb_w, thumb_h), interpolation=cv2.INTER_AREA)
    overview_thumbs.append({
        "name": out_base_name,
        "page": mag_p,
        "thumb": thumb_img
    })
    
    # Header strip (top 150px of enhanced)
    hdr_h = 80
    hdr_w = 600
    strip_t = cv2.resize(enhanced[:160, :], (hdr_w, hdr_h), interpolation=cv2.INTER_AREA)
    cv2.putText(strip_t, f"P.{mag_p:02d} {out_base_name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    top_strips.append(strip_t)
    
    # Footer strip (bottom 160px of enhanced)
    strip_b = cv2.resize(enhanced[crop_h-160:, :], (hdr_w, hdr_h), interpolation=cv2.INTER_AREA)
    cv2.putText(strip_b, f"P.{mag_p:02d} {out_base_name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    btm_strips.append(strip_b)
    
    record = {
        "raw_file": src_file,
        "booklet_page": mag_p,
        "spread_side": side,
        "output_basename": out_base_name,
        "description": desc,
        "raw_dimensions": {"width": w600, "height": h600},
        "crop_box_300dpi": {"left": left, "top": top, "right": right, "bottom": btm},
        "archive": {
            "file": f"archive/{arch_filename}",
            "width": crop_w,
            "height": crop_h,
            "dpi": 300,
            "quality": 92,
            "md5": arch_md5
        },
        "web": {
            "file": f"web/{web_filename}",
            "width": web_target_w,
            "height": web_target_h,
            "quality": 84,
            "md5": web_md5
        }
    }
    manifest_records.append(record)
    p_label = "Cover" if mag_p == 1 else ("Back" if mag_p == 999 else f"P.{mag_p:02d}")
    print(f"  [{p_label:>5}] {src_file} -> {out_base_name}.jpg (Arch: {crop_w}x{crop_h}, Web: {web_target_w}x{web_target_h})")

# Write scan-manifest.json
manifest_path = os.path.join(OUT_BASE, "scan-manifest.json")
manifest_data = {
    "booklet_title": "ポケモン誕生秘話 ポケットモンスターブラック・ホワイト 完全総集版",
    "publication": "Nintendo DREAM 2011年7月号 特別付録",
    "editor_in_chief": "マッスル五十嵐 (五十嵐達雄)",
    "publisher": "毎日コミュニケーションズ",
    "date": "2011-07",
    "format": "A5判・52ページ付録小冊子 (精錬50ページ)",
    "calibration_height_300dpi": 3076,
    "total_unique_pages": len(manifest_records),
    "excluded_files": [
        {
            "filename": "page017.jpg",
            "reason": "Upside-down duplicate scan of Page 15 (エルフーン & レシラム). Re-scanned right-side up as page018.jpg."
        }
    ],
    "skipped_file_numbers": [
        {
            "filename": "page052.jpg",
            "note": "Skipped in scanner counter naming. page051.jpg is Page 48, followed directly by page053.jpg as Page 49. No physical pages missing."
        }
    ],
    "pages": manifest_records
}

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest_data, f, indent=2, ensure_ascii=False)
print(f"Saved manifest to {manifest_path}")

# Generate Contact Sheets
print("Generating contact sheets...")
from PIL import Image, ImageDraw

# 1. Overview sheets (2 sheets, 25 pages each, 5 cols x 5 rows)
cols = 5
rows = 5
cell_w = 380
cell_h = 530

for sheet_idx, chunk in enumerate([overview_thumbs[:25], overview_thumbs[25:]]):
    grid = Image.new("RGB", (cols * cell_w, rows * cell_h), (24, 24, 28))
    draw = ImageDraw.Draw(grid)
    for idx, item in enumerate(chunk):
        r = idx // cols
        c = idx % cols
        thumb_pil = Image.fromarray(cv2.cvtColor(item["thumb"], cv2.COLOR_BGR2RGB))
        grid.paste(thumb_pil, (c * cell_w + 10, r * cell_h + 30))
        p_label = "Cover" if item["page"] == 1 else ("Back" if item["page"] == 999 else f"P.{item['page']:02d}")
        draw.text((c * cell_w + 15, r * cell_h + 10), f"[{p_label}] {item['name']}", fill=(255, 230, 100))
    sheet_name = f"bw_prepared_sheet_{sheet_idx+1}.jpg"
    sheet_path = os.path.join(BRAIN_DIR, sheet_name)
    grid.save(sheet_path, quality=85)
    print(f"Saved contact sheet to {sheet_path}")

# 2. Top header strips comparison (2 columns of 25)
c1_top = np.vstack(top_strips[:25])
c2_top = np.vstack(top_strips[25:])
grid_top = np.hstack([c1_top, c2_top])
top_path = os.path.join(BRAIN_DIR, "bw_prepared_top.jpg")
save_img(top_path, grid_top, quality=85)
print(f"Saved header strips sheet to {top_path}")

# 3. Bottom footer strips comparison (2 columns of 25)
c1_btm = np.vstack(btm_strips[:25])
c2_btm = np.vstack(btm_strips[25:])
grid_btm = np.hstack([c1_btm, c2_btm])
btm_path = os.path.join(BRAIN_DIR, "bw_prepared_btm.jpg")
save_img(btm_path, grid_btm, quality=85)
print(f"Saved footer strips sheet to {btm_path}")

print("Calibrated batch processing completed successfully!")
