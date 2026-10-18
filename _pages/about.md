---
layout: library
title: "关于本站"
crumb: 关于本站
permalink: /about/
description: "Poke Amice Docs（宝可梦友会 文档站点）是什么、收什么、资料怎么来的、怎么引用、版权与撤下、怎么帮忙，以及这个站是怎么搭起来的。"
---
{%- comment -%}
The one page about the site itself. Everything a reader might want to know about the archive rather than
inside it starts here: what it is, what it holds and what it leaves to others, how an entry is made and what
its status labels mean, how to cite it, rights and take-down, how to help, how the site is built, and its
record. The methods tab on the home page (home-methods.html), the navigation's MOre at, the footer and the
two old site posts (2022 更新日志, 2024 建站纪事) all point here. Counts are computed, not written.
Sites by others - peers, encyclopedias, archives - are on /references/, not here.
{%- endcomment -%}
<link rel="stylesheet" href="{{ '/assets/css/home-tabs.css' | relative_url }}">
<link rel="stylesheet" href="{{ '/assets/css/site-info.css' | relative_url }}">
{%- assign ab_first = site.posts.last.date | date: "%Y" -%}
{%- assign ab_gaps = site.data.archive_gaps.entries | size -%}
{%- assign ab_wanted = site.data.wanted.items | where_exp: "i", "i.status == 'known' or i.status == 'candidate' or i.status == 'text'" | size -%}
{%- assign ab_feed = site.data.feed | sort: "date" | reverse -%}
{%- assign ab_repo = "https://github.com/Asimov2144/pokeamice" -%}

<header class="library__head">
  <p class="library__eyebrow">About · 关于本站</p>
  <h1 class="library__title">关于本站</h1>
  <p class="library__lead"><b>Poke Amice Docs</b>（宝可梦友会 文档站点）是宝可梦开发相关资料的中文存档：开发者访谈、杂志扫描、GAME FREAK 的官方博客与专栏，以及从这些资料里整理出来的人物、作品和制作名单。它是<a href="https://pokeamice.com">宝可梦友会</a>的资料部分，由站主 Asimov2144 维护。</p>
  <p class="library__facts"><b>{{ site.posts.size }}</b> 条资料 · 资料年份 {{ ab_first }}–{{ site.time | date: "%Y" }} · 2024 年 12 月建站 · 本页数字更新于 {{ site.time | date: "%Y-%m-%d" }}</p>
</header>

<div class="si">
  <div class="si-main">

    <section class="si-sec" id="scope">
      <h2>这里收什么 <small>Scope</small></h2>
      <dl class="si-defs">
        <dt>访谈翻译</dt><dd>网页、杂志、讲演里的宝可梦开发者访谈，中文译文，多数可以和原文对照。<a href="{{ '/#interview-translations' | relative_url }}">按年代看 →</a></dd>
        <dt>杂志扫描</dt><dd>杂志与攻略本的整页扫描，逐页转写、翻译，页图和译文对照着读。<a href="{{ '/search/?type=%E6%89%AB%E6%8F%8F%E7%BF%BB%E8%AF%91' | relative_url }}">全部扫描 →</a></dd>
        <dt>官方博客</dt><dd>GAME FREAK 的<a href="{{ '/gamefreak-director/' | relative_url }}">部长专栏</a>、<a href="{{ '/gamefreak-staff/' | relative_url }}">员工博客</a>、<a href="{{ '/gamefreak-art/' | relative_url }}">杉森建的博客</a>，按原站的样子复刻，附译文。</dd>
        <dt>人物与作品</dt><dd>从每篇资料的元数据整理出的<a href="{{ '/people/' | relative_url }}">人物库</a>、<a href="{{ '/works/' | relative_url }}">作品库</a>和<a href="{{ '/credits/' | relative_url }}">制作名单</a>，以及<a href="{{ '/timeline/' | relative_url }}">时间线</a>、<a href="{{ '/resource-graph/' | relative_url }}">关系图谱</a>。</dd>
        <dt>站主笔记</dt><dd>站主自己的<a href="{{ '/long-analysis/' | relative_url }}">长文分析</a>和<a href="{{ '/notes/weibo/' | relative_url }}">微博碎片</a>。这部分是原创，不是存档。</dd>
      </dl>
      <p><b>不收</b>：游戏数据、图鉴、攻略和新闻。这些去百科站和资讯站查更全，常用的几个列在<a href="{{ '/references/' | relative_url }}">参考与同类站</a>。</p>
      <p><b>其他语言</b>：<a href="{{ '/en/' | relative_url }}">English</a> 是英文入口；<a href="{{ '/ja/' | relative_url }}">日本語</a>收了海外媒体访谈的日文译本，由 AI 翻译，没有人工校对。</p>
    </section>

    <section class="si-sec" id="method">
      <h2>资料怎么来的 <small>Method</small></h2>
      <ol class="me-flow" aria-label="一篇资料怎么进来">
        <li><i class="fas fa-box-archive" aria-hidden="true"></i><b>收集</b><span>杂志扫描、官网与博客的归档页、媒体访谈原文</span></li>
        <li><i class="fas fa-eye" aria-hidden="true"></i><b>转写</b><span>扫描页整页转写，逐页对照，不用别处附带的转写</span></li>
        <li><i class="fas fa-language" aria-hidden="true"></i><b>翻译</b><span>模型初译，译法与术语按站内统一表核对</span></li>
        <li><i class="fas fa-check-double" aria-hidden="true"></i><b>校对</b><span>对着原页、原文抽查，每篇的 workflow 字段记着做到哪一步</span></li>
        <li><i class="fas fa-link" aria-hidden="true"></i><b>关联</b><span>人物、作品、制作名单与时间线互相指向</span></li>
      </ol>
      <p>每篇开头的资料卡片写着它的来源、原文链接和处理进度；字段的含义见<a href="{{ '/metadata-schema/' | relative_url }}">资料元数据规范</a>。网页原文以收录时的页面为准；官网改版或撤下了的，用 Wayback Machine 里的存档版本。</p>
      <h3>译文的两种状态</h3>
      <dl class="si-defs">
        <dt><i class="si-tag si-tag--draft">初译待校</i></dt><dd>大模型初译，还没有人工逐句校对。意思大体可靠，措辞和细节可能有出入，引用前请对照原文。</dd>
        <dt><i class="si-tag si-tag--done">已校对</i></dt><dd>译文已经有人对着原文校过。</dd>
      </dl>
      <p>没有这两个标签的条目，是没有登记处理进度的。转写和初译用到的模型有 Qwen-VL 和 DeepSeek 等，校对、译法统一和关联由人来定。</p>
    </section>

    <section class="si-sec" id="cite">
      <h2>引用与转载 <small>Citing</small></h2>
      <p>引用一篇资料时，请<b>同时写明原始出处和本站页面</b>。原始出处在每篇页头的「原文 ↗」和资料卡片里。可以照这个格式写：</p>
      <p class="si-cite">〈篇名〉，原载〈刊物或网站〉（〈年月〉），<span>Poke Amice Docs 中译，</span>〈本站网址〉，〈访问日期〉。</p>
      <ul>
        <li>标着「初译待校」的译文，请先对照原文再引用；发言的原意以原文为准。</li>
        <li>转载本站的译文或整理，请注明出处并附上链接。</li>
      </ul>
    </section>

    <section class="si-sec" id="rights">
      <h2>版权与撤下 <small>Rights</small></h2>
      <p>本站收录的访谈、杂志页面、博客文章和图片，版权归原刊物、网站和作者所有。本站的翻译和整理出于研究与资料保存的目的。</p>
      <p>如果你是权利人，认为某一篇不宜公开，或者需要更正署名、出处，请发邮件到 <a href="mailto:asimov2144@gmail.com">asimov2144@gmail.com</a>，写明是哪一页，我们会尽快处理。</p>
      <p>站点的代码公开在 <a href="{{ ab_repo }}">GitHub</a>；主题基于 <a href="https://mmistakes.github.io/minimal-mistakes/">Minimal Mistakes</a>（MIT 许可）。</p>
    </section>

    <section class="si-sec" id="contact">
      <h2>怎么帮忙、怎么联系 <small>Contact</small></h2>
      <div class="me-grid">
        <a class="me-card" href="{{ '/wanted/' | relative_url }}"><i class="fas fa-bullhorn" aria-hidden="true"></i><span><b>原刊征集</b><em>{{ ab_wanted }} 条杂志访谈在找原刊，手机拍几页就能帮上忙</em></span></a>
        <a class="me-card" href="{{ '/keys/archive-gaps/' | relative_url }}"><i class="fas fa-puzzle-piece" aria-hidden="true"></i><span><b>收录缺口</b><em>登记了 {{ ab_gaps }} 条站内没有或只有一部分的资料</em></span></a>
        <a class="me-card" href="{{ ab_repo }}/issues"><i class="fab fa-github" aria-hidden="true"></i><span><b>报错与建议</b><em>原文对不上、译错、缺页，在 GitHub 开一个 Issue</em></span></a>
        <a class="me-card" href="mailto:asimov2144@gmail.com"><i class="fas fa-envelope" aria-hidden="true"></i><span><b>邮件</b><em>asimov2144@gmail.com</em></span></a>
      </div>
      <p>也可以在 <a href="https://weibo.com/u/6306512172">微博</a>、<a href="https://space.bilibili.com/13876658">哔哩哔哩</a>、<a href="https://x.com/asimov74320758">X</a> 找到站主；QQ 交流群 716536347。</p>
    </section>

    <section class="si-sec" id="build">
      <h2>这个站怎么搭的 <small>Building</small></h2>
      <dl class="si-defs">
        <dt>生成</dt><dd>静态站，用 <a href="https://jekyllrb.com/">Jekyll</a> 生成。主题从 Minimal Mistakes 起步，首页、访谈与扫描阅读器、人物和制作名单等页面是另写的。</dd>
        <dt>部署</dt><dd>推到 GitHub 的 main 分支后，由 GitHub Actions 构建并发布到 GitHub Pages。</dd>
        <dt>图片</dt><dd>文中配图在仓库里；杂志扫描的页图放在宝可梦友会的图库（gallery.pokeamice.com）。</dd>
        <dt>搜索</dt><dd>顶部的放大镜是在浏览器里运行的全文搜索（Lunr）；<a href="{{ '/search/' | relative_url }}">检索中心</a>按类型、人物、作品、年份筛选。</dd>
        <dt>派生数据</dt><dd>人物、作品、制作名单、时间线、关系图谱和今日一句，都由仓库里的脚本从每篇的元数据生成。</dd>
      </dl>
      <div class="me-grid">
        <a class="me-card" href="{{ ab_repo }}"><i class="fab fa-github" aria-hidden="true"></i><span><b>源码仓库</b><em>github.com/Asimov2144/pokeamice</em></span></a>
        <a class="me-card" href="{{ '/metadata-schema/' | relative_url }}"><i class="fas fa-tags" aria-hidden="true"></i><span><b>资料元数据规范</b><em>每篇的字段：来源、人物、作品、进度</em></span></a>
        <a class="me-card" href="{{ '/local-editing-tools/' | relative_url }}"><i class="fas fa-toolbox" aria-hidden="true"></i><span><b>本地编辑工具索引</b><em>导入、检查、生成各类脚本</em></span></a>
        <a class="me-card" href="{{ '/editor-workbench/' | relative_url }}"><i class="fas fa-pen-to-square" aria-hidden="true"></i><span><b>本地编辑工作台</b><em>在本机整理与校对条目</em></span></a>
        <a class="me-card" href="{{ '/article-migration-guide/' | relative_url }}"><i class="fas fa-truck-moving" aria-hidden="true"></i><span><b>旧平台文章迁移</b><em>把旧站的图文搬进来的教程</em></span></a>
      </div>
      <p>早期的主题、图标与图床怎么来的，以及鸣谢，记在 2024 年的<a href="{{ '/sites/%E6%96%87%E6%A1%A3/%E5%AE%9D%E5%8F%AF%E6%A2%A6%E5%8F%8B%E4%BC%9A/%E7%AB%99%E7%82%B9-%E5%BB%BA%E7%AB%99%E7%BA%AA%E4%BA%8B-Building-Records/' | relative_url }}">建站纪事</a>里。</p>
    </section>

    <section class="si-sec" id="history">
      <h2>站点记录 <small>History</small></h2>
      <ul class="si-log">
        {%- for e in ab_feed limit: 3 %}
        <li><time datetime="{{ e.date }}">{{ e.date }}</time><span><a href="{{ e.url | relative_url }}">{{ e.title }}</a></span></li>
        {%- endfor %}
        <li><time datetime="2026-09">2026-09 起</time><span>大批收录与整理开始；每件事记在<a href="{{ '/news/' | relative_url }}">站点动态</a>，可以 <a href="{{ '/feed.xml' | relative_url }}">RSS 订阅</a>。</span></li>
        <li><time datetime="2024-12-15">2024-12</time><span>在 GitHub 建仓，用 Jekyll 搭起文档站。<a href="{{ '/sites/%E6%96%87%E6%A1%A3/%E5%AE%9D%E5%8F%AF%E6%A2%A6%E5%8F%8B%E4%BC%9A/%E7%AB%99%E7%82%B9-%E5%BB%BA%E7%AB%99%E7%BA%AA%E4%BA%8B-Building-Records/' | relative_url }}">建站纪事 →</a></span></li>
        <li><time datetime="2022-05">2022-05</time><span>宝可梦友会早期的更新日志，留作记录。<a href="{{ '/sites/%E6%96%87%E6%A1%A3/Updates/' | relative_url }}">更新日志 →</a></span></li>
      </ul>
    </section>

  </div>

  <aside class="si-rail">
    <section class="si-box">
      <h2><i class="fas fa-list" aria-hidden="true"></i>本页</h2>
      <ul>
        <li><a href="#scope">这里收什么</a></li>
        <li><a href="#method">资料怎么来的</a></li>
        <li><a href="#cite">引用与转载</a></li>
        <li><a href="#rights">版权与撤下</a></li>
        <li><a href="#contact">怎么帮忙、怎么联系</a></li>
        <li><a href="#build">这个站怎么搭的</a></li>
        <li><a href="#history">站点记录</a></li>
      </ul>
    </section>
    <section class="si-box si-box--more">
      <h2><i class="fas fa-signs-post" aria-hidden="true"></i>接着看</h2>
      <ul>
        <li><a href="{{ '/guide/docs-site/' | relative_url }}"><b>文档站怎么用</b></a><span>首页各分区、读访谈和扫描的方法</span></li>
        <li><a href="{{ '/news/' | relative_url }}"><b>站点动态</b></a><span>收录、整理、新功能、征集</span></li>
        <li><a href="{{ '/references/' | relative_url }}"><b>参考与同类站</b></a><span>做同类事情的站、百科与档案工具</span></li>
        <li><a href="https://pokeamice.com"><b>宝可梦友会主站</b></a><span>pokeamice.com</span></li>
      </ul>
    </section>
  </aside>
</div>
