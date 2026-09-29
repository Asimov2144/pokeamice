---
layout: guide
title: "指南写作模板"
lead: "写一篇新指南要用到的全部版式：每一种都有效果和源码，复制改字即可。这一页本身也是用这些写的。"
permalink: /guide/template/
verified: 2026-09-29
search: false
sitemap: false
chips:
  - label: 新建一篇
    url: "#新建一篇"
  - label: 写作规范
    url: "#写作规范"
  - label: 上线前检查
    url: "#上线前检查"
---
{%- comment -%}
The living reference for writing a guide: each part shown as it renders and as
it is written. Unlisted on purpose (not in _data/guides.yml, no search, no
sitemap) - it is for the person writing, not the reader. When a component is
added or changed in _guide.scss / _includes/guide/, change it here in the same
commit.
{%- endcomment -%}

## 新建一篇

1. 在 `_data/guides.yml` 末尾加一条：`id`、`group`（这篇属于哪个站）、`title`、`summary`，`url` 留空，`status: planned`。侧栏和专题首页立刻会出现一张灰色的「编写中」。
2. 新建 `_pages/guide/<id>.md`，把下面的头部复制进去。
3. 写完、对着线上走通每一步之后，回到 `guides.yml`：填 `url`、`verified`，把 `status` 改成 `published`。侧栏、专题首页和上一篇 / 下一篇才会链到它。
{: .steps}

```text
---
layout: guide
title: "文档站怎么用"
lead: "一两句话：这篇讲什么、给谁看。"
permalink: /guide/docs-site/
verified: 2026-09-29
chips:
  - label: 从首页开始
    url: "/#overview"
---
```

> `search` 和 `sitemap` 不写就是默认打开。要藏起来的页面（像本页）才写 `search: false`、`sitemap: false`。
{: .note}

## 一篇的骨架

一篇指南按这个顺序，缺哪段就不写哪段，不要凑：

1. **开头**：`lead` 一两句话；需要时放 2–4 个快捷入口（`chips`）。
2. **总览图**：一张图讲清这个站有哪几个入口、彼此什么关系。用「流程」或手画 SVG。
3. **一节一个任务**：每节三段——这是什么，怎么用（编号步骤），实机（截图加编号圈）。
4. **相关阅读**：结尾放一排卡片，指向下一步该看的页面。

## 提示框

四种，只在读者可能踩坑时用，一节最多一个。用引用块加一个 class：

> 补充说明，不看也不影响操作。
{: .note}

> 更省事的做法或者小技巧。
{: .hint}

> 容易出错的地方：这一步做错了，后面看到的结果会不对。
{: .warn}

> 会丢数据或者不可撤销的操作。
{: .danger}

{% raw %}
```text
> 补充说明，不看也不影响操作。
{: .note}

> 更省事的做法。
{: .hint}

> 容易出错的地方。
{: .warn}

> 会丢数据或者不可撤销的操作。
{: .danger}
```
{% endraw %}

## 步骤

有先后的操作用编号步骤：有序列表后面加 `{: .steps}`。每步一个动作，动词开头，最多五步；某一步要展开，缩进四个空格接一段。

1. 打开首页，在顶部的搜索条里输入一个人名或作品名。
2. 按回车，或者点右边的「搜索」。

    结果按相关度排列，人名和作品名会排在前面。
3. 点开任意一条，进入文章。
{: .steps}

{% raw %}
```text
1. 打开首页，在顶部的搜索条里输入一个人名或作品名。
2. 按回车，或者点右边的「搜索」。

    结果按相关度排列，人名和作品名会排在前面。
3. 点开任意一条，进入文章。
{: .steps}
```
{% endraw %}

## 解说图

截图加编号圈，旁边逐条解说。图里只放干净的截图，圈是叠上去的：文案改了不用重拍，编号和解说也不会错位。鼠标移到解说上，图上对应的圈会放大。

{% include guide/shot.html src="/assets/img/guide/demo-shot.svg" alt="示例：一张画出来的首页线框，上方是搜索条，下面是一排专题图块，再下面是文章卡片，右侧是维度面板" pins="9;19;搜索条：输入人名、作品名或关键词|14;33;专题图块：点一块直接筛出这个专题|45;53;文章卡片：封面、标题和人物一眼可见|86;35;维度面板：按年份、人物、作品、类型收窄" caption="示例图，只用来演示写法；真实指南用线上站点的截图。" %}

{% raw %}
```text
{% include guide/shot.html
   src="/assets/img/guide/home-desktop.webp"
   alt="首页：上方是搜索条，下面是专题图块和文章卡片，右侧是维度面板"
   pins="9;19;搜索条：输入人名、作品名或关键词|14;33;专题图块：点一块直接筛出这个专题"
   caption="桌面宽度 1280。" %}
```
{% endraw %}

- `pins` 里每个圈是 `x;y;说明`，圈与圈之间用 `|`。x、y 是圈心在图上的百分比（宽、高各按 100 算）。说明里不能有 `;` 和 `|`。
- 一张图最多六个圈；再多就拆成两张。
- 手机截图加 `device="phone"`：图窄，解说排在它右边（窄屏自动叠到下面）。
- 图放在 `assets/img/guide/`，WebP，单张不超过 250 KB；`alt` 写图里有什么，不写「截图」。

{% include guide/shot.html device="phone" src="/assets/img/guide/demo-shot.svg" alt="示例：同一张线框图，用来演示手机截图的排法" pins="20;19;圈心的位置按百分比算，图的宽高变了圈也跟着走|60;53;手机截图窄，解说排在它右边" caption="phone 排法。" %}

## 流程

一行走完的流程用 `guide/flow`：步骤之间用 `>`；某一步有几条路可走，用 `/` 把它们写在一起。第一步是起点，最后一步是终点。

{% include guide/flow.html title="找资料" steps="首页>搜索条/专题图块/维度面板>结果列表>文章" %}

{% raw %}
```text
{% include guide/flow.html title="找资料"
   steps="首页>搜索条/专题图块/维度面板>结果列表>文章" %}
```
{% endraw %}

步骤文字里不要出现 `>` 和 `/`，用「或」代替。窄屏（700px 以下）自动变成从上到下。

### 手画 SVG

有回路、要分多行、要标线上文字的图，手画内联 SVG：加 `class="guide-svg"`，颜色用 `g-node`、`g-node--accent`、`g-line`、`g-arrow`、`g-text`、`g-text--faint` 这几个类，它们跟着站点的深浅色走；**不要写死颜色**。SVG 里不要有空行（会打断 Markdown 的 HTML 块）。外面包一层 `<div class="guide-svg-wrap">`：手机上图会保持约 600px 宽并可以横向滑动，字不会缩得看不清；`viewBox` 的宽度最好在 640–720 之间，字号 14 左右。

<div class="guide-svg-wrap">
<svg class="guide-svg" viewBox="0 0 640 150" role="img" aria-label="示例：舞台翻页和文字栏滚动互相跟随">
<defs><marker id="g-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="g-arrow" d="M0,0 L10,5 L0,10 z"/></marker></defs>
<rect class="g-node g-node--accent" x="10" y="45" width="130" height="50" rx="12"/><text class="g-text" x="75" y="75" text-anchor="middle">舞台翻页</text>
<rect class="g-node g-node--accent" x="250" y="45" width="130" height="50" rx="12"/><text class="g-text" x="315" y="75" text-anchor="middle">文字栏滚动</text>
<rect class="g-node" x="490" y="45" width="140" height="50" rx="12"/><text class="g-text" x="560" y="75" text-anchor="middle">热区点亮</text>
<path class="g-line" d="M140 62 L248 62" marker-end="url(#g-ah)"/><path class="g-line" d="M250 80 L142 80" marker-end="url(#g-ah)"/>
<text class="g-text g-text--faint" x="195" y="52" text-anchor="middle">翻页时滚动</text><text class="g-text g-text--faint" x="195" y="100" text-anchor="middle">滚动时翻页</text>
<path class="g-line" d="M380 70 L488 70" marker-end="url(#g-ah)"/>
</svg>
</div>

## 标签页

同一件事有两种做法（桌面和手机）时用。按钮和面板按顺序一一对应；面板里照常写 Markdown（`markdown="1"`，且面板标签下一行要空一行）。

<div class="guide-tabs" data-guide-tabs>
<div class="guide-tabs__list"><button type="button">桌面</button><button type="button">手机</button></div>
<div class="guide-tabs__panel" markdown="1">

在页面左上角的搜索条里输入，或者按 <kbd>/</kbd> 直接跳到搜索条。

</div>
<div class="guide-tabs__panel" markdown="1">

点顶部的放大镜，输入后点软键盘上的「搜索」。

</div>
</div>

{% raw %}
```text
<div class="guide-tabs" data-guide-tabs>
<div class="guide-tabs__list"><button type="button">桌面</button><button type="button">手机</button></div>
<div class="guide-tabs__panel" markdown="1">

桌面上怎么做，可以写多段、列表、图。

</div>
<div class="guide-tabs__panel" markdown="1">

手机上怎么做。

</div>
</div>
```
{% endraw %}

## 表格

普通 Markdown 表格就是圆角框加浅色表头。对照表（一列是项目名、其余是取值）后面加 `{: .matrix}`，第一列会着浅底。

| 项目 | 桌面 | 手机 |
|---|---|---|
| 目录 | 左侧常驻 | 折叠成「目录」抽屉 |
| 本页目录 | 右侧，随滚动高亮 | 放在文章上方 |
| 截图宽度 | 1280 | 390 |
{: .matrix}

{% raw %}
```text
| 项目 | 桌面 | 手机 |
|---|---|---|
| 目录 | 左侧常驻 | 折叠成「目录」抽屉 |
{: .matrix}
```
{% endraw %}

## 代码与按键

行内代码用反引号：`/search/?q=增田`。代码块右上角悬停出现「复制」。按键用 `<kbd>`：<kbd>Ctrl</kbd> + <kbd>K</kbd>、<kbd>←</kbd> <kbd>→</kbd>。

```text
https://docs.pokeamice.com/search/?q=增田
```

## 卡片与标签

结尾的「相关阅读」用卡片，一排最多四张；没有页面的写成灰色的「编写中」（`url` 留空）。

<div class="guide-cards">
{% include guide/card.html kind="文档站" title="怎么找资料" text="搜索、专题图块、维度面板和分类。" url="/guide/" %}
{% include guide/card.html kind="文档站" title="读一篇扫描" text="舞台、文字栏和热区怎么配合。" url="" %}
</div>

{% raw %}
```text
<div class="guide-cards">
{% include guide/card.html kind="文档站" title="怎么找资料" text="搜索、专题图块、维度面板和分类。" url="/guide/docs-site/#找资料" %}
{% include guide/card.html kind="文档站" title="读一篇扫描" text="…" url="" %}
</div>
```
{% endraw %}

标签：<span class="guide-tag">默认</span> <span class="guide-tag is-tip">新</span> <span class="guide-tag is-soon">编写中</span>，写在标题或句子里：`<span class="guide-tag is-tip">新</span>`。

## 写作规范

- **一节一个任务。** 标题写读者想做的事（「找到某人参与过的作品」），不写功能名（「人物库」）。
- **三段式。** 这是什么（一两句）→ 怎么用（编号步骤，最多五步）→ 实机（截图加圈）。
- **按钮和菜单写真实文字，用「」括起来。** 不写「点右上角的图标」；实在没有文字的，写它的位置和样子。
- **每步一个动作，动词开头。** 结果写在步骤后面另起一段，不塞进步骤。
- **不讲实现。** 不出现 Jekyll、JSON、脚本名——那些写在 `design/`，读者用不着。
- **名词与站内一致。** 日文原名保留并给中文译名；译法参照 `design/glossary-site.json`。
- **截图来自线上站点**，桌面宽 1280、手机 390×844，WebP，单张不超过 250 KB；不用本地预览，本地数据会过期。
- **例子挑稳定的。** 用不会再改的老帖当例子，不用正在修订的。
- **提示框节制。** 一节最多一个；整篇满是提示框，读者就不看了。

## 上线前检查

- 每一节的「怎么用」都在线上站点走通了一遍，走完写进 `verified`。
- 每个圈都压在它说的东西上；缩到 390 宽再看一遍。
- 页面里出现的每个链接都能打开；`guides.yml` 里的 `url` 已填、`status` 已改。
- 浅色和夜间主题（站点右上角的主题切换）各看一遍，图和圈都读得清。
- 每张截图登记进 `guides.yml` 的 `shots`（文件、页面地址、视口、拍摄日期）。
- 导航（KEy docs → 使用指南）和首页专题架上的图块已经挂好，指向 `/guide/`；新增一篇不用再动它们，只要 `guides.yml` 里填对 `url` 和 `status`。首页图块上的数字是已发布的指南篇数。
