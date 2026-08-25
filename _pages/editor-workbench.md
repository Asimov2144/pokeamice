---
title: "本地编辑工作台"
permalink: /editor-workbench/
layout: single
search: false
categories: [文档, 站点]
tags: [workflow, tools, ocr, translation]
archive_type: article
source:
  title: "站点本地工具"
  source_type: site_tooling
workflow:
  scan: done
  preprocess: done
  ocr: draft
  translation: draft
  proofreading: draft
  published: done
entities:
  organizations:
    - Poke Amice Docs
relations:
  related_posts:
    - /metadata-schema/
    - /resource-graph/
    - /search/
---

<section class="editor-workbench">
  <div class="editor-workbench__hero">
    <p>Local Publishing Pipeline</p>
    <h2>从素材到发布的一站式入口</h2>
    <span>这里把本地工具、资料规范和发布检查放在同一页，之后编辑时可以按顺序走完整流程。</span>
  </div>

  <div class="editor-workbench__quick">
    <a href="{{ '/assets/tools/editor-toolbox.html' | relative_url }}">打开统一编辑工具箱</a>
    <a href="{{ '/assets/tools/editor-toolbox.html#workflow' | relative_url }}">项目工作流</a>
    <a href="{{ '/assets/tools/editor-toolbox.html#region' | relative_url }}">杂志分区工具</a>
    <a href="{{ '/assets/tools/editor-toolbox.html#translate' | relative_url }}">文章翻译编辑器</a>
    <a href="{{ '/assets/tools/editor-toolbox.html#web' | relative_url }}">网页访谈收录</a>
    <a href="http://127.0.0.1:4175/assets/tools/editor-toolbox.html#import">文章导入向导</a>
    <a href="{{ '/article-migration-guide/' | relative_url }}">旧文迁移教程</a>
    <a href="{{ '/search/' | relative_url }}">资料检索中心</a>
    <a href="{{ '/metadata-schema/' | relative_url }}">元数据规范</a>
  </div>

  <div class="editor-workbench__pipeline">
    <article>
      <span>01</span>
      <h3>建立项目</h3>
      <p>先在项目工作流中登记来源、人物、作品、目标文件和当前阶段，之后按步骤推进。</p>
      <code>assets/tools/project-workflow-board.html</code>
    </article>
    <article>
      <span>02</span>
      <h3>导入素材</h3>
      <p>把扫描图、采访原文、旧平台 HTML 或网页素材放入本地目录，先保留原始文件。</p>
      <code>migration/inbox/</code>
    </article>
    <article>
      <span>03</span>
      <h3>分区与预处理</h3>
      <p>用杂志分区工具处理跨栏、图文块和阅读顺序，再交给 OCR 脚本。</p>
      <code>assets/tools/magazine-region-annotator.html</code>
    </article>
    <article>
      <span>04</span>
      <h3>OCR / 合并</h3>
      <p>对 ScanTailor 输出做切栏、OCR、合并 Markdown，并保留坐标和中间 JSON。</p>
      <code>tools/process_scantailor_batch.py</code>
    </article>
    <article>
      <span>05</span>
      <h3>翻译与评注</h3>
      <p>进入文章翻译编辑器整理原文、译文、注释、图片和链接解析。</p>
      <code>assets/tools/article-translation-editor.html</code>
    </article>
    <article>
      <span>06</span>
      <h3>旧文迁移</h3>
      <p>用迁移脚本读取旧平台 HTML / Markdown，下载图片、生成站点展示图，并输出 Jekyll 草稿。</p>
      <code>node tools\migrate-article-images.mjs --input migration\inbox\article.html --title "标题"</code>
    </article>
    <article>
      <span>07</span>
      <h3>资料卡片</h3>
      <p>补齐人物、作品、年份、来源、工作流状态，让搜索和关系图谱能自动使用。</p>
      <code>tools/check-metadata.js</code>
    </article>
    <article>
      <span>08</span>
      <h3>本地预览 / 发布</h3>
      <p>本地浏览确认排版、主题、移动端和检索结果，再发布到站点。</p>
      <code>serve-local.ps1</code>
    </article>
  </div>

  <section class="editor-workbench__commands">
    <h3>常用本地动作</h3>
    <div>
      <p><strong>启动站点预览</strong><code>.\serve-local.ps1</code></p>
      <p><strong>启动统一编辑工具箱</strong><code>npm run tools</code></p>
      <p><strong>打开项目工作流</strong><code>assets/tools/project-workflow-board.html</code></p>
      <p><strong>迁移旧平台文章</strong><code>npm run migrate:article -- --input migration\inbox\article.html --title "文章标题" --date 2026-07-16 --slug article-slug</code></p>
      <p><strong>查看迁移教程</strong><code>/article-migration-guide/</code></p>
      <p><strong>启用图片压缩</strong><code>npm install --no-save sharp</code></p>
      <p><strong>重建资料网络</strong><code>ruby tools\build-resource-index.rb</code></p>
      <p><strong>检查资料卡片</strong><code>node tools\check-metadata.js</code></p>
      <p><strong>统一工具箱地址</strong><code>http://127.0.0.1:4175/assets/tools/editor-toolbox.html</code></p>
      <p><strong>启动 DeepSeek 检索代理</strong><code>$env:DEEPSEEK_API_KEY="你的 key"; node tools\deepseek-search-proxy.mjs</code></p>
    </div>
  </section>

  <section class="editor-workbench__commands">
    <h3>Markdown 简化方式</h3>
    <div>
      <p><strong>网页访谈</strong><code>先用网页访谈收录工具生成草稿，再放入 _posts</code></p>
      <p><strong>扫描访谈</strong><code>先用文章翻译编辑器生成 parallel_items / translation_segments</code></p>
      <p><strong>资料字段</strong><code>人物、作品、来源、引用、工作流由工具预填，VSCode 里只做校对</code></p>
      <p><strong>引用</strong><code>正文只写 {% raw %}{% include citation-ref.html id="source-web" %}{% endraw %}</code></p>
    </div>
  </section>

  <section class="editor-workbench__status">
    <h3>发布前检查</h3>
    <label><input type="checkbox"> 标题、日期、分类和标签已经确认</label>
    <label><input type="checkbox"> 来源、人物、作品、内容类型已经补齐</label>
    <label><input type="checkbox"> OCR 原文、译文、评注已校对</label>
    <label><input type="checkbox"> 搜索页可以按人物 / 作品 / 年份 / 来源筛到本文</label>
    <label><input type="checkbox"> 手机端和黑色主题浏览正常</label>
  </section>
</section>
