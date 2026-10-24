---
layout: library
title: "站主笔记"
permalink: /notes/
---
{%- comment -%}
The keeper's own writing: the long articles (category 长文分析) and the short posts (/notes/weibo/).
{%- endcomment -%}
<link rel="stylesheet" href="{{ '/assets/css/home-recent.css' | relative_url }}">
{% assign la = site.posts | where_exp: "p", "p.categories contains '长文分析'" %}
<header class="library__head">
  <p class="library__eyebrow">Notes · 站主笔记</p>
  <h1 class="library__title">站主笔记</h1>
  <p class="library__lead">2144jx 自己写的东西，不是资料转录：长文把一件事想透，碎片是随手记下的观察和猜想。它们原来发在微博，这里存档、配图、重新排版。</p>
</header>
<section class="nb nb--page" aria-label="两个入口">
  <a class="nb-card nb-card--long" href="{{ '/long-analysis/' | relative_url }}">
    <img src="{{ '/assets/img/topics/long-analysis.jpg' | relative_url }}" alt="" width="336" height="192" loading="lazy" decoding="async">
    <span class="nb-card__text">
      <span class="nb-kicker"><i class="fas fa-chart-line" aria-hidden="true"></i>专题</span>
      <strong>长文分析</strong>
      <em>PV 逐帧分析、设定与模型考察、玩法推演、巡礼与建站笔记——{{ la.size }} 篇</em>
    </span>
  </a>
  <a class="nb-card nb-card--frag" href="{{ '/notes/weibo/' | relative_url }}">
    <span class="nb-stickers" aria-hidden="true" data-covers="{{ '/assets/data/weibo-covers.json' | relative_url }}">
      <img src="https://gallery.pokeamice.com/pokemon-assets/pokemon-home/pokemon-home--0025.png" alt="" loading="lazy">
      <img src="{{ '/assets/img/works/home-legends-arceus.png' | relative_url }}" alt="" loading="lazy">
      <img src="https://gallery.pokeamice.com/pokemon-assets/pokemon-home/pokemon-home--0133.png" alt="" loading="lazy">
      <img src="{{ '/assets/img/works/home-scarlet.png' | relative_url }}" alt="" loading="lazy">
    </span>
    <span class="nb-card__text">
      <span class="nb-kicker"><i class="fas fa-note-sticky" aria-hidden="true"></i>碎片</span>
      <strong>微博存档</strong>
      <em>近千条随手发的东西，按时间摊开，可按作品和宝可梦筛选</em>
      <small class="nb-pick" hidden></small>
    </span>
  </a>
</section>
<script src="{{ '/assets/js/home-notes-covers.js' | relative_url }}" defer></script>
<section class="rc" aria-label="最新长文">
  <section class="rc-day">
    <header class="rc-dayhead"><b>最新长文</b><span class="rc-tally"><a href="{{ '/long-analysis/' | relative_url }}">全部 {{ la.size }} 篇 →</a></span></header>
    <div class="rc-grid">{% for post in la limit: 8 %}{% include home-recent-card.html post=post %}{% endfor %}</div>
  </section>
</section>
