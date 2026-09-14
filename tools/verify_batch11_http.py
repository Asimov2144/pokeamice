import urllib.request, urllib.parse, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')

urls = [
    ("PKMN-0043", "http://127.0.0.1:4000/" + urllib.parse.quote("访谈翻译/翻译/访谈整理") + "/interview-gameinformer-masuda-morimoto-hgss/", "2007"),
    ("PKMN-0086", "http://127.0.0.1:4000/" + urllib.parse.quote("访谈翻译/翻译/访谈整理") + "/interview-famitsu-b2w2-fanmeeting-masuda-unno/", "2011"),
    ("PKMN-0072", "http://127.0.0.1:4000/" + urllib.parse.quote("访谈翻译/翻译/访谈整理") + "/interview-famitsu-xy-music-fanmeeting-masuda-kageyama/", "2014")
]

headers = {'User-Agent': 'Mozilla/5.0'}

print("=== VERIFYING BATCH 11 HTTP STATUS & ERA SKINS ===")
for pid, u, expected_skin in urls:
    req = urllib.request.Request(u, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('utf-8', errors='replace')
        status = resp.status
        era_skin = re.search(r'data-era-skin=["\']([^"\']+)["\']', content)
        era_body = re.search(r'data-era=["\']([^"\']+)["\']', content)
        imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        speakers = re.findall(r'parallel-speaker__name', content)
        
        actual_skin = era_skin.group(1) if era_skin else 'NONE'
        skin_ok = (actual_skin == expected_skin)
        print(f"[{pid}] {u}")
        print(f"  Status: {status} | Length: {len(content)} bytes")
        print(f"  Era Skin: {actual_skin} (Expected: {expected_skin}, Matches: {skin_ok})")
        print(f"  Speakers rendered: {len(speakers)} | Images count: {len(imgs)}")

with open("data/pokemon_1000_interviews.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

imported = [d for d in catalog if d.get("status") == "imported"]
print(f"\nTotal imported interviews in catalog: {len(imported)}")
batch11_ids = ['PKMN-0043', 'PKMN-0086', 'PKMN-0072']
for d in imported:
    if d.get('id') in batch11_ids:
        print(f"  [{d['id']}] {d.get('title')} ({d.get('date')}) -> {d.get('post_file')}")
