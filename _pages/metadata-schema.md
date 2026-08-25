---
title: "资料元数据规范"
permalink: /metadata-schema/
layout: single
categories: [文档, 站点]
tags: [metadata, workflow, graph]
archive_type: article
source:
  title: "站点内部规范"
  source_type: site_note
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
  related_posts: []
references:
  - id: csl-project
    type: documentation
    author: "Citation Style Language Project"
    title: "Citation Style Language"
    url: "https://citationstyles.org/"
    note: "字段设计参考 CSL 对引用与参考文献格式化的思路。"
---

这份规范用于统一站内文章、访谈翻译和扫描 OCR 页面所使用的资料字段。字段放在 Markdown 文件顶部的 front matter 中。

## 基础字段

```yaml
archive_type: interview_translation
source:
  title: "Nintendo DREAM 2008.12"
  url:
  scan_folder:
  language: ja
  source_type: magazine
```

常用 `archive_type`：

- `article`
- `interview_translation`
- `scan_translation`

## 工作流状态

```yaml
workflow:
  scan: done
  preprocess: done
  ocr: draft
  translation: draft
  proofreading: pending
  published: done
```

推荐状态值：

- `pending`：尚未开始
- `draft`：已有草稿
- `processing`：处理中
- `review`：等待复核
- `done`：完成

## 关系字段

```yaml
entities:
  people:
    - 增田顺一
  works:
    - 宝可梦 心金・魂银
  organizations:
    - Game Freak
  events:
    - 2008年采访

relations:
  related_posts:
    - /访谈翻译/扫描存档/扫描访谈-DREAM-2008-12-OCR翻译模板示例/
```

`entities` 用于自动生成站内相关资料。只要两篇文章拥有相同人物、作品、组织或事件，文章页底部就会出现自动关联。

`relations.related_posts` 用于手动指定强关联文章，适合上下篇、同一来源拆分、多页扫描访谈等情况。

## 评注元数据

评注也可以填写 `entities`。这样评注会被反向汇总到人物页、作品页、组织页、事件页和时间线页。

```yaml
annotations:
  - id: tajiri-note
    type: note
    title: "田尻智相关说明"
    text: "这里解释采访中提到的开发背景。"
    date: 1996
    source:
      title: "电击 Online 30周年纪念专栏"
    entities:
      people:
        - 田尻智
      works:
        - 宝可梦 红・绿
```

默认情况下，评注会继承文章本身的 `entities`。如果某条评注只想使用自己填写的实体，可以加：

```yaml
inherit_entities: false
```

## 引用与参考文献

文章可以使用接近科学文献的引用结构。字段设计参考 CSL 对 citations / bibliographies 的分层思路。{% include citation-ref.html id="csl-project" %} 先在 front matter 中声明 `references`，再在正文需要引用的位置插入引用标记。

```yaml
references:
  - id: famitsu-review
    type: magazine
    authors:
      - 周刊Fami通编辑部
    year: 1996
    title: "ポケットモンスター 赤・緑 レビュー"
    publication: "週刊ファミ通"
    issue: "1996年3月号"
    pages: "32-33"
    language: ja
    note: "用于说明当时媒体评价语境。"
  - id: pokemon-30th
    type: web_article
    author: "电击 Online 编辑部"
    year: 2026
    title: "与宝可梦同行的30年"
    url: "https://example.com/article"
    accessed: "2026-06-24"
```

正文中插入：

```liquid
这段资料来自当时的杂志报道。{% raw %}{% include citation-ref.html id="famitsu-review" %}{% endraw %}
```

生成效果：

- 正文出现上标编号，例如 `[1]`
- 文末自动生成“参考文献”
- 每条参考文献可以包含作者、年份、题名、刊物、卷期页码、出版社、ISBN、URL、存档链接
- 参考文献条目支持“回到正文”和“复制引用”

推荐字段：

- `id`：站内引用键，英文或短横线命名
- `type`：`book`、`journal_article`、`magazine`、`web_article`、`interview`、`game_manual`、`archive`
- `authors` / `author`：作者或机构
- `year` / `date`：出版年份或日期
- `title`：题名
- `publication` / `journal` / `container`：刊物、网站、书名或资料集
- `volume`、`issue`、`pages`：卷、期、页码
- `publisher`、`isbn`、`url`、`archive_url`、`accessed`

## 网页访谈收录模板

网页访谈和网页文章建议先用本地工具生成草稿：

```text
assets/tools/web-interview-capture.html
```

推荐流程：

1. 打开网页，复制正文或网页 HTML。
2. 粘贴到“正文 / HTML 粘贴区”。
3. 填写标题、来源 URL、来源站点、作者、受访者、人物、作品、组织、标签。
4. 选择“网页访谈 / 对照翻译”或“网页文章 / 资料整理”。
5. 点击“生成 Markdown”，把生成结果作为 `_posts` 草稿继续校对。

这样可以减少手写 front matter 的负担，并自动预填：

- `source`
- `workflow`
- `entities`
- `references`
- 正文引用标记
- `parallel_items` 或普通 Markdown 正文

生成索引：

```powershell
ruby tools\build-resource-index.rb
```

生成后会更新 `_data/resource-index.json`，并在 `_pages/generated/` 下生成实体页和时间线页。

## 扫描访谈推荐模板

```yaml
archive_type: scan_translation
source:
  title: "Nintendo DREAM 25th Anniversary"
  scan_folder: "F:/Pokeamice/scan/DREAM 25TH/out"
  language: ja
  source_type: magazine
workflow:
  scan: done
  preprocess: done
  ocr: draft
  translation: pending
  proofreading: pending
  published: draft
entities:
  people:
    - 高桥宏之
    - 高桥秀五
  organizations:
    - Camelot
    - Nintendo
```
