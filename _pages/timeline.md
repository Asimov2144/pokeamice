---
layout: timeline
title: "资料时间线"
permalink: /timeline/
search: false
---
{%- comment -%}
资料时间线 as a desk calendar (2026-10 redesign, design/timeline-redesign-2026-10/):
the top sheet is the reader's today (time of day, season, 历史上的今天 from feed-days.json),
then one torn-off sheet per year, oldest first, under six era tabs. Behind the sheets each
generation's cover legends stand as silhouettes in its version colours
(_data/timeline_covers.yml, assets/img/timeline/legends/); assets/js/timeline-calendar.js
cross-fades them as the reader scrolls through the years, slides each year's speakers past,
and sets the time of day and the season. Without the script the page reads as a plain
list of years in daylight.
{%- endcomment -%}
{%- assign tl = site.data.timeline -%}
{%- assign covers = site.data.timeline_covers -%}
{%- assign tl_by_year = site.posts | group_by_exp: "p", "p.date | date: '%Y'" -%}
{%- include timeline-counts.html posts=site.posts -%}
{%- assign total_docs = tlc_docs -%}{%- assign total_blogs = tlc_stream -%}
{%- assign first_y = tl.span[0] -%}{%- assign last_y = tl.span[1] -%}
{%- assign art = '/assets/img/timeline/' | relative_url -%}
<div class="tlc" data-tlc-root data-feed="{{ '/assets/js/feed-days.json' | relative_url }}" data-art="{{ art }}">
  <div class="tlc-backdrop" aria-hidden="true"><div class="tlc-backdrop__stage">
    {%- for g in covers %}
    <div class="tlc-gen{% if forloop.last %} is-on{% endif %}" data-tlc-gen="{{ g.gen }}" data-from="{{ g.from }}" data-to="{{ g.to }}" data-c1="{{ g.colors[0] }}" data-c2="{{ g.colors[1] }}" style="--c1: {{ g.colors[0] }}; --c2: {{ g.colors[1] }}">
      {%- for lg in g.legends %}<i class="tlc-legend tlc-legend--{{ forloop.index }}" data-head="{{ lg.head }}" style="--src: url('{{ art }}legends/{{ lg.dex }}.png')"></i>{% endfor %}
    </div>
    {%- endfor %}
  </div></div>

  <div class="tlc-desk">
    <div class="tlc-rings" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
    <section class="tlc-today" aria-labelledby="tlc-today-date" data-tlc-today>
      <div class="tlc-sky" data-tod="day">
        <p class="tlc-sky__tod" data-tlc-tod>DAY · 白天</p>
        <h1 class="tlc-sky__date"><span id="tlc-today-date" data-tlc-date>资料时间线</span><small data-tlc-weekday></small></h1>
        <p class="tlc-sky__season"><img src="{{ art }}deerling-spring.png" alt="" width="22" height="36" data-tlc-season-img><span data-tlc-season>{{ first_y }} — {{ last_y }}</span></p>
        <img class="tlc-sky__actor" src="{{ art }}espeon.png" alt="" data-tlc-actor>
      </div>
      <div class="tlc-today__body">
        <p class="tlc-k" data-tlc-otd-label>历史上的今天</p>
        <ul class="tlc-otd" data-tlc-otd><li class="tlc-otd__empty">按发表日期，把访谈、原刊和开发者手记放回当年。</li></ul>
        <p class="tlc-today__note" data-tlc-actor-note></p>
        <hr class="tlc-perf">
        <p class="tlc-facts"><span><b>{{ total_docs }}</b> 篇文献</span><span><b>{{ total_blogs }}</b> 篇博客</span><span><b>{{ last_y | minus: first_y | plus: 1 }}</b> 个年份</span><span>一页一年，从 {{ first_y }} 翻到 {{ last_y }}</span></p>
      </div>
    </section>

    <nav class="tlc-tabs" aria-label="按时代跳转" data-tlc-tabs>
      {%- for e in tl.eras %}{% assign era_key = e.from | append: "" %}{% assign era_copy = site.data.timeline_editorial[era_key] %}
      <a href="#era-{{ forloop.index }}" data-tlc-tab="{{ forloop.index }}" title="{{ era_copy.title | default: e.label }}"><b>{{ e.from | slice: 2, 2 }}–{{ e.to | slice: 2, 2 }}</b><span>{{ era_copy.title | default: e.label }}</span></a>
      {%- endfor %}
    </nav>

    {%- for e in tl.eras %}
    {%- assign era_key = e.from | append: "" %}{% assign era_copy = site.data.timeline_editorial[era_key] %}
    <section class="tlc-era" id="era-{{ forloop.index }}" data-tlc-era="{{ forloop.index }}">
      <header class="tlc-era__head">
        <p class="tlc-k">0{{ forloop.index }} · {{ e.from }} — {{ e.to }}</p>
        <h2>{{ era_copy.title | default: e.label }}</h2>
        {% if era_copy.note %}<p>{{ era_copy.note }}</p>{% endif %}
      </header>
      {%- for y in tl.years %}{% if y.year >= e.from and y.year <= e.to %}
      {%- assign row_year = y.year | append: "" %}{% assign row_group = tl_by_year | where: "name", row_year | first %}
      {%- include timeline-counts.html posts=row_group.items %}
      {%- if tlc_docs > 0 or tlc_stream > 0 %}
      {%- assign yg = nil %}{% for g in covers %}{% if y.year >= g.from and y.year <= g.to %}{% assign yg = g %}{% endif %}{% endfor %}
      {%- assign year_docs = tlc_documents | sort: "date" | reverse %}
      {%- assign year_url = '/timeline/' | append: y.year | append: '/' | relative_url %}
      <article class="tlc-sheet" id="y{{ y.year }}" data-tlc-year="{{ y.year }}" style="--c1: {{ yg.colors[0] }}; --c2: {{ yg.colors[1] }}">
        {%- assign li = y.year | minus: yg.from | modulo: yg.legends.size %}{% assign sl = yg.legends[li] %}
        <i class="tlc-sheet__legend" aria-hidden="true" data-head="{{ sl.head }}" style="--src: url('{{ art }}legends/{{ sl.dex }}.png')"></i>
        <div class="tlc-sheet__holes" aria-hidden="true"><i></i><i></i><i></i></div>
        <header class="tlc-sheet__head">
          <a class="tlc-sheet__year" href="{{ year_url }}">{{ y.year }}</a>
          <p class="tlc-sheet__count">{% if tlc_docs > 0 %}<b>{{ tlc_docs }}</b> 篇文献{% endif %}{% if tlc_stream > 0 %}{% if tlc_docs > 0 %}<br>{% endif %}<b>{{ tlc_stream }}</b> 篇博客{% endif %}</p>
          <p class="tlc-sheet__gen"><i aria-hidden="true"></i>{{ yg.label }}{% if yg.legends.size > 0 %} · {% for lg in yg.legends %}{{ lg.name }}{% unless forloop.last %}／{% endunless %}{% endfor %}{% endif %}</p>
        </header>
        {%- if y.games.size > 0 %}
        <p class="tlc-works">{% for g in y.games %}<a href="{{ '/credits/' | append: g.slug | append: '/' | relative_url }}" title="{{ g.title }} · 制作名单">{% if g.icon %}<img src="{{ g.icon | relative_url }}" alt="" width="20" height="20" loading="lazy">{% if g.icon2 %}<img src="{{ g.icon2 | relative_url }}" alt="" width="20" height="20" loading="lazy">{% endif %}{% endif %}<span>{{ g.title | remove_first: "宝可梦 " }}</span></a>{% endfor %}</p>
        {%- endif %}
        {%- if y.people.size > 0 %}
        <div class="tlc-passers" aria-label="{{ y.year }} 年说话的人"><div class="tlc-passers__row" data-tlc-passers>
          {%- for who in y.people limit: 12 %}{% assign pr = site.data.people | where: "slug", who.slug | first %}
          <a href="{{ '/people/' | append: who.slug | append: '/' | relative_url }}" class="tlc-passer">{% if pr.avatar %}<img src="{{ pr.avatar | relative_url }}" alt="" width="26" height="26" loading="lazy">{% else %}<i aria-hidden="true">{{ who.name | slice: 0, 1 }}</i>{% endif %}<span>{{ who.name }}</span></a>
          {%- endfor %}
        </div></div>
        {%- endif %}
        {%- if y.picks.size > 0 %}
        <ol class="tlc-entries" data-tlc-picks>
          {%- for r in y.picks %}{% if forloop.first %}{% assign role = "rep" %}{% else %}{% assign role = "pick" %}{% endif %}{% include timeline-pick.html row=r role=role %}{% endfor %}
          {%- for r in y.pool %}{% include timeline-pick.html row=r role="pool" hidden=true %}{% endfor %}
        </ol>
        {%- elsif year_docs.size > 0 %}
        <ol class="tlc-entries">{% for p in year_docs limit: 3 %}{% include timeline-entry.html post=p compact=true %}{% endfor %}</ol>
        {%- else %}
        <p class="tlc-sheet__note">这一年的记录，留在开发者博客里。</p>
        {%- endif %}
        <footer class="tlc-sheet__foot">{% if y.pool.size > 1 %}<button type="button" class="tlc-shuffle" data-tlc-shuffle hidden>换几篇</button>{% endif %}<a href="{{ year_url }}">读这一年{% if tlc_docs > 3 %}的 {{ tlc_docs }} 篇{% endif %} <span aria-hidden="true">↗</span></a></footer>
      </article>
      {%- endif %}{% endif %}{% endfor %}
    </section>
    {%- endfor %}
    <p class="tlc-end">翻到这里是 {{ last_y }} 年。之后的事，还没有发生。</p>
  </div>

  <details class="tlc-jump" data-tlc-jump>
    <summary aria-label="跳到某一年"><img src="{{ art }}celebi.png" alt="" width="44" height="40"><span>跳到某一年</span></summary>
    <nav class="tlc-jump__years" aria-label="年份">
      {%- for y in tl.years %}{% assign jy = y.year | append: "" %}{% assign jg = tl_by_year | where: "name", jy | first %}{% if jg.items.size > 0 %}{% assign yg = nil %}{% for g in covers %}{% if y.year >= g.from and y.year <= g.to %}{% assign yg = g %}{% endif %}{% endfor %}<a href="#y{{ y.year }}" style="--c1: {{ yg.colors[0] }}">{{ y.year }}</a>{% endif %}{% endfor %}
    </nav>
  </details>
</div>
