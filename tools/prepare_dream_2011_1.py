# -*- coding: utf-8 -*-
"""
Batch preparation script for Nintendo DREAM 2011年1月号 (Vol.201)
Source: E:\Pokeamice\scan\DREAM 2011.1改\DREAM 2011.1改
Output: E:\Pokeamice\scan\DREAM 2011.1_prepared\
  - archive/ (300 DPI, Quality 92)
  - web/ (2048px height, Quality 84)
  - scan-manifest.json
  - Contact sheets in brain directory
"""

import os
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC_DIR = r"E:\Pokeamice\scan\DREAM 2011.1改\DREAM 2011.1改"
OUT_BASE = r"E:\Pokeamice\scan\DREAM 2011.1_prepared"
OUT_ARCHIVE = os.path.join(OUT_BASE, "archive")
OUT_WEB = os.path.join(OUT_BASE, "web")
BRAIN_DIR = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334"

os.makedirs(OUT_ARCHIVE, exist_ok=True)
os.makedirs(OUT_WEB, exist_ok=True)

# 30 unique pages mapping (page024 is duplicate of page025, excluded)
PAGE_SPECS = [
    ("page001.jpg", 1,   "p001_cover", "Cover / 表紙: ポケットモンスターB・W 絵と音から魅力を解き明かす"),
    ("page002.jpg", 3,   "p003_contents", "Contents / 目次"),
    ("page004.jpg", 6,   "p006_bw_special_intro", "ALL ABOUT ポケモンB・W 扉絵"),
    ("page005.jpg", 7,   "p007_bw_pokemon_making_intro", "ポケモン＆新キャラ誕生秘話 導入・色紙プレゼント"),
    ("page006.jpg", 8,   "p008_bw_pokemon_design_process", "新ポケモンのデザインはどう進んだのか？"),
    ("page007.jpg", 9,   "p009_bw_pokemon_reshiram_zekrom", "生みの親が語る レシラム・ゼクロム"),
    ("page008.jpg", 10,  "p010_bw_pokemon_snivy_tepig", "ツタージャ・ポカブ 誕生秘話"),
    ("page009.jpg", 11,  "p011_bw_pokemon_emboar_oshawott_samurott", "エンブオー・ミジュマル・ダイケンキ 誕生秘話"),
    ("page010.jpg", 12,  "p012_bw_pokemon_zoroark_victini_audino", "ゾロア・ゾロアーク・ビクティニ・チラーミィ・タブンネ"),
    ("page011.jpg", 13,  "p013_bw_pokemon_emolga_musharna_monkeys", "エモンガ・ムシャーナ・三猿・ダゲキ・ナゲキ"),
    ("page012.jpg", 14,  "p014_bw_pokemon_accelgor_escavalier_conkeldurr", "アギルダー・シュバルゴ・ローブシン・ヤブクロン・クマシュン・シンボラー"),
    ("page014.jpg", 15,  "p015_bw_characters_protagonists_juniper", "登場人物編 主人公・アララギ博士・アララギパパ"),
    ("page015.jpg", 16,  "p016_bw_characters_cheren_bianca_n_ghetsis", "チェレン・ベル・マコモ・N・プラズマ団・ゲーチス"),
    ("page016.jpg", 17,  "p017_bw_characters_gym_leaders_cilan_elesa_skyla", "ジムリーダー サンヨウ三兄弟・アロエ・アーティ・カミツレ・ヤーコン・フウロ"),
    ("page017.jpg", 18,  "p018_bw_sound_interview_kageyama", "楽曲魂 特別編 景山将太さんインタビュー"),
    ("page018.jpg", 19,  "p019_bw_sound_roundtable_masuda_ichinose_sato_kageyama", "サウンドチーム座談会 増田順一・一之瀬剛・佐藤仁美・景山将太"),
    ("page019.jpg", 20,  "p020_bw_sound_pokemon_cries_interactive", "ポケモンの鳴き声・街の音楽・インタラクティブサウンド"),
    ("page021.jpg", 21,  "p021_bw_art_director_masuda_aesthetic", "絵画・美術へのこだわり ディレクター増田さんのこと！"),
    ("page022.jpg", 22,  "p022_bw_special_dialogue_sugimori_masuda_part1", "杉森建×増田順一 スペシャル対談 Part 1"),
    ("page023.jpg", 23,  "p023_bw_special_dialogue_sugimori_masuda_part2", "杉森建×増田順一 スペシャル対談 Part 2"),
    ("page025.jpg", 69,  "p069_memorial_200_muscle_chief_editor_greeting", "創刊200号突破記念 新たな門出スペシャル / マッスル新編集長挨拶"),
    ("page026.jpg", 70,  "p070_memorial_200_editorial_team_walkthrough", "ニンドリ編集部、魅せます！ お仕事マップ"),
    ("page027.jpg", 71,  "p071_memorial_200_staff_roster_chronology", "歴代編集部員名簿・年表・マッスル号"),
    ("page030.jpg", 72,  "p072_memorial_200_sakurai_masahiro_dialogue_part1", "新たな門出に桜井さんがやってきた!! 桜井政博インタビュー Part 1"),
    ("page031.jpg", 73,  "p073_memorial_200_sakurai_masahiro_dialogue_part2", "桜井政博インタビュー Part 2"),
    ("page032.jpg", 74,  "p074_memorial_200_sakurai_masahiro_dialogue_part3", "桜井政博インタビュー Part 3"),
    ("page033.jpg", 75,  "p075_memorial_200_sakurai_masahiro_dialogue_part4", "桜井政博インタビュー Part 4・色紙プレゼント"),
    ("page034.jpg", 118, "p118_column_paris_nintendo_report_florent_gorges", "パリ発！任天堂レポート Florent Gorges"),
    ("page035.jpg", 126, "p126_nintendo_scramble_3ds_hands_on_event", "ニンドリスクランブル 3DS体験イベント告知"),
    ("page036.jpg", 999, "p999_back_cover_super_robot_wars_l", "Back Cover / 表4: スーパーロボット大戦L")
]

def load_img(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)

def save_img(path, img, quality=92):
    ext = os.path.splitext(path)[1]
    ret, buf = cv2.imencode(ext, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if ret:
        with open(path, "wb") as f:
            f.write(buf)

def detect_trim(img, fname):
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Check top/bottom/left/right for black scanner borders (< 35)
    t = 0
    while t < min(100, h // 15):
        if np.mean(gray[t, :]) < 35:
            t += 1
        else:
            break
            
    b = h
    while b > max(h - 100, h * 14 // 15):
        if np.mean(gray[b - 1, :]) < 35:
            b -= 1
        else:
            break
            
    l = 0
    while l < min(100, w // 15):
        if np.mean(gray[:, l]) < 35:
            l += 1
        else:
            break
            
    r = w
    while r > max(w - 100, w * 14 // 15):
        if np.mean(gray[:, r - 1]) < 35:
            r -= 1
        else:
            break
            
    return (l, t, r, b)

manifest_records = []
processed_images_for_contacts = []

print("Starting batch image processing for DREAM 2011.1...")

for src_file, mag_p, out_base_name, desc in PAGE_SPECS:
    src_path = os.path.join(SRC_DIR, src_file)
    img = load_img(src_path)
    orig_h, orig_w = img.shape[:2]
    
    # Detect black border trim
    l, t, r, b = detect_trim(img, src_file)
    cropped = img[t:b, l:r]
    crop_h, crop_w = cropped.shape[:2]
    
    # Dynamic percentile stretching
    p_low = np.percentile(cropped, 0.4)
    p_high = np.percentile(cropped, 99.2)
    stretched = np.clip((cropped.astype(np.float32) - p_low) * (255.0 / max(1.0, p_high - p_low)), 0, 255).astype(np.uint8)
    
    # Subtle unsharp mask
    blur = cv2.GaussianBlur(stretched, (0, 0), 1.2)
    sharpened = cv2.addWeighted(stretched, 1.15, blur, -0.15, 0)
    
    # Save archive image (300 DPI, Quality 92)
    arch_filename = f"{out_base_name}.jpg"
    arch_path = os.path.join(OUT_ARCHIVE, arch_filename)
    save_img(arch_path, sharpened, quality=92)
    
    # Save web image (Height 2048px, Quality 84)
    web_target_h = 2048
    web_target_w = int(round(crop_w * (web_target_h / float(crop_h))))
    web_img = cv2.resize(sharpened, (web_target_w, web_target_h), interpolation=cv2.INTER_AREA)
    web_filename = f"{out_base_name}.jpg"
    web_path = os.path.join(OUT_WEB, web_filename)
    save_img(web_path, web_img, quality=84)
    
    # For contact sheets, downsample to 360px width
    contact_w = 360
    contact_h = int(round(crop_h * (contact_w / float(crop_w))))
    contact_thumb = cv2.resize(sharpened, (contact_w, contact_h), interpolation=cv2.INTER_AREA)
    
    # Header crop (top 15%)
    hdr_h = int(crop_h * 0.15)
    hdr_thumb = cv2.resize(sharpened[:hdr_h, :], (contact_w, int(contact_w * hdr_h / float(crop_w))), interpolation=cv2.INTER_AREA)
    
    # Footer crop (bottom 15%)
    ftr_thumb = cv2.resize(sharpened[crop_h - hdr_h:, :], (contact_w, int(contact_w * hdr_h / float(crop_w))), interpolation=cv2.INTER_AREA)
    
    processed_images_for_contacts.append({
        "name": out_base_name,
        "page": mag_p,
        "full": contact_thumb,
        "hdr": hdr_thumb,
        "ftr": ftr_thumb
    })
    
    record = {
        "raw_file": src_file,
        "magazine_page": mag_p,
        "output_basename": out_base_name,
        "description": desc,
        "raw_dimensions": {"width": orig_w, "height": orig_h},
        "crop_box": {"left": l, "top": t, "right": r, "bottom": b},
        "archive_dimensions": {"width": crop_w, "height": crop_h},
        "archive_file": f"archive/{arch_filename}",
        "web_dimensions": {"width": web_target_w, "height": web_target_h},
        "web_file": f"web/{web_filename}"
    }
    manifest_records.append(record)
    print(f"  [P.{mag_p:03d}] {src_file} -> {out_base_name}.jpg ({crop_w}x{crop_h})")

# Write scan-manifest.json
manifest_path = os.path.join(OUT_BASE, "scan-manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump({
        "issue": "Nintendo DREAM 2011年1月号 (Vol.201)",
        "total_unique_pages": len(manifest_records),
        "excluded_duplicates": ["page024.jpg (duplicate of page025.jpg)"],
        "pages": manifest_records
    }, f, indent=2, ensure_ascii=False)
print(f"Saved manifest to {manifest_path}")

# Generate Contact Sheets
print("Generating contact sheets...")
# 1. All pages: 5 cols x 6 rows (30 pages)
cols = 5
rows = 6
cell_w = 380
cell_h = 520
grid_all = Image.new("RGB", (cols * cell_w, rows * cell_h), (25, 25, 25))
draw_all = ImageDraw.Draw(grid_all)

for idx, item in enumerate(processed_images_for_contacts):
    r = idx // cols
    c = idx % cols
    thumb_pil = Image.fromarray(cv2.cvtColor(item["full"], cv2.COLOR_BGR2RGB))
    tw, th = thumb_pil.size
    grid_all.paste(thumb_pil, (c * cell_w + 10, r * cell_h + 30))
    draw_all.text((c * cell_w + 15, r * cell_h + 10), f"P.{item['page']:03d} {item['name']}", fill=(255, 255, 100))

all_sheet_path = os.path.join(BRAIN_DIR, "dream_2011_1_prepared_all.jpg")
grid_all.save(all_sheet_path, quality=85)
print(f"Saved all-pages contact sheet to {all_sheet_path}")

# 2. Top headers contact sheet (5 cols x 6 rows)
hdr_cell_h = 180
grid_top = Image.new("RGB", (cols * cell_w, rows * hdr_cell_h), (25, 25, 25))
draw_top = ImageDraw.Draw(grid_top)

for idx, item in enumerate(processed_images_for_contacts):
    r = idx // cols
    c = idx % cols
    hdr_pil = Image.fromarray(cv2.cvtColor(item["hdr"], cv2.COLOR_BGR2RGB))
    grid_top.paste(hdr_pil, (c * cell_w + 10, r * hdr_cell_h + 25))
    draw_top.text((c * cell_w + 15, r * hdr_cell_h + 8), f"P.{item['page']:03d} {item['name']}", fill=(255, 255, 100))

top_sheet_path = os.path.join(BRAIN_DIR, "dream_2011_1_prepared_top.jpg")
grid_top.save(top_sheet_path, quality=85)
print(f"Saved top headers contact sheet to {top_sheet_path}")

# 3. Bottom footers contact sheet (5 cols x 6 rows)
grid_btm = Image.new("RGB", (cols * cell_w, rows * hdr_cell_h), (25, 25, 25))
draw_btm = ImageDraw.Draw(grid_btm)

for idx, item in enumerate(processed_images_for_contacts):
    r = idx // cols
    c = idx % cols
    ftr_pil = Image.fromarray(cv2.cvtColor(item["ftr"], cv2.COLOR_BGR2RGB))
    grid_btm.paste(ftr_pil, (c * cell_w + 10, r * hdr_cell_h + 25))
    draw_btm.text((c * cell_w + 15, r * hdr_cell_h + 8), f"P.{item['page']:03d} {item['name']}", fill=(255, 255, 100))

btm_sheet_path = os.path.join(BRAIN_DIR, "dream_2011_1_prepared_btm.jpg")
grid_btm.save(btm_sheet_path, quality=85)
print(f"Saved bottom footers contact sheet to {btm_sheet_path}")

print("Batch preparation for DREAM 2011.1 completed successfully!")
