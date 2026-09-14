import urllib.request
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

BASE_URL = "https://www.gamefreak.co.jp"

INTERVIEWS = {
    "2021-gamefreak-crosstalk-system-programmer": [
        "mv.jpg", "member-km.jpg", "member-ht.jpg", "img-01-01.jpg", "img-02-01.jpg", "img-03-01.jpg"
    ],
    "2021-gamefreak-crosstalk-scenario": [
        "mv.jpg", "member-ki.jpg", "member-km.jpg", "img-01-01.jpg", "img-02-01.jpg", "img-03-01.jpg"
    ],
    "2021-gamefreak-crosstalk-new-graduate": [
        "mv.jpg", "member-if.jpg", "member-tm.jpg", "member-at.jpg", "member-rn.jpg", "member-rs.jpg", "member-kk.jpg",
        "img-01-01.jpg", "img-02-01.jpg", "img-03-01.jpg"
    ]
}

ROOT_IMG = Path("assets/img/interviews")

for slug, files in INTERVIEWS.items():
    dest_dir = ROOT_IMG / slug
    dest_dir.mkdir(parents=True, exist_ok=True)
    crosstalk_sub = slug.replace("2021-gamefreak-crosstalk-", "")
    print(f"\n--- Downloading for {slug} ---")
    for f in files:
        target = dest_dir / f
        if target.exists() and target.stat().st_size > 500:
            print(f"  Already exists: {f} ({target.stat().st_size} bytes)")
            continue
        url = f"{BASE_URL}/assets/recruit/img/crosstalk/{crosstalk_sub}/{f}"
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                target.write_bytes(data)
                print(f"  Downloaded: {f} ({len(data)} bytes)")
        except Exception as e:
            print(f"  Error downloading {url}: {e}")
