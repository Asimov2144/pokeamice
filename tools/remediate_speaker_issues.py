import re
import sys
from pathlib import Path
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def fix_denfami_morimoto():
    p = Path("_posts/2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md")
    content = p.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        return
    fm = yaml.safe_load(parts[1])
    items = fm.get("parallel_items", [])
    changed = False

    for idx, it in enumerate(items):
        if not isinstance(it, dict):
            continue
        orig = it.get("original", "")
        trans = it.get("translation", "")
        spk = it.get("speaker")

        # Handle 一同 / 众人
        if ("一同：" in orig or "众人：" in trans) and not spk:
            clean_orig = re.sub(r"^一同[：:]\s*", "", orig)
            clean_trans = re.sub(r"^(众人|一同)[：:]\s*", "", trans)
            it["speaker"] = "众人"
            it["original"] = clean_orig
            it["translation"] = clean_trans
            changed = True
            print(f"Fixed denfami morimoto #{idx}: {clean_trans}")
        elif "相关文章：" in trans and not spk:
            it["type"] = "note"
            changed = True
            print(f"Fixed denfami morimoto #{idx} -> note")

    if changed:
        fm["parallel_items"] = items
        new_content = "---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + parts[2]
        p.write_text(new_content, encoding="utf-8")
        print("Saved 2016-04-18 post.")

def fix_denfami_heritage():
    p = Path("_posts/2017-07-03-interview-denfami-ohmori-onoue-gamefreak-heritage.md")
    content = p.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        return
    fm = yaml.safe_load(parts[1])
    items = fm.get("parallel_items", [])
    changed = False

    for idx, it in enumerate(items):
        if not isinstance(it, dict):
            continue
        trans = str(it.get("translation", "")).strip()
        if trans.startswith("※") and not it.get("speaker"):
            it["type"] = "note"
            changed = True
            print(f"Fixed heritage footnote #{idx}: {trans[:40]}")

    if changed:
        fm["parallel_items"] = items
        new_content = "---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + parts[2]
        p.write_text(new_content, encoding="utf-8")
        print("Saved 2017-07-03 post.")

def fix_topofarmer():
    p = Path("_posts/2014-11-01-interview-topofarmer-ideame-masuda-ohmori.md")
    content = p.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        return
    fm = yaml.safe_load(parts[1])
    items = fm.get("parallel_items", [])
    changed = False

    for idx, it in enumerate(items):
        if not isinstance(it, dict):
            continue
        trans = str(it.get("translation", "")).strip()
        orig = str(it.get("original", "")).strip()

        if "（孩子们：耶！）" in trans:
            it["speaker"] = "现场孩子们"
            it["translation"] = "耶！"
            it["original"] = "¡Sí!" if "¡Sí!" in orig else orig
            changed = True
        elif "（孩子们：噢……）" in trans:
            it["speaker"] = "现场孩子们"
            it["translation"] = "噢……"
            changed = True
        elif "（大森：笑）" in trans:
            it["speaker"] = "大森滋"
            it["translation"] = "（笑）"
            changed = True
        elif "（问：大森？增田？）：" in trans:
            it["speaker"] = "大森滋"
            it["translation"] = re.sub(r"^（问：大森？增田？）：\s*", "", trans)
            changed = True
        elif trans.startswith("属性：加泰罗尼亚"):
            it["type"] = "note"
            changed = True

    if changed:
        fm["parallel_items"] = items
        new_content = "---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + parts[2]
        p.write_text(new_content, encoding="utf-8")
        print("Saved 2014-11-01 post.")

def fix_cgworld():
    p = Path("_posts/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline.md")
    content = p.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        return
    fm = yaml.safe_load(parts[1])
    items = fm.get("parallel_items", [])
    
    new_items = []
    changed = False
    for idx, it in enumerate(items):
        if not isinstance(it, dict):
            new_items.append(it)
            continue
        trans = str(it.get("translation", "")).strip()
        orig = str(it.get("original", "")).strip()

        # Remove pagination residue "下一页："
        if trans.startswith("下一页：") or orig.startswith("次ページ："):
            changed = True
            print(f"Removed CGWorld pagination residue #{idx}: {trans}")
            continue

        if trans.startswith("照片从右起：") or trans.startswith("发售："):
            it["type"] = "note"
            changed = True

        new_items.append(it)

    if changed:
        fm["parallel_items"] = new_items
        new_content = "---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + parts[2]
        p.write_text(new_content, encoding="utf-8")
        print("Saved 2017-07-10 post.")

def fix_miscellaneous():
    # 2000-11-01
    p = Path("_posts/2000-11-01-interview-nintendo-power-gs-bigwigs.md")
    if p.exists():
        parts = p.read_text(encoding="utf-8").split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            changed = False
            for it in fm.get("parallel_items", []):
                if isinstance(it, dict) and str(it.get("translation", "")).startswith("相关访谈："):
                    it["type"] = "note"
                    changed = True
            if changed:
                p.write_text("---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + parts[2], encoding="utf-8")
                print("Saved 2000-11-01 post.")

    # 2010-05-12
    p = Path("_posts/2010-05-12-interview-wedge-ishihara-pokemon-disney.md")
    if p.exists():
        parts = p.read_text(encoding="utf-8").split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            changed = False
            for it in fm.get("parallel_items", []):
                if isinstance(it, dict) and str(it.get("translation", "")).startswith("此前内容："):
                    it["type"] = "note"
                    changed = True
            if changed:
                p.write_text("---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + parts[2], encoding="utf-8")
                print("Saved 2010-05-12 post.")

    # 2011-03-01
    p = Path("_posts/2011-03-01-interview-nintendo-power-bw-masuda-sugimori.md")
    if p.exists():
        parts = p.read_text(encoding="utf-8").split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            items = []
            changed = False
            for it in fm.get("parallel_items", []):
                if isinstance(it, dict):
                    t = str(it.get("translation", "")).strip()
                    if t == "相关文章：" or not t:
                        changed = True
                        continue
                    if t.startswith("熔岩博士的注释："):
                        it["type"] = "note"
                        changed = True
                items.append(it)
            if changed:
                fm["parallel_items"] = items
                p.write_text("---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + parts[2], encoding="utf-8")
                print("Saved 2011-03-01 post.")

    # 2015-07-14
    p = Path("_posts/2015-07-14-interview-movie18-yuyama-hoopa-model-sheets.md")
    if p.exists():
        parts = p.read_text(encoding="utf-8").split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            changed = False
            for it in fm.get("parallel_items", []):
                if isinstance(it, dict):
                    t = str(it.get("translation", "")).strip()
                    if t.startswith("最终部分：") or t.startswith("「巴尔札："):
                        it["type"] = "heading"
                        it["level"] = 3
                        changed = True
            if changed:
                p.write_text("---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + parts[2], encoding="utf-8")
                print("Saved 2015-07-14 post.")

    # 2016-08-25
    p = Path("_posts/2016-08-25-interview-nikkei-utsunomiya-pokemon-go.md")
    if p.exists():
        parts = p.read_text(encoding="utf-8").split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            changed = False
            for it in fm.get("parallel_items", []):
                if isinstance(it, dict) and str(it.get("translation", "")).startswith("（采访者："):
                    it["type"] = "note"
                    changed = True
            if changed:
                p.write_text("---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + parts[2], encoding="utf-8")
                print("Saved 2016-08-25 post.")

if __name__ == "__main__":
    fix_denfami_morimoto()
    fix_denfami_heritage()
    fix_topofarmer()
    fix_cgworld()
    fix_miscellaneous()
    print("All remediations applied.")
