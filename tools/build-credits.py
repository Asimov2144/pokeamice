#!/usr/bin/env python3
"""历作宝可梦 staff 名单：抓取、解析、建人物索引。

  python tools/build-credits.py fetch    Bulbapedia「Staff of …」原始 wikitext → archive/credits/wiki/<slug>.wiki
                                         ポケモンWiki「…のスタッフクレジット」→ archive/credits/wiki/<slug>.ja.wiki（假名读法 + 已知汉字）
                                         poke-corpus 里的 staff_list 文本（Switch 世代游戏内原文）→ archive/credits/corpus/<slug>.<lang>.txt
  python tools/build-credits.py parse    wiki（英）为骨架，对齐 ポケモンWiki（日）→ _data/credits/<slug>.yml（职务层级 → 名字 / 假名 / 汉字）
  python tools/build-credits.py index    → archive/credits/index.yml（每个人一条：各作职务；罗马字变体、假名、汉字合并）
  python tools/build-credits.py all

英日对齐：假名转罗马字后与英文名归一比较（去长音/撇号/大小写、ou→o、oh→o、uu→u、忽略姓名先后）；
对不上的（片假名外国人名等）按锚点之间的位置补齐，标 ja_match: positional 供人工核对。
GAMES 表是这份研究的范围：Game Freak 开发的宝可梦作品，外加 ILCA 的 晶灿钻石·明亮珍珠 作对照（developer 标出）。
"""
import argparse
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = ROOT / "archive" / "credits" / "wiki"
CORPUS_OUT = ROOT / "archive" / "credits" / "corpus"
DATA_DIR = ROOT / "_data" / "credits"
INDEX_FILE = ROOT / "archive" / "credits" / "index.yml"  # 全量索引（4MB+），进站的精简版由 site 步骤另生成
CORPUS_SRC = Path(os.environ.get("POKE_CORPUS", r"C:\Users\2144j\Downloads\poke-corpus-main\poke-corpus-main\corpus"))

EN_API = "https://bulbapedia.bulbagarden.net/w/index.php"
JA_API = "https://wiki.pokemonwiki.com/w/index.php"
UA = "pokeamice-research/1.0 (staff credits study)"

# slug, Bulbapedia 页名, ポケモンWiki 页名, 站内 works 名（无则 None）, 年份, 开发商, 备注
GAMES = [
    ("red-green",            "Staff of Pokémon Red and Green",                            "ポケットモンスター 赤・緑のスタッフクレジット",                 "宝可梦 红·绿",                 1996, "Game Freak", None),
    ("blue-jp",              "Staff of Pokémon Blue (JP)",                                "ポケットモンスター 青のスタッフクレジット",                    "宝可梦 蓝",                    1996, "Game Freak", None),
    ("yellow",               "Staff of Pokémon Yellow",                                   "ポケットモンスター ピカチュウのスタッフクレジット",            "宝可梦 皮卡丘版",              1998, "Game Freak", None),
    ("red-blue",             "Staff of Pokémon Red and Blue",                             None,                                                            None,                           1998, "Game Freak", "海外版：含本地化人员"),
    ("gold-silver",          "Staff of Pokémon Gold and Silver",                          "ポケットモンスター 金・銀のスタッフクレジット",                 "宝可梦 金·银",                 1999, "Game Freak", None),
    ("crystal",              "Staff of Pokémon Crystal",                                  "ポケットモンスター クリスタルバージョンのスタッフクレジット",   "宝可梦 水晶版",                2000, "Game Freak", None),
    ("ruby-sapphire",        "Staff of Pokémon Ruby and Sapphire",                        "ポケットモンスター ルビー・サファイアのスタッフクレジット",     "宝可梦 红宝石·蓝宝石",         2002, "Game Freak", None),
    ("box",                  "Staff of Pokémon Box Ruby & Sapphire",                      "ポケモンボックス ルビー&サファイアのスタッフクレジット",       None,                           2003, "Nintendo × Game Freak", "任天堂与 Game Freak 共同开发"),
    ("firered-leafgreen",    "Staff of Pokémon FireRed and LeafGreen",                    "ポケットモンスター ファイアレッド・リーフグリーンのスタッフクレジット", "宝可梦 火红·叶绿",       2004, "Game Freak", None),
    ("emerald",              "Staff of Pokémon Emerald",                                  "ポケットモンスター エメラルドのスタッフクレジット",            "宝可梦 绿宝石",                2004, "Game Freak", None),
    ("diamond-pearl",        "Staff of Pokémon Diamond and Pearl",                        "ポケットモンスター ダイヤモンド・パールのスタッフクレジット",   "宝可梦 钻石·珍珠",             2006, "Game Freak", None),
    ("platinum",             "Staff of Pokémon Platinum",                                 "ポケットモンスター プラチナのスタッフクレジット",              "宝可梦 白金",                  2008, "Game Freak", None),
    ("heartgold-soulsilver", "Staff of Pokémon HeartGold and SoulSilver",                 "ポケットモンスター ハートゴールド・ソウルシルバーのスタッフクレジット", "宝可梦 心金·魂银",       2009, "Game Freak", None),
    ("black-white",          "Staff of Pokémon Black and White",                          "ポケットモンスターブラック・ホワイトのスタッフクレジット",      "宝可梦 黑·白",                 2010, "Game Freak", None),
    ("black2-white2",        "Staff of Pokémon Black 2 and White 2",                      "ポケットモンスターブラック2・ホワイト2のスタッフクレジット",    "宝可梦 黑2·白2",               2012, "Game Freak", None),
    ("dream-radar",          "Staff of Pokémon Dream Radar",                              "ポケモンARサーチャーのスタッフクレジット",                     None,                           2012, "Game Freak", None),
    ("x-y",                  "Staff of Pokémon X and Y",                                  "ポケットモンスター X・Yのスタッフクレジット",                   "宝可梦 X·Y",                   2013, "Game Freak", None),
    ("oras",                 "Staff of Pokémon Omega Ruby and Alpha Sapphire",            "ポケットモンスター オメガルビー・アルファサファイアのスタッフクレジット", "宝可梦 欧米伽红宝石·阿尔法蓝宝石", 2014, "Game Freak", None),
    ("sun-moon",             "Staff of Pokémon Sun and Moon",                             "ポケットモンスター サン・ムーンのスタッフクレジット",           "宝可梦 太阳·月亮",             2016, "Game Freak", None),
    ("usum",                 "Staff of Pokémon Ultra Sun and Ultra Moon",                 "ポケットモンスター ウルトラサン・ウルトラムーンのスタッフクレジット", "宝可梦 究极之日·究极之月", 2017, "Game Freak", None),
    ("lets-go",              "Staff of Pokémon: Let's Go, Pikachu! and Let's Go, Eevee!", "ポケットモンスター Let's Go! ピカチュウ・Let's Go! イーブイのスタッフクレジット", "宝可梦 Let's Go！皮卡丘·Let's Go！伊布", 2018, "Game Freak", None),
    ("sword-shield",         "Staff of Pokémon Sword and Shield",                         "ポケットモンスター ソード・シールドのスタッフクレジット",       "宝可梦 剑·盾",                 2019, "Game Freak", None),
    ("bdsp",                 "Staff of Pokémon Brilliant Diamond and Shining Pearl",      "ポケットモンスター ブリリアントダイヤモンド・シャイニングパールのスタッフクレジット", "宝可梦 晶灿钻石·明亮珍珠", 2021, "ILCA", "对照组：非 Game Freak 开发"),
    ("legends-arceus",       "Staff of Pokémon Legends: Arceus",                          "Pokémon LEGENDS アルセウスのスタッフクレジット",               "宝可梦传说 阿尔宙斯",          2022, "Game Freak", None),
    ("scarlet-violet",       "Staff of Pokémon Scarlet and Violet",                       "ポケットモンスター スカーレット・バイオレットのスタッフクレジット", "宝可梦 朱·紫",             2022, "Game Freak", None),
    ("area-zero",            "Staff of The Hidden Treasure of Area Zero",                 "ポケットモンスター スカーレット・バイオレット ゼロの秘宝のスタッフクレジット", None,          2023, "Game Freak", "朱·紫 DLC"),
    ("legends-za",           "Staff of Pokémon Legends: Z-A",                             "Pokémon LEGENDS Z-Aのスタッフクレジット",                      "Pokémon LEGENDS Z-A",          2025, "Game Freak", None),
    ("pokopia",              "Staff of Pokémon Pokopia",                                  "ぽこ あ ポケモンのスタッフクレジット",                          "Pokémon Pokopia",              2026, "Koei Tecmo × Game Freak", "Koei Tecmo（OMEGA FORCE）与 Game Freak 共同开发；GF 深度参与"),
    ("champions",            "Staff of Pokémon Champions",                                None,                                                            "Pokémon Champions",            2026, "Game Freak", None),
]

SPINOFFS_FILE = ROOT / "archive" / "credits" / "spinoffs.yml"
# discover 时跳过：动画、道具页、Masters EX 的年度分页（DeNA 员工会撑大索引；要加再单列）
DISCOVER_SKIP = re.compile(r"anime|animated|^Staff of (Courage|Purpose)$|Masters EX/|Masters EX$|^Staff of Pokemon ", re.I)


def all_games():
    """核心表（Game Freak 作品，core=True）+ discover 出来的外传（archive/credits/spinoffs.yml，core=False）。"""
    games = [dict(slug=s, title=t, ja_title=j, work=w, year=y, developer=d, note=n, core=True) for s, t, j, w, y, d, n in GAMES]
    if SPINOFFS_FILE.exists():
        seen = {g["slug"] for g in games}
        for g in yaml.safe_load(SPINOFFS_FILE.read_text(encoding="utf-8")) or []:
            if g["slug"] not in seen:
                games.append({"work": None, "note": None, "ja_title": None, **g, "core": False})
    return games


def slugify(title):
    s = unicodedata.normalize("NFKD", title.replace("Staff of ", ""))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    s = re.sub(r"^(the )?pokemon:? ", "", s)
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")


def cmd_discover():
    """Bulbapedia 全部「Staff of …」页 → 外传表：从页首句取游戏页名，再读游戏 infobox 的 developer / release_date_ja。"""
    r = requests.get("https://bulbapedia.bulbagarden.net/w/api.php",
                     params={"action": "query", "list": "allpages", "apprefix": "Staff of", "aplimit": 500, "format": "json"},
                     headers={"User-Agent": UA}, timeout=60)
    titles = [p["title"] for p in r.json()["query"]["allpages"]]
    core = {t for _, t, *_ in GAMES}
    known = {g["slug"]: g for g in (yaml.safe_load(SPINOFFS_FILE.read_text(encoding="utf-8")) or [])} if SPINOFFS_FILE.exists() else {}
    out = []
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    for title in titles:
        if title in core or DISCOVER_SKIP.search(title):
            continue
        slug = slugify(title)
        if slug in known:
            out.append(known[slug])
            continue
        text = _get(EN_API, title, follow=False)
        time.sleep(1.0)
        if text is None or re.match(r"\s*#REDIRECT", text, re.I):
            continue
        if not re.search(r"^\*|^\{\|", text, re.M):
            continue  # 目录页（如 Masters EX）
        (WIKI_DIR / f"{slug}.wiki").write_text(text, encoding="utf-8")
        g = {"slug": slug, "title": title}
        jm = re.search(r"\[\[ja:([^\]]+)\]\]", text)
        if jm:
            g["ja_title"] = jm.group(1).strip()
        intro = text.split("\n==", 1)[0]
        page, dev, year = game_infobox(title, intro)
        if page:
            g["game_page"] = page
        dm2 = re.search(r"developed by (.+?)(?:\.|,? and (?:was )?published| for the)", intro)
        if not dev and dm2:
            dev = clean_markup(LINK_RE.sub(lambda m: m.group(2) or m.group(1), dm2.group(1)))
        g["developer"] = dev or "?"
        g["year"] = year or 0
        out.append(g)
        print(f"{slug}: {g.get('year')} {g.get('developer')} {'ja✓' if g.get('ja_title') else 'ja✗'}")
    out.sort(key=lambda g: (g.get("year") or 0, g["slug"]))
    with SPINOFFS_FILE.open("w", encoding="utf-8") as fh:
        fh.write("# 由 tools/build-credits.py discover 生成：Bulbapedia 全部「Staff of …」页里核心表之外的游戏（year/developer 取自游戏页 infobox，可手改）\n")
        yaml.safe_dump(out, fh, allow_unicode=True, sort_keys=False, width=200)
    print(f"discover: {len(out)} 部外传 → {SPINOFFS_FILE.relative_to(ROOT)}")


# corpus 目录名 → (slug, staff_list 文本块名)
CORPUS = {
    "LetsGoPikachuLetsGoEevee": ("lets-go", "staff_list"),
    "SwordShield": ("sword-shield", "staff_list"),
    "BrilliantDiamondShiningPearl": ("bdsp", "dlp_staff_list"),
    "LegendsArceus": ("legends-arceus", "staff_list"),
    "ScarletViolet": ("scarlet-violet", "staff_list"),
    "LegendsZA": ("legends-za", "staff_list"),
    "DreamRadar": ("dream-radar", "StaffRoll"),
}


# ---------------------------------------------------------------- fetch

def _get(api, title, follow=True):
    r = requests.get(api, params={"title": title, "action": "raw"}, headers={"User-Agent": UA}, timeout=60, allow_redirects=True)
    if r.status_code != 200 or not r.text.strip():
        return None
    m = re.match(r"\s*#(?:REDIRECT|転送)\s*\[\[([^\]|]+)", r.text, re.I)
    if m and follow:
        r = requests.get(api, params={"title": m.group(1), "action": "raw"}, headers={"User-Agent": UA}, timeout=60)
    return r.text


PLATFORM_LINK_RE = re.compile(r"Generation|Nintendo|Game Boy|Wii|3DS|Switch|series|iOS|Android|arcade|mobile|smartphone|Virtual Console", re.I)


def game_infobox(title, intro):
    """找游戏页：先试「Staff of X」的 X，再试首句里的链接（跳过平台/世代链接）；返回 (页名, developer, year)。"""
    cands = [title.replace("Staff of ", "").strip()]
    cands += [m.group(1).strip() for m in LINK_RE.finditer(intro) if not PLATFORM_LINK_RE.search(m.group(1)) and m.group(1).strip() not in cands]
    for cand in cands[:4]:
        page = _get(EN_API, cand)
        time.sleep(1.0)
        if not page or not re.search(r"\{\{Infobox[_ ]game", page, re.I):
            continue
        dev = year = None
        dm = re.search(r"^\|\s*developer\s*=\s*(.+)$", page, re.M)
        if dm:
            dev = clean_markup(re.sub(r"<br\s*/?>", ", ", LINK_RE.sub(lambda m: m.group(2) or m.group(1), dm.group(1))))
        ym = re.search(r"^\|\s*release_date_ja\s*=[^\n]*?(\d{4})", page, re.M) or re.search(r"^\|\s*release_date_\w+\s*=[^\n]*?(\d{4})", page, re.M)
        if ym:
            year = int(ym.group(1))
        return cand, dev, year
    return None, None, None


def fetch_wiki(force=False):
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    for g in all_games():
        slug = g["slug"]
        for api, title, suffix in ((EN_API, g["title"], ".wiki"), (JA_API, g["ja_title"], ".ja.wiki")):
            if not title:
                continue
            out = WIKI_DIR / f"{slug}{suffix}"
            if out.exists() and not force:
                continue
            text = _get(api, title)
            if text is None:
                print(f"!! {slug}{suffix}: 抓取失败（{title}）", file=sys.stderr)
                continue
            out.write_text(text, encoding="utf-8")
            print(f"{slug}{suffix}: {len(text)} bytes")
            time.sleep(1.0)


def corpus_block(path, block):
    """poke-corpus 文本：qid 文件给 ID，各语言文件同行号给文本。返回 staff 块的行。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln == f"Text File : {block}":
            start = i + 2  # 跳过下一行的 ~~~~
        elif start is not None and i >= start and ln.startswith("~~~~~"):
            return lines[start:i - 1] if lines[i - 1].startswith("Text File") else lines[start:i]
    return lines[start:] if start is not None else []


def fetch_corpus():
    if not CORPUS_SRC.exists():
        print(f"!! corpus 不存在：{CORPUS_SRC}（用 POKE_CORPUS 指定）", file=sys.stderr)
        return
    CORPUS_OUT.mkdir(parents=True, exist_ok=True)
    for folder, (slug, block) in CORPUS.items():
        d = CORPUS_SRC / folder
        if not d.exists():
            continue
        for kind in [p.name.split("_", 1)[1] for p in d.glob("qid_*.txt")]:
            qid = corpus_block(d / f"qid_{kind}", block)
            if not qid:
                continue
            for lang in ("en", "ja", "ja-Hrkt", "zh-Hans"):
                f = d / f"{lang}_{kind}"
                if f.exists():
                    (CORPUS_OUT / f"{slug}.{lang}.txt").write_text("\n".join(corpus_block(f, block)) + "\n", encoding="utf-8")
            (CORPUS_OUT / f"{slug}.qid.txt").write_text("\n".join(qid) + "\n", encoding="utf-8")
            print(f"{slug}: corpus {block} {len(qid)} 行 ({kind})")
            break


# ---------------------------------------------------------------- kana → romaji

_KANA = {
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
    "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko", "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
    "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so", "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
    "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to", "だ": "da", "ぢ": "ji", "づ": "zu", "で": "de", "ど": "do",
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
    "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho", "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
    "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo", "や": "ya", "ゆ": "yu", "よ": "yo",
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro", "わ": "wa", "ゐ": "i", "ゑ": "e", "を": "o", "ん": "n",
    "ゔ": "vu",
    "きゃ": "kya", "きゅ": "kyu", "きょ": "kyo", "ぎゃ": "gya", "ぎゅ": "gyu", "ぎょ": "gyo",
    "しゃ": "sha", "しゅ": "shu", "しょ": "sho", "じゃ": "ja", "じゅ": "ju", "じょ": "jo",
    "ちゃ": "cha", "ちゅ": "chu", "ちょ": "cho", "にゃ": "nya", "にゅ": "nyu", "にょ": "nyo",
    "ひゃ": "hya", "ひゅ": "hyu", "ひょ": "hyo", "びゃ": "bya", "びゅ": "byu", "びょ": "byo", "ぴゃ": "pya", "ぴゅ": "pyu", "ぴょ": "pyo",
    "みゃ": "mya", "みゅ": "myu", "みょ": "myo", "りゃ": "rya", "りゅ": "ryu", "りょ": "ryo",
    "しぇ": "she", "じぇ": "je", "ちぇ": "che", "てぃ": "ti", "でぃ": "di", "とぅ": "tu", "どぅ": "du", "つぁ": "tsa", "つぃ": "tsi", "つぇ": "tse", "つぉ": "tso",
    "ふぁ": "fa", "ふぃ": "fi", "ふぇ": "fe", "ふぉ": "fo", "ふゅ": "fyu", "うぃ": "wi", "うぇ": "we", "うぉ": "wo",
    "ゔぁ": "va", "ゔぃ": "vi", "ゔぇ": "ve", "ゔぉ": "vo", "いぇ": "ye", "でゅ": "dyu", "てゅ": "tyu",
}


def kana_to_romaji(s):
    """假名（平/片）→ 简易黑本式罗马字；ー 延长前一元音，っ 重复下一辅音。仅用于归一比较，不求美观。"""
    out, i = [], 0
    # 片假名 → 平假名（ー 保留）
    s = "".join(chr(ord(ch) - 0x60) if "ァ" <= ch <= "ヶ" else ch for ch in s)
    while i < len(s):
        ch = s[i]
        if ch == "っ":
            nxt = _KANA.get(s[i + 1:i + 3]) or _KANA.get(s[i + 1:i + 2]) if i + 1 < len(s) else None
            if nxt:
                out.append(nxt[0] if nxt[0] not in "aeiou" else "")
            i += 1
            continue
        if ch == "ー":
            if out and out[-1] and out[-1][-1] in "aeiou":
                out.append(out[-1][-1])
            i += 1
            continue
        two = _KANA.get(s[i:i + 2])
        if two:
            out.append(two)
            i += 2
            continue
        one = _KANA.get(ch)
        if one is not None:
            out.append(one)
        elif ch in " \u3000":
            out.append(" ")
        i += 1
    return "".join(out)


def norm(name):
    """罗马字归一：去附加符号、小写、去非字母；oh→o、ou→o、oo→o、uu→u；姓名顺序不计。"""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    s = re.sub(r"[^a-z ]", "", s)

    def n1(p):
        p = re.sub(r"oh(?=[^aeiou]|$)", "o", p)
        p = re.sub(r"uh(?=[^aeiou]|$)", "u", p)
        # 训令式 → 黑本式（Nisino/Fuziwara/Tutiya/Huzi）：先拆成训令式再统一成黑本式
        p = re.sub(r"s(?=i)", "sh", re.sub(r"sh(?=i)", "s", p))
        p = re.sub(r"(?<!s)t(?=i)", "ch", re.sub(r"ch(?=i)", "t", p))
        p = re.sub(r"(?<![cs])t(?=u)", "ts", re.sub(r"ts(?=u)", "t", p))
        p = re.sub(r"(?<![cs])h(?=u)", "f", re.sub(r"f(?=u)", "h", p))
        p = re.sub(r"zy", "j", re.sub(r"sy", "sh", re.sub(r"ty", "ch", p)))
        p = re.sub(r"z(?=i)", "j", re.sub(r"j(?=i)", "z", p))
        p = p.replace("dzu", "zu").replace("du", "zu")
        return p.replace("ou", "o").replace("uu", "u").replace("oo", "o").replace("ii", "i").replace("mb", "nb").replace("mp", "np")
    return " ".join(sorted(n1(p) for p in s.split()))


# ---------------------------------------------------------------- parse: Bulbapedia

LEAD_RE = re.compile(r"^(?:'''\s*([A-Za-z][A-Za-z /&-]*?)\s*:?\s*'''\s*:?\s*|(Lead|Leader|Chief|Sub-?lead|Team Lead|Section Lead|Manager)\s*:\s*)")
LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
JA_RE = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
INTERWIKI_RE = re.compile(r"^\[\[[a-z]{2,3}:")
VIRTUAL_PARENT_RE = re.compile(r"\b(Section|Studio|Laboratory|Lab|Department|Division)\s*$", re.I)
TOP_TIER_RE = re.compile(r"^((very )?special thanks|supervisors?|(general |executive |associate |co-)?producers?|executive directors?)$")
ROLE_NOTE_RE = re.compile(r"(?:Called|Referred to as)\s+'''([^']+)'''\s*\(Japanese:\s*'''([^']+)'''\)|\(Japanese:\s*'''([^']+)'''\)")


def clean_markup(s):
    s = re.sub(r"<ref[^>]*/>", "", s)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"\{\{tt\|([^|}]+)\|[^}]*\}\}", r"\1", s)
    s = re.sub(r"\{\{[^}]*\}\}", "", s)
    s = s.replace("'''", "").replace("''", "")
    s = re.sub(r"<[^>]+>", "", s)
    return s.strip()


def parse_name_line(raw):
    """`* [[Link|Name]]` / `* '''Lead:''' Name` / `* Name (note)` → dict"""
    s = raw.lstrip("*#: ").strip()
    s = re.sub(r"\[https?://\S+\s+([^\]]+)\]", r"\1", s)  # 外链 [url 文字] → 文字
    footnote = bool(re.search(r"\*\s*$", s)) or "<ref" in s
    s = re.sub(r"\*+\s*$", "", s).strip()
    lead = None
    m = LEAD_RE.match(s)
    if m:
        lead = (m.group(1) or m.group(2)).strip()
        s = s[m.end():]
    bm = re.match(r"^((?:[A-Z][a-z]+ ){0,3}by)\s*:\s*", s)  # 「Remix by: Toby Fox」「Performed by: …」
    note = None
    if bm:
        note, s = bm.group(1), s[bm.end():]
    link = None
    lm = LINK_RE.search(s)
    if lm:
        link = lm.group(1).strip()
        s = s[:lm.start()] + (lm.group(2) or lm.group(1)) + s[lm.end():]
    s = clean_markup(s)
    nm = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", s)
    if nm and nm.group(1).strip():
        s, note = nm.group(1).strip(), (note + "; " if note else "") + nm.group(2).strip()
    s = re.sub(r"\*+$", "", s).strip()
    if not s or re.fullmatch(r"(\w+ )?(Editing|Translation|Testing|Localization|Localisation)", s):
        return None
    d = {"name": s}
    if footnote:
        d["footnote"] = True
    if link and link != s:
        d["link"] = link
    if lead:
        d["lead"] = lead
    if note:
        d["note"] = note
    return d


def parse_wiki(text):
    """Bulbapedia wikitext → sections: [{path: [...], names: [...]}]；表格里的日文列按顺序对齐到同节的罗马字名。"""
    sections, anomalies = [], []
    stack = {}
    virtual = {}  # level → 「… Section」标题：同级后续标题挂到它下面（Z-A 等页把 section 与 team 写成同级）
    cur = None
    in_table = False
    table_cols = []
    col = -1

    def flush_table():
        nonlocal table_cols, col, in_table
        if not table_cols:
            return
        roman = [c for c in table_cols if c and not JA_RE.search(c[0]["name"])]
        ja = [c for c in table_cols if c and JA_RE.search(c[0]["name"])]
        for c in roman:
            cur["names"].extend(c)
        if ja and roman:
            flat = [n for c in roman for n in c]
            jflat = [n["name"] for c in ja for n in c]
            if len(flat) == len(jflat):
                for n, j in zip(flat, jflat):
                    n["kanji"] = re.sub(r"[\s\u3000]+", "", j)
                    n["ja_match"] = "bulbapedia-table"
            else:
                anomalies.append(f"表格日文列对不齐：{cur['path']} {len(flat)} vs {len(jflat)}")
                cur.setdefault("ja_unaligned", []).extend(jflat)
        elif ja:
            cur.setdefault("ja_unaligned", []).extend(n["name"] for c in ja for n in c)
        table_cols, col, in_table = [], -1, False

    for raw in text.splitlines():
        ln = raw.strip()
        if not ln:
            continue
        hm = re.match(r"^(=+)\s*(.*?)\s*\1$", ln)
        if hm:
            flush_table()
            level = len(hm.group(1))
            title = clean_markup(hm.group(2))
            title = LINK_RE.sub(lambda m: m.group(2) or m.group(1), title)
            for k in [k for k in stack if k >= level]:
                del stack[k]
            # 虚拟父级只服务「平铺」写法（Z-A：===Programming Section=== 后面跟同级的 ===Field Team===）；
            # 一旦出现更深一级的标题，说明这页是真嵌套，作废
            for k in [k for k in virtual if k != level]:
                del virtual[k]
            stack[level] = title
            vparent = None
            if VIRTUAL_PARENT_RE.search(title):
                virtual[level] = title
            elif virtual.get(level) and re.search(r"\bteam\b|supervisors?$|section directors?$|^main scenario$", title, re.I):
                vparent = virtual[level]
            elif level in virtual:
                del virtual[level]
            path = [stack[k] for k in sorted(stack) if k >= 2 and stack[k].lower() not in ("list of staff", "staff", "staff list", "credits")]
            if vparent and path and path[-1] == title:
                path = path[:-1] + [vparent, title]
            # 页尾的 Producers / Supervisors / Special Thanks 常被排在最后一个公司标题下面：它们是全局职务，去掉公司父级
            if TOP_TIER_RE.match(title.lower()) and len(path) > 1 and (is_company(path[-2]) or "pokémon company" in path[-2].lower()):
                path = [title]
            if title.lower() in ("see also", "references", "external links", "trivia", "notes", "related articles"):
                cur = None
                continue
            cur = {"path": path, "names": []}
            sections.append(cur)
            continue
        if cur is None or INTERWIKI_RE.match(ln):
            continue
        if ln.startswith("{|"):
            in_table, table_cols, col = True, [], -1
            continue
        if in_table:
            if ln.startswith("|}"):
                flush_table()
                continue
            if ln.startswith("|") or ln.startswith("!"):
                if ln.startswith("|-"):
                    continue
                table_cols.append([])
                col += 1
                rest = ln.lstrip("|! ").split("|", 1)
                body = rest[1].strip() if len(rest) > 1 and "=" in rest[0] else ln.lstrip("|! ").strip()
                if body and not re.match(r"^(width|lang|style|align|class)=", body):
                    d = parse_name_line(body) if body.startswith("*") else None
                    if d:
                        table_cols[col].append(d)
                continue
            if ln.startswith("*") and col >= 0:
                d = parse_name_line(ln)
                if d:
                    table_cols[col].append(d)
                continue
            continue
        if ln.startswith("*") or ln.startswith("#"):
            d = parse_name_line(ln)
            if d:
                cur["names"].append(d)
            continue
        rn = ROLE_NOTE_RE.search(ln)
        if rn:
            cur["ja_role"] = rn.group(2) or rn.group(3)
            if rn.group(1):
                cur["ja_role_en"] = rn.group(1)
            continue
        if ln.startswith(("This is a", "The following", "[[Category", "{{", "}}", "<!--", "__")):
            continue
        if ln.startswith("'''NOTE") or ln.startswith("<blockquote"):
            cur.setdefault("notes", []).append(clean_markup(ln)[:300])
            continue
        anomalies.append(f"{cur['path']}: {ln[:80]}")

    sections = [s for s in sections if s["names"] or s.get("ja_unaligned")]
    return sections, anomalies


# ---------------------------------------------------------------- parse: ポケモンWiki

def parse_ja_wiki(text):
    """ポケモンWiki 两种写法：`;職名` + `:[[漢字|かな]]`（定义列表），或 `===職名===` + `* かな`（标题 + 列表）。
    → 平铺的 [{kana, kanji?, lead?, role, comment?}]，按 credits 顺序；kana 也可能是罗马字（第七世代起日版 credits 用拉丁字母）。"""
    out, role, pending = [], [], False
    for raw in text.splitlines():
        ln = raw.strip()
        if not ln or INTERWIKI_RE.match(ln) or ln.startswith("[[Category") or ln.startswith("{{"):
            continue
        hm = re.match(r"^(=+)\s*(.*?)\s*\1$", ln)
        if hm:
            level = len(hm.group(1))
            title = clean_markup(LINK_RE.sub(lambda m: m.group(2) or m.group(1), hm.group(2)))
            role = [] if level <= 2 else role[:level - 3] + [title]
            continue
        if ln.startswith(";"):
            title = clean_markup(LINK_RE.sub(lambda m: m.group(2) or m.group(1), ln[1:]))
            if not pending:
                role = []  # 上一组已有名字：新的 ; 开启新职务
            role.append(title)
            pending = True
            continue
        if ln.startswith(":") or ln.startswith("*"):
            pending = False
            body = ln.lstrip(":* ").strip()
            comment = None
            cm = re.search(r"<!--(.*?)-->", body, re.S)
            if cm:
                comment = cm.group(1).strip()
            lead = None
            lm = re.match(r"^(?:'''\s*)?(リーダー|リード|チーフ|サブリーダー|Lead|Leader)\s*(?:'''\s*)?[:：]?\s*", body)
            if lm:
                lead, body = lm.group(1), body[lm.end():]
            kanji = None
            km = LINK_RE.search(body)
            if km:
                kanji = km.group(1).strip()
                body = body[:km.start()] + (km.group(2) or km.group(1)) + body[km.end():]
            kana = clean_markup(body)
            pm = re.search(r"[（(]([^）)]*)[）)]\s*$", kana)
            ja_note = None
            if pm:  # 「いべ まな（ゲームフリーク）」：括号是所属，不是名字
                ja_note, kana = pm.group(1).strip(), kana[:pm.start()].strip()
            # 行内夹带的职名（「アートディレクター うじいえ あつこ」）
            kana = re.sub(r"^[゠-ヿ・]+(ディレクター|マネージャー|プロデューサー|リーダー|デザイナー)\s+", "", kana)
            if not kana:
                continue
            d = {"kana": kana, "role": " / ".join(role)}
            if kanji:
                kanji = re.sub(r"^w:", "", kanji)
                kanji = re.sub(r"\s*[（(][^）)]*[）)]\s*$", "", kanji).strip()
            if kanji and kanji != kana and JA_RE.search(kanji) and not re.fullmatch(r"[\u30a0-\u30ff・ー\s]+", kanji):
                d["kanji"] = kanji
            if ja_note:
                d["note"] = ja_note
            if lead:
                d["lead"] = lead
            if comment:
                d["comment"] = comment
            out.append(d)
    return out


ROMAJI_SYL = re.compile(r"^(?:(?:[bcdfghjkmnprstvwyz]|sh|ch|ts|ky|gy|ny|hy|by|py|my|ry|dz)?y?[aeiou]h?|n|m(?=[bp]))+$")


def looks_japanese_romaji(name):
    toks = re.sub(r"[^a-z ]", "", unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()).split()
    return bool(toks) and all(ROMAJI_SYL.match(t) for t in toks)


def script_compatible(en, ja):
    """位置补齐的守卫：英文名像日式罗马字 ↔ 日文是平假名/汉字；否则 ↔ 片假名。拉丁字母的日文名一律放行。"""
    if not JA_RE.search(ja):
        return True
    katakana = bool(re.fullmatch(r"[\u30a0-\u30ff・ー\s]+", ja.strip()))
    return looks_japanese_romaji(en) != katakana


def ja_key(kana):
    """日文名单里的名字 → 归一键：假名转罗马字；已是拉丁字母就直接归一。"""
    return norm(kana_to_romaji(kana)) if JA_RE.search(kana) else norm(kana)


def align_ja(sections, ja_list, stats):
    """英文骨架 ↔ 日文名单：先按归一罗马字精确匹配，再按锚点间位置补齐。"""
    flat = [n for s in sections for n in s["names"]]
    ja_keys = [ja_key(j["kana"]) for j in ja_list]
    en_keys = [norm(n["name"]) for n in flat]
    # 同一游戏里同一个人会在多处出现（如 Special Thanks），按出现次序一一配对
    from collections import defaultdict
    ja_pos = defaultdict(list)
    for i, k in enumerate(ja_keys):
        ja_pos[k].append(i)
    used_ja = set()
    match = {}  # en idx → ja idx
    for i, k in enumerate(en_keys):
        if ja_pos.get(k):
            j = ja_pos[k].pop(0)
            match[i] = j
            used_ja.add(j)
    # 位置补齐：相邻两个锚点之间，未匹配的英文/日文数量相等则一一对应
    blocked = set()
    anchors = sorted(match.items())
    bounds = [(-1, -1)] + anchors + [(len(flat), len(ja_list))]
    for (e0, j0), (e1, j1) in zip(bounds, bounds[1:]):
        ens = [i for i in range(e0 + 1, e1) if i not in match]
        jas = [j for j in range(j0 + 1, j1) if j not in used_ja]
        if ens and jas and len(ens) == len(jas):
            pairs = list(zip(ens, jas))
            # 文字系统要对得上：日式罗马字 ↔ 平假名，外国名 ↔ 片假名；对不上的整段放弃（宁缺毋错），
            # 但这些日文名多半就是同一批人，不能再当"日文独有"补进去
            if all(script_compatible(flat[i]["name"], ja_list[j]["kana"]) for i, j in pairs):
                for i, j in pairs:
                    match[i] = j
                    used_ja.add(j)
                    flat[i]["ja_match"] = "positional"
            else:
                blocked.update(jas)
    for i, j in match.items():
        n, jd = flat[i], ja_list[j]
        n["ja"] = jd["kana"]
        if jd.get("kanji") and "kanji" not in n:
            n["kanji"] = jd["kanji"]
        if jd.get("note") and not n.get("note"):
            n["note"] = jd["note"]
        if jd.get("comment"):
            n["ja_comment"] = jd["comment"]
        n.setdefault("ja_match", "romaji")
    # 每节的日文职名：该节已对齐名字所属的日文职名里最常见的那个
    from collections import Counter
    sec_of = {}
    k = 0
    for s in sections:
        for _ in s["names"]:
            sec_of[k] = s
            k += 1
    for s in sections:
        roles = Counter(ja_list[match[i]]["role"] for i, n in enumerate(flat) if i in match and sec_of[i] is s and ja_list[match[i]]["role"])
        if roles and not s.get("ja_role"):
            s["ja_role"] = roles.most_common(1)[0][0]
    stats["ja_total"] = len(ja_list)
    stats["ja_matched"] = len(match)
    stats["ja_positional"] = sum(1 for n in flat if n.get("ja_match") == "positional")
    # 只在日文名单里出现的人（Bulbapedia 漏收）：按日文职名挂到对应的节，没有就在前一个节后新建一节；
    # 名字用假名转的罗马字并标记来源
    leftover, added = [], 0
    anchor_sec = {j: sec_of[i] for i, j in match.items()}
    by_ja_role = {}
    for s in sections:
        if s.get("ja_role"):
            by_ja_role.setdefault(s["ja_role"], s)
    last_sec = sections[0] if sections else None
    for j, jd in enumerate(ja_list):
        if j in anchor_sec:
            last_sec = anchor_sec[j]
            continue
        if j in blocked or is_company(jd["kana"]) or not JA_RE.search(jd["kana"]) or " " not in jd["kana"].strip() or last_sec is None:
            leftover.append(jd)
            continue
        fam, giv = jd["kana"].split(None, 1)
        d = {"name": f"{kana_to_romaji(giv).capitalize()} {kana_to_romaji(fam).capitalize()}", "name_source": "ja-only",
             "ja": jd["kana"], "ja_match": "ja-only"}
        if jd.get("kanji"):
            d["kanji"] = jd["kanji"]
        if jd.get("lead"):
            d["lead"] = jd["lead"]
        sec = by_ja_role.get(jd["role"])
        if sec is None:
            sec = {"path": [jd["role"]], "ja_role": jd["role"], "source": "ja-only", "names": []}
            sections.insert(sections.index(last_sec) + 1, sec)
            by_ja_role[jd["role"]] = sec
        sec["names"].append(d)
        last_sec = sec
        added += 1
    stats["ja_only_added"] = added
    return [{"kana": j["kana"], "role": j["role"], **({"kanji": j["kanji"]} if j.get("kanji") else {})} for j in leftover]


COMPANY_RE = re.compile(r"(株式会社|有限会社|かぶしき|かいしゃ|がいしゃ|ゆうげん|\b(?:CO\.?|LTD\.?|INC\.?|LLC|GMBH|CORP\.?|CORPORATION|COMPANY|STUDIOS?|LIMITED|K\.K\.|S\.A\.|S\.R\.L\.|PTE|PTY|B\.V\.)\b|\bPublished by\b)", re.I)
COMPANY_WORDS = re.compile(r"\b(Union|Federation|Association|Foundation|Council|Bureau|Committee|Department|Division|Laboratories|Sdn|Bhd|Technicians|Sect\.|Library|Testing|Blind|Braille|Studio|Club|Works|Digital|Entertainment|Sonority|Laboratory|Creatures|Nintendo|Freak|Chunsoft|Hudson|Jupiter|Ambrella|HAL|Bandai|Namco|Koei|Tecmo|ILCA|DeNA|Group|Team|Systems|Technolog\w*|Software|Games|Interactive|Media|Records|Agency|Productions?|Publishing|Design Office|Office|Project|Network|Solutions|Service|Center|Institute|University|Orchestra|Choir|Ensemble|Band)\b")


def is_company(name):
    return bool(COMPANY_RE.search(name)) or bool(COMPANY_WORDS.search(name)) or len(name.split()) > 6


def parse_corpus(slug):
    """游戏内原文 en/ja 同行对齐：非全大写的英文行是名字。返回 [{name, ja?, role, lead?}]"""
    en_f, ja_f = CORPUS_OUT / f"{slug}.en.txt", CORPUS_OUT / f"{slug}.ja.txt"
    if not en_f.exists():
        return []
    en = en_f.read_text(encoding="utf-8").splitlines()
    ja = ja_f.read_text(encoding="utf-8").splitlines() if ja_f.exists() else [""] * len(en)
    out, role = [], None
    for e, j in zip(en, ja):
        e, j = e.strip(), j.strip()
        if not e or e == "THE END" or e.startswith("Thank you") or e.startswith("[~") or e == "[NULL]":
            continue
        lead = None
        m = re.match(r"^(LEAD|LEADER|CHIEF|SUB[- ]?LEAD)\s*:\s*(.+)$", e, re.I)
        if m:
            lead, e = m.group(1).title(), m.group(2).strip()
            j = re.sub(r"^(リーダー|リード|チーフ)\s*[:：]?\s*", "", j)
        letters = re.sub(r"[^A-Za-z]", "", e)
        if letters and letters.isupper() and not lead:
            role = e
            continue
        d = {"name": e, "role": role}
        if j and JA_RE.search(j) and j != e:
            d["ja"] = j
        if lead:
            d["lead"] = lead
        out.append(d)
    return out


def cmd_parse():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for g in all_games():
        slug, en_title, ja_title, work, year, dev, note = g["slug"], g["title"], g["ja_title"], g["work"], g["year"], g["developer"], g["note"]
        f = WIKI_DIR / f"{slug}.wiki"
        if not f.exists():
            print(f"-- {slug}: 没有 wiki 文件，先 fetch", file=sys.stderr)
            continue
        sections, anomalies = parse_wiki(f.read_text(encoding="utf-8"))
        for s in sections:
            for n in s["names"]:
                if is_company(n["name"]):
                    n["kind"] = "company"
        stats = {}
        leftover = []
        jf = WIKI_DIR / f"{slug}.ja.wiki"
        if jf.exists():
            leftover = align_ja(sections, parse_ja_wiki(jf.read_text(encoding="utf-8")), stats)
        corpus = parse_corpus(slug)
        if corpus:  # 游戏内原文：补假名（SV/ZA 的日文 credits 是假名，其余是罗马字）
            readings = {norm(c["name"]): c["ja"] for c in corpus if c.get("ja")}
            for s in sections:
                for n in s["names"]:
                    r = readings.get(norm(n["name"]))
                    if r and "ja" not in n:
                        n["ja"] = r
                        n["ja_match"] = "corpus"
        total = sum(len(s["names"]) for s in sections)
        doc = {
            "slug": slug, "title": en_title, "work": work, "year": year, "developer": dev, "core": g["core"],
            "source": f"https://bulbapedia.bulbagarden.net/wiki/{en_title.replace(' ', '_')}",
            "count": total,
        }
        if ja_title:
            doc["source_ja"] = f"https://wiki.pokemonwiki.com/wiki/{ja_title.replace(' ', '_')}"
        if g.get("title_zh"):
            doc["title_zh"] = g["title_zh"]  # 外传的中文名（spinoffs.yml 手填）
        if note:
            doc["note"] = note
        if stats:
            doc["ja_alignment"] = stats
        if corpus:
            doc["corpus_count"] = len(corpus)
        doc["sections"] = sections
        if leftover:
            doc["ja_unmatched"] = leftover
        if anomalies:
            doc["anomalies"] = anomalies
        with (DATA_DIR / f"{slug}.yml").open("w", encoding="utf-8") as fh:
            fh.write(f"# 由 tools/build-credits.py parse 生成，来源 {doc['source']}" + (f" + {doc['source_ja']}" if ja_title else "") + "\n")
            yaml.safe_dump(doc, fh, allow_unicode=True, sort_keys=False, width=200)
        ja_msg = f"，日文对齐 {stats['ja_matched']}/{stats['ja_total']}（位置补齐 {stats['ja_positional']}，剩 {len(leftover)}）" if stats else ""
        print(f"{slug}: {len(sections)} 节 {total} 人{ja_msg}" + (f"，{len(anomalies)} 处异常" if anomalies else ""))


# ---------------------------------------------------------------- index

MERGES_FILE = ROOT / "archive" / "credits" / "merges.yml"


def load_merges():
    """merges: {错拼: 正拼}（按 norm 比较）；splits: [{name, role_match, suffix}] 把同罗马字的不同人按职务拆开。"""
    if not MERGES_FILE.exists():
        return {}, []
    d = yaml.safe_load(MERGES_FILE.read_text(encoding="utf-8")) or {}
    merges = {norm(a): norm(b) for a, b in (d.get("merges") or {}).items()}
    return merges, d.get("splits") or []


def cmd_index():
    people = {}
    merges, splits = load_merges()
    games = all_games()
    order = {g["slug"]: i for i, g in enumerate(games)}
    core = {g["slug"] for g in games if g["core"]}
    for g in games:
        slug, year = g["slug"], g["year"]
        f = DATA_DIR / f"{slug}.yml"
        if not f.exists():
            continue
        doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        for s in doc["sections"]:
            role = " / ".join(s["path"])
            for n in s["names"]:
                key = norm(n["name"])
                key = merges.get(key, key)
                for sp in splits:
                    if key == norm(sp["name"]) and re.search(sp["role_match"], role, re.I):
                        key = f"{key} ({sp['suffix']})"
                if not key or n.get("kind") == "company":
                    continue
                p = people.setdefault(key, {"key": key, "name": None, "variants": [], "links": [], "kanji": [], "kana": [], "credits": []})
                for fld, val in (("variants", n["name"]), ("links", n.get("link")), ("kanji", n.get("kanji")), ("kana", n.get("ja"))):
                    if fld == "kana" and val and not JA_RE.search(val):
                        continue  # 日文页用拉丁字母写的名字不是读法
                    if val and val not in p[fld]:
                        p[fld].append(val)
                c = {"game": slug, "year": year, "role": role, "_variant": n["name"]}
                if n.get("note"):
                    c["note"] = n["note"]
                if n.get("lead"):
                    c["lead"] = n["lead"]
                if s.get("ja_role"):
                    c["role_ja"] = s["ja_role"]
                p["credits"].append(c)
    # 罗马字拼法不同但 Bulbapedia 条目或汉字相同 → 同一人，合并
    def merge_by(field):
        seen = {}
        for key in list(people):
            p = people.get(key)
            if not p:
                continue
            for v in p[field]:
                if v.startswith("w:"):
                    continue
                if v in seen and seen[v] is not p:
                    q = seen[v]
                    for fld in ("variants", "links", "kanji", "kana"):
                        q[fld] += [x for x in p[fld] if x not in q[fld]]
                    q["credits"] += p["credits"]
                    q.setdefault("merged_from", []).append(key)
                    del people[key]
                    p = q
                    break
            for v in p[field]:
                seen.setdefault(v, p)
    merge_by("links")
    merge_by("kanji")
    for p in people.values():
        p["credits"].sort(key=lambda c: order[c["game"]])
        # 主显示名：出现最多的写法；Bulbapedia 条目名若也是其中一种写法则优先
        from collections import Counter
        freq = Counter(v for c in p["credits"] for v in [c.pop("_variant", None)] if v)
        p["name"] = (freq.most_common(1)[0][0] if freq else p["variants"][-1])
        for lk in p["links"]:
            if norm(lk) == norm(p["name"]) or lk in p["variants"]:
                p["name"] = lk
                break
        if p["key"].endswith(")"):
            p["name"] += " " + p["key"][p["key"].rindex("("):]
        p["games"] = sorted({c["game"] for c in p["credits"]}, key=order.get)
        p["core_games"] = [g for g in p["games"] if g in core]
        p["first"] = p["credits"][0]["year"]
        p["last"] = p["credits"][-1]["year"]
        for fld in ("variants", "links", "kanji", "kana"):
            if not p[fld]:
                del p[fld]
        if len(p.get("kanji", [])) > 1:
            p["flag"] = "多个汉字写法：可能是同罗马字的不同人"
    rows = sorted(people.values(), key=lambda p: (-len(p["core_games"]), -len(p["games"]), p["first"], p["name"]))
    with INDEX_FILE.open("w", encoding="utf-8") as fh:
        fh.write("# 由 tools/build-credits.py index 生成：历作 staff 每人一条（罗马字归一合并，variants / kanji 供核对同名异人）\n")
        yaml.safe_dump(rows, fh, allow_unicode=True, sort_keys=False, width=200)
    multi = sum(1 for p in rows if len(p["games"]) > 1)
    kanji = sum(1 for p in rows if p.get("kanji"))
    flagged = sum(1 for p in rows if p.get("flag"))
    print(f"index: {len(rows)} 人，{multi} 人参与 2 作以上，{kanji} 人有汉字，{flagged} 条疑似同名异人 → {INDEX_FILE.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["discover", "fetch", "parse", "index", "all"])
    ap.add_argument("--force", action="store_true", help="fetch 时覆盖已有 wiki 文件")
    a = ap.parse_args()
    if a.cmd == "discover":
        cmd_discover()
    if a.cmd in ("fetch", "all"):
        fetch_wiki(force=a.force)
        fetch_corpus()
    if a.cmd in ("parse", "all"):
        cmd_parse()
    if a.cmd in ("index", "all"):
        cmd_index()


if __name__ == "__main__":
    main()
