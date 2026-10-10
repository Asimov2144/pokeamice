# PokeAmice Docs：英文搜索与 GEO 回归审计

审计日期：2026-10-10。正式站点：[PokeAmice Docs](https://docs.pokeamice.com/)。

**结论：完整 production 构建、目标人物与 credits 页面、英文入口、实体图解析和 sitemap 校验通过；这不是全站所有要求均通过的报告。** 全站仍有 35 个相对 canonical 的迁移页、238 个 canonical 信号冲突的旧分页页，搜索页没有 noindex。本轮还确认扫描文章的 Article `image` 存在字段保留回归。浏览器无法初始化，未完成截图视觉验收。

本地结果只说明构建输出满足相应条件，不能证明 Google 已发现、抓取、收录页面，不能证明英文排名或 AI 引用已经改善。

## 1. 范围、版本与证据来源

- 修改前基线：Git `8394e53afe7ad7575b711190152657531d0d898b`，也是本工作树的起点。
- 修改后：`codex/english-search-semantics` 当前未提交的工作树。
- 工作树：`C:/Users/2144j/.codex/worktrees/english-search-semantics/pokeamice-main`。用户原来的 `P:/WEBSITE/pokeamice-main (1)/pokeamice-main` 是较旧的 `staff-credits` 工作目录，本轮没有在那里修改文件。
- 最终产物：工作树下 `_site/`；重新进行完整、非 incremental 的 `JEKYLL_ENV=production` 构建。本轮没有用三个页面的补渲染代替 full build。
- 对照方法：从上述 Git commit 提取模板、页面、文章、数据和样式，使用同一 Jekyll/Ruby 环境生成全量 URL 清单，定向渲染 97 个对照页面。**基线是定向渲染，修改后是完整构建。**
- 本轮只新增本报告；构建日志、基线副本和辅助审计清单位于被忽略的 `._site-seo-checks/`，没有继续增加站点功能、提交、推送或部署。

证据均来自本轮重新构建。下文的 `_site/...` 路径相对工作树；报告中的相对链接可在本地打开，构建产物与忽略目录不会随 Git 自动提交。

## 2. 修改前问题

以下文字来自 Git 基线实际渲染的 head，而非对线上页面的猜测。

| 页面 | 修改前 title | 修改前 description 摘要 | 问题 |
| --- | --- | --- | --- |
| `/people/masuda-junichi/` | `增田顺一 - Poke Amice Docs` | 中文介绍；67 作、126 篇“相关访谈与文章” | head 未明确对应 Junichi Masuda 和英文 interview / credits 意图；混合资料数量不能直接当访谈数 |
| `/people/ohmori-shigeru/` | `大森滋 - Poke Amice Docs` | 中文介绍；23 作、32 篇相关资料 | Shigeru Ohmori 英文实体没有进入 title |
| `/credits/x-y/` | `宝可梦 X·Y 制作名单 - Poke Amice Docs` | 中文介绍；580 条署名 | 缺少 Pokémon X and Y / Staff Credits / Development Team 的英文 head identity |
| `/people/` | `人物 - Poke Amice Docs` | 中文人物库说明 | 目录的英文用途不明确 |
| `/credits/` | `制作名单 - Poke Amice Docs` | 中文介绍；93 部作品 | 目录的英文用途不明确 |
| `/` | `Poke Amice Docs - 宝可梦友会 文档站点` | `存档一些非图为主的整理和博客` | 首页缺少开发者访谈档案的明确描述 |

此外，之前没有本次五页英文 discovery 层；人物与作品关系缺少统一的 canonical entity ID；人物链接的英文 alias 展示不统一。原有 Article JSON-LD 已存在，不能把它当成完全缺失，也不能通过额外叠加第二套冲突的 Article 来解决。

**未发现目标人物页的 sitemap 漏项证据。** 增田页此前已经在 sitemap 中，普通人物目录链接也已经存在。不能用 GSC 的“未检测到引荐站点地图”推出 XML 没有此 URL，不能把当前英文表现弱直接归因于 robots。

## 3. 前面已完成的修改

| 内容 | 统一位置 / 具体文件 | 规则与边界 |
| --- | --- | --- |
| 人物姓名 identity | [_plugins/person_identity.rb](../_plugins/person_identity.rb)、[_includes/person-name.html](../_includes/person-name.html) | 统一中文名、日文名、英文名、别名、slug 和展示 label；优先已有明确英文名，再取有依据的登记别名 / credits 姓名；不自行转写缺失姓名 |
| 英文 head metadata | [_plugins/search_metadata.rb](../_plugins/search_metadata.rb)、[_includes/seo.html](../_includes/seo.html) | 对人物、credits 和三个主目录统一生成；不手写到 700 多个人物页面；保留原 page.title / H1 / 中文正文语言 |
| 人物统计 | `_data/people.yml`、`_data/people_profiles.yml`、`_data/credits_people.yml` 和已分类文章 | 访谈数按实际访谈分类统计，使用“related interviews”；credited works 去重，major roles 来自明确署名角色；不把仅提及该人物的访谈当其全部受访记录 |
| 作品统计 | `_data/credits_games.yml`、`assets/data/credits-profile/<slug>.json` | 署名条数、人数、部门与 atlas 来自数据；580 / 533 等数字没有写死在生成模板 |
| 实体图 | [_plugins/entity_graph.rb](../_plugins/entity_graph.rb)、[_data/structured_entities.yml](../_data/structured_entities.yml)、[_includes/entity-schema.html](../_includes/entity-schema.html)、[_includes/article-schema.html](../_includes/article-schema.html) | 单一 Article 图；Person / VideoGame / Organization 采用统一绝对 URL 与固定 fragment ID；实体事实受可见正文约束 |
| 文章模板 | `_layouts/interview-editorial.html`、`parallel-translation.html`、`single.html` | 去掉同一正文的匿名 Article / CreativeWork microdata 副本；保留一个明确的文章实体 |
| 英文入口 | [_plugins/english_discovery.rb](../_plugins/english_discovery.rb)、[_data/english_discovery.yml](../_data/english_discovery.yml)、`_pages/en/`、`_layouts/english-discovery.html`、`_includes/english/`、`assets/css/english-discovery.css` | 只生成 `/en/`、`/en/interviews/`、`/en/people/`、`/en/credits/`、`/en/archive/`；提供英文摘要和导航，资料详情仍可进入中文原页 |
| 语言入口 | [_data/language_homes.yml](../_data/language_homes.yml)、`_includes/head/custom.html`、三个 masthead、`_layouts/default.html`、`_pages/ja-index.html` | 三首页 hreflang 闭环；真正的中日文章版本各自 canonical；四个英文子入口没有伪造全文语言版本 |
| 可见内链 | `people-index.html`、`person.html`、`credits-game.html`、`credits-staff.html` 等布局；`home-featured-people.html`、`interview-related.html`、`person-avatar.html`、`resource-card.html` 等 include；`assets/js/catalogue.js`、`quote.js`、`tips.json` | 中文优先的自然 `中文名 · English name`；所有调用使用统一 identity；静态人物链接仍是 `<a href>`，没有 SEO-only 隐藏姓名 |
| 卡片样式 | `_sass/minimal-mistakes/_search.scss`、`_custom-themes.scss` | 修正嵌套英文 alias 被误当成单独标签的选择器；没有整体重做中文主题 |
| sitemap | [sitemap.xml](../sitemap.xml) | 把五个英文 discovery 页面纳入现有白名单；保留原人物页覆盖；没有为了数量拆 sitemap |
| 可重复 benchmark | [tools/seo/english-seo-benchmark.json](../tools/seo/english-seo-benchmark.json)、[tools/check_english_seo_benchmark.py](../tools/check_english_seo_benchmark.py)、[使用说明](../tools/seo/README.md)、`tools/tests/`、`.github/workflows/jekyll.yml` | 15 条 query 检查本地语义信号；构建后、上传前运行；不模拟 Google 排名 |

人物 identity 共 718 条，其中 665 条有来源支持的英文姓名，53 条保留原有姓名作为回退，不为了覆盖率虚构 romanization。Title 依实体名、页面用途及长度选择别名；description 使用真实统计和少量有依据的角色，不复制整份英文正文。

## 4. 完整构建与验证结果

构建工具：Jekyll 4.4.1、Windows Ruby 3.3，production，`incremental: false`。执行完整 `Jekyll::Site#process`，退出码 **0**。

```json
{
  "seconds": 439.8,
  "pages": 3603,
  "posts": 1194,
  "static_files": 8028,
  "jekyll": "4.4.1",
  "environment": "production"
}
```

`pages` 是 Jekyll page 对象数量，不能直接当最终 HTML 总数；最终扫描 **4,853 个 HTML**。日志仍有 Sass 弃用提示和 Game Freak tag/category 目标冲突提示；基线中也存在这些问题，不能把 exit 0 写成“零 warning”。本次没有执行 GitHub Actions 的 Linux / Ruby 3.2 部署环境。

| 回归项 | 实际结果 | 判定 |
| --- | --- | --- |
| Jekyll full build | 439.8 秒，exit 0；不是预览或增量构建 | 通过 |
| 原有 URL | 基线 4,840 个唯一生成 HTML URL 全部仍有本地产物；缺失 0 | 通过 |
| 中文内容 / H1 | 97 个实际渲染对照样本，H1 差异 0、canonical 差异 0；`_posts/`、`_ja/` 和核心 people / credits 登记数据没有源码差异 | 通过相应范围；不等于全站截图验收 |
| `/ja/` | 全部 65 页 title、description、HTML lang 与基线一致；64 篇日文文章正文 CJK 字符序列一致；日文首页新增 archive overview 与导航，且加入三个首页 hreflang 组 | 通过文章、URL 和 metadata 回归；首页有预期内容增量 |
| `/en/` | 仅 5 页；`lang=en`、英文 title / description、自引用 canonical、sitemap、CollectionPage；英文首页有 WebSite | 通过静态产物检查 |
| 新 metadata 重复 | 814 个统一生成页 + 5 个英文入口；title 重复组 0、description 重复组 0、缺 description 0 | 通过 |
| 全站旧 title 重复 | 全 HTML 扫描仍有 26 组范围外重复；既有目录、栏目、同名旧文章等 | 未宣称全站所有 title 唯一 |
| 主资料 canonical | 所有 Person、credits、中日文章、英文入口使用 HTTPS 正式域名、自引用 | 通过 |
| 所有 HTML canonical | 35 个迁移页为相对 URL；9 页缺 canonical；238 个分页页在 head/body 各有一条 canonical | **全站要求未通过** |
| hreflang | 135 页；目标存在、语言标签唯一、目标 canonical 正确、回链完整；错误 0 | 通过 |
| JSON-LD | 6,809 个 script 全可解析；718 Person、93 VideoGame、1,258 Article | 通过解析与图关系校验 |
| canonical entity | 主资料实体 ID 冲突 0；17,966 条引用关系通过；Person subjectOf 最多 8 个轻量引用，最大人物图 8,491 B | 通过 |
| Article 结构 | 中文文章 1,194 + 日文文章 64；单一主 Article，无冲突正文 microdata | 通过结构检查 |
| Article 原字段保留 | 基线样本发现 image 等字段变化；两篇可见扫描图没有进入新版 Article image | **不能判为完全无回归** |
| sitemap 本地文件 | 2,076 / 2,076 对应 HTML；重复、query、双 slash、noindex、refresh、canonical 不匹配均 0 | 通过 |
| sitemap 本地 HTTP | 临时 loopback 静态服务器请求全部 2,076 URL，全部 200，响应 SHA-256 与文件一致；服务器已关闭 | 通过本地服务；不是生产 HTTP 检查 |
| robots | 只有正式 sitemap 地址，没有 Disallow；Googlebot / OAI-SearchBot 对重点路径均允许 | 通过本地规则 |
| 英文内链 | 39,005 个受统一 identity 管理的静态人物 anchor，错误 0；动态 search / hover / featured label 也核验一致 | 通过静态与数据检查；未执行浏览器动态交互 |
| benchmark | 15/15 query；327 条检查；读取 135 个相关 HTML；setup error 0 | 通过 |
| 生成规则 / 检查器测试 | Ruby 27 tests / 129 assertions；Python 21 tests；均 0 失败 | 通过 |
| 视觉截图 | computer-use 浏览器初始化失败：`failed to write kernel assets (os error 3)` | **未完成** |

可见英文别名、首页 featured people、EN 导航是前面已授权的设计增量。中文资料的原 URL、H1 和正文主语言保留；首页与日文首页的布局结构有预期增量，不能称画面与基线逐像素相同。此次对照中，10 篇中文 Article 和全部 64 篇日文文章的 body 中文 / 日文字符序列一致；比较已排除 script / style 与英文 alias span。人物和 credits 的可见姓名因统一 alias 而变化，日文首页还新增了日文 archive overview 和人物 / credits / 招聘复原资料入口。这些文本变化不应藏在“视觉完全不变”的结论里。字符序列检查也不能单独证明 CSS 渲染完全相同。

## 5. 两个固定验收页面：最终 HTML

### `/people/masuda-junichi/`

产物：[_site/people/masuda-junichi/index.html](../_site/people/masuda-junichi/index.html)。第 13–14 行的 head 原文（HTML entity 解码后）：

```html
<title>Junichi Masuda (増田順一 / 增田顺一) — Interviews & Pokémon Credits | Poke Amice Docs</title>
<meta name="description" content="Junichi Masuda (増田順一 / 增田顺一): director, producer and composer. 113 related interviews and Pokémon credits across 67 games. Chinese-language archive with original sources.">
```

第 48 行：

```html
<link rel="canonical" href="https://docs.pokeamice.com/people/masuda-junichi/">
```

HTML 为 `lang="zh-CN"`，H1 仍是 `增田顺一`。第 5499 行的实体图中，Person 的实际值摘录如下；这是完整图的字段摘录，不是另一份新增 schema：

```json
{
  "@type": "Person",
  "@id": "https://docs.pokeamice.com/people/masuda-junichi/#person",
  "name": "Junichi Masuda",
  "alternateName": ["增田顺一", "増田順一", "Junichi Masuda", "Jun'ichi Masuda", "ますだ じゅんいち"],
  "url": "https://docs.pokeamice.com/people/masuda-junichi/",
  "image": "https://docs.pokeamice.com/assets/img/people/masuda-junichi.jpg",
  "sameAs": ["https://x.com/Junichi_Masuda", "https://www.instagram.com/pokemon_masuda/"]
}
```

ProfilePage `mainEntity` 指向该 Person；Person `subjectOf` 使用最多 8 个已链接、实际受访文章的 `#article` 引用。描述来自可见履历，sameAs 来自现有核实账号数据，本轮没有重新在线核验账号归属，也没有推测当前雇佣关系。

`sitemap.xml` 中恰好出现一次该正式 URL；`/people/` 有真实 `<a href="/people/masuda-junichi/">`，可见姓名含 `增田顺一 · Junichi Masuda`。113 是相关访谈分类数，67 是去重署名作品数，不是把人物目录的“篇”或受访资料总数直接改名为 interview count。

### `/credits/x-y/`

产物：[_site/credits/x-y/index.html](../_site/credits/x-y/index.html)。第 13–14 行：

```html
<title>Pokémon X and Y Staff Credits &amp; Development Team | Poke Amice Docs</title>
<meta name="description" content="Pokémon X and Y staff credits: 580 credited entries and 533 people. Includes department breakdown, development atlas and source-linked staff profiles.">
```

第 48 行是 `https://docs.pokeamice.com/credits/x-y/` 自引用 canonical；HTML 仍为 `zh-CN`，H1 仍是 `宝可梦 X·Y`。第 185 行的图包含：

```json
{
  "@type": "VideoGame",
  "@id": "https://docs.pokeamice.com/credits/x-y/#game",
  "name": "宝可梦 X·Y",
  "alternateName": ["宝可梦 X·Y", "Pokémon X and Y", "ポケットモンスター X・Y"],
  "url": "https://docs.pokeamice.com/credits/x-y/",
  "datePublished": "2013",
  "creator": [{"@id": "https://docs.pokeamice.com/entities/organizations/game-freak/#organization"}],
  "director": [{"@id": "https://docs.pokeamice.com/people/masuda-junichi/#person"}]
}
```

同一图的 CollectionPage `mainEntity` 指向 `#game`，ItemList `numberOfItems=580`；creator 指向图内定义的 Game Freak Organization。年份仅到数据支持的年，没有推测发行日。580 / 533 同时对照当前 build 的 `assets/data/credits-profile/x-y.json`、可见 atlas 统计和 metadata。游戏页与 Person 的 director / musicBy 关系来自明确署名。

## 6. 实体随机抽样

固定随机 seed 为 `20261010`，抽样之外已完成全量 JSON 解析与主实体关系校验。样本恰好覆盖至少 5 Person、3 credits、5 interview。

| 类型 | 实际抽样 URL |
| --- | --- |
| Person | `/people/ming-xu/` |
| Person | `/people/k-o/` |
| Person | `/people/xiao-dao-bin/` |
| Person | `/people/campa-diego-luque-de-la/` |
| Person | `/people/kawashima-masashi/` |
| VideoGame | `/credits/new-pokemon-snap/` |
| VideoGame | `/credits/pokepark-2/` |
| VideoGame | `/credits/mystery-dungeon-wiiware/` |
| Interview / Article | `/访谈翻译/翻译/访谈整理/interview-iwata-asks-gates-to-infinity-chapter-1-impossible-combination/` |
| Interview / Article | `/访谈翻译/翻译/访谈整理/interview-cgworld-2026-cedec-pkmnza/` |
| Interview / Article | `/developer-interviews/pokemon-recruit/interview-pokemon-recruit-staff-hayakawa/` |
| Interview / Article | `/访谈翻译/扫描存档/continue-vol31-aoi-yu-pikachu/` |
| Interview / Article | `/访谈翻译/官方档案/interview-pokemoncom-2018-letsgo-makers/` |

## 7. hreflang 与技术索引矩阵

三个首页均输出下列四条 head link，并分别保留自身 canonical：

```html
<link rel="alternate" hreflang="zh-CN" href="https://docs.pokeamice.com/">
<link rel="alternate" hreflang="ja" href="https://docs.pokeamice.com/ja/">
<link rel="alternate" hreflang="en" href="https://docs.pokeamice.com/en/">
<link rel="alternate" hreflang="x-default" href="https://docs.pokeamice.com/">
```

64 对中日文章双向关联；其余四个英文 discovery 页面只有 `en` 自己和 `x-default` 自己。它们是精选导航 / 摘要页，不是假装逐篇对应的译本。中文 Person / Credits 详情不会因为英文 head 或名字而被标成英文全文。实际语言版本的 reciprocal link 检查依照 [Google hreflang 文档](https://developers.google.com/search/docs/specialty/international/localized-versions)。

以下 `index` / `follow` 表示本地指令允许与否，**不是 Google 收录状态**。

| URL family | index | follow | canonical | sitemap | hreflang |
| --- | --- | --- | --- | --- | --- |
| 三首页 `/`、`/ja/`、`/en/` | 允许 | 允许 | 各自 HTTPS 正式 URL | 全部在 | zh-CN / ja / en / x-default 闭环 |
| 人物目录 + 718 Person | 允许 | 允许 | 绝对自引用 | 719 | 无独立译本，不制造语言副本 |
| credits 目录 + 93 作品 + staff | 允许 | 允许 | 绝对自引用 | 95 | 无独立译本 |
| 中文文章 | 允许 | 允许 | 绝对自引用 | 1,191 / 1,194；3 篇 Sites 站务资料按设计排除 | 64 篇与日文双向 |
| 日文文章 | 允许 | 允许 | 日文自身 | 64 / 64 | 中日双向 |
| 四个英文子入口 | 允许 | 允许 | 英文自身 | 4 / 4 | en / x-default 自身 |
| `/search/` 及 `?q`、搜索 filters | 允许；尚缺 noindex | 允许 | 无参 `/search/` | 不在 | 无 |
| 首页 / timeline / overseas / graph UI query | 没有明确禁止索引 | 允许 | 各自无参入口 | 参数 URL 不在 | 首页继承首页组 |
| `/page2/`–`/page239/` | 没有 noindex；refresh 回首页 | 允许 | head 自身、body 首页，两条冲突 | 不在 | 无 |
| 35 个旧人物 / 文章迁移 URL | noindex | 未禁止 | 相对迁移目标 | 不在 | 无 |
| taxonomy / entities / timeline 等旧导航 | 通常允许 | 允许 | 通常绝对自引用 | 按白名单省略 | 无 |
| 8 个 `/assets/tools/*.html` | 未禁止 | 允许 | 缺失 | 不在 | 无 |
| `/jleague-pokemon/` 独立 HTML | 未禁止 | 允许 | 缺失 | 不在 | 无 |

最终 sitemap 共 2,076 URL、289,527 bytes：home 1、article 1,191、people 719、credits 95、ja 65、en 5。没有提交 noindex 页、HTML redirect 页、query URL、重复 slash URL，所有 loc 与目标唯一 canonical 一致。本地服务器全量 200 不能排除上线后的 CDN redirect 或 `X-Robots-Tag`。

robots 最终内容：

```text
Sitemap: https://docs.pokeamice.com/sitemap.xml
```

没有本地 robots 误封 Person、credits 或 en 的证据。现有规模与检查结果不需要为拆分而拆分 sitemap。

## 8. 未通过项与具体证据

### 8.1 Article image 字段保留回归（P2）

**结构解析通过，不代表原有有意义字段全部保留。** 基线中有 Article 的 10 个对照样本全部仍有一个主 Article，但字段发生变化：10 页 datePublished / dateModified 有变化、10 页 image 有变化、9 页 articleSection 有变化；3 页 headline / name 改为当前可见 H1。

日期移除部分属于事实约束收紧：旧版使用 Git 归档加入日期，不能将其未经页面证实当作译文的真实发表或修改日期；不建议为“保持字段数量”盲目恢复。封面回退从站点 logo 改为可见资料图片，以及 headline 对齐 H1，也应与图片遗漏区别记录。

**已证实的图片遗漏**有两个例子：

| 最终 HTML | 当前正文实际 img src | Article 当前结果 |
| --- | --- | --- |
| `_site/访谈翻译/扫描存档/scan-shodai-zukan-1996-staff-interview/index.html` | `https://gallery.pokeamice.com/scan-archive/shodai-zukan-1996-staff-interview/pages/p001_cover.jpg` | 第 232 行实体图没有 image；旧 Article 有此图 |
| `_site/杂志特辑/扫描存档/scan-shodai-zukan-1996-pokemon-journal/index.html` | `https://gallery.pokeamice.com/scan-archive/shodai-zukan-1996-pokemon-journal/pages/p131_p129_ch5_journal_part1.jpg` | 新 Article 没有 image；旧 Article 有此图 |

原因：`_plugins/entity_graph.rb` 的 Article 图片选择只接受含 `/interviews/` 或 `/scans/` 的正文图片路径，遗漏 gallery 的 `/scan-archive/` 路径。这是源码可定位的字段保留问题；不是 JSON 语法错误，也不能据此推断文章不能收录。本轮没有扩大修复范围，**“Article 完全未被破坏”不作无条件通过声明**。

后续最小修复应复用已有代表图选择，且只在该图确实呈现于正文时输出，或支持已有 gallery scan 图；仍保持单一 Article 和原 canonical ID。articleSection 等已有可见且有依据的字段也应逐项保留核对。真实日期不足时继续省略，不杜撰 dateModified。

### 8.2 全站 canonical 规范未完全满足（既有问题）

35 个旧迁移页使用相对 canonical，例如：

```html
<!-- _site/people/sen-zhao-ren/index.html -->
<link rel="canonical" href="/people/sen-zhang-ren/">
<meta name="robots" content="noindex">
```

源文件：[_pages/redirects/people-sen-zhao-ren.html](../_pages/redirects/people-sen-zhao-ren.html)。这些页面都在 sitemap 外，不是正常人物详情页的 canonical 错误。相对 canonical 属一致性问题，不能称为已证实的抓取故障。还有 8 个内部 HTML 工具及 `/jleague-pokemon/` 缺 canonical。因此“所有 canonical 使用 HTTPS 正式域名”按全站严格口径未通过。

### 8.3 搜索与旧分页索引边界（既有问题）

`_site/search/index.html:48` 只有干净路径 canonical，没有 noindex。搜索 query / filters 继承同一个静态 HTML；2065 个产物页面包含 query anchor。未进 sitemap 不等于禁止索引。

`_site/page2/index.html` 的实际输出：

```html
<!-- head:48 -->
<link rel="canonical" href="https://docs.pokeamice.com/page2/">
<!-- body:194-196 -->
<link rel="canonical" href="https://docs.pokeamice.com/">
<meta http-equiv="refresh" content="0; url=/">
<p class="home-paginated-stub">这一页没有内容，请回到<a href="/">首页</a>。</p>
```

238 个旧分页页均有这一类信号冲突、没有 noindex、未进入 sitemap；首页仍有 rel=next 指向 `/page2/`。源位置：[_layouts/home.html](../_layouts/home.html)、[_config.yml](../_config.yml)、[_includes/seo.html](../_includes/seo.html)。这不是当前 Person / credits 详情页的阻断。

### 8.4 数据与旧页面范围限制

- 53 个 Person 尚无有依据的英文主名；不把未猜测姓名写成实现失败，也不保证这些实体可匹配 romanized query。
- 旧 registry 的四组 alias 冲突仍在：H.T.、Hiro Nakamura、たなかまさみ、たかはしやすこ；前面未擅自重新归属。目标增田、大森、杉森的 identity 与 anchor 检查通过，但不能声称所有历史别名已经消歧。
- 存在 26 组范围外 title 重复和 Game Freak tag/category 目标冲突。本次新 metadata 的唯一性通过，不扩展成全站 title 清理项目。
- `gamefreak-director/lineblog-8169063/` 仍有两处旧 external anchor 嵌套；不属于本次人物 anchor，新的人物链接检查未发现嵌套错误。

## 9. 英文实体内链抽样

均是构建 HTML 中真实 `<a href>`。人物目录整张卡片的 anchor 还含日文名、篇数和署名统计；下面完整保留该采样 anchor 文本。篇数是原目录资料统计，不等同于新版 metadata 的访谈分类数。

| Source page | anchor text | target page |
| --- | --- | --- |
| `/` | `增田顺一 · Junichi Masuda` | `/people/masuda-junichi/` |
| `/people/` | `增田顺一 · Junichi Masuda 増田順一 635 篇 · 1996–2023 署名 28 作 · 1996–23` | `/people/masuda-junichi/` |
| `/developer-interviews/gamefreak-recruit/interview-gamefreak-career-message-masuda/` | `增田顺一 · Junichi Masuda` | `/people/masuda-junichi/` |
| `/credits/x-y/` | `增田顺一 · Junichi Masuda` | `/people/masuda-junichi/` |
| `/` | `大森滋 · Shigeru Ohmori` | `/people/ohmori-shigeru/` |
| `/credits/x-y/` | `大森滋 · Shigeru Ohmori` | `/people/ohmori-shigeru/` |
| `/` | `杉森建 · Ken Sugimori` | `/people/sugimori-ken/` |
| `/credits/x-y/` | `杉森建 · Ken Sugimori` | `/people/sugimori-ken/` |

全部静态唯一来源页计数：增田 home 1 / people 1 / interview 122 / credits 67；大森 1 / 1 / 39 / 23；杉森 1 / 1 / 52 / 56。这里 interview 是来源页面类型计数，可包括 related 人物卡片，不等同于本人受访次数。没有把 JavaScript 字符串、hidden text 或 nofollow 链接当作必要 discovery anchor。

## 10. 本地 build 无法判定的项目

- 生产 HTTPS、HTTP 状态码、HTTP redirect、CDN/WAF、`X-Robots-Tag`、响应 header 的 canonical、Googlebot / OAI-SearchBot 的真实网络可达性。
- Google 是否已发现或读取 sitemap、是否抓取最新部署、Google-selected canonical、是否收录，以及实际标题 / snippet 是否采用新版 metadata。
- 英文 query 的 impressions、点击、排名变化、Google 或其他 AI 系统是否引用本网站。允许 crawler 与实体图有效都不能保证 retrieval 或展示。
- schema.org 语法可解析不等于 Google 富媒体结果验收、质量策略验收或所有模型对实体关系的解释一致。本轮没有运行在线 Rich Results Test / schema validator。
- 浏览器截图、移动端换行 / 截断、图片实际加载、筛选和 search 卡片运行时交互。浏览器运行环境启动失败，不能将静态 HTML 验证冒充浏览器验证。
- GitHub Actions Linux / Ruby 3.2 实际构建和发布结果。这里的 full build 是本地 Windows / Ruby 3.3。

中文详情页依然以中文为主要内容语言。英文 title、alias 和入口是可核查的匹配信号，不足以证明 Google 会把这些详情当成英文资料页或将其用于任何指定英文 query。

## 11. 上线后必须在 Google Search Console 验证

先记录部署 commit 与时间，再执行下面六项。推荐固定检查增田、大森、杉森、X·Y、Black·White、Scarlet·Violet、`/en/`、`/en/interviews/`，并以 `/`、`/ja/` 和一篇已有日文文章作为回归对照。

| 项目 | 实际应记录的证据 | 通过 / 异常的判读 |
| --- | --- | --- |
| 1. Google URL Inspection | 先查看 indexed result，再做 Live Test；记录 fetch、crawl allowed、indexing allowed、rendered HTML、user-declared canonical、Google-selected canonical | Live Test 成功说明当前可能可访问；不能替代 indexed result，也不能预测 Google 最终 canonical |
| 2. sitemap processed | 在 Sitemaps report 检查正式 `sitemap.xml` 的 Status、Last read、Discovered pages；保存截图 / 导出 | Success 表示已抓取并读取 sitemap；不等于其中所有 URL 已抓取或收录 |
| 3. crawl date | URL Inspection 的 Last crawl 是否在本次部署之后；View crawled page 中是否有新 title / Person / game 图 | 旧 crawl date 表示尚不能用索引中的旧 HTML 验收新改动；Live Test 与 indexed result 要分开记录 |
| 4. indexing 状态 | 各目标 URL 的 indexed / not indexed reason、Google-selected canonical、页面索引报告 | 抓取成功与收录是两项独立结果；继续“Google 无法识别此网址”时核对实际网络、发现与抓取证据 |
| 5. impressions | 按同一 landing page 和日期窗口导出上线前后 impressions / clicks；同时保留中文和日文对照 | 在发生新 crawl / indexing 后再观察变化；无曝光不能单凭本地 metadata 宣称成功 |
| 6. 英文 query exposure | Performance 的 Queries + Pages；观察 benchmark 的 15 条 query 及 Pokemon / Pokémon 拼写、实体名和英文意图词变体 | 记录真实出现的 query、landing、impressions；不设置“必须第一名”或无依据的增长目标 |

URL Inspection 的 indexed data、Live Test 和 Google-selected canonical 的区别见 [Google URL Inspection 文档](https://support.google.com/webmasters/answer/9012289?hl=en)。未列出 referring page / sitemap 不能反向证明本地没有链接或 XML URL。

Sitemap 的 Success、Last read 与 Discovered pages 各有不同意义；处理成功不保证所有 URL 收录，见 [Google Sitemaps report 文档](https://support.google.com/webmasters/answer/7451001?hl=en)。本地 XML 已确认增田 URL 存在，后续诊断必须保留这一事实。

实际曝光以 Queries / Pages / Impressions 数据为准，见 [Google Performance report 文档](https://support.google.com/webmasters/answer/7576553?hl=en)。Performance 没有直接的“页面英文语言”维度，应使用真实英文 query 分组；不能把国家筛选直接等同于英文检索，也不能把报告中未显示某条 query 当成绝对零曝光。

## 12. 可复跑检查与本轮日志

日常可重复的核心检查（正常已配置构建依赖的环境）：

```sh
JEKYLL_ENV=production bundle exec jekyll build
python tools/check_english_seo_benchmark.py --site _site
python -m unittest discover -s tools/tests -p test_english_seo_benchmark.py
```

完整英文 query、landing、关键词、entity、lang、anchor、schema、canonical 与 sitemap 约定位于 [benchmark 文件](../tools/seo/english-seo-benchmark.json)。运行方法、可检查范围及限制见 [README](../tools/seo/README.md)。现有 CI 已在 Jekyll build 后、上传前执行 benchmark，CI 本身尚待实际运行。

本轮辅助全量验证器均 exit 0；它们检查各自定义的范围，**不会自动把旧分页 / 搜索问题或 Article 字段回归升级成失败**，因此本报告补充基线字段对照和全站技术检查。部分辅助验证器需要本地 build hook 生成的 manifest，不能假设仅拷贝 `_site` 后就拥有全部辅助输入。

| 证据 | 文件 |
| --- | --- |
| 本轮 full build | [regression-full-build.log](../._site-seo-checks/regression-full-build.log)、[entity-build-result.json](../._site-seo-checks/entity-build-result.json) |
| Git 基线与 97 页对照 | [baseline-provenance.json](../._site-seo-checks/baseline-provenance.json)、[baseline-render-result.json](../._site-seo-checks/baseline-render-result.json)、[regression-baseline-comparison.json](../._site-seo-checks/regression-baseline-comparison.json) |
| metadata 与唯一性 | [verification.json](../._site-seo-checks/verification.json)、[regression-metadata-uniqueness.json](../._site-seo-checks/regression-metadata-uniqueness.json) |
| 实体图与随机样本 | [entity-verification.json](../._site-seo-checks/entity-verification.json)、[entity-verification.md](../._site-seo-checks/entity-verification.md) |
| Article 字段回归 | [regression-article-property-evidence.json](../._site-seo-checks/regression-article-property-evidence.json) |
| 英文入口与内链 | [english-discovery-validation.json](../._site-seo-checks/english-discovery-validation.json)、[internal-links-validation.json](../._site-seo-checks/internal-links-validation.json) |
| 全站索引 inventory | [technical-index-inventory.json](../._site-seo-checks/technical-index-inventory.json)、[regression-canonical-exceptions.json](../._site-seo-checks/regression-canonical-exceptions.json) |
| sitemap 全量本地 HTTP | [regression-sitemap-http.json](../._site-seo-checks/regression-sitemap-http.json) |
| benchmark | [english-seo-benchmark-results.json](../._site-seo-checks/english-seo-benchmark-results.json) |
| 规则 / 检查器测试 | [regression-ruby-tests.log](../._site-seo-checks/regression-ruby-tests.log)、[regression-benchmark-tests.log](../._site-seo-checks/regression-benchmark-tests.log) |

发布验收前仍需浏览器视觉抽查和生产 HTTP / GSC 验证；本报告不把“本地信号已增加”写成“Google 排名已改善”。
