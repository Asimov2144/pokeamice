---
layout: timeline
title: "海外媒体专访"
permalink: /overseas/
search: false
---
{%- comment -%}
The interviews that a media outlet outside Japan ran - Game Informer, Eurogamer, Nintendo Power, the
Spanish press, Pokemon.com - gathered from every year in one place. Who counts and how the outlets
are grouped is decided in tools/build-hubs.py; the numbers and the cards are baked into
_data/hubs.yml. The same interviews carry the topic 海外媒体专访 on their entry cards. The outlet
buttons hide the cards that are already on the page (assets/js/hubs.js).
{%- endcomment -%}
{% assign ov = site.data.hubs.overseas %}
<div class="tl tl--hub tl--overseas">
  <header class="library__head tl-intro">
    <p class="library__eyebrow">Key docs · 横切专题</p>
    <h1 class="library__title">海外媒体专访</h1>
    <p class="library__lead">日本以外的媒体做的宝可梦主创访谈：<b>{{ ov.total }}</b> 篇，来自 <b>{{ ov.outlets.size }}</b> 家媒体，{{ ov.from }} 到 {{ ov.to }}。多是新作在欧美发售前后，对增田顺一、杉森建、大森滋等人的采访；原文是英语、西班牙语、法语或意大利语，本站译成中文。</p>
    <div class="library__stats">
      {% for r in ov.regions %}<span class="is-interview"><i class="tl-dot"></i>{{ r.label }} <b>{{ r.n }}</b></span>{% endfor %}
    </div>
  </header>

  <section class="hub-years" aria-label="每年的篇数">
    <p class="hub-years__title">哪一年最多</p>
    <div class="hub-years__cols" style="--n: {{ ov.years.size }}">
      {% for y in ov.years %}
      <span class="hub-year{% if y.n == 0 %} is-empty{% endif %}" title="{{ y.year }}：{% if y.n > 0 %}{{ y.n }} 篇{% else %}暂无{% endif %}">
        <b class="hub-year__n">{% if y.n > 0 %}{{ y.n }}{% endif %}</b>
        <i style="height: {{ y.n | times: 100 | divided_by: ov.max_year }}%"></i>
        <em>{{ y.year | modulo: 100 | plus: 100 | append: '' | slice: 1, 2 }}</em>
      </span>
      {% endfor %}
    </div>
  </section>

  <div class="tl-bar">
    <div class="tl-filters" role="group" aria-label="按媒体筛选" data-hub-bar>
      <button type="button" class="is-on" data-hub-filter="all">全部<b>{{ ov.total }}</b></button>
      {% for o in ov.outlets %}{% if o.n > 1 %}<button type="button" data-hub-filter="{{ o.key }}">{{ o.name }}<b>{{ o.n }}</b></button>{% endif %}{% endfor %}
    </div>
  </div>

  {% for r in ov.regions %}
  <section class="tl-era" id="{{ r.key }}" data-hub-region>
    <header class="tl-era__head">
      <p class="tl-era__range">{{ r.from }} – {{ r.to }}</p>
      <h2 class="tl-era__title">{{ r.label }}</h2>
      <p class="tl-era__sum"><b data-hub-count>{{ r.n }}</b> 篇 · {{ r.outlets.size }} 家</p>
      <p class="hub-note">{{ r.note }}</p>
      <div class="tl-chips">
        {% for o in r.outlets %}<span class="tl-chip">{{ o.name }} <b>{{ o.n }}</b></span>{% endfor %}
      </div>
    </header>
    <div class="tl-picks hub-picks">
      {% for it in r.items %}
      <a class="tl-pick is-{{ it.kind }}" href="{{ it.url | relative_url }}" data-hub-item="{{ it.outlet }}">
        {% if it.cover %}<span class="tl-pick__cover"><img src="{{ it.cover | relative_url }}" alt="" loading="lazy" decoding="async"></span>{% endif %}
        <span class="tl-pick__body">
          <small>{{ it.outlet_name }} · {{ it.date | slice: 0, 7 }}</small>
          <strong>{{ it.title }}</strong>
          {% if it.blurb %}<em>{{ it.blurb }}</em>{% elsif it.people.size > 0 %}<em>{{ it.people | join: "、" }}</em>{% endif %}
        </span>
      </a>
      {% endfor %}
    </div>
  </section>
  {% endfor %}

  <section class="hub-who">
    <div class="tl-chips"><span class="tl-chips__label">被问得最多</span>{% for p in ov.people %}<a class="tl-chip" href="{{ '/people/' | append: p.slug | append: '/' | relative_url }}">{% include person-name.html person=p.slug %} <b>{{ p.n }}</b></a>{% endfor %}</div>
    <div class="tl-chips"><span class="tl-chips__label">谈得最多的作品</span>{% for w in ov.works %}<a class="tl-game" href="{{ '/search/' | relative_url }}?work={{ w.name | url_encode }}" title="在检索里看提到 {{ w.name }} 的全部文献">{% if w.icon %}<img src="{{ w.icon | relative_url }}" alt="" width="18" height="18" loading="lazy">{% if w.icon2 %}<img src="{{ w.icon2 | relative_url }}" alt="" width="18" height="18" loading="lazy">{% endif %}{% endif %}<span>{{ w.name | remove_first: "宝可梦 " }}</span> <b>{{ w.n }}</b></a>{% endfor %}</div>
  </section>

  <p class="tl-foot">这一页只收海外媒体自己做的采访。英文粉丝站 GlitterBerri 转译的日本杂志、日本媒体转载的海外文章不在其中；想按作品看，去 <a href="{{ '/games/' | relative_url }}">按游戏读</a>，想按年份看，去 <a href="{{ '/timeline/' | relative_url }}">资料时间线</a>。</p>
</div>
<script src="{{ '/assets/js/hubs.js' | relative_url }}" defer></script>
