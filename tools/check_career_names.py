from pathlib import Path
import yaml, sys

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

p = Path("_posts/2020-04-01-interview-pokemon-company-career.md")
fm = yaml.safe_load(p.read_text(encoding="utf-8").split("---", 2)[1])
items = fm["parallel_items"]
for i, it in enumerate(items):
    orig = it.get("original", "")
    trans = it.get("translation", "")
    if any(k in orig for k in ["リーダー", "室長", "マネージャー", "部長", "氏", "様"]) or any(k in trans for k in ["室长", "部长", "经理"]):
        print(f"Item {i}: orig={orig[:50]} | trans={trans[:50]}")
