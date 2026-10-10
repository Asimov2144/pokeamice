---
layout: timeline
title: "资料时间线"
permalink: /timeline/
search: false
---
{%- comment -%}
The library laid out along the years: which year each interview, magazine scan, official topic and
Game Freak blog belongs to, against the games that came out. The numbers, the eras and each year's
picks are baked into _data/timeline.yml by tools/build-timeline.py; the chart is plain HTML and CSS
(a column per year, the documents stacked above the line, the blogs hung below it, the games under
the year), each column a link to /timeline/<year>/ (_includes/timeline-year.html).
{%- endcomment -%}
{% assign tl = site.data.timeline %}
{% assign first_y = tl.span[0] %}
{% assign last_y = tl.span[1] %}
<div class="tl tl--index">
  <header class="library__head tl-intro">
    <p class="library__eyebrow">Key docs · 时间线</p>
    <h1 class="library__title">资料时间线</h1>
    <p class="library__lead">{{ first_y }} 到 {{ last_y }}：<b>{{ tl.totals.docs }}</b> 篇访谈、杂志扫描和官方专题，外加 <b>{{ tl.totals.stream }}</b> 篇 Game Freak 的博客，各自落在发表的那一年，旁边是那一年发售的作品。点一年进去，按月份读。</p>
    <div class="library__stats">
      <span class="is-interview"><i class="tl-dot"></i>访谈翻译 <b>{{ tl.totals.interview }}</b></span>
      <span class="is-scan"><i class="tl-dot"></i>杂志扫描 <b>{{ tl.totals.scan }}</b></span>
      <span class="is-topic"><i class="tl-dot"></i>官方专题 <b>{{ tl.totals.topic }}</b></span>
      <span class="is-article"><i class="tl-dot"></i>文章 <b>{{ tl.totals.article }}</b></span>
      <span class="is-stream"><i class="tl-dot"></i>博客 <b>{{ tl.totals.stream }}</b></span>
    </div>
  </header>

  <section class="tl-chart" aria-label="每年收录的数量">
    <div class="tl-chart__scroll">
      <div class="tl-chart__inner" style="--n: {{ last_y | minus: first_y | plus: 1 }}">
        <div class="tl-chart__eras">
          {% for e in tl.eras %}<a class="tl-chart__era is-e{{ forloop.index0 | modulo: 2 }}" href="#era-{{ forloop.index }}" style="grid-column: span {{ e.to | minus: e.from | plus: 1 }}"><span>{{ e.label }}</span></a>{% endfor %}
        </div>
        <div class="tl-chart__cols">
          {% for e in tl.eras %}{% for y in tl.years %}{% if y.year >= e.from and y.year <= e.to %}
          {% assign has = false %}{% if y.docs > 0 or y.stream > 0 %}{% assign has = true %}{% endif %}
          {% capture tip %}{{ y.year }}：{% if y.docs > 0 %}{{ y.docs }} 篇文献{% endif %}{% if y.stream > 0 %}{% if y.docs > 0 %}，{% endif %}{{ y.stream }} 篇博客{% endif %}{% unless has %}暂无收录{% endunless %}{% if y.games.size > 0 %}｜作品：{% for g in y.games %}{{ g.title }}{% unless forloop.last %}、{% endunless %}{% endfor %}{% endif %}{% endcapture %}
          <{% if has %}a href="{{ '/timeline/' | append: y.year | append: '/' | relative_url }}"{% else %}span{% endif %} class="tl-col is-e{{ forloop.parentloop.index0 | modulo: 2 }}{% unless has %} is-empty{% endunless %}" title="{{ tip | strip }}">
            <span class="tl-col__docs">
              {% if y.kinds.interview > 0 %}<i class="is-interview" style="height: {{ y.kinds.interview | times: 2 }}px"></i>{% endif %}
              {% if y.kinds.scan > 0 %}<i class="is-scan" style="height: {{ y.kinds.scan | times: 2 }}px"></i>{% endif %}
              {% if y.kinds.topic > 0 %}<i class="is-topic" style="height: {{ y.kinds.topic | times: 2 }}px"></i>{% endif %}
              {% if y.kinds.article > 0 %}<i class="is-article" style="height: {{ y.kinds.article | times: 2 }}px"></i>{% endif %}
            </span>
            <span class="tl-col__stream">{% if y.stream > 0 %}<i style="height: {{ y.stream | times: 0.25 }}px"></i>{% endif %}</span>
            <b class="tl-col__y">{{ y.year | modulo: 100 | prepend: '00' | slice: -2, 2 }}</b>
            <span class="tl-col__games">{% assign shown = 0 %}{% for g in y.games %}{% if shown < 3 %}{% if g.icon %}<img src="{{ g.icon | relative_url }}" alt="" width="18" height="18" loading="lazy">{% else %}<i class="tl-game__dot"></i>{% endif %}{% assign shown = shown | plus: 1 %}{% endif %}{% endfor %}{% if y.games.size > 3 %}<em>+{{ y.games.size | minus: 3 }}</em>{% endif %}</span>
          </{% if has %}a{% else %}span{% endif %}>
          {% endif %}{% endfor %}{% endfor %}
        </div>
      </div>
    </div>
    <p class="tl-chart__key">
      <span class="is-interview"><i></i>访谈翻译</span><span class="is-scan"><i></i>杂志扫描</span><span class="is-topic"><i></i>官方专题</span><span class="is-article"><i></i>文章</span>
      <span class="is-stream"><i></i>线下是 Game Freak 博客（按四分之一比例）</span><span class="is-game"><i></i>年份下的图标是那一年有制作名单的作品</span>
    </p>
  </section>

  <nav class="tl-eranav" aria-label="按时代跳转">
    {% for e in tl.eras %}<a href="#era-{{ forloop.index }}"><b>{{ e.label }}</b><span>{{ e.from }}–{{ e.to }} · {{ e.docs }} 篇</span></a>{% endfor %}
  </nav>

  {% for e in tl.eras %}
  <section class="tl-era" id="era-{{ forloop.index }}">
    <header class="tl-era__head">
      <p class="tl-era__range">{{ e.from }} – {{ e.to }}</p>
      <h2 class="tl-era__title">{{ e.label }}</h2>
      <p class="tl-era__sum"><b>{{ e.docs }}</b> 篇文献{% if e.stream > 0 %} · <b>{{ e.stream }}</b> 篇博客{% endif %}</p>
      {% if e.games.size > 0 %}
      <div class="tl-chips tl-era__games">
        {% for g in e.games %}<a class="tl-game" href="{{ '/credits/' | append: g.slug | append: '/' | relative_url }}" title="{{ g.title }} · {{ g.year }} · 制作名单">{% if g.icon %}<img src="{{ g.icon | relative_url }}" alt="" width="20" height="20" loading="lazy">{% if g.icon2 %}<img src="{{ g.icon2 | relative_url }}" alt="" width="20" height="20" loading="lazy">{% endif %}{% else %}<i class="tl-game__dot"></i>{% endif %}<span>{{ g.title }}</span></a>{% endfor %}
      </div>
      {% endif %}
      {% if e.people.size > 0 %}
      <div class="tl-chips tl-era__people"><span class="tl-chips__label">谈得最多</span>{% for p in e.people %}<a class="tl-chip" href="{{ '/people/' | append: p.slug | append: '/' | relative_url }}">{% include person-name.html person=p.slug %} <b>{{ p.n }}</b></a>{% endfor %}</div>
      {% endif %}
    </header>

    <ol class="tl-years">
      {% for y in tl.years %}{% if y.year >= e.from and y.year <= e.to %}{% if y.docs > 0 or y.stream > 0 %}
      <li class="tl-year" id="y{{ y.year }}">
        <a class="tl-year__head" href="{{ '/timeline/' | append: y.year | append: '/' | relative_url }}">
          <span class="tl-year__n">{{ y.year }}</span>
          <span class="tl-year__count">{% if y.docs > 0 %}<b>{{ y.docs }}</b> 篇文献{% endif %}{% if y.stream > 0 %}{% if y.docs > 0 %}<br>{% endif %}<b>{{ y.stream }}</b> 篇博客{% endif %}</span>
          <span class="tl-year__go" aria-hidden="true">进入 →</span>
        </a>
        <div class="tl-year__main">
          {% if y.games.size > 0 %}
          <div class="tl-chips tl-year__games">{% for g in y.games %}<a class="tl-game" href="{{ '/credits/' | append: g.slug | append: '/' | relative_url }}" title="{{ g.title }} · 制作名单">{% if g.icon %}<img src="{{ g.icon | relative_url }}" alt="" width="18" height="18" loading="lazy">{% if g.icon2 %}<img src="{{ g.icon2 | relative_url }}" alt="" width="18" height="18" loading="lazy">{% endif %}{% else %}<i class="tl-game__dot"></i>{% endif %}<span>{{ g.title }}</span></a>{% endfor %}</div>
          {% endif %}
          {% if y.picks.size > 0 %}
          <div class="tl-picks">
            {% for pk in y.picks %}
            <a class="tl-pick is-{{ pk.kind }}" href="{{ pk.url | relative_url }}">
              {% if pk.cover %}<span class="tl-pick__cover"><img src="{{ pk.cover | relative_url }}" alt="" loading="lazy" decoding="async"></span>{% endif %}
              <span class="tl-pick__body">
                <small>{% case pk.kind %}{% when "interview" %}访谈翻译{% when "scan" %}杂志扫描{% when "topic" %}官方专题{% else %}文章{% endcase %}{% if pk.pub != "" %} · {{ pk.pub }}{% endif %}</small>
                <strong>{{ pk.title }}</strong>
                {% if pk.blurb %}<em>{{ pk.blurb }}</em>{% endif %}
              </span>
            </a>
            {% endfor %}
          </div>
          {% else %}
          <p class="tl-year__note">这一年收的是 Game Freak 的博客，没有访谈或杂志。</p>
          {% endif %}
        </div>
      </li>
      {% endif %}{% endif %}{% endfor %}
    </ol>
  </section>
  {% endfor %}
</div>
