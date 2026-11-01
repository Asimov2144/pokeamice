---
title: "T02 Game Snapshot 截图检索"
permalink: /toolbox/game-snapshot/
layout: single
search: true
sitemap: true
categories: [站点, 工具]
tags: [百宝箱, 游戏截图, VLM, OCR, 语料库]
archive_type: site_tooling
summary: "宝可梦游戏截图语料库：输入任意语言的台词、角色或地点，找到对应的游戏画面。"
sidebar:
  nav: "toolbox"
toc: true
toc_label: "目录"
toc_sticky: true
---

**入口：** [pokeamice.com/game_gallery/](https://pokeamice.com/game_gallery/)

宝可梦游戏截图的语料库。每张截图里的对话、地名、术语都经过视觉模型识别，所以可以用一句台词、一个角色名或一个地点，找回记忆里的那个画面。2026-11-01 时收录 73,942 张。

<figure>
  <img src="{{ '/assets/img/toolbox/game-snapshot-search.jpg' | relative_url }}" alt="Game Snapshot 搜索「密阿雷」的结果：顶部是搜索框和作品筛选条，下方是截图卡片，每张卡片标着剧情、术语数和对应作品">
  <figcaption>搜索「密阿雷」：结果按卡片排列，每张标出类型（剧情）、识别到的术语数，以及来自哪部作品的哪种语言存档。</figcaption>
</figure>

## 怎么用

1. 在搜索框输入台词、角色或地点，任何语言都可以。搜索框右边标着快捷键 <kbd>⌘</kbd> <kbd>K</kbd>，可以直接跳到搜索框。
2. 搜索框下面一排是作品筛选，数字是该作收录的截图数。2026-11-01 时最多的是《宝可梦传说 Z-A》31,525 张，其次是《朱》《紫》《剑》《阿尔宙斯》。
3. 右上角「排序」可以选随机漫游、剧情优先、术语最多、最新收录、最早收录，或按截图编号排。
4. 勾选「含进化 / 退化家族」后，搜一只宝可梦会连同它的进化链一起找。
5. 点开截图看大图和识别出的全文；页面提供左右两栏的译文对照，可以各选一种语言比较。

## 卡片上的标签

| 标签 | 含义 |
| --- | --- |
| 剧情 | 画面类型，例如剧情对话 |
| N 术语 | 这张截图里识别到的游戏术语数量 |
| N 份投稿 | 同一画面收到的投稿数 |
| 中文存档 / 日文存档 | 截图来自哪种语言的游戏存档 |

## 发现识别错误

页面上有更正表单：选择错误类型，留下联系方式（选填，邮箱或社交账号）。识别文字是模型生成的，难免有错字，欢迎指出。

## 背景

这个工具的想法和实现过程见主站文章《[PokeAmice Game Gallery 启动！](https://pokeamice.com/2026/08/06/pokeamice-game-gallery%e5%90%af%e5%8a%a8%ef%bc%81/)》。
