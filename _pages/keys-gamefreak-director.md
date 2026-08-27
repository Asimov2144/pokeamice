---
layout: archive
title: "Game Freak 部长专栏"
permalink: /keys/gamefreak-director/
classes: wide
sidebar: false
---

{% assign gf = site.data.gamefreak_director %}
{% assign gf_posts = site.posts | where: "archive_type", "gamefreak_director_column" %}
{% assign gf_posts = gf_posts | where_exp: "post", "post.gf_archive_id != nil" %}

<section class="key-window key-window--gf">
  <header class="key-window-hero">
    <p>Official Blog Window</p>
    <h2>Game Freak 部长专栏</h2>
    <span>用于集中展示 `gamefreak_director_column` 类型文章。这里可以作为后续“专题窗口”的模板：左侧是系列信息，右侧按文章、分类和年月组织资料。</span>
    <div class="key-window-actions">
      <a href="{{ '/gamefreak-director/' | relative_url }}">专题还原页</a>
      <a href="{{ gf.source_url }}" target="_blank" rel="noopener">官方首页</a>
      <a href="{{ gf.category_url }}" target="_blank" rel="noopener">官方分类</a>
      <a href="{{ gf.archive_url }}" target="_blank" rel="noopener">官方归档</a>
    </div>
  </header>

  <div class="key-window-layout">
    {% include gamefreak-director-sidebar.html %}

    <div class="key-window-main">
      <section class="key-window-panel">
        <header>
          <p>Entries</p>
          <h3>本地收录文章</h3>
        </header>
        <div class="key-window-list">
          {% for post in gf_posts %}
            <a href="{{ post.url | relative_url }}">
              <span>{% if post.gf_entry_no %}第{{ post.gf_entry_no }}回{% else %}Entry{% endif %}</span>
              <strong>{{ post.title }}</strong>
              <em>{{ post.date | date: "%Y.%m.%d" }}{% if post.gf_archive %} / {{ post.gf_archive }}{% endif %}</em>
              {% if post.summary %}
                <p>{{ post.summary }}</p>
              {% endif %}
            </a>
          {% else %}
            <p class="key-window-empty">还没有导入部长专栏文章。</p>
          {% endfor %}
        </div>
      </section>

      <section class="key-window-panel">
        <header>
          <p>Archives</p>
          <h3>年月归档</h3>
        </header>
        <div class="key-window-archive">
          {% for archive in gf.archives limit:12 %}
            {% assign archive_key = archive | replace: "年", "-" | replace: "月", "" %}
            {% assign archive_key_normalized = archive_key | replace: "-0", "-" %}
            {% assign archive_hits = "" | split: "," %}
            {% for post in gf_posts %}
              {% assign post_archive = post.gf_archive %}
              {% if post_archive == nil or post_archive == empty %}
                {% assign post_archive = post.date | date: "%Y-%m" %}
              {% endif %}
              {% assign post_archive_normalized = post_archive | replace: "-0", "-" %}
              {% if post_archive_normalized == archive_key_normalized %}
                {% assign archive_hits = archive_hits | push: post %}
              {% endif %}
            {% endfor %}
            <a href="{{ gf.archive_url }}" target="_blank" rel="noopener">
              <strong>{{ archive }}</strong>
              <span>{{ archive_hits | size }} local</span>
            </a>
          {% endfor %}
        </div>
        <div class="key-window-more">
          <span>仅显示最近 12 个归档月份，完整月份列表保留在专题归档页。</span>
          <a href="{{ '/gamefreak-director/archive/' | relative_url }}">查看完整归档</a>
        </div>
      </section>
    </div>
  </div>
</section>
