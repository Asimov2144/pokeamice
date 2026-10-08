import re, sys, json, yaml, collections
from pathlib import Path
from common import POSTS, read_post, write_post, split_fm, load_fm, L
from fixer import (yq, plan_items, plan_top, apply_edits, verify, top_block, indent_of)

sys.stdout.reconfigure(encoding="utf-8")
DRY = "--dry" in sys.argv
ONLY = [a for a in sys.argv[1:] if not a.startswith("--")]

# ---------------- summaries (new text written from each post's body) ----------------
SUMMARY = {
    "2026-06-24-[整理]-宝扭蛋怎么找.md": "作者偶然发现一个收录新扭蛋的网站，基本涵盖近期各种新扭蛋，连 PCO 的 30 周年挂件也收录其中，附上了网站链接。",
    "2022-05-31-Updates.md": "Poke Amice 更新日志（2022 年 5 月至 6 月）：石原访谈回顾、全世代 OST 小册子扫描、设计者页面翻译与菜单调整、PTCG 访谈投稿等。",
    "2022-10-10-[采访]-宝可梦传说阿尔宙斯-日本游戏大赏-岩尾获奖感言.md": "岩尾和昌在「日本游戏大赏 2022」优秀奖获奖后的完整感言：感谢投票与玩家，说明开发初衷是让新玩家也能进入系列，并在变革中保留系列的根本乐趣。",
    "2024-12-10-[站点]-建站纪事-Building-Records.md": "记录 Poke Amice 的建站过程与鸣谢：站点主题已开源，并介绍随机背景图、站点图标、腾讯云 COS 图床与开发工具等。",
    "2024-12-24-[技能机]-卡图下载-查询时间-Download & Inqury.md": "宝活小妙招：如何推测 151 卡图的静态链接，用 Python 脚本批量下载，并用浏览器查询服务器存档时间。",
    "2025-01-01-[整理]-GameFreak-Development-TimeLine.md": "按时间整理 Game Freak 近年的开发事件：从 2008 年迁入新办公室起，依次列出第五世代以来各作的发售与立项节点。",
    "2016-05-19-gamefreak-lineblog-3556962.md": "GAME FREAK 员工在海边偶遇海鸥，拍下海鸥走路的视频分享，并发现视频中途有谷歌街景车经过。",
    "2016-12-24-gamefreak-lineblog-9250993.md": "GAME FREAK 与宝可梦公司、Kiki 送上圣诞祝福，分享宝可梦 GO 玩家为进化雷丘而捕捉皮卡丘的近况，并问《太阳·月亮》玩家是否记得一面橙色的墙。",
    "2007-11-01-gamefreak-director-111.md": "部长专栏第 111 回：专栏将推出英文版，由有海外生活经历的游戏设计师 Hiro Nakamura 负责翻译；英文版更新会慢于日文版，过去的专栏也会陆续翻译。",
    "2008-02-27-gamefreak-director-124.md": "2 月 27 日是《宝可梦 红·绿》在日本发售的纪念日，部长专栏回顾当年的开发心情，感谢全世界的支持，并表示宝可梦今后也会继续进化。",
}

# ---------------- tags ----------------
TAG_EXPLICIT = {
    "宝可梦红绿": "宝可梦 红·绿", "宝可梦 红·绿": "宝可梦 红·绿",
    "赤·绿": "宝可梦 红·绿", "赤绿": "宝可梦 红·绿",
    "宝可梦 金·银": "宝可梦 金·银", "宝可梦金银": "宝可梦 金·银", "金·银": "宝可梦 金·银", "金银": "宝可梦 金·银",
    "红宝石·蓝宝石": "宝可梦 红宝石·蓝宝石", "红宝石蓝宝石": "宝可梦 红宝石·蓝宝石",
    "钻石·珍珠": "宝可梦 钻石·珍珠", "钻石珍珠": "宝可梦 钻石·珍珠",
    "黑·白": "宝可梦 黑·白", "黑白": "宝可梦 黑·白", "宝可梦黑白": "宝可梦 黑·白",
    "宝可梦 黑2·白2": "宝可梦 黑2·白2", "宝可梦黑2白2": "宝可梦 黑2·白2",
    "宝可梦 X·Y": "宝可梦 X·Y", "宝可梦XY": "宝可梦 X·Y", "宝可梦 XY": "宝可梦 X·Y", "XY": "宝可梦 X·Y", "X·Y": "宝可梦 X·Y",
    "宝可梦 ORAS": "宝可梦 ORAS", "宝可梦ORAS": "宝可梦 ORAS",
    "Pokémon GO": "Pokémon GO", "PokémonGO": "Pokémon GO",
    "宝可梦 太阳·月亮": "宝可梦 太阳·月亮", "宝可梦 太阳／月亮": "宝可梦 太阳·月亮",
    "太阳·月亮": "宝可梦 太阳·月亮", "太阳月亮": "宝可梦 太阳·月亮", "太阳／月亮": "宝可梦 太阳·月亮",
    "宝可梦 剑·盾": "宝可梦 剑·盾", "宝可梦剑盾": "宝可梦 剑·盾", "剑盾": "宝可梦 剑·盾", "剑／盾": "宝可梦 剑·盾",
    "宝可梦 朱·紫": "宝可梦 朱·紫", "宝可梦朱紫": "宝可梦 朱·紫",
    "究极之日·究极之月": "宝可梦 究极之日·究极之月", "究极之日究极之月": "宝可梦 究极之日·究极之月",
    "Nintendo Dream": "Nintendo DREAM",
    "Lets Go": "Let's Go",
    "pokemon": "Pokemon",
}
JP_TAG = {
    "ポケモン": "宝可梦", "ポケットモンスター": "宝可梦", "ポケモンセンター": "宝可梦中心",
    "株式会社ポケモン": "株式会社宝可梦", "ポケモンGO": "Pokémon GO", "ポケモンGo": "Pokémon GO",
    "ポケモンGOスタジアム": "Pokémon GO 竞技场",
    "週刊ファミ通": "Fami通", "ファミ通": "Fami通", "ファミ通アワード2016": "Fami通 Awards 2016",
    "電ファミニコゲーマー": "电玩迷电玩", "ファミマガ64": "FamiMaga 64", "ファミマガ": "FamiMaga",
    "オトナファミ": "大人Fami", "週刊アスキー": "周刊ASCII", "ゲーセン天国": "游戏中心天国",
    "ピカチュウ": "皮卡丘", "アナハイム": "阿纳海姆", "ものづくり": "制作理念", "イベント": "活动",
    "食べもの飲みもの": "饮食", "サン": "宝可梦 太阳", "ムーン": "宝可梦 月亮",
    "サンムーン": "宝可梦 太阳·月亮", "ポケモンサンムーン": "宝可梦 太阳·月亮",
    "ポケットモンスターサンムーン": "宝可梦 太阳·月亮", "ポケットモンスターサン": "宝可梦 太阳",
    "ポケットモンスタームーン": "宝可梦 月亮",
    "ゲーム": "游戏", "ポケモン世界大会": "宝可梦世界大赛", "ポケモン2": "宝可梦2", "スイス": "瑞士",
    "株式会社ゲームフリーク": "Game Freak", "ゲームフリーク": "Game Freak",
    "ダ・ヴィンチ": "Da Vinci", "お知らせ": "公告", "サントラ": "原声带", "サウンドトラック": "原声带",
    "サイン会": "签名会", "シアトル": "西雅图", "チーズ": "奶酪", "アンノーン": "未知图腾",
    "よこはま": "横滨", "ポケポケ": "宝可梦 Pocket", "ポケモン・ストーリー": "宝可梦故事",
    "コロコロコミック": "CoroCoro Comic", "泣かせどころ": "催泪场面", "ソリティ馬": "纸牌赛马",
    "ニコニコ": "NicoNico", "カードゲーム": "卡牌游戏", "遊び": "玩乐", "ポッ拳": "宝可拳", "ラジオ": "广播",
    "もみじ": "红叶", "ポータル": "传送门", "キャロットタワー": "Carrot Tower",
    "ポケモンファン": "宝可梦粉丝", "ポルト": "波尔图", "コミコン": "Comic-Con", "ポルトガル": "葡萄牙",
    "ねこ": "猫", "あけましておめでとう": "新年快乐", "ゼニガメ": "杰尼龟", "ヒトカゲ": "小火龙",
    "フシギダネ": "妙蛙种子", "シンガポール": "新加坡", "ラン二ング": "跑步", "走る": "跑步",
    "金銀ポケモン": "宝可梦 金·银", "ブログ": "博客", "打ち上げ": "庆功宴", "スタッフ": "工作人员",
    "ママ": "妈妈", "お祝い": "庆祝", "コイキング": "鲤鱼王", "オイスター": "牡蛎", "ホタテ": "扇贝",
    "シーフード": "海鲜", "カニ": "螃蟹", "インフィオラータ": "Infiorata", "スターバックス": "星巴克",
    "スタバ": "星巴克", "おうじゃのしるし": "王者之证", "ヤドキング": "呆河王", "やどん": "呆呆兽",
    "スマホ": "智能手机", "スマホケース": "手机壳", "モントルー": "蒙特勒", "ディナー": "晚餐",
    "グリュイエール": "格吕耶尔", "ロケット団": "火箭队", "ニャース": "喵喵", "フリーザー": "急冻鸟",
    "ルギア": "洛奇亚", "ジラーチ": "基拉祈", "七夕祭り": "七夕祭", "バリヤード": "魔尼尼",
    "はまれぽ": "Hamarepo", "パレード": "游行", "レイド": "团体战", "横浜スタジアム": "横滨体育场",
    "ミュウツー": "超梦", "ディズニー": "迪士尼", "ガルーラ": "袋兽", "ブロック": "积木",
    "メキシコ料理": "墨西哥料理", "ほぼ日": "Hobonichi", "ガチャ": "扭蛋",
    # no established Chinese form: kept as the source writes them
    "ぽこ あ ポケモン": "ぽこ あ ポケモン", "福嶋ゆかり": "福嶋ゆかり", "大奈路まりな": "大奈路まりな",
}
TAG_DELETE = {"sun", "moon", "party", "christmas", "madrid", "airport", "art", "architecture", "tattoo", "translation"}
DOMAIN = re.compile(r"\.(com|jp|net|org|cn|tv)$|https?:", re.I)
ADD_TAGS = {
    "1997-05-23-interview-famimaga-tajiri-pokemon2-secret.md": ["访谈", "田尻智", "杉森建", "增田顺一", "宝可梦 红·绿", "FamiMaga"],
    "1997-10-16-interview-gamefreak-official-red-green-staff.md": ["访谈", "田尻智", "杉森建", "增田顺一", "宝可梦 红·绿", "Game Freak"],
    "2009-09-18-interview-dengeki-hgss-shigeki-morimoto.md": ["访谈", "森本茂树", "宝可梦 心金·魂银", "电击"],
    "2010-03-31-interview-pokemon-com-hgss-masuda-morimoto.md": ["访谈", "增田顺一", "森本茂树", "大森滋", "宝可梦 心金·魂银"],
    "2013-10-24-interview-onm-xy-sugimori.md": ["访谈", "杉森建", "宝可梦 X·Y", "任天堂官方杂志"],
    "2014-08-22-interview-niconico-gamefreak-origins-masuda.md": ["访谈", "增田顺一", "Game Freak", "NicoNico"],
    "2014-11-01-interview-topofarmer-ideame-masuda-ohmori.md": ["访谈", "增田顺一", "大森滋", "Game Freak"],
    "2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md": ["访谈", "田尻智", "杉森建", "远藤雅伸", "电玩迷电玩"],
    "2016-08-25-interview-nikkei-utsunomiya-pokemon-go.md": ["访谈", "宇都宫崇人", "Pokémon GO", "日经商务"],
    "2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline.md": ["访谈", "Game Freak", "Creatures", "宝可梦 太阳·月亮", "CGWORLD"],
    "2017-07-15-interview-cgworld-creatures-3d-character-life.md": ["访谈", "Creatures", "CGWORLD", "氏家淳子", "中广健吾", "畠祐贵"],
    "2017-11-09-interview-pokemon-com-usum-ohmori-iwao.md": ["访谈", "大森滋", "岩尾和昌", "宝可梦 究极之日·究极之月"],
    "2018-02-23-interview-newspicks-pokemon-utsunomiya-kawamoto.md": ["访谈", "宇都宫崇人", "河本拓", "石原恒和", "NewsPicks"],
    "2018-03-30-interview-famitsu-detective-pikachu-jinnai-miyashita.md": ["访谈", "阵内弘之", "宫下尚生", "名侦探皮卡丘", "Fami通"],
    "2018-05-30-interview-gamer-pokemon-press-conference-2018.md": ["访谈", "石原恒和", "增田顺一", "大森滋", "Let's Go"],
    "2018-09-12-interview-businesslawyers-pokemon-legal.md": ["访谈", "富田裕介", "株式会社宝可梦", "法务"],
    "2018-10-26-interview-eurogamer-masuda-nabana-lets-go.md": ["访谈", "增田顺一", "菜花健作", "Let's Go"],
    "2019-10-25-interview-famitsu-sword-shield-masuda-ohmori.md": ["访谈", "增田顺一", "大森滋", "宝可梦 剑·盾"],
    "2020-07-01-interview-canuch-gamefreak-office-architecture.md": ["访谈", "Game Freak", "建筑", "CANUCH"],
    "2020-12-25-interview-corocoro-coco-okazaki-taiiku.md": ["访谈", "冈崎体育", "剧场版 宝可梦 可可", "CoroCoro Comic"],
}

def norm(s):
    return re.sub(r"[\s·・•/／\-—_.,，、:：()（）「」『』“”\"'《》]+", "", str(s).lower())

# corpus-wide raw tag counts, for the generic cluster canonical form
def _tags_of(d):
    t = d.get("tags")
    if isinstance(t, str): t = [t]
    return [str(x).strip() for x in (t or []) if str(x).strip()]

RAW = collections.Counter()
for _p in POSTS.glob("*.md"):
    _fm, _b, _ = split_fm(read_post(_p)[0])
    _d = load_fm(_fm) if _fm else None
    if _d: RAW.update(set(_tags_of(_d)))
_clusters = collections.defaultdict(set)
for _t in RAW: _clusters[norm(_t)].add(_t)
GENERIC = {}
for _k, _forms in _clusters.items():
    if len(_forms) < 2 or not _k: continue
    if any(f in TAG_EXPLICIT or f in JP_TAG for f in _forms): continue
    GENERIC[_k] = max(_forms, key=lambda f: RAW[f])

def canon(t):
    if t in TAG_DELETE or DOMAIN.search(t): return None
    if t in TAG_EXPLICIT: return TAG_EXPLICIT[t]
    if t in JP_TAG: return JP_TAG[t]
    return GENERIC.get(norm(t), t)

def tags_fn(old, name):
    if old is None or old == []:
        return ADD_TAGS.get(name)
    if isinstance(old, str): old = [old]
    new = []
    for t in old:
        c = canon(str(t).strip())
        if c and c not in new: new.append(c)
    if new == [str(x) for x in old]:
        return None
    return new

# ---------------- phase 0: five posts whose YAML fails on unquoted "ISBN: …" / "JAN: …" ----------------
def phase0_quote(text_lf, name):
    fm, body, head = split_fm(text_lf)
    lines = fm.split("\n")
    changed = False
    for j, l in enumerate(lines):
        m = re.match(r"^(\s*-?\s*)(original|translation):\s(.*)$", l)
        if m and ": " in m.group(3) and not m.group(3)[:1] in "'\"":
            lines[j] = m.group(1) + m.group(2) + ": " + yq(m.group(3))
            changed = True
    if not changed:
        return text_lf, False
    new_fm = "\n".join(lines)
    d = yaml.load(new_fm, Loader=L)  # must now parse
    return "---\n" + new_fm + "\n---\n" + body, True

# ---------------- driver ----------------
stats = collections.Counter(); failures = []; samples = []
for p in sorted(POSTS.glob("*.md")):
    name = p.name
    if ONLY and name not in ONLY: continue
    text, eol = read_post(p)
    bom = "﻿" if text.startswith("﻿") else ""
    if bom: text = text[1:]
    if split_fm(text)[0] is None: continue
    try:
        text2, did0 = phase0_quote(text, name)
        if did0: stats["yaml_quoted"] += 1
        fm, body, head = split_fm(text2)
        d0 = load_fm(fm)
        if d0 is None:
            failures.append((name, "yaml still broken")); continue
        lines = fm.split("\n")
        edits_i, exp_items, notes_log = plan_items(lines, d0)
        edits_t, exp_top = plan_top(lines, d0, name, SUMMARY, tags_fn)
        if not edits_i and not edits_t and not did0 and not re.search(r"^#{1,6}[^\s#]", body, re.M):
            continue
        new_lines = apply_edits(list(lines), edits_i + edits_t)
        new_fm = "\n".join(new_lines)
        verify(new_fm, d0, exp_items, exp_top)
        body_new = re.sub(r"^(#{1,6})(?=[^\s#])", r"\1 ", body, flags=re.M)
        out = bom + "---\n" + new_fm + "\n---\n" + body_new
        stats["files_changed"] += 1
        stats["notes_extracted"] += len(notes_log)
        stats["items_newline_fixed"] += sum(1 for i, v in exp_items.items() if "translation" in v and "\n\n" in v["translation"] and "note" not in v)
        stats["tags_changed"] += 1 if "tags" in exp_top else 0
        stats["summary_changed"] += 1 if "summary" in exp_top else 0
        stats["heading_fixed"] += 1 if body_new != body else 0
        for i, tr, t2, note in notes_log[:2]:
            samples.append((name[:40], i, tr[-70:], t2[-50:], note[:90]))
        if not DRY:
            write_post(p, out, eol)
    except Exception as e:
        failures.append((name, str(e)[:160]))

print("STATS", dict(stats))
print("FAILURES", len(failures))
for f in failures[:30]: print("  ", f)
for s in samples[:40]: print("SAMPLE", s)
print("GENERIC clusters:", GENERIC)
