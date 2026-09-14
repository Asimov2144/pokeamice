import urllib.request
import re
import html
from pathlib import Path

url = "https://web.archive.org/web/20221226222004/https://www.nintendo.co.jp/nom/0211/"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read().decode("shift_jis", errors="replace")
        m_title = re.search(r"<title>(.*?)</title>", raw, re.I)
        print("NOM 0211 Title:", m_title.group(1).strip() if m_title else "No title")
        links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', raw, re.I | re.DOTALL)
        print(f"Found {len(links)} links:")
        for h, t in links:
            clean = re.sub(r"<[^>]+>", "", t).strip().replace("\n", " ")
            if clean and not h.startswith("#") and "archive.org" not in h:
                print(f"  [{clean[:40]}] -> {h}")
except Exception as e:
    print("Error:", e)
