#!/usr/bin/env python3
"""
Register Batch 23 entries into database:
- PKMN-1060: Game Informer 2017: Here's How Game Freak Designs Pokémon Creatures (Sugimori & Masuda)
- PKMN-1061: Game Informer 2017: Why Ruby And Sapphire Were The Most Challenging Pokémon To Make (Masuda)
- PKMN-1062: FUN'S PROJECT 2018: Atsuko Nishida × Shoko Nakagawa Character Design Special (Nishida & Nakagawa)
"""

import sys
import json
import csv
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

JSON_PATH = Path("data/pokemon_1000_interviews.json")
CSV_PATH = Path("data/pokemon_1000_interviews.csv")

BATCH_23 = [
    {
        "id": "PKMN-1060",
        "title": "Game Informer 独家特写：Game Freak 是如何设计宝可梦的？——杉森建与增田顺一深度复盘生物设计法则、评审委员会机制与 3D 演进",
        "original_title": "Here's How Game Freak Designs Pokémon Creatures",
        "url": "https://www.gameinformer.com/b/features/archive/2017/08/10/heres-how-game-freak-designs-pokemon-creatures.aspx",
        "date": "2017-08-10",
        "people": [
            "杉森建",
            "增田顺一"
        ],
        "generation": "Gen 7",
        "language": "EN",
        "outlet": "Game Informer",
        "type": "Web Feature",
        "tags": [
            "Game Informer",
            "Game Freak",
            "杉森建",
            "增田顺一",
            "宝可梦设计",
            "生物设计",
            "角色设计",
            "第七世代",
            "日月",
            "3D建模",
            "EN"
        ],
        "summary": "2017年《Game Informer》深入探访 Game Freak 东京总部，艺术总监杉森建与制作人增田顺一首次完整解密宝可梦的诞生管线：从全员提案制、由核心主创组成的‘设计评审委员会’，到杉森建独创的‘反差美学法则’（在帅气的怪物上加点滑稽，在可爱的精灵上加点惊悚），以及从 2D 点阵过渡到 3D 全模型时代对宝可梦眼部表情与动态剪影的严苛要求。",
        "status": "imported",
        "imported_post_slug": "2017-08-10-interview-gameinformer-how-game-freak-designs-pokemon-creatures",
        "imported_post_path": "_posts/2017-08-10-interview-gameinformer-how-game-freak-designs-pokemon-creatures.md",
        "post_file": "_posts/2017-08-10-interview-gameinformer-how-game-freak-designs-pokemon-creatures.md"
    },
    {
        "id": "PKMN-1061",
        "title": "Game Informer 独家专访：为何《红宝石·蓝宝石》是 Game Freak 史上最艰巨的一役？——增田顺一复盘 GBA 转型阵痛、健康危机与破局之道",
        "original_title": "Why Ruby And Sapphire Were The Most Challenging Pokémon To Make",
        "url": "https://www.gameinformer.com/b/features/archive/2017/08/14/why-ruby-and-sapphire-were-the-most-challenging-pokemon-to-make.aspx",
        "date": "2017-08-14",
        "people": [
            "增田顺一"
        ],
        "generation": "Gen 3",
        "language": "EN",
        "outlet": "Game Informer",
        "type": "Web Interview",
        "tags": [
            "Game Informer",
            "Game Freak",
            "增田顺一",
            "红宝石·蓝宝石",
            "GBA",
            "第三世代",
            "开发秘辛",
            "丰缘地区",
            "EN"
        ],
        "summary": "在第三世代《宝可梦 红宝石·蓝宝石》开发期间，Game Freak 面临前所未有的生死关头：坊间充斥着‘宝可梦热潮已死’的断言，技术从黑白GB一跃进入GBA色彩绚烂的全新硬件。首次独自挑起总监兼作曲重担的增田顺一，因背负全社命运的极端焦虑与高压突发重度胃病送医急救、佩戴动态心电监护仪坚持研发。本访谈真实还原了增田顺一如何带领团队以特性、性格、双打对战等划时代系统实现逆风翻盘的悲壮历史。",
        "status": "imported",
        "imported_post_slug": "2017-08-14-interview-gameinformer-why-ruby-and-sapphire-were-most-challenging",
        "imported_post_path": "_posts/2017-08-14-interview-gameinformer-why-ruby-and-sapphire-were-most-challenging.md",
        "post_file": "_posts/2017-08-14-interview-gameinformer-why-ruby-and-sapphire-were-most-challenging.md"
    },
    {
        "id": "PKMN-1062",
        "title": "FUN'S PROJECT 独家对谈：皮卡丘之母西田敦子 × 中川翔子角色设计特辑——从大福饼、松鼠颊囊到点阵原画与女性创作者心得",
        "original_title": "グラフィックデザイナー・イラストレーター にしだあつこ対談 - 中川翔子のポップカルチャー・ラボ",
        "url": "https://funs-project.com/poplab/007/",
        "date": "2018-06-25",
        "people": [
            "西田敦子",
            "中川翔子"
        ],
        "generation": "Gen 7",
        "language": "JA",
        "outlet": "FUN'S PROJECT",
        "type": "Web Interview",
        "tags": [
            "西田敦子",
            "中川翔子",
            "皮卡丘",
            "仙子伊布",
            "风妖精",
            "角色设计",
            "点阵绘",
            "FUN'S PROJECT",
            "伊布",
            "初代开发",
            "JA"
        ],
        "summary": "大日本印刷创作者共创服务‘FUN'S PROJECT’专栏特辑。宝可梦初代王牌设计师、‘皮卡丘之母’西田敦子与知名艺人兼漫画家中川翔子展开深度对谈。西田敦子首次详述：仙子伊布为何采用粉红配天蓝的大胆配色、成吉思汗烤肉如何启发风妖精、随身携带的A5大学笔记里藏着的‘大福饼’构想、宝可梦设计精髓‘尽量精简部件以确保剪影辨识度’的黄金法则，以及早期受制于Game Boy点阵与色阶限制如何反而锤炼出传世设计的独到心法。",
        "status": "imported",
        "imported_post_slug": "2018-06-25-interview-funsproject-atsuko-nishida-shoko-nakagawa-character-design",
        "imported_post_path": "_posts/2018-06-25-interview-funsproject-atsuko-nishida-shoko-nakagawa-character-design.md",
        "post_file": "_posts/2018-06-25-interview-funsproject-atsuko-nishida-shoko-nakagawa-character-design.md"
    }
]

def main():
    # Update JSON
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    existing_ids = {item["id"] for item in data}
    added_count = 0
    for b in BATCH_23:
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
    for b in BATCH_23:
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
