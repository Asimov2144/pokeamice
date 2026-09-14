import sys
from pathlib import Path
import yaml
import re
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

posts_dir = Path("_posts")
posts = sorted(posts_dir.glob("*interview*.md"))

issues = {
    "orig_is_chinese": [],
    "untranslated_japanese": [],
    "untranslated_english": [],
    "empty_trans": [],
    "mistranslations": [],
    "missing_metadata": [],
    "broken_yaml": [],
}

# Key terms to verify
OFFICIAL_CATCHPHRASES = [
    ("ポケモン、ゲットだぜ", "就决定是你了", "应当翻译为'我收服宝可梦了！'而非'就决定是你了'")
]

for p in posts:
    content = p.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        issues["broken_yaml"].append((p.name, "Missing frontmatter delimiters"))
        continue
    try:
        fm = yaml.safe_load(parts[1])
    except Exception as e:
        issues["broken_yaml"].append((p.name, str(e)))
        continue
        
    title = fm.get("title", "")
    source = fm.get("source")
    if not source:
        issues["missing_metadata"].append((p.name, "source is None or missing"))
        
    items = fm.get("parallel_items", [])
    for idx, it in enumerate(items):
        if not isinstance(it, dict):
            continue
        orig = str(it.get("original", "")).strip()
        trans = str(it.get("translation", "")).strip()
        itype = it.get("type", "paragraph")
        
        if itype in ("image", "hr"):
            continue
        if not orig:
            continue
            
        # 1. Check if original is actually Chinese (should be Japanese or English)
        # If orig has > 20 chars, no kana, > 50% CJK ideographs, and matches trans
        cjk_ideographs = len(re.findall(r"[\u4e00-\u9fff]", orig))
        kana_count = len(re.findall(r"[\u3040-\u309f\u30a0-\u30ff]", orig))
        if len(orig) > 20 and kana_count == 0 and cjk_ideographs / len(orig) > 0.4:
            # Check if this interview was originally Japanese
            if "nom" in p.name or "famitsu" in p.name or "denfami" in p.name or "gamefreak" in p.name:
                issues["orig_is_chinese"].append((p.name, idx, orig[:50]))
                
        # 2. Check untranslated Japanese in translation
        trans_kana = len(re.findall(r"[\u3040-\u309f\u30a0-\u30ff]", trans))
        if trans_kana > 8 and len(trans) > 15 and (trans_kana / len(trans) > 0.15):
            issues["untranslated_japanese"].append((p.name, idx, trans[:50]))
            
        # 3. Check untranslated English in translation
        orig_en = bool(re.search(r"^[A-Za-z0-9\s\.,\?!\"'’—–\(\)]+$", orig))
        trans_en = bool(re.search(r"^[A-Za-z0-9\s\.,\?!\"'’—–\(\)]+$", trans))
        if orig_en and trans_en and len(trans) > 50:
            if not any(k in trans.lower() for k in ["http", "copyright", "(c)"]):
                issues["untranslated_english"].append((p.name, idx, trans[:50]))
                
        # 4. Check empty translation
        if not trans:
            issues["empty_trans"].append((p.name, idx, orig[:50]))
            
        # 5. Check specific known mistranslations
        for o_sub, t_bad, desc in OFFICIAL_CATCHPHRASES:
            if o_sub in orig and t_bad in trans:
                issues["mistranslations"].append((p.name, idx, desc, orig[:40], trans[:40]))

print("=" * 60)
print(f"COMPREHENSIVE AUDIT REPORT ACROSS {len(posts)} POSTS")
print("=" * 60)
for k, v in issues.items():
    print(f"{k}: {len(v)} occurrences")
    for sample in v[:5]:
        print(f"   -> {sample}")
    if len(v) > 5:
        print(f"   ... and {len(v)-5} more")
    print()
