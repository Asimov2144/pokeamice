# 杉森建のお絵かき日和数字存档

这是 GAME FREAK 官方历史博客“杉森建のお絵かき日和”的非官方数字存档工作区。

- 原站：`http://www.gamefreak.co.jp/blog/art/`
- 主要快照：`20130808124032`
- 已发现文章：5 篇（2007–2011）
- 内容特点：电影原创角色设计说明、150×150 缩略图及 `ZOOM` 原尺寸设定图

目录结构：

```text
raw/                 Web Archive 原始 HTML 与响应元数据
assets/original/     缩略图、原尺寸设定图和原模板素材
manifest/            文章与素材清单
content/             结构化日文正文、来源 HTML 和元数据
translations/zh-CN/  中文翻译层
reports/             完整性验证结果
```

完整运行：

```powershell
python tools/gamefreak_legacy_blogs_pipeline.py all --blog art --all --strict
```

素材清单使用 `design-thumbnail` 和 `design-full-resolution` 标记缩略图与原图的对应关系。发布页面默认引用原尺寸文件，并保留点击打开原图的交互。

公开页面遵循原博客的连续阅读方式：5 篇完整文章在同一页依次排列。中文译文与日文原文共用原有段落和图片位置，可在当前页面直接切换。

本项目与 GAME FREAK、Nintendo、Creatures、The Pokémon Company 无隶属关系。原文、角色与图片版权归原权利方所有。
