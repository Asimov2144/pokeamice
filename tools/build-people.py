"""The people library: one registry, portraits gathered from what the site already has, a page per person.

    python tools/build-people.py registry      # _data/people.yml: every name in entities.people, slugs, kinds, aliases
    python tools/build-people.py harvest       # the verified photographs in PORTRAITS -> assets/img/people, portraits by year, main avatar
    python tools/build-people.py portraits     # look for more: crop candidates from captioned photos in the posts into scratch/people-candidates
    python tools/build-people.py commons       # (older) the COMMONS map; PORTRAITS' commons: rows do the same now
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
    "横井军平": "yokoi-gunpei", "宫本茂": "miyamoto-shigeru", "廣部圭太": "hirobe-keita", "橘庆太": "tachibana-keita", "木村KAELA": "kimura-kaela",
    "三枝成彰": "saegusa-shigeaki", "松本梨香": "matsumoto-rica", "松岛贤二": "matsushima-kenji", "小林幸子": "kobayashi-sachiko", "远藤雅伸": "endo-masanobu",
    "冈崎体育": "okazaki-taiiku", "高桥伸也": "takahashi-shinya", "武上纯希": "takegami-junki", "松本理恵": "matsumoto-rie", "北村一树": "kitamura-kazuki", "岩本翔": "iwamoto-sho",
    "村田佳奈子": "murata-kanako", "枝川拓人": "edagawa-takuto", "绫野万里奈": "ayano-marina", "阵内弘之": "jinnai-hiroyuki", "宫下尚生": "miyashita-naoki",
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
    "大谷育江": ["大谷育江", "Ikue Otani"], "James Turner": ["James Turner"], "宗像快": ["宗像快", "Kai Munakata"], "小幡敏宏": ["小幡敏宏", "Toshihiro Obata"],
    "吉田宏信": ["吉田宏信", "Hironobu Yoshida"], "市村正亲": ["市村正親", "Masachika Ichimura"], "小笠原裕": ["小笠原裕"], "竹内敦": ["竹内敦"],
    "折本哲也": ["折本哲也"], "小泽达雄": ["小澤達雄"], "松村直树": ["松村直樹"], "长畑成一郎": ["長畑成一郎"], "富江慎一郎": ["冨江慎一郎", "Shinichiro Tomie"],
    "宫本茂": ["宮本茂", "Shigeru Miyamoto"], "井部真那": ["井部真那", "Mana Ibe"], "小野寺瞬": ["小野寺瞬"], "深谷卓": ["深谷卓"], "米谷由贵": ["米谷由貴"],
    "林原惠美": ["林原めぐみ", "Megumi Hayashibara"], "菜花健作": ["菜花健作", "Kensaku Nabana"], "三浦昌幸": ["三浦昌幸"], "三木真一郎": ["三木眞一郎", "Shin-ichiro Miki"],
    "犬山犬子": ["犬山イヌコ", "Inuko Inuyama"], "田谷正夫": ["田谷正夫"], "凯尔·希利亚德": ["Kyle Hilliard"], "川岛优志": ["川島優志", "Masashi Kawashima"],
    "克里斯·塔普塞尔": ["Chris Tapsell"], "北村一树": ["北村一樹"], "岩本翔": ["岩本翔"], "松本梨香": ["松本梨香", "Rica Matsumoto"], "三枝成彰": ["三枝成彰", "Shigeaki Saegusa"],
    "赤木达也": ["赤木達也"], "横井军平": ["横井軍平", "Gunpei Yokoi"], "远藤雅伸": ["遠藤雅伸", "Masanobu Endo"], "小林幸子": ["小林幸子", "Sachiko Kobayashi"],
    "冈崎体育": ["岡崎体育", "Okazaki Taiiku"], "木村KAELA": ["木村カエラ", "Kaela Kimura"], "橘庆太": ["橘慶太", "Keita Tachibana"], "松本理恵": ["松本理恵", "Rie Matsumoto"],
    "武上纯希": ["武上純希", "Junki Takegami"], "本·里夫斯": ["Ben Reeves"], "韦斯利·尹-普尔": ["Wesley Yin-Poole"], "蒂姆·拉里默": ["Tim Larimer"],
    "松岛贤二": ["松島賢二", "Kenji Matsushima"], "高桥伸也": ["高橋伸也", "Shinya Takahashi"], "廣部圭太": ["廣部圭太", "Keita Hirobe"], "野村达雄": ["野村達雄", "Tatsuo Nomura"],
    "村田佳奈子": ["村田佳奈子", "Kanako Murata"], "枝川拓人": ["枝川拓人", "Takuto Edagawa"], "绫野万里奈": ["綾野万里奈", "Marina Ayano"],
    "阵内弘之": ["陣内弘之", "Hiroyuki Jinnai"], "宫下尚生": ["宮下尚生", "Naoki Miyashita"],
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
        "# kind=character 是动画角色、kind=figure 是只被引述的人物，都不建人物页。由 tools/build-people.py 维护：registry 只添加不覆盖，",
        "# harvest 按脚本里 PORTRAITS 表（已核对过身份的照片）裁头像；portraits 里的 post 是照片所在的条目，该条目优先显示这张。",
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
    s = "-".join(lazy_pinyin(re.sub(r"[·・]", "", name)))
    s = re.sub(r"[^a-z0-9-]+", "", s.lower())     # a kana or a symbol that pinyin passed through
    return re.sub(r"-{2,}", "-", s).strip("-")


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


# ---------------------------------------------------------------- harvest
# Photographs whose subject is settled - by the name printed next to it (the 1996 図鑑,
# the staff blog's signed posts), by the original page's markup (社長が訊く: each photo
# follows the box of the person it shows; the importer's captions got the 岩田 ones wrong),
# or by the wiki page it illustrates. src is a path under the repo, a URL, "commons:File:…"
# (licence and author are looked up and recorded) or "bulba:File:…" (the Bulbagarden
# archive). post is the stem of the _posts file the photo comes from, so that entry shows
# this picture rather than the main one; main=True makes it the main portrait. box is an
# explicit face box (x, y, w, h) for a page with several faces on it.
_GF = "assets/images/gamefreak-legacy/staff/"
_IA = "assets/img/interviews/"
_ZUKAN = "https://gallery.pokeamice.com/scan-archive/shodai-zukan-1996-staff-interview/pages/"
_FAMI_POKOPIA = "https://cimg.kgl-systems.io/camion/files/66124/thumbnail_yALX.png?x=1280"   # the article's four-up thumbnail, the profile avatars are its faces
PORTRAITS = [
    # Game Freak staff blog 「晴れたり時々曇ったり」- the writer's own photo in a signed post
    dict(name="海野隆雄", year=2009, src=_GF + "155/unno091120-83ab7cdd.jpg", source="Game Freak 员工博客 2009-11-20「ＨＧ・ＳＳ 語っちゃいます！ その6」", post="2009-11-20-gamefreak-staff-155"),
    dict(name="大村祐介", year=2010, src=_GF + "207/bw101112-bde32c5b.jpg", box=(140, 25, 60, 70), source="Game Freak 员工博客 2010-11-12「ブラック・ホワイトのつくりかた 第7回」", post="2010-11-12-gamefreak-staff-207"),
    dict(name="吉田宏信", year=2008, src=_GF + "89/yoshida080926-7777eb49.jpg", box=(40, 15, 70, 80), source="Game Freak 员工博客 2008-09-26「プラチナここだけの話 第1回」", post="2008-09-26-gamefreak-staff-89"),
    dict(name="松岛贤二", year=2009, src=_GF + "160/matsushima091218-f0bf25c7.jpg", source="Game Freak 员工博客 2009-12-18「ＨＧ・ＳＳ 語っちゃいます！ 最終回」", post="2009-12-18-gamefreak-staff-160"),
    dict(name="松岛贤二", year=2010, src=_GF + "206/bw101105-77d7c4a5.jpg", box=(120, 25, 65, 75), source="Game Freak 员工博客 2010-11-05「ブラック・ホワイトのつくりかた 第6回」", post="2010-11-05-gamefreak-staff-206"),
    dict(name="James Turner", year=2010, src=_GF + "204/bw101022-93dde018.jpg", source="Game Freak 员工博客 2010-10-22「ブラック・ホワイト 開発者インタビュー 第4弾」", post="2010-10-22-gamefreak-staff-204"),
    dict(name="森本茂树", year=2009, src=_GF + "142/morimoto090911-3aedbd5f.jpg", source="Game Freak 员工博客 2009-09-11", post="2009-09-11-gamefreak-staff-142"),
    dict(name="森本茂树", year=2010, src=_GF + "182/morimoto100514_1-2fbbd466.jpg", source="Game Freak 员工博客 2010-05-14", post="2010-05-14-gamefreak-staff-182"),
    dict(name="一之濑刚", year=2009, src=_GF + "151/ichinose091027-025b3780.jpg", source="Game Freak 员工博客 2009-10-27「ＨＧ・ＳＳ 語っちゃいます！ その3」", post="2009-10-27-gamefreak-staff-151"),
    dict(name="景山将太", year=2009, src=_GF + "153/kageyama091106-6457cc0e.jpg", source="Game Freak 员工博客 2009-11-06「ＨＧ・ＳＳ 語っちゃいます！ その4」", post="2009-11-06-gamefreak-staff-153"),
    dict(name="大森滋", year=2009, src=_GF + "148/ohmori091009-767adcf0.jpg", source="Game Freak 员工博客 2009-10-09「ＨＧ・ＳＳ 語っちゃいます！ その1」", post="2009-10-09-gamefreak-staff-148"),
    dict(name="太田哲司", year=2008, src=_GF + "90/tetsuzi081003-ecfe4970.jpg", box=(55, 35, 75, 85), source="Game Freak 员工博客 2008-10-03「プラチナここだけの話 第2回」", post="2008-10-03-gamefreak-staff-90"),
    # 社長が訊く - the photo follows the speaker's box on nintendo.co.jp (checked against the page)
    dict(name="小笠原裕", year=2011, main=True, src=_IA + "2011-06-16-interview-iwata-asks-pokedex-3d-bw-chapter-1/photo2.jpg", source="社長が訊く『ポケモン立体図鑑BW』第1章 photo2", post="2011-06-16-interview-iwata-asks-pokedex-3d-bw-chapter-1"),
    dict(name="竹内敦", year=2011, main=True, src=_IA + "2011-06-16-interview-iwata-asks-pokedex-3d-bw-chapter-1/photo3.jpg", source="社長が訊く『ポケモン立体図鑑BW』第1章 photo3", post="2011-06-16-interview-iwata-asks-pokedex-3d-bw-chapter-1"),
    dict(name="折本哲也", year=2011, main=True, src=_IA + "2011-06-16-interview-iwata-asks-pokedex-3d-bw-chapter-1/photo4.jpg", source="社長が訊く『ポケモン立体図鑑BW』第1章 photo4", post="2011-06-16-interview-iwata-asks-pokedex-3d-bw-chapter-1"),
    dict(name="石原恒和", year=2011, src=_IA + "2011-06-16-interview-iwata-asks-pokedex-3d-bw-chapter-1/photo1.jpg", source="社長が訊く『ポケモン立体図鑑BW』第1章 photo1", post="2011-06-16-interview-iwata-asks-pokedex-3d-bw-chapter-1"),
    dict(name="松村直树", year=2011, main=True, src=_IA + "2011-08-04-interview-iwata-asks-super-pokemon-rumble-chapter-1/photo2.jpg", source="社長が訊く『スーパーポケモンスクランブル』第1章 photo2", post="2011-08-04-interview-iwata-asks-super-pokemon-rumble-chapter-1"),
    dict(name="小泽达雄", year=2011, main=True, src=_IA + "2011-08-04-interview-iwata-asks-super-pokemon-rumble-chapter-1/photo3.jpg", source="社長が訊く『スーパーポケモンスクランブル』第1章 photo3", post="2011-08-04-interview-iwata-asks-super-pokemon-rumble-chapter-1"),
    dict(name="长畑成一郎", year=2012, main=True, src=_IA + "2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-1/photo1.jpg", source="社長が訊く『ポケモン不思議のダンジョン マグナゲートと∞迷宮』第1章 photo1", post="2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-1"),
    dict(name="富江慎一郎", year=2012, main=True, src=_IA + "2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-1/photo2.jpg", source="社長が訊く『ポケモン不思議のダンジョン マグナゲートと∞迷宮』第1章 photo2", post="2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-1"),
    dict(name="石原恒和", year=2012, src=_IA + "2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-1/photo3.jpg", source="社長が訊く『ポケモン不思議のダンジョン マグナゲートと∞迷宮』第1章 photo3", post="2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-1"),
    dict(name="岩田聪", year=2012, src=_IA + "2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-1/photo4.jpg", source="社長が訊く『ポケモン不思議のダンジョン マグナゲートと∞迷宮』第1章 photo4", post="2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-1"),
    # ポケットモンスター図鑑 (1996) staff pages - the name is printed beside each photo
    dict(name="渡边哲也", year=1996, src=_ZUKAN + "p143_p141_ch6_interview_part7.jpg", box=(229, 161, 116, 116), source="ポケットモンスター図鑑 1996 P.141", post="1996-04-05-scan-shodai-zukan-1996-staff-interview"),
    dict(name="藤原基史", year=1996, main=True, src=_ZUKAN + "p143_p141_ch6_interview_part7.jpg", box=(858, 154, 116, 116), source="ポケットモンスター図鑑 1996 P.141（藤原基史）", post="1996-04-05-scan-shodai-zukan-1996-staff-interview"),
    dict(name="西田敦子", year=1996, src=_ZUKAN + "p144_p142_ch6_interview_part8.jpg", box=(901, 137, 106, 106), source="ポケットモンスター図鑑 1996 P.142", post="1996-04-05-scan-shodai-zukan-1996-staff-interview"),
    dict(name="西野弘二", year=1996, src=_ZUKAN + "p144_p142_ch6_interview_part8.jpg", box=(205, 109, 127, 127), source="ポケットモンスター図鑑 1996 P.142", post="1996-04-05-scan-shodai-zukan-1996-staff-interview"),
    # inside other posts
    dict(name="久保雅一", year=2021, main=True, box=(500, 190, 320, 350), src=_IA + "2021-10-25-interview-hobonichi-2021-kubo/001.jpg", source="ほぼ日刊イトイ新聞「編集とは何か。12 小学館 久保雅一さん」（2021）", post="2021-10-25-interview-hobonichi-2021-kubo"),
    dict(name="增田顺一", year=2014, src=_IA + "2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras/img01.jpg", source="2083WEB 2014-10 GAME FREAK サウンドチーム インタビュー", post="2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras"),
    dict(name="佐藤仁美", year=2014, src=_IA + "2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras/img02.jpg", box=(100, 40, 70, 80), source="2083WEB 2014-10 GAME FREAK サウンドチーム インタビュー（左）", post="2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras"),
    dict(name="足立美奈子", year=2014, src=_IA + "2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras/img02.jpg", box=(275, 35, 80, 85), source="2083WEB 2014-10 GAME FREAK サウンドチーム インタビュー（右）", post="2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras"),
    dict(name="廣部圭太", year=2014, main=True, src=_IA + "2014-05-01-tpc-global-hirobe/profimg.jpg", source="株式会社ポケモン 採用サイト インタビュー（2014）", post="2014-05-01-interview-tpc-global-business-hirobe"),
    dict(name="岩尾和昌", year=2022, main=True, src="https://gallery.pokeamice.com/008gUrWjgy1h6zitw3w8pj307s07s75b.jpg", source="日本ゲーム大賞2022 優秀賞 受賞コメントページ", post="2022-10-10-[采访]-宝可梦传说阿尔宙斯-日本游戏大赏-岩尾获奖感言"),
    # CEDiL - every CEDEC talk's page carries its speakers' photographs (cedil_sessions/speaker/<id>/photo)
    dict(name="前泽圭一", year=2026, main=True, src="https://cedil.cesa.or.jp/cedil_sessions/speaker/6586/photo", source="CEDiL 講演者プロフィール（CEDEC 2026 セッション 3366）", post="2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck"),
    dict(name="前泽圭一", year=2023, src="https://cedil.cesa.or.jp/cedil_sessions/speaker/5512/photo", source="CEDiL 講演者プロフィール（CEDEC 2023 セッション 2782）", post="2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza"),
    dict(name="前泽圭一", year=2022, src="https://cedil.cesa.or.jp/cedil_sessions/speaker/5155/photo", source="CEDiL 講演者プロフィール（CEDEC 2022 セッション 2586）", post="2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline"),
    dict(name="Alfredo Spadafina", year=2026, main=True, src="https://cedil.cesa.or.jp/cedil_sessions/speaker/6587/photo", source="CEDiL 講演者プロフィール（CEDEC 2026 セッション 3366）", post="2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck"),
    dict(name="赤木达也", year=2026, main=True, src="https://cedil.cesa.or.jp/cedil_sessions/speaker/6588/photo", source="CEDiL 講演者プロフィール（CEDEC 2026 セッション 3366）", post="2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck"),
    dict(name="宗像快", year=2026, main=True, src="https://cedil.cesa.or.jp/cedil_sessions/speaker/6638/photo", source="CEDiL 講演者プロフィール（CEDEC 2026 セッション 3390）", post="2026-07-22-interview-cedec-2026-battle-system-deck"),
    dict(name="小幡敏宏", year=2026, main=True, src="https://cedil.cesa.or.jp/cedil_sessions/speaker/6639/photo", source="CEDiL 講演者プロフィール（CEDEC 2026 セッション 3390）", post="2026-07-22-interview-cedec-2026-battle-system-deck"),
    dict(name="髙山玲央名", year=2026, main=True, src="https://cedil.cesa.or.jp/cedil_sessions/speaker/6539/photo", source="CEDiL 講演者プロフィール（CEDEC 2026 セッション 3341）", post="2026-07-22-interview-cedec-2026-za-kubernetes-windows-containers"),
    dict(name="髙山玲央名", year=2023, src="https://cedil.cesa.or.jp/cedil_sessions/speaker/5535/photo", source="CEDiL 講演者プロフィール（CEDEC 2023 セッション 2792）"),
    dict(name="一之濑刚", year=2023, src="https://cedil.cesa.or.jp/cedil_sessions/speaker/5584/photo", source="CEDiL 講演者プロフィール（CEDEC 2023 セッション 2819）", post="2023-08-25-interview-cedec-2023-sound-design-ichinose-paldea"),
    dict(name="北村一树", year=2023, main=True, src="https://cedil.cesa.or.jp/cedil_sessions/speaker/5585/photo", source="CEDiL 講演者プロフィール（CEDEC 2023 セッション 2819）", post="2023-08-25-interview-cedec-2023-sound-design-ichinose-paldea"),
    dict(name="岩本翔", year=2023, main=True, src="https://cedil.cesa.or.jp/cedil_sessions/speaker/5586/photo", source="CEDiL 講演者プロフィール（CEDEC 2023 セッション 2819）", post="2023-08-25-interview-cedec-2023-sound-design-ichinose-paldea"),
    # the interviewee profiles the web articles open with - a photograph per speaker; a group shot is cut by face box
    dict(name="村田佳奈子", year=2026, main=True, src=_FAMI_POKOPIA, box=(153, 266, 106, 106), source="ファミ通.com 2026-02-16『ぽこ あ ポケモン』開発インタビュー（サムネイル左から1人目）", post="2026-02-16-interview-famitsu-2026-pokopia"),
    dict(name="大森滋", year=2026, src=_FAMI_POKOPIA, box=(446, 103, 111, 111), source="ファミ通.com 2026-02-16『ぽこ あ ポケモン』開発インタビュー（サムネイル左から2人目）", post="2026-02-16-interview-famitsu-2026-pokopia"),
    dict(name="枝川拓人", year=2026, main=True, src=_FAMI_POKOPIA, box=(736, 157, 113, 113), source="ファミ通.com 2026-02-16『ぽこ あ ポケモン』開発インタビュー（サムネイル左から3人目）", post="2026-02-16-interview-famitsu-2026-pokopia"),
    dict(name="绫野万里奈", year=2026, main=True, src=_FAMI_POKOPIA, box=(925, 268, 108, 108), source="ファミ通.com 2026-02-16『ぽこ あ ポケモン』開発インタビュー（サムネイル左から4人目）", post="2026-02-16-interview-famitsu-2026-pokopia"),
    dict(name="阵内弘之", year=2018, main=True, src="https://www.famitsu.com/images/000/154/405/y_5ab938900d505.jpg", source="ファミ通.com 2018-03-30『名探偵ピカチュウ』開発陣インタビュー（プロフィール写真）", post="2018-03-30-interview-famitsu-detective-pikachu-jinnai-miyashita"),
    dict(name="宫下尚生", year=2018, main=True, src="https://www.famitsu.com/images/000/154/405/y_5ab938f100a5d.jpg", box=(200, 70, 130, 140), source="ファミ通.com 2018-03-30『名探偵ピカチュウ』開発陣インタビュー（プロフィール写真）", post="2018-03-30-interview-famitsu-detective-pikachu-jinnai-miyashita"),
    dict(name="米谷由贵", year=2023, main=True, src=_IA + "2023-04-19-interview-cgworld-2023-sv-making-1/004.jpg", box=(260, 71, 169, 169), source="CGWORLD 2023-04『ポケットモンスター スカーレット・バイオレット』メイキング PART3（左から米谷由貴、小野寺瞬、深谷卓）", post="2023-04-19-interview-cgworld-2023-sv-making-1"),
    dict(name="小野寺瞬", year=2023, main=True, src=_IA + "2023-04-19-interview-cgworld-2023-sv-making-1/004.jpg", box=(856, 60, 161, 161), source="CGWORLD 2023-04『ポケットモンスター スカーレット・バイオレット』メイキング PART3（左から米谷由貴、小野寺瞬、深谷卓）", post="2023-04-19-interview-cgworld-2023-sv-making-1"),
    dict(name="深谷卓", year=2023, main=True, src=_IA + "2023-04-19-interview-cgworld-2023-sv-making-1/004.jpg", box=(1564, 94, 164, 164), source="CGWORLD 2023-04『ポケットモンスター スカーレット・バイオレット』メイキング PART3（左から米谷由貴、小野寺瞬、深谷卓）", post="2023-04-19-interview-cgworld-2023-sv-making-1"),
    dict(name="中津井优", main=True, src="https://media.pocketmonsters.net/staff/10488/main.png", source="PocketMonsters.Net スタッフページ 10488（雑誌掲載のプランナー紹介写真）"),
    dict(name="武上纯希", main=True, src="https://lain.bgm.tv/pic/crt/l/f7/77/294_prsn_oZe70.jpg", source="Bangumi 番组计划 person/294"),
    dict(name="远藤雅伸", main=True, src="https://unavatar.io/x/evezoo", source="X @evezoo プロフィール写真（2026-09 取得）"),
    # the wikis - Bulbapedia's staff pages and the Nintendo Wiki on Fandom, when the site has nothing better
    dict(name="海野隆雄", main=True, src="bulba:File:Takao_Unno.png", source="Bulbapedia File:Takao_Unno.png"),
    dict(name="海野隆雄", src="https://static.wikia.nocookie.net/nintendo/images/2/24/Takao_Unno-0.jpg/revision/latest?path-prefix=en", source="Nintendo Wiki (Fandom) File:Takao_Unno-0.jpg"),
    dict(name="汤山邦彦", main=True, src="https://static.wikia.nocookie.net/nintendo/images/c/c1/Kunihiko_Yuyama.png/revision/latest?path-prefix=en", source="Nintendo Wiki (Fandom) File:Kunihiko_Yuyama.png"),
    dict(name="大村祐介", main=True, src="bulba:File:Yusuke_Ohmura.jpg", source="Bulbapedia File:Yusuke_Ohmura.jpg"),
    dict(name="吉田宏信", main=True, src="bulba:File:Hironobu_Yoshida.jpg", source="Bulbapedia File:Hironobu_Yoshida.jpg"),
    dict(name="大谷育江", main=True, src="bulba:File:Ikue_Otani.jpg", source="Bulbapedia File:Ikue_Otani.jpg"),
    dict(name="井部真那", main=True, src="bulba:File:Mana_Ibe.jpg", source="Bulbapedia File:Mana_Ibe.jpg"),
    dict(name="西田敦子", main=True, src="https://static.wikia.nocookie.net/nintendo/images/1/12/Atsuko_Nishida.jpg/revision/latest?path-prefix=en", source="Nintendo Wiki (Fandom) File:Atsuko_Nishida.jpg"),
    dict(name="林原惠美", main=True, src="bulba:File:Megumi_Hayashibara.jpg", source="Bulbapedia File:Megumi_Hayashibara.jpg"),
    dict(name="James Turner", year=2019, main=True, src="bulba:File:James_Turner_2019.jpg", source="Bulbapedia File:James_Turner_2019.jpg"),
    dict(name="菜花健作", year=2018, main=True, src="bulba:File:Kensaku_Nabana_2018.png", source="Bulbapedia File:Kensaku_Nabana_2018.png"),
    dict(name="渡边哲也", main=True, src="bulba:File:Tetsuya_Watanabe.png", source="Bulbapedia File:Tetsuya_Watanabe.png"),
    dict(name="犬山犬子", main=True, src="bulba:File:Inuko_Inuyama.jpg", source="Bulbapedia File:Inuko_Inuyama.jpg"),
    dict(name="松本梨香", main=True, src="bulba:File:Rica_Matsumoto.jpg", source="Bulbapedia File:Rica_Matsumoto.jpg"),
    dict(name="松岛贤二", main=True, src="bulba:File:Kenji_Matsushima.jpg", source="Bulbapedia File:Kenji_Matsushima.jpg"),
    dict(name="足立美奈子", main=True, src="bulba:File:Minako_Adachi.png", source="Bulbapedia File:Minako_Adachi.png"),
    dict(name="宇都宫崇人", main=True, src="bulba:File:Takato_Utsunomiya.png", source="Bulbapedia File:Takato_Utsunomiya.png"),
    dict(name="岩尾和昌", src="bulba:File:Kazumasa_Iwao.png", source="Bulbapedia File:Kazumasa_Iwao.png"),
    dict(name="前泽圭一", main=True, box=(215, 80, 130, 150), src="https://static.wikia.nocookie.net/nintendo/images/0/06/Keiichi_Maezawa.jpg/revision/latest?path-prefix=en", source="Nintendo Wiki (Fandom) File:Keiichi_Maezawa.jpg"),
    dict(name="横井军平", main=True, src="https://static.wikia.nocookie.net/nintendo/images/3/36/Gunpei_Yokoi.jpg/revision/latest?path-prefix=en", source="Nintendo Wiki (Fandom) File:Gunpei_Yokoi.jpg"),
    dict(name="小幡敏宏", main=True, src="https://static.wikia.nocookie.net/nintendo/images/9/9a/Toshihiro_Obata.jpg/revision/latest?path-prefix=en", source="Nintendo Wiki (Fandom) File:Toshihiro_Obata.jpg"),
    dict(name="森本茂树", main=True, src="https://static.wikia.nocookie.net/nintendo/images/8/89/Shigeki_Morimoto-0.jpg/revision/latest?path-prefix=en", source="Nintendo Wiki (Fandom) File:Shigeki_Morimoto-0.jpg"),
    dict(name="一之濑刚", src="https://static.wikia.nocookie.net/nintendo/images/6/67/Go_Ichinose.png/revision/latest?path-prefix=en", source="Nintendo Wiki (Fandom) File:Go_Ichinose.png"),
    dict(name="景山将太", src="https://static.wikia.nocookie.net/nintendo/images/a/ab/Shota_Kageyama.jpg/revision/latest?path-prefix=en", source="Nintendo Wiki (Fandom) File:Shota_Kageyama.jpg"),
    # Wikimedia Commons, with the licence and author the file page gives
    dict(name="市村正亲", year=2018, main=True, src='commons:File:Ichimura Masachika from "The Man Who Invented Christmas" at Opening Ceremony of the Tokyo International Film Festival 2018 (45619249711).jpg'),
    dict(name="宫本茂", year=2015, main=True, src="commons:File:Shigeru Miyamoto 20150610 (cropped).jpg"),
    dict(name="三木真一郎", main=True, src="commons:File:Shin-ichiro Miki.jpg"),
    dict(name="三枝成彰", year=2010, main=True, src="commons:File:Shigeaki Saegusa 20100124 1.jpg"),
    dict(name="木村KAELA", year=2014, main=True, src="commons:File:Kaela Kimura MTV VMAJ 2014.jpg"),
    dict(name="橘庆太", year=2020, main=True, src="commons:File:Keita Tachibana SOS47 20201222.jpg"),
    dict(name="小林幸子", year=2017, main=True, src="commons:File:Sachiko Kobayashi 2017 (35361318945).jpg"),
    # 2026-09-17: interview photos with the person named in the caption (or, for CGWORLD, the photo that follows the name heading on the page)
    dict(name="尾上将之", year=2019, main=True, src=_IA + "2019-05-09-interview-vgc-gamefreak-gear-project/onoue.jpg", source="VGC 2019-05-09 GAME FREAK 专访：程序员兼总监 尾上将之", post="2019-05-09-interview-vgc-gamefreak-gear-project"),
    dict(name="尾上将之", year=2017, src=_IA + "2017-07-03-interview-denfami-ohmori-onoue-gamefreak-heritage/denfami_ohmori_63.jpg", source="電ファミニコゲーマー 2017-07-03 新世代に訊く 大森滋・尾上将之（_062）", post="2017-07-03-interview-denfami-ohmori-onoue-gamefreak-heritage"),
    dict(name="大洞翔一", year=2020, main=True, src=_IA + "2020-03-01-interview-tpc-business-professionals/career_cont3_topimg.jpg", source="株式会社ポケモン 採用情報 2020「Business Professionals」大洞翔一", post="2020-03-01-interview-tpc-business-professionals"),
    dict(name="森彰人", year=2010, main=True, src=_IA + "2010-03-31-interview-pokemon-com-hgss-masuda-morimoto/mori.jpg", source="Pokemon.com 2010-03-31 HGSS 开发者访谈 森彰人（Programming Lead）", post="2010-03-31-interview-pokemon-com-hgss-masuda-morimoto"),
    dict(name="江上周作", year=2016, main=True, src=_IA + "2016-09-30-interview-gnn-pokemon-go-tokyo-roundtable/0001446177.JPG", source="GNN 2016-09-30 Pokémon GO 东京圆桌：The Pokémon Company 江上周作", post="2016-09-30-interview-gnn-pokemon-go-tokyo-roundtable"),
    dict(name="河合敬一", year=2016, main=True, src=_IA + "2016-09-30-interview-gnn-pokemon-go-tokyo-roundtable/0001446182.JPG", source="GNN 2016-09-30 Pokémon GO 东京圆桌：Niantic 产品本部长 河合敬一", post="2016-09-30-interview-gnn-pokemon-go-tokyo-roundtable"),
    dict(name="野村达雄", year=2016, main=True, src=_IA + "2016-09-30-interview-gnn-pokemon-go-tokyo-roundtable/0001446176.JPG", source="GNN 2016-09-30 Pokémon GO 东京圆桌：Niantic 野村达雄", post="2016-09-30-interview-gnn-pokemon-go-tokyo-roundtable"),
    dict(name="田中宏和", year=2021, main=True, src=_IA + "2020-11-08-interview-creatures-25th-ishihara-tanaka/sec03_img02.png", source="Creatures 公司史特别访谈 2021：田中宏和（代表取締役会長／社長）", post="2021-11-08-interview-creatures-history-special-ishihara-tanaka"),
    dict(name="氏家淳子", year=2017, main=True, src=_IA + "2017-07-15-interview-cgworld-creatures-3d-character-life/creatures_cg_creatures_01.jpg", source="CGWORLD 2017-07 クリーチャーズ 取材写真（氏家淳子氏 见出し后）", post="2017-07-15-interview-cgworld-creatures-3d-character-life"),
    dict(name="中广健吾", year=2017, main=True, src=_IA + "2017-07-15-interview-cgworld-creatures-3d-character-life/creatures_cg_creatures_02.jpg", source="CGWORLD 2017-07 クリーチャーズ 取材写真（中廣健吾氏 见出し后）", post="2017-07-15-interview-cgworld-creatures-3d-character-life"),
    dict(name="畠祐贵", year=2017, main=True, src=_IA + "2017-07-15-interview-cgworld-creatures-3d-character-life/creatures_cg_creatures_03.jpg", source="CGWORLD 2017-07 クリーチャーズ 取材写真（畠 祐貴氏 见出し后）", post="2017-07-15-interview-cgworld-creatures-3d-character-life"),
    dict(name="冈崎体育", main=True, src="bulba:File:Taiiku Okazaki.png", source="Bulbagarden Archives"),
    dict(name="河内丸武史", year=2009, main=True, src=_IA + "2009-03-24-interview-g4tv-platinum-masuda-kawachimaru/01_photo_1.jpg", box=(330, 30, 130, 140), source="G4TV 2009-03-24 白金专访：增田顺一（左）与河内丸武史（右）· 摄影 Raymond Padilla", post="2009-03-24-interview-g4tv-platinum-masuda-kawachimaru"),
    # 2026-09-17 第三批：augment-images 补进访谈的照片里点名受访者的（联系表人眼确认；青年座谈会三人按"5年後の目標"各段的说话人对上）
    dict(name="三浦昌幸", year=2001, main=True, src=_IA + "2001-11-01-interview-nom-2001-pokemon-mini-developers/001.jpg", source="N.O.M 2001-11 ポケモンミニ開発者インタビュー（三浦昌幸さん）", post="2001-11-01-interview-nom-2001-pokemon-mini-developers"),
    dict(name="久須美龍太", year=2001, main=True, src=_IA + "2001-11-01-interview-nom-2001-pokemon-mini-developers/002.jpg", source="N.O.M 2001-11 ポケモンミニ開発者インタビュー（久須美龍太さん）", post="2001-11-01-interview-nom-2001-pokemon-mini-developers"),
    dict(name="久保雅一", year=2000, src=_IA + "2000-06-01-interview-nom-2000-kubo-masakazu-pokemon-hit/001.jpg", source="N.O.M 2000-06 小学館 久保雅一さん", post="2000-06-01-interview-nom-2000-kubo-masakazu-pokemon-hit"),
    dict(name="石原恒和", year=2001, src=_IA + "2001-11-01-interview-nom-2001-ishihara-tsunekazu-pokemon-world/001.jpg", source="N.O.M 2001-11 石原恒和氏", post="2001-11-01-interview-nom-2001-ishihara-tsunekazu-pokemon-world"),
    dict(name="增田顺一", year=2013, src=_IA + "2013-11-16-interview-famitsu-xy-music-fanmeeting-masuda-kageyama/001.jpg", source="ファミ通 2013-11-16 XY 音楽ファンミーティング 増田順一氏", post="2013-11-16-interview-famitsu-xy-music-fanmeeting-masuda-kageyama"),
    dict(name="石原恒和", year=2018, src=_IA + "2018-06-08-interview-denfaminicogamer-pokemon-go-miracle/011.jpg", source="電ファミニコゲーマー 2018-06-08 ポケモン GO 座談会 石原恒和氏（DSC1438）", post="2018-06-08-interview-denfaminicogamer-pokemon-go-miracle"),
    dict(name="川岛优志", year=2018, main=True, src=_IA + "2018-06-08-interview-denfaminicogamer-pokemon-go-miracle/012.jpg", source="電ファミニコゲーマー 2018-06-08 ポケモン GO 座談会 川島優志氏（DSC1458）", post="2018-06-08-interview-denfaminicogamer-pokemon-go-miracle"),
    dict(name="增田顺一", year=2018, src=_IA + "2018-06-08-interview-denfaminicogamer-pokemon-go-miracle/003.jpg", source="電ファミニコゲーマー 2018-06-08 ポケモン GO 座談会 増田順一氏（DSC1430）", post="2018-06-08-interview-denfaminicogamer-pokemon-go-miracle"),
    dict(name="大奈路まりな", year=2014, main=True, src=_IA + "2014-05-01-interview-tpc-youth-roundtable/001.jpg", source="株式会社ポケモン 採用情報 2014 若手座談会（catch_img1）", post="2014-05-01-interview-tpc-youth-roundtable"),
    dict(name="菅野隼人", year=2014, main=True, src=_IA + "2014-05-01-interview-tpc-youth-roundtable/006.jpg", source="株式会社ポケモン 採用情報 2014 若手座談会「ポケモン→現実世界へ」（goal_img2）", post="2014-05-01-interview-tpc-youth-roundtable"),
    dict(name="古谷翔", year=2014, main=True, src=_IA + "2014-05-01-interview-tpc-youth-roundtable/004.jpg", source="株式会社ポケモン 採用情報 2014 若手座談会（catch_img5）", post="2014-05-01-interview-tpc-youth-roundtable"),
    # 2026-09-17 第二批：按访谈逐篇核对的照片（联系表人眼确认；多人合影按左右/三等分取人脸），post 绑定到该篇，卡片就用它
    dict(name="一之濑刚", year=2014, src=_IA + "2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras/contentsTitle_solitiba.jpg", source="2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras · 特别篇：祝贺荣获日本游戏大赏 2014 特别奖！一之濑刚访谈《纸牌跑马》", post="2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras"),
    dict(name="增田顺一", year=2011, src=_IA + "2011-03-04-interview-spong-bw-launch-masuda-sugimori/spong_02.jpg", source="2011-03-04-interview-spong-bw-launch-masuda-sugimori · 增田顺一在欧洲首发活动现场接受媒体专访，神情专注而沉稳。 增田顺一受访照片", post="2011-03-04-interview-spong-bw-launch-masuda-sugimori"),
    dict(name="增田顺一", year=2017, src=_IA + "2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s01.jpg", source="2017-09-05-interview-gigazine-gamefreak-sketches-masuda · 增田顺一谈及早期档案管理：在传真与纸质办公的红绿时代，从未想过未来会向公众展示这些草稿。 增田顺一受访微笑", post="2017-09-05-interview-gigazine-gamefreak-sketches-masuda"),
    dict(name="增田顺一", year=2000, src=_IA + "2000-07-01-interview-nom-genesis-gamefreak/masuda.jpg", source="2000-07-01-interview-nom-genesis-gamefreak · 增田顺一（董事・开发部长）：负责总监、游戏设计、音乐、程序。在《红／绿》中负责音乐、程序。目前负责几乎所有企划和整体总监", post="2000-07-01-interview-nom-genesis-gamefreak"),
    dict(name="增田顺一", year=2000, src=_IA + "2000-07-01-interview-nom-gold-silver-gamefreak/m074.jpg", source="2000-07-01-interview-nom-gold-silver-gamefreak · 增田顺一（董事・开发部长）：追求彻底的执着与人人皆可享受的趣味性，畅谈制作超越宝可梦的全新游戏的抱负。 增田顺一谈 Ga", post="2000-07-01-interview-nom-gold-silver-gamefreak"),
    dict(name="增田顺一", year=2006, src=_IA + "2006-10-01-interview-nom-dp-ishihara-masuda-sugimori/h_ph_2.jpg", source="2006-10-01-interview-nom-dp-ishihara-masuda-sugimori · 增田顺一（株式会社GAME FREAK 董事·开发部长／总监）：继红蓝宝石后再次执掌正作总监，负责神奥世界观、DS双屏系", post="2006-10-01-interview-nom-dp-ishihara-masuda-sugimori"),
    dict(name="石原恒和", year=2006, src=_IA + "2006-10-01-interview-nom-dp-ishihara-masuda-sugimori/ph_73.jpg", region="left3", source="2006-10-01-interview-nom-dp-ishihara-masuda-sugimori · 石原恒和、增田顺一、杉森建三位主创十年重聚珍贵大合影 石原恒和、增田顺一、杉森建三位主创十年重聚珍贵大合影", post="2006-10-01-interview-nom-dp-ishihara-masuda-sugimori"),
    dict(name="增田顺一", year=2006, src=_IA + "2006-10-01-interview-nom-dp-ishihara-masuda-sugimori/ph_73.jpg", region="mid3", source="2006-10-01-interview-nom-dp-ishihara-masuda-sugimori · 石原恒和、增田顺一、杉森建三位主创十年重聚珍贵大合影 石原恒和、增田顺一、杉森建三位主创十年重聚珍贵大合影", post="2006-10-01-interview-nom-dp-ishihara-masuda-sugimori"),
    dict(name="杉森建", year=2006, src=_IA + "2006-10-01-interview-nom-dp-ishihara-masuda-sugimori/ph_73.jpg", region="right3", source="2006-10-01-interview-nom-dp-ishihara-masuda-sugimori · 石原恒和、增田顺一、杉森建三位主创十年重聚珍贵大合影 石原恒和、增田顺一、杉森建三位主创十年重聚珍贵大合影", post="2006-10-01-interview-nom-dp-ishihara-masuda-sugimori"),
    dict(name="增田顺一", year=2010, src=_IA + "2010-03-31-interview-pokemon-com-hgss-masuda-morimoto/masuda.jpg", source="2010-03-31-interview-pokemon-com-hgss-masuda-morimoto · 增田顺一（Junichi Masuda，制作总监 / Director） 增田顺一（Junichi Masuda，制作总", post="2010-03-31-interview-pokemon-com-hgss-masuda-morimoto"),
    dict(name="增田顺一", year=2013, src=_IA + "2013-09-21-interview-nintendolife-2013-xy/001.jpg", source="2013-09-21-interview-nintendolife-2013-xy · Junichi Masuda", post="2013-09-21-interview-nintendolife-2013-xy"),
    dict(name="增田顺一", year=2013, src=_IA + "2013-11-16-interview-4gamer-xy-music-fanmeeting-masuda-kageyama/002.jpg", source="2013-11-16-interview-4gamer-xy-music-fanmeeting-masuda-kageyama · 宝可梦XY总监增田顺一氏。除担任游戏总指挥外，还深度参与作曲", post="2013-11-16-interview-4gamer-xy-music-fanmeeting-masuda-kageyama"),
    dict(name="岩尾和昌", year=2018, src=_IA + "2018-05-15-interview-famitsu-usum-fanmeeting-masuda-battle-music/011_y_5af906045dcd7.jpg", region="mid3", source="2018-05-15-interview-famitsu-usum-fanmeeting-masuda-battle-music · 增田顺一详解为何《宝可梦》系列从不出现“Now Loading”读盘黑屏 增田顺一详解为何《宝可梦》系列从不出现“Now", post="2018-05-15-interview-famitsu-usum-fanmeeting-masuda-battle-music"),
    dict(name="增田顺一", year=2018, src=_IA + "2018-05-15-interview-famitsu-usum-fanmeeting-masuda-battle-music/011_y_5af906045dcd7.jpg", region="right3", source="2018-05-15-interview-famitsu-usum-fanmeeting-masuda-battle-music · 增田顺一详解为何《宝可梦》系列从不出现“Now Loading”读盘黑屏 增田顺一详解为何《宝可梦》系列从不出现“Now", post="2018-05-15-interview-famitsu-usum-fanmeeting-masuda-battle-music"),
    dict(name="菜花健作", year=2018, src=_IA + "2018-10-26-interview-eurogamer-masuda-nabana-lets-go/eurogamer_letsgo_03_gf01.jpg", region="left", source="2018-10-26-interview-eurogamer-masuda-nabana-lets-go · Director Junichi Masuda und 3D Map Design Leader Kensaku Nab", post="2018-10-26-interview-eurogamer-masuda-nabana-lets-go"),
    dict(name="增田顺一", year=2018, src=_IA + "2018-10-26-interview-eurogamer-masuda-nabana-lets-go/eurogamer_letsgo_03_gf01.jpg", region="right", source="2018-10-26-interview-eurogamer-masuda-nabana-lets-go · Director Junichi Masuda und 3D Map Design Leader Kensaku Nab", post="2018-10-26-interview-eurogamer-masuda-nabana-lets-go"),
    dict(name="大森滋", year=2019, src=_IA + "2019-10-24-interview-polygon-2019-swsh/001.jpg", region="left", source="2019-10-24-interview-polygon-2019-swsh · Shigeru Ohmori (left) and Junichi Masuda (right) Shigeru Ohm", post="2019-10-24-interview-polygon-2019-swsh"),
    dict(name="增田顺一", year=2019, src=_IA + "2019-10-24-interview-polygon-2019-swsh/001.jpg", region="right", source="2019-10-24-interview-polygon-2019-swsh · Shigeru Ohmori (left) and Junichi Masuda (right) Shigeru Ohm", post="2019-10-24-interview-polygon-2019-swsh"),
    dict(name="增田顺一", year=2019, src=_IA + "2019-11-12-interview-4gamer-sword-shield-ohmori-masuda-strongest/003.jpg", source="2019-11-12-interview-4gamer-sword-shield-ohmori-masuda-strongest · 《宝可梦 剑·盾》制作人 增田顺一（Junichi Masuda） Game Freak 制作人增田顺一", post="2019-11-12-interview-4gamer-sword-shield-ohmori-masuda-strongest"),
    dict(name="大森滋", year=2016, src=_IA + "2016-09-06-interview-pokemoncojp-2016-ohmori-sm/001.png", source="2016-09-06-interview-pokemoncojp-2016-ohmori-sm · ディレクター・大森滋氏が語る、2つのソフトに込めた想いとは？", post="2016-09-06-interview-pokemoncojp-2016-ohmori-sm"),
    dict(name="大森滋", year=2010, src=_IA + "2010-03-31-interview-pokemon-com-hgss-masuda-morimoto/ohmori.jpg", source="2010-03-31-interview-pokemon-com-hgss-masuda-morimoto · 大森滋（Shigeru Ohmori，策划·游戏设计 / Planner） 大森滋（Shigeru Ohmori，策划·", post="2010-03-31-interview-pokemon-com-hgss-masuda-morimoto"),
    dict(name="大森滋", year=2019, src=_IA + "2019-11-12-interview-4gamer-sword-shield-ohmori-masuda-strongest/002.jpg", source="2019-11-12-interview-4gamer-sword-shield-ohmori-masuda-strongest · 《宝可梦 剑·盾》总监 大森滋（Shigeru Ohmori） Game Freak 游戏总监大森滋", post="2019-11-12-interview-4gamer-sword-shield-ohmori-masuda-strongest"),
    dict(name="宇都宫崇人", year=2016, src=_IA + "2016-08-25-interview-nikkei-utsunomiya-pokemon-go/nikkei_go_p1_p1.jpg", source="2016-08-25-interview-nikkei-utsunomiya-pokemon-go · 宝可梦的宇都宫崇人专务执行董事。兼任统管游戏软件《宝可梦》系列开发的开发本部长，在Pokémon GO中也从最初就作为日", post="2016-08-25-interview-nikkei-utsunomiya-pokemon-go"),
    dict(name="宇都宫崇人", year=2023, src=_IA + "2023-11-20-interview-guardian-pokemon-chief-utsunomiya-hundreds-of-years/utsunomiya_portrait.jpg", source="2023-11-20-interview-guardian-pokemon-chief-utsunomiya-hundreds-of-years · Takato Utsunomiya, COO of The Pokémon Company.（株式会社宝可梦代表取缔役首", post="2023-11-20-interview-guardian-pokemon-chief-utsunomiya-hundreds-of-years"),
    dict(name="宇都宫崇人", year=2024, src=_IA + "2024-11-20-interview-famitsu-pokemon-sleep-1st-anniversary-utsunomiya-nakahata/005.jpg", source="2024-11-20-interview-famitsu-pokemon-sleep-1st-anniversary-utsunomiya-nakahata · 宇都宫崇人 COO 谈及从《Ingress》《Pokémon GO》到生活健康题材的演进 宇都宫崇人 COO 谈及从《I", post="2024-11-20-interview-famitsu-pokemon-sleep-1st-anniversary-utsunomiya-nakahata"),
    dict(name="富江慎一郎", year=2012, src=_IA + "2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-2/photo5.jpg", source="2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-2-system-drama · 富江 慎一郎（株式会社Spike Chunsoft 总监／剧本） 富江慎一郎肖像", post="2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-2-system-drama"),
    dict(name="米谷由贵", year=2023, src=_IA + "2023-04-20-interview-cgworld-2023-sv-making-2/004.jpg", region="left3", source="2023-04-20-interview-cgworld-2023-sv-making-2 · 左から、米谷由貴さん（アートチームサブマネージャー）、小野寺 瞬さん（アートチームマネージャー）、深谷 卓さん（アートチ", post="2023-04-20-interview-cgworld-2023-sv-making-2"),
    dict(name="小野寺瞬", year=2023, src=_IA + "2023-04-20-interview-cgworld-2023-sv-making-2/004.jpg", region="mid3", source="2023-04-20-interview-cgworld-2023-sv-making-2 · 左から、米谷由貴さん（アートチームサブマネージャー）、小野寺 瞬さん（アートチームマネージャー）、深谷 卓さん（アートチ", post="2023-04-20-interview-cgworld-2023-sv-making-2"),
    dict(name="深谷卓", year=2023, src=_IA + "2023-04-20-interview-cgworld-2023-sv-making-2/004.jpg", region="right3", source="2023-04-20-interview-cgworld-2023-sv-making-2 · 左から、米谷由貴さん（アートチームサブマネージャー）、小野寺 瞬さん（アートチームマネージャー）、深谷 卓さん（アートチ", post="2023-04-20-interview-cgworld-2023-sv-making-2"),
    dict(name="景山将太", year=2010, src=_IA + "2015-11-20-interview-steinberg-gamefreak-sound-cubase/studio1.jpg", source="2010-11-20-interview-steinberg-gamefreak-sound-cubase · 景山将太的个人 DAW 编曲工作台：运行着最新版的 Cubase 工程。 编曲工作台实况", post="2010-11-20-interview-steinberg-gamefreak-sound-cubase"),
    dict(name="景山将太", year=2013, src=_IA + "2013-11-16-interview-4gamer-xy-music-fanmeeting-masuda-kageyama/003.jpg", source="2013-11-16-interview-4gamer-xy-music-fanmeeting-masuda-kageyama · 宝可梦XY音响总监景山将太氏。自心金／魂银起参与，统筹本作音乐", post="2013-11-16-interview-4gamer-xy-music-fanmeeting-masuda-kageyama"),
    dict(name="杉森建", year=2000, src=_IA + "2000-07-01-interview-nom-genesis-gamefreak/sugimori.jpg", source="2000-07-01-interview-nom-genesis-gamefreak · 杉森建（董事・艺术总监）：负责角色设计、背景等所有图形相关工作。 杉森建肖像（2000年）", post="2000-07-01-interview-nom-genesis-gamefreak"),
    dict(name="杉森建", year=2000, src=_IA + "2000-07-01-interview-nom-gold-silver-gamefreak/m080.jpg", source="2000-07-01-interview-nom-gold-silver-gamefreak · 杉森建（董事・艺术总监）：充分发挥Game Boy Color的表现力，追求能够激发宝可梦全新魅力的图形表现。 杉森建谈", post="2000-07-01-interview-nom-gold-silver-gamefreak"),
    dict(name="杉森建", year=2006, src=_IA + "2006-10-01-interview-nom-dp-ishihara-masuda-sugimori/h_ph_3.jpg", source="2006-10-01-interview-nom-dp-ishihara-masuda-sugimori · 杉森建（株式会社GAME FREAK 董事·艺术总监）：统领美术团队，负责新宝可梦生态构想、主角与登场人物设计、以及世界", post="2006-10-01-interview-nom-dp-ishihara-masuda-sugimori"),
    dict(name="杉森建", year=2013, src=_IA + "2013-10-08-interview-4gamer-2013-solitiba/006.jpg", source="2013-10-08-interview-4gamer-2013-solitiba · 画像ギャラリー No.010のサムネイル画像 / ゲーム制作集団「ゲームフリーク」が試みる“原点回帰”という挑戦――初の", post="2013-10-08-interview-4gamer-2013-solitiba"),
    dict(name="渡边哲也", year=2013, src=_IA + "2013-10-08-interview-4gamer-2013-solitiba/005.jpg", source="2013-10-08-interview-4gamer-2013-solitiba · 画像ギャラリー No.017のサムネイル画像 / ゲーム制作集団「ゲームフリーク」が試みる“原点回帰”という挑戦――初の", post="2013-10-08-interview-4gamer-2013-solitiba"),
    dict(name="松岛贤二", year=2010, src=_IA + "2010-03-31-interview-pokemon-com-hgss-masuda-morimoto/matsushima.jpg", source="2010-03-31-interview-pokemon-com-hgss-masuda-morimoto · 松岛贤二（Kenji Matsushima，策划 / Planner） 松岛贤二（Kenji Matsushima，策划", post="2010-03-31-interview-pokemon-com-hgss-masuda-morimoto"),
    dict(name="森本茂树", year=2000, src=_IA + "2000-07-01-interview-nom-genesis-gamefreak/morimoto.jpg", source="2000-07-01-interview-nom-genesis-gamefreak · 森本茂树（程序员・策划）：负责程序、策划。在宝可梦中主要担任战斗程序。 森本茂树肖像（2000年）", post="2000-07-01-interview-nom-genesis-gamefreak"),
    dict(name="森本茂树", year=2010, src=_IA + "2010-03-31-interview-pokemon-com-hgss-masuda-morimoto/morimoto.jpg", source="2010-03-31-interview-pokemon-com-hgss-masuda-morimoto · 森本茂树（Shigeki Morimoto，游戏总监 / Game Director） 森本茂树（Shigeki Mor", post="2010-03-31-interview-pokemon-com-hgss-masuda-morimoto"),
    dict(name="海野隆雄", year=2010, src=_IA + "2010-03-31-interview-pokemon-com-hgss-masuda-morimoto/unno.jpg", source="2010-03-31-interview-pokemon-com-hgss-masuda-morimoto · 海野隆雄（Takao Unno，艺术总监 / Art Director） 海野隆雄（Takao Unno，艺术总监 / ", post="2010-03-31-interview-pokemon-com-hgss-masuda-morimoto"),
    dict(name="渡边哲也", year=2000, src=_IA + "2000-07-01-interview-nom-genesis-gamefreak/watanabe.jpg", source="2000-07-01-interview-nom-genesis-gamefreak · 渡边哲也（程序员）：在《红／绿》中负责演出方面的程序，在《金／银》中负责系统程序及声音驱动等。 渡边哲也肖像（2000年", post="2000-07-01-interview-nom-genesis-gamefreak"),
    dict(name="渡边哲也", year=2000, src=_IA + "2000-07-01-interview-nom-gold-silver-gamefreak/m031.jpg", source="2000-07-01-interview-nom-gold-silver-gamefreak · 渡边哲也（程序员）：当初连爆发式走红这种事都做梦也不敢想，只是在一味追求自己所喜爱的东西——他如此说道。 渡边哲也谈最初", post="2000-07-01-interview-nom-gold-silver-gamefreak"),
    dict(name="石原恒和", year=2010, src=_IA + "2010-05-12-interview-wedge-ishihara-pokemon-disney/wedge_p1_img_ed555d907b966ee061416ad1d79f686949592.jpg", source="2010-05-12-interview-wedge-ishihara-pokemon-disney · 石原恒和（宝可梦公司代表取缔役社长）：手持初代iPad接受WEDGE专访，探讨横跨15年的世界级商业奇迹。 石原恒和受访", post="2010-05-12-interview-wedge-ishihara-pokemon-disney"),
    dict(name="石原恒和", year=2020, src=_IA + "2020-12-21-interview-nikkei-ishihara-go-boardgames/ishihara_nikkei_portrait.jpg", source="2020-12-21-interview-nikkei-ishihara-go-boardgames · 株式会社宝可梦代表取缔役社长石原恒和 / Tsunekazu Ishihara, President and CEO o", post="2020-12-21-interview-nikkei-ishihara-go-boardgames"),
    dict(name="石原恒和", year=2006, src=_IA + "2006-10-01-interview-nom-dp-ishihara-masuda-sugimori/h_ph_1.jpg", source="2006-10-01-interview-nom-dp-ishihara-masuda-sugimori · 石原恒和（株式会社宝可梦 代表取缔役社长／制作人）：统筹宝可梦品牌的整体战略规划，在《钻石·珍珠》中作为制作人把控硬件联", post="2006-10-01-interview-nom-dp-ishihara-masuda-sugimori"),
    dict(name="石原恒和", year=2011, src=_IA + "2011-08-04-interview-iwata-asks-super-pokemon-rumble-chapter-1/photo1.jpg", source="2011-08-04-interview-iwata-asks-super-pokemon-rumble-chapter-1-even-my-wife · 石原 恒和（株式会社宝可梦 代表取缔役社长） 石原恒和肖像", post="2011-08-04-interview-iwata-asks-super-pokemon-rumble-chapter-1-even-my-wife"),
    dict(name="石原恒和", year=2012, src=_IA + "2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-2/photo7.jpg", source="2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-2-system-drama · 石原 恒和（株式会社宝可梦 代表取缔役社长） 石原恒和肖像", post="2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-2-system-drama"),
    dict(name="石原恒和", year=2021, src=_IA + "2020-11-08-interview-creatures-25th-ishihara-tanaka/sec02_img02.png", source="2021-11-08-interview-creatures-history-special-ishihara-tanaka · 石原恒和（Tsunekazu Ishihara）：株式会社 The Pokémon Company 代表取缔役社长、株式", post="2021-11-08-interview-creatures-history-special-ishihara-tanaka"),
    dict(name="菜花健作", year=2019, src=_IA + "2019-11-20-interview-cit-kensaku-nabana-robotics/c8856789ec11ab8b1013037cef6929f9-300x225.png", source="2019-11-20-interview-cit-kensaku-nabana-robotics · 名花健作入职 GAME FREAK 后的工作环境与 3DCG 开发工作流 / Kensaku Nabana's crea", post="2019-11-20-interview-cit-kensaku-nabana-robotics"),
    dict(name="西野弘二", year=2000, src=_IA + "2000-07-01-interview-nom-genesis-gamefreak/nishino.jpg", source="2000-07-01-interview-nom-genesis-gamefreak · 西野弘二（策划）：负责企划、数据管理。负责宝可梦出现率的设定以及世界观设定。 西野弘二肖像（2000年）", post="2000-07-01-interview-nom-genesis-gamefreak"),
    dict(name="西野弘二", year=2000, src=_IA + "2000-07-01-interview-nom-gold-silver-gamefreak/m040.jpg", source="2000-07-01-interview-nom-gold-silver-gamefreak · 西野弘二（策划）：不仅构建了地图上的生息分布与出现率，还构筑了每位训练家的隐藏设定与成长谱系。 西野弘二谈训练家职业与内", post="2000-07-01-interview-nom-gold-silver-gamefreak"),
    dict(name="长畑成一郎", year=2012, src=_IA + "2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-2/photo6.jpg", source="2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-2-system-drama · 长畑 成一郎（株式会社Spike Chunsoft 开发制作人） 长畑成一郎肖像", post="2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-2-system-drama"),
]


def _fetch(src):
    """Bytes of a picture: a repo path, a URL, commons:File:… or bulba:File:… - plus a credit
    string for the Commons ones (author · licence)."""
    import json
    import subprocess
    import urllib.parse
    import urllib.request
    hdr = {"User-Agent": "pokeamice-docs/1.0 (docs.pokeamice.com; portrait lookup)"}
    credit = ""
    if src.startswith("commons:") or src.startswith("bulba:"):
        api = "https://commons.wikimedia.org/w/api.php" if src.startswith("commons:") else "https://archives.bulbagarden.net/w/api.php"
        title = src.split(":", 1)[1]
        u = api + "?" + urllib.parse.urlencode({"format": "json", "action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": "1000"})
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=hdr), timeout=60))
        page = next(iter(d["query"]["pages"].values()))
        if "imageinfo" not in page:
            raise RuntimeError(f"no such file: {title}")
        ii = page["imageinfo"][0]
        em = ii.get("extmetadata") or {}
        if src.startswith("commons:"):
            licence = em.get("LicenseShortName", {}).get("value", "")
            artist = re.sub(r"<[^>]+>", "", em.get("Artist", {}).get("value", "")).strip()
            credit = f"Wikimedia Commons {title} · {artist} · {licence}"
        src = ii.get("thumburl") or ii["url"]
    if not src.startswith("http"):
        return (ROOT / src).read_bytes(), credit
    try:
        raw = urllib.request.urlopen(urllib.request.Request(src, headers=hdr), timeout=120).read()
        if raw[:1] != b"<":
            return raw, credit
    except Exception:
        pass
    # Fandom sits behind Cloudflare, which turns urllib away; curl gets through
    import time
    for attempt in range(4):
        raw = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36", src], capture_output=True, timeout=120).stdout
        if raw and raw[:1] != b"<":
            return raw, credit
        time.sleep(3 + 3 * attempt)
    raise RuntimeError(f"could not fetch {src}")


REGIONS = {"left": (0, 0.5), "right": (0.5, 1), "center": (0.25, 0.75), "left3": (0, 0.34), "mid3": (0.33, 0.67), "right3": (0.66, 1)}


def square_crop(raw, box=None, region=None):
    """A 240x240 portrait: around the given face box, else the largest detected face (inside `region`
    - "left" / "right" / "center" / thirds - when the photo has several people), else the middle."""
    import cv2
    import numpy as np
    from PIL import Image
    # webp and the odd format cv2 does not open: go through PIL
    img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        pim = Image.open(io.BytesIO(raw)).convert("RGB")
        img = cv2.cvtColor(np.array(pim), cv2.COLOR_RGB2BGR)
    H, W = img.shape[:2]
    if box is None:
        casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = casc.detectMultiScale(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1.08, 5, minSize=(max(24, W // 14), max(24, H // 14)))
        faces = [tuple(int(v) for v in b) for b in faces]
        if region in REGIONS:
            lo, hi = REGIONS[region]
            faces = [b for b in faces if lo * W <= b[0] + b[2] / 2 <= hi * W]
        if faces:
            box = max(faces, key=lambda b: b[2] * b[3])
        elif region in REGIONS:  # no face found in that part: frame the part itself
            lo, hi = REGIONS[region]
            side = int((hi - lo) * W)
            box = (int(lo * W), max(0, H // 2 - side // 2), side, min(H, side))
            box = (box[0], box[1], box[2] // 2, box[3] // 2)
    if box:
        x, y, w, h = box
        side = int(max(w, h) * 1.8)
        cx, cy = x + w // 2, y + h // 2 + int(h * 0.05)
    else:
        side = min(W, H)
        cx, cy = W // 2, min(H // 2, side // 2 + H // 6)
    side = min(side, W, H)
    x0 = max(0, cx - side // 2); y0 = max(0, cy - side // 2)
    x1 = min(W, x0 + side); y1 = min(H, y0 + side); x0 = max(0, x1 - side); y0 = max(0, y1 - side)
    crop = cv2.resize(img[y0:y1, x0:x1], (240, 240), interpolation=cv2.INTER_AREA if side >= 240 else cv2.INTER_CUBIC)
    ok, buf = cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 86])
    return buf.tobytes(), box is not None


def cmd_harvest(only=None, force=False):
    entries = load_registry()
    known = {e["name"]: e for e in entries}
    AVATARS.mkdir(parents=True, exist_ok=True)
    n_new = n_main = 0
    for row in PORTRAITS:
        name = row["name"]
        if only and name not in only:
            continue
        e = known.get(name)
        if not e:
            print(f"  ?? {name} is not in the registry"); continue
        e.setdefault("slug", slug_for(name))
        # the file's own name tags an undated picture: Takao_Unno-0.jpg -> takao-unno-0
        m = re.search(r"([^/:]+?)[.](?:jpe?g|png|webp|gif)", row["src"].lower())
        tag = str(row.get("year") or re.sub(r"[^a-z0-9]+", "-", m.group(1) if m else row["src"]).strip("-")[:32])
        fname = f"{e['slug']}-{tag}.jpg"
        web = f"/assets/img/people/{fname}"
        have = [p for p in (e.get("portraits") or []) if p.get("image") == web]
        if have and row.get("post") and have[0].get("post") != row["post"]:
            # a second picture from the same year, bound to another entry: its own file, tagged by that entry
            import hashlib
            tag = f"{tag}-{hashlib.md5(row['post'].encode()).hexdigest()[:4]}"
            fname = f"{e['slug']}-{tag}.jpg"
            web = f"/assets/img/people/{fname}"
            have = [p for p in (e.get("portraits") or []) if p.get("image") == web]
        if have and (AVATARS / fname).exists() and not force:
            continue
        try:
            raw, credit = _fetch(row["src"])
            jpg, by_face = square_crop(raw, row.get("box"), row.get("region"))
        except Exception as ex:
            print(f"  !! {name}: {ex}"); continue
        (AVATARS / fname).write_bytes(jpg)
        source = row.get("source") or credit
        if credit and row.get("source"):
            source = f"{row['source']} · {credit}"
        entry = {"image": web}
        if row.get("year"):
            entry["year"] = row["year"]
        entry["source"] = source
        if row.get("post"):
            entry["post"] = row["post"]
        if not have:
            e.setdefault("portraits", []).append(entry)
            n_new += 1
        else:
            have[0].update(entry)
        if row.get("main") or not e.get("avatar"):
            (AVATARS / (e["slug"] + ".jpg")).write_bytes(jpg)
            e["avatar"] = f"/assets/img/people/{e['slug']}.jpg"
            e["avatar_source"] = source
            n_main += 1
        print(f"  {name:8s} {tag:>6s} {'face' if by_face else 'mid '} <- {row['src'][-60:]}")
    for e in entries:
        if e.get("portraits"):
            e["portraits"].sort(key=lambda p: (p.get("year") or 9999, p["image"]))
    save_registry(entries)
    print(f"harvest: {n_new} portraits added, {n_main} main portraits set; {sum(1 for e in entries if e.get('avatar'))} people with a portrait")


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
    ap.add_argument("cmd", choices=["registry", "harvest", "portraits", "commons", "pages", "all"])
    ap.add_argument("--only", nargs="*", help="harvest: just these names")
    ap.add_argument("--force", action="store_true", help="harvest: redo portraits that are already there")
    a = ap.parse_args()
    if a.cmd in ("registry", "all"):
        cmd_registry()
    if a.cmd in ("harvest", "all"):
        cmd_harvest(only=a.only, force=a.force)
    if a.cmd == "portraits":
        cmd_portraits()
    if a.cmd == "commons":
        cmd_commons()
    if a.cmd in ("pages", "all"):
        cmd_pages()


if __name__ == "__main__":
    main()
