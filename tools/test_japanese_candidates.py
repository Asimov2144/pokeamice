import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

candidates = [
    # 1. 4Gamer 历代长篇
    ("4Gamer BW开发阵专访：增田顺一与杉森建谈新机制与制作姿态", "https://www.4gamer.net/games/108/G010839/20101008077/", ["增田顺一", "杉森建", "第五世代", "黑白", "4Gamer", "JP"]),
    ("4Gamer B2W2开发阵专访：增田顺一与海野隆雄谈系列首个‘2’的挑战", "https://www.4gamer.net/games/150/G015034/20120622080/", ["增田顺一", "海野隆雄", "第五世代", "B2W2", "4Gamer", "JP"]),
    ("4Gamer XY全球同日发售专访：增田顺一谈该变与不该变之物", "https://www.4gamer.net/games/198/G019893/20131011099/", ["增田顺一", "第六世代", "XY", "4Gamer", "JP"]),
    ("4Gamer ORAS总监大森滋专访：不作为‘重制’而是作为‘完全新作’挑战", "https://www.4gamer.net/games/256/G025642/20141120103/", ["大森滋", "第六世代", "ORAS", "4Gamer", "JP"]),
    ("4Gamer 日月大森滋与增田顺一专访：抱定‘改变一切’决心的20周年集大成", "https://www.4gamer.net/games/335/G033525/20161117109/", ["大森滋", "增田顺一", "第七世代", "日月", "4Gamer", "JP"]),
    ("4Gamer LGPE增田顺一专访：消除初学者与老玩家之间的藩篱", "https://www.4gamer.net/games/421/G042131/20181114099/", ["增田顺一", "第八世代", "LGPE", "4Gamer", "JP"]),
    ("4Gamer 剑盾大森滋与增田顺一专访：在Switch上描绘最棒的宝可梦", "https://www.4gamer.net/games/451/G045142/20191114093/", ["大森滋", "增田顺一", "第八世代", "剑盾", "4Gamer", "JP"]),
    ("4Gamer 传说阿鲁宙斯开发专访：动作与RPG的融合及洗翠生态系", "https://www.4gamer.net/games/556/G055610/20220127083/", ["岩尾和昌", "大森滋", "第八世代", "传说阿尔宙斯", "4Gamer", "JP"]),
    ("4Gamer 朱紫大森滋总监专访：开放世界的巨大挑战与多人联机革新", "https://www.4gamer.net/games/619/G061966/20221117088/", ["大森滋", "第九世代", "朱紫", "4Gamer", "JP"]),
    
    # 2. Denfami 巨匠对谈与技术特辑
    ("Denfami 巨匠对谈：田尻智 × 杉森建 × 远藤雅伸谈铁板阵与宝可梦诞生哲学", "https://news.denfaminicogamer.jp/projectbook/xevious", ["田尻智", "杉森建", "远藤雅伸", "极客", "同人志", "第一世代", "Denfami", "JP"]),
    ("Denfami 赛马模拟与GF极客精神：森本茂树 × 田谷正夫 × 一之濑刚", "https://news.denfaminicogamer.jp/projectbook/dabisuta", ["森本茂树", "田谷正夫", "一之濑刚", "梦幻", "数值平衡", "Denfami", "JP"]),
    ("Denfami Pokemon GO现象级爆款幕后：石原恒和 × 川岛优志（前篇）", "https://news.denfaminicogamer.jp/interview/160824", ["石原恒和", "川岛优志", "Pokemon GO", "Denfami", "JP"]),
    ("Denfami GF新人培养与齿轮企划：大森滋 × 尾上将之（前篇）", "https://news.denfaminicogamer.jp/interview/170703", ["大森滋", "尾上将之", "齿轮企划", "日月", "Denfami", "JP"]),
    
    # 3. Famitsu 独家现场与纪念座谈
    ("Fami通 2010 黑白发售特辑：增田顺一与杉森建谈焕然一新的合众世界", "https://www.famitsu.com/news/201009/18033730.html", ["增田顺一", "杉森建", "第五世代", "黑白", "Fami通", "JP"]),
    ("Fami通 2013 XY横滨音乐展会实况：增田顺一与景山将太现场演奏与音频揭秘", "https://www.famitsu.com/news/201311/16043307.html", ["增田顺一", "景山将太", "第六世代", "XY", "音乐", "Fami通", "JP"]),
    ("Fami通 2016 日月发售纪念：大森滋与增田顺一谈阿罗拉自然与生命赞歌", "https://www.famitsu.com/news/201611/18120892.html", ["大森滋", "增田顺一", "第七世代", "日月", "Fami通", "JP"]),
    ("Fami通 2018 究极日月粉丝见面会实况：增田顺一作曲战斗曲与开发秘辛披露", "https://www.famitsu.com/news/201805/15157253.html", ["增田顺一", "大森滋", "岩尾和昌", "第七世代", "究极日月", "Fami通", "JP"]),
    ("Fami通 2019 E3独家直击：增田顺一与大森滋直面关于剑盾宝可梦阵容的关切", "https://www.famitsu.com/news/201906/13177936.html", ["增田顺一", "大森滋", "第八世代", "剑盾", "E3", "Fami通", "JP"]),
    ("Fami通 2024 Pokemon Sleep独家：宇都宫崇人与SELECT BUTTON谈睡眠娱乐化四年攻坚", "https://www.famitsu.com/article/202411/24717", ["宇都宫崇人", "中内之公", "Pokemon Sleep", "生活方式", "Fami通", "JP"]),

    # 4. CGWorld / 技术工程
    ("CGWorld 2017：Creatures谈宝可梦设定画赋予生命力与3D管线未来", "https://cgworld.jp/interview/creatures-201707.html", ["Creatures", "3D建模", "骨骼", "第七世代", "名侦探皮卡丘", "CGWorld", "JP"]),
    ("CGWorld 2017 日月篇：宝可梦3D资产制作与GF-Creatures高度三社协作体制", "https://cgworld.jp/feature/201707-cgw227GG-pokemon.html", ["海野隆雄", "大森滋", "3D建模", "第七世代", "日月", "CGWorld", "JP"]),

    # 5. 音频团队 / 媒体特辑
    ("2083.jp 音效专访：Game Freak 代代传承的宝可梦音乐接力棒", "http://www.2083.jp/contents/201410gamefreak/", ["增田顺一", "一之濑刚", "足立美奈子", "佐藤仁美", "音乐", "第六世代", "JP"]),
    ("Steinberg 官网特写：Game Freak 宝可梦制作现场与 Cubase 音频编配", "https://japan.steinberg.net/jp/artists/steinberg_stories/gamefreak.html", ["景山将太", "DAW", "音乐", "第五世代", "黑白", "JP"]),
    ("ASCII 周刊未删节版：杂志篇幅所未能尽述的宝可梦黑白开发秘辛", "https://weekly.ascii.jp/elem/000/002/602/2602549/?r=1", ["增田顺一", "第五世代", "黑白", "ASCII", "JP"]),
    
    # 6. 日本宝可梦考据玩家与民间专题汇编
    ("「砂の日」初代杂志访谈总集：1996-1998年各大绝版杂志主创发言考据全集", "http://sunanohi.web.fc2.com/pokemon/magazine/game.html#kaigi9", ["田尻智", "杉森建", "增田顺一", "第一世代", "赤绿", "民间考据", "JP"]),
    ("网络黎明期宝可梦站记忆：1996-1999年金银发售前田尻智与主创言论整理", "http://www2u.biglobe.ne.jp/~kakeru/pokemon/pokemon_site.htm", ["田尻智", "增田顺一", "第一世代", "第二世代", "金银", "民间考据", "JP"]),
    ("Funs Project 专访：皮卡丘之母西田敦子与中川翔子角色设计对谈", "https://funs-project.com/poplab/007/", ["西田敦子", "中川翔子", "皮卡丘", "角色设计", "FunsProject", "JP"]),
    ("TOKYO FM《SCHOOL OF LOCK!》：增田顺一与大森滋来校！2小时宝可梦公开课实录", "https://www.tfm.co.jp/lock/staff/index.php?itemid=8978", ["增田顺一", "大森滋", "广播公开课", "第七世代", "日月", "JP"]),
    ("日经商务 Nikkei Business：Pokemon GO 诞生爆发力的日美跨国协作舞台幕后", "https://business.nikkei.com/atcl/report/16/081700063/081700002/", ["宇都宫崇人", "Pokemon GO", "商业模式", "日经", "JP"]),
    ("日经 Style：石原恒和专访——受父亲教导围棋启蒙而迷上游戏的游戏人生", "https://style.nikkei.com/article/DGXKZO67530060R21C20A2KNTP00/", ["石原恒和", "围棋", "个人史", "宝可梦社长", "日经", "JP"]),
    ("NewsPicks 深度特写：唯因‘只有宝可梦’才有趣——倾注一切的两位掌舵人", "https://newspicks.com/news/2833811/body/", ["宇都宫崇人", "河本拓", "第七世代", "宝可梦公司", "NewsPicks", "JP"]),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
}

print(f"Testing {len(candidates)} candidate URLs...")
results = []
for title, url, tags in candidates:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            status = resp.status
            size = len(resp.read())
            print(f"OK [{status}] ({size}b) | {title[:40]} | {url}")
            results.append({"status": "OK", "code": status, "title": title, "url": url, "tags": tags, "size": size})
    except Exception as e:
        print(f"ERR | {title[:40]} | {url} -> {e}")
        results.append({"status": "ERR", "code": str(e), "title": title, "url": url, "tags": tags})

print(f"\nFinished testing. Success count: {len([r for r in results if r['status'] == 'OK'])} / {len(candidates)}")
