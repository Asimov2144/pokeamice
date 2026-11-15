#!/usr/bin/env python3
"""作曲家名单页（/credits/composers/）的数据。

  python tools/build-composers.py [--report]

输入：
  archive/credits/index.yml    历作 staff 名单（每人各作职务，tools/build-credits.py index）
  _data/people.yml             人物登记表（credits_key ↔ 名单 key：有人物页的人才有链接和头像）
  _data/credits_games.yml      作品中文名、年份、是否核心作品
  assets/data/credits-staff.json  核心作品的世代（gens / games[].gen）
输出：
  _data/composers.yml          页面数据：按人、按作品两套

只看名单里的职务字样，不碰别的来源：
  A  作曲·编曲   Composer(s) / Music / Music Composition / Arrangement / Original Music …
                 （含音乐总监、Music Leader；中日文职务里有「作曲」「編曲」「音楽」的也算）
  B  演奏·演唱·录音   Musician / 乐器 / Vocals / Ending Theme（多是演唱者）/ Music Recording Engineer / Mastering …
  职务只看最后一段（前面是部门或公司名）。
  其余的音响职务（Sound、Sound Effects、Sound Director、Sound Programming、Voice …）不算：
  这些名单只署「Sound」的作品（多数第四世代以后的核心作），作曲和音效没法在名单上分开，
  页面上只在方法说明里点出来，并链到各作名单自己去看。
改职务判定只动 tier_of()；改作品分组只动 group_of()。
"""
import argparse
import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "archive" / "credits" / "index.yml"
REGISTRY = ROOT / "_data" / "people.yml"
GAMES = ROOT / "_data" / "credits_games.yml"
STAFF_JSON = ROOT / "assets" / "data" / "credits-staff.json"
OUT = ROOT / "_data" / "composers.yml"

# B 先于 A：制作类的 "Music …" 不是作曲
B_FIRST = re.compile(r"music\W+(recording|preparation|programm|supervis|copy|edit|data|support|engineer|production\s+coord|coordinat)", re.I)
A_PAT = re.compile(
    r"compos|arrang|original\s+music|musical\s+score|battle\s+music"
    r"|(^|\W)music(\W|$)|作曲|編曲|音楽", re.I)
B_PAT = re.compile(
    r"musician|ending\s+theme|main\s+theme|guitar|violin|cello|flute|harmonica|mandolin|\bbass\b|recorder|piano|drum|vocal|"
    r"mastering|mixing|(music|sound|vocal)\s+recording|recording\s*&|演奏|歌", re.I)
SKIP = re.compile(r"thanks|special|voice", re.I)
CRED_PREFIX = re.compile(r"^original song performed by:\s*", re.I)   # 名单里把职务和人名连在一起写的残片


def tier_of(role, role_ja=""):
    """'A' 作曲·编曲、'B' 演奏·演唱·录音、'' 不算。"""
    # 只看最后一段（具体职务）：前面几段是部门或公司，「Music & Sound Effect / SPICA MUSICA」不是作曲署名
    r = html.unescape(role or "").split(" / ")[-1].strip()
    j = (role_ja or "").split(" / ")[-1].strip()
    if SKIP.search(r) and not A_PAT.search(r):
        return ""
    if B_FIRST.search(r):
        return "B"
    if A_PAT.search(r) or re.search(r"作曲|編曲|音楽", j):
        return "A"
    if B_PAT.search(r):
        return "B"
    return ""


def short_role(role):
    """职务串里去掉前面的部门，只留最后一段，给提示用。"""
    return html.unescape(role).split(" / ")[-1].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="只打印概况，不写文件")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    index = yaml.safe_load(INDEX.read_text(encoding="utf-8"))
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    games = {g["slug"]: g for g in yaml.safe_load(GAMES.read_text(encoding="utf-8"))}
    staff = json.loads(STAFF_JSON.read_text(encoding="utf-8"))
    gen_of = {g["slug"]: g["gen"] for g in staff["games"]}
    gen_names = staff["gens"]
    by_key = {p["credits_key"]: p for p in registry if p.get("credits_key")}

    def group_of(slug):
        n = gen_of.get(slug)
        return (int(n), gen_names[str(n)]) if n else (99, "外传与其他")

    people = []
    seen = {}
    for e in index:
        mine = {}
        for c in e.get("credits", []):
            g = games.get(c["game"])
            if not g:
                continue
            t = tier_of(c.get("role"), c.get("role_ja"))
            if not t:
                continue
            # 同一作里 A 压过 B；同一作同一职务只记一次
            cur = mine.get(c["game"])
            role = short_role(c.get("role") or "")
            if cur is None or (cur["tier"] == "B" and t == "A"):
                mine[c["game"]] = {"game": c["game"], "tier": t, "roles": [role]}
            elif cur["tier"] == t and role not in cur["roles"]:
                cur["roles"].append(role)
        if not mine:
            continue
        en_name = CRED_PREFIX.sub("", e["name"])
        reg = by_key.get(e["key"])
        kanjis = e.get("kanji") or []
        # 一个人名单里有好几个汉字写法时（日文名单把同一人的别名署在一起），不猜哪个对：罗马字作主名，汉字全列
        kanji = kanjis[0] if len(kanjis) == 1 else ""
        d = {
            "id": re.sub(r"[^a-z0-9]+", "-", e["key"]).strip("-"),
            "name": (reg or {}).get("name") or kanji or e["name"],
            "en": en_name,
            "credits_key": e["key"],
            "games": [],
        }
        if kanjis:
            d["ja"] = " / ".join(kanjis)
        if reg:
            d["person"] = reg["slug"]
            if reg.get("avatar"):
                d["avatar"] = reg["avatar"]
        for slug, m in mine.items():
            g = games[slug]
            d["games"].append({"game": slug, "title": g.get("title_zh") or g["title"], "year": g["year"],
                               "tier": m["tier"], "role": " · ".join(m["roles"][:3]),
                               "gen": group_of(slug)[0], "core": bool(g.get("core"))})
        # 同名（去掉残片前缀、不分大小写）的两条合成一人
        twin = seen.get(en_name.lower())
        if twin is not None:
            have = {x["game"]: x for x in twin["games"]}
            for x in d["games"]:
                if x["game"] not in have:
                    twin["games"].append(x)
                elif have[x["game"]]["tier"] == "B" and x["tier"] == "A":
                    twin["games"][twin["games"].index(have[x["game"]])] = x
            if reg and not twin.get("person"):
                twin["person"] = reg["slug"]; twin["name"] = reg["name"]
            continue
        seen[en_name.lower()] = d
        people.append(d)
    for d in people:
        d["games"].sort(key=lambda x: (x["year"], x["game"]))
        a = [x for x in d["games"] if x["tier"] == "A"]
        d["tier"] = "A" if a else "B"
        d["n"] = len(a) if a else len(d["games"])
        d["first"], d["last"] = d["games"][0]["year"], d["games"][-1]["year"]

    # 按署名作品数、再按最早年份排；B 只有演奏录音的放后面
    composers = sorted((p for p in people if p["tier"] == "A"), key=lambda p: (-p["n"], p["first"], p["en"]))
    others = sorted((p for p in people if p["tier"] == "B"), key=lambda p: (-p["n"], p["first"], p["en"]))

    # 按作品：每作的作曲名单（A）和演奏录音（B）
    by_game = defaultdict(lambda: {"a": [], "b": []})
    for p in people:
        for x in p["games"]:
            by_game[x["game"]]["a" if x["tier"] == "A" else "b"].append(
                {"name": p["name"], "person": p.get("person", ""), "role": x["role"]})
    groups = defaultdict(list)
    for slug, v in by_game.items():
        g = games[slug]
        gi = group_of(slug)
        groups[gi].append({"game": slug, "title": g.get("title_zh") or g["title"], "year": g["year"],
                           "composers": v["a"], "musicians": v["b"]})
    by_game_out = []
    for (n, label), items in sorted(groups.items()):
        items.sort(key=lambda x: (x["year"], x["game"]))
        by_game_out.append({"gen": n, "label": label, "games": items})

    n_games = len({x["game"] for p in composers for x in p["games"] if x["tier"] == "A"})
    out = {
        "counts": {"composers": len(composers), "others": len(others), "games_with_a": n_games,
                   "games_total": len(games),
                   "linked": sum(1 for p in composers if p.get("person"))},
        "composers": composers,
        "others": others,
        "by_game": by_game_out,
    }
    print(f"作曲·编曲 {len(composers)} 人（{out['counts']['linked']} 人有人物页）· {n_games}/{len(games)} 部作品有作曲署名 · 只有演奏/录音 {len(others)} 人")
    if args.report:
        for p in composers[:40]:
            print(f"  {p['n']:>2}  {p['name']} ({p['en']})  {p['first']}–{p['last']}  {'→' + p['person'] if p.get('person') else ''}")
        return
    header = "# 由 tools/build-composers.py 生成：作曲·编曲名单（只看 staff 名单里的职务字样）。不要手改。\n"
    OUT.write_text(header + yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8", newline="\n")
    print("写入", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
