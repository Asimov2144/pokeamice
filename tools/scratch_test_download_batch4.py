import urllib.request
from pathlib import Path

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def test_download(url, out_name):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            print(f"[OK] {out_name}: {len(data)} bytes from {url}")
    except Exception as e:
        print(f"[FAIL] {out_name}: {e} from {url}")

test_download("https://www.famitsu.com/images/000/143/850/y_59df9b5882ecb.jpg", "famitsu_ohmori_iwao.jpg")
test_download("https://www.famitsu.com/images/000/148/529/y_5a39ff72557da.jpg", "famitsu_iwao_suginaka.jpg")
test_download("https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/prof.jpg", "cgworld_prof.jpg")
test_download("https://cgworld.jp/feature/images/interview/201707-cgw227GG-pokemon/B01a.jpg", "cgworld_B01a.jpg")
