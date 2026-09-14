import urllib.request

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

test_urls = [
    # Famitsu 1
    ("famitsu_ohmori_iwao.jpg", "https://www.famitsu.com/images/000/143/850/y_59df9b5882ecb.jpg"),
    ("famitsu_ohmori.jpg", "https://www.famitsu.com/images/000/143/850/y_59df9b589382b.jpg"),
    ("famitsu_iwao.jpg", "https://www.famitsu.com/images/000/143/850/y_59df9b584eecb.jpg"),
    ("famitsu_battle.jpg", "https://www.famitsu.com/images/000/143/850/l_59e84ac8cb882.jpg"),
    # Famitsu 2
    ("famitsu_iwao_suginaka.jpg", "https://www.famitsu.com/images/000/148/529/y_5a39ff72557da.jpg"),
    ("famitsu_story_necrozma.jpg", "https://www.famitsu.com/images/000/148/529/l_5a3a002c3f158.jpg"),
    ("famitsu_rainbow_rocket.jpg", "https://www.famitsu.com/images/000/148/529/l_5a39ff72459ed.jpg"),
    ("famitsu_guzma.jpg", "https://www.famitsu.com/images/000/148/529/l_5a39ff724dad6.jpg"),
    # CGWORLD
    ("cgw_prof.jpg", "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/prof.jpg"),
    ("cgw_pipeline.jpg", "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/A01a.jpg"),
    ("cgw_database.jpg", "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/A02a.jpg"),
    ("cgw_modeling.jpg", "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/B01a.jpg"),
    ("cgw_texture.jpg", "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/B02a.jpg"),
    ("cgw_solgaleo.jpg", "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/C01a.jpg"),
    ("cgw_lunala.jpg", "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/C02a.jpg"),
    ("cgw_rigging.jpg", "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/D01a.jpg"),
    ("cgw_human_rig.jpg", "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/E01a.jpg"),
    ("cgw_vfx.jpg", "https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/E02a.jpg"),
]

for name, u in test_urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            print(f"[OK] {name}: {len(data)} bytes")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
