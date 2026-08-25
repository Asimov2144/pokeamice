---
layout: scan-translation
title: "[扫描访谈] 标题"
date: YYYY-MM-DD
categories: [访谈翻译, 扫描存档]
tags: [OCR, 对照翻译]
archive_type: scan_translation
source:
  title: "来源刊物或网页标题"
  url:
  scan_folder:
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
    - 受访者
  works:
    - 相关作品
  organizations:
    - 相关组织
  events:
    - 相关事件
relations:
  related_posts: []
kicker: "Magazine Scan Translation"
publication: "杂志名"
issue: "刊期"
interviewee: "受访者"
translator: "译者"
box_editor: false
summary: "页面摘要。"
scan_pages:
  - image: /assets/img/interviews/example/page001.jpg
    label: "page001"
    caption: "扫描页说明。"
  - image: /assets/img/interviews/example/page002.jpg
    label: "page002"
    caption: "第二张扫描页说明。"
translation_segments:
  - speaker: "杂志图片 1"
    kind: image
    region_type: image
    region_id: image-001
    order: 1
    scan_page: 0
    scan_box: [x1, y1, x2, y2]
    image: /assets/img/interviews/example/figure-001.jpg
    alt: "杂志内页图片"
  - speaker: "图片图注"
    kind: caption
    region_type: caption
    region_id: caption-001
    caption_for: image-001
    writing_direction: vertical
    order: 2
    scan_page: 0
    scan_box: [x1, y1, x2, y2]
    writing_direction: horizontal
    original: |-
      图片旁的日文图注。
    translation: |-
      图片旁的中文图注。
  - speaker: "发言人"
    scan_page: 0
    scan_box: [x1, y1, x2, y2]
    original: |-
      日文原文。
    translation: |-
      中文译文。
    note: "可选校注。"
    comment: "可选单条评论。"
    comments:
      - "可选多条评论之一。"
      - "可选多条评论之二。"
---

## 校对说明

这里可以写来源说明、OCR 状态、译者注或版本记录。
