import json

with open("data/pokemon_1000_interviews.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    if item.get("id") in ["PKMN-0016", "PKMN-0015", "PKMN-0012"]:
        print(f"ID: {item.get('id')}")
        print(f"  Title: {item.get('title')}")
        print(f"  Source: {item.get('source_name')}")
        print(f"  Date: {item.get('date')}")
        print(f"  URL: {item.get('source_url')}")
        print(f"  Status: {item.get('status')}")
        print(f"  Post File: {item.get('post_file')}")
