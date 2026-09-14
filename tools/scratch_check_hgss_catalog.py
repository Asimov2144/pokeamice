import json

with open("data/pokemon_1000_interviews.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    cid = item.get("id")
    if cid in [f"PKMN-063{i}" for i in range(6, 10)]:
        print(f"ID: {cid}")
        print(f"  Title: {item.get('title')}")
        print(f"  Date: {item.get('date')}")
        print(f"  URL: {item.get('source_url')}")
        print(f"  Status: {item.get('status')}")
