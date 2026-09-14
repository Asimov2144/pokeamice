import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("data/pokemon_1000_interviews.json", "r", encoding="utf-8") as f:
    cat = json.load(f)

targets = ['PKMN-0837', 'PKMN-0838', 'PKMN-0841', 'PKMN-0124', 'PKMN-0128', 'PKMN-0041', 'PKMN-0060', 'PKMN-0104', 'PKMN-0688', 'PKMN-0676']
for it in cat:
    if it.get('id') in targets:
        cid = it.get('id')
        yr = it.get('year')
        title = it.get('title')
        url = it.get('source_url')
        print(f"[{cid}] ({yr}) {title} | url={url}")
