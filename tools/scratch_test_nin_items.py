import json, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

with open('data/pokemon_1000_interviews.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

nin_items = [d for d in catalog if d.get('status') != 'imported' and 'nintendo.co.jp' in d.get('url', '')]
print(f"Unimported Nintendo.co.jp items ({len(nin_items)}):")

headers = {'User-Agent': 'Mozilla/5.0'}
for d in nin_items:
    u = d.get('url', '')
    status = 'TEST'
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = str(resp.status)
    except Exception as e:
        status = str(e)
    print(f"[{d['id']}] {status} | {d.get('date')} | {d.get('title')[:40]} | {u}")
