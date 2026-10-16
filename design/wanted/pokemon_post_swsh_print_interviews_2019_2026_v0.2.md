# Pokémon 剑盾之后实体访谈收录档案（2019–2026）

> 版本：v0.1  
> 日期：2026-10-08  
> 用途：PokeAmice Interview Archive / Wanted / 实体杂志扫描征集  
> 范围：Pokémon Sword / Shield → Expansion Pass → BDSP → Pokémon LEGENDS アルセウス → Scarlet / Violet → The Hidden Treasure of Area Zero → Pokémon LEGENDS Z-A

---

## 0. 收录原则

优先收录实体杂志原生开发者访谈、实体杂志采访的官方网页复刻、杂志 cover story、大型官方册子与开发者书籍。普通网页专访、发布会问答、CEDEC/GDC 演讲和普通攻略特集单独分类。

### 状态字段

```text
CONFIRMED_PRINT                 已确认实体刊载且明确有访谈
PRINT_DERIVED                   当前可访问网页，但官方明确说明源自实体杂志
FEATURE_ONLY                    实体大特集，尚未确认开发者采访
NO_INTERVIEW_CONFIRMED_YET      当前尚未确认，不代表绝对不存在
PAGE_RANGE_WANTED               采访精确页码待确认
SCAN_WANTED                     需要原刊扫描/数字版页图
```

---

# 1. Pokémon Sword / Shield（2019）

## 1.1 週刊ファミ通 2019年11月28日号

- 发售：2019-11-14
- Sword / Shield 发售纪念特集：44 页
- 采访：増田順一 × 大森滋
- 状态：`CONFIRMED_PRINT` / `PAGE_RANGE_WANTED` / `SCAN_WANTED`

Fami通 2019-10-25 网页采访明确说明，网页只刊出部分内容，完整 long interview 将刊载于该期纸本：

https://www.famitsu.com/news/201910/25185773.html

发售号官方介绍确认 44 页 Pokémon 特集，并明确包含増田、大森采访：

https://www.famitsu.com/news/201911/12186564.html

https://www.famitsu.com/news/201911/14186877.html

### Wanted

- [ ] interview 起始页 / 结束页
- [ ] 标题页版面与采访照片
- [ ] 与 Famitsu.com 摘录逐段 diff
- [ ] BOOK☆WALKER / Kindle / 实体扫描来源

---

## 1.2 Game Informer #319 — November 2019

- Issue：#319
- 类型：Pokémon Sword / Shield Cover Story
- 地点：GAME FREAK Tokyo headquarters
- 状态：`CONFIRMED_PRINT` / `PRINT_DERIVED` / `PAGE_RANGE_WANTED` / `SCAN_WANTED`

核心采访对象至少包括：

- Shigeru Ohmori
- Junichi Masuda
- Kazumasa Iwao
- James Turner

核心文章：**Going Big — The behind-the-scenes story of Pokémon’s next evolution**

https://gameinformer.com/feature/2019/11/13/going-big

网页明确说明：`This article originally appeared in the November 2019 issue of Game Informer.` 并写明记者前往 GAME FREAK 东京总部。

这次 reporting trip 后拆出了 Wild Area、Max Raid、Dynamax/Gigantamax、Pokémon design、Galar/UK inspiration、competitive systems、Exp. Share、autosave、National Pokédex、James Turner 设计过程、101 Rapid-Fire Questions、Burning Questions 等大量内容。

建议数据库按一个项目组织：

```yaml
series_id: GI_2019_SWSH_COVER_STORY
publication:
  title: Game Informer
  issue: 319
  month: 2019-11
primary_reporting_trip:
  location: GAME FREAK HQ, Tokyo
  interviewees:
    - Junichi Masuda
    - Shigeru Ohmori
    - Kazumasa Iwao
    - James Turner
outputs:
  - print_cover_story
  - topic_split_web_articles
  - videos
  - rapid_fire
  - follow_up_articles
```

### Wanted

- [ ] #319 完整目录
- [ ] Going Big 精确页码
- [ ] cover story 总页数
- [ ] 三种封面版本
- [ ] 数字版 / 原刊扫描
- [ ] 网页拆稿与纸本正文映射

---

# 2. Nintendo DREAM（2019–2020 Sword / Shield）

Nintendo DREAM 2019年5月号目录已经出现：

> [新作] ポケットモンスター ソード・シールド

https://www.ndw.jp/nd1905-301/

但该期对其他确有访谈的作品会直接标 `インタビュー`，Sword / Shield 条目没有。因此当前只能标 `FEATURE_ONLY`。

下一轮需逐期搜索：2019年5–12月、2020年1–12月，尤其关注 Expansion Pass 节点，并检索 `増田順一 / 大森滋 / 岩尾和昌 / James Turner / インタビュー / 開発者 / 制作スタッフ`。

---

# 3. Sword / Shield Expansion Pass（2020）

目前尚未确认与 2019 Fami通 / Game Informer 同等级的实体核心开发者长访。

状态：`NO_INTERVIEW_CONFIRMED_YET`

重点检索：週刊ファミ通 2020 Pokémon Direct 后、鎧の孤島、冠の雪原发售期、Nintendo DREAM、N-ZONE、EDGE、英国游戏杂志。

---

# 4. Pokémon HOME（2020）

当前没有确认实体开发者采访。状态：`NO_INTERVIEW_CONFIRMED_YET`。

---

# 5. Brilliant Diamond / Shining Pearl（2021）

当前尚未确认 ILCA 核心开发团队实体长访，也尚未确认増田順一的 BDSP 实体 director interview。

状态：`MAJOR_GAP` / `NO_INTERVIEW_CONFIRMED_YET`

重点刊物：週刊ファミ通、Nintendo DREAM、EDGE、N-ZONE、英国纸媒。

重点人物：Junichi Masuda、Yuichi Ueda、ILCA development staff、TPC project staff。

---

# 6. Pokémon LEGENDS アルセウス（2022）

目前可以确认 Fami通和 Nintendo DREAM 有大量发售特集、攻略、图鉴、试玩与 review，但第一轮尚未找到官方目录明确写 `開発者インタビュー`。

状态：`NO_INTERVIEW_CONFIRMED_YET`

重要相关开发资料但不是实体采访：CEDEC 2022，GAME FREAK 前澤圭一介绍 Legends Arceus / Scarlet Violet 同时开发的图形制作与 pipeline：

https://www.famitsu.com/news/202208/27273621.html

分类：`DEVELOPER_TALK`。

---

# 7. Pokémon Scarlet / Violet（2022）

## 7.1 週刊ファミ通 2022年12月1日号 / No.1772

- 发售：2022-11-17
- Scarlet / Violet：34 页发售大特集
- 内容包括开放世界、Paldea、Pokémon、Terastal、Tera Raid Battles、Picnic、preview/impressions
- 第一轮官方目录未确认 GAME FREAK 核心开发者采访

状态：`FEATURE_ONLY` / `NO_INTERVIEW_CONFIRMED_YET`

## 7.2 Nintendo DREAM

2022末–2023年间有大量 S/V 专题。当前观察到的目录规律是：真正有开发者采访的作品通常会明确标 `インタビュー / 開発者インタビュー / サウンドインタビュー`；Pokémon S/V 多数条目目前只标特集、企画、Pokédex 等。

因此当前仍为 `NO_INTERVIEW_CONFIRMED_YET`，下一轮继续逐期反证。

---

# 8. The Hidden Treasure of Area Zero（2023–2024）

Nintendo DREAM 2024年2月号目录包含：

- ポケットモンスター スカーレット・バイオレット　ゼロの秘宝
- 四天王メモリアル

https://www.ndw.jp/nd2402-357/

但同一期其他作品有访谈时会明确标 `インタビュー`，Pokémon DLC 条目没有。

状态：`FEATURE_ONLY` / `NO_INTERVIEW_CONFIRMED_YET`

---

# 9. Scarlet / Violet 开发资料：CEDEC

Nintendo DREAM WEB 对 CEDEC 2023 的报道：

https://www.ndw.jp/cedec2023-report-230827/

讲者：前澤圭一（GAME FREAK 研究開発部 CGテクノロジーラボ）。内容涉及 Paldea visual pipeline、地形与表现、rendering / asset workflow。

状态：`DEVELOPER_TALK / WEB_REPORT`。

---

# 10. Pokémon LEGENDS Z-A（2025–2026）

第一轮尚未确认传统纸媒中的核心开发者长访。

状态：`OPEN_SEARCH`

重点：週刊ファミ通 2025–2026、Nintendo DREAM 2024–2026、EDGE、N-ZONE、发售期官方 guide / staff interview。

---

# 11. 初步历史判断

2019 是明显高点：

- 日本：週刊ファミ通 2019年11月28日号
- 北美：Game Informer #319

两者均为核心开发者、大规模发售前后开发幕后、明确实体刊载。

2021–2024 则出现明显资料断层：纸媒 Pokémon coverage 仍然很高，但第一轮检索中明确标记的 GAME FREAK / ILCA 核心开发者长访明显减少。

应区分：

```text
print coverage remains high
≠
developer print interviews remain high
```

---

# 12. Wanted 优先级

## S级

### Game Informer #319
- 完整扫描
- cover story 页码
- interview pages
- 三种 cover
- 纸本与网页拆稿映射

### 週刊ファミ通 2019年11月28日号
- 増田 × 大森采访精确页码
- 原始版面
- 完整纸本正文
- 与 Famitsu.com 的差异

## A级

### BDSP developer print interview
目标：増田順一、上田祐一、ILCA team

### Legends Arceus print developer interview
目标：GAME FREAK director / planning / art / environment / battle staff

### Scarlet / Violet print developer interview
目标：director、GAME FREAK technical / art staff、Paldea planning team

---

# 13. 下一轮刊物矩阵

| 刊物 | 2019 SwSh | 2020 DLC | 2021 BDSP | 2022 PLA | 2022 SV | 2023–24 DLC | 2025–26 Z-A |
|---|---|---|---|---|---|---|---|
| 週刊ファミ通 | ★★★★★ | ? | ? | ? | FEATURE | ? | ? |
| Nintendo DREAM | FEATURE | ? | ? | FEATURE | FEATURE | FEATURE | ? |
| Game Informer | ★★★★★ | ? | ? | ? | ? | — | — |
| EDGE | ? | ? | ? | ? | ? | ? | ? |
| N-ZONE | ? | ? | ? | ? | ? | ? | ? |
| UK gaming magazines | ? | ? | ? | ? | ? | ? | ? |

下一轮需要逐条确认：

```text
issue
publication_date
article_title
interviewees
page_start
page_end
print_or_web
original_or_reprint
scan_source
digital_issue
PokeAmice_status
```

---

# 14. 当前结论

剑盾之后的实体访谈研究目前呈现：

```text
2019 Sword / Shield
├─ Famitsu long interview
└─ Game Informer massive cover-story reporting trip
       ↓
2020 Expansion Pass
       ↓
2021 BDSP
       ↓
2022 Legends Arceus
       ↓
2022 Scarlet / Violet
       ↓
2023–24 DLC
```

从 BDSP 起，纸媒 Pokémon coverage 仍很多，但真正能够第一时间确认的核心开发者实体长访明显变少。

下一阶段的任务是：**逐期证明哪些真的没有，而不是继续假设应该有。**

---

# 15. 第二轮逐期矩阵（v0.2）

> 本轮方法：不再只搜“Pokémon + interview”，而是利用杂志自身目录格式做反证：如果同一期其他作品明确标 `インタビュー / 開発者インタビュー`，而 Pokémon 条目只标 `特集 / 企画 / 新作`，则记为 `NO_INTERVIEW_CONFIRMED_YET`，但不写成绝对不存在。

---

## 15.1 Sword / Shield Expansion Pass — Nintendo DREAM 2020

### 20年4月号

- 发售：2020-02-21
- 封面：Sword / Shield Expansion Pass「鎧の孤島」「冠の雪原」
- 同期也介绍 Pokémon HOME
- Pokémon 内容以新情报、插图、介绍为主
- 页面未标开发者采访

来源：

https://www.ndw.jp/nd2004-312/

状态：`FEATURE_ONLY`

### 20年7・8月合併号

- 「鎧の孤島」配信 + 「冠の雪原」续报
- 同期其他栏目明确写 `プラチナゲームズインタビュー`、`キャラクターインタビュー`
- Pokémon Expansion Pass 条目没有 interview 标记

来源：

https://www.ndw.jp/nd200708-315/

状态：`FEATURE_ONLY`

### 20年9月号

- 付录：`ヨロイじま＋ガラル地方 人物名鑑`
- 本志 Pokémon 主要为新作特集
- 同期 `ニンジャラ` 明确写开发采访，说明目录并不会省略 interview 标签

来源：

https://www.ndw.jp/nd2009-316/

状态：`FEATURE_ONLY`

### 20年12月号

- 封面：`冠の雪原`
- Pokémon 両面ポスター
- 同期有 `ファイアーエムブレム0 フィナーレインタビュー`
- Pokémon 条目仍未见开发者访谈标记

来源：

https://www.ndw.jp/nd2012-319/

状态：`FEATURE_ONLY`

### 21年3月号

- 付录：Sword / Shield `ガラルスターファンブック`
- 内容核心是角色人气投票、角色资料、读者评论、卡片等
- 不是开发者访谈

来源：

https://www.ndw.jp/nd2103-322/

状态：`FEATURE_ONLY`

### 阶段结论

2020–early 2021 Nintendo DREAM 对 Expansion Pass 的纸本投入非常高：

```text
cover
poster
guide booklet
character encyclopedia
DLC features
```

但目前仍未找到一篇被目录明确标为 GAME FREAK 开发者访谈的 Expansion Pass 纸本文章。

当前：`NO_INTERVIEW_CONFIRMED_YET`

---

## 15.2 Famitsu — Expansion Pass

### 週刊ファミ通 2020年3月12日号

- 发售：2020-02-27 / Pokémon Day
- 内容：Sword / Shield 玩家调查、系列历史回顾、Expansion Pass 介绍、特制贴纸

来源：

https://www.famitsu.com/news/202002/25193148.html

此前的调查募集：

https://www.famitsu.com/news/202001/24191032.html

目前官方介绍未出现开发者采访。

状态：`FEATURE_ONLY`

本轮针对「鎧の孤島」「冠の雪原」继续搜索，也主要命中攻略、预览和新闻，没有找到能对应实体刊物的 GAME FREAK 长访。

---

# 16. BDSP — 纸媒逐期结果

## Nintendo DREAM 21年11月号

- BDSP 最新情报
- Legends Arceus 最新情报
- Pokémon news roundup
- 同期另有创刊25周年 creator 企划
- 未见 BDSP / PLA 开发者访谈标记

来源：

https://www.ndw.jp/nd2111-330/

状态：`FEATURE_ONLY`

## Nintendo DREAM 21年12月号

- Pokémon 相关以 BDSP / Legends Arceus B2 海报、`ポケモン堂 EXPERT` 等为主
- 同期明确标：
  - ドラクエX インタビュー
  - Monster Hunter 开发者 Q&A
  - Eastward artist interview
- Pokémon 条目没有 interview 标记

来源：

https://www.ndw.jp/nd2112-331/

状态：`FEATURE_ONLY`

## Nintendo DREAM 22年3月号

- 封面：Pokémon LEGENDS アルセウス
- BDSP：别册 `シンオウ図鑑＋お役立ちガイド`
- Legends Arceus：发售前系统/世界观/设施/队长/战斗特集
- BDSP：Gym Leader 名场面、读者投票
- 未见开发者采访

来源：

https://www.ndw.jp/nd2203-334/

状态：`FEATURE_ONLY`

## Famitsu — BDSP

2022年2月3日号是 BDSP 的“シンオウ地方振り返り”特集：

https://www.famitsu.com/news/202201/18248041.html

https://www.famitsu.com/news/202201/20248298.html

核心为：

- 游戏魅力回顾
- 玩家问卷
- 原版 DP 回忆
- 特制贴纸

未见 ILCA / 増田 / 上田访谈。

状态：`FEATURE_ONLY`

## Game Informer

2021-10-13 有 BDSP preview event：

https://gameinformer.com/preview/2021/10/13/whats-new-in-pokemon-brilliant-diamond-and-shining-pearl

属于媒体观看 demo / preview，不是 ILCA 开发者 interview，也没有发现对应实体 cover-story 长访。

因此 BDSP 仍应保持：

`MAJOR_GAP`

---

# 17. Pokémon LEGENDS アルセウス — 逐期结果

## Famitsu 2022年2月10日号

- 发售：2022-01-27
- 封面：Legends Arceus
- 发售纪念特集
- 世界观、人物、Pokémon、新操作、战斗/捕捉、先行 impression
- 没有在官方介绍中出现 interview

来源：

https://www.famitsu.com/news/202201/25248781.html

https://www.famitsu.com/news/202201/27249114.html

状态：`FEATURE_ONLY`

## Nintendo DREAM 22年3月号

如上，发售前总整理，没有 interview 标记。

## Nintendo DREAM 22年4月号

- Legends Arceus 特大海报
- Pokédex completion / 捕捉技巧特集
- 同一期 `Ocean's Heart` 明确写开发者 interview
- Legends Arceus 没有 interview 标签

来源：

https://www.ndw.jp/nd2204-335/

状态：`FEATURE_ONLY`

## Nintendo DREAM 22年5月号

- `Pokémon LEGENDS アルセウス　図鑑コンプリートへの道 その2`
- 同一期 Monster Hunter Rise 明确标 `1周年 総振り返りインタビュー`
- Pokémon 条目仍是攻略/调查型内容

来源：

https://www.ndw.jp/nd2205-336/

状态：`FEATURE_ONLY`

## Nintendo DREAM 22年6月号

- Scarlet / Violet + Legends Arceus clear file
- Pokémon 仍是资讯/企划向

来源：

https://www.ndw.jp/nd2206-337/

状态：`FEATURE_ONLY`

## EDGE April 2022

Pocketmags 可以确认 Edge April 2022 实体/数字期刊确有 Pokémon Legends: Arceus 文章：

https://pocketmags.com/us/edge-magazine/april-2022/articles/pok-mon-legends-arceus

但该文是 **review**，不是开发者采访。

状态：`PRINT_REVIEW / EXCLUDE_FROM_INTERVIEW_ARCHIVE`

### 阶段结论

PLA 有相当强的实体纸媒 coverage，但本轮横扫 Famitsu、Nintendo DREAM、EDGE 后，仍没有找到与 Sword/Shield 2019 类似的核心开发者实体访谈。

---

# 18. Scarlet / Violet — 逐期结果

## Famitsu 2022年12月1日号 No.1772

- 发售：2022-11-17
- 34页发售大特集
- 内容：Paldea、开放世界、Pokémon、Terastal、Tera Raid、Picnic、先行体验
- 官方介绍没有开发者访谈

来源：

https://www.famitsu.com/news/202211/16282730.html

https://www.famitsu.com/news/202211/17282914.html

状态：`FEATURE_ONLY`

## Nintendo DREAM 22年12月号

- Pokémon S/V 条目：角色自定义、Terastal、Picnic 等系统介绍
- 同一期明确出现：
  - `ソニックフロンティア インタビュー＋プレイレビュー`
  - `ハーヴェステラ 開発者インタビュー`
- Pokémon 仅标 `[特集]`

来源：

https://www.ndw.jp/nd2212-343/

状态：`FEATURE_ONLY`

## Nintendo DREAM 23年1月号

- S/V 封面
- 信息总整理、Iono 专题、starter personality test
- 未见 interview

来源：

https://www.ndw.jp/nd2301-344/

状态：`FEATURE_ONLY`

## Nintendo DREAM 23年2月号

- Pokémon S/V 独自调查企划、Academy teachers、Pokédex completion
- 同期明确列：
  - `オメガ6 開発者インタビュー`
  - `ソニックフロンティア サウンドインタビュー`
- Pokémon 条目仍没有 interview 标签

来源：

https://www.ndw.jp/nd2302-345/

状态：`FEATURE_ONLY`

## N-ZONE

N-ZONE issue chronology 显示：

- #308 / 12-2022：Pokémon Karmesin und Purpur cover
- #309 / 01-2023：Pokémon Karmesin und Purpur cover
- #310 / 02-2023：仍含 Pokémon Karmesin und Purpur

但目前只确认封面/评测/专题层级，尚未找到 GAME FREAK developer interview 证据。

状态：`PRINT_COVERAGE_CONFIRMED / INTERVIEW_UNCONFIRMED`

---

# 19. The Hidden Treasure of Area Zero — 逐期结果

## Nintendo DREAM 24年2月号 / vol.357

- Pokémon S/V + Zero no Hihou wall calendar
- B2 poster
- `[特集] ゼロの秘宝`
- `[特集] 四天王メモリアル`
- 同一期明确出现：
  - `超おどる メイド イン ワリオ　踊るインタビュー`
  - `OU 幸田御魚さんインタビュー`
- Pokémon 条目没有 interview 标签

来源：

https://www.ndw.jp/nd2402-357/

状态：`FEATURE_ONLY`

这一期是非常强的目录反证样本。

---

# 20. Pokémon LEGENDS Z-A — 2025–2026 实体矩阵

## Famitsu 2025年10月23日号 No.1918

- 发售：2025-10-09
- Z-A 发售直前特集：`ミアレシティ冒険ガイド`
- 官方介绍主要是玩法和已公开情报总结
- 同一号其他文章标题会明确写“インタビュー”
- Z-A 条目未见 developer interview

来源：

https://www.famitsu.com/article/202510/54674

状态：`FEATURE_ONLY`

---

## Nintendo DREAM 25年11月号 / vol.378

- Z-A B2 poster
- Z-A feature：Battle Club、新 Mega Evolution 等
- 同一期 `ドンキーコング バナンザ` 明确标 `開発者インタビュー`
- Z-A 没有 interview 标记

来源：

https://www.ndw.jp/nd2511-378/

状态：`FEATURE_ONLY`

## Nintendo DREAM 26年1月号 / vol.380

目录：

`[特集] Pokémon LEGENDS Z-A`

仍没有 interview 标记。

来源：

https://www.ndw.jp/nd2601-380/

状态：`FEATURE_ONLY`

## Nintendo DREAM 26年2月号 / vol.381

Z-A：

- Mega Evolution 深挖
- side missions
- paid DLC `M次元ラッシュ`

同一期 `ドラゴンクエストI&II` 明确标 `[インタビュー]`，而 Z-A 是 `[特集]`。

来源：

https://www.ndw.jp/nd2602-381/

状态：`FEATURE_ONLY`

## Nintendo DREAM 26年3月号 / vol.382

- Z-A long poster
- 独自企画 / feature
- 未见 developer interview

来源：

https://www.ndw.jp/nd2603-382/

状态：`FEATURE_ONLY`

## Nintendo DREAM 26年5月号 / vol.384

- Z-A popularity poll
- 同期 `ドラゴンクエストVII Reimagined` 和 `パラノマサイト` 明确标 `[インタビュー]`
- Z-A 仍为 `[特集]`

来源：

https://www.ndw.jp/nd2605-384/

状态：`FEATURE_ONLY`

## Nintendo DREAM 26年9月号 / vol.388

- Z-A clear file
- Z-A popularity/result feature
- 当期官方介绍直接写：`インタビュー記事は...2本立て`
- 指的是其他两个作品，不包括 Z-A
- 目录中 Z-A 为 `[企画]`

来源：

https://www.ndw.jp/nd2609-388/

状态：`FEATURE_ONLY`

## 截至 2026-10-08 的 Z-A 判断

截至目前能检索到的 Nintendo DREAM 2025秋–2026夏多期目录，Z-A 获得：

```text
poster
postcard
clear file
cover/feature
battle guide
Mega Evolution feature
DLC feature
popularity poll
```

但暂时未找到一篇目录明确标记为 GAME FREAK developer interview 的 Z-A 文章。

因此 Z-A 当前应从 `OPEN_SEARCH` 提升为：

`REPEATED_PRINT_COVERAGE / NO_DEVELOPER_PRINT_INTERVIEW_CONFIRMED_YET`

---

# 21. 海外纸媒第二轮排查

## Game Informer after 2019

### Expansion Pass 2020

找到 Crown Tundra preview：

https://www.gameinformer.com/preview/2020/10/21/pokemon-sword-shield-the-crown-tundra-preview-looking-for-legendary-status

这是 media preview，不是开发者专访。

### BDSP 2021

找到 preview event：

https://gameinformer.com/preview/2021/10/13/whats-new-in-pokemon-brilliant-diamond-and-shining-pearl

仍是 preview/demo。

### Legends Arceus 2022

Game Informer 主要为 podcast/review coverage，没有发现第二个像 #319 一样的 Pokémon cover-story developer reporting trip。

### Scarlet / Violet 2022

找到 Pokémon Presents 信息整理，但本轮未见 developer interview。

阶段结论：

**#319 仍然是 2019 之后 Game Informer Pokémon 开发者纸本访谈的异常高峰，而不是延续性的常态。**

---

## EDGE

### April 2022 — Pokémon Legends: Arceus

确认实体/数字刊载，但文章是 review：

https://pocketmags.com/us/edge-magazine/april-2022/articles/pok-mon-legends-arceus

不收入 interview archive。

## Retro Gamer

### Issue 228 — Pokémon Shining Pearl

Pocketmags 可确认纸本文章：

https://pocketmags.com/retro-gamer-magazine/issue-228/articles/pok-mon-shining-pearl

内容为 game review / Pick of the Month，不是开发者访谈。

状态：`PRINT_REVIEW / EXCLUDE`

---

# 22. 第二轮后的“实体采访断层”判断

现在已经可以把第一轮的直觉改写成一个有较多逐期证据支撑的命题：

## Sword / Shield 2019

```text
Famitsu          confirmed long developer interview
Game Informer    confirmed large-scale developer cover story
```

## Expansion Pass 2020

```text
Famitsu          large feature / survey
Nintendo DREAM   covers + guides + booklets + posters
Game Informer    previews
                 ↓
no core print developer interview confirmed yet
```

## BDSP 2021

```text
Nintendo DREAM   extensive print coverage
Famitsu          retrospective/features
Game Informer    preview event
                 ↓
ILCA/Masuda/Ueda print interview remains a major gap
```

## Legends Arceus 2022

```text
Famitsu          cover + launch feature
Nintendo DREAM   cover + posters + multi-issue guide
EDGE             print review
                 ↓
no core developer print interview confirmed yet
```

## Scarlet / Violet 2022–24

```text
Famitsu          34-page launch feature
Nintendo DREAM   repeated covers/features/DLC coverage
N-ZONE           repeated cover/review presence
                 ↓
no Game Freak core print interview confirmed yet
```

## Legends Z-A 2025–26

```text
Famitsu          launch feature
Nintendo DREAM   repeated features + posters + DLC + polls
                 ↓
no Game Freak developer print interview confirmed yet
```

---

# 23. 下一轮检索方向

现在继续扫普通发售特集的收益已经下降。下一轮应该改搜更容易藏有“工作人员原话”的载体：

## A. 官方攻略本 / 完全攻略本 / 设定资料书

重点：

- Sword / Shield official guide
- Expansion Pass guide
- BDSP official guide
- Legends Arceus guide / art & world books
- Scarlet / Violet complete guide / Pokédex books
- Z-A official guide

查：

```text
スタッフインタビュー
開発者インタビュー
制作秘話
設定資料
クリエイターコメント
```

## B. 攻略本出版社

- OVERLAP
- KADOKAWA / Famitsu
- 小学館
- 徳間書店 / Nintendo DREAM 系书籍

## C. 非游戏专业纸媒

- Nintendo DREAM special books
- 日経エンタテインメント！
- CGWORLD
- CGWORLD + digital
- 月刊CG / technical magazines
- CEDEC papers → magazine reprints

## D. 技术 / 美术工作人员

从“总监长访”转向：

- environment art
- CG technology
- Pokémon modeling / animation
- UI
- sound
- localization
- outsourcing pipeline

因为 2022 以后公开的开发信息越来越多地转移到 CEDEC / technical talks，而不是传统发售杂志 Q&A。

---

# 24. v0.2 结论

第二轮最重要的不是发现一篇新的超级长访，而是把一个长期趋势逐期坐实：

> **Pokémon 的实体纸媒曝光并没有在剑盾后减少；减少的是“核心开发者以传统杂志 Q&A/长访形式出现”的频率。**

尤其 Nintendo DREAM 是最有说服力的证据：它在同一期中会明确把其他游戏标为 `開発者インタビュー`，而 Pokémon 从 Expansion Pass、BDSP、PLA、SV 到 Z-A 反复只出现 `特集 / 企画 / 新作`。

因此后续 Wanted 页面不应该简单写“找某期 Pokémon 杂志”，而应该拆成：

```text
PRINT_COVERAGE_WANTED
DEVELOPER_INTERVIEW_WANTED
PAGE_RANGE_WANTED
SCAN_WANTED
OFFICIAL_GUIDE_STAFF_INTERVIEW_WANTED
```

这能避免把大量“有 Pokémon 的实体杂志”误认为“有开发者访谈的实体杂志”。

