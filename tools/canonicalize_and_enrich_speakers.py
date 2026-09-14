"""Enrich and canonicalize speaker fields across all interview posts in _posts/.
- Standardizes diverse speaker names (e.g., Masuda, 増田, 增田 -> 增田顺一)
- Regex-extracts speakers from unlabelled dialogue paragraphs
- Cleans leading speaker prefix tokens from translations/originals when appropriate
"""

import re
import sys
from pathlib import Path
import yaml

sys.stdout.reconfigure(encoding='utf-8')

POSTS_DIR = Path('_posts')

CANONICAL_MAP = {
    # Key creators
    '増田順一': '增田顺一', '増田': '增田顺一', '增田': '增田顺一', 'Masuda': '增田顺一', 'Junichi Masuda': '增田顺一',
    '増田氏': '增田顺一', '增田氏': '增田顺一', 'Mr. Masuda': '增田顺一', '增田先生': '增田顺一', 'JM': '增田顺一', 'J.M.': '增田顺一',
    'Junichi Masuda, Director': '增田顺一',
    '杉森建': '杉森建', '杉森': '杉森建', 'Sugimori': '杉森建', 'Ken Sugimori': '杉森建', '杉森氏': '杉森建', '杉森建建': '杉森建',
    '田尻智': '田尻智', '田尻': '田尻智', 'Tajiri': '田尻智', 'Satoshi Tajiri': '田尻智', '田尻氏': '田尻智',
    '森本茂树': '森本茂树', '森本茂樹': '森本茂树', '森本': '森本茂树', 'Morimoto': '森本茂树', 'Shigeki Morimoto': '森本茂树',
    'Shigeki Morimoto, Game Director': '森本茂树', '森本氏': '森本茂树',
    '大森滋': '大森滋', '大森': '大森滋', 'Ohmori': '大森滋', 'Shigeru Ohmori': '大森滋', '大森氏': '大森滋',
    'Mr. Ohmori': '大森滋', '大森先生': '大森滋', 'S.O.': '大森滋', '大森滋（策划）': '大森滋',
    '海野隆雄': '海野隆雄', '海野': '海野隆雄', 'Unno': '海野隆雄', 'Takao Unno': '海野隆雄', '海野氏': '海野隆雄',
    'Mr. Unno': '海野隆雄', '海野先生': '海野隆雄', '海野隆雄（艺术总监）': '海野隆雄',
    '松岛贤二': '松岛贤二', '松島': '松岛贤二', 'Matsushima': '松岛贤二', '松岛': '松岛贤二', '松岛贤治': '松岛贤二',
    'Kenji Matsushima, Planner': '松岛贤二',
    '井部真那': '井部真那', '井部': '井部真那', 'Ibe': '井部真那',
    '石原恒和': '石原恒和', '石原': '石原恒和', 'Ishihara': '石原恒和', 'Tsunekazu Ishihara': '石原恒和',
    '石原氏': '石原恒和', '石原 恒和 （いしはら つねかず）': '石原恒和',
    '田中宏和': '田中宏和', '田中': '田中宏和', 'Tanaka': '田中宏和', 'Hirokazu Tanaka': '田中宏和',
    '汤山邦彦': '汤山邦彦', '湯山': '汤山邦彦', 'Yuyama': '汤山邦彦', 'Kunihiko Yuyama': '汤山邦彦', '答（汤山邦彦）': '汤山邦彦',
    '尾上将之': '尾上将之', '尾上': '尾上将之', 'Onoue': '尾上将之', 'Masayuki Onoue': '尾上将之', '尾上氏': '尾上将之',
    '渡边哲也': '渡边哲也', '渡辺': '渡边哲也', '渡边': '渡边哲也', 'Watanabe': '渡边哲也', '渡辺氏': '渡边哲也',
    '西野弘二': '西野弘二', '西野浩二': '西野弘二', '西野': '西野弘二', 'Nishino': '西野弘二',
    '鹤田': '鹤田', '鶴田': '鹤田', 'Tsuruta': '鹤田',
    '川知丸': '川知丸武', '川知丸武': '川知丸武', 'Kawachimaru': '川知丸武', 'Takeshi Kawachimaru': '川知丸武',
    '河内丸': '川知丸武', '河内丸武志': '川知丸武', '川内丸': '川知丸武', 'TK': '川知丸武',
    '须崎': '须崎春树', '須崎': '须崎春树', 'Suzaki': '须崎春树', 'Haruki Suzaki': '须崎春树',
    '岩尾和昌': '岩尾和昌', '岩尾': '岩尾和昌', 'Iwao': '岩尾和昌', 'Kazumasa Iwao': '岩尾和昌', '岩尾氏': '岩尾和昌', 'Mr. Iwao': '岩尾和昌', '岩尾先生': '岩尾和昌',
    '宇都宫崇人': '宇都宫崇人', '宇都宮崇人': '宇都宫崇人', 'Utsunomiya': '宇都宫崇人', 'Takato Utsunomiya': '宇都宫崇人',
    '西田敦子': '西田敦子', '西田': '西田敦子', 'Nishida': '西田敦子', 'Atsuko Nishida': '西田敦子',
    '名手工作': '名手工作', '名手': '名手工作', 'Nabana': '名手工作', 'Kensaku Nabana': '名手工作', '菜花健作': '菜花健作',
    '宫崎慎二': '宫崎慎二', '宫崎': '宫崎慎二', '宮崎': '宫崎慎二', 'Miyazaki': '宫崎慎二', 'Shinji Miyazaki': '宫崎慎二',
    '一之瀬剛': '一之濑刚', 'Tsuyoshi Ichinose': '一之濑刚',
    '太田健程': '太田健典', 'Takenori Ota': '太田健典', '太田健典': '太田健典', '太田': '太田健典',
    '大森滋 / 増田順一': '大森滋 / 增田顺一',
    '田谷＆一之瀬': '田谷正夫 & 一之濑刚',
    '宇都宮 崇人': '宇都宫崇人', '宇都宮崇人': '宇都宫崇人',
    '増田順一（ディレクター・コンポーザー）': '增田顺一', '増田順一（開発部長）': '增田顺一', '増田順一（ディレクター）': '增田顺一',
    '增田顺一（总监）': '增田顺一', '增田顺一（制作人）': '增田顺一', '增田顺一（游戏系列总监）': '增田顺一',
    '杉森建（アートディレクター）': '杉森建', '杉森建（艺术总监）': '杉森建',
    '渡辺哲也（プログラマー）': '渡边哲也', '西野弘二（プランナー）': '西野弘二',
    '森本茂樹（プログラマー）': '森本茂树', '森本茂樹（プログラマー・プランナー）': '森本茂树',
    '海野隆雄（总监）': '海野隆雄', '海野隆雄（3D艺术总监）': '海野隆雄',
    '大村祐介（设计师）': '大村祐介', '井部真那（设计师）': '井部真那',
    '景山将太（サウンドプロジェクトリーダー）': '景山将太',
    '佐藤仁美（游戏音乐设计）': '佐藤仁美', '一之濑刚（游戏音乐总监）': '一之濑刚', '宫崎慎二（动画作曲家）': '宫崎慎二',
    'S.O. (大森滋)': '大森滋', '名花健策（游戏设计）': '菜花健作', '名花健作': '菜花健作',
    'NOM 編集部（杉森建 証言）': '杉森建', 'NOM 編集部（増田順一 証言）': '增田顺一', 'NOM 編集部（森本茂樹 証言）': '森本茂树',
    'NOM 編集部': 'N.O.M采访者', 'Nintendo Online Magazine (NOM)': 'N.O.M采访者', 'NOM': 'N.O.M采访者',
    'Game Informer 记者': 'Game Informer', 'Eurogamer 记者': 'Eurogamer',
    'Fami通（提问）': 'Fami通', 'Pokemon.com（提问）': 'Pokemon.com', 'GameSpot（提问）': 'GameSpot',
    'Corocoro（提问）': '快乐快乐月刊', 'NewsPicks（提问）': 'NewsPicks',
    'PR clarifies': '宝可梦官方PR',
    
    # Interviewers / Questions / Media Outlets
    '问': '提问', '問': '提问', 'Q': '提问', 'Question': '提问', '记者': '提问', '記者': '提问',
    '采访者': '提问', '采访': '提问', '提问者': '提问', '编者': '提问', '编辑部': '提问',
    '向石原先生提问': '提问', '采访田尻智社长': '提问', '采访石原社长': '提问',
    '第一个问题是': '提问', '下一个问题是': '提问', '第二个问题是': '提问',
    'IGN': 'IGN记者', 'IGN:': 'IGN记者', 'IGN记者': 'IGN记者',
    'TIME': '时代周刊', '时代周刊': '时代周刊',
    'GI': 'Game Informer', 'Game Informer': 'Game Informer',
    'NP': 'Nintendo Power', 'Nintendo Power': 'Nintendo Power',
    '4Gamer': '4Gamer', '4Gamer 记者': '4Gamer',
    'Famitsu': 'Fami通', 'Fami通': 'Fami通', 'ファミ通': 'Fami通', 'Fami通记者': 'Fami通',
    'Pokemon.com': 'Pokemon.com', 'P.Com': 'Pokemon.com',
    'G4': 'G4记者', 'G4记者': 'G4记者',
    '電ファミ': '电玩志', 'Denfami': '电玩志', '电玩志': '电玩志', '电玩迷电玩（提问）': '电玩志',
    '答': '受访嘉宾', '受访者': '受访嘉宾'
}

# Prefixes to strip when extracting
PREFIX_PATTERNS = [
    (r'^([A-Za-z\u4e00-\u9fa5\u3040-\u30ff]{1,10})[:：>>＞＞\-\–\—]\s*', 1),
    (r'^(Junichi Masuda|Shigeru Ohmori|Ken Sugimori|Satoshi Tajiri|Shigeki Morimoto|Tsunekazu Ishihara)[:：\-\–\—\s]\s*', 1),
    (r'^(増田|杉森|田尻|森本|大森|海野|石原|田中|湯山|尾上|渡辺|西野)>>\s*', 1),
]

def canonicalize_speaker(sp: str) -> str:
    if not sp:
        return ""
    sp_clean = sp.strip().rstrip(':：-–— ')
    return CANONICAL_MAP.get(sp_clean, sp_clean)

def extract_speaker_from_text(orig: str, trans: str) -> tuple[str, str, str]:
    """Returns (detected_speaker, cleaned_orig, cleaned_trans)"""
    for patt, group_idx in PREFIX_PATTERNS:
        m_trans = re.match(patt, trans)
        m_orig = re.match(patt, orig)
        
        raw_name = None
        if m_trans:
            candidate = m_trans.group(group_idx).strip()
            if candidate in CANONICAL_MAP or any(k in candidate for k in ['增田', '杉森', '田尻', '森本', '大森', '石原', '记者', '问', 'IGN']):
                raw_name = candidate
        elif m_orig:
            candidate = m_orig.group(group_idx).strip()
            if candidate in CANONICAL_MAP or any(k in candidate for k in ['Masuda', 'Sugimori', 'Tajiri', 'Morimoto', 'Ohmori', 'Ishihara', 'IGN', 'TIME', '増田', '杉森']):
                raw_name = candidate
                
        if raw_name:
            canon = canonicalize_speaker(raw_name)
            return canon, orig, trans
            
    return "", orig, trans

def process_file(path: Path) -> dict:
    raw = path.read_text(encoding='utf-8')
    parts = raw.split('---', 2)
    if len(parts) < 3:
        return {}
    
    fm = yaml.safe_load(parts[1])
    items = fm.get('parallel_items', [])
    updated = 0
    canonicalized = 0
    
    unique_speakers = set()

    for it in items:
        if it.get('type') in ('image', 'hr'):
            continue
            
        sp = (it.get('speaker') or '').strip()
        orig = str(it.get('original') or '')
        trans = str(it.get('translation') or '')
        
        if sp:
            canon = canonicalize_speaker(sp)
            if canon != sp:
                it['speaker'] = canon
                canonicalized += 1
            unique_speakers.add(canon)
        else:
            detected, c_orig, c_trans = extract_speaker_from_text(orig, trans)
            if detected:
                it['speaker'] = detected
                unique_speakers.add(detected)
                updated += 1

    # Update metadata interviewee if needed
    non_q_speakers = [s for s in unique_speakers if not any(q in s for q in ['提问', '记者', '问', 'IGN', 'TIME', 'GI', '4Gamer', 'Fami通'])]
    if non_q_speakers:
        fm['interviewee'] = ", ".join(sorted(non_q_speakers))
        
    fm_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    body = parts[2] if len(parts) >= 3 else ""
    path.write_text(f"---\n{fm_yaml}---\n{body}", encoding='utf-8')
    
    return {
        'file': path.name,
        'updated': updated,
        'canonicalized': canonicalized,
        'speakers': list(unique_speakers)
    }

def main():
    print("=== Enriching and Canonicalizing Speakers ===")
    total_updated = 0
    total_canon = 0
    all_speakers = {}
    
    for p in sorted(POSTS_DIR.glob('*interview*.md')):
        res = process_file(p)
        if res:
            total_updated += res['updated']
            total_canon += res['canonicalized']
            for s in res['speakers']:
                all_speakers[s] = all_speakers.get(s, 0) + 1
            if res['updated'] > 0 or res['canonicalized'] > 0:
                print(f"  {res['file']}: +{res['updated']} extracted, {res['canonicalized']} canonicalized | Speakers: {res['speakers']}")

    print(f"\nFinished! Total new speakers extracted: {total_updated}, Total canonicalized: {total_canon}")
    print("\nAll identified speakers across database:")
    for sp, cnt in sorted(all_speakers.items(), key=lambda x: -x[1]):
        print(f"  {sp}: in {cnt} posts")

if __name__ == "__main__":
    main()
