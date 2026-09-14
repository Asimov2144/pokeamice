import json
from pathlib import Path
import re
import sys
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


with open('_data/notion_interviews.json', 'r', encoding='utf-8') as f:
    notion = json.load(f)

rows = notion['rows']
print(f"Total rows in notion: {len(rows)}")

posts = list(Path('_posts').glob('*interview*.md'))
print(f"Total posts in _posts: {len(posts)}")

post_data = []
for p in posts:
    text = p.read_text(encoding='utf-8')
    parts = text.split('---', 2)
    if len(parts) >= 3:
        try:
            fm = yaml.safe_load(parts[1])
            title = fm.get('title', '')
            source = fm.get('source', '')
            post_data.append({
                'file': p.name,
                'title': title,
                'source': str(source),
                'items_count': len(fm.get('parallel_items', []))
            })
        except Exception as e:
            pass

print(f"Parsed {len(post_data)} valid interview posts.")

matched = []
unmatched = []

for r in rows:
    rtitle = (r.get('Title') or r.get('Name') or '').strip()
    rlink = (r.get('Links') or '').strip()
    
    found_post = None
    for p in post_data:
        # compare URL or link
        if rlink and (rlink in p['source'] or (p['source'] and p['source'] in rlink)):
            found_post = p
            break
        # Clean titles for comparison
        clean_rtitle = re.sub(r'[^\w]', '', rtitle.lower())
        clean_ptitle = re.sub(r'[^\w]', '', p['title'].lower())
        if clean_rtitle and (clean_rtitle in clean_ptitle or clean_ptitle in clean_rtitle):
            found_post = p
            break
            
    if found_post:
        matched.append((r, found_post))
    else:
        unmatched.append(r)

print(f"Matched: {len(matched)}")
print(f"Unmatched: {len(unmatched)}")

print("\n--- Unmatched Items in Notion ---")
for idx, u in enumerate(unmatched, 1):
    print(f"{idx}. {u.get('Title')} | {u.get('Links')}")
