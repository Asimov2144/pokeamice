import urllib.request
import sys
from bs4 import BeautifulSoup
from pathlib import Path
import json

sys.stdout.reconfigure(encoding="utf-8")

CACHE_DIR = Path("tools/cache_batch_17")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

urls = [
    ("PKMN-1005", "https://www.gamefreak.co.jp/recruit/crosstalk-system-programmer/"),
    ("PKMN-1007", "https://www.gamefreak.co.jp/recruit/crosstalk-scenario/"),
    ("PKMN-1008", "https://www.gamefreak.co.jp/recruit/crosstalk-new-graduate/"),
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for cid, url in urls:
    cache_file = CACHE_DIR / f"{cid}_raw.html"
    if not cache_file.exists():
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8")
            cache_file.write_text(html, encoding="utf-8")
    else:
        html = cache_file.read_text(encoding="utf-8")
        
    soup = BeautifulSoup(html, "html.parser")
    print(f"\n==================== {cid} ====================")
    print("Title:", soup.title.string.strip() if soup.title else "None")
    
    # Check images
    imgs = [img.get("src") for img in soup.find_all("img") if img.get("src")]
    print(f"Total images: {len(imgs)}")
    for img in imgs[:8]:
        print("  Img:", img)
        
    # Check headings
    h1 = [h.get_text().strip() for h in soup.find_all("h1")]
    h2 = [h.get_text().strip() for h in soup.find_all("h2")]
    h3 = [h.get_text().strip() for h in soup.find_all("h3")]
    print("H1:", h1)
    print("H2:", h2[:5])
    print("H3:", h3[:5])
