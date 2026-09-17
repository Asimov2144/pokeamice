# 开发规划：Pokémon Development Atlas（分段实现、按数据完整度降级）

前提：`design/credits-atlas-plan-audit_2026-09.md` 的审计结论。原则一句话：**每个模块声明它需要的数据等级；
作品够不到等级时，模块换成降级形态或显示"来源不支持"，而不是显示错误数字。**

## 0. 数据等级（每作自动判定，写进生成的 JSON）

| 等级 | 判据（可自动） | 已达到的核心作 | 解锁的分析 |
|---|---|---|---|
| **L0 平铺** | 只有英文页，无日文对齐 | 海外版红蓝、Champions | 类别分布、Origins、Cohorts、Destinations、Relations（人级重叠） |
| **L1 平铺 + 对齐** | 有日文页（kana、`lead` 标记；2012 前 lead 由职名判） | 红绿 → LGPE、BDSP | + Leadership（rank 0–4）、职名 domain |
| **L2 嵌套** | 有 ≥3 个挂在 Section / Team 之下的区块（地区包装、公司标题、并列头衔不算） | 零之秘宝（剑盾、阿尔宙斯、朱紫、Z-A 已升 L3）；Champions 的层级只是公司 / 平台包装，算 L0 | + Team Anatomy（按解析树） |
| **L3 人工区块表** | `_data/credits_blocks/<game>.yml` 存在 | 无（第 1 阶段做 4 部） | + Core / Partner / Asset / QA / Loc 拆分、完整层级、组织连续性 |

等级只是"可以算什么"，不是评分。页面顶部一行标出：`数据：日文对齐 ✓ · 结构 nested · 组织归属 人工`。

降级规则（写死在生成脚本里，前端不判断）：

| 模块 | L3 | L2 | L1 | L0 |
|---|---|---|---|---|
| Team Snapshot | 五分 scope 堆叠 + 类别条 | 类别条 + "nested 结构 N team" | 类别条 | 类别条（标"无日文对齐"） |
| Team Anatomy | Studio→Section→Team | Section→Team（解析树） | 区块按类别/domain 分组列表 | 同 L1 |
| Leadership | rank + 组织 | rank（lead 来自日文页） | rank（职名判；lead 覆盖率脚注） | 仅 rank≥2（Director 类），Lead 行显示"来源无标记" |
| Origins / Cohorts / Destinations | 全 | 全 | 全 | 全（低置信匹配脚注） |
| Relations 人级重叠 | 全 | 全 | 全 | 全 |
| Relations 同 domain / Bridge 分类 | 全 | 全 | 职名 domain 能判的部分 | 同 L1 |
| 组织连续性（Remake） | developer + 区块 | developer 字段 | developer 字段 | developer 字段 |

## 1. 阶段 0：数据前置（只改工具和 _data，不出页面）

产出全部是可回归的文件；这一阶段结束就能用一条 python 查询回答方案 35 节的例句。

### 0.1 `tools/analyze-credits.py` 扩展
- `domain_of(role, path)`：规则表 `DOMAIN`（Battle / Field / Map / UI / Network / Tools & Pipeline / Graphics Tech /
  Pokémon asset / Character / Motion / Movie / VFX / Sound / Scenario / Localization / QA / Management / —），
  与 `CATEGORY` 同风格；先看 team 名，再看职名。未命中 → `null`，页面显示"未归类 N 人"，不猜。
- `FAMILY`：DLC → 母作（area-zero → scarlet-violet；今后的 DLC 同）。Origins / Destinations / Cohorts 默认按家族。
- `identity_confidence`：romaji 匹配 = high；positional = medium；无对齐或经 merges/splits = low。
- 输出 `assets/data/credits-profile/<game>.json`（方案 30 节的结构 + `level`、`coverage`），
  `assets/data/credits-relations.json`，`assets/data/credits-careers.json`（每人：作品 → category / rank / domain / raw_role）。
  现有 markdown 产物照旧。

### 0.2 `_data/credits_relations.yml`（人工维护）
```yaml
- source: legends-arceus
  target: scarlet-violet
  type: parallel
  evidence: [2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline]
  note: 前泽圭一 CEDEC 2022：模型制作环境同时服务两作
```
第一批：chronological = GF 本传主线（红绿 → 金银 → 红蓝宝石 → 钻珍 → 黑白 → XY → 日月 → 剑盾 → 朱紫 → Z-A）
加"第三版 / 续作"边（金银→水晶、钻珍→白金、黑白→黑白 2、日月→究极日月）；remake = 红绿→火红叶绿、
金银→心金魂银、红蓝宝石→ΩRαS、皮卡丘→LGPE、钻珍→BDSP；parallel = 阿尔宙斯 ⇄ 朱紫（有证据）、LGPE ⇄ 剑盾（候选，待证据）；
lineage = XY → Z-A、阿尔宙斯 → Z-A（候选）。analyze-credits 现有的开发变动链保留为 `transitions.md` 的口径，
页面上的"前作"改读这张表。

### 0.3 `_data/credits_blocks/<game>.yml`（人工，先做 Z-A、朱紫、阿尔宙斯、剑盾）
```yaml
- heading: Pokémon 3D Modeling          # 英文页标题（起点）
  until: Dcc Support Teams              # 含此标题为止
  organization: Creatures Inc.
  scope: asset
- heading: Research & Development
  until: Development Assistant
  organization: Game Freak
  scope: core
  parent_of: [Framework Team, Pokémon & Battle System Team, Communication Features Team, CG Technology Laboratory]
- heading: CG Technology Laboratory
  parent_of: [Base Technology Section, AI Section, Environment Development Section]
```
`tools/build-atlas.py` 读它，叠在解析结果上（解析文件 `_data/credits/<game>.yml` 保持是 wiki 的忠实记录）：给 section 加 `org` / `scope`，把 `parent` 接回 `path` 顶层。未覆盖的作不变。
实际格式：`from` / `until` 写区块顶层标题（或完整路径），`parent` 是祖先列表，后写的条目覆盖先写的；见 `_data/credits_blocks/legends-za.yml` 头注。
写表时对照实机片尾（公司标题在 wiki 里丢了，片尾有），每个区块的归属写在 `note`。

### 0.4 `_data/credits_eras.yml`
Cohort 的时代分段（RGB–GSC / RSE–DP / BW–XY / SM–SwSh / PLA–SV / 本作首次），可改；
Cohort 默认只算核心作，开关"含外传"。

### 0.5 回归
`tools/build-atlas.py --check`：从生成的 JSON 复现 `synthesis.md` 的三条结论（12 人 → 两企划团队 + 共享工厂；
领导层交接链；平行企划信号）和方案 35 节的 5 个例句，每条一段断言，失败即报。以后改分类规则先跑它。

## 2. 阶段 1：单作品页（5 个组件，先 Z-A 与日月两部验收）

`build-credits-site.py` 在 `/credits/<game>/` 名单之前插入一块 `<section class="atlas">`（预渲染 HTML，
JS 只做切换与展开，读同目录的 profile JSON）。组件顺序按数据等级从不依赖到依赖：

1. **TeamSnapshot**：总署名数、开发职务数（analyze 口径）、类别横条；L2 起加 team 数；L3 起加 scope 堆叠。
2. **StaffOrigins**：上一次 credit 来源（按家族聚合）；切换"最近一次 / 任一前作"；脚注低置信 N 人。
3. **ExperienceCohorts**：首次核心作 credit 的时代；切换"含外传"。
4. **TeamAnatomy**：L2/L3 树（人数、Lead、Section Director，展开成员）；L0/L1 降级为按类别 → domain 的区块列表。
5. **RelatedWorks**：读 relations 表：← 前作 / ⇄ 并行 / ↺ 复刻·原作 / → 谱系；每条带证据帖链接；点进 Compare（阶段 2 之前先链到对方名单页）。

验收：Z-A（L2，对齐好）、日月（L1，平铺、Section Director 只在职名里）两页都要能回答方案 34 节 Team / Experience / Origins 的问题，
且日月页没有任何"0 team / 0 lead"式的假数字。

## 3. 阶段 2：跨作品

- 页面按 relations 表生成 `/credits/compare/<a>--<b>/`（只生成表里有的对，不做任意配对；任意配对留给客户端后做）。
- 公共块：Shared / A only / B only（按类别 → domain 下钻）、Retention / Inheritance / Jaccard 三个并列、
  Role Transition Matrix（建在 category 上，格子展开到 raw_role）、Leadership 留任 / 首次 Lead。
- 按 `type` 切模板：
  - chronological：函数级留任（Prog→Prog…）、职务变动列表、新人；
  - parallel：Bridge 三分（同 domain / 跨 domain / Leadership），页首固定一句"两作署名≠同期在两组，关系级证据见证据栏"；
  - remake：People / Knowledge（生产职 → 监督职的识别规则：Supervisor / Advisor / Original 词 + rank 变化）/ Organization（developer + 区块表）三层；
  - lineage：只列重叠与证据，不出结论句。
- **StaffDestinations** 加到单作品页（数据集有后作时）；措辞固定"未见后续收录署名"。
- 人物页加 **Career Timeline**（`credits-careers.json`：作品 → category / rank / domain，raw_role 悬停）。

验收：阿尔宙斯 ⇄ 朱紫 的 Bridge 里 Graphics Tech / Tools 占比是否明显高于其他 domain（方案 35 节例句）；红蓝宝石 → ΩRαS 能列出转监督职的人。

## 4. 阶段 3：档案证据与研究结论

- **Archive Evidence**：帖子的 `entities.works` ↔ `credits_games.yml.work`、`entities.people` ↔ `people.yml.credits_key`、
  帖子 `topics` ↔ domain 词表（一张映射表）。单作品页与 Compare 页尾自动列"相关档案"，CEDEC / lecture_report 优先。
- **Development Topic** 就用 domain 词表本身，不另建实体。
- **Research Claim**：`_data/credits_claims.yml`（claim / credits 证据 / 档案证据 / status），首批三条来自 synthesis.md，
  状态 Hypothesis；页面上 Observation / Evidence / Interpretation 三色分栏。

## 5. 不做（沿用方案 33 节）
大型 network graph、几百人 Sankey、3D、综合评分、自动生成历史结论。任意两作 Compare 也推迟。

## 6. 工作量与顺序
阶段 0 ≈ 2 次工具会话（0.3 的 4 张区块表是人工对片尾，另算）；阶段 1 ≈ 2–3 次；阶段 2 ≈ 3 次；阶段 3 ≈ 2 次。
每阶段末跑 `build-atlas.py --check` + 全站构建，提交一次。阶段 0 完成前不写任何前端。

## 7. 阶段 0 完成记录（2026-09-17）

产出：`tools/build-atlas.py`（生成 + `--check` 20 条断言全过）、`analyze-credits.py` 的 `DOMAIN` / `domain_of` / `FAMILY` / `CORE_ORDER`、
`_data/credits_eras.yml`、`_data/credits_relations.yml`（40 条：25 chronological / 8 parallel / 5 remake / 2 lineage）、
`_data/credits_blocks/{legends-za,scarlet-violet,legends-arceus,sword-shield}.yml`（`verified: false`，待对片尾）、
`assets/data/credits-profile/<93 作>.json`（3.8 MB）、`credits-relations.json`（1.0 MB）、`credits-careers.json`（2.8 MB，3683 人；前端按需拆）、
`design/credits-analysis/{domains,atlas-summary}.md`。

跑出来就改了方案的三处：
- **"immediate previous credit" 默认要按核心作**（`immediate_core`）：数全部收录作品时，Z-A 的来源前三是「朱紫 366、名侦探皮卡丘 闪电回归 18、TCG Pocket 12」——
  后两者是 TPC / Creatures 方在外传里的署名，不是团队来源；火红叶绿的第一来源会变成 Genius Sonority 的圆形竞技场。两个视图都写进 JSON，页面默认 core。
- **immediate 视图会遮住并行前作**：朱紫的 dev 有 298 人上一次署名是阿尔宙斯（2022-01），剑盾只剩 66；Z-A 上一次是朱紫 392、阿尔宙斯 3。
  「Z-A 继承阿尔宙斯线」必须用 `any_core` 视图（曾在阿尔宙斯 ≥150 人）才看得见——RelatedWorks / Origins 要默认给两个数。
- **复刻的「生产职 → 监督职」在名单里基本不成立**：红蓝宝石 → ΩRαS 转监督 0 人、升职 4 人（大森 Game Designer → Director）；
  金银 → 心金魂银、皮卡丘 → Let's Go 各只有杉森一人（Graphic / Creative Supervisor）；钻珍 → BDSP 共同参与 4 人（GF → ILCA，连续性在组织层）。
  Remake 模板的重点改为「原作成员在复刻里升职」+「开发方是否更换」，Supervisory 只作为列表附带。

其他发现：Champions 的两级路径是「Staff list (2026) / ILCA,Inc. / …」这类公司 / 平台包装，不是团队，等级判定已排除，Champions 是 L0；
日月的两级只是「Digital Movie Design Section Director / Effect Design Section Director」并列头衔，L1。`puzzle-challenge.yml` 有 31 个空名字（解析问题，另修）。
阿尔宙斯 ⇄ 朱紫共同参与 299（Jaccard 0.325），Bridge 同领域 223 / 跨领域 44，同领域里 Pokémon Asset 116（Creatures 模型组）远超其他——
方案 35 节说的「Tools / CG Technology」在类别层要把 Creatures 拆出去后才看得到，这正是 L3 区块表的用处。
按占比看则成立：Tools & Pipeline 共享 12 人 = 朱紫该领域 21 人的 57%（Map & Field 23/97 = 24%，Pokémon Asset 116/252 = 46%）——Compare 页的领域表要同时给绝对数和占比。

## 8. 阶段 1 完成记录（2026-09-17）

产出：`tools/build-atlas-pages.py`（`build-atlas.py` 末尾自动调用）→ `_includes/atlas/<game>.html`（93 个预渲染区块，4.7 MB）；
`_layouts/credits-game.html` 在名单之前 `{% include atlas/<game>.html %}`，名单加了 `#roll` 标题；`assets/js/atlas.js`（只做切换）；
`_sass/minimal-mistakes/_atlas.scss`。区块表四张已对片尾核对（`verified: true`），Z-A 的 Concept Art 子块接回 Design & World Concept Section 之下。

验收（mini-site 实测，方案 34 节的问题）：

| 问题 | Z-A（L3） | 日月（L1） |
|---|---|---|
| 核心团队多大 | 参与 620 / 署名 966；构成条：开发本体 GF 375 · Creatures 199 · 本地化 148 · 测试 46 · 制作 43 · 感谢 82 | 参与 299 / 署名 586；无构成条（无区块表），页顶标「组织归属 无」 |
| 最大职能 | 美术 355（57%）、程序 98、企划 37 | 美术 184、程序 69、企划 49 |
| 独立 Team | 39 个；树：Programming / Graphic Design / Planning / Sound / Concept & Visual Studio（Design & World Concept、3D Visual）/ R&D → CG Technology Lab（Base Technology、AI、Environment Development）；Creatures 的 Pokémon 3D Modeling 单列 | 不显示 Team 数；组织结构卡写明「来源平铺」，按类别 → 领域列 102 个区块（程序：通信 34、地图 7、工具 5、界面 5…） |
| Leadership | Lead 以上 67、Director 级 30；lead 标记 31（日文页） | Lead 以上 38、Director 级 17；lead 标记 22 |
| 入行时代 | 2021–24 入行 245（40%）、本作首次 213（34%）、2016–20 88 | 2010–15 入行 111（37%）、本作首次 139（46%） |
| 来自哪里 | 最近一次：朱紫 392（63%）、首次 213；任一前作：曾在阿尔宙斯 ≥150 | 最近一次：ΩRαS 123（41%）、XY 35、首次 139（46%）；任一前作：XY 123 = ΩRαS 123 |
| 与前作共享 | 阿尔宙斯 224（本作 36% 来自它，领导层留任 37）；朱紫 392（63%，留任 49） | XY 122（41%，留任 22）；ΩRαS 121（40%） |
| 并行项目 | Pokopia 共同 42（同领域 Bridge 17）、Champions 51（26） | ΩRαS 121（同领域 Bridge 94 / 跨领域 19） |
| 证据 | 关系卡上的档案帖链接（阿尔宙斯 ⇄ 朱紫的 CEDEC 2022 两帖挂在那两页） | 前作 XY 的关系注明「67 人缺席 ΩRαS、在日月回归」 |

日月页没有出现任何「0 team / 0 lead」式的假数字；两页在 375px 宽下单列、无横向滚动。

阶段 1 之后的观察：Origins 的「最近一次」与「任一前作」并排后，并行开发的痕迹一眼可见（日月：ΩRαS 123 = XY 123，
即日月的老成员几乎全部同时在 XY 与 ΩRαS 署名过）。下一步阶段 2（Compare 页）就从关系表里已有的 40 条边生成。
QoL：职务 / 区块名带中文小字（`tools/role-zh.py`：短语表 → 逐词词典，公司名与「Staff list (2025)」类包装不译；
名单页 `<h3>`、画像树、人物页职务栏各显示一份，`.credits__zh-role` / `.atlas__zh` 在 ≤640px 隐藏）。
改词典后跑 `python tools/role-zh.py 400` 看译文，再跑 `build-credits-site.py` 与 `build-atlas-pages.py`。

