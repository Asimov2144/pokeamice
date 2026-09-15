# 访谈收录现状评估与收录计划（2026-09）

> 数据来源：`_posts/`（257 篇访谈版式页面）、`data/pokemon_1000_interviews.json`（主清单 1,063 条）、`data/*curation*.json`（人工筛选队列）。统计全部由脚本从文件里数出来，不含手填数字。
> 附件：[interview_queue_2026-09.json](interview_queue_2026-09.json) — 主清单里"未收录"项的逐条体检结果。

---

## 1. 现在站内有什么

**257 篇**访谈版式页面（`interview-editorial` 216 + 旧 `parallel-translation` 41）。

| 维度 | 分布 |
|---|---|
| 原文语言 | 日 202 · 英 44 · 西 9 · 中 2 |
| 年代（版式） | 1999：12 · 2003：5 · 2007：59 · 2011：39 · 2014：51 · 2019：81 · 2026：9 |
| 人物（受访次数） | 增田顺一 71 · 首藤刚志 46（手记连载）· 石原恒和 41 · 岩田聪 29 · 大森滋 23 · 杉森建 21 · 海野隆雄 13 · 森本茂树 12 · 一之濑刚 7 · 田尻智 6 · 岩尾和昌 6 · 宇都宫崇人 5 |
| 作品（实体标注） | 红·绿 69 · 动画系列 38 · 黑·白 34 · X·Y 33 · 超梦的逆袭 22 · 剑·盾 21 · 日·月 20 · 金·银 19 · GO 16 · 阿尔宙斯 14 · LGPE 13 · 朱·紫 12 · 心金魂银 11 · 红蓝宝石 10 |
| 来源域名 | style.fm 46 · nintendo.co.jp 34 · web.archive.org 30 · gamefreak.co.jp 18 · famitsu.com 12 · gameinformer.com 9 · denfaminicogamer 7 · recruit.pokemon.co.jp 5 · 4gamer 4 · dengekionline 4 · eurogamer 4 |
| 资料类型 | 网络访谈为主；杂志扫描 4 册；技术专题 4 篇；社长问 29 章；首藤手记 46 回；招聘访谈 49 篇 |
| 视频 | 0（全站只有 1 篇正文提到过视频平台链接） |

**读法**：这是一个以"增田顺一 × 任天堂/Game Freak 官方渠道 × 2008–2021"为重心的库。它在第五、六、八世代的官方口径上已经很厚，但在三个方向上薄：

1. **1996–2005**：1999 与 2003 两个年代合计 17 篇，而且 1999 的 12 篇里一半是 GlitterBerri / HelixChamber 这类研究整理，不是访谈本身。田尻智作为受访者只有 6 次。
2. **主系列以外**：钻石·珍珠 6、白金 6、ORAS 7、BDSP 0、Legends Z-A 0；衍生作几乎空白——圆形竞技场/XD 0、Ranger 0、Pokkén 0、Unite 0、Masters 0、随乐拍 3、不可思议迷宫 4。
3. **非官方、非日英语种、非文字**：西语 9 篇（全部是增田 2013–2016 访西），法/德/意/葡/韩/繁中 0；视频 0。

---

## 2. 主清单（1,063 条）体检

主清单不能直接当"待收录 800 条"来用，它有三层水分：

| 类别 | 条数 | 说明 |
|---|---|---|
| **编号占位符** | **289** | `欧美权威媒体专访 #847–#996`（150）、`日本专业游戏媒体专访 #698–#824`（127）、`元宫秀介完全攻略本对谈 #N`（12）——统一日期、URL 指向 notion 站内 slug、人物一律"增田顺一, 大森滋"。这是凑数的行，背后没有任何一篇具体文章 |
| Notion 站内 URL、无外部来源 | 39 | 其中 28 条"公式攻略本访谈"（1996 赤绿 → 2020 剑盾 DLC），标题写得像摘要，但没有页码、没有扫描；是"值得去翻的书"，不是已核实的条目 |
| 有真实 URL | **735** | 其中 444 已导入 |
| 真实 URL 且未导入 | 291 | = 首藤手记 150（另一会话正在逐回导入，站内已 46）+ Game Freak 博客 56（属博客复刻线，不走访谈）+ **访谈 85** |

对这 85 条逐条核对（见附件 JSON 的 `queue_status`）：

- `synthetic` 18：`N.O.M 宝可梦特别专栏 #130–#145`、`社長が訊く/開発者专栏 #673/#674`——又是编号占位符
- `already_on_site` 8：MeriStation 2016、El País 2014、Hobby Consolas 2013、Dordogne 2017 等其实已在站内，主清单的 `status` 字段没同步
- `triage` 16：`Notion收录：…` 一类的指针，混着真访谈（電撃 X·Y 增田×冈本信彦、宇都宫崇人对谈、J教室 YouTube 课）和非访谈（BW 不满点 wiki、staff blog、推特搜索）
- **`verified` 43**：真正可以立刻排期的

**所以：主清单里可核实、可立刻做的存量只有 43 条**，而不是标题上的"1000"。这 43 条按来源：N.O.M 17 · 任天堂「開発者に訊きました」8 · Game Informer 5 · 4Gamer 3 · Polygon 2 · 週刊ファミ通 2 · 法/意/德各 1 · Kotaku 1 · Game Developer 1 · CGWorld 1。

另外两个人工筛选队列（`unimported_english_interviews_curation.json` 60 条、`unimported_japanese_interviews_curation.json` 67 条、`new_batch_verified_japanese_interviews.json` 36 条）与主清单有大量重叠，且同样没有对着 `_posts` 同步状态——Eurogamer 2019 剑盾、電ファミ 铁板阵鼎谈、社长问 HGSS 都已在站内却仍列为未导入。

**结论**：继续从主清单里"挖"是挖不出多少东西的；更多访谈在清单之外。

---

## 3. 清单之外还有多少——按来源评估

下面按"能带来多少新访谈 / 获取难度 / 与现有工作流是否匹配"给每条线打分。标 **（核实）** 的是我凭记忆列出、需要逐条确认存在与原文的条目。

### 3.1 日文纸媒 —— 最大的未开采矿，需要扫描工作流

| 来源 | 预期 | 说明 |
|---|---|---|
| **Nintendo DREAM（ニンドリ）** | ★★★ 每代 1–3 篇，2004–2024 累计 30 篇以上（核实） | 每一部正作发售前后都有开发者访谈（DP、Pt、HGSS、BW、B2W2、XY、ORAS、SM、USUM、LGPE、剑盾、BDSP、LA、SV、ZA）；杉森建在此有过连载（主清单已列 2010）。站内只有 2011 年"黑白之桥"一篇。全部需要实体杂志 → CONTINUE 那套扫描 + OCR + 对照流程 |
| 週刊ファミ通 / ファミ通 DS+Wii | ★★★ | 每代发售特辑、20 周年（2016）与 25 周年（2021）特辑（后两者在 43 条队列里）；1996–2000 年田尻智的多次登场只在纸刊 |
| 電撃Nintendo / 電撃ゲームス | ★★ | 2010 年代的开发者访谈；電撃 X·Y 增田×冈本信彦已有指针 |
| CONTINUE / ユーゲー / ゲーム批評 / ゲームラボ | ★★ | 2000 年代亚文化刊物，田尻·杉森的长篇对谈集中在这里；CONTINUE vol.23/31/32 已做，同刊还有其它期 |
| CoroCoro / ポケモンファン | ★ | 面向儿童，但增田、杉森的专栏与发售前访谈有史料价值；有 CoroCoro 初代扫描指针 |
| BRUTUS / Casa BRUTUS / Pen（核实） | ★★ | 生活方式杂志做过宝可梦特集，杉森建、石原恒和的访谈角度与游戏媒体完全不同 |
| 书籍 | ★★★ 但版权最敏感 | 『ポケモンストーリー』（畠山けんじ・久保雅一，2000）是初代开发的口述正史；『田尻智 ポケモンを創った男』；各代公式ガイドブック的卷末 staff 访谈（主清单 28 条即指此）。建议只做**索引 + 摘译**，不整本翻 |

### 3.2 日文网络 —— 持续有产出，适合关键词监控

- **官方**：`nintendo.co.jp/nom/`（N.O.M 剩余 17 条已在队列；2000–2008 全部宝可梦相关号还可以再扫一遍目录）、`nintendo.co.jp/interview/`（「開発者に訊きました」阿尔宙斯 4 章 + 朱紫 4 章在队列，**Z-A 一期尚未检查**）、`pokemon.co.jp` 各作品官网的开发者留言、`gamefreak.co.jp/recruit/`（已 18 篇，站点会持续新增）、`creatures.co.jp` 招聘访谈（未收录）、`corporate.pokemon.co.jp`
- **媒体**：4Gamer、ファミ通.com、電撃オンライン、Inside、GAME Watch、AUTOMATON、IGN Japan、電ファミニコゲーマー、ねとらぼ、ITmedia；商业向的 日経クロストレンド / NewsPicks（已 2）/ 東洋経済 / WIRED.jp 上有石原恒和、宇都宫崇人的经营访谈
- **会议**：CEDEC（2011 田尻受赏在队列；2019 剑盾技术、2023 朱紫技术已做 4 篇；**2024–2026 各届未扫**）、GDC Vault（Game Freak 的英文讲座，核实具体年份）

### 3.3 英文 —— 存量大但翻译价值参差

- 队列里的硬货：**Polygon 2014 二十年口述史**（长文，几乎所有初代人物都发言）、Game Informer 2019 剑盾四连访、Game Developer 吉田宏信怪兽设计管线
- 纸刊扫描：Nintendo Power 1998–2012、Official Nintendo Magazine、EDGE / Retro Gamer 的 making-of（核实各期）
- 翻译型二手站（Shmuplations、Nintendo Everything、Lava Cut Content、Siliconera）——**用途是找到日文原始出处，不是拿英译再转中**；Shmuplations 尤其覆盖 1996–1999 年 Famitsu / 電撃 上的 Game Freak 访谈，正好补 1999 年代
- 视频/播客里的英文访谈见 §3.6

### 3.4 小语种 —— 按"人物出访事件"成批出现

增田、大森每到一个国家做发售宣传，当地媒体会在同一周集中发 3–8 篇访谈。按事件找比按媒体找效率高得多：

| 事件 | 语种 | 已有 | 可能还有（核实） |
|---|---|---|---|
| 2013-10 X·Y 欧洲巡回（巴黎、米兰、马德里） | fr / it / es | Hobby Consolas | Jeuxvideo.com（队列）、Multiplayer.it（队列）、Gamekult、Everyeye、Vandal、3DJuegos |
| 2014 iDÉAME Kids 巴塞罗那 / El País | es | Topo Gamer、El País | La Vanguardia、Nintenderos、Vida Extra |
| 2016-12 Switch 前夕西班牙 | es | MeriStation、GQ | Xataka、ABC |
| 2017 Game Freak 多尔多涅（法国取景考察） | fr | Pokémon Trash | Le Monde Pixels、Puissance Nintendo |
| 2018 LGPE 德国 | de | — | Eurogamer.de（队列）、GamePro、Spiegel Netzwelt、ntower |
| 2016 / 2019 台北（SM、剑盾）| zh-TW | — | 巴哈姆特 GNN、4Gamers TW |
| 2019–2023 中国大陆（石原、朱紫远程） | zh-CN | — | 篝火、游研社、VGtime、机核 |
| 剑盾 / 朱紫 韩国 | ko | — | Ruliweb、Inven、ThisIsGame |
| 巴西 / 葡语 | pt-BR | — | IGN Brasil、Omelete（增田是否到访待核实） |

法德意西这些语种的价值主要不在信息增量（内容多与英日重叠），而在**旁证与差异**：同一周不同记者问出的不同答案。建议每个事件收 1–2 篇最长的，其余做索引。

### 3.5 旁支人物 —— 目前接近零，且都有现成来源

| 人物/机构 | 站内 | 来源提示 |
|---|---|---|
| 山名学 / Genius Sonority（圆形竞技场、XD、对战革命） | 0 | N.O.M 队列里就有 4 篇 |
| 中村光一 / Chunsoft（不可思议迷宫） | 0（长畑已 4） | N.O.M 2005 队列 |
| 吉田宏信（美术） | 3 | Game Developer 2015 在队列 |
| James Turner（剑盾美术总监） | 0 | GI 2019 在队列、Nintendo DREAM 2019 有指针 |
| 田中宏和 / Creatures、前田纯太（卡牌） | 4 | Creatures 招聘站、Polygon「TCG at 20」（核实） |
| 一之濑刚、景山将太、佐藤仁美（音乐） | 7 / 4 / 0 | Steinberg 已做；演奏会节目册、Sound & Recording 杂志（核实） |
| 野村达雄 / Niantic（GO） | 1 | 日经、4Gamer、GDC 讲座 |
| 湯山邦彦、冨岡淳広、松本梨香（动画） | 0 | 主清单里 152 次是与首藤手记共标，真正的湯山访谈另需找 |
| 久保雅一（剧场版制片、『ポケモンストーリー』作者） | 0 | 出版社访谈、电影 pamphlet |
| 本地化：Nob Ogasawara、Hiro Nakamura | 0 | 英文播客/视频为主（§3.6） |
| Game Freak 前宝可梦时代（Quinty / Pulseman / Mario & Wario） | 1（Quinty 归来） | Shmuplations、GDRI、当年 Famitsu |

### 3.6 视频 / 音频 —— 只做索引不收录，但索引本身就是缺口

站内目前没有任何视频条目。候选（均需核实链接与时间戳）：

- **官方**：Nintendo Direct / Pokémon Presents 中的开发者段落；E3 2019 Nintendo Treehouse Live 剑盾（大森出镜，数小时）；E3 Coliseum 2019 剑盾座谈；Pokémon 官方 YouTube 的 Legends 系列开发者访谈；GAME FREAK 官方频道（招聘、杉森作画）；CEDEC / GDC 讲座录像
- **电视**：NHK『トップランナー』田尻智（1999 年前后）；テレビ東京『ポケモンの家あつまる？』增田出演回；『J教室』（队列指针）
- **纪录片 / 独立频道**：toco toco tv「Ken Sugimori」（2019 前后）；Archipel；Did You Know Gaming 对增田、对初代英文本地化者的采访
- **播客**：Game Informer Show、IGN Nintendo Voice Chat、Kinda Funny 的增田/大森访谈；日本侧的 ゲーム系 podcast

---

## 4. 收录计划

### 阶段 0（一周内）：把账做平
1. **清洗主清单**：289 + 18 条编号占位符标 `synthetic` 并从统计里剔除；28 条攻略本条目改为"待翻书"状态；`status` 字段改为由脚本对着 `_posts` 的 `original_link / source.url` 自动同步（现在有 8 条已在站内却标未导入）
2. 三个 curation 队列合并进主清单，去重键 = 规范化 URL + 日期
3. 产出一份"真实未收录 = 43 + triage 16"的工作队列（附件 JSON 已是雏形）

### 阶段 1（1–2 个月）：清掉 43 条 verified
按现有工作流即可（网页 → `interview-roles.py` → `interview-clean.py` → 编辑版），优先级：
1. 「開発者に訊きました」阿尔宙斯 ×4、朱紫 ×4 — 官方、成系列、2022 年代目前只有 9 篇
2. N.O.M ×17 — 2000–2008，填 1999/2003 两个薄年代，且旁支（Genius Sonority、Chunsoft）四篇在其中
3. Game Informer 2019 剑盾 ×4 + 2017 ×1，Polygon 2014 口述史（长文，单独排期）、2016
4. Fami通 20 周年 / 25 周年特辑，4Gamer CEDEC 2011 / 2026、年末汇总
5. 法 / 意 / 德各 1 篇 + 16 条 triage 里的真访谈（電撃 X·Y、宇都宫对谈、J教室）

### 阶段 2（一季度）：清单之外的三条硬线
1. **Nintendo DREAM 扫描线**：先列各期目录（二手书店 / 国会图书馆目录可查期号），按代购入，走 CONTINUE 流程；目标先做 DP / BW / XY / 剑盾四代
2. **1996–2000 日文原始出处回溯**：以 Shmuplations 已译篇目为线索找 Famitsu / 電撃 / ゲーム批評 原刊，从日文重译；目标把 1999 年代从 12 篇做到 30 篇，田尻智从 6 次做到 15 次
3. **旁支批次**：Creatures 招聘站、Genius Sonority / Chunsoft / Niantic / Bandai Namco 各作品的开发者访谈，每家 2–3 篇打底

### 阶段 3（并行）：小语种按事件收
按 §3.4 的事件表，每个事件收 1–2 篇最长的做全译，其余入索引；zh-TW / zh-CN 的巴哈 GNN、篝火优先（无需翻译，只需整理）。

### 阶段 4（并行）：视频索引
站内新建 `_data/video_interviews.yml` + 一个索引页，**只存链接与元数据**：

```yaml
- id: v-2019-e3-treehouse-swsh
  title: Nintendo Treehouse Live E3 2019 — Pokémon Sword & Shield
  date: 2019-06-11
  platform: youtube          # youtube / nicovideo / bilibili / podcast / tv
  url: https://…
  language: en
  people: [大森滋, 增田顺一]
  duration: "1:12:00"
  works: [宝可梦 剑·盾]
  segments:                  # 时间戳 + 一句话，是索引的价值所在
    - { at: "00:14:30", note: 旷野地带镜头设计 }
  transcript: none           # none / auto / manual —— 有字幕稿再考虑摘译
```
这一层做完，视频才真正进入检索和"同类资料"书架，而不只是外链。

---

## 5. 让"发现"可持续：关键词与监控

现在的发现是靠人翻 Notion。建议固定成一张按语种的关键词表 + 每月跑一次的来源巡检：

- **人名（各语种写法一并搜）**：田尻智 / Satoshi Tajiri；増田順一 / ますだ / Junichi Masuda；杉森建 / Ken Sugimori；石原恒和 / Tsunekazu Ishihara；大森滋 / Shigeru Ohmori；森本茂樹；岩尾和昌；宇都宮崇人；James Turner；一之瀬剛；山名学；中村光一；野村達雄
- **体裁词**：インタビュー / 対談 / 鼎談 / 座談会 / 訊く / 開発者に聞く / メイキング / 制作秘話；interview / Q&A / oral history / making of / postmortem；entrevista / interview / Interview / intervista / 인터뷰 / 專訪 / 专访
- **机构词**：ゲームフリーク / GAME FREAK；株式会社ポケモン / The Pokémon Company；クリーチャーズ；ジニアス・ソノリティ
- **巡检来源**：4Gamer 与 Famitsu 的「ポケモン」标签 RSS；`nintendo.co.jp/interview/`、`gamefreak.co.jp/recruit/`、`creatures.co.jp/recruit/` 的 Wayback CDX 变更；各作品官网的「開発者メッセージ」页；发售月 ±2 周对上述人名做一次全语种搜索
- **去重**：URL 规范化 + 日期 + 标题前 20 字；同一访谈的多语版本（日文原文 / 官方英译 / 二手英译）合并为一条，只标原文

---

## 6. 一句话

站内 257 篇已经把"增田 × 官方渠道 × 2008–2021"做厚了；主清单剩下的可做存量只有 43 条，不是几百条。**真正的增量在纸刊（Nintendo DREAM、90 年代 Famitsu）、旁支工作室、按出访事件成批出现的小语种访谈，以及尚未建立索引的视频**——这四条线各需要一套不同于"网页 → 翻译"的获取方式，而扫描流程和编辑版模版已经就位，缺的只是清单。
