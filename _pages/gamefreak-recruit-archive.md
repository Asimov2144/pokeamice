---
layout: timeline
title: "GAME FREAK 招聘站版本档案"
permalink: /keys/gamefreak-recruit-archive/
description: GAME FREAK 招聘网站的同一个网址，在不同年份放过不同的人和不同的正文。这里按 Wayback 存档逐页列出每一版、它在官网上的时间，以及本站对应的译文。
---
{%- comment -%}
The recruit site as a versioned archive. Everything here is drawn from _data/recruit_archive.yml,
which tools/recruit-archive.py builds from the Wayback Machine's copies (pages and labels in
design/recruit-archive/pages.yml); a post says which version it translates in its `recruit:` front
matter, and its version note (_includes/recruit-version.html) links back to the page's row here.
{%- endcomment -%}
{%- assign RA = site.data.recruit_archive -%}
{%- assign n_versions = 0 -%}{%- assign n_in = 0 -%}
{%- for p in RA.pages -%}{%- for v in p.versions -%}{%- assign n_versions = n_versions | plus: 1 -%}{%- if v.post -%}{%- assign n_in = n_in | plus: 1 -%}{%- endif -%}{%- endfor -%}{%- endfor -%}
<div class="tl tl--hub rarc">
  <header class="library__head tl-intro">
    <p class="library__eyebrow">Key docs · RECRUIT ARCHIVE</p>
    <h1 class="library__title">GAME FREAK 招聘站版本档案</h1>
    <p class="library__lead">GAME FREAK 的招聘网站会沿用网址：同一个「程序员对谈」的地址，2019 年是 T.T. 和 K.I.，2024 年整页换成了 T.T. 和 M.O.；人物卡也有换人、撤下。所以一篇招聘访谈要说清楚它是哪一年的哪一版。这里按 Wayback Machine 的存档快照，把每个网址的每一版列出来，并连到本站的译文。</p>
    <div class="library__stats">
      <span>网址 <b>{{ RA.pages.size }}</b></span>
      <span>版本 <b>{{ n_versions }}</b></span>
      <span>已有译文 <b>{{ n_in }}</b></span>
      <span>更新 <b>{{ RA.updated }}</b></span>
    </div>
  </header>

  <section class="rarc-sec" id="roster" aria-labelledby="rarc-roster-title">
    <h2 class="rarc-h2" id="rarc-roster-title">招聘首页上的人物与对谈</h2>
    <p class="rarc-lead">每一列是招聘首页的一段时期（内容不变的连续快照并成一段），每一行是首页链到的一个页面。格子涂色 = 那段时期首页上有它。</p>
    {%- assign periods = RA.index -%}
    {%- assign all_ids = "" | split: "" -%}
    {%- for per in periods -%}{%- assign all_ids = all_ids | concat: per.cards | concat: per.talks -%}{%- endfor -%}
    {%- assign all_ids = all_ids | uniq -%}
    <div class="rarc-grid-wrap">
      <table class="rarc-grid">
        <thead>
          <tr><th scope="col">页面</th>{% for per in periods %}<th scope="col" title="{{ per.first }} – {{ per.last }}（{{ per.snapshots }} 个快照）"><span>{{ per.first | date: "%Y.%m" }}</span></th>{% endfor %}</tr>
        </thead>
        <tbody>
          {%- for id in all_ids -%}
          {%- assign pg = RA.pages | where: "id", id | first -%}
          <tr>
            <th scope="row">{% if pg %}<a href="#{{ id }}">{{ pg.label }}</a>{% else %}{{ id }}{% endif %}</th>
            {%- for per in periods -%}
              {%- if per.cards contains id or per.talks contains id -%}<td class="is-on" title="{{ per.first }} – {{ per.last }}"></td>{%- else -%}<td></td>{%- endif -%}
            {%- endfor -%}
          </tr>
          {%- endfor -%}
        </tbody>
      </table>
    </div>
    <p class="rarc-note">时期按首页快照划分：2019-12-11 改版后的首页要到 2020-05 才有快照，所以首发名单那一列从 2020-05 写起；人物页本身的首次快照都是 2019-12-11。</p>
  </section>

  {%- assign groups = "crosstalk,story,message,people,gen1,gen0,career2009" | split: "," -%}
  {%- assign group_title = "对谈 Cross Talk,Project Story,开发负责人寄语,人物 People,2015–2017 员工访谈（编号页）,2013 员工访谈,2009 中途招聘寄语" | split: "," -%}
  <section class="rarc-sec" id="pages" aria-labelledby="rarc-pages-title">
    <h2 class="rarc-h2" id="rarc-pages-title">每个网址的版本</h2>
    <p class="rarc-lead">「首见」「末见」是 Wayback 快照的日期，真实的上线和撤下落在相邻两个快照之间。正文换人、删人或大段改写算新的一版；只改了个别字句的记在同一版里。</p>
    {%- for g in groups -%}
    {%- assign gp = RA.pages | where: "group", g -%}
    {%- if gp.size > 0 -%}
    <h3 class="rarc-h3">{{ group_title[forloop.index0] }}</h3>
    <div class="rarc-pages">
      {%- for p in gp -%}
      <article class="rarc-page" id="{{ p.id }}">
        <header>
          <h4>{{ p.label }}{% if p.label_ja and p.label_ja != p.label %}<span lang="ja">{{ p.label_ja }}</span>{% endif %}</h4>
          <p><a href="{{ p.url }}" target="_blank" rel="noopener">{{ p.url | remove: "https://www.gamefreak.co.jp" }}</a> <span class="rarc-status rarc-status--{{ p.status }}">{% case p.status %}{% when "live" %}官网仍在{% when "moved" %}已移址{% else %}已撤下{% endcase %}</span></p>
          {% if p.note %}<p class="rarc-pnote">{{ p.note }}</p>{% endif %}
        </header>
        {%- if p.versions.size == 0 -%}
        <p class="rarc-empty">还没有读到存档快照。</p>
        {%- else -%}
        <ol class="rarc-versions">
          {%- for v in p.versions -%}
          {%- assign v_post = nil -%}{%- if v.post -%}{%- assign v_path = "_posts/" | append: v.post | append: ".md" -%}{%- assign v_post = site.posts | where: "path", v_path | first -%}{%- endif -%}
          <li class="{% if v_post %}is-in{% else %}is-out{% endif %}">
            <span class="rarc-v__when">{{ v.first | date: "%Y.%m.%d" }} – {% if forloop.last and p.status == "live" %}现在{% else %}{{ v.last | date: "%Y.%m.%d" }}{% endif %}</span>
            <span class="rarc-v__who">{% if v.members.size > 0 %}{{ v.members | join: " × " }}{% else %}—{% endif %}</span>
            <span class="rarc-v__change">{% case v.change %}{% when "replaced" %}整页换人{% when "members_removed" %}删去部分成员{% when "rewritten" %}改写{% else %}{% if forloop.first %}首版{% endif %}{% endcase %}{% if v.edits %}<i title="{% for e in v.edits %}{{ e.at }} 保留 {{ e.kept | times: 100 | round }}%{% unless forloop.last %}；{% endunless %}{% endfor %}">· 小改 {{ v.edits.size }} 次</i>{% endif %}</span>
            <span class="rarc-v__post">{% if v_post %}<a href="{{ v_post.url | relative_url }}">译文 →</a>{% else %}<span>未收录</span>{% endif %} <a class="rarc-wb" href="https://web.archive.org/web/{{ v.wayback }}/{{ p.url }}" target="_blank" rel="noopener">存档</a></span>
            {% if v.note %}<span class="rarc-v__note">{{ v.note }}</span>{% endif %}
          </li>
          {%- endfor -%}
        </ol>
        {%- endif -%}
      </article>
      {%- endfor -%}
    </div>
    {%- endif -%}
    {%- endfor -%}
  </section>

  <section class="rarc-sec" id="method" aria-labelledby="rarc-method-title">
    <h2 class="rarc-h2" id="rarc-method-title">怎么读这些日期</h2>
    <ul class="rarc-list">
      <li><b>文章日期</b>：招聘页不写发布日期。本站招聘译文的日期取自它那一版在官网出现的时间，标「约」，文章开头的「版本」说明写了依据（Wayback 首见、页面素材的批次号如 <code>?20240213</code>、首页哪个快照开始有它）。素材批次号只说明图片什么时候换过，不等于正文写成的时间。</li>
      <li><b>首页与个人页不一定同步</b>：例如设计师 M.I. 的个人页一直写「2021 年新卒入社」，招聘首页的卡片在 2024 年改版后却写 2022 年。</li>
      <li><b>原文核对</b>：每篇招聘译文的日文原文都逐段对过它所标的那一版快照（<code>tools/recruit-archive.py check</code>）。2026 年 10 月核对时发现 10 篇的「原文」与官网不符，已按存档重新导入、重新翻译。</li>
    </ul>
  </section>
</div>
