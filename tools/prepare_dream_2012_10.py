import os
import json
import cv2
import numpy as np
from datetime import datetime, timezone

SOURCE_DIR = r"E:\Pokeamice\scan\DREAM 2012.10"
TARGET_DIR = r"E:\Pokeamice\scan\DREAM 2012.10_prepared"
ARCHIVE_DIR = os.path.join(TARGET_DIR, "archive")
WEB_DIR = os.path.join(TARGET_DIR, "web")
MANIFEST_PATH = os.path.join(TARGET_DIR, "scan-manifest.json")
SCRATCH_DIR = r"C:\Users\2144j\.gemini\antigravity\brain\c01b4c66-5dcf-4279-a3dd-5000421d0334"

PAGE_DEFINITIONS = [
    {
        "index": 0,
        "magazine_page": 1,
        "source_file": "page001.jpg",
        "stem": "p001_cover",
        "description": "表紙：ニンドリ 2012年10月号 Vol.222（とびだせ どうぶつの森 / B2W2）",
        "spread_side": "single"
    },
    {
        "index": 1,
        "magazine_page": 3,
        "source_file": "page002.jpg",
        "stem": "p003_contents",
        "description": "目次：CONTENTS P3",
        "spread_side": "odd"
    },
    {
        "index": 2,
        "magazine_page": 22,
        "source_file": "page004.jpg",
        "stem": "p022_b2w2_legendary",
        "description": "特集：伝説のポケモン入手 ゼクロム・レシラム・キュレム、三聖剣",
        "spread_side": "even"
    },
    {
        "index": 3,
        "magazine_page": 23,
        "source_file": "page005.jpg",
        "stem": "p023_b2w2_legendary",
        "description": "特集：伝説のポケモン入手 レジ系・霊獣フォルム・隠れ特性",
        "spread_side": "odd"
    },
    {
        "index": 4,
        "magazine_page": 24,
        "source_file": "page006.jpg",
        "stem": "p024_b2w2_pickup",
        "description": "新要素攻略＋開発秘話：フェスミッション開発秘話",
        "spread_side": "even",
        "manual_crop": [18, 223, 2341, 3300]
    },
    {
        "index": 5,
        "magazine_page": 25,
        "source_file": "page007.jpg",
        "stem": "p025_b2w2_pokewood",
        "description": "新要素攻略＋開発秘話：ポケウッド映画撮影秘話",
        "spread_side": "odd"
    },
    {
        "index": 6,
        "magazine_page": 26,
        "source_file": "page008.jpg",
        "stem": "p026_b2w2_pwt",
        "description": "新要素攻略：PWT（ポケモントーナメント）歴代強豪バトル",
        "spread_side": "even"
    },
    {
        "index": 7,
        "magazine_page": 27,
        "source_file": "page012.jpg",
        "stem": "p027_b2w2_join_avenue",
        "description": "新要素攻略：ジョインアベニュー発展ガイド",
        "spread_side": "odd"
    },
    {
        "index": 8,
        "magazine_page": 28,
        "source_file": "page010.jpg",
        "stem": "p028_sound_interview",
        "description": "特集：特濃！！ポケモン音楽インタビュー さらなる進化を目指して…（前編）",
        "spread_side": "even"
    },
    {
        "index": 9,
        "magazine_page": 29,
        "source_file": "page011.jpg",
        "stem": "p029_sound_interview",
        "description": "特集：特濃！！ポケモン音楽インタビュー さらなる進化を目指して…（後編 / パルスマン）",
        "spread_side": "odd"
    },
    {
        "index": 10,
        "magazine_page": 30,
        "source_file": "page013.jpg",
        "stem": "p030_pokemon_next_genesect",
        "description": "連載：ポケモン堂NEXT 幻のポケモン・ゲノセクト その能力とは？",
        "spread_side": "even"
    },
    {
        "index": 11,
        "magazine_page": 31,
        "source_file": "page015.jpg",
        "stem": "p031_pokemon_next_contest",
        "description": "連載：ポケモン堂NEXT 全国図鑑Pro・ARサーチャー写真コンテスト",
        "spread_side": "odd"
    },
    {
        "index": 12,
        "magazine_page": 126,
        "source_file": "page016.jpg",
        "stem": "p126_sales_ranking",
        "description": "連載：ニンドリ売上データランキング研究所（B2W2 累計250万本）",
        "spread_side": "even"
    },
    {
        "index": 13,
        "magazine_page": 999,
        "source_file": "page017.jpg",
        "stem": "p999_back_cover",
        "description": "広告：裏表紙 ロストヒーローズ（LOST HEROES）",
        "spread_side": "single"
    }
]

def find_crop_bounds(im300, side):
    h, w, _ = im300.shape
    if side == "even":
        left = 18
        right = w - 140
    elif side == "odd":
        left = 115
        right = w - 18
    else:
        left = 18
        right = w - 18

    gray = cv2.cvtColor(im300, cv2.COLOR_BGR2GRAY)
    sobely = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))

    top_z = sobely[10:500, 40:w-40]
    grad_top = (np.percentile(top_z, 90, axis=1) + np.mean(top_z, axis=1)) / 2.0
    btm_z = sobely[2800:h-10, 40:w-40]
    grad_btm = (np.percentile(btm_z, 90, axis=1) + np.mean(btm_z, axis=1)) / 2.0

    top_peaks = [y + 10 for y in np.where(grad_top > np.max(grad_top)*0.15)[0]]
    btm_peaks = [y + 2800 for y in np.where(grad_btm > np.max(grad_btm)*0.15)[0]]

    best_pair = None
    best_score = -1e9
    for tp in top_peaks:
        for bp in btm_peaks:
            dist = bp - tp
            if 3055 <= dist <= 3085:
                s = grad_top[tp - 10] + grad_btm[bp - 2800] - abs(dist - 3070)*0.5
                if s > best_score:
                    best_score = s
                    best_pair = (tp, bp, dist)

    if best_pair:
        top, btm, dist = best_pair
    else:
        top, btm = 220, 3290
    return int(left), int(top), int(right), int(btm)

def enhance_image(cropped):
    result = np.zeros_like(cropped)
    for c in range(3):
        ch = cropped[:, :, c].astype(np.float32)
        p_low = np.percentile(ch, 0.4)
        p_high = np.percentile(ch, 99.1)
        ch_adj = np.clip((ch - p_low) * (255.0 / max(1.0, (p_high - p_low))), 0, 255)
        result[:, :, c] = ch_adj.astype(np.uint8)

    gaussian = cv2.GaussianBlur(result, (0, 0), 1.5)
    sharpened = cv2.addWeighted(result, 1.2, gaussian, -0.2, 0)
    return sharpened

def main():
    print("=== Starting DREAM 2012.10 Scan Preparation ===")
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    os.makedirs(WEB_DIR, exist_ok=True)

    manifest = {
        "magazine": "Nintendo DREAM 2012年10月号 (Vol.222)",
        "source": SOURCE_DIR,
        "target": TARGET_DIR,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_source_scans": 16,
        "selected_pages_count": len(PAGE_DEFINITIONS),
        "deduplicated_count": 2,
        "pages": []
    }

    prepared_crops = []

    for i, pdef in enumerate(PAGE_DEFINITIONS):
        src_path = os.path.join(SOURCE_DIR, pdef["source_file"])
        raw = cv2.imread(src_path)
        if raw is None:
            print(f"Error reading {src_path}")
            continue

        # Downsample 600 DPI (4962x7019) to 300 DPI (2481x3509)
        im300 = cv2.resize(raw, (raw.shape[1]//2, raw.shape[0]//2), interpolation=cv2.INTER_AREA)

        if "manual_crop" in pdef:
            left, top, right, btm = pdef["manual_crop"]
        else:
            left, top, right, btm = find_crop_bounds(im300, pdef["spread_side"])

        cropped = im300[top:btm, left:right]
        enhanced = enhance_image(cropped)
        ch, cw, _ = enhanced.shape

        # Archive version (full 300 DPI JPEG Q92)
        arch_name = f"{pdef['stem']}.jpg"
        arch_path = os.path.join(ARCHIVE_DIR, arch_name)
        cv2.imwrite(arch_path, enhanced, [cv2.IMWRITE_JPEG_QUALITY, 92])
        arch_bytes = os.path.getsize(arch_path)

        # Web version (height 2048px JPEG Q84)
        target_web_h = 2048
        scale = target_web_h / float(ch)
        target_web_w = int(round(cw * scale))
        web_img = cv2.resize(enhanced, (target_web_w, target_web_h), interpolation=cv2.INTER_AREA)
        web_name = f"{pdef['stem']}.jpg"
        web_path = os.path.join(WEB_DIR, web_name)
        cv2.imwrite(web_path, web_img, [cv2.IMWRITE_JPEG_QUALITY, 84])
        web_bytes = os.path.getsize(web_path)

        page_meta = {
            "index": pdef["index"],
            "magazine_page": pdef["magazine_page"],
            "source_file": pdef["source_file"],
            "stem": pdef["stem"],
            "description": pdef["description"],
            "spread_side": pdef["spread_side"],
            "crop_coordinates_300dpi": {
                "left": left,
                "top": top,
                "right": right,
                "bottom": btm,
                "width": cw,
                "height": ch
            },
            "archive": {
                "filename": arch_name,
                "width": cw,
                "height": ch,
                "file_size": arch_bytes
            },
            "web": {
                "filename": web_name,
                "width": target_web_w,
                "height": target_web_h,
                "file_size": web_bytes
            }
        }
        manifest["pages"].append(page_meta)
        prepared_crops.append((pdef["stem"], enhanced))
        print(f"[{i+1}/{len(PAGE_DEFINITIONS)}] Processed {pdef['stem']} (P{pdef['magazine_page']}) -> {cw}x{ch} (Archive: {arch_bytes//1024}KB, Web: {web_bytes//1024}KB)")

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"Wrote manifest: {MANIFEST_PATH}")

    # Generate Contact Sheets
    print("Generating contact sheets...")
    # 1. Full-page contact sheet: 14 pages (7 columns x 2 rows)
    thumb_w, thumb_h = 280, 370
    sheet_all = np.ones((thumb_h * 2, thumb_w * 7, 3), dtype=np.uint8) * 255
    for idx, (stem, img) in enumerate(prepared_crops):
        c = idx % 7
        r = idx // 7
        small = cv2.resize(img, (thumb_w, thumb_h), interpolation=cv2.INTER_AREA)
        sheet_all[r*thumb_h:(r+1)*thumb_h, c*thumb_w:(c+1)*thumb_w] = small
    cv2.imwrite(os.path.join(SCRATCH_DIR, "dream_2012_10_prepared_all.jpg"), sheet_all, [cv2.IMWRITE_JPEG_QUALITY, 85])

    # 2. Top-margin contact sheet (top 150px)
    top_strips = []
    for stem, img in prepared_crops:
        strip = cv2.resize(img[:180, :], (380, 80), interpolation=cv2.INTER_AREA)
        top_strips.append(strip)
    sheet_top = np.vstack(top_strips)
    cv2.imwrite(os.path.join(SCRATCH_DIR, "dream_2012_10_prepared_top.jpg"), sheet_top, [cv2.IMWRITE_JPEG_QUALITY, 85])

    # 3. Bottom-margin contact sheet (bottom 150px)
    btm_strips = []
    for stem, img in prepared_crops:
        strip = cv2.resize(img[-180:, :], (380, 80), interpolation=cv2.INTER_AREA)
        btm_strips.append(strip)
    sheet_btm = np.vstack(btm_strips)
    cv2.imwrite(os.path.join(SCRATCH_DIR, "dream_2012_10_prepared_btm.jpg"), sheet_btm, [cv2.IMWRITE_JPEG_QUALITY, 85])

    print("All contact sheets generated successfully.")

if __name__ == "__main__":
    main()
