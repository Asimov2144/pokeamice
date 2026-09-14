import json

with open("data/pokemon_1000_interviews.json", "r", encoding="utf-8") as f:
    data = json.load(f)

nom_entries = []
for it in data:
    title = it.get("title", "")
    url = it.get("source_url") or it.get("archive_url") or it.get("url") or ""
    source = it.get("source_name", "")
    if "nom" in title.lower() or "nom" in url.lower() or "nintendo online magazine" in title.lower() or "nintendo online magazine" in url.lower() or "nom" in source.lower():
        nom_entries.append((it.get("id"), title, it.get("date"), url))

print(f"Total NOM entries found: {len(nom_entries)}")
for cid, title, date, url in nom_entries[:25]:
    print(f"[{cid}] ({date}) {title} | {url[:60]}")
