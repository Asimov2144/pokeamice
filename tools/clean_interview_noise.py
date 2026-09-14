"""Clean navigation, advertising, related games, and wayback noise from interview posts.
"""

from pathlib import Path
import re
import sys
import yaml

sys.stdout.reconfigure(encoding='utf-8')

POSTS_DIR = Path('_posts')

# Exact match original text to remove anywhere
NOISE_ORIGINAL_EXACT = {
    "Share", "share", "Post Tweet Email", "Twitter Facebook Instagram Twitch YouTube",
    "View the discussion thread.", "gamescom 2026", "Mega Man: Dual Override",
    "interview", "Review", "Orbitals", "Review – Space For Improvement", "News",
    "▲トップへ", "メニュー へ戻る", "Feature", "Popular Content",
    "Sep", "OCT", "Nov", "18", "1999 2000 2001", "success", "fail",
    "Sep OCT Nov",
    "ブラック ホワイト", "ブラック ホワイト 増田順一"
}

# Prefix patterns for noisy originals
NOISE_ORIGINAL_PREFIXES = [
    "https://gameinformer.com",
    "Preview – Mega Man's",
    "Preview - Mega Man",
    "Showa American Story",
    "Ace Combat 8:",
    "Total War: Warhammer",
    "No Law Isn't Just A Cyberpunk",
    "No Rest For The Wicked",
    "The Blood of Dawnwalker",
    "Review – Time Doesn't",
    "Review - Time Doesn't",
    "Review –",
    "Review -",
    "The Can't Miss Games",
    "Onimusha:",
    "Still on the fence",
    "★ ページａ ★",
    "18 Oct 2000 -",
    "07 Jul 1997 -",
    "Crawl data donated by Alexa Internet",
    "Collection: Alexa Crawls",
    "Organization: Alexa Crawls",
    "Check out our review for Pokemon",
    "「砂の碑」トップページ >"
]

def is_noise_item(item: dict) -> bool:
    if item.get("type") != "paragraph":
        return False
    orig = item.get("original", "").strip()
    # Normalize non-breaking spaces to regular spaces
    orig = orig.replace('\xa0', ' ')
    if not orig:
        return True
    if orig in NOISE_ORIGINAL_EXACT:
        return True
    if any(orig.startswith(p) for p in NOISE_ORIGINAL_PREFIXES):
        return True
    # Strip site branding headlines
    if orig.endswith("- Game Informer Skip to main content") or orig == "E3 2004: The Pokemon Creators Speak - IGN":
        return True
    return False


def clean_post(post_path: Path):
    text = post_path.read_text(encoding='utf-8')
    parts = text.split('---', 2)
    if len(parts) < 3:
        return
    
    fm_text = parts[1]
    body = parts[2]
    try:
        fm = yaml.safe_load(fm_text)
    except Exception as e:
        print(f"Error parsing {post_path.name}: {e}")
        return

    items = fm.get("parallel_items", [])
    original_count = len(items)
    
    # 1. Trim head noise
    while items and is_noise_item(items[0]):
        print(f"  [{post_path.name}] Removed HEAD noise: {items[0].get('original')[:60]}")
        items.pop(0)

    # 2. Trim tail noise
    while items and is_noise_item(items[-1]):
        print(f"  [{post_path.name}] Removed TAIL noise: {items[-1].get('original')[:60]}")
        items.pop(-1)

    # 3. Filter any remaining pure ad/noise in middle
    cleaned_items = []
    for it in items:
        if is_noise_item(it):
            print(f"  [{post_path.name}] Removed INLINE noise: {it.get('original')[:60]}")
        else:
            cleaned_items.append(it)

    fm["parallel_items"] = cleaned_items
    removed = original_count - len(cleaned_items)
    
    # Re-dump YAML
    new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    new_content = f"---\n{new_yaml}---\n{body.lstrip()}"
    post_path.write_text(new_content, encoding='utf-8')
    print(f"[CLEANED] {post_path.name}: {original_count} -> {len(cleaned_items)} items (-{removed})\n")


def main():
    posts = sorted(POSTS_DIR.glob('*interview*.md'))
    print(f"Cleaning noise from {len(posts)} posts...\n")
    for p in posts:
        clean_post(p)

if __name__ == "__main__":
    main()
