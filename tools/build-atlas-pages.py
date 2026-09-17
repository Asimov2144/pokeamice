#!/usr/bin/env python3
"""Development Atlas 阶段 1：把每作画像渲染成 /credits/<game>/ 页顶部的「团队画像」区块（预渲染 HTML，JS 只做切换）。

  python tools/build-atlas-pages.py          读 assets/data/credits-profile/*.json、credits-relations.json → _includes/atlas/<game>.html
                                             （tools/build-atlas.py 跑完会自动调用；单独跑用来改版式）

五个组件，按作品的数据等级降级（等级由 build-atlas.py 写进 JSON，这里只照着渲染）：
  TeamSnapshot   规模、参与人数、类别条；L2 起加 team 数；L3 加 scope 堆叠（开发本体 / 宝可梦资产 / 本地化 …）
  StaffOrigins   上一次 / 下一次署名来自哪些作品；默认只数核心作、最近一次；可切「任一前作」「含外传」
  Cohorts        首次核心作署名落在哪个时代；可切「含外传」
  TeamAnatomy    L2 / L3：Studio → Section → Team 树；L0 / L1：按类别 → 领域分组的区块列表（来源没有层级时不假装有）
  RelatedWorks   ← 前作 / ⇄ 并行 / ↺ 复刻·原作 / → 谱系，带共同参与数与档案证据链接
"""
import html
import importlib.util
import json
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("role_zh", Path(__file__).with_name("role-zh.py"))
_rz = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rz)
role_zh = _rz.role_zh


def zh_small(name):
    z = role_zh(name)
    return f'<small class="atlas__zh">（{esc(z)}）</small>' if z else ""
PROFILES = ROOT / "assets" / "data" / "credits-profile"
RELATIONS = ROOT / "assets" / "data" / "credits-relations.json"
OUT = ROOT / "_includes" / "atlas"

CAT_ZH = {"Dir": "总监/制作人", "Plan": "企划", "Prog": "程序", "Art": "美术", "Sound": "音乐", "Mgmt": "管理/协调", "Debug": "调试",
          "Loc/QA": "本地化/海外QA", "Thanks": "特别感谢", "Other": "其他"}
CAT_ORDER = ["Dir", "Plan", "Prog", "Art", "Sound", "Mgmt", "Debug", "Other", "Loc/QA", "Thanks"]
DOM_ZH = {"Localization": "本地化", "QA": "测试 / QA", "Sound": "音乐音效", "Marketing & PR": "宣传", "Scenario & Text": "剧本 / 文本", "Battle": "对战",
          "Network": "通信 / 网络", "UI": "界面", "Map & Field": "地图 / 场景", "Tools & Pipeline": "工具 / 管线", "Graphics Tech": "图形技术", "AI": "AI",
          "Pokémon Asset": "宝可梦资产", "Character": "角色", "Motion": "动作", "Modeling": "建模", "Movie": "影像 / 演出", "VFX": "特效", "Event": "事件",
          "Concept & Illustration": "概念 / 插画", "Management": "管理 / 协调", "未归类": "未归类"}
SCOPE_ZH = {"core": "开发本体", "partner": "外部协力", "asset": "宝可梦资产", "qa": "测试 / 调试", "localization": "本地化", "production": "制作 / 协调",
            "marketing": "宣传美术", "thanks": "特别感谢", "other": "其他"}
SCOPE_ORDER = ["core", "asset", "partner", "qa", "production", "localization", "marketing", "thanks", "other"]
TYPE_ZH = {"chronological": ("←", "前作", "→", "后作"), "parallel": ("⇄", "并行企划", "⇄", "并行企划"), "remake": ("↺", "原作", "↺", "复刻"), "lineage": ("→", "谱系", "→", "谱系")}
STATUS_ZH = {"evidenced": "有档案", "observed": "名单可见", "candidate": "待证"}
RANK_ZH = {1: "Lead", 2: "Section Director 级", 3: "Director / Producer", 4: "Executive Producer"}


def esc(s):
    return html.escape(str(s), quote=True)


def pct(n, d):
    return f"{round(100 * n / d)}%" if d else "—"


def bars(rows, total, cls=""):
    """rows: [(label_html, n, title)] → 横条列表；宽度按组内最大值"""
    mx = max((n for _, n, _ in rows), default=0) or 1
    out = [f'<ol class="atlas__bars {cls}">']
    for label, n, title in rows:
        out.append(f'<li title="{esc(title)}"><span class="atlas__bar-label">{label}</span><span class="atlas__bar"><i style="width:{round(100 * n / mx, 1)}%"></i></span>'
                   f'<span class="atlas__bar-n">{n}<small>{pct(n, total)}</small></span></li>')
    out.append("</ol>")
    return "\n".join(out)


def toggle(name, options, current):
    """options: [(value, label)]；JS 切 data-<name>，无 JS 时只显示默认那组"""
    b = [f'<button type="button" data-set="{name}" data-value="{v}"{" class=is-on" if v == current else ""}>{esc(l)}</button>' for v, l in options]
    return f'<span class="atlas__toggle" role="group">{"".join(b)}</span>'


class Site:
    def __init__(self):
        self.games = {g["slug"]: g for g in yaml.safe_load((ROOT / "_data" / "credits_games.yml").read_text(encoding="utf-8"))}
        self.key2slug = {}
        for e in yaml.safe_load((ROOT / "_data" / "people.yml").read_text(encoding="utf-8")) or []:
            if e.get("credits_key") and e.get("slug"):
                self.key2slug[e["credits_key"]] = e["slug"]
        self.rels = json.loads(RELATIONS.read_text(encoding="utf-8"))
        self._posts = {}

    def gtitle(self, slug):
        g = self.games.get(slug)
        return g["title_zh"] if g else slug

    def glink(self, slug, anchor=""):
        return f'<a href="/credits/{esc(slug)}/{anchor}">{esc(self.gtitle(slug))}</a>'

    def person(self, m):
        s = self.key2slug.get(m["key"])
        nm = esc(m["name"])
        return f'<a href="/people/{esc(s)}/">{nm}</a>' if s else nm

    def post(self, stem):
        """证据帖：文件名 → (url, 标题)；地址按 /:categories/:title/"""
        if stem in self._posts:
            return self._posts[stem]
        f = ROOT / "_posts" / f"{stem}.md"
        res = None
        if f.exists():
            t = f.read_text(encoding="utf-8")
            m = re.match(r"﻿?---\r?\n(.*?)\r?\n---", t, re.S)
            if m:
                try:
                    fm = yaml.safe_load(m.group(1)) or {}
                except yaml.YAMLError:
                    fm = {}
                cats = fm.get("categories") or []
                if isinstance(cats, str):
                    cats = [cats]
                url = "/" + "/".join(list(cats) + [stem[11:]]) + "/"
                res = (url, fm.get("display_title") or fm.get("title") or stem)
        self._posts[stem] = res
        return res

    def relation(self, a, b, typ):
        for r in self.rels:
            if r["type"] == typ and {r["source"], r["target"]} == {a, b}:
                return r
        return None


# ---------------------------------------------------------------- 组件
def snapshot(p, site):
    lv, ts, cov = p["level"], p["team_size"], p["coverage"]
    dev = ts["dev"]
    ranks = {int(k): v for k, v in p["leadership"]["by_rank"].items()}
    leads = sum(v for r, v in ranks.items() if r >= 1)
    dirs = sum(v for r, v in ranks.items() if r >= 2)
    nums = [("署名", ts["names"], "名单上的条目数（含公司）"), ("人", ts["persons"], "去掉公司、同一人合并后的人数"),
            ("参与", dev, "主职不是 Special Thanks、也不是本地化 / 海外 QA 的人——跨作品比较都用这个数")]
    if lv["nested"]:
        nums.append(("Team", ts["nested_teams"], "挂在 Section / Studio 之下的组数（来源有层级时才有）"))
    nums.append(("Lead 以上", leads, f"级别 ≥1 的参与者；lead 标记来源：{cov['lead_source']}"))
    nums.append(("Director 级", dirs, "Section Director 及以上（含 Producer）"))
    out = ['<div class="atlas__card atlas__snapshot"><h3>团队规模 <small>Team Snapshot</small></h3>', '<dl class="atlas__nums">']
    out += [f'<div title="{esc(t)}"><dt>{esc(l)}</dt><dd>{n}</dd></div>' for l, n, t in nums]
    out.append("</dl>")
    if ts.get("by_scope"):
        segs = [(s, ts["by_scope"].get(s, 0)) for s in SCOPE_ORDER if ts["by_scope"].get(s)]
        tot = sum(n for _, n in segs) or 1
        out.append('<p class="atlas__sub">署名构成（人工区块表' + ("，已对片尾核对" if lv.get("curated_verified") else "，草拟") + "）</p>")
        out.append('<div class="atlas__stack">' + "".join(f'<i class="scope-{s}" style="width:{round(100 * n / tot, 1)}%" title="{esc(SCOPE_ZH[s])} {n}"></i>' for s, n in segs) + "</div>")
        out.append('<ul class="atlas__legend">' + "".join(f'<li><i class="scope-{s}"></i>{esc(SCOPE_ZH[s])} <b>{n}</b></li>' for s, n in segs) + "</ul>")
    rd = p["role_distribution"]
    rows = [(f'<i class="cat-{esc(c)}">{esc(CAT_ZH[c])}</i>', rd.get(c, 0), f"{CAT_ZH[c]}：主职为此类别的参与者") for c in CAT_ORDER if c in rd and rd.get(c)]
    out.append('<p class="atlas__sub">参与者的主职类别</p>')
    out.append(bars(rows, dev, "atlas__bars--cat"))
    dd = [(d, n) for d, n in p["domain_distribution"].items() if d != "未归类"]
    top, rest = dd[:10], dd[10:]
    rows = [(esc(DOM_ZH.get(d, d)), n, f"{d}：按职名 / 组名判的领域") for d, n in top]
    if rest:
        rows.append(("其他领域", sum(n for _, n in rest), "、".join(f"{DOM_ZH.get(d, d)} {n}" for d, n in rest)))
    if p["domain_distribution"].get("未归类"):
        rows.append(('<span class="is-muted">未归类</span>', p["domain_distribution"]["未归类"], "职名里没有领域词（Programming、Special Thanks…），不猜"))
    out.append('<p class="atlas__sub">领域（职名 / 组名里带的开发领域）</p>')
    out.append(bars(rows, dev, "atlas__bars--dom"))
    out.append("</div>")
    return "\n".join(out)


def origins(p, site):
    ps, nd = p["previous_credit_sources"], p["next_credit_destinations"]
    dev = ps["n"]
    out = ['<div class="atlas__card atlas__origins" data-scope="core" data-view="immediate">',
           '<h3>来源与去向 <small>Staff Origins</small></h3>',
           '<p class="atlas__ctl">范围 ' + toggle("scope", [("core", "核心作"), ("all", "含外传")], "core") + ' 视图 ' + toggle("view", [("immediate", "最近一次"), ("any", "任一前作")], "immediate") + "</p>"]
    for scope in ("core", "all"):
        for view in ("immediate", "any"):
            key = view + ("_core" if scope == "core" else "")
            lst = ps.get(key) or []
            first = ps["first_core_credit"] if scope == "core" else ps["first_pokemon_credit"]
            hid = "" if (scope == "core" and view == "immediate") else " hidden"
            out.append(f'<div class="atlas__list" data-scope="{scope}" data-view="{view}"{hid}>')
            out.append('<p class="atlas__sub">' + ("参与者上一次署名的作品" if view == "immediate" else "参与者此前署名过的作品（一人可计入多作）") + ("" if scope == "core" else "，含外传与其他公司的作品") + "</p>")
            rows = [(site.glink(x["family"]) + f' <small>{x["year"]}</small>', x["n"], f"{x['n']} 人上一次署名在 {site.gtitle(x['family'])}" if view == "immediate" else f"{x['n']} 人曾署名 {site.gtitle(x['family'])}") for x in lst[:10]]
            if len(lst) > 10:
                rows.append(("其他作品", sum(x["n"] for x in lst[10:]), "、".join(f"{site.gtitle(x['family'])} {x['n']}" for x in lst[10:])))
            if view == "immediate":
                rows.append(('<b>首次署名</b>', first, "此前没有任何收录作品的署名" if scope == "all" else "此前没有核心作品的署名"))
            out.append(bars(rows, dev))
            out.append("</div>")
    if ps.get("low_confidence"):
        out.append(f'<p class="atlas__note">身份合并置信度低的参与者 {ps["low_confidence"]} 人（同罗马字多汉字，或经人工拆分）——来源统计对他们最敏感。</p>')
    # 去向
    later = nd.get("immediate_core") or []
    out.append('<p class="atlas__sub">参与者下一次核心作署名</p>')
    rows = [(site.glink(x["family"]) + f' <small>{x["year"]}</small>', x["n"], f"{x['n']} 人下一次署名在 {site.gtitle(x['family'])}") for x in later[:8]]
    rows.append(('<b>未见后续收录署名</b>', nd["no_later_core"], f"数据收录至 {nd['latest_recorded']} 年；没有后续署名 ≠ 离职"))
    out.append(bars(rows, nd["n"]))
    out.append("</div>")
    return "\n".join(out)


def cohorts(p, site):
    out = ['<div class="atlas__card atlas__cohorts" data-scope="core">', '<h3>参与者的时代 <small>Experience Cohorts</small></h3>',
           '<p class="atlas__ctl">首次署名范围 ' + toggle("scope", [("core", "核心作"), ("all", "含外传")], "core") + "</p>"]
    for scope in ("core", "all"):
        c = p["experience_cohorts"][scope]
        hid = "" if scope == "core" else " hidden"
        out.append(f'<div class="atlas__list" data-scope="{scope}"{hid}>')
        rows = [(f'{esc(b["label"])} <small>{b["from"]}–{b["to"] if b["to"] < 2099 else ""}</small>', b["n"], f"首次{'核心作' if scope == 'core' else ''}署名在 {b['from']}–{b['to']} 年的参与者") for b in c["bins"] if b["n"] or b["from"] <= p["year"]]
        rows.append(("<b>本作首次</b>", c["first_here"], "第一次出现在收录名单里（家族内的 DLC / 版本算同一作）"))
        if c.get("unclassified"):
            rows.append(('<span class="is-muted">无法归段</span>', c["unclassified"], ""))
        out.append(bars(rows, c["n"]))
        out.append("</div>")
    out.append('<p class="atlas__note">分段见 <code>_data/credits_eras.yml</code>，可改。</p>')
    out.append("</div>")
    return "\n".join(out)


def related(p, site):
    out = ['<div class="atlas__card atlas__related">', '<h3>相关作品 <small>Related Works</small></h3>']
    if not p["related_games"]:
        out.append('<p class="atlas__note">关系表（<code>_data/credits_relations.yml</code>）里还没有这部作品的边。</p></div>')
        return "\n".join(out)
    groups = OrderedDict()
    for r in p["related_games"]:
        arrow, lab = (TYPE_ZH[r["type"]][0], TYPE_ZH[r["type"]][1]) if r["direction"] in ("prev", "both") else (TYPE_ZH[r["type"]][2], TYPE_ZH[r["type"]][3])
        groups.setdefault((arrow, lab), []).append(r)
    for (arrow, lab), rs in groups.items():
        out.append(f'<h4><span class="atlas__arrow">{arrow}</span> {esc(lab)}</h4><ul class="atlas__rel">')
        for r in rs:
            rel = site.relation(p["family"], r["slug"], r["type"]) or {}
            facts = []
            if rel:
                a_is_me = rel["family_a"] == p["family"]
                facts.append(f"共同参与 <b>{rel['shared']}</b>")
                if r["type"] == "chronological":
                    if a_is_me:
                        facts.append(f"本作 {pct(rel['shared'], rel['a']['dev'])} 的人继续参与")
                    else:
                        facts.append(f"本作 {pct(rel['shared'], rel['b']['dev'])} 的人来自它")
                    facts.append(f"领导层留任 {rel['leadership']['retained']}")
                elif r["type"] == "parallel":
                    facts.append(f"同领域 Bridge {rel['bridge']['same_domain']} · 跨领域 {rel['bridge']['cross_domain']}")
                elif r["type"] == "remake":
                    facts.append(f"升职 {rel['leadership']['promoted']} · 转监督 {len(rel.get('supervisory') or [])}")
                    if rel.get("organization") and rel["organization"]["a"] != rel["organization"]["b"]:
                        facts.append(f"开发方 {esc(rel['organization']['a'])} → {esc(rel['organization']['b'])}")
                else:
                    facts.append(f"Jaccard {rel['jaccard']}")
            ev = []
            for stem in r.get("evidence") or []:
                pu = site.post(stem)
                if pu:
                    ev.append(f'<a href="{esc(pu[0])}">{esc(pu[1])}</a>')
            status = r.get("status") or ""
            status_zh = STATUS_ZH.get(status, status) if (status != "evidenced" or ev) else "官方事实"
            out.append(f'<li><div class="atlas__rel-head">{site.glink(r["slug"], "#atlas")} <small>{r["year"]}</small> <span class="atlas__chip is-{esc(status)}">{esc(status_zh)}</span></div>'
                       + (f'<div class="atlas__rel-facts">{" · ".join(facts)}</div>' if facts else "")
                       + (f'<div class="atlas__rel-note">{esc(r["note"])}</div>' if r.get("note") else "")
                       + (f'<div class="atlas__rel-ev">证据：{"；".join(ev)}</div>' if ev else "") + "</li>")
        out.append("</ul>")
    out.append('<p class="atlas__note">关系是人工维护的（不按发售日推）；「共同参与」按作品家族算，DLC 归母作。</p></div>')
    return "\n".join(out)


def anatomy(p, site):
    lv = p["level"]
    out = ['<div class="atlas__card atlas__anatomy">', '<h3>组织结构 <small>Team Anatomy</small></h3>']
    secs = [s for s in p["sections"] if s["n"] or s["companies"]]
    if lv["nested"]:
        out.append(_tree(secs, site))
    else:
        out.append('<p class="atlas__note">这部作品的名单在来源里是平铺的（没有 Section / Team 层级'
                   + ("，日文页也没有" if lv["alignment"] else "，也没有日文页") + "），这里按类别 → 领域归组显示区块，不假装有组织树。</p>")
        out.append(_flat(secs, site))
    out.append("</div>")
    return "\n".join(out)


def _leaf(s, site, open_=False):
    members = s["members"]
    leads = [m for m in members if m["rank"] >= 1]
    lead_html = " ".join(f'<span class="atlas__lead r{m["rank"]}" title="{esc(RANK_ZH.get(m["rank"], ""))}">{site.person(m)}</span>' for m in sorted(leads, key=lambda m: -m["rank"])[:6])
    tags = f'<i class="cat-{esc(s["cat"])}">{esc(CAT_ZH[s["cat"]])}</i>' + (f'<em>{esc(DOM_ZH.get(s["domain"], s["domain"]))}</em>' if s["domain"] else "")
    name = esc(s["path"][-1]) + zh_small(s["path"][-1])
    ja = f' <span class="credits__ja-role">{esc(s["ja_role"])}</span>' if s.get("ja_role") and s["ja_role"].strip().lower() != s["path"][-1].strip().lower() else ""
    body = ""
    if members:
        body = '<ul class="atlas__members">' + "".join(f'<li{" class=is-lead" if m["rank"] >= 1 else ""}>{site.person(m)}</li>' for m in members) + "</ul>"
    if s["companies"]:
        body += '<ul class="atlas__members atlas__members--co">' + "".join(f"<li>{esc(c)}</li>" for c in s["companies"]) + "</ul>"
    return (f'<details class="atlas__leaf"{" open" if open_ else ""}><summary><span class="atlas__name">{name}{ja}</span><b>{s["n"]}</b>{tags}'
            f'{" <span class=atlas__leads>" + lead_html + "</span>" if lead_html else ""}</summary>{body}</details>')


def _tree(secs, site):
    """path → 树。同一父级下同名叶子合并；顶层按 scope（有区块表时）分组。"""
    def node():
        return {"kids": OrderedDict(), "leaves": [], "n": 0}
    groups, orgs = OrderedDict(), defaultdict(list)
    for s in secs:
        gkey = s.get("scope") or ""
        if s.get("org") and s["org"] not in orgs[gkey]:
            orgs[gkey].append(s["org"])
        root = groups.setdefault(gkey, node())
        cur = root
        for part in s["path"][:-1]:
            cur = cur["kids"].setdefault(part, node())
        cur["leaves"].append(s)
    def count(nd):
        nd["n"] = sum(l["n"] for l in nd["leaves"]) + sum(count(k) for k in nd["kids"].values())
        return nd["n"]
    for g in groups.values():
        count(g)

    def render(name, nd, depth):
        directors = [m for l in nd["leaves"] for m in l["members"] if m["rank"] >= 2 and re.search(r"director|supervisor|manager", l["path"][-1], re.I)]
        d_html = " ".join(f'<span class="atlas__lead r{m["rank"]}">{site.person(m)}</span>' for m in directors[:4])
        inner = []
        for l in nd["leaves"]:
            inner.append(_leaf(l, site))
        for k, v in nd["kids"].items():
            inner.append(render(k, v, depth + 1))
        return (f'<details class="atlas__node d{depth}"{" open" if depth == 0 else ""}><summary><span class="atlas__name">{esc(name)}{zh_small(name)}</span><b>{nd["n"]}</b>'
                f'{" <span class=atlas__leads>" + d_html + "</span>" if d_html else ""}</summary>{"".join(inner)}</details>')

    out = []
    keyed = bool(any(k for k in groups))
    order = sorted(groups, key=lambda k: (SCOPE_ORDER.index(k) if k in SCOPE_ORDER else 99)) if keyed else list(groups)
    for gkey in order:
        g = groups[gkey]
        if keyed:
            scope = gkey
            out.append(f'<div class="atlas__org"><h4><i class="scope-{esc(scope or "other")}"></i>{esc(SCOPE_ZH.get(scope, scope or "未标"))}'
                       + (f' <small>{esc(" · ".join(orgs[scope]))}</small>' if orgs[scope] else "") + f' <b>{g["n"]}</b></h4>')
        singles = []
        for k, v in g["kids"].items():
            out.append(render(k, v, 0))
        for l in g["leaves"]:
            singles.append(l)
        if singles:
            # 没有父级的区块：多的按类别归组收起，少的直接列
            if len(singles) > 6:
                bycat = OrderedDict()
                for l in singles:
                    bycat.setdefault(l["cat"], []).append(l)
                for c in CAT_ORDER:
                    if c in bycat:
                        ls = bycat[c]
                        out.append(f'<details class="atlas__node d0"><summary><span class="atlas__name"><i class="cat-{esc(c)}">{esc(CAT_ZH[c])}</i> 区块</span><b>{sum(l["n"] for l in ls)}</b><small>{len(ls)} 块</small></summary>'
                                   + "".join(_leaf(l, site) for l in ls) + "</details>")
            else:
                out += [_leaf(l, site) for l in singles]
        if keyed:
            out.append("</div>")
    return "\n".join(out)


def _flat(secs, site):
    bycat = OrderedDict()
    for s in secs:
        bycat.setdefault(s["cat"], OrderedDict()).setdefault(s["domain"] or "未归类", []).append(s)
    out = []
    for c in CAT_ORDER:
        if c not in bycat:
            continue
        doms = bycat[c]
        n = sum(s["n"] for ls in doms.values() for s in ls)
        opn = " open" if c not in ("Loc/QA", "Thanks", "Debug", "Other") else ""
        out.append(f'<details class="atlas__node d0"{opn}><summary><span class="atlas__name"><i class="cat-{esc(c)}">{esc(CAT_ZH[c])}</i></span><b>{n}</b><small>{sum(len(v) for v in doms.values())} 块</small></summary>')
        for d, ls in sorted(doms.items(), key=lambda t: -sum(s["n"] for s in t[1])):
            out.append(f'<div class="atlas__dom"><h5>{esc(DOM_ZH.get(d, d))} <b>{sum(s["n"] for s in ls)}</b></h5>' + "".join(_leaf(s, site) for s in ls) + "</div>")
        out.append("</details>")
    return "\n".join(out)


def level_line(p):
    lv, cov = p["level"], p["coverage"]
    flags = [f'<span class="atlas__flag is-on">{esc(lv["tier"])}</span>',
             f'<span class="atlas__flag{" is-on" if lv["alignment"] else ""}">日文对齐 {"✓" if lv["alignment"] else "✗"}</span>',
             f'<span class="atlas__flag{" is-on" if lv["nested"] else ""}">结构 {"nested" if lv["nested"] else "flat"}</span>',
             f'<span class="atlas__flag{" is-on" if lv["curated"] else ""}">组织归属 {("人工表" + ("（已核）" if lv["curated_verified"] else "（草拟）")) if lv["curated"] else "无"}</span>',
             f'<span class="atlas__flag">lead 标记 {cov["lead_marks"]}</span>']
    return '<p class="atlas__level">数据 ' + " ".join(flags) + "</p>"


def render(p, site):
    parts = [f'<section class="atlas" id="atlas" data-level="{esc(p["level"]["tier"])}">',
             '<header class="atlas__head"><h2 class="credits__h2">团队画像 <small>Development Atlas</small></h2>', level_line(p),
             '<p class="atlas__intro">名单当结构证据读：这些是 credits 直接显示的现象，不是正式组织架构；没出现 ≠ 没参与，没有后续署名 ≠ 离职。</p></header>',
             '<div class="atlas__grid">', snapshot(p, site), origins(p, site), cohorts(p, site), related(p, site), "</div>", anatomy(p, site),
             "</section>"]
    return "\n".join(parts) + "\n"


def main():
    site = Site()
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.html"):
        old.unlink()
    n = 0
    for f in sorted(PROFILES.glob("*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        (OUT / f"{p['slug']}.html").write_text(render(p, site), encoding="utf-8", newline="\n")
        n += 1
    print(f"atlas pages: {n} → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
