import urllib.request
import json

headers = {'User-Agent': 'Mozilla/5.0'}

# Test Wayback CDX API for Nintendo NOM
urls_to_check = [
    "http://www.nintendo.co.jp/nom/0007/",
    "https://www.nintendo.co.jp/nom/0007/",
    "http://www.nintendo.co.jp/nom/0211/",
]

for target in urls_to_check:
    api = f"https://web.archive.org/cdx/search/cdx?url={target}*&output=json&limit=15"
    try:
        req = urllib.request.Request(api, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"\nTarget: {target}")
            print(f"Wayback matches: {len(data)-1}")
            for row in data[1:6]:
                # timestamp, original, status
                print(f"  {row[1]} -> https://web.archive.org/web/{row[1]}/{row[2]} ({row[4]})")
    except Exception as e:
        print(f"Error checking {target}: {e}")
