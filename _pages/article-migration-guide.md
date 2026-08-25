---
title: "旧平台文章迁移图文教程"
permalink: /article-migration-guide/
layout: single
search: true
sitemap: false
categories: [文档, 站点, 工具]
tags: [文章迁移, 图片迁移, Markdown, GitHub Pages]
archive_type: site_tooling
source:
  title: "Poke Amice Docs 本地工具"
  source_type: site_tooling
workflow:
  proofreading: draft
  published: done
relations:
  related_posts:
    - /editor-workbench/
    - /metadata-schema/
---

<style>
  .migration-guide {
    --guide-ink: #243746;
    --guide-muted: #60707d;
    --guide-line: rgba(68, 94, 116, 0.16);
    --guide-soft: #f5f8fa;
    --guide-accent: #2f7894;
    --guide-warm: #c78a2f;
    width: min(1080px, calc(100vw - 48px));
    margin-left: 50%;
    transform: translateX(-50%);
    color: var(--guide-ink);
  }

  .migration-guide__hero {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(280px, 0.72fr);
    gap: 18px;
    align-items: stretch;
    margin: 8px 0 24px;
  }

  .migration-guide__hero-copy,
  .migration-guide__panel,
  .migration-guide__step,
  .migration-guide__card,
  .migration-guide__output {
    border: 1px solid var(--guide-line);
    border-radius: 8px;
    background: #fff;
  }

  .migration-guide__hero-copy {
    padding: 28px;
    background:
      linear-gradient(135deg, rgba(255,255,255,0.96), rgba(239,247,248,0.92)),
      linear-gradient(90deg, rgba(47,120,148,0.12), rgba(199,138,47,0.12));
  }

  .migration-guide__hero-copy p,
  .migration-guide__panel p,
  .migration-guide__step p,
  .migration-guide__card p,
  .migration-guide__output p,
  .migration-guide li {
    color: var(--guide-muted);
    line-height: 1.72;
  }

  .migration-guide__kicker {
    margin: 0 0 10px;
    color: var(--guide-accent);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .migration-guide h2 {
    margin: 30px 0 14px;
    font-size: 1.35rem;
  }

  .migration-guide__hero h2 {
    margin: 0 0 12px;
    font-size: clamp(1.8rem, 4vw, 3rem);
    line-height: 1.08;
  }

  .migration-guide__panel {
    display: grid;
    gap: 10px;
    padding: 18px;
  }

  .migration-guide__chip {
    display: flex;
    justify-content: space-between;
    gap: 14px;
    padding: 11px 12px;
    border-radius: 6px;
    background: var(--guide-soft);
    font-size: 0.86rem;
  }

  .migration-guide__chip code {
    padding: 0;
    background: transparent;
    color: var(--guide-accent);
    font-size: 0.8rem;
  }

  .migration-guide__flow {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin: 18px 0 24px;
  }

  .migration-guide__step {
    position: relative;
    min-height: 170px;
    padding: 16px;
    overflow: hidden;
  }

  .migration-guide__step span {
    display: inline-flex;
    width: 30px;
    height: 30px;
    align-items: center;
    justify-content: center;
    margin-bottom: 12px;
    border-radius: 50%;
    background: #dceef3;
    color: #245468;
    font-size: 0.8rem;
    font-weight: 800;
  }

  .migration-guide__step strong {
    display: block;
    margin-bottom: 8px;
  }

  .migration-guide__diagram {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr;
    gap: 10px;
    align-items: center;
    margin: 16px 0 22px;
  }

  .migration-guide__node {
    min-height: 104px;
    padding: 16px;
    border: 1px solid var(--guide-line);
    border-radius: 8px;
    background: var(--guide-soft);
  }

  .migration-guide__node strong {
    display: block;
    margin-bottom: 8px;
  }

  .migration-guide__arrow {
    color: var(--guide-warm);
    font-size: 1.8rem;
    font-weight: 800;
  }

  .migration-guide__grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
  }

  .migration-guide__card {
    padding: 16px;
  }

  .migration-guide__card h3,
  .migration-guide__output h3 {
    margin: 0 0 8px;
    font-size: 1rem;
  }

  .migration-guide__output {
    display: grid;
    grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr);
    gap: 16px;
    padding: 18px;
    margin: 16px 0;
  }

  .migration-guide pre {
    border-radius: 8px;
  }

  .migration-guide__table {
    width: 100%;
    border-collapse: collapse;
    overflow: hidden;
    border: 1px solid var(--guide-line);
    border-radius: 8px;
    font-size: 0.9rem;
  }

  .migration-guide__table th,
  .migration-guide__table td {
    padding: 10px 12px;
    border-bottom: 1px solid var(--guide-line);
    text-align: left;
    vertical-align: top;
  }

  .migration-guide__table th {
    background: var(--guide-soft);
  }

  .migration-guide__table tr:last-child td {
    border-bottom: 0;
  }

  @media (max-width: 860px) {
    .migration-guide {
      width: min(100%, calc(100vw - 24px));
    }

    .migration-guide__hero,
    .migration-guide__flow,
    .migration-guide__grid,
    .migration-guide__output {
      grid-template-columns: 1fr;
    }

    .migration-guide__diagram {
      grid-template-columns: 1fr;
    }

    .migration-guide__arrow {
      text-align: center;
      transform: rotate(90deg);
    }
  }
</style>

<section class="migration-guide">
  <div class="migration-guide__hero">
    <div class="migration-guide__hero-copy">
      <p class="migration-guide__kicker">Article Migration</p>
      <h2>把旧平台文章和图片迁移到本站</h2>
      <p>这个流程适合从微博长文、公众号、Notion、语雀、旧博客或网页访谈中迁移内容。目标是让正文变成 Jekyll Markdown，让阅读用图片进入 Pages，让原始图片留在本地归档。</p>
    </div>
    <div class="migration-guide__panel">
      <div class="migration-guide__chip"><span>迁移脚本</span><code>tools/migrate-article-images.mjs</code></div>
      <div class="migration-guide__chip"><span>站点图片</span><code>assets/img/posts/&lt;slug&gt;/</code></div>
      <div class="migration-guide__chip"><span>原图归档</span><code>archive/raw-images/&lt;slug&gt;/</code></div>
      <div class="migration-guide__chip"><span>文章草稿</span><code>_posts/YYYY-MM-DD-slug.md</code></div>
    </div>
  </div>

  <h2>流程总览</h2>
  <div class="migration-guide__flow">
    <article class="migration-guide__step">
      <span>1</span>
      <strong>准备旧文</strong>
      <p>从旧平台保存 HTML，或把网页正文复制成一个本地 `.html` / `.md` 文件。</p>
    </article>
    <article class="migration-guide__step">
      <span>2</span>
      <strong>运行脚本</strong>
      <p>脚本读取正文，提取图片，生成 Jekyll front matter 和 Markdown 草稿。</p>
    </article>
    <article class="migration-guide__step">
      <span>3</span>
      <strong>整理图片</strong>
      <p>原图进入本地归档，站点展示图进入 `assets/img/posts`，正文图片路径自动替换。</p>
    </article>
    <article class="migration-guide__step">
      <span>4</span>
      <strong>预览发布</strong>
      <p>本地构建确认排版、链接、图片体积和移动端阅读，再推送到 GitHub Pages。</p>
    </article>
  </div>

  <h2>目录长什么样</h2>
  <div class="migration-guide__diagram" aria-label="迁移目录示意">
    <div class="migration-guide__node">
      <strong>输入</strong>
      <code>migration/inbox/article.html</code>
      <p>旧平台复制出来的 HTML 或 Markdown。</p>
    </div>
    <div class="migration-guide__arrow">→</div>
    <div class="migration-guide__node">
      <strong>脚本处理</strong>
      <code>npm run migrate:article</code>
      <p>提取正文、下载图片、替换路径。</p>
    </div>
    <div class="migration-guide__arrow">→</div>
    <div class="migration-guide__node">
      <strong>输出</strong>
      <code>_posts/</code>
      <p>文章、站点图片和本地原图归档。</p>
    </div>
  </div>

  <h2>第一步：保存旧平台正文</h2>
  <div class="migration-guide__grid">
    <article class="migration-guide__card">
      <h3>优先保存 HTML</h3>
      <p>HTML 通常能保留图片顺序、链接、加粗、标题层级和图注。只复制纯文本会丢掉图片位置，后面要花更多时间补。</p>
    </article>
    <article class="migration-guide__card">
      <h3>推荐放置位置</h3>
      <p>把待迁移文件放到 `migration/inbox/`。这个目录只是本地工作区，不需要发布到 Pages。</p>
    </article>
  </div>

```text
migration/
  inbox/
    old-article.html
```

  <h2>第二步：运行迁移命令</h2>
  <p>最常用的命令如下。`slug` 会成为图片目录名，也会进入文章文件名，建议使用英文、数字和短横线。</p>

```powershell
npm run migrate:article -- --input migration\inbox\old-article.html --title "文章标题" --date 2026-07-16 --slug article-slug --source-title "原平台" --source-url "https://example.com/article"
```

  <p>如果只是想先看会输出什么，不写入文件，可以加 `--dry-run`。</p>

```powershell
npm run migrate:article -- --input migration\inbox\old-article.html --title "文章标题" --slug article-slug --dry-run
```

  <h2>第三步：检查输出结果</h2>
  <div class="migration-guide__output">
    <div>
      <h3>生成的文章</h3>
      <p>文章会写入 `_posts`，顶部自动带有标题、日期、分类、来源和迁移信息。</p>
    </div>
    <pre><code>_posts/
  2026-07-16-article-slug.md</code></pre>
  </div>

  <div class="migration-guide__output">
    <div>
      <h3>图片输出</h3>
      <p>展示图会进入 Pages，原图留在本地归档。`archive/` 已经被 `_config.yml` 排除，不会发布。</p>
    </div>
    <pre><code>assets/img/posts/article-slug/
  01-abcd1234.webp
  02-efgh5678.webp

archive/raw-images/article-slug/
  01-abcd1234.jpg
  02-efgh5678.png
  migration-report.json</code></pre>
  </div>

  <h2>第四步：启用图片压缩</h2>
  <p>脚本本身不强制依赖图片库。没有压缩库时，它会先复制图片，保证迁移不中断。想自动生成 WebP 展示图，可以安装 `sharp`。</p>

```powershell
npm install --no-save sharp
```

  <p>安装后再次运行迁移命令，展示图会按默认宽度和质量压缩。</p>

```powershell
npm run migrate:article -- --input migration\inbox\old-article.html --title "文章标题" --slug article-slug --max-width 1600 --quality 78
```

  <h2>推荐图片规格</h2>
  <table class="migration-guide__table">
    <thead>
      <tr>
        <th>图片类型</th>
        <th>建议宽度</th>
        <th>处理建议</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>普通配图</td>
        <td>1200-1600px</td>
        <td>压成 WebP，单张尽量控制在 200KB-800KB。</td>
      </tr>
      <tr>
        <td>手机截图</td>
        <td>900-1200px</td>
        <td>保留清晰文字，避免过度压缩。</td>
      </tr>
      <tr>
        <td>扫描图局部</td>
        <td>1600-2200px</td>
        <td>正文只放阅读用图，完整原图包放本地归档或外部链接。</td>
      </tr>
      <tr>
        <td>GIF</td>
        <td>按原文件</td>
        <td>脚本会保留 GIF，不转 WebP，避免动图失效。</td>
      </tr>
    </tbody>
  </table>

  <h2>常见问题</h2>
  <table class="migration-guide__table">
    <thead>
      <tr>
        <th>情况</th>
        <th>处理方式</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>图片下载失败</td>
        <td>查看 `migration-report.json` 的 `failures`。旧平台可能防盗链，可以先手动下载图片，再把 Markdown 里的图片路径指向本地文件。</td>
      </tr>
      <tr>
        <td>正文格式很乱</td>
        <td>优先找平台的 HTML 导出。没有导出时，复制网页正文到本地 HTML，再运行脚本，最后人工校对标题层级和列表。</td>
      </tr>
      <tr>
        <td>图片太多</td>
        <td>先迁移全部图片，再筛掉正文不需要的图片。保留原图归档，Pages 只放阅读需要的展示图。</td>
      </tr>
      <tr>
        <td>想先生成草稿</td>
        <td>加 `--draft`，输出到 `_drafts/slug.md`，确认无误后再改成 `_posts/YYYY-MM-DD-slug.md`。</td>
      </tr>
    </tbody>
  </table>

  <h2>发布前检查</h2>
  <ul>
    <li>文章标题、日期、分类和来源链接已经确认。</li>
    <li>正文图片都指向 `/assets/img/posts/article-slug/`。</li>
    <li>`archive/raw-images/` 只保留在本地，不进入 GitHub Pages。</li>
    <li>运行 `bundle exec ruby -S jekyll build` 后没有新增错误。</li>
    <li>打开本地预览检查手机端、暗色主题、长图和图注。</li>
  </ul>
</section>
