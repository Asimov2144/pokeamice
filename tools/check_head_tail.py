"""Inspect head and tail items of all posts to catch web scraping chrome.
"""
import sys
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

POSTS_DIR = Path("_posts")

def check_head_tail():
    posts = sorted(POSTS_DIR.glob("*interview*.md"))
    for p in posts:
        parts = p.read_text(encoding="utf-8").split("---", 2)
        if len(parts) < 3:
            continue
        try:
            fm = yaml.safe_load(parts[1])
        except Exception:
            continue
        items = fm.get("parallel_items", [])
        if not items:
            continue
        
        # Check first 3 items
        first_texts = [str(x.get("translation", x.get("original", ""))) for x in items[:3]]
        last_texts = [str(x.get("translation", x.get("original", ""))) for x in items[-3:]]
        
        # Suspicious markers
        suspicious = []
        for t in first_texts:
            if any(k in t for k in ["首页", "官方X账号", "网站使用方法", "排行榜", "TOP", "TOP30", "联系我们"]):
                suspicious.append(f"HEAD: {t[:40]}")
        for t in last_texts:
            if any(k in t for k in ["相关作品", "版权所有", "保留所有权利", "无断转载", "联系我们", "关闭", "隐私政策"]):
                suspicious.append(f"TAIL: {t[:40]}")
        
        if suspicious:
            print(f"[{p.name}] ({len(items)} items)")
            for s in suspicious:
                print(f"  {s}")

if __name__ == "__main__":
    check_head_tail()
