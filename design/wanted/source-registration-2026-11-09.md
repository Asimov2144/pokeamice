# 三项原刊来源登记 · 2026-11-09

本轮只登记已找到的原刊与来源，不托管扫描、不重做译文，也不把外部可阅标为「本站已收录原刊」。

## 原刊与阅读入口

- Nintendo Power #265，2011 年 3 月：**Breeding the Fifth**，印刷 pp.18–20。Reetroz 第 20–22 图对应这三页，p.19 侧栏为 **The Birth of Game Freak**，p.20 侧栏为 **A Visit to the Pokémon Center**。受访者为增田顺一与杉森建。[从印刷 p.18 阅读](https://reetroz.com/issue/nintendo-power-265?p=20)。
- Nintendo Power #240，2009 年 4 月：**Talking Pokémon**，印刷 pp.42–44。Reetroz 第 44–46 图对应这三页；**Pokémon Goes Platinum** 是专题页眉。受访者为增田顺一与河内丸武史。[从印刷 p.42 阅读](https://reetroz.com/issue/nintendo-power-240?p=44)。
- ファミマガ64 #28，1998 年 1 月：**田尻智さんと裕木奈江さんの ポケモン㊙インタビュー**，印刷 p.70，对应 Internet Archive n69。页上栏目为「裕木奈江プロジェクト番外編 その2」；不把「その2」推定为第 26 期文章的直接续篇。[阅读 p.70](https://archive.org/details/famimaga-64-issue-28-january-1998-600dpi-ozidual/page/n69/mode/1up)。

两期 Reetroz 的页面均标注「via Video Game History Foundation Library」。这只是阅读入口标明的来源，不能据此推定扫描制作者或再发布许可。Internet Archive 的第 28 期条目元数据标明出版者 Tokuma Shoten，上传者 ozidual，描述为 600dpi 扫描。扫描元数据与公开阅读不等于本站获准托管。

核对方法：直接查看上述七张原页的题名、印刷页码与人物标识，并读取 Reetroz 期号页、Internet Archive 条目元数据。页图仅用于核对，不加入仓库。

## 与本站现有内容的关系

- #265 与 #240 已分别存在于 `_posts/2011-03-01-interview-nintendo-power-bw-masuda-sugimori.md` 和 `_posts/2009-04-01-interview-nintendo-power-masuda-gens-1-4.md`。现有文字来源仍为 Lava Cut Content 的转录与解说。
- #28 已在 `_posts/1997-05-23-interview-famimaga-tajiri-pokemon2-secret.md` 的跨期 sunanohi 摘要中提到；它不是 p.70 全文。
- 不新增重复文章，不改变这三份文章正文或原有转录链接。来源卡与文章页提示从 `_data/wanted.yml` 共用记录；三条状态改为 `found`，不改为 `scan`。
- 原有其他 `found` 条目不因此获得本轮核验日期，也不扩大本轮对其页码、扫描或文字完整性的判断。

## 检查与发布边界

基于 main `196d7d84b9660de8885004249055199486101775` 独立分支工作。仓库 main 的 push 会部署 GitHub Pages；本轮只推送安全分支，不合并或部署。`tools/check-build.py` 增加三项来源卡、稳定锚点、原页链接、撤下重复征集、文章声明与非本轮条目隔离的回归检查，由原有分支 CI 在 Jekyll 构建后运行。
