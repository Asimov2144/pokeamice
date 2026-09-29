# 翻译质量审计（2026-09-25）：杂志访谈与新入库内容

接 `translation-integrity-audit-2026-09-19.md` / `-fixes-2026-09-19.md`。本轮对象是
自提交 17d22f1b 以来新加入 `_posts` 的 **91 篇未跟踪帖**，以及全站的两项签名筛查。
截至本报告完成时只审计，未修改任何帖子。后续修订状态见本文末记录及
[2026-09-26 边界与排版复核](translation-integrity-audit-2026-09-26.md)。

工具（本轮新写，已入库）：

- `tools/audit_source_fidelity.py` —— 逐段把 `original` 对回它自己声称的来源
  （本地页面副本 / `data/cache_scan` 转写 / 网络抓取，缓存在 `data/cache_audit/`），
  按字符 6-gram 覆盖率判定。`--untracked` 一次跑完所有未跟踪帖。
- `tools/audit_translation_padding.py` —— 找"译文比原文说得多"的段：膨胀率
  （忠实的日→中一般 ≤1.0）＋夸张词表。全 81 篇的总体膨胀中位数是 1.01，所以排名靠前的是真异常。

## 一句话结论

新入库的 91 篇分成两半，两半各有一种缺陷：

- **50 篇官网帖（corporate.pokemon.co.jp 44 + recruit 4 + 2）原文是真的**——逐段 100%
  能在现网页面上找到。问题在译文：14 篇正文注水，36 篇在译文里塞进了原文没有的
  【寄寓解读】小作文。
- **41 篇杂志／视频访谈里，17 篇已证实"原文"不是那本杂志上的字**，2 篇属逐句改写，5 篇只有标题是编的，9 篇无法核对。来源条目大多真实存在
  （archive.org 上的扫描、还活着的网页），但帖子里的日文是对着真访谈改写的，不是抄下来的。

## 一、结构性损坏（12 篇，先于内容）

只有开头的 `---`、没有结束符，Jekyll 无法当 front matter 解析（和 09-19 那批同一缺陷，
这次是 09-22 生成的，CRLF）。**这 12 篇正好全是引用杂志扫描的那批**：

`1997-11-27-spaceworld` / `2003-02-21-nintendodream-084` / `2004-03-21-nintendodream-108` /
`2005-07-15-corocoro` / `2009-05-15-nintendoaccion-199` / `2010-09-16-famitsu-1137` /
`2010-09-23-famitsu-1138` / `2012-07-19-famitsu-1233` / `2012-07-21-nintendodream-221` /
`2012-08-21-nintendodream-222` / `2013-09-21-nintendodream-235` / `2018-05-02-yomiuri`

其中 `2009-05-15-nintendoaccion-199` 还有 YAML 语法错误：第 69 行
`original: Seamos honestos: con DP…` 未加引号，冒号把映射打断。

## 二、原文核对（逐段对来源）

### P1 决定性：原文不是来源上的字

来源真实存在且被完整读取，但帖子里的段落对不上。日文扫描用 `qwen3.8-max`
逐页重转写（IA 自带的日文 OCR 基本是乱码，不能作为判据；转写缓存在 `%TEMP%/iavlm`）。

| 帖子 | 来源与读取方式 | 命中 |
| --- | --- | ---: |
| `2004-03-21-nintendodream-108`（FRLG） | IA 扫描全 10 页 VLM 转写（20,081 字） | 0/11 |
| `2012-08-21-nintendodream-222`（PWT） | 全 9 页（18,701 字） | 0/7 |
| `2013-09-21-nintendodream-235`（X·Y 妖精属性） | 全 6 页（13,942 字） | 0/8 |
| `2012-07-21-nintendodream-221` | 全 9 页（13,014 字） | 3/12 |
| `2005-07-15-corocoro`（DP 特报） | 全 2 页（2,283 字） | 0/7 |
| `2011-01-20-otonafamily` | 全 2 页（3,699 字） | 0/8 |
| `2012-07-19-famitsu-1233` | 全 3 页（4,003 字） | 0/7 |
| `2011-01-06-davinci` | 全 3 页（6,972 字） | 0/7 |
| `2010-12-24-nintendo-sp-kiritani`（女子大生が訊く） | Wayback 全 7 页（38,702 字） | 1/13 |
| `2014-08-22-gameatsumaru`（niconico） | Wayback 快照（8,683 假名） | 0/15 |
| `2010-09-13-weekly-ascii` | Wayback 快照（5,984 假名） | 9/21 |
| `2010-12-20-otonafami-sugimori` | atwiki 现网页（4,967 假名） | 0/10 |
| `2010-11-20-nintendodream-201-sugimori` | atwiki 现网页 | 3/13 |
| `2011-01-06-famitsu-1153` | atwiki 现网页（7,463 假名） | 7/14 |
| `2018-05-02-yomiuri` | Wayback 快照（4,502 假名） | 0/9 |
| `2003-02-21-nintendodream-084`（R·S） | IA 条目 6 张 PNG 全部 VLM 转写 | 0/9 |
| `1997-11-27-spaceworld` | 见下（来源是英文页） | 0/9 |

`2003-02-21-nintendodream-084` 的 item 8 里写着"洗**练**された"——练 是简体，日文作 練，
又一处生成痕迹（这个字不在第四节筛查的字集里，应补）。

**改写程度较轻的两篇**（真访谈、逐句改写但未见凭空添事，缺的段多在 cov 0.48–0.54，
属同义改写而非虚构），修复时可只做回改而不必重建：

| 帖子 | 来源 | 命中 |
| --- | --- | ---: |
| `2010-09-16-famitsu-1137` | IA 扫描全 3 页 VLM 转写（4,645 字） | 7/11 |
| `2010-09-23-famitsu-1138` | 全 3 页（4,758 字） | 4/11 |

**这批的共同手法不是凭空编造，而是"改写真访谈"**，三个已核实的实例：

1. `2004-03-21-nintendodream-108`。真页（增田）：岩田社长与石原社长谈话时
   "ジャジャジャーン！って「ワイヤレスアダプタ」を出されて、「やらない？」って"，
   岩田的要求是"移植ということを思わせない、新しいものを入れて欲しい"，而
   **同捆发售是增田自己提的**（"どうせやるなら同梱で出したいという話をしたんです"）。
   帖子把它合成一句伪引言："岩田社長から『移植という形にするのではなく、ワイヤレスアダプタを付けて出そう』と言われたんです"——决定权被移给了岩田。
2. `2010-12-24-nintendo-sp-kiritani`。真页：桐谷问"フシギバナって、何なんですか？（笑）"，
   杉森答"あれはカエルみたいなものです……モチーフはカエル"。帖子改写成问句
   "足の形とか座り方がカエルっぽく見えて…"、答句"ガマ（ヒキガエル）がモチーフ……
   オタマジャクシの名残"——蟾蜍、蝌蚪都是添的；还有"ミジュマルは開発初期に「クルマル」と
   呼ばれていた"，全 7 页 0 命中。
3. `2000-07-01-nintendo-power-134`（英文刊，IA 英文 OCR 可靠）。真页：石原说
   "Gold and Silver aren't just colors, they're also real, material things. Precious things."；
   增田答"Approximately 20 people… We started three years ago"。帖子把"Precious things."
   换成两句自撰，把增田的人数／工期答案改成"about three and a half years"并挂到石原名下，
   还把森本 2009 年那段"删掉调试工具腾出约 300 字节塞进梦幻"整段安到这期 NP 上（原刊无此内容）。

`1997-11-27-spaceworld` 是另一种：它引用的 IA 条目是 **GlitterBerri 英文翻译页的 PDF**
（Wayback 抓的 glitterberri.com），整份没有日文，帖子却给出 9 段日文"原文"。

### P2 只有标题是编的（正文可信）

正文逐段能对上，缺的只是版面上没有的章节标题（`第N章：…――…` / `序章：` / `巻頭：` 体例）：

- `2000-07-01-interview-nom-gold-silver-gamefreak`（已提交）：34/39，5 个标题
- `2010-03-31-interview-pokemon-com-hgss-six-gamefreak-masters`：9/11，2 个标题
- `2010-11-20-interview-steinberg-gamefreak-sound-cubase`（已提交）：28/32
- `2017-09-05-interview-gigazine-gamefreak-sketches-masuda`（已提交）：27/34
- `2016-05-12-interview-inside-pokken-tournament-developers`（已提交）：54/102（可能还有分页未抓全）

### P3 无法核对（9 篇）

- 纸刊无扫描：`2005-08-18-continue-vol23`（标 `manual-verified`）、
  `2017-06-10-cgworld-2017-07`、`2010-02-20` 三篇 ndream-2010-04（09-19 已列，仍未核）
- 来源是视频，文本无从取得：6 篇 YouTube 来源（`2015-11-03-nikkei`、
  `2018-09-21-rock-on`、`2019-02-15-mew-secret-origin`、`2019-10-09`/`2019-10-18` 两篇
  Game Informer、`2019-10-18-celebi`）。其中三篇的"原文"是日文，但 Game Informer 的视频是英语访谈。
- `2009-05-17-g4tv`：原站与 Wayback 都没有存档

## 三、译文质量（原文已验真的 50 篇）

### P1 译文里塞进原文没有的内容

**36 篇**在招式说明段的 `translation` 里附了一整段【寄寓解读】小作文。原文是游戏内招式描述
（来源页确实有这段日文），译文先把它扩写 3–8 倍，再接一段原文完全没有的"寓意阐发"。
已提交的帖子里 **0 篇**有这种写法，是这批新引入的。膨胀倍数示例：

- `topic-35`：`なかよくする…相手の攻撃をさげる` → 8.1×（"以毫无防备的真诚微笑与对手握手言和…彻底融化对方的防备与戾气"＋【寄寓解读】）
- `topic-38`：`めざめるパワー` 8.8×；`topic-45`：`へんしん` 8.1×；`topic-17`：`プレゼント` 7.0×

### P2 正文注水（14 篇正文膨胀中位数 >1.15）

抽检出的加料都是"原文没有的具体事实"：

- `topic-48`：原文"この反響を受け、担当者は「考えることそのものの楽しさを感じてもらえたらうれしい」と笑顔を見せました。"
  → 译文自撰"家长们感激地发现孩子不再沉溺于毫无营养的短视频碎片，而是每天主动拉着父母一起围坐在平板前为一个几何解法热烈争论"（3.1×）
- `topic-18`：原文只说两种形态的特征在茶碗上复刻 → 译文加"购买到杰作形态的幸运顾客，能够在碗底发现象征真正名家古瓷的专属朱印"
- `topic-17`：原文"行政とも慎重に協議を重ねながら" → 译文加"石川县政府及前线救灾指挥部"
- `topic-13`：`匠人们…倾注了近乎着魔的精益求精`；`topic-02`：`系列巨作`、`盛大`

排名最高的 14 篇：topic-48 / 23 / 45 / 35 / 38 / 13 / 08 / 17 / 50 / 18 / 07 / 02 / 25 /
`2015-11-03-nikkei`。

## 四、全站签名筛查（不限新帖）

1. **日文原文里混进简体字** = 该段日文是生成的。全站命中 12 篇 13 处，其中已提交的有：
   `2017-06-01-gamefreak-rnd-ta-taya-kk`（飛**跃**的）、`2008-08-13-shudo-ch156`（声**优**，
   同段内 優/优 混用）、`2020-12-21-nikkei-ishihara`（伊**势**湾）、
   `2020-12-25-corocoro-okazaki`（完**结**）、`2000-07-01-nom-gold-silver`（**关**都，在编造的
   章节标题里）、`2002-11-01-nom-2002-ruby-sapphire-staff-messages`（原文栏写着"增田顺一："）、
   `2010-11-01-nintendo-joshi-daisei`（两处原文栏里是中文）、`2026-08-29-continue-vol32`
   （"魅力的**线上**んだけど"，疑 OCR/生成损坏）。
2. **`第N章：…――…` 体例的章节标题**：7 篇共 31 个（见 P2 与 P1 列表）。
3. `■` 前缀本身不是签名（dengeki、4gamer、oricon、首藤专栏原文都在用）；
   `■` ＋ `――` 副标题的组合才与生成帖重合。

## 建议处理顺序

1. 12 篇结构损坏＋1 篇 YAML 错误：先补 `---`、给冒号加引号，否则内容审不了也渲染不了。
2. 上面 P1 那 16 篇"原文不是来源上的字"：扫描页的 VLM 转写已在手
   （`%TEMP%/iavlm`，如要留档应移入 `data/cache_scan/`），可以照 09-19 那批的办法按真页重建；
   `1997-11-27-spaceworld` 没有日文来源，只能按 GlitterBerri 的英文重做或不收。
3. 36 篇【寄寓解读】：属于译文里的自撰内容，建议整体删除或移出 `translation` 字段。
4. 14 篇正文注水：按原文逐段收回。
5. P2 那 5 篇（含 4 篇已提交）：只删编造的章节标题即可，正文不动。
6. P3 那 9 篇：纸刊要扫描、视频要听写，或降级为 draft 并注明"原文无法核对"。

---

# 处理记录（2026-09-25 同日）

## 一、12 篇结构损坏已修

补上缺失的结束 `---`；`2009-05-15-nintendoaccion-199` 里那条被冒号打断的
`original: Seamos honestos: …` 加了引号。全站 1172 篇现在 0 处结构问题
（脚本：`scratchpad/fix_structure.py` 的逻辑，只动分隔符与该行引号，不改内容）。

## 二、17 篇按真页重建完毕

**11 篇杂志扫描**（来源：archive.org 条目）走仓库既有的扫描流水线。
`design/scan_sets_2026-09.json` 新登记 11 套 `ia-*`，页图暂存到 `E:/Pokeamice/scan/ia-*_prepared`，
qwen3.8-max 的逐页转写归档进 `data/cache_scan/ia-*/`（原始记录），再 `build` 出帖：

| 新帖 | 段数 | 逐段对页面转写 |
| --- | ---: | ---: |
| `2003-02-21-scan-ndream-084-ruby-sapphire-interview` | 382 | 305/305 |
| `2004-03-21-scan-ndream-108-frlg-developer-interview` | 393 | 313/313 |
| `2005-07-15-scan-corocoro-200508-diamond-pearl-scoop` | 53 | 47/47 |
| `2010-09-16-scan-famitsu-1137-bw-launch-interview` | 47 | 42/42 |
| `2010-09-23-scan-famitsu-1138-bw-secrets-interview` | 50 | 43/43 |
| `2011-01-06-scan-davinci-201102-masuda-comment` | 73 | 63/63 |
| `2011-01-20-scan-otonafamily-201103-masuda-bw-adults` | 40 | 31/31 |
| `2012-07-19-scan-famitsu-1233-b2w2-interview` | 44 | 40/40 |
| `2012-07-21-scan-ndream-221-b2w2-developer-interview` | 142 | 129/129 |
| `2012-08-21-scan-ndream-222-b2w2-pwt-pokewood` | 388 | 280/280 |
| `2013-09-21-scan-ndream-235-xy-developer-interview` | 242 | 222/222 |

原来的帖子每篇只有 7–12 段"原文"，真页上是整篇访谈加图注，所以段数差这么多。
**页图没有转存**：这些扫描是第三方上传到 archive.org 的，转存到本站 CDN 属于再分发，
需要你拍板。所以帖子内不嵌页图，front matter 里 `scan_pages` 记下条目与页号，
`review_scope` 指向来源条目。要改成本站托管，只需一条 `import-scan-set.py upload <slug>`。

**4 篇网页来源**走 `tools/import-web.py`：

- `2010-09-13-interview-weekly-ascii-masuda-bw-secrets`（原地重导）71/71
- `2018-05-02-interview-pokemon-official-pikachu-tanjou-hiwa` 110/110（2 页）
  —— 原帖把出处写成"读卖新闻朝刊 深层断面"，真来源是**株式会社ポケモン官网「ピカチュウ誕生秘話」**，出处已改正
- `2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw` 200/201（7 页）
- `2014-08-22-interview-gameatsumaru-masuda-indie-gamefreak-origins`（原地重导）124/124

顺带修了 `import-web.py` 的一个真 bug：Wayback 快照开头是工具栏自己的 UTF-8 `<meta>`，
于是 Shift_JIS 正文被按 UTF-8 解码成乱码（nintendo.co.jp 那批）。现在把候选编码都解一遍、
取替换字符最少的，并支持目标声明 `encoding`。另外 `audit_source_fidelity.py` 认 `source_pages`，
否则多页访谈的第 2 页起会被误判成"不在来源里"。

**3 篇只有粉丝 wiki 摘录**（`w.atwiki.jp/bwhuman2`，页面自注"※ほとんど部分的な抜粋"，
文本源自 2ch 帖，期号与帖子原先声称的对不上）：新写 `tools/import_atwiki_excerpts.py`，
按 wiki 实际分节重建为**摘录帖**，`archive_type: interview_excerpt`、
`source_kind: fan_wiki_excerpt`、`published: draft`，刊名照 wiki 所记并注明本站未核原刊：

- `2011-01-06-interview-famitsu-1153-ota-ohmori-c-gear` 49/49
- `2010-11-20-interview-nintendodream-201-sugimori-bw-characters` 104/104
- `2010-12-20-interview-otonafami-sugimori-starters-victini` 31/31

**1 篇只有英译**：`1997-11-27-interview-spaceworld-…` 引用的是 GlitterBerri 英文页，
无日文来源。重建为 `1997-11-27-interview-glitterberri-spaceworld-pokemon2-en`
（`original_lang: en`，22/22），并注明"日文原文本站未取得，original 栏是英译，不应当作日文原文引用"。

被取代的 14 篇移入 `_drafts/retired-2026-09-25/`（另 5 篇是原地重导，旧文本已不存在）。

## 三、仍然未处理（截至 2026-09-25）

1. **3 篇 Nintendo Power（英文刊）**：`NP-134`（已证实改写＋错挂发言人＋拼入别处轶事）、
   `NP-241`、`NP-265`。它们不在上面 17 篇之列，IA 有英文 OCR 可据以重建。
2. **36 篇【寄寓解读】+ 14 篇正文注水**（原文为真、译文自撰），见前文第三节。
3. **6 篇视频来源 + 4 篇无扫描**：仍无法核对。
4. 第四节那 8 篇仍带简体字痕迹的已提交帖（`gamefreak-rnd-ta-taya-kk` 等）。

## 后续修订记录（截至 2026-09-27）

- 36 篇企业专题的“寄寓解读”已移出 translation，改放 comment 并标注为“本站解读”。
- topic-17、topic-18、topic-48 中有明确原文证据的事实增写已收回。其余 11 篇正文膨胀候选及招式说明的夸饰译文尚未逐条重校。
- 09-26 边界审计发现的污染、空标题译文、OCR 失真和段落格式问题，处理状态详见上方链接；该报告同时列出了仍待原刊对照的项目。
