import urllib.request

headers = {'User-Agent': 'Mozilla/5.0'}
base = "https://www.nintendo.co.jp/ds/interview/irbj/vol1/"

for fn in ["img/photo1.jpg", "img/mainvisual1.jpg", "img/photo10.jpg"]:
    u = base + fn
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            print(f"[OK] {fn}: {len(data)} bytes")
    except Exception as e:
        print(f"[FAIL] {fn}: {e}")
