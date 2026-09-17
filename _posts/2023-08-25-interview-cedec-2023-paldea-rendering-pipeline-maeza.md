---
layout: interview-editorial
title: '[访谈翻译] 4Gamer CEDEC 2023 报告：前泽圭一详解《宝可梦 朱·紫》帕底亚全开放世界视觉呈现与流式渲染管线'
original_title: ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
date: '2023-08-25'
era: 2019–2026 · Expansion / 极巨化与开放世界
era_skin: '2019'
publication: 4Gamer.net (CEDEC 2023 特别报道 / Igarashi)
source_kind: technical_report
author: Igarashi / 4Gamer.net
translator: Poke Amice Studio
interviewee: 前泽圭一
toc: true
toc_sticky: true
parallel_view: translation
categories:
- 访谈翻译
- 翻译
- 访谈整理
tags:
- Pokemon
- 访谈
- 技术报告
- CEDEC
- Game Freak
- 前泽圭一
- 朱紫
- 帕底亚
- 图形渲染
- 开放世界
archive_type: interview_translation
source:
  title: ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
  url: https://www.4gamer.net/games/619/G061991/20230823075/
  language: ja
  source_type: technical_report
original_link: https://www.4gamer.net/games/619/G061991/20230823075/
summary: 2023年8月日本最大电脑娱乐开发者大会（CEDEC 2023）上，Game Freak CG 技术总监前泽圭一发表题为《帕底亚地区全景渲染——画面机制彻底解密》的技术报告。详细解构了《宝可梦 朱·紫》从微观生物到宏观开放世界的全链路着色与资产管线：明确了‘写实与变形’的核心美术基调；首次披露在宝可梦身上采用次表面散射（SSS）阴影漫反射、凝胶透明体与结构色；解密太晶化（Terastal）如何利用原有母模即时替换法线/噪波纹理、指定非太晶化保护网格，并通过外层半透明与内层不透明的双层折射网格塑造王冠立体纵深感；详述主角捏脸采用 Maya 晶格变形（Lattice）、5部件面部变形目标（Morph Target）与伪造法线平滑皮肤；并在全开放大地上引入 Maya+Houdini 程序化地形与植被遮罩、流向图与定制海岸拍岸浪花模型，以及基于预计算大气散射的动态天空。
entities:
  people:
  - 前泽圭一
  works:
  - 宝可梦 朱·紫
  - 宝可梦 剑·盾
parallel_items:
- speaker: 4Gamer
  original: 2023年8月23日，在游戏开发者大会‘CEDEC 2023’上，Game Freak 的 CG 技术总监前泽圭一进行了题为《【宝可梦 朱·紫】帕底亚地区全景渲染——画面机制彻底解密！》的主题演讲。全系列一贯秉承‘仅看画面就能认出是哪部作品’的前提进行研发。本讲座以《宝可梦 朱·紫》为例，从着色器渲染到资产构建，全面解析宝可梦、主角与开放世界大地的视觉技术体系。
  translation: "2023年8月23日，在游戏开发者大会“CEDEC 2023”上，GAME FREAK的CG技术总监前泽圭一发表了题为《【宝可梦 朱·紫】帕底亚地区全景渲染——画面机制彻底解密！》的主题演讲。该系列一贯秉承“仅凭画面即可辨识作品”的理念进行开发。本次讲座以《宝可梦 朱·紫》为例，从着色器渲染到资产构建，全面剖析了宝可梦、主角以及开放世界大地的视觉技术体系。"
- type: heading
  level: 3
  original: 'Artistic Direction: Finding Harmony Between Stylized Characters and Realistic Environments'
  translation: 视觉中枢理念：卡通变形生物与物理写实世界的黄金交点
- speaker: 前泽圭一
  original: 在《宝可梦 朱·紫》中，视觉核心概念被定义为‘写实与变形（Real & Deformed）’。我们的目标是将大自然背景的质感与地貌朝真实物理方向靠拢。然而，宝可梦和人类角色是高度卡通变形的，因此必须找到将它们完美融为一体的平衡折中点。
  translation: 在《宝可梦 朱·紫》中，视觉核心概念被定义为“写实与变形（Real & Deformed）”。我们的目标是将自然背景的质感与地貌向真实物理方向靠拢。然而，宝可梦和人类角色是高度卡通化的变形设计，因此必须找到将两者完美融合的平衡点。
- type: heading
  level: 3
  original: 'Pokémon Shaders: Subsurface Scattering, Paradox Particles, and Terastal Stereoscopic Crystals'
  translation: 宝可梦微观着色器：次表面散射、悖谬粒子与太晶化双层水晶折射
- speaker: 前泽圭一
  original: 在宝可梦主体的渲染中，首先广泛应用了次表面散射（SSS，Subsurface Scattering）的阴影漫反射技术。依据宝可梦体型大小、生物组织密度分别配置参数，极大丰富了宝可梦的肉体生命感。此外，还有半透明凝胶质感、结构色反光，以及悖谬宝可梦专属的粒子发光等多种特殊着色方案。
  translation: 在宝可梦主体的渲染中，首先广泛采用了次表面散射（SSS）的阴影漫反射技术。根据宝可梦的体型大小和生物组织密度分别配置参数，极大地增强了宝可梦肉体的生命感。此外，还实现了半透明凝胶质感、结构色反光，以及悖谬宝可梦专属的粒子发光等多种特殊着色方案。
  note: 次表面散射（SSS）是一种模拟光线穿透半透明材质（如皮肤、蜡）内部散射的渲染技术，能显著提升真实感。
- speaker: 前泽圭一
  original: 本作最大特色的‘太晶化’，在宝可梦主体上保留了原始母本模型，仅实时替换水晶物理材质，叠加法线贴图、色彩贴图与噪波纹理，呈现出晶莹剔透的水晶质感。同时系统支持指定‘非太晶化网格’，以保证眼睛和关键器官不被过度宝石化而失真。至于头顶出现的太晶王冠，则采用外层半透明网格搭配内层不透明网格的双层立体折射，营造出厚重而深邃的纵深感。
  translation: 本作最大特色“太晶化”在宝可梦主体上保留了原始模型，仅实时替换为水晶物理材质，并叠加法线贴图、色彩贴图与噪波纹理，呈现出晶莹剔透的水晶质感。同时，系统支持指定“非太晶化网格”，以确保眼睛和关键器官不会因过度宝石化而失真。至于头顶出现的太晶王冠，则采用外层半透明网格与内层不透明网格相结合的双层立体折射，营造出厚重而深邃的纵深感。
  note: 太晶化是《宝可梦 朱·紫》引入的独特战斗机制，可使宝可梦变为水晶形态并改变属性。
- type: heading
  level: 3
  original: 'Character Pipeline: Maya Lattice Facial Customization and Blendshape Runtime Morphing'
  translation: 角色定制与面部表情管线：Maya 晶格变形捏脸与伪造法线平滑皮肤
- speaker: 前泽圭一
  original: 关于主角的捏脸与形象定制：玩家可以在开局定制吊眼、垂眼、眼睛大小等面部细节。这一系统借助了 Maya 的晶格变形（Lattice）功能实现。通过晶格调节眼角倾斜、眼睛缩放、嘴巴宽窄与嘴唇薄厚。为了避免玩家手动微调过于繁复，团队将合理的变形数值组合打包成了面部预设。
  translation: 关于主角的捏脸与形象定制：玩家可以在游戏开始时定制吊眼、垂眼、眼睛大小等面部细节。该系统借助Maya的晶格变形（Lattice）功能实现，通过晶格调节眼角倾斜、眼睛缩放、嘴巴宽窄与嘴唇薄厚。为避免玩家手动微调过于繁琐，团队将合理的变形数值组合打包成了面部预设。
  note: Maya是Autodesk公司出品的3D建模与动画软件，晶格变形是一种通过控制点网格来整体变形物体的技术。
- speaker: 前泽圭一
  original: 眉毛则采用带有 Alpha 渐变的层级纹理贴图，实现了不同眉毛长度的自由切换。面部表情将五官划分为 5 个部件的变形目标（Morph Target），在运行时引擎中首先套用表情，随后叠加先前的晶格捏脸数据，完美实现了多变生动的面部表情。
  translation: 眉毛则采用带有Alpha渐变的层级纹理贴图，实现了不同眉毛长度的自由切换。面部表情将五官划分为5个部件的变形目标（Morph Target），在运行时引擎中首先套用表情，随后叠加先前的晶格捏脸数据，完美实现了多变生动的面部表情。
  note: Morph Target（变形目标）是一种通过插值不同顶点位置来生成动画的技术，常用于面部表情。
- speaker: 前泽圭一
  original: 皮肤质感方面，开发组通过生成伪造法线并与基础法线进行线性混合，针对面部与摄像机角度、光源方向等不同工况反复推敲最佳混合比例，平滑压制高光镜面反射（Specular），最终达成了符合‘写实与卡通共存’的高级质感。
  translation: 在皮肤质感方面，开发组通过生成伪造法线并与基础法线进行线性混合，针对面部与摄像机角度、光源方向等不同工况反复推敲最佳混合比例，平滑压制高光镜面反射（Specular），最终达成了符合“写实与卡通共存”的高级质感。
  note: 法线贴图是一种通过扰动表面法线来模拟细节凹凸的渲染技术，此处“伪造法线”可能指程序化生成的法线细节。
- type: heading
  level: 3
  original: 'Open-World Paldea: Procedural Houdini Landscapes, Wave Modeling, and Atmospheric Scattering'
  translation: 帕底亚全开放世界大地：Houdini 程序化地貌、海岸浪花模型与大气散射苍穹
- speaker: 前泽圭一
  original: 构建帕底亚全开放大地的技术管线：地貌以 Maya 的基础网格为底，利用 Houdini 进行全自动程序化细节增强，输出高度图（HeightMap）、地表物理材质与用于生成植被草花的遮罩（Mask）。此外，Houdini 还负责程序化建模悬崖岩石群并批量散布，自然雕琢出地貌细节。
  translation: 构建帕底亚全开放大地的技术管线：地貌以Maya的基础网格为底，利用Houdini进行全自动程序化细节增强，输出高度图（HeightMap）、地表物理材质以及用于生成植被草花的遮罩（Mask）。此外，Houdini还负责程序化建模悬崖岩石群并批量散布，自然雕琢出地貌细节。
  note: Houdini是SideFX公司出品的程序化3D软件，常用于生成复杂地形和特效。
- speaker: 前泽圭一
  original: 海面与河流的水体渲染：结合了顶点波浪位移、流向贴图（Flow Map）、基于水深的渐变透明度以及屏幕空间折射（Screen Space Refraction）。尤其在海岸线附近，研发团队专门制作了专属的岸边白浪模型，越接近陆地翻涌越剧烈，极大强化了波浪拍击感。
  translation: 海面与河流的水体渲染结合了顶点波浪位移、流向贴图（Flow Map）、基于水深的渐变透明度以及屏幕空间折射（Screen Space Refraction）。尤其在海岸线附近，研发团队专门制作了专属的岸边白浪模型，越接近陆地翻涌越剧烈，极大强化了波浪拍击感。
  note: Flow Map是一种控制纹理流动方向的贴图，常用于模拟水流。
- speaker: 前泽圭一
  original: 天空则基于预计算大气散射（Precomputed Atmospheric Scattering）技术呈现水平线的自然渐变。云层制作方面，将体积建模的云朵在 6 个方向打光烘焙至 2 张纹理贴图中，依据真实世界太阳天光光照信息动态计算渲染色彩。室内场景则采用轻量高效的光照贴图（Lightmap）呈现。
  translation: 天空则基于预计算大气散射（Precomputed Atmospheric Scattering）技术呈现水平线的自然渐变。云层制作方面，将体积建模的云朵在6个方向打光烘焙至2张纹理贴图中，依据真实世界太阳天光光照信息动态计算渲染色彩。室内场景则采用轻量高效的光照贴图（Lightmap）呈现。
  note: 预计算大气散射是一种模拟天空和大气效果的渲染技术，光照贴图是预先烘焙光照信息的纹理，用于提高实时渲染效率。
- speaker: 4Gamer
  original: 以上便是本次演讲的精髓。通过写实材质、程序化地形、次表面散射与多层晶格着色等一系列先进图形管线的配合，Game Freak 成功描绘出了兼具宝可梦梦幻魅力与广袤自然尺度的全新帕底亚大世界。
  translation: "以上便是本次演讲的精髓。通过写实材质、程序化地形、次表面散射与多层晶格着色等一系列先进图形管线的配合，GAME FREAK成功描绘出了兼具宝可梦梦幻魅力与广袤自然尺度的全新帕底亚大世界。"
original_lang: zh
display_title: 描摹广袤帕底亚：Game Freak 详解《宝可梦 朱·紫》全开放世界视觉渲染与着色器架构
---
