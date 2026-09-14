from pathlib import Path
import yaml
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

posts = sorted(Path("_posts").glob("*interview*.md"))
for p in posts:
    parts = p.read_text(encoding="utf-8").split("---", 2)
    if len(parts) < 3:
        continue
    fm = yaml.safe_load(parts[1])
    for idx, it in enumerate(fm.get("parallel_items", [])):
        if isinstance(it, dict) and it.get("speaker") == "受访嘉宾":
            trans = str(it.get("translation", ""))[:60]
            print(f"{p.name}#{idx}: {trans}")
