# 历作 staff 名单研究（2026-09-17）

目标：收录历作宝可梦 staff 名单，挂到人物页；研究 Game Freak 内部职务变动；从"某作没出现的人"推测正在进行的新企划。
决定（用户 2026-09-17）：给核心 staff 自动建人物页；分析叙述用 3 个子代理按世代分段；范围扩到 GF 员工客串的外传。

## 流水线（按顺序跑）

```
python tools/build-credits.py discover   # Bulbapedia 全部「Staff of …」→ archive/credits/spinoffs.yml（外传表，可手改 year/developer；已有条目保留）
python tools/build-credits.py fetch      # Bulbapedia + ポケモンWiki 原始 wikitext → archive/credits/wiki/；corpus staff_list → archive/credits/corpus/
python tools/build-credits.py parse      # → _data/credits/<slug>.yml（93 作：29 核心 + 64 外传；Pokopia 2026-09-17 起算核心，与 Champions 同级）
python tools/build-credits.py index      # → archive/credits/index.yml（全量 7.9k 人，读 archive/credits/merges.yml 的错拼合并 / 同名拆分）
python tools/analyze-credits.py          # → design/credits-analysis/*.md + people.json（类别 / 级别规则在这里）
python tools/build-credits-site.py       # → _data/people.yml 追加 kind: staff（≥5 部核心作品，或在 GF 自研作品里任 lead 以上；ILCA/Koei Tecmo 领队不算）、_data/credits_games.yml、
                                         #   _data/credits_people.yml、_pages/credits/*.md、assets/data/credits-staff.json
python tools/build-people.py pages       # 重生成 _pages/people/（含 staff 页）
```

## 站内

- `/credits/` 总览（`_layouts/credits-index.html`）、`/credits/<slug>/` 每作名单（HTML 由脚本渲染进页面，`_layouts/credits-game.html`）、
  `/credits/staff/` 全体核心 staff 总表（客户端 JS 读 1.4MB JSON，`_layouts/credits-staff.html`：表头两行 + 人名列固定、列底色按世代交替、悬停点亮行列、点格子弹卡片——作品图标/人物头像/该作全部职务/首次·最近参与/参与轨迹）；样式 `_sass/minimal-mistakes/_credits.scss`；导航 KEy docs → 制作名单。
- 专题入口：首页专题架多了「制作名单」瓦片（`assets/img/topics/credits.jpg`，`tools/build-topic-tiles.py` 画的矩阵图）、资料窗口多了 Credits 卡；`/credits/` 顶部加「研究札记」摘要。
- 人物库 `/people/` 改成两层：受访者网格（卡片带「署名 N 作」）+ 「制作名单里的人」名录（kind: staff，按核心作数排序，可筛）；作品库新页 `/works/`（`_layouts/works-index.html`）：有制作名单的游戏按年排、其他作品按收录数排，首页瓦片与导航「作品索引」改指 `/works/`，旧的生成页 `/entities/works/` 保留作长尾。
- 总表 sticky 曾失效：主题的 `table { display: block; overflow-x: auto }` 让单元格贴在表格自己的滚动区上；`.credits__table` 已改回 `display: table; overflow: visible`。
- Game Freak 标记：`assets/img/works/gamefreak-mark.svg`（Logopedia 的 Game_Freak_(Symbol).svg 清洗后只留企鹅标，viewBox 0 0 409.43 1000）。非 GF 自研的作品（外传、BDSP、Box、Pokopia、Champions）名单页里，GF 成员名字旁带此标；`_data/credits_games.yml` 的 `gf_count` 给总览卡片。
  「GF 成员」按名单推断（build-credits-site.py `gf_evidence`）：在 ≥2 部 GF 自研作品里有 Plan/Prog/Art/Sound/Dir 类署名，或一部里任 lead 以上；排除制作人、Text Editor、artwork、声优/录音、Global Link、Battle Tower Data、路径含 Nintendo/TPC/Creatures 等——固定外协（3D 模型团队）仍会被标上，页面说明里写明了。
- Pokopia 作品图标：`assets/img/works/pokopia.png`（官方「ぽこ あ ポケモン」标志裁成方形，原图 `pokopia-logo.png`），`_data/works.yml` 有条目。
- 人物页（`_layouts/person.html`）：有 `site.data.credits_people[slug]` 的显示「参与作品」表与署名统计；`kind: staff` 的页跳过 posts 扫描、不进受访者目录。
- 登记表：`kind: staff` 条目的 name / aliases 每次由脚本从索引刷新（手改加 `pinned: true`）；staff 的 name 用日文汉字（无简体转换库），没有汉字用罗马字；slug = 姓-名。

## 数据质量

- 英日对齐：假名→罗马字归一精确匹配 → 锚点间位置补齐（加了文字系统守卫）→ 日文独有的人按日文职名挂节（`name_source: ja-only`）。
- 已知限制：同罗马字异人只能靠 merges.yml 手工拆；Bulbapedia 与日文页职务偶有出入（红绿 Debug Play vs プロデューサー；田尻降级英页晚两年）；
  黑白2 的"黑白原班整体署名"块、DLC Director 与正传 Director 同级。
- 代理点名待核的人：`design/credits-analysis/workflow-era-results.json` 各段 `people_to_verify`。

## 分析产出

- `design/credits-analysis/`：sections.md（每作类别人数）、transitions.md（逐作新人/回归/缺席/离开/职务变动）、timeline.md（≥4 作矩阵）、
  absences.md（Switch 世代缺席名单）、era-1/2/3 材料包、narrative-era-1/2/3（代理叙述）、**synthesis.md（综合）**。
- 工作流 `wf_2cef5c7f-f38`（3 代理，实耗 67 万 subagent tokens，高于预估的 25 万——era-3 材料包 228KB 是大头）。叙述写在数据修正前，
  修正后核对过 A/B 级缺席名单仍成立。

## 提交

- 分支 `staff-credits`，commit `c9dbb78d`（2026-09-17）：全部名单 / 分析 / 站内改动 + Let's Go 作品名合并。工作区里其余 `_posts` 改动是另一会话的，未纳入。

## 待做

- 人工核对 people_to_verify；给 B 级 Section Director 层查外部去向。
- 构建时间：+549 人物页后本地 build 336s → 222s（staff 页跳过 posts 扫描后；person.html 717 页合计 11.6s，不再是瓶颈）。
- 站内中文名：外传 `title_zh` 已补齐 64 部（2026-09-17，神奇宝贝百科查名 + 手核；11 部与 works.yml 条目对上 `work`，共用图标并从作品库链回名单）；staff 条目名的日→简转换仍待做。
- Masters EX 年度分页、动画 staff 未收（DISCOVER_SKIP）。

## 待办（与本课题相邻，2026-09-17 记）

- **访谈补图**（等另一会话的译名统一提交完再动，用户要求）：`tools/audit-web-imports.py` 已跑全量（`design/web_import_audit.json`，214 篇），
  102 篇图少于原页——①整篇 0 图约 45 篇（社長が訊く 12 章、Nintendo Power 3、N.O.M 6、Fami通 5、電ファミ GO 2、Creatures 20 周年、GameSpot、GI、CEDEC 2022 shader…）
  ②被 `max_images=10` 截断约 25 篇（CGWorld 朱紫 making ×3、CEDEC 报道、Fami通 Pokopia 10/65、Sleep 周年 21/38、Gigazine 齿轮画稿 28/37）③零星差 1–3 张 / 原页计数混 chrome 约 30 篇。
  做法：新写 `augment-images`（复用 import-web 的正文切割），按"前一段原文"对齐把缺的图插进 `parallel_items`，已有 URL 跳过，下载 + >300 KB 压 1280px，
  重跑 `build-cover-dims.py`；先 `--dry-run` 出"每篇补几张、插在哪段后"清单再分批跑。另：24 篇正文 <60%、41 页抓不到正文是另一件事。
- 已并掉的重复导入：Denfami 2017 后篇 → 四回完整版（`92d68c17`）。审计里还看到疑似重复：G4TV 白金 2009-03-24 vs 2013-01-11、
  Creatures 20 周年 2015-11-08（0 图）vs 2021-11-08（15 图）、kakeru pokemon_site 1999-12-01 vs 2000-05-01——待核后同样处理。
- **受访者头像**（2026-09-17）：审核了访谈的 entities.people（游戏角色、提问的记者移出，11 篇；社長が訊く 的岩田聪保留；首藤手记 39 篇的动画角色标注是有意为之、未动；
  2 篇脏文件未处理：pokemon-com-usum-ohmori-iwao 的 坂木/古兹马、recruit-business-anatomy）。用访谈自带、图注点名的照片补了 12 人头像（尾上将之两张、大洞翔一、森彰人、江上周作、
  河合敬一、野村达雄、田中宏和、CGWORLD 的 氏家淳子/中广健吾/畠祐贵 按原页标题顺序、河内丸武史 G4TV 合影右侧框；冈崎体育 取自 Bulbagarden）。
  还差 51 位受访者没照片，多是招聘访谈（寺田佑贵、古谷翔、小岛彬、的场昂树、髙草真生、林祐衣、早川裕崇、伊泽景胜、小杉要、吉原有香、田谷正夫、三浦昌幸、河本拓…）——
  原页有照片但帖子没导入，随 augment-images 一起补；另有 小澤/松村/多和田/折尾/五十岚/町田/李/川島/永山/為藤 这类只有姓氏的条目，待核是否该留在人物库。
  森昭人 已并入 森彰人（同一位 Akito Mori）。

