"""Comprehensive cleaning, unrolling, and speaker normalization for all interview posts in _posts/.
"""

from __future__ import annotations
import re
import sys
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

POSTS_DIR = Path("_posts")

# 1. Superseded raw files to remove
SUPERSEDED_FILES = [
    "1999-11-22-interview-1999-11-22-time-magazine-tajiri.md",
    "2000-07-01-interview-2000-07-01-nom-gen1-gamefreak.md",
    "2000-07-01-interview-2000-07-01-nom-gen2-gamefreak.md",
    "2010-03-19-interview-2010-03-19-game-informer-hgss.md",
    "2017-08-10-interview-heres-how-game-freak-designs-pokemo.md",
    "2021-04-30-interview-new-pokemon-snap-ishihara-suzaki.md",
]

# 2. Comprehensive speaker canonicalization mapping
SPEAKER_MAP = {
    # Creators (unify Chinese names to remove spaces)
    "岩田 聪": "岩田聪",
    "石原 恒和": "石原恒和",
    "增田 顺一": "增田顺一",
    "杉森 建": "杉森建",
    "海野 隆雄": "海野隆雄",
    "森本 茂树": "森本茂树",
    "田尻 智": "田尻智",
    "尾上 将之": "尾上将之",
    "大森 滋": "大森滋",
    "岩尾 和昌": "岩尾和昌",
    "川岛 优志": "川岛优志",
    "须崎 春树": "须崎春树",
    "西野 弘二": "西野弘二",
    "渡边 哲也": "渡边哲也",
    "松岛 贤二": "松岛贤二",
    "景山 将太": "景山将太",
    "杉中 克考": "杉中克考",
    "前泽 圭一": "前泽圭一",
    "宫崎 慎二": "宫崎慎二",
    "一之濑 刚": "一之濑刚",
    "川知丸 武": "川知丸武",
    "森 昭人": "森昭人",

    # Surnames to full names where unambiguous
    "星野": "星野正昭",
    "宇都宫": "宇都宫崇人",
    "原田": "原田胜弘",
    "杉中": "杉中克考",
    "岩尾": "岩尾和昌",
    "野村達雄氏": "野村达雄",
    "高橋伸也氏": "高桥伸也",
    "田上怜子": "田上玲子",

    # Interviewers / Media
    "TIME 记者": "时代周刊",
    "TIME": "时代周刊",
    "N.O.M 采访者": "N.O.M采访者",
    "N.O.M 导览": "N.O.M导览",
    "电玩志 记者": "电玩志",
    "Eurogamer 记者": "Eurogamer",
    "Fami通 记者": "Fami通",
    "Fami通记者": "Fami通",
    "Nintendo Power 记者": "Nintendo Power",
    "Game Informer 记者": "Game Informer",
    "4Gamer 记者": "4Gamer",
    "4Gamer记者": "4Gamer",
    "ライター: 稲元徹也": "4Gamer",
    "IGN记者": "IGN",
    "G4记者": "G4",
    "CGWORLD 技术解析": "CGWORLD",
    "Dr Lava": "Dr. Lava",
    "Doctor Lava": "Dr. Lava",
    "Dr Lava 的注释": "Dr. Lava",

    # Composites
    "石原 & 森本": "石原恒和 & 森本茂树",
    "石原 恒和・增田 顺一": "石原恒和 & 增田顺一",
    "大森滋 & 增田顺一": "大森滋 & 增田顺一",
}

# Noise patterns to drop entire parallel item
NOISE_ITEM_PATTERNS = [
    r"小売希望価格|新品最安値|発売日：20\d\d年",
    r"Robloxギフトカード",
    r"Page Tags:\s*(Interview|Music|Ultra Sun|Anime)",
    r"Website Programming:\s*JDS,\s*Hiroki,\s*Sunain",
    r"None\s+None",
    r"^\{\"\d+\":\[\"\d+\"\]\}",
    r"PlayStation 5/PlayStation 4",
    r"gamescom 2026",
    r"ACE COMBAT 8",
    r"Cronos Lazarus",
    r"Bye Bye Bonnie",
    r"Mega Man:\s*Dual Override",
    r"Preview – Mega Man",
    r"Review – Space For Improvement",
    r"Popular Content",
    r"Showa American Story",
    r"Total War:\s*Warhammer",
    r"No Rest For The Wicked",
    r"The Can't Miss Games Of",
    r"Check out our review for Pokemon",
    r"View the discussion thread",
    r"Post Tweet Email",
    r"Twitter Facebook Instagram Twitch YouTube",
    r"▲トップへ",
    r"メニュー へ戻る",
    r"「砂の碑」トップページ",
    r"由WordPress强力驱动|自豪地采用 WordPress 驱动",
    r"版权所有 © 2013 时而晴朗",
    r"历史存档一览",
    r"^网站规则$|^隐私政策$|^使用条款$|^联盟政策$",
    r"^评论已关闭$",
    r"^博客帖子编号\d+$",
    r"^http://www\.g4tv\.com/thefeed/blog/post/",
    r"^http://files\.g4tv\.com/ImageDb3/",
    r"しまむら（岛村）将于9月5日发售《魔法姐妹露露托莉莉》",
    r"世嘉幸运抽奖《圣诞夜惊魂》系列超酷！",
    r"《命运高达SpecII》以最终决战配色商品化！",
    r"查看更多最新新闻",
    r"^推特 脸书 YouTube RSS$",
    r"^ホーム › 任天堂 › Wii U › 記事$",
    r"^首页 › 任天堂 › Wii U › 文章$",
]

# Patterns for in-line trailing noise within an otherwise valid item
INLINE_TRAILING_NOISE = [
    r"\n?（以下为商品信息.*?）?$",
    r"\n?集計期間：20\d\d年.*?$",
    r"\n?本記事はアフィリエイトプログラムによる収益を得ている場合があります.*$",
    r"\n?本文可能包含通过联盟计划获得的收益.*$",
]

def is_noise_item(item: dict) -> bool:
    orig = str(item.get("original", "")).strip()
    trans = str(item.get("translation", "")).strip()
    combined = orig + " " + trans
    
    if not orig and not trans:
        return True
    if orig.lower() in ["none", "none none", "null", "undefined"]:
        return True
    if trans.lower() in ["none", "none none", "null", "undefined"]:
        return True

    for pat in NOISE_ITEM_PATTERNS:
        if re.search(pat, combined, re.IGNORECASE):
            return True

    return False

def clean_inline_trailing(text: str) -> str:
    for pat in INLINE_TRAILING_NOISE:
        text = re.sub(pat, "", text, flags=re.DOTALL).strip()
    return text

def unwrap_text(text: str) -> str:
    """Unwrap hard line breaks within a single speech turn/paragraph.
    Preserves lists (- item, * item, 1. item) if present.
    """
    if not text:
        return ""
    
    text = text.replace("\xa0", " ").replace("\r\n", "\n").replace("\r", "\n")
    lines = [l.strip() for l in text.split("\n")]
    lines = [l for l in lines if l]
    if not lines:
        return ""
    
    if any(l.startswith(("- ", "* ", "1. ", "2. ", "3. ", "> ", "```")) for l in lines):
        return "\n".join(lines)

    cjk_count = len(re.findall(r"[\u4e00-\u9fa5\u3040-\u30ff]", text))
    total_len = len("".join(lines))
    is_cjk = (cjk_count / max(total_len, 1)) > 0.25

    if is_cjk:
        result = "".join(lines)
    else:
        result = " ".join(lines)
        result = re.sub(r"\s+", " ", result)
    
    return result

def clean_specific_post_chrome(fname: str, items: list[dict]) -> list[dict]:
    """Special handling for posts with extensive portal header/footer chrome."""
    # 1. 2013-11-16 4Gamer report
    if "2013-11-16-interview-20131116014.md" in fname:
        start_idx = None
        end_idx = None
        for i, it in enumerate(items):
            orig = it.get("original", "")
            if "「ポケットモンスター X・Y」のサウンド制作秘話を開発陣が披露" in orig:
                start_idx = i
            if "プラターヌ博士のテーマ" in orig:
                end_idx = i + 2 # include photo note and next item if official site link
        if start_idx is not None:
            if end_idx is None:
                end_idx = len(items)
            print(f"  [20131116014] Sliced from {start_idx} to {end_idx} (trimmed portal chrome)")
            items = items[start_idx:end_idx]

    # 2. 2015-07-15 Movie 18 Yuyama interview
    elif "movie-18" in fname or "yuyama" in fname:
        start_idx = None
        end_idx = None
        for i, it in enumerate(items):
            orig = it.get("original", "")
            trans = it.get("translation", "")
            if "映画公開直前スペシャルインタビュー：湯山邦彦監督" in orig or "电影首映前特别访谈：汤山邦彦导演" in trans:
                if start_idx is None:
                    start_idx = i
            if "劇場でフーパやピカチュウ、サトシたちと一緒に冒険しよう" in orig or "在影院与胡帕、皮卡丘和小智一起冒险吧" in trans:
                end_idx = i + 1
        if start_idx is not None and end_idx is not None:
            print(f"  [movie-18] Sliced from {start_idx} to {end_idx} (isolated Yuyama interview)")
            items = items[start_idx:end_idx]

    return items

def clean_post(post_path: Path):
    content = post_path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        return
    
    fm_text = parts[1]
    body = parts[2]
    
    try:
        fm = yaml.safe_load(fm_text)
    except Exception as e:
        print(f"Error parsing YAML in {post_path.name}: {e}")
        return

    items = fm.get("parallel_items", [])
    if not items:
        return

    # Trim site chrome if applicable
    items = clean_specific_post_chrome(post_path.name, items)

    cleaned_items = []
    removed_count = 0
    unwrapped_count = 0
    speaker_canon_count = 0

    is_movie_18 = ("movie-18" in post_path.name or "yuyama" in post_path.name)
    is_staff_diary = ("staff-diary" in post_path.name)
    is_career = ("career" in post_path.name)

    # Detect Matsushima section in staff diary
    in_matsushima = False

    for it in items:
        if not isinstance(it, dict):
            continue

        orig = str(it.get("original", ""))
        trans = str(it.get("translation", ""))
        sp = str(it.get("speaker", "")).strip()

        # Check if noise item
        if is_noise_item(it):
            removed_count += 1
            continue

        # Clean trailing noise attached to end of paragraph
        orig = clean_inline_trailing(orig)
        trans = clean_inline_trailing(trans)

        # Unwrap hard breaks
        if "\n" in orig:
            unwrapped_count += 1
            orig = unwrap_text(orig)
        if "\n" in trans:
            trans = unwrap_text(trans)

        # Track diary context
        if is_staff_diary:
            if "プランナーの松島です" in orig or "我是策划松岛" in trans:
                in_matsushima = True
            elif "プランナーのカニ子です" in orig or "我是策划卡妮子" in trans:
                in_matsushima = False

        # Speaker canonicalization
        if is_movie_18 and sp in ["受访嘉宾", "受访者", "答"]:
            sp = "汤山邦彦"
            speaker_canon_count += 1
        elif is_staff_diary and in_matsushima and sp in ["受访嘉宾", "受访者", "答"]:
            sp = "松岛贤二"
            speaker_canon_count += 1
        elif is_career and sp in ["受访嘉宾", "受访者", "答"]:
            sp = "TPC员工"
            speaker_canon_count += 1
        elif sp in SPEAKER_MAP:
            sp = SPEAKER_MAP[sp]
            speaker_canon_count += 1

        it["original"] = orig
        it["translation"] = trans
        if sp:
            it["speaker"] = sp
        elif "speaker" in it:
            it["speaker"] = ""

        cleaned_items.append(it)

    fm["parallel_items"] = cleaned_items

    # Update metadata interviewee
    all_speakers = set(it.get("speaker") for it in cleaned_items if it.get("speaker"))
    non_q = [s for s in all_speakers if s not in ["提问", "时代周刊", "Fami通", "Game Informer", "Nintendo Power", "4Gamer", "电玩志", "N.O.M采访者", "N.O.M导览", "CGWORLD", "IGN", "Eurogamer", "Pokemon.com", "全员", "众人"]]
    if non_q:
        fm["interviewee"] = ", ".join(sorted(non_q))

    # Re-dump YAML
    new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    new_content = f"---\n{new_yaml}---\n{body.lstrip()}"
    post_path.write_text(new_content, encoding="utf-8")

    if removed_count > 0 or unwrapped_count > 0 or speaker_canon_count > 0:
        print(f"[{post_path.name}] -{removed_count} noise, {unwrapped_count} unwrapped, {speaker_canon_count} speakers canonicalized")

def remove_superseded_files():
    print("=== REMOVING SUPERSEDED DRAFT FILES ===")
    for fname in SUPERSEDED_FILES:
        p = POSTS_DIR / fname
        if p.exists():
            p.unlink()
            print(f"  Removed obsolete file: {fname}")
        else:
            print(f"  Already absent: {fname}")
    print()

def main():
    remove_superseded_files()
    
    posts = sorted(POSTS_DIR.glob("*interview*.md"))
    print(f"Processing and cleaning {len(posts)} remaining interview posts...\n")
    for p in posts:
        clean_post(p)

    print("\nCorpus cleanup completed successfully!")

if __name__ == "__main__":
    main()
