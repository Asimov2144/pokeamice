---
layout: library
title: "长文分析"
permalink: /long-analysis/
---
{%- comment -%}
The dedicated page for 2144jx's long articles (category 长文分析): PV frame-by-frame readings,
design and model studies, gameplay essays, trip and site notes. Sections are cut by tag;
whatever no section claims lands in the last one. The short posts live at /notes/weibo/.
{%- endcomment -%}
{% assign la = site.posts | where_exp: "p", "p.categories contains '长文分析'" %}
{% assign la_pv = "" | split: "" %}{% assign la_design = "" | split: "" %}{% assign la_cards = "" | split: "" %}{% assign la_other = "" | split: "" %}
{% for p in la %}
  {% if p.tags contains "逐帧分析" %}{% assign la_pv = la_pv | push: p %}
  {% elsif p.tags contains "设定分析" or p.tags contains "模型" %}{% assign la_design = la_design | push: p %}
  {% elsif p.tags contains "宝可梦卡牌" or p.tags contains "J联赛" %}{% assign la_cards = la_cards | push: p %}
  {% else %}{% assign la_other = la_other | push: p %}{% endif %}
{% endfor %}

<header class="library__head">
  <p class="library__eyebrow">Long reads · 长文分析</p>
  <h1 class="library__title">长文分析</h1>
  <p class="library__lead">站主 2144jx 的原创长文：PV 逐帧分析、设定与模型考察、玩法与开发体制的推演，还有巡礼和建站笔记。原发布在微博头条文章（专栏「宝可梦友会」），这里存档并配上图片；文中的猜想写在当时的信息之下，有出入时请以资料室正文为准。</p>
  <p class="library__facts"><b>{{ la.size }}</b> 篇{% if la.size > 0 %} · {{ la.last.date | date: "%Y" }}–{{ la.first.date | date: "%Y" }}{% endif %} · <a href="{{ '/notes/weibo/' | relative_url }}">随手发的碎片（微博存档）→</a> · <a href="{{ '/keys/' | relative_url }}">资料窗口 →</a></p>
</header>

{% if la_pv.size > 0 %}
<section class="library__section" aria-label="PV 逐帧分析">
  <p class="library__eyebrow">逐帧分析 · {{ la_pv.size }}</p>
  <div class="feed__cards">{% for post in la_pv %}{% include entry-card.html card_post=post compact=true %}{% endfor %}</div>
</section>
{% endif %}
{% if la_design.size > 0 %}
<section class="library__section" aria-label="设定与模型考察">
  <p class="library__eyebrow">设定与模型考察 · {{ la_design.size }}</p>
  <div class="feed__cards">{% for post in la_design %}{% include entry-card.html card_post=post compact=true %}{% endfor %}</div>
</section>
{% endif %}
{% if la_other.size > 0 %}
<section class="library__section" aria-label="玩法、随笔、巡礼与站点">
  <p class="library__eyebrow">玩法 · 随笔 · 巡礼 · 站点 · {{ la_other.size }}</p>
  <div class="feed__cards">{% for post in la_other %}{% include entry-card.html card_post=post compact=true %}{% endfor %}</div>
</section>
{% endif %}
{% if la_cards.size > 0 %}
<section class="library__section" aria-label="卡牌与 J 联赛">
  <p class="library__eyebrow">卡牌与 J 联赛 · {{ la_cards.size }}</p>
  <div class="feed__cards">{% for post in la_cards %}{% include entry-card.html card_post=post compact=true %}{% endfor %}</div>
</section>
{% endif %}
