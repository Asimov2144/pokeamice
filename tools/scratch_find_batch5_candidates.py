import json

with open("data/pokemon_1000_interviews.json", "r", encoding="utf-8") as f:
    data = json.load(f)

unimported = [it for it in data if it.get("status") != "imported"]
print(f"Total unimported in catalog: {len(unimported)}")

# Let's inspect early entries (e.g. from index 0 to 50) and entries with good titles
candidates = []
for it in unimported:
    cid = it.get("id")
    title = it.get("title", "")
    url = it.get("source_url") or it.get("archive_url") or it.get("url") or ""
    date = it.get("date", "")
    source = it.get("source_name", "")
    candidates.append((cid, title, date, source, url))

print("\nFirst 20 unimported candidates:")
for cid, title, date, source, url in candidates[:20]:
    print(f"[{cid}] ({date}) {source}: {title[:50]} | URL: {url[:50]}")
