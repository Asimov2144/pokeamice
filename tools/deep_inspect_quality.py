import re
import sys
import yaml
from pathlib import Path
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

POSTS_DIR = Path("_posts")
posts = sorted(POSTS_DIR.glob("*interview*.md"))

issues = defaultdict(list)

NOISE_SNIPPETS = [
    "About Us | Contact Us",
    "Interactive: #Pocketmonsters",
    "This page has been viewed",
    "All assorted characters, images and audio are ©",
    "Site Updates RSS",
    "Submit News",
    "Affiliates:",
    "Terms of Use & Rules",
    "▲トップへ",
    "ページトップへ",
    "メニュー へ戻る",
    "View the discussion thread",
]

HTML_ENTITIES = [
    "&quot;", "&#39;", "&amp;", "&lt;", "&gt;", "&nbsp;", "&#x27;", "&#x2F;"
]

for p in posts:
    content = p.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        issues["broken_frontmatter"].append((p.name, "No YAML boundary"))
        continue
    
    try:
        fm = yaml.safe_load(parts[1])
    except Exception as e:
        issues["yaml_error"].append((p.name, str(e)))
        continue
        
    title = fm.get("title", "")
    for ent in HTML_ENTITIES:
        if ent in title:
            issues["html_entity_in_title"].append((p.name, f"Entity '{ent}' in title: {title}"))

    items = fm.get("parallel_items", [])
    for idx, it in enumerate(items):
        if not isinstance(it, dict):
            continue
            
        orig = str(it.get("original", "")).strip()
        trans = str(it.get("translation", "")).strip()
        spk = str(it.get("speaker", "")).strip()
        itype = it.get("type", "paragraph")
        
        # 1. Noise snippets
        for ns in NOISE_SNIPPETS:
            if ns.lower() in orig.lower() or ns.lower() in trans.lower():
                issues["noise_snippet"].append((p.name, idx, f"Noise '{ns}': {trans[:60]}"))
                
        # 2. HTML entities in text
        for ent in HTML_ENTITIES:
            if ent in trans and ent not in ["&amp;"]: # &amp; can rarely be valid code, check context
                issues["html_entity_in_trans"].append((p.name, idx, f"Entity '{ent}': {trans[:60]}"))
                
        # 3. Speaker prefix inside translation
        m = re.match(r"^([^\s:：]{2,6})[:：]\s*(.*)$", trans)
        if m and not spk and itype == "paragraph":
            lead = m.group(1)
            if lead in ["增田", "大森", "杉森", "石原", "田尻", "森本", "海野", "岩尾", "西野", "西田"]:
                issues["speaker_leaked_in_text"].append((p.name, idx, f"Speaker '{lead}': {trans[:60]}"))

        # 4. Untranslated identical text (when length > 25 and not code/URL)
        if orig and trans and orig == trans and len(orig) > 25:
            if not orig.startswith("http") and not orig.startswith("/") and not "©" in orig:
                issues["identical_untranslated"].append((p.name, idx, orig[:60]))

print(f"==================================================")
print(f"Deep Quality Audit on {len(posts)} interview posts")
print(f"==================================================")
for cat, lst in issues.items():
    print(f"\n[{cat.upper()}] ({len(lst)} occurrences):")
    for sample in lst[:10]:
        print(f"  {sample}")
    if len(lst) > 10:
        print(f"  ... and {len(lst) - 10} more")

