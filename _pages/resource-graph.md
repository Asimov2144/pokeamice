---
title: "站内关系图谱"
permalink: /resource-graph/
layout: single
categories: [文档, 站点]
tags: [graph, metadata, guide]
archive_type: article
source:
  title: "站点自动生成"
  source_type: site_index
workflow:
  scan: pending
  preprocess: pending
  ocr: pending
  translation: pending
  proofreading: draft
  published: done
entities:
  organizations:
    - Poke Amice Docs
relations:
  related_posts:
    - /metadata-schema/
---

{% assign graph_posts = site.posts | where_exp: "post", "post.entities.people or post.entities.works or post.entities.organizations or post.entities.events" %}
{% assign resource_index = site.data.resource-index %}

<section class="resource-graph-page">
  <div class="resource-graph-hero">
    <p>Guide</p>
    <h2>从文章列表走向资料网络</h2>
    <span>这里会汇总站内已经填写 `entities` 字段的文章和评注，并按人物、作品、组织、事件建立可浏览的关系入口。</span>
  </div>

  <div class="resource-graph-stats">
    <div><strong>{{ graph_posts | size }}</strong><span>已入图文章</span></div>
    <div><strong>{{ resource_index.annotations | size | default: 0 }}</strong><span>已入图评注</span></div>
    <div><strong>{{ site.posts | size }}</strong><span>全部文章</span></div>
    <div><strong>4</strong><span>关系类型</span></div>
  </div>

  <div class="resource-graph-entry">
    <a href="{{ '/entities/people/' | relative_url }}"><strong>人物页</strong><span>按人物汇总文章和评注</span></a>
    <a href="{{ '/entities/works/' | relative_url }}"><strong>作品页</strong><span>按作品汇总来源和说明</span></a>
    <a href="{{ '/entities/organizations/' | relative_url }}"><strong>组织页</strong><span>整理公司、社群和媒体来源</span></a>
    <a href="{{ '/entities/events/' | relative_url }}"><strong>事件页</strong><span>连接专题、活动和资料节点</span></a>
    <a href="{{ '/timeline/' | relative_url }}"><strong>时间线</strong><span>按年份回看资料网络</span></a>
  </div>

  <div class="resource-graph-grid">
    <section>
      <h3>人物</h3>
      <div class="resource-graph-tags">
        {% assign people_text = "" %}
        {% for post in graph_posts %}
          {% for item in post.entities.people %}
            {% unless people_text contains item %}
              {% assign people_text = people_text | append: item | append: "||" %}
              <a href="#entity-{{ item | slugify }}">{{ item }}</a>
            {% endunless %}
          {% endfor %}
        {% endfor %}
        {% if people_text == "" %}<p>等待补充人物字段。</p>{% endif %}
      </div>
    </section>

    <section>
      <h3>作品</h3>
      <div class="resource-graph-tags">
        {% assign works_text = "" %}
        {% for post in graph_posts %}
          {% for item in post.entities.works %}
            {% unless works_text contains item %}
              {% assign works_text = works_text | append: item | append: "||" %}
              <a href="#entity-{{ item | slugify }}">{{ item }}</a>
            {% endunless %}
          {% endfor %}
        {% endfor %}
        {% if works_text == "" %}<p>等待补充作品字段。</p>{% endif %}
      </div>
    </section>

    <section>
      <h3>组织</h3>
      <div class="resource-graph-tags">
        {% assign organizations_text = "" %}
        {% for post in graph_posts %}
          {% for item in post.entities.organizations %}
            {% unless organizations_text contains item %}
              {% assign organizations_text = organizations_text | append: item | append: "||" %}
              <a href="#entity-{{ item | slugify }}">{{ item }}</a>
            {% endunless %}
          {% endfor %}
        {% endfor %}
        {% if organizations_text == "" %}<p>等待补充组织字段。</p>{% endif %}
      </div>
    </section>

    <section>
      <h3>事件</h3>
      <div class="resource-graph-tags">
        {% assign events_text = "" %}
        {% for post in graph_posts %}
          {% for item in post.entities.events %}
            {% unless events_text contains item %}
              {% assign events_text = events_text | append: item | append: "||" %}
              <a href="#entity-{{ item | slugify }}">{{ item }}</a>
            {% endunless %}
          {% endfor %}
        {% endfor %}
        {% if events_text == "" %}<p>等待补充事件字段。</p>{% endif %}
      </div>
    </section>
  </div>

  <section class="resource-graph-list">
    <h3>已入图资料</h3>
    {% for post in graph_posts %}
      <article>
        <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
        <p>
          {% for item in post.entities.people %}<span id="entity-{{ item | slugify }}">{{ item }}</span>{% endfor %}
          {% for item in post.entities.works %}<span id="entity-{{ item | slugify }}">{{ item }}</span>{% endfor %}
          {% for item in post.entities.organizations %}<span id="entity-{{ item | slugify }}">{{ item }}</span>{% endfor %}
          {% for item in post.entities.events %}<span id="entity-{{ item | slugify }}">{{ item }}</span>{% endfor %}
        </p>
      </article>
    {% else %}
      <p>还没有文章填写关系字段。</p>
    {% endfor %}
  </section>
</section>
