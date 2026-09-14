#!/usr/bin/env python3
import sys
import re
import yaml
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
posts = sorted(Path("_posts").glob("*interview*.md"))


def clean_text(s: str) -> str:
    if not isinstance(s, str):
        return s
    if "&quot;" not in s and "&#39;" not in s and "&amp;" not in s and "： " not in s:
        return s

    # Convert &quot; to proper quotes
    # Replace alternating or paired quotes
    parts = s.split("&quot;")
    if len(parts) > 1:
        res = []
        for i, part in enumerate(parts):
            res.append(part)
            if i < len(parts) - 1:
                res.append("“" if i % 2 == 0 else "”")
        s = "".join(res)

    s = s.replace("&#39;", "'")
    s = s.replace("&amp;", "&")
    return s


def clean_obj(obj):
    if isinstance(obj, str):
        return clean_text(obj)
    elif isinstance(obj, list):
        return [clean_obj(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: clean_obj(v) for k, v in obj.items()}
    return obj


# Also clean speaker prefix leaks from quote and items
name_map = {
    "森本：": "森本茂树：",
    "增田：": "增田顺一：",
    "杉森：": "杉森建：",
    "大森：": "大森滋：",
    "海野：": "海野隆雄：",
    "石原：": "石原恒和：",
    "阵内：": "阵内弘之：",
    "田尻：": "田尻智：",
}

count = 0
for p in posts:
    txt = p.read_text(encoding="utf-8")
    if any(k in txt for k in ["&quot;", "&#39;", "森本：", "增田：", "海野：", "石原：", "阵内："]):
        parts = txt.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            fm = clean_obj(fm)

            # Check quotes in fm
            if "quote" in fm and isinstance(fm["quote"], str):
                q = fm["quote"]
                for k, v in name_map.items():
                    if q.startswith(k):
                        q = q.replace(k, v, 1)
                fm["quote"] = q

            # Check parallel_items
            items = fm.get("parallel_items", [])
            for it in items:
                if isinstance(it, dict):
                    trans = it.get("translation", "")
                    spk = it.get("speaker", "")
                    if isinstance(trans, str):
                        for k, v in name_map.items():
                            clean_k = k.rstrip("：")
                            prefix_regex = r"^" + re.escape(clean_k) + r"[:：]\s*"
                            if re.match(prefix_regex, trans):
                                if not spk:
                                    it["speaker"] = v.rstrip("：")
                                it["translation"] = re.sub(prefix_regex, "", trans).strip()
                                break

            new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
            p.write_text(f"---\n{new_yaml}---\n{parts[2].lstrip()}", encoding="utf-8")
            count += 1
            print(f"Cleaned: {p.name}")

print(f"Total files cleaned: {count}")
