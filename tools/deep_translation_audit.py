import re
import sys
from pathlib import Path
from collections import defaultdict
import yaml

sys.stdout.reconfigure(encoding='utf-8')

POSTS_DIR = Path('_posts')
posts = sorted(POSTS_DIR.glob('*interview*.md'))

issues = defaultdict(list)

# Official terminology check (forbidden -> recommended)
TERM_RULES = [
    (r"口袋妖怪", "口袋妖怪 -> 宝可梦"),
    (r"宠物小精灵", "宠物小精灵 -> 宝可梦"),
    (r"神奇宝贝", "神奇宝贝 -> 宝可梦"),
    (r"口袋魔鬼", "口袋魔鬼 -> 宝可梦"),
    (r"小精灵球", "小精灵球 -> 宝可梦球"),
    (r"怪兽球", "怪兽球 -> 精灵球/宝可梦球"),
    (r"小智版", "小智版 -> 皮卡丘版/黄版"),
]

# Patterns of noise
NOISE_PATTERNS = [
    (r"▲トップへ|▲返回顶部", "nav_top"),
    (r"定価：.*円|定价：.*日元.*含税", "store_price_ad"),
    (r"ページトップへ|返回页面顶部", "nav_page_top"),
    (r"Roblox|ギフトカード", "irrelevant_ad"),
]

for p in posts:
    content = p.read_text(encoding='utf-8')
    parts = content.split('---', 2)
    if len(parts) < 3:
        issues['broken_frontmatter'].append((p.name, 0, 'No frontmatter delimiters'))
        continue
    try:
        fm = yaml.safe_load(parts[1])
    except Exception as e:
        issues['broken_yaml'].append((p.name, 0, str(e)))
        continue
        
    # Metadata audit
    if not fm.get('source'):
        issues['missing_source'].append((p.name, 0, 'Missing source field'))
    if not fm.get('interviewee') and not fm.get('author'):
        issues['missing_person'].append((p.name, 0, 'Missing interviewee and author'))
    if not fm.get('era') and not fm.get('date'):
        issues['missing_era_date'].append((p.name, 0, 'Missing era and date'))
        
    items = fm.get('parallel_items', [])
    for idx, it in enumerate(items):
        if not isinstance(it, dict):
            continue
        itype = it.get('type', 'text')
        orig = str(it.get('original', '')).strip()
        trans = str(it.get('translation', '')).strip()
        spk = str(it.get('speaker', '')).strip()
        
        if itype in ('image', 'hr'):
            continue
            
        # Empty translation
        if orig and not trans:
            issues['empty_translation'].append((p.name, idx, orig[:60]))
            
        # Noise check
        for n_pat, n_label in NOISE_PATTERNS:
            if re.search(n_pat, orig) or re.search(n_pat, trans):
                issues['noise_item'].append((p.name, idx, f"{n_label}: {trans[:60]}"))
                
        # Term check
        for t_pat, t_msg in TERM_RULES:
            if re.search(t_pat, trans):
                # allow explanatory notes explaining historical names
                if not any(k in trans for k in ["旧译", "曾译", "早期译名", "译名演变", "台湾译名", "香港译名"]):
                    issues['outdated_term'].append((p.name, idx, f"{t_msg}: {trans[:70]}"))
                    
        # Speaker prefix leaked into translation
        m = re.match(r"^([^\s:：]{1,8})[:：]\s*(.*)$", trans)
        if m and not spk and itype == 'text':
            lead = m.group(1)
            # filter out non-speaker patterns like 注:, 来源:, 附:, 第X章:, or timestamps like 10:30
            if not re.match(r"^\d{1,2}$", lead) and not any(lead.startswith(k) for k in ["注", "来源", "附", "第", "参考", "特别感谢", "题外话", "读物", "备注", "站内链接"]):
                issues['speaker_in_text'].append((p.name, idx, f"Speaker '{lead}' in text: {trans[:60]}"))

print(f"Total posts audited: {len(posts)}")
for k, v in issues.items():
    print(f"\n=== {k.upper()} ({len(v)} occurrences) ===")
    for item in v[:8]:
        print(f"  {item}")
    if len(v) > 8:
        print(f"  ... and {len(v)-8} more")
