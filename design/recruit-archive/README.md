# GAME FREAK 招聘站档案：核对与整改（2026-10-09）

用户 10-08 给的研究稿《GAME FREAK Recruit Archive Reconstruction（2019–2024）v0.1》提出：招聘站同一网址
换过人和正文、站内 19 篇标 2021-12-27 的日期不对、有几篇失落页面、人物名单分代。本目录是逐条核对的
材料与脚本，结论在 `findings.md`，整改方案在 `plan.md`。

## 做法

1. **网址枚举**：Wayback CDX 列出 `gamefreak.co.jp/recruit/*` 与 `recruit.gamefreak.co.jp/*` 存过的全部网址
   （`cdx-*.txt`，每行 urlkey / 首次快照 / 状态）。
2. **人物卡与对谈导航**：招聘首页 21 个快照（2019-09 → 2026-09），抽出每个快照里的 `interview-*` 与
   `crosstalk-*` / `projectstory-*` 链接（`index-rosters.json`，脚本 `scripts/roster.py`）。
3. **每页版本**：每个页面按 digest 去重抓全部快照的原始字节（`id_`），切出成员块与正文，正文哈希相同的
   连续快照并成一版；换版时记文字保留比例（difflib ratio）与增删行（研究时的结果 `versions-research.json`，`scripts/versions.py`；整理成工具后是 `tools/recruit-archive.py` → `_data/recruit_archive.yml`）。
   正文文本在 `versions/<slug>/<首个快照>.txt`。
4. **站内原文核对**：每篇站内帖子 `parallel_items` 里的日文 `original`，规范化后逐段在对应版本正文里找
   全段原样（重导前的结果 `fidelity-before-reimport.json`，`scripts/fidelity.py`；现在用 `tools/recruit-archive.py check`；旧版 .html 页用 `scripts/audit_old.py` 抓帖子自己引用的快照）。

原始快照缓存在 `data/cache_web/recruit-wayback/`（不进 git），可用 `tools/recruit-archive.py fetch` 重抓；Wayback 的 CDX 接口限流时会返回 “Temporarily
Offline”，脚本把它当成 0 个快照——数字异常的页面要单独重跑。

## 落地（2026-10-09）

- `pages.yml`：追踪的 37 个网址；`targets.yml`：`tools/import-gf-recruit.py` 导入 / 重导的 23 条。
- 重导 10 篇编造原文的帖子、新收 12 篇、世界观对谈补首版段落；其余招聘帖只改日期并加 `recruit:`（`scripts/stamp_posts.py`、`scripts/fix_gen1_dates.py`）。
- 衍生数据按新原文重算：今日一句（build-quotes --only interview-gamefreak-）、14 位员工的专长摘要、23 篇图鉴条目。
- 文章页「版本」说明：`_includes/recruit-version.html`；档案页：`_pages/gamefreak-recruit-archive.md`。
