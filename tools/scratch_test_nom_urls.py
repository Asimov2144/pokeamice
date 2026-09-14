import urllib.request

headers = {'User-Agent': 'Mozilla/5.0'}

test_nom_urls = [
    "https://www.nintendo.co.jp/nom/0007/index.html",
    "https://www.nintendo.co.jp/nom/0007/gamefreak/index.html",
    "https://www.nintendo.co.jp/nom/0007/game/index.html",
    "https://www.nintendo.co.jp/nom/0007/tokusyu/index.html",
    "https://www.nintendo.co.jp/nom/0007/anisen/index.html",
    "https://www.nintendo.co.jp/nom/0211/index.html", # 2002-11 Ruby Sapphire
    "https://www.nintendo.co.jp/nom/0211/p01/index.html",
    "https://www.nintendo.co.jp/nom/0211/p02/index.html",
    "https://www.nintendo.co.jp/nom/0211/p03/index.html",
]

for u in test_nom_urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            print(f"[OK] {u} ({len(data)} bytes, HTTP {resp.status})")
    except Exception as e:
        print(f"[FAIL] {u}: {e}")
