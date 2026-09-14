import json

with open("data/pokemon_1000_interviews.json", "r", encoding="utf-8") as f:
    data = json.load(f)

iwata_asks = []
for it in data:
    title = it.get("title", "")
    url = it.get("source_url") or it.get("archive_url") or it.get("url") or ""
    if "iwata" in title.lower() or "iwata" in url.lower() or "社長が訊く" in title or "社长" in title:
        iwata_asks.append((it.get("id"), title, it.get("date"), url))

print(f"Total Iwata Asks entries found: {len(iwata_asks)}")
for cid, title, date, url in iwata_asks:
    print(f"[{cid}] ({date}) {title} | {url[:60]}")
