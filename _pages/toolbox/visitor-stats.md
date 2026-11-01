---
title: "T09 访客统计"
permalink: /toolbox/visitor-stats/
layout: single
search: true
sitemap: true
categories: [站点, 工具]
tags: [百宝箱, 访客统计, 爬虫, 统计口径]
archive_type: site_tooling
summary: "宝可梦友会全站的真人访问统计，以及为什么只算执行过页面脚本的浏览器。"
sidebar:
  nav: "toolbox"
toc: true
toc_label: "目录"
toc_sticky: true
---

**入口：** [pokeamice.com/visitor/](https://pokeamice.com/visitor/)

全站最近 30 天的访问统计，每小时更新一次：今天、昨天、最近 7 天、30 天合计的浏览次数和会话数，每天的走势，以及访问最多的页面。

<figure>
  <img src="{{ '/assets/img/toolbox/visitor-stats.jpg' | relative_url }}" alt="访客统计页：今天、昨天、最近 7 天、全部 30 天四个数字卡片，下面是每日走势柱状图和服务器收到的页面请求图">
  <figcaption>页面顶部是今天、昨天、最近 7 天、30 天合计四组数字，下面是每日真人浏览走势，再往下是服务器收到的全部请求（含爬虫）。</figcaption>
</figure>

## 为什么叫「真人口径」

服务器收到的页面请求里，绝大多数来自爬虫。2026-11-01 的 30 天统计里，爬虫的页面请求有 52 万多次，占 98.1%。所以这一页**只统计真的执行了页面脚本、向本站发回过访问记录的浏览器**。

原因是很多爬虫会把自己伪装成普通浏览器：

- **按浏览器标识（User-Agent）判断不可靠**。很多爬虫随机换用新旧 Chrome 的标识。
- **它们的行为不像人**：只打开一个页面、不加载脚本，而且来自住宅代理网络里分散的地址。

页面上的灰色柱就是这类请求，单独画出来，没有算进真人数。

## 局限

- 有些爬虫也会执行脚本，会混进真人数里。所以这里的数字只能当**上限**看。
- 2026-09-16 之前的服务器日志只记录了 CDN 节点地址，没法区分访客，统计从这一天开始。
- 站主自己登录浏览时不计入。

