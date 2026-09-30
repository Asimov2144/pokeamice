---
layout: timeline
title: "按游戏读"
permalink: /games/
search: false
---
{%- comment -%}
The library by game: the works of the series in the order they came out, by generation, each with
how many documents talk about it, what kind, and three to read first. The numbers and the picks are
baked into _data/hubs.yml by tools/build-hubs.py (entities.works decides what a post is about; the
Game Freak blogs name games in passing, so they are counted apart). "检索全部" opens the search page
already filtered to the game.
{%- endcomment -%}
{% assign gm = site.data.hubs.games %}
<div class="tl tl--hub tl--games">
  <header class="library__head tl-intro">
    <p class="library__eyebrow">Key docs · 横切专题</p>
    <h1 class="library__title">按游戏读</h1>
    <p class="library__lead">想知道某一作是怎么做出来的：<b>{{ gm.n }}</b> 部作品按发售顺序排开，每部列出谈到它的访谈、杂志扫描和文章的数量，再挑三篇先读。一篇文献可以同时谈几部作品，所以各作的数字加起来比 <b>{{ gm.docs }}</b> 大。</p>
    <div class="tl-chips hub-top">
      <span class="tl-chips__label">谈得最多</span>
      {% for t in gm.top %}<a class="tl-game" href="#{{ t.id }}">{% if t.icon %}<img src="{{ t.icon | relative_url }}" alt="" width="20" height="20" loading="lazy">{% if t.icon2 %}<img src="{{ t.icon2 | relative_url }}" alt="" width="20" height="20" loading="lazy">{% endif %}{% endif %}<span>{{ t.name | remove_first: "宝可梦 " }}</span> <b>{{ t.docs }}</b></a>{% endfor %}
    </div>
  </header>

  <nav class="tl-eranav" aria-label="按世代跳转">
    {% for g in gm.groups %}<a href="#grp-{{ g.key }}"><b>{{ g.label }}</b><span>{% if g.from %}{{ g.from }}{% if g.to != g.from %}–{{ g.to }}{% endif %} · {% endif %}{{ g.docs }} 篇</span></a>{% endfor %}
  </nav>

  {% for g in gm.groups %}
  <section class="tl-era" id="grp-{{ g.key }}">
    <header class="tl-era__head">
      {% if g.from %}<p class="tl-era__range">{{ g.from }}{% if g.to != g.from %} – {{ g.to }}{% endif %}</p>{% endif %}
      <h2 class="tl-era__title">{{ g.label }}</h2>
      <p class="hub-note">{{ g.sub }}</p>
      <p class="tl-era__sum"><b>{{ g.docs }}</b> 篇文献</p>
      {% if g.people.size > 0 %}
      <div class="tl-chips tl-era__people"><span class="tl-chips__label">谈得最多</span>{% for p in g.people %}<a class="tl-chip" href="{{ '/people/' | append: p.slug | append: '/' | relative_url }}">{{ p.name }} <b>{{ p.n }}</b></a>{% endfor %}</div>
      {% endif %}
    </header>
    <div class="hub-games">
      {% for c in g.games %}
      <article class="hub-game" id="{{ c.id }}"{% if c.color %} style="--hg-c: {{ c.color }}; --hg-c2: {{ c.color2 | default: c.color }}"{% endif %}>
        <header class="hub-game__head">
          <span class="hub-game__icons">{% if c.icon %}<img src="{{ c.icon | relative_url }}" alt="" width="40" height="40" loading="lazy">{% if c.icon2 %}<img src="{{ c.icon2 | relative_url }}" alt="" width="40" height="40" loading="lazy">{% endif %}{% else %}<i class="tl-game__dot"></i>{% endif %}</span>
          <div class="hub-game__title">
            <h3>{{ c.name | remove_first: "宝可梦 " }}</h3>
            <p>{% if c.year %}{{ c.year }} · {% endif %}<b>{{ c.docs }}</b> 篇文献{% if c.span and c.span[0] != c.span[1] %} · {{ c.span[0] }}–{{ c.span[1] }}{% endif %}</p>
          </div>
        </header>
        <p class="hub-game__kinds">
          {% if c.kinds.interview > 0 %}<span class="is-interview"><i class="tl-dot"></i>访谈 <b>{{ c.kinds.interview }}</b></span>{% endif %}
          {% if c.kinds.scan > 0 %}<span class="is-scan"><i class="tl-dot"></i>扫描 <b>{{ c.kinds.scan }}</b></span>{% endif %}
          {% if c.kinds.topic > 0 %}<span class="is-topic"><i class="tl-dot"></i>专题 <b>{{ c.kinds.topic }}</b></span>{% endif %}
          {% if c.kinds.article > 0 %}<span class="is-article"><i class="tl-dot"></i>文章 <b>{{ c.kinds.article }}</b></span>{% endif %}
          {% if c.blogs > 0 %}<span class="is-stream"><i class="tl-dot"></i>博客提到 <b>{{ c.blogs }}</b></span>{% endif %}
        </p>
        {% if c.picks.size > 0 %}
        <ol class="hub-game__picks">
          {% for pk in c.picks %}
          <li class="is-{{ pk.kind }}"><a href="{{ pk.url | relative_url }}"><small>{{ pk.date | slice: 0, 4 }}{% if pk.pub != "" %} · {{ pk.pub }}{% endif %}</small><span>{{ pk.title }}</span></a></li>
          {% endfor %}
        </ol>
        {% endif %}
        <footer class="hub-game__foot">
          <a href="{{ '/search/' | relative_url }}?work={{ c.name | url_encode }}">在检索里看全部 {{ c.docs | plus: c.blogs }} 篇 →</a>
          {% if c.credits %}<a href="{{ '/credits/' | append: c.credits | append: '/' | relative_url }}">制作名单</a>{% endif %}
        </footer>
      </article>
      {% endfor %}
    </div>
  </section>
  {% endfor %}

  <p class="tl-foot">“文献”指访谈翻译、杂志扫描、官方专题和文章，不含 Game Freak 的博客。同一部电影在数据里有几个名字（例如《超梦的逆袭》），这里合在一起数。想看海外媒体怎么谈这些作品，去 <a href="{{ '/overseas/' | relative_url }}">海外媒体专访</a>。</p>
</div>
