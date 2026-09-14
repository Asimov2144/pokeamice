from pathlib import Path
import yaml, sys

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

posts = sorted(Path("_posts").glob("*interview*.md"))
for p in posts:
    fm = yaml.safe_load(p.read_text(encoding="utf-8").split("---", 2)[1])
    for i, it in enumerate(fm.get("parallel_items", [])):
        t = (it.get("translation", "") + " " + it.get("original", "")).lower()
        if any(k in t for k in ["newsletter", "新闻通讯", "退订", "unsubscribe", "sign up", "注册", "电子邮件地址", "email address", "广告", "advertisement"]):
            # Filter out genuine text where '广告' is mentioned
            orig = str(it.get("original", "")).strip()
            trans = str(it.get("translation", "")).strip()
            if orig.lower() in ["advertisement", "ad", "广告"] or trans in ["广告", "赞助商内容"]:
                print(f"{p.name} #{i}: [PURE AD LABEL] {orig} | {trans}")
            elif any(k in orig.lower() for k in ["newsletter", "unsubscribe", "sign up for", "privacy policy"]):
                print(f"{p.name} #{i}: [NEWSLETTER/POLICY] {orig[:40]} | {trans[:40]}")
