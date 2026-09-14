import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/pokemon_1000_interviews.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

unimported = [d for d in catalog if d.get('status') != 'imported']
print('Total unimported:', len(unimported))

# Group by domain
domains = {}
for d in unimported:
    u = d.get('url', '')
    if '://' in u:
        dom = u.split('://')[1].split('/')[0]
        domains.setdefault(dom, []).append(d)

print('\n=== Domains in unimported ===')
for dom, items in sorted(domains.items(), key=lambda x: -len(x[1])):
    print(f"{dom}: {len(items)}")

print('\n=== Sample interviews by domain ===')
for dom in ['www.4gamer.net', 'dengekionline.com', 'game.watch.impress.co.jp', 'news.denfaminicogamer.jp', 'www.famitsu.com', 'www.nintendo.co.jp']:
    if dom in domains:
        print(f"\n--- {dom} ({len(domains[dom])}) ---")
        for item in domains[dom][:5]:
            print(f"  [{item['id']}] ({item.get('date')}) {item.get('title')[:45]} -> {item.get('url')}")
