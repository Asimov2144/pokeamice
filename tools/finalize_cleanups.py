"""Final targeted cleanups for remaining edge-case items.
"""
from pathlib import Path
import yaml
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

POSTS_DIR = Path("_posts")

def finalize():
    # 1. 2016-05-12 Pokken
    p_pokken = POSTS_DIR / "2016-05-12-interview-pokken-tournament-inside.md"
    if p_pokken.exists():
        text = p_pokken.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        fm = yaml.safe_load(parts[1])
        items = fm["parallel_items"]
        new_items = []
        for it in items:
            orig = str(it.get("original", "")).strip()
            trans = str(it.get("translation", "")).strip()
            if "ホーム › 任天堂" in orig or "首页 › 任天堂" in trans:
                continue
            if any(k in orig for k in ["しまむら", "セガ ラッキーくじ", "METAL ROBOT魂", "最新ニュースをもっと見る", "ツイッター フェイスブック"]):
                continue
            new_items.append(it)
        fm["parallel_items"] = new_items
        new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
        p_pokken.write_text(f"---\n{new_yaml}---\n{parts[2].lstrip()}", encoding="utf-8")
        print(f"Cleaned Pokken: {len(items)} -> {len(new_items)} items")

    # 2. 2013-01-11 Masuda / Kawachimaru G4TV
    p_g4 = POSTS_DIR / "2013-01-11-interview-junichi-masuda-takeshi-kawachimaru.md"
    if p_g4.exists():
        text = p_g4.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        fm = yaml.safe_load(parts[1])
        items = fm["parallel_items"]
        new_items = [it for it in items if not any(k in str(it.get("original", "")) for k in ["g4tv.com", "files.g4tv.com", "Blog post #694081", "Comments are closed"])]
        new_items = [it for it in new_items if not any(k in str(it.get("translation", "")) for k in ["博客帖子编号", "评论已关闭"])]
        fm["parallel_items"] = new_items
        new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
        p_g4.write_text(f"---\n{new_yaml}---\n{parts[2].lstrip()}", encoding="utf-8")
        print(f"Cleaned G4TV: {len(items)} -> {len(new_items)} items")

    # 3. 2019-05-18 Siliconera Harmoknight
    p_siliconera = POSTS_DIR / "2019-05-18-interview-siliconera-harmoknight-drill-dozer.md"
    if p_siliconera.exists():
        text = p_siliconera.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        fm = yaml.safe_load(parts[1])
        items = fm["parallel_items"]
        new_items = [it for it in items if not any(k in str(it.get("translation", "")) for k in ["网站规则", "隐私政策", "使用条款", "联盟政策"])]
        fm["parallel_items"] = new_items
        new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
        p_siliconera.write_text(f"---\n{new_yaml}---\n{parts[2].lstrip()}", encoding="utf-8")
        print(f"Cleaned Siliconera: {len(items)} -> {len(new_items)} items")

    # 4. 2019-05-09 VGC Gear Project
    p_vgc = POSTS_DIR / "2019-05-09-interview-vgc-gamefreak-gear-project.md"
    if p_vgc.exists():
        text = p_vgc.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        fm = yaml.safe_load(parts[1])
        items = fm["parallel_items"]
        new_items = [it for it in items if "Mega Man" not in str(it.get("original", ""))]
        fm["parallel_items"] = new_items
        new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
        p_vgc.write_text(f"---\n{new_yaml}---\n{parts[2].lstrip()}", encoding="utf-8")
        print(f"Cleaned VGC: {len(items)} -> {len(new_items)} items")

    # 5. 2013-10-10 XY Chapter 1 Iwata Intro unwrapping
    p_xy = POSTS_DIR / "2013-10-10-interview-iwata-asks-xy-chapter-1-global-simultaneous-release.md"
    if p_xy.exists():
        text = p_xy.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        fm = yaml.safe_load(parts[1])
        items = fm["parallel_items"]
        for it in items:
            if "任天堂の岩田です" in it.get("original", ""):
                it["original"] = "みなさん、こんにちは。任天堂の岩田です。先日、「Pokémon Direct 2013.9.4」を放映しましたが、その収録の際に、プロデューサーの石原さんとディレクターの増田さんは、『ポケットモンスター Ｘ・Ｙ』の新しい魅力について、「Pokémon Direct」でお伝えしたほかにも、たくさんのとても興味深い話をしてくれました。そこで今回は、いつもの「社長が訊く」とちょっと趣向を変えて、「Pokémon Direct」のなかで紹介しきれなかった内容について、ときおりインタビューの映像を交えつつ再編集し、「うごく社長が訊く」としてご紹介することにいたしました。「社長が訊く」も気がつけば、２００回以上続けてきましたが、記事と映像を組み合わせる新しい試みとして、ご覧いただければと思います。よろしくお願いいたします。"
                it["translation"] = "大家好，我是任天堂的岩田。前几天，我们播出了「Pokémon Direct 2013.9.4」，在录制那次节目时，制作人石原先生和总监增田先生，除了在「Pokémon Direct」中介绍的内容之外，还跟我们聊了很多非常有趣的话题。所以这次，我们稍微改变了一下以往「社长问」的形式，将「Pokémon Direct」中未能完全呈现的内容，穿插着访谈影像重新编辑，以「动态社长问」的形式呈现给大家。不知不觉间，「社长问」已经连载了200多回，这次作为文章与影像相结合的新尝试，希望大家能够喜欢。请多关照。"
        fm["parallel_items"] = items
        new_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
        p_xy.write_text(f"---\n{new_yaml}---\n{parts[2].lstrip()}", encoding="utf-8")
        print(f"Cleaned XY Chapter 1 Iwata intro")

if __name__ == "__main__":
    finalize()
