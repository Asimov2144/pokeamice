"""Curate, clean, and finalize all interview posts in _posts/.
- Deletes invalid error pages (S3 AccessDenied, Cloudflare challenge)
- Resolves dates and renames 9999-99-99 files to canonical historical dates
- Prunes website navigation, country pickers, cookie bars, and subscription prompts
- Normalizes frontmatter and ensures valid YAML
"""

import os
import re
import sys
from pathlib import Path
import yaml

sys.stdout.reconfigure(encoding='utf-8')

POSTS_DIR = Path('_posts')

INVALID_FILES = [
    "9999-99-99-interview-interviews.md",     # AWS S3 AccessDenied XML
    "9999-99-99-interview-page-3.md"          # ResetEra Cloudflare Challenge
]

# Canonical date and slug mapping for 9999 files
DATE_SLUG_MAP = {
    "9999-99-99-interview-1100-6462538.md": (
        "2018-10-18", "interview-gamespot-lgpe-masuda",
        "[访谈翻译] GameSpot 专访增田顺一：《Let's Go！皮卡丘／伊布》如何重塑《宝可梦 黄》"
    ),
    "9999-99-99-interview-202104.md": (
        "2021-04-30", "interview-new-pokemon-snap-ishihara-suzaki",
        "[访谈翻译] Fami通专访石原恒和与须崎D：《New 宝可梦随乐拍》开发秘辛"
    ),
    "9999-99-99-interview-entrevista-con-junichi-masuda-59058.md": (
        "2013-10-11", "interview-hobbyconsolas-masuda-xy",
        "[访谈翻译] Hobby Consolas 专访增田顺一：宝可梦系列的灵魂与《X·Y》创新"
    ),
    "9999-99-99-interview-game-freak-illustration-video-serie.md": (
        "2019-05-18", "interview-siliconera-harmoknight-drill-dozer",
        "[访谈翻译] Siliconera 专访 Game Freak 插画视频系列：《节奏骑士》与《钻地少女》开发揭秘"
    ),
    "9999-99-99-interview-game-freak-were-trying-to-create-so.md": (
        "2019-05-09", "interview-vgc-gamefreak-gear-project",
        "[访谈翻译] VGC 专访 Game Freak 尾上将之：我们一直在尝试创造超越宝可梦的作品"
    ),
    "9999-99-99-interview-history-special-interview.md": (
        "2015-11-08", "interview-creatures-20th-anniversary",
        "[访谈翻译] Creatures 成立20周年特别对谈：石原恒和 × 田中宏和 回顾宝可梦黎明期"
    ),
    "9999-99-99-interview-interview-game-freak-usum.md": (
        "2017-10-19", "interview-pocketmonsters-usum-iwao-ohmori",
        "[访谈翻译] PocketMonsters 独家专访开发团队：岩尾和昌与大森滋谈《究极之日／究极之月》"
    ),
    "9999-99-99-interview-interview.md": (
        "2020-04-01", "interview-pokemon-company-career",
        "[访谈翻译] 宝可梦公司（TPC）职业特别访谈：业务骨干眼中的宝可梦事业"
    ),
    "9999-99-99-interview-masuda-interview-pokemon-platinum.md": (
        "2009-04-01", "interview-nintendo-power-masuda-gens-1-4",
        "[访谈翻译] Nintendo Power 2009 增田顺一专访：第一至第四世代宝可梦的演进与《白金》"
    ),
    "9999-99-99-interview-miyazaki-interview-anime-ost.md": (
        "2006-12-20", "interview-shinji-miyazaki-gf-sound-team",
        "[访谈翻译] 宫崎慎二 × Game Freak 声音团队对谈：“畅谈宝可梦音乐的世界”"
    ),
    "9999-99-99-interview-pokemon-lets-go-pikachu-und-evoli-d.md": (
        "2018-10-24", "interview-eurogamer-lgpe-masuda",
        "[访谈翻译] Eurogamer 专访增田顺一与名手工作：通往大师训练家之路"
    ),
    "9999-99-99-interview-pokemon-movie-channel-movie-details.md": (
        "2015-07-15", "interview-movie-18-director-yuyama",
        "[访谈翻译] 宝可梦电影频道 M18 公映前特别专访：汤山邦彦监督谈《光环的超魔神 胡帕》"
    )
}

# General noise text patterns to eliminate
NOISE_EXACT = {
    "Share", "share", "Post Tweet Email", "Twitter Facebook Instagram Twitch YouTube",
    "View the discussion thread.", "gamescom 2026", "Mega Man: Dual Override",
    "interview", "Review", "Orbitals", "Review – Space For Improvement", "News",
    "▲トップへ", "メニュー へ戻る", "Feature", "Popular Content",
    "Sep", "OCT", "Nov", "18", "1999 2000 2001", "success", "fail", "Sep OCT Nov",
    "ブラック ホワイト", "ブラック ホワイト 増田順一",
    "Seleccione:", "- - -", "---", "España", "América", "México", "Colombia", "Chile",
    "Argentina", "US Español", "US English", "SUSCRÍBETE AHORA", "Síguenos en:",
    "El País en Facebook", "El País en Twitter", "El País en Youtube", "El País en Instagram",
    "Cerrar", "Lo último", "Juegos", "Recommended Videos", "Open main menu", "scroll",
    "chapter 01", "Skip to content"
}

NOISE_PREFIXES = [
    "https://gameinformer.com", "Preview – Mega Man's", "Preview - Mega Man",
    "Showa American Story", "Ace Combat 8:", "Total War: Warhammer",
    "No Law Isn't Just A Cyberpunk", "No Rest For The Wicked",
    "The Blood of Dawnwalker", "Review – Time Doesn't", "Review - Time Doesn't",
    "Review –", "Review -", "The Can't Miss Games", "Onimusha:", "Still on the fence",
    "★ ページａ ★", "18 Oct 2000 -", "07 Jul 1997 -",
    "Crawl data donated by Alexa Internet", "Collection: Alexa Crawls", "Organization: Alexa Crawls",
    "Check out our review for Pokemon", "「砂の碑」トップページ >",
    "Home / Content DB /", "[WARNING] Ignore caches that are heterogeneous",
    "Si quieres seguir toda la actualidad sin límites"
]

def is_noise(item: dict) -> bool:
    if item.get("type") != "paragraph":
        return False
    orig = item.get("original", "").strip().replace('\xa0', ' ')
    if not orig:
        return True
    if orig in NOISE_EXACT:
        return True
    if any(orig.startswith(p) for p in NOISE_PREFIXES):
        return True
    if orig.endswith("- Game Informer Skip to main content"):
        return True
    return False

def clean_post_content(post_path: Path):
    raw = post_path.read_text(encoding='utf-8')
    parts = raw.split('---', 2)
    if len(parts) < 3:
        return
    
    # Try parsing YAML
    fm_raw = parts[1]
    # Guard against unescaped '---' within yaml
    lines = fm_raw.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip() == "translation: '---'":
            cleaned_lines.append("  translation: '——'")
        else:
            cleaned_lines.append(line)
    fm_str = '\n'.join(cleaned_lines)
    
    try:
        fm = yaml.safe_load(fm_str)
    except Exception as e:
        print(f"Error loading YAML in {post_path.name}: {e}")
        return

    # Check and clean items
    items = fm.get("parallel_items", [])
    original_len = len(items)

    # Trim head
    while items and is_noise(items[0]):
        items.pop(0)

    # Trim tail
    while items and is_noise(items[-1]):
        items.pop(-1)

    # Filter inline
    final_items = [it for it in items if not is_noise(it)]
    fm["parallel_items"] = final_items

    # Ensure required frontmatter fields
    fm["categories"] = ["访谈翻译", "翻译", "访谈整理"]
    if not fm.get("translator"):
        fm["translator"] = "Poke Amice Studio"
    if not fm.get("original_title"):
        fm["original_title"] = fm.get("title", "").replace("[访谈翻译] ", "")
    if not fm.get("original_link") and fm.get("source", {}).get("url"):
        fm["original_link"] = fm["source"]["url"]
    if not fm.get("interviewee"):
        people = fm.get("entities", {}).get("people", [])
        fm["interviewee"] = ", ".join(people) if people else "开发团队"

    new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    new_text = f"---\n{new_yaml}---\n"
    post_path.write_text(new_text, encoding='utf-8')
    print(f"  [Cleaned] {post_path.name}: {original_len} -> {len(final_items)} items (-{original_len - len(final_items)})")


def main():
    print("=== Step 1: Deleting Invalid Error Pages ===")
    for fname in INVALID_FILES:
        fpath = POSTS_DIR / fname
        if fpath.exists():
            fpath.unlink()
            print(f"  Deleted invalid error file: {fname}")

    print("\n=== Step 2: Renaming 9999-99-99 Files to Canonical Dates ===")
    for old_name, (new_date, new_slug, new_title) in DATE_SLUG_MAP.items():
        old_path = POSTS_DIR / old_name
        if old_path.exists():
            new_name = f"{new_date}-{new_slug}.md"
            new_path = POSTS_DIR / new_name
            # Update date and title in file
            raw = old_path.read_text(encoding='utf-8')
            parts = raw.split('---', 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1])
                    fm["date"] = new_date
                    fm["title"] = new_title
                    fm_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
                    new_path.write_text(f"---\n{fm_yaml}---\n", encoding='utf-8')
                    old_path.unlink()
                    print(f"  Renamed: {old_name} -> {new_name}")
                except Exception as e:
                    print(f"  Error renaming {old_name}: {e}")

    print("\n=== Step 3: Curating and Cleaning All Interview Posts ===")
    for post in sorted(POSTS_DIR.glob('*interview*.md')):
        clean_post_content(post)

    print("\n=== Curation Completed Successfully ===")

if __name__ == "__main__":
    main()
