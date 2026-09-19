---
layout: library
title: "资料窗口"
permalink: /keys/
---
{%- comment -%}
The hub of the library: every collection as a picture tile (the home's shelf,
wrapped into a wall), then each of the big collections with its latest entries
as the front desk's cards, then the categories and the tags the entries are
filed under. Nothing here is a list of titles: a window is something to look
into. The sets are cut the way home.html and home-topics.html cut them, so the
counts agree with the home page.
{%- endcomment -%}
{% assign lib_posts = site.posts | where_exp: "post", "post.search != false" %}
{% assign gf_director_posts = site.posts | where: "archive_type", "gamefreak_director_column" %}
{% assign gf_lineblog_posts = site.posts | where: "archive_type", "gamefreak_masuda_lineblog" %}
{% assign gf_legacy_posts = site.posts | where: "archive_type", "gamefreak_legacy_blog" %}
{% assign gf_art_posts = gf_legacy_posts | where: "gf_legacy_blog", "art" %}
{% assign gf_staff_posts = gf_legacy_posts | where: "gf_legacy_blog", "staff" %}
{% assign gf_masuda_posts = gf_director_posts | concat: gf_lineblog_posts | sort: "date" | reverse %}
{% assign lib_scan = lib_posts | where: "archive_type", "scan_translation" %}
{% assign lib_interview = lib_posts | where_exp: "p", "p.layout == 'interview-editorial' or p.layout == 'parallel-translation' or p.categories contains '访谈翻译'" | where_exp: "p", "p.archive_type != 'scan_translation'" %}
{% assign lib_shudo = lib_posts | where_exp: "p", "p.categories contains '首藤刚志手记'" %}
{% assign lib_recruit = lib_posts | where_exp: "p", "p.tags contains '招聘访谈'" %}
{% assign lib_tech = lib_posts | where_exp: "p", "p.source_kind == 'technical_report' or p.article_kind == 'technical_feature'" %}
{% assign lib_iwata = lib_posts | where_exp: "p", "p.publication contains '社長が訊く' or p.title contains '社长问'" %}
{% assign lib_people = site.data.people | where_exp: "e", "e.kind != 'character' and e.kind != 'figure' and e.kind != 'staff'" %}
{% assign lib_by_year = lib_posts | group_by_exp: "p", "p.date | date: '%Y'" | sort: "name" %}

<header class="library__head">
  <p class="library__eyebrow">Key Docs</p>
  <h1 class="library__title">资料窗口</h1>
  <p class="library__lead">馆藏按来源分成一个个窗口：访谈、杂志扫描、GAME FREAK 的三种博客、手记、招聘访谈、技术报告，还有人物、作品、制作名单和图谱。每个窗口都能一路点进去，也都能在检索中心再按年份、人物、作品筛。</p>
  <p class="library__stats" aria-label="收录规模">
    <span><b>{{ lib_posts | size }}</b> 条 · {{ lib_by_year.first.name }}–{{ lib_by_year.last.name }}</span>
    <a href="{{ '/search/?type=%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91' | relative_url }}">访谈 <b>{{ lib_interview | size }}</b></a>
    <a href="{{ '/search/?type=%E6%89%AB%E6%8F%8F%E7%BF%BB%E8%AF%91' | relative_url }}">扫描 <b>{{ lib_scan | size }}</b></a>
    <a href="{{ '/gamefreak-director/' | relative_url }}">博客 <b>{{ gf_masuda_posts.size | plus: gf_art_posts.size | plus: gf_staff_posts.size }}</b></a>
    <a href="{{ '/people/' | relative_url }}">人物 <b>{{ lib_people | size }}</b></a>
    <a href="{{ '/works/' | relative_url }}">作品 <b>{{ site.data.works | size }}</b></a>
    <a href="{{ '/credits/' | relative_url }}">制作名单 <b>{{ site.data.credits_games | size }}</b> 作</a>
  </p>
</header>

{% include home-topics.html grid=true %}

{%- comment -%} each big collection: its name, its count, where the whole of it is, and its latest four {%- endcomment -%}
{% assign lib_sections = "访谈翻译|interview|/search/?type=%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91|开发者与媒体的对谈译文，日中对照;;杂志扫描|scan|/search/?type=%E6%89%AB%E6%8F%8F%E7%BF%BB%E8%AF%91|整页扫描，逐页转写翻译，段落可在页图上定位;;部长专栏|director|/gamefreak-director/|増田部長のめざめるパワー，2004 年起的开发随笔;;员工博客|staff|/gamefreak-staff/|晴时偶有阴：员工写的开发、招聘、活动与日常;;杉森建博客|art|/gamefreak-art/|绘画日和：电影角色设计稿与设计说明;;首藤刚志手记|shudo|/people/shudo-takeshi/|动画系列构成的连载手记;;招聘访谈|recruit|/search/?q=%E6%8B%9B%E8%81%98%E8%AE%BF%E8%B0%88|GAME FREAK 与宝可梦公司招聘站上的员工访谈;;技术报告|tech|/search/?q=%E6%8A%80%E6%9C%AF|CEDEC 等讲演的技术报道;;社长问|iwata|/search/?q=%E7%A4%BE%E9%95%BF%E9%97%AE|岩田聪的访谈系列" | split: ";;" %}
{% for sec in lib_sections %}
  {% assign f = sec | split: "|" %}
  {% case f[1] %}
    {% when "interview" %}{% assign sec_posts = lib_interview %}
    {% when "scan" %}{% assign sec_posts = lib_scan %}
    {% when "director" %}{% assign sec_posts = gf_masuda_posts %}
    {% when "staff" %}{% assign sec_posts = gf_staff_posts %}
    {% when "art" %}{% assign sec_posts = gf_art_posts %}
    {% when "shudo" %}{% assign sec_posts = lib_shudo %}
    {% when "recruit" %}{% assign sec_posts = lib_recruit %}
    {% when "tech" %}{% assign sec_posts = lib_tech %}
    {% else %}{% assign sec_posts = lib_iwata %}
  {% endcase %}
  {% if sec_posts.size > 0 %}
  <section class="library__section" aria-label="{{ f[0] }}">
    <header class="library__section-head">
      <h2>{{ f[0] }}</h2>
      <small>{{ sec_posts | size }} 条 · {{ f[3] }}</small>
      <a href="{{ f[2] | relative_url }}">查看全部 →</a>
    </header>
    <div class="library__row">
      {% for post in sec_posts limit: 4 %}{% include entry-card.html card_post=post compact=true %}{% endfor %}
    </div>
  </section>
  {% endif %}
{% endfor %}

{%- comment -%} the categories: the ones with a word about them first, then any other with three entries or more; then the tags most used {%- endcomment -%}
<section class="library__section" aria-label="分类">
  <header class="library__section-head">
    <h2>分类</h2>
    <small>{{ site.categories | size }} 个分类 · 每篇条目按来源和体裁归档</small>
  </header>
  <div class="library__cats">
    {% for c in site.data.categories %}
      {% assign c_posts = site.categories[c.name] %}{% assign c_slug = c.name | slugify %}
      {% if c_posts and c_posts.size > 0 %}
        <a class="library__cat" href="{{ '/categories/' | append: c_slug | append: '/' | relative_url }}"><strong>{{ c.title | default: c.name }}</strong><b>{{ c_posts | size }}</b><span>{{ c.blurb }}</span>{% if c.title %}<small>{{ c.name }}</small>{% endif %}</a>
      {% endif %}
    {% endfor %}
  </div>
  {% assign cat_named = site.data.categories | map: "name" %}
  {% capture cat_rest %}{% for cat in site.categories %}{% unless cat_named contains cat[0] %}{% if cat[1].size >= 3 %}{% assign cat_slug = cat[0] | slugify %}<a href="{{ '/categories/' | append: cat_slug | append: '/' | relative_url }}">{{ cat[0] }}<b>{{ cat[1].size }}</b></a>{% endif %}{% endunless %}{% endfor %}{% endcapture %}
  {% assign cat_rest = cat_rest | strip %}
  {% if cat_rest != "" %}<div class="library__cats--plain" aria-label="其他分类">{{ cat_rest }}</div>{% endif %}
</section>

{%- comment -%} site.tags is the `tags` collection here (_config.yml), not the posts' tags, so the tags are gathered from the posts themselves {%- endcomment -%}
{% capture tag_blob %}{% for p in lib_posts %}{% for t in p.tags %}{{ t }}
{% endfor %}{% endfor %}{% endcapture %}
{% assign tag_groups = tag_blob | split: "
" | group_by_exp: "t", "t" | sort: "size" | reverse %}
<section class="library__section" aria-label="标签">
  <header class="library__section-head">
    <h2>常用标签</h2>
    <small>{{ tag_groups | size }} 个标签 · 用得最多的 30 个</small>
  </header>
  <div class="library__tags">
    {% for g in tag_groups limit: 30 %}{% if g.name != "" %}{% assign g_slug = g.name | slugify %}<a href="{{ '/tags/' | append: g_slug | append: '/' | relative_url }}">{{ g.name }}<b>{{ g.size }}</b></a>{% endif %}{% endfor %}
  </div>
</section>
