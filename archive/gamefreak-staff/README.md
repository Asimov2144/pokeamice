# 晴れたり時々曇ったり数字存档

这是 GAME FREAK 官方员工博客“晴れたり時々曇ったり”的非官方数字存档工作区。

- 原站：`http://www.gamefreak.co.jp/blog/staff/`
- 主要快照：`20130808162750`
- 过往日志清单：209 篇
- 内容范围：开发记录、员工日记、招聘、公司活动与宝可梦作品话题

目录结构：

```text
raw/                 Web Archive 原始索引、单篇 HTML 与响应元数据
assets/original/     正文图片、作者头像和原模板素材
manifest/            文章与素材清单
content/             结构化日文正文、来源 HTML 和元数据
translations/zh-CN/  中文翻译层
reports/             完整性验证结果
raw/history/         2013 年换主题以前的全部快照（逐篇页 / 月归档 / 首页 / 分类 / 标签 / RSS，862 份）
content/history/     从上面切出来的逐篇版本（<id>.yml，每篇带各次快照的正文、署名、分类、图片）
content/<id>/history.yml   逐篇恢复记录：署名、真实分类、乱码修复、原站改稿
assets/history/      早期模板素材（themes/）与员工头像（writers/）
```

早期版本对照（2026-09-29）：

```powershell
python tools/gamefreak_staff_history.py list; python tools/gamefreak_staff_history.py fetch
python tools/gamefreak_staff_history.py extract; python tools/gamefreak_staff_history.py compare
python tools/gamefreak_staff_history.py restore; python tools/gamefreak_staff_history.py publish
python tools/gamefreak_staff_history.py report    # → reports/history-report.md
```

结论见 `reports/history-report.md`：没有被删的文章、图片或视频；署名与分类在 2013 年换主题时丢了，
日文原文带着那次迁移造成的乱码——都已按早期版本补回 / 修正，原站真正改过的 2 处在文末「修订记录」。

完整运行：

```powershell
python tools/gamefreak_legacy_blogs_pipeline.py all --blog staff --all --strict
```

管线以原站“過去ログいちらん”的 209 条链接为权威清单。固定快照缺少素材时，会查询 Wayback CDX 并选择距离主要快照最近的成功记录。

公开页面保留原 WordPress 博客的阅读节奏：每页连续显示 10 篇完整文章，通过 Newer/Older 导航浏览，共生成 21 页；中文译文与日文原文可在当前阅读页直接切换。

本项目与 GAME FREAK、Nintendo、Creatures、The Pokémon Company 无隶属关系。原文与图片版权归原权利方所有。
