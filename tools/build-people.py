"""The people library: one registry, portraits gathered from what the site already has, a page per person.

    python tools/build-people.py registry      # _data/people.yml: every name in entities.people, slugs, kinds, aliases
    python tools/build-people.py portraits     # crop a portrait for anyone without one, from captioned photos in the posts (check the result: the Iwata Asks captions are shifted)
    python tools/build-people.py commons       # the few on Wikimedia Commons, with attribution
    python tools/build-people.py pages         # _pages/people/<slug>.md for each entry, and the directory page
    python tools/build-people.py all

The registry (_data/people.yml) is the source of truth for slug, aliases, kind and
avatar; this script adds names it does not know and never overwrites what is
there. Portraits come, in order, from the scanned pages (cut by hand, see
avatar_source), from photographs inside the web interviews whose caption names
the person (face detection, the largest face), and only then from elsewhere -
Wikimedia Commons for the few public figures it has, each recorded with its
source. A person page lists and counts what the site holds on that person; the
layout (_layouts/person.html) computes the counts from the posts at build time,
so nothing here goes stale when a post is added.
"""
import argparse
import collections
import glob
import io
import re
import sys
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "_data" / "people.yml"
PAGES = ROOT / "_pages" / "people"
AVATARS = ROOT / "assets" / "img" / "people"

# romaji slugs for the names that get a real URL; anyone else gets pinyin
SLUGS = {
    "增田顺一": "masuda-junichi", "石原恒和": "ishihara-tsunekazu", "首藤刚志": "shudo-takeshi", "汤山邦彦": "yuyama-kunihiko",
    "杉森建": "sugimori-ken", "岩田聪": "iwata-satoru", "大森滋": "ohmori-shigeru", "田尻智": "tajiri-satoshi", "海野隆雄": "unno-takao",
    "森本茂树": "morimoto-shigeki", "久保雅一": "kubo-masakazu", "大村祐介": "ohmura-yusuke", "一之濑刚": "ichinose-go",
    "佐藤仁美": "sato-hitomi", "岩尾和昌": "iwao-kazumasa", "西野弘二": "nishino-koji", "吉田宏信": "yoshida-hironobu",
    "大谷育江": "otani-ikue", "市村正亲": "ichimura-masachika", "小笠原裕": "ogasawara-yutaka", "竹内敦": "takeuchi-atsushi",
    "折本哲也": "orimoto-tetsuya", "小泽达雄": "ozawa-tatsuo", "松村直树": "matsumura-naoki", "长畑成一郎": "nagahata-seiichiro",
    "富江慎一郎": "tomie-shinichiro", "前泽圭一": "maezawa-keiichi", "井部真那": "ibe-mana", "景山将太": "kageyama-shota",
    "野村达雄": "nomura-tatsuo", "约翰·汉克": "john-hanke", "小野寺瞬": "onodera-shun", "深谷卓": "fukaya-taku", "米谷由贵": "yonetani-yuki",
    "宗像快": "munakata-kai", "小幡敏宏": "obata-toshihiro", "渡边哲也": "watanabe-tetsuya", "太田健程": "ota-takenori",
    "西田敦子": "nishida-atsuko", "三浦昌幸": "miura-masayuki", "林原惠美": "hayashibara-megumi", "三木真一郎": "miki-shinichiro",
    "犬山犬子": "inuyama-inuko", "James Turner": "james-turner", "田谷正夫": "taya-masao", "太田哲司": "ota-tetsuji", "水口舞": "mizuguchi-mai",
    "足立美奈子": "adachi-minako", "中津井优": "nakatsui-yu", "宇都宫崇人": "utsunomiya-takato", "川岛优志": "kawashima-masashi",
    "菜花健作": "nabana-kensaku", "藤原": "fujiwara", "河内丸武史": "kawachimaru-takeshi", "田中宏和": "tanaka-hirokazu",
    "江上周作": "egami-shusaku", "中川翔子": "nakagawa-shoko", "苍井优": "aoi-yu", "桐谷美玲": "kiritani-mirei",
}
# JA / EN spellings, so a search for either finds the person
ALIASES = {
    "增田顺一": ["増田順一", "Junichi Masuda"], "石原恒和": ["石原恒和", "Tsunekazu Ishihara"], "首藤刚志": ["首藤剛志", "Takeshi Shudo"],
    "汤山邦彦": ["湯山邦彦", "Kunihiko Yuyama"], "杉森建": ["杉森建", "Ken Sugimori"], "岩田聪": ["岩田聡", "Satoru Iwata"],
    "大森滋": ["大森滋", "Shigeru Ohmori"], "田尻智": ["田尻智", "Satoshi Tajiri"], "海野隆雄": ["海野隆雄", "Takao Unno"],
    "森本茂树": ["森本茂樹", "Shigeki Morimoto"], "久保雅一": ["久保雅一", "Masakazu Kubo"], "大村祐介": ["大村祐介", "Yusuke Ohmura"],
    "一之濑刚": ["一之瀬剛", "Go Ichinose"], "佐藤仁美": ["佐藤仁美", "Hitomi Sato"], "岩尾和昌": ["岩尾和昌", "Kazumasa Iwao"],
    "西野弘二": ["西野弘二", "Koji Nishino"], "景山将太": ["景山将太", "Shota Kageyama"], "野村达雄": ["野村達雄", "Tatsuo Nomura"],
    "约翰·汉克": ["John Hanke"], "太田健程": ["太田健程", "Takenori Oota"], "渡边哲也": ["渡辺哲也", "Tetsuya Watanabe"],
    "西田敦子": ["西田敦子", "Atsuko Nishida"], "太田哲司": ["太田哲司"], "水口舞": ["水口舞"], "足立美奈子": ["足立美奈子", "Minako Adachi"],
    "中津井优": ["中津井優"], "前泽圭一": ["前澤圭一", "Keiichi Maezawa"], "宇都宫崇人": ["宇都宮崇人", "Takato Utsunomiya"],
    "大谷育江": ["大谷育江", "Ikue Otani"], "James Turner": ["James Turner"], "宗像快": ["宗像快"], "小幡敏宏": ["小幡敏宏"],
}
# not people: the anime's cast, who the memoir chapters tag as if they were
CHARACTERS = {"超梦", "小智", "小次郎", "武藏", "梦幻", "小刚", "喵喵", "皮卡丘", "小霞", "大木博士", "N", "火箭队", "萨卡基", "乔伊", "小爱", "小建", "盖奇斯", "AZ", "布拉塔诺博士", "弗拉达利", "莎娜", "坂木", "古兹马", "花子", "正辉"}
# real people who are only quoted or cited in the memoir - no page, not in the directory
FIGURES = {"芥川龙之介", "司马辽太郎", "盐野七生", "萨蒂亚吉特·雷伊", "玛丽·雪莱", "阿尔伯特·爱因斯坦", "爱因斯坦", "弗朗西斯·福特·科波拉", "黑泽明", "笛卡尔", "赤冢不二夫", "吉拉尔丹", "宫崎骏", "押井守", "手冢治虫", "牛顿", "居里夫人", "宇野重吉", "斋藤武市", "桥本忍", "川村元気"}


def posts():
    out = []
    for p in sorted(glob.glob(str(ROOT / "_posts" / "*.md"))):
        t = io.open(p, encoding="utf-8").read()
        m = re.match(r"^---\r?\n(.*?)\r?\n---", t, re.S)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        if fm.get("layout") not in ("interview-editorial", "parallel-translation"):
            continue
        fm["_path"] = p
        out.append(fm)
    return out


def load_registry():
    if REGISTRY.exists():
        return yaml.safe_load(io.open(REGISTRY, encoding="utf-8")) or []
    return []


def save_registry(entries):
    header = "\n".join([
        "# 人物库：站内 entities.people 的每个名字一条。slug 定 URL（/people/<slug>/），avatar 是主头像，",
        "# portraits 是不同时期的照片（image / year / source），avatar_source 记主头像出处；aliases 供检索；",
        "# kind=character 是动画角色、kind=figure 是只被引述的人物，都不建人物页。由 tools/build-people.py 维护：只添加不覆盖。",
        "",
    ])
    io.open(REGISTRY, "w", encoding="utf-8", newline="\n").write(header + yaml.safe_dump(entries, allow_unicode=True, sort_keys=False, width=1000))


def needs_quote(v):
    return bool(re.search(r"[:#\[\]{}&*!|>'\"%@`,]|^\s|\s$", str(v)))


def json_str(v):
    import json
    return json.dumps(str(v), ensure_ascii=False)


def slug_for(name):
    if name in SLUGS:
        return SLUGS[name]
    if re.match(r"^[A-Za-z .'-]+$", name):
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if re.match(r"^[A-Z]\.[A-Z]\.$", name):          # GF's initials-only staff
        return "gf-" + name.replace(".", "").lower()
    from pypinyin import lazy_pinyin
    return "-".join(lazy_pinyin(re.sub(r"[·・]", "", name)))


def cmd_registry():
    entries = load_registry()
    known = {e["name"]: e for e in entries}
    counts = collections.Counter()
    for fm in posts():
        for n in (fm.get("entities") or {}).get("people") or []:
            counts[n] += 1
    added = 0
    for name, _ in counts.most_common():
        if name in known:
            e = known[name]
            e.setdefault("slug", slug_for(name))
            if name in ALIASES and not e.get("aliases"):
                e["aliases"] = ALIASES[name]
            continue
        e = {"name": name, "slug": slug_for(name)}
        if name in CHARACTERS:
            e["kind"] = "character"
        elif name in FIGURES:
            e["kind"] = "figure"
        if name in ALIASES:
            e["aliases"] = ALIASES[name]
        entries.append(e)
        known[name] = e
        added += 1
    # the same slug for two names would be two pages at one URL
    seen = {}
    for e in entries:
        s = e["slug"]
        if s in seen and seen[s] != e["name"]:
            e["slug"] = s + "-" + str(sum(1 for x in entries if x["slug"].startswith(s)))
        seen[e["slug"]] = e["name"]
    save_registry(entries)
    print(f"registry: {len(entries)} names ({added} added), {sum(1 for e in entries if e.get('avatar'))} with a portrait")


# ---------------------------------------------------------------- portraits
def cmd_portraits():
    import cv2
    import numpy as np
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    entries = load_registry()
    known = {e["name"]: e for e in entries}
    # every picture inside a post whose caption opens with a person's name
    cands = collections.defaultdict(list)
    for fm in posts():
        people = (fm.get("entities") or {}).get("people") or []
        for it in fm.get("parallel_items") or []:
            if not (isinstance(it, dict) and it.get("type") == "image" and it.get("image")):
                continue
            cap = (it.get("caption") or it.get("alt") or "").strip()
            for n in people:
                if n in CHARACTERS or known.get(n, {}).get("avatar"):
                    continue
                spaced = n[:2] + " " + n[2:] if len(n) >= 3 and re.match(r"^[一-鿿]+$", n) else n
                head = cap[:14]
                if n in head or spaced in head or (n.replace("·", " ") in head):
                    cands[n].append((it["image"], cap, Path(fm["_path"]).name))
    done = 0
    for name, items in cands.items():
        best = None
        for img_path, cap, post in items:
            f = ROOT / img_path.lstrip("/")
            if not f.exists():
                continue
            img = cv2.imdecode(np.frombuffer(f.read_bytes(), np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                continue
            g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = casc.detectMultiScale(g, 1.08, 6, minSize=(48, 48))
            if len(faces) == 0:
                continue
            # a portrait caption names one person; take the largest face, prefer pictures with a single one
            x, y, w, h = max((tuple(int(v) for v in b) for b in faces), key=lambda b: b[2] * b[3])
            score = w * h * (1.5 if len(faces) == 1 else 1.0)
            if best is None or score > best[0]:
                best = (score, img, (x, y, w, h), img_path, cap, post)
        if not best:
            continue
        _, img, (x, y, w, h), img_path, cap, post = best
        H, W = img.shape[:2]
        side = int(max(w, h) * 1.7)
        cx, cy = x + w // 2, y + h // 2
        x0 = max(0, cx - side // 2); y0 = max(0, cy - side // 2)
        x1 = min(W, x0 + side); y1 = min(H, y0 + side); x0 = max(0, x1 - side); y0 = max(0, y1 - side)
        crop = cv2.resize(img[y0:y1, x0:x1], (240, 240), interpolation=cv2.INTER_AREA)
        e = known[name]
        e.setdefault("slug", slug_for(name))
        # a candidate, not a portrait: the captions in some imported posts (社長が訊く) are shifted
        # against the photographs, so each crop is looked at before it goes into the registry
        cand_dir = ROOT / "scratch" / "people-candidates"
        cand_dir.mkdir(parents=True, exist_ok=True)
        ok, buf = cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 86])
        (cand_dir / (e["slug"] + ".jpg")).write_bytes(buf.tobytes())
        (cand_dir / (e["slug"] + ".txt")).write_text(chr(10).join([name, f"{post} · {cap}", img_path]) + chr(10), encoding="utf-8")
        done += 1
        print(f"  {name:8s} <- {img_path.split('/')[-2][:40]}/{img_path.split('/')[-1]}  ({cap[:30]})")
    print(f"portraits: {done} candidates in scratch/people-candidates - check each against its caption, then copy the good ones to assets/img/people and fill avatar / avatar_source in the registry")


# ---------------------------------------------------------------- commons
# The few people the site has no photograph of and Wikimedia Commons does, under a
# licence that allows reuse with attribution; the attribution goes into avatar_source.
COMMONS = {
    "约翰·汉克": "File:John Hanke by Gage Skidmore.jpg",
    "首藤刚志": "File:Takeshinoshasin.JPG",
}


def cmd_commons():
    import json
    import urllib.parse
    import urllib.request
    import cv2
    import numpy as np
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    entries = load_registry()
    known = {e["name"]: e for e in entries}
    hdr = {"User-Agent": "pokeamice-docs/1.0 (docs.pokeamice.com)"}
    for name, title in COMMONS.items():
        e = known.get(name)
        if not e or e.get("avatar"):
            continue
        u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({"format": "json", "action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": "800"})
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=hdr), timeout=60))
        ii = next(iter(d["query"]["pages"].values()))["imageinfo"][0]
        em = ii.get("extmetadata", {})
        licence = em.get("LicenseShortName", {}).get("value", "")
        artist = re.sub(r"<[^>]+>", "", em.get("Artist", {}).get("value", "")).strip()
        raw = urllib.request.urlopen(urllib.request.Request(ii.get("thumburl") or ii["url"], headers=hdr), timeout=120).read()
        img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = casc.detectMultiScale(g, 1.08, 6, minSize=(48, 48))
        H, W = img.shape[:2]
        if len(faces):
            x, y, w, h = max((tuple(int(v) for v in b) for b in faces), key=lambda b: b[2] * b[3])
            side = int(max(w, h) * 1.7); cx, cy = x + w // 2, y + h // 2
        else:
            side = min(W, H); cx, cy = W // 2, H // 2
        x0 = max(0, cx - side // 2); y0 = max(0, cy - side // 2)
        x1 = min(W, x0 + side); y1 = min(H, y0 + side); x0 = max(0, x1 - side); y0 = max(0, y1 - side)
        crop = cv2.resize(img[y0:y1, x0:x1], (240, 240), interpolation=cv2.INTER_AREA)
        e.setdefault("slug", slug_for(name))
        AVATARS.mkdir(parents=True, exist_ok=True)
        ok, buf = cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 86])
        (AVATARS / (e["slug"] + ".jpg")).write_bytes(buf.tobytes())
        e["avatar"] = f"/assets/img/people/{e['slug']}.jpg"
        e["avatar_source"] = f"Wikimedia Commons {title} · {artist} · {licence}"
        print(f"  {name}: {title} ({licence}, {artist})")
    save_registry(entries)


# ---------------------------------------------------------------- pages
def cmd_pages():
    entries = load_registry()
    PAGES.mkdir(parents=True, exist_ok=True)
    for old in PAGES.glob("*.md"):
        old.unlink()
    n = 0
    for e in entries:
        if e.get("kind") in ("character", "figure"):
            continue
        fm = {"layout": "person", "title": e["name"], "person": e["name"], "slug": e["slug"], "permalink": f"/people/{e['slug']}/",
              "aliases": e.get("aliases") or [], "avatar": e.get("avatar") or "", "avatar_source": e.get("avatar_source") or "",
              "search": False, "sitemap": True}
        text = "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n"
        (PAGES / f"{e['slug']}.md").write_text(text, encoding="utf-8", newline="\n")
        n += 1
    index = {"layout": "people-index", "title": "人物", "permalink": "/people/", "search": False}
    (PAGES / "index.md").write_text("---\n" + yaml.safe_dump(index, allow_unicode=True, sort_keys=False) + "---\n", encoding="utf-8", newline="\n")
    print(f"pages: {n} person pages + index")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["registry", "portraits", "commons", "pages", "all"])
    a = ap.parse_args()
    if a.cmd in ("registry", "all"):
        cmd_registry()
    if a.cmd in ("portraits", "all"):
        cmd_portraits()
    if a.cmd in ("commons", "all"):
        cmd_commons()
    if a.cmd in ("pages", "all"):
        cmd_pages()


if __name__ == "__main__":
    main()
