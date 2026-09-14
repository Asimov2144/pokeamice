import yaml
from pathlib import Path
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

posts = sorted(Path("_posts").glob("*interview*.md"))
post_list = []
for p in posts:
    parts = p.read_text(encoding="utf-8").split("---", 2)
    fm = yaml.safe_load(parts[1]) if len(parts) >= 3 else {}
    title = fm.get("title", "")
    url = ""
    src = fm.get("source", "")
    if isinstance(src, dict):
        url = src.get("url", "")
    elif isinstance(src, str):
        url = src
    items_count = len(fm.get("parallel_items", []))
    post_list.append({
        "path": p,
        "name": p.name,
        "title": title,
        "url": str(url),
        "items": items_count,
        "era": fm.get("era_skin")
    })

dupes = []
for i in range(len(post_list)):
    for j in range(i + 1, len(post_list)):
        p1 = post_list[i]
        p2 = post_list[j]
        d1 = p1["name"][:10]
        d2 = p2["name"][:10]
        if d1 != d2:
            continue
            
        url_match = p1["url"] and p2["url"] and (p1["url"] == p2["url"])
        
        t1 = re.sub(r"[^\w]", "", p1["title"].lower())
        t2 = re.sub(r"[^\w]", "", p2["title"].lower())
        
        k1 = set(p1["name"].replace(".md", "").split("-")[3:])
        k2 = set(p2["name"].replace(".md", "").split("-")[3:])
        k_sim = len(k1 & k2) / max(len(k1 | k2), 1)
        
        title_match = bool(t1 and t2 and (t1 in t2 or t2 in t1 or len(set(t1) & set(t2)) / max(len(set(t1) | set(t2)), 1) > 0.75))
        
        if url_match or k_sim > 0.5 or title_match:
            dupes.append((p1, p2, f"k_sim={k_sim:.2f}, url_match={url_match}, title_match={title_match}"))

print(f"Found {len(dupes)} duplicate pairs:")
for p1, p2, reason in dupes:
    print("---")
    print(f"P1: {p1['name']} | items: {p1['items']} | era: {p1['era']} | url: {p1['url']}")
    print(f"    title: {p1['title']}")
    print(f"P2: {p2['name']} | items: {p2['items']} | era: {p2['era']} | url: {p2['url']}")
    print(f"    title: {p2['title']}")
    print(f"Reason: {reason}")
