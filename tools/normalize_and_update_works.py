"""Normalize entities and update works across all posts in _posts/

1. Standardize entities.games -> entities.works.
2. Canonicalize work names (e.g. 宝可梦 赤·绿 -> 宝可梦 红·绿, 剑／盾 -> 剑·盾).
3. Detect works for posts missing works from tags, title, and summary.
4. Set archive_type: interview_translation for interview posts missing archive_type.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"

CANONICAL_WORKS = {
    "宝可梦 赤·绿": "宝可梦 红·绿",
    "宝可梦 红·蓝": "宝可梦 红·绿",
    "宝可梦 青": "宝可梦 蓝",
    "宝可梦 皮卡丘": "宝可梦 皮卡丘版",
    "宝可梦 黄": "宝可梦 皮卡丘版",
    "宝可梦 2（金·银早期代号）": "宝可梦 金·银",
    "宝可梦 传说 阿尔宙斯": "宝可梦传说 阿尔宙斯",
    "Pokémon LEGENDS 阿尔宙斯": "宝可梦传说 阿尔宙斯",
    "Pokemon LEGENDS 阿尔宙斯": "宝可梦传说 阿尔宙斯",
    "精灵宝可梦 Let's Go！皮卡丘／Let's Go！伊布": "宝可梦 Let's Go！皮卡丘·Let's Go！伊布",
    "宝可梦 Let's Go！皮卡丘／Let's Go！伊布": "宝可梦 Let's Go！皮卡丘·Let's Go！伊布",
    "宝可梦 剑／盾": "宝可梦 剑·盾",
    "宝可梦 X／Y": "宝可梦 X·Y",
    "宝可梦 太阳／月亮": "宝可梦 太阳·月亮",
    "宝可梦 心金／魂银": "宝可梦 心金·魂银",
    "宝可梦 黑／白": "宝可梦 黑·白",
    "宝可梦 黑2／白2": "宝可梦 黑2·白2",
    "宝可梦 金／银": "宝可梦 金·银",
    "宝可梦 火红／叶绿": "宝可梦 火红·叶绿",
    "乱战！宝可梦乱战": "宝可梦乱战",
    "宝可梦不可思议迷宫 极大之门与∞迷宫": "宝可梦不可思议迷宫",
    "宝可梦不可思议迷宫 青之救助队·赤之救助队": "宝可梦不可思议迷宫",
    "宝可梦不可思议迷宫 时之探险队·暗之探险队·空之探险队": "宝可梦不可思议迷宫",
    "特鲁尼克大冒险 不可思议迷宫": "不可思议迷宫",
}

WORK_PATTERNS = [
    (re.compile(r"黑2[·／/ ]?白2|B2W2|Black 2|White 2"), "宝可梦 黑2·白2"),
    (re.compile(r"黑[·／/ ]?白|BW|Black & White|Black and White"), "宝可梦 黑·白"),
    (re.compile(r"心金[·／/ ]?魂银|HGSS|HeartGold|SoulSilver"), "宝可梦 心金·魂银"),
    (re.compile(r"钻石[·／/ ]?珍珠|钻珍|Diamond & Pearl"), "宝可梦 钻石·珍珠"),
    (re.compile(r"白金版?|Platinum"), "宝可梦 白金"),
    (re.compile(r"火红[·／/ ]?叶绿|FireRed|LeafGreen"), "宝可梦 火红·叶绿"),
    (re.compile(r"红宝石[·／/ ]?蓝宝石|Ruby & Sapphire"), "宝可梦 红宝石·蓝宝石"),
    (re.compile(r"欧米伽红宝石[·／/ ]?阿尔法蓝宝石|终极红宝石[·／/ ]?始源蓝宝石|ORAS"), "宝可梦 欧米伽红宝石·阿尔法蓝宝石"),
    (re.compile(r"绿宝石版?|Emerald"), "宝可梦 绿宝石"),
    (re.compile(r"水晶版"), "宝可梦 水晶版"),
    (re.compile(r"金[·／/ ]?银|宝可梦2|Pocket Monsters 2"), "宝可梦 金·银"),
    (re.compile(r"皮卡丘版|黄版|宝可梦 黄"), "宝可梦 皮卡丘版"),
    (re.compile(r"红[·／/ ]?绿|赤[·／/ ]?绿|红[·／/ ]?蓝|胶囊怪兽|Capsule Monsters"), "宝可梦 红·绿"),
    (re.compile(r"X[·／/ ]?Y|XY"), "宝可梦 X·Y"),
    (re.compile(r"究极之日[·／/ ]?究极之月|究极日月|USUM"), "宝可梦 究极之日·究极之月"),
    (re.compile(r"太阳[·／/ ]?月亮|太阳月亮|Sun & Moon|Sun and Moon|宝可梦.*日月|《日月》|『日月』"), "宝可梦 太阳·月亮"),
    (re.compile(r"Let'?s Go[！! ]?皮卡丘|皮卡丘[·／/ ]?伊布"), "宝可梦 Let's Go！皮卡丘·Let's Go！伊布"),
    (re.compile(r"剑[·／/ ]?盾|剑盾|Sword & Shield"), "宝可梦 剑·盾"),
    (re.compile(r"晶灿钻石[·／/ ]?明亮珍珠|BDSP"), "宝可梦 晶灿钻石·明亮珍珠"),
    (re.compile(r"传说[· ]?阿尔宙斯|阿尔宙斯|Legends:? Arceus"), "宝可梦传说 阿尔宙斯"),
    (re.compile(r"朱[·／/ ]?紫|朱紫|Scarlet & Violet"), "宝可梦 朱·紫"),
    (re.compile(r"传说[· ]?Z-A|Legends:? Z-A"), "宝可梦传说 Z-A"),
    (re.compile(r"Pok[eé]mon GO"), "Pokémon GO"),
    (re.compile(r"立体图鉴BW|Pok[eé]dex 3D"), "宝可梦立体图鉴BW"),
    (re.compile(r"超级宝可梦乱战|Super Pok[eé]mon Rumble"), "超级宝可梦乱战"),
    (re.compile(r"宝可梦乱战|Pok[eé]mon Rumble"), "宝可梦乱战"),
    (re.compile(r"名侦探皮卡丘|Detective Pikachu"), "名侦探皮卡丘"),
    (re.compile(r"不可思议迷宫|极大之门|Mystery Dungeon"), "宝可梦不可思议迷宫"),
    (re.compile(r"宝可梦随乐拍|Pok[eé]mon Snap"), "宝可梦随乐拍"),
    (re.compile(r"宝可梦竞技场|Pok[eé]mon Stadium"), "宝可梦竞技场"),
    (re.compile(r"宝可梦卡牌|集换式卡牌|TCG"), "宝可梦集换式卡牌游戏"),
]

SERIES_EXCLUDE = {
    "宝可梦", "Pokémon", "ポケットモンスター", "Pokemon",
    "任天堂 3DS", "任天堂 DS", "Game Boy", "Game Boy Advance"
}


def update_post(path: Path) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return False, "no front matter"
    fm_text, body = m.group(1), m.group(2)
    try:
        data = yaml.safe_load(fm_text) or {}
    except Exception as e:
        return False, f"yaml error: {e}"

    modified = False

    # 1. Update archive_type if unset and looks like an interview
    at = data.get("archive_type")
    new_at = None
    if not at:
        title = str(data.get("title", ""))
        cats = [str(c) for c in (data.get("categories") or [])]
        layout = str(data.get("layout", ""))
        fname = path.name
        if "访谈" in title or "专访" in title or "访谈翻译" in cats or "interview" in fname:
            new_at = "interview_translation"
            modified = True

    # 2. Gather entities
    ents = data.get("entities") or {}
    w_list = list(ents.get("works") or [])
    g_list = list(ents.get("games") or [])

    new_works = []
    seen = set()

    for w in w_list + g_list:
        cw = CANONICAL_WORKS.get(w, w)
        if cw not in SERIES_EXCLUDE and cw not in seen:
            seen.add(cw)
            new_works.append(cw)

    # If games had entries or works had canonical changes
    if g_list or (new_works != w_list):
        modified = True

    # 3. If no works yet, infer from tags, title, summary
    if not new_works:
        tags = [str(t) for t in (data.get("tags") or [])]
        title = str(data.get("title", ""))
        summary = str(data.get("summary", ""))
        search_text = " ".join(tags + [title, summary])
        for pat, w_name in WORK_PATTERNS:
            if pat.search(search_text) and w_name not in seen:
                seen.add(w_name)
                new_works.append(w_name)
                modified = True

    if not modified:
        return False, "unchanged"

    # 4. Reconstruct front matter text cleanly
    if new_at and not re.search(r"^archive_type:", fm_text, re.MULTILINE):
        fm_text = f"archive_type: {new_at}\n{fm_text}"

    # Reconstruct entities block
    people = ents.get("people") or []
    orgs = ents.get("organizations") or []
    events = ents.get("events") or []

    # If any entity field exists or new_works exists
    if people or new_works or orgs or events:
        new_ents_lines = ["entities:"]
        if people:
            new_ents_lines.append("  people:")
            for p in people:
                new_ents_lines.append(f"  - {p}")
        if new_works:
            new_ents_lines.append("  works:")
            for w in new_works:
                new_ents_lines.append(f"  - {w}")
        if orgs:
            new_ents_lines.append("  organizations:")
            for o in orgs:
                new_ents_lines.append(f"  - {o}")
        if events:
            new_ents_lines.append("  events:")
            for e in events:
                new_ents_lines.append(f"  - {e}")
        new_ents_block = "\n".join(new_ents_lines)

        ent_match = re.search(r"\nentities:\n(.*?)(?=\n[a-zA-Z0-9_-]+:|\Z)", fm_text, re.DOTALL)
        if ent_match:
            old_block = "entities:\n" + ent_match.group(1)
            fm_text = fm_text.replace(old_block, new_ents_block)
        else:
            fm_text = fm_text.strip() + "\n" + new_ents_block

    new_full_text = f"---\n{fm_text.strip()}\n---\n{body}"
    path.write_text(new_full_text, encoding="utf-8")
    return True, "updated"


def main():
    posts = sorted(POSTS_DIR.glob("*.md"))
    print(f"Processing {len(posts)} posts in {POSTS_DIR}...")
    updated_count = 0
    for p in posts:
        mod, reason = update_post(p)
        if mod:
            updated_count += 1

    print(f"Completed: {updated_count} posts updated.")


if __name__ == "__main__":
    main()
