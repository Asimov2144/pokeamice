---
layout: archive
title: "站内收录缺口（文档补盲）"
permalink: /keys/archive-gaps/
classes: wide
categories: [文档, Game Freak, 分析]
tags: [GAME FREAK, 实体杂志, 招聘访谈, 收录缺口]
summary: "对照两份档案的条目与链接，列出站内已收、部分收、需要按链接占位，以及文档没有给出链接的缺口。"
search: true
sidebar: false
---

{% assign gaps = site.data.archive_gaps %}
{% assign all = gaps.entries %}
{% assign in_site = all | where: "site", "in_site" %}
{% assign partial = all | where: "site", "partial" %}
{% assign placeholder = all | where: "site", "placeholder" %}
{% assign gap = all | where: "site", "gap" %}

<section class="key-window gf-gaps">
  <header class="key-window-hero">
    <p>COVERAGE GAPS · RECRUIT + PRINT</p>
    <h2>文档里的条目，站内收到了哪里</h2>
    <span>这一页按两份档案（招聘版本档案、剑盾之后实体访谈档案）的条目逐一对照站内情况。已经收录的列出对应文章；缺的有链接的按链接占位，只登记状态与来源，不放正文；文档没有链接的只标为缺口。</span>
    <div class="key-window-actions">
      <a href="{{ '/keys/gamefreak-recruit-archive/' | relative_url }}">招聘版本档案</a>
      <a href="{{ '/keys/pokemon-post-swsh-print-interviews/' | relative_url }}">实体访谈档案</a>
      <a href="{{ '/keys/' | relative_url }}">返回资料窗口</a>
    </div>
  </header>

  <section class="key-window-stats" aria-label="收录概况">
    <a href="#in-site"><strong>{{ in_site | size }}</strong><span>条已在站内收录</span></a>
    <a href="#partial"><strong>{{ partial | size }}</strong><span>条只收了一部分</span></a>
    <a href="#placeholder"><strong>{{ placeholder | size }}</strong><span>条按链接占位</span></a>
    <a href="#gap"><strong>{{ gap | size }}</strong><span>条缺口（文档未给链接）</span></a>
  </section>

  <section class="key-window-panel" id="placeholder">
    <header><div><p>Placeholder</p><h3>按链接占位（站内缺，有可核对的链接）</h3></div><span>{{ placeholder | size }} 条</span></header>
    <ul class="gap-list">
      {% for e in placeholder %}
      <li class="gap-item" id="{{ e.id }}">
        <p><strong>{{ e.title }}</strong> <span class="gap-tag">{% if e.doc == "recruit" %}招聘{% else %}实体{% endif %}</span>{% if e.priority and e.priority != "" %} <span class="gap-tag">优先级 {{ e.priority }}</span>{% endif %}</p>
        <p class="gap-meta">{{ e.period }}{% if e.people.size > 0 %} · {{ e.people | join: "、" }}{% endif %}</p>
        {% if e.posts.size > 0 %}
        <p class="gap-related">相关站内文章：{% for pf in e.posts %}{% assign p = site.posts | where_exp: "x", "x.path contains pf" | first %}{% if p %}<a href="{{ p.url | relative_url }}">{{ p.title }}</a>{% endif %}{% endfor %}</p>
        {% endif %}
        {% if e.links.size > 0 %}
        <ul class="gap-links">
          {% for l in e.links %}<li><a href="{{ l.url }}">{{ l.label }}</a></li>{% endfor %}
        </ul>
        {% endif %}
        {% if e.need and e.need != "" %}<p class="gap-need">还缺：{{ e.need }}</p>{% endif %}
        {% if e.note and e.note != "" %}<p class="gap-note">{{ e.note }}</p>{% endif %}
      </li>
      {% endfor %}
    </ul>
  </section>

  <section class="key-window-panel" id="partial">
    <header><div><p>Partial</p><h3>只收了一部分</h3></div><span>{{ partial | size }} 条</span></header>
    <ul class="gap-list">
      {% for e in partial %}
      <li class="gap-item" id="{{ e.id }}">
        <p><strong>{{ e.title }}</strong> <span class="gap-tag">{% if e.doc == "recruit" %}招聘{% else %}实体{% endif %}</span>{% if e.priority and e.priority != "" %} <span class="gap-tag">优先级 {{ e.priority }}</span>{% endif %}</p>
        <p class="gap-meta">{{ e.period }}{% if e.people.size > 0 %} · {{ e.people | join: "、" }}{% endif %}</p>
        {% if e.posts.size > 0 %}
        <p class="gap-related">站内已有：{% for pf in e.posts %}{% assign p = site.posts | where_exp: "x", "x.path contains pf" | first %}{% if p %}<a href="{{ p.url | relative_url }}">{{ p.title }}</a>{% endif %}{% endfor %}</p>
        {% endif %}
        {% if e.links.size > 0 %}
        <ul class="gap-links">
          {% for l in e.links %}<li><a href="{{ l.url }}">{{ l.label }}</a></li>{% endfor %}
        </ul>
        {% endif %}
        {% if e.need and e.need != "" %}<p class="gap-need">还缺：{{ e.need }}</p>{% endif %}
        {% if e.note and e.note != "" %}<p class="gap-note">{{ e.note }}</p>{% endif %}
      </li>
      {% endfor %}
    </ul>
  </section>

  <section class="key-window-panel" id="gap">
    <header><div><p>Gap</p><h3>缺口：文档里有，但没有链接</h3></div><span>{{ gap | size }} 条</span></header>
    <ul class="gap-list">
      {% for e in gap %}
      <li class="gap-item" id="{{ e.id }}">
        <p><strong>{{ e.title }}</strong> <span class="gap-tag">{% if e.doc == "recruit" %}招聘{% else %}实体{% endif %}</span>{% if e.priority and e.priority != "" %} <span class="gap-tag">优先级 {{ e.priority }}</span>{% endif %}</p>
        <p class="gap-meta">{{ e.period }}{% if e.people.size > 0 %} · {{ e.people | join: "、" }}{% endif %}</p>
        {% if e.posts.size > 0 %}
        <p class="gap-related">相关站内文章：{% for pf in e.posts %}{% assign p = site.posts | where_exp: "x", "x.path contains pf" | first %}{% if p %}<a href="{{ p.url | relative_url }}">{{ p.title }}</a>{% endif %}{% endfor %}</p>
        {% endif %}
        {% if e.need and e.need != "" %}<p class="gap-need">还缺：{{ e.need }}</p>{% endif %}
        {% if e.note and e.note != "" %}<p class="gap-note">{{ e.note }}</p>{% endif %}
      </li>
      {% endfor %}
    </ul>
  </section>

  <section class="key-window-panel" id="in-site">
    <header><div><p>In site</p><h3>已收录（对照用）</h3></div><span>{{ in_site | size }} 条</span></header>
    <ul class="gap-list">
      {% for e in in_site %}
      <li class="gap-item" id="{{ e.id }}">
        <p><strong>{{ e.title }}</strong> <span class="gap-tag">{% if e.doc == "recruit" %}招聘{% else %}实体{% endif %}</span></p>
        <p class="gap-meta">{{ e.period }}</p>
        {% if e.posts.size > 0 %}
        <p class="gap-related">{% for pf in e.posts %}{% assign p = site.posts | where_exp: "x", "x.path contains pf" | first %}{% if p %}<a href="{{ p.url | relative_url }}">{{ p.title }}</a>{% endif %}{% endfor %}</p>
        {% endif %}
        {% if e.note and e.note != "" %}<p class="gap-note">{{ e.note }}</p>{% endif %}
      </li>
      {% endfor %}
    </ul>
  </section>

  <section class="key-window-panel" id="excluded">
    <header><div><p>Not placed</p><h3>文档里有，但按收录原则不占位</h3></div></header>
    <ul class="gap-list">
      {% for x in gaps.excluded %}<li>{{ x }}</li>{% endfor %}
    </ul>
  </section>
</section>
