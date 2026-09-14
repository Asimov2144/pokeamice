import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/pokemon_1000_interviews.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

print("=== N.O.M 2000-12 Crystal ===")
for d in catalog:
    if 'PKMN-0111' <= d.get('id', '') <= 'PKMN-0114':
        print(d['id'], d.get('status'), d.get('title'), d.get('url'))

print("\n=== Early Guidebook / Milestone Interviews ===")
for d in catalog:
    if d.get('id') in ['PKMN-0146', 'PKMN-0147', 'PKMN-0148', 'PKMN-0149', 'PKMN-0150']:
        print(d['id'], d.get('status'), d.get('title'), d.get('url'))

print("\n=== Developer Asks (Arceus & SV) ===")
for d in catalog:
    if 'PKMN-0656' <= d.get('id', '') <= 'PKMN-0665':
        print(d['id'], d.get('status'), d.get('title'), d.get('url'))
