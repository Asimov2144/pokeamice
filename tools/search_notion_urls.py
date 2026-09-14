import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("_data/notion-interview-plan.md", "r", encoding="utf-8") as f:
    text = f.read()

# match table rows: | 序号 | 标题 | tags | url | mode |
rows = re.findall(r"\|\s*\d+\s*\|\s*\*\*([^\*]+)\*\*\s*\|\s*`([^`]+)`\s*\|\s*\[来源链接\]\(([^)]+)\)", text)
print(f"Total rows extracted from notion plan: {len(rows)}")

keywords = ["Shinji", "Miyazaki", "赛马", "自传漫画", "helix", "E3 2004", "GF如何设计", "远古官网", "BW开发访谈", "第二世代百余只", "不可思议迷宫", "Polygon", "Le Monde", "El Pais"]

for title, tags, url in rows:
    for k in keywords:
        if k.lower() in title.lower() or k.lower() in tags.lower():
            print(f"[{title}] tags={tags[:40]} url={url}")
            break
