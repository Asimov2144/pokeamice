"""Keep the translations saying the same thing the same way, across a thousand entries.

The library's parallel rows (original / translation, some 20,000 of them) are themselves the
evidence of how a term has been rendered. This tool reads them all and:

    python tools/glossary-audit.py mine
        For every recurring source term (katakana words, the registry's names, the site
        glossary's own terms) it finds the Chinese renderings the translations actually
        use, by which Chinese strings co-occur with the term far above their background
        rate. A term with one dominant rendering is a convention; a term with several is a
        contradiction to settle. Writes design/glossary-audit.json and prints the
        contested ones and the ones that contradict the glossary.

    python tools/glossary-audit.py check
        For every glossary term (the master glossary + design/glossary-site.json) found in
        an original, is the glossary's rendering in the translation? Lists the rows where a
        listed variant was used instead, per post.

    python tools/glossary-audit.py fix [--apply]
        Replaces the site glossary's listed `variants` with the `target`, only inside a
        row's translation line and only when the row's original carries one of the term's
        source forms - the same one-line edits fill-translations.py makes. Without
        --apply it only prints what it would change.

    python tools/glossary-audit.py seed
        Writes the first design/glossary-site.json: the registry's people, the works, and
        every mined term whose rendering is settled (>= 80% of its rows, >= 3 posts), each
        with its evidence; the contested ones go under "review" for a decision.

design/glossary-site.json is the site's own glossary - the development-history vocabulary
the master (game terms) does not have: people, companies, departments, magazines, dev
jargon. import-nom.py loads it on top of the master, so import-web.py and
fill-translations.py translate with it; run `check` after changing it, `fix` to bring the
older translations in line.
"""
import glob
import io
import json
import random
import re
import sys
import collections
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "design" / "glossary-site.json"
AUDIT = ROOT / "design" / "glossary-audit.json"
MASTER = Path("P:/WEBSITE/pokeamice/event/public/glossary-master.json")
FRONT = re.compile(r"\A\ufeff?---\r?\n(.*?)\r?\n---\r?\n", re.S)
KATA = re.compile(r"[\u30a0-\u30ff\u30fc]{3,}")
ZH_TOKEN = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf0-9·]{2,12}|[A-Za-z][A-Za-z0-9 .·'-]{1,24}[A-Za-z0-9]")
MASTER_CATEGORIES = {"宝可梦", "地点", "分类"}   # names; the master's moves, items and abilities are everyday words too (プレゼント, プレッシャー)
EDGE = set("的了是在和与一个也就都把被对从向给让着过之及或并很更最不没有这那些们")
STOP_KATA = {"ポケモン", "ゲーム", "シリーズ", "アニメ", "デザイン", "イメージ", "テーマ", "キャラクター", "タイプ", "プレイ", "タイトル",
             "プレイヤー", "アイデア", "スタッフ", "ユーザー", "ソフト", "ヒット", "データ", "インタビュー", "チーム", "ストーリー", "プロジェクト",
             "ページ", "システム", "ファン", "ハード", "・・・", "モチーフ", "ボール", "レベル", "バランス", "シーン", "サウンド", "ポイント",
             "スタート", "コンセプト", "パターン", "スケジュール", "サポート", "リアル", "ダメージ", "セリフ", "メッセージ", "コミュニケーション"}


# ---------------------------------------------------------------- the corpus
def posts():
    for f in sorted(glob.glob(str(ROOT / "_posts" / "*.md"))):
        text = io.open(f, encoding="utf-8", errors="replace").read()
        m = FRONT.match(text)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        yield Path(f), fm, text


def corpus():
    """every row with an original and a translation: (post stem, row index, original, translation)"""
    rows = []
    for path, fm, _ in posts():
        items = fm.get("parallel_items") or fm.get("translation_segments") or []
        for i, it in enumerate(items):
            if not isinstance(it, dict):
                continue
            o, t = it.get("original"), it.get("translation")
            if isinstance(o, str) and isinstance(t, str) and o.strip() and t.strip():
                rows.append((path.stem, i, o, t))
    return rows


def load_site():
    if SITE.exists():
        return json.load(io.open(SITE, encoding="utf-8"))
    return {"note": "", "entries": [], "review": []}


def load_master():
    if not MASTER.exists():
        return []
    d = json.load(io.open(MASTER, encoding="utf-8"))
    return [e for e in d.get("entries", []) if e.get("target") and e.get("terms")]


def registry_terms():
    """source form -> target, from the people registry (aliases) and the works"""
    out = {}
    for p in yaml.safe_load(io.open(ROOT / "_data" / "people.yml", encoding="utf-8")) or []:
        if p.get("kind") in ("character", "figure"):
            continue
        for a in p.get("aliases") or []:
            if a != p["name"]:
                out[a] = ("人物", p["name"])
    return out


# ---------------------------------------------------------------- mining
def renderings(term_rows, background, n_all):
    """the Chinese strings that co-occur with a term far above their background rate:
    candidate -> (rows with it, lift)"""
    counts = collections.Counter()
    for _, _, o, t in term_rows:
        seen = set()
        for tok in ZH_TOKEN.findall(t):
            if re.match(r"[A-Za-z]", tok):
                seen.add(tok.strip())
                continue
            for n in range(2, min(8, len(tok)) + 1):
                for s in range(0, len(tok) - n + 1):
                    seen.add(tok[s:s + n])
        for c in seen:
            counts[c] += 1
    n = len(term_rows)
    out = {}
    for c, k in counts.items():
        if k < max(2, n * 0.2):
            continue
        if c[0] in EDGE or c[-1] in EDGE:
            continue
        bg = background.get(c, 0) / max(1, n_all)
        lift = (k / n) / max(bg, 1.0 / max(1, n_all))
        # a rendering is specific: common beside the term and rare elsewhere; a long name
        # that is everywhere (增田顺一, GAME FREAK) cannot lift far, so for four characters
        # or more a strong share counts too - a two-character commonplace never does
        if not ((lift >= 8 and bg <= 0.08) or (len(c) >= 4 and k / n >= 0.6 and lift >= 3)):
            continue
        out[c] = (k, lift)
    # the longest form that keeps the support: 增田顺一 over 增田, 宝可梦公司 over 宝可梦
    keep = {}
    for c, (k, lift) in sorted(out.items(), key=lambda kv: (-kv[1][0], -len(kv[0]))):
        covered = False
        for c2, (k2, _) in list(keep.items()):
            if c in c2 and k <= k2 * 1.15:
                covered = True
                break
            if c2 in c and k2 <= k * 1.15:
                del keep[c2]
        if not covered:
            keep[c] = (k, lift)
    return dict(sorted(keep.items(), key=lambda kv: -kv[1][0])[:6])


def mine(rows):
    site = load_site()
    master = {t: e["target"] for e in load_master() if e.get("category") in MASTER_CATEGORIES
              for t in e.get("terms", []) if re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", t) and len(t) >= 4 and len(e["target"]) >= 2}
    site_terms = {t: e["target"] for e in site.get("entries", []) for t in e.get("terms", [])}
    reg = registry_terms()
    # background rates from a sample of the corpus
    sample = random.Random(7).sample(rows, min(4000, len(rows)))
    background = collections.Counter()
    for _, _, o, t in sample:
        seen = set()
        for tok in ZH_TOKEN.findall(t):
            if re.match(r"[A-Za-z]", tok):
                seen.add(tok.strip())
                continue
            for n in range(2, min(8, len(tok)) + 1):
                for s in range(0, len(tok) - n + 1):
                    seen.add(tok[s:s + n])
        background.update(seen)
    n_all = len(sample)
    # the terms: katakana words in >= 3 posts, plus every known source form that occurs
    by_term = collections.defaultdict(list)
    post_of = collections.defaultdict(set)
    known = {}
    known.update({k: ("master", v) for k, v in master.items()})
    known.update({k: ("registry", v[1]) for k, v in reg.items()})
    known.update({k: ("site", v) for k, v in site_terms.items()})
    for stem, i, o, t in rows:
        terms = set(KATA.findall(o)) - STOP_KATA
        for k in known:
            if len(k) >= 2 and k in o:
                terms.add(k)
        for term in terms:
            by_term[term].append((stem, i, o, t))
            post_of[term].add(stem)
    report = []
    for term, trs in by_term.items():
        if len(post_of[term]) < 3 or len(trs) < 3:
            continue
        rend = renderings(trs[:400], background, n_all)
        if not rend:
            continue
        top = next(iter(rend.items()))
        n = min(len(trs), 400)
        contested = [c for c, (k, _) in rend.items() if k >= n * 0.2 and c != top[0] and c not in top[0] and top[0] not in c]
        entry = {"term": term, "rows": len(trs), "posts": len(post_of[term]),
                 "renderings": {c: k for c, (k, _) in rend.items()},
                 "top": top[0], "share": round(top[1][0] / n, 2),
                 "examples": sorted(post_of[term])[:4]}
        if term in known:
            entry["known"] = known[term][1]
            entry["known_from"] = known[term][0]
            known_share = sum(1 for _, _, _, tr in trs[:400] if known[term][1] in tr) / n
            entry["known_share"] = round(known_share, 2)
            if known_share < 0.5 and known[term][1] not in top[0] and top[0] not in known[term][1] and top[1][0] >= n * 0.4:
                entry["conflict"] = True
        if contested:
            entry["contested"] = contested
        report.append(entry)
    report.sort(key=lambda e: (-bool(e.get("conflict")), -bool(e.get("contested")), -e["posts"]))
    AUDIT.parent.mkdir(exist_ok=True)
    io.open(AUDIT, "w", encoding="utf-8", newline="\n").write(json.dumps(report, ensure_ascii=False, indent=1))
    conflicts = [e for e in report if e.get("conflict")]
    contested = [e for e in report if e.get("contested") and not e.get("conflict")]
    print(f"{len(rows)} rows, {len(report)} recurring terms mined -> {AUDIT.relative_to(ROOT)}")
    print(f"\n{len(conflicts)} terms rendered against the glossary:")
    for e in conflicts[:40]:
        print(f"  {e['term']:18s} glossary {e['known']:14s} corpus {e['top']} ({e['share']:.0%} of {e['rows']} rows, {e['posts']} posts)  {e.get('known_from')}")
    print(f"\n{len(contested)} terms rendered more than one way:")
    for e in contested[:60]:
        alts = ", ".join(f"{c} {k}" for c, k in e["renderings"].items() if c == e["top"] or c in e["contested"])
        print(f"  {e['term']:18s} {alts}   [{e['posts']} posts]")


# ---------------------------------------------------------------- check / fix
def has_term(term, text):
    """the term in the original: a Latin term as a whole word, a kana/kanji term as a run"""
    if re.match(r"^[A-Za-z0-9 .'&-]+$", term):
        return re.search(r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])", text) is not None
    return term in text


def satisfied(target, translation):
    """the rendering, or its short form (《红·绿》 for 宝可梦 红·绿)"""
    if target in translation:
        return True
    short = re.sub(r"^宝可梦 ", "", target)
    return len(short) >= 2 and short != target and short in translation


def site_index(site):
    """source form -> entry, for the site glossary"""
    idx = {}
    for e in site.get("entries", []):
        for t in e.get("terms", []):
            idx[t] = e
    return idx


def check(rows):
    site = load_site()
    idx = site_index(site)
    master = {t: e["target"] for e in load_master() if e.get("category") in MASTER_CATEGORIES
              for t in e.get("terms", []) if re.search(r"[\u3040-\u30ff]", t) and len(t) >= 5 and len(e["target"]) >= 2}
    per_post = collections.defaultdict(list)
    n = 0
    for stem, i, o, t in rows:
        for term, e in idx.items():
            if len(term) < 3 and not re.match(r"^[A-Z]{2,}$", term):
                continue
            if has_term(term, o) and not satisfied(e["target"], t):
                used = next((v for v in e.get("variants", []) if v in t), None)
                per_post[stem].append((i, term, e["target"], used))
                n += 1
        for term, target in master.items():
            if term in o and target not in t and term not in idx:
                per_post[stem].append((i, term, target, None))
                n += 1
    print(f"{n} rows where a glossary term's rendering is missing from the translation, in {len(per_post)} posts")
    for stem, hits in sorted(per_post.items(), key=lambda kv: -len(kv[1]))[:40]:
        terms = collections.Counter(f"{h[1]}→{h[2]}" + (f" (用了 {h[3]})" if h[3] else "") for h in hits)
        print(f"  {len(hits):3d}  {stem[:60]}: " + "; ".join(f"{k} ×{v}" for k, v in terms.most_common(4)))


def fix(rows, apply):
    site = load_site()
    idx = site_index(site)
    changes = collections.defaultdict(list)     # stem -> [(row index, old, new)]
    for stem, i, o, t in rows:
        new = t
        for term, e in idx.items():
            if not has_term(term, o):
                continue
            for v in e.get("variants", []):
                if v and v in new and not satisfied(e["target"], new):
                    new = new.replace(v, e["target"])
        if new != t:
            changes[stem].append((i, t, new))
    total = sum(len(v) for v in changes.values())
    print(f"{total} translations in {len(changes)} posts would change" + ("" if apply else " (dry run; --apply to write)"))
    for stem, ch in list(changes.items())[:12]:
        for i, old, new in ch[:3]:
            print(f"  {stem[:50]} #{i}: {old[:50]}  ->  {new[:50]}")
    if not apply:
        return
    for stem, ch in changes.items():
        path = ROOT / "_posts" / f"{stem}.md"
        text = io.open(path, encoding="utf-8", newline="").read()
        nl = "\r\n" if "\r\n" in text[:2000] else "\n"
        lines = text.replace("\r\n", "\n").split("\n")
        for i, old, new in ch:
            # the row's translation line: the one that holds exactly this text
            for n_, l in enumerate(lines):
                m = re.match(r"^(\s+translation: )(.*)$", l)
                if not m:
                    continue
                val = m.group(2)
                try:
                    parsed = yaml.safe_load("v: " + val)["v"] if val.strip() else ""
                except yaml.YAMLError:
                    parsed = None
                if parsed == old:
                    lines[n_] = m.group(1) + json.dumps(new, ensure_ascii=False)
                    break
        out = "\n".join(lines)
        io.open(path, "w", encoding="utf-8", newline="").write(out.replace("\n", nl) if nl == "\r\n" else out)
    print("written")


# ---------------------------------------------------------------- seed
def seed(rows):
    if not AUDIT.exists():
        mine(rows)
    report = json.load(io.open(AUDIT, encoding="utf-8"))
    site = load_site()
    have = {t for e in site.get("entries", []) for t in e.get("terms", [])}
    entries = list(site.get("entries", []))
    # the registry's people
    for p in yaml.safe_load(io.open(ROOT / "_data" / "people.yml", encoding="utf-8")) or []:
        if p.get("kind") in ("character", "figure"):
            continue
        terms = [a for a in (p.get("aliases") or []) if a != p["name"]]
        if terms and not any(t in have for t in terms):
            entries.append({"category": "人物", "target": p["name"], "terms": terms, "source": "people.yml"})
            have.update(terms)
    # the settled conventions of the corpus
    review = list(site.get("review", []))
    for e in report:
        if e["term"] in have or e["term"].endswith("・") or (e.get("known_from") == "master" and not e.get("conflict")):
            continue
        r = e["renderings"]
        # a contradiction worth a decision: two specific renderings, each in a quarter of the rows
        alts = [c for c, k in r.items() if k >= e["rows"] * 0.25]
        if e.get("conflict") or (len(alts) >= 2 and e["posts"] >= 8):
            review.append({"term": e["term"], "renderings": {c: r[c] for c in alts} if not e.get("conflict") else r, "known": e.get("known"), "posts": e["posts"], "examples": e["examples"]})
            continue
        # a settled convention: one rendering, whole (not the start of a longer one), well attested
        top, k = e["top"], r[e["top"]]
        fragment = any(top != c and top in c and r[c] >= k * 0.5 for c in r)
        if e["share"] >= 0.8 and e["posts"] >= 5 and not fragment and len(top) >= 2:
            entries.append({"category": "corpus", "target": top, "terms": [e["term"]], "evidence": {"rows": e["rows"], "posts": e["posts"], "share": e["share"]}, "auto": True})
            have.add(e["term"])
    review.sort(key=lambda x: -x["posts"])
    site["note"] = ("站内术语库：开发史料的词汇（人物、公司、部门、杂志、开发行话）——主术语表（游戏内名词）之外的那一层。"
                    "entries 里 target 是站内统一写法，terms 是原文写法，variants 是要改掉的旧译法（glossary-audit.py fix 会替换）；"
                    "auto: true 的条目是从语料里挖出来的既成惯例（share 是占比），review 里是译法不一、等人拍板的。"
                    "import-nom.py 会把这份和主术语表一起喂给翻译。")
    site["entries"] = entries
    site["review"] = review
    io.open(SITE, "w", encoding="utf-8", newline="\n").write(json.dumps(site, ensure_ascii=False, indent=1))
    print(f"{SITE.relative_to(ROOT)}: {len(entries)} entries ({sum(1 for e in entries if e.get('auto'))} from the corpus), {len(review)} to review")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "mine"
    rows = corpus()
    if cmd == "mine":
        mine(rows)
    elif cmd == "check":
        check(rows)
    elif cmd == "fix":
        fix(rows, "--apply" in sys.argv)
    elif cmd == "seed":
        seed(rows)
    else:
        print(__doc__)
