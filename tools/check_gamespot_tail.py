from pathlib import Path
import yaml, sys

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

p = Path("_posts/2018-10-18-interview-gamespot-lgpe-masuda.md")
fm = yaml.safe_load(p.read_text(encoding="utf-8").split("---", 2)[1])
items = fm["parallel_items"]
for i in range(50, len(items)):
    print(f"Item {i}: {repr(items[i].get('translation')[:60])}")
