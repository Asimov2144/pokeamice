import urllib.request
import re
import html
import time
from pathlib import Path

CACHE_DIR = Path("data/cache_nom")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_and_cache(url: str, filename: str) -> str:
    cache_file = CACHE_DIR / filename
    if cache_file.exists() and cache_file.stat().st_size > 500:
        print(f"  [CACHE HIT] {filename}")
        return cache_file.read_bytes().decode("cp932", errors="replace")

    url_https = url.replace("http://", "https://")
    for attempt in range(5):
        try:
            req = urllib.request.Request(url_https, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as r:
                raw_bytes = r.read()
                cache_file.write_bytes(raw_bytes)
                print(f"  [SAVED] {filename} ({len(raw_bytes)} bytes)")
                return raw_bytes.decode("cp932", errors="replace")
        except Exception as e:
            print(f"  [RETRY {attempt+1}] {url_https}: {e}")
            time.sleep(3 * (attempt + 1))
    return ""

base = "https://web.archive.org/web/20221226222004/https://www.nintendo.co.jp/nom/0211/"
items = [
    ("01/01_02/index.html", "nom_0211_01_02.html"),
    ("01/01_04/index.html", "nom_0211_01_04.html"),
    ("01/01_05/index.html", "nom_0211_01_05.html")
]

for p, fn in items:
    fetch_and_cache(base + p, fn)
    time.sleep(1.5)
