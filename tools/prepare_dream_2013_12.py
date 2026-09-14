import os
import json
import glob
import cv2
import numpy as np
from datetime import datetime, timezone

SOURCE_DIR = r"E:\Pokeamice\scan\DREAM 2013.12"
TARGET_DIR = r"E:\Pokeamice\scan\DREAM 2013.12_prepared"
ARCHIVE_DIR = os.path.join(TARGET_DIR, "archive")
WEB_DIR = os.path.join(TARGET_DIR, "web")
MANIFEST_PATH = os.path.join(TARGET_DIR, "scan-manifest.json")

# 12 Curated pages (excluding duplicates page003 and page008)
PAGE_DEFINITIONS = [
    {
        "index": 0,
        "magazine_page": 1,
        "source_file": "page001.jpg",
        "stem": "p001_cover",
        "description": "表紙：ポケモンX・Y キャラ誕生秘話 / 歴代任天堂プロダクトカタログ",
        "spread_side": "single",
        "manual_crop": [0, 0, 2426, 3072]
    },
    {
        "index": 1,
        "magazine_page": 0,
        "source_file": "page002.jpg",
        "stem": "p000_ad_x",
        "description": "広告：ポケットモンスター X（ゼルネアス）",
        "spread_side": "even"
    },
    {
        "index": 2,
        "magazine_page": 0,
        "source_file": "page004.jpg",
        "stem": "p000_ad_y",
        "description": "広告：ポケットモンスター Y（イベルタル）",
        "spread_side": "odd"
    },
    {
        "index": 3,
        "magazine_page": 2,
        "source_file": "page005.jpg",
        "stem": "p002_yamauchi",
        "description": "編集长コラム：山内さん、ありがとうございました！（山内溥追悼）",
        "spread_side": "even",
        "manual_crop": [18, 207, 2341, 3281]
    },
    {
        "index": 4,
        "magazine_page": 12,
        "source_file": "page006.jpg",
        "stem": "p012_character",
        "description": "特集：カロス地方のあるきかた / ゲームフリークに訊く！人物キャラクターデザインの秘密（前篇）",
        "spread_side": "even"
    },
    {
        "index": 5,
        "magazine_page": 13,
        "source_file": "page007.jpg",
        "stem": "p013_character",
        "description": "特集：ゲームフリークに訊く！人物キャラクターデザインの秘密（杉森建・中村エリカ・中津井優）",
        "spread_side": "odd"
    },
    {
        "index": 6,
        "magazine_page": 14,
        "source_file": "page009.jpg",
        "stem": "p014_character",
        "description": "カロスコレクション特別篇：主人公 カルム＆セレナ",
        "spread_side": "even"
    },
    {
        "index": 7,
        "magazine_page": 15,
        "source_file": "page010.jpg",
        "stem": "p015_character",
        "description": "カロスコレクション特别篇：サナ、ティエルノ、トロバ",
        "spread_side": "odd"
    },
    {
        "index": 8,
        "magazine_page": 16,
        "source_file": "page011.jpg",
        "stem": "p016_character",
        "description": "カロスコレクション特別篇：プラターヌ博士、ビオラ、パンジー",
        "spread_side": "even"
    },
    {
        "index": 9,
        "magazine_page": 17,
        "source_file": "page012.jpg",
        "stem": "p017_character",
        "description": "カロスコレクション特别篇：ジムリーダー ザクロ、コルニ、読者へのメッセージ",
        "spread_side": "odd"
    },
    {
        "index": 10,
        "magazine_page": 112,
        "source_file": "page013.jpg",
        "stem": "p112_columns",
        "description": "ニンドリCOLUMNS：任天堂レアもの図鑑『ポケットモンスター 青』＆ VC",
        "spread_side": "even"
    },
    {
        "index": 11,
        "magazine_page": 113,
        "source_file": "page016.jpg",
        "stem": "p113_columns",
        "description": "ニンドリCOLUMNS：パリ発任天堂レポート『ファミコン30周年 日本人の知らない任天堂の歴史』",
        "spread_side": "odd"
    }
]

def find_crop_bounds(img, side, page_num):
    h, w, _ = img.shape
    if h < 3200:
        return 0, 0, w, 3072

    # Horizontal bounds
    if side == "even":
        left = 18
        right = w - 140
    elif side == "odd":
        left = 115
        right = w - 18
    else:
        left = 18
        right = w - 18

    # Vertical bounds via Dual-peak Sobel
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sobely = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))

    top_z = sobely[10:450, 40:w-40]
    grad_top = (np.percentile(top_z, 90, axis=1) + np.mean(top_z, axis=1)) / 2.0
    btm_z = sobely[2900:h-10, 40:w-40]
    grad_btm = (np.percentile(btm_z, 90, axis=1) + np.mean(btm_z, axis=1)) / 2.0

    top_peaks = [y + 10 for y in np.where(grad_top > np.max(grad_top)*0.15)[0]]
    btm_peaks = [y + 2900 for y in np.where(grad_btm > np.max(grad_btm)*0.15)[0]]

    best_pair = None
    best_score = -1e9
    for tp in top_peaks:
        for bp in btm_peaks:
            dist = bp - tp
            if 3055 <= dist <= 3085:
                s = grad_top[tp - 10] + grad_btm[bp - 2900] - abs(dist - 3070)*0.5
                if s > best_score:
                    best_score = s
                    best_pair = (tp, bp, dist)

    if best_pair:
        top, btm, dist = best_pair
    else:
        top, btm = 150, 3220

    return int(left), int(top), int(right), int(btm)

def enhance_image(cropped):
    # Channel-wise percentile white-balance
    result = np.zeros_like(cropped)
    for c in range(3):
        ch = cropped[:, :, c].astype(np.float32)
        p_low = np.percentile(ch, 0.4)
        p_high = np.percentile(ch, 99.1)
        ch_adj = np.clip((ch - p_low) * (255.0 / max(1.0, (p_high - p_low))), 0, 255)
        result[:, :, c] = ch_adj.astype(np.uint8)

    # Mild unsharp mask
    gaussian = cv2.GaussianBlur(result, (0, 0), 1.5)
    sharpened = cv2.addWeighted(result, 1.2, gaussian, -0.2, 0)
    return sharpened

def main():
    print("=== Starting DREAM 2013.12 Scan Preparation ===")
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    os.makedirs(WEB_DIR, exist_ok=True)

    manifest = {
        "magazine": "Nintendo DREAM 2013年12月号 (Vol.236)",
        "source": SOURCE_DIR,
        "target": TARGET_DIR,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_source_scans": 14,
        "selected_pages_count": len(PAGE_DEFINITIONS),
        "deduplicated_count": 2,
        "pages": []
    }

    total = len(PAGE_DEFINITIONS)
    for i, pdef in enumerate(PAGE_DEFINITIONS):
        src_path = os.path.join(SOURCE_DIR, pdef["source_file"])
        img = cv2.imread(src_path)
        if img is None:
            print(f"Error reading {src_path}")
            continue

        if "manual_crop" in pdef:
            left, top, right, btm = pdef["manual_crop"]
        else:
            left, top, right, btm = find_crop_bounds(img, pdef["spread_side"], pdef["magazine_page"])

        cropped = img[top:btm, left:right]
        enhanced = enhance_image(cropped)
        ch, cw, _ = enhanced.shape

        # Archive version (full-res JPEG Q92)
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

        p_str = f"P{pdef['magazine_page']}" if pdef['magazine_page'] > 0 else "AD"
        print(f"[{i+1:2d}/{total:2d}] {pdef['source_file']:12s} -> {pdef['stem']:18s} {p_str:4s} [{pdef['spread_side']:6s}] "
              f"crop=[L:{left:4d}, T:{top:4d}, R:{right:4d}, B:{btm:4d}, H:{ch:4d}] "
              f"web={web_bytes//1024}KB arch={arch_bytes//1024}KB")

        manifest["pages"].append({
            "index": pdef["index"],
            "magazine_page": pdef["magazine_page"],
            "source_file": pdef["source_file"],
            "stem": pdef["stem"],
            "description": pdef["description"],
            "spread_side": pdef["spread_side"],
            "crop_box": {
                "top": int(top),
                "bottom": int(btm),
                "left": int(left),
                "right": int(right),
                "cropped_width": int(cw),
                "cropped_height": int(ch)
            },
            "outputs": [
                {
                    "file_name": arch_name,
                    "relative_path": f"archive/{arch_name}",
                    "size": [int(cw), int(ch)],
                    "bytes": int(arch_bytes),
                    "quality": 92,
                    "profile": "archive"
                },
                {
                    "file_name": web_name,
                    "relative_path": f"web/{web_name}",
                    "size": [int(target_web_w), int(target_web_h)],
                    "bytes": int(web_bytes),
                    "quality": 84,
                    "profile": "web"
                }
            ]
        })

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\nManifest written to: {MANIFEST_PATH}")
    print(f"Preparation complete! Total processed pages: {total}")

if __name__ == "__main__":
    main()
