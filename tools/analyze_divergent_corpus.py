import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("data/pokemon_1000_interviews.json", "r", encoding="utf-8") as f:
    cat = json.load(f)

print(f"Total entries in catalog: {len(cat)}")
imported = [it for it in cat if it.get("status") == "imported"]
print(f"Total already imported: {len(imported)}")

categories = {
    "【创作者哲学与业界巨匠对谈】(Founders & Master Dialogues)": [
        "田尻", "宫本", "岩田", "石原", "远藤", "Xevious", "同人志", "Game On", "Heart of a Gamer", "GDC"
    ],
    "【角色造型设计与废案考古】(Creature Design & Cut Content)": [
        "杉森", "西田", "大村", "James Turner", "水谷", "有贺", "高老丸", "Gorochu", "Cut Content", "Helix", "草图", "废案", "原型"
    ],
    "【音频生态与芯片音乐工程】(Soundtracks, Chiptunes & Audio)": [
        "音乐", "Sound", "作曲", "景山", "一之濑", "Toby Fox", "合成器", "调音台", "声效", "Sound Driver", "音频"
    ],
    "【技术架构、底层工程与网络狂潮】(Hardcore Engineering & Networking)": [
        "CEDEC", "3D", "建模", "着色器", "骨骼", "程序员", "森本", "服务器", "Kubernetes", "云端", "通信", "网络"
    ],
    "【旁支宇宙与生态扩展】(Spinoffs, TCG & Ecological Lifestyle)": [
        "不可思议迷宫", "TCG", "卡牌", "有田满弘", "竞技场", "Colosseum", "XD", "暗影", "Sleep", "随乐拍", "Snap", "Ranger", "巡护员", "名侦探"
    ],
    "【跨文化本地化与全球巡礼】(Localization & Cultural Adaptations)": [
        "本地化", "Localization", "Ogasawara", "小笠原", "Le Monde", "世界报", "El Pais", "国家报", "法国", "西班牙", "Eurogamer", "Polygon", "Wired"
    ]
}

print("\n" + "="*80)
print("CORPUS DIVERGENCE ANALYSIS")
print("="*80)

for cname, kwlist in categories.items():
    matched = []
    for it in cat:
        text = f"{it.get('title') or ''} {it.get('original_title') or ''} {it.get('source') or ''} {it.get('source_url') or ''} {it.get('summary') or ''} {' '.join(it.get('people') or [])}"
        if any(k.lower() in text.lower() for k in kwlist):
            matched.append(it)
    imp = [it for it in matched if it.get("status") == "imported"]
    unimp = [it for it in matched if it.get("status") != "imported"]
    print(f"\n{cname}")
    print(f"  Total matched: {len(matched)} | Imported: {len(imp)} | Unimported (Available to Harvest): {len(unimp)}")
    print("  Top 6 High-Value Unimported Candidates:")
    for it in unimp[:6]:
        cid = it.get("id")
        yr = it.get("year") or "Undated"
        title = (it.get("title") or "")[:55]
        src = (it.get("source_url") or it.get("source") or "")[:45]
        print(f"    * [{cid}] ({yr}) {title} | {src}")
