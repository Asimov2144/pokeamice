import sys
from pathlib import Path
import re
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

POSTS_DIR = Path("_posts")

target_files = sorted([p.name for p in POSTS_DIR.glob("*interview*.md")])

print("=== Cleaning internal newlines in targeted posts ===")

for fname in target_files:
    fpath = POSTS_DIR / fname
    if not fpath.exists():
        continue
    raw = fpath.read_text(encoding="utf-8")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        continue

    fm = yaml.safe_load(parts[1])
    if not fm or "parallel_items" not in fm:
        continue

    cleaned_count = 0
    for item in fm["parallel_items"]:
        if not isinstance(item, dict):
            continue
        for key in ["original", "translation"]:
            val = item.get(key)
            if isinstance(val, str) and "\n" in val:
                # If there are consecutive newlines \n\n, preserve them
                # Single \n between CJK characters should be joined without spaces
                # Single \n between English words should be joined with a space
                def replace_cjk_newline(match):
                    c1 = match.group(1)
                    c2 = match.group(2)
                    # if both are CJK or punctuation, join directly
                    if re.match(r'[\u4e00-\u9fff\u3040-\u30ff\u3000-\u303f\uff00-\uffef]', c1) and \
                       re.match(r'[\u4e00-\u9fff\u3040-\u30ff\u3000-\u303f\uff00-\uffef]', c2):
                        return f"{c1}{c2}"
                    return f"{c1} {c2}"

                # First protect \n\n
                val_clean = val.replace("\r\n", "\n")
                val_clean = re.sub(r'(?<!\n)\n(?!\n)', ' \n ', val_clean)
                val_clean = re.sub(r'([^\s\n])\s*\n\s*([^\s\n])', replace_cjk_newline, val_clean)
                val_clean = re.sub(r'[ \t]+', ' ', val_clean).strip()
                if val_clean != val:
                    item[key] = val_clean
                    cleaned_count += 1

    if cleaned_count > 0:
        new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
        body = parts[2] if len(parts) >= 3 else ""
        fpath.write_text(f"---\n{new_yaml}---\n{body}", encoding="utf-8")
        print(f"Cleaned {cleaned_count} items in {fname}")

print("Internal newline cleaning complete.")
