import sys
import ssl
import urllib.request
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

candidates = [
    ("interview-gr-kn", "K.N.", "kn"),
    ("interview-gr-mi", "M.I.", "mi"),
    ("interview-gr-ek", "E.K.", "ek"),
    ("interview-gr-ht", "H.T.", "ht")
]

for slug, name, short_id in candidates:
    url = f"https://www.gamefreak.co.jp/recruit/{slug}/"
    soup = BeautifulSoup(urllib.request.urlopen(url, context=ctx).read(), "html.parser")
    main = soup.find("main")
    print(f"=== {slug} ({name}) ===")
    
    # Catchphrase / Main Title
    lead_h2 = soup.find("h2", class_=lambda c: c and "lead" in c) or soup.find("div", class_=lambda c: c and "lead" in c)
    print("Lead element:", lead_h2.get_text(strip=True) if lead_h2 else "None")
    
    # Check all sections
    sections = main.find_all("section")
    print(f"Sections count: {len(sections)}")
    for i, s in enumerate(sections):
        classes = s.get("class", [])
        h = s.find(["h2", "h3"])
        htxt = h.get_text(strip=True) if h else ""
        ps = [p.get_text(strip=True) for p in s.find_all("p") if len(p.get_text(strip=True)) > 20]
        imgs = [img.get("src") for img in s.find_all("img") if f"/{short_id}/" in img.get("src", "")]
        print(f"  Sec {i} ({classes}): h='{htxt[:40]}' | ps={len(ps)} | imgs={imgs}")
    print()
