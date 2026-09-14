import urllib.request

headers = {'User-Agent': 'Mozilla/5.0'}
base = "https://www.nintendo.co.jp/ds/interview/irbj/vol1/"

photos = [
    ("nintendo_bw_mainvisual1.jpg", base + "img/mainvisual1.jpg"),
    ("nintendo_bw_photo1.jpg", base + "img/photo1.jpg"),
    ("nintendo_bw_photo2.jpg", base + "img/photo2.jpg"),
    ("nintendo_bw_photo3.jpg", base + "img/photo3.jpg"),
    ("nintendo_bw_photo4.jpg", base + "img/photo4.jpg"),
    ("nintendo_bw_photo5.jpg", base + "img/photo5.jpg"),
    ("nintendo_bw_photo6.jpg", base + "img/photo6.jpg"),
    ("nintendo_bw_photo10.jpg", base + "img/photo10.jpg"),
    ("reshiram.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/643.png"),
    ("zekrom.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/644.png"),
    ("snivy.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/495.png"),
    ("victini.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/494.png"),
]

for name, u in photos:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            print(f"[OK] {name}: {len(data)} bytes")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
