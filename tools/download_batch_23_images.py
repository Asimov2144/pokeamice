import urllib.request
import ssl
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"}

def download_gi():
    gi1_dir = Path("assets/img/interviews/2017-08-10-interview-gameinformer-how-game-freak-designs-pokemon-creatures")
    gi1_dir.mkdir(parents=True, exist_ok=True)
    gi1_map = {
        "design_01.jpg": "https://web.archive.org/web/20170812165751if_/http://www.gameinformer.com/s3/files/styles/body_default/s3/legacy-images/imagefeed/Here%27s%20How%20Game%20Freak%20Designs%20Pok%C3%A9mon%20Creatures/pokemondocs_5F00_610.jpg",
        "design_02.jpg": "https://web.archive.org/web/20170812165751if_/http://www.gameinformer.com/s3/files/styles/body_default/s3/legacy-images/imagefeed/Here%27s%20How%20Game%20Freak%20Designs%20Pok%C3%A9mon%20Creatures/toyshelf.jpg",
        "design_03.jpg": "https://web.archive.org/web/20170812165751if_/http://www.gameinformer.com/s3/files/styles/body_default/s3/legacy-images/imagefeed/Here%27s%20How%20Game%20Freak%20Designs%20Pok%C3%A9mon%20Creatures/threeheads_5F00_610.jpg",
        "design_04.jpg": "https://web.archive.org/web/20170812165751if_/http://www.gameinformer.com/s3/files/styles/body_default/s3/legacy-images/imagefeed/Here%27s%20How%20Game%20Freak%20Designs%20Pok%C3%A9mon%20Creatures/mewtwovpopplio.jpg"
    }
    for name, url in gi1_map.items():
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            data = resp.read()
            (gi1_dir / name).write_bytes(data)
        print(f"Saved {name}: {len(data)} bytes")

    gi2_dir = Path("assets/img/interviews/2017-08-14-interview-gameinformer-why-ruby-and-sapphire-were-most-challenging")
    gi2_dir.mkdir(parents=True, exist_ok=True)
    gi2_url = "https://web.archive.org/web/20170815124933if_/http://www.gameinformer.com/s3/files/styles/body_default/s3/legacy-images/imagefeed/Why%20Ruby%20And%20Sapphire%20Were%20The%20Most%20Challenging%20Pok%C3%A9mon%20To%20Make/pokemonsaphruby_5F00_610.jpg"
    req = urllib.request.Request(gi2_url, headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
        data = resp.read()
        (gi2_dir / "rs_dev_01.jpg").write_bytes(data)
    print(f"Saved rs_dev_01.jpg: {len(data)} bytes")

def download_funs():
    funs_dir = Path("assets/img/interviews/2018-06-25-interview-funsproject-atsuko-nishida-shoko-nakagawa-character-design")
    funs_dir.mkdir(parents=True, exist_ok=True)
    urls = [
        "https://funs-project.com/poplab/007/",
        "https://funs-project.com/poplab/007/index_2.html"
    ]
    seen = set()
    counter = 1
    for u in urls:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            soup = BeautifulSoup(resp.read().decode("utf-8", errors="ignore"), "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if any(k in src for k in ["007", "spe_", "special"]) and not any(k in src for k in ["btn", "arrow", "icon", "logo", "tw", "fb"]):
                abs_src = urljoin(u, src)
                if abs_src not in seen:
                    seen.add(abs_src)
                    name = f"funs_007_{counter:02d}.jpg"
                    try:
                        req_img = urllib.request.Request(abs_src, headers=headers)
                        with urllib.request.urlopen(req_img, context=ctx, timeout=20) as resp_img:
                            data = resp_img.read()
                        if len(data) > 1000:
                            (funs_dir / name).write_bytes(data)
                            print(f"Saved Funs image {name}: {len(data)} bytes from {abs_src}")
                            counter += 1
                    except Exception as e:
                        print(f"Error downloading {abs_src}: {e}")

if __name__ == "__main__":
    download_gi()
    download_funs()
    print("All Batch 23 images saved.")
