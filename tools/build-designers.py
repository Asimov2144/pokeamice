#!/usr/bin/env python3
"""宝可梦设计者页（/credits/designers/）的数据。

  python tools/build-designers.py [--report]

输入：
  archive/designers/gfworks-designer.html   gfworks「Pokémon Primary Designers」原页快照（抓取日期见 SNAPSHOT_DATE）
  archive/credits/index.yml                  历作 staff 名单（每人各作职务，tools/build-credits.py index）
  _data/people.yml                           人物登记表（credits_key ↔ 名单 key）
  _data/credits_games.yml                    作品中文名
  52poke species.lite.json                   宝可梦中 / 日 / 英名与全国图鉴号（--species，默认 P:/WEBSITE/.cache/52poke-out）
  App 精灵图                                 Pokeamice_app/public/pokemon-sprites/<id>.png（--sprites；地区形态用 PokeAPI 形态号）
输出：
  _data/pokemon_designers.yml                页面数据：原表 + 逐作名单核对 + 宝可梦中文名 + 站内已有的译文
  assets/img/pokemon-sprites/<id>.png        用到的精灵图

原表的「Gen N」是作者按各世代名单整理的；这里按本站名单逐作找"宝可梦设计"类职务重新核对，
两边不一致的格子在页面上分开标（原表有、名单没找到 / 名单有、原表没记），并列出名单里署名了宝可梦设计、
原表没收的人。改职务判定只动 is_design_role()；改世代分组只动 GENS。
"""
import argparse
import html
import re
import shutil
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "archive" / "designers" / "gfworks-designer.html"
SNAPSHOT_DATE = "2026-10-29"
SOURCE_URL = "https://gfworks.github.io/designer.html"
MIRROR_URL = "https://pokeamice.com/designers/"
INDEX = ROOT / "archive" / "credits" / "index.yml"
REGISTRY = ROOT / "_data" / "people.yml"
GAMES = ROOT / "_data" / "credits_games.yml"
OUT = ROOT / "_data" / "pokemon_designers.yml"
SPRITE_DIR = ROOT / "assets" / "img" / "pokemon-sprites"
SPRITE_URL = "/assets/img/pokemon-sprites/"

# 每个世代核对哪几作（海外版红·蓝是本地化名单，不另算；冠军 / Pokopia 没有新宝可梦设计）
GENS = [
    (1, ["red-green", "blue-jp", "yellow"]),
    (2, ["gold-silver", "crystal"]),
    (3, ["ruby-sapphire", "firered-leafgreen", "emerald"]),
    (4, ["diamond-pearl", "platinum", "heartgold-soulsilver"]),
    (5, ["black-white", "black2-white2"]),
    (6, ["x-y", "oras"]),
    (7, ["sun-moon", "usum", "lets-go"]),
    (8, ["sword-shield", "bdsp", "legends-arceus"]),
    (9, ["scarlet-violet", "area-zero", "legends-za"]),
]
SHORT = {
    "red-green": "红绿", "blue-jp": "蓝", "yellow": "皮卡丘", "gold-silver": "金银", "crystal": "水晶",
    "ruby-sapphire": "红蓝宝石", "firered-leafgreen": "火红叶绿", "emerald": "绿宝石", "diamond-pearl": "钻石珍珠",
    "platinum": "白金", "heartgold-soulsilver": "心金魂银", "black-white": "黑白", "black2-white2": "黑2白2",
    "x-y": "XY", "oras": "ΩRαS", "sun-moon": "日月", "usum": "究极日月", "lets-go": "Let's Go",
    "sword-shield": "剑盾", "bdsp": "晶灿明亮", "legends-arceus": "阿尔宙斯", "scarlet-violet": "朱紫",
    "area-zero": "零之秘宝", "legends-za": "Z-A",
}

# 名单索引里没合并上的同一人（片假名转写 / 错拼 / 头衔混进名字），这里并到正身上；
# 根治是加进 archive/credits/merges.yml 重跑 build-credits.py index
INDEX_ALIASES = {
    "jeimusu taanaa": "james tsurner",           # 黑2白2 ジェイムス ターナー
    "okubo tomuhiko": "okubo tomohiko",          # 黑2白2 Tomuhiko Ohkubo
    "direkutaa ken sugimori": "ken sugimori",    # X·Y「ディレクター すぎもり けん」
}
# 原表的拼写错误
NAME_FIX = {"Wobbufett": "Wobbuffet", "Foonguss": "Foongus"}
# 原表括注 → 中文
REMARK_ZH = {
    "w/ Yūsuke Ōmura": "与大村祐介合作",
    "or Ibe?": "也可能是井部真那",
    "her favorite": "她最喜欢的一只",
    "finalized design; original by 'female designer'": "定稿；原案出自一位「女性设计师」",
    "draft design, finished by Game Freak": "草案，由 Game Freak 定稿",
    "as part of a team": "团队合作",
}
# 地区形态 → PokeAPI 形态号（与 App 的 src/pokemonForms.ts 同一套）
REGIONAL = {
    "Alolan": ("阿罗拉", {26: 10100, 74: 10109, 75: 10110, 76: 10111, 88: 10112, 89: 10113, 103: 10114}),
    "Galarian": ("伽勒尔", {263: 10174, 264: 10175}),
    "Hisuian": ("洗翠", {58: 10229, 59: 10230, 215: 10235, 570: 10238, 571: 10239}),
    "Paldean": ("帕底亚", {128: 10250}),          # 斗战种；三个种类共用一格
}
SUPPLEMENT = ROOT / "archive" / "designers" / "supplement.yml"
ROLE_ZH = {"co": "合作", "idea": "构想", "draft": "初稿", "colors": "配色"}
# 原表出处 → 站内已收的同一篇（文件名不带 .md；只收确认是同一来源的）
SOURCE_POSTS = {
    3: "2009-09-04-interview-iwata-asks-hgss-chapter-1-red-green-mew",
    6: "2011-03-01-interview-eurogamer-masuda-sugimori-black-white-brains",
    8: "2010-09-10-interview-pokemon-peer-sugimori-ohmori-designers",
    13: "2013-10-24-interview-onm-xy-sugimori",
    14: "2018-07-26-interview-creators-of-pikachu",
    15: "2006-04-24-interview-gpara-2006-yoshida",
    17: "2014-02-14-interview-gameinformer-masuda-afterwords-xy",
    18: "2010-10-22-gamefreak-staff-204",
    19: "2011-02-21-scan-ndream-2011-04-bw-design-secrets-part2",
    20: "2011-03-21-scan-ndream-2011-05-bw-design-secrets-ex",
    21: "2011-03-05-interview-1up-black-white-how-pokemon-get-made",
    22: "2010-11-20-interview-nintendodream-201-sugimori-bw-characters",
    40: "2018-06-25-interview-funsproject-atsuko-nishida-shoko-nakagawa-character-design",
    41: "2019-11-20-interview-cit-kensaku-nabana-robotics",
    43: "2000-07-01-interview-nintendopower-gold-silver-roundtable",
}
# 原表把纸本 / 视频出处写成文字，这里补中文说明
SOURCE_ZH = {
    9: "Nintendo DREAM vol.187 访谈",
    19: "Nintendo DREAM vol.204（2011 年 4 月号）",
    20: "Nintendo DREAM vol.205（2011 年 5 月号）",
    21: "周刊 Fami通 No.1140（2010-11-11）「报道特集 宝可梦热卖的理由」",
    22: "Nintendo DREAM vol.201（2011 年 1 月号）",
    43: "Nintendo Power vol.134（2000 年 7 月）",
    52: "动画《宝可梦 起源》（2013）",
    54: "GAME FREAK 插画演示 第 1 集：杉森建 × Pulseman（YouTube）",
    71: "宝可梦集换式卡牌游戏 插画集",
    72: "宝可梦中心在线 My151 活动",
}


def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z ]", "", s).strip()


def romaji_keys(name):
    """长音的几种写法都试：Ōmura → omura / oomura / oumura / ohmura。"""
    keys = {norm(name)}
    for o, u in (("o", "u"), ("oo", "uu"), ("ou", "uu"), ("oh", "u")):
        keys.add(norm(name.replace("Ō", o.capitalize()).replace("ō", o).replace("ū", u)))
    return keys | {" ".join(reversed(k.split())) for k in keys}


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def parse_snapshot(src):
    overview = []
    for cell, rest in re.findall(r'<tr>\s*<td class="name">(.*?)</td>(.*?)</tr>', src, re.S):
        anchor = re.search(r'href="#([^"]*)"', cell)
        ja = re.search(r'<span lang="ja">([^<]*)', cell)
        en = text(re.sub(r"<span.*", "", cell, flags=re.S)).rstrip(" (")
        overview.append({
            "anchor": anchor.group(1) if anchor else "",
            "en": en,
            "ja": ja.group(1).strip() if ja else "",
            "gens": [c.strip() == "Y" for c in re.findall(r"<td>(.*?)</td>", rest)],
        })
    designers = {}
    block = src[src.index("<h1>Designers</h1>"):src.index("<h1>Sources</h1>")]
    for head, body in re.findall(r"<h2([^>]*)>.*?</h2>(.*?)(?=<h2|$)", block, re.S):
        hid = re.search(r'id="([^"]+)"', head)
        items = []
        for li in re.findall(r"<li>(.*?)</li>", body, re.S):
            name = text(li.split("<sup>")[0])
            refs = [int(n) for n in re.findall(r'href="#note(\d+)"', li)]
            remark = ""
            m = re.match(r"(.*?)\s*\((.*)\)\s*$", name)
            if m:
                name, remark = m.group(1), m.group(2)
            items.append({"name": name, "refs": refs, "remark": remark})
        designers[hid.group(1) if hid else "unknown-a"] = items
    sources = []
    for n, body in re.findall(r'<li id="note(\d+)">(.*?)</li>', src, re.S):
        links = []
        for u, lab in re.findall(r'<a href="([^"]+)">(.*?)</a>', body, re.S):
            lab = text(lab)
            if lab == u:          # 原表把网址本身当链接文字；页面上只显示域名 + 路径开头，存档链接另标
                bare = re.sub(r"^https?://web\.archive\.org/web/\d+[a-z_]*/", "", u)
                lab = re.sub(r"^https?://(www\.)?", "", bare)
                lab = lab if len(lab) <= 64 else lab[:61] + "…"
            link = {"url": u, "label": lab}
            if "web.archive.org/" in u:
                link["archived"] = True
            links.append(link)
        plain = text(re.sub(r"<a [^>]*>.*?</a>", " ", body, flags=re.S)).strip(" ()")
        sources.append({"n": int(n), "text": plain, "links": links})
    changelog = [{"date": d, "text": text(t)} for d, t in
                 re.findall(r'<time datetime="([^"]+)">[^<]*</time>\s*-\s*(.*?)</span>', src, re.S)]
    return overview, designers, sources, changelog


def is_design_role(role):
    """名单里的"宝可梦设计"：看职务路径的最后一段。参数 / 叫声 / 游戏设计 / 3D / 图标 / 协调 / 动作等都不算。"""
    seg = (role or "").split(" / ")[-1]
    if re.search(r"parameter|voice|game ?design|global link|world tournament|3-?d|icon|coordinat|version|movie|motion|effect|planning", seg, re.I):
        return False
    return bool(re.search(r"(pok[eé]mon|monster)s?\b.*design|concept art, pok[eé]mon", seg, re.I))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--species", default="P:/WEBSITE/.cache/52poke-out/species.lite.json")
    ap.add_argument("--sprites", default="P:/WEBSITE/pokeamice/Pokeamice_app/public/pokemon-sprites")
    # App 那套里没有的形态（如阿罗拉椰蛋树 10114），从 PokeAPI/sprites 同一套补到这里
    ap.add_argument("--extra-sprites", default="P:/WEBSITE/.cache/designers-research/sprites")
    ap.add_argument("--report", action="store_true", help="只打印核对结果，不写文件")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    src = SNAPSHOT.read_text(encoding="utf-8")
    overview, lists, sources, changelog = parse_snapshot(src)
    index = yaml.safe_load(INDEX.read_text(encoding="utf-8"))
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    games = {g["slug"]: g for g in yaml.safe_load(GAMES.read_text(encoding="utf-8"))}
    import json
    species = json.loads(Path(args.species).read_text(encoding="utf-8"))
    by_en = {s["name"]["en"]: s for s in species}

    by_kanji, by_rom = defaultdict(list), defaultdict(list)
    for p in index:
        for k in p.get("kanji") or []:
            by_kanji[re.sub(r"\s", "", k)].append(p)
        for v in (p.get("variants") or []) + [p["name"]]:
            for k in romaji_keys(v):
                by_rom[k].append(p)
    people_by_key = {p["credits_key"]: p for p in registry if p.get("credits_key")}
    gen_of = {slug: n for n, slugs in GENS for slug in slugs}
    alias_credits = defaultdict(list)
    for p in index:
        if p["key"] in INDEX_ALIASES:
            alias_credits[INDEX_ALIASES[p["key"]]] += p.get("credits", [])

    def credits_of(p):
        return p.get("credits", []) + alias_credits.get(p["key"], [])

    def design_credits(p):
        out = defaultdict(list)
        for c in credits_of(p):
            if c["game"] in gen_of and is_design_role(c.get("role")):
                out[c["game"]].append(c)
        return out

    def find_entry(en, ja):
        cands = by_kanji.get(re.sub(r"[\s\-]", "", ja), [])
        if not cands:
            for k in romaji_keys(en):
                cands = by_rom.get(k, [])
                if cands:
                    break
        uniq = list({id(p): p for p in cands}.values())
        # 同名的几条里取署名过宝可梦设计的那条，再取署名最多的
        uniq.sort(key=lambda p: (-len(design_credits(p)), -len(p.get("credits", []))))
        return uniq[0] if uniq else None, len(uniq)

    def resolve(name):
        """英文名（可带形态前缀）→ 中日名、图鉴号、精灵图号。"""
        m = re.match(r"(Mega|Ultra|Alolan|Galarian|Hisuian|Paldean|Gigantamax|Shadow) (.+?)( [XY])?$", name)
        base = m.group(2) if m else name
        sp = by_en.get(base)
        if not sp:
            raise SystemExit(f"宝可梦名对不上 52poke：{name!r}")
        nd = sp["ndex"]
        zh, ja, form_zh, sprite = sp["name"]["zh"], sp["name"]["ja"], "", nd
        if m:
            kind, xy = m.group(1), (m.group(3) or "").strip()
            if kind == "Mega":
                zh, ja, form_zh = f"超级{zh}{xy}", f"メガ{ja}{xy}", "超级进化"
            elif kind == "Ultra":
                zh, ja, form_zh = f"究极{zh}", f"ウルトラ{ja}", "究极"
            elif kind == "Gigantamax":
                zh, ja, form_zh = f"超极巨化{zh}", f"{ja}（キョダイマックスのすがた）", "超极巨化"
            elif kind == "Shadow":
                zh, ja, form_zh = f"暗影{zh}", f"ダーク{ja}", "暗影"
            else:
                region, ids = REGIONAL[kind]
                zh, form_zh = f"{region}{zh}", f"{region}的样子"
                ja = f"{ja}（{ {'Alolan': 'アローラ', 'Galarian': 'ガラル', 'Hisuian': 'ヒスイ', 'Paldean': 'パルデア'}[kind]}のすがた）"
                sprite = ids[nd]
        out = {"en": name, "zh": zh, "ja": ja, "ndex": nd, "sprite": sprite}
        if form_zh:
            out["form"] = form_zh
        return out

    def pokemon(item):
        name = NAME_FIX.get(item["name"], item["name"])
        remark = item["remark"]
        unsure = remark == "?" or not item["refs"]
        out = dict(resolve(name), refs=item["refs"])
        if remark and remark != "?":
            if remark not in REMARK_ZH:
                raise SystemExit(f"原表括注没有中文：{remark!r}")
            out["remark"] = REMARK_ZH[remark]
            out["remark_en"] = remark
        if unsure:
            out["unsure"] = True
        return out

    designers, report = [], []
    for row in overview:
        entry, n_hits = find_entry(row["en"], row["ja"])
        if not entry:
            raise SystemExit(f"名单里找不到：{row['en']} {row['ja']}")
        dc = design_credits(entry)
        person = people_by_key.get(entry["key"])
        gens = []
        for (n, slugs), gf in zip(GENS, row["gens"]):
            credited = [{"game": s, "short": SHORT[s], "title": games[s]["title_zh"],
                         "role": dc[s][0].get("role", "").split(" / ")[-1], "role_ja": dc[s][0].get("role_ja") or ""}
                        for s in slugs if dc.get(s)]
            cell = {"gen": n, "gf": gf, "games": credited}
            if gf and not credited:
                other = []
                for c in credits_of(entry):
                    if c["game"] in slugs:
                        r = c.get("role", "").split(" / ")[-1]
                        if r not in [o["role"] for o in other]:
                            other.append({"game": c["game"], "short": SHORT[c["game"]], "role": r})
                cell["other"] = other[:3]
            cell["state"] = ("both" if gf and credited else "gf" if gf else "credits" if credited else "")
            gens.append(cell)
            if cell["state"] in ("gf", "credits"):
                report.append(f"{row['en']:24} Gen{n} {cell['state']:8} {[c['short'] for c in credited] or cell.get('other')}")
        # 原表只给有宝可梦清单的人设了锚点；其余用罗马字，姓氏撞车（两位吉田 / 藤原 / 吉川）也靠这个分开
        anchor = row["anchor"] or norm(row["en"]).replace(" ", "-")
        d = {
            "id": anchor,
            "en": row["en"],
            "ja": row["ja"].replace("-", "").strip(),
            "name": person["name"] if person else row["ja"].replace("-", "").strip(),
            "credits_key": entry["key"],
            "gens": gens,
            "pokemon": [pokemon(i) for i in lists.get(row["anchor"], [])] if row["anchor"] else [],
        }
        if person:
            d["person"] = person["slug"]
            if person.get("avatar"):
                d["avatar"] = person["avatar"]
        if n_hits > 1:
            report.append(f"{row['en']:24} 名单同名 {n_hits} 条，取 {entry['key']} {entry.get('kanji')}")
        designers.append(d)

    # 名单里署名了宝可梦设计、原表没收的人
    listed = {d["credits_key"] for d in designers}
    extra = []
    for p in index:
        if p["key"] in listed or p["key"] in INDEX_ALIASES:
            continue
        dc = design_credits(p)
        if not dc:
            continue
        person = people_by_key.get(p["key"])
        by_gen = defaultdict(list)
        for s in dc:
            by_gen[gen_of[s]].append({"game": s, "short": SHORT[s], "title": games[s]["title_zh"],
                                      "role": dc[s][0].get("role", "").split(" / ")[-1]})
        e = {"en": p["name"], "ja": (p.get("kanji") or [""])[0], "credits_key": p["key"],
             "gens": [{"gen": n, "games": by_gen.get(n, [])} for n, _ in GENS]}
        if person:
            e["person"] = person["slug"]
            e["name"] = person["name"]
        extra.append(e)
    extra.sort(key=lambda e: (min(g["gen"] for g in e["gens"] if g["games"]), e["en"]))

    unknown = [pokemon(i) for i in lists.get("unknown-a", [])]

    # 补充条目（archive/designers/supplement.yml）：排在各人原表条目之后，出处编号 S1、S2…（原表出处写 gf<N> 的直接用 N）
    supp = yaml.safe_load(SUPPLEMENT.read_text(encoding="utf-8"))
    by_name = {d["en"]: d for d in designers}
    supp_sources, sid = [], {}
    for e in supp["entries"]:
        d = by_name.get(e["designer"])
        if not d:
            raise SystemExit(f"补充条目的设计者不在原表里：{e['designer']}")
        refs = []
        for k in e["sources"]:
            if re.fullmatch(r"gf\d+", k):
                refs.append(int(k[2:]))
                continue
            if k not in supp["sources"]:
                raise SystemExit(f"补充条目引用了没登记的出处：{k}")
            if k not in sid:
                sid[k] = f"S{len(sid) + 1}"
                s = dict(supp["sources"][k], id=sid[k])
                if s.get("post") and not (ROOT / "_posts" / f"{s['post']}.md").exists():
                    raise SystemExit(f"补充出处 {k} 对应的帖子不存在：{s['post']}")
                supp_sources.append(s)
            refs.append(sid[k])
        p = dict(resolve(f"{e['form']} {e['pokemon']}" if e.get("form") else e["pokemon"]), refs=refs, supp=True)
        if e.get("role") in ROLE_ZH:
            p["role"] = ROLE_ZH[e["role"]]
        if e.get("remark"):
            p["remark"] = e["remark"]
        if e.get("unsure"):
            p["unsure"] = True
        d["pokemon"].append(p)
    for a in supp.get("annotate", []):
        hit = [p for p in by_name[a["designer"]]["pokemon"] if p["en"] == a["pokemon"] and not p.get("supp")]
        if not hit:
            raise SystemExit(f"annotate 对不上原表条目：{a}")
        hit[0]["note"] = a["remark"]

    used = defaultdict(list)          # 出处 → 引了它的宝可梦（出处列表里反查用）
    for d in designers:
        for p in d["pokemon"]:
            for n in p["refs"]:
                used[n].append({"zh": p["zh"], "designer": d["id"]})
    for s in sources:
        s["used"] = used.get(s["n"], [])
        if s["n"] in SOURCE_POSTS:
            s["post"] = SOURCE_POSTS[s["n"]]
            if not (ROOT / "_posts" / f"{s['post']}.md").exists():
                raise SystemExit(f"出处 {s['n']} 对应的帖子不存在：{s['post']}")
        if s["n"] in SOURCE_ZH:
            s["zh"] = SOURCE_ZH[s["n"]]
    for s in supp_sources:
        s["used"] = used.get(s["id"], [])

    # 按图鉴号的一览：同一只宝可梦（含形态）一行，列出设计者
    dex = []
    for d in designers:
        for p in d["pokemon"]:
            dex.append(dict(p, designer=d["id"], designer_name=d["name"]))
    for p in unknown:
        dex.append(dict(p, designer="unknown-a", designer_name="不明人物 A"))
    dex.sort(key=lambda p: (p["ndex"], p["sprite"]))

    if args.report:
        print(f"{len(designers)} 位设计者、{sum(len(d['pokemon']) for d in designers)} 只宝可梦、{len(sources)} 条出处")
        print("\n".join(report))
        print(f"\n名单里有宝可梦设计署名、原表没收：{len(extra)} 人")
        for e in extra:
            print("  ", e["en"], e["ja"], e.get("person", ""), [g["short"] for x in e["gens"] for g in x["games"]])
        print(f"\n补充条目 {len(supp['entries'])} 条、补充出处 {len(supp_sources)} 条、原表条目加注 {len(supp.get('annotate', []))} 条")
        return

    sprites = sorted({p["sprite"] for p in dex})
    SPRITE_DIR.mkdir(parents=True, exist_ok=True)
    missing = []
    for num in sprites:
        f = next((Path(d) / f"{num}.png" for d in (args.sprites, args.extra_sprites) if (Path(d) / f"{num}.png").exists()), None)
        if f:
            shutil.copyfile(f, SPRITE_DIR / f.name)
        else:
            missing.append(num)
    if missing:
        raise SystemExit(f"缺精灵图：{missing}")

    states = [c["state"] for d in designers for c in d["gens"]]
    data = {
        "source": {"name": "Pokémon Primary Designers", "url": SOURCE_URL, "mirror": MIRROR_URL,
                   "fetched": SNAPSHOT_DATE, "updated": changelog[0]["date"] if changelog else ""},
        # 世代表的格子数：两边一致 / 只有名单 / 只有原表（页面导语和图例按这个说话）
        "cells": {s: states.count(s) for s in ("both", "credits", "gf")},
        "supp_count": len(supp["entries"]),
        "supp_sources": supp_sources,
        "rejected": supp.get("rejected", []),
        "sprite_base": SPRITE_URL,
        "gens": [{"gen": n, "games": [{"game": s, "short": SHORT[s], "title": games[s]["title_zh"]} for s in slugs]}
                 for n, slugs in GENS],
        "designers": designers,
        "unknown": unknown,
        "extra": extra,
        "dex": dex,
        "sources": sources,
        "changelog": changelog,
    }
    header = "# 由 tools/build-designers.py 生成：宝可梦设计者（gfworks 原表 + 本站名单核对），别手改\n"
    OUT.write_text(header + yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8", newline="\n")
    print(f"写入 {OUT.relative_to(ROOT)}：{len(designers)} 人、{len(dex)} 只、{len(extra)} 位名单补充；精灵图 {len(sprites)} 张")


if __name__ == "__main__":
    main()
