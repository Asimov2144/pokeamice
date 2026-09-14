import urllib.request

headers = {'User-Agent': 'Mozilla/5.0'}
base = "https://www.nintendo.co.jp/ds/interview/irej/vol1/"

test_assets = [
    ("nintendo_b2w2_mainvisual1.jpg", base + "img/mainvisual1.jpg"),
    ("nintendo_b2w2_photo1.jpg", base + "img/photo1.jpg"),
    ("nintendo_b2w2_photo2.jpg", base + "img/photo2.jpg"),
    ("nintendo_b2w2_photo3.jpg", base + "img/photo3.jpg"),
    ("nintendo_b2w2_photo4.jpg", base + "img/photo4.jpg"),
    ("nintendo_b2w2_photo10.jpg", base + "img/photo10.jpg"),
    ("black_kyurem.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10022.png"),
    ("white_kyurem.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10023.png"),
    ("keldeo.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/647.png"),
    ("meloetta.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/648.png"),
]

for name, u in test_assets:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            print(f"[OK] {name}: {len(data)} bytes")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
