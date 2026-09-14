import urllib.request
import urllib.parse

base_url = "http://127.0.0.1:4000"

test_paths = [
    "/访谈翻译/翻译/访谈整理/interview-famitsu-usum-ohmori-iwao-director/",
    "/访谈翻译/翻译/访谈整理/interview-famitsu-usum-iwao-suginaka-story-secrets/",
    "/访谈翻译/翻译/访谈整理/interview-cgworld-sun-moon-3d-pipeline-creatures-gamefreak/"
]

for p in test_paths:
    full_url = base_url + urllib.parse.quote(p)
    try:
        req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            print(f"\n[HTTP 200 OK] {p}")
            print(f"  Content length: {len(content)} chars")
            
            # Check era skin
            has_era = 'data-era="2019"' in content or 'data-era-skin="2019"' in content
            print(f"  Era Skin 2019 present: {has_era}")
            
            # Check parallel layout
            has_parallel = 'data-parallel-translation' in content
            print(f"  Parallel translation layout: {has_parallel}")
            
            # Check title
            idx_t = content.find("<title>")
            if idx_t != -1:
                t_end = content.find("</title>", idx_t)
                print(f"  Page title: {content[idx_t+7:t_end].strip()}")
                
            # Check speakers
            speakers = set()
            for spk in ["提问", "大森 滋", "岩尾 和昌", "杉中 克考", "海野 隆雄", "氏家 淳子"]:
                if spk in content:
                    speakers.add(spk)
            print(f"  Speakers found: {speakers}")
            
            # Check images
            has_img = "/assets/img/interviews/" in content
            print(f"  Images referenced: {has_img}")
            
    except Exception as e:
        print(f"\n[HTTP ERROR] {p}: {e}")
