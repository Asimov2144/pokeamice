# 其他访谈文本质量审计（2026-09-27）

接续 [2026-09-26 文本边界与排版复核](translation-integrity-audit-2026-09-26.md)。本轮范围是当前 `_posts/` 访谈相关内容的自动筛查，加上若干高风险页面的来源及段落抽查；**不是 398 篇逐句对原刊的完整人工校勘**。以下记录审计发现及 2026-09-27 已执行的定点修订。

## 结论摘要

- 修订前快照共 1,172 篇帖子、31,500 个段落项；当前修订后为 31,486 项。按文件名、分类和标题宽泛识别，398 篇与访谈相关；其中包括首藤刚志连载随笔等并非问答访谈的内容。计数随工作区内容变化，不能直接与旧报告的项目数作差。
- `audit_reading_integrity.py` 未报出段落级“原文有字、译文为空”或“译文有字、原文为空”；这只能说明当前成对字段表面完整，不能证明 OCR 没漏整页或译文忠实。
- `audit_text_boundaries.py` 仍有 30 个内嵌标题／图注候选（20 篇）、37 个编号标题候选（22 篇）；都是待复核项，不应批量删除。
- `audit_translation_padding.py` 对 297 篇 `interview` 文件名帖子作长度筛查，34 篇译文项的中位中文／原文字数比超过 1.15。此规则只是风险排序；抽查后，首藤连载中确有多处无依据扩写与语义偏移，见下文。

## P0：三篇 Nintendo Power 文稿与刊物原文不符（已修复）

离线来源核验最初把三篇标为 `UNVERIFIABLE`，原因是仓库没有对应的本地原刊文本。随后对照刊物转录，并按原刊问答与 Dr. Lava 的作者解说分层修订；不再要求作者注释逐字对应杂志，也不把它伪装成受访者原话。三篇现已恢复发布状态。

1. **Issue 134（2000 年 7 月）**：[`2000-07-01-interview-nintendo-power-134-gold-silver-mew.md`](../_posts/2000-07-01-interview-nintendo-power-134-gold-silver-mew.md) 现在只把“我在初代开发结束前两周创造了梦幻”列为《Nintendo Power》问答；约300字节和调试功能移除的背景保留为 Dr. Lava 注，并注明来自后续 Iwata Asks，而非本期杂志原话。[扫描转录](https://www.rigelatin.net/copycat/media/print/np134.php) · [Nintendo 官方 Iwata Asks](https://iwataasks.nintendo.com/interviews/ds/pokemon/0/0/)

2. **Issue 240（2009 年 4 月；旧稿误标 Issue 241／5 月）**：[`2009-05-01-interview-nintendo-power-241-platinum-masuda-kawachimaru.md`](../_posts/2009-05-01-interview-nintendo-power-241-platinum-masuda-kawachimaru.md) 已校正刊期与期号，并用实际问答替换伪造的“破损世界”描述。Dr. Lava 对河内丸职业经历的推测仍予保留，但明确标作作者评论。[采访转录及刊期说明](https://lavacutcontent.com/masuda-interview-pokemon-platinum/) · [Issue 240 馆藏记录](https://library.gamehistory.org/repositories/2/digital_objects/12428)

3. **Issue 265（2011 年 3 月）**：[`2011-03-01-interview-nintendo-power-265-masuda-sugimori-bw-dexit.md`](../_posts/2011-03-01-interview-nintendo-power-265-masuda-sugimori-bw-dexit.md) 已将黑白主题改为增田所说的“两极性”，补回杉森对设计流程的原答；400–500 份明确为 Dr. Lava 根据“三倍左右”和156只新增宝可梦作出的推算。关于《剑／盾》的回顾继续保留为作者评论，未并入增田的访谈回答。[Issue 265 采访转录](https://lavacutcontent.com/masuda-sugimori-gen-5/)

## P1：确认为正文边界／翻译错误

### Game Informer 2017：相关推荐被当作访谈正文

`2017-08-18-interview-gi-2017-usum-mode.md` 在实机视频专题正文之后录入了 11 个其他专题／采访链接标题，末尾又把当前文章标题作为普通段落重复一次。原页面在“online features and interviews linked below”之后明确列出这些推荐链接；页面类型标为 **video feature**，主体是编辑说明、模式介绍和视频入口，并无问答逐字稿。**已删除正文中的推荐链接段落及重复标题，改标为媒体视频专题，并从访谈目录与相关推荐池中排除。**[Game Informer 原页](https://www.gameinformer.com/b/features/archive/2017/08/18/exclusive-reveal-of-a-new-mode-in-pokemon-ultra-sun-and-moon.aspx)

### 日经石原恒和访谈：一处主客体译反并伴随扩写

`2020-12-21-interview-nikkei-ishihara-go-boardgames.md`：原文是“母亲把接电话的我错认成父亲”；旧译文却写成“母亲接电话”，主客体颠倒。原文接着只说合照时父子身高一样，旧译文扩写为“全家福”、身形体态和站姿背影相同，并加入原文没有的信息。**已改正主客体，并收回无依据细节，调整为简洁自然的口语表达。**

### 访谈／专题的范围和标题层级

- `2015-07-14-interview-movie18-yuyama-hoopa-model-sheets.md` 对应的是 PocketMonsters 的电影频道内容页：前面有设定图与频道历史条目，中间是四期汤山邦彦专访，之后又继续收录设定资料。页面缓存标题为 “Pokémon Movie Channel: Appear! Movie Details”。这些内容并非已证实的抓取噪声，但整页合集被归为单篇 `interview_translation` 会让读者误以为所有内容都是访谈；宜拆分或明确标为频道档案合集。原站现已不可用，本项依据仓库保存的页面缓存和导入条目核对，尚未对历史页面做在线复核。
- `2016-08-25-interview-nikkei-utsunomiya-pokemon-go.md` 在前、后篇分别重复出现系列总标题，当前都作为普通段落；应确认它们是分篇标题、栏目标识还是导航，再用 heading／metadata 表达，不要当正文句子。
- `2004-05-13-interview-2004-05-13-ign-e3-2004-pokemon-creators.md` 开头的 “We chat with the director…” 是来源页导语，不是对话。保留可以，但应归为导语／摘要，不进入问答角色。

## P1：翻译扩写与口语流畅度

### 首藤刚志连载：需按系列集中校对

长度筛查覆盖 82 篇首藤随笔，其中 32 篇的中文／日文中位长度比超过 1.15。它们不是传统访谈，应与问答稿分开设校对标准；但抽查显示若干译文把朴素叙述加工成戏剧化评论，既不够忠实，也不够自然：

- `2010-06-30-interview-takeshi-shudo-pokemon-memoir-ch226.md`：已将相关句子收回为企划会议、预定播出半年、周六 17:30 与大相扑转播同档等原文信息，删除无依据的评价和播出范围扩写。
- `2010-01-20-interview-takeshi-shudo-pokemon-memoir-ch209.md`：已将相关句子改为“我原本打算在那部未能实现的第三部剧场版里，稍微触及这个问题”，删除病榻、笔记本电脑和“禁忌”等原文没有的情节与判断。

这些是经文本对照确认的例子，不代表该系列 82 篇已全部逐句核完。筛查分布显示应优先复核中位比最高及扩写最明显的篇目，避免把整篇改写成更华丽的中文散文。

## 自动候选与误报边界

- `source_heading_as_body` 的 32 个命中不等于 32 个标题错误：Steinberg 访谈中匹配到的多个 `<h>` 本来就是记者问题；1997 年 FamiMaga 的“其他宝可梦游戏相关文章”也属于该帖所述的杂志报道整理，不应当作网站噪声删除。
- 12 个“原文与译文相同”命中多为版权行、网址或保留原文的名称；不能据此批量补译。
- 日文残留命中多数是译文中有意保留的宝可梦名、日文标题或口号；只有逐项判断后才可认定 OCR／漏译。
- 本轮没有逐页抽检 2003–2013 年全部杂志扫描。当前字段层面没有检出空白译文，不等于 OCR 逐页完整，也不等于历史页序已确认。

## 建议顺序

1. **已完成修复**三篇 Nintendo Power 稿件，并将原刊问答、后续来源与作者评论分开标注；后续若取得原刊扫描页，可再补做逐页 OCR 与页序校对。
2. **已完成**日经石原访谈一处主客体纠错，以及首藤连载两处经原句核实的扩写修订；首藤系列其余高风险篇目仍需逐篇复核。
3. **已完成** Game Informer 视频专题的正文清理与归档分类修正。2015 电影频道合集和 2016 日经分篇标题层级仍待核实后处理。
4. 其余标题、图注、软换行候选按页面逐项核验。未经来源验证的自动命中继续留作待审，不批量清理。

