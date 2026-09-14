import urllib.request

headers = {'User-Agent': 'Mozilla/5.0'}

# Test URLs for BW vol2 (Creatures) and B2W2
probe_urls = [
    # BW vol 2?
    "https://www.nintendo.co.jp/ds/interview/irbj/vol2/index.html",
    "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index.html",
    # B2W2? Where was B2W2 hosted?
    # Let's check Nintendo DS interview list or B2W2 url
    "https://www.nintendo.co.jp/ds/interview/irej/index.html",
    "https://www.nintendo.co.jp/ds/interview/irej/vol1/index.html",
    "https://www.nintendo.co.jp/ds/interview/index.html",
    "https://www.nintendo.co.jp/ds/interview/b2w2/index.html",
    "https://www.nintendo.co.jp/nom/",
    # Let's search Nintendo's interview site index
    "https://www.nintendo.co.jp/interview/index.html"
]

for u in probe_urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            print(f"[OK] {u} ({len(data)} bytes, HTTP {resp.status})")
    except Exception as e:
        print(f"[FAIL] {u}: {e}")
