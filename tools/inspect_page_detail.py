import sys
import ssl
import urllib.request
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for short_id in ["kn", "mi", "ek", "ht"]:
    url = f"https://www.gamefreak.co.jp/recruit/interview-gr-{short_id}/"
    soup = BeautifulSoup(urllib.request.urlopen(url, context=ctx).read(), "html.parser")
    print(f"=== {short_id.upper()} ===")
    lead = soup.find(class_=lambda c: c and "lead" in c)
    if lead:
        print("Lead tag:", lead.name, lead.get("class"))
        spans = lead.find_all("span")
        if spans:
            for s in spans:
                print("  span:", s.get_text(strip=True))
        else:
            print("  text:", lead.get_text(strip=True))
    
    # Profile / Info
    profile = soup.find(class_=lambda c: c and "profile" in c)
    if profile:
        print("Profile text:", profile.get_text(" ", strip=True))
    
    # Check sections 1, 2, 3
    units = soup.find_all("section", class_=lambda c: c and "contents__unit" in c)
    print(f"Units count: {len(units)}")
    for idx, u in enumerate(units):
        h = u.find(["h2", "h3"])
        htxt = h.get_text(strip=True) if h else ""
        ps = [p.get_text(strip=True) for p in u.find_all("p") if p.get_text(strip=True)]
        imgs = [img.get("src") for img in u.find_all("img") if f"/{short_id}/" in img.get("src", "")]
        print(f"  Unit {idx+1}:")
        print(f"    Heading: {htxt}")
        print(f"    Images: {imgs}")
        for p_i, p_txt in enumerate(ps):
            print(f"    P{p_i+1}: {p_txt[:50]}...")
    print()
