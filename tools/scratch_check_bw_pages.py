import urllib.request

headers = {'User-Agent': 'Mozilla/5.0'}

for i in range(1, 10):
    fn = "index.html" if i == 1 else f"index{i}.html"
    u = f"https://www.nintendo.co.jp/ds/interview/irbj/vol1/{fn}"
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            print(f"[OK] {fn}: {len(data)} bytes, HTTP {resp.status}")
    except Exception as e:
        print(f"[END/FAIL] {fn}: {e}")
        break
