import urllib.request

headers = {'User-Agent': 'Mozilla/5.0'}

urls = [
    ("nintendo_photo01.jpg", "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/img/photo01.jpg"),
    ("nintendo_photo02.jpg", "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/img/photo02.jpg"),
    ("nintendo_photo03.jpg", "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/img/photo03.jpg"),
    ("nintendo_photo04.jpg", "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/img/photo04.jpg"),
    ("nintendo_mainvisual1.jpg", "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/img/mainvisual1.jpg"),
    ("nintendo_sub_photo01.jpg", "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/img/sub_photo01.jpg"),
    ("nintendo_sub_photo04.jpg", "https://www.nintendo.co.jp/ds/interview/ipkj/vol1/img/sub_photo04.jpg"),
    ("mew.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/151.png"),
    ("pikachu.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"),
    ("ho_oh.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/250.png"),
    ("lugia.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/249.png")
]

for name, u in urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            print(f"[OK] {name}: {len(data)} bytes")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
