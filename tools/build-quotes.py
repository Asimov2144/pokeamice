"""A sentence a day: the lines in the interviews worth reading on their own.

    python tools/build-quotes.py                       # every interview and scan (blogs left out)
    python tools/build-quotes.py --only iwata-asks-xy  # posts whose file name contains this
    python tools/build-quotes.py --limit 5             # the first N posts that would be asked
    python tools/build-quotes.py --force               # ignore the cache

Writes _data/quotes.yml, the pool the home page's 今日一句 card (home-quote.html) and the
/quotes/ page draw from. For each post the candidates are the interviewees' own answers
(speaker = a registered person), 30-260 characters of translation with the original beside
it; the question before each answer goes along as context. DeepSeek picks two to four
per post - a concrete fact, number, decision or first time, something against
expectation, or something simply well said - and writes for each:

  hook   one line (<= 30 chars) in one of two forms: a question the line itself answers
         (为什么《黑·白》要放弃全部旧宝可梦？) or the speaker's words as a headline
         (增田：我们把自己想象成小学一年级生); nothing from outside the material
  why    one or two sentences on why the line matters or what it refers to
  more   what the library can add: another passage of the same piece, a person, a work
         or a term the site has - names the script turns into links, the rest is cut

Every quote carries the post's file stem and the row's 1-based index, which is the row's
anchor on the page (#segment-N in interview-editorial, parallel-translation and
scan-translation); the layouts resolve URL, cover and avatar at build time. Answers are
cached in data/cache_quotes/<stem>.json by a hash of the candidates, so a re-run only
asks about new or changed posts. design/quotes-review.txt lists every hook per post for
a read-through; an id put under `rejected:` at the top of quotes.yml stays out.
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
OUT = ROOT / "_data" / "quotes.yml"
REVIEW = ROOT / "design" / "quotes-review.txt"
CACHE = ROOT / "data" / "cache_quotes"
FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)
BLOG_LAYOUTS = {"gamefreak-director", "gamefreak-legacy-blog"}
MIN_ZH, MAX_ZH = 30, 260
MAX_CANDIDATES = 60
SYSTEM = ("你是宝可梦开发史料库的编辑，从一篇访谈里挑出值得单独拿出来读的句子，并为每句写一行钩子。"
          "只依据给出的材料，不补充材料之外的事实；钩子不夸张、不悬念式吊胃口、不用感叹号；人名与作品名照给出的写法；只输出合法 JSON。")

_spec = importlib.util.spec_from_file_location("import_nom", ROOT / "tools" / "import-nom.py")
_nom = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_nom)


# ---------------------------------------------------------------- the library
def registry():
    people = yaml.safe_load(io.open(ROOT / "_data" / "people.yml", encoding="utf-8")) or []
    names, alias_of = {}, {}
    for p in people:
        if p.get("kind") in ("character", "figure"):
            continue
        names[p["name"]] = p
        for a in p.get("aliases") or []:
            alias_of[re.sub(r"\s+", "", a)] = p["name"]
            if " " in a and re.match(r"^[A-Za-z' .-]+$", a):
                alias_of.setdefault(a.split()[-1].lower(), p["name"])      # Masuda for Junichi Masuda
    works = [w["name"] for w in (yaml.safe_load(io.open(ROOT / "_data" / "works.yml", encoding="utf-8")) or []) if w.get("name")]
    terms = []
    site = ROOT / "design" / "glossary-site.json"
    if site.exists():
        for e in json.load(io.open(site, encoding="utf-8")).get("entries", []):
            if e.get("category") in ("开发", "组织", "职务", "刊物", "corpus") and len(e.get("target", "")) >= 2:
                terms.append(e["target"])
    return names, alias_of, works, terms


def load_posts():
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
        if fm.get("layout") in BLOG_LAYOUTS or "官方博客" in cats or fm.get("search") is False:
            continue
        items = fm.get("parallel_items") or fm.get("translation_segments") or []
        if not items:
            continue
        pub = fm.get("publication") or ""
        if not pub and isinstance(fm.get("source"), dict):
            pub = fm["source"].get("publication") or fm["source"].get("title") or ""
        pub = str(pub or fm.get("outlet") or "").split("（")[0].strip()
        ents = fm.get("entities") or {}
        posts.append({"stem": f.stem, "title": str(fm.get("title") or f.stem), "date": str(fm.get("date") or f.stem[:10])[:10],
                      "publication": pub, "people": [str(x) for x in (ents.get("people") or [])], "author": str(fm.get("author") or ""),
                      "works": [str(x) for x in (ents.get("works") or [])], "items": items,
                      "lang": str(fm.get("original_lang") or "ja")})
    return posts


def speaker_name(sp, post_people, names, alias_of):
    """the registered person a speaker label stands for, or None for the interviewer and the chrome"""
    s = re.sub(r"\s+", "", str(sp or ""))
    if not s or s in ("caption", "body", "note", "image", "──", "—", "提问", "全员"):
        return None
    if s in names:
        return s
    if s in alias_of:
        return alias_of[s]
    if s.lower() in alias_of and alias_of[s.lower()] in post_people:
        return alias_of[s.lower()]
    for n in post_people:
        if n not in names:
            continue
        if " " in n and s.lower() == n.split()[-1].lower():      # Miyamoto for Shigeru Miyamoto
            return n
        if len(s) >= 2 and n.startswith(s):                       # 增田 for 增田顺一
            return n
    return None


def candidates(post, names, alias_of):
    out, prev_q = [], ""
    labelled = any(isinstance(it, dict) and it.get("speaker") for it in post["items"])
    # a piece with no speaker labels is its author's own writing (a memoir chapter): every row is theirs;
    # a feature or a report with no labels speaks as the publication - the card says so
    author = next((n for n in names if n and n in post["author"] and n in post["people"]), None) if not labelled else None
    if not labelled and not author:
        author = f"{post['publication'] or '本文'}（报道）"
    for i, it in enumerate(post["items"], 1):
        if not isinstance(it, dict):
            continue
        t = it.get("type") or "paragraph"
        if t in ("image", "heading"):
            continue
        zh, ja = it.get("translation"), it.get("original")
        if not (isinstance(zh, str) and isinstance(ja, str) and zh.strip() and ja.strip()):
            continue
        who = speaker_name(it.get("speaker"), post["people"], names, alias_of) or author
        if not who:
            prev_q = re.sub(r"\s+", " ", zh.strip())[:120]
            continue
        z = re.sub(r"\s+", " ", zh.strip())
        if MIN_ZH <= len(z) <= MAX_ZH:
            out.append({"i": i, "who": who, "q": prev_q, "zh": z, "ja": re.sub(r"\s+", " ", ja.strip()), "note": it.get("note") or ""})
        prev_q = ""
    if len(out) > MAX_CANDIDATES:
        idx = sorted({round(k * (len(out) - 1) / (MAX_CANDIDATES - 1)) for k in range(MAX_CANDIDATES)})
        out = [out[k] for k in idx]
    return out


# ---------------------------------------------------------------- the model
def ask(post, cands):
    want = "1–2" if len(cands) <= 8 else "2–4"
    payload = [{"i": c["i"], "who": c["who"], "q": c["q"], "text": c["zh"]} for c in cands]
    prompt = (f"访谈：《{post['title']}》（{post['publication'] or '出处未记'}，{post['date']}）\n"
              f"候选句（i 是行号，who 说话人，q 是它回答的提问，text 是这句译文）：\n{json.dumps(payload, ensure_ascii=False)}\n\n"
              f"从中挑 {want} 句最值得单独拿出来读的：有具体事实、数字、决定或「第一次」；或与常识相反；或说得漂亮、能独立成立。"
              "寒暄、过渡、离开上下文就看不懂的不要。对每句写：\n"
              "hook：一行钩子，30 字以内，两种体裁二选一——疑问句（这句话本身就能回答的问题，如「为什么《黑·白》要放弃全部旧宝可梦？」）"
              "或引言式（「说话人：原话精简」，如「增田：我们把自己想象成小学一年级生」）；不许加材料之外的事实，不许悬念式吊胃口。\n"
              "why：一两句（60 字内），这句为什么重要、说的是什么背景。\n"
              "more：一两句（80 字内），从这篇里能延伸看的另一处，或相关的人物/作品/术语（只写材料与本站语料里确有的名字）；没有就留空字符串。\n"
              "kind：question 或 quote。\n\n"
              "输出：{\"picks\":[{\"i\":行号,\"kind\":\"question\",\"hook\":\"…\",\"why\":\"…\",\"more\":\"…\"}]}")
    raw = _nom.deepseek([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], max_tokens=1200)
    got = json.loads(raw)
    picks = got.get("picks") if isinstance(got, dict) else None
    if not isinstance(picks, list):
        raise ValueError("no picks")
    return picks


def link_entities(text, post, names, works, terms):
    """the people, works and terms the site has that the text names: [{type, name}]"""
    links = []
    for n in sorted(names, key=len, reverse=True):
        if len(n) >= 2 and n in text and (n in post["people"] or len(n) >= 3):
            links.append({"type": "person", "name": n, "slug": names[n].get("slug")})
    for w in sorted(works, key=len, reverse=True):
        if w in text:
            links.append({"type": "work", "name": w})
    for t in sorted(terms, key=len, reverse=True):
        if len(t) >= 3 and t in text and not any(t in l["name"] for l in links):
            links.append({"type": "term", "name": t})
    seen, out = set(), []
    for l in links:
        if l["name"] not in seen and not any(l["name"] != o["name"] and l["name"] in o["name"] for o in links):
            seen.add(l["name"])
            out.append(l)
    return out[:5]


def key_of(cands):
    h = hashlib.sha1()
    for c in cands:
        h.update(f"{c['i']}|{c['who']}|{c['zh']}".encode("utf-8"))
    return h.hexdigest()[:16]


# ---------------------------------------------------------------- main
def main():
    args = sys.argv[1:]
    only = args[args.index("--only") + 1] if "--only" in args else ""
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else 0
    force = "--force" in args
    names, alias_of, works, terms = registry()
    posts = load_posts()
    CACHE.mkdir(parents=True, exist_ok=True)
    existing = {"rejected": [], "quotes": []}
    if OUT.exists():
        existing = yaml.safe_load(io.open(OUT, encoding="utf-8")) or existing
    rejected = set(existing.get("rejected") or [])
    kept = {q["id"]: q for q in (existing.get("quotes") or [])}
    quotes, review, asked, t0 = [], [], 0, time.time()
    for post in posts:
        if only and only not in post["stem"]:
            quotes.extend(q for q in kept.values() if q["post"] == post["stem"])
            continue
        cands = candidates(post, names, alias_of)
        if not cands:
            continue
        key = key_of(cands)
        cache = CACHE / f"{post['stem']}.json"
        picks = None
        if cache.exists() and not force:
            c = json.loads(cache.read_text(encoding="utf-8"))
            if c.get("key") == key:
                picks = c["picks"]
        if picks is None:
            if limit and asked >= limit:
                continue
            print(f"  {post['stem'][:60]}: {len(cands)} candidates ...", flush=True)
            try:
                picks = ask(post, cands)
            except Exception as exc:
                print(f"    failed: {exc}", file=sys.stderr)
                continue
            cache.write_text(json.dumps({"key": key, "picks": picks}, ensure_ascii=False, indent=1), encoding="utf-8")
            asked += 1
            time.sleep(0.2)
        by_i = {c["i"]: c for c in cands}
        for p in picks:
            try:
                i = int(p.get("i"))
            except (TypeError, ValueError):
                continue
            c = by_i.get(i)
            hook = re.sub(r"\s+", " ", str(p.get("hook") or "")).strip(" 。")
            if not c or not hook or len(hook) > 36:
                continue
            # a name in the hook that the piece does not carry is invented
            if any(n in hook for n in names if len(n) >= 2 and n not in post["people"] and n != c["who"] and n not in c["zh"] and n not in c["q"]):
                continue
            qid = f"{post['stem']}#{i}"
            if qid in rejected:
                continue
            why = re.sub(r"\s+", " ", str(p.get("why") or "")).strip()
            more = re.sub(r"\s+", " ", str(p.get("more") or "")).strip()
            reported = c["who"].endswith("（报道）")
            q = {"id": qid, "post": post["stem"], "segment": i, "speaker": None if reported else c["who"], "reported": reported,
                 "kind": "question" if hook.endswith(("？", "?")) else "quote",
                 "hook": hook, "zh": c["zh"], "ja": c["ja"][:400], "lang": post["lang"], "year": int(post["date"][:4]),
                 "date": post["date"], "publication": post["publication"] or None, "title": post["title"],
                 "why": why or None, "more": more or None, "people": post["people"][:6], "works": post["works"][:4]}
            if c.get("note"):
                q["note"] = str(c["note"])[:200]
            if more:
                q["links"] = link_entities(more, post, names, works, terms)
            quotes.append(q)
    quotes.sort(key=lambda q: (q["date"], q["post"], q["segment"]))
    by_post = collections.OrderedDict()
    for q in quotes:
        by_post.setdefault(q["post"], []).append(f"  [{q['segment']}] {q['hook']} — {q['zh'][:60]}")
    review = [stem + "\n" + "\n".join(lines) for stem, lines in by_post.items()]
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(
        "# 由 tools/build-quotes.py 生成：首页「今日一句」与 /quotes/ 的句库。rejected 里的 id 重跑不再出现。\n"
        + yaml.safe_dump({"rejected": sorted(rejected), "quotes": quotes}, allow_unicode=True, sort_keys=False, width=1000))
    if review:
        REVIEW.parent.mkdir(exist_ok=True)
        io.open(REVIEW, "w", encoding="utf-8", newline="\n").write(f"{len(quotes)} quotes in {len(review)} posts\n\n" + "\n\n".join(review) + "\n")
    print(f"{OUT.relative_to(ROOT)}: {len(quotes)} quotes from {len(review)} posts; {asked} asked this run, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
