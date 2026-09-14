import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/pokemon_1000_interviews.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

print(f"Total catalog entries: {len(catalog)}")

keywords = ['Sleep', 'CGWorld', '远藤', 'Xevious', '田尻', '增田', '大森', '石原', '岩田', '杉森', '任天堂', 'Fami通', 'Nintendo Dream', 'Game Informer', '4Gamer', 'Dengeki']

results = []
for it in catalog:
    if it.get('status') == 'imported':
        continue
    title = it.get('title') or ''
    orig_title = it.get('original_title') or ''
    text = title + ' ' + orig_title
    for k in keywords:
        if k.lower() in text.lower():
            results.append(it)
            break

print(f"Found {len(results)} candidate entries:")
for it in results[:35]:
    cid = it.get('id')
    yr = it.get('year')
    title = (it.get('title') or '')[:60]
    src = it.get('source_url') or it.get('source') or ''
    print(f"[{cid}] ({yr}) {title} | src={src}")
