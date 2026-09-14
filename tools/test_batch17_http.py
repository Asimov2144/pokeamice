import urllib.request
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

urls = [
    ("PKMN-1005", "https://www.gamefreak.co.jp/recruit/crosstalk-system-programmer/"),
    ("PKMN-1007", "https://www.gamefreak.co.jp/recruit/crosstalk-scenario/"),
    ("PKMN-1008", "https://www.gamefreak.co.jp/recruit/crosstalk-new-graduate/"),
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for cid, url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8")
            soup = BeautifulSoup(html, "html.parser")
            print(f"[{cid}] Success! Title: {soup.title.string if soup.title else 'No title'} (HTML length: {len(html)})")
    except Exception as e:
        print(f"[{cid}] Failed: {e}")
