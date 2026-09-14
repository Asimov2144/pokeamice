import urllib.request

headers = {'User-Agent': 'Mozilla/5.0'}
pokeapi_urls = [
    ("dusk_mane_necrozma.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10155.png"),
    ("dawn_wings_necrozma.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10156.png"),
    ("ultra_necrozma.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/10157.png"),
    ("poipole.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/803.png"),
    ("solgaleo.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/791.png"),
    ("lunala.png", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/792.png"),
]

for name, u in pokeapi_urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            print(f"[OK] {name}: {len(data)} bytes")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
