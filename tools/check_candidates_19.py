import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

data = json.load(open("data/pokemon_1000_interviews.json", encoding="utf-8"))
unimported_10 = [x for x in data if x.get("status") != "imported" and x.get("id", "").startswith("PKMN-10")]
print(f"Total PKMN-10xx unimported: {len(unimported_10)}")
for x in unimported_10:
    print(f"{x.get('id')}: {x.get('title')} ({x.get('publication')}, {x.get('date')}) - {x.get('original_link')}")
