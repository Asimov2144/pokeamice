from pathlib import Path
import yaml, sys

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

# 1. Check vgc
p1 = Path("_posts/2019-05-09-interview-vgc-gamefreak-gear-project.md")
fm1 = yaml.safe_load(p1.read_text(encoding="utf-8").split("---", 2)[1])
for i, it in enumerate(fm1.get("parallel_items", [])):
    t = it.get("original", "") + " " + it.get("translation", "")
    if any(k in t.lower() for k in ["mega man", "review", "space for improvement", "popular content"]):
        print(f"VGC #{i}: orig={repr(it.get('original'))} | trans={repr(it.get('translation'))}")

# 2. Check 2013-10-10 XY Iwata Asks paragraph
p2 = Path("_posts/2013-10-10-interview-iwata-asks-xy-chapter-1-global-simultaneous-release.md")
fm2 = yaml.safe_load(p2.read_text(encoding="utf-8").split("---", 2)[1])
for i, it in enumerate(fm2.get("parallel_items", [])):
    if "\n" in it.get("original", "") or "\n" in it.get("translation", ""):
        print(f"XY Chapter 1 #{i}: orig={repr(it.get('original'))}")

# 3. Check 2023-08-25 Ichinose paragraph
p3 = Path("_posts/2023-08-25-interview-cedec-2023-sound-design-ichinose-paldea.md")
fm3 = yaml.safe_load(p3.read_text(encoding="utf-8").split("---", 2)[1])
for i, it in enumerate(fm3.get("parallel_items", [])):
    if "\n" in it.get("original", "") or "\n" in it.get("translation", ""):
        print(f"CEDEC Ichinose #{i}: orig={repr(it.get('original'))}")
