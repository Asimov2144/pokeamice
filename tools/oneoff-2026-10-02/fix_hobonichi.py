"""Tidy the two re-imported ほぼ日 1999 series (2026-10-02).

- Ambrella (nin3): a monologue by 小澤宗明 with the odd line by 内山; the part titles 「（第３回のN）…」 become headings.
- Jack and Beans (nin5): 岩田 / 宮本 / 糸井 talk, with the team's own comments set beside it ("山本洋一 ディレクター …").
  The importer hands a comment to whoever spoke last; here it goes to the staff member, and so do the paragraphs after it
  until the next labelled turn (the importer's `_explicit` flag in data/cache_web/<key>.items.json, same order as the post).
- a lone 「（岩田さん）」 under a picture is that picture's caption.
"""
import json
import re
import sys

import yaml

sys.stdout.reconfigure(encoding="utf-8")
ROOT = "P:/WEBSITE/pokeamice-main (1)/app-data-export/"
STAFF = re.compile(r"^(山本洋一|川瀬シゲゾー|猪ノ口幸治|山本正宣|町田武幸|関森一紀|加藤博孝|篠原)\s*(?:[（(][^）)]*[）)])?\s*(ディレクター|デザイナー|プログラマー|プランナー)")
CAPTION = re.compile(r"^（\S{1,8}さん）$")
NAMES = [("《皮卡丘你好啊》", "《皮卡丘你好吗》"), ("《皮卡丘你好》", "《皮卡丘你好吗》"), ("《宝可梦写真》", "《宝可梦随乐拍》"), ("《宝可梦快照》", "《宝可梦随乐拍》"),
         ("《宝可梦拍照》", "《宝可梦随乐拍》"), ("《宝可梦 Snap》", "《宝可梦随乐拍》"), ("《宝可梦Snap》", "《宝可梦随乐拍》")]


def load(path):
    text = open(path, encoding="utf-8").read()
    return yaml.safe_load(text.split("\n---\n")[0][4:])


def save(path, fm):
    open(path, "w", encoding="utf-8", newline="\n").write("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n")


def rename(fm):
    for x in fm["parallel_items"]:
        for k in ("translation", "caption"):
            if x.get(k):
                for a, b in NAMES:
                    x[k] = x[k].replace(a, b)
    for k in ("title", "display_title", "dek", "summary"):
        if fm.get(k):
            for a, b in NAMES:
                fm[k] = fm[k].replace(a, b)
    fm["tags"] = [t for t in fm["tags"] if t != "Game Freak"]


def captions(items):
    out = []
    for x in items:
        if out and out[-1].get("type") == "image" and CAPTION.match((x.get("original") or "").strip()):
            out[-1]["caption"] = x.get("translation") or x["original"]
            out[-1]["caption_original"] = x["original"]
            continue
        out.append(x)
    return out


# ---- Ambrella
p = ROOT + "_posts/1999-02-10-interview-hobonichi-1999-ambrella-ozawa.md"
fm = load(p)
items = fm["parallel_items"]
for k, x in enumerate(items):
    if x.get("type") is None and re.match(r"^（第３回の[１-５]）", x.get("original") or ""):
        items[k] = {"type": "heading", "level": 2, "original": x["original"], "translation": x["translation"]}
fm["parallel_items"] = captions(items)
rename(fm)
fm["title"] = "ほぼ日 1999：Ambrella 小泽宗明谈《皮卡丘你好吗》与语音识别游戏"
fm["publication"] = "ほぼ日刊イトイ新聞「樹の上の秘密基地」（1999 年 2 月 10 日—3 月 2 日连载 5 回）"
fm["interviewee"] = "小泽宗明（Ambrella 代表）、内山（Ambrella）"
fm["entities"]["people"] = ["小澤宗明"]
fm["source_kind"] = "media_feature"
save(p, fm)
print("ambrella", len(fm["parallel_items"]), "items,", sum(1 for x in fm["parallel_items"] if x.get("type") == "heading"), "headings")

# ---- Jack and Beans
key = "hobonichi-1999-jack-and-beans-snap"
p = ROOT + f"_posts/1999-05-13-interview-{key}.md"
fm = load(p)
items = fm["parallel_items"]
raw = json.load(open(ROOT + f"data/cache_web/{key}.items.json", encoding="utf-8"))
assert len(raw) == len(items), (len(raw), len(items))
current, moved = None, 0
for k, (x, r) in enumerate(zip(items, raw)):
    o = (x.get("original") or "").strip()
    if x.get("type") in ("image", "heading"):
        continue
    m = STAFF.match(o)
    if m:
        current = m.group(1)
    elif r.get("_explicit"):
        current = None
    if current:
        if x.get("speaker") != current:
            moved += 1
        x["speaker"], x["role"] = current, "answer"
    elif x.get("type") is None and not x.get("role"):
        # the labelled openings: 「（ ハル研究所代表取締役社長 岩田 聡さん 以下岩田）…」 / 「岩田聡さん：（以下岩田）」
        if re.match(r"^[（(].{0,30}岩田|^岩田聡さん", o):
            x["speaker"], x["role"] = "岩田聪", "answer"
        elif re.match(r"^[（(].{0,30}宮本", o):
            x["speaker"], x["role"] = "宫本茂", "answer"
fm["parallel_items"] = captions(items)
rename(fm)
fm["title"] = "ほぼ日 1999：岩田聪、宫本茂与 Jack and Beans 团队谈《宝可梦随乐拍》的诞生"
fm["publication"] = "ほぼ日刊イトイ新聞「樹の上の秘密基地」第 5 弹（1999 年 5 月 13 日—6 月 20 日连载 6 回）"
fm["interviewee"] = "岩田聪（HAL 研究所社长）、宫本茂（任天堂）、Jack and Beans 开发团队"
fm["entities"]["people"] = ["岩田聪", "宫本茂", "糸井重里"]
save(p, fm)
from collections import Counter  # noqa: E402

print("snap: moved", moved, Counter(x.get("speaker") for x in fm["parallel_items"] if x.get("role")).most_common())
