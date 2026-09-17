# 审计：《PokeAmice Credits：Pokémon Staff Development Atlas》方案（2026-09-17）

对照物：`_data/credits/*.yml`（93 作、23,287 条署名，核心作 29 部）、`archive/credits/{index,merges}.yml`、
`tools/analyze-credits.py` → `design/credits-analysis/`、`tools/build-credits-site.py` → `/credits/<game>/`、`/credits/staff/`。

## 总评

方向对：把"某作有哪些人"升级成"这支团队是什么样、从哪来、往哪去"。方案里最该守住的判断都在：
Core 与 Total 分开（4 节）、Observation / Evidence / Interpretation 三分（3.1）、Retention / Inheritance / Jaccard
并列（13 节）、禁止综合评分（9、22 节）、"No later recorded credit" 而非"离职"（11 节）、raw_role 不可覆盖（26 节）、
关系手工维护（28 节）、先验证"有没有新认识"再谈 UI（35 节）。

问题在于方案是按理想数据写的。对照实际数据，有三类偏差：**来源里没有的字段**（组织归属、大部分年代的层级与 lead）、
**已经做了的部分**（变动链、类别、级别、逐作变动表——别再起一条流水线）、**跨年代比较会被来源粒度骗的指标**
（Section/Team 数量、Lead 数量）。下面按模块逐条说。

## A. 数据能否支撑

### A1. organization / scope 在来源里不存在 —— 第一版的前置工作，不是可选项

Bulbapedia 与日文 wiki 都是平铺的 `===` / `;` 标题，没有公司归属。Z-A 的 "Pokémon 3D Modeling"
（Art Director → Pokémon Character Modeling 101 → Motion 78，约 200 人，按惯例是 Creatures）、"Research & Development /
CG Technology Laboratory"（GF 内部）、"Pokémon Series QA"、"Project Management" 在来源里都只是并列标题；`kind: company`
只出现在 Partners / Developed By / Special Thanks 的 44 条公司名上。

→ 4 节的 Total → Core / Partner / Asset / QA / Localization 拆分，需要一张**人工维护的逐作区块表**
（如 `_data/credits_blocks/<game>.yml`：标题范围 → organization + scope），否则 "Core Development 312" 是猜出来的数字。
过渡期只能给 analyze-credits 的 category 分布（`sections.md` 已有），并写明口径。

### A2. 层级只有 2019 年以后才有；解析还压掉了一层

`path` 深度 > 1 的核心作：剑盾 54 个 team、阿尔宙斯 65、朱紫 101、零之秘宝 50、Z-A 39、Champions 79、Pokopia 139；
XY–LGPE 全部 depth 1（日月却在标题里有 9 个 "○○ Section Director"，说明 Section 层 2016 年就存在，只是 wiki 平铺了）。
Z-A 实际是 Studio → Section → Team（Concept & Visual Studio / Design & World Concept Section / Concept Art / Pokémon &
Character Design）和 R&D → Lab → Section → Team 四级，解析成两级后 "Pokémon & Character Design(16)" 丢了父级。

→ Team Anatomy 只对 6–7 作有意义。"Section 数量 / Team 数量" 放进 Team Snapshot 做跨作比较，会把 wiki 排版当成组织变化
——正是 3.1 自己禁止的事。建议：Snapshot 标 **结构粒度 flat / nested**，数量只在 nested 作之间比；解析器加逐作层级覆盖表
（标题 → 父级），可与 A1 的区块表合成一张。

### A3. lead 标记来自日文 wiki 的 '''リーダー'''

BW2 之前 lead 为 0；Champions 和海外版红蓝没有日文页 → lead 0、kana 0。Leadership Structure 对 Champions 会显示"无 Lead"，
对 2012 年以前也一样——缺数据，不是事实。DP / RS 年代的 lead 写在职名里（Program Leader / Graphic Leader / Main Programmer），
`rank_of` 已经处理。

→ `level` 必须允许 `unknown`，页面标注 lead 来源覆盖率；模块沿用 `rank_of`（职名 + lead 标记合一），不要只看 lead 字段。

### A4. 身份：罗马字归一 + 人工 merges / splits，置信度可直接派生

kanji 只有带 wiki 链接的人才有（Z-A 34/966），kana 在有日文页的作里近乎全覆盖。`identity_confidence` 直接由
`ja_match`（romaji / positional / 无）+ 是否经过 merges / splits 派生即可。真正的风险是同罗马字异人：Experience Cohort 的
"首次出现"和 Staff Origins 的"上一作"对误合并最敏感（一次误合并把新人变老手）。

→ 每个模块的数字旁给脚注"含 positional / 低置信匹配 N 人"，或在 cohort 里把低置信者单列。

### A5. 变动链必须显式定义，不能按发售日

数据里零之秘宝（DLC，839 条）夹在朱紫与 Z-A 之间；BDSP（ILCA）夹在剑盾与阿尔宙斯之间；Champions（2026）在 Z-A 之后；
Pokopia 是 Koei Tecmo。"immediate previous credit" 若按日期，Z-A 的 Origins 会变成 "零之秘宝 4xx 人"，朱紫被吞掉。
analyze-credits 已有 `CHAIN_SKIP` 与变动链。

→ 12 / 28 节手工维护关系是对的，再补一条：**DLC 归入母作（release family）**，Origins 默认按家族聚合，可切换到逐条 credit。

## B. 已经有的，别重做

- `analyze-credits.py` 已算：10 类 category、0–4 级 rank、逐作 transitions（留任 / 新人 / 回归 / 缺席后回来 / 之后再没出现 /
  职务变动）、每作各类人数、absences、`people.json`。这就是模块 3、4、5、6、13、14 的后端，只是现在输出 markdown 给代理读。
  最省的路径：让它多写一份 `assets/data/credits-profile/<game>.json`（30 节的结构），前端读它；
  不要另起 normalization → credits.json → analysis 的新流水线。
- `build-credits-site.py` 已生成 `/credits/<game>/`（HTML 预渲染，不走 Liquid）与 `/credits/staff/`（JS 读 credits-staff.json）。
  新模块做成同页区块或 `/credits/<game>/analysis/`，沿用预渲染（全站构建 6m49s，29 节"全部预计算"是对的）。
- `synthesis.md` 已有三条结论（12 人 → 两个企划团队 + 共享工厂；领导层交接链；平行企划信号）。
  25 节的 Research Claim 可直接把它们当第一批 claim，状态 Hypothesis。

## C. 指标与口径

1. **Retention / Inheritance 的分母**：Core 依赖 A1 的人工表。过渡期用 analyze-credits 的口径（排除 Thanks、Loc/QA、公司）并写明。
2. **Experience Cohort 的"首次 Pokémon credit"**：数据集含 64 部非核心作（Stadium / Snap / Pinball / 不可思议的迷宫……多为其他
   公司开发）。Creatures 建模师首次署名在 Ranch，不等于"进入 Pokémon 开发"的年代。Cohort 按"首次核心作"计，或范围可切换。
   11 节的 "Other Game Freak title" 措辞错：外传大多不是 GF 做的，应为"其他收录作品（外传 / 其他开发商）"。
3. **domain 轴目前不存在**——第一版唯一必须新写的分类器。好消息：平铺年代的职名自带 domain 词（Field Contents Programming /
   Battle System Programming / Tool Programming / 3D Map Graphics / Network Programming），可从职名 + team 名做规则表
   （Battle / Field / Map / UI / Network / Tools & Pipeline / Pokémon asset / Motion / Movie / VFX / Sound / Scenario /
   Localization…），与 `CATEGORY` 同放在 analyze-credits 里。Same-domain continuity、Bridge 分类、Matrix 都依赖它。
4. **Bridge Staff 加时间约束**：Parallel 关系里"同时出现在阿尔宙斯与朱紫"在 credit 上只是"两作都署名"，两作相隔 10 个月，
   不等于同期在两组工作。CEDEC 2022 的"同时开发"是关系级证据，不能下放到个人级。
5. **Role Transition Matrix 建在 role_family 上**，drill-down 才显示 raw_role；否则 "Programmers → Programming Section /
   Field Team" 这类措辞变化会污染对角线。
6. **Section Director 的两种来源**（日月：职名；剑盾后：层级）要合成一个 level 判断（`rank_of` 已合为 rank 2），否则同一模块两套口径。

## D. 范围与顺序

第一版 5 个组件建议改序：
1. 数据前置：A1 区块 → 组织表、A2 层级覆盖、C3 domain 分类器、A5 关系表 + 家族；
2. TeamSnapshot、StaffOrigins、ExperienceCohorts（平铺年代也成立）；
3. TeamAnatomy（只对 7 作有意义）；
4. RelatedWorks（依赖关系表）。

以 Z-A 做验收对象是对的（层级最全、有日文对齐、有阿尔宙斯 / 朱紫双前作和 XY lineage），但**同时用一部平铺年代的作（日月）验收**，
确保模块在 depth 1 数据上不塌。

## E. 成功标准补两条

- 35 节的 5 个例句直接当验收用例：每句都要能从生成的 JSON 用一条查询答出来。
- 34 节 Relations 加一问：**能否复现 synthesis.md 已有的三条结论？** 人工已得出的结论新系统显示不出来，就是口径错了——最便宜的回归测试。
