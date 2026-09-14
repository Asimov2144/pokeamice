import os
import json
import hashlib
from PIL import Image

src_dir = r"E:\Pokeamice\scan\金银攻略"
prep_dir = r"E:\Pokeamice\scan\金银攻略_prepared"
archive_dir = os.path.join(prep_dir, "archive")
web_dir = os.path.join(prep_dir, "web")
spreads_arch_dir = os.path.join(prep_dir, "spreads_archive")
spreads_web_dir = os.path.join(prep_dir, "spreads_web")
ocr_dir = os.path.join(prep_dir, "ocr_transcriptions")

for d in [archive_dir, web_dir, spreads_arch_dir, spreads_web_dir, ocr_dir]:
    os.makedirs(d, exist_ok=True)

# Specs for each of the 6 spreads:
# (raw_file, top, btm, left, right, gutter, left_id, right_id, left_page_num, right_page_num, left_title, right_title)
spread_specs = [
    {
        "raw_file": "1.png", "top": 0, "btm": 4970, "crop_left": 0, "crop_right": 7015, "gutter": 3415,
        "spread_name": "spread_01_p192_p193.jpg",
        "left": {
            "page_num": 192, "filename": "p192_tools_mystery_gift.jpg",
            "section": "どうぐ 『ふしぎなおくりもの』で手に入るどうぐ・もようがえグッズ",
            "type": "even"
        },
        "right": {
            "page_num": 193, "filename": "p193_interview_koko_ga_shiritai_intro.jpg",
            "section": "開発スタッフ直撃インタビュー POKEMON 金・銀のココが知りたい！ (導入)",
            "type": "odd"
        }
    },
    {
        "raw_file": "2.png", "top": 45, "btm": 5015, "crop_left": 85, "crop_right": 7015, "gutter": 3643,
        "spread_name": "spread_02_p194_p195.jpg",
        "left": {
            "page_num": 194, "filename": "p194_interview_development_time_pkrs.jpg",
            "section": "開発スタッフ直撃インタビュー (開発期間・時計システム・ポケルス)",
            "type": "even"
        },
        "right": {
            "page_num": 195, "filename": "p195_interview_new_pokemon_creation.jpg",
            "section": "開発スタッフ直撃インタビュー (新ポケモン誕生・新わざ・あく＆はがねタイプ)",
            "type": "odd"
        }
    },
    {
        "raw_file": "3.png", "top": 0, "btm": 4965, "crop_left": 0, "crop_right": 7015, "gutter": 3549,
        "spread_name": "spread_03_p196_p197.jpg",
        "left": {
            "page_num": 196, "filename": "p196_interview_251st_pokemon_celebi.jpg",
            "section": "開発スタッフ直撃インタビュー (251匹めのポケモン・徘徊3匹捕獲のコツ)",
            "type": "even"
        },
        "right": {
            "page_num": 197, "filename": "p197_interview_shiny_unown_26_letters.jpg",
            "section": "開発スタッフ直撃インタビュー (色ちがいポケモン・アンノーン26タイプ)",
            "type": "odd"
        }
    },
    {
        "raw_file": "4.png", "top": 40, "btm": 5015, "crop_left": 0, "crop_right": 7015, "gutter": 3433,
        "spread_name": "spread_04_p198_p199.jpg",
        "left": {
            "page_num": 198, "filename": "p198_staff_zukan_part1.jpg",
            "section": "ポケットモンスター金・銀 かいはつスタッフずかん (前編 No.001-008)",
            "type": "even"
        },
        "right": {
            "page_num": 199, "filename": "p199_staff_zukan_part2.jpg",
            "section": "ポケットモンスター金・銀 かいはつスタッフずかん (後編 No.009-018)",
            "type": "odd"
        }
    },
    {
        "raw_file": "5.png", "top": 35, "btm": 5010, "crop_left": 0, "crop_right": 7015, "gutter": 3427,
        "spread_name": "spread_05_p200_p201.jpg",
        "left": {
            "page_num": 200, "filename": "p200_oak_interview_utsugi_lecture_part1.jpg",
            "section": "ポケモン研究の現在 オーキド博士に聞く＆タマゴ研究に関する報告 (ウツギ博士講演録1)",
            "type": "even"
        },
        "right": {
            "page_num": 201, "filename": "p201_utsugi_lecture_part2.jpg",
            "section": "タマゴ研究に関する報告 (ウツギ博士講演録2: 24時間監視と5分の隙)",
            "type": "odd"
        }
    },
    {
        "raw_file": "6.png", "top": 40, "btm": 5010, "crop_left": 0, "crop_right": 7015, "gutter": 3442,
        "spread_name": "spread_06_p202_p203.jpg",
        "left": {
            "page_num": 202, "filename": "p202_utsugi_lecture_part3.jpg",
            "section": "タマゴ研究に関する追加報告 (ウツギ博士講演録3: タマゴ運搬説・異種交配)",
            "type": "even"
        },
        "right": {
            "page_num": 203, "filename": "p203_utsugi_lecture_part4_letter.jpg",
            "section": "タマゴ研究に関する追加報告 (ウツギ博士講演録4: メタモン交配・オーキド博士への手紙)",
            "type": "odd"
        }
    }
]

manifest = {
    "book_title": "小学館 任天堂公式ガイドブック ポケットモンスター 金・銀 (巻末直撃インタビュー＆開発秘話)",
    "publication_year": 1999,
    "total_pages": 12,
    "total_spreads": 6,
    "pages": [],
    "spreads": []
}

order = 1
for s in spread_specs:
    raw_path = os.path.join(src_dir, s["raw_file"])
    with Image.open(raw_path) as img:
        l, t, r, b = s["crop_left"], s["top"], s["crop_right"], s["btm"]
        g = s["gutter"]
        
        # 1. Spread processing
        spread_crop = img.crop((l, t, r, b))
        spread_arch_path = os.path.join(spreads_arch_dir, s["spread_name"])
        spread_crop.save(spread_arch_path, "JPEG", quality=92, progressive=True, subsampling=0)
        
        # Spread web
        web_w = int(spread_crop.width * (2048 / spread_crop.height))
        spread_web = spread_crop.resize((web_w, 2048), Image.Resampling.LANCZOS)
        spread_web_path = os.path.join(spreads_web_dir, s["spread_name"])
        spread_web.save(spread_web_path, "JPEG", quality=84, progressive=True)
        
        manifest["spreads"].append({
            "spread_id": s["spread_name"],
            "raw_file": s["raw_file"],
            "pages": [s["left"]["page_num"], s["right"]["page_num"]],
            "archive_size": [spread_crop.width, spread_crop.height],
            "web_size": [web_w, 2048]
        })
        
        # 2. Left single page
        left_crop = img.crop((l, t, min(g + 20, r), b))
        left_arch_path = os.path.join(archive_dir, s["left"]["filename"])
        left_crop.save(left_arch_path, "JPEG", quality=92, progressive=True, subsampling=0)
        
        left_web_w = int(left_crop.width * (2048 / left_crop.height))
        left_web = left_crop.resize((left_web_w, 2048), Image.Resampling.LANCZOS)
        left_web_path = os.path.join(web_dir, s["left"]["filename"])
        left_web.save(left_web_path, "JPEG", quality=84, progressive=True)
        
        with open(left_arch_path, "rb") as f:
            left_md5 = hashlib.md5(f.read()).hexdigest()
            
        manifest["pages"].append({
            "order": order,
            "page_num": s["left"]["page_num"],
            "type": s["left"]["type"],
            "filename": s["left"]["filename"],
            "source_raw": s["raw_file"],
            "section": s["left"]["section"],
            "archive_size": [left_crop.width, left_crop.height],
            "web_size": [left_web_w, 2048],
            "md5": left_md5
        })
        order += 1
        
        # 3. Right single page
        right_crop = img.crop((max(g - 20, l), t, r, b))
        right_arch_path = os.path.join(archive_dir, s["right"]["filename"])
        right_crop.save(right_arch_path, "JPEG", quality=92, progressive=True, subsampling=0)
        
        right_web_w = int(right_crop.width * (2048 / right_crop.height))
        right_web = right_crop.resize((right_web_w, 2048), Image.Resampling.LANCZOS)
        right_web_path = os.path.join(web_dir, s["right"]["filename"])
        right_web.save(right_web_path, "JPEG", quality=84, progressive=True)
        
        with open(right_arch_path, "rb") as f:
            right_md5 = hashlib.md5(f.read()).hexdigest()
            
        manifest["pages"].append({
            "order": order,
            "page_num": s["right"]["page_num"],
            "type": s["right"]["type"],
            "filename": s["right"]["filename"],
            "source_raw": s["raw_file"],
            "section": s["right"]["section"],
            "archive_size": [right_crop.width, right_crop.height],
            "web_size": [right_web_w, 2048],
            "md5": right_md5
        })
        order += 1
        
        print(f"Completed {s['raw_file']} -> spread + P{s['left']['page_num']} + P{s['right']['page_num']}")

# Save manifest
manifest_path = os.path.join(prep_dir, "scan-manifest.json")
with open(manifest_path, "w", encoding="utf-8") as jf:
    json.dump(manifest, jf, ensure_ascii=False, indent=2)

print(f"Manifest written to: {manifest_path}")
