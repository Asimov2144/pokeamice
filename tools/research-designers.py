#!/usr/bin/env python3
"""宝可梦设计者页的补充调查：从 Bulbapedia 收集「谁设计了哪只」及其引用，和现有数据（gfworks 原表）对照。

  python tools/research-designers.py fetch     搜索 + 抓 wikitext 到缓存（默认 P:/WEBSITE/.cache/designers-research）
  python tools/research-designers.py parse     → archive/designers/bulbapedia-candidates.json（每条带原句 / 引用原文 / 链接）
  python tools/research-designers.py compare   和 _data/pokemon_designers.yml 对照：新的（宝可梦, 设计者）对、新出处、冲突

两类页面：
  人物页「The following is a list of Pokémon designed by …」后面的表：每格一只，格里的 <ref> 是出处；
  宝可梦页「Design and development」里写 "designed by [[某人]]" / "designer" 的句子。
Bulbapedia 是二手整理，引用才是证据：compare 只把带外部链接或纸本出处的条目当候选，没有引用的单列。
"""
import argparse
import html
import json
import re
import sys
import time
import unicodedata
from collections import defaultdict
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path("P:/WEBSITE/.cache/designers-research")
OUT = ROOT / "archive" / "designers" / "bulbapedia-candidates.json"
DATA = ROOT / "_data" / "pokemon_designers.yml"
API = "https://bulbapedia.bulbagarden.net/w/api.php"
UA = {"User-Agent": "pokeamice-research/1.0 (pokemon designers study)"}
SPECIES = Path("P:/WEBSITE/.cache/52poke-out/species.lite.json")


def search(q):
    out, off = [], 0
    while True:
        r = requests.get(API, params={"action": "query", "list": "search", "srsearch": q, "srlimit": 500, "sroffset": off,
                                      "srnamespace": 0, "format": "json", "srprop": ""}, headers=UA, timeout=60).json()
        out += [x["title"] for x in r["query"]["search"]]
        if "continue" not in r:
            return out
        off = r["continue"]["sroffset"]


def cmd_fetch(cache):
    cache.mkdir(parents=True, exist_ok=True)
    people = search('insource:"list of Pokémon designed by"')
    species = [t for q in ('insource:"designed by"', 'insource:"designer" insource:"Pokémon)"') for t in search(q)
               if t.endswith("(Pokémon)")]
    titles = sorted(set(people) | set(species))
    pages = {}
    for i in range(0, len(titles), 50):
        r = requests.get(API, params={"action": "query", "prop": "revisions", "rvprop": "content|timestamp", "rvslots": "main",
                                      "titles": "|".join(titles[i:i + 50]), "format": "json", "formatversion": 2, "redirects": 1},
                         headers=UA, timeout=120).json()
        for p in r["query"]["pages"]:
            if "revisions" in p:
                pages[p["title"]] = {"ts": p["revisions"][0]["timestamp"], "text": p["revisions"][0]["slots"]["main"]["content"]}
        time.sleep(1)
    (cache / "wiki").mkdir(exist_ok=True)
    (cache / "wiki" / "pages.json").write_text(json.dumps(pages, ensure_ascii=False), encoding="utf-8")
    (cache / "search.json").write_text(json.dumps({"person_lists": people}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(people)} 张人物页、{len(titles) - len(people)} 张宝可梦页 → {cache / 'wiki' / 'pages.json'}")


# ---------------------------------------------------------------- wikitext helpers
REF_DEF = re.compile(r"<ref\s+name\s*=\s*\"?([^\"/>]+?)\"?\s*>(.*?)</ref>", re.S)
REF_ANY = re.compile(r"<ref(?:\s+name\s*=\s*\"?([^\"/>]+?)\"?)?\s*(/>|>(.*?)</ref>)", re.S)


def ref_table(text):
    return {n.strip(): body.strip() for n, body in REF_DEF.findall(text)}


def refs_in(chunk, table):
    out = []
    for name, close, body in REF_ANY.findall(chunk):
        body = body.strip() if close != "/>" else table.get((name or "").strip(), "")
        if body and body not in out:
            out.append(body)
    return out


def plain(s):
    s = REF_ANY.sub("", s)
    s = re.sub(r"\{\{color2\|[^|{}]*\|(?:[^|{}]*\|)?([^|{}]*)\}\}", r"\1", s)     # {{color2|色|链接|文字}}：取最后一项
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"\{\{(?:pcolor|p|pkmn|tt|color2|DL|m|t|a|i|g|game|gen|ga|bp|pmd|OBP|mdc)\|([^|{}]*)[^{}]*\}\}", r"\1", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[https?://\S+\s+([^\]]*)\]", r"\1", s)
    s = re.sub(r"'''?|<[^>]+>", "", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def cite(body):
    """一条引用 → {text, urls}：纸本出处只有文字，网络出处带链接（存档链接也算）。"""
    urls = re.findall(r"https?://[^\s\]|<>]+", body)
    return {"text": plain(body), "urls": urls}


def cmd_parse(cache):
    pages = json.loads((cache / "wiki" / "pages.json").read_text(encoding="utf-8"))
    people = set(json.loads((cache / "search.json").read_text(encoding="utf-8"))["person_lists"])
    out = []
    for title, page in sorted(pages.items()):
        text, table = page["text"], ref_table(page["text"])
        if title in people:
            i = text.find("list of Pokémon designed by")
            end = re.search(r"\n===?[^=]", text[i:])          # 下一节（===Characters=== 是人物设计，不要）
            sect = text[i:i + end.start()] if end else text[i:]
            gen = ""
            for line in sect.split("\n"):
                g = re.search(r"\{\{color2\|[^|]*\|([^}]*)\}\}", line)
                if g and "colspan" in line or (g and line.strip().startswith("'''")):
                    gen = g.group(1)
                    continue
                if not line.startswith("|") or line.startswith(("|-", "|}", "|+")) or "[[File:" in line or "colspan" in line:
                    continue
                cell = re.sub(r"^\|\s*(?:style=\"[^\"]*\"\s*\|)?", "", line)
                # 名字是粗体那一段（Gigantamax<br>Gengar 这种形态词也在里面），粗体之后是括注（idea by …）；没有粗体就按 <br> 分
                bold = re.match(r"\s*'''(.*?)'''(.*)$", cell, re.S)
                head, rest = (bold.group(1), bold.group(2)) if bold else (re.split(r"<br\s*/?>", cell, maxsplit=1) + [""])[:2]
                name = plain(head)
                if not name:
                    continue
                note = plain(rest).strip(" ()")
                m = re.match(r"(.*?)\s*\(([^)]*)\)$", name)      # "Sneasler (and Shiny)" 这类括注
                if m:
                    name, note = m.group(1), (m.group(2) + ("; " + note if note else ""))
                out.append({"kind": "person-list", "page": title, "designer": title, "pokemon": name, "note": note, "group": gen,
                            "cites": [cite(b) for b in refs_in(cell, table)], "ts": page["ts"]})
        else:
            for m in re.finditer(r"[^\n.]*(?:designed by|designer|design was|designs? (?:of|for) [^.\n]* (?:was|were) (?:done|created|drawn))[^\n]*", text, re.I):
                line = m.group(0)
                linked = re.findall(r"\[\[([^|\]#]+)(?:\|[^\]]*)?\]\]", line)
                # 只要提到人的句子：链接到人物页，或者句子里写了 "designed by <大写名字>"
                named = re.findall(r"designed by (?:\[\[)?([A-Z][\w'ōūŌŪ.-]+(?: [A-Z][\w'ōūŌŪ.-]+)+)", line)
                if not linked and not named:
                    continue
                out.append({"kind": "species-sentence", "page": title, "pokemon": title.replace(" (Pokémon)", ""),
                            "sentence": plain(line)[:600], "linked": linked, "named": named,
                            "cites": [cite(b) for b in refs_in(line, table)], "ts": page["ts"]})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"{sum(o['kind'] == 'person-list' for o in out)} 条人物页表格、{sum(o['kind'] == 'species-sentence' for o in out)} 条宝可梦页句子 → {OUT.relative_to(ROOT)}")


# ---------------------------------------------------------------- compare
def nk(name):
    """人名比对键：去长音符、oh/ou/oo→o、uu→u，姓名顺序无关。"""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"[^a-z ]", "", s)
    s = re.sub(r"(?<=[aeiou])h(?![aeiouy])", "", s)          # Ohmura → omura（Ishihara 的 h 后面是元音，保留）
    s = s.replace("ou", "o").replace("oo", "o").replace("uu", "u")
    return " ".join(sorted(s.split()))


def cmd_compare():
    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    cands = json.loads(OUT.read_text(encoding="utf-8"))
    species = json.loads(SPECIES.read_text(encoding="utf-8"))
    en_names = {s["name"]["en"] for s in species}
    have = defaultdict(set)                       # (宝可梦英文名) → {设计者键}
    for d in data["designers"]:
        for p in d["pokemon"]:
            have[p["en"]].add(nk(d["en"]))
    known = {nk(d["en"]): d["en"] for d in data["designers"]}
    rows = []
    for c in cands:
        if c["kind"] == "person-list":
            pairs = [(c["pokemon"], c["designer"])]
        else:
            who = [w for w in c["linked"] if not w.endswith("(Pokémon)") and nk(w) and len(w.split()) >= 2] + c["named"]
            pairs = [(c["pokemon"], w) for w in dict.fromkeys(who)]
        for mon, who in pairs:
            status = "same" if nk(who) in have.get(mon, set()) else ("conflict" if have.get(mon) else "new")
            rows.append({"pokemon": mon, "designer": who, "status": status, "in_dex": mon in en_names,
                         "known_designer": nk(who) in known, "kind": c["kind"], "page": c["page"],
                         "cited": any(x["urls"] or x["text"] for x in c["cites"]), "c": c})
    by = defaultdict(list)
    for r in rows:
        by[r["status"]].append(r)
    for k in ("new", "conflict"):
        print(f"\n== {k}: {len(by[k])}")
        for r in sorted(by[k], key=lambda r: (r["designer"], r["pokemon"])):
            flag = ("" if r["in_dex"] else " [非图鉴名]") + ("" if r["cited"] else " [无引用]") + ("" if r["known_designer"] else " [原表无此人]")
            print(f"  {r['designer']:22} {r['pokemon']:28} {r['kind']:16}{flag}")
    print(f"\nsame: {len(by['same'])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fetch", "parse", "compare"])
    ap.add_argument("--cache", default=str(CACHE))
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    {"fetch": lambda: cmd_fetch(Path(a.cache)), "parse": lambda: cmd_parse(Path(a.cache)), "compare": cmd_compare}[a.cmd]()


if __name__ == "__main__":
    main()
