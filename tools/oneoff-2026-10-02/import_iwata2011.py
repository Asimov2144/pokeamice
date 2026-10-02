"""Import a 2011-layout 社長が訊く (nintendo.co.jp/ds/interview/<code>/volN/indexK.html) through import-web's own
fetch / picture / translation / writing code. That layout is regular enough to read directly: per chapter an <h3> whose
image alt is the chapter title, then div.int-box blocks with div.int-name (the speaker) and div.int-text (the turn, lines
broken with <br> that are not paragraph breaks; <p> are paragraphs), div.notes-box (※N notes) inside the turn, and
pictures. import-web's generic reader splits every <br> line into its own turn there, so it is not used for this layout.

    python import_iwata2011.py <target key> [--dry-run]       (targets in design/import_web_targets_2026-10a.json)
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")
DOCS = Path("P:/WEBSITE/pokeamice-main (1)/app-data-export")
spec = importlib.util.spec_from_file_location("import_web", DOCS / "tools" / "import-web.py")
W = importlib.util.module_from_spec(spec)
spec.loader.exec_module(W)

key = sys.argv[1]
dry = "--dry-run" in sys.argv
targets = W.load_targets(DOCS / "design" / "import_web_targets_2026-10a.json")
target = targets[key]
slug = target.get("slug") or f"{target['date']}-interview-{key}"
asker = target.get("asker", "岩田")
names = {**target["speakers"], asker: "岩田聪"}

items, n_img = [], 0
for n, url in enumerate([target["url"]] + target.get("pages", [])):
    t = {**target, "key": key if n == 0 else f"{key}_p{n + 1}", "url": url, "wayback": None}
    soup = BeautifulSoup(W.fetch(t), "html.parser")
    wrap = soup.select_one("#int-box-wrap")
    for el in wrap.find_all(["h3", "div", "img"], recursive=True):
        if el.name == "h3":
            img = el.find("img")
            title = (img.get("alt") if img else el.get_text()).strip()
            items.append({"type": "heading", "level": 2, "original": title})
        elif el.name == "div" and "int-box" in (el.get("class") or []):
            who = el.select_one(".int-name").get_text(strip=True) if el.select_one(".int-name") else ""
            text = el.select_one(".int-text")
            if text is None:
                continue
            notes = []
            for nb in text.select(".notes-box"):
                num = nb.select_one(".notes-num").get_text(strip=True)
                for s in nb.find_all("script"):
                    s.decompose()
                notes.append(f"{num} " + nb.select_one(".notes-text").get_text("", strip=True))
                nb.decompose()
            for s in text.find_all(["script", "noscript"]):
                s.decompose()
            paras = []
            for p in text.find_all("p"):
                for br in p.find_all("br"):
                    br.replace_with("")
                s = re.sub(r"\s+", "", p.get_text())
                s = s.replace("（※", "（※")
                if s:
                    paras.append(s)
            speaker = names.get(who, who)
            role = "question" if who == asker else "answer"
            for s in paras:
                items.append({"original": s, "role": role, "speaker": speaker})
            for s in notes:
                items.append({"original": s, "role": "answer", "speaker": "编者注"})
        elif el.name == "img" and el.find_parent("h3") is None and el.find_parent(class_="int-name") is None:
            src = el.get("src") or ""
            if not re.search(r"img/photo|img/slide|img/img_\d", src) or src.endswith(".gif"):
                continue
            n_img += 1
            if dry:
                items.append({"type": "image", "image": src})
                continue
            local = W.fetch_image(src, url, None, W.IMG_DIR / slug, n_img)
            if local:
                items.append({"type": "image", "image": local, "alt": el.get("alt") or ""})

from collections import Counter  # noqa: E402

print(key, len(items), "items", Counter(x.get("speaker") or x.get("type") for x in items).most_common(), sum(len(x.get("original", "")) for x in items), "chars")
if dry:
    for x in items[:30]:
        print("  ", x.get("type") or x.get("role"), x.get("speaker", ""), (x.get("original") or x.get("image"))[:80])
    sys.exit()
glossary = W.load_glossary()
items = W.translate_items(items, target, glossary)
path = W.write_post(target, items, {}, slug)
print("wrote", path)
