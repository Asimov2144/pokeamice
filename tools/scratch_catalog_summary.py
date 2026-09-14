import json

with open("data/pokemon_1000_interviews.json", "r", encoding="utf-8") as f:
    data = json.load(f)

imported = [item for item in data if item.get("status") == "imported"]
print(f"Total interviews in catalog: {len(data)}")
print(f"Total imported interviews: {len(imported)}")
print("\nList of imported interviews:")
for i, item in enumerate(sorted(imported, key=lambda x: x.get("date", "")), 1):
    print(f"  {i:02d}. [{item.get('id')}] ({item.get('date')}) {item.get('source_name', 'Unknown')}: {item.get('title')[:45]}... -> {item.get('post_file')}")
