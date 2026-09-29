---
layout: guide
title: "使用指南"
lead: "这些站点能做什么、怎么用：一个站一篇，图文讲解，带流程图和实机截图。"
permalink: /guide/
---
{%- comment -%}
The 使用指南 topic's front page: one card per guide, from _data/guides.yml. A
guide without a published page is a grey 编写中 card, not a link. Linked from
the navigation (KEy docs) and the home shelf (home-topics.html), and in the
masthead search and the sitemap like any page - see design/user-guide-plan_2026-09.md, §9.
{%- endcomment -%}
{% assign hub_groups = site.data.guides | group_by: "group" %}
{% for grp in hub_groups %}
## {{ grp.name }}

<div class="guide-cards">
{%- for g in grp.items %}
{%- assign card_url = "" %}{% if g.url and g.status == "published" %}{% assign card_url = g.url %}{% endif %}
{% include guide/card.html title=g.title text=g.summary url=card_url kind=grp.name %}
{%- endfor %}
</div>
{% endfor %}
