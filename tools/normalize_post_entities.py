"""Bring the hand-tagged entity blocks onto one naming convention.

Sixteen posts were tagged by hand before the extractor existed, and they do not
agree with each other or with what the extractor produces. Three problems, all
of which would split the index the moment 459 machine-tagged posts arrive:

* the same organisation written three ways (GAME FREAK / Game Freak / ゲームフリーク)
  and Japanese titles where the extractor writes Chinese (ポケットモンスター プラチナ
  against 宝可梦 白金);
* `works` used as a tag bucket, holding 开发, 年表, Leak, 第四世代, 开源, 2025,
  Chrome 插件 - none of which is a work;
* one entry filing the person 岩尾和昌 as a work.

Renames and reclassifications are declared below rather than guessed, because
there are few enough to read and each one is a judgement about this archive.
Run without --apply to see the diff.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "_posts"
KINDS = ("people", "works", "organizations", "events")

# One canonical spelling per entity, matching what the extractor emits.
#
# The extractor is told to use formal names and mostly does, but across 459
# posts it still returned GAME FREAK five times, 宝可梦GO beside Pokémon GO, and
# bare surnames where the full name appears elsewhere. Those are the same
# entity, so they are folded here rather than left to split the index.
RENAME = {
    "GAME FREAK": "Game Freak",
    "GameFreak": "Game Freak",
    "gamefreak": "Game Freak",
    "ゲームフリーク": "Game Freak",
    "石原": "石原恒和",
    "增田": "增田顺一",
    "杉森": "杉森建",
    "田尻": "田尻智",
    "大森": "大森滋",
    "宝可梦GO": "Pokémon GO",
    "宝可梦 GO": "Pokémon GO",
    "Pokemon GO": "Pokémon GO",
    "任天堂株式会社": "任天堂",
    "Nintendo Co., Ltd.": "任天堂",
    "株式会社ポケモン": "宝可梦公司",
    "The Pokémon Company": "宝可梦公司",
    "宝可梦公司": "宝可梦公司",
    # The staff blog signs posts with pen names, sometimes in kana and
    # sometimes transliterated, which split one author across two entries.
    "もりもと": "森本",
    "エノキ": "榎木",
    "なぎー": "纳吉",
    "スティック": "斯蒂克",
    "カニ子": "蟹子",
    "宝可梦 白金版": "宝可梦 白金",
    "宝可梦 心金・魂银": "宝可梦 心金·魂银",
    "宝可梦 黑・白": "宝可梦 黑·白",
    "宝可梦 钻石・珍珠": "宝可梦 钻石·珍珠",
    "宝可梦世界锦标赛2010": "宝可梦世界锦标赛",
    "看我嘛": "看我嘛活动",
    "Nintendo": "任天堂",
    "ポケットモンスター": "宝可梦",
    "ポケットモンスター プラチナ": "宝可梦 白金",
    "ポケモンだいすきクラブ": "宝可梦爱好者俱乐部",
    "宝可梦 红・绿": "宝可梦 红·绿",
    "一之瀬剛": "一之濑刚",
    "James Turnner": "James Turner",
    "宝可梦传说 阿尔宙斯": "宝可梦传说 阿尔宙斯",
    "LA": "宝可梦传说 阿尔宙斯",
    "宝可梦传说Z-A": "宝可梦传说 Z-A",
    "Pokémon GO": "Pokémon GO",
    "PokemonDay": "宝可梦日",
}

# Values filed under the wrong kind. A work is a game, film or publication.
RECLASSIFY = {
    "岩尾和昌": "people",
    "Nintendo DREAM": "organizations",
    "电击 Online": "organizations",
    "宝可梦日": "events",
    "日本游戏大赏": "events",
    "宝可梦30周年": "events",
}

# Tags that are not entities at all: themes, eras, formats, years.
DROP = {
    "开发", "年表", "开源", "Leak", "2025", "简中PTCG", "宝活小妙招",
    "Chrome 插件", "宝可梦友会", "第四世代", "第五世代", "第六世代", "第八世代",
    "バトルビデオ", "Wi-Fi", "WCS",
}


def parse_block(text: str):
    match = re.search(r"^entities:\n((?:  \w+:\n(?:    - .*\n)+)+)", text, re.M)
    if not match:
        return None, None
    parsed, kind = {}, None
    for line in match.group(1).rstrip().split("\n"):
        if re.match(r"^  \w+:$", line):
            kind = line.strip().rstrip(":")
            parsed[kind] = []
        elif line.startswith("    - ") and kind:
            parsed[kind].append(line[6:].strip().strip('"').strip("'"))
    return match, parsed


def normalize(parsed: dict) -> dict:
    out = {k: [] for k in KINDS}
    for kind, values in parsed.items():
        for value in values:
            if value in DROP:
                continue
            name = RENAME.get(value, value)
            target = RECLASSIFY.get(value, RECLASSIFY.get(name, kind))
            if target not in out:
                continue
            if name not in out[target]:
                out[target].append(name)
    return out


def render(entities: dict) -> str:
    lines = ["entities:"]
    for kind in KINDS:
        if not entities.get(kind):
            continue
        lines.append(f"  {kind}:")
        for value in entities[kind]:
            lines.append(f'    - "{value}"')
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    changed = 0
    for path in sorted(POSTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        match, parsed = parse_block(text)
        if not match:
            continue
        after = normalize(parsed)
        block = render(after)
        if block == match.group(0):
            continue
        changed += 1
        print(f"--- {path.name[:60]}")
        before_flat = {k: v for k, v in parsed.items() if v}
        for kind in KINDS:
            was, now = before_flat.get(kind, []), after.get(kind, [])
            if was != now:
                print(f"    {kind:<14} {was}  ->  {now}")
        if args.apply:
            path.write_text(text.replace(match.group(0), block, 1), encoding="utf-8")

    print(f"\n{changed} post(s) {'rewritten' if args.apply else 'would change'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
