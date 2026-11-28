# PokeAmice 访谈归档与校对验收规格 V2（Zero-Fabrication Spec）

本规格基于 2026-10 至 2026-11 多轮审计（`translation-review` 全站批审、首藤刚志回忆录 87 章原页重建、全库 418 篇机械扫页 `original-check`、行注释与说话人核查、Wave B + Archive.org 扫描导入复验，以及本地待合流稿件深查）暴露出的全部系统性缺陷制定。**所有后续新收录稿件、修订稿件与上线合并前检查均须通过本规格（对应脚本 [audit_v2_spec.py](../tools/audit_v2_spec.py)）验证。**

---

## 历史审计暴露的核心问题与对应硬性门禁

### V2-G1：双语结构统一门（禁止绕过机器审计的旧格式）
- **历史问题**：部分旧稿将双语内容写在正文 HTML（`<div class="parallel-lang-source">`、`<div class="lang-ja">`）或 Markdown 表格中，或采用 `{type, text: {zh, en}}` 结构，或 `original` 全部留空只填中文，导致 `audit_source_fidelity.py` 与 `audit_translation_padding.py` 完全失效并跳过检测。
- **验收标准**：
  1. `layout: interview-editorial`（及访谈/扫图类文章）必须使用 YAML frontmatter 中的 `parallel_items`（或已登记 `scan_set` 的 `translation_segments`）。
  2. 正文 Markdown 体禁止残留 `<div class="parallel-lang-source">`、`<div class="lang-ja">` 或 `| 日本語原文 | 中文对照翻译 |` 双语表格。
  3. 禁止使用 `{text: {zh, en}}` 无 `original` 字段的条目结构；非编者小标题、非图片/分隔符的条目禁止 `original` 与 `translation` 任一为空；全篇 `original` 空值比例不得高于编者分段合理范围（非 `heading` 段落禁止 `original: ""`）。

### V2-G2：原文零伪造与多源 6-gram 忠实门
- **历史问题**：
  - 伪造日文/英文原话、用 AI 按中文或英文摘要反向回译成日文（如 CEDIL 摘要扩写成 16 段、App Famitsu / ファミ通 `パンドランド` 仅前两段为真、HarmoKnight 日文原文内甚至残留简体字 `（完美时机命中）`）；
  - 自造伪学术综述替代原稿（以 `考証前言：`、`考証背景：`、`本稿は、...`、`> **文献档案库说明**：` 开篇，`original` 与 `translation` 混入简体汉字，在未读取原页或已有 `scan-prepared/` OCR 的情况下凭空撰写条目）；
  - 无原页来源支撑或引用伪 URL（如把 `source.url` 写成 `https://pokeamice.com`）；
  - AI 自编「第1章 / Prologue / 小结」并反向翻译填入 `original`。
- **验收标准**：
  1. 严禁自指 `https://pokeamice.com` 作为文献来源；非纯线下印刷品必须在 `source.url` 与目录 `url` 具备完整有效的 `https?://` 主源 URL（不得为相对路径、空值或 `<NO_URL>`）。
  2. 严禁出现 `考証前言`、`考証背景`、`^本稿は、`、`文献档案库说明`、`学术归档评注` 等 AI 伪综述模板文本；日文 `original` 中不得出现简体中文独有字形或中文括注解释。
  3. 编者自拟中文小标题须置 `original: ""`，严禁自编外文原文小标题。
  4. 按完整多分页（`source_pages` / `source.pages` / 本地 `scratch/fetched_html/` / Wayback 原始捕获 `id_` / `scan-prepared/` OCR 或 `scratch/scans/*_source.json`）做 6-gram（拉丁文 12-gram）对照：有效长度段落单段覆盖率须 `>= 0.55`，全篇命中率须 **`>= 90%`**（多页/扫描未拆分源须达 `100%`）。任何已核实存在完整源页但覆盖率不达标的文章必须基于原页重抓重建，或无法取证时移出 `_posts/` 至 `_drafts/retired-*`。

### V2-G3：译文防注水、假名保守与注释真实门
- **历史问题**：AI 翻译常擅自添加背景解释、修辞套话（`x1.2–x2.0` 膨胀比）；将原文仅有的假名/罗马字人名猜译为汉字（如 `サトチ` 猜作佐藤、`Unno` 猜成 `宇野`）；行注释 `note` 编造年份/履历或混入译者工作笔记。
- **验收标准**：
  1. 日译中有效段落中位长度比 `med <= 0.90`（目标区间 `0.55–0.78`）；单段（排除括号注音）膨胀比 `> 1.15` 触发人工复核/重写门禁；拉丁文译中单段不得无故远超合理压缩比。
  2. 禁用 AI 套话空洞修饰堆砌，严禁引入原页未包含的专名、游戏标题、数字、人物履历与主观评价。
  3. 行内 `note` 禁止包含 `TODO`、`待确认`、`疑似网页` 等译者工作笔记，内容不得超出原文直接事实边界。
  4. 严禁残留大段未译日文假名（>12 假名且占比 >18%）、HTML 实体/标签、占位符及旧版非官方译名（`神奇宝贝`、`宠物小精灵`、`口袋妖怪`）。
  5. **保风格、重可读、上下文一致（区分门面与口头对话）**：
     - **标题、导语、摘要与客观叙述**：保持清晰、克制、规范的简体中文；禁用未转写日文汉字（`企画`、`出展`、`编集部`）、生硬构词直译（`过家家共犯关系`、`营销人`、`营销媒体`、`企画阵`/`企划阵`/`制作阵`、独立 `企划人`、`致死量`、`装置机能`、`负痛点`、`狙击点`）及出戏的营销号/大厂黑话（`赋能他人`、`心智占领`、`生态闭环`、`版权裂变`、`跨媒体破圈`、`史诗长访`、`殿堂级`、`颗粒度`），并确保同篇及同系列连访的媒体名、人名汉字与称谓前后统一。
     - **受访者口头对话**：只要中文读者读得顺、不产生错愕感，**鼓励适度保留日系访谈的语感与常用日系用语**（如音乐/演出语境中的“一体感”“疾走感”“跃动感”、画师口中的“空气感”、原文直喻 `ごっこ遊び` 或 `薄味/濃い味` 等口语比喻，以及贴合圈层语境的轻度口语），不得为求保守而强行改写为干瘪书面腔。

### V2-G4：网页抓取杂质与边界纯净门
- **历史问题**：爬虫抓取带入跨篇导航（`→ 公式サイト`、`■ 最近のコラム`、`［ HOME ］`、`バックナンバー`）、文内关联推荐（`関連記事：`、`▼関連記事`、`［関連記事］`）、杂志购书/附录广告（`Amazon で買う`、`ご購入はお早めに`、`特別付録`）、通讯订阅 CTA（`Sign up for ... newsletter`）、联盟免责（`アフィリエイトリンク`）、版权/邮箱页脚及同场无关他社获奖条目。
- **验收标准**：首尾与正文各段 `noise_candidate` / `site_chrome_in_body` 命中数为 **`0`**；剥离杂质时不得改写或截断任何真实访谈句子。

### V2-G5：说话人归属与段落对齐门
- **历史问题**：媒体记者提问或编辑部导语被错误标为受访者（`增田顺一`/`大森滋`/`太田`）；使用 `受访嘉宾` 等泛化占位名；两段原文并译到一行导致后续全篇错行偏移。
- **验收标准**：
  1. 全库通用占位 `受访嘉宾` 数为 **`0`**。
  2. 当 `original` 明显以媒体/采访者前缀引导时，`role` 不得误标为 `answer` 或归名至受访开发者。
  3. 首尾及核心问答段数、引号配对与行对齐逐段核实无偏移。

### V2-G6：去重与退役隔离门
- **历史问题**：同一篇文章因域名迁移（`gamasutra.com` ↔ `gamedeveloper.com`）或跨语言重复（`eurogamer.de` / `style.fm/shudoNNN`）或旧工作区脏索引残留，导致已退役于 `_drafts/retired-*` 的稿件与现行 `_posts/` 并存。
- **验收标准**：
  1. `_posts/` 内不得出现与 `_drafts/retired-*` 同名的退役稿件。
  2. 归一化来源 URL（去除尾斜杠与 `http/https` 差异、兼容 `gamedeveloper.com`/`gamasutra.com` 等别名）在 `_posts/` 中唯一，不得与已上线正式稿件重复收录。

### V2-G7：必需元数据与目录一致门
- **验收标准**：每篇上线候选文章的 frontmatter 必须完整包含 `archive_type`、`source`（规范字典格式，含真实来源标题与 URL/刊期）、`workflow`（含 `translation`/`proofreading`/`published`）、`entities`（`people`/`works`），且 `interview_id` 与 [pokemon_1000_interviews.json](../data/pokemon_1000_interviews.json) 的 `id` / `post_file` 1:1 匹配。

### V2-G8：目录、CSV 与派生数据同步门
- **验收标准**：
  1. [audit_corpus.py](../tools/audit_corpus.py) `broken_links_count == 0`、`missing_links_count == 0`、`csv_synced == true`。
  2. 所有未导入条目必须有明确且实证核验的 `disposition`（不得保留空占位）。
  3. 任何改动过行号、增删段或改标题的条目，须同步更新 `_data/quotes.yml`、`post_lore.yml`、`people_profiles.yml` 与 CSV。
