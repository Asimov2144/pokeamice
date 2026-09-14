import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("_data/notion_interviews.json", "r", encoding="utf-8") as f:
    notion_data = json.load(f)

rows = notion_data.get("rows", [])
print(f"Total rows: {len(rows)}")

for idx, r in enumerate(rows):
    title = r.get("Title") or r.get("Name") or ""
    link = r.get("Links") or ""
    tags = r.get("Tags") or []
    date = r.get("Date") or ""
    print(f"[{idx+1}] {date} | {title} | {link} | {tags}")
