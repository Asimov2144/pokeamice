# 翻译完整性审计 · 处理记录（2026-09-19）

对应 `translation-integrity-audit-2026-09-19.md`。均为工作树修改，未提交。
复跑 `tools/audit_reading_integrity.py --compact`：no_frontmatter 3→0、missing_original 14→1（剩 1 条是站内链接卡）、
noise_candidate 6→1、source_heading_as_body 62→32、identical_translation 12→11、duplicate_original 4→3。

## 已处理

| 报告条目 | 文件 | 做法 |
| --- | --- | --- |
| 8 头部损坏 | nom-2000-kubo / ndream-frlg / nom-emerald（均为 `??` 新文件） | 补 `---`；`type: speech` + 对象 speaker（53 条）转成模板认的 `speaker: 字符串` + `role` |
| 6 首藤 ch174 | ch174 | **整段错位**：item 109–142 译文向前错一位，末句"未译"只是尾巴。108 拆两条、110–142 后移一位，无需新译 |
| 1 TIME | 1999-11-22-time | teenager→"十几岁的少年"，删错误译注 |
| 11 card-e | 2001-11-01-card-e | 吉野元文回答与采访者收尾拆成两条（采访者 = `N.O.M采访者 / question`） |
| 4 评论区 | topofarmer | 以来源 `id="comments"` 为界，删末尾 12 条读者留言（item 91–102） |
| 5 整理页边界 | sunanohi-kaigi | **只保留 `#kaigi9` 一节**（26 条），h3/h4 补成 heading，front matter（标题/摘要/人物/URL）按该节重写；"石恒恒和"是来源笔误，译文改石原恒和并加 note |
| 5 / 2 | famimaga-tajiri | 同一页的另一份整页副本：保留 1995–2000 年杂志条目（原 item 3–53、63–75），删前言/目录、`#kaigi9` 段（已归 kaigi 篇）和 2003 年以后条目；source_url 改 `#1`；摘要/人物重写。Fami通 ↔ ファミマガ 混淆随前言一并消失，两篇复查无残留 |
| 9 GI 2019 | gi-2019-going-big | 删 7 处 `.toc-anchor` 复制段（3 处紧邻标题，4 处隔一张图） |
| 10 标题分类 | dordogne | 7 个源 h2/h3 提升为 heading |
| 10 | denfami-sonobe / funsproject-nishida | `type: section`（interview-editorial 模板不认）→ `heading`，共 17 条 |
| 10 | pocketmonsters-usum / famitsu-usum-director / reportajes | 按缓存源 h2/h3 提升 10 个标题；删 pocketmonsters、reportajes 各 1 条重复标题 |
| 13 | pokemon-peer-sugimori-ohmori | 7 条 original 从 pokebeach 缓存回填（英文） |
| 14 | denfami-pokemon-go-server-miracle | 6 条 original 从 denfami 缓存回填（日文）；川岛两条 question→answer；繁体译文按原文重译为简体 |
| 3 XD 扩写 | nom-xd-gale-of-darkness（`??` 新文件） | 23 条正文 + 15 条图注 + 标题/副题/摘要全部按原文重译，去掉"残酷人工手段""科研结晶""救赎叙事"等无中生有；workflow 改 `proofreading: pending` |

## 未动、需要拍板

- 剩余 32 条 heading 候选：Steinberg 11 条是 `role: question` 的提问（报告已说别改）；hoopa 设定图帖 16 条是来源页的新闻目录列表（与后文标题重复，属页面结构）；nikkei 宇都宫 2 条是标题重复，但该文件当前有别的会话的未提交改动，没碰；gi-2017-usum-mode / ign-e3-2004 各 1 条是 h1 标题 / 导语，不宜当章节。
- 单换行 451 条、vol31 OCR 乱码（需回原图）、`2026-08-29-continue-vol31` 的 `published: true` 未处理。
- **同一批 `??` 新文件（kubo / ndream-frlg / emerald）与 XD 同源**，标着 `human_reviewed / completed / published`，尾段已见"核心灵魂""未卜先知"式扩写，很可能和 XD 一样需要整篇重译。建议提交前先决定这批的去留。
- card-e 那条别的会话留下的 `human_reviewed` 标记未动。

## 第二批：`??` 新文件（kubo / ndream-frlg / emerald / XD）逐一回源核对

先对着 Wayback 原页核对"原文栏是不是原文"，再决定重译：

| 文件 | 原文核对 | 处理 |
| --- | --- | --- |
| nom-2000-kubo-pokemon-hit-secret | 问答原文真（nom/0006/04/04c01–02），但 8 个"第N章"标题是生成的日文；**且仓库里已有同一访谈的正式版** `2000-06-01-interview-nom-2000-kubo-masakazu-pokemon-hit.md`（已提交，DeepSeek 初译，draft，带真实页图） | 重译版已按原文重做（47 条、两页真实标题），但因属重复条目，**移到 `_drafts/…DUPLICATE-of-kubo-masakazu-pokemon-hit.md`**，不进 `_posts`。要用它的译文可整体搬到正式版 |
| nom-emerald-battle-frontier | 试玩报告段真（nom/0409/report），但卷头语、5 个章节标题、"技术进化系谱"总结是生成的 | 按 index / ayumi / hispoke / evopoke / report / newinfo 六页**整期重建**（40 条）：编辑长与コンドー分角色，历代软件表按原表转写，去掉全部生成段 |
| nom-xd-gale-of-darkness | 正文真（nom/0508/12、13、16） | 上一批已重译；这次补回漏掉的 2 句，章节标题换成原页标题 1-2 / 1-3 / 1-6，1-3 内恢复原页顺序（先メタング后新井寄语） |
| ndream-frlg-masuda-watanabe-nishino-uno | **原文栏是伪造的**：source_url 指向 gamesradar 2024 报道，该报道只转引 DidYouKnowGaming 视频里的几句英译；文件里 3,100 字"Nintendo Dream 2004年3月号原文"是据此生成的日文 | 不重译（重译只会把伪造洗白）。改 `workflow.published: draft`、`translation: unverified`，写入 integrity_note。要么找到 Nintendo Dream Vol.108 扫描重做，要么删除 |

另见：`2006-10-01-interview-nom-2006-diamond-pearl-…` 与 `2006-10-01-interview-nom-dp-…` 两篇已提交文件疑似同一访谈的重复，未处理。

## 并发冲突提示（2026-09-19 20:25）

- `2018-06-08-interview-denfaminicogamer-pokemon-go-server-miracle.md` 在本记录第一批修完之后（20:25）被另一个会话**整篇重导**（`fetch: live`、`deepseek-chat`、223 条、新图 011–026），我回填的 6 条日文原文与角色修正随之消失；重导后的版本不再包含「相思相愛」那一段（页 2），而是後篇页 3 的内容。该篇要按新版本重新审。
- 同一时段还有别的会话在往 `_posts` 加新文件（crystal / mobile / latios / dp-underground / 多个 ndream 扫描帖）并改 `2010-05-12-wedge-ishihara`、`2013-10-08-4gamer-solitiba`（审计新增的 9 条 missing_translation、6 条 duplicate_original 来自这两篇，不是本记录的改动造成的）。

## 第三批：新加的 `??` 帖子逐篇对 Wayback（2026-09-19 晚）

四篇 N.O.M 网页帖（其余 11 篇是扫描帖，Wayback 无从对起，见末尾）：

| 文件 | 原文核对（Wayback 实页 + data/cache_nom） | 处理 |
| --- | --- | --- |
| 2000-12-14 crystal | 正文全真（nom/0012/catalog/crystal + nom/0101/crystal 体験記）；3 个"第N章"标题是生成的 | 标题换成两页真实标题；20 条译文全部按原文重译（去掉"跨世纪登场""破天荒""擂主"等）；图注只写图里有的东西（原来把米那君写成"毕生追寻水君之谜"、水君写成"烧焦塔传说与北风化身"，都不在原文） |
| 2001-01-27 mobile | 正文真（what / asobi / get 三页）；4 个标题生成；原"接続と設定"一段是把 hituyo 页和未缓存的 provider（DION）页压成一段的改写 | 标题换成页面真实的 5 个栏目名；改写段拆回 hituyo 与 provider 两页的原句（provider 页从 Wayback 现取）；23 条译文重译，去掉"云端计算演进""熔断""P2P拨号直连""通信架构"等原文没有的词 |
| 2002-05-01 latios | 正文真（nom/0205/04）；4 个标题生成；原译把ソーナノ等写成"第三世代""丰缘地区"新宝可梦——2002 年 5 月的原文没有这种说法 | 标题换成页内 4 个真实栏目；8 条重译 |
| 2006-10-01 dp | 正文真（nom/0610/11，规格与作品简介是页面 alt 文本）；4 个"第N章"里 2 个有页面小标题依据、2 个纯生成 | 只保留 2 个真实小标题 + 页面标题；13 条重译（原译把"ぶつり・とくしゅ"扩写成整段"前三世代由属性绑定"的解说，把「久しぶりに遊ぶ」写成"正传全新世代久违的感动回归"，都删了） |

四篇都改成 `translation: human_retranslated_2026-09`、`proofreading: pending`，请再过一遍。

**11 篇扫描帖没法对 Wayback**（2005-08-18 continue-vol23；2008-08-21 ndream-2008-10 ×2；2008-10-21 ndream-2008-12 ×3；2009-09-21 ndream-2009-11 ×2；2010-02-20 ndream-2010-04 ×3）。只能说三点：
- 2008/2009 的 7 篇 workflow 标着 `ocr: visual-multimodal-aligned / translation: professional-proofread / proofreading: master-verified`，`pending_review_regions: 0`——这套标签和 XD / emerald 那批"human_reviewed / completed"是同一种口气，杉森 charakami 篇的译文里已出现原文没有的"【历代正统作演进一览】"清单；
- 2010-02-20 的 3 篇标 `ocr: qwen3.8-max full-page / translation: claude-editorial`，与仓库既定的扫描流程一致；
- 要核这些，只能按 scan-sets-import 的办法逐页对图重转写。没有做。

## 第四批：7 篇 ndream 2008/2009 扫描帖逐页对图重转写（2026-09-19 21:10）

对图确认：旧帖的"原文"是写出来的，不是读出来的。例：2008-10 P.007 洛托姆剪影页，页面只有マッスル的"うーむ、わからん!!"，旧帖却写出了五种形态的名字和描述；P.036 田尻访谈的问句和答句都是改写（"釣り堀が…改装されちゃったんです（笑）" 页面上没有这句）。

按仓库既定流程重做（`tools/import-scan-set.py`）：
1. `design/scan_sets_2026-09.json` 新登记 `ndream-2008-10`（20 页）、`ndream-2008-12`（16 页，`ocr_pages` 限 13 页）、`ndream-2009-11`（20 页），feature 页范围与 7 篇旧帖一致；speaker_map 补太田哲司、川内丸武史、森昭人、松岛贤二。
2. `ocr`：53 页 qwen3.8-max 整页转写（300 dpi 母版 + 高分辨率），缓存在 `data/cache_scan/ndream-2008-10|2008-12|2009-11/`，0 页失败。
3. `pages` 核对标题与页范围后 `build`：7 篇原地覆盖（文件名相同），DeepSeek 初译，`translation: deepseek-machine / proofreading: pending`，`pending_review_regions` = 全部文本段（225 / 227 / 106 / 84 / 133 / 311 / 151）。
4. `upload`：页图已传 COS（`https://gallery.pokeamice.com/scan-archive/<feature>/pages/`），抽查 200。

旧帖留底：`_drafts/retired-2026-09-19/`（7 篇）。另一个会话放在 `assets/images/scan-archive/dream-2008-10|2008-12|2009-11/` 的本地页图现已无帖引用，可删。
杉森 キャラかみ 页的问句在版面上是小标题，转写也按标题记，所以该篇 `questions 0` 是对的，不是漏识别。

未做：2005-08-18 continue-vol23（旧帖标 `manual-verified`，未对图）；2010-02-20 三篇（本来就是 qwen 流程产出，未复查）。
