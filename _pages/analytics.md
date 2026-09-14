---
layout: archive
title: "全站资料库全景数据分析中心 · ARCHIVE ANALYTICS & DATA OBSERVATORY"
permalink: /analytics/
classes: wide
categories: [文档, 资料库, 数据分析]
tags: [数据中心, 全景分析, 宝可梦历史, 创作者, 世代矩阵, 千篇工程]
summary: "全景观测宝可梦 30 年档案库：971 篇珍贵文献、474 篇收录访谈千篇工程里程碑、全世代作品 3D 翻转矩阵、核心创作者群像与三十载编年分布。"
search: true
sidebar: false
---

{% assign data = site.data.site_analytics %}
{% assign overview = data.overview %}
{% assign hof = data.hall_of_fame %}
{% assign staff = data.staff_voices %}
{% assign gen_matrix = data.generation_matrix %}
{% assign timeline = data.timeline_data %}
{% assign top_orgs = data.top_orgs %}
{% assign gov = data.governance_stats %}

<div class="archive-analytics-root">
  <!-- Hero Section -->
  <header class="analytics-hero">
    <div class="analytics-hero__badge">ARCHIVE OBSERVATORY &bull; DATA INTELLIGENCE</div>
    <h1 class="analytics-hero__title">全站资料库全景数据分析中心</h1>
    <p class="analytics-hero__subtitle">
      以结构化数据穿透三十载宝可梦历史 &bull; 聚合 <strong>{{ overview.total_posts }}</strong> 篇文献、<strong>{{ overview.total_interviews_imported }}</strong> 篇高质量访谈、<strong>{{ overview.total_people }}</strong> 位核心创作者与 <strong>{{ overview.total_works }}</strong> 部世代经典
    </p>
    <div class="analytics-nav-anchors">
      <a href="#milestone" class="analytics-nav-btn"><i class="fas fa-flag-checkered"></i> 千篇工程进度</a>
      <a href="#matrix" class="analytics-nav-btn"><i class="fas fa-th-large"></i> 全世代 3D 矩阵</a>
      <a href="#hall-of-fame" class="analytics-nav-btn"><i class="fas fa-user-tie"></i> 创作者殿堂</a>
      <a href="#timeline" class="analytics-nav-btn"><i class="fas fa-chart-bar"></i> 三十载分布图</a>
      <a href="#governance" class="analytics-nav-btn"><i class="fas fa-shield-alt"></i> 底层治理架构</a>
    </div>
  </header>

  <!-- Core KPI Grid -->
  <section class="analytics-kpi-container" aria-label="核心数据看板">
    <div class="analytics-kpi-card">
      <div class="kpi-icon"><i class="fas fa-book-open"></i></div>
      <div class="kpi-value">{{ overview.total_posts }}</div>
      <div class="kpi-label">全站文献总数</div>
      <div class="kpi-sub">深度访谈 &bull; 专栏 &bull; 官方档案</div>
    </div>
    <div class="analytics-kpi-card kpi-card--highlight">
      <div class="kpi-icon"><i class="fas fa-microphone-alt"></i></div>
      <div class="kpi-value">{{ overview.total_interviews_imported }}</div>
      <div class="kpi-label">已收录深度访谈</div>
      <div class="kpi-sub">千篇工程达成率 {{ overview.interview_progress_pct }}%</div>
    </div>
    <div class="analytics-kpi-card">
      <div class="kpi-icon"><i class="fas fa-history"></i></div>
      <div class="kpi-value">{{ overview.years_span }} 年</div>
      <div class="kpi-label">时间跨度</div>
      <div class="kpi-sub">{{ overview.earliest_year }} &ndash; {{ overview.latest_year }} 年持续收录</div>
    </div>
    <div class="analytics-kpi-card">
      <div class="kpi-icon"><i class="fas fa-users"></i></div>
      <div class="kpi-value">{{ overview.total_people }}</div>
      <div class="kpi-label">收录业界名家</div>
      <div class="kpi-sub">总监 &bull; 作曲家 &bull; 编剧 &bull; 美术</div>
    </div>
    <div class="analytics-kpi-card">
      <div class="kpi-icon"><i class="fas fa-gamepad"></i></div>
      <div class="kpi-value">{{ overview.total_works }}</div>
      <div class="kpi-label">涵盖关联作品</div>
      <div class="kpi-sub">九大世代 &bull; 衍生作 &bull; 卡牌</div>
    </div>
    <div class="analytics-kpi-card">
      <div class="kpi-icon"><i class="fas fa-building"></i></div>
      <div class="kpi-value">{{ overview.total_organizations }}</div>
      <div class="kpi-label">合作与收录机构</div>
      <div class="kpi-sub">GF &bull; 任天堂 &bull; TPC &bull; 媒体</div>
    </div>
    <div class="analytics-kpi-card">
      <div class="kpi-icon"><i class="fas fa-calendar-star"></i></div>
      <div class="kpi-value">{{ overview.total_events }}</div>
      <div class="kpi-label">重大展会与事件</div>
      <div class="kpi-sub">E3 &bull; SpaceWorld &bull; 直面会</div>
    </div>
  </section>

  <!-- Section 1: 1000-Interview Archival Milestone -->
  <section class="analytics-panel" id="milestone">
    <div class="panel-header">
      <div class="panel-header-left">
        <span class="panel-tag">ARCHIVAL ROADMAP</span>
        <h2 class="panel-title">访谈收录千篇工程进度观测</h2>
        <p class="panel-desc">面向宝可梦三十载开发秘辛的抢救性数字归档，致力于打造全球中文互联网最完备的中日双语对照创作者访谈文库。</p>
      </div>
      <div class="panel-header-badge">
        <strong>{{ overview.total_interviews_imported }}</strong> / {{ overview.target_milestone }} 篇
      </div>
    </div>

    <div class="milestone-progress-wrap">
      <div class="milestone-progress-bar-bg">
        <div class="milestone-progress-bar-fill" style="width: {{ overview.interview_progress_pct }}%;">
          <span class="milestone-progress-label">{{ overview.interview_progress_pct }}% 达成</span>
        </div>
      </div>
      <div class="milestone-markers">
        <span class="marker marker--0">0 篇 (起点)</span>
        <span class="marker marker--200">200 篇 (Phase 1)</span>
        <span class="marker marker--400">400 篇 (Phase 2)</span>
        <span class="marker marker--600">600 篇 (Phase 3)</span>
        <span class="marker marker--800">800 篇 (Phase 4)</span>
        <span class="marker marker--1000">1000 篇 (千篇里程碑)</span>
      </div>
    </div>

    <div class="milestone-phases-grid">
      <div class="phase-card phase-card--done">
        <div class="phase-status-badge"><i class="fas fa-check-circle"></i> 已达成</div>
        <h4 class="phase-title">第一阶段：初代黎明与官方通讯 (1996&ndash;2002)</h4>
        <p class="phase-desc">涵盖 GB/GBC 时代田尻智、石原恒和、增田顺一早期访谈，Game Freak 官方通讯，MicroGroup 早期文献等 1&ndash;200 篇。</p>
      </div>
      <div class="phase-card phase-card--done">
        <div class="phase-status-badge"><i class="fas fa-check-circle"></i> 已达成</div>
        <h4 class="phase-title">第二阶段：掌机黄金时代与社长访谈 (2002&ndash;2010)</h4>
        <p class="phase-desc">GBA/NDS 时期跨越，包括全套《社长提问》（岩田聪对谈宝石/珍钻/心金魂银）以及北美任天堂官方专访等 201&ndash;400 篇。</p>
      </div>
      <div class="phase-card phase-card--active">
        <div class="phase-status-badge phase-badge--pulse"><i class="fas fa-spinner fa-spin"></i> 冲刺中 (474 / 600)</div>
        <h4 class="phase-title">第三阶段：首藤刚志专栏与 3DS/Switch 时代 (2010&ndash;2019)</h4>
        <p class="phase-desc">全网独家首藤刚志原版生前博客专栏全译、黑白/XY/日月总监大访谈、GAME FREAK 员工专栏深度校订。</p>
      </div>
      <div class="phase-card phase-card--pending">
        <div class="phase-status-badge phase-badge--gray"><i class="fas fa-clock"></i> 规划编纂中</div>
        <h4 class="phase-title">第四阶段：全媒体生态与现代文献 (2019&ndash;2026+)</h4>
        <p class="phase-desc">剑盾/朱紫/阿尔宙斯新世代访谈、PTCG 卡牌设计师深度对谈、欧美开发者特辑，向 1000+ 篇终极目标进发！</p>
      </div>
    </div>
  </section>

  <!-- Section 2: 3D Flip Card Generation Matrix -->
  <section class="analytics-panel" id="matrix">
    <div class="panel-header">
      <div class="panel-header-left">
        <span class="panel-tag">GENERATION MATRIX</span>
        <h2 class="panel-title">全世代作品双语矩阵 &bull; 3D 翻转卡片</h2>
        <p class="panel-desc">
          涵盖正作全部九个世代与跨媒介衍生生态。卡片<strong>正面呈现中文官方译名与文献收录量</strong>，<strong>背面呈现全球权威英文缩写</strong>（如 ORAS、BDSP、LGPE、FRLG、HGSS、PTCG 等）与英文全名。<br>
          系统每隔约 <strong>10 秒</strong> 自动平滑翻转，亦可随时手动点击卡片或使用下方开关随时切换。
        </p>
      </div>
      <div class="panel-controls">
        <button id="toggle-flip-btn" class="analytics-btn-primary" type="button">
          <i class="fas fa-sync-alt"></i> <span>翻转全部卡片 (中文 ⇋ 英文缩写)</span>
        </button>
        <span class="flip-timer-indicator" id="flip-timer-indicator">
          <i class="fas fa-clock"></i> <span id="timer-text">10秒自动轮播中</span>
        </span>
      </div>
    </div>

    <div class="generation-matrix-container">
      {% for gen in gen_matrix %}
        <div class="gen-era-block">
          <div class="gen-era-banner">
            <div class="gen-era-badge">{{ gen.gen }}</div>
            <div class="gen-era-info">
              <h3 class="gen-era-cn">{{ gen.era_cn }}</h3>
              <span class="gen-era-en">{{ gen.era_en }}</span>
            </div>
            <div class="gen-era-stat">
              <strong>{{ gen.total_posts }}</strong> 篇文献
            </div>
          </div>

          <div class="gen-cards-grid">
            {% for work in gen.works %}
              <div class="analytics-flip-card" data-work-abbr="{{ work.abbr }}" tabindex="0" role="button" aria-label="点击翻转查看 {{ work.cn }} 英文缩写与详情">
                <div class="analytics-flip-card__inner">
                  <!-- Front Face: Chinese Title -->
                  <div class="analytics-flip-card__face analytics-flip-card__face--front">
                    <div class="card-top-row">
                      <span class="card-abbr-badge">{{ work.abbr }}</span>
                      <span class="card-year-tag">{{ work.year }}</span>
                    </div>
                    <div class="card-center">
                      <h4 class="card-title-cn">{{ work.cn }}</h4>
                    </div>
                    <div class="card-bottom-row">
                      <span class="card-posts-count"><i class="fas fa-file-alt"></i> {{ work.posts_count }} 篇文献</span>
                      <span class="card-flip-prompt">翻转 ⇄</span>
                    </div>
                  </div>
                  <!-- Back Face: English Title & Abbreviation -->
                  <div class="analytics-flip-card__face analytics-flip-card__face--back">
                    <div class="card-top-row">
                      <span class="card-abbr-badge card-abbr-badge--accent">{{ work.abbr }}</span>
                      <span class="card-year-tag">{{ work.year }}</span>
                    </div>
                    <div class="card-center">
                      <div class="card-abbr-large">{{ work.abbr }}</div>
                      <h4 class="card-title-en">{{ work.en }}</h4>
                    </div>
                    <div class="card-bottom-row">
                      <a href="{{ work.url | relative_url }}" class="card-explore-link" onclick="event.stopPropagation();">
                        查看专页 ({{ work.posts_count }}) &rarr;
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            {% endfor %}
          </div>
        </div>
      {% endfor %}
    </div>
  </section>

  <!-- Section 3: Creators Hall of Fame -->
  <section class="analytics-panel" id="hall-of-fame">
    <div class="panel-header">
      <div class="panel-header-left">
        <span class="panel-tag">CREATORS HALL OF FAME</span>
        <h2 class="panel-title">业界名家殿堂 &bull; 核心创作者群像</h2>
        <p class="panel-desc">按全站收录文献量与深度访谈综合排序。凝聚了宝可梦之父、历代总监、音乐大师、美术设计师与关键制片人的珍贵历史印记。</p>
      </div>
      <div class="panel-header-badge">
        共收录 <strong>{{ hof | size }}</strong> 位领军名家
      </div>
    </div>

    <div class="creators-hof-grid">
      {% for person in hof %}
        <a href="{{ person.url | relative_url }}" class="creator-card">
          <div class="creator-card__header">
            <div class="creator-avatar-badge">{{ person.name | slice: 0 }}</div>
            <div class="creator-names">
              <h4 class="creator-name-cn">{{ person.name }}</h4>
              <span class="creator-name-other">{{ person.name_ja }} &bull; {{ person.name_en }}</span>
            </div>
            <div class="creator-posts-badge">
              <strong>{{ person.posts_count }}</strong>
              <small>篇文献</small>
            </div>
          </div>
          <div class="creator-role-box">
            <i class="fas fa-id-badge"></i> {{ person.role }}
          </div>
          <div class="creator-footer">
            <span class="creator-years"><i class="fas fa-calendar-alt"></i> 活跃: {{ person.years_active }}</span>
            <span class="creator-view-arrow">进入人物主页 &rarr;</span>
          </div>
        </a>
      {% endfor %}
    </div>
  </section>

  <!-- Section 4: GF Staff Blog Voices -->
  <section class="analytics-panel" id="staff-voices">
    <div class="panel-header">
      <div class="panel-header-left">
        <span class="panel-tag">STAFF DIARY VOICES</span>
        <h2 class="panel-title">GAME FREAK 员工博客生活切片 &bull; 专栏博主</h2>
        <p class="panel-desc">《晴时偶有阴》官方员工博客（2007&ndash;2012）中的一线开发者笔名。记载了企划构思、社内对战、音乐创作与日常生活的生动微观切片。</p>
      </div>
      <div class="panel-header-badge">
        <strong>209</strong> 篇员工日志归档
      </div>
    </div>

    <div class="staff-voices-grid">
      {% for member in staff %}
        <a href="{{ member.url | relative_url }}" class="staff-voice-card">
          <div class="staff-voice-top">
            <span class="staff-voice-kana">{{ member.name_ja }}</span>
            <span class="staff-voice-cn">（{{ member.name }}）</span>
            <span class="staff-voice-count">{{ member.posts_count }} 篇</span>
          </div>
          <p class="staff-voice-role">{{ member.role }}</p>
        </a>
      {% endfor %}
    </div>
  </section>

  <!-- Section 5: Chronological Density Timeline -->
  <section class="analytics-panel" id="timeline">
    <div class="panel-header">
      <div class="panel-header-left">
        <span class="panel-tag">CHRONOLOGICAL DENSITY</span>
        <h2 class="panel-title">三十载历史文献密度编年分布 (1990&ndash;2026)</h2>
        <p class="panel-desc">直观呈现全站文献在历史时间轴上的分布波峰。突出展现了 2008&ndash;2010 年（珍钻/心金魂银/黑白黄金交接期）与 2016 年（宝可梦 20 周年狂欢）等重大历史高峰。</p>
      </div>
      <div class="panel-header-badge">
        <strong>{{ timeline | size }}</strong> 个收录历史年份
      </div>
    </div>

    <div class="timeline-bars-container">
      {% for item in timeline %}
        {% assign height_pct = item.posts | times: 100 | divided_by: 230 %}
        {% if height_pct > 100 %}{% assign height_pct = 100 %}{% endif %}
        {% if item.posts > 0 and height_pct < 6 %}{% assign height_pct = 6 %}{% endif %}
        <div class="timeline-bar-column {% if item.posts >= 50 %}timeline-bar-column--peak{% endif %}">
          <div class="timeline-bar-tooltip">{{ item.year }}年: {{ item.posts }} 篇文献</div>
          <div class="timeline-bar-track">
            <div class="timeline-bar-fill" style="height: {{ height_pct }}%;">
              {% if item.posts >= 20 %}
                <span class="bar-count-label">{{ item.posts }}</span>
              {% endif %}
            </div>
          </div>
          <div class="timeline-bar-year">{{ item.year }}</div>
        </div>
      {% endfor %}
    </div>
    <div class="timeline-notes-box">
      <span class="note-pill"><i class="fas fa-fire"></i> 2016年 巅峰高峰: 227 篇 (20周年纪念特辑 & Pokémon GO 席卷全球)</span>
      <span class="note-pill"><i class="fas fa-crown"></i> 2008&ndash;2010年 黄金三部曲: 273 篇 (心金魂银、白金与黑白公布)</span>
      <span class="note-pill"><i class="fas fa-seedling"></i> 1996&ndash;2000年 创世黎明: 初代红绿蓝黄与第二世代奠基纪事</span>
    </div>
  </section>

  <!-- Section 6: Organizations & Outlets -->
  <section class="analytics-panel" id="organizations">
    <div class="panel-header">
      <div class="panel-header-left">
        <span class="panel-tag">INSTITUTIONAL NETWORK</span>
        <h2 class="panel-title">制作机构与媒体传播网络</h2>
        <p class="panel-desc">收录涉及的核心开发公司、发行商、合作工作室与三十年间报道宝可梦的最具公信力媒体阵列。</p>
      </div>
    </div>

    <div class="orgs-grid">
      {% for org in top_orgs %}
        <a href="{{ org.url | relative_url }}" class="org-card">
          <div class="org-card-icon"><i class="fas fa-building"></i></div>
          <div class="org-card-info">
            <h4 class="org-card-name">{{ org.name }}</h4>
            <span class="org-card-posts">{{ org.posts_count }} 篇相关文献</span>
          </div>
          <div class="org-card-arrow">&rarr;</div>
        </a>
      {% endfor %}
    </div>
  </section>

  <!-- Section 7: Data Governance & Integrity Architecture -->
  <section class="analytics-panel panel--governance" id="governance">
    <div class="panel-header">
      <div class="panel-header-left">
        <span class="panel-tag panel-tag--gold">DATA INTEGRITY & INFRASTRUCTURE</span>
        <h2 class="panel-title">底层数据治理与元数据规范体系</h2>
        <p class="panel-desc">彻底杜绝“中日人名空格分裂”、“作品标点不统一”、“英文缩写混乱”等历史痛点，构建企业级规范化索引中枢。</p>
      </div>
    </div>

    <div class="governance-kpi-row">
      <div class="gov-kpi">
        <strong>{{ gov.posts_normalized }}</strong>
        <span>篇历史文章修正</span>
      </div>
      <div class="gov-kpi">
        <strong>{{ gov.replacements_made }}</strong>
        <span>处裂解实体清洗合并</span>
      </div>
      <div class="gov-kpi">
        <strong>{{ gov.duplicate_clusters_after }}</strong>
        <span>个裂解孤岛 (彻底清零)</span>
      </div>
      <div class="gov-kpi">
        <strong>{{ gov.rules_active }}</strong>
        <span>条规范化映射规则生效中</span>
      </div>
    </div>

    <div class="governance-specs-grid">
      <div class="spec-card">
        <div class="spec-icon"><i class="fas fa-magic"></i></div>
        <h4>中日韩文字正则智能去空格</h4>
        <p>
          针对 <code>增田 顺一</code>、<code>石原 恒和</code> 等历史遗留空格，底层引擎采用 <code>(?&lt;=[\p{Han}\p{Hiragana}\p{Katakana}])\s+(?=[\p{Han}\p{Hiragana}\p{Katakana}])</code> 正则，仅智能剔除 CJK 表意文字之间的全半角空格，<strong>严谨保留 Western 欧美作者（如 <code>James Turner</code>、<code>Kevin Knezevic</code>）的正常词间空格</strong>。
        </p>
      </div>
      <div class="spec-card">
        <div class="spec-icon"><i class="fas fa-sliders-h"></i></div>
        <h4>作品标点标准化 (斜杠统一居中点)</h4>
        <p>
          彻底纠正 <code>宝可梦 红／绿</code>、<code>宝可梦 剑／盾</code> 中易造成 Markdown 渲染歧义的半角与全角斜杠，全站统一为国家标准书名连接符 <code>·</code>（如 <code>宝可梦 红·绿</code>、<code>宝可梦 剑·盾</code>），从根本上合并分散在各处的作品计数。
        </p>
      </div>
      <div class="spec-card">
        <div class="spec-icon"><i class="fas fa-book"></i></div>
        <h4>CANONICAL 权威词典双重校验</h4>
        <p>
          在 <code>tools/build-resource-index.rb</code> 构建管线中嵌入权威实体字典（Canonical Map），涵盖人物原名假名映射、机构全称与简写映射（如 <code>株式会社ゲームフリーク</code> 统一归纳至 <code>Game Freak</code>），确保任何新入库文章自动享受全局治理红利。
        </p>
      </div>
      <div class="spec-card">
        <div class="spec-icon"><i class="fas fa-network-wired"></i></div>
        <h4>全站实体图谱动态同步构建</h4>
        <p>
          结合 <code>tools/build-resource-index.rb</code> 与 <code>tools/build-resource-graph.rb</code>，每次构建均自动输出零冗余的 <code>_data/resource-index.json</code> 并生成规范的实体详情页（<code>/entities/...</code>），保证时间线、关系图谱与全景分析数据源高度同步。
        </p>
      </div>
    </div>
  </section>
</div>

<!-- Scoped Styles for Analytics Dashboard -->
<style>
/* Root Container */
.archive-analytics-root {
  margin: 0 auto;
  padding: 1rem 0 4rem;
  color: var(--text-color, #2d3748);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  line-height: 1.6;
}

/* Hero Section */
.analytics-hero {
  text-align: center;
  padding: 3rem 1.5rem 2.5rem;
  background: linear-gradient(135deg, rgba(235, 12, 12, 0.08) 0%, rgba(30, 64, 175, 0.08) 100%);
  border-radius: 16px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  margin-bottom: 2rem;
  backdrop-filter: blur(8px);
}
.analytics-hero__badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #eb0c0c;
  background: rgba(235, 12, 12, 0.12);
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  margin-bottom: 1rem;
}
.analytics-hero__title {
  font-size: 2.2rem;
  font-weight: 800;
  margin: 0 0 1rem;
  letter-spacing: -0.02em;
  color: inherit;
}
.analytics-hero__subtitle {
  font-size: 1.05rem;
  max-width: 860px;
  margin: 0 auto 1.75rem;
  opacity: 0.88;
}
.analytics-hero__subtitle strong {
  color: #eb0c0c;
  font-weight: 700;
}
.analytics-nav-anchors {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.65rem;
}
.analytics-nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(203, 213, 225, 0.8);
  border-radius: 8px;
  font-size: 0.88rem;
  font-weight: 600;
  color: #334155;
  text-decoration: none;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.analytics-nav-btn:hover {
  background: #ffffff;
  color: #eb0c0c;
  border-color: #eb0c0c;
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(235, 12, 12, 0.15);
}

/* Dark theme hero adjustment */
body.theme-bg-black .analytics-hero {
  background: linear-gradient(135deg, rgba(235, 12, 12, 0.15) 0%, rgba(30, 64, 175, 0.2) 100%);
  border-color: rgba(255, 255, 255, 0.12);
}
body.theme-bg-black .analytics-nav-btn {
  background: rgba(30, 41, 59, 0.85);
  color: #e2e8f0;
  border-color: rgba(255, 255, 255, 0.1);
}
body.theme-bg-black .analytics-nav-btn:hover {
  background: #1e293b;
  color: #ff6b6b;
  border-color: #ff6b6b;
}

/* KPI Container */
.analytics-kpi-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  margin-bottom: 2.5rem;
}
.analytics-kpi-card {
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 12px;
  padding: 1.25rem 1rem;
  text-align: center;
  transition: all 0.25s ease;
  backdrop-filter: blur(6px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
}
.analytics-kpi-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  border-color: rgba(235, 12, 12, 0.4);
}
.kpi-card--highlight {
  background: linear-gradient(145deg, rgba(235, 12, 12, 0.06), rgba(255, 255, 255, 0.9));
  border-color: rgba(235, 12, 12, 0.35);
}
.kpi-icon {
  font-size: 1.25rem;
  color: #eb0c0c;
  margin-bottom: 0.4rem;
}
.kpi-value {
  font-size: 1.85rem;
  font-weight: 800;
  line-height: 1.1;
  color: inherit;
  margin-bottom: 0.3rem;
}
.kpi-label {
  font-size: 0.88rem;
  font-weight: 700;
  color: inherit;
  margin-bottom: 0.2rem;
}
.kpi-sub {
  font-size: 0.72rem;
  opacity: 0.65;
}

body.theme-bg-black .analytics-kpi-card {
  background: rgba(30, 41, 59, 0.7);
  border-color: rgba(255, 255, 255, 0.08);
}
body.theme-bg-black .kpi-card--highlight {
  background: linear-gradient(145deg, rgba(235, 12, 12, 0.18), rgba(30, 41, 59, 0.85));
  border-color: rgba(235, 12, 12, 0.5);
}

/* Generic Panel Styling */
.analytics-panel {
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2.5rem;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}
body.theme-bg-black .analytics-panel {
  background: rgba(30, 41, 59, 0.5);
  border-color: rgba(255, 255, 255, 0.08);
}
.panel-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.75rem;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
  padding-bottom: 1.25rem;
}
body.theme-bg-black .panel-header {
  border-bottom-color: rgba(255, 255, 255, 0.08);
}
.panel-tag {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #2563eb;
  background: rgba(37, 99, 235, 0.1);
  padding: 0.25rem 0.65rem;
  border-radius: 4px;
  margin-bottom: 0.4rem;
}
.panel-tag--gold {
  color: #b45309;
  background: rgba(245, 158, 11, 0.15);
}
.panel-title {
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0 0 0.4rem;
  letter-spacing: -0.01em;
}
.panel-desc {
  font-size: 0.92rem;
  opacity: 0.8;
  margin: 0;
  max-width: 820px;
}
.panel-header-badge {
  font-size: 1rem;
  font-weight: 700;
  padding: 0.5rem 1.1rem;
  background: rgba(235, 12, 12, 0.1);
  color: #eb0c0c;
  border-radius: 999px;
  border: 1px solid rgba(235, 12, 12, 0.2);
  white-space: nowrap;
}

/* Milestone Progress */
.milestone-progress-wrap {
  margin: 1.75rem 0 2rem;
}
.milestone-progress-bar-bg {
  height: 28px;
  background: rgba(203, 213, 225, 0.4);
  border-radius: 14px;
  overflow: hidden;
  position: relative;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
}
.milestone-progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #eb0c0c 0%, #f97316 50%, #3b82f6 100%);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 12px;
  border-radius: 14px;
  transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}
.milestone-progress-label {
  color: #ffffff;
  font-size: 0.78rem;
  font-weight: 800;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.4);
  white-space: nowrap;
}
.milestone-markers {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  opacity: 0.7;
  font-weight: 600;
  margin-top: 0.6rem;
}

.milestone-phases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
}
.phase-card {
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 10px;
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.75);
}
body.theme-bg-black .phase-card {
  background: rgba(30, 41, 59, 0.7);
  border-color: rgba(255, 255, 255, 0.08);
}
.phase-card--done {
  border-left: 4px solid #10b981;
}
.phase-card--active {
  border-left: 4px solid #eb0c0c;
  background: linear-gradient(135deg, rgba(235, 12, 12, 0.04), rgba(255, 255, 255, 0.85));
}
body.theme-bg-black .phase-card--active {
  background: linear-gradient(135deg, rgba(235, 12, 12, 0.15), rgba(30, 41, 59, 0.85));
}
.phase-card--pending {
  border-left: 4px solid #94a3b8;
  opacity: 0.75;
}
.phase-status-badge {
  font-size: 0.75rem;
  font-weight: 700;
  color: #10b981;
  margin-bottom: 0.5rem;
}
.phase-badge--pulse {
  color: #eb0c0c;
}
.phase-badge--gray {
  color: #64748b;
}
.phase-title {
  font-size: 0.95rem;
  font-weight: 700;
  margin: 0 0 0.4rem;
}
.phase-desc {
  font-size: 0.82rem;
  opacity: 0.8;
  margin: 0;
  line-height: 1.5;
}

/* Section 2: 3D Flip Card Generation Matrix */
.panel-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.analytics-btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #eb0c0c;
  color: #ffffff !important;
  border: none;
  padding: 0.6rem 1.25rem;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(235, 12, 12, 0.3);
  transition: all 0.2s ease;
}
.analytics-btn-primary:hover {
  background: #c90a0a;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(235, 12, 12, 0.4);
}
.flip-timer-indicator {
  font-size: 0.8rem;
  opacity: 0.75;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.generation-matrix-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.gen-era-block {
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(226, 232, 240, 0.7);
  border-radius: 12px;
  padding: 1.25rem;
}
body.theme-bg-black .gen-era-block {
  background: rgba(30, 41, 59, 0.4);
  border-color: rgba(255, 255, 255, 0.06);
}
.gen-era-banner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px dashed rgba(203, 213, 225, 0.7);
}
body.theme-bg-black .gen-era-banner {
  border-bottom-color: rgba(255, 255, 255, 0.1);
}
.gen-era-badge {
  font-size: 0.82rem;
  font-weight: 800;
  padding: 0.3rem 0.75rem;
  background: #1e293b;
  color: #f8fafc;
  border-radius: 6px;
  letter-spacing: 0.05em;
}
body.theme-bg-black .gen-era-badge {
  background: #334155;
}
.gen-era-info {
  flex: 1;
  min-width: 200px;
}
.gen-era-cn {
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0;
}
.gen-era-en {
  font-size: 0.75rem;
  opacity: 0.65;
  display: block;
}
.gen-era-stat {
  font-size: 0.88rem;
  font-weight: 600;
  opacity: 0.85;
}
.gen-era-stat strong {
  font-size: 1.15rem;
  color: #eb0c0c;
}

/* 3D Flip Card Component */
.gen-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.15rem;
}

.analytics-flip-card {
  background-color: transparent;
  width: 100%;
  height: 150px;
  perspective: 1000px;
  cursor: pointer;
  user-select: none;
}
.analytics-flip-card__inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: left;
  transition: transform 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
  transform-style: preserve-3d;
  border-radius: 12px;
}
.analytics-flip-card.is-flipped .analytics-flip-card__inner {
  transform: rotateY(180deg);
}

.analytics-flip-card__face {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: border-color 0.2s, box-shadow 0.2s;
}
.analytics-flip-card:hover .analytics-flip-card__face {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  border-color: rgba(235, 12, 12, 0.4);
}

/* Front Face */
.analytics-flip-card__face--front {
  background: rgba(255, 255, 255, 0.92);
}
body.theme-bg-black .analytics-flip-card__face--front {
  background: rgba(30, 41, 59, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}
.card-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-abbr-badge {
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  background: rgba(235, 12, 12, 0.1);
  color: #eb0c0c;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
}
.card-abbr-badge--accent {
  background: #eb0c0c;
  color: #ffffff;
}
.card-year-tag {
  font-size: 0.72rem;
  font-weight: 600;
  opacity: 0.65;
}
.card-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.card-title-cn {
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.35;
}
.card-bottom-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
}
.card-posts-count {
  font-weight: 600;
  color: #eb0c0c;
}
.card-flip-prompt {
  opacity: 0.55;
  font-weight: 600;
}

/* Back Face */
.analytics-flip-card__face--back {
  background: linear-gradient(145deg, #1e293b, #0f172a);
  color: #f8fafc;
  border-color: #334155;
  transform: rotateY(180deg);
}
.card-abbr-large {
  font-size: 1.6rem;
  font-weight: 900;
  letter-spacing: 0.05em;
  color: #fbbf24;
  line-height: 1;
  margin-bottom: 0.25rem;
}
.card-title-en {
  font-size: 0.82rem;
  font-weight: 600;
  margin: 0;
  color: #cbd5e1;
  line-height: 1.25;
}
.card-explore-link {
  color: #fbbf24 !important;
  font-weight: 700;
  font-size: 0.78rem;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  transition: transform 0.2s;
}
.card-explore-link:hover {
  transform: translateX(3px);
  text-decoration: underline;
}

/* Creators Hall of Fame */
.creators-hof-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.15rem;
}
.creator-card {
  display: block;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 12px;
  padding: 1.25rem;
  text-decoration: none !important;
  color: inherit !important;
  transition: all 0.25s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
}
body.theme-bg-black .creator-card {
  background: rgba(30, 41, 59, 0.7);
  border-color: rgba(255, 255, 255, 0.08);
}
.creator-card:hover {
  transform: translateY(-3px);
  border-color: #eb0c0c;
  box-shadow: 0 8px 20px rgba(235, 12, 12, 0.12);
}
.creator-card__header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}
.creator-avatar-badge {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: linear-gradient(135deg, #eb0c0c, #f97316);
  color: #ffffff;
  font-weight: 800;
  font-size: 1.15rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(235, 12, 12, 0.3);
}
.creator-names {
  flex: 1;
  min-width: 0;
}
.creator-name-cn {
  font-size: 1.05rem;
  font-weight: 800;
  margin: 0 0 0.15rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.creator-name-other {
  font-size: 0.72rem;
  opacity: 0.65;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.creator-posts-badge {
  text-align: right;
  flex-shrink: 0;
}
.creator-posts-badge strong {
  display: block;
  font-size: 1.35rem;
  font-weight: 800;
  color: #eb0c0c;
  line-height: 1;
}
.creator-posts-badge small {
  font-size: 0.68rem;
  opacity: 0.65;
}
.creator-role-box {
  font-size: 0.82rem;
  font-weight: 600;
  background: rgba(241, 245, 249, 0.8);
  padding: 0.45rem 0.75rem;
  border-radius: 6px;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: #334155;
}
body.theme-bg-black .creator-role-box {
  background: rgba(15, 23, 42, 0.6);
  color: #cbd5e1;
}
.creator-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  opacity: 0.75;
}
.creator-view-arrow {
  font-weight: 700;
  color: #eb0c0c;
}

/* Staff Voices Grid */
.staff-voices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.85rem;
}
.staff-voice-card {
  display: block;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 8px;
  padding: 0.85rem 1rem;
  text-decoration: none !important;
  color: inherit !important;
  transition: all 0.2s ease;
}
body.theme-bg-black .staff-voice-card {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(255, 255, 255, 0.06);
}
.staff-voice-card:hover {
  border-color: #2563eb;
  transform: translateY(-2px);
}
.staff-voice-top {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
  margin-bottom: 0.35rem;
}
.staff-voice-kana {
  font-weight: 700;
  font-size: 0.95rem;
}
.staff-voice-cn {
  font-size: 0.8rem;
  opacity: 0.75;
}
.staff-voice-count {
  margin-left: auto;
  font-size: 0.72rem;
  font-weight: 700;
  color: #2563eb;
  background: rgba(37, 99, 235, 0.1);
  padding: 0.1rem 0.45rem;
  border-radius: 4px;
}
.staff-voice-role {
  font-size: 0.75rem;
  opacity: 0.7;
  margin: 0;
  line-height: 1.4;
}

/* Chronological Density Bar Chart */
.timeline-bars-container {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 240px;
  padding: 1.5rem 0.5rem 0.5rem;
  border-bottom: 2px solid rgba(203, 213, 225, 0.8);
  margin-bottom: 1.5rem;
  overflow-x: auto;
}
body.theme-bg-black .timeline-bars-container {
  border-bottom-color: rgba(255, 255, 255, 0.15);
}
.timeline-bar-column {
  flex: 1;
  min-width: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  position: relative;
  cursor: pointer;
}
.timeline-bar-track {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}
.timeline-bar-fill {
  width: 100%;
  max-width: 28px;
  background: linear-gradient(180deg, #60a5fa 0%, #2563eb 100%);
  border-radius: 4px 4px 0 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 4px;
  transition: all 0.3s ease;
}
.timeline-bar-column--peak .timeline-bar-fill {
  background: linear-gradient(180deg, #f87171 0%, #eb0c0c 100%);
  box-shadow: 0 0 10px rgba(235, 12, 12, 0.3);
}
.timeline-bar-column:hover .timeline-bar-fill {
  filter: brightness(1.2);
  transform: scaleY(1.04);
}
.bar-count-label {
  font-size: 0.65rem;
  font-weight: 800;
  color: #ffffff;
  writing-mode: vertical-rl;
  text-orientation: mixed;
  transform: rotate(180deg);
  opacity: 0.9;
}
.timeline-bar-year {
  font-size: 0.68rem;
  font-weight: 600;
  opacity: 0.7;
  margin-top: 0.4rem;
  transform: rotate(-45deg);
  transform-origin: top left;
  white-space: nowrap;
}
.timeline-bar-tooltip {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: #0f172a;
  color: #f8fafc;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s;
  z-index: 10;
}
.timeline-bar-column:hover .timeline-bar-tooltip {
  opacity: 1;
}

.timeline-notes-box {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding-top: 1rem;
}
.note-pill {
  font-size: 0.8rem;
  font-weight: 600;
  background: rgba(241, 245, 249, 0.8);
  border: 1px solid rgba(226, 232, 240, 0.8);
  padding: 0.4rem 0.85rem;
  border-radius: 999px;
  color: #334155;
}
body.theme-bg-black .note-pill {
  background: rgba(30, 41, 59, 0.8);
  border-color: rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
}

/* Organizations Grid */
.orgs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}
.org-card {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 10px;
  padding: 0.9rem 1.1rem;
  text-decoration: none !important;
  color: inherit !important;
  transition: all 0.2s ease;
}
body.theme-bg-black .org-card {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(255, 255, 255, 0.08);
}
.org-card:hover {
  border-color: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
}
.org-card-icon {
  font-size: 1.15rem;
  color: #2563eb;
}
.org-card-info {
  flex: 1;
  min-width: 0;
}
.org-card-name {
  font-size: 0.95rem;
  font-weight: 700;
  margin: 0 0 0.15rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.org-card-posts {
  font-size: 0.75rem;
  opacity: 0.65;
}
.org-card-arrow {
  font-weight: 700;
  color: #2563eb;
  opacity: 0.5;
  transition: transform 0.2s;
}
.org-card:hover .org-card-arrow {
  opacity: 1;
  transform: translateX(3px);
}

/* Governance Panel */
.panel--governance {
  border-color: rgba(245, 158, 11, 0.3);
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.04), rgba(255, 255, 255, 0.7));
}
body.theme-bg-black .panel--governance {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(30, 41, 59, 0.7));
  border-color: rgba(245, 158, 11, 0.25);
}
.governance-kpi-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1.75rem;
}
.gov-kpi {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 10px;
  padding: 1.15rem;
  text-align: center;
}
body.theme-bg-black .gov-kpi {
  background: rgba(15, 23, 42, 0.6);
  border-color: rgba(255, 255, 255, 0.08);
}
.gov-kpi strong {
  display: block;
  font-size: 1.85rem;
  font-weight: 800;
  color: #b45309;
  line-height: 1;
  margin-bottom: 0.35rem;
}
.gov-kpi span {
  font-size: 0.8rem;
  font-weight: 600;
  opacity: 0.8;
}

.governance-specs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.15rem;
}
.spec-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 10px;
  padding: 1.25rem;
}
body.theme-bg-black .spec-card {
  background: rgba(15, 23, 42, 0.6);
  border-color: rgba(255, 255, 255, 0.08);
}
.spec-icon {
  font-size: 1.25rem;
  color: #b45309;
  margin-bottom: 0.6rem;
}
.spec-card h4 {
  font-size: 0.98rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
}
.spec-card p {
  font-size: 0.83rem;
  opacity: 0.85;
  margin: 0;
  line-height: 1.55;
}
.spec-card code {
  background: rgba(0, 0, 0, 0.06);
  padding: 0.15rem 0.35rem;
  border-radius: 4px;
  font-size: 0.8em;
  color: #b45309;
}
body.theme-bg-black .spec-card code {
  background: rgba(255, 255, 255, 0.1);
  color: #fcd34d;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .analytics-hero__title {
    font-size: 1.65rem;
  }
  .panel-title {
    font-size: 1.25rem;
  }
  .gen-cards-grid {
    grid-template-columns: 1fr 1fr;
  }
}
@media (max-width: 480px) {
  .gen-cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<!-- Script for Smooth 3D Flip Card Transition (~10s Interval) -->
<script>
(function() {
  var cards = document.querySelectorAll('.analytics-flip-card');
  var toggleBtn = document.getElementById('toggle-flip-btn');
  var timerIndicator = document.getElementById('timer-text');
  var matrixContainer = document.querySelector('.generation-matrix-container');

  if (!cards.length) return;

  var isAllFlipped = false;
  var FLIP_INTERVAL_MS = 10000;
  var autoFlipTimer = null;
  var isPaused = false;
  var countdown = 10;
  var countdownTimer = null;

  // Individual card manual click
  cards.forEach(function(card) {
    card.addEventListener('click', function(e) {
      // Don't flip if user clicked directly on the internal link
      if (e.target.closest('.card-explore-link')) return;
      card.classList.toggle('is-flipped');
    });
  });

  // Toggle all cards button
  if (toggleBtn) {
    toggleBtn.addEventListener('click', function() {
      isAllFlipped = !isAllFlipped;
      flipAllCards(isAllFlipped);
      resetAutoFlipTimer();
    });
  }

  function flipAllCards(flipState) {
    cards.forEach(function(card, idx) {
      // Small staggered delay for visual elegance
      setTimeout(function() {
        if (flipState) {
          card.classList.add('is-flipped');
        } else {
          card.classList.remove('is-flipped');
        }
      }, idx * 25);
    });
  }

  // Automatic Flip Loop
  function startAutoFlip() {
    countdown = 10;
    updateTimerText();

    if (countdownTimer) clearInterval(countdownTimer);
    countdownTimer = setInterval(function() {
      if (!isPaused) {
        countdown--;
        if (countdown <= 0) countdown = 10;
        updateTimerText();
      }
    }, 1000);

    if (autoFlipTimer) clearInterval(autoFlipTimer);
    autoFlipTimer = setInterval(function() {
      if (!isPaused) {
        isAllFlipped = !isAllFlipped;
        flipAllCards(isAllFlipped);
      }
    }, FLIP_INTERVAL_MS);
  }

  function updateTimerText() {
    if (timerIndicator) {
      if (isPaused) {
        timerIndicator.textContent = "轮播已暂停 (悬停中)";
      } else {
        timerIndicator.textContent = countdown + " 秒后自动翻转 (悬停暂停)";
      }
    }
  }

  function resetAutoFlipTimer() {
    countdown = 10;
    startAutoFlip();
  }

  // Pause on hover
  if (matrixContainer) {
    matrixContainer.addEventListener('mouseenter', function() {
      isPaused = true;
      updateTimerText();
    });
    matrixContainer.addEventListener('mouseleave', function() {
      isPaused = false;
      updateTimerText();
    });
  }

  // Start auto-flip on load
  startAutoFlip();
})();
</script>
