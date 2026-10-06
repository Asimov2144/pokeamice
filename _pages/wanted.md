---
layout: timeline
title: "原刊征集"
permalink: /wanted/
description: 实体杂志里的宝可梦主创访谈，本站已知存在、但还缺原刊的那些。手上有这一期的话，拍几页发给我们，就能把它补进资料库。
---
{%- comment -%}
The wanted board: the magazine interviews the archive knows of but cannot yet show from the page
itself. The items are _data/wanted.yml (with the fixed wording in _data/wanted_ui.yml), written from
the bibliographic research in design/wanted/. A card is a "wanted" poster with what is known, what is
missing, and two buttons that open an e-mail or a GitHub issue with the item already filled in; the
chain below shows every interview of the period, the ones already here included, so a reader can see
where the gap is. A post whose text came from a transcript points here (interview-editorial.html).
{%- endcomment -%}
{%- assign W = site.data.wanted -%}
{%- assign UI = site.data.wanted_ui -%}
<div class="tl tl--hub wanted">
  <header class="library__head tl-intro">
    <p class="library__eyebrow">Key docs · WANTED</p>
    <h1 class="library__title">原刊征集</h1>
    <p class="library__lead">这些杂志访谈，我们知道它们存在——有的在目录里、有的在当年的公告里、有的只剩网上一份转录——但本站还没有原刊。手上有这一期的话，哪怕只是用手机拍几页，也能帮它补全：页码、标题、谁接受了采访，都要靠原页来定。</p>
    <div class="library__stats wanted-stats">
      {%- assign keys = "known,text,candidate,found,scan" | split: "," -%}
      {%- for k in keys -%}
        {%- assign n = W.items | where: "status", k | size -%}
        <span class="wst-{{ k }}"><i class="wanted-dot"></i>{{ UI.status[k].label }} <b>{{ n }}</b></span>
      {%- endfor -%}
    </div>
  </header>

  <section class="wanted-how" id="how" aria-labelledby="wanted-how-title">
    <h2 class="wanted-h2" id="wanted-how-title">怎么帮忙</h2>
    <ol class="wanted-steps">
      <li><b>找到你手上的那一期</b>下面每张卡片都写了期号和还缺哪几页。</li>
      <li><b>拍下来就行</b>手机平拍即可：光线均匀，整页入镜，页码和页眉别裁掉；能扫描更好（300 dpi 以上）。封面和目录页也拍一张，方便核对期号。</li>
      <li><b>发给我们</b>点卡片上的按钮，邮件或 GitHub 都会带好条目编号。文件大可以给网盘链接。收录后在条目里注明提供者，也可以不署名。</li>
    </ol>
    <p class="wanted-also">没有原刊也能帮：知道页码、在别处见过这一期的目录、二手书店的商品页、图书馆馆藏——这些线索同样欢迎。</p>
    <ul class="wanted-channels">
      {%- for c in UI.channels %}
      <li><a href="{{ c.url }}"{% unless c.url contains "mailto:" %} target="_blank" rel="noopener"{% endunless %}><b>{{ c.label }}</b>{{ c.text }}</a>{% if c.note != "" %}<span>{{ c.note }}</span>{% endif %}</li>
      {%- endfor %}
    </ul>
    <p class="wanted-rights">收到的照片和扫描只用于资料研究、书目核对与翻译整理，会标明出处与提供者。请只分享你自己持有的刊物。</p>
  </section>

  <section class="wanted-board" id="board" aria-labelledby="wanted-board-title">
    <h2 class="wanted-h2" id="wanted-board-title">正在征集</h2>
    {%- assign prios = "S,A,B" | split: "," -%}
    {%- for p in prios -%}
      {%- assign group = W.items | where: "priority", p -%}
      {%- assign shown = 0 -%}
      {%- for it in group %}{% if UI.status[it.status].wanted %}{% assign shown = shown | plus: 1 %}{% endif %}{% endfor -%}
      {%- if shown > 0 %}
    <h3 class="wanted-tier"><b>{{ p }}</b>{{ UI.priority[p] }}<span>{{ shown }} 期</span></h3>
    <div class="wanted-grid">
      {%- for it in group -%}
        {%- if UI.status[it.status].wanted -%}{% include wanted-card.html item=it %}{%- endif -%}
      {%- endfor %}
    </div>
      {%- endif -%}
    {%- endfor %}
  </section>

  <section class="wanted-chain" id="chain" aria-labelledby="wanted-chain-title">
    <h2 class="wanted-h2" id="wanted-chain-title">整条采访链</h2>
    <p class="wanted-chain__lead">1996 到 2012 年实体杂志里的主创访谈，已经收录的也列在里面——看得出缺口在哪。</p>
    {%- for e in W.eras %}
      {%- assign rows = W.items | where: "era", e.key -%}
      {%- if rows.size > 0 %}
    <div class="wanted-era">
      <p class="wanted-era__label">{{ e.label }}</p>
      <ol class="wanted-rows">
        {%- for it in rows -%}
          {%- assign href = "" -%}
          {%- if it.post -%}
            {%- assign wr_path = "_posts/" | append: it.post | append: ".md" -%}
            {%- assign wr_post = site.posts | where: "path", wr_path | first -%}
            {%- if wr_post and it.status == "scan" %}{% assign href = wr_post.url | relative_url %}{% endif -%}
          {%- endif -%}
          {%- if href == "" and UI.status[it.status].wanted %}{% capture href %}#{{ it.id }}{% endcapture %}{% endif -%}
          {%- if href == "" and it.post and wr_post %}{% assign href = wr_post.url | relative_url %}{% endif -%}
          {%- if href == "" and it.sources %}{% assign href = it.sources[0].url %}{% endif %}
        <li class="wanted-row wst-{{ it.status }}">
          <i class="wanted-dot" title="{{ UI.status[it.status].label }}"></i>
          <span class="wanted-row__date">{{ it.date | slice: 0, 7 }}</span>
          <a class="wanted-row__name" href="{{ href }}"{% if href contains "://" %} target="_blank" rel="noopener"{% endif %}><b>{{ it.pub }} {{ it.issue }}</b>{{ it.title }}</a>
          <span class="wanted-row__state">{{ UI.status[it.status].label }}{% if it.conflict %} · 资料矛盾{% endif %}</span>
        </li>
        {%- endfor %}
      </ol>
    </div>
      {%- endif -%}
    {%- endfor %}
  </section>

  <section class="wanted-legend" aria-labelledby="wanted-legend-title">
    <h2 class="wanted-h2" id="wanted-legend-title">状态说明</h2>
    <dl>
      {%- for k in keys %}
      <div class="wst-{{ k }}"><dt><i class="wanted-dot"></i>{{ UI.status[k].label }}</dt><dd>{{ UI.status[k].text }}</dd></div>
      {%- endfor %}
      <div class="wst-conflict"><dt>资料矛盾</dt><dd>不同来源在期号、人物、标题或页码上说法不一，卡片上写了矛盾在哪。原刊是最终依据。</dd></div>
    </dl>
  </section>
</div>
