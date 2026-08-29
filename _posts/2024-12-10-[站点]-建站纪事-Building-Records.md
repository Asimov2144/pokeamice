---
title: "[站点]-建站纪事-Building-Records"
date: 2024-12-10
categories: [Sites,文档,宝可梦友会]
tags: [日志,PokeAmice,Updating,更新中,开源,OpenSource]
card_image: /assets/avator/rental_logo.png
annotations:
  - id: mm-theme
    type: link
    skin: box-1
    title: "Minimal Mistakes 主题"
    text: "本站基础结构来自 Minimal Mistakes。后续的首页、侧边栏、扫描翻译页和评注系统都在这个主题上继续扩展。"
    url: "https://mmistakes.github.io/minimal-mistakes/"
    link_label: "主题文档"
    entities:
      works:
        - Minimal Mistakes
      organizations:
        - Poke Amice Docs
  - id: random-bg
    type: note
    skin: box-10
    title: "随机背景方案"
    text: "这里记录的是早期站点视觉系统的一部分：通过接口随机抽取背景图，让站点每次打开都有轻微变化。"
    entities:
      works:
        - PokeAmice.com
      organizations:
        - Poke Amice Docs
      events:
        - 站点视觉系统
archive_type: "article"
summary: "https://github.com/Asimov2144/pokeamice"
source:
  title: "Pokeamice.com"
  url: "https://pokeamice.com"
  source_type: "web"
links:
  - title: "Pokeamice.com"
    url: "https://pokeamice.com"
    domain: "pokeamice.com"
    type: "web"
  - title: "代码协力——DeepSeek"
    url: "https://www.deepseek.com/"
    domain: "deepseek.com"
    type: "web"
  - title: "腾讯云COS对象存储+PicGo搭建图床教程"
    url: "https://cloud.tencent.com/developer/article/1834573"
    domain: "cloud.tencent.com"
    type: "web"
  - title: "github.com"
    url: "https://github.com/Asimov2144/pokeamice"
    domain: "github.com"
    type: "web"
  - title: "PokeAmice 链接"
    url: "https://pokeamice.com/bot/randomback.php/"
    domain: "pokeamice.com"
    type: "web"
  - title: "peateasea.de"
    url: "https://peateasea.de/add-favicon-to-mm-jekyll-site/"
    domain: "peateasea.de"
    type: "web"
  - title: "realfavicongenerator.net"
    url: "https://realfavicongenerator.net/"
    domain: "realfavicongenerator.net"
    type: "web"
workflow:
  scan: "pending"
  preprocess: "pending"
  ocr: "pending"
  translation: "pending"
  proofreading: "done"
  published: "done"
entities:
  works:
    - "宝可梦"
  organizations:
    - "Poke Amice Docs"
---

# 建站纪事&鸣谢
前人栽树，后人乘凉。\
立碑刻道，按图索骥。
## Main Theme
### 站点已开源
https://github.com/Asimov2144/pokeamice
{% include annotation-ref.html id="mm-theme" text="本站主题与后续功能扩展" %}
## 优化
采用主站[Pokeamice.com](https://pokeamice.com)的背景图随机方案，从已经逝去的宝衬衫项目的壁纸图库中随机。{% include annotation-ref.html id="random-bg" text="随机背景图方案" %}
    api : https://pokeamice.com/bot/randomback.php/

## 景观
### 添加icon 站点图标
鸣谢\
https://peateasea.de/add-favicon-to-mm-jekyll-site/ 

https://realfavicongenerator.net/
## 工具
[代码协力——DeepSeek](https://www.deepseek.com/)

### 图床
[腾讯云COS对象存储+PicGo搭建图床教程](https://cloud.tencent.com/developer/article/1834573){:target="_blank"}

### VsCode & git
[Vscode](code.visualstudio.com)


## 插件
  - jekyll-paginate
  - jekyll-sitemap
  - jekyll-gist
  - jekyll-feed
  - jekyll-include-cache
  - jekyll-archives
