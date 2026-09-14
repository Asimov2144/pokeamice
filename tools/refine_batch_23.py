import re
import sys
import yaml
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def refine_pkmn_1060():
    p = Path("_posts/2017-08-10-interview-gameinformer-how-game-freak-designs-pokemon-creatures.md")
    content = p.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    fm = yaml.safe_load(parts[1])
    fm["image"] = "/assets/img/interviews/2017-08-10-interview-gameinformer-how-game-freak-designs-pokemon-creatures/design_01.jpg"
    
    # Check items
    for it in fm.get("parallel_items", []):
        if it.get("type") == "image":
            if "design_01" in it.get("image", ""):
                it["caption"] = "Game Freak 内部开发企划档案与设计草案"
            elif "design_02" in it.get("image", ""):
                it["caption"] = "Game Freak 会议室陈列架上摆放的全世代宝可梦官方模型"
            elif "design_03" in it.get("image", ""):
                it["caption"] = "增田顺一在白板上随手画出的‘三头猫’草图，用以阐释‘进化不能只靠简单堆砌器官’的逻辑"
            elif "design_04" in it.get("image", ""):
                it["caption"] = "第一世代锐利棱角分明的眼睛与第七世代西狮海壬圆润柔和眼睛的演变对比"

    new_content = "---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + parts[2]
    p.write_text(new_content, encoding="utf-8")
    print("Refined PKMN-1060")

def refine_pkmn_1061():
    p = Path("_posts/2017-08-14-interview-gameinformer-why-ruby-and-sapphire-were-most-challenging.md")
    content = p.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    fm = yaml.safe_load(parts[1])
    fm["image"] = "/assets/img/interviews/2017-08-14-interview-gameinformer-why-ruby-and-sapphire-were-most-challenging/rs_dev_01.jpg"
    
    for it in fm.get("parallel_items", []):
        if it.get("type") == "image":
            it["caption"] = "2002年 GBA 原版《宝可梦 红宝石·蓝宝石》封面神兽固拉多与盖欧卡"

    new_content = "---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + parts[2]
    p.write_text(new_content, encoding="utf-8")
    print("Refined PKMN-1061")

def refine_pkmn_1062():
    p = Path("_posts/2018-06-25-interview-funsproject-atsuko-nishida-shoko-nakagawa-character-design.md")
    content = p.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    fm = yaml.safe_load(parts[1])
    slug = "2018-06-25-interview-funsproject-atsuko-nishida-shoko-nakagawa-character-design"
    fm["image"] = f"/assets/img/interviews/{slug}/thumb.jpg"

    items = fm.get("parallel_items", [])
    new_items = []

    # Insert hero image after section heading
    hero_inserted = False
    img01_inserted = False
    img02_inserted = False
    img03_inserted = False

    for idx, it in enumerate(items):
        if not isinstance(it, dict):
            new_items.append(it)
            continue
        
        orig = it.get("original", "")
        trans = it.get("translation", "")
        spk = it.get("speaker")

        # Fix nickname
        if "小幸碳" in trans:
            trans = trans.replace("小幸碳", "翔子碳")
            it["translation"] = trans

        # Clean prefix in first dialogue turns
        if orig.startswith("翔子（以下、中川）"):
            it["original"] = re.sub(r"^翔子（以下、中川）\s*", "", orig)
            it["translation"] = re.sub(r"^翔子（以下简称中川）[：:]\s*", "", trans)
        elif orig.startswith("あつこ（以下、にしだ）"):
            it["original"] = re.sub(r"^あつこ（以下、にしだ）\s*", "", orig)
            it["translation"] = re.sub(r"^敦子（以下简称西田）[：:]\s*", "", trans)

        new_items.append(it)

        # Insert hero thumb after the first intro paragraph
        if not hero_inserted and it.get("type") == "paragraph" and "中川翔子による一対一のトークセッション" in orig:
            new_items.append({
                "type": "image",
                "image": f"/assets/img/interviews/{slug}/thumb.jpg",
                "caption": "西田敦子与中川翔子在《FUN'S PROJECT》对谈现场，共同展示皮卡丘插画与签名板",
                "alt": "西田敦子与中川翔子对谈现场合影"
            })
            hero_inserted = True

        # Insert img01 around notebook / daifuku discussion
        if not img01_inserted and "コクヨの大学ノート" in orig:
            new_items.append({
                "type": "image",
                "image": f"/assets/img/interviews/{slug}/img01.jpg",
                "caption": "西田敦子展示用于记录灵感与构想草图的横线大学笔记",
                "alt": "西田敦子的灵感笔记"
            })
            img01_inserted = True

        # Insert img02 around part 2 dot art heading
        if not img02_inserted and "ドット絵は私の原点" in orig:
            new_items.append({
                "type": "image",
                "image": f"/assets/img/interviews/{slug}/img02.jpg",
                "caption": "中川翔子与西田敦子就点阵原画与宝可梦设计进行热烈讨论",
                "alt": "点阵绘图与插画心得探讨"
            })
            img02_inserted = True

        # Insert img03 near the end
        if not img03_inserted and idx >= len(items) - 5 and it.get("type") == "paragraph":
            new_items.append({
                "type": "image",
                "image": f"/assets/img/interviews/{slug}/img03.jpg",
                "caption": "西田敦子手绘的皮卡丘纪念色纸与对谈纪念合影",
                "alt": "皮卡丘特制色纸合影"
            })
            img03_inserted = True

    fm["parallel_items"] = new_items
    new_content = "---\n" + yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n" + parts[2]
    p.write_text(new_content, encoding="utf-8")
    print(f"Refined PKMN-1062 ({len(new_items)} items)")

if __name__ == "__main__":
    refine_pkmn_1060()
    refine_pkmn_1061()
    refine_pkmn_1062()
    print("Refinements finished.")
