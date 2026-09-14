# -*- coding: utf-8 -*-
"""
Batch preparation script for:
『ポケモン誕生秘話 ポケットモンスターブラック・ホワイト 完全総集版』
(Nintendo DREAM 2011年7月号 特別付録 小冊子)

Source: E:\Pokeamice\scan\黑白 诞生秘话
Output: E:\Pokeamice\scan\黑白 诞生秘话_prepared\
  - archive/ (300 DPI master, Quality 92)
  - web/ (2048px height, Quality 84)
  - scan-manifest.json
  - Contact sheets in brain directory
"""

import os
import sys
import json
import hashlib
import cv2
import numpy as np
from PIL import Image, ImageDraw

SRC_DIR = r"E:\Pokeamice\scan\黑白 诞生秘话"
OUT_BASE = r"E:\Pokeamice\scan\黑白 诞生秘话_prepared"
OUT_ARCHIVE = os.path.join(OUT_BASE, "archive")
OUT_WEB = os.path.join(OUT_BASE, "web")
BRAIN_DIR = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334"

os.makedirs(OUT_ARCHIVE, exist_ok=True)
os.makedirs(OUT_WEB, exist_ok=True)

# 50 unique pages mapping (page017.jpg is upside-down duplicate of page018.jpg, excluded)
PAGE_SPECS = [
    ("page004.jpg", 1,   "p001_cover", "Cover / 表紙: ポケモン誕生秘話 ポケットモンスターブラック・ホワイト 完全総集版"),
    ("page005.jpg", 3,   "p003_contents", "Contents / 目次 & はじめに (編集長 マッスル五十嵐)"),
    ("page006.jpg", 4,   "p004_poll_pokemon_top10_part1", "ポケモン人気投票 結果発表 第1位～第3位 (シャンデラ, エルフーン, レシラム)"),
    ("page007.jpg", 5,   "p005_poll_pokemon_top10_part2", "ポケモン人気投票 結果発表 第4位～第10位 (ランクルス, サザンドラ, ジャローダ, ツタージャ, バチュル, ミジュマル, ドレディア)"),
    ("page008.jpg", 6,   "p006_poll_pokemon_11_20", "ポケモン人気投票 結果発表 第11位～第20位 (ゼクロム, デンチュラ, ヤナップ, ペンドラー, ウルガモス, エモンガ, ゾロアーク, ヒトモシ, ビクティニ, チラーミィ)"),
    ("page009.jpg", 7,   "p007_poll_pokemon_21_50_ranking", "ポケモン人気投票 結果発表 第21位～第50位＆イッシュ全ポケモン順位一覧"),
    ("page010.jpg", 8,   "p008_poll_character_top3", "人物キャラ部門 結果発表 第1位～第3位 (1位 N 366票, 2位 ノボリ 348票, 3位 クダリ 298票)"),
    ("page011.jpg", 9,   "p009_poll_character_4_15_ranking", "人物キャラ部門 結果発表 第4位～第15位＆総合順位・編集部コメント"),
    ("page012.jpg", 10,  "p010_reader_postcards_part1", "みんなのおハガキ大紹介 Part 1 (マッスル五十嵐感謝感激企画)"),
    ("page013.jpg", 11,  "p011_reader_postcards_part2", "みんなのおハガキ大紹介 Part 2"),
    ("page014.jpg", 12,  "p012_reader_postcards_part3", "みんなのおハガキ大紹介 Part 3"),
    ("page015.jpg", 13,  "p013_reader_postcards_part4", "みんなのおハガキ大紹介 Part 4 & 読者イラスト"),
    ("page016.jpg", 14,  "p014_special_top3_pokemon_chandelure", "人気投票TOP3おめでとう企画 ポケモン編: 第1位 シャンデラ徹底特集"),
    ("page018.jpg", 15,  "p015_special_top3_pokemon_whimsicott_reshiram", "人気投票TOP3おめでとう企画 ポケモン編: 第2位 エルフーン & 第3位 レシラム特集"),
    ("page019.jpg", 16,  "p016_special_top3_character_n", "人気投票TOP3おめでとう企画 人物キャラ編: 第1位 プラズマ団の王 N 名場面集"),
    ("page020.jpg", 17,  "p017_special_top3_character_subway_masters", "人気投票TOP3おめでとう企画 人物キャラ編: 第2位・第3位 サブウェイマスター ノボリ＆クダリ 名場面集"),
    ("page021.jpg", 18,  "p018_making_pokemon_roundtable_intro", "ポケモン誕生秘話 総集編 導入・スペシャル会談 (杉森建・海野隆雄・大村祐介)"),
    ("page022.jpg", 19,  "p019_making_pokemon_snivy_tepig", "ポケモン誕生秘話: ツタージャ・ジャノビー・ジャローダ / ポカブ・チャオブー"),
    ("page023.jpg", 20,  "p020_making_pokemon_emboar_oshawott_samurott", "ポケモン誕生秘話: エンブオー / ミジュマル・フタチマル・ダイケンキ"),
    ("page024.jpg", 21,  "p021_making_pokemon_patrat_pidove_monkeys", "ポケモン誕生秘話: ミネズミ・ミルホッグ / マメパト・ハトーボー・ケンホロウ / ヤナップ・バオップ・ヒヤップ・進化形"),
    ("page025.jpg", 22,  "p022_making_pokemon_cinccino_munna_karrablast_shelmet", "ポケモン誕生秘話: チラーミィ・チラチーノ / ムンナ・ムシャーナ / カブルモ・シュバルゴ / チョボマキ・アギルダー"),
    ("page026.jpg", 23,  "p023_making_pokemon_audino_whimsicott_lilligant_emolga_sigilyph", "ポケモン誕生秘話: モンメン・エルフーン / チュリネ・ドレディア / タブンネ / エモンガ / シンボラー"),
    ("page027.jpg", 24,  "p024_making_pokemon_chandelure_conkeldurr_klinklang", "ポケモン誕生秘話: ヒトモシ・ランプラー・シャンデラ / ドッコラー・ドテッコツ・ローブシン / ギアル・ギギアル・ギギギアル"),
    ("page028.jpg", 25,  "p025_making_pokemon_garbodor_sawsbuck_beartic", "ポケモン誕生秘話: ヤブクロン・ダストダス / シキジカ・メブキジカ / クマシュン・ツンベアー"),
    ("page029.jpg", 26,  "p026_making_pokemon_bisharp_eelektross_heatmor_durant", "ポケモン誕生秘話: コマタナ・キリキザン / シビシラス・シビビール・シビルドン / クイタラン / アイアント"),
    ("page030.jpg", 27,  "p027_making_pokemon_haxorus_darmanitan_jellicent", "ポケモン誕生秘話: キバゴ・オノンド・オノノクス / ダルマッカ・ヒヒダルマ / プルリル・ブルンゲル"),
    ("page031.jpg", 28,  "p028_making_pokemon_tympole_stunfisk_cofagrigus_crustle", "ポケモン誕生秘話: オタマロ・ガマガル・ガマゲロゲ / マッギョ / デスマス・デスカーン / イシズマイ・イワパレス"),
    ("page032.jpg", 29,  "p029_making_pokemon_golurk_vanilluxe_basculin", "ポケモン誕生秘話: ゴビット・ゴルーグ / バニプッチ・バニリッチ・バイバニラ / バスラオ"),
    ("page033.jpg", 30,  "p030_making_pokemon_volcarona_braviary_mandibuzz", "ポケモン誕生秘話: メラルバ・ウルガモス / ワシボン・ウォーグル / バルチャイ・バルジーナ"),
    ("page034.jpg", 31,  "p031_making_pokemon_amoonguss_ferrothorn_zoroark_scrafty", "ポケモン誕生秘話: タマゲタケ・モロバレル / テッシード・ナットレイ / ゾロア・ゾロアーク / ズルッグ・ズルズキン"),
    ("page035.jpg", 32,  "p032_making_pokemon_mienshao_hydreigon_victini", "ポケモン誕生秘話: コジョフー・コジョンド / モノズ・ジヘッド・サザンドラ / ビクティニ"),
    ("page036.jpg", 33,  "p033_making_pokemon_reshiram_zekrom", "ポケモン誕生秘話: 伝説のポケモン レシラム / ゼクロム"),
    ("page037.jpg", 34,  "p034_making_pokemon_forces_of_nature_throh_sawk", "ポケモン誕生秘話: コピペロス トルネロス・ボルトロス・ランドロス / ナゲキ・ダゲキ"),
    ("page038.jpg", 35,  "p035_making_pokemon_swords_of_justice_favorites", "ポケモン誕生秘話: 聖剣士 コバルオン・テラキオン・ビリジオン / イッシュ地方で一番のお気に入りは？"),
    ("page039.jpg", 36,  "p036_making_pokemon_summary_favorite_poll", "ポケモン誕生秘話: 開発者インタビュー総括＆お気に入りポケモン談義"),
    ("page040.jpg", 37,  "p037_special_single_illustration_gallery", "特別企画「ポケモンB・W」一枚絵ギャラリー (バトルサブウェイ, ミュージカル, ゲーチス, ブラックシティ/ホワイトフォレスト, ヒウンシティ)"),
    ("page041.jpg", 38,  "p038_making_characters_protagonists_fennel", "29キャラの裏話が満載!! 登場人物編: 主人公 (男の子・女の子) / マコモ"),
    ("page042.jpg", 39,  "p039_making_characters_juniper_cheren_bianca", "登場人物編: アララギ博士・アララギパパ / チェレン / ベル"),
    ("page043.jpg", 40,  "p040_making_characters_n_ghetsis_grunts", "登場人物編: N (エヌ) / ゲーチス / プラズマ団したっぱ (男女)"),
    ("page044.jpg", 41,  "p041_making_characters_gym_leaders_cilan_burgh_lenora", "登場人物編 ジムリーダー: ポッド＆デント＆コーン / アーティ / アロエ"),
    ("page045.jpg", 42,  "p042_making_characters_gym_leaders_clay_skyla_elesa", "登場人物編 ジムリーダー: ヤーコン / フウロ / カミツレ"),
    ("page046.jpg", 43,  "p043_making_characters_gym_leaders_brycen_iris_drayden", "登場人物編 ジムリーダー: ハチク / アイリス / シャガ"),
    ("page047.jpg", 44,  "p044_making_characters_elite_four_grimsley_shauntal", "登場人物編 四天王: ギーマ / シキミ"),
    ("page048.jpg", 45,  "p045_making_characters_elite_four_marshal_caitlin", "登場人物編 四天王: レンブ / カトレア (※コクラン解説)"),
    ("page049.jpg", 46,  "p046_making_characters_subway_masters_alder", "登場人物編: サブウェイマスター クダリ・ノボリ / ポケモンリーグチャンピオン アデク"),
    ("page050.jpg", 47,  "p047_pokemon_do_special_movie_distributions", "特別企画「ポケモン堂」出張版: 劇場版プレゼントポケモン (ゼクロム・レシラム)＆前売券ビクティニ"),
    ("page051.jpg", 48,  "p048_pokemon_do_special_pgl_pokemon_cafe", "特別企画「ポケモン堂」出張版: PGL「ポケモンカフェ」＆ポケモンセンターコラボグッズ"),
    ("page053.jpg", 49,  "p049_pokemon_do_special_tcg_victini_decks", "特別企画「ポケモン堂」出張版: ポケモンカードゲームBW バトルテーマデッキ「ビクティニ」＆拡張パック「レッドコレクション」"),
    ("page054.jpg", 50,  "p050_pokemon_do_special_tcg_tournament_colophon", "特別企画「ポケモン堂」出張版: マッスル五十嵐レポート はじめて大会へGO!! / バトリオV / 奥付 (ニンドリ2011年7月号 附録)"),
    ("page055.jpg", 999, "p999_back_cover", "Back Cover / 表4: ポケモン誕生秘話 完全総集版 (ニンテンドードリーム2011年7月号 別冊付録)")
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

def detect_trim(img):
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    t = 0
    while t < min(120, h // 20):
        if np.mean(gray[t, :]) < 30:
            t += 1
        else:
            break
            
    b = h
    while b > max(h - 120, h * 19 // 20):
        if np.mean(gray[b - 1, :]) < 30:
            b -= 1
        else:
            break
            
    l = 0
    while l < min(120, w // 20):
        if np.mean(gray[:, l]) < 30:
            l += 1
        else:
            break
            
    r = w
    while r > max(w - 120, w * 19 // 20):
        if np.mean(gray[:, r - 1]) < 30:
            r -= 1
        else:
            break
            
    return (l, t, r, b)

manifest_records = []
contact_images = []

print(f"Starting batch image processing for 『ポケモン誕生秘話 完全総集版』 (50 unique pages)...")

for src_file, mag_p, out_base_name, desc in PAGE_SPECS:
    src_path = os.path.join(SRC_DIR, src_file)
    img = load_img(src_path)
    orig_h, orig_w = img.shape[:2]
    
    # Scanner margin trim
    l, t, r, b = detect_trim(img)
    cropped = img[t:b, l:r]
    crop_h, crop_w = cropped.shape[:2]
    
    # Gentle contrast enhancement (preserving delicate line art and watercolors)
    p_low = np.percentile(cropped, 0.3)
    p_high = np.percentile(cropped, 99.4)
    stretched = np.clip((cropped.astype(np.float32) - p_low) * (255.0 / max(1.0, p_high - p_low)), 0, 255).astype(np.uint8)
    
    # Subtle unsharp mask for crisp type rendering
    blur = cv2.GaussianBlur(stretched, (0, 0), 1.0)
    sharpened = cv2.addWeighted(stretched, 1.12, blur, -0.12, 0)
    
    # 1. Archive tier: 300 DPI master (approx 2481 x 3509)
    # Since original is 600 DPI (approx 4962 x 7019), resize to exactly half for ideal descreening
    arch_w = int(round(crop_w * 0.5))
    arch_h = int(round(crop_h * 0.5))
    arch_img = cv2.resize(sharpened, (arch_w, arch_h), interpolation=cv2.INTER_AREA)
    
    arch_filename = f"{out_base_name}.jpg"
    arch_path = os.path.join(OUT_ARCHIVE, arch_filename)
    save_img(arch_path, arch_img, quality=92)
    arch_md5 = calc_md5(arch_path)
    
    # 2. Web tier: Height 2048px, Quality 84
    web_target_h = 2048
    web_target_w = int(round(arch_w * (web_target_h / float(arch_h))))
    web_img = cv2.resize(arch_img, (web_target_w, web_target_h), interpolation=cv2.INTER_AREA)
    
    web_filename = f"{out_base_name}.jpg"
    web_path = os.path.join(OUT_WEB, web_filename)
    save_img(web_path, web_img, quality=84)
    web_md5 = calc_md5(web_path)
    
    # Contact thumbnail (width 360px)
    thumb_w = 360
    thumb_h = int(round(arch_h * (thumb_w / float(arch_w))))
    thumb_img = cv2.resize(web_img, (thumb_w, thumb_h), interpolation=cv2.INTER_AREA)
    contact_images.append({
        "name": out_base_name,
        "page": mag_p,
        "thumb": thumb_img
    })
    
    record = {
        "raw_file": src_file,
        "booklet_page": mag_p,
        "output_basename": out_base_name,
        "description": desc,
        "raw_dimensions": {"width": orig_w, "height": orig_h},
        "crop_box": {"left": l, "top": t, "right": r, "bottom": b},
        "archive": {
            "file": f"archive/{arch_filename}",
            "width": arch_w,
            "height": arch_h,
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
    print(f"  [{p_label:>5}] {src_file} -> {out_base_name}.jpg (Arch: {arch_w}x{arch_h}, Web: {web_target_w}x{web_target_h})")

# Write scan-manifest.json
manifest_path = os.path.join(OUT_BASE, "scan-manifest.json")
manifest_data = {
    "booklet_title": "ポケモン誕生秘話 ポケットモンスターブラック・ホワイト 完全総集版",
    "publication": "Nintendo DREAM 2011年7月号 特別付録",
    "editor_in_chief": "マッスル五十嵐 (五十嵐達雄)",
    "publisher": "毎日コミュニケーションズ",
    "date": "2011-07",
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

# Generate Contact Sheets (2 sheets: 25 pages each, 5 cols x 5 rows)
print("Generating contact sheets...")
cols = 5
rows = 5
cell_w = 380
cell_h = 530

for sheet_idx, chunk in enumerate([contact_images[:25], contact_images[25:]]):
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

print("Batch preparation completed successfully!")
