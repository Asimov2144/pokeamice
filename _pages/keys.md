---
layout: archive
title: "资料窗口"
permalink: /keys/
sidebar:
  nav: "docs"
---

{% assign gf_director_posts = site.posts | where: "archive_type", "gamefreak_director_column" %}
{% assign interview_posts = site.posts | where_exp: "post", "post.categories contains '访谈翻译'" %}

<section class="key-window-hub">
  <header class="key-window-hero">
    <p>Key Docs</p>
    <h2>把重要资料系列做成可检索、可追踪的窗口。</h2>
    <span>这里不是普通文章列表，而是给长期资料项目准备的入口。每个窗口可以汇总文章、来源、年月归档、分类、人物作品和工作流状态。</span>
  </header>

  <div class="key-window-grid">
    <a class="key-window-card key-window-card--primary" href="{{ '/keys/gamefreak-director/' | relative_url }}">
      <span>Official Blog</span>
      <strong>Game Freak 部长专栏</strong>
      <em>{{ gf_director_posts | size }} 篇本地条目</em>
      <p>还原“増田部長のめざめるパワー”的分类、年月归档和文章信息。</p>
    </a>

    <a class="key-window-card" href="{{ '/resource-graph/' | relative_url }}">
      <span>Guide</span>
      <strong>站内关系图谱</strong>
      <em>人物 / 作品 / 时间线</em>
      <p>把文章和评注反向汇总到实体页面，形成资料网络。</p>
    </a>

    <a class="key-window-card" href="{{ '/search/' | relative_url }}">
      <span>Search</span>
      <strong>资料检索中心</strong>
      <em>按人物、作品、年份、来源筛选</em>
      <p>未来内容增长后，搜索会成为比栏目更重要的主入口。</p>
    </a>

    <a class="key-window-card" href="{{ '/timeline/' | relative_url }}">
      <span>Timeline</span>
      <strong>时间线</strong>
      <em>按年份阅读</em>
      <p>适合追踪开发记录、访谈发布时间和资料整理脉络。</p>
    </a>
  </div>

  <section class="key-window-panel">
    <header>
      <p>Current Collections</p>
      <h3>当前资料规模</h3>
    </header>
    <div class="key-window-stats">
      <a href="{{ '/keys/gamefreak-director/' | relative_url }}">
        <strong>{{ gf_director_posts | size }}</strong>
        <span>部长专栏</span>
      </a>
      <a href="{{ '/search/' | relative_url }}?type=%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91">
        <strong>{{ interview_posts | size }}</strong>
        <span>访谈翻译</span>
      </a>
    </div>
  </section>
</section>
