import urllib.request

headers = {'User-Agent': 'Mozilla/5.0'}
base = "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/"

for fn in ["img/photo01.jpg", "img/mainvisual1.jpg", "img/sub_photo01.jpg"]:
    u = base + fn
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            print(f"[OK] {fn}: {len(data)} bytes")
    except Exception as e:
        print(f"[FAIL] {fn}: {e}")
