# 概念层：人写的词表 + 逐段标注（2026-09-26）

App 侧的要求（`Pokeamice_app/docs/discourse-lens-2026-09-26.md` 「还没做」）：

> **概念层**：「宝可梦的设计原则」「对战平衡」这种概念，要 docs 导出器加一轮概念标注和人审的词表。
> 现在的 `ENTITIES REPEATED` 到时候换成 `CONCEPT REPEATED`。

那一版用「同一个对象（宝可梦 / 人 / 作品）在别的几篇里也说到」代替概念，因为
`local-scenes/gap-audit-2026-09-26.md` §3 记的是「**概念词表 0 条**（glossary 257 条是译名表）」。
这一份把那 0 条补上。

## 为什么是词表，不是让模型每篇归纳

概念层的用处全在**跨篇能对上**：一篇说「容量不够所以砍了」，另一篇也说容量，两段才能并排看。
模型每篇自由归纳出来的说法对不上（「机能限制」「容量问题」「卡带装不下」各写一遍），
一联就散。所以这里的分工是：

- **词表是人写的、封闭的**（`data/lore_tables/concepts.yml`）：一条概念一个 id，带语料里实际出现的写法；
- **标注是规则的**：逐段按写法命中，`via: body / tag / title`，置信度 0.90 / 0.85 / 0.80，
  App 的证据闸认这一档（`via ≠ llm`）；
- **模型只在两处帮忙，都不参与标注**：从语料里挖候选写法（`tools/mine-concepts.py`），
  和当第二个读者量词表的缺口（`--audit`）。

这跟地点那一套是同一个做法（gazetteer 命中 → `via` → 置信度），不是新发明的。

## 文件

| 文件 | 是什么 |
| --- | --- |
| `data/lore_tables/concepts.yml` | **词表**。114 条，11 面。一条 = id / name / facet / gloss / aliases（+ `with` 同段必须出现、`avoid` 撞上不算）/ status |
| `data/lore_tables/concepts.review.json` | **人审的裁定**，审核工具写（`approve` / `drop` + 改过的名字 · 说明 · 写法）。词表保持人手写的样子，工具不改它 |
| `design/concepts-evidence.json` | 每条在语料里命中几篇 / 几段、实际命中的写法、分布、两三句原文。审核台读它 |
| `design/concepts-candidates.json` / `.yml` | `mine-concepts.py` 挖出来、模型归拢的候选（没人看过）。收哪些由人定 |
| `design/concepts-audit.json` | 抽 59 篇让模型当第二个读者的结果：规则漏了哪些、词表缺什么 |

跑法：

```bash
python tools/build-post-lore.py --concepts     # 标注 1,172 篇（规则，免费，约 1 分 20 秒）
python tools/export-docs-archive.py            # App：每篇 lore.facets.concepts + by_seg + concepts.json
python tools/export-document-entities.py       # 服务器：document-concepts.json
python tools/mine-concepts.py                  # 找词表漏了什么（要 DEEPSEEK_API_KEY）
python tools/mine-concepts.py --audit 60       # 量漏标与缺口
```

改了词表以后这四步都要重跑；`--concepts` 只写 `facets.concepts` 与 `sources.concepts`，别的字段不碰，
人手改过的记录（`edited: true` 且已有 concepts）不动。

## 导出里的三处

**1. 每篇的记录**（`data/post_lore/<id>.json` → App 的 `posts/<id>.json` 的 `lore`）

```json
{"id": "hardware-limits", "name": "机能与容量", "facet": "tech",
 "seg": [43, 45, 51], "as": ["容量", "卡带"], "via": "body"}
```

`seg` 是 App 的段号（`body.segments[].n`），最多记 6 段；`as` 是这一篇里实际出现的写法。
`reviewed: true` 只出现在人审过的那几条上。

**2. 段级**（`lore.by_seg["45"].concepts = ["hardware-limits", …]`）和
**索引**（`index.json` 的 `lore.concepts`，每篇最多 8 个 id，正文命中的排前面）。
App 要画页边标记、算「别的几篇也说到」，这两处就够，不必拉那张大表。

**3. 词表本身**（`assets/data/app/concepts.json`）：`{version, facets, items:[{id,name,facet,gloss,reviewed,docs,segs}]}`。
`docs` 是出现在几篇——App 用它把太泛的概念排除掉（「这篇也说到」只在够具体的概念上才是线索）。

**服务器那张表**（worklist D-2 的 `document_entities`）：概念行单独一个文件
`assets/data/app/document-concepts.json`（4.4 MB，15,131 行），和 `document-entities.json`
是同一张表的两半（各带 `part` / `pair`），服务器两份都收。分开写是因为阅读器要整份拉实体那一半，
手机上不该为概念再多背一倍。概念行：

```json
{"document_id": "document:interview-…", "entity_id": "concept:hardware-limits", "role": "topic",
 "start_offset": 45, "end_offset": null, "confidence": 0.9, "reviewed": 0,
 "via": "body", "source": {"system": "docs", "type": "concept", "id": "hardware-limits",
                           "name": "机能与容量", "facet": "tech", "as": ["容量"]}}
```

`concept` 是 dex-core 十二类之一，规范 ID 就是 `concept:<id>`，id 空间是 docs 这份词表——
和 person 一样，docs 是它的 source of truth，服务器不必再建一套。

## 数量（2026-09-26，词表 114 条全是 draft，人审 0）

- 词表：114 条。玩法与系统 20 · 开发流程 15 · 设计思路 15 · 技术与机能 13 · 玩家与社会 10 ·
  商业与发行 10 · 系列与跨媒体 9 · 剧情与文本 6 · 美术 6 · 团队与人 5 · 声音 5。
- 标注（工作区全部 1,158 篇记录）：**958 篇**至少有一条（中位数 3 条，平均 7.2；662 篇有 3 条以上），
  段级 14,624 处，篇级 8,391 条。按体裁：访谈 5,876 · 博客 1,508 · 扫描件 927 · 站内长文 80。
- 来源：`body` 8,067 · `tag` 291 · `title` 33。没有一条来自模型。
- 每条概念都至少命中 4 篇，112 条命中 10 篇以上——都够撑「别处也说到」。
- 收得最宽的几条（人审先看这些）：儿童玩家 190 · 公司氛围 187 · 完成度与打磨 172 · 剧本 164 ·
  进公司之前 163 · 本地化 163。
  （09-29 更正：「招聘与新人」原先 301 篇，其中一半是员工博客被错挂的「招聘」标签——导入时给 209 篇
  每篇都挂了全部 6 个分类。按早期快照改回真实分类后降到 144 篇，见
  `archive/gamefreak-staff/reports/history-report.md`。）

## 人审怎么走

审核台（`Pokeamice_app/tools/lore-review`，`npm run review` → :4790）多了一个队列
「概念词表 · docs」：一条一屏，显示说明、按哪些写法收的、实际命中的写法、分布和两三句原文，
`1` 收下 / `2` 删掉，名字 · 说明 · 写法 · 收窄条件可以直接改。裁定写 docs 的
`concepts.review.json`，之后 docs 会话重跑上面那四步。

几条建议先看的：上面那七条（审核台给它们打了 `可能太泛`）。这些多半要靠 `with` 收窄，
或者干脆把名字改小（「招聘与新人」其实同时收了 GF 招聘博客和访谈里谈「新人」的段落）。

## 还没做 / 已知的限

- **隐含的谈论抓不到**。抽 59 篇让模型当第二个读者：它点的 300 次里 172 次页面上也标了（57%）。
  剩下的多是「通篇在谈容量却没写容量」这类，规则不该硬猜——`design/concepts-audit.json`
  里按概念列了差在哪（机能与容量 8、作品主题 8、宝可梦设计 7、分工与协作 7…）。
  要补这一层，得让模型在**词表之内**选（`--audit` 的问法就是那个形状），标成 `via: llm`、
  置信度 0.5，App 按证据闸另眼看待。等人审过词表再说。
- **文章页还没有这一栏**。「本篇提到」现在是宝可梦 / 作品 / 人 / 地点四行；概念这一行等人审过再加，
  免得把没人看过的 draft 词摆到读者面前（`_data/post_lore.yml` 这一轮没有变化，站点输出一字未改）。
- **App 还在用 `ENTITIES REPEATED`**。换成 `CONCEPT REPEATED` 是 App 侧的下一步：索引里的
  `lore.concepts` + `by_seg.concepts` + `concepts.json` 就位了，不需要再等 docs。
- 词表里两个字的写法（`叫声`、`容量`、`外包`）靠人挑过一遍；再加新条时同样要看 `forms`，
  别让一个泛词把一百篇都收进来。
