import re
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

def fix_kf():
    p = Path('_posts/2021-12-27-interview-gamefreak-recruit-planner-kf.md')
    txt = p.read_text(encoding='utf-8')
    txt = txt.replace(
        "publication: GAME FREAK 採用情報\noriginal_link: https://www.gamefreak.co.jp/recruit/interview-pl-kf/",
        "publication: GAME FREAK 採用情報\noriginal_link: https://www.gamefreak.co.jp/recruit/interview-pl-kf/\nsource:\n  name: GAME FREAK 採用情報\n  url: https://www.gamefreak.co.jp/recruit/interview-pl-kf/"
    )
    p.write_text(txt, encoding='utf-8')
    print("Fixed KF source")

def fix_rm():
    p = Path('_posts/2021-12-27-interview-gamefreak-recruit-planner-rm.md')
    txt = p.read_text(encoding='utf-8')
    txt = txt.replace(
        "publication: GAME FREAK 採用情報\noriginal_link: https://www.gamefreak.co.jp/recruit/interview-pl-rm/",
        "publication: GAME FREAK 採用情報\noriginal_link: https://www.gamefreak.co.jp/recruit/interview-pl-rm/\nsource:\n  name: GAME FREAK 採用情報\n  url: https://www.gamefreak.co.jp/recruit/interview-pl-rm/"
    )
    p.write_text(txt, encoding='utf-8')
    print("Fixed RM source")

def fix_tk():
    p = Path('_posts/2021-12-27-interview-gamefreak-recruit-ta-tk.md')
    txt = p.read_text(encoding='utf-8')
    txt = txt.replace(
        "publication: GAME FREAK 採用情報\noriginal_link: https://www.gamefreak.co.jp/recruit/interview-ta-tk/",
        "publication: GAME FREAK 採用情報\noriginal_link: https://www.gamefreak.co.jp/recruit/interview-ta-tk/\nsource:\n  name: GAME FREAK 採用情報\n  url: https://www.gamefreak.co.jp/recruit/interview-ta-tk/"
    )
    p.write_text(txt, encoding='utf-8')
    print("Fixed TK source")

def fix_famimaga():
    p = Path('_posts/1997-05-23-interview-famimaga-tajiri-pokemon2-secret.md')
    txt = p.read_text(encoding='utf-8')
    # Remove ▲トップへ
    txt = re.sub(r"- original: ▲トップへ\s+translation: ▲返回顶部\s*", "", txt)
    p.write_text(txt, encoding='utf-8')
    print("Fixed famimaga top noise")

def fix_cgworld_sm():
    p = Path('_posts/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline.md')
    txt = p.read_text(encoding='utf-8')
    # Remove the ad block at the end
    txt = re.sub(
        r"- original: 月刊CGWORLD.*?\n  translation: 月刊CGWORLD.*?\n- type: image\s+image: [^\n]+\n  alt: [^\n]+\n  caption: ''\s*",
        "",
        txt,
        flags=re.DOTALL
    )
    # Add interviewee if not present
    if "interviewee:" not in txt:
        txt = txt.replace("source_url: https://cgworld.jp/feature/201707-cgw227GG-pokemon.html", "source_url: https://cgworld.jp/feature/201707-cgw227GG-pokemon.html\ninterviewee: 海野隆雄、大森滋、氏家淳子、畠祐貴、中廣健吾、植松俊介")
    p.write_text(txt, encoding='utf-8')
    print("Fixed cgworld sm pipeline")

def fix_kakeru():
    p = Path('_posts/1999-12-01-interview-web-dawn-pokemon-gold-silver.md')
    txt = p.read_text(encoding='utf-8')
    if "author:" not in txt and "interviewee:" not in txt:
        txt = txt.replace("original_lang: ja", "original_lang: ja\nauthor: かける（Kakeru）\ninterviewee: かける、个人网站宝可梦爱好者")
        p.write_text(txt, encoding='utf-8')
    print("Fixed kakeru gold silver")

def fix_creatures():
    p = Path('_posts/2017-07-15-interview-cgworld-creatures-3d-character-life.md')
    txt = p.read_text(encoding='utf-8')
    if "interviewee:" not in txt:
        txt = txt.replace("original_lang: ja", "original_lang: ja\ninterviewee: Creatures 宝可梦CG工作室开发团队")
        if "interviewee:" not in txt:
            txt = txt.replace("source_url: https://cgworld.jp/interview/creatures-201707.html", "source_url: https://cgworld.jp/interview/creatures-201707.html\ninterviewee: Creatures 宝可梦CG工作室开发团队")
        p.write_text(txt, encoding='utf-8')
    print("Fixed creatures 3d")

def fix_gamer_press():
    p = Path('_posts/2018-05-30-interview-gamer-pokemon-press-conference-2018.md')
    txt = p.read_text(encoding='utf-8')
    if "interviewee:" not in txt:
        txt = txt.replace("original_lang: ja", "original_lang: ja\ninterviewee: 石原恒和、増田順一、高橋伸也、野村達雄")
        p.write_text(txt, encoding='utf-8')
    print("Fixed gamer press 2018")

def fix_legal():
    p = Path('_posts/2018-09-12-interview-businesslawyers-pokemon-legal.md')
    txt = p.read_text(encoding='utf-8')
    if "interviewee:" not in txt:
        txt = txt.replace("original_lang: ja", "original_lang: ja\ninterviewee: 福嶋ゆかり、鹿瀬島英介")
        p.write_text(txt, encoding='utf-8')
    print("Fixed businesslawyers legal")

def fix_canuch():
    p = Path('_posts/2020-07-01-interview-canuch-gamefreak-office-architecture.md')
    txt = p.read_text(encoding='utf-8')
    if "interviewee:" not in txt:
        txt = txt.replace("original_lang: ja", "original_lang: ja\ninterviewee: CANUCH 设计团队、GAME FREAK 办公室环境委员会")
        p.write_text(txt, encoding='utf-8')
    print("Fixed canuch office")

fix_kf()
fix_rm()
fix_tk()
fix_famimaga()
fix_cgworld_sm()
fix_kakeru()
fix_creatures()
fix_gamer_press()
fix_legal()
fix_canuch()
print("All quality fixes applied successfully!")
