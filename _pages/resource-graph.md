---
title: "关系图谱"
permalink: /resource-graph/
layout: graph
classes: layout--graph
categories: [文档, 站点]
tags: [graph, metadata, guide]
archive_type: article
search: false
sitemap: true
source:
  title: "站点自动生成"
  source_type: site_index
entities:
  organizations:
    - Poke Amice Docs
---

<section class="graph" data-graph>
  <header class="graph__head">
    <p class="graph__kicker">Relationship Graph</p>
    <h1 class="graph__title">关系图谱</h1>
    <p class="graph__lede">库内每一篇访谈、讲演、专栏都标注了在场的人物和谈到的作品。把这些标注连起来，就是下面的图：<b>两个人在同一篇资料里出现过，之间就有一条线，线越粗同场的篇数越多</b>；人物按同场关系自动聚成群落，颜色相同即同一群落。点一个人，看他的同场者、谈过的作品和活跃年份。</p>
    <div class="graph__stats" data-graph-stats>
      <div><strong>…</strong><span>人物</span></div>
      <div><strong>…</strong><span>同场关系</span></div>
      <div><strong>…</strong><span>作品</span></div>
      <div><strong>…</strong><span>资料</span></div>
    </div>
  </header>

  <nav class="graph__jump" aria-label="本页分区">
    <a href="#graph-network">人物网络</a>
    <a href="#graph-matrix">人物 × 作品</a>
    <a href="#graph-timeline">年代脉络</a>
    <a href="#graph-index">关系索引</a>
    <a href="#graph-method">怎么算的</a>
  </nav>

  <section class="graph__section" id="graph-network">
    <div class="graph__bar">
      <h2>人物网络</h2>
      <label class="graph__control"><span>至少同场</span><select data-graph-min><option value="1">1 篇</option><option value="2" selected>2 篇</option><option value="3">3 篇</option><option value="5">5 篇</option></select></label>
      <label class="graph__control"><span>范围</span><select data-graph-scope><option value="all">全部资料</option><option value="interview" selected>访谈与讲演</option></select></label>
      <label class="graph__control graph__control--find"><span>找人</span><input type="search" list="graph-people" placeholder="输入姓名" data-graph-find><datalist id="graph-people"></datalist></label>
      <button type="button" class="graph__button" data-graph-reset>全图</button>
    </div>
    <div class="graph__stage">
      <div class="graph__canvas-wrap">
        <canvas class="graph__canvas" data-graph-canvas aria-label="人物同场关系网络图"></canvas>
        <div class="graph__tip" data-graph-tip hidden></div>
        <p class="graph__loading" data-graph-loading>正在读取目录并计算关系…</p>
      </div>
      <aside class="graph__panel" data-graph-panel aria-live="polite"></aside>
    </div>
    <div class="graph__legend" data-graph-legend></div>
  </section>

  <section class="graph__section" id="graph-matrix">
    <div class="graph__bar">
      <h2>人物 × 作品</h2>
      <p class="graph__note">收录最多的人物对上主系列与主要作品：格子里的数字是两者同时出现的资料数，颜色越深越多。看得出谁陪伴了哪几个世代。</p>
    </div>
    <div class="graph__matrix-wrap" data-graph-matrix></div>
  </section>

  <section class="graph__section" id="graph-timeline">
    <div class="graph__bar">
      <h2>年代脉络</h2>
      <p class="graph__note">每一行是一个人，每一个点是他在那一年出现过的资料数（点越大越多）。首尾就是这个人在库里的时间跨度。</p>
    </div>
    <div class="graph__timeline-wrap" data-graph-timeline></div>
  </section>

  <section class="graph__section" id="graph-index">
    <div class="graph__bar">
      <h2>关系索引</h2>
      <p class="graph__note">同场最多的搭档，以及每个群落的成员。</p>
    </div>
    <div class="graph__index" data-graph-index></div>
  </section>

  <section class="graph__section graph__method" id="graph-method">
    <h2>怎么算的</h2>
    <ul>
      <li><b>节点</b>是人物库里的真人（动画角色、只被引述的历史人物不入图）；大小按其出现的资料篇数。</li>
      <li><b>连线</b>是"同场"：两人的名字出现在同一篇资料的人物标注里。粗细和索引里的数字都是同场篇数；默认只画同场 2 篇以上的线，1 篇的偶遇可以在上面放开。</li>
      <li><b>群落</b>用标签传播（label propagation）在加权同场网络上聚出，每个群落以其中出现最多的三个人命名；颜色只标群落，不代表公司归属。</li>
      <li><b>范围</b>默认是访谈与讲演类资料；把 Game Freak 博客也算进来时，増田顺一一个人的七百多篇专栏会把他的节点放得很大，但不会增加同场关系。</li>
      <li>数据来自每篇资料的 <code>entities</code> 字段，和检索页、人物页同一份；标注有缺漏，图就有缺漏——发现错的可以在资料页反馈。</li>
    </ul>
  </section>
</section>
