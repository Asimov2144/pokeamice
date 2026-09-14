import json
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

curation = json.load(open('data/unimported_japanese_interviews_curation.json', encoding='utf-8'))
print('Total in unimported_japanese_interviews_curation:', len(curation))

# Check against _posts
posts = list(Path('_posts').glob('*.md'))
post_texts = []
for p in posts:
    post_texts.append((p.name, p.read_text(encoding='utf-8')))

unimported_items = []
for idx, c in enumerate(curation):
    url = c.get('url', '')
    title = c.get('title', '')
    found = False
    for pname, ptext in post_texts:
        if url and url in ptext:
            found = True
            break
        short_title = title.split('（')[0].strip()
        if short_title and len(short_title) > 6 and short_title in ptext:
            found = True
            break
    if not found:
        unimported_items.append((idx, c))

print(f'Remaining truly unimported in curation: {len(unimported_items)} / {len(curation)}')
for idx, item in unimported_items:
    print(f"[{idx}] {item['title']} -> {item.get('url')}")
