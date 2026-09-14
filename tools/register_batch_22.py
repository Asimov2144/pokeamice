#!/usr/bin/env python3
"""
Register Batch 22 entries into database:
- PKMN-1057: CEDEC 2022 SV Shader & Pipeline
- PKMN-1058: Famitsu Returns Detective Pikachu (Ishihara x Jinnai)
- PKMN-1059: Game Watch Quinty 25th (Sugimori x Masuda x Morimoto)
"""

import sys
import json
import csv
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

JSON_PATH = Path("data/pokemon_1000_interviews.json")
CSV_PATH = Path("data/pokemon_1000_interviews.csv")

BATCH_22 = [
    {
        "id": "PKMN-1057",
        "title": "Famitsu / CEDEC 2022 专访《宝可梦 朱／紫》：皮卡丘实现系列史上最佳蓬松毛发质感——与《传说 阿尔宙斯》双线并行的开放世界技术秘辛",
        "original_title": "『ポケモン スカーレット・バイオレット』のピカチュウはシリーズ史上最高のふさふさ感を実現。『ポケモンレジェンズ アルセウス』との同時制作における制作環境を解説【CEDEC2022】",
        "url": "https://www.famitsu.com/news/202208/27273621.html",
        "date": "2022-08-27",
        "people": [
            "前座晃宏",
            "大谷一登"
        ],
        "generation": "Gen 9",
        "language": "JA",
        "outlet": "ファミ通.com / CEDEC 2022",
        "type": "Web Interview",
        "tags": [
            "宝可梦 朱／紫",
            "宝可梦传说 阿尔宙斯",
            "CEDEC",
            "Game Freak",
            "3D建模",
            "着色器",
            "皮卡丘",
            "开放世界",
            "第九世代",
            "JA"
        ],
        "summary": "CEDEC 2022 官方技术专场报道：GAME FREAK R&D 部技术总监前座晃宏与角色模型工程师大谷一登，深度披露《宝可梦 朱／紫》与《宝可梦传说 阿尔宙斯》并行制作时 1000+ 宝可梦 3D 模型通用化、材质着色器（毛发/金属/绒毛）创新与开放世界管线管理秘辛。",
        "status": "imported",
        "imported_post_slug": "2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline",
        "imported_post_path": "_posts/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline.md",
        "post_file": "_posts/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline.md"
    },
    {
        "id": "PKMN-1058",
        "title": "Famitsu 专访《名侦探皮卡丘 归来》：石原恒和×阵内弘之——大叔皮卡丘是“会说人类语言的宝可梦”的终点，兼谈《赤·绿》诞生秘话与《Pokémon Sleep》",
        "original_title": "『帰ってきた 名探偵ピカチュウ』陣内弘之氏＆石原恒和氏インタビュー。おっさんピカチュウは、人の言葉をしゃべるポケモンのひとつの到達点。『ポケモン 赤・緑』開発時の想い出話も",
        "url": "https://www.famitsu.com/news/202310/19320055.html",
        "date": "2023-10-19",
        "people": [
            "石原恒和",
            "阵内弘之"
        ],
        "generation": "Gen 9",
        "language": "JA",
        "outlet": "ファミ通.com",
        "type": "Web Interview",
        "tags": [
            "名侦探皮卡丘",
            "石原恒和",
            "阵内弘之",
            "Creatures",
            "The Pokémon Company",
            "皮卡丘",
            "Pokémon Sleep",
            "赤·绿",
            "第九世代",
            "JA"
        ],
        "summary": "Fami通深度对谈：宝可梦社长石原恒和与 Creatures 董事长阵内弘之畅谈《名侦探皮卡丘 归来》，追溯皮卡丘从《赤·绿》电子音到大谷育江人声再到“大叔人话”的设定演进，并揭秘《Pokémon Sleep》长达5年的睡眠数据研发历程。",
        "status": "imported",
        "imported_post_slug": "2023-10-19-interview-famitsu-detective-pikachu-returns-ishihara-jinnai",
        "imported_post_path": "_posts/2023-10-19-interview-famitsu-detective-pikachu-returns-ishihara-jinnai.md",
        "post_file": "_posts/2023-10-19-interview-famitsu-detective-pikachu-returns-ishihara-jinnai.md"
    },
    {
        "id": "PKMN-1059",
        "title": "GAME Watch 独家专访：红白机名作《旋转方块（Quinty）》归来！GAME FREAK 创业元老杉森建×增田顺一×森本茂树回顾黎明期与宝可梦的原点",
        "original_title": "ついにファミコンの名作、あの「クインティ」が帰ってきた！ Wii Uバーチャルコンソールでプレイ可能!!制作を手掛けたゲームフリークの杉森建氏、増田順一氏、森本茂樹氏が当時を振り返る",
        "url": "https://game.watch.impress.co.jp/docs/news/655639.html",
        "date": "2014-07-02",
        "people": [
            "杉森建",
            "增田顺一",
            "森本茂树"
        ],
        "generation": "Gen 1",
        "language": "JA",
        "outlet": "GAME Watch",
        "type": "Web Interview",
        "tags": [
            "Game Freak",
            "旋转方块",
            "Quinty",
            "杉森建",
            "增田顺一",
            "森本茂树",
            "田尻智",
            "红白机",
            "Famicom",
            "宝可梦原点",
            "JA"
        ],
        "summary": "GAME Watch 深度专访 GAME FREAK 创业三元老：杉森建、增田顺一与森本茂树回溯处女作《旋转方块（Quinty）》研发秘辛，披露田尻智自制纸箱开发机、汇编语言作曲、点阵像素绘制，以及直接奠定《宝可梦 赤·绿》创生基石的同人精神。",
        "status": "imported",
        "imported_post_slug": "2014-07-02-interview-gamewatch-quinty-gamefreak-origins-sugimori-masuda-morimoto",
        "imported_post_path": "_posts/2014-07-02-interview-gamewatch-quinty-gamefreak-origins-sugimori-masuda-morimoto.md",
        "post_file": "_posts/2014-07-02-interview-gamewatch-quinty-gamefreak-origins-sugimori-masuda-morimoto.md"
    }
]

def main():
    # Update JSON
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    existing_ids = {item["id"] for item in data}
    added_count = 0
    for b in BATCH_22:
        if b["id"] not in existing_ids:
            data.append(b)
            added_count += 1
            print(f"Added {b['id']} to JSON: {b['title']}")
        else:
            print(f"{b['id']} already exists in JSON")

    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Total entries in JSON: {len(data)} (added {added_count})")

    # Update CSV
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    existing_csv_ids = {r["id"] for r in rows if "id" in r}
    csv_added = 0
    for b in BATCH_22:
        if b["id"] not in existing_csv_ids:
            new_row = {fn: "" for fn in fieldnames}
            new_row["id"] = b["id"]
            new_row["title"] = b["title"]
            new_row["original_title"] = b["original_title"]
            new_row["url"] = b["url"]
            new_row["date"] = b["date"]
            new_row["people"] = "; ".join(b["people"])
            new_row["generation"] = b["generation"]
            new_row["language"] = b["language"]
            new_row["outlet"] = b["outlet"]
            new_row["type"] = b["type"]
            new_row["tags"] = "; ".join(b["tags"])
            new_row["summary"] = b["summary"]
            new_row["status"] = b["status"]
            if "imported_post_slug" in fieldnames:
                new_row["imported_post_slug"] = b["imported_post_slug"]
            if "imported_post_path" in fieldnames:
                new_row["imported_post_path"] = b["imported_post_path"]
            if "post_file" in fieldnames:
                new_row["post_file"] = b["post_file"]
            rows.append(new_row)
            csv_added += 1
            print(f"Added {b['id']} to CSV")

    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Total rows in CSV: {len(rows)} (added {csv_added})")

if __name__ == "__main__":
    main()
