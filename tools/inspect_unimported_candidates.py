import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

with open("data/unimported_japanese_interviews_curation.json", "r", encoding="utf-8") as f:
    ja = json.load(f)

print(f"=== TOP 15 UNIMPORTED JAPANESE INTERVIEWS ({len(ja)} total) ===")
for i, item in enumerate(ja[:15], 1):
    print(f"{i}. {item.get('title')}")
    print(f"   URL: {item.get('url')}")
    print(f"   Tags: {item.get('tags')}")

with open("data/unimported_english_interviews_curation.json", "r", encoding="utf-8") as f:
    en = json.load(f)

print(f"\n=== TOP 15 UNIMPORTED ENGLISH INTERVIEWS ({len(en)} total) ===")
for i, item in enumerate(en[:15], 1):
    print(f"{i}. {item.get('title')}")
    print(f"   URL: {item.get('url')}")
    print(f"   Tags: {item.get('tags')}")
