"""Automated scan page preparation script for Nintendo DREAM January 2014 issue (v2).

Deduplicates raw scans, detects physical page boundaries via Sobel gradients
with physical page height consistency constraints (approx 3070px),
crops scanner bed frames and inner spine bleed, normalises per-channel tone,
and exports dual profiles (archive and web) plus scan-manifest.json.
"""

from __future__ import annotations

import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageOps

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SOURCE_DIR = Path(r"E:\Pokeamice\scan\DREAM 2014.1")
TARGET_DIR = Path(r"E:\Pokeamice\scan\DREAM 2014.1_prepared")

# Page catalog and deduplication mapping:
PAGE_CATALOG = [
    ("page001.jpg", "p001_cover", 1, "single", "表紙：FE覚醒 / マリオ3D / ポケモンXY大特集"),
    ("page003.jpg", "p003_contents", 3, "odd", "目次：CONTENTS / 特集案内"),
    ("page004.jpg", "p006_mega", 6, "even", "新ポケモン編：新たなメガシンカポケモン"),
    ("page005.jpg", "p007_mega", 7, "odd", "新ポケモン編：メガギャラドス / メガフーディン"),
    ("page008.jpg", "p008_mega", 8, "even", "新ポケモン編：メガカイロス / メガヘラクロス / メガライボルト / メガヘルガー"),
    ("page009.jpg", "p009_mega", 9, "odd", "新ポケモン編：メガハッサム / メガチャーレム / メガバンギラス"),
    ("page010.jpg", "p010_mega", 10, "even", "新ポケモン編：メガプテラ / メガユキノオー / チーム作り"),
    ("page011.jpg", "p011_walkthrough", 11, "odd", "攻略編：チャート・マップ攻略 5つ目のジムまでを攻略！"),
    ("page012.jpg", "p012_walkthrough", 12, "even", "攻略編：13番道路 / カロス発電所"),
    ("page013.jpg", "p013_walkthrough", 13, "odd", "攻略編：ミアレシティ / ミアレジム"),
    ("page014.jpg", "p014_walkthrough", 14, "even", "攻略編：14番道路 / クノエシティ"),
    ("page015.jpg", "p015_walkthrough", 15, "odd", "攻略編：クノエジム / ボール工場 / 15番道路"),
    ("page016.jpg", "p016_lumiose", 16, "even", "企画：ミアレシティ観光ガイド 全体マップ"),
    ("page017.jpg", "p017_lumiose", 17, "odd", "企画：ミアレシティ観光ガイド 一度は訪れたい観光スポット"),
    ("page019.jpg", "p018_lumiose", 18, "even", "企画：ミアレシティ観光ガイド 専門店＆さまざまなカフェ"),
    ("page021.jpg", "p019_lumiose", 19, "odd", "企画：ミアレシティ観光ガイド 出会う人々（シトロン / フラダリ）"),
    ("page022.jpg", "p020_interview", 20, "even", "楽曲魂 PART 1：DNAを受け継ぎ進化する音"),
    ("page023.jpg", "p021_interview", 21, "odd", "楽曲魂 PART 2：景山将太 / 足立美奈子"),
    ("page024.jpg", "p022_interview", 22, "even", "楽曲魂 PART 3：佐藤仁美（ジムリーダー戦曲）"),
    ("page025.jpg", "p023_interview", 23, "odd", "楽曲魂 PART 4：黒田英明 / 増田順一（イベルタル戦曲）"),
    ("page026.jpg", "p024_interview", 24, "even", "楽曲魂 PART 5：全体対談（ポケモンらしさの音）"),
    ("page027.jpg", "p025_interview", 25, "odd", "楽曲魂 PART 6：ポケモンX・Yサウンドのヒミツ"),
    ("page028.jpg", "p026_goods", 26, "even", "ポケモン堂NEXT：ポケモンドール / ポケモンセンター新商品"),
    ("page029.jpg", "p027_goods", 27, "odd", "ポケモン堂NEXT：トレッタ / ポケモンカードゲームXY"),
    ("page030.jpg", "p126_ranking", 126, "even", "ランキング研究所：ポケモンX・Y 273万本 首位独走研报"),
    ("page031.jpg", "p128_back", 128, "single", "裏表紙：ワンピース アンリミテッドワールド レッド 広告"),
]


def detect_page_bounds(img_gray: np.ndarray, side: str) -> tuple[int, int, int, int]:
    h, w = img_gray.shape

    # 1. Top Sobel search
    sobel_y_top = np.abs(cv2.Sobel(img_gray[0:450, 40:w-40], cv2.CV_32F, 0, 1, ksize=3))
    top_score = np.percentile(sobel_y_top, 90, axis=1) * 0.5 + np.mean(sobel_y_top, axis=1) * 0.5

    top_cands = []
    for y in range(60, 400):
        if top_score[y] > 15.0 and top_score[y] == max(top_score[max(0, y-8):min(len(top_score), y+9)]):
            top_cands.append((y, float(top_score[y])))
    top_cands.sort(key=lambda x: x[1], reverse=True)

    # 2. Bottom Sobel search
    sobel_y_btm = np.abs(cv2.Sobel(img_gray[2950:3480, 40:w-40], cv2.CV_32F, 0, 1, ksize=3))
    btm_score = np.percentile(sobel_y_btm, 90, axis=1) * 0.5 + np.mean(sobel_y_btm, axis=1) * 0.5

    btm_cands = []
    for y_rel in range(20, len(btm_score) - 20):
        y_abs = 2950 + y_rel
        if btm_score[y_rel] > 15.0 and btm_score[y_rel] == max(btm_score[max(0, y_rel-8):min(len(btm_score), y_rel+9)]):
            btm_cands.append((y_abs, float(btm_score[y_rel])))
    btm_cands.sort(key=lambda x: x[1], reverse=True)

    # Physical page height constraint (standard magazine is 3070px +- 15px)
    best_pair = None
    best_err = 9999
    for ty, _ in top_cands:
        for by, _ in btm_cands:
            diff = by - ty
            if 3055 <= diff <= 3085:
                err = abs(diff - 3070)
                if err < best_err:
                    best_err = err
                    best_pair = (ty, by)

    if best_pair is not None:
        top_edge, btm_edge = best_pair
    else:
        if top_cands:
            top_edge = top_cands[0][0]
            btm_edge = top_edge + 3070
        elif btm_cands:
            btm_edge = btm_cands[0][0]
            top_edge = btm_edge - 3070
        else:
            top_edge = 210
            btm_edge = 210 + 3070

    # 3. Left / Right crease and margin detection
    if side == "even":
        left = 18
        search = img_gray[int(h * 0.2):int(h * 0.8), w - 220:w - 80]
        col_prof = np.mean(search, axis=0)
        crease_rel = int(np.argmax(col_prof))
        right = (w - 220) + crease_rel
        right = min(max(right, w - 140), w - 110)
    elif side == "odd":
        search = img_gray[int(h * 0.2):int(h * 0.8), 80:220]
        col_prof = np.mean(search, axis=0)
        crease_rel = int(np.argmax(col_prof))
        left = 80 + crease_rel
        left = max(min(left, 130), 105)
        right = w - 18
    else:
        left = 18
        right = w - 18

    return top_edge, btm_edge, left, right


def auto_tone_normalise(img_rgb: np.ndarray) -> np.ndarray:
    out = np.zeros_like(img_rgb, dtype=np.float32)
    for c in range(3):
        channel = img_rgb[..., c].astype(np.float32)
        p_high = float(np.percentile(channel, 99.1))
        p_low = float(np.percentile(channel, 0.4))
        p_high = max(p_high, 230.0)
        p_low = min(p_low, 35.0)
        scaled = (channel - p_low) / max(p_high - p_low, 1.0) * 255.0
        out[..., c] = np.clip(scaled, 0.0, 255.0)

    out_u8 = out.astype(np.uint8)
    blurred = cv2.GaussianBlur(out_u8, (0, 0), 1.8)
    sharpened = cv2.addWeighted(out_u8, 1.20, blurred, -0.20, 0)
    return sharpened


def save_derivative(
    img_pil: Image.Image,
    dest_path: Path,
    quality: int,
    long_edge: int | None = None,
) -> dict[str, Any]:
    working = img_pil
    if long_edge and max(img_pil.size) > long_edge:
        scale = long_edge / max(img_pil.size)
        new_size = (round(img_pil.width * scale), round(img_pil.height * scale))
        working = img_pil.resize(new_size, Image.Resampling.LANCZOS)

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    working.save(
        buf,
        format="JPEG",
        quality=quality,
        subsampling=0 if long_edge is None else 2,
        optimize=True,
        progressive=True,
    )
    data = buf.getvalue()
    dest_path.write_bytes(data)

    return {
        "file_name": dest_path.name,
        "relative_path": dest_path.relative_to(TARGET_DIR).as_posix(),
        "size": list(working.size),
        "bytes": len(data),
        "quality": quality,
    }


def main() -> None:
    print("=== Starting DREAM 2014.1 Scan Preparation (v2 with Physical Height Constraint) ===")
    print(f"Source: {SOURCE_DIR}")
    print(f"Output: {TARGET_DIR}")

    archive_dir = TARGET_DIR / "archive"
    web_dir = TARGET_DIR / "web"
    archive_dir.mkdir(parents=True, exist_ok=True)
    web_dir.mkdir(parents=True, exist_ok=True)

    manifest_pages: list[dict[str, Any]] = []

    for idx, (src_name, stem, page_no, side, desc) in enumerate(PAGE_CATALOG, start=1):
        src_path = SOURCE_DIR / src_name
        if not src_path.exists():
            print(f"[{idx:>2}/{len(PAGE_CATALOG)}] ERROR: Missing file {src_path}")
            continue

        raw_img = Image.open(src_path)
        raw_img = ImageOps.exif_transpose(raw_img).convert("RGB")
        raw_arr = np.asarray(raw_img)
        gray_arr = cv2.cvtColor(raw_arr, cv2.COLOR_RGB2GRAY)

        top, btm, left, right = detect_page_bounds(gray_arr, side)
        cropped_arr = raw_arr[top:btm, left:right]
        toned_arr = auto_tone_normalise(cropped_arr)
        proc_img = Image.fromarray(toned_arr, mode="RGB")

        archive_file = archive_dir / f"{stem}.jpg"
        arch_info = save_derivative(proc_img, archive_file, quality=92, long_edge=None)

        web_file = web_dir / f"{stem}.jpg"
        web_info = save_derivative(proc_img, web_file, quality=84, long_edge=2048)

        page_record = {
            "index": idx - 1,
            "magazine_page": page_no,
            "source_file": src_name,
            "stem": stem,
            "description": desc,
            "spread_side": side,
            "crop_box": {
                "top": top,
                "bottom": btm,
                "left": left,
                "right": right,
                "cropped_width": right - left,
                "cropped_height": btm - top,
            },
            "outputs": [
                {**arch_info, "profile": "archive"},
                {**web_info, "profile": "web"},
            ],
        }
        manifest_pages.append(page_record)

        print(
            f"[{idx:>2}/{len(PAGE_CATALOG)}] {src_name} -> {stem:<18} "
            f"P{page_no:<3} [{side:<5}] "
            f"crop=[L:{left:4d}, T:{top:4d}, R:{right:4d}, B:{btm:4d}, H:{btm-top:4d}] "
            f"web={web_info['bytes']//1024}KB arch={arch_info['bytes']//1024}KB"
        )

    manifest = {
        "magazine": "Nintendo DREAM 2014年1月号 (Vol.237)",
        "source": str(SOURCE_DIR),
        "target": str(TARGET_DIR),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_source_scans": 31,
        "selected_pages_count": len(manifest_pages),
        "deduplicated_count": 31 - len(manifest_pages),
        "pages": manifest_pages,
    }

    manifest_path = TARGET_DIR / "scan-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nManifest written to: {manifest_path}")
    print(f"Preparation v2 complete! Total processed pages: {len(manifest_pages)}")


if __name__ == "__main__":
    main()
