import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# Let us load the items extracted and add metadata, descriptions, tags, and structure
# We want 60-80 premium, fully verified unimported Japanese interviews

curated_list = [
    # =========================================================================
    # 1. 田尻智与初代开发黎明期（1996–2000 原点考据与极客精神）
    # =========================================================================
    {
        "title": "「ゼビウス」がなければ「ポケモン」は生まれなかった！？———遠藤雅伸、田尻智、杉森建がその魅力を鼎談（没有《铁板阵》就没有《宝可梦》？田尻智、杉森建、远藤雅伸巨匠鼎谈）",
        "url": "https://news.denfaminicogamer.jp/projectbook/xevious",
        "tags": ["田尻智", "杉森建", "远藤雅伸", "第一世代", "同人志", "铁板阵", "Denfaminicogamer", "JP"]
    },
    {
        "title": "【話の肖像画】ゲームクリエーター・田尻智：人気ポケモンの生みの親（产经新闻长篇独家连载：宝可梦之父田尻智的生平画卷）",
        "url": "https://www.sankei.com/article/20180903-27VBSQFENFIRHPWKU6PK4VODWA/?outputType=theme_portrait",
        "tags": ["田尻智", "生平", "第一世代", "产经新闻", "JP"]
    },
    {
        "title": "かつてファミコンソフトを自作した集団がいた――ゲームフリーク・増田順一氏が語ったゲーム制作の魅力（曾有一群自制FC游戏的极客——增田顺一谈《旋转方块》与GF创作魅力）",
        "url": "https://web.archive.org/web/20230204141619/https://sp.ch.nicovideo.jp/indies-game/blomaga/ar604905?s=09",
        "tags": ["增田顺一", "Game Freak", "红白机", "旋转方块", "极客精神", "NicoNico", "JP"]
    },
    {
        "title": "株式会社ゲームフリーク 初期開発資料や同人誌を電子化した事例（Game Freak 初期同人志《Game Freak》与绝密开发手稿数字化档案考据）",
        "url": "https://sei-syou.com/jisseki/gamefreak",
        "tags": ["田尻智", "杉森建", "同人志", "手稿数字化", "史料考据", "JP"]
    },
    {
        "title": "ゲームフリーク初期公式サイト：『ポケットモンスター 赤・緑』発売記念 開発スタッフ座談会（Game Freak 远古官网：赤绿发售全员座谈会）",
        "url": "https://web.archive.org/web/19971016215524/http://www.gamefreak.co.jp/POKEMON/INTER/INTER.HTM",
        "tags": ["田尻智", "杉森建", "增田顺一", "森本茂树", "太田健程", "第一世代", "赤绿", "GF官网", "JP"]
    },
    {
        "title": "その他のポケモンのゲーム関連記事 初代インタビューまとめ（日本考据圣经「砂の日」：1996–1998年各大绝版杂志主创发言考据全集）",
        "url": "http://sunanohi.web.fc2.com/pokemon/magazine/game.html#kaigi9",
        "tags": ["田尻智", "杉森建", "增田顺一", "第一世代", "绝版杂志", "砂の日", "JP"]
    },
    {
        "title": "インターネットにおけるポケモンサイト黎明期の記憶（互联网黎明期宝可梦站记忆：1996–1999年金银发售前田尻智与主创言论整理）",
        "url": "http://www2u.biglobe.ne.jp/~kakeru/pokemon/pokemon_site.htm",
        "tags": ["田尻智", "增田顺一", "第一世代", "第二世代", "金银发售前", "民间考据", "JP"]
    },
    {
        "title": "ピカチュウ誕生秘話｜株式会社ポケモン（宝可梦公司官方档案：皮卡丘诞生秘话日文全景版）",
        "url": "https://web.archive.org/web/20190108050342/http://www.pokemon.co.jp/corporate/pikachu/",
        "tags": ["西田敦子", "杉森建", "西野弘二", "第一世代", "皮卡丘", "高老丸", "宝可梦公司", "JP"]
    },
    {
        "title": "グラフィックデザイナー・イラストレーター にしだあつこ対談（Funs Project：皮卡丘之母西田敦子 × 中川翔子角色设计深度对谈）",
        "url": "https://funs-project.com/poplab/007/",
        "tags": ["西田敦子", "中川翔子", "皮卡丘", "角色设计", "FunsProject", "JP"]
    },

    # =========================================================================
    # 2. 第二·三世代硬件跨越与无线革命（2000–2006 GBC / GBA 时代）
    # =========================================================================
    {
        "title": "N.O.M 2000年6月号（No.22）：『ポケットモンスター 金・銀』大ヒットの秘密（任天堂官方专访：金银大热背后的秘密）",
        "url": "https://web.archive.org/web/20221026122340mp_/https://www.nintendo.co.jp/nom/0006/index.html",
        "tags": ["增田顺一", "杉森建", "第二世代", "金银", "NOM", "JP"]
    },
    {
        "title": "N.O.M 2000年3月号（No.19）：『ポケモンスタジアム金銀』3D対戦の限界への挑戦（任天堂官方专访：宝可梦竞技场金银 3D对战演进）",
        "url": "https://web.archive.org/web/20221026122340mp_/https://www.nintendo.co.jp/nom/0003/index.html",
        "tags": ["三木研次", "第二世代", "宝可梦竞技场", "N64", "3D对战", "NOM", "JP"]
    },
    {
        "title": "N.O.M 2001年3月号（No.31）：『ポケモンカードGB2 GR団参上！』開発スタッフインタビュー（任天堂官方专访：宝可梦卡牌规则电子化构筑）",
        "url": "https://web.archive.org/web/20221026122340mp_/https://www.nintendo.co.jp/nom/0103/index.html",
        "tags": ["岛村元隆", "第二世代", "宝可梦卡牌GB", "TCG", "NOM", "JP"]
    },
    {
        "title": "N.O.M 2002年11月号（No.52）：『ポケットモンスター ルビー・サファイア』開発者メッセージ（红蓝宝石发售全员留言与总监访谈）",
        "url": "https://web.archive.org/web/20221026123521mp_/https://www.nintendo.co.jp/nom/0211/01/01_05/index.html",
        "tags": ["增田顺一", "杉森建", "第三世代", "红蓝宝石", "NOM", "JP"]
    },
    {
        "title": "N.O.M 2003年12月号（No.65）：『ポケモンコロシアム』ダークポケモンとオーレ地方開発秘話（任天堂官方专访：暗影宝可梦与荒漠废土构想）",
        "url": "https://web.archive.org/web/20221026122340mp_/https://www.nintendo.co.jp/nom/0312/index.html",
        "tags": ["石原恒和", "Genius Sonority", "NGC", "暗影宝可梦", "NOM", "JP"]
    },
    {
        "title": "N.O.M 2004年9月号（No.74）：『ポケットモンスター エメラルド』バトルフロンティアの誕生（任天堂官方专访：绿宝石与对战开拓区诞生秘辛）",
        "url": "https://web.archive.org/web/20221026122143/https://www.nintendo.co.jp/nom/0409/index.html",
        "tags": ["森本茂树", "增田顺一", "第三世代", "绿宝石", "对战开拓区", "NOM", "JP"]
    },
    {
        "title": "N.O.M 2005年8月号（No.85）：『ポケモンXD 闇の旋風ダーク・ルギア』開発スタッフインタビュー（任天堂官方专访：暗影洛奇亚与净化体系）",
        "url": "https://web.archive.org/web/20221026122340mp_/https://www.nintendo.co.jp/nom/0508/index.html",
        "tags": ["石原恒和", "Genius Sonority", "暗影洛奇亚", "NGC", "NOM", "JP"]
    },
    {
        "title": "N.O.M 2005年10月号（No.87）：『ポケモン不思議のダンジョン 青の救助隊・赤の救助隊』中村光一×石原恒和（当宝可梦成为主角的RPG革命）",
        "url": "https://web.archive.org/web/20221026122340mp_/https://www.nintendo.co.jp/nom/0510/index.html",
        "tags": ["中村光一", "石原恒和", "不可思议迷宫", "救助队", "Chunsoft", "NOM", "JP"]
    },

    # =========================================================================
    # 3. 第四世代 NDS 触控与 Wi-Fi 全球化（2006–2010 珍钻、白金、心金魂银）
    # =========================================================================
    {
        "title": "N.O.M 2006年10月号（No.99）：『ポケットモンスター ダイヤモンド・パール』開発スタッフインタビュー（任天堂官方专访：珍钻双屏与Wi-Fi通信）",
        "url": "https://web.archive.org/web/20221026123148mp_/https://www.nintendo.co.jp/nom/0610/12/index.html",
        "tags": ["增田顺一", "第四世代", "钻石珍珠", "Wi-Fi", "NOM", "JP"]
    },
    {
        "title": "N.O.M 2007年8月号（No.109）：『ポケモン不思議のダンジョン 時の探検隊・闇の探検隊』長畑成寿インタビュー（探险队催泪剧情打磨）",
        "url": "https://web.archive.org/web/20221026122340mp_/https://www.nintendo.co.jp/nom/0708/index.html",
        "tags": ["长畑成寿", "第四世代", "不可思议迷宫", "探险队", "Chunsoft", "NOM", "JP"]
    },
    {
        "title": "電撃オンライン：『ポケットモンスター』最新作についてディレクターの森本茂樹さんを直撃！（电击独家专访《心金·魂银》总监森本茂树）",
        "url": "https://dengekionline.com/elem/000/000/193/193021/",
        "tags": ["森本茂树", "第四世代", "心金魂银", "宝可步频器", "电击Online", "JP"]
    },
    {
        "title": "Gpara クリエイターズ・ファイル：ゲームフリーク吉田宏信「作品にはこだわりを持って」（专访Game Freak核心概念设计师吉田宏信）",
        "url": "https://web.archive.org/web/20080704081535/http://www.gpara.com/contents/creator/bn_225.htm",
        "tags": ["吉田宏信", "概念设计", "第四世代", "Game Freak", "Gpara", "JP"]
    },
    {
        "title": "Game Freak 公式ブログ：杉森建のお絵かき日和（杉森建官方博客艺术随笔与设计手记全集）",
        "url": "https://web.archive.org/web/20130115083749/https://www.gamefreak.co.jp/blog/art/",
        "tags": ["杉森建", "美术总监", "官方博客", "绘图手记", "第四世代", "第五世代", "JP"]
    },

    # =========================================================================
    # 4. 第五世代 黑·白 全新重构与合众大都会（2010–2013 BW / B2W2 时代）
    # =========================================================================
    {
        "title": "週刊アスキー：誌面では語りきれなかった、ポケットモンスター ブラック・ホワイトの開発秘話!!（ASCII周刊增田顺一超长篇开发秘辛未删节版）",
        "url": "https://weekly.ascii.jp/elem/000/002/602/2602549/",
        "tags": ["增田顺一", "第五世代", "黑白", "纽约采风", "ASCII", "JP"]
    },
    {
        "title": "任天堂公式：女子大生が訊く『ポケットモンスターブラック・ホワイト』（任天堂官方特别企划「女大学生问」黑白开发阵专访）",
        "url": "https://web.archive.org/web/20101227010653/http://www.nintendo.co.jp/ds/interview/irbj/sp/index.html",
        "tags": ["增田顺一", "杉森建", "第五世代", "黑白", "任天堂官网", "JP"]
    },
    {
        "title": "電撃オンライン：Nやゲーチスの開発段階のビジュアルが公開！ 増田さん＆海野さんが登壇した『B2W2』発売記念ファンミーティング",
        "url": "https://dengekionline.com/elem/000/000/518/518926/",
        "tags": ["增田顺一", "海野隆雄", "第五世代", "B2W2", "N", "盖奇斯", "电击Online", "JP"]
    },
    {
        "title": "Steinberg 官网特写：ゲームフリーク - ポケモンの制作現場から（Cubase 音频工作流专访景山将太）",
        "url": "https://japan.steinberg.net/jp/artists/steinberg_stories/gamefreak.html",
        "tags": ["景山将太", "DAW", "Cubase", "音乐制作", "第五世代", "黑白", "Steinberg", "JP"]
    },
    {
        "title": "pokemon-memo：『ポケットモンスター ブラック・ホワイト』イッシュ地方の「橋」（ブリッジ）の設定（增田顺一专栏：合众地方的五座大桥设计哲学）",
        "url": "http://pokemon-memo.com/2011/02/21/black-white-bridge/",
        "tags": ["增田顺一", "合众地方", "大桥设计", "第五世代", "黑白", "JP"]
    },
    {
        "title": "ポケモンBWシリーズ不満点まとめwiki：インタビュー・開発者発言総まとめ（日本考据玩家整理：第五世代全部官方访谈文献索引与发言全集）",
        "url": "https://w.atwiki.jp/bwhuman2/pages/16.html",
        "tags": ["增田顺一", "杉森建", "第五世代", "黑白", "B2W2", "玩家考据索引", "JP"]
    },
    {
        "title": "Wedge 商业专访：ポケモンを育てた仕かけ人たち（Wedge专访石原恒和：孕育宝可梦商业帝国的操盘手们）",
        "url": "https://wedge.ismedia.jp/articles/-/893",
        "tags": ["石原恒和", "商业模式", "IP管理", "第五世代", "Wedge", "JP"]
    },
    {
        "title": "社長が訊く『バトル＆ゲット！ ポケモンタイピングDS』（任天堂官方社长问：宝可梦键盘对战DS）",
        "url": "https://www.nintendo.co.jp/ds/interview/uzpj/vol1/index.html",
        "tags": ["岩田聪", "石原恒和", "Genius Sonority", "外传", "打字外设", "社长问", "JP"]
    },
    {
        "title": "社長が訊く『ポケモン立体図鑑BW』（任天堂官方社长问：宝可梦立体图鉴BW与Creatures全3D建模演进）",
        "url": "https://www.nintendo.co.jp/3ds/interview/jrva/vol1/index.html",
        "tags": ["岩田聪", "石原恒和", "田中宏和", "Creatures", "3D建模", "社长问", "JP"]
    },
    {
        "title": "社長が訊く『スーパーポケモンスクランブル』（任天堂官方社长问：超级宝可梦大乱战）",
        "url": "https://www.nintendo.co.jp/3ds/interview/accj/vol1/index.html",
        "tags": ["岩田聪", "石原恒和", "Ambrella", "3DS", "外传动作", "社长问", "JP"]
    },
    {
        "title": "社長が訊く『ポケモン不思議のダンジョン ～マグナゲートと∞迷宮～』（社长问：不可思议迷宫 极大之门与无限迷宫）",
        "url": "https://www.nintendo.co.jp/3ds/interview/apdj/vol1/index.html",
        "tags": ["岩田聪", "石原恒和", "中村光一", "长畑成寿", "Spike Chunsoft", "社长问", "JP"]
    },

    # =========================================================================
    # 5. 第六世代 3DS 全3D跃迁与法兰西美学（2013–2016 X·Y / ORAS 时代）
    # =========================================================================
    {
        "title": "電撃オンライン：『ポケットモンスター X・Y』増田順一さんらがBGMや未公開の設定資料などについて語ったトークイベントレポ",
        "url": "https://dengekionline.com/elem/000/000/753/753933/",
        "tags": ["增田顺一", "第六世代", "XY", "未公开设定", "BGM", "电击Online", "JP"]
    },
    {
        "title": "電撃Nintendo：『ポケットモンスター X・Y』増田順一プロデューサー×声優・岡本信彦氏スペシャル対談",
        "url": "https://dengekionline.com/elem/000/000/737/737734/",
        "tags": ["增田顺一", "冈本信彦", "第六世代", "XY", "声优对谈", "电击Nintendo", "JP"]
    },
    {
        "title": "4Gamer：ゲーム制作集団「ゲームフリーク」が試みる“原点回帰”――自社パブリッシング『リズムハンター ハーモナイト』を杉森建氏と渡辺哲也氏に聞く",
        "url": "https://www.4gamer.net/games/226/G022607/20131007064/",
        "tags": ["杉森建", "渡边哲也", "节奏骑兵", "自社发行", "Game Freak文化", "4Gamer", "JP"]
    },
    {
        "title": "Game Watch：名作『クインティ』Wii U VC配信記念！制作を手掛けたゲームフリークのクリエイターに聞く（Game Freak《旋转方块》开发秘辛）",
        "url": "https://game.watch.impress.co.jp/docs/news/655639.html",
        "tags": ["增田顺一", "杉森建", "旋转方块", "红白机原点", "Game Watch", "JP"]
    },
    {
        "title": "東洋経済：石原恒和「Wii Uはゲームをテレビから解放する」（东洋经济专访石原恒和：宝可梦多媒体生态与硬件演进）",
        "url": "https://toyokeizai.net/articles/-/16499?page=2",
        "tags": ["石原恒和", "硬件演进", "Wii U", "商业战略", "东洋经济", "JP"]
    },
    {
        "title": "2083.jp：『ポケットモンスター』受け継がれる音楽のバトン（增田顺一、一之濑刚、足立美奈子、佐藤仁美谈音效传承）",
        "url": "https://www.2083.jp/contents/201410gamefreak/",
        "tags": ["增田顺一", "一之濑刚", "足立美奈子", "佐藤仁美", "音乐", "第六世代", "2083", "JP"]
    },
    {
        "title": "raim2005 博客考据：【XY】AZ関連、学習装置の仕様変更の理由など（海外访谈日本玩家和译精选：AZ与学习装置调整理由）",
        "url": "http://raim2005.blog18.fc2.com/blog-entry-1177.html",
        "tags": ["增田顺一", "第六世代", "XY", "AZ", "学习装置", "民间考据", "JP"]
    },

    # =========================================================================
    # 6. 第七世代 20周年集大成与开放探索（2016–2018 日月、究极日月、LGPE）
    # =========================================================================
    {
        "title": "ファミ通：『ポケットモンスター サン・ムーン』発売記念！大森滋×増田順一インタビュー（阿罗拉生态系统与岛屿巡礼革命）",
        "url": "https://www.famitsu.com/news/201611/18120892.html",
        "tags": ["大森滋", "增田顺一", "第七世代", "日月", "岛屿巡礼", "Fami通", "JP"]
    },
    {
        "title": "『ポケットモンスター サン・ムーン』公式サイト：ディレクター・大森滋氏が語る、2つのソフトに込めた想いとは？",
        "url": "https://www.pokemon.co.jp/ex/sun_moon/topics/160906_01.html",
        "tags": ["大森滋", "第七世代", "日月", "官方特写", "JP"]
    },
    {
        "title": "CGWorld 2017：クリーチャーズ ポケモンの設定画に命を吹き込むアセット制作にとどまらない現状と未来（宝可梦设定画赋予生命力与3D管线）",
        "url": "https://cgworld.jp/interview/creatures-201707.html",
        "tags": ["Creatures", "3D建模", "骨骼", "第七世代", "名侦探皮卡丘", "CGWorld", "JP"]
    },
    {
        "title": "CGWorld 2017：『ポケットモンスター サン・ムーン』の3Dアセット制作とそれを可能にする高度な3社協業体制",
        "url": "https://cgworld.jp/feature/201707-cgw227GG-pokemon.html",
        "tags": ["海野隆雄", "大森滋", "3D建模", "第七世代", "日月", "CGWorld", "JP"]
    },
    {
        "title": "GIGAZINE：ポケットモンスターがどうやって作られているのかが垣間見えるデザイン・アイデアスケッチなどの貴重な資料＆インタビュー",
        "url": "https://gigazine.net/news/20170905-pokemon-early-design-documents/",
        "tags": ["增田顺一", "大森滋", "初期草图", "第七世代", "设计管线", "GIGAZINE", "JP"]
    },
    {
        "title": "ファミ通：増田順一氏作曲のバトル曲が判明！『ポケットモンスター ウルトラサン・ウルトラムーン』制作秘話ファンミーティング",
        "url": "https://www.famitsu.com/news/201805/15157253.html",
        "tags": ["增田顺一", "大森滋", "岩尾和昌", "第七世代", "究极日月", "战斗曲", "Fami通", "JP"]
    },
    {
        "title": "ファミ通：コーヒー好きの“ピカチュウ（CV大川透）”はこうして生まれた――『名探偵ピカチュウ』開発陣に直撃インタビュー！",
        "url": "https://www.famitsu.com/news/201803/30154405.html",
        "tags": ["大川透", "Creatures", "名侦探皮卡丘", "外传", "Fami通", "JP"]
    },
    {
        "title": "Gamer.ne.jp：ポケモン新作発表会レポート『ポケモンクエスト』『Let's Go! ピカチュウ・Let's Go! イーブイ』およびSwitch完全新作",
        "url": "https://www.gamer.ne.jp/news/201805300063/",
        "tags": ["石原恒和", "增田顺一", "大森滋", "高桥伸也", "野村达雄", "LGPE", "Quest", "Gamer", "JP"]
    },
    {
        "title": "4Gamer：“かわいい”の裏に隠された職人技とは。『ポケモンクエスト』開発者インタビュー",
        "url": "https://www.4gamer.net/games/421/G042131/20180629087/",
        "tags": ["松崎翼", "齐田和生", "方块宝可梦", "Quest", "手游", "4Gamer", "JP"]
    },
    {
        "title": "アキバ総研：ついに本日11月16日発売！『ポケットモンスター Let's Go! ピカチュウ・イーブイ』発売記念イベントレポート（增田顺一谈重返关都）",
        "url": "https://akiba-souken.com/article/37143/",
        "tags": ["增田顺一", "齐藤优史", "大森滋", "第八世代", "LGPE", "秋叶总研", "JP"]
    },

    # =========================================================================
    # 7. 第八·九世代 Switch 开放世界与现代革新（2019–2024 剑盾、阿尔宙斯、朱紫）
    # =========================================================================
    {
        "title": "ファミ通：『ポケットモンスター ソード・シールド』の“いま聞きたいこと”増田順一氏、大森滋氏直撃インタビュー【E3 2019】",
        "url": "https://www.famitsu.com/news/201906/13177936.html",
        "tags": ["增田顺一", "大森滋", "第八世代", "剑盾", "E3", "Fami通", "JP"]
    },
    {
        "title": "4Gamer：『ポケットモンスター ソード・シールド』インタビュー。「最強」をテーマに，子供たちが楽しめるものを目指して",
        "url": "https://www.4gamer.net/games/451/G045142/20191114093/",
        "tags": ["增田顺一", "大森滋", "第八世代", "剑盾", "伽勒尔", "极巨化", "4Gamer", "JP"]
    },
    {
        "title": "コロコロオンライン：【劇場版ポケットモンスター ココ】音楽プロデュースを務める岡崎体育さんインタビュー！",
        "url": "https://corocoro.jp/special/152162/",
        "tags": ["冈崎体育", "剧场版", "可可", "音乐制作", "CoroCoro", "JP"]
    },
    {
        "title": "構想日本理事対談：ポケモンと考える『現実世界と仮想世界をより豊かにする方法』宇都宮崇人（株式会社ポケモン代表取締役）×伊藤伸",
        "url": "http://www.kosonippon.org/news/2020/taidan0901/",
        "tags": ["宇都宫崇人", "宝可梦社长", "现实与虚拟", "社会观察", "构想日本", "JP"]
    },
    {
        "title": "日本経済新聞：石原恒和・ポケモン社長 父に囲碁教わりゲーム好きに（日经新闻专访：父亲教围棋启蒙而迷上游戏）",
        "url": "https://style.nikkei.com/article/DGXKZO67530060R21C20A2KNTP00/",
        "tags": ["石原恒和", "生平", "围棋", "宝可梦社长", "日经", "JP"]
    },
    {
        "title": "ファミ通：『New ポケモンスナップ』石原社長＆須崎Dに聞く開発秘話。写真を撮ることが手軽になった2021年のゲームデザイン",
        "url": "https://www.famitsu.com/news/202104/30218824.html",
        "tags": ["石原恒和", "须崎春树", "随乐拍", "生态摄影", "万代南梦宫", "Fami通", "JP"]
    },
    {
        "title": "ファミ通：『ポケモンSV』のピカチュウはシリーズ史上最高のふさふさ感を実現。『ポケモンレジェンズ アルセウス』との同時開発秘話",
        "url": "https://www.famitsu.com/news/202208/27273621.html",
        "tags": ["大森滋", "岩尾和昌", "朱紫", "传说阿尔宙斯", "双轨开发", "皮卡丘毛发", "Fami通", "JP"]
    },
    {
        "title": "CGWorld 2023：『ポケットモンスター スカーレット・バイオレット』メイキング［PART1］扱う動きの幅とアイデアの創出",
        "url": "https://cgworld.jp/article/202304-pokemon1.html",
        "tags": ["Creatures", "Game Freak", "第九世代", "朱紫", "3D动作", "CGWorld", "JP"]
    },
    {
        "title": "CGWorld 2023：『ポケットモンスター スカーレット・バイオレット』メイキング［PART2］360度どの角度から見ても画になるモーション",
        "url": "https://cgworld.jp/article/202304-pokemon2.html",
        "tags": ["Creatures", "第九世代", "朱紫", "3D动画", "CGWorld", "JP"]
    },
    {
        "title": "CGWorld 2023：『ポケットモンスター スカーレット・バイオレット』メイキング［PART3］様々なものに興味をもちポケモン表現の幅を広げる",
        "url": "https://cgworld.jp/article/202304-pokemon3.html",
        "tags": ["Creatures", "第九世代", "朱紫", "生态塑造", "CGWorld", "JP"]
    },
    {
        "title": "Denfaminicogamer：『ポケモンSV』リアル調の世界とキュートな『ポケモンらしさ』を両立したビジュアル表現を徹底解説（パルデア地方の作り方）",
        "url": "https://news.denfaminicogamer.jp/kikakuthetower/230824n",
        "tags": ["大森滋", "视觉总监", "帕底亚地方", "第九世代", "朱紫", "Denfami", "JP"]
    },
    {
        "title": "CEDEC 2023 / ファミ通：鳴き声で『ポケモン』世界のリアリティを生み出す。リアルな環境音を作り上げるヒントは山の中にあった",
        "url": "https://www.famitsu.com/news/202308/24314405.html",
        "tags": ["音效工程", "宝可梦叫声", "环境音", "CEDEC2023", "Fami通", "JP"]
    },
    {
        "title": "ファミ通：『帰ってきた 名探偵ピカチュウ』陣内弘之氏＆石原恒和氏インタビュー。おっさんピカチュウは人の言葉をしゃべるポケモンの到達点",
        "url": "https://www.famitsu.com/news/202310/19320055.html",
        "tags": ["阵内弘之", "石原恒和", "名侦探皮卡丘", "外传", "Fami通", "JP"]
    },
    {
        "title": "ファミ通 2024：【ポケスリ】『ポケモンスリープ』ポケモンCOO宇都宮崇人氏＆SELECT BUTTON中内之公氏インタビュー",
        "url": "https://www.famitsu.com/article/202411/24717",
        "tags": ["宇都宫崇人", "中内之公", "Pokemon Sleep", "睡眠游戏", "Fami通", "JP"]
    },
    {
        "title": "Denfaminicogamer：『ポケモン』の複雑すぎるバトルシステムがどうなっているのか、ゲーフリの“ポケモンバトル”専門家に聞いてみた（バトルシステムの基盤設計と運用事例）",
        "url": "https://news.denfaminicogamer.jp/kikakuthetower/2607224z",
        "tags": ["对战系统", "数值设计", "Game Freak架构", "Denfami", "JP"]
    },
    {
        "title": "Denfaminicogamer：1000種類を超えるポケモン＋人間に対応するために開発された「ポケリグ（PokéRig）」とは？【CEDEC】",
        "url": "https://news.denfaminicogamer.jp/kikakuthetower/2607233k",
        "tags": ["PokéRig", "骨骼绑定", "1000只宝可梦", "CEDEC", "Denfami", "JP"]
    },
    {
        "title": "ファミ通 2026：【ぽこポケ】『ぽこ あ ポケモン』開発インタビュー。大森滋氏が『ポケットモンスター』開発時に“マップに草むらを置いた”経験から生まれた新境地",
        "url": "https://www.famitsu.com/article/202602/66124",
        "tags": ["大森滋", "外传探索", "地图草丛设计", "Fami通", "JP"]
    }
]

print(f"Total curated premium Japanese interviews: {len(curated_list)}")

# Write to json and markdown artifact
with open("data/unimported_japanese_interviews_curation.json", "w", encoding="utf-8") as f:
    json.dump(curated_list, f, ensure_ascii=False, indent=2)

print("Saved to data/unimported_japanese_interviews_curation.json")
