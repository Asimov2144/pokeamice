---
layout: library
title: "站点动态"
crumb: 站点动态
permalink: /news/
---
{%- comment -%}
News: the keeper's own news - batches finished, tidy-ups, features, calls for pages (_data/feed.yml,
written by hand, newest first). Not the list of new entries (that is 近期发布 on the home page) and not
the day-by-day stream with quotes and people (that is the resource window, /keys/).
{%- endcomment -%}
<link rel="stylesheet" href="{{ '/assets/css/home-tabs.css' | relative_url }}">
{% assign nw_items = site.data.feed | sort: "date" | reverse %}
{% assign nw_months = nw_items | group_by_exp: "i", "i.date | date: '%Y-%m'" %}
{% assign nw_log = site.posts | where_exp: "p", "p.categories contains '文档'" %}
{% assign nw_thresholds = "100,250,500,750,1000,1500,2000" | split: "," %}
{% assign nw_oldest = site.data.feed_log | reverse %}
{% assign nw_cum = 0 %}{% assign nw_passed = "," %}{% assign nw_ms = "" | split: "" %}
{% for e in nw_oldest %}{% assign nw_cum = nw_cum | plus: e.count %}{% for th in nw_thresholds %}{% assign th_n = th | plus: 0 %}{% assign th_key = "," | append: th | append: "," %}{% if nw_cum >= th_n %}{% unless nw_passed contains th_key %}{% assign nw_passed = nw_passed | append: th | append: "," %}{% assign nw_row = e.date | append: "|" | append: th %}{% assign nw_ms = nw_ms | push: nw_row %}{% endunless %}{% endif %}{% endfor %}{% endfor %}
{% assign nw_ms = nw_ms | reverse %}

<header class="library__head nw-head">
  <p class="library__eyebrow">News · 站点动态</p>
  <h1 class="library__title">站点动态</h1>
  <p class="library__lead">这个站自己的事：一批资料收完了、整理校对做完了、新功能上线了、在找哪些原刊。新进了哪些条目，看首页的<a href="{{ '/#recent-updates' | relative_url }}">近期发布</a>；按入库日的完整记录、今日一句和人物聚焦，在<a href="{{ '/keys/' | relative_url }}">资料窗口</a>。</p>
  <p class="library__facts"><b>{{ nw_items.size }}</b> 条动态 · {{ nw_items.last.date | date: "%Y-%m" }} 起 · <a href="{{ '/feed.xml' | relative_url }}"><i class="fas fa-rss" aria-hidden="true"></i> 订阅</a></p>
</header>

<div class="nw">
  <div class="nw-main">
  {% for m in nw_months %}
    <section class="nw-month">
      <h2 class="nw-monthhead">{{ m.name | date: "%Y 年 %-m 月" }}<span>{{ m.items | size }} 条</span></h2>
      {% for i in m.items %}
        {% assign nw_k = "动态" %}{% assign nw_kc = "misc" %}{% assign nw_ki = "fa-bullhorn" %}
        {% if i.title contains "征集" %}{% assign nw_k = "征集" %}{% assign nw_kc = "call" %}{% assign nw_ki = "fa-hand" %}
        {% elsif i.title contains "上线" or i.title contains "改版" or i.title contains "新功能" or i.title contains "多了" or i.title contains "有了" or i.title contains "成了" %}{% assign nw_k = "新功能" %}{% assign nw_kc = "feature" %}{% assign nw_ki = "fa-wand-magic-sparkles" %}
        {% elsif i.title contains "整理" or i.title contains "重排" or i.title contains "校对" or i.title contains "统一" or i.title contains "补回" or i.title contains "补齐" or i.title contains "合成" or i.title contains "清掉" or i.title contains "换成" %}{% assign nw_k = "整理" %}{% assign nw_kc = "tidy" %}{% assign nw_ki = "fa-broom" %}
        {% elsif i.title contains "收" or i.title contains "入库" %}{% assign nw_k = "收录" %}{% assign nw_kc = "ingest" %}{% assign nw_ki = "fa-box-archive" %}{% endif %}
        <article class="nw-item nw-k-{{ nw_kc }}">
          <div class="nw-item__body">
            <header class="nw-item__head">
              <time datetime="{{ i.date }}">{{ i.date | date: "%-m月%-d日" }}</time>
              <b class="nw-badge"><i class="fas {{ nw_ki }}" aria-hidden="true"></i>{{ nw_k }}</b>
            </header>
            <h3><a href="{{ i.url | relative_url }}">{{ i.title }}</a></h3>
            <p>{{ i.text }}</p>
            <a class="nw-go" href="{{ i.url | relative_url }}">{{ i.label | default: "看看 →" }}</a>
          </div>
          {% if i.cover %}<a class="nw-item__cover" href="{{ i.url | relative_url }}" tabindex="-1" aria-hidden="true"><img src="{{ i.cover | relative_url }}" alt="" loading="lazy" decoding="async"></a>{% endif %}
        </article>
      {% endfor %}
    </section>
  {% endfor %}
  </div>

  <aside class="nw-rail">
    <section class="nw-box">
      <h2><i class="fas fa-signs-post" aria-hidden="true"></i>哪里看什么</h2>
      <ul class="nw-where">
        <li><b>News · 本页</b><span>站点自己的事：批量收录、整理校对、新功能、征集</span></li>
        <li><a href="{{ '/#recent-updates' | relative_url }}"><b>近期发布</b></a><span>最近几天新进了哪些条目</span></li>
        <li><a href="{{ '/keys/' | relative_url }}"><b>资料窗口</b></a><span>按入库日的完整记录，今日一句、历史上的今天、人物聚焦</span></li>
        <li><a href="{{ '/#retrieval' | relative_url }}"><b>馆藏概览</b></a><span>馆藏由什么构成、缺什么</span></li>
        <li><a href="{{ '/about/' | relative_url }}"><b>关于本站</b></a><span>收什么、怎么做的、怎么引用、怎么搭的</span></li>
      </ul>
    </section>
    <section class="nw-box">
      <h2><i class="fas fa-flag-checkered" aria-hidden="true"></i>馆藏里程碑</h2>
      <ul class="nw-ms">
        {% for row in nw_ms %}{% assign f = row | split: "|" %}<li><b>{{ f[1] }}</b><span>条 · {{ f[0] | date: "%Y-%m-%d" }}</span></li>{% endfor %}
      </ul>
    </section>
    <section class="nw-box">
      <h2><i class="fas fa-clock-rotate-left" aria-hidden="true"></i>站点记录</h2>
      <ul class="nw-log">
        {% for p in nw_log limit: 6 %}<li><time datetime="{{ p.date | date: '%Y-%m-%d' }}">{{ p.date | date: "%Y-%m-%d" }}</time><a href="{{ p.url | relative_url }}">{{ p.title }}</a></li>{% endfor %}
      </ul>
    </section>
  </aside>
</div>
