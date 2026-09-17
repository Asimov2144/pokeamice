#!/usr/bin/env python3
"""把 staff 名单接进站内（阶段 D）。跑完再跑 `python tools/build-people.py pages` 重生成人物页。

  python tools/build-credits-site.py

做的事：
  1. 名单里的人 ↔ _data/people.yml 登记表：按罗马字别名 / 汉字对上的，登记表条目加 credits_key；
     对不上的、且够"核心 staff"门槛（≥5 部核心作品，或任 lead / section director / director）的人，
     以 kind: staff 追加进登记表（name 用汉字，没有就用罗马字；slug = 姓-名）。
  2. _data/credits_games.yml      每作元数据（含中文名、人数、来源链接）
  3. _data/credits_people.yml     有人物页的人 → 各作职务（slug 作键，人物页「参与作品」栏用）
  4. _pages/credits/index.md      名单总览；_pages/credits/<slug>.md 每作名单（HTML 在这里渲染好，不走 Liquid）；
     _pages/credits/staff.md      全体核心 staff 总表（客户端 JS 读 assets/data/credits-staff.json）
门槛和分类规则与 tools/analyze-credits.py 一致（直接读它的 design/credits-analysis/people.json）。
"""
import html
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "archive" / "credits" / "index.yml"
ANALYSIS = ROOT / "design" / "credits-analysis"
GAMES_DIR = ROOT / "_data" / "credits"
REGISTRY = ROOT / "_data" / "people.yml"
PAGES = ROOT / "_pages" / "credits"
ASSETS = ROOT / "assets" / "data"

# 核心作品里没有对应站内 works 名的中文名
ZH_TITLES = {
    "red-blue": "宝可梦 红·蓝（海外版）", "box": "宝可梦盒子 红宝石·蓝宝石", "dream-radar": "宝可梦AR搜寻器",
    "area-zero": "宝可梦 朱·紫 零之秘宝", "champions": "Pokémon Champions", "legends-za": "Pokémon LEGENDS Z-A",
}
CAT_ZH = {"Dir": "总监/制作人", "Plan": "企划", "Prog": "程序", "Art": "美术", "Sound": "音乐", "Mgmt": "管理/协调",
          "Debug": "调试", "Loc/QA": "本地化/海外QA", "Thanks": "特别感谢", "Other": "其他"}
RANK_MARK = {0: "", 1: "*", 2: "^", 3: "!", 4: "!!"}
# 总表列头的短标签 + 世代分组（列底色按世代交替，表头加世代行）
ABBR = {"red-green": "红绿", "blue-jp": "蓝", "yellow": "皮卡丘", "red-blue": "红蓝海外", "gold-silver": "金银", "crystal": "水晶",
        "ruby-sapphire": "RS", "box": "Box", "firered-leafgreen": "FRLG", "emerald": "绿宝石", "diamond-pearl": "DP", "platinum": "白金",
        "heartgold-soulsilver": "HGSS", "black-white": "BW", "black2-white2": "BW2", "dream-radar": "AR", "x-y": "XY", "oras": "ORAS",
        "sun-moon": "SM", "usum": "USUM", "lets-go": "LGPE", "sword-shield": "剑盾", "bdsp": "BDSP", "legends-arceus": "阿尔宙斯",
        "scarlet-violet": "朱紫", "area-zero": "零之秘宝", "legends-za": "Z-A", "pokopia": "Pokopia", "champions": "Champions"}
GEN = {"red-green": 1, "blue-jp": 1, "yellow": 1, "red-blue": 1, "gold-silver": 2, "crystal": 2, "ruby-sapphire": 3, "box": 3, "firered-leafgreen": 3,
       "emerald": 3, "diamond-pearl": 4, "platinum": 4, "heartgold-soulsilver": 4, "black-white": 5, "black2-white2": 5, "dream-radar": 5,
       "x-y": 6, "oras": 6, "sun-moon": 7, "usum": 7, "lets-go": 7, "sword-shield": 8, "bdsp": 8, "legends-arceus": 8,
       "scarlet-violet": 9, "area-zero": 9, "legends-za": 9, "pokopia": 9, "champions": 9}
GEN_LABEL = {1: "第一世代", 2: "第二世代", 3: "第三世代", 4: "第四世代", 5: "第五世代", 6: "第六世代", 7: "第七世代", 8: "第八世代", 9: "第九世代"}
RANK_ZH = {1: "lead", 2: "section/art director", 3: "director/producer", 4: "executive producer"}
JA_RE = re.compile(r"[぀-ヿ一-鿿]")


def norm(name):
    """与 build-credits.norm 相同的归一，用来对登记表别名"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bc", ROOT / "tools" / "build-credits.py")
    bc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bc)
    globals()["norm"] = bc.norm
    return bc.norm(name)


# 日本新字体 ↔ 简体：只放登记表里实际会遇到、且一对一的字
JP2ZH = str.maketrans("増順澤沢齋斉濱浜邊辺藝櫻桜國廣廷實緒繩縄關関鐵鉄鹽塩學学號号鬪闘藏蔵祿禄德徳傳伝壽寿豐豊寶宝榮栄濕湿獨独團団圓円辯弁寫写體体豫予與与劇剧點点黨党樂楽發発變変齒歯續続讀読圖図賣売惠恵榘",
                      "增顺泽泽斋齐滨滨边边艺樱樱国广廷实绪绳绳关关铁铁盐盐学学号号斗斗藏藏禄禄德德传传寿寿丰丰宝宝荣荣湿湿独独团团圆圆辩辩写写体体预予与与剧剧点点党党乐乐发发变变齿齿续续读读图图卖卖惠惠榘")


def zh_forms(s):
    return {s, s.translate(JP2ZH)}


def load_games():
    games = {}
    for f in GAMES_DIR.glob("*.yml"):
        d = yaml.safe_load(f.read_text(encoding="utf-8"))
        games[d["slug"]] = d
    return games


def game_title_zh(g):
    if g.get("work"):
        return g["work"]
    if g["slug"] in ZH_TITLES:
        return ZH_TITLES[g["slug"]]
    if g.get("title_zh"):
        return g["title_zh"]
    return g["title"].replace("Staff of ", "")


def slug_for(name_roman, taken):
    suffix = re.findall(r"\(([^)]+)\)", name_roman)  # 「Hiro Nakamura (NOA)」→ nakamura-hiro-noa
    base_name = re.sub(r"\([^)]*\)", "", name_roman)
    parts = re.sub(r"[^A-Za-z ]", "", unicodedata.normalize("NFKD", base_name)).lower().split()
    if not parts:
        return None
    base = "-".join(parts[-1:] + parts[:-1]) if len(parts) > 1 else parts[0]  # 姓-名
    if suffix:
        base += "-" + re.sub(r"[^a-z0-9]+", "-", suffix[0].lower()).strip("-")
    slug, i = base, 2
    while slug in taken:
        slug, i = f"{base}-{i}", i + 1
    return slug


def main():
    games = load_games()
    people = yaml.safe_load(INDEX.read_text(encoding="utf-8"))
    analysis = {p["name"]: p for p in json.loads((ANALYSIS / "people.json").read_text(encoding="utf-8"))}
    ginfo = json.loads((ANALYSIS / "games.json").read_text(encoding="utf-8"))
    core_order = ginfo["order"]
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or []

    # ---- 1. 对登记表
    by_roman, by_kanji = {}, {}
    for e in registry:
        if e.get("kind") in ("character", "figure"):
            continue
        for a in [e["name"]] + (e.get("aliases") or []):
            if re.search(r"[A-Za-z]", a) and not JA_RE.search(a):
                by_roman[norm(a)] = e
            elif JA_RE.search(a):
                for f in zh_forms(a):
                    by_kanji[f] = e
    # 上次追加的 staff 条目若在索引里已不存在（错拼被合并、被判成公司），删掉；登记表原有条目只清掉失效的 credits_key
    keys = {p["key"] for p in people}
    stale = [e for e in registry if e.get("kind") == "staff" and e.get("credits_key") not in keys]
    for e in stale:
        registry.remove(e)
    for e in registry:
        if e.get("credits_key") and e["credits_key"] not in keys:
            del e["credits_key"]
    if stale:
        print(f"删掉失效的 staff 条目 {len(stale)}：{', '.join(e['name'] for e in stale)}")
    matched, taken = {}, {e["slug"] for e in registry}
    for e in registry:
        if e.get("credits_key"):
            matched[e["credits_key"]] = e
    for p in people:
        if p["key"] in matched:
            continue
        hit = None
        for v in p.get("variants", []) + p.get("links", []):
            hit = by_roman.get(norm(v))
            if hit:
                break
        if not hit:
            for k in p.get("kanji", []):
                for f in zh_forms(k):
                    hit = by_kanji.get(f)
                    if hit:
                        break
                if hit:
                    break
        if hit and not hit.get("credits_key"):
            hit["credits_key"] = p["key"]
            matched[p["key"]] = hit
    print(f"登记表里对上 {len(matched)} 人")

    # 核心 staff 门槛 → 追加登记
    by_key = {p["key"]: p for p in people}

    def fill_staff_entry(e, p):
        roman = p["name"]
        kanji = (p.get("kanji") or [None])[0]
        aliases = []
        for v in [roman] + p.get("variants", []) + (p.get("kana") or []) + ([kanji] if kanji else []):
            if v and v not in aliases and v != (kanji or roman):
                aliases.append(v)
        e["name"] = kanji or roman
        e["aliases"] = aliases
        if p.get("links"):
            e["bulbapedia"] = p["links"][0]
        elif "bulbapedia" in e:
            del e["bulbapedia"]

    added = 0
    for p in people:
        if p["key"] in matched or not p.get("core_games"):
            continue
        a = analysis.get(p["name"])
        if not a:
            continue
        # 门槛：≥5 部核心作品，或在 Game Freak 自己开发的作品里任 lead 以上（BDSP 的 ILCA、Pokopia 的 Koei Tecmo 领队不算）
        gf_rank = max((a["primary"][g]["rank"] for g in a["core_games"] if games[g].get("developer") == "Game Freak"), default=0)
        if len(a["core_games"]) < 5 and gf_rank < 1:
            continue
        slug = slug_for(p["name"], taken)
        if not slug:
            continue
        taken.add(slug)
        e = {"name": None, "slug": slug, "kind": "staff", "credits_key": p["key"]}
        fill_staff_entry(e, p)
        registry.append(e)
        matched[p["key"]] = e
        added += 1
    print(f"追加 kind: staff {added} 人")
    # 已有的 staff 条目：名字/别名是从索引派生的，每次刷新（手改过的加 pinned: true 就不动）；不再够门槛的删掉
    def meets(p):
        a = analysis.get(p["name"])
        if not a or not a["core_games"]:
            return False
        gf_rank = max((a["primary"][g]["rank"] for g in a["core_games"] if games[g].get("developer") == "Game Freak"), default=0)
        return len(a["core_games"]) >= 5 or gf_rank >= 1
    dropped = [e for e in registry if e.get("kind") == "staff" and not e.get("pinned") and not meets(by_key[e["credits_key"]])]
    for e in dropped:
        registry.remove(e)
        matched.pop(e["credits_key"], None)
    if dropped:
        print(f"不够门槛、删掉的 staff 条目 {len(dropped)}")
    for e in registry:
        if e.get("kind") == "staff" and not e.get("pinned"):
            fill_staff_entry(e, by_key[e["credits_key"]])
    header = REGISTRY.read_text(encoding="utf-8").split("\n- name:", 1)[0].rstrip("\n") + "\n"
    if "kind=staff" not in header:
        header = header.rstrip("\n") + "\n# kind=staff 是只出现在游戏 staff 名单里的人（tools/build-credits-site.py 按门槛追加，credits_key 对 archive/credits/index.yml），建页但不进受访者目录。\n"
    REGISTRY.write_text(header + yaml.safe_dump(registry, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8", newline="\n")

    # ---- Game Freak 员工 / 曾员工：在 GF 自研作品里做过实际开发职务（Thanks、本地化、任天堂/TPC 方的制作人与协调不算）
    NOT_GF_PATH = re.compile(r"nintendo|\bncl\b|noa|noe|pokémon company|tpc|creatures|ilca|koei|omega force|mario club", re.I)
    EXTERNAL_ROLE = re.compile(r"produc|text editor|editors?$|artwork|battle tower data|global link|voice|vocal|recording|narrat|actor|musician|chorus|orchestra|perform|remix|arrange|advisor|supervis", re.I)

    def gf_evidence(p):
        a = analysis.get(p["name"])
        if not a:
            return []
        ev = []
        for g in a["core_games"]:
            if games[g].get("developer") != "Game Freak":
                continue
            for r in a["roles"][g]:
                # 只认企划 / 程序 / 美术 / 音乐 / 总监：协调、制作人、调试多是任天堂 / TPC / 外包方
                if r["cat"] not in ("Plan", "Prog", "Art", "Sound", "Dir") or NOT_GF_PATH.search(r["role"]):
                    continue
                if EXTERNAL_ROLE.search(r["role"]):
                    continue  # 制作人（任天堂 / TPC）、本地化文本编辑、声优与录音、TPC 网络组、外包 artwork
                ev.append((games[g]["year"], g, r["rank"]))
                break
        ev.sort()
        # 要么 ≥2 部 GF 作品的开发职务，要么在一部里带 lead 以上——一次性的外部参与者不算
        if len(ev) >= 2 or any(e[2] >= 1 for e in ev):
            return ev
        return []

    gf_years = {}  # key → (首次年份, GF 作品数)
    for p in people:
        ev = gf_evidence(p)
        if ev:
            gf_years[p["key"]] = (ev[0][0], len(ev))
    name_keys = {}
    for p in people:
        for v in [p["name"]] + p.get("variants", []):
            name_keys.setdefault(v, []).append(p["key"])
    key_games = {p["key"]: set(p["games"]) for p in people}

    def gf_key_for(name, slug):
        """名单页上的一个名字在这一作对应哪条索引（同名拆分时按参与作品挑）→ 若是 GF 人，返回 (首次年份, 作数)"""
        for k in name_keys.get(name, []):
            if slug in key_games.get(k, ()) and k in gf_years:
                return gf_years[k]
        return None

    gf_count = {}
    for slug, g in games.items():
        seen = set()
        for sct in g["sections"]:
            if "thanks" in " / ".join(sct["path"]).lower():
                continue
            for n in sct["names"]:
                for k in name_keys.get(n["name"], []):
                    if slug in key_games.get(k, ()) and k in gf_years:
                        seen.add(k)
        gf_count[slug] = len(seen)
    print(f"Game Freak 员工/曾员工：{len(gf_years)} 人")

    # ---- 2. credits_games.yml
    glist = []
    for slug in core_order + sorted((s for s in games if not games[s].get("core")), key=lambda s: (games[s].get("year") or 0, s)):
        g = games[slug]
        row = {"slug": slug, "title": g["title"].replace("Staff of ", ""), "title_zh": game_title_zh(g), "year": g["year"], "developer": g["developer"],
               "core": bool(g.get("core")), "count": g["count"], "source": g["source"]}
        if g.get("work"):
            row["work"] = g["work"]
        if g.get("source_ja"):
            row["source_ja"] = g["source_ja"]
        if g.get("note"):
            row["note"] = g["note"]
        if g["developer"] != "Game Freak":
            row["gf_count"] = gf_count.get(slug, 0)
        glist.append(row)
    (ROOT / "_data" / "credits_games.yml").write_text("# 由 tools/build-credits-site.py 生成：staff 名单收录的作品\n" + yaml.safe_dump(glist, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8", newline="\n")
    gz = {g["slug"]: g for g in glist}

    # ---- 3. credits_people.yml（有人物页的人）
    key2slug = {k: e["slug"] for k, e in matched.items()}
    cp = {}
    for p in people:
        e = matched.get(p["key"])
        if not e:
            continue
        credits = []
        for c in p["credits"]:
            if c["game"] not in gz:
                continue
            row = {"game": c["game"], "year": gz[c["game"]]["year"], "role": re.sub(r"^(Global staff|Japanese version|Staff list[^/]*|List of staff) / ", "", c["role"])}
            if c.get("role_ja") and c["role_ja"].strip().lower() != row["role"].split(" / ")[-1].strip().lower() and c["role_ja"].strip().lower() != row["role"].strip().lower():
                row["role_ja"] = c["role_ja"]  # 日文页用拉丁字母时职名与英文相同，不重复显示
            if c.get("lead"):
                row["lead"] = c["lead"]
            credits.append(row)
        a = analysis.get(p["name"])
        cp[e["slug"]] = {"name": p["name"], "kanji": (p.get("kanji") or [None])[0], "kana": (p.get("kana") or [None])[0],
                         "games": len(p["games"]), "core_games": len(p.get("core_games", [])), "first": p["first"], "last": p["last"],
                         "credits": credits}
        if a:
            latest = (a.get("real_games") or a["core_games"] or [None])[-1]  # 最近一次实际参与（Special Thanks 不算）
            if latest:
                cp[e["slug"]]["latest_role"] = a["primary"][latest]["role"]
                cp[e["slug"]]["latest_game"] = latest
    (ROOT / "_data" / "credits_people.yml").write_text("# 由 tools/build-credits-site.py 生成：人物页 slug → 历作 staff 职务\n" + yaml.safe_dump(cp, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8", newline="\n")
    print(f"credits_people.yml: {len(cp)} 人")

    # ---- 4. 每作名单页
    PAGES.mkdir(parents=True, exist_ok=True)
    for old in PAGES.glob("*.md"):
        old.unlink()
    name2slug = {}
    for p in people:
        e = matched.get(p["key"])
        if e:
            for v in [p["name"]] + p.get("variants", []):
                name2slug[v] = e["slug"]
    for slug, g in games.items():
        body = []
        mark_gf = g["developer"] != "Game Freak"  # 外传、BDSP、Pokopia、Champions：标出 GF 的人
        for s in g["sections"]:
            if not s["names"]:
                continue
            path = [x for x in s["path"] if not re.match(r"^(Global staff|Japanese version|Staff list.*|List of staff)$", x)]
            crumbs = " / ".join(html.escape(x) for x in path[:-1])
            title = html.escape(path[-1]) if path else "—"
            body.append('<section class="credits__section">')
            crumb_html = f"<small>{crumbs} / </small>" if crumbs else ""
            ja_html = f'<span class="credits__ja-role">{html.escape(s["ja_role"])}</span>' if s.get("ja_role") and s["ja_role"].strip().lower() != (path[-1] if path else "").strip().lower() else ""
            body.append(f"<h3>{crumb_html}{title}{ja_html}</h3>")
            body.append('<ul class="credits__names">')
            for n in s["names"]:
                cls = ["credits__name"]
                if n.get("kind") == "company":
                    cls.append("is-company")
                if n.get("lead"):
                    cls.append("is-lead")
                nm = html.escape(n["name"])
                ps = name2slug.get(n["name"])
                inner = f'<a href="/people/{ps}/">{nm}</a>' if ps else nm
                if mark_gf:
                    gf = gf_key_for(n["name"], slug)
                    if gf:
                        inner += f'<img class="credits__gf" src="/assets/img/works/gamefreak-mark.svg" alt="Game Freak" title="Game Freak 成员（按名单推断：在 {gf[1]} 部 GF 自研作品里有开发职务署名，最早 {gf[0]}）">'
                        cls.append("is-gf")
                sub = []
                if n.get("kanji") and not n["kanji"].startswith("w:"):
                    sub.append(html.escape(n["kanji"]))
                if n.get("ja") and JA_RE.search(n["ja"]) and n.get("ja") != n.get("kanji"):
                    sub.append(html.escape(n["ja"]))
                lead = f'<b>{html.escape(n["lead"])}</b> ' if n.get("lead") else ""
                subs = f' <small>{" · ".join(sub)}</small>' if sub else ""
                body.append(f'<li class="{" ".join(cls)}">{lead}{inner}{subs}</li>')
            body.append("</ul></section>")
        fm = {"layout": "credits-game", "title": f"{game_title_zh(g)} 制作名单", "game": slug, "permalink": f"/credits/{slug}/", "search": False, "sitemap": True}
        if mark_gf:
            fm["gf_count"] = gf_count.get(slug, 0)
        text = "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + "\n".join(body) + "\n"
        (PAGES / f"{slug}.md").write_text(text, encoding="utf-8", newline="\n")
    (PAGES / "index.md").write_text("---\n" + yaml.safe_dump({"layout": "credits-index", "title": "制作名单", "permalink": "/credits/", "search": False}, allow_unicode=True, sort_keys=False) + "---\n", encoding="utf-8", newline="\n")
    (PAGES / "staff.md").write_text("---\n" + yaml.safe_dump({"layout": "credits-staff", "title": "历作 staff 总表", "permalink": "/credits/staff/", "search": False}, allow_unicode=True, sort_keys=False) + "---\n", encoding="utf-8", newline="\n")
    print(f"pages: {len(games)} 作 + index + staff")

    # ---- 5. 总表 JSON（核心作品参与者）
    ASSETS.mkdir(parents=True, exist_ok=True)
    rows = []
    works = {w["name"]: w for w in (yaml.safe_load((ROOT / "_data" / "works.yml").read_text(encoding="utf-8")) or [])}
    for p in people:
        a = analysis.get(p["name"])
        if not a or not a["core_games"]:
            continue
        cells = {}
        for g in a["core_games"]:
            r = a["primary"][g]
            # 该作全部职务（主职之外的也带上，卡片里列出来），日文职名与英文相同时省略
            allroles = []
            for rr in a["roles"][g]:
                ja = rr.get("role_ja")
                if ja and ja.strip().lower() in (rr["role"].strip().lower(), rr["role"].split(" / ")[-1].strip().lower()):
                    ja = None
                allroles.append([rr["role"], ja] if ja else [rr["role"]])
            cells[g] = [r["cat"], r["rank"], r["role"], allroles]
        e = matched.get(p["key"])
        row = {"n": p["name"], "k": (p.get("kanji") or [None])[0], "y": (p.get("kana") or [None])[0], "s": key2slug.get(p["key"]),
               "c": len(a["core_games"]), "g": len(p["games"]), "f": p["first"], "l": p["last"], "r": cells}
        if e and e.get("avatar"):
            row["a"] = e["avatar"]
        rows.append(row)
    data = {"games": [{"slug": s, "year": gz[s]["year"], "title": gz[s]["title_zh"], "short": gz[s]["title"], "developer": gz[s]["developer"],
                       "abbr": ABBR.get(s, s), "gen": GEN.get(s, 0),
                       **({"icon": works[gz[s]["work"]]["icon"]} if gz[s].get("work") in works and works[gz[s]["work"]].get("icon") else {})} for s in core_order],
            "gens": GEN_LABEL,
            "cat_zh": CAT_ZH, "rank_zh": RANK_ZH, "people": rows}
    (ASSETS / "credits-staff.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"credits-staff.json: {len(rows)} 人，{(ASSETS / 'credits-staff.json').stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
