import json
from pathlib import Path

catalog = json.loads(Path("data/pokemon_1000_interviews.json").read_text(encoding="utf-8"))

print(f"Total interviews: {len(catalog)}")
imported = [x for x in catalog if x.get("status") == "imported"]
print(f"Imported: {len(imported)}")

unimported = [x for x in catalog if x.get("status") != "imported"]

# Let's see sources with highest count
sources = {}
for x in unimported:
    src = x.get("source_name") or "Unknown"
    sources[src] = sources.get(src, 0) + 1

print("\nTop Sources in Unimported:")
for src, cnt in sorted(sources.items(), key=lambda item: -item[1])[:20]:
    print(f"  {cnt:3d} : {src}")

# Let's inspect early interviews (pre-2006)
early = [x for x in unimported if x.get("date") and x.get("date") < "2006"]
print(f"\nPre-2006 Interviews: {len(early)}")
for x in sorted(early, key=lambda item: item.get("date", ""))[:25]:
    title = (x.get("title") or "").strip().replace("\n", " ")
    url = x.get("source_url") or ""
    print(f"  [{x.get('id')}] {x.get('date')} | {x.get('source_name')} | {title[:45]} | {url[:50]}")
