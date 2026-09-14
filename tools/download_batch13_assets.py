import os
import urllib.request
import shutil

os.makedirs("assets/img/interviews/1999-11-22-interview-time-satoshi-tajiri-ultimate-game-freak", exist_ok=True)
os.makedirs("assets/img/interviews/2009-05-01-interview-nintendo-power-masuda-kawachimaru-platinum-gens", exist_ok=True)

# 1. Tajiri photo
src_tajiri = "assets/img/interviews/2000-07-01-interview-nom-special-dialogue-tajiri-ishihara/tajiri.jpg"
dst_tajiri = "assets/img/interviews/1999-11-22-interview-time-satoshi-tajiri-ultimate-game-freak/tajiri.jpg"
if os.path.exists(src_tajiri) and not os.path.exists(dst_tajiri):
    shutil.copyfile(src_tajiri, dst_tajiri)
    print("Copied tajiri.jpg")

# 2. Nintendo power images
np_images = [
    ("header.png", "http://lavacutcontent.com/wp-content/uploads/2020/11/Nintendo-Power-Issue-240-April-2009-page-00a.png"),
    ("interviewees.jpg", "http://lavacutcontent.com/wp-content/uploads/2020/11/Interviewees.jpg"),
    ("giratina_distortion.png", "http://lavacutcontent.com/wp-content/uploads/2020/11/Gira.png"),
    ("battle_frontier.png", "http://lavacutcontent.com/wp-content/uploads/2020/11/Frontier.png"),
    ("gts_site.png", "http://lavacutcontent.com/wp-content/uploads/2020/11/GTS-Site.png"),
    ("pichu.png", "http://lavacutcontent.com/wp-content/uploads/2020/11/Pichu.png"),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

for fname, url in np_images:
    dst = os.path.join("assets/img/interviews/2009-05-01-interview-nintendo-power-masuda-kawachimaru-platinum-gens", fname)
    if not os.path.exists(dst):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp, open(dst, "wb") as out:
                out.write(resp.read())
            print(f"Downloaded {fname} ({os.path.getsize(dst)} bytes)")
        except Exception as e:
            print(f"Failed {fname}: {e}")
    else:
        print(f"Already exists: {fname}")
