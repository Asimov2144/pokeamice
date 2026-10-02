"""Tidy the 8 re-imported Creatures recruit posts (2026-10-02): profile block → one line, column titles → headings,
schedule headings back, duplicate initials / page-title heading out, front matter (who, what kind, the date's basis)."""
import glob
import re
import sys

import yaml

sys.stdout.reconfigure(encoding="utf-8")
ROOT = "P:/WEBSITE/pokeamice-main (1)/app-data-export/"

META = {
    "director": dict(title="Creatures 招聘网站：董事氏家淳子谈宝可梦 CG 工作室", who="氏家淳子（Creatures 董事、宝可梦CG工作室本部 执行美术总监）",
                     people=["氏家淳子"], page="役员访谈", orig_title="役員インタビュー：ポケモンという無限大の世界へ 〜ポケモンをつくり、育てる〜"),
    "sound-creator": dict(title="Creatures 招聘网站：声音创作者 M.H. 谈《宝可梦集换式卡牌游戏 Pocket》的声音", who="M.H.（Creatures 数字游戏开发 声音创作者，2023 年入职）"),
    "card-game-designer": dict(title="Creatures 招聘网站：游戏设计师 K.K. 谈宝可梦卡牌的游戏性与宝可梦的魅力", who="K.K.（Creatures 宝可梦卡牌游戏开发 游戏设计师）"),
    "card-illustration-production": dict(title="Creatures 招聘网站：插画制作进度管理 S.H. 谈宝可梦卡牌美术的使命", who="S.H.（Creatures 宝可梦卡牌游戏开发 插画制作进度管理）"),
    "cg-character-modeler": dict(title="Creatures 招聘网站：角色模型师 S.H. 谈宝可梦建模", who="S.H.（Creatures 宝可梦CG工作室 角色模型师）"),
    "cg-environment-artist": dict(title="Creatures 招聘网站：背景模型师 T.T. 谈《名侦探皮卡丘》的世界观", who="T.T.（Creatures 宝可梦CG工作室 背景模型师）"),
    "cg-animator": dict(title="Creatures 招聘网站：动画师 I.K. 谈宝可梦的动作表现", who="I.K.（Creatures 宝可梦CG工作室 动画师，2024 年入职）"),
    "pokepoke-product-planner": dict(title="Creatures 招聘网站：商品企划 F.Y. 谈《宝可梦集换式卡牌游戏 Pocket》", who="F.Y.（Creatures 宝可梦卡牌游戏开发 商品企划 / 副经理，2021 年入职）"),
}
NAMES = [("《PokéPoke》", "《宝可梦集换式卡牌游戏 Pocket》"), ("PokéPoke", "《宝可梦集换式卡牌游戏 Pocket》"),
         ("《宝可梦卡牌Pocket》", "《宝可梦集换式卡牌游戏 Pocket》"), ("《侦探皮卡丘》", "《名侦探皮卡丘》")]
TIME = re.compile(r"^\d{1,2}[:：]\d{2}[:：]")
END = re.compile(r"[。．.]$")


INITIALS = re.compile(r"^[A-Z]\.[A-Z]\.$")
WRONG = {"サウンドクリエイター 2023年入社", "ゲームデザイナー", "イラスト制作進行", "キャラクターモデラー", "背景モデラー",
         "アニメーター 2024年入社", "商品企画 / サブマネージャー 2021年入社"}


def short(x, n=40):
    o = x.get("original") or ""
    return x.get("type") is None and len(o) <= n and (not END.search(o) or bool(INITIALS.match(o)))


def norm(s):
    return re.sub(r"[\s　“”\"']", "", s or "")


for path in sorted(glob.glob(ROOT + "_posts/*-interview-creatures-recruit-*.md")):
    key = re.search(r"creatures-recruit-(.+)\.md$", path).group(1)
    meta = META[key]
    text = open(path, encoding="utf-8").read()
    fm = yaml.safe_load(text.split("\n---\n")[0][4:])
    items = fm["parallel_items"]
    log = []
    # 0. role lines the first pass took for column titles go back into the profile
    items = [{"original": x["original"], "translation": x["translation"]} if x.get("type") == "heading" and x["original"] in WRONG else x for x in items]
    # 1. the initials above the title, and the title itself repeated as the first heading
    if items and short(items[0], 16) and items[1].get("type") == "heading":
        log.append(f"drop lead {items[0]['original']}")
        items.pop(0)
    if items[0].get("type") == "heading" and (norm(items[0]["original"]) == norm(fm["original_title"]) or (meta.get("orig_title") and fm["original_title"] != meta["orig_title"])):
        log.append(f"drop title heading {items[0]['original'][:30]}")
        items.pop(0)
    # 2. the profile under the first picture: its short lines as one
    out, i = [], 0
    while i < len(items):
        x = items[i]
        if out and out[-1].get("type") == "image" and short(x):
            j = i
            while j < len(items) and short(items[j]):
                j += 1
            if j - i >= 2:
                run = items[i:j]
                out.append({"original": "　".join(r["original"].rstrip(" ／/").strip() for r in run),
                            "translation": "　".join((r.get("translation") or "").rstrip(" ／/").strip() for r in run)})
                log.append(f"profile {out[-1]['original'][:60]}")
                i = j
                continue
        out.append(x)
        i += 1
    items = out
    # 3. a column's title (a short line between a picture/paragraph and a paragraph) → heading 3
    for k, x in enumerate(items):
        if k + 1 < len(items) and short(x) and not TIME.match(x["original"]) and items[k + 1].get("type") is None \
                and len(items[k + 1].get("original") or "") > 60 and "　" not in x["original"]:
            x["type"], x["level"] = "heading", 3
            items[k] = {"type": "heading", "level": 3, "original": x["original"], "translation": x["translation"]}
            log.append(f"column heading {x['original']}")
    # 4. the day's schedule and the holiday line get their headings back
    have = any(x.get("original") == "Day Schedule" for x in items)
    first = None if have else next((k for k, x in enumerate(items) if x.get("type") is None and TIME.match(x.get("original") or "")), None)
    if first is not None:
        last = max(k for k, x in enumerate(items) if x.get("type") is None and TIME.match(x.get("original") or ""))
        tail = items[last + 1:]
        if tail and tail[0].get("type") == "image" and len(tail) > 1:
            items.insert(last + 1, {"type": "heading", "level": 3, "original": "Holiday Schedule", "translation": "假日的安排"})
            log.append("holiday heading")
        items.insert(first, {"type": "heading", "level": 3, "original": "Day Schedule", "translation": "一天的日程"})
        log.append("day heading")
    # 5. names of the games as the site writes them
    for x in items:
        for a, b in NAMES:
            if x.get("translation"):
                x["translation"] = x["translation"].replace(a, b)
    fm["parallel_items"] = items
    # 6. front matter
    fm["title"] = meta["title"]
    if meta.get("orig_title"):
        fm["original_title"] = meta["orig_title"]
        fm["source"]["title"] = meta["orig_title"]
    for k in ("display_title", "dek", "summary"):
        if fm.get(k):
            for a, b in NAMES:
                fm[k] = fm[k].replace(a, b)
    fm["tags"] = [t for t in fm["tags"] if t != "Game Freak"]
    fm["source_kind"] = "official_interview"
    fm["source"]["source_type"] = "official_web"
    fm["interviewer"] = "Creatures 招聘网站"
    fm["interviewee"] = meta["who"]
    fm["entities"]["people"] = meta.get("people", [])
    page = meta.get("page", "社员访谈")
    fm["publication"] = f"Creatures 招聘网站「{page}」（原页没有日期；Wayback 最早存档 {fm['date']}）"
    fm["date_note"] = "原页没有发布日期。这里用的是 Wayback Machine 最早的存档日，文章不晚于这天上线。"
    order = list(fm)
    if "date_note" in order:
        order.remove("date_note")
        order.insert(order.index("date") + 1, "date_note")
    fm = {k: fm[k] for k in order}
    open(path, "w", encoding="utf-8", newline="\n").write("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n")
    print("==", key)
    for line in log:
        print("   ", line)
