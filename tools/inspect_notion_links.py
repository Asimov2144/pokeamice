import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("_data/notion_interviews.json", "r", encoding="utf-8") as f:
    notion_data = json.load(f)

rows = notion_data.get("rows", [])
print(f"Total rows in notion_interviews.json: {len(rows)}")

valid_notion = []
for r in rows:
    title = r.get("Title") or r.get("Name") or ""
    link = r.get("Links") or ""
    tags = r.get("Tags") or []
    date = r.get("Date") or ""
    if link and title:
        valid_notion.append({
            "title": title,
            "link": link,
            "tags": tags,
            "date": date
        })

print(f"Rows with links: {len(valid_notion)}")
for idx, v in enumerate(valid_notion[:20]):
    print(f"[{idx+1}] {v['title']} | {v['link'][:60]} | tags={v['tags']}")
