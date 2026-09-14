from bs4 import BeautifulSoup
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")

html = Path("tools/cache_batch_17/PKMN-1005_raw.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")

talkers = soup.find_all(class_="talker")
print(f"Total talker blocks: {len(talkers)}")
for i, t in enumerate(talkers[:5]):
    name_el = t.find(class_="talker__name")
    name = name_el.get_text().strip() if name_el else "Unknown"
    # Find next sibling or parent structure
    p_el = t.find_next_sibling("p") or t.parent.find("p")
    p_text = p_el.get_text().strip() if p_el else ""
    print(f"[{i}] Speaker: {name} | Text: {p_text[:80]}")
