from pathlib import Path
import yaml, sys

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

p = Path("_posts/2020-04-01-interview-pokemon-company-career.md")
fm = yaml.safe_load(p.read_text(encoding="utf-8").split("---", 2)[1])
items = fm["parallel_items"]
for i in range(15):
    sp = items[i].get("speaker")
    print(f"Item {i}: sp={sp} | {items[i].get('translation')[:60]}")
