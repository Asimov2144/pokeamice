#!/usr/bin/env python3
"""语料里反复谈的、词表还没收的那些说法 —— 概念词表的候选。

    python tools/mine-concepts.py                 # 挖 + 问模型，写 design/concepts-candidates.json
    python tools/mine-concepts.py --no-llm        # 只挖，不问模型（免费）
    python tools/mine-concepts.py --min-df 20     # 提高门槛
    python tools/mine-concepts.py --force         # 不用缓存
    python tools/mine-concepts.py --audit 60      # 抽 60 篇让模型当第二个读者，量漏标与词表缺口

词表 data/lore_tables/concepts.yml 是人写的，这个工具不改它——它只负责「你漏了什么」：

  1. 逐段扫全部 1,172 篇，按 Apriori 数 2–6 字的中日文说法各出现在几篇里（df）；
  2. 去掉几乎总被更长说法带着出现的（保留最长的那个）、虚词收尾的、词表已经收了的写法，
     以及人名 / 宝可梦名 / 作品名 / 地名（那些是实体，不是概念）；
  3. 剩下的按 df 排序，分批交给 DeepSeek 判：这是不是「开发者会谈的一件事」，若是，归到哪一面、
     叫什么、一句说明、哪些候选说法是同一个概念；
  4. 写出 design/concepts-candidates.json（带每条的 df 与两句原文）和一段可以直接贴进词表的
     YAML（design/concepts-candidates.yml）。收哪些由人定。

模型只用来**归拢候选写法**，不参与标注：标注一律按人定下来的词表逐段命中（build-post-lore.py --concepts）。
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import io
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "data" / "lore_tables"
CACHE = ROOT / "data" / "cache_concepts"
OUT_JSON = ROOT / "design" / "concepts-candidates.json"
OUT_YML = ROOT / "design" / "concepts-candidates.yml"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bp = _load("build_post_lore", ROOT / "tools" / "build-post-lore.py")
nom = _load("import_nom", ROOT / "tools" / "import-nom.py")

CJK = re.compile(r"[一-鿿぀-ヿ]+")
#  虚词、代词、量词：概念不会从这些字起或到这些字止
EDGE = set("的了是在和也就这那我你他她它们很但都有之其所而及或等还又再只不没把被从与如若因由于到过着地得更最太已将曾才每各些呢吗吧啊么请让使给对能会要想说看做为以并如即则却像比再更好多少一二三两个位次件种样件回点边下上中前后里外来去")
INSIDE = set("的了是呢吗吧啊么，。！？、；：（）「」『』…—")
SYSTEM = ("你是宝可梦开发史料库的编辑，正在整理一份「概念词表」：开发者在访谈里反复谈的那些事"
          "（设计上的难题、手艺、流程、机能限制、面向谁做、商业与社会的事）。只输出合法 JSON。")


def load_vocab() -> tuple[set, dict]:
    raw = yaml.safe_load(io.open(TABLES / "concepts.yml", encoding="utf-8")) or {}
    covered = set()
    for ent in raw.get("concepts") or []:
        for alias in ent.get("aliases") or []:
            covered.add(str(alias))
        for word in (ent.get("with") or []) + (ent.get("avoid") or []):
            covered.add(str(word))
    return covered, raw.get("facets") or {}


def load_entities() -> set:
    """人名 / 宝可梦名 / 作品名 / 地名：这些是实体，词表不收"""
    names = set()
    table = json.load(io.open(TABLES / "pokemon_names.json", encoding="utf-8"))
    names.update(table.get("names") or {})
    places = json.load(io.open(TABLES / "tour_places.json", encoding="utf-8"))
    for row in places.get("places") or []:
        for key in ("name", "name_zh", "name_ja", "area"):
            if row.get(key):
                names.add(str(row[key]))
        names.update(str(a) for a in (row.get("aliases") or []))
    people = yaml.safe_load(io.open(ROOT / "_data" / "people.yml", encoding="utf-8")) or []
    for row in people if isinstance(people, list) else people.values():
        if not isinstance(row, dict):
            continue
        for key in ("name", "name_zh", "name_ja", "name_en"):
            if row.get(key):
                names.add(str(row[key]))
        names.update(str(a) for a in (row.get("aliases") or []))
    works = yaml.safe_load(io.open(ROOT / "_data" / "works.yml", encoding="utf-8")) or []
    for row in works if isinstance(works, list) else works.values():
        if isinstance(row, dict):
            for key in ("name", "title", "title_zh", "title_ja"):
                if row.get(key):
                    names.add(str(row[key]))
    return {n for n in names if n}


def runs_of(posts: list) -> list:
    out = []
    for post in posts:
        runs = []
        for seg in post["segs"]:
            text = bp.seg_text(seg)
            if text:
                runs.extend(CJK.findall(text))
        out.append(runs)
    return out


def mine(runs_per_post: list, min_df: int, longest: int = 6) -> dict:
    """Apriori：先数两个字的，再只数「两头都还留着」的三个字的，以此类推"""
    levels = {}
    prev = None
    for n in range(2, longest + 1):
        counts = collections.Counter()
        for runs in runs_per_post:
            local = set()
            for run in runs:
                for i in range(len(run) - n + 1):
                    gram = run[i:i + n]
                    if prev is not None and (gram[:-1] not in prev or gram[1:] not in prev):
                        continue
                    local.add(gram)
            counts.update(local)
        keep = {g: v for g, v in counts.items() if v >= min_df}
        levels[n] = keep
        prev = set(keep)
        print(f"  n={n}: {len(counts)} seen, {len(keep)} over df {min_df}", flush=True)
    return levels


def prune(levels: dict, covered: set, entities: set) -> list:
    every = {}
    for keep in levels.values():
        every.update(keep)
    out = []
    for gram, df in every.items():
        if gram[0] in EDGE or gram[-1] in EDGE or (set(gram) & INSIDE):
            continue
        #  几乎总跟着更长的说法出现 -> 留长的那个
        longer = levels.get(len(gram) + 1) or {}
        if any((ext[1:] == gram or ext[:-1] == gram) and cnt >= 0.75 * df for ext, cnt in longer.items()):
            continue
        if gram in covered or any(gram in alias or alias in gram for alias in covered if len(alias) >= 2):
            continue
        if gram in entities or any(gram in name for name in entities if len(name) >= len(gram)):
            continue
        out.append((gram, df))
    out.sort(key=lambda kv: (-kv[1], kv[0]))
    return out


def samples_for(words: list, posts: list, per: int = 2) -> dict:
    want = {w: [] for w in words}
    for post in posts:
        for seg in post["segs"]:
            text = bp.seg_text(seg)
            if not text:
                continue
            for word in words:
                rows = want[word]
                if len(rows) >= per or word not in text:
                    continue
                at = text.find(word)
                rows.append({"post": post["id"], "seg": seg["n"], "text": text[max(0, at - 40):at + 80]})
    return want


def ask(batch: list, facets: dict, force: bool) -> list:
    words = ", ".join(f"{w}（{df}篇）" for w, df in batch)
    prompt = (
        "下面是宝可梦开发史料（开发者访谈、官方博客、杂志扫描件）语料里的高频说法，括号里是出现在几篇文章里。\n"
        "挑出其中**能当概念用**的：开发者会专门谈的一件事——设计上的取舍、某项手艺、开发流程、机能限制、"
        "面向谁做、商业或社会层面的话题。\n"
        "不要：人名 / 作品名 / 公司名 / 地名（实体），泛泛的动词与形容词（「非常」「做出来」），"
        "零碎的片段（「个世界」「为一」），日文助词串，和只是在描述某一件具体事情的说法。\n"
        "同一个概念的几种说法并成一条，aliases 只写**语料里出现过的**那几个说法（就是我给你的这些词，"
        "可以只收其中一部分）。name 用中文，四到八个字；gloss 一句话说这个概念指什么，平实，不用感叹号。\n"
        f"facet 从这些里选一个：{json.dumps(facets, ensure_ascii=False)}\n\n"
        '输出：{"concepts":[{"id":"英文小写连字符","name":"中文名","facet":"key","gloss":"一句话",'
        '"aliases":["写法1","写法2"]}]}\n\n'
        f"候选：{words}")
    key = hashlib.sha1(prompt.encode("utf-8")).hexdigest()[:16]
    CACHE.mkdir(parents=True, exist_ok=True)
    cache = CACHE / f"{key}.json"
    if cache.exists() and not force:
        return json.load(io.open(cache, encoding="utf-8")).get("concepts") or []
    raw = nom.deepseek([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], max_tokens=3000)
    try:
        got = json.loads(raw)
    except ValueError:
        start, end = raw.find("{"), raw.rfind("}")
        got = json.loads(raw[start:end + 1]) if start >= 0 < end else {"concepts": []}
    io.open(cache, "w", encoding="utf-8", newline="\n").write(json.dumps(got, ensure_ascii=False))
    return got.get("concepts") or []


def audit(n: int, force: bool) -> int:
    """抽 n 篇，让模型当第二个读者：这篇谈的概念，从词表里选；词表里没有的另说。

    用来量两件事——规则标注漏了多少（模型点出来、页面上没标的），以及词表本身有没有窟窿
    （模型反复提、词表里确实没有的）。它不写任何标注，只写 design/concepts-audit.json。"""
    vocab = bp.load_concepts()
    by_id = {ent["id"]: ent for ent in vocab}
    listing = "\n".join(f"{ent['id']} = {ent['name']}（{ent['gloss']}）" for ent in vocab)
    posts = bp.load_posts()
    chosen = bp.pilot(posts, n)
    print(f"{len(chosen)} posts sampled of {len(posts)}")
    rows = []
    miss = collections.Counter()
    extra = collections.Counter()
    for i, post in enumerate(chosen, 1):
        rec = bp.read_record(post["id"])
        marked = [r["id"] for r in ((rec.get("facets") or {}).get("concepts") or [])]
        body = bp.body_for_model(post)
        prompt = ("下面是一篇宝可梦开发史料（访谈 / 博客 / 杂志扫描件）的正文，按段编号。\n"
                  "一、从词表里挑出这篇**确实在谈**的概念（不是随口带过一句的），最多六个，写 id。\n"
                  "二、如果有这篇明显在谈、词表里却没有的概念，最多两个，写中文名和一句说明；没有就给空数组。\n\n"
                  f"词表：\n{listing}\n\n"
                  '输出：{"concepts":["id",…],"missing":[{"name":"中文名","gloss":"一句话","seg":段号}]}\n\n'
                  f"《{post['title']}》（{post['date']}）\n{body}")
        key = hashlib.sha1(prompt.encode("utf-8")).hexdigest()[:16]
        CACHE.mkdir(parents=True, exist_ok=True)
        cache = CACHE / f"audit-{key}.json"
        if cache.exists() and not force:
            got = json.load(io.open(cache, encoding="utf-8"))
        else:
            try:
                raw = nom.deepseek([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}], max_tokens=1200)
                got = json.loads(raw)
                io.open(cache, "w", encoding="utf-8", newline="\n").write(json.dumps(got, ensure_ascii=False))
            except Exception as exc:                                     # noqa: BLE001
                print(f"  {i:>3}/{len(chosen)} {post['id'][:44]}  failed: {exc}")
                continue
            time.sleep(0.3)
        said = [c for c in (got.get("concepts") or []) if c in by_id]
        agreed = [c for c in said if c in marked]
        missed = [c for c in said if c not in marked]
        for c in missed:
            miss[c] += 1
        for row in got.get("missing") or []:
            name = str((row or {}).get("name") or "").strip()
            if name:
                extra[name] += 1
        rows.append({"post": post["id"], "kind": post["kind"], "marked": marked, "model": said,
                     "agreed": agreed, "model_only": missed, "missing": got.get("missing") or []})
        print(f"  {i:>3}/{len(chosen)} {post['id'][:44]}  标注 {len(marked)} · 模型 {len(said)} · 都认 {len(agreed)}")
    hit = sum(len(r["agreed"]) for r in rows)
    said = sum(len(r["model"]) for r in rows)
    out = {"generated": date.today().isoformat(), "posts": len(rows),
           "counts": {"model_picks": said, "also_marked": hit, "model_only": said - hit,
                      "recall": round(hit / said, 3) if said else 0,
                      "marked_total": sum(len(r["marked"]) for r in rows)},
           "model_only_top": [{"id": c, "n": n, "name": by_id[c]["name"]} for c, n in miss.most_common(20)],
           "missing_named": [{"name": c, "n": n} for c, n in extra.most_common(30)],
           "rows": rows}
    path = ROOT / "design" / "concepts-audit.json"
    io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"模型点了 {said} 次，其中 {hit} 次页面上也标了（{out['counts']['recall']:.0%}）；"
          f"词表外的说法 {len(extra)} 种 → {path.relative_to(ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", type=int, default=0, help="抽 N 篇让模型当第二个读者，量漏标与词表缺口")
    ap.add_argument("--min-df", type=int, default=12)
    ap.add_argument("--top", type=int, default=1500, help="交给模型的候选上限")
    ap.add_argument("--min-len", type=int, default=3, help="交给模型的最短说法（两个字的词表里基本都有了）")
    ap.add_argument("--batch", type=int, default=60)
    ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.audit:
        return audit(args.audit, args.force)

    covered, facets = load_vocab()
    entities = load_entities()
    print(f"词表已收 {len(covered)} 个写法，实体名 {len(entities)} 个")
    posts = bp.load_posts()
    print(f"{len(posts)} posts")
    levels = mine(runs_of(posts), args.min_df)
    cand = prune(levels, covered, entities)
    print(f"候选 {len(cand)} 个（df ≥ {args.min_df}，去掉词表已收与实体名）")
    print("  头 40：", ", ".join(f"{w}·{d}" for w, d in cand[:40]))

    proposed = []
    if not args.no_llm:
        head = [(w, d) for w, d in cand if len(w) >= args.min_len][:args.top]
        for start in range(0, len(head), args.batch):
            batch = head[start:start + args.batch]
            print(f"  asking {start + 1}-{start + len(batch)} / {len(head)} ...", flush=True)
            try:
                proposed.extend(ask(batch, facets, args.force))
            except Exception as exc:                                     # noqa: BLE001
                print(f"    batch failed: {exc}")
            time.sleep(0.3)

    df = dict(cand)
    seen_ids = set()
    rows = []
    for got in proposed:
        cid = str(got.get("id") or "").strip()
        aliases = [str(a).strip() for a in (got.get("aliases") or []) if str(a).strip()]
        aliases = [a for a in aliases if a in df]                        # 只留语料里真有的写法
        if not cid or not aliases or cid in seen_ids:
            continue
        seen_ids.add(cid)
        rows.append({"id": cid, "name": (got.get("name") or "").strip(), "facet": (got.get("facet") or "").strip(),
                     "gloss": (got.get("gloss") or "").strip(), "aliases": aliases,
                     "df": max(df.get(a, 0) for a in aliases)})
    rows.sort(key=lambda r: -r["df"])
    look = samples_for([a for r in rows for a in r["aliases"]][:600], posts)
    for row in rows:
        row["samples"] = [s for a in row["aliases"] for s in look.get(a, [])][:3]

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {"generated": date.today().isoformat(), "min_df": args.min_df,
               "counts": {"candidates": len(cand), "asked": min(len(cand), args.top) if not args.no_llm else 0,
                          "proposed": len(rows)},
               "unused_candidates": [{"w": w, "df": d} for w, d in cand[:400]],
               "proposed": rows}
    io.open(OUT_JSON, "w", encoding="utf-8", newline="\n").write(json.dumps(payload, ensure_ascii=False, indent=1) + "\n")

    block = ["# tools/mine-concepts.py 提的候选（模型归拢，没人看过）。挑要收的贴进 data/lore_tables/concepts.yml。\n"]
    for row in rows:
        block.append(f"  - id: {row['id']}\n    name: {row['name']}\n    facet: {row['facet']}\n"
                     f"    gloss: {row['gloss']}\n    aliases: [{', '.join(row['aliases'])}]\n"
                     f"    status: draft\n    note: 语料 {row['df']} 篇（mine-concepts 提）\n")
    io.open(OUT_YML, "w", encoding="utf-8", newline="\n").write("\n".join(block))
    print(f"提了 {len(rows)} 条候选概念 → {OUT_JSON.relative_to(ROOT)} / {OUT_YML.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
