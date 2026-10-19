---
layout: timeline
title: "媒体专访"
permalink: /media/
search: false
description: "日本和海外的游戏媒体做的宝可梦主创访谈，每家大媒体一个板块：Nintendo DREAM、Fami通、任天堂 NOM、電撃、4Gamer、Game Informer、IGN、GameSpot、Polygon、Eurogamer 等。"
---
{%- comment -%}
The interviews that the press ran, Japanese and foreign, one board per outlet. Which post belongs to which
outlet is decided once in tools/build-hubs.py (JP_OUTLETS, OUTLETS) and baked into _data/hubs.yml (media);
which outlets get a board of their own is _data/media_boards.yml - a named outlet has one however few it
ran, the rest share the last board of their side. The home page's magazine tiles count from the same
mapping (media.by_stem), so a tile and its board agree. /overseas/ is a redirect to #overseas.
{%- endcomment -%}
{%- assign md = site.data.hubs.media -%}
{%- assign sides = "japan,overseas" | split: "," -%}
<div class="tl tl--hub tl--media">
  <header class="library__head tl-intro">
    <p class="library__eyebrow">Key docs · 横切专题</p>
    <h1 class="library__title">媒体专访</h1>
    <p class="library__lead">游戏媒体做的宝可梦主创访谈：<b>{{ md.total }}</b> 篇，日本媒体 <b>{{ md.japan.n }}</b> 篇、海外媒体 <b>{{ md.overseas.n }}</b> 篇。每家大媒体一个板块，篇数少的几家合在每边最后一块。官方渠道（社长问、官网专题、招聘访谈）不在这里，在首页的专题图块里。</p>
    <div class="library__stats">
      <a class="is-interview" href="#japan"><i class="tl-dot"></i>日本媒体 <b>{{ md.japan.n }}</b></a>
      <a class="is-interview" href="#overseas"><i class="tl-dot"></i>海外媒体 <b>{{ md.overseas.n }}</b></a>
    </div>
  </header>

  <nav class="tl-bar media-bar" aria-label="跳到一家媒体">
    {%- for side in sides -%}{%- assign sd = md[side] %}
    <div class="tl-filters">
      <span class="media-bar__label">{% if side == "japan" %}日本{% else %}海外{% endif %}</span>
      {% for b in sd.boards %}<a href="#o-{{ b.key }}">{{ b.name }}<b>{{ b.n }}</b></a>{% endfor %}
      {% if sd.rest.n > 0 %}<a href="#o-{{ side }}-rest">其他<b>{{ sd.rest.n }}</b></a>{% endif %}
    </div>
    {%- endfor %}
  </nav>

  {% for side in sides %}{% assign sd = md[side] %}
  <section class="media-side" id="{{ side }}">
    <h2 class="media-side__title">{% if side == "japan" %}日本媒体{% else %}海外媒体{% endif %} <small>{{ sd.n }} 篇 · {{ sd.outlets }} 家 · {{ sd.from }}–{{ sd.to }}</small></h2>
    {% for b in sd.boards %}
    <section class="tl-era hub-board" id="o-{{ b.key }}">
      <header class="tl-era__head">
        <p class="tl-era__range">{{ b.from }}{% if b.to != b.from %} – {{ b.to }}{% endif %}</p>
        <h3 class="tl-era__title">{{ b.name }}</h3>
        <p class="tl-era__sum"><b>{{ b.n }}</b> 篇</p>
        {% if b.blurb != "" %}<p class="hub-note">{{ b.blurb }}</p>{% endif %}
      </header>
      <div class="tl-picks hub-picks">
        {% for it in b.items %}{% include hub-pick.html it=it %}{% endfor %}
      </div>
    </section>
    {% endfor %}
    {% if sd.rest.n > 0 %}
    <section class="tl-era hub-board" id="o-{{ side }}-rest">
      <header class="tl-era__head">
        <p class="tl-era__range">&nbsp;</p>
        <h3 class="tl-era__title">{% if side == "japan" %}其他日本媒体{% else %}其他海外媒体{% endif %}</h3>
        <p class="tl-era__sum"><b>{{ sd.rest.n }}</b> 篇 · {{ sd.rest.outlets.size }} 家</p>
        <div class="tl-chips">{% for o in sd.rest.outlets %}<span class="tl-chip">{{ o.name }} <b>{{ o.n }}</b></span>{% endfor %}</div>
      </header>
      <div class="tl-picks hub-picks">
        {% for it in sd.rest.items %}{% include hub-pick.html it=it %}{% endfor %}
      </div>
    </section>
    {% endif %}
  </section>
  {% endfor %}

  <p class="tl-foot">只收媒体自己做的采访。英文粉丝站 GlitterBerri 转译的日本杂志不算海外媒体；想按作品看，去<a href="{{ '/games/' | relative_url }}">按游戏读</a>，想按年份看，去<a href="{{ '/timeline/' | relative_url }}">资料时间线</a>。</p>
</div>
