---
layout: archive
title: "所有文章"
permalink: /posts/
author_profile: false  # 隐藏作者信息
classes: wide         # 启用宽屏模式
---

{% include base_path %}

{% capture written_year %}'None'{% endcapture %}
{% for post in site.posts %}
  {% capture year %}{{ post.date | date: '%Y' }}{% endcapture %}
  {% if year != written_year %}
    <h2 id="{{ year }}" class="archive__subtitle">{{ year }}</h2>
    {% capture written_year %}{{ year }}{% endcapture %}
  {% endif %}
  {% include archive-single.html %}
{% endfor %}

{% include paginator.html %}