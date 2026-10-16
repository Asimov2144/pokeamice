---
layout: timeline
title: "资料时间线"
permalink: /timeline/
search: false
---
{% assign tl = site.data.timeline %}
{% assign tl_by_year = site.posts | group_by_exp: "p", "p.date | date: '%Y'" %}
{% include timeline-counts.html posts=site.posts %}
{% assign total_docs = tlc_docs %}{% assign total_blogs = tlc_stream %}
{% assign first_y = tl.span[0] %}{% assign last_y = tl.span[1] %}
{% assign max_docs = 1 %}{% assign max_blogs = 1 %}
{% for tg in tl_by_year %}
  {% include timeline-counts.html posts=tg.items %}
  {% if tlc_docs > max_docs %}{% assign max_docs = tlc_docs %}{% endif %}
  {% if tlc_stream > max_blogs %}{% assign max_blogs = tlc_stream %}{% endif %}
{% endfor %}
{% assign featured = site.posts | where: "slug", "interview-time-satoshi-tajiri-ultimate-game-freak" | first %}
<div class="tl tl--index" data-tl-root>
  <header class="tl-hero">
    <div class="tl-hero__copy">
      <p class="tl-eyebrow">Poke Amice / Chronicle <span>{{ first_y }} — {{ last_y }}</span></p>
      <h1>资料时间线<span>在当年的声音里，<br>重读宝可梦。</span></h1>
      <p class="tl-hero__lead">一段访谈、一页原刊、一篇开发者手记。<br class="tl-desktop-break">把它们放回发表的那一年，沿着时间继续读。</p>
      <div class="tl-hero__facts"><span><b data-tl-total-docs>{{ total_docs }}</b> 篇文献</span><span><b data-tl-total-stream>{{ total_blogs }}</b> 篇博客</span><span>{{ last_y | minus: first_y | plus: 1 }} 个年份</span></div>
      <a class="tl-text-link" href="#chronicle">翻开年代目录 <span aria-hidden="true">↓</span></a>
    </div>
    {% if featured %}
    {% assign feature_image = featured.image | default: featured.featured_image | default: "" %}
    {% if feature_image == "" %}{% assign feature_pics = featured.parallel_items | where: "type", "image" %}{% assign feature_image = feature_pics.first.image | default: feature_pics.first.src | default: "" %}{% endif %}
    {% assign feature_portrait = false %}{% if feature_image == "" %}{% include person-avatar.html who="田尻智" post=featured %}{% assign feature_image = pa_src %}{% assign feature_portrait = true %}{% assign feature_portrait_record = pa_hit.portraits | where: "image", pa_src | first %}{% assign feature_portrait_source = feature_portrait_record.source | default: pa_hit.avatar_source %}{% endif %}
    <a class="tl-feature" href="{{ featured.url | relative_url }}">
      <span class="tl-feature__folio">档案选读 <span>No. 1999 / TIME</span></span>
      {% if feature_image != "" %}<span class="tl-feature__image"><img src="{{ feature_image | relative_url }}" alt="" width="460" height="240" fetchpriority="high" decoding="async"></span>{% endif %}
      {% if feature_portrait and feature_image != "" %}<span class="tl-feature__image-note">人物资料图：田尻智{% if feature_portrait_source %} · {{ feature_portrait_source | escape }}{% endif %}</span>{% endif %}
      <span class="tl-feature__body"><span class="tl-feature__date">1999.11.22 · 田尻智 × TIME</span><strong>{{ featured.display_title | default: featured.title }}</strong><span class="tl-feature__caption">从昆虫少年到 Game Freak，读一篇留下来的对话。</span><span class="tl-feature__read">进入访谈 <span aria-hidden="true">↗</span></span></span>
    </a>
    {% endif %}
  </header>
  <section class="tl-chart" aria-labelledby="tl-chart-title">
    <div class="tl-section-label"><h2 id="tl-chart-title">年度收录分布</h2><p>文献在上，博客在下；点击年份进入档案。</p></div>
    <div class="tl-chart__scroll" tabindex="0" role="region" aria-label="年度数量图，可横向滚动">
      <div class="tl-chart__inner" style="--n: {{ last_y | minus: first_y | plus: 1 }}">
        {% for y in tl.years %}
        {% assign chart_year = y.year | append: "" %}
        {% assign chart_group = tl_by_year | where: "name", chart_year | first %}
        {% include timeline-counts.html posts=chart_group.items %}
        {% assign has_entries = false %}{% if tlc_docs > 0 or tlc_stream > 0 %}{% assign has_entries = true %}{% endif %}
        <{% if has_entries %}a href="{{ '/timeline/' | append: y.year | append: '/' | relative_url }}"{% else %}span{% endif %} class="tl-column{% unless has_entries %} is-empty{% endunless %}"{% if has_entries %} aria-label="{{ y.year }} 年：{{ tlc_docs }} 篇文献，{{ tlc_stream }} 篇博客"{% endif %} title="{{ y.year }} · {{ tlc_docs }} 篇文献 / {{ tlc_stream }} 篇博客" data-tl-chart-year="{{ y.year }}" data-docs="{{ tlc_docs }}" data-stream="{{ tlc_stream }}">
          <span class="tl-column__docs" aria-hidden="true"><i style="--bar: {{ tlc_docs | times: 100.0 | divided_by: max_docs }}%"></i></span>
          <span class="tl-column__year">{{ y.year }}</span>
          <span class="tl-column__blogs" aria-hidden="true"><i style="--bar: {{ tlc_stream | times: 100.0 | divided_by: max_blogs }}%"></i></span>
        </{% if has_entries %}a{% else %}span{% endif %}>
        {% endfor %}
      </div>
    </div>
    <p class="tl-chart__note"><span><i></i>文献</span><span><i class="is-blog"></i>博客</span><span>两组柱高分别按各自最多的年份缩放，不用于直接比较文献与博客数量。</span><span class="tl-chart__hint">左右滑动查看年份 →</span></p>
  </section>
  <div class="tl-catalogue" id="chronicle">
    <aside class="tl-side">
      <div class="tl-side__inner">
        <p class="tl-side__label">年代目录 <span>01 — 06</span></p>
        <nav class="tl-era-nav" aria-label="按时代跳转">
          {% for e in tl.eras %}{% assign era_key = e.from | append: "" %}{% assign era_copy = site.data.timeline_editorial[era_key] %}
          <a href="#era-{{ forloop.index }}" data-tl-section-link><span class="tl-era-nav__number">0{{ forloop.index }}</span><span><b>{{ era_copy.title | default: e.label }}</b><small>{{ e.from }} — {{ e.to }}</small></span></a>
          {% endfor %}
        </nav>
        <div class="tl-enhance" hidden>{% include timeline-year-picker.html %}</div>
        <p class="tl-side__note">按原资料的发表日期排列。<br>作品图标通向制作名单。</p>
      </div>
    </aside>
    <div class="tl-era-list">
      {% for e in tl.eras %}
      {% assign era_key = e.from | append: "" %}{% assign era_copy = site.data.timeline_editorial[era_key] %}
      <section class="tl-era" id="era-{{ forloop.index }}" data-tl-section>
        <header class="tl-era__head"><span class="tl-era__number" aria-hidden="true">0{{ forloop.index }}</span><div><p class="tl-eyebrow">{{ e.from }} — {{ e.to }} / {{ e.label }}</p><h2>{{ era_copy.title | default: e.label }}</h2><p class="tl-era__note">{{ era_copy.note }}</p></div></header>
        <ol class="tl-years">
          {% for y in tl.years %}{% if y.year >= e.from and y.year <= e.to %}
          {% assign row_year = y.year | append: "" %}{% assign row_group = tl_by_year | where: "name", row_year | first %}
          {% include timeline-counts.html posts=row_group.items %}
          {% if tlc_docs > 0 or tlc_stream > 0 %}
          {% assign year_docs = tlc_documents | sort: "date" | reverse %}
          <li class="tl-year" id="y{{ y.year }}">
            <a class="tl-year__head" href="{{ '/timeline/' | append: y.year | append: '/' | relative_url }}"><b>{{ y.year }}</b><span>{% if tlc_docs > 0 %}{{ tlc_docs }} 篇文献{% endif %}{% if tlc_stream > 0 %}{% if tlc_docs > 0 %} · {% endif %}{{ tlc_stream }} 篇博客{% endif %}</span><span class="tl-year__go">读这一年 <span aria-hidden="true">↗</span></span></a>
            <div class="tl-year__main">
              {% if y.games.size > 0 %}<div class="tl-works" aria-label="{{ y.year }} 年的作品">{% for g in y.games %}<a href="{{ '/credits/' | append: g.slug | append: '/' | relative_url }}" title="{{ g.title }} · 制作名单">{% if g.icon %}<img src="{{ g.icon | relative_url }}" alt="" width="22" height="22" loading="lazy">{% if g.icon2 %}<img src="{{ g.icon2 | relative_url }}" alt="" width="22" height="22" loading="lazy">{% endif %}{% endif %}<span>{{ g.title }}</span></a>{% endfor %}</div>{% endif %}
              {% if year_docs.size > 0 %}<ul class="tl-selections" aria-label="{{ y.year }} 年最近发表的文献">{% for p in year_docs limit: 2 %}{% include timeline-entry.html post=p compact=true %}{% endfor %}</ul>{% else %}<p class="tl-year__note">这一年的记录，留在开发者博客里。<a href="{{ '/timeline/' | append: y.year | append: '/' | relative_url }}">翻开手记 →</a></p>{% endif %}
            </div>
          </li>
          {% endif %}{% endif %}{% endfor %}
        </ol>
      </section>
      {% endfor %}
    </div>
  </div>
  <noscript><p class="tl-foot">年份与年代链接均可直接使用。搜索与快捷年份选择需要启用 JavaScript。</p></noscript>
</div>
