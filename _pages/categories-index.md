---
layout: library
title: "全部分类"
permalink: /categories/
---
{%- comment -%}
Every category of the library: the ones _data/categories.yml describes first, then the rest.
{%- endcomment -%}
{% assign cat_named = site.data.categories | map: "name" %}
<header class="library__head">
  <p class="library__eyebrow">Categories</p>
  <h1 class="library__title">全部分类</h1>
  <p class="library__lead">条目的分类：每个分类下按时间倒序。想按标签、作品或人物找，用 <a href="{{ '/search/' | relative_url }}">检索中心</a>。</p>
</header>
<div class="library__cats">
  {% for c in site.data.categories %}{% assign c_posts = site.categories[c.name] %}{% if c_posts and c_posts.size > 0 %}{% assign c_slug = c.name | slugify %}
  <a class="library__cat" href="{{ '/categories/' | append: c_slug | append: '/' | relative_url }}"><b>{{ c.title | default: c.name }}</b><span>{{ c_posts | size }} 条</span>{% if c.blurb %}<em>{{ c.blurb }}</em>{% endif %}</a>
  {% endif %}{% endfor %}
</div>
<h2 class="library__sub">其他分类</h2>
<div class="library__cats--plain">
  {% for cat in site.categories %}{% unless cat_named contains cat[0] %}{% assign cat_slug = cat[0] | slugify %}<a href="{{ '/categories/' | append: cat_slug | append: '/' | relative_url }}">{{ cat[0] }}<b>{{ cat[1].size }}</b></a>{% endunless %}{% endfor %}
</div>
