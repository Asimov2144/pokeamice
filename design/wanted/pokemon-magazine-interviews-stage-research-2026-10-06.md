# Pokémon 实体杂志访谈收录复原：阶段性研究整理

> **整理日期：2026-10-06**  
> **覆盖范围：1996–2012；本阶段重点为 2004–2011（Emerald → DP → Platinum → HGSS → BW）及欧美纸媒采访链**  
> **用途：PokeAmice 访谈资料库 / 杂志索引 / 扫描补档 / 后续书目核验**

---

## 0. 本阶段结论

这一轮检索已经从“发现可能存在的采访”逐步进入 **书目复原（bibliographic reconstruction）与原刊闭环（scan verification）** 阶段。

当前最重要的阶段性成果：

1. **DP → Platinum → BW 的欧美纸媒采访链已经形成。**
   - `Nintendo Power #215`：DP，**Pearls of Wisdom**
   - `Nintendo Power #240`：Platinum，**Pokémon Goes Platinum**
   - `Nintendo Acción #199`：Platinum 开发采访
   - `Official Nintendo Magazine #65`：BW / GAME FREAK 本社采访
   - `Nintendo Power #265`：BW，**Breeding the Fifth**
   - `Nintendo Acción #220`：BW，**Crear Pokémon es toda una responsabilidad**
   - `Official Nintendo Magazine #68`：Masuda × Sugimori Reader Q&A

2. **Nintendo Power #240 可以从过去的“#240/241”模糊记录修正为明确的 #240。**
   - 期号：#240
   - 日期：April 2009
   - 采访：Junichi Masuda × Takeshi Kawachimaru
   - 页码：**pp.42–44**
   - #241 不属于这篇采访。

3. **Nintendo Power #265 已可正式收录。**
   - 文章：**Breeding the Fifth**
   - 受访：Junichi Masuda × Ken Sugimori
   - 页码：**pp.18–20**
   - 同篇带有 `The Birth of Game Freak`、`A Visit to the Pokémon Center` 两个 sidebar。

4. **Nintendo Acción #220 可以正式建立记录。**
   - 文章：**Crear Pokémon es toda una responsabilidad**
   - 受访：Junichi Masuda × Mana Ibe
   - BW 专题约 pp.26–31，采访模块大概率位于 **pp.30–31**。
   - 页码仍应标记为 reconstructed，等待原刊逐页确认。

5. **ONM #68 / #69 的冲突基本可以收束。**
   - Nintendo UK 于 **2011-04-14** 明确宣传当期 ONM 内有 Masuda × Sugimori 回答读者问题。
   - 该当期对应 **ONM #68 / May 2011**。
   - 后来的历史网页镜像把同一内容标作 `Issue #069`，很可能是网页归档 metadata 错位。
   - 因此暂不应为 #69 另建一篇 Pokémon interview。

6. **BW 日文纸媒已经能形成“开发职能口述史”结构。**
   - Famitsu No.1137：项目 / Direction
   - No.1138：Masuda / Overall Direction
   - No.1146：Scenario
   - No.1153：Communication / C-Gear
   - No.1155：Battle

7. **2008–2009 的电击系仍是当前最大的扫描空缺。**
   - `電撃DS&Wii Vol.3` 可以确认是 Platinum 重点号，并附 `ポケットモンスター エントリーブック`。
   - 但目前仍没有足够证据确认其中存在 GAME FREAK 主创 Interview。
   - 因此应保持 `CANDIDATE / SCAN WANTED`，不能计入正式采访数量。

---

# 1. 验证状态与数据库规则

建议以后不再统一使用“待查”，而是至少区分以下状态：

| 状态 | 含义 |
|---|---|
| `VERIFIED` | 期号、文章、采访存在、主要受访者、页码基本闭环 |
| `ARTICLE_VERIFIED` | 文章和采访确认存在，但页码、版面或人物框仍待原刊确认 |
| `CANDIDATE` | 有专题/目录/二手证据，但尚不能确认是真正的开发者采访 |
| `SCAN_WANTED` | 已知目标明确，主要缺原刊扫描 |
| `METADATA_CONFLICT` | 不同来源在期号、人物、标题、页码等字段发生冲突 |

推荐继续保留验证字段：

```yaml
publication_verified:
article_verified:
interview_verified:
pagination_verified:
interviewees_verified:

source_scan:
source_catalog:
source_official:
source_secondary:

scan_wanted:
metadata_conflict:
notes:
```

### 证据优先级

建议按以下顺序处理来源：

1. **原刊扫描 / 原页**
2. **出版社、Nintendo、Famitsu 等同期官方公告**
3. **国家图书馆、杂志目录、Retromags 等书目记录**
4. **当年转载 / 同期新闻**
5. **可靠采访转录**
6. **后世 Wiki / 二次整理**
7. **搜索摘要、无来源转载**

特别注意：

> **网页转录页面的标题、期号、受访者 metadata 不能自动视为纸本 metadata。**

Nintendo Acción #199 与 ONM #68/#69 都已经证明这一点。

---

# 2. 阶段性总表

## 2.1 1996–2004：早期实体访谈链

| 年 | 刊物 | 内容 | 当前状态 |
|---|---|---|---|
| 1996 | Family Computer Magazine 1996-06-28 No.13 | 初代相关访谈 / FAX Q&A | 已识别 |
| 1997 | FamiMaga64 Issue 26 / 11月号 | 田尻智 Pokémon 2 长访谈 | A+ |
| 1998 | FamiMaga64 Issue 28 / 1月号 | 田尻智 × 裕木奈江 follow-up | A− / 原页复核 |
| 2000 | 電撃NINTENDO64 1月号 | 「苦労話インタビュー 『ポケモン 金・銀』開発秘話!!」 | A− / Scan Wanted |
| 2000 | The 64 DREAM #41 / 2月号 | 増田・渡辺・森本等 Gold/Silver 开发采访 | A+ |
| 2003 | Nintendo DREAM Vol.84 | Ruby / Sapphire：増田順一 × 杉森建等 | 既有 A |
| 2004 | Nintendo DREAM Vol.108 | FireRed / LeafGreen 开发采访 | 既有 A |
| 2004 | 週刊ファミ通 No.823 | Emerald 発売直前 Interview | A / 子页待扫 |

### 已找到的原刊 / 档案入口

- FamiMaga64 Issue 26 / November 1997  
  https://archive.org/details/famimaga-64-issue-26-november-1997-600dpi-ozidual
- The 64 DREAM #41 / February 2000  
  https://archive.org/details/64-dream-february-2000-02-600dpi-ozidual
- 電撃NINTENDO64 2000年1月号（中古书目入口）  
  https://www.suruga-ya.jp/product/detail/ZNON6622

### PokeAmice 已整理

- 《ゲーム会議》Vol.9  
  https://docs.pokeamice.com/%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91/%E7%BF%BB%E8%AF%91/%E8%AE%BF%E8%B0%88%E6%95%B4%E7%90%86/interview-2000-01-01-sunanohi-pokemon-game-kaigi/

---

# 3. Emerald：週刊ファミ通 No.823

## 基本信息

```yaml
publication: 週刊ファミ通
issue: No.823
year: 2004
game: Pokémon Emerald
article_type: interview
verification_grade: A
pagination_range_candidate: 147-151
scan_wanted: true
```

当前可以确认 No.823 存在 Emerald 发售前访谈，但仍需要把 **pp.147–151** 内的实际采访边界彻底复原。

## 尚需确认

- 正式文章标题
- 采访准确起止页
- 全部受访者
- 人物职位
- 是完整独立 Interview，还是 Emerald 大型特集中的子模块
- 是否存在 sidebar / developer comment

## 后世回忆线索

- 電撃オンライン 2026 对 2004 Emerald / Famitsu Interview 的后世回忆：  
  https://dengekionline.com/article/202604/73546

> 此链接适合作为“采访存在与内容背景”的后世佐证，不应代替 2004 年原刊。

---

# 4. Diamond / Pearl：欧美纸媒采访开始形成

## 4.1 Nintendo Power #215 — *Pearls of Wisdom*

### 当前记录

```yaml
publication: Nintendo Power
issue: 215
cover_date: 2007-05
article_title: Pearls of Wisdom
game: Pokémon Diamond / Pearl
interviewees:
  - Junichi Masuda
  - Ken Sugimori
  - Shigeru Ohmori
  - Takao Unno
article_verified: true
interview_verified: true
interviewees_verified: true
pagination_verified: partial
verification_grade: A-
scan_wanted: true
```

这是目前 **DP 海外纸媒线最重要的一篇大型开发采访**。

### 已确认

Retromags 的 #215 目录明确列出：

> `Pearls of Wisdom – Interview with the creators of Pokémon Diamond & Pokémon Pearl`

Bulbapedia 的 Nintendo Power Generation IV 索引进一步确认四位受访者：

- Junichi Masuda
- Ken Sugimori
- Shigeru Ohmori
- Takao Unno

### 页码

目前至少有后世文献引用指向 **Nintendo Power #215 p.37**，说明 p.37 位于该采访范围内；但尚未取得完整起止页。

### 来源

- Retromags — Nintendo Power Issue 215  
  https://www.retromags.com/magazines/usa/nintendo-power/nintendo-power-issue-215/
- Bulbapedia — Nintendo Power / Generation IV  
  https://bulbapedia.bulbagarden.net/wiki/Nintendo_Power/Generation_IV
- Greenfield City Developer Interviews（访谈索引）  
  https://greenfieldcity.net/pokemon/interviews/

### 下一步

**优先寻找 #215 扫描，确认 `Pearls of Wisdom` 首页与尾页。**

---

# 5. Platinum：当前复原最清楚的海外线之一

## 5.1 Nintendo Power #240 — *Pokémon Goes Platinum*

### 修正后的正式记录

```yaml
publication: Nintendo Power
issue: 240
cover_date: 2009-04
article_title: Pokémon Goes Platinum
game: Pokémon Platinum
interviewees:
  - Junichi Masuda
  - Takeshi Kawachimaru
pages: 42-44
article_verified: true
interview_verified: true
pagination_verified: true
interviewees_verified: true
verification_grade: A
```

### 重要修正

旧整理中曾出现：

> Nintendo Power #240/241（2009年4/5月号）

现在应修正为：

> **Nintendo Power #240 — April 2009**

Bulbapedia 的 Generation IV 索引明确：

- #240：`Pokémon goes Platinum`
- 内容包含 Masuda × Kawachimaru Interview
- #241：主要为 Platinum review，而不是这篇开发访谈

相关书目引用进一步将采访指向：

> **pp.42–44**

### 来源

- Retromags — Nintendo Power Issue 240  
  https://www.retromags.com/magazines/usa/nintendo-power/nintendo-power-issue-240/
- Bulbapedia — Nintendo Power / Generation IV  
  https://bulbapedia.bulbagarden.net/wiki/Nintendo_Power/Generation_IV
- PokeAmice 已整理翻译  
  https://docs.pokeamice.com/%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91/%E7%BF%BB%E8%AF%91/%E8%AE%BF%E8%B0%88%E6%95%B4%E7%90%86/interview-nintendo-power-masuda-kawachimaru-platinum-gens/

### 状态

**可以直接作为 VERIFIED 记录入库。**

---

## 5.2 Nintendo Acción #199 — Platinum Interview

### 当前记录

```yaml
publication: Nintendo Acción
issue: 199
cover_date: 2009-06
article_title_en: We talk with the creators of Pokemon
game: Pokémon Platinum
interviewees:
  - Junichi Masuda
  - Takeshi Kawachimaru
verification_grade: A-
metadata_conflict: true
scan_wanted: true
```

### 重要 metadata 冲突

Lewtwo 单篇转录页顶部写：

> Junichi Masuda, Ken Sugimori

但正文回答者明显出现：

> **Kawachimaru**

同时 Lewtwo 的总 Interview Index 又将该篇列为：

> **Takeshi Kawachimaru, Junichi Masuda**

因此当前更合理的数据库记录是：

- Junichi Masuda
- Takeshi Kawachimaru

而不是直接复制单页页眉中的 `Ken Sugimori`。

### 来源

- Lewtwo — Nintendo Acción 199 Interview  
  https://lewtwo.neocities.org/Interviews/plat-NintendoAccion199
- Lewtwo — Interview Index  
  https://lewtwo.neocities.org/interviews

### 尚需原刊确认

- 西班牙语原始标题
- 精确页码
- 人物介绍框
- “Sugimori” 是否纯粹为转录页 copy/paste error

---

## 5.3 Nintendo DREAM Vol.176

### 当前记录

```yaml
publication: Nintendo DREAM
volume: 176
cover_date: 2008-12
game: Pokémon Platinum
article_type: interview
interviewees_known:
  - Junichi Masuda
  - Takeshi Kawachimaru
  - others
verification_grade: A+
```

该期已经可以确认存在真正的 **GAME FREAK 开发阵 Interview**，不是单纯攻略或宣传专题。

### 当前建议

如果 PokeAmice 自有扫描已经完整保存，应把它重新补回：

- Nintendo DREAM Master Index
- Platinum Interview Series
- Person → Article 关系

### 尚需补齐

- 正式标题
- 页码
- 完整开发者名单
- 是否存在多个 interview module

---

## 5.4 電撃DS&Wii Vol.3 — 暂不升级为 Interview

### 基本书目

```yaml
publication: 電撃DS&Wii
volume: 3
cover_issue: 2008-10
release_period: 2008-09
game: Pokémon Platinum
status:
  - CANDIDATE
  - SCAN_WANTED
```

可以确认：

- 2008 年 9 月发行 / 10 月号 Vol.3
- Platinum 为重点内容
- 附：
  **ポケットモンスター エントリーブック**

但尚未找到可靠证据证明其中存在：

- GAME FREAK Interview
- Masuda Interview
- Kawachimaru Interview
- 開発スタッフ対談

因此不能仅仅因为它处在 Platinum 发售前关键节点，就自动升级成正式采访。

### 来源

- 駿河屋 — 電撃DS＆Wii 2008年10月号 Vol.3  
  https://www.suruga-ya.jp/kaitori/kaitori_detail/ZNON4512

该页面明确记录：

> 別冊付録：ポケットモンスターエントリーブック

---

# 6. HeartGold / SoulSilver：日本杂志线进入“书目清理”阶段

## 6.1 週刊ファミ通 2009年9月24日号

### 当前记录

```yaml
publication: 週刊ファミ通
cover_date: 2009-09-24
actual_release: ~2009-09-10
game: Pokémon HeartGold / SoulSilver
interviewee:
  - Tsunekazu Ishihara
verification_grade: A
```

核心内容：

- 为什么 Gold / Silver 相隔约十年才重制
- HGSS 的产品定位
- Pokémon 系列之后的发展

目前采访存在与核心人物已经可靠。

仍应补：

- 精确页码
- 正式标题
- 版式

---

## 6.2 週刊ファミ通 2009年10月1日号

### 当前记录

```yaml
publication: 週刊ファミ通
cover_date: 2009-10-01
actual_release: ~2009-09-17
game: Pokémon HeartGold / SoulSilver
interviewees:
  - Shigeki Morimoto
  - three_more_pending
verification_grade: A-
scan_wanted: true
```

已经可以确认存在约 **4 名开发者**参与的 HGSS 开发采访。

已知内容涉及：

- 菊草叶作为测试选择
- 难度 / 战斗平衡
- Platinum 基础
- 环境音
- 寺院实地录音

### 最大缺口

- 其余三名开发者全名
- 正式标题
- 页码

这是 HGSS 书目复原中很适合优先闭环的一篇。

---

## 6.3 Nintendo DREAM Vol.187

### 当前结构

这一期不应该在数据库里被简单记为“一篇 HGSS 采访”。

大型 HGSS 特集至少可以拆成：

```text
PUB-NDREAM-187
 ├─ ARTICLE-HGSS-GAMEFREAK-STAFF
 └─ ARTICLE-SUGIMORI
```

### GAME FREAK Staff Interview 已知人物

- 増田順一
- 森本茂樹
- 海野隆雄
- 森昭人
- 松島賢二
- 一之瀬剛

此外还有：

- 杉森建 individual interview

### 建议

后续数据库应分别创建 Article，不要将整个 Vol.187 合成一条记录。

### 当前状态

```yaml
publication_verified: true
interview_verified: true
pagination_verified: false
scan_wanted: true
verification_grade: A+
```

---

## 6.4 デンゲキニンテンドーDS 2009

目前可以确认该刊对 HGSS 的持续覆盖：

- 7月号：HGSS 封面 / 初报
- 9月号：HGSS 大型附录
- 10月号：发售前重点宣传
- 11月号：攻略阶段

但截至本阶段：

> **仍未找到足够证据证明其中存在 GAME FREAK 主创 Interview。**

因此目前统一保留：

```yaml
article_type: feature
interview_verified: false
scan_wanted: true
```

---

# 7. Black / White：目前复原最完整的一代之一

# 7.1 電撃GAMES Vol.14

这是目前第五世代实体杂志中史料价值非常高的一篇。

### 正式信息

```yaml
publication: 電撃GAMES
volume: 14
serial_number: 174
date: 2010-10-15
parent_publication: 電撃Nintendo DS 12月号増刊
article_title:
  GAME FREAK 開発スタッフインタビュー
  『ポケットモンスター』を変えること／変わらないこと
interviewees:
  - Junichi Masuda
  - Ken Sugimori
  - Shigeru Ohmori
  - Tetsuji Ohta
  - Mai Mizuguchi
verification_grade: A+
```

### 史料价值

核心主题不是普通发售宣传，而是：

- “Pokémon 感”到底是什么
- 系列中什么可以改变
- 什么不能改变
- 字体、窗口、地图为什么会影响 Pokémon identity
- C-Gear
- 擦肩通信
- PGL
- Game Sync
- 游戏与 Web 外部空间之间的关系

### PokeAmice 扫描与翻译

https://docs.pokeamice.com/%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91/%E6%89%AB%E6%8F%8F%E5%AD%98%E6%A1%A3/scan-dengeki-games-vol14-bw-gamefreak-interview/

当前页面已经保存原刊页图与正文，属于 PokeAmice 自有高价值证据。

---

# 8. Famitsu BW：“开发部门口述史”

当前越来越清楚，2010–2011 年的 Famitsu 并不是随机采访几位开发者，而是逐步采访不同开发职能。

建议建立：

```yaml
series_id: FAMITSU_BW_DEVELOPMENT_SERIES
```

结构：

```text
No.1137
Executive / Project / Direction
        ↓
No.1138
Overall Direction / Masuda
        ↓
No.1146
Scenario / Matsumiya
        ↓
No.1153
Communication / System
        ↓
No.1155
Battle
```

---

## 8.1 No.1137 — 发售期核心采访

```yaml
publication: 週刊ファミ通
issue: No.1137
cover_date: 2010-09-30
actual_release: ~2010-09-16
game: Pokémon Black / White
verification_grade: A+
```

涉及：

- 项目商业决策
- 为什么同一 NDS 平台仍制作完全新作
- 系列“新生”
- 用户层
- PGL

PokeAmice 自有扫描应作为主要证据。

---

## 8.2 No.1138 — 増田順一

```yaml
publication: 週刊ファミ通
issue: No.1138
cover_date: 2010-10-07
interviewee:
  - Junichi Masuda
verification_grade: A+
```

主要话题：

- BW 的“革新”
- 通关前只出现新 Pokémon
- 新地区 / 新角色
- N 与整体方向

---

## 8.3 No.1146 — 松宮稔展 / Scenario

```yaml
publication: 週刊ファミ通
issue: No.1146
cover_date: 2010-12-16
date_in_archive: 2010-12-02
interviewee:
  - Toshinobu Matsumiya
role: Scenario
verification_grade: A
```

主要内容：

- “Pokémon 解放”
- N
- Cheren / Bianca
- 人与 Pokémon 的关系
- 为什么不写善恶分明的故事
- 人的生活方式与思想多样性

### PokeAmice

https://docs.pokeamice.com/%E5%BC%80%E5%8F%91%E8%80%85%E8%AE%BF%E8%B0%88/%E5%AE%9D%E5%8F%AF%E6%A2%A6%E4%B8%BB%E7%B3%BB%E5%88%97/%E5%AE%9E%E4%BD%93%E6%9D%82%E5%BF%97%E4%B8%93%E8%AE%BF/interview-famitsu-1146-matsumiya-bw-scenario/

---

## 8.4 No.1153 — Communication / C-Gear

```yaml
publication: 週刊ファミ通
issue: No.1153
date_in_archive: 2011-01-06
interviewees:
  - Tetsuji Ohta
  - Shigeru Ohmori
topic:
  - C-Gear
  - Pass-by communication
  - High Link / Entralink
verification_grade: A-
```

重要内容：

- 降低通信功能门槛
- 不让多人玩法妨碍玩家各自的目标
- “自然地帮助别人的冒险”
- High Link 的设计思想
- 擦肩通信的实际反响

### PokeAmice

https://docs.pokeamice.com/%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91/%E6%9D%82%E5%BF%97%E6%91%98%E5%BD%95/interview-famitsu-1153-ota-ohmori-c-gear/

> 当前页面属于摘录型整理，应继续寻找原刊扫描以提升为 A/A+。

---

## 8.5 No.1155 — Battle

```yaml
publication: 週刊ファミ通
issue: No.1155
cover_date: 2011-02-03
date_in_archive: 2011-01-20
article_title:
  『ポケットモンスターブラック・ホワイト』
  開発スタッフが語るバトルの秘密
interviewees:
  - Shigeki Morimoto
  - Masaaki Taya
  - Kazumasa Iwao
verification_grade: A
```

主题：

- Triple Battle
- Rotation Battle
- 大爆炸削弱
- 战斗平衡
- 新宝可梦能力
- Dream / Hidden Ability

### PokeAmice

https://docs.pokeamice.com/%E5%BC%80%E5%8F%91%E8%80%85%E8%AE%BF%E8%B0%88/%E5%AE%9D%E5%8F%AF%E6%A2%A6%E4%B8%BB%E7%B3%BB%E5%88%97/%E5%AE%9E%E4%BD%93%E6%9D%82%E5%BF%97%E4%B8%93%E8%AE%BF/interview-famitsu-1155-morimoto-taya-iwao-battle-secrets/

---

# 9. BW：欧美纸媒采访链

当前已经可以整理成：

```text
Official Nintendo Magazine #65
GAME FREAK HQ / Sugimori
          ↓
Nintendo Power #265
Masuda × Sugimori
          ↓
Nintendo Acción #220
Masuda × Mana Ibe
          ↓
Official Nintendo Magazine #68
Masuda × Sugimori Reader Q&A
```

这些采访与日本 Famitsu 的“职能拆访”并不重复。

欧美纸媒常问：

- Pokémon 设计灵感
- 为什么重做全部新 Pokémon
- 最喜欢的 Pokémon / 地区 / 音乐
- 系列未来
- 主机与掌机
- 全球玩家
- 设计哲学

日本纸媒则更容易进入：

- 具体开发职能
- Scenario
- Battle
- Communication
- UI / System
- 组织与制作流程

因此建议把它们视为 **互补史料**。

---

# 10. Official Nintendo Magazine #65

### 当期官方证据

Nintendo UK 于 **2011-01-21** 发布：

> ONM travelled to Japan for an exclusive interview with Pokémon developers Game Freak.

并明确说明采访讨论：

- 如何创造大量 Pokémon
- 新作的灵感
- 如何超越 HGSS

Nintendo UK 同时提到该期存在 Reshiram / Zekrom 双封面。

### 二手同步报道

PocketMonsters 同日称：

> `Exclusive Interview with Ken Sugimori`

并整理了杉森建关于“150只新 Pokémon”设计的内容。

### 当前数据库建议

```yaml
publication: Official Nintendo Magazine
issue: 65
cover_period: 2011-02
release_date: 2011-01-21
game: Pokémon Black / White
interview_verified: true
core_interviewee:
  - Ken Sugimori
article_title: pending_scan
pages: pending_scan
verification_grade: A-/A
scan_wanted: true
```

### 来源

- Nintendo UK 官方当期宣传  
  https://www.nintendo.com/en-gb/News/2011/The-new-Official-Nintendo-Magazine-is-on-sale-now--253631.html
- PocketMonsters 同期整理  
  https://pocketmonsters.net/index.php/news/979

### 尚需确认

- 原刊正式标题
- 是否只有 Sugimori，还是还有其他 GAME FREAK 人员
- 页码
- 人物框

---

# 11. Nintendo Power #265 — *Breeding the Fifth*

### 正式记录

```yaml
publication: Nintendo Power
issue: 265
cover_date: 2011-03
article_title: Breeding the Fifth
pages: 18-20
game: Pokémon Black / White
interviewees:
  - Junichi Masuda
  - Ken Sugimori
sidebars:
  - The Birth of Game Freak
  - A Visit to the Pokémon Center
verification_grade: A
```

### 来源

- Bulbapedia — Nintendo Power  
  https://bulbapedia.bulbagarden.net/wiki/Nintendo_Power
- Dr. Lava / Lava Cut Content 转录与扫描整理  
  https://lavacutcontent.com/masuda-sugimori-gen-5/
- PokeAmice 已整理  
  https://docs.pokeamice.com/%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91/%E7%BF%BB%E8%AF%91/%E8%AE%BF%E8%B0%88%E6%95%B4%E7%90%86/interview-nintendo-power-bw-masuda-sugimori/

### 内容价值

- Black / White 名称与“二元性”
- 为什么通关前只出现第五世代 Pokémon
- Pokémon 的筛选流程
- 设计数量远高于最终 156 只
- 硬件分辨率对设计细节的影响
- GAME FREAK 早期历史

### 状态

**VERIFIED**

---

# 12. Nintendo Acción #220

### 当前记录

```yaml
publication: Nintendo Acción
issue: 220
cover_date: 2011-03
game: Pokémon Black / White
article_title_es: Crear Pokémon es toda una responsabilidad
article_title_en: Creating Pokemon is a responsibility
interviewees:
  - Junichi Masuda
  - Mana Ibe
feature_pages: 26-31
interview_pages: 30-31  # reconstructed
verification_grade: A-
scan_wanted: true
```

### 已确认

采访背景是两人在伦敦宣传 Black / White。

Mana Ibe 不应只记作“同行设计师”，因为转录中她实际回答了问题，因此应进入 `interviewees`。

### 来源

- Lewtwo 转录  
  https://lewtwo.neocities.org/Interviews/bw-NintendoAccion220
- DeVuego — Nintendo Acción #220 书目页  
  https://www.devuego.es/pres/revista/nintendo-accion/220

DeVuego 同时提供 Archive.org 阅读入口。

### 当前页码判断

目前较合理的重建：

- Pokémon BW feature：约 pp.26–31
- Interview module：约 pp.30–31

但仍应：

```yaml
pagination_verified: false
pagination_method: reconstructed_from_feature_boundaries
```

直到直接检查扫描页脚。

---

# 13. Official Nintendo Magazine #68 / #69 冲突

这是本阶段最重要的 metadata 修复之一。

## 13.1 同期官方证据

Nintendo UK 于 **2011-04-14** 宣布：

> Pokémon Black Version and Pokémon White Version directors Junichi Masuda and Ken Sugimori answer reader questions.

来源：

https://www.nintendo.com/en-gb/News/2011/The-latest-issue-of-Official-Nintendo-Magazine-is-on-shop-shelves-now--253616.html

这对应当时正在销售的新一期 ONM，即 **#68 / May 2011**。

---

## 13.2 历史网页镜像

PocketMonsters 保存了一篇：

> **The best of Pokémon**

内容确实是：

- Junichi Masuda
- Ken Sugimori
- Reader Q&A

问题包括：

- Starter 选择
- 最喜欢的地区
- Wii 主系列想法
- 最喜欢的音乐
- MMO Pokémon
- Pokémon 设计是否会枯竭
- Global Link / Entralink 灵感

但该镜像标记为：

> `Issue #069`

来源：

https://pocketmonsters.net/content/Interview_The_best_of_Pokemon

---

## 13.3 当前判断

建议数据库以 **#68** 为主记录：

```yaml
publication: Official Nintendo Magazine
issue: 68
cover_date: 2011-05
interviewees:
  - Junichi Masuda
  - Ken Sugimori
format: reader_qa
web_title: The best of Pokémon
print_title: pending_scan
pages: pending_scan
verification_grade: A-
metadata_conflict:
  web_mirror_issue: 69
  contemporary_official_issue: 68
```

### 不建议

不要因为历史网页镜像写了 #069，就自动建立：

```text
ONM #68 Interview
ONM #69 Interview
```

两篇重复记录。

### 下一步

找到 #68 原刊扫描：

- 确认 paper title
- 确认页码
- 确认该 Q&A 是否为纸本正文全部内容
- 检查 #69 是否只是后续网页再发布 / online feature

---

# 14. BW 的官方同期背景材料

虽然不是本轮实体杂志收录的主要目标，但可以帮助交叉验证实体采访主题。

## Iwata Asks — Pokémon Black / White

任天堂官方：

- Chapter 1：Making a Completely New Sequel for the Nintendo DS  
  https://www.nintendo.com/en-gb/Iwata-Asks/Iwata-Asks-Pokemon-Black-Version-and-Pokemon-White-Version/Pokemon-Black-Version-and-Pokemon-White-Version/1-Making-a-Completely-New-Sequel-for-the-Nintendo-DS/1-Making-a-Completely-New-Sequel-for-the-Nintendo-DS-209957.html

- Chapter 2：A Brand New Pokémon World  
  https://www.nintendo.com/en-gb/Iwata-Asks/Iwata-Asks-Pokemon-Black-Version-and-Pokemon-White-Version/Pokemon-Black-Version-and-Pokemon-White-Version/2-A-Brand-New-Pokemon-World/2-A-Brand-New-Pokemon-World-210016.html

- Chapter 4：The Unchanging Pokémon-ness  
  https://www.nintendo.com/en-za/Iwata-Asks/Iwata-Asks-Pokemon-Black-Version-and-Pokemon-White-Version/Pokemon-Black-Version-and-Pokemon-White-Version/4-The-Unchanging-Pokemon-ness/4-The-Unchanging-Pokemon-ness-210156.html

这些内容与：

- 電撃GAMES Vol.14 的“改变 / 不改变”
- Nintendo Power #265 的第五世代设计
- ONM #65 的 150+ 新 Pokémon
- Famitsu No.1137/1138 的总体 Direction

可以互相验证。

---

# 15. 2012 Black 2 / White 2：下一条已经基本成型的系列

虽然本阶段重点是 2004–2011，但 2012 Famitsu 的结构已经值得保留。

## 「開発キーパーソンインタビュー 1–5」

| # | Famitsu | 发售日 | 受访者 | 领域 | 当前证据 |
|---:|---|---:|---|---|---|
| 1 | No.1229 / 2012年7月5日号 | 2012-06-21 | 増田順一 × 海野隆雄 | Producer / Director | B+ |
| 2 | No.1230 / 2012年7月12日号 | 2012-06-28 | 増田順一 × 海野隆雄 | Direction / Character / World | B+ |
| 3 | No.1232 / 2012年7月26日号 | 2012-07-12 | 大村祐介 × 大久保智彦 | Design / Graphics | A− |
| 4 | No.1233 / 2012年8月2・9日合併号 | 2012-07-19 | **斉藤優史** | **Planning** | **A+** |
| 5 | No.1235 / 2012年8月16日号 | 2012-08-02 | 佐藤仁美 × 一之瀬剛 | Sound | A− |

### #4 是当前锚点

已有原刊页眉可确认：

> 開発キーパーソンインタビュー 4  
> INTERVIEW ～プランナー編～

受访者为：

> **斉藤優史**

如果旧数据库把海野隆雄也列为本篇 interviewee，应修正为：

```yaml
interviewees:
  - 斉藤優史

mentioned_people:
  - 海野隆雄
```

### Famitsu 官方 #1 入口

https://www.famitsu.com/news/201206/21016656.html

该页面确认：

- 2012-06-21 发售
- 7月5日号
- B2W2 16页特集
- Producer & Director Interview

### 同期二手线索

- B2W2 Design：大村祐介 × 大久保智彦  
  https://pk-mn.com/n/pokemon-b2w2-jinbutu-n-rival-design/
- B2W2 Sound：佐藤仁美 × 一之瀬剛  
  https://pk-mn.com/n/black2-white2-23ban-douro-music/

---

# 16. 当前 Scan Wanted 总表

## S 级：拿到扫描就能完成关键闭环

### S1 — Nintendo Power #215

目标：

- `Pearls of Wisdom` 首页
- 尾页
- 完整页码
- 是否有 sidebar

意义：

> 完成 DP 欧美纸媒核心采访。

---

### S2 — Official Nintendo Magazine #65

目标：

- 正式纸本标题
- 完整采访人物
- 页码
- GAME FREAK HQ 采访版面

意义：

> 完成 BW 海外发售前英国纸媒主线。

---

### S3 — Official Nintendo Magazine #68

目标：

- Masuda × Sugimori Reader Q&A
- 纸本标题
- 页码
- 彻底解决 #68 / #69 metadata conflict

---

### S4 — 週刊ファミ通 No.823 / pp.147–151

目标：

- Emerald Interview 首页
- 精确页码
- 标题
- 全部人物
- 栏目结构

意义：

> 完成第三世代后期的重要断层。

---

### S5 — Nintendo Acción #199

目标：

- 原刊人物框
- 页码
- 原始西语标题
- 验证 Kawachimaru / Sugimori metadata

---

## A 级：日本杂志书目补全

### A1 — Nintendo DREAM Vol.176

- 正式标题
- 完整人物
- 页码

### A2 — Nintendo DREAM Vol.187

- GAME FREAK group interview 页段
- Sugimori individual interview 页段
- 两篇分开建 Article

### A3 — Famitsu 2009-10-01

- HGSS 四名开发者全名单
- 页码
- 标题

---

## B 级：存在专题，但 Interview 尚未确认

### B1 — 電撃DS&Wii Vol.3

搜索目标：

```text
インタビュー
開発スタッフ
GAME FREAK
増田順一
川内丸武史
プロデューサー
ディレクター
```

### B2 — デンゲキニンテンドーDS 2009年9–10月号

同样不以“是否有 Pokémon 内容”为目标，而是判断：

> 是否真的存在开发者 Q&A / Interview。

---

# 17. 建议的采访系列页

随着资料增多，建议不要只依赖单篇卡片。

## Series A — `POKEMON_EARLY_MAGAZINE_ORAL_HISTORY`

覆盖：

```text
1996 Family Computer Magazine
→ 1997 FamiMaga64
→ 1998 FamiMaga64
→ 2000 電撃NINTENDO64
→ 2000 64DREAM
```

主题：

> Pokémon 2 / Gold & Silver 开发史。

---

## Series B — `GEN4_MAGAZINE_INTERVIEW_ARCHIVE`

覆盖：

```text
DP
Nintendo Power #215
      ↓
Platinum
Nintendo DREAM Vol.176
Nintendo Power #240
Nintendo Acción #199
      ↓
HGSS
Famitsu 2009-09/24
Famitsu 2009-10/01
Nintendo DREAM Vol.187
```

---

## Series C — `FAMITSU_BW_DEVELOPMENT_SERIES`

```text
No.1137
→ No.1138
→ No.1146 Scenario
→ No.1153 Communication
→ No.1155 Battle
```

---

## Series D — `BW_WESTERN_MAGAZINE_INTERVIEWS`

```text
ONM #65
→ Nintendo Power #265
→ Nintendo Acción #220
→ ONM #68
```

---

## Series E — `FAMITSU_B2W2_KEY_PERSON_1_5`

```text
1 Producer / Director
2 Direction
3 Design / Graphics
4 Planning
5 Sound
```

---

# 18. 推荐 Article 数据结构

```yaml
publication_id:
publication_title:
publication_series:
volume:
issue:
serial_number:
cover_date:
actual_release_date:
publisher:
jan:
isbn:
total_pages:

article_id:
article_title:
section_title:
article_pages:
article_type:
interview_format:

series_id:
series_number:
interview_session_id:

interviewees:
mentioned_people:
roles:

game:
generation:
topic_tags:

verification_grade:
publication_verified:
article_verified:
interview_verified:
pagination_verified:
interviewees_verified:

source_scan:
source_catalog:
source_official:
source_secondary:

scan_wanted:
metadata_conflict:
notes:
```

推荐 `article_type`：

```text
interview
roundtable
dialogue
fax_qa
developer_commentary
staff_comment
essay
feature
news
guide
retrospective
```

这样可以避免把：

- 专题
- 开发者寄语
- Roundtable
- Q&A
- 真正采访

全部混成 `interview`。

---

# 19. 关键来源索引

## Nintendo Power

### Generation IV Index
https://bulbapedia.bulbagarden.net/wiki/Nintendo_Power/Generation_IV

### Nintendo Power 总索引
https://bulbapedia.bulbagarden.net/wiki/Nintendo_Power

### Nintendo Power #215 / Retromags
https://www.retromags.com/magazines/usa/nintendo-power/nintendo-power-issue-215/

### Nintendo Power #240 / Retromags
https://www.retromags.com/magazines/usa/nintendo-power/nintendo-power-issue-240/

### #265 / Lava Cut Content
https://lavacutcontent.com/masuda-sugimori-gen-5/

---

## Nintendo Acción

### Lewtwo 总索引
https://lewtwo.neocities.org/interviews

### #199 Platinum
https://lewtwo.neocities.org/Interviews/plat-NintendoAccion199

### #220 Black / White
https://lewtwo.neocities.org/Interviews/bw-NintendoAccion220

### DeVuego #220
https://www.devuego.es/pres/revista/nintendo-accion/220

---

## Official Nintendo Magazine

### 2011-01-21 Nintendo UK — GAME FREAK interview
https://www.nintendo.com/en-gb/News/2011/The-new-Official-Nintendo-Magazine-is-on-sale-now--253631.html

### ONM #65 同期报道
https://pocketmonsters.net/index.php/news/979

### 2011-04-14 Nintendo UK — Masuda / Sugimori Reader Q&A
https://www.nintendo.com/en-gb/News/2011/The-latest-issue-of-Official-Nintendo-Magazine-is-on-shop-shelves-now--253616.html

### 历史镜像 — The best of Pokémon
https://pocketmonsters.net/content/Interview_The_best_of_Pokemon

---

## 電撃

### 電撃DS&Wii Vol.3
https://www.suruga-ya.jp/kaitori/kaitori_detail/ZNON4512

### NDL — 電撃DS&Wii Style
https://ndlsearch.ndl.go.jp/books/R100000002-I000009123139

### NDL — 電撃DS&Wii
https://ndlsearch.ndl.go.jp/books/R100000002-I000009408972

### PokeAmice — 電撃GAMES Vol.14
https://docs.pokeamice.com/%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91/%E6%89%AB%E6%8F%8F%E5%AD%98%E6%A1%A3/scan-dengeki-games-vol14-bw-gamefreak-interview/

---

## Famitsu / B2W2

### Famitsu 官方 — 2012-06-21
https://www.famitsu.com/news/201206/21016656.html

### Design / Graphics 同期佐证
https://pk-mn.com/n/pokemon-b2w2-jinbutu-n-rival-design/

### Sound 同期佐证
https://pk-mn.com/n/black2-white2-23ban-douro-music/

---

## PokeAmice BW 实体访谈

### Famitsu No.1146 — 松宮稔展
https://docs.pokeamice.com/%E5%BC%80%E5%8F%91%E8%80%85%E8%AE%BF%E8%B0%88/%E5%AE%9D%E5%8F%AF%E6%A2%A6%E4%B8%BB%E7%B3%BB%E5%88%97/%E5%AE%9E%E4%BD%93%E6%9D%82%E5%BF%97%E4%B8%93%E8%AE%BF/interview-famitsu-1146-matsumiya-bw-scenario/

### Famitsu No.1153 — 太田哲司 / 大森滋
https://docs.pokeamice.com/%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91/%E6%9D%82%E5%BF%97%E6%91%98%E5%BD%95/interview-famitsu-1153-ota-ohmori-c-gear/

### Famitsu No.1155 — 森本 / 田谷 / 岩尾
https://docs.pokeamice.com/%E5%BC%80%E5%8F%91%E8%80%85%E8%AE%BF%E8%B0%88/%E5%AE%9D%E5%8F%AF%E6%A2%A6%E4%B8%BB%E7%B3%BB%E5%88%97/%E5%AE%9E%E4%BD%93%E6%9D%82%E5%BF%97%E4%B8%93%E8%AE%BF/interview-famitsu-1155-morimoto-taya-iwao-battle-secrets/

### Nintendo Power #240
https://docs.pokeamice.com/%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91/%E7%BF%BB%E8%AF%91/%E8%AE%BF%E8%B0%88%E6%95%B4%E7%90%86/interview-nintendo-power-masuda-kawachimaru-platinum-gens/

### Nintendo Power #265
https://docs.pokeamice.com/%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91/%E7%BF%BB%E8%AF%91/%E8%AE%BF%E8%B0%88%E6%95%B4%E7%90%86/interview-nintendo-power-bw-masuda-sugimori/

---

# 20. 下一阶段执行顺序

## Priority 1 — 原刊闭环

按优先级：

1. **Nintendo Power #215 — Pearls of Wisdom**
2. **ONM #65**
3. **ONM #68**
4. **Famitsu No.823 pp.147–151**
5. **Nintendo Acción #199**

目标：

> `ARTICLE_VERIFIED / A−` → `VERIFIED / A or A+`

---

## Priority 2 — HGSS 书目清理

1. Famitsu 2009-10-01 四人名单
2. Nintendo DREAM Vol.187 两篇 Article 页段
3. Nintendo DREAM Vol.176 完整人物 / 页码

---

## Priority 3 — 电击系排雷

重点不是继续寻找“有 Pokémon 的期号”，而是针对已经锁定的期号检查：

```text
インタビュー
開発スタッフ
GAME FREAK
増田順一
森本茂樹
川内丸武史
プロデューサー
ディレクター
```

若不存在问答结构或人物采访框：

> 保持 `feature`，不要为了填补年代断层而升级成 `interview`。

---

# 21. 当前阶段总结

到 2026-10-06 为止，2004–2011 的采访收录骨架已经相当清楚：

```text
Emerald
Famitsu #823
     ↓
Diamond / Pearl
Nintendo Power #215
     ↓
Platinum
Nintendo DREAM Vol.176
Nintendo Power #240
Nintendo Acción #199
     ↓
HeartGold / SoulSilver
Famitsu 9/24
Famitsu 10/1
Nintendo DREAM Vol.187
     ↓
Black / White
電撃GAMES Vol.14
Famitsu #1137 → #1138 → #1146 → #1153 → #1155
ONM #65 → Nintendo Power #265 → Nintendo Acción #220 → ONM #68
```

因此项目目前不再处于：

> “还有哪些采访存在？”

而逐渐转向：

> **“如何把已经发现的采访恢复成可靠、可引用、可追溯到原刊的书目数据库？”**

后续工作的核心应该是：

1. 原刊扫描
2. 页码
3. 正式标题
4. 人物框
5. 同一采访 session 的关系
6. 纸本 metadata 与后世网页 metadata 的冲突管理
7. 将单篇采访组合成游戏 / 世代 / 媒体系列页

这将比继续无差别扩张采访数量更能提高 PokeAmice 资料库的研究价值。
