---
title: "本地编辑工具索引"
permalink: /local-editing-tools/
layout: single
search: true
sitemap: false
categories: [站点, 工具]
tags: [本地编辑, OCR, 翻译, 扫描分区, 网页访谈, DeepSeek, Qwen-VL-OCR]
archive_type: site_tooling
source:
  title: "Poke Amice Docs 本地工具"
  source_type: site_tooling
summary: "隐藏的本地编辑工具索引，可通过站内搜索进入，用于整理 OCR、翻译、网页访谈收录和发布流程。"
---

<style>
  .local-tools-page {
    width: min(1180px, calc(100vw - 48px));
    margin-left: 50%;
    transform: translateX(-50%);
  }

  .local-tools-hero {
    display: grid;
    grid-template-columns: minmax(0, 1.05fr) minmax(320px, 0.95fr);
    gap: 24px;
    align-items: stretch;
    margin: 8px 0 26px;
  }

  .local-tools-hero__copy {
    padding: 28px;
    border: 1px solid rgba(78, 103, 138, 0.18);
    border-radius: 8px;
    background:
      linear-gradient(135deg, rgba(250, 252, 255, 0.94), rgba(237, 246, 247, 0.8)),
      linear-gradient(90deg, rgba(77, 156, 180, 0.14), rgba(240, 185, 73, 0.12));
  }

  .local-tools-hero__copy p {
    margin: 0;
    color: #52636f;
  }

  .local-tools-hero__copy strong {
    display: block;
    margin-bottom: 10px;
    color: #476071;
    font-size: 0.82rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .local-tools-hero__copy h2 {
    margin: 0 0 12px;
    font-size: clamp(1.7rem, 4vw, 3rem);
    line-height: 1.08;
  }

  .local-tools-hero__panel {
    display: grid;
    gap: 10px;
    padding: 18px;
    border: 1px solid rgba(78, 103, 138, 0.18);
    border-radius: 8px;
    background: #fff;
  }

  .local-tool-search-chip {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 12px 14px;
    border-radius: 6px;
    background: #f6f8fb;
    color: #334452;
    font-size: 0.86rem;
  }

  .local-tool-search-chip code {
    padding: 0;
    background: transparent;
    color: #2b7896;
    font-size: 0.82rem;
  }

  .local-tools-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 18px;
    margin: 24px 0;
  }

  .local-tool-card {
    overflow: hidden;
    border: 1px solid rgba(76, 95, 120, 0.18);
    border-radius: 8px;
    background: #fff;
    box-shadow: 0 14px 38px rgba(42, 56, 74, 0.08);
  }

  .local-tool-card__preview {
    position: relative;
    height: 230px;
    overflow: hidden;
    background:
      linear-gradient(180deg, rgba(255, 255, 255, 0) 58%, rgba(255, 255, 255, 0.94) 100%),
      #eef4f6;
  }

  .local-tool-card__preview iframe {
    width: 1440px;
    height: 900px;
    border: 0;
    transform: scale(0.32);
    transform-origin: 0 0;
    pointer-events: none;
  }

  .local-tool-card__body {
    padding: 16px 18px 18px;
  }

  .local-tool-card__body h3 {
    display: flex;
    align-items: center;
    gap: 9px;
    margin: 0 0 8px;
    font-size: 1.05rem;
  }

  .local-tool-card__body p {
    margin: 0 0 14px;
    color: #516170;
    font-size: 0.88rem;
    line-height: 1.65;
  }

  .local-tool-card__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-bottom: 14px;
  }

  .local-tool-card__meta span {
    padding: 4px 8px;
    border: 1px solid rgba(44, 116, 145, 0.18);
    border-radius: 999px;
    background: #f3f8fa;
    color: #31576b;
    font-size: 0.72rem;
  }

  .local-tool-card__body a,
  .local-tools-flow a {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 11px;
    border-radius: 6px;
    background: #27475a;
    color: #fff;
    text-decoration: none;
    font-size: 0.82rem;
  }

  .local-tools-flow {
    margin: 30px 0 18px;
    padding: 22px;
    border: 1px solid rgba(76, 95, 120, 0.16);
    border-radius: 8px;
    background: #f9fbfc;
  }

  .local-tools-flow h2 {
    margin-top: 0;
    font-size: 1.25rem;
  }

  .local-tools-flow__steps {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 10px;
    margin: 16px 0 18px;
  }

  .local-tools-flow__steps div {
    min-height: 112px;
    padding: 13px;
    border-radius: 8px;
    background: #fff;
    border: 1px solid rgba(76, 95, 120, 0.12);
  }

  .local-tools-flow__steps span {
    display: inline-flex;
    width: 24px;
    height: 24px;
    align-items: center;
    justify-content: center;
    margin-bottom: 10px;
    border-radius: 50%;
    background: #dcecf1;
    color: #245468;
    font-size: 0.75rem;
    font-weight: 700;
  }

  .local-tools-flow__steps strong {
    display: block;
    margin-bottom: 6px;
    font-size: 0.9rem;
  }

  .local-tools-flow__steps p {
    margin: 0;
    color: #5d6972;
    font-size: 0.78rem;
    line-height: 1.5;
  }

  html[data-theme="dark"] .local-tools-hero__copy,
  html[data-theme="dark"] .local-tools-hero__panel,
  html[data-theme="dark"] .local-tool-card,
  html[data-theme="dark"] .local-tools-flow,
  html[data-theme="dark"] .local-tools-flow__steps div {
    border-color: rgba(214, 225, 236, 0.16);
    background: #182029;
    color: #e6edf3;
  }

  html[data-theme="dark"] .local-tools-hero__copy {
    background:
      linear-gradient(135deg, rgba(22, 28, 36, 0.96), rgba(22, 43, 50, 0.82)),
      linear-gradient(90deg, rgba(77, 156, 180, 0.18), rgba(240, 185, 73, 0.12));
  }

  html[data-theme="dark"] .local-tools-hero__copy p,
  html[data-theme="dark"] .local-tool-card__body p,
  html[data-theme="dark"] .local-tools-flow__steps p {
    color: #bac7d3;
  }

  html[data-theme="dark"] .local-tool-search-chip,
  html[data-theme="dark"] .local-tool-card__meta span {
    background: #202b36;
    color: #d8e4ed;
  }

  @media (max-width: 900px) {
    .local-tools-page {
      width: min(100%, calc(100vw - 24px));
    }

    .local-tools-hero,
    .local-tools-grid,
    .local-tools-flow__steps {
      grid-template-columns: 1fr;
    }

    .local-tool-card__preview {
      height: 190px;
    }

    .local-tool-card__preview iframe {
      transform: scale(0.27);
    }
  }
</style>

<div class="local-tools-page">
  <section class="local-tools-hero">
    <div class="local-tools-hero__copy">
      <strong>Hidden Editing Hub</strong>
      <h2>从扫描图到站点文章的本地工具启动台</h2>
      <p>这个页面不放在首页和顶部导航里，只作为站内搜索可发现的入口。进入后可以直接打开分区、OCR、翻译、网页收录和资料索引相关工具。</p>
    </div>
    <div class="local-tools-hero__panel" aria-label="可搜索关键词">
      <div class="local-tool-search-chip"><span>搜索入口</span><code>本地编辑工具</code></div>
      <div class="local-tool-search-chip"><span>扫描流程</span><code>扫描分区 / OCR 工作台</code></div>
      <div class="local-tool-search-chip"><span>VLM OCR</span><code>Qwen-VL-OCR / VLM</code></div>
      <div class="local-tool-search-chip"><span>翻译整理</span><code>DeepSeek 翻译 / 对照翻译</code></div>
    </div>
  </section>

  <section class="local-tools-grid" aria-label="本地工具预览">
    <article class="local-tool-card">
      <div class="local-tool-card__preview">
        <iframe src="/assets/tools/magazine-region-annotator.html" title="杂志分区工具预览" loading="lazy"></iframe>
      </div>
      <div class="local-tool-card__body">
        <h3><i class="fas fa-vector-square" aria-hidden="true"></i>杂志分区工具</h3>
        <p>导入扫描图，手动框选文字块、图片块和跨页段落，生成给 OCR 后端使用的分区 JSON。</p>
        <div class="local-tool-card__meta"><span>扫描图</span><span>跨栏</span><span>跨页合并</span><span>Qwen 命令</span></div>
        <a href="/assets/tools/editor-toolbox.html#region">在工具箱中打开</a>
      </div>
    </article>

    <article class="local-tool-card">
      <div class="local-tool-card__preview">
        <iframe src="/assets/tools/ocr-translation-workbench.html" title="OCR 翻译整理工作台预览" loading="lazy"></iframe>
      </div>
      <div class="local-tool-card__body">
        <h3><i class="fas fa-language" aria-hidden="true"></i>OCR 翻译整理工作台</h3>
        <p>导入 `translation-segments.yml`、OCR Markdown 或已有文章，整理日文原文、中文译文、评注和导出扫描对照页。</p>
        <div class="local-tool-card__meta"><span>YAML 导入</span><span>DeepSeek</span><span>译文格式</span><span>scan-translation</span></div>
        <a href="/assets/tools/editor-toolbox.html#ocr">在工具箱中打开</a>
      </div>
    </article>

    <article class="local-tool-card">
      <div class="local-tool-card__preview">
        <iframe src="/assets/tools/web-interview-capture.html" title="网页访谈收录工具预览" loading="lazy"></iframe>
      </div>
      <div class="local-tool-card__body">
        <h3><i class="fas fa-globe" aria-hidden="true"></i>网页访谈收录</h3>
        <p>粘贴网页正文或 HTML，清理页面噪音，补充来源和元数据，再生成可放入站点的 Markdown 草稿。</p>
        <div class="local-tool-card__meta"><span>网页正文</span><span>来源引用</span><span>front matter</span><span>草稿</span></div>
        <a href="/assets/tools/editor-toolbox.html#web">在工具箱中打开</a>
      </div>
    </article>

    <article class="local-tool-card">
      <div class="local-tool-card__preview">
        <iframe src="/assets/tools/project-workflow-board.html" title="项目工作流看板预览" loading="lazy"></iframe>
      </div>
      <div class="local-tool-card__body">
        <h3><i class="fas fa-tasks" aria-hidden="true"></i>项目工作流看板</h3>
        <p>登记素材、OCR、翻译、校对、发布阶段，把杂志访谈或网页资料整理成可追踪的项目。</p>
        <div class="local-tool-card__meta"><span>项目阶段</span><span>素材记录</span><span>发布检查</span><span>进度管理</span></div>
        <a href="/assets/tools/editor-toolbox.html#workflow">在工具箱中打开</a>
      </div>
    </article>
  </section>

  <section class="local-tools-flow">
    <h2>推荐处理流程</h2>
    <div class="local-tools-flow__steps">
      <div><span>1</span><strong>框选区域</strong><p>在杂志分区工具中按阅读顺序框选正文、标题、图注和跨页段落。</p></div>
      <div><span>2</span><strong>VLM OCR</strong><p>用 Qwen-VL-OCR 或其他 VLM 后端读取分区图片，输出结构化段落。</p></div>
      <div><span>3</span><strong>校对原文</strong><p>在 OCR 工作台导入文件，修正常见错字和术语。</p></div>
      <div><span>4</span><strong>翻译评注</strong><p>填入中文译文、链接解析、图片说明和编辑评注。</p></div>
      <div><span>5</span><strong>生成文章</strong><p>导出 `scan-translation` Markdown，放入 `_posts` 后本地预览。</p></div>
    </div>
    <a href="/search/">返回资料检索中心</a>
  </section>
</div>
