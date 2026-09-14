---
layout: archive
title: "GAME FREAK 员工博客内容分析"
permalink: /keys/gamefreak-staff-analysis/
classes: wide
categories: [文档, Game Freak, 分析]
tags: [GAME FREAK, 员工博客, 数字存档, 内容分析]
summary: "从年份、更新节奏、主题、人物和图像使用分析《晴时偶有阴》的 209 篇员工日志。"
search: true
sidebar: false
---

{% assign report = site.data.gamefreak_staff_analysis %}
{% assign overview = report.overview %}

<section class="key-window gf-staff-report">
  <header class="key-window-hero gf-staff-report__hero">
    <p>DOCUMENT ANALYSIS · STAFF DIARY</p>
    <h2>209 篇日志构成的 GAME FREAK 工作现场</h2>
    <span>这份报告分析官方员工博客《晴れたり時々曇ったり》的完整本地存档。它关注博客何时更新、谈了什么、哪些员工反复出现，以及图片与链接如何参与叙事。</span>
    <div class="key-window-actions">
      <a href="{{ '/gamefreak-staff/' | relative_url }}">连续阅读原博客</a>
      <a href="{{ '/search/' | relative_url }}?type=Game%20Freak%20%E5%8D%9A%E5%AE%A2">检索全部文章</a>
      <a href="{{ '/keys/' | relative_url }}">返回文档索引</a>
    </div>
  </header>

  <section class="key-window-stats gf-staff-report__stats" aria-label="存档概况">
    <a href="#timeline"><strong>{{ overview.articles }}</strong><span>篇文章 · {{ overview.first_date }}—{{ overview.last_date }}</span></a>
    <a href="#cadence"><strong>{{ report.cadence.median_gap_days }} 天</strong><span>相邻文章的中位间隔</span></a>
    <a href="#visual"><strong>{{ overview.images }}</strong><span>幅正文图片 · {{ overview.image_article_rate }}% 文章含图</span></a>
    <a href="#people"><strong>{{ overview.named_people }}</strong><span>位可识别员工昵称</span></a>
    <a href="#translation"><strong>{{ overview.translation_rate }}%</strong><span>中文译文覆盖率</span></a>
  </section>

  <section class="key-window-panel gf-staff-report__finding">
    <header><div><p>Reading</p><h3>怎样理解这批材料</h3></div></header>
    <div class="gf-staff-report__prose">
      <p>这不是一份只在新作发售时更新的宣传博客。2008—2010 年几乎保持周更，开发话题、公司活动、招聘说明和私人兴趣持续交错，使它更接近一份由多名员工共同书写的“公司生活切片”。</p>
      <p>作品信息固然重要，但这批材料更稀有的部分，是游戏制作被放回具体工作环境以后留下的细节：员工如何描述企划、程序、美术和声音工作，如何组织内部比赛与旅行，以及招聘、新人培养和办公室文化如何反复进入公开叙述。</p>
      <p>因此，本页的主题类别允许重叠。一篇公司内部宝可梦对战文章可以同时属于“宝可梦与作品”“公司与集体活动”及“日常、兴趣与旅行”，这比强行给每篇文章贴一个唯一标签更接近原博客的混合性质。</p>
    </div>
  </section>

  <section class="key-window-panel" id="timeline">
    <header><div><p>Timeline</p><h3>年度文章分布</h3></div><span>{{ overview.years }} 个日历年</span></header>
    <div class="gf-staff-report__bars">
      {% for item in report.years %}
        <div class="gf-staff-report__bar" style="--report-value: {{ item.relative }}%;">
          <strong>{{ item.year }}</strong>
          <span><i></i></span>
          <em>{{ item.count }} 篇 · {{ item.share }}%</em>
        </div>
      {% endfor %}
    </div>
    <p class="gf-staff-report__note">2009 年达到最高点，共 56 篇；2008 与 2010 年也分别保持 52 篇和 51 篇。2011 年起更新明显放缓，2012 年仅留下 4 篇。</p>
  </section>

  <section class="key-window-panel" id="cadence">
    <header><div><p>Cadence</p><h3>更新节奏</h3></div><span>{{ report.cadence.within_10_days_rate }}% 的间隔不超过 10 天</span></header>
    <div class="key-window-grid">
      <article class="key-window-card"><span>Median</span><strong>{{ report.cadence.median_gap_days }} 天</strong><p>典型更新节奏接近每周一次。</p></article>
      <article class="key-window-card"><span>Average</span><strong>{{ report.cadence.average_gap_days }} 天</strong><p>长时间停更把平均值略微拉高。</p></article>
      <article class="key-window-card"><span>Longest pause</span><strong>{{ report.cadence.longest_gap_days }} 天</strong><p>{{ report.cadence.longest_gap_from }} 至 {{ report.cadence.longest_gap_to }}。</p></article>
    </div>
  </section>

  <section class="key-window-panel" id="themes">
    <header><div><p>Topics</p><h3>主题关键词覆盖</h3></div><span>类别可重叠</span></header>
    <div class="gf-staff-report__topic-grid">
      {% for theme in report.themes %}
        <article>
          <div><strong>{{ theme.label }}</strong><em>{{ theme.count }} 篇 · {{ theme.share }}%</em></div>
          <span class="gf-staff-report__meter" style="--report-value: {{ theme.share }}%;"><i></i></span>
          <p>{{ theme.description }}</p>
          <small>命中词：{{ theme.keywords | join: "、" }}</small>
        </article>
      {% endfor %}
    </div>
    <p class="gf-staff-report__note">“开发与制作”覆盖 125 篇，“公司与集体活动”覆盖 111 篇；两者共同说明这套博客既在介绍作品，也在持续解释制作作品的人和组织。原存档清单没有提供可靠的逐篇分类值，因此这里没有把原站的六个全局分类误当作每篇文章的标签。</p>
  </section>

  <section class="key-window-panel" id="roles">
    <header><div><p>Work</p><h3>职位与工作语汇</h3></div><span>正文关键词命中</span></header>
    <div class="key-window-stats">
      {% for role in report.roles %}
        <a href="{{ '/search/' | relative_url }}?q={{ role.label | url_encode }}&type=Game%20Freak%20%E5%8D%9A%E5%AE%A2"><strong>{{ role.count }}</strong><span>{{ role.label }}相关 · {{ role.share }}%</span></a>
      {% endfor %}
    </div>
    <p class="gf-staff-report__note">这些数字表示文章是否谈到相关工作，并不等同于作者职位统计；一篇跨部门访谈可能同时命中多个职位。</p>
  </section>

  <section class="key-window-panel" id="people">
    <header><div><p>People</p><h3>反复出现的员工昵称</h3></div><span>{{ overview.named_people }} 人被人物表识别</span></header>
    <div class="gf-staff-report__people">
      {% for person in report.people limit:16 %}
        <article>
          <header><strong>{{ person.source }}（{{ person.target }}）</strong><em>{{ person.article_count }} 篇</em></header>
          <p><a href="{{ person.first.url | relative_url }}">首次：{{ person.first.date }}</a><a href="{{ person.last.url | relative_url }}">末次：{{ person.last.date }}</a></p>
        </article>
      {% endfor %}
    </div>
    <p class="gf-staff-report__note">人物数来自校订过的 Staff 昵称表；统计的是正文提及次数，不把每次提及都解释为该员工亲自署名。カニ子贯穿早期博客，にょろリカ从 2010 年起承担了明显的网站编辑与串联角色。</p>
  </section>

  <section class="key-window-panel" id="visual">
    <header><div><p>Document form</p><h3>文本、图片与链接</h3></div></header>
    <div class="key-window-stats">
      <a href="#visual"><strong>{{ overview.source_characters }}</strong><span>日文正文字符</span></a>
      <a href="#visual"><strong>{{ overview.median_characters }}</strong><span>每篇正文字符中位数</span></a>
      <a href="#visual"><strong>{{ overview.image_articles }}</strong><span>篇文章含有图片</span></a>
      <a href="#visual"><strong>{{ overview.links }}</strong><span>条正文链接</span></a>
    </div>
    <div class="gf-staff-report__rankings">
      <div class="key-window-list">
        <h4>正文最长的文章</h4>
        {% for item in report.longest_articles %}
          <a href="{{ item.url | relative_url }}"><span>{{ item.date }}</span><strong>{{ item.title_zh | default: item.title }}</strong><em>{{ item.characters }} 字符 · {{ item.images }} 图</em></a>
        {% endfor %}
      </div>
      <div class="key-window-list">
        <h4>图片最多的文章</h4>
        {% for item in report.most_visual_articles %}
          <a href="{{ item.url | relative_url }}"><span>{{ item.date }}</span><strong>{{ item.title_zh | default: item.title }}</strong><em>{{ item.images }} 图 · {{ item.characters }} 字符</em></a>
        {% endfor %}
      </div>
    </div>
    <p class="gf-staff-report__note">195 篇文章包含图片，占全部文章的 {{ overview.image_article_rate }}%。图片不是偶尔出现的装饰，而是这套员工日志的常规叙事组成。</p>
  </section>

  <section class="key-window-panel" id="translation">
    <header><div><p>Archive status</p><h3>存档与翻译覆盖</h3></div><span>{{ overview.translations }} / {{ overview.articles }}</span></header>
    <div class="gf-staff-report__prose">
      <p>当前 209 篇文章均已建立本地日文内容层和简体中文译文层，中文覆盖率为 {{ overview.translation_rate }}%。正文中的图片位置、显式换行与链接结构由存档管线保留，员工昵称采用“首次保留假名并附中文译名、同篇后续只保留假名”的校订规则。</p>
      <p>本报告只描述当前存档可以支持的结论，不把关键词命中当作人工主题标注，也不把人物提及当作严格作者署名。后续若补齐原站逐篇分类、作者字段或新增人工标签，可重新运行分析脚本更新本页。</p>
    </div>
    <div class="key-window-actions">
      <a href="{{ '/gamefreak-staff/' | relative_url }}">开始连续阅读</a>
      <a href="{{ '/keys/' | relative_url }}">浏览其他资料窗口</a>
    </div>
  </section>

  <details class="gf-staff-report__method">
    <summary>统计方法与复现</summary>
    <p>{{ report.method.note }}</p>
    <code>python tools/gamefreak_staff_analysis.py</code>
    <p>文章权威清单：<code>{{ report.method.article_authority }}</code><br>正文层：<code>{{ report.method.text_layer }}</code><br>人物表：<code>{{ report.method.people_policy }}</code></p>
  </details>
</section>
