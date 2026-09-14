import urllib.request, urllib.parse, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')

urls = [
    "http://127.0.0.1:4000/" + urllib.parse.quote("访谈翻译/翻译/访谈整理") + "/interview-iwata-asks-xy-chapter-1-global-simultaneous-release/",
    "http://127.0.0.1:4000/" + urllib.parse.quote("访谈翻译/翻译/访谈整理") + "/interview-iwata-asks-xy-chapter-2-reborn-pokemon-3d-amie/",
    "http://127.0.0.1:4000/" + urllib.parse.quote("访谈翻译/翻译/访谈整理") + "/interview-iwata-asks-xy-chapter-3-new-battles-fairy-type/",
    "http://127.0.0.1:4000/" + urllib.parse.quote("访谈翻译/翻译/访谈整理") + "/interview-iwata-asks-xy-chapter-4-closer-bonds-mega-evolution/"
]

headers = {'User-Agent': 'Mozilla/5.0'}

print("=== VERIFYING BATCH 10 HTTP STATUS & ERA SKINS ===")
for u in urls:
    req = urllib.request.Request(u, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('utf-8', errors='replace')
        status = resp.status
        era_skin = re.search(r'data-era-skin=["\']([^"\']+)["\']', content)
        era_body = re.search(r'data-era=["\']([^"\']+)["\']', content)
        turns = len(re.findall(r'class=["\']dialogue-item', content))
        imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        
        print(f"URL: {u}")
        print(f"  Status: {status} | Length: {len(content)} bytes")
        print(f"  Era Skin: {era_skin.group(1) if era_skin else 'NONE'} | Body Era: {era_body.group(1) if era_body else 'NONE'}")
        print(f"  Rendered Dialogue Turns: {turns} | Images Count: {len(imgs)}")
        
with open("data/pokemon_1000_interviews.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

imported = [d for d in catalog if d.get("status") == "imported"]
print(f"\nTotal imported interviews in catalog: {len(imported)}")
xy_imported = [d for d in imported if "XY" in d.get("id", "") or "0653" <= d.get("id", "") <= "0655-4" or "ekjj" in d.get("url", "")]
print(f"Batch 10 XY imported count: {len(xy_imported)}")
for d in xy_imported:
    print(f"  [{d['id']}] {d.get('title')} ({d.get('date')}) -> {d.get('post_file')}")
