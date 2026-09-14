import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("data/pokemon_1000_interviews.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

unimported = [x for x in catalog if x.get("status") != "imported"]
print(f"Total unimported in catalog: {len(unimported)}")

# Let's inspect different categories of unimported
# 1. Official recruitment or developer crosstalk interviews (like Game Freak / Creatures / TPC)
# 2. Major developer interviews (Tajiri, Sugimori, Masuda, Ohmori, Ishihara)
# 3. Famous magazines/outlets (Famitsu, Dengeki, 4Gamer, CEDEC, Iwata Asks)

crosstalk_recruit = []
major_devs = []
tech_art = []

for it in unimported:
    title = it.get("title", "")
    otitle = it.get("original_title", "")
    url = it.get("url", "")
    people = it.get("people", [])
    outlet = it.get("outlet", "")
    text = f"{title} {otitle} {url} {' '.join(people)} {outlet}"
    
    if any(k in text.lower() for k in ["recruit", "crosstalk", "座談会", "採用"]):
        crosstalk_recruit.append(it)
    elif any(k in text for k in ["CEDEC", "CGWORLD", "CGWorld", "3D", "サウンド", "Sound"]):
        tech_art.append(it)
    elif any(p in ["田尻智", "增田顺一", "杉森建", "大森滋", "石原恒和"] for p in people):
        major_devs.append(it)

print(f"Crosstalk/Recruit candidates: {len(crosstalk_recruit)}")
for it in crosstalk_recruit[:10]:
    print(f"  [{it['id']}] {it['title']} ({it['date']}) -> {it['url']}")

print(f"\nTech/Art candidates: {len(tech_art)}")
for it in tech_art[:10]:
    print(f"  [{it['id']}] {it['title']} ({it['date']}) -> {it['url']}")

print(f"\nMajor Devs candidates: {len(major_devs)}")
for it in major_devs[:10]:
    print(f"  [{it['id']}] {it['title']} ({it['date']}) -> {it['url']}")
