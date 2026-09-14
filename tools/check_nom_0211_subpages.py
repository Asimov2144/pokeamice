import urllib.request
import re
import html

base = "https://web.archive.org/web/20221226222004/https://www.nintendo.co.jp/nom/0211/"
pages = [
    "sitemap.html",
    "01/01_02/index.html",
    "01/01_04/index.html",
    "01/01_05/index.html"
]

for p in pages:
    u = base + p
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode("shift_jis", errors="replace")
            m = re.search(r"<title>(.*?)</title>", raw, re.I)
            title = m.group(1).strip() if m else "No title"
            print(f"{p} -> {title} (len={len(raw)})")
            # If sitemap, print links
            if p == "sitemap.html":
                links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', raw, re.I | re.DOTALL)
                for h, t in links:
                    clean = re.sub(r"<[^>]+>", "", t).strip().replace("\n", " ")
                    if clean and not h.startswith("#") and "archive.org" not in h:
                        print(f"    [{clean[:40]}] -> {h}")
    except Exception as e:
        print(f"{p} -> Error {e}")
