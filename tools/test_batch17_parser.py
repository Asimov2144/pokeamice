from bs4 import BeautifulSoup
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")

CACHE_DIR = Path("tools/cache_batch_17")

def test_parse(cid):
    html = (CACHE_DIR / f"{cid}_raw.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    # Catch main heading
    h2 = soup.find("h2")
    main_title = h2.get_text().strip().split("\n")[0] if h2 else ""
    print(f"\n=================== {cid} ===================")
    print("Main catchphrase:", main_title)
    
    # Members
    members = []
    for unit in soup.find_all(class_="member__list__unit"):
        name_el = unit.find(class_="member__list__name")
        info_el = unit.find(class_="member__list__info")
        prof_el = unit.find(class_="member__list__profile")
        img_el = unit.find("img")
        name = name_el.get_text().strip() if name_el else ""
        info = info_el.get_text().strip() if info_el else ""
        prof = prof_el.get_text().strip() if prof_el else ""
        img_src = img_el.get("src") if img_el else ""
        members.append({"name": name, "info": info, "profile": prof, "img": img_src})
    print(f"Members found: {len(members)}")
    for m in members:
        print(f"  {m['name']} ({m['info']}): {m['profile'][:40]}... [img: {m['img']}]")
        
    # Dialogue sections
    dialogues = []
    # Find all units/blocks
    for block in soup.find_all(class_="contents__unit__block"):
        h3 = block.find(class_="contents__unit__block__ttl")
        if h3:
            dialogues.append({"type": "heading", "text": h3.get_text().strip()})
        
        # Look for photos
        photo_fig = block.find(class_="contents__unit__block__photo")
        if photo_fig and photo_fig.find("img"):
            dialogues.append({"type": "image", "src": photo_fig.find("img").get("src")})
            
        # Look for dialogues
        for p in block.find_all("p"):
            talker = p.find(class_="talker")
            speak = p.find(class_="speak")
            if talker and speak:
                name_el = talker.find(class_="talker__name")
                name = name_el.get_text().strip() if name_el else ""
                dialogues.append({"type": "dialogue", "speaker": name, "text": speak.get_text().strip()})
            elif not talker and p.get_text().strip():
                # check if regular paragraph
                t = p.get_text().strip()
                if len(t) > 10 and not any(k in t for k in ["Recruit", "Corporate", "GAME FREAK", "PAGE TOP"]):
                    dialogues.append({"type": "paragraph", "text": t})
                    
    print(f"Content items found: {len(dialogues)}")
    headings = [d['text'] for d in dialogues if d['type'] == 'heading']
    spks = set(d['speaker'] for d in dialogues if d['type'] == 'dialogue')
    print("Headings:", headings)
    print("Speakers in dialogue:", spks)

for cid in ["PKMN-1005", "PKMN-1007", "PKMN-1008"]:
    test_parse(cid)
