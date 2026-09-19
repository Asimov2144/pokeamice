---
layout: library
title: "资料窗口"
permalink: /keys/
---
{%- comment -%}
The resource hub as a stream: the home page is the catalogue, this is the
library's own timeline. Down the middle, newest first, the days entries came in
(tools/build-feed.py, from git), the keeper's own news (_data/feed.yml), the
days the library passed a round number, and a collection every few posts with
its latest entries; three posts are written in the browser for the day of the
visit - 今日一句, 历史上的今天, 人物聚焦 (assets/js/feed.js). On the right, every
collection as a tile, the numbers, the categories and the tags. Nothing here is
a list of titles: each post is something that happened.
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
{% assign lib_ndream = lib_posts | where_exp: "p", "p.publication contains 'Nintendo DREAM'" %}
{% assign lib_gi = lib_posts | where_exp: "p", "p.publication contains 'Game Informer'" %}
{% assign lib_people = site.data.people | where_exp: "e", "e.kind != 'character' and e.kind != 'figure' and e.kind != 'staff'" %}
{% assign lib_by_year = lib_posts | group_by_exp: "p", "p.date | date: '%Y'" | sort: "name" %}
{% assign site_avatar = "/assets/img/site/author-pikachu.jpg" %}
{% assign site_name = "Poke Amice Docs" %}
{% assign day_n = site.time | date: "%j" | plus: 0 %}

<header class="library__head feed__head">
  <p class="library__eyebrow">Key Docs · 动态</p>
  <h1 class="library__title">资料窗口</h1>
  <p class="library__lead">馆藏在动：哪天进了哪些条目，站点做了什么，今天该读哪一句、翻到哪一页、认识哪个人。首页管找资料，这里管看热闹。</p>
  <nav class="feed__filters" aria-label="只看" data-feed-filters>
    <button type="button" class="is-on" data-feed-kind="all">全部</button>
    <button type="button" data-feed-kind="added">新收录</button>
    <button type="button" data-feed-kind="site">站点动态</button>
    <button type="button" data-feed-kind="quote">今日一句</button>
    <button type="button" data-feed-kind="today">历史上的今天</button>
    <button type="button" data-feed-kind="person">人物聚焦</button>
    <button type="button" data-feed-kind="topic">专题</button>
  </nav>
</header>

<div class="feed" data-feed>
<div class="feed__stream" data-feed-stream>

{%- comment -%}
  The dated posts, merged and sorted: "date|kind|index". The milestones come from
  the import log walked oldest first; a threshold is passed on the day the running
  total first reaches it.
{%- endcomment -%}
{% assign dated = "" | split: "" %}
{% for e in site.data.feed_log %}{% assign row = e.date | append: "|added|" | append: forloop.index0 %}{% assign dated = dated | push: row %}{% endfor %}
{% for e in site.data.feed %}{% assign row = e.date | append: "|site|" | append: forloop.index0 %}{% assign dated = dated | push: row %}{% endfor %}
{% assign thresholds = "100,250,500,750,1000,1500,2000" | split: "," %}
{% assign log_oldest = site.data.feed_log | reverse %}
{% assign cum = 0 %}{% assign passed = "," %}
{% for e in log_oldest %}
  {% assign cum = cum | plus: e.count %}
  {% for th in thresholds %}
    {% assign th_n = th | plus: 0 %}{% assign th_key = "," | append: th | append: "," %}
    {% if cum >= th_n %}{% unless passed contains th_key %}{% assign passed = passed | append: th | append: "," %}{% assign row = e.date | append: "|milestone|" | append: th %}{% assign dated = dated | push: row %}{% endunless %}{% endif %}
  {% endfor %}
{% endfor %}
{% assign dated = dated | sort | reverse %}

{%- comment -%} the collections that take a turn in the stream: key|title|tile|href|blurb {%- endcomment -%}
{% assign topics = "interview|访谈翻译|iwata|/search/?type=%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91|开发者与媒体的对谈译文，日中对照，从 1996 年的图鉴访谈到最新的讲演报道;;scan|杂志扫描|scan|/search/?type=%E6%89%AB%E6%8F%8F%E7%BF%BB%E8%AF%91|整页扫描，逐页转写翻译，段落可在页图上定位;;director|部长专栏|director|/gamefreak-director/|増田部長のめざめるパワー，2004 年起的开发随笔;;staff|员工博客|staff|/gamefreak-staff/|晴时偶有阴：员工写的开发、招聘、活动与日常;;art|杉森建博客|art|/gamefreak-art/|绘画日和：电影角色设计稿与设计说明;;shudo|首藤刚志手记|shudo|/people/shudo-takeshi/|动画系列构成的连载手记，226 章;;recruit|招聘访谈|recruit|/search/?q=%E6%8B%9B%E8%81%98%E8%AE%BF%E8%B0%88|GAME FREAK 与宝可梦公司招聘站上的员工访谈;;tech|技术报告|tech|/search/?q=%E6%8A%80%E6%9C%AF|CEDEC 等讲演的技术报道;;iwata|社长问|iwata|/search/?q=%E7%A4%BE%E9%95%BF%E9%97%AE|岩田聪的访谈系列;;ndream|Nintendo DREAM|ndream|/search/?q=Nintendo%20DREAM|任天堂杂志的开发者访谈与特辑;;gi|Game Informer|gi|/search/?q=Game%20Informer|海外媒体的深度报道" | split: ";;" %}
{% assign t_n = topics | size %}
{% assign t_off = day_n | modulo: t_n %}
{% assign t_used = 0 %}
{% assign n = 0 %}

{% for row in dated %}
  {% assign f = row | split: "|" %}
  {% assign d = f[0] %}{% assign kind = f[1] %}{% assign idx = f[2] | plus: 0 %}

  {% if kind == "added" %}
    {% assign e = site.data.feed_log[idx] %}
    {% assign shown = "" | split: "" %}
    {% for stem in e.posts %}
      {% assign stem_md = "/" | append: stem | append: ".md" %}
      {% assign fp = site.posts | where_exp: "p", "p.path contains stem_md" | first %}
      {% if fp %}{% assign shown = shown | push: fp %}{% endif %}
    {% endfor %}
    {% if shown.size > 0 %}
    {% assign show_n = 6 %}{% if e.count >= 120 %}{% assign show_n = 3 %}{% endif %}
    {% capture tally %}{% for t in e.types %}{{ t[0] }} {{ t[1] }}{% unless forloop.last %} · {% endunless %}{% endfor %}{% endcapture %}
    {% capture body %}
      <p class="feed__tally">{{ tally }}</p>
      <div class="feed__cards">{% for post in shown limit: show_n %}{% include entry-card.html card_post=post compact=true %}{% endfor %}</div>
    {% endcapture %}
    {% capture foot %}{% if e.count > show_n %}<a href="{{ '/search/' | relative_url }}">这天一共 {{ e.count }} 篇，去检索中心看全部 →</a>{% endif %}{% endcapture %}
    {% capture head %}{% if e.count >= 120 %}大批入库：{{ e.count }} 篇{% else %}新收录 {{ e.count }} 篇{% endif %}{% endcapture %}
    {% include feed-item.html kind="added" date=d who=site_name avatar=site_avatar head=head body=body foot=foot %}
    {% assign n = n | plus: 1 %}
    {% endif %}

  {% elsif kind == "site" %}
    {% assign e = site.data.feed[idx] %}
    {% capture body %}
      <p>{{ e.text }}</p>
      {% if e.cover %}<a class="feed__cover" href="{{ e.url | relative_url }}" tabindex="-1" aria-hidden="true"><img src="{{ e.cover | relative_url }}" alt="" loading="lazy" decoding="async"></a>{% endif %}
    {% endcapture %}
    {% capture foot %}<a href="{{ e.url | relative_url }}">{{ e.label | default: "看看 →" }}</a>{% endcapture %}
    {% include feed-item.html kind="site" date=d who=site_name avatar=site_avatar head=e.title href=e.url body=body foot=foot %}
    {% assign n = n | plus: 1 %}

  {% elsif kind == "milestone" %}
    {% capture head %}馆藏过 {{ idx }} 条{% endcapture %}
    {% capture body %}<p>到这一天，资料窗口一共收录了 {{ idx }} 条访谈、扫描与博客。现在是 {{ lib_posts | size }} 条。</p>{% endcapture %}
    {% include feed-item.html kind="milestone" date=d who=site_name avatar="" head=head body=body %}
    {% assign n = n | plus: 1 %}
  {% endif %}

  {%- comment -%} the browser's three posts sit after the first, third and fifth dated post; a collection every sixth {%- endcomment -%}
  {% if n == 1 and slot_quote != true %}{% assign slot_quote = true %}
    {% assign hq_all = site.data.quotes.quotes | sort: "id" %}
    {% assign hq_n = hq_all.size %}{% assign hq_window = 30 %}{% if hq_window > hq_n %}{% assign hq_window = hq_n %}{% endif %}
    {% assign hq_offset = day_n | times: 11 | modulo: hq_n %}
    {% assign hq_pool = "" | split: "" %}
    {% for i in (1..hq_window) %}{% assign hq_idx = hq_offset | plus: i | minus: 1 | modulo: hq_n %}{% assign hq_pool = hq_pool | push: hq_all[hq_idx] %}{% endfor %}
    {% capture body %}
      <div class="feed__quote" data-feed-quote data-people-base="{{ '/people/' | relative_url }}" data-search-base="{{ '/search/?q=' | relative_url }}"><p class="feed__muted">正在挑今天的一句…</p></div>
      <script type="application/json" data-feed-quotes>[{% include quote-pool.html quotes=hq_pool %}]</script>
    {% endcapture %}
    {% capture foot %}<button type="button" class="feed__btn" data-feed-quote-next>换一句 ↻</button><a href="{{ '/quotes/' | relative_url }}">全部 {{ hq_n }} 句 →</a>{% endcapture %}
    {% include feed-item.html kind="quote" date="" who="今日一句" avatar="" body=body foot=foot id="feedQuote" %}
  {% endif %}
  {% if n == 3 and slot_today != true %}{% assign slot_today = true %}
    {% capture body %}<div class="feed__today" data-feed-today data-src="{{ '/assets/js/feed-days.json' | relative_url }}"><p class="feed__muted">正在翻日历…</p></div>{% endcapture %}
    {% capture foot %}<a href="{{ '/timeline/' | relative_url }}">时间线 →</a>{% endcapture %}
    {% include feed-item.html kind="today" date="" who="历史上的今天" avatar="" body=body foot=foot id="feedToday" %}
  {% endif %}
  {% if n == 5 and slot_person != true %}{% assign slot_person = true %}
    {% assign pf_all = site.data.people_profiles | where_exp: "p", "p.summary and p.interviews.entries >= 3" %}
    {% capture body %}
      <div class="feed__person" data-feed-person><p class="feed__muted">正在选今天的人…</p></div>
      <script type="application/json" data-feed-people>[{% for pf in pf_all limit: 60 %}{% assign pp = site.data.people | where: "slug", pf.slug | first %}{"n":{{ pf.name | jsonify }},"s":{{ pf.slug | jsonify }},"a":{{ pp.avatar | default: "" | relative_url | jsonify }},"r":{{ pp.role | default: pf.credits.line | default: "" | truncate: 60 | jsonify }},"m":{{ pf.summary | strip_newlines | truncate: 150 | jsonify }},"e":{{ pf.interviews.entries | default: 0 }},"y":{{ pf.interviews.first | append: "–" | append: pf.interviews.last | jsonify }}}{% unless forloop.last %},{% endunless %}{% endfor %}]</script>
    {% endcapture %}
    {% capture foot %}<a href="{{ '/people/' | relative_url }}">人物库 {{ lib_people | size }} 人 →</a>{% endcapture %}
    {% include feed-item.html kind="person" date="" who="人物聚焦" avatar="" body=body foot=foot id="feedPerson" %}
  {% endif %}
  {% assign n_mod = n | modulo: 6 %}
  {% if n_mod == 0 and n > 0 and t_used < 4 %}
    {% assign t_i = t_used | times: 5 | plus: t_off | modulo: t_n %}
    {% assign tf = topics[t_i] | split: "|" %}
    {% assign t_used = t_used | plus: 1 %}
    {% case tf[0] %}
      {% when "interview" %}{% assign t_posts = lib_interview %}
      {% when "scan" %}{% assign t_posts = lib_scan %}
      {% when "director" %}{% assign t_posts = gf_masuda_posts %}
      {% when "staff" %}{% assign t_posts = gf_staff_posts %}
      {% when "art" %}{% assign t_posts = gf_art_posts %}
      {% when "shudo" %}{% assign t_posts = lib_shudo %}
      {% when "recruit" %}{% assign t_posts = lib_recruit %}
      {% when "tech" %}{% assign t_posts = lib_tech %}
      {% when "iwata" %}{% assign t_posts = lib_iwata %}
      {% when "ndream" %}{% assign t_posts = lib_ndream %}
      {% else %}{% assign t_posts = lib_gi %}
    {% endcase %}
    {% capture body %}
      <a class="feed__tile" href="{{ tf[3] | relative_url }}"><img src="{{ '/assets/img/topics/' | append: tf[2] | append: '.jpg' | relative_url }}" alt="" width="336" height="192" loading="lazy" decoding="async"><span>{{ t_posts | size }} 条</span></a>
      <p>{{ tf[4] }}</p>
      <div class="feed__cards">{% for post in t_posts limit: 3 %}{% include entry-card.html card_post=post compact=true %}{% endfor %}</div>
    {% endcapture %}
    {% capture foot %}<a href="{{ tf[3] | relative_url }}">查看全部 {{ t_posts | size }} 条 →</a>{% endcapture %}
    {% assign t_avatar = "/assets/img/topics/" | append: tf[2] | append: ".jpg" %}
    {% assign t_title = tf[1] %}{% assign t_href = tf[3] %}
    {% include feed-item.html kind="topic" date="" who=t_title avatar=t_avatar head=t_title href=t_href body=body foot=foot %}
  {% endif %}
{% endfor %}

  <p class="feed__end">动态到这里为止。更早的入库都在 <a href="{{ '/search/' | relative_url }}">检索中心</a>；分类和标签在右边。</p>
</div>

<aside class="feed__rail">
  <section class="feed__rail-section" aria-label="专题">
    <h2 class="feed__rail-head">专题</h2>
    {% include home-topics.html grid=true %}
  </section>
  <section class="feed__rail-section" aria-label="收录规模">
    <h2 class="feed__rail-head">规模</h2>
    <p class="library__stats">
      <span><b>{{ lib_posts | size }}</b> 条 · {{ lib_by_year.first.name }}–{{ lib_by_year.last.name }}</span>
      <a href="{{ '/search/?type=%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91' | relative_url }}">访谈 <b>{{ lib_interview | size }}</b></a>
      <a href="{{ '/search/?type=%E6%89%AB%E6%8F%8F%E7%BF%BB%E8%AF%91' | relative_url }}">扫描 <b>{{ lib_scan | size }}</b></a>
      <a href="{{ '/gamefreak-director/' | relative_url }}">博客 <b>{{ gf_masuda_posts.size | plus: gf_art_posts.size | plus: gf_staff_posts.size }}</b></a>
      <a href="{{ '/people/' | relative_url }}">人物 <b>{{ lib_people | size }}</b></a>
      <a href="{{ '/works/' | relative_url }}">作品 <b>{{ site.data.works | size }}</b></a>
      <a href="{{ '/credits/' | relative_url }}">制作名单 <b>{{ site.data.credits_games | size }}</b> 作</a>
    </p>
  </section>
  <section class="feed__rail-section" aria-label="分类">
    <h2 class="feed__rail-head">分类</h2>
    <div class="library__cats--plain">
      {% for c in site.data.categories %}{% assign c_posts = site.categories[c.name] %}{% if c_posts and c_posts.size > 0 %}{% assign c_slug = c.name | slugify %}<a href="{{ '/categories/' | append: c_slug | append: '/' | relative_url }}" title="{{ c.blurb | escape }}">{{ c.title | default: c.name }}<b>{{ c_posts | size }}</b></a>{% endif %}{% endfor %}
      {% assign cat_named = site.data.categories | map: "name" %}
      {% for cat in site.categories %}{% unless cat_named contains cat[0] %}{% if cat[1].size >= 3 %}{% assign cat_slug = cat[0] | slugify %}<a href="{{ '/categories/' | append: cat_slug | append: '/' | relative_url }}">{{ cat[0] }}<b>{{ cat[1].size }}</b></a>{% endif %}{% endunless %}{% endfor %}
    </div>
  </section>
  {%- comment -%} site.tags is the `tags` collection here (_config.yml), so the tags are gathered from the posts {%- endcomment -%}
  {% capture tag_blob %}{% for p in lib_posts %}{% for t in p.tags %}{{ t }}
{% endfor %}{% endfor %}{% endcapture %}
  {% assign tag_groups = tag_blob | split: "
" | group_by_exp: "t", "t" | sort: "size" | reverse %}
  <section class="feed__rail-section" aria-label="标签">
    <h2 class="feed__rail-head">常用标签</h2>
    <div class="library__tags">
      {% for g in tag_groups limit: 30 %}{% if g.name != "" %}{% assign g_slug = g.name | slugify %}<a href="{{ '/tags/' | append: g_slug | append: '/' | relative_url }}">{{ g.name }}<b>{{ g.size }}</b></a>{% endif %}{% endfor %}
    </div>
  </section>
</aside>
</div>
