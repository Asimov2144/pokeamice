"""Two old recruit pages whose markup import-web's generic reader cannot tell speakers in (2026-10-02 re-import):

- GAME FREAK 2015 (gamefreak.co.jp/recruit/interview_02.html): h2 = section, h3 = the question, then <dl><dt><img alt=
  "研究開発部部長 S.T."></dt><dd>answer, lines broken with <br></dd>; the first <dl>s are the two profiles.
- 株式会社ポケモン 2014 (corporate/job/saiyo/interview/interview3.html): a profile <dl>, then section.person blocks with an
  h1 image whose alt is the section title, p.question and p.answer.

Fetching, pictures (through the Wayback snapshot), translation and writing are import-web's own.
    python import_recruit_old.py <target key> [--dry-run]
"""
import importlib.util
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
target = W.load_targets(DOCS / "design" / "import_web_targets_2026-10a.json")[key]
slug = target["slug"]
soup = BeautifulSoup(W.fetch(target), "html.parser")
for s in soup.find_all(["script", "style", "noscript"]):
    s.decompose()


def text(el):
    for br in el.find_all("br"):
        br.replace_with("")
    return re.sub(r"\s+", " ", el.get_text()).strip()


items, n_img = [], 0


def picture(img):
    global n_img
    src = img.get("src") or ""
    if not src or src.endswith(".gif") or "spacer" in src:
        return
    n_img += 1
    if dry:
        items.append({"type": "image", "image": src})
        return
    local = W.fetch_image(src, target["url"], target.get("wayback"), W.IMG_DIR / slug, n_img)
    if local:
        items.append({"type": "image", "image": local, "alt": img.get("alt") or target["title"]})


if key.startswith("gamefreak"):
    root = soup.select_one("div.content_inner")
    for el in root.find_all(["h2", "h3", "dl", "img"]):
        if el.name == "img":
            if el.find_parent("dt") is None and "photo" in (el.get("src") or ""):
                picture(el)
            continue
        if el.name == "h2":
            items.append({"type": "heading", "level": 2, "original": text(el)})
        elif el.name == "h3":
            items.append({"original": text(el), "role": "question", "speaker": "采访者"})
        else:
            for dt in el.find_all("dt"):
                dd = dt.find_next_sibling("dd")
                img = dt.find("img")
                who = (img.get("alt") if img else text(dt)) or ""
                init = re.search(r"[A-Z]\.[A-Z]\.", who)
                body = text(dd) if dd else ""
                if body:
                    items.append({"original": body, "role": "answer", "speaker": init.group(0) if init else who})
else:
    root = soup
    prof = soup.select_one("div.profile dl") or soup.find("dl")
    if prof:
        items.append({"original": text(prof)})
    for sec in soup.select("section.person"):
        for el in sec.find_all(["h1", "p", "img", "dl", "li"], recursive=True):
            if el.name == "img":
                if el.find_parent("h1") is None:
                    picture(el)
                continue
            if el.name == "h1":
                img = el.find("img")
                t = (img.get("alt") if img else text(el)) or ""
                if t:
                    items.append({"type": "heading", "level": 2, "original": t})
            elif el.name in ("p", "li", "dl"):
                if el.find_parent(["p", "li", "dl"]) is not None:
                    continue
                cls = el.get("class") or []
                t = text(el)
                if not t:
                    continue
                if "question" in cls:
                    items.append({"original": t, "role": "question", "speaker": "采访者"})
                elif "answer" in cls:
                    items.append({"original": t, "role": "answer", "speaker": "广部圭太"})
                else:
                    items.append({"original": t})

from collections import Counter  # noqa: E402

print(key, len(items), Counter(x.get("speaker") or x.get("type") or "-" for x in items).most_common(), sum(len(x.get("original", "")) for x in items), "chars")
if "--fill-pictures" in sys.argv:
    # the pictures Wayback refused (429) on the import: the same file from the old post's folder, else fetched again
    import yaml
    OLD = {"gamefreak-2015-recruit-rnd": "2015-gamefreak-rnd-launch", "tpc-2014-recruit-global-hirobe": "2014-05-01-tpc-global-hirobe"}[key]
    post = DOCS / "_posts" / f"{slug}.md"
    fm = yaml.safe_load(post.read_text(encoding="utf-8").split("\n---\n")[0][4:])
    have = [x for x in fm["parallel_items"] if x.get("type") != "image"]
    got = {x["image"].rsplit("/", 1)[-1].split(".")[0]: x for x in fm["parallel_items"] if x.get("type") == "image"}
    out, k, n = [], 0, 0
    for x in items:
        if x.get("type") != "image":
            out.append(have[k]); k += 1
            continue
        n += 1
        name = x["image"].rsplit("/", 1)[-1]
        if f"{n:03d}" in got:
            out.append(got[f"{n:03d}"]); continue
        old = DOCS / "assets" / "img" / "interviews" / OLD / name
        if old.exists():
            out.append({"type": "image", "image": f"/assets/img/interviews/{OLD}/{name}", "alt": target["title"]})
            print("   old file", name)
            continue
        local = W.fetch_image(x["image"], target["url"], target.get("wayback"), W.IMG_DIR / slug, n)
        if local:
            out.append({"type": "image", "image": local, "alt": target["title"]})
            print("   fetched", name)
        else:
            print("   still missing", name)
    assert k == len(have), (k, len(have))
    fm["parallel_items"] = out
    post.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n", encoding="utf-8", newline="\n")
    sys.exit()
if dry:
    for x in items:
        print("  ", x.get("type") or x.get("role") or "-", x.get("speaker", ""), (x.get("original") or x.get("image"))[:70])
    sys.exit()
items = W.translate_items(items, target, W.load_glossary())
cover = W.propose_cover(items, target)
path = W.write_post(target, items, cover, slug)
W.prune_pictures(slug, items)
print("wrote", path)
