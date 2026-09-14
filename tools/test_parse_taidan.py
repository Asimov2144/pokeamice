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
        return cache_file.read_bytes().decode("cp932", errors="replace")

    url_https = url.replace("http://", "https://")
    for attempt in range(4):
        try:
            req = urllib.request.Request(url_https, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as r:
                raw_bytes = r.read()
                cache_file.write_bytes(raw_bytes)
                print(f"  [SAVED] {filename} ({len(raw_bytes)} bytes)")
                return raw_bytes.decode("cp932", errors="replace")
        except Exception as e:
            print(f"  [RETRY {attempt+1}] {url_https}: {e}")
            time.sleep(2 * (attempt + 1))
    return ""

print("Checking taidan1 pages:")
for p in range(1, 5):
    u = f"https://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/taidan1/page0{p}.html"
    c = fetch_and_cache(u, f"nom_0007_taidan1_page0{p}.html")
    m = re.search(r"<title>(.*?)</title>", c, re.I)
    title = m.group(1).strip() if m else "No title"
    print(f"  taidan1 p0{p}: {title} (len={len(c)})")
    time.sleep(1)

print("\nChecking taidan2 pages:")
for p in range(1, 5):
    u = f"https://web.archive.org/web/20221026124927/https://www.nintendo.co.jp/nom/0007/taidan2/page0{p}.html"
    c = fetch_and_cache(u, f"nom_0007_taidan2_page0{p}.html")
    m = re.search(r"<title>(.*?)</title>", c, re.I)
    title = m.group(1).strip() if m else "No title"
    print(f"  taidan2 p0{p}: {title} (len={len(c)})")
    time.sleep(1)
