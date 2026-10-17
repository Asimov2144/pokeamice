"""Which Pokémon works and species a fragment talks about (for the sticker row).

Dictionary matching, not a model: works by hand-written aliases against _data/works.yml names,
species by Chinese / English names from tools/weibo_species.json (the app's species snapshot).
Text, the model's topics and caption are searched; OCR text only for species (3+ characters).
"""
import json, re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# work name (as in _data/works.yml) -> regex
WORK_ALIASES = [
    ("宝可梦传说 阿尔宙斯", r"阿尔宙斯|(?<![A-Za-z])(?:PLA|LA)(?![A-Za-z])|Legends:? ?Arceus|洗翠"),
    ("Pokémon LEGENDS Z-A", r"Z-A|(?<![A-Za-z])ZA(?![A-Za-z])|LEGENDS ?Z|密阿雷"),
    ("宝可梦 朱·紫", r"朱[·・＆&/ ]?紫|零之秘宝|(?<![A-Za-z])SV(?![A-Za-z])|Scarlet|帕底亚|蓝之圆盘|碧之假面"),
    ("宝可梦 剑·盾", r"剑[·・＆&/ ]?盾|(?<![A-Za-z])SwSh(?![A-Za-z])|伽勒尔|冠之雪原|铠之孤岛"),
    ("宝可梦 晶灿钻石·明亮珍珠", r"晶灿钻石|明亮珍珠|BDSP"),
    ("宝可梦 钻石·珍珠", r"钻石[·・＆&/ ]?珍珠|(?<![A-Za-z])DPPt?(?![A-Za-z])|(?<![A-Za-z])DP(?![A-Za-z])|神奥"),
    ("宝可梦 Let's Go！皮卡丘·Let's Go！伊布", r"Let'?s ?Go|LGPE|皮卡丘[·・/]伊布"),
    ("宝可梦 太阳·月亮", r"太阳[·・＆&/ ]?月亮|日月|阿罗拉"),
    ("宝可梦 究极之日·究极之月", r"究极之日|究极之月|USUM|究极日月"),
    ("宝可梦 X·Y", r"(?<![A-Za-z])XY(?![A-Za-z])|X[·・＆&/ ]Y(?![A-Za-z])|卡洛斯"),
    ("宝可梦 欧米伽红宝石·阿尔法蓝宝石", r"欧米伽红宝石|阿尔法蓝宝石|ORAS"),
    ("宝可梦 红宝石·蓝宝石", r"红宝石|蓝宝石|丰缘"),
    ("宝可梦 绿宝石", r"绿宝石"),
    ("宝可梦 黑·白", r"黑[·・＆&/ ]?白(?!色)|(?<![A-Za-z])BW(?![A-Za-z])"),
    ("宝可梦 黑2·白2", r"黑2|白2|BW2"),
    ("宝可梦 金·银", r"金[·・＆&/ ]?银"),
    ("宝可梦 心金·魂银", r"心金|魂银|HGSS"),
    ("宝可梦 水晶版", r"水晶版"),
    ("宝可梦 红·绿", r"红[·・＆&/ ]?绿(?!灯)"),
    ("宝可梦 火红·叶绿", r"火红|叶绿|FRLG"),
    ("宝可梦 皮卡丘版", r"皮卡丘版"),
    ("Pokémon GO", r"Pok[ée]mon ?GO|宝可梦 ?GO|PoGo"),
    ("Pokémon HOME", r"Pok[ée]mon ?HOME|宝可梦 ?HOME"),
    ("Pokémon Pokopia", r"Pokopia"),
    ("Pokémon Champions", r"Pok[ée]mon ?Champions|(?<![A-Za-z])Champions(?![A-Za-z])"),
    ("宝可梦集换式卡牌游戏", r"PTCG|TCG|宝可梦卡牌|集换式卡牌|卡牌游戏"),
    ("宝可梦 动画系列", r"宝可梦动画|动画系列|旅途系列"),
    ("名侦探皮卡丘", r"名侦探皮卡丘|Detective Pikachu"),
    ("宝可梦：超梦的逆袭", r"超梦的逆袭|Mewtwo Strikes"),
    ("洛奇亚爆诞", r"洛奇亚爆诞"),
    ("结晶塔的帝王", r"结晶塔的帝王"),
    ("宝可梦随乐拍", r"随乐拍|Pok[ée]mon Snap"),
    ("宝可梦不可思议迷宫", r"不可思议的?迷宫|宝可梦迷宫|(?<![A-Za-z])PMD(?![A-Za-z])"),
    ("宝可梦圆形竞技场", r"圆形竞技场|Colosseum"),
    ("宝可梦竞技场", r"宝可梦竞技场|Pok[ée]mon Stadium"),
    ("宝可梦乱战", r"宝可梦乱战|Rumble"),
    ("宝可梦对战革命", r"对战革命|Battle Revolution"),
    ("宝可梦频道", r"宝可梦频道"),
    ("宝可梦立体图鉴BW", r"立体图鉴"),
    ("宝可梦打字DS", r"打字DS"),
]

# two-character species names that are safe to match as plain substrings
SAFE_TWO = set("波波 拉达 胖丁 六尾 九尾 猴怪 凯西 胡地 臭泥 鬼斯 耿鬼 伊布 快龙 超梦 皮丘 电龙 雷公 炎帝 水君 凤王 谢米 胡帕 布拨 喵喵 豪力".split())
# names that are ordinary words or clash with a title when they stand alone
SKIP = {"梦幻", "阿尔宙斯"}  # bare 阿尔宙斯 in these posts means the game; the species only counts when written Arceus

_works = None
_species = None


def works():
    global _works
    if _works is None:
        data = yaml.safe_load((ROOT / "_data" / "works.yml").read_text(encoding="utf-8"))
        by_name = {w["name"]: w for w in data}
        out = []
        for name, pat in WORK_ALIASES:
            w = by_name.get(name)
            if not w or not w.get("icon"):
                continue
            out.append({"key": f"w{len(out)}", "name": name, "icons": [i for i in (w.get("icon"), w.get("icon2")) if i],
                        "color": w.get("color"), "re": re.compile(pat, re.I)})
        _works = out
    return _works


def species():
    global _species
    if _species is None:
        data = json.loads((ROOT / "tools" / "weibo_species.json").read_text(encoding="utf-8"))
        zh, en = [], []
        for s in data:
            z = s["zh"]
            if z in SKIP:
                continue
            if len(z) >= 3 or z in SAFE_TWO:
                zh.append((z, s))
            if len(s["en"]) >= 5:
                en.append((re.compile(r"(?<![A-Za-z])" + re.escape(s["en"]) + r"(?![A-Za-z])", re.I), s))
        _species = {"zh": zh, "en": en, "arceus": next(s for s in data if s["id"] == 493)}
    return _species


ARCEUS_BARE = re.compile(r"(?<!传说 )(?<!传说)阿尔宙斯")


def find(text, topics="", caption="", ocr=""):
    """-> (work records in order of first mention, species records in order of first mention)"""
    main = "\n".join([text or "", topics or "", caption or ""])
    ws = []
    for w in works():
        m = w["re"].search(main)
        if m:
            ws.append((m.start(), w))
    ws.sort(key=lambda x: x[0])
    sp = {}
    S = species()
    hay = main + "\n" + (ocr or "")
    for z, s in S["zh"]:
        i = hay.find(z)
        if i >= 0 and s["id"] not in sp:
            sp[s["id"]] = (i, s)
    for rx, s in S["en"]:
        m = rx.search(main)
        if m and s["id"] not in sp:
            sp[s["id"]] = (m.start(), s)
    return [w for _, w in ws], [s for _, s in sorted(sp.values(), key=lambda x: x[0])]
