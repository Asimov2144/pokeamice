"""Find translations that say more than their original.

    python tools/audit-translation-inflation.py [--only <stem>] [--top N] [--json design/….json]

Reads every post's parallel_items and flags two things per row:

  long     the Chinese is much longer than this script's usual ratio would give
           (ratio / median >= 1.6, at least 25 characters over, original >= 20 characters).
           The median is measured on the corpus itself, per script of the original
           (kana -> ja, Latin -> en/es/fr…, Han without kana -> zh), not per post's
           original_lang, which is missing on some posts.
  phrase   an intensifier or stock flourish in the translation (近乎变态, 堪称, 简直, 神来之笔 …)
           with nothing in the original that licenses it. Each phrase lists the source-side
           cues that would (簡直 <- まるで / 本当に / literally …); a phrase without cues is
           flagged whenever it appears. Strong phrases are ones a faithful translation of an
           interview almost never needs; weak ones are common words that are only suspicious
           when unlicensed.

Nothing is edited. The output ranks posts by flagged rows; read the rows before deciding
anything — a long row can be a translator's note or an expanded proper name, and an
intensifier can be licensed by a word the cue list does not know.
"""
import glob
import io
import json
import os
import re
import statistics
import sys

import yaml

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONT = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)
KANA = re.compile(r"[぀-ヿ]")
LATIN = re.compile(r"[A-Za-z]")
HAN = re.compile(r"[一-鿿]")

# phrase: (weight, source cues that license it). weight 2 = strong, 1 = weak.
JA_VERY = r"とても|すごく|すご|非常|本当に|ほんと|めちゃ|かなり|大変|相当|極めて|実に|ものすごく|超"
EN_VERY = r"\b(very|really|extremely|incredibly|so|super|truly|highly|hugely)\b"
PHRASES = {
    # strong: invented intensity or characterisation
    "近乎变态": (2, r"変態|異常|pervert|obsess"),
    "变态": (2, r"変態|pervert|obsess"),
    "最恐怖": (2, r"怖|恐ろし|scar|terrif|fright"),
    "恐怖": (1, r"怖|恐|ホラー|scar|terrif|fright|horror|fear"),
    "大铁闸": (2, None),
    "铁闸": (2, None),
    "断舍离": (2, r"断捨離"),
    "神来之笔": (2, r"英断|ひらめ|閃|stroke of genius|brilliant"),
    "寸土寸金": (2, None),
    "每一字节": (2, r"1バイト|１バイト|every byte|each byte"),
    "精打细算": (2, r"節約|切り詰め|ケチ|save|squeez|tight"),
    "呕心沥血": (2, None),
    "殚精竭虑": (2, None),
    "绝密": (2, r"極秘|機密|秘密|top secret|classified|secret"),
    "秘史": (2, r"秘話|秘史|secret history"),
    "重磅": (2, None),
    "里程碑": (2, r"記念碑|節目|マイルストーン|milestone|landmark"),
    "惊天": (2, None),
    "史诗级": (2, r"壮大|epic"),
    "封神": (2, None),
    "神级": (2, r"神|godlike"),
    "炸裂": (2, r"爆発|炸裂|explo"),
    "降维打击": (2, None),
    "大杀器": (2, None),
    "天花板": (2, r"天井|ceiling"),
    "骨子里": (2, r"根っから|根は|骨の髄|at heart|deep down|to the core"),
    "全社": (1, r"全社|社内|会社中|社員全員|company|everyone|entire"),
    "叹为观止": (2, r"感嘆|圧巻|astonish|amaz|breathtaking"),
    "登峰造极": (2, None),
    "无与伦比": (2, r"比類|比べ物|唯一無二|unparallel|unmatched|unrivall|incomparab"),
    "淋漓尽致": (2, None),
    "浓墨重彩": (2, None),
    "当之无愧": (2, r"ふさわし|名実|deserv|worthy"),
    "举足轻重": (2, r"重要|大きな役割|important|crucial|key role"),
    "匠心": (2, r"職人|こだわり|craft|artisan"),
    "深度统领": (2, None),
    "底盘": (2, None),
    "核心骨干": (2, None),
    "造物者": (2, r"生みの親|創造|creator"),
    "堪称": (2, r"と言える|といえる|と呼べ|ともいえる|と言って|べき|まさに|can be called|could be called|so-called|dubbed|fair to say|arguably"),
    "可谓": (2, r"と言える|といえる|と言って|まさに|can be called|could be called|fair to say|arguably"),
    "简直": (1, r"まるで|まさに|本当に|ほとんど|もはや|みたい|ような|literally|practically|virtually|simply|just like|almost"),
    "毫无疑问": (2, r"間違いな|もちろん|確かに|疑い|undoubted|no doubt|without doubt|certainly|definitely|of course"),
    "毋庸置疑": (2, r"間違いな|疑い|undoubted|no doubt|without doubt|certainly"),
    "疯狂": (1, r"狂|クレイジー|夢中|熱狂|めちゃくちゃ|crazy|insane|mad|wild|frenz"),
    "极其": (1, JA_VERY + "|" + EN_VERY),
    "极度": (1, JA_VERY + "|" + EN_VERY),
    "无比": (1, JA_VERY + "|" + EN_VERY),
    "极致": (1, r"極|究極|最高|徹底|ultimate|utmost|perfect|extreme"),
    "彻底": (1, r"徹底|完全|すっかり|全く|まったく|根本|完璧|completely|thorough|entirely|totally|fully|utterly"),
    "绝对": (1, r"絶対|必ず|決して|absolute|definite|certainly|never|always"),
    "震撼": (1, r"衝撃|ショック|驚|圧倒|感動|shock|stun|blown away|amaz|astonish|impress|power"),
    "颠覆": (1, r"覆|ひっくり返|常識を|一変|overturn|revolution|upend|subvert|turn.*upside"),
    "前所未有": (1, r"初めて|はじめて|かつてな|前例|史上初|これまでにな|今までにな|never before|unprecedented|first ever|first time"),
    "苛刻": (1, r"厳し|うるさ|シビア|こだわ|strict|harsh|demanding|picky|particular"),
    "偏执": (1, r"執着|こだわ|偏執|obsess|paranoi|fixat"),
    "狂热": (1, r"熱狂|マニア|オタク|夢中|熱|fanatic|passion|enthusias|obsess|fever"),
    "心血": (1, r"心血|情熱|魂|苦労|力を注|passion|heart|effort|labou?r"),
    "灵魂": (1, r"魂|ソウル|soul|spirit"),
    "魔鬼": (1, r"鬼|悪魔|デビル|devil|demon|fiend"),
    "宛如": (1, r"まるで|ような|ように|みたい|like|as if|as though"),
    "犹如": (1, r"まるで|ような|ように|みたい|like|as if|as though"),
    "仿佛": (1, r"まるで|ような|ように|みたい|気が|like|as if|as though|seem"),
    "完完全全": (2, r"完全|全く|まったく|すべて|全部|completely|entirely|totally"),
    "不折不扣": (2, r"正真正銘|まさに|本物|true|genuine|real|through and through"),
}
PHRASE_RE = re.compile("|".join(sorted(map(re.escape, PHRASES), key=len, reverse=True)))


def script(text):
    if KANA.search(text):
        return "ja"
    letters = len(LATIN.findall(text))
    if letters and letters >= len(HAN.findall(text)):
        return "latin"
    if HAN.search(text):
        return "zh"
    return None


def plain(s):
    return re.sub(r"\s+", "", str(s or ""))


def rows():
    for path in sorted(glob.glob(f"{ROOT}/_posts/*.md")):
        t = io.open(path, encoding="utf-8").read()
        m = FRONT.match(t)
        if not m or "parallel_items" not in m.group(1):
            continue
        fm = yaml.safe_load(m.group(1)) or {}
        stem = os.path.basename(path)[:-3]
        for n, it in enumerate(fm.get("parallel_items") or [], 1):
            if not isinstance(it, dict):
                continue
            o, z = plain(it.get("original")), plain(it.get("translation"))
            if not o or not z or o == z or re.match(r"(/|https?:)\S*$", o):
                continue   # untranslated rows: names, picture paths, links
            yield stem, fm, n, it, o, z


def main():
    args = sys.argv[1:]
    only = args[args.index("--only") + 1] if "--only" in args else None
    top = int(args[args.index("--top") + 1]) if "--top" in args else 40
    out = args[args.index("--json") + 1] if "--json" in args else None
    data = list(rows())

    ratios = {}
    for _, _, _, _, o, z in data:
        s = script(o)
        if s and len(o) >= 40:
            ratios.setdefault(s, []).append(len(z) / len(o))
    median = {s: statistics.median(r) for s, r in ratios.items() if len(r) >= 30}

    posts = {}
    for stem, fm, n, it, o, z in data:
        if only and only not in stem:
            continue
        p = posts.setdefault(stem, {
            "post": stem, "title": fm.get("title"), "lang": fm.get("original_lang"),
            "rows": 0, "orig_chars": 0, "zh_chars": 0, "expected_zh": 0.0, "flags": []})
        p["rows"] += 1
        s = script(o)
        med = median.get(s)
        p["orig_chars"] += len(o)
        p["zh_chars"] += len(z)
        if med:
            p["expected_zh"] += med * len(o)
        flag = {"n": n, "type": it.get("type"), "speaker": it.get("speaker")}
        if med and len(o) >= 20:
            rel = len(z) / len(o) / med
            over = len(z) - med * len(o)
            if rel >= 1.6 and over >= 25:
                flag["long"] = {"rel": round(rel, 2), "over": int(over)}
        found = []
        for hit in dict.fromkeys(PHRASE_RE.findall(z)):
            weight, cues = PHRASES[hit]
            if cues and re.search(cues, o, re.I):
                continue
            if hit == "变态" and "近乎变态" in z:
                continue
            if hit == "铁闸" and "大铁闸" in z:
                continue
            found.append({"phrase": hit, "weight": weight})
        if found:
            flag["phrases"] = found
        if "long" in flag or found:
            flag["original"] = str(it.get("original"))
            flag["translation"] = str(it.get("translation"))
            p["flags"].append(flag)

    ranked = []
    for p in posts.values():
        f = p["flags"]
        p["long_rows"] = sum(1 for x in f if "long" in x)
        p["over_chars"] = sum(x["long"]["over"] for x in f if "long" in x)
        p["strong_phrases"] = sum(1 for x in f for y in x.get("phrases", []) if y["weight"] == 2)
        p["weak_phrases"] = sum(1 for x in f for y in x.get("phrases", []) if y["weight"] == 1)
        p["post_rel"] = round(p["zh_chars"] / p["expected_zh"], 2) if p["expected_zh"] else None
        p["score"] = round(p["long_rows"] + 2 * p["strong_phrases"] + 0.5 * p["weak_phrases"]
                           + p["over_chars"] / 200, 1)
        if f:
            ranked.append(p)
    ranked.sort(key=lambda p: -p["score"])

    print("medians (zh chars per original char):", {k: round(v, 3) for k, v in median.items()})
    print(f"{len(posts)} posts read, {len(ranked)} with at least one flag, "
          f"{sum(p['long_rows'] for p in ranked)} long rows, "
          f"{sum(p['strong_phrases'] for p in ranked)} strong / {sum(p['weak_phrases'] for p in ranked)} weak phrases")
    print(f"\n{'score':>6} {'long':>4} {'str':>4} {'weak':>4} {'rel':>5} {'rows':>4}  post")
    for p in ranked[:top]:
        print(f"{p['score']:6.1f} {p['long_rows']:4d} {p['strong_phrases']:4d} {p['weak_phrases']:4d} "
              f"{p['post_rel'] or 0:5.2f} {p['rows']:4d}  {p['post']}")
    if only:
        for p in ranked:
            for x in p["flags"]:
                tag = []
                if "long" in x:
                    tag.append(f"long x{x['long']['rel']} +{x['long']['over']}")
                tag += [y["phrase"] for y in x.get("phrases", [])]
                print(f"\n#{x['n']} [{', '.join(tag)}]\n  {x['original']}\n  {x['translation']}")
    if out:
        io.open(os.path.join(ROOT, out), "w", encoding="utf-8", newline="\n").write(
            json.dumps({"medians": median, "posts": ranked}, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main()
