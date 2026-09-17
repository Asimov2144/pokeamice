"""What each person is good at, and where the library heard it from.

    python tools/build-people-profiles.py                 # every registry person
    python tools/build-people-profiles.py --only masuda-junichi sugimori-ken
    python tools/build-people-profiles.py --no-llm        # the credits part only
    python tools/build-people-profiles.py --force         # ignore the cache

Writes _data/people_profiles.yml, one record per person of _data/people.yml (characters
and merely-cited figures left out), read by _layouts/person.html:

  credits     from the staff rolls (design/credits-analysis/people.json): how many games,
              which departments how often, when the person first led, directed, produced -
              a rule-written line, no model involved
  expertise   a few words: the departments the rolls show, plus what the interviews add
  summary     three to five sentences on the person's craft and contribution, with [n]
              marks pointing at the interviews they rest on
  citations   [n] -> the post (its file stem; the layout resolves the URL), title, date,
              publication, and one line on what that interview specifically tells

The summary and the citation lines are written by DeepSeek from the person's own words:
their speaking turns in the library's interview translations (up to a dozen entries spread
over the years, a few hundred characters each), never from anything outside the library.
A person with no interview gets the credits part only. Every model answer is cached in
data/cache_profiles/<slug>.json against a hash of its input, so a re-run only asks about
people whose material changed.
"""
import collections
import hashlib
import importlib.util
import io
import json
import re
import sys
import time
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_data" / "people_profiles.yml"
CACHE = ROOT / "data" / "cache_profiles"
FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)

_spec = importlib.util.spec_from_file_location("import_nom", ROOT / "tools" / "import-nom.py")
_nom = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_nom)

CAT_ZH = {"Dir": "总监/制作人", "Plan": "企划", "Prog": "程序", "Art": "美术", "Sound": "音乐", "Mgmt": "管理/协调",
          "Debug": "调试", "Loc/QA": "本地化/海外QA", "Thanks": "特别感谢", "Other": "其他"}
CAT_ORDER = ["Dir", "Plan", "Prog", "Art", "Sound", "Mgmt", "Debug", "Loc/QA", "Thanks", "Other"]
RANK_ZH = {1: "组长", 2: "部门总监", 3: "总监/制作人", 4: "执行制作人"}
BLOG_LAYOUTS = {"gamefreak-director", "gamefreak-legacy-blog"}
MAX_POSTS = 12          # interviews shown to the model
MAX_CHARS_PER_POST = 700
SYSTEM = ("你是宝可梦开发史料库的编辑，为人物页写「开发专长」。只依据给出的材料写，不补充材料之外的事实；"
          "平实、具体、不评价人品、不用感叹号；人名与作品名照给出的写法；只输出合法 JSON。")


# ---------------------------------------------------------------- the library
def load_posts():
    """each post's front matter, its kind, its people, and the rows spoken by each person"""
    posts = []
    for f in sorted((ROOT / "_posts").glob("*.md")):
        text = io.open(f, encoding="utf-8", errors="replace").read()
        m = FRONT.match(text)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        cats = fm.get("categories") or []
        cats = cats if isinstance(cats, list) else [cats]
        if fm.get("layout") in BLOG_LAYOUTS or "官方博客" in cats:
            kind = "blog"
        elif fm.get("translation_segments") or "扫描存档" in cats or "扫描翻译" in cats:
            kind = "scan"
        else:
            kind = "interview"
        items = fm.get("parallel_items") or fm.get("translation_segments") or []
        spoken = collections.defaultdict(list)
        prose = []          # every text row, for a piece with no speaker labels (a memoir, a report)
        for it in items:
            if not isinstance(it, dict) or not isinstance(it.get("translation"), str) or it.get("type") in ("image", "heading"):
                continue
            if it.get("speaker") and str(it["speaker"]).strip() not in ("caption", "body", "note", "image"):
                spoken[str(it["speaker"]).strip()].append(it["translation"].strip())
            prose.append(it["translation"].strip())
        pub = fm.get("publication") or (fm.get("source") or {}).get("publication") if isinstance(fm.get("source"), dict) else fm.get("publication")
        if not pub and isinstance(fm.get("source"), dict):
            pub = fm["source"].get("title")
        posts.append({"stem": f.stem, "title": str(fm.get("title") or f.stem), "date": str(fm.get("date") or f.stem[:10])[:10],
                      "kind": kind, "publication": str(pub or fm.get("outlet") or "").split("（")[0].strip(),
                      "author": str(fm.get("author") or ""), "prose": prose if not spoken else [],
                      "people": [str(x) for x in ((fm.get("entities") or {}).get("people") or [])], "spoken": spoken})
    return posts


# ---------------------------------------------------------------- the rolls
def credits_profile(a, games):
    """the rule-written credits part: games, departments, when the person first led"""
    if not a:
        return None
    year = {g["slug"]: g["year"] for g in games}
    title = {g["slug"]: g["title_zh"] for g in games}
    core = {g["slug"] for g in games if g.get("core")}
    slugs = [s for s in a.get("games", []) if s in year]
    if not slugs:
        return None
    slugs.sort(key=lambda s: (year[s], s))
    cat_games = collections.defaultdict(set)
    cat_years = collections.defaultdict(list)
    firsts = {}          # rank -> (year, game, role)
    for s in slugs:
        for r in a["roles"].get(s, []):
            cat_games[r["cat"]].add(s)
            cat_years[r["cat"]].append(year[s])
            if r["rank"] >= 1 and (r["rank"] not in firsts or year[s] < firsts[r["rank"]][0]):
                firsts[r["rank"]] = (year[s], title[s], r["role"])
    n_core = len([s for s in slugs if s in core])
    span = f"{year[slugs[0]]}–{year[slugs[-1]]}" if year[slugs[0]] != year[slugs[-1]] else str(year[slugs[0]])
    cats = sorted(cat_games, key=lambda c: (-len(cat_games[c]), CAT_ORDER.index(c) if c in CAT_ORDER else 99))
    real = [c for c in cats if c not in ("Thanks", "Other")]
    parts = [f"{CAT_ZH[c]} {len(cat_games[c])} 作（{min(cat_years[c])}–{max(cat_years[c])}）" if min(cat_years[c]) != max(cat_years[c])
             else f"{CAT_ZH[c]} {len(cat_games[c])} 作（{min(cat_years[c])}）" for c in real[:4]]
    line = f"署名 {len(slugs)} 作" + (f"（核心 {n_core} 作）" if n_core and n_core != len(slugs) else "") + f"，{span}"
    if parts:
        line += "：" + "、".join(parts)
    steps = []
    for rank in sorted(firsts, key=lambda r: (firsts[r][0], r)):      # in the order they happened
        y, g, role = firsts[rank]
        steps.append(f"{y} 年《{g}》起任{RANK_ZH[rank]}（{role}）")
    if steps:
        line += "；" + "，".join(steps)
    line += "。"
    expertise = [CAT_ZH[c] for c in real[:3] if len(cat_games[c]) >= 2 or len(slugs) <= 2]
    top_rank = max([r["rank"] for s in slugs for r in a["roles"].get(s, [])] + [0])
    if top_rank >= 3 and "总监/制作人" not in expertise:
        expertise.insert(0, "总监/制作人")
    return {"games": len(slugs), "core_games": n_core, "span": span, "line": line, "expertise": expertise,
            "categories": [{"cat": CAT_ZH[c], "games": len(cat_games[c])} for c in cats]}


# ---------------------------------------------------------------- the interviews
def own_words(person, aliases, posts):
    """the interview entries the person speaks in, oldest first, each with their words joined;
    a piece with no speaker labels that names the person (a memoir chapter, a lecture report)
    gives its prose instead, marked as the person's own writing or as a report"""
    names = {re.sub(r"\s+", "", n) for n in {person} | set(aliases)}
    surnames = {n.split()[-1].lower() for n in {person} | set(aliases) if " " in n}     # Miyamoto for Shigeru Miyamoto
    out = []
    for p in posts:
        if p["kind"] == "blog" or person not in p["people"]:
            continue
        rows = []
        for sp, texts in p["spoken"].items():
            s = re.sub(r"\s+", "", sp)
            if s in names or s.lower() in surnames or (len(s) >= 2 and any(n.startswith(s) and len(n) > len(s) for n in names)):
                rows.extend(texts)
        mode = "spoken"
        if not rows and p["prose"]:
            rows = p["prose"]
            mode = "written" if person in p["author"] else "reported"
        if rows:
            out.append((dict(p, mode=mode), rows))
    out.sort(key=lambda x: x[0]["date"])
    return out


def sample(entries, k):
    """k entries spread over the years, the first and the last always in"""
    if len(entries) <= k:
        return entries
    idx = sorted({round(i * (len(entries) - 1) / (k - 1)) for i in range(k)})
    return [entries[i] for i in idx]


def excerpt(rows, limit):
    out, n = [], 0
    for r in rows:
        r = re.sub(r"\s+", " ", r)
        if n + len(r) > limit:
            r = r[: max(0, limit - n)].rstrip() + ("…" if limit - n > 20 else "")
        if r:
            out.append(r)
            n += len(r)
        if n >= limit:
            break
    return " ".join(out)


def ask(person, credits_line, chosen):
    LABEL = {"spoken": f"{person}的发言摘录", "written": f"{person}本人撰文的摘录", "reported": "该篇正文摘录（第三方报道或转述，不是本人原话）"}
    material = "\n\n".join(f"[{i + 1}] 《{p['title']}》（{p['publication'] or '出处未记'}，{p['date']}）\n{LABEL[p.get('mode', 'spoken')]}：{excerpt(rows, MAX_CHARS_PER_POST)}"
                           for i, (p, rows) in enumerate(chosen))
    prompt = (f"人物：{person}\n"
              f"制作名单里的履历：{credits_line or '（无游戏署名记录）'}\n\n"
              f"以下是本站收录的访谈中{person}本人的发言摘录，编号 [n]：\n\n{material}\n\n"
              "请写：\n"
              "1. summary：3–5 句，概括这个人的开发专长、经手的领域、做事的方法或观点。凡是来自某篇访谈的说法，句末标 [n]（可多个）；来自履历的不用标。不要复述履历里的数字。\n"
              "2. expertise：3–6 个短语（每个 2–6 字），概括专长领域，如「战斗系统」「宝可梦设计」「音乐作曲」「本地化」。\n"
              "3. citations：对每一篇你引用过的访谈，写一句 detail（40 字以内），说明这篇访谈里关于此人的具体细节（一个事实、数字、决定或说法），不要泛泛。\n\n"
              "只引用给出的编号；来自第三方报道的内容要写成「据……报道」一类的转述而非本人说法；材料不足以判断的就不写。输出：{\"summary\":\"…\",\"expertise\":[\"…\"],\"citations\":[{\"n\":1,\"detail\":\"…\"}]}")
    raw = _nom.deepseek([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], max_tokens=1500)
    got = json.loads(raw)
    if not isinstance(got, dict) or not isinstance(got.get("summary"), str):
        raise ValueError("bad answer")
    return got


def profile_key(person, credits_line, chosen):
    h = hashlib.sha1()
    h.update(person.encode("utf-8"))
    h.update((credits_line or "").encode("utf-8"))
    for p, rows in chosen:
        h.update(p["stem"].encode("utf-8"))
        h.update(excerpt(rows, MAX_CHARS_PER_POST).encode("utf-8"))
    return h.hexdigest()[:16]


# ---------------------------------------------------------------- main
def main():
    args = sys.argv[1:]
    only = set()
    if "--only" in args:
        i = args.index("--only")
        only = {a for a in args[i + 1:] if not a.startswith("--")}
    use_llm = "--no-llm" not in args
    force = "--force" in args
    registry = yaml.safe_load(io.open(ROOT / "_data" / "people.yml", encoding="utf-8")) or []
    analysis = {p["key"]: p for p in json.loads((ROOT / "design" / "credits-analysis" / "people.json").read_text(encoding="utf-8"))}
    games = yaml.safe_load(io.open(ROOT / "_data" / "credits_games.yml", encoding="utf-8")) or []
    posts = load_posts()
    CACHE.mkdir(parents=True, exist_ok=True)
    existing = {}
    if OUT.exists() and not force:
        existing = {r["slug"]: r for r in (yaml.safe_load(io.open(OUT, encoding="utf-8")) or []) if r.get("slug")}
    out, asked, t0 = [], 0, time.time()
    people = [p for p in registry if p.get("kind") not in ("character", "figure") and p.get("slug")]
    for k, p in enumerate(people):
        if only and p["slug"] not in only:
            if p["slug"] in existing:
                out.append(existing[p["slug"]])
            continue
        name = p["name"]
        cr = credits_profile(analysis.get(p.get("credits_key") or ""), games)
        entries = own_words(name, p.get("aliases") or [], posts)
        n_blog = sum(1 for q in posts if q["kind"] == "blog" and name in q["people"])
        n_all = sum(1 for q in posts if q["kind"] != "blog" and name in q["people"])
        rec = {"name": name, "slug": p["slug"], "kind": p.get("kind") or "person",
               "interviews": {"entries": n_all, "spoken_in": len(entries), "columns": n_blog,
                              "first": entries[0][0]["date"][:4] if entries else None, "last": entries[-1][0]["date"][:4] if entries else None}}
        if cr:
            rec["credits"] = cr
        expertise = list(cr["expertise"]) if cr else []
        if entries and use_llm:
            chosen = sample(entries, MAX_POSTS)
            key = profile_key(name, cr["line"] if cr else "", chosen)
            cache = CACHE / f"{p['slug']}.json"
            got = None
            if cache.exists() and not force:
                c = json.loads(cache.read_text(encoding="utf-8"))
                if c.get("key") == key:
                    got = c["answer"]
            if got is None:
                print(f"  [{k + 1}/{len(people)}] {name}: {len(entries)} interviews, asking about {len(chosen)} ...", flush=True)
                try:
                    got = ask(name, cr["line"] if cr else "", chosen)
                except Exception as exc:
                    print(f"    failed: {exc}", file=sys.stderr)
                    got = None
                if got:
                    cache.write_text(json.dumps({"key": key, "answer": got, "posts": [q["stem"] for q, _ in chosen]}, ensure_ascii=False, indent=1), encoding="utf-8")
                    asked += 1
                    time.sleep(0.3)
            if got:
                rec["summary"] = got["summary"].strip()
                for e in got.get("expertise") or []:
                    e = str(e).strip()
                    # a word the rolls' chips already say (总监 beside 总监/制作人) adds nothing
                    plain = lambda s: re.sub(r"[/／\s·]", "", s)
                    if e and len(expertise) < 6 and not any(plain(e) in plain(x) or plain(x) in plain(e) for x in expertise):
                        expertise.append(e)
                cites = []
                seen = set()
                for c in got.get("citations") or []:
                    try:
                        n = int(c.get("n"))
                    except (TypeError, ValueError):
                        continue
                    if not 1 <= n <= len(chosen) or n in seen:
                        continue
                    seen.add(n)
                    q = chosen[n - 1][0]
                    cites.append({"n": n, "post": q["stem"], "title": q["title"], "date": q["date"], "publication": q["publication"] or None,
                                  "detail": str(c.get("detail") or "").strip() or None})
                # a mark in the summary that the model did not list still gets its post
                for n in {int(x) for x in re.findall(r"\[(\d+)\]", rec["summary"])}:
                    if 1 <= n <= len(chosen) and n not in seen:
                        q = chosen[n - 1][0]
                        cites.append({"n": n, "post": q["stem"], "title": q["title"], "date": q["date"], "publication": q["publication"] or None, "detail": None})
                cites.sort(key=lambda c: c["n"])
                rec["citations"] = cites
        elif p["slug"] in existing and existing[p["slug"]].get("summary") and not force:
            rec["summary"] = existing[p["slug"]]["summary"]
            rec["citations"] = existing[p["slug"]].get("citations") or []
            for e in existing[p["slug"]].get("expertise") or []:
                if e not in expertise:
                    expertise.append(e)
        if expertise:
            rec["expertise"] = expertise
        out.append(rec)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(
        "# 由 tools/build-people-profiles.py 生成：每个人物的开发专长——制作名单归纳的履历、访谈归纳的专长与要点（带出处）\n"
        + yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=1000))
    with_sum = sum(1 for r in out if r.get("summary"))
    with_cr = sum(1 for r in out if r.get("credits"))
    print(f"{OUT.relative_to(ROOT)}: {len(out)} people, {with_cr} with a credits line, {with_sum} with an interview summary; {asked} asked this run, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
