import json, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

with open('data/pokemon_1000_interviews.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

test_domains = ['www.4gamer.net', 'news.denfaminicogamer.jp', 'dengekionline.com', 'www.famitsu.com', 'cgworld.jp', 'www.gameinformer.com']
candidates = [d for d in catalog if d.get('status') != 'imported' and any(dom in d.get('url', '') for dom in test_domains)]

print(f"Testing {len(candidates)} candidates across major media outlets:")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
live_items = []
for d in candidates:
    u = d.get('url', '')
    status = 'TEST'
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            status = str(resp.status)
            if resp.status == 200:
                live_items.append((d, resp.status))
    except Exception as e:
        status = str(e)
    print(f"[{d['id']}] {status} | {d.get('title')[:40]} | {u}")

print(f"\nTotal Live Items: {len(live_items)}")
for item, code in live_items:
    print(f"  * [{item['id']}] {item.get('title')} ({item.get('url')})")
