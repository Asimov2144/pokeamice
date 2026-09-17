#!/usr/bin/env python3
"""Development Atlas 阶段 0：把 staff 名单算成前端要的 JSON（每作画像、作品关系、个人履历），并做回归检查。

  python tools/build-atlas.py            生成全部
  python tools/build-atlas.py --check    只跑回归断言（读已生成的 JSON；改分类规则后先跑这个）

读：_data/credits/<game>.yml            解析结果（不改）
    archive/credits/index.yml           人物归一（罗马字 key）+ archive/credits/merges.yml
    _data/credits_blocks/<game>.yml     区块 → 组织 / 范围 / 父级（人工；有它的作品才有 scope 拆分和完整层级）
    _data/credits_relations.yml         作品关系（人工）
    _data/credits_eras.yml              Experience cohort 分段（人工）
写：assets/data/credits-profile/<game>.json   每作画像：level / coverage / team_size / role & domain 分布 / sections /
                                              leadership / experience_cohorts / previous_credit_sources / next_credit_destinations / related_games
    assets/data/credits-relations.json        每条关系：共同人员、Retention / Inheritance / Jaccard、类别矩阵、Bridge、复刻的监督化
    assets/data/credits-careers.json          每人（≥1 部核心作）：作品 → 类别 / 级别 / 领域 / 原职名
    design/credits-analysis/domains.md        区块 → 类别 / 领域 对照表（人工审规则用）
    design/credits-analysis/atlas-summary.md  每作等级、覆盖率、来源前三（人工看）

口径（写在 JSON 里，前端照抄，不自己判断）：
  * 参与（dev）= 主职类别不是 Thanks、也不是 Loc/QA 的人——与 analyze-credits 的"GF 本体"一致，各等级统一，
    跨年代比较用它；区块表给的 scope 拆分是另一张视图，只在 curated 的作品上有。
  * 家族：DLC / 版本差分归母作（analyze-credits.FAMILY）。"上一次 / 下一次署名"、"首次参与"都按家族算。
  * 上一次署名 = 全部收录作品（含外传）里、按发售序严格在前、且不是纯 Special Thanks 的最近一次。
  * 级别（rank）来自职名 + 日文页的 lead 标记；lead 标记只有有日文页的作品才有，coverage.lead_marks 说明来源。
  * 领域（domain）未命中 = null（"未归类"），不猜。
  * 身份置信度：single（只署名一次，无合并风险）/ high（多作且假名或汉字一致）/ medium（只靠罗马字合并）/ low（同罗马字多汉字、或经人工拆分 / 合并）。
"""
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), ROOT / "tools" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ac = _load("analyze-credits")
bc = _load("build-credits")

GAMES_DIR = ROOT / "_data" / "credits"
BLOCKS_DIR = ROOT / "_data" / "credits_blocks"
INDEX = ROOT / "archive" / "credits" / "index.yml"
RELATIONS = ROOT / "_data" / "credits_relations.yml"
ERAS = ROOT / "_data" / "credits_eras.yml"
OUT = ROOT / "assets" / "data"
PROFILES = OUT / "credits-profile"
DESIGN = ROOT / "design" / "credits-analysis"

DEV_EXCLUDE = {"Thanks", "Loc/QA"}
SCOPES = ["core", "partner", "asset", "qa", "localization", "production", "marketing", "thanks", "other"]


# ---------------------------------------------------------------- 读
def load_games():
    games = {}
    for f in GAMES_DIR.glob("*.yml"):
        d = yaml.safe_load(f.read_text(encoding="utf-8"))
        games[d["slug"]] = d
    core_idx = {s: i for i, s in enumerate(ac.CORE_ORDER)}
    order = sorted(games, key=lambda s: (games[s]["year"], core_idx.get(s, 50), s))   # 同年：核心作按 CORE_ORDER，外传排在核心作之后
    return games, order


def load_blocks(slug, sections):
    """区块表叠到 sections 上：每个 section 得到 org / scope / parent（后写的条目覆盖先写的）。返回 (verified, 命中的条目数) 或 None。"""
    f = BLOCKS_DIR / f"{slug}.yml"
    if not f.exists():
        return None
    d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    tops = [s["path"][0] for s in sections]
    fulls = [" / ".join(s["path"]) for s in sections]

    def find(key, last=False, start=0):
        hits = [i for i in range(start, len(sections)) if fulls[i] == key or tops[i] == key]
        if not hits:
            raise SystemExit(f"{slug}: 区块表里的 {key!r} 在名单里找不到")
        return hits[-1] if last else hits[0]

    for b in d.get("blocks") or []:
        a = find(b["from"])
        if b.get("until"):
            z = find(b["until"], last=True, start=a)
        elif tops[a] == b["from"]:
            z = a                       # from 写的是顶层标题：同一顶层下紧接着的子块都算进去
            while z + 1 < len(sections) and tops[z + 1] == tops[a]:
                z += 1
        else:
            z = a
        for i in range(a, z + 1):
            s = sections[i]
            s["_org"] = b.get("organization")
            s["_scope"] = b.get("scope", "other")
            s["_parent"] = list(b.get("parent") or [])
    return bool(d.get("verified")), len(d.get("blocks") or [])


def load_people():
    people = yaml.safe_load(INDEX.read_text(encoding="utf-8"))
    by_key = {}
    for p in people:
        by_key[p["key"]] = p
        for k in p.get("merged_from") or []:
            by_key[k] = p
    return people, by_key


def key_for(name, role, merges, splits, by_key):
    k = bc.norm(name)
    k = merges.get(k, k)
    for sp in splits:
        if k == bc.norm(sp["name"]) and re.search(sp["role_match"], role, re.I):
            k = f"{k} ({sp['suffix']})"
    p = by_key.get(k)
    return p["key"] if p else None


def confidence(p):
    n = len(p["credits"])
    if n <= 1:
        return "single"
    if p.get("flag") or p.get("merged_from") or p["key"].endswith(")"):
        return "low"
    kana = {k for k in p.get("kana") or []}
    if p.get("kanji") or (kana and len(kana) == 1 and sum(1 for c in p["credits"]) >= 2):
        return "high"
    return "medium"


# ---------------------------------------------------------------- 算
def main():
    games, order = load_games()
    idx = {s: i for i, s in enumerate(order)}
    family = {s: ac.FAMILY.get(s, s) for s in order}
    people, by_key = load_people()
    merges, splits = bc.load_merges()
    conf = {p["key"]: confidence(p) for p in people}
    pinfo = {p["key"]: p for p in people}
    eras = yaml.safe_load(ERAS.read_text(encoding="utf-8"))
    relations = yaml.safe_load(RELATIONS.read_text(encoding="utf-8")) or []

    # 每作：sections 叠区块表；每人每作：roles → 主职
    roles = defaultdict(lambda: defaultdict(list))     # key → game → [role dicts]
    game_sections = {}
    unmatched = Counter()
    curated = {}
    for slug in order:
        g = games[slug]
        secs = g["sections"]
        curated[slug] = load_blocks(slug, secs)
        rows = []
        for i, s in enumerate(secs):
            path = list(s.get("_parent") or []) + list(s["path"])
            role = " / ".join(path)
            cat, rank0, dom = ac.category_of(role), ac.rank_of(role, None), ac.domain_of(role)
            members = []
            for n in s["names"]:
                if n.get("kind") == "company":
                    continue
                k = key_for(n["name"], " / ".join(s["path"]), merges, splits, by_key)
                if not k:
                    unmatched[slug] += 1
                    continue
                r = {"cat": cat, "rank": ac.rank_of(role, n.get("lead")), "domain": dom, "role": ac.short_role(role), "raw": role,
                     "lead": n.get("lead"), "sec": i, "org": s.get("_org"), "scope": s.get("_scope"), "ja_match": n.get("ja_match")}
                roles[k][slug].append(r)
                members.append({"key": k, "name": n["name"], "rank": r["rank"], "lead": n.get("lead")})
            rows.append({"i": i, "path": path, "raw_path": list(s["path"]), "org": s.get("_org"), "scope": s.get("_scope"),
                         "cat": cat, "domain": dom, "ja_role": s.get("ja_role"), "n": len(members),
                         "companies": [n["name"] for n in s["names"] if n.get("kind") == "company"], "members": members})
        game_sections[slug] = rows

    primary = defaultdict(dict)      # key → game → 主职
    for k, per in roles.items():
        for slug, rs in per.items():
            primary[k][slug] = sorted(rs, key=lambda r: (-r["rank"], ac.CAT_ORDER.index(r["cat"])))[0]

    def is_dev(k, slug):
        return slug in primary[k] and primary[k][slug]["cat"] not in DEV_EXCLUDE

    def is_credit(k, slug):       # 非纯 Thanks 的署名
        return slug in primary[k] and primary[k][slug]["cat"] != "Thanks"

    # 家族级参与：家族里任一作
    fam_games = defaultdict(list)
    for s in order:
        fam_games[family[s]].append(s)
    fam_order = [f for f in dict.fromkeys(family[s] for s in order)]
    fidx = {f: i for i, f in enumerate(fam_order)}

    def fam_dev(k, f):
        return any(is_dev(k, s) for s in fam_games[f])

    def fam_credit(k, f):
        return any(is_credit(k, s) for s in fam_games[f])

    def fam_primary(k, f):
        cands = [primary[k][s] for s in fam_games[f] if s in primary[k] and primary[k][s]["cat"] != "Thanks"]
        return sorted(cands, key=lambda r: (-r["rank"], ac.CAT_ORDER.index(r["cat"])))[0] if cands else None

    credit_fams = {k: [f for f in fam_order if fam_credit(k, f)] for k in roles}     # 每人按序的家族署名
    max_rank_before = {}

    def prev_family(k, f):
        fs = [x for x in credit_fams[k] if fidx[x] < fidx[f]]
        return fs[-1] if fs else None

    def next_family(k, f):
        fs = [x for x in credit_fams[k] if fidx[x] > fidx[f]]
        return fs[0] if fs else None

    def earlier_max_rank(k, f):
        return max((fam_primary(k, x)["rank"] for x in credit_fams[k] if fidx[x] < fidx[f]), default=None)

    def title_of(s):
        g = games[s]
        return g.get("work") or g.get("title", s).replace("Staff of ", "")

    # ---- 每作画像
    PROFILES.mkdir(parents=True, exist_ok=True)
    for old in PROFILES.glob("*.json"):
        old.unlink()
    summary = []
    rel_by_game = defaultdict(list)
    for r in relations:
        rel_by_game[r["source"]].append(("next", r))
        rel_by_game[r["target"]].append(("prev", r))
    profiles = {}
    for slug in order:
        g, secs, f = games[slug], game_sections[slug], family[slug]
        persons = [k for k in roles if slug in roles[k]]
        dev = [k for k in persons if is_dev(k, slug)]
        names = sum(len(s["names"]) for s in g["sections"])
        companies = sum(1 for s in g["sections"] for n in s["names"] if n.get("kind") == "company")
        jam = Counter(n.get("ja_match") for s in g["sections"] for n in s["names"] if n.get("kind") != "company")
        lead_marks = sum(1 for s in g["sections"] for n in s["names"] if n.get("lead"))
        # 嵌套 = 父级是部门 / 组（Section、Studio、Team…），不是「US Version Staff」「Global staff」这类地区 / 版本包装
        def is_team(path):
            parts = ac.strip_wrappers(" / ".join(path))
            return len(parts) > 1 and any(ac.DEPT_RE.search(x.lower()) and not ac.REGION_RE.search(x.lower()) and not re.search(r"director|supervisor", x.lower()) for x in parts[:-1])
        nested = sum(1 for s in secs if is_team(s["raw_path"]))
        if nested < 3:
            nested = 0                  # 一两个偶然的两级标题不算有层级
        alignment = bool(g.get("ja_alignment", {}).get("ja_matched"))
        cur = curated[slug]
        tier = "L3" if cur else ("L2" if nested else ("L1" if alignment else "L0"))
        cat_dist = Counter(primary[k][slug]["cat"] for k in dev)
        dom_dist = Counter(primary[k][slug]["domain"] or "未归类" for k in dev)
        scope_dist = Counter(primary[k][slug]["scope"] or "other" for k in persons) if cur else None
        ranks = Counter(primary[k][slug]["rank"] for k in dev)
        lead_cat = defaultdict(Counter)
        for k in dev:
            r = primary[k][slug]
            if r["rank"] >= 1:
                lead_cat[r["cat"]]["director" if r["rank"] >= 2 else "lead"] += 1
        first_lead, retained_lead, newcomer_lead = [], 0, 0
        for k in dev:
            r = primary[k][slug]
            if r["rank"] < 1:
                continue
            emr = earlier_max_rank(k, f)
            if emr is None:
                newcomer_lead += 1
            elif emr == 0:
                first_lead.append({"key": k, "name": pinfo[k]["name"], "rank": r["rank"], "cat": r["cat"], "role": r["role"]})
            else:
                retained_lead += 1
        # cohorts：首次核心作 / 首次任一作
        def cohorts(core_only):
            bins = [{"label": e["label"], "from": e["from"], "to": e["to"], "n": 0} for e in eras]
            first_here = unknown = 0
            for k in dev:
                fams = [x for x in credit_fams[k] if (games[x]["core"] if core_only else True)]
                if not fams:
                    unknown += 1
                    continue
                if fams[0] == f:
                    first_here += 1
                    continue
                y = games[fams[0]]["year"]
                b = next((b for b in bins if b["from"] <= y <= b["to"]), None)
                if b:
                    b["n"] += 1
                else:
                    unknown += 1
            return {"bins": bins, "first_here": first_here, "unclassified": unknown, "n": len(dev)}
        prev_imm, prev_any, nxt_imm = Counter(), Counter(), Counter()
        prev_imm_core, prev_any_core, nxt_imm_core = Counter(), Counter(), Counter()
        first_credit = no_later = first_core = no_later_core = 0
        for k in dev:
            cf = [x for x in credit_fams[k] if games[x]["core"]]
            before = [x for x in cf if fidx[x] < fidx[f]]
            after = [x for x in cf if fidx[x] > fidx[f]]
            if before:
                prev_imm_core[before[-1]] += 1
                for x in before:
                    prev_any_core[x] += 1
            else:
                first_core += 1
            if after:
                nxt_imm_core[after[0]] += 1
            else:
                no_later_core += 1
            pf = prev_family(k, f)
            if pf:
                prev_imm[pf] += 1
            else:
                first_credit += 1
            for x in credit_fams[k]:
                if fidx[x] < fidx[f]:
                    prev_any[x] += 1
            nf = next_family(k, f)
            if nf:
                nxt_imm[nf] += 1
            else:
                no_later += 1
        def src_list(c):
            return [{"family": x, "title": title_of(x), "year": games[x]["year"], "core": bool(games[x]["core"]), "n": n} for x, n in sorted(c.items(), key=lambda t: -t[1])]
        related = []
        for direction, r in rel_by_game.get(slug, []):
            other = r["target"] if direction == "next" else r["source"]
            related.append({"slug": other, "title": title_of(other), "year": games[other]["year"], "type": r["type"], "direction": "both" if r["type"] == "parallel" else direction,
                            "status": r.get("status"), "evidence": r.get("evidence") or [], "note": r.get("note")})
        low = sum(1 for k in dev if conf[k] == "low")
        prof = {
            "slug": slug, "title": title_of(slug), "year": g["year"], "developer": g.get("developer"), "core": bool(g.get("core")), "family": f,
            "family_members": fam_games[f],
            "level": {"tier": tier, "alignment": alignment, "nested": nested > 0, "curated": bool(cur), "curated_verified": bool(cur and cur[0])},
            "coverage": {"names": names, "companies": companies, "persons": len(persons), "unmatched": unmatched.get(slug, 0),
                         "ja_romaji": jam.get("romaji", 0), "ja_positional": jam.get("positional", 0), "ja_none": jam.get(None, 0),
                         "kanji": sum(1 for s in g["sections"] for n in s["names"] if n.get("kanji")), "lead_marks": lead_marks,
                         "lead_source": ("ja_marker+role_text" if lead_marks else ("role_text" if alignment else "role_text (no ja page)")),
                         "domain_unclassified": dom_dist.get("未归类", 0),
                         "identity": dict(Counter(conf[k] for k in dev))},
            "team_size": {"names": names, "persons": len(persons), "dev": len(dev), "sections": len(secs), "nested_teams": nested,
                          "max_depth": max((len(s["path"]) for s in secs), default=0),
                          "by_scope": ({s: scope_dist.get(s, 0) for s in SCOPES} if cur else None)},
            "role_distribution": {c: cat_dist.get(c, 0) for c in ac.CAT_ORDER if c not in DEV_EXCLUDE},
            "domain_distribution": dict(dom_dist.most_common()),
            "sections": secs,
            "leadership": {"by_rank": {str(r): ranks.get(r, 0) for r in range(5)}, "lead_marks": lead_marks,
                           "by_category": {c: dict(v) for c, v in lead_cat.items()},
                           "first_time_lead": sorted(first_lead, key=lambda x: -x["rank"]), "retained_lead": retained_lead, "newcomer_lead": newcomer_lead},
            "experience_cohorts": {"core": cohorts(True), "all": cohorts(False)},
            "previous_credit_sources": {"immediate": src_list(prev_imm), "any": src_list(prev_any), "first_pokemon_credit": first_credit,
                                        "immediate_core": src_list(prev_imm_core), "any_core": src_list(prev_any_core), "first_core_credit": first_core,
                                        "n": len(dev), "low_confidence": low,
                                        "note": "immediate/any 数全部收录作品（含外传、其他公司的作品）；*_core 只数核心作。默认展示 *_core。"},
            "next_credit_destinations": {"immediate": src_list(nxt_imm), "no_later_recorded": no_later,
                                         "immediate_core": src_list(nxt_imm_core), "no_later_core": no_later_core, "n": len(dev),
                                         "latest_recorded": games[order[-1]]["year"]},
            "related_games": sorted(related, key=lambda x: x["year"]),
            "archive_evidence": [],
        }
        profiles[slug] = prof
        (PROFILES / f"{slug}.json").write_text(json.dumps(prof, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        top = "、".join(f"{title_of(x)} {n}" for x, n in prev_imm_core.most_common(3))
        summary.append((slug, g["year"], tier, names, len(persons), len(dev), jam.get("romaji", 0) + jam.get("positional", 0), nested, lead_marks,
                        dom_dist.get("未归类", 0), first_credit, top, bool(g.get("core"))))

    # ---- 关系
    rels = []
    for r in relations:
        a, b = family[r["source"]], family[r["target"]]
        A = {k for k in roles if fam_dev(k, a)}
        B = {k for k in roles if fam_dev(k, b)}
        shared = A & B
        pa = {k: fam_primary(k, a) for k in shared}
        pb = {k: fam_primary(k, b) for k in shared}
        by_cat = {}
        for c in ac.CAT_ORDER:
            if c in DEV_EXCLUDE:
                continue
            ca = {k for k in A if fam_primary(k, a)["cat"] == c}
            cb = {k for k in B if fam_primary(k, b)["cat"] == c}
            by_cat[c] = {"a": len(ca), "b": len(cb), "shared_a": len(ca & shared), "shared_b": len(cb & shared), "same": len(ca & cb)}
        by_dom = {}
        doms = {fam_primary(k, a)["domain"] for k in A} | {fam_primary(k, b)["domain"] for k in B}
        for d in doms:
            da = {k for k in A if fam_primary(k, a)["domain"] == d}
            db = {k for k in B if fam_primary(k, b)["domain"] == d}
            by_dom[d or "未归类"] = {"a": len(da), "b": len(db), "shared_a": len(da & shared), "shared_b": len(db & shared), "same": len(da & db)}
        matrix = defaultdict(Counter)
        for k in shared:
            matrix[pa[k]["cat"]][pb[k]["cat"]] += 1
        la = {k for k in A if fam_primary(k, a)["rank"] >= 1}
        lb = {k for k in B if fam_primary(k, b)["rank"] >= 1}
        promoted = [k for k in shared if pb[k]["rank"] > pa[k]["rank"] and pb[k]["rank"] >= 1]
        demoted = [k for k in shared if pb[k]["rank"] < pa[k]["rank"]]
        people_rows = sorted(({"key": k, "name": pinfo[k]["name"], "kanji": (pinfo[k].get("kanji") or [None])[0],
                               "a": {x: pa[k][x] for x in ("cat", "rank", "domain", "role")}, "b": {x: pb[k][x] for x in ("cat", "rank", "domain", "role")},
                               "confidence": conf[k]} for k in shared), key=lambda x: (-max(x["a"]["rank"], x["b"]["rank"]), x["name"]))
        rel = {"source": r["source"], "target": r["target"], "family_a": a, "family_b": b, "type": r["type"], "status": r.get("status"),
               "evidence": r.get("evidence") or [], "note": r.get("note"),
               "a": {"slug": a, "title": title_of(a), "year": games[a]["year"], "developer": games[a].get("developer"), "dev": len(A), "leads": len(la)},
               "b": {"slug": b, "title": title_of(b), "year": games[b]["year"], "developer": games[b].get("developer"), "dev": len(B), "leads": len(lb)},
               "shared": len(shared), "a_only": len(A - B), "b_only": len(B - A),
               "retention": round(len(shared) / len(A), 3) if A else None, "inheritance": round(len(shared) / len(B), 3) if B else None,
               "jaccard": round(len(shared) / len(A | B), 3) if A | B else None,
               "same_category": sum(1 for k in shared if pa[k]["cat"] == pb[k]["cat"]),
               "same_domain": sum(1 for k in shared if pa[k]["domain"] and pa[k]["domain"] == pb[k]["domain"]),
               "by_category": by_cat, "by_domain": dict(sorted(by_dom.items(), key=lambda t: -t[1]["same"])),
               "matrix": {x: dict(y) for x, y in matrix.items()},
               "leadership": {"a_leads": len(la), "b_leads": len(lb), "retained": len(la & lb & shared), "promoted": len(promoted), "demoted": len(demoted),
                              "b_first_time_lead": sum(1 for k in lb & shared if k not in la)},
               "low_confidence": sum(1 for k in shared if conf[k] == "low"),
               "shared_people": people_rows}
        if r["type"] == "parallel":
            rel["bridge"] = {"same_domain": [k for k in shared if pa[k]["domain"] and pa[k]["domain"] == pb[k]["domain"]],
                             "cross_domain": [k for k in shared if pa[k]["domain"] and pb[k]["domain"] and pa[k]["domain"] != pb[k]["domain"]],
                             "leadership": [k for k in shared if pa[k]["rank"] >= 1 and pb[k]["rank"] >= 1],
                             "unclassified": [k for k in shared if not (pa[k]["domain"] and pb[k]["domain"])]}
            rel["bridge"] = {x: len(v) for x, v in rel["bridge"].items()}
            rel["caveat"] = "两作都署名 ≠ 同期在两组工作；同期开发是关系级证据（见 evidence），不下放到个人。"
        if r["type"] == "remake":
            sup = re.compile(r"supervis|advis|original|監修|スーパーバイ", re.I)
            rel["supervisory"] = [{"key": k, "name": pinfo[k]["name"], "a_role": pa[k]["role"], "b_role": pb[k]["role"]} for k in shared if sup.search(pb[k]["raw"]) and not sup.search(pa[k]["raw"])]
            rel["organization"] = {"a": games[a].get("developer"), "b": games[b].get("developer")}
        rels.append(rel)
    (OUT / "credits-relations.json").write_text(json.dumps(rels, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # ---- 履历（≥1 部核心作）
    careers = {}
    for k, per in roles.items():
        if not any(games[s]["core"] for s in per):
            continue
        p = pinfo[k]
        careers[k] = {"name": p["name"], "kanji": (p.get("kanji") or [None])[0], "kana": (p.get("kana") or [None])[0], "confidence": conf[k],
                      "credits": [{"game": s, "year": games[s]["year"], "core": bool(games[s]["core"]), "cat": r["cat"], "rank": r["rank"], "domain": r["domain"],
                                   "role": r["role"], "lead": r["lead"], "org": r["org"], "scope": r["scope"]}
                                  for s in order if s in per for r in [primary[k][s]]]}
    (OUT / "credits-careers.json").write_text(json.dumps(careers, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # ---- 人工审表
    DESIGN.mkdir(parents=True, exist_ok=True)
    blk = Counter()
    for slug in order:
        for s in game_sections[slug]:
            blk[(" / ".join(s["raw_path"]), s["cat"], s["domain"] or "—")] += s["n"]
    lines = ["# 区块 → 类别 / 领域（tools/build-atlas.py 生成；改 analyze-credits.py 的 CATEGORY / DOMAIN 后重跑对照）", "",
             "按领域分组，组内按人数。`—` = 未归类（页面上如实显示，不猜）。", ""]
    by_dom = defaultdict(list)
    for (path, cat, dom), n in blk.items():
        by_dom[dom].append((n, path, cat))
    for dom in sorted(by_dom, key=lambda d: (d == "—", -sum(n for n, _, _ in by_dom[d]))):
        rows = sorted(by_dom[dom], reverse=True)
        lines += [f"## {dom}（{sum(n for n, _, _ in rows)} 人次，{len(rows)} 种区块）", "", "| 人次 | 区块 | 类别 |", "|---|---|---|"]
        lines += [f"| {n} | {path} | {cat} |" for n, path, cat in rows[:80]]
        if len(rows) > 80:
            lines.append(f"| … | 另 {len(rows) - 80} 种 | |")
        lines.append("")
    (DESIGN / "domains.md").write_text("\n".join(lines), encoding="utf-8")
    lines = ["# Atlas 每作概况（tools/build-atlas.py 生成）", "",
             "等级：L0 平铺无日文对齐 · L1 平铺+对齐 · L2 有嵌套层级 · L3 有人工区块表。参与 = 非 Thanks、非 Loc/QA 的主职人数。", "",
             "| 作品 | 年 | 等级 | 署名 | 人 | 参与 | 日文对齐 | 嵌套块 | lead 标记 | 领域未归类 | 首次署名 | 上一次署名来源前三 |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for slug, year, tier, names, persons, dev, ja, nested, leads, dnull, first, top, core in summary:
        if core:
            lines.append(f"| {slug} | {year} | {tier} | {names} | {persons} | {dev} | {ja} | {nested} | {leads} | {dnull} | {first} | {top} |")
    lines += ["", "## 关系表（前 20 条按共同人数）", "", "| A | B | 类型 | 状态 | A 参与 | B 参与 | 共同 | Retention | Inheritance | Jaccard | 同类别 | 同领域 | 领导层留任 |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for rel in sorted(rels, key=lambda x: -x["shared"])[:20]:
        lines.append(f"| {rel['a']['slug']} | {rel['b']['slug']} | {rel['type']} | {rel['status']} | {rel['a']['dev']} | {rel['b']['dev']} | {rel['shared']} | {rel['retention']} | {rel['inheritance']} | {rel['jaccard']} | {rel['same_category']} | {rel['same_domain']} | {rel['leadership']['retained']} |")
    (DESIGN / "atlas-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"profiles: {len(profiles)} → {PROFILES.relative_to(ROOT)}；relations: {len(rels)}；careers: {len(careers)} 人")
    if unmatched:
        print("  名单里对不上索引的名字:", dict(unmatched.most_common(5)))
    return profiles, rels, careers


# ---------------------------------------------------------------- 回归
def check():
    """从生成的 JSON 复现 synthesis.md 的结论与方案 35 节的例句；数字改了就会在这里响。"""
    P = lambda s: json.loads((PROFILES / f"{s}.json").read_text(encoding="utf-8"))
    rels = json.loads((OUT / "credits-relations.json").read_text(encoding="utf-8"))
    careers = json.loads((OUT / "credits-careers.json").read_text(encoding="utf-8"))
    R = {(r["source"], r["target"], r["type"]): r for r in rels}
    fails = []

    def ok(cond, msg):
        print(("  ok   " if cond else "  FAIL ") + msg)
        if not cond:
            fails.append(msg)

    def rank_in(key, game):
        c = careers[key]
        return next((x["rank"] for x in c["credits"] if x["game"] == game), None)

    print("synthesis.md：领导层交接链")
    ok(rank_in("omori shigeru", "x-y") == 2 and rank_in("omori shigeru", "oras") == 3 and rank_in("omori shigeru", "legends-za") >= 3, "大森滋：XY Planning Director(2) → ORAS Director(3) → Z-A General Producer(3+)")
    ok(rank_in("junichi masuda", "gold-silver") >= 2 and rank_in("junichi masuda", "crystal") == 3, "増田順一：金银 Sub Director(2+) → 水晶 Director(3)")
    ok(rank_in("ichiraku katsuhiko", "usum") == 1 and rank_in("ichiraku katsuhiko", "scarlet-violet") == 2 and rank_in("ichiraku katsuhiko", "champions") == 3, "一楽克彦：究极日月 lead(1) → 朱紫 Section Director(2) → Champions Producer(3)（synthesis 写的「日月 lead」按名单是究极日月）")
    print("synthesis.md：平行企划")
    r = R[("legends-arceus", "scarlet-violet", "parallel")]
    ok(r["shared"] >= 250 and r["jaccard"] >= 0.25, f"阿尔宙斯 ⇄ 朱紫共同参与 {r['shared']}（Jaccard {r['jaccard']}）")
    ok(r["bridge"]["same_domain"] >= r["bridge"]["cross_domain"], f"Bridge 同领域 {r['bridge']['same_domain']} ≥ 跨领域 {r['bridge']['cross_domain']}")
    top = sorted(((d, v["same"]) for d, v in r["by_domain"].items() if d != "未归类"), key=lambda t: -t[1])[:3]
    ok(any(d in ("Pokémon Asset", "Tools & Pipeline", "Graphics Tech", "Modeling") for d, _ in top), f"共享最多的领域：{top}（方案 35 节：Tools / CG Technology / 宝可梦资产）")
    r = R[("x-y", "sun-moon", "chronological")]
    ok(r["shared"] >= 100, f"XY → 日月共同参与 {r['shared']}（日月班底 2014 年从 XY 分出）")
    r = R[("oras", "sun-moon", "parallel")]
    ok(r["retention"] is not None and r["retention"] < 0.7, f"ΩRαS → 日月 retention {r['retention']}（两线并行，不是同一队顺延）")
    print("synthesis.md：组织形态")
    ok(P("red-green")["team_size"]["dev"] <= 25 and P("red-green")["role_distribution"]["Debug"] >= 5, f"红绿参与 {P('red-green')['team_size']['dev']} 人（GF 12 人 + 任天堂 Debug Play {P('red-green')['role_distribution']['Debug']} 人等）")
    lead_n = lambda s: sum(v for r, v in P(s)["leadership"]["by_rank"].items() if r != "0")
    ok(lead_n("ruby-sapphire") > lead_n("crystal") and P("ruby-sapphire")["role_distribution"]["Mgmt"] >= 10, f"红蓝宝石 lead 以上 {lead_n('ruby-sapphire')} > 水晶 {lead_n('crystal')}，Mgmt {P('ruby-sapphire')['role_distribution']['Mgmt']}（2002 组织拐点：Art/Battle Director、Coordinators、Task Managers）")
    ok(P("sun-moon")["leadership"]["by_rank"]["2"] >= 8, f"日月 Section Director 层 {P('sun-moon')['leadership']['by_rank']['2']} 人（Section Director 制）")
    ok(P("sword-shield")["level"]["nested"] and not P("usum")["level"]["nested"], "嵌套层级从剑盾开始（究极日月是平铺）——页面必须按等级降级")
    print("方案 35 节例句")
    za = P("legends-za")
    src = {x["family"]: x["n"] for x in za["previous_credit_sources"]["immediate_core"]}
    anyc = {x["family"]: x["n"] for x in za["previous_credit_sources"]["any_core"]}
    ok(src.get("scarlet-violet", 0) > za["previous_credit_sources"]["first_core_credit"] and anyc.get("legends-arceus", 0) >= 150, f"Z-A 上一次核心作署名：朱紫 {src.get('scarlet-violet')} / 首次 {za['previous_credit_sources']['first_core_credit']}；曾在阿尔宙斯 {anyc.get('legends-arceus')} 人（「Z-A 继承阿尔宙斯线」要用 any 视图看，immediate 视图里阿尔宙斯被朱紫遮住）")
    r = R[("ruby-sapphire", "oras", "remake")]
    ok(len(r["supervisory"]) == 0 and r["leadership"]["promoted"] >= 3, f"红蓝宝石 → ΩRαS：转监督职 {len(r['supervisory'])} 人、升级 {r['leadership']['promoted']} 人——GF 自家复刻里原作成员是升职（大森 Game Designer → Director），不是退居监督；方案 18 节的「生产职 → 监督职」只在杉森一人身上成立")
    r = R[("gold-silver", "heartgold-soulsilver", "remake")]
    ok(any(x["name"] == "Ken Sugimori" for x in r["supervisory"]), f"金银 → 心金魂银：杉森建 → Graphic Supervisor（{len(r['supervisory'])} 人转监督）")
    r = R[("diamond-pearl", "bdsp", "remake")]
    ok(r["shared"] <= 10 and r["organization"]["b"] == "ILCA", f"钻珍 → BDSP：共同参与只有 {r['shared']} 人，开发方 {r['organization']['a']} → {r['organization']['b']}——外部复刻的连续性在组织层不在人员层")
    ok(P("scarlet-violet")["team_size"]["nested_teams"] > P("sword-shield")["team_size"]["nested_teams"], "朱紫的 team 细分多于剑盾")
    print("降级规则")
    ok(P("champions")["level"]["tier"] == "L0" and P("champions")["coverage"]["lead_marks"] == 0, "Champions 是 L0：没有日文页，lead 标记 0（页面写「来源无标记」，不写「无 Lead」）")
    ok(P("red-blue")["level"]["tier"] == "L0", "海外版红蓝是 L0")
    ok(P("sun-moon")["level"]["tier"] == "L1", "日月是 L1")
    ok(P("legends-za")["level"]["tier"] == "L3" and P("legends-za")["team_size"]["by_scope"]["asset"] >= 150, f"Z-A 是 L3：asset（Creatures）{P('legends-za')['team_size']['by_scope']['asset']} 人")
    ok(P("area-zero")["family"] == "scarlet-violet", "零之秘宝归朱紫家族")
    print(f"\n{len(fails)} 条失败" if fails else "\n全部通过")
    return not fails


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check() else 1)
    main()
    if "--no-check" not in sys.argv:
        check()
    if "--no-pages" not in sys.argv:
        _load("build-atlas-pages").main()      # 页面区块 _includes/atlas/<game>.html
