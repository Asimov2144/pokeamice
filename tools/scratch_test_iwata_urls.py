import urllib.request

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

test_urls = [
    "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index.html",
    "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/index2.html",
    "https://www.nintendo.co.jp/ds/interview/ipkj/vol2/index.html",
    "https://www.nintendo.co.jp/ds/interview/irbj/vol1/index.html", # BW
    "https://www.nintendo.co.jp/ds/interview/irbj/vol2/index.html", # BW Creatures
    "https://www.nintendo.co.jp/3ds/interview/ired/vol1/index.html"  # XY
]

for u in test_urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            print(f"[OK] {u} ({len(data)} bytes, HTTP {resp.status})")
    except Exception as e:
        print(f"[FAIL] {u}: {e}")
