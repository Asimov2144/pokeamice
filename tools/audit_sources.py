import sys
from pathlib import Path
import yaml

sys.stdout.reconfigure(encoding="utf-8")

posts = sorted(Path("_posts").glob("*interview*.md"))
has_source_dict = 0
has_source_url = 0
has_original_link = 0
no_source_at_all = 0

no_source_files = []

for p in posts:
    parts = p.read_text(encoding="utf-8").split("---", 2)
    if len(parts) < 3:
        continue
    try:
        fm = yaml.safe_load(parts[1])
    except:
        continue
        
    src = fm.get("source")
    src_url = fm.get("source_url")
    orig_link = fm.get("original_link")
    
    url = None
    if isinstance(src, dict):
        url = src.get("url")
        has_source_dict += 1
    elif isinstance(src, str) and src.startswith("http"):
        url = src
        has_source_url += 1
    elif src_url:
        url = src_url
        has_source_url += 1
    elif orig_link:
        url = orig_link
        has_original_link += 1
    else:
        no_source_at_all += 1
        no_source_files.append((p.name, fm.get("title", "")))

print(f"Total posts: {len(posts)}")
print(f"has_source_dict: {has_source_dict}")
print(f"has_source_url: {has_source_url}")
print(f"has_original_link: {has_original_link}")
print(f"no_source_at_all: {no_source_at_all}")
print("\nFiles with no source at all:")
for fn, t in no_source_files:
    print(f"  {fn} -> {t}")
