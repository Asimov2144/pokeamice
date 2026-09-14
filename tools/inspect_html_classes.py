from bs4 import BeautifulSoup
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")

html = Path("tools/cache_batch_17/PKMN-1005_raw.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")

# Find main content container
main = soup.find("main") or soup.find("article") or soup.find(class_="c-crosstalk") or soup

# Let's see what classes exist in the content
classes = set()
for tag in soup.find_all(True):
    for c in tag.get("class", []):
        if any(k in c for k in ["crosstalk", "talk", "member", "dialogue", "interview", "sec", "block"]):
            classes.add(c)

print("Matching classes:", sorted(list(classes)))

# Print sample text structure
talk_items = soup.find_all(class_=lambda x: x and ("talk" in x or "member" in x))
print(f"Total talk_items: {len(talk_items)}")
for it in talk_items[:10]:
    print("Tag:", it.name, "Class:", it.get("class"), "Text:", it.get_text().strip()[:80])
