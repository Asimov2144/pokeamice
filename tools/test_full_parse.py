from bs4 import BeautifulSoup
from pathlib import Path
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

CACHE_DIR = Path("tools/cache_batch_17")

def test_full_parse(cid):
    html = (CACHE_DIR / f"{cid}_raw.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    # Catchphrase
    h2 = soup.find("h2")
    main_title = h2.get_text().strip().split("\n")[0] if h2 else ""
    
    # Members
    members = []
    member_map = {}
    for unit in soup.find_all(class_="member__list__unit"):
        name_el = unit.find(class_="member__list__name")
        info_el = unit.find(class_="member__list__info")
        prof_el = unit.find(class_="member__list__profile")
        img_el = unit.find("img")
        name = name_el.get_text().strip() if name_el else ""
        info = info_el.get_text().strip() if info_el else ""
        prof = prof_el.get_text().strip() if prof_el else ""
        img_src = img_el.get("src") if img_el else ""
        m_data = {"name": name, "info": info, "profile": prof, "img": img_src}
        members.append(m_data)
        # map image filename to name/role
        if img_src:
            m_code = Path(img_src.split("?")[0]).stem.replace("member-", "")
            member_map[m_code] = name
            
    print(f"\n=================== {cid} ===================")
    print("Catchphrase:", main_title)
    print("Members:", [(m['name'], m['info']) for m in members])
    
    units = soup.find_all(class_="contents__unit")
    print(f"Contents units found: {len(units)}")
    
    items = []
    for u_idx, unit in enumerate(units):
        h3 = unit.find("h3")
        if h3:
            items.append({"type": "heading", "text": h3.get_text().strip()})
            
        # Check photos
        for p_img in unit.find_all(class_="contents__unit__block__photo"):
            img = p_img.find("img")
            if img:
                items.append({"type": "image", "src": img.get("src")})
                
        # Check dialogues
        for p in unit.find_all("p"):
            talker = p.find(class_="talker")
            speak = p.find(class_="speak")
            if talker and speak:
                name_el = talker.find(class_="talker__name")
                job_el = talker.find(class_="talker__job")
                thumb_img = talker.find("img")
                name = name_el.get_text().strip() if name_el else ""
                job = job_el.get_text().strip() if job_el else ""
                
                if not name and thumb_img:
                    t_src = thumb_img.get("src", "")
                    m_code = Path(t_src.split("?")[0]).stem.replace("member-", "")
                    name = member_map.get(m_code, m_code.upper())
                
                spk = f"{name}（{job}）" if job else name
                items.append({"type": "dialogue", "speaker": spk, "text": speak.get_text().strip()})

    print(f"Total extracted items: {len(items)}")
    for it in items[:6]:
        print(" ", it["type"], it.get("speaker") or "", it.get("text", "")[:50])

for cid in ["PKMN-1005", "PKMN-1007", "PKMN-1008"]:
    test_full_parse(cid)
