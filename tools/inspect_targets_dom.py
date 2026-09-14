import urllib.request
import ssl
import sys
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"}

def inspect_funs():
    req = urllib.request.Request("https://funs-project.com/poplab/007/", headers=headers)
    with urllib.request.urlopen(req, context=ctx) as resp:
        soup = BeautifulSoup(resp.read().decode("utf-8", errors="ignore"), "html.parser")
    print("=== FUNS PROJECT INSPECTION ===")
    body = soup.find("body")
    # find all containers with dialogues
    for tag in body.find_all(["section", "article", "div", "main"]):
        cls = tag.get("class", [])
        id_ = tag.get("id", "")
        if any(k in str(cls) for k in ["interview", "talk", "dialogue", "content", "main", "detail", "body"]):
            print(f"Container: {tag.name} class={cls} id={id_}")
    
    qa = soup.find("div", class_="specialQA")
    if qa:
        for child in qa.children:
            if child.name:
                print(f"child: {child.name} class={child.get('class')} text={child.get_text(strip=True)[:60]}")
    # check images
    imgs = soup.find_all("img")
    for img in imgs:
        src = img.get("src", "")
        if "poplab" in src or "007" in src or "special" in src:
            print(f"Img: {src}")

def inspect_gi(url, name):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx) as resp:
        soup = BeautifulSoup(resp.read().decode("utf-8", errors="ignore"), "html.parser")
    print(f"\n=== {name} INSPECTION ===")
    article = soup.find("div", class_="field--name-body")
    if not article:
        print("article body not found!")
        return
    children = article.find_all(["p", "h2", "h3", "img", "figure", "blockquote"], recursive=False)
    print(f"Top-level children in article: {len(children)}")
    for c in children[:15]:
        txt = c.get_text(strip=True)
        img = c.find("img") or (c if c.name == "img" else None)
        img_src = img.get("src") if img else ""
        print(f"  {c.name} (img: {bool(img)}): {txt[:80] or img_src[:80]}")

if __name__ == "__main__":
    inspect_funs()
    inspect_gi("https://www.gameinformer.com/b/features/archive/2017/08/10/heres-how-game-freak-designs-pokemon-creatures.aspx", "GI DESIGN")
    inspect_gi("https://www.gameinformer.com/b/features/archive/2017/08/14/why-ruby-and-sapphire-were-the-most-challenging-pokemon-to-make.aspx", "GI RS")
