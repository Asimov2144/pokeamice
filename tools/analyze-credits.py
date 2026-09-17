#!/usr/bin/env python3
"""从 archive/credits/index.yml 算职务变动表（阶段 B）。输出到 design/credits-analysis/：

  people.json        核心作品 ≥1 作的每个人：各作类别/级别/职名（精简，给站内和代理用）
  timeline.md        ≥4 部核心作品的人 × 核心作品 矩阵（类别缩写 + 级别标记）
  transitions.md     每部核心作品相对上一部的：新人 / 回归 / 缺席（之后回来=平行企划信号）/ 离开 / 职务变动
  sections.md        每作各类别人数
  absences.md        2019 年起：在剑盾/阿尔宙斯/朱紫出现、Z-A 与 Champions 都缺席的人 + 他们在外传里的去向
  era-*.md           三段（1996–2009 / 2010–2017 / 2018–2026）打包给分析代理读的材料

类别（category）和级别（rank）都是从职名关键词判的，规则见 CATEGORY / rank_of；同名异人无法区分。
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "archive" / "credits" / "index.yml"
GAMES_DIR = ROOT / "_data" / "credits"
OUT = ROOT / "design" / "credits-analysis"

# 版本差分（同一作的海外版 / 姊妹版）不进变动链：与母版重叠太多，会把"新人/离开"全抹平
# 版本差分（海外版/姊妹版）、非 GF 的 BDSP、小型副产品（Box / AR搜寻器）不进变动链
CHAIN_SKIP = {"red-blue", "blue-jp", "bdsp", "box", "dream-radar", "pokopia"}  # Pokopia 是核心作品但不在正传链上（与 Koei Tecmo 合作的生活模拟）

WRAPPER_RE = re.compile(r"^(global staff|japanese version( staff)?|staff list.*|list of staff|japanese staff|staff)$")
# 海外/本地化方的标记：出现在路径里时，测试/QA/翻译类都算 Loc/QA（Nintendo of America、TPCi、欧洲各语种…）
REGION_RE = re.compile(r"locali[sz]|translat|\bnoa\b|\bnoe\b|\bnok\b|nintendo of|tpci|pokémon company international|european|us version|(the )?americas|korea|chinese|french|german|italian|spanish|english|overseas|\(asia\)|\(europe\)|おうしゅう|えいご|フランスご|ドイツご|イタリアご|スペインご|かんこくご|ちゅうごくご|ほんやく|へんしゅう|ローカライズ|翻訳|欧州|英語|韓国語|中国語")

CATEGORY = [
    ("Thanks", r"special thanks|thanks|サンクス"),
    ("Loc/QA", r"locali[sz]|translat|editing|ほんやく|へんしゅう|ローカライズ|翻訳|\bnoa\b|\bnoe\b|nintendo of|tpci|pokémon company international|european|us version|korean|chinese|french|german|italian|spanish|english|overseas"),
    ("Debug", r"debug|\btest|quality|\bqa\b|デバッグ|テスティング|ひんしつ|品質"),
    ("Sound", r"sound|music|compos|voice|vocal|audio|bgm|jingle|サウンド|おんがく|音楽|作曲|コンポーザー"),
    ("Art", r"technical art"),  # 先于 Prog：Technical Art 归美术
    ("Prog", r"program|engineer|technical|technology|global link|framework|pipeline|physics|\btool|network|server|system|software|\bai\b|render|machine learning|simulation|library|workflow|dcc|attribute team|trinity|game engine|プログラム|プログラマ|エンジニア"),
    ("Plan", r"planning|planner|game design|scenario|script|story|braille|battle tower|battle team|field team|map design|map data|parametric|parameter|battle design|event|text|pokédex|level design|game designer|setting|data design|balance|シナリオ|プランニング|プランナー|せってい|設定|マップ|レベルデザイン"),
    ("Art", r"graphic|model|motion|animat|effect|vfx|\bui\b|\bart\b|design|visual|illustrat|character|3d|3-d|2d|background|movie|\bcg\b|cinematic|concept|lighting|shader|texture|artwork|packag|logo|artist|look development|デザイン|グラフィック|モーション|アーティスト|モデリング|アニメーション|エフェクト"),
    ("Mgmt", r"manag|coordinat|assistant|assistance|advisor|customer service|support|\bpr\b|marketing|promotion|licens|legal|business|administration|secretar|information|public relations|in cooperation with|media team|マネージ|こうほう|せんでん|広報|宣伝|協力"),
    ("Dir", r"director|supervis|ディレクター"),
]
DIR_LAST_RE = re.compile(r"^((co-|assistant )?directors?|(executive |co-|associate |line |general |chief )?producers?|produced by|directors? & producers?|game directors?|ディレクター|プロデューサー|エグゼクティブ プロデューサー)$")


DEPT_RE = re.compile(r"\b(section|studio|lab|laboratory|department|division|team)\b")

# 领域（domain）：类别说"做什么工种"，领域说"做游戏的哪一块"。先看末级职名 / 组名，再往上看父级；
# 都不命中就是 None——页面上写"未归类"，不猜。顺序即优先级（Localization / QA 先于一切，Battle 先于 Prog 的泛词……）。
DOMAIN = [
    ("Localization", r"locali[sz]|translat|\bediting|ほんやく|翻訳|ローカライズ|へんしゅう"),
    ("QA", r"debug|\btest|quality|\bqa\b|inspection|デバッグ|品質|テスト|チェック"),
    ("Sound", r"sound|music|compos|voice|vocal|audio|\bbgm\b|recording|musician|jingle|サウンド|音楽|おんがく|作曲|ボイス|ミュージシャン|レコーディング"),
    ("Marketing & PR", r"marketing|promotion|\bsales\b|public relations|\bpr\b|advertis|licens|\bbrand|宣伝|広報|販促|マーケ|ライセンス"),
    ("Scenario & Text", r"scenario|story|script|dialogue|\btext\b|pokédex text|narrative|シナリオ|ストーリー|テキスト|スクリプト|図鑑"),
    ("Battle", r"battle|バトル|contest|コンテスト"),
    ("Network", r"network|communication|wi-?fi|server|online|global link|connection|つうしん|通信|ネットワーク|サーバ"),
    ("UI", r"\bui\b|user interface|\bmenu|インターフェース|メニュー|\bhud\b"),
    ("Map & Field", r"\bmaps?\b|\bfield|world|terrain|level design|background|dungeon|environment(al)? (artists?|art|design|model)|マップ|フィールド|はいけい|背景|ダンジョン"),
    ("Tools & Pipeline", r"\btools?\b|pipeline|environment|framework|library|workflow|\bdcc\b|rigging|infrastructure|build system|環境|ツール|パイプライン|ライブラリ|フレームワーク|リギング"),
    ("Graphics Tech", r"render|shader|lighting|graphics? (programming|engine|technology)|technical art|look development|simulation|physics|cg technology|ライティング|レンダ|シェーダ|テクニカルアート|物理|シミュレーション"),
    ("AI", r"\bai\b|machine learning|機械学習"),
    ("Pokémon Asset", r"pok[eé]mon (characters? |3d |data )?(model|motion|design|drawing|visual|graphic|concept|attribute|check|inspection|coordination)|pok[eé]mon (& |and )(character|graphic|trainer)|monster design|ポケモンモデル|ポケモン3d|ポケモンデザイン|ポケモングラフィック|ポケモンモーション|ポケモンデータ"),
    ("Character", r"character|trainer|costume|\bnpc\b|キャラクター|トレーナー|人物"),
    ("Motion", r"\bmotion|animat|モーション|アニメーション"),
    ("Modeling", r"\bmodel(ing|er)?s?\b|モデリング|モデル"),
    ("Movie", r"movie|cinematic|\bvideo\b|\bdemo\b|storyboard|ムービー|デモ|絵コンテ"),
    ("VFX", r"\beffects?\b|\bvfx\b|エフェクト"),
    ("Event", r"\bevent|イベント"),
    ("Concept & Illustration", r"concept|illustrat|artwork|\blogo\b|packag|コンセプト|イラスト|ロゴ|パッケージ"),
    ("Management", r"manag|coordinat|produc|assistant|information|advisor|secretar|マネージ|コーディネート|プロデュ|アシスタント"),
]


def domain_of(role):
    """领域：末级职名先判，未命中再逐级看父级（Programming Section / UI Team → UI）。"""
    parts = strip_wrappers(role)
    for part in reversed(parts):
        pl = part.strip().lower()
        for dom, pat in DOMAIN:
            if re.search(pat, pl):
                return dom
    return None


# 核心作品的发售先后（同年作品按这个，不按 slug）；build-atlas.py 也用
CORE_ORDER = ["red-green", "blue-jp", "yellow", "red-blue", "gold-silver", "crystal", "ruby-sapphire", "box", "firered-leafgreen", "emerald",
              "diamond-pearl", "platinum", "heartgold-soulsilver", "black-white", "black2-white2", "dream-radar", "x-y", "oras", "sun-moon", "usum",
              "lets-go", "sword-shield", "bdsp", "legends-arceus", "scarlet-violet", "area-zero", "legends-za", "pokopia", "champions"]

# 作品家族：DLC 与同一作的版本差分归到母作——算"上一次 / 下一次署名"和"首次参与"时按家族，别把零之秘宝当成朱紫与 Z-A 之间的另一部作品
FAMILY = {"area-zero": "scarlet-violet", "blue-jp": "red-green", "red-blue": "red-green"}


def strip_wrappers(role):
    return [p for p in role.split(" / ") if not WRAPPER_RE.match(p.strip().lower())]


def _cat(text):
    for cat, pat in CATEGORY:
        if re.search(pat, text):
            return cat
    return "Other"


def category_of(role):
    """先看最末一级职名，再看整条路径；路径里带海外/本地化标记时，测试/翻译/杂项都归 Loc/QA。"""
    parts = strip_wrappers(role)
    if not parts:
        return "Other"
    last = parts[-1].strip().lower()
    full = " / ".join(parts).lower()
    if DIR_LAST_RE.match(last):
        return "Dir"
    if re.search(r"information (supervisor|management)", full):
        return "Mgmt"
    region = bool(REGION_RE.search(full))
    if re.search(r"(system|game|battle|field|network|ui|event|map) design\b(?!er)", last) and "program" not in last:
        return "Plan"  # GF 的「○○ System Design」是企划（日文 ゲームデザイン・システムせっけい）
    c = _cat(last)
    # 音乐 / 调试 / 本地化 / 感谢 这几类看末级职名就够了（阿尔宙斯把 Sound 挂在 Planning Section 下）
    if c in ("Sound", "Thanks", "Loc/QA") or (c == "Debug" and not region):
        return c
    # 「Programming Section / UI Team」这类：子组（或末级职名不带类别词的）继承部门的类别
    if re.search(r"\bteam$", last) or c == "Other":
        for parent in reversed(parts[:-1]):
            pl = parent.strip().lower()
            if DEPT_RE.search(pl) and not REGION_RE.search(pl):
                pc = _cat(pl)
                if pc not in ("Other", "Dir", "Thanks"):
                    return pc
    if region and c in ("Debug", "Loc/QA", "Other", "Mgmt"):
        return "Loc/QA"
    if c != "Other":
        return c
    c = _cat(full)
    if region and c in ("Debug", "Other", "Mgmt"):
        return "Loc/QA"
    return c


def rank_of(role, lead):
    parts = strip_wrappers(role)
    r = " / ".join(parts).lower()
    last = parts[-1].strip().lower() if parts else ""
    if re.search(r"information (supervisor|management)", r):
        return 0
    if re.search(r"executive producer|エグゼクティブ", r):
        return 4
    if DIR_LAST_RE.match(last):
        return 3
    if re.search(r"(section|art|program|programming|planning|graphics?|sound|cg|battle|animation|design|technical|game|story|world|field|3d|motion|ui|vfx|recording|environment|physics|creative|visual|character|scenario|map|network|system|ai|debug|localization|development|narrative|2d|chief) directors?|\bchief\b|supervisor|general manager|department|section (chief|manager)|head of|セクションディレクター|スーパーバイザー", r):
        return 2
    if re.search(r"\bdirectors?\b", last) and "assistant" not in last:
        return 2
    if lead or re.search(r"\blead(er)?s?\b|\bmanager|\bmain\b|リーダー", r):
        return 1
    return 0


RANK_MARK = {0: "", 1: "*", 2: "^", 3: "!", 4: "!!"}
CAT_ORDER = ["Dir", "Plan", "Prog", "Art", "Sound", "Mgmt", "Debug", "Loc/QA", "Thanks", "Other"]


def short_role(role):
    """去掉地区/总节包装，取最后两级"""
    parts = strip_wrappers(role)
    return " / ".join(parts[-2:]) if parts else role


def load():
    games = {}
    for f in GAMES_DIR.glob("*.yml"):
        d = yaml.safe_load(f.read_text(encoding="utf-8"))
        games[d["slug"]] = {k: d.get(k) for k in ("slug", "title", "work", "year", "developer", "core", "count", "note")}
    people = yaml.safe_load(INDEX.read_text(encoding="utf-8"))
    return games, people


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    games, people = load()
    core_order = [g["slug"] for g in sorted((g for g in games.values() if g["core"]), key=lambda g: (g["year"], g["slug"]))]
    core_order = [s for s in CORE_ORDER if s in games] + [s for s in core_order if s not in CORE_ORDER]
    chain = [s for s in core_order if s not in CHAIN_SKIP]

    # 每个人每作：roles → (category, rank, short)
    rows = []
    for p in people:
        if not p.get("core_games"):
            continue
        per = defaultdict(list)
        for c in p["credits"]:
            per[c["game"]].append({"cat": category_of(c["role"]), "rank": rank_of(c["role"], c.get("lead")), "role": short_role(c["role"]),
                                   "lead": c.get("lead"), "role_ja": c.get("role_ja")})
        prim = {}
        for g, rs in per.items():
            # 主职：级别最高，其次类别顺序（Dir > Plan > Prog > Art …），Thanks 最后
            best = sorted(rs, key=lambda r: (-r["rank"], CAT_ORDER.index(r["cat"])))[0]
            prim[g] = best
        rows.append({"name": p["name"], "kanji": (p.get("kanji") or [None])[0], "kana": (p.get("kana") or [None])[0],
                     "variants": p.get("variants", []), "link": (p.get("links") or [None])[0], "flag": p.get("flag"), "key": p.get("key"),
                     "core_games": [g for g in core_order if g in per], "games": p["games"],
                     "real_games": [g for g in core_order if g in per and prim[g]["cat"] != "Thanks"],
                     "roles": {g: rs for g, rs in per.items()}, "primary": prim})
    (OUT / "people.json").write_text(json.dumps(rows, ensure_ascii=False, indent=None, separators=(",", ":")), encoding="utf-8")
    (OUT / "games.json").write_text(json.dumps({"order": core_order, "chain": chain, "games": games}, ensure_ascii=False, indent=1), encoding="utf-8")

    def label(p):
        k = f"（{p['kanji']}）" if p.get("kanji") else ""
        return f"{p['name']}{k}"

    def cell(p, g):
        r = p["primary"].get(g)
        if not r:
            return "·"
        return f"{r['cat']}{RANK_MARK[r['rank']]}"

    # ---- timeline.md
    abbr = {s: f"{games[s]['year']} {s}" for s in core_order}
    lines = ["# 核心作品职务矩阵（≥4 部核心作品）", "",
             "类别：Dir 总监/制作人层 · Plan 企划 · Prog 程序 · Art 美术 · Sound 音乐 · Mgmt 管理/协调 · Debug 调试 · Loc/QA 本地化与海外QA · Thanks 特别感谢",
             "级别：`*` lead/leader · `^` section/art/program director 一级 · `!` director/producer · `!!` executive producer", "",
             "| 人 | " + " | ".join(abbr[s] for s in core_order) + " |", "|---|" + "---|" * len(core_order)]
    for p in sorted(rows, key=lambda p: (core_order.index(p["core_games"][0]), -len(p["real_games"]))):
        if len(p["real_games"]) < 4:
            continue
        lines.append(f"| {label(p)} | " + " | ".join(cell(p, g) for g in core_order) + " |")
    (OUT / "timeline.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- sections.md
    lines = ["# 每作各类别人数（主职计一次；公司、纯 Thanks 不计入总数）", "", "| 作品 | 年 | 总 | " + " | ".join(CAT_ORDER) + " |", "|---|---|---|" + "---|" * len(CAT_ORDER)]
    for g in core_order:
        cnt = Counter(p["primary"][g]["cat"] for p in rows if g in p["primary"])
        total = sum(v for k, v in cnt.items() if k != "Thanks")
        lines.append(f"| {g} | {games[g]['year']} | {total} | " + " | ".join(str(cnt.get(c, 0)) for c in CAT_ORDER) + " |")
    (OUT / "sections.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- transitions.md
    for i, p in enumerate(rows):
        p["id"] = i
    by_game = {g: {p["id"]: p for p in rows if g in p["primary"]} for g in core_order}
    later = {}
    for i, g in enumerate(chain):
        later[g] = set().union(*(set(by_game[h]) for h in chain[i + 1:])) if i + 1 < len(chain) else set()
    tr = ["# 逐作变动（相对变动链上的前一作；Thanks 级别的出现不算参与）", "",
          "变动链：" + " → ".join(chain), ""]
    spin_by_name = defaultdict(list)
    for p in rows:
        for g in p["games"]:
            if g not in games or games[g]["core"]:
                continue
            if g in p["primary"] and p["primary"][g]["cat"] == "Thanks":
                continue  # 外传里只是 Special Thanks 不算去向
            spin_by_name[p["id"]].append((games[g]["year"], g))

    def real(p, g):  # 只算 Thanks 以外的参与
        return g in p["primary"] and p["primary"][g]["cat"] != "Thanks"

    prev = None
    for g in chain:
        cur = {n: p for n, p in by_game[g].items() if real(p, g)}
        tr.append(f"## {g}（{games[g]['year']}，{games[g]['developer']}）— 参与 {len(cur)} 人")
        if prev:
            pv = {n: p for n, p in by_game[prev].items() if real(p, prev)}
            new = [p for n, p in cur.items() if n not in pv and not any(real(p, h) for h in chain[:chain.index(g)])]
            back = [p for n, p in cur.items() if n not in pv and any(real(p, h) for h in chain[:chain.index(g)])]
            gone = [p for n, p in pv.items() if n not in cur]
            gap = [p for p in gone if any(real(p, h) for h in chain[chain.index(g) + 1:])]
            left = [p for p in gone if p not in gap]
            stay = [p for n, p in cur.items() if n in pv]
            changes = []
            for p in stay:
                a, b = p["primary"][prev], p["primary"][g]
                # 只记级别变化，或 ≥3 部核心作品者的类别变化（一次性人员的类别漂移多是章节命名差异）
                if a["rank"] != b["rank"] or (a["cat"] != b["cat"] and len(p["real_games"]) >= 3):
                    arrow = "↑" if b["rank"] > a["rank"] else ("↓" if b["rank"] < a["rank"] else "→")
                    changes.append((-(b["rank"] - a["rank"]), f"- {label(p)}：{a['cat']}{RANK_MARK[a['rank']]} {a['role']} {arrow} {b['cat']}{RANK_MARK[b['rank']]} {b['role']}"))
            tr.append(f"上一作 {prev}：留任 {len(stay)}，新人 {len(new)}，回归 {len(back)}，缺席但之后回来 {len(gap)}，之后再没出现 {len(left)}")
            tr.append("")
            tr.append(f"### 职务变动（{len(changes)}）")
            tr += [c[1] for c in sorted(changes)] or ["（无）"]
            tr.append("")
            tr.append(f"### 缺席、之后回来（{len(gap)}）— 平行企划信号")
            for p in sorted(gap, key=lambda p: -p["primary"][prev]["rank"]):
                nxt = next(h for h in chain[chain.index(g) + 1:] if real(p, h))
                sp = [f"{s}({y})" for y, s in sorted(spin_by_name.get(p["id"], [])) if games[prev]["year"] <= y <= games[nxt]["year"]]
                tr.append(f"- {label(p)}：{prev} {p['primary'][prev]['cat']}{RANK_MARK[p['primary'][prev]['rank']]} {p['primary'][prev]['role']} → 再现于 {nxt} {p['primary'][nxt]['cat']}{RANK_MARK[p['primary'][nxt]['rank']]} {p['primary'][nxt]['role']}" + (f"；期间外传：{'、'.join(sp)}" if sp else ""))
            if not gap:
                tr.append("（无）")
            tr.append("")
            tr.append(f"### 之后再没出现（{len(left)}，只列 lead 以上或 ≥3 作）")
            for p in sorted(left, key=lambda p: (-p["primary"][prev]["rank"], -len(p["real_games"]))):
                if p["primary"][prev]["rank"] >= 1 or len(p["real_games"]) >= 3:
                    sp = [f"{s}({y})" for y, s in sorted(spin_by_name.get(p["id"], [])) if y >= games[prev]["year"]]
                    tr.append(f"- {label(p)}：{p['primary'][prev]['cat']}{RANK_MARK[p['primary'][prev]['rank']]} {p['primary'][prev]['role']}（{len(p['real_games'])} 作，{games[(p['real_games'] or p['core_games'])[0]]['year']}–）" + (f"；之后外传：{'、'.join(sp)}" if sp else ""))
            tr.append("")
            tr.append(f"### 回归（{len(back)}，此前参与过、上一作缺席）")
            for p in sorted(back, key=lambda p: -p["primary"][g]["rank"]):
                last = [h for h in chain[:chain.index(g)] if real(p, h)][-1]
                tr.append(f"- {label(p)}：上次 {last} {p['primary'][last]['cat']}{RANK_MARK[p['primary'][last]['rank']]} {p['primary'][last]['role']} → {p['primary'][g]['cat']}{RANK_MARK[p['primary'][g]['rank']]} {p['primary'][g]['role']}")
            if not back:
                tr.append("（无）")
            tr.append("")
            tr.append(f"### 新人里直接带 lead 以上的（{sum(1 for p in new if p['primary'][g]['rank'] >= 1)}）")
            for p in sorted(new, key=lambda p: -p["primary"][g]["rank"]):
                if p["primary"][g]["rank"] >= 1:
                    sp = [f"{s}({y})" for y, s in sorted(spin_by_name.get(p["id"], [])) if y < games[g]["year"]]
                    tr.append(f"- {label(p)}：{p['primary'][g]['cat']}{RANK_MARK[p['primary'][g]['rank']]} {p['primary'][g]['role']}" + (f"；此前外传：{'、'.join(sp)}" if sp else ""))
            tr.append("")
        else:
            tr.append("（链首）")
            tr.append("")
        prev = g
    (OUT / "transitions.md").write_text("\n".join(tr) + "\n", encoding="utf-8")

    # ---- absences.md：Switch 世代重点
    recent = ["sword-shield", "legends-arceus", "scarlet-violet", "area-zero"]
    latest = ["legends-za", "pokopia", "champions"]
    ab = ["# Switch 世代缺席名单", "",
          "在 剑盾 / 阿尔宙斯 / 朱紫 / 零之秘宝 任一作实际参与（非 Thanks）、且 Z-A、Pokopia、Champions 都没出现的人。",
          "列出最后一次出现的职务；`外传` 列出 2019 年后的外传出现。", ""]
    cand = []
    for p in rows:
        if any(real(p, g) for g in recent) and not any(real(p, g) for g in latest):
            last = [g for g in recent if real(p, g)][-1]
            cand.append((p, last))
    ab.append(f"共 {len(cand)} 人。按最后出现职务级别、参与作数排序。", )
    ab.append("")
    ab.append("| 人 | 核心作数 | 首作 | 最后出现 | 最后职务 | 2019 年后外传 |")
    ab.append("|---|---|---|---|---|---|")
    for p, last in sorted(cand, key=lambda t: (-t[0]["primary"][t[1]]["rank"], -len(t[0]["real_games"]))):
        sp = [f"{s}({y})" for y, s in sorted(spin_by_name.get(p["id"], [])) if y >= 2019]
        r = p["primary"][last]
        ab.append(f"| {label(p)} | {len(p['real_games'])} | {games[(p['real_games'] or p['core_games'])[0]]['year']} | {last} | {r['cat']}{RANK_MARK[r['rank']]} {r['role']} | {'、'.join(sp)} |")
    ab.append("")
    # 反向：Z-A / Champions 里的人在朱紫时期在干什么
    ab.append("## Z-A / Pokopia / Champions 参与者中、朱紫（2022）与零之秘宝（2023）都缺席的人（可能整段在做 Z-A / Pokopia / Champions / 未公布企划）")
    ab.append("")
    ab.append("| 人 | 核心作数 | 之前最后出现 | 当时职务 | 现在 | 现职务 |")
    ab.append("|---|---|---|---|---|---|")
    for p in sorted(rows, key=lambda p: -max((p["primary"][g]["rank"] for g in latest if g in p["primary"]), default=0)):
        now = [g for g in latest if real(p, g)]
        if not now or real(p, "scarlet-violet") or real(p, "area-zero"):
            continue
        before = [g for g in chain[:chain.index("scarlet-violet")] if real(p, g)]
        if not before:
            continue
        b, n = before[-1], now[0]
        ab.append(f"| {label(p)} | {len(p['real_games'])} | {b} | {p['primary'][b]['cat']}{RANK_MARK[p['primary'][b]['rank']]} {p['primary'][b]['role']} | {n} | {p['primary'][n]['cat']}{RANK_MARK[p['primary'][n]['rank']]} {p['primary'][n]['role']} |")
    (OUT / "absences.md").write_text("\n".join(ab) + "\n", encoding="utf-8")

    # ---- era bundles
    eras = {
        "era-1-1996-2009": [g for g in chain if games[g]["year"] <= 2009],
        "era-2-2010-2017": [g for g in chain if 2010 <= games[g]["year"] <= 2017],
        "era-3-2018-2026": [g for g in chain if games[g]["year"] >= 2018],
    }
    tr_text = (OUT / "transitions.md").read_text(encoding="utf-8")
    blocks = re.split(r"(?m)^## ", tr_text)
    head, blocks = blocks[0], blocks[1:]
    for era, gs in eras.items():
        sel = [b for b in blocks if b.split("（", 1)[0].strip() in gs]
        sub = [p for p in rows if sum(1 for g in gs if g in p["primary"]) >= 3 or max((p["primary"][g]["rank"] for g in gs if g in p["primary"]), default=0) >= 1]
        lines = [f"# {era}：分析材料", "", "## 变动链片段", "", head.strip(), ""] + ["## " + b for b in sel]
        lines += ["", "## 本段职务矩阵（本段 ≥2 作的人）", "",
                  "| 人 | " + " | ".join(f"{games[s]['year']} {s}" for s in gs) + " |", "|---|" + "---|" * len(gs)]
        for p in sorted(sub, key=lambda p: (core_order.index(p["core_games"][0]), -len(p["real_games"]))):
            lines.append(f"| {label(p)} | " + " | ".join(cell(p, g) for g in gs) + " |")
        lines += ["", "## 本段各作类别人数", ""] + [l for l in (OUT / "sections.md").read_text(encoding="utf-8").splitlines()[2:] if l.startswith("| 作品") or l.startswith("|---") or l.split("|")[1].strip() in gs]
        (OUT / f"{era}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"people: {len(rows)} → {OUT.relative_to(ROOT)}")
    for f in sorted(OUT.glob("*.md")):
        print(f"  {f.name}: {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
