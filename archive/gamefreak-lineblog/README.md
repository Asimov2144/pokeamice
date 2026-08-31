# 増田順一 LINE BLOG 数字存档

本目录保存已关闭的「増田順一 公式ブログ Powered by LINE」之本地工作副本。资料按 `raw → assets → content → translations` 分层；网站页面由这些层生成，不直接修改原始抓取文件。

- 原站：`https://lineblog.me/masudajunichi/`
- 基准快照：`2018-06-03 17:19:31 UTC`
- 展示入口：`/gamefreak-director/`
- 性质：非官方、非商业数字存档与中文翻译项目

默认管线只处理三篇结构样本：

```powershell
python tools/gamefreak_lineblog_pipeline.py all
```

完整发现与抓取：

```powershell
python tools/gamefreak_lineblog_pipeline.py discover --all
python tools/gamefreak_lineblog_pipeline.py capture --all
python tools/gamefreak_lineblog_pipeline.py extract --all
python tools/gamefreak_lineblog_pipeline.py publish --all
python tools/gamefreak_lineblog_pipeline.py validate --all --strict
```

原文、图片及商标权利归各权利方所有；LINE BLOG 平台曾由 LINE 运营。本目录仅为研究、检索与保存历史页面结构而设。
