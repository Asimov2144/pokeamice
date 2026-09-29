---
layout: guide
title: "文档站怎么用"
lead: "从找资料到读杂志扫描：这个站的主要入口、每种页面的读法，以及不点开就不知道的小功能。"
permalink: /guide/docs-site/
verified: 2026-09-29
chips:
  - label: 怎么找资料
    url: "#怎么找资料"
  - label: 读一篇访谈
    url: "#读一篇访谈"
  - label: 读一篇杂志扫描
    url: "#读一篇杂志扫描"
---
{%- comment -%}
The first guide of the 使用指南 topic. Written from the live site on 2026-09-29:
every label quoted here was read off docs.pokeamice.com that day, every screenshot
is of it (assets/img/guide/, listed in _data/guides.yml under shots). When a page
this guide describes changes, redo the section that mentions it - the sections
say which page they are about. How to write these pieces: _pages/guide/template.md.
{%- endcomment -%}

## 先看全貌

这里收的是宝可梦开发相关的**访谈、杂志扫描和官方博客**的中文存档，一千多条（2026 年 9 月）。每一条背后还连着**人物、作品和制作名单**：读到一个名字，就能顺着走到这个人参与过的所有资料。

下面这张图是全站的骨架，后面每一节讲其中一块。

<div class="guide-svg-wrap">
<svg class="guide-svg" viewBox="0 0 720 300" role="img" aria-label="全站结构：从首页、资料窗口和顶部的全文搜索进入，读到访谈翻译、杂志扫描和官方博客，再通过人名和作品名走向人物库、作品库与制作名单、时间线与关系图谱">
<defs><marker id="ov-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="g-arrow" d="M0,0 L10,5 L0,10 z"/></marker></defs>
<text class="g-text g-text--faint" x="12" y="16">入口</text><text class="g-text g-text--faint" x="273" y="16">资料</text><text class="g-text g-text--faint" x="534" y="16">索引与全景</text>
<rect class="g-node" style="fill:none" stroke-dasharray="5 4" x="4" y="24" width="190" height="264" rx="14"/>
<rect class="g-node" style="fill:none" stroke-dasharray="5 4" x="265" y="24" width="190" height="264" rx="14"/>
<rect class="g-node" style="fill:none" stroke-dasharray="5 4" x="526" y="24" width="190" height="264" rx="14"/>
<rect class="g-node g-node--accent" x="16" y="40" width="166" height="64" rx="12"/><text class="g-text" x="99" y="68" text-anchor="middle">首页</text><text class="g-text g-text--faint" x="99" y="88" text-anchor="middle">检索栏 · 专题图块 · 筛选</text>
<rect class="g-node" x="16" y="120" width="166" height="64" rx="12"/><text class="g-text" x="99" y="148" text-anchor="middle">资料窗口</text><text class="g-text g-text--faint" x="99" y="168" text-anchor="middle">动态流 · 今日一句</text>
<rect class="g-node" x="16" y="200" width="166" height="64" rx="12"/><text class="g-text" x="99" y="228" text-anchor="middle">全文搜索</text><text class="g-text g-text--faint" x="99" y="248" text-anchor="middle">顶部的放大镜</text>
<rect class="g-node g-node--accent" x="277" y="40" width="166" height="64" rx="12"/><text class="g-text" x="360" y="68" text-anchor="middle">访谈翻译</text><text class="g-text g-text--faint" x="360" y="88" text-anchor="middle">网页与杂志访谈的中译</text>
<rect class="g-node g-node--accent" x="277" y="120" width="166" height="64" rx="12"/><text class="g-text" x="360" y="148" text-anchor="middle">杂志扫描</text><text class="g-text g-text--faint" x="360" y="168" text-anchor="middle">页图与译文对照</text>
<rect class="g-node g-node--accent" x="277" y="200" width="166" height="64" rx="12"/><text class="g-text" x="360" y="228" text-anchor="middle">官方博客</text><text class="g-text g-text--faint" x="360" y="248" text-anchor="middle">部长专栏 · 员工博客</text>
<rect class="g-node" x="538" y="40" width="166" height="64" rx="12"/><text class="g-text" x="621" y="68" text-anchor="middle">人物库</text><text class="g-text g-text--faint" x="621" y="88" text-anchor="middle">谁谈了什么、署名了什么</text>
<rect class="g-node" x="538" y="120" width="166" height="64" rx="12"/><text class="g-text" x="621" y="148" text-anchor="middle">作品库 · 制作名单</text><text class="g-text g-text--faint" x="621" y="168" text-anchor="middle">每部游戏的署名</text>
<rect class="g-node" x="538" y="200" width="166" height="64" rx="12"/><text class="g-text" x="621" y="228" text-anchor="middle">时间线 · 关系图谱</text><text class="g-text g-text--faint" x="621" y="248" text-anchor="middle">按年份、按同场</text>
<path class="g-line" d="M196 156 L263 156" marker-end="url(#ov-ah)"/>
<path class="g-line" d="M457 140 L524 140" marker-end="url(#ov-ah)"/><path class="g-line" d="M524 172 L457 172" marker-end="url(#ov-ah)"/>
</svg>
</div>

> 本文按 2026 年 9 月 29 日的线上站点写成，截图和页面上的文字也都取自那天。站点在持续更新，数字会变，入口和读法一般不变。
{: .note}

## 怎么找资料

首页就是目录：默认列出综合推荐的前 36 条，全部资料都在这一页里，用下面四种办法缩小范围。**它们可以叠加**：先选年份再选人物，就只剩那一年里这个人的资料。

1. **检索栏**：在首页最上方输入人名、作品名或关键词。不用点「检索」，下面的卡片边输边筛。
2. **专题图块**：检索栏下面一排带图的块，横着滑还有更多。点「社长问」这类，会把词填进检索栏并筛选；点「部长专栏」「人物库」这类，直接进入它自己的页面。
3. **筛选**：左边的下拉框可以选内容类型、人物、作品、年份、来源，也可以改排序（综合推荐、时间新到旧、时间旧到新、标题）。点「清空」还原。
4. **维度面板**：右边按年份、人物、作品、类型列出数量，点一项就加上一个条件；再点一次取消。
{: .steps}

<div class="guide-tabs" data-guide-tabs>
<div class="guide-tabs__list"><button type="button">桌面</button><button type="button">手机</button></div>
<div class="guide-tabs__panel" markdown="1">

{% include guide/shot.html src="/assets/img/guide/home-d.webp" alt="文档站首页（桌面）：顶部是检索栏，下面是一排专题图块，左侧是筛选和个人卡片，中间是文章卡片，右侧是按年份和人物的维度面板" pins="36.3;29;检索栏：输入就筛，不用按检索|43.7;37.5;专题图块：点一块进入这个专题|10.5;70;筛选：类型、人物、作品、年份、来源和排序|35;58;卡片：类型标签、来源、标题、人物和日期。「初译待校」表示译文还没有人工校对|87.5;24.1;维度面板：按年份、人物、作品、类型，点一项加一个条件" caption="首页，宽度 1280。" %}

</div>
<div class="guide-tabs__panel" markdown="1">

手机上右边的维度面板变成一行行的条件按钮，排在「筛选」下面；顶部的标签可以跳到首页的各个分区。

{% include guide/shot.html device="phone" src="/assets/img/guide/home-m.webp" alt="文档站首页（手机）：顶部一排分区标签，检索栏，横向滑动的专题图块，折叠成一栏的筛选，以及类型、年份、人物、作品的条件按钮" pins="10;15.2;顶部标签：总览、资料检索、近期发布、文档索引、访谈翻译，点一个跳到对应分区|75;19.7;检索栏：和桌面一样，输入就筛|60.3;29.9;专题图块：左右滑动|25.6;52.1;筛选：手机上收成一栏|94;57.3;条件按钮：类型、年份、人物、作品，点一个加一个条件" caption="首页，宽度 390。" %}

</div>
</div>

{% include guide/flow.html title="找资料" steps="首页>检索栏/专题图块/筛选/维度面板>缩小后的列表>一篇资料" %}

> 首页上的「初译待校」表示这一篇的译文还没经过人工校对，遇到疑问以原文为准。
{: .warn}

站里还有两个单独的搜索：

- **顶部的放大镜**：点开是一个搜索浮层，输入词，下面直接列出命中的页面，每条是标题加一小段摘录。它搜的是正文，人物页这类页面也在里面；想找「某个词出现在哪里」用它。
- **筛选页**（`/search/`）：筛选栏和首页一样，用来按类型、人物、作品、年份缩小范围。地址可以带关键词，比如 `https://docs.pokeamice.com/search/?q=黑白`，方便把一次检索的结果发给别人。

## 读一篇访谈

「访谈翻译」类的文章是中文译文加原文出处。同一批文章会随原刊年代换版式：2011 年的访谈像 2011 年的网页，2019 年的像 2019 年的。

1. 打开一篇访谈。页顶的**面包屑**（首页 › 访谈翻译 › 2011 › 1UP.com › 标题）每一级都能点，回到同分类、同年份或同来源的列表。
2. 点右上角的「译文 ⊙」，展开**阅读工具**，按钮上写的是当前的阅读方式。
3. 想对照原文，选「双栏对照」；想按原刊年代读，保持「年代主题」；夜里读选「深色」；想只留正文，选「专注模式」。
4. 头部的**人名**可以悬停出卡片，见下面「认识人物与作品」；「原文 ↗」跳到原文出处。
5. 读到文末，看「本篇提到」和「同类资料」。
{: .steps}

{% include guide/shot.html src="/assets/img/guide/reader-tools-d.webp" alt="一篇访谈的页头：左上角是面包屑，右上角展开的阅读工具里有译文、双栏对照、原文，年代主题、深色、纯净，以及专注模式；标题下面是人物署名和原文按钮" pins="50.2;10;面包屑：每一级都能点|78.5;10;阅读工具：点开展开，按钮上是当前的阅读方式|74.6;15.8;译文、双栏对照、原文|74.6;20.3;年代主题、深色、纯净|66.4;24.9;专注模式|46.5;38.8;原文 ↗：跳到原文出处" caption="阅读工具展开后。" %}

| 按钮 | 作用 |
|---|---|
| 译文 | 只读中文译文 |
| 双栏对照 | 原文与译文左右并排，逐段对照 |
| 原文 | 只读原文 |
| 年代主题 | 按原刊年代换版式，例如 2010–2012 年是「互联时代」 |
| 深色 | 深色纸面，夜里读 |
| 纯净 | 不带年代装饰的白底 |
| 专注模式 | 隐去站点导航与边栏，只留正文 |
| 竖排原文 | 纵排区域的原文按原刊竖排（只在有竖排原文的扫描里出现） |
{: .matrix}

**文末的「本篇提到」**是这一篇讲了什么的索引，比正文更适合先扫一眼：

{% include guide/shot.html src="/assets/img/guide/lore-d.webp" alt="访谈文末的「本篇提到」：几条带段号的要点，人物、作品、宝可梦、地点四行名字，两条指向其他文章的关联，下面是「同类资料」的卡片" pins="50.8;9;带 § 的要点：点段号跳到正文里的那一段|66.4;19.7;人、作品、宝可梦、地点：蓝色的有自己的页面，可以点进去|46.9;31.8;「同一件事的另一种说法」：指向另一篇讲同一件事的文章，并写明为什么相关|58.6;84;同类资料：同一个人物、同一部作品的其他文章" caption="「本篇提到」和「同类资料」。" %}

## 读一篇杂志扫描

「扫描翻译」类的文章是杂志的**页图**加上逐页的译文，页和文互相对得上：读到哪一段，页图上就框出它在哪里。

1. 打开一篇扫描，页码条在标题下面，写着「共 N 页」。
2. 选**页码**、页图上方的 ‹ ›，或者键盘 <kbd>←</kbd> <kbd>→</kbd> 翻页。
3. 滚动右边的文字，左边的页图会**自己翻到当前读的那一页**；反过来，你翻页时，文字也会滚到那一页。
4. 鼠标移到一段文字上，页图上会出现**橙色的框**，标出它在页上的位置；点页图上的框，文字栏就滚到那一段并闪一下。
5. 页图上方的 − ○ + 缩放（○ 还原），可以拖动平移；「整页 ↗」打开大图。
6. 点标题下的「档案」，看这份扫描是怎么做出来的。
{: .steps}

<div class="guide-svg-wrap">
<svg class="guide-svg" viewBox="0 0 640 220" role="img" aria-label="扫描阅读器里页图和文字栏互相跟随：翻页时文字栏滚到那一页，滚动文字时页图翻到当前页；鼠标移到段落上，页上对应区域亮起橙框，点页上的框，文字栏滚到那一段">
<defs><marker id="sc-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="g-arrow" d="M0,0 L10,5 L0,10 z"/></marker></defs>
<rect class="g-node g-node--accent" x="10" y="15" width="140" height="56" rx="12"/><text class="g-text" x="80" y="48" text-anchor="middle">页图翻页</text>
<rect class="g-node g-node--accent" x="490" y="15" width="140" height="56" rx="12"/><text class="g-text" x="560" y="48" text-anchor="middle">文字栏滚动</text>
<path class="g-line" d="M152 32 L488 32" marker-end="url(#sc-ah)"/><text class="g-text g-text--faint" x="320" y="24" text-anchor="middle">翻页时，文字栏滚到那一页</text>
<path class="g-line" d="M488 56 L152 56" marker-end="url(#sc-ah)"/><text class="g-text g-text--faint" x="320" y="76" text-anchor="middle">滚动时，页图翻到当前那一页</text>
<rect class="g-node" x="10" y="135" width="140" height="56" rx="12"/><text class="g-text" x="80" y="168" text-anchor="middle">一段文字</text>
<rect class="g-node" x="490" y="135" width="140" height="56" rx="12"/><text class="g-text" x="560" y="168" text-anchor="middle">页上的橙框</text>
<path class="g-line" d="M152 152 L488 152" marker-end="url(#sc-ah)"/><text class="g-text g-text--faint" x="320" y="144" text-anchor="middle">鼠标移上去，页上亮起对应区域</text>
<path class="g-line" d="M488 176 L152 176" marker-end="url(#sc-ah)"/><text class="g-text g-text--faint" x="320" y="196" text-anchor="middle">点页上的框，文字栏滚到那一段并闪一下</text>
</svg>
</div>

<div class="guide-tabs" data-guide-tabs>
<div class="guide-tabs__list"><button type="button">桌面</button><button type="button">手机</button></div>
<div class="guide-tabs__panel" markdown="1">

{% include guide/shot.html src="/assets/img/guide/scan-d.webp" alt="扫描阅读器（桌面）：上方是「阅读」「档案」和页码条，左边是杂志第 3 页的页图，其中标题区域被橙色框圈出，右边是逐页的译文文字栏" pins="6;8.5;「阅读」「档案」：切换视图|27;8.5;页码条：点数字翻到那一页|8;15;‹ ›：上一页、下一页|40;15;− ○ +：缩放，○ 还原。「整页 ↗」打开大图|7;32;橙色框：鼠标停着的这一段在页上的位置|54.7;77;文字栏：译文按页排列，滚动时页图跟着翻" caption="扫描阅读器，宽度 1280。" %}

</div>
<div class="guide-tabs__panel" markdown="1">

手机上页图缩成右边的一小条，点它就全屏看这一页；页码条自动换行。

{% include guide/shot.html device="phone" src="/assets/img/guide/scan-m.webp" alt="扫描阅读器（手机）：上方是「阅读」「档案」和换行的页码条，下面一行是翻页按钮，右边是当前页的小缩略图，再往下是逐页的译文" pins="19;4;「阅读」「档案」|36;9;页码条：一行放不下会换行|90;23;页图缩成小条，点它全屏看|24;23;‹ ›：上一页、下一页" caption="扫描阅读器，宽度 390。" %}

</div>
</div>

> 页图和文字的对应框，目前只有做过区域定位的扫描才有（先做的是《ダ・ヴィンチ》和 Nintendo DREAM 2011 年 1 月号）。其余的扫描仍然有页图、页码和逐页译文，只是没有橙框。
{: .note}

> 「档案」里能看到这份扫描的处理进度和校对状态。多数扫描写着「整页由视觉模型一次转写、DeepSeek 初译；未经人工逐字校对，读者请以页图为准」——读到有疑问的地方，就以页图为准。
{: .warn}

## 认识人物与作品

任何页面里的**人名**都是链接。把鼠标停在人名上，出现一张小卡片；点进去是这个人的页面。

1. 把鼠标停在人名上：正文里的、页头署名里的、文末「本篇提到」里的都可以。
2. 卡片上是头像、职务、他在站里的分量（访谈几篇、发言几篇、署名几作），以及简介的头一句。
3. 点人名，进入他的页面，看他的年份分布、参与过的作品、全部条目，以及历作署名。
{: .steps}

{% include guide/shot.html src="/assets/img/guide/person-card-d.webp" alt="访谈页头的人物署名，鼠标停在「井部真那」上，出现的卡片里有头像、姓名、职务、访谈和署名的篇数、分类标签和简介" pins="27.7;30.8;停在人名上|15.6;12.4;头像、姓名、职务|34.8;13.4;访谈、发言、署名的数量|41.8;21.1;简介的头一句，点人名看全部" caption="人物卡片。触屏没有悬停，点人名直接进入他的页面。" %}

**人物库**（`/people/`）把所有人排在一起，按站内收录篇数从多到少：

{% include guide/shot.html src="/assets/img/guide/people-d.webp" alt="人物库：一排人物卡片，每张有头像、中文名、罗马字名、访谈篇数和年份跨度、制作名单署名作数和年份跨度" pins="11.7;49.4;一张卡片是一个人，点开看他的页面|15;64;「615 篇 · 1996–2023」：站内收录了他的多少篇，以及最早和最晚的年份|15;71.5;「署名 28 作」：他在多少部游戏的制作名单里署名过" caption="人物库，宽度 1280。" %}

**作品库**（`/works/`）按作品排列：每张卡片写站内收录了多少条相关资料，有制作名单的游戏另外标出署名人数，点「名单」看整份 credits。

**制作名单**（`/credits/`）每部游戏一页，除了名单本身，页面上部还有一块「团队画像」（Development Atlas），从名单里读出团队规模、成员从哪些作品来、之后去了哪些作品：

{% include guide/shot.html src="/assets/img/guide/credits-bw-d.webp" alt="《宝可梦 黑·白》的制作名单页：顶部是作品名，下面是「团队画像」，有数据等级标签、团队规模的数字块、来源与去向的柱状图和「怎么读」说明" pins="43.8;49.6;数据等级：这份名单能做多细的分析，一眼看出来|23.4;60.9;团队规模：署名数、人数、参与者、组长以上|59.4;60.9;来源与去向：这一作的参与者上一次署名在哪些作品|74.4;65.1;范围和视图可以切换：核心作、含外传，最近一次、任一前作|87.5;46.9;「怎么读」：读这块之前先看一眼" caption="一部游戏的制作名单页（《宝可梦 黑·白》）。" %}

> 「团队画像」是把名单直接显示的现象读出来，**不是官方组织架构**：名单里没出现不等于没参与，之后没有署名也不等于离职。页面右侧的「怎么读」写得更细。
{: .warn}

## 官方博客

站里存了三个 GAME FREAK 的官方博客：**部长专栏**（増田順一）、**员工博客**《晴れたり時々曇ったり》和**杉森建博客**。入口在首页专题图块的头三块。它们保留原站的版式，而不是套站点自己的样式。

1. 从首页专题图块点「员工博客」。页顶是仿原站的导航：「ORIGINAL ↗」通向 Web Archive 里的原站快照，「REPORT」是员工博客的内容分析，「MASUDA」和「ART」通向部长专栏和杉森建博客，「ABOUT」跳到这个博客的介绍。
2. 「阅读语言」在「中文译文」和「日文原文」之间切换。
3. 每篇有日期、「書いた人」署名（作者的头像和昵称）和分类。
4. 右栏的「历代页头」是 2013 年以前的旧版页头，可以看博客的样子怎么变。
{: .steps}

{% include guide/shot.html src="/assets/img/guide/staff-d.webp" alt="员工博客页：顶部是仿原站的页头和导航，下面是阅读语言的切换，然后是一篇日志，有日期、书いた人署名和分类，右栏是关于和历代页头" pins="54.7;28.8;原站式的页头和导航|43.8;66.6;阅读语言：中文译文、日文原文|40.6;83;书いた人：这一篇的作者|78.5;79.5;历代页头：2013 年以前的旧版页头" caption="员工博客，宽度 1280。" %}

## 看全景

前面都是读一篇；这一节是把整批资料摆在一起看。

- **资料时间线**（`/timeline/`）：按年份汇总，每一年一张卡，写着当年有多少条资料，点进去看那一年。
- **关系图谱**（`/resource-graph/`）：把每篇资料里同时出现过的人连起来。
- **全景数据分析**（`/analytics/`）和**员工博客内容分析**（`/keys/gamefreak-staff-analysis/`）：对整批资料和对员工博客的统计报告。

关系图谱的读法：**两个人在同一篇资料里出现过，之间就有一条线，线越粗同场的篇数越多**；圆点越大出现的篇数越多；颜色相同的是同一个群落。

1. 用「至少同场」和「范围」调整要看多密的图：同场篇数越高越精简。
2. 在「找人」里输入姓名，图会定位到这个人。
3. 点一个人，看他的同场者、谈过的作品和活跃年份。
4. 滚轮缩放、拖动平移；「全图」回到整体。
5. 上方还有「人物 × 作品」「年代脉络」「关系索引」几个视图，「怎么算的」说明了统计方法。
{: .steps}

{% include guide/shot.html src="/assets/img/guide/graph-d.webp" alt="关系图谱页：上方是人物、同场关系、作品、资料的数字，一排视图标签，「至少同场」「范围」「找人」三个控件，下面是人物网络图，右边是「怎么看」说明" pins="46.9;59.4;视图：人物网络、人物 × 作品、年代脉络、关系索引、怎么算的|61.7;66;控件：「至少同场」「范围」决定图里画多少，「找人」输入姓名定位，「全图」还原|35;86;人物网络：圆点大小是篇数，线的粗细是同场篇数|84.4;74.8;「怎么看」：读图的说明" caption="关系图谱，宽度 1280。" %}

## 资料窗口和今日一句

首页管找资料，**资料窗口**（`/keys/`）管看热闹：它是一条动态流，按时间列出哪天进了哪些资料、站点做了什么，还夹着「今日一句」「历史上的今天」「人物聚焦」几种每天变的内容。

{% include guide/shot.html src="/assets/img/guide/keys-d.webp" alt="资料窗口页：顶部是全部、新收录、站点动态、今日一句、历史上的今天、人物聚焦、专题几个筛选标签，中间是一条站点动态，右侧是专题图块墙" pins="46.1;36;筛选标签：只看某一种动态|46.9;43.1;一条动态：站点做了什么，或者哪几篇新收录|68;42.3;专题：所有专题图块摆成一面墙" caption="资料窗口，宽度 1280。" %}

**今日一句**平时是藏着的：在首页上停留约 75 秒没有滚动、点击或按键，或者隔了七天以上再回来，才会出现一张小卡，写着从访谈里摘的一句话。点「换一句」换一条，点 × 收起（这次访问里不再出现）。想一次看完，去 `/quotes/`。

## 小技巧

| 想做的事 | 怎么做 |
|---|---|
| 换成夜间配色 | 首页个人卡片右下角的「切换白天 / 黑夜」（月亮图标） |
| 只读正文，不要导航和边栏 | 访谈页的阅读工具里选「专注模式」 |
| 夜里读一篇文章 | 阅读工具里的「深色」：深色纸面 |
| 在扫描里快速翻页 | 键盘 <kbd>←</kbd> <kbd>→</kbd> |
| 把一次检索发给别人 | 用筛选页（`/search/`），地址后面带 `?q=关键词` |
| 一次去掉所有条件 | 首页筛选栏里的「清空」 |
{: .matrix}
