# 英文 SEO semantic benchmark

这个 benchmark 验证最终 HTML 是否为目标英文 query 提供约定的语义信号。它不请求 Google、不调用 Search Console、不模拟排名、不输出 SEO 分数。

规则文件是 `tools/seo/english-seo-benchmark.json`，检查器是 `tools/check_english_seo_benchmark.py`。只需要 Python 3.10+ 标准库；无需安装第三方库，也不依赖 `._site-seo-checks` 中的历史构建 manifest。

构建后运行：

```sh
JEKYLL_ENV=production bundle exec jekyll build
python tools/check_english_seo_benchmark.py --site _site
```

Windows PowerShell：

```powershell
$env:JEKYLL_ENV = 'production'
bundle exec jekyll build
if ($LASTEXITCODE -eq 0) { python tools/check_english_seo_benchmark.py --site _site }
```

部署 workflow 已在构建后、上传构建产物前自动执行检查。退出码 `0` 表示所有约定满足，`1` 表示语义条件失败或缺少构建输入，`2` 表示 benchmark 配置/读取错误。失败时报告列出每个失败条件的 expected 和 actual，便于定位差异。

默认输出为忽略目录中的 `._site-seo-checks/english-seo-benchmark-results.json` 及同名 `.md`；可用 `--report` 指定其他位置，`--benchmark` 指定另一套规则。报告不会进入 `_site`。

每个 query 通过 `target` 引用一套完整的页面约定，避免三条增田 query 重复维护同一份实体和内链定义。报告会展开每条 query 的预期 landing、title keywords、entity、language、anchors、schema、canonical 与 sitemap。不要为了让失败消失而放宽规则；页面职责真的发生变化时才更新 landing 或语义约定。

| Query | Expected landing | Expected HTML language |
| --- | --- | --- |
| Junichi Masuda interview archive | `/people/masuda-junichi/` | zh-CN |
| Junichi Masuda Pokemon interviews | `/people/masuda-junichi/` | zh-CN |
| Junichi Masuda credits | `/people/masuda-junichi/` | zh-CN |
| Shigeru Ohmori interviews | `/people/ohmori-shigeru/` | zh-CN |
| Ken Sugimori interview archive | `/people/sugimori-ken/` | zh-CN |
| Pokemon X Y staff credits | `/credits/x-y/` | zh-CN |
| Pokemon Black White staff credits | `/credits/black-white/` | zh-CN |
| Pokemon Scarlet Violet development team | `/credits/scarlet-violet/` | zh-CN |
| Pokemon developer interviews | `/en/interviews/` | en |
| Game Freak developer interviews | `/en/interviews/` | en |
| Pokemon development archive | `/en/` | en |
| Pokemon interview archive | `/en/interviews/` | en |
| Pokemon magazine interview archive | `/en/archive/` | en |
| Game Freak recruitment interviews | `/en/interviews/` | en |
| Pokemon game credits archive | `/en/credits/` | en |

关键词使用分组规则：组之间全部满足，一组中的替代词满足一个即可。匹配忽略大小写、Latin 重音、标点与空白，因此 `Pokemon` 能匹配 `Pokémon`，`interview` 与 `interviews` 可以明确声明为替代词。按完整词/词组匹配，单字 `X` 不会匹配单词内部。没有模糊召回或模拟搜索引擎的权重。`expected_title_keywords` 必须在 title；其他意图可以明确要求 title/description 或可见正文，不强迫所有 query 原样塞进 title。

人物规则要求英文主名进入 title，中文页面保留 `lang="zh-CN"`；Person 的 canonical entity ID、name/alternateName 和页面可见别名一致。ProfilePage 必须连接到该 Person，subjectOf 必须连接到页面上真正链接的 Article。首页、人物目录、英文人物入口、X·Y credits 必须有可见英文姓名 anchor；至少三个可抓取访谈目标必须在 Article 的 about/mentions 中引用该人物。credits 数量必须与 ProfilePage 连接且实际有链接的 VideoGame 数量一致。

`interview_count` 检查 description 中明确的正整数统计，并配合真实访谈链接与实体关系验证；它不把人物页的全部“资料条目”数量冒充访谈数量，也不固定当前数量。精确的源分类统计仍由已有 search metadata 数据核验负责。

作品规则要求游戏 identity、staff credits/development team title、VideoGame/CollectionPage/ItemList，以及 Game Freak Organization 的实际 creator 关系。署名条数和人数从 **当前 build** 的 `assets/data/credits-profile/<slug>.json` 读取，对照 description、可见 `atlas__nums` 区块；ItemList 的 numberOfItems 也必须一致。不会写死 580、533 或其他统计。

英文入口使用真实 CollectionPage，英文首页同时需要 WebSite。杂志和招聘意图要求已有英文摘要/collection anchor 与实际资料链接，无须新增无意义 Person/Organization schema。招聘 query 的英文 landing 是 `/en/interviews/`，其明确英文 anchor 连接到中文深层专题 `/keys/gamefreak-recruit-archive/`；没有要求这个中文专题假装成英文页。

所有 landing 必须有唯一、位于 head 的绝对自引用 canonical，sitemap 中恰好出现一次，没有 noindex/nofollow/refresh，robots 允许 Googlebot 和 OAI-SearchBot。检查器支持单一 sitemap 和同域本地 sitemap index，不进行在线请求。

内链检查只接受源 HTML 中的 `<a href>`，目标必须存在、自引用 canonical、可索引，且满足指定 schema。隐藏属性、aria-hidden、常见仅屏幕阅读器 class、inline display:none/visibility:hidden 和脚本字符串不充当可见 anchor；nofollow anchor 不满足 discovery 要求。这是静态 HTML 核验，不运行 JavaScript，也不计算外部 CSS 的最终可见性；动态渲染的检索卡片应另由现有 internal-link 检查负责。

检查器自身的反例回归测试：

```sh
python -m unittest discover -s tools/tests -p test_english_seo_benchmark.py
```

测试覆盖 hidden/script-only/nofollow 内链、错误实体关系、重复 entity ID、错误语言、noindex、错误位置或重复 canonical、缺少或重复 sitemap URL、OAI-SearchBot 禁抓、无效 JSON-LD、数字失配、配置错误和 CLI 非零退出。通过只是满足可本地核验的约定，不代表 Google 已发现、收录或给出任何排名。
