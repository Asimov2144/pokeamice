---
layout: interview-editorial
archive_type: interview_translation
title: CEDEC 2026：GAME FREAK 讲《Pokémon LEGENDS Z-A》密阿雷市渲染与绑定技术
display_title: 《Z-A》密阿雷市渲染技术
dek: 从《朱・紫》的广阔自然转向都市空间，GAME FREAK 详解高效渲染、景观表现与骨骼绑定。
original_title: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術
date: '2026-07-23'
era_skin: '2026'
categories:
- 访谈翻译
- 翻译
- 访谈整理
tags:
- 技术专题
- CEDEC 2026
- 讲演资料
- CEDiL
- 前泽圭一
- Alfredo Spadafina
- 赤木达也
- 株式会社ゲームフリーク
publication: CEDEC 2026 講演資料（CEDEC Digital Library）
source_kind: technical_report
article_kind: slide_deck
author: 前澤圭一、スパダフィーナアルフレド、赤木達也
interviewer: CEDEC 2026
interviewee: 前泽圭一、スパダフィーナアルフレド、赤木達也
organization: 株式会社ゲームフリーク
translator: PokeAmice（DeepSeek 初译）
original_lang: ja
translation_lang: zh-CN
source:
  title: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術
  url: https://cedil.cesa.or.jp/cedil_sessions/view/3366
  language: ja
  source_type: conference_slides
  file: ミアレシティがメガシンカ⁉ 『Pokémon LEGENDS Z-A』の描画技術.pdf
  access: CEDiL 免费注册后可下载
  text_is: 幻灯片文字
original_link: https://cedil.cesa.or.jp/cedil_sessions/view/3366
summary: 本讲演由 GAME FREAK 的前泽圭一、Alfredo Spadafina、赤木达也主讲，介绍《Pokémon LEGENDS Z-A》中以密阿雷市为舞台的都市空间实现。内容涵盖实例化与剔除等高效渲染机制、天空与水面及阴影等景观表现、角色渲染与超级进化表现、ポケリグ（PokéRig）的动作重定向举措，以及 Nintendo Switch 2 Edition 的支持工作。
session_abstract: '『Pokémon LEGENDS Z-A』で生まれ変わった"ミアレシティ"。

  前作『スカーレット・バイオレット』の広大な自然環境から一変し、多数の建物が立ち並ぶ都市空間をどのように実装したのか。

  本セッションでは、多数の建造物などを効率的に描画する仕組みや都市環境に適したライティング表現、キャラクターのリギングについてなど、網羅的に解説します。

  Nintendo Switch 2 Edition に向けた対応についてもお話します。'
session_abstract_zh: '《Pokémon LEGENDS Z-A》中焕然一新的“密阿雷市”。

  从前作《朱・紫》的广阔自然环境一变，本作要如何实现众多建筑林立的都市空间？

  本场讲演将全面解说高效渲染大量建筑物等对象的机制、适合都市环境的灯光表现、角色骨骼绑定等内容。

  此外也会谈及面向 Nintendo Switch 2 Edition 的对应工作。'
speakers:
- name: 前澤圭一
  org: 株式会社ゲームフリーク
  dept: CGテクノロジーラボ
  role: ディレクター
- name: スパダフィーナ アルフレド
  org: 株式会社ゲームフリーク
  dept: CGテクノロジーラボ 基盤技術セクション 技術展開チーム
  role: リーダー
- name: 赤木達也
  org: 株式会社ゲームフリーク
  dept: CGテクノロジーラボ ワークフローセクション
  role: セクションディレクター
entities:
  people:
  - 前泽圭一
  - Alfredo Spadafina
  - 赤木达也
  works:
  - Pokémon LEGENDS Z-A
  organizations:
  - 株式会社ゲームフリーク
workflow:
  fetch: cedil-pdf
  translation: deepseek-chat
  proofreading: pending
  published: draft
parallel_items:
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-01.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第1页
- original: 'ミアレシティがメガシンカ!?

    『Pokémon LEGENDS Z-A』の描画技術

    株式会社ゲームフリーク ／ 前澤圭一 ／ スパダフィーナアルフレド ／ 赤木達也'
  translation: '密阿雷市超级进化！？

    《Pokémon LEGENDS Z-A》的渲染技术

    株式会社GAME FREAK ／ 前泽圭一 ／ Alfredo Spadafina ／ 赤木达也'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-02.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第2页
- original: 'おことわり

    1. 本講演では、紙面の都合等により以下の省略表記を使用しています。

    2. 使用しているゲーム画面は開発機で撮影したものです。

    『ポケットモンスター』シリーズ

    →ポケモン

    『Pokémon LEGENDS Z-A』

    →Z-A ／ 『ポケットモンスターX・Y』 ／ →X・Y

    『ポケットモンスタースカーレット・バイオレット』

    →スカーレット・バイオレット'
  translation: '声明

    1. 本演讲中，出于篇幅等考虑，使用以下省略表述。

    2. 使用的游戏画面是在开发机上拍摄的。

    《宝可梦》系列

    →宝可梦

    《Pokémon LEGENDS Z-A》

    →Z-A ／ 《宝可梦X・Y》 ／ →X・Y

    《宝可梦 朱・紫》

    →朱・紫'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-03.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第3页
- original: '- 『ポケットモンスター』シリーズの新たな

    挑戦作

    - 『X・Y』に登場した街のひとつ、『ミアレ

    シティ』が舞台

    - 『スカーレット・バイオレット』の広大な

    自然環境から一変し、都市空間へ

    『Z-A』について'
  translation: '- 《宝可梦》系列的全新

    挑战作品

    - 以《X・Y》中登场的城市之一

    『密阿雷市』为舞台

    - 从《朱・紫》的广阔

    自然环境一变，转向都市空间

    关于《Z-A》'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-04.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第4页
- original: '- 都市空間について

    – 効率的に描画する仕組み ／ – 景観表現

    - キャラクターについて

    – 描画の仕組み（ちょっとだけ）

    – リグの取り組み

    - Nintendo Switch 2 対応

    本日の内容'
  translation: '- 关于都市空间

    – 高效渲染的机制 ／ – 景观表现

    - 关于角色

    – 渲染机制（稍微提及）

    – 骨骼绑定的举措

    - Nintendo Switch 2 支持

    今天的内容'
- type: heading
  level: 2
  original: 都市空間を効率的に描画
  translation: 高效渲染都市空间
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-06.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第6页
- original: マップの特徴 ／ [降り立ちのスクショ]
  translation: 地图的特征 ／ [降落时的截图]
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-07.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第7页
- original: 'マップの特徴 ／ [降り立ちのスクショ]

    - 同モデルのインスタンスが多い

    - 都市空間のため、遮蔽される描画物が多い'
  translation: '地图的特征 ／ [降落时的截图]

    - 相同模型的实例很多

    - 因为是都市空间，被遮挡的渲染物很多'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-08.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第8页
- original: '- 効率的な描画を行うにはこの点が重要となる

    – InstancedDraw

    – カリングの仕組み ／ マップの特徴'
  translation: '- 为了实现高效渲染，这一点很重要

    – InstancedDraw

    – 剔除机制 ／ 地图的特征'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-09.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第9页
- original: 'インスタンシング

    インスタンスモデルの種類ごとに

    InstancedDrawを大活用'
  translation: '实例化

    按实例模型种类

    大量使用 InstancedDraw'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-10.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第10页
- original: '- フラスタムカリング

    – 視野外のものをカリング

    - オクルージョンカリング

    – 遮蔽されているものをカリング

    カリング'
  translation: '- 视锥体剔除

    – 剔除视野外的物体

    - 遮挡剔除

    – 剔除被遮挡的物体

    剔除'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-11.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第11页
- original: '- ユニークモデル

    – CPU側で行う

    - インスタンスモデル

    – CPU側でグループ粒度で行う

    – GPU側でインスタンス粒度で行う

    (IndirectDraw) ／ フラスタムカリング'
  translation: '- 唯一模型

    – 在 CPU 侧进行

    - 实例模型

    – 在 CPU 侧以组粒度进行

    – 在 GPU 侧以实例粒度进行

    (IndirectDraw) / 视锥体剔除'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-12.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第12页
- original: フラスタムカリング
  translation: 视锥体剔除
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-13.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第13页
- original: 'オクルージョンカリング

    - オクルーダーをDepthPrePassに描画

    - オクルーダーのポリゴン数削減のため

    –

    シャドウマップ用のメッシュを利用

    – ／ （アーティスト側で用意） ／ –

    描画用メッシュからはみ出ないように調整'
  translation: '遮挡剔除

    - 将遮挡体绘制到 DepthPrePass

    - 为了减少遮挡体的多边形数量

    –

    利用阴影贴图用的网格

    – / （由美术师侧准备） / –

    调整使其不超出绘制用网格'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-14.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第14页
- original: オクルージョンカリング
  translation: 遮挡剔除
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-15.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第15页
- original: '- Hierarchical-Z カリング用のミップマップを作成

    オクルージョンカリング'
  translation: '- 创建用于 Hierarchical-Z 剔除的 mipmap

    遮挡剔除'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-16.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第16页
- original: '- パス構成

    オクルージョンカリング ／ DepthPrePass ／ OcclusionQuery ／ ComputeCulling ／ GBuffer描画等 ／ ユニークモデル ／ インスタンスモデル'
  translation: '- 通道构成

    遮挡剔除 / DepthPrePass / OcclusionQuery / ComputeCulling / GBuffer 绘制等 / 唯一模型 / 实例模型'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-17.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第17页
- original: '- ユニークモデル

    オクルージョンカリング ／ OcclusionQuery ／ AABBテスト

    DrawConditional

    GPU Counter ／ ¼ミップ

    （CPU・GPU間の同期不要）'
  translation: '- 独特模型

    遮挡剔除 ／ OcclusionQuery ／ AABB测试

    DrawConditional

    GPU Counter ／ ¼ Mip

    （无需 CPU 与 GPU 间同步）'
  note: OcclusionQuery 是 GPU 查询遮挡的机制；AABB 为轴对齐包围盒。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-18.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第18页
- original: '- インスタンスモデル

    オクルージョンカリング ／ ComputeCulling ／ 球体テスト ／ IndirectDraw ／ Hi-Zミップ

    ＊Nintendo Switch 2では

    AsyncComputeで実行'
  translation: '- 实例模型

    遮挡剔除 ／ ComputeCulling ／ 球体测试 ／ IndirectDraw ／ Hi-Z Mip

    ＊在 Nintendo Switch 2 上

    使用 AsyncCompute 执行'
  note: Hi-Z 为层次 Z 缓冲；AsyncCompute 指异步计算。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-19.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第19页
- original: 'オクルージョンカリング

    キャラクターはアニメを考慮するため、

    余裕を持ったバウンディングを利用'
  translation: '遮挡剔除

    角色因需考虑动画，

    使用留有余量的包围体'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-20.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第20页
- original: 'ポイントライトのカリング

    - ポイントライトは距離によるフェード'
  translation: '点光源的剔除

    - 点光源根据距离淡出'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-21.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第21页
- original: 'ポイントライトのカリング

    - Stencilマスクでポイントライトの計算範囲を絞る

    – 壁に隠れたライトに効果的'
  translation: '点光源的剔除

    - 用 Stencil 遮罩缩小点光源的计算范围

    – 对隐藏在墙壁后的光源有效'
  note: Stencil 遮罩即模板缓冲遮罩。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-22.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第22页
- original: 'ポイントライトのカリング

    - Stencilマスクでポイントライトの計算範囲を絞る

    – ポイントライトのバウンディングを一括描画（2回）

    → StencilMaskを生成

    – ステンシルテスト有効で ／ 実際にライトを計算'
  translation: '点光源的剔除

    - 用 Stencil 遮罩缩小点光源的计算范围

    – 批量绘制点光源的包围体（2 次）

    → 生成 StencilMask

    – 启用模板测试 ／ 实际计算光源'
- type: heading
  level: 2
  original: 都市空間の景観表現
  translation: 城市空间的景观表现
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-24.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第24页
- original: '空の表現

    - 天球モデルを利用

    - 空シェーダーで各種表現を実装'
  translation: '天空的表现

    - 使用天球模型

    - 通过天空着色器实现各种表现'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-25.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第25页
- original: '- 動的時間帯や天候に対応

    空の表現'
  translation: '- 支持动态时间段和天气

    天空的表现'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-26.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第26页
- original: '- 雲表現

    – カメラのレイ＋雲平面の交点を計算（UV)

    – 天候に合わせて、

    雲テクスチャのアルファの閾値を変更

    – さらにノイズを加味 ／ 空の表現'
  translation: '- 云的表现

    – 计算相机光线与云平面的交点（UV）

    – 根据天气改变云纹理的alpha阈值

    – 进一步加入噪声 ／ 天空的表现'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-27.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第27页
- original: '- Precomputed Atmospheric Scattering (Bruneton08)を参考に

    LUT参照でMie散乱を上乗せ

    - Rayleigh散乱はグラデーションで表現

    空の表現 ／ Mie散乱無し ／ Mie散乱有り'
  translation: '- 参考Precomputed Atmospheric Scattering (Bruneton08)

    通过LUT参照叠加Mie散射

    - Rayleigh散射用渐变表现

    天空的表现 ／ 无Mie散射 ／ 有Mie散射'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-28.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第28页
- original: '- 水面の描画

    水面の表現

    - フローマップテクスチャによる流れの表現

    - スクリーンスペース屈折'
  translation: '- 水面的绘制

    水面的表现

    - 通过流图纹理表现流动

    - 屏幕空间折射'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-29.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第29页
- original: '- 水面の反射

    – ／ SSRは負荷により断念 ／ –

    代わりにレイマーチが不要なScreen Space Planar Reflectionsを採用

    水面の表現 ／ 無し ／ 有り'
  translation: '- 水面的反射

    – ／ 因负载放弃SSR ／ –

    作为替代，采用不需要光线步进的Screen Space Planar Reflections

    水面的表现 ／ 无 ／ 有'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-30.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第30页
- original: '- SSPRの特徴

    – レイマーチを行わない（SSRより低コスト）

    – シーンをもう一度描画しない（PlanarReflectionより低コスト）

    – 制約：水面は固定の高さ（PlanarReflectionと同様）

    水面の表現'
  translation: '- SSPR的特点

    – 不进行光线步进（比SSR成本低）

    – 不重新绘制场景（比PlanarReflection成本低）

    – 限制：水面高度固定（与PlanarReflection相同）

    水面的表现'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-31.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第31页
- original: '- SSPRの条件

    – 水面が固定の高さである

    - 問題

    – ミアレシティは川や池があり、高さはバラバラ

    → 条件を満たせない ／ 水面の表現'
  translation: '- SSPR的条件

    – 水面高度固定

    - 问题

    – 密阿雷市有河流和池塘，高度各不相同

    → 无法满足条件 ／ 水面的表现'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-32.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第32页
- original: '- 回避策

    - ３つのSSPRテクスチャを計算

    – ／ 主要な水面のみに適用 ／ （他はIBLのみ） ／ –

    高さが近いものは同じテクスチャ

    を参照 ／ – ／ 処理負荷が増えるが ／ SSRよりまだまだ軽い ／ 水面の表現 ／ 高さはcm単位'
  translation: '- 规避方案

    - 计算3个SSPR纹理

    – ／ 仅应用于主要水面 ／ （其他仅用IBL） ／ –

    高度相近的水面参照相同的纹理 ／ – ／ 虽然处理负载增加 ／ 但仍比SSR轻得多 ／ 水面的表现 ／ 高度以cm为单位'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-33.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第33页
- original: '水面の表現

    SSPR計算結果（1/2解像度）

    水シェーダーで合成

    反射が取れないところは周辺ピクセルの色で補完'
  translation: '水面表现

    SSPR 计算结果（1/2 分辨率）

    在水面 shader 中合成

    无法取得反射的部分用周边像素颜色补全'
  note: SSPR 即屏幕空间平面反射（Screen Space Planar Reflection）。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-34.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第34页
- original: '影

    - 中景まではCSMで表現

    - 中～遠景はベイク影で表現'
  translation: '阴影

    - 中景为止用 CSM 表现

    - 中景至远景用烘焙阴影表现'
  note: CSM 即级联阴影贴图（Cascaded Shadow Maps）。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-35.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第35页
- original: 影 ／ CSM影 ／ ベイク影
  translation: 阴影 ／ CSM 阴影 ／ 烘焙阴影
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-36.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第36页
- original: ベイク影（遠景） ／ ベイク影無し
  translation: 烘焙阴影（远景） ／ 无烘焙阴影
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-37.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第37页
- original: ベイク影（遠景） ／ ベイク影有り
  translation: 烘焙阴影（远景） ／ 有烘焙阴影
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-38.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第38页
- original: ベイク影（遠景） ／ ベイク影無し
  translation: 烘焙阴影（远景） ／ 无烘焙阴影
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-39.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第39页
- original: ベイク影（遠景） ／ ベイク影有り
  translation: 烘焙阴影（远景） ／ 有烘焙阴影
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-40.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第40页
- original: '- ベイク手法

    – 雨の遮蔽計算にも使われる、ミアレシティ全体のY軸デプスを用

    いて、オフラインで計算

    - ベイク影の時間帯対応

    – ４つの太陽の方向からベイクし、RGBAテクスチャに格納

    – 時間帯に合わせてRGBAを動的にブレンド

    - 結果をY軸（上）から投影

    ベイク影（遠景）'
  translation: '- 烘焙方法

    – 使用也用于雨遮蔽计算的密阿雷市整体 Y 轴深度，离线计算

    - 烘焙阴影的时间段对应

    – 从 4 个太阳方向烘焙，存入 RGBA 纹理

    – 根据时间段动态混合 RGBA

    - 将结果从 Y 轴（上方）投影

    烘焙阴影（远景）'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-41.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第41页
- original: ベイク影 ／ Y+デプス ／ 影ベイク ／ 4方向ベイク結果 ／ R ／ G ／ B ／ A ／ 時間
  translation: 烘焙阴影 ／ Y+深度 ／ 阴影烘焙 ／ 4方向烘焙结果 ／ R ／ G ／ B ／ A ／ 时间
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-42.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第42页
- original: '- ロワイヤルナイト（夜）

    – メインライト（月）の方向と軌道が

    太陽と異なる

    – 昼間とテクスチャを分けてベイク

    – ロワイヤルナイトの出入りの演出で

    切り替えが見えない

    - プリズムタワーの影は除外

    – 大きすぎるため ／ ベイク影 ／ （昼用） ／ （夜用）'
  translation: '- 皇家骑士（夜）

    – 主光源（月亮）的方向和轨道与太阳不同

    – 白天和夜晚的纹理分开烘焙

    – 皇家骑士出入的演出中看不到切换

    - 棱镜塔的阴影除外

    – 因为太大 ／ 烘焙阴影 ／ （白天用） ／ （夜晚用）'
  note: 皇家骑士是密阿雷市的地标建筑，夜晚有灯光演出。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-43.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第43页
- original: '- Y軸投影によるアーティファクト

    – 建物の壁等、Y軸に平行な表面では

    アーティファクトが発生

    – 影ピクセルのエイリアシングが原因

    ベイク影'
  translation: '- Y轴投影导致的伪影

    – 建筑物的墙壁等与Y轴平行的表面会产生伪影

    – 原因是阴影像素的锯齿

    烘焙阴影'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-44.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第44页
- original: '- ベイクツール側でフィルタリングして緩和

    ベイク影 ／ デプスから壁などを検知（緑） ／ マスクとして利用 ／ フィルター処理 ／ エッジをぼかす ／ 周辺のピクセルを考慮して、

    影があるかないかはっきりさせる

    ＋'
  translation: '- 在烘焙工具侧进行过滤来缓解

    烘焙阴影 ／ 从深度检测墙壁等（绿色） ／ 作为遮罩使用 ／ 过滤处理 ／ 模糊边缘 ／ 考虑周围像素，明确有无阴影

    ＋'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-45.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第45页
- original: '- ベイクツール側でフィルタリングして緩和

    ベイク影 ／ 改善前 ／ 改善後'
  translation: '- 在烘焙工具侧进行过滤来缓解

    烘焙阴影 ／ 改善前 ／ 改善后'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-46.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第46页
- original: '- Y軸投影による制限：高さレイヤーに対応できない

    –

    上にある物の影状態が下に引き継がれる

    ベイク影 ／ 橋'
  translation: '- Y轴投影的限制：无法对应高度层

    –

    上方物体的阴影状态会继承到下方

    烘焙阴影 ／ 桥'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-47.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第47页
- original: '- 夜の絵作りに重要な街灯

    街灯の表現'
  translation: '- 对夜晚画面构建重要的街灯

    街灯的表现'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-48.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第48页
- original: '- 光源部分はビルボード

    - デプスフェード

    - 距離フェード

    街灯の表現'
  translation: '- 光源部分使用公告板

    - 深度淡出

    - 距离淡出

    街灯的表现'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-49.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第49页
- original: '- スポットライトのボリューム表現

    - 半透明の

    円錐モデルで疑似表現 ／ 街灯の表現'
  translation: '- 聚光灯的体积表现

    - 用半透明的

    圆锥模型进行伪表现 ／ 街灯的表现'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-50.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第50页
- original: '- 法線によるαフェード

    街灯の表現

    - 頂点距離によるαフェード

    - デプス距離によるαフェード'
  translation: '- 基于法线的α淡出

    街灯的表现

    - 基于顶点距离的α淡出

    - 基于深度距离的α淡出'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-51.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第51页
- original: キャラクターの描画の仕組み ／ （ちょっとだけ）
  translation: 角色绘制的机制 ／ （稍微提一下）
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-52.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第52页
- original: '- 背景は全ディファード

    - キャラクターは一部フォワードで計算（Emissionに入力）

    – ／ メインライト成分 ／ – ／ リムライト表現 ／ キャラクターの描画の仕組み ／ 時間帯'
  translation: '- 背景全部使用延迟渲染

    - 角色部分使用前向渲染计算（输入到Emission）

    – ／ 主光源成分 ／ – ／ 边缘光表现 ／ 角色绘制的机制 ／ 时间段'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-53.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第53页
- original: 'キャラクターの描画の仕組み

    - GIの合成

    - ポイントライト・スポットライト（LambertDiffuseのみ）

    - ディファードで計算'
  translation: '角色绘制的机制

    - GI的合成

    - 点光源・聚光灯（仅LambertDiffuse）

    - 在延迟渲染中计算'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-54.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第54页
- original: 'メガシンカの表現

    - メガシンカ時の見た目

    –

    リムライト＋ノイズテクスチャを

    上乗せ（Triplanar) ／ – ／ スクロールアニメーション ／ –

    ポケモンのサイズグループ単位で

    パラメータを設定 ／ ＋ ／ 色 ／ 強度'
  translation: '超级进化的表现

    - 超级进化时的外观

    –

    叠加边缘光＋噪声纹理

    （Triplanar） ／ – ／ 滚动动画 ／ –

    按宝可梦的尺寸组

    设置参数 ／ ＋ ／ 颜色 ／ 强度'
- type: heading
  level: 2
  original: リグの取り組み
  translation: Rig的举措
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-56.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第56页
- original: '目次(リグパート)

    - ポケモンタイトル制作での課題

    - ポケリグとは？

    - ポケリグによる課題解決

    - 『Z-A』で取り組んだ内容

    - 今後の予定'
  translation: "目录（Rig部分）\n- 宝可梦标题制作中的课题\n- 什么是ポケリグ？\n- 通过ポケリグ解决课题\n- 在《Z-A》中着手的内容\n- 今后的计划"
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-57.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第57页
- original: '総数1000種以上のポケモン+ 人物

    ポケモンタイトル制作での課題

    - 登場するキャラクタの数が膨大(x モーションの数)

    - 継続・進化していくシリーズタイトル(一度作ったら終わり、ではない)

    - 『スカーレット・バイオレット』以前は、人物リグとポケモンリグは異なるリグシステム

    解決のアプローチ

    これらを解決する統合リギングシステム=ポケリグを開発し解決

    誰もがリグを作る事が出来る

    関わるデザイナーが多くとも堅牢かつ安定

    リグモジュール・ビルドシステム

    効率的なデータ再利用

    リグや骨が異なっていてもモーションを再利用

    モーションリターゲット ／ リグシステムの統合 ／ 学習コスト・運用コスト低減 ／ 段階的な導入'
  translation: '总数1000种以上的宝可梦+ 人物

    宝可梦作品制作中的课题

    - 登场角色数量庞大（× 动作数量）

    - 持续进化中的系列作品（并非做完一次就结束）

    - 在《朱·紫》之前，人物绑定与宝可梦绑定使用不同的绑定系统

    解决方案

    开发出解决这些问题的集成绑定系统=ポケリグ

    任何人都能制作绑定

    即使参与的设计师众多也能保持稳健与稳定

    绑定模块·构建系统

    高效的数据复用

    即使绑定和骨骼不同也能复用动作

    动作重定向 ／ 绑定系统的集成 ／ 学习成本·运维成本降低 ／ 分阶段导入'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-58.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第58页
- original: 'ポケリグ：リグモジュール・ビルドシステム

    リグモジュール ／ リグ生成 ／ リグ用モデル ／ IK設定 ／ 補助骨設定 ／ リグシーン ／ 手作業による ／ エラー防止 ／ 部分更新可能 ／ 規則・最適化 ／ 自動適用

    必ずリグ生成内の処理で完成させる！'
  translation: 'ポケリグ：绑定模块·构建系统

    绑定模块 ／ 绑定生成 ／ 绑定用模型 ／ IK设置 ／ 辅助骨骼设置 ／ 绑定场景 ／ 手动操作 ／ 防止错误 ／ 可部分更新 ／ 规则·优化 ／ 自动应用

    必须在绑定生成内的处理中完成！'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-59.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第59页
- original: 'ポケリグ：モーションリターゲット

    モーション ／ リマップ処理 ／ FKコントローラ ／ IKコントローラ

    - 骨名の変換

    - 抽象化

    コンバートシーン ／ リターゲット ／ 元キャラ ／ リグ ／ リグ ／ リターゲット ／ 先キャラ

    ポケモンにおけるモーションリターゲット

    - ポケモン毎に骨構造が異なる

    関係性を表すシーンが必要

    - コンバートシーンを用意する事

    で大量リターゲットに対応 ／ モーション'
  translation: 'ポケリグ：动作重定向

    动作 ／ 重映射处理 ／ FK控制器 ／ IK控制器

    - 骨骼名称的转换

    - 抽象化

    转换场景 ／ 重定向 ／ 原角色 ／ 绑定 ／ 绑定 ／ 重定向 ／ 目标角色

    宝可梦中的动作重定向

    - 每只宝可梦的骨骼结构不同

    需要表示关系的场景

    - 通过准备转换场景

    应对大量重定向 ／ 动作'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-60.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第60页
- original: '前作：『ポケットモンスタースカーレット・バイオレット』

    ポケリグの段階的な導入

    今作：『Pokémon LEGENDS Z-A』

    人物 ／ ポケモン ／ ポケリグ ／ 一部ポケモンで初導入 ／ 一部ポケモンおよび人物で導入 ／ 人物 ／ ポケモン ／ ポケリグ ／ 段階的な導入中：リスク低減

    人物キャラクタ対応が大きなポイント'
  translation: '前作：《宝可梦 朱·紫》

    ポケリグ的分阶段导入

    本作：《Pokémon LEGENDS Z-A》

    人物 ／ 宝可梦 ／ ポケリグ ／ 部分宝可梦首次导入 ／ 部分宝可梦及人物导入 ／ 人物 ／ 宝可梦 ／ ポケリグ ／ 分阶段导入中：降低风险

    人物角色支持是重点'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-61.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第61页
- original: 『Z-A』で取り組んだ内容 ／ キャラクタエディット ／ 過去作からの ／ モーションリターゲット ／ 人物への ／ モーションキャプチャ ／ ポケリグを拡張し ／ 人物キャラクタに対応する
  translation: 《Z-A》中着手的内容 ／ 角色编辑 ／ 来自过去作品的 ／ 动作重定向 ／ 对人物的 ／ 动作捕捉 ／ 扩展ポケリグ ／ 支持人物角色
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-62.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第62页
- original: '対応の方針

    - 共通のワークフロー・データフロー化

    リグの機能・仕様はなるべく統一する。

    - 個別の対応を行わない。

    ポケモンと人物のリグの対応をそれぞれ行わない。'
  translation: '应对方针

    - 统一工作流·数据流

    尽量统一绑定的功能·规格。

    - 不进行个别应对。

    不对宝可梦和人物的绑定分别进行应对。'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-63.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第63页
- original: 'キャラクタエディット

    複数のパーツリグを合成し一つのリグとして組み上げるフロー

    服パーツリグモジュール ／ リグ生成 ／ リグ用服モデル ／ FKリグ ／ 補助骨設定 ／ 服パーツリグ ／ リグシーン ／ リグ生成 ／ 顔パーツリグモジュール ／ リグ生成 ／ リグ用顔モデル ／ FKリグ ／ Eyeリグ ／ 顔パーツリグ

    リグビルドシステムの拡張で対応'
  translation: '角色编辑

    将多个部件绑定合成并组装为一个绑定的流程

    服装部件绑定模块 ／ 绑定生成 ／ 绑定用服装模型 ／ FK绑定 ／ 辅助骨骼设置 ／ 服装部件绑定 ／ 绑定场景 ／ 绑定生成 ／ 面部部件绑定模块 ／ 绑定生成 ／ 绑定用面部模型 ／ FK绑定 ／ Eye绑定 ／ 面部部件绑定

    通过扩展绑定构建系统来应对'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-64.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第64页
- original: '人物へのモーションキャプチャ対応

    フローは変えずに、ポケモンの仕様の一つとして

    リマップ処理内で対応 ／ FKコントローラ ／ IKコントローラ ／ T-Pose ／ HumanIK ／ リマップ処理 ／ ポケリグ ／ リターゲット ／ 先キャラ ／ モーション ／ モーキャプモーション ／ 人物は骨構造の共通化可能 ／ コンバートシーン無し

    - リマップ処理内で分岐

    - モーキャプデータの入力時

    に切替'
  translation: '对人物的动作捕捉支持

    不改变流程，作为宝可梦规格之一

    在重映射处理内应对 ／ FK控制器 ／ IK控制器 ／ T-Pose ／ HumanIK ／ 重映射处理 ／ ポケリグ ／ 重定向 ／ 目标角色 ／ 动作 ／ 动捕动作 ／ 人物可共用骨骼结构 ／ 无需转换场景

    - 在重映射处理内分支

    - 动捕数据输入时

    切换'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-65.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第65页
- original: '過去作からのリターゲット対応

    フローは変えずに、ポケモンの仕様の一つとして

    リマップ処理内で対応 ／ FKコントローラ ／ IKコントローラ ／ 過去作モーション ／ 過去作リグ ／ ポケリグ ／ リターゲット ／ 先キャラ ／ モーション

    - リマップ処理内で分岐

    - 人物の仕様は、リグシステムに

    つき１つだけなので、過去作リグ

    の仕様差を補間する処理を通す ／ リマップ処理 ／ HumanIK'
  translation: '从过去作品的重定向支持

    流程不变，作为宝可梦规格之一

    在重映射处理内应对 ／ FK控制器 ／ IK控制器 ／ 过去作品动作 ／ 过去作品骨骼 ／ 宝可梦骨骼 ／ 重定向 ／ 目标角色 ／ 动作

    - 在重映射处理内分支

    - 人物的规格，在骨骼系统中

    只有一个，因此通过处理来补间过去作品骨骼

    的规格差异 ／ 重映射处理 ／ HumanIK'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-66.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第66页
- original: '⚫全ポケモンのポケリグ化

    ⚫中間構造を挟む事で抽象度を上げる

    ⚫リグの構造に依らないモーションリターゲット

    今後の予定'
  translation: '⚫所有宝可梦的宝可梦骨骼化

    ⚫通过插入中间结构提高抽象度

    ⚫不依赖骨骼结构的动作重定向

    今后的计划'
- type: heading
  level: 2
  original: Nintendo Switch 2 対応
  translation: Nintendo Switch 2 支持
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-68.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第68页
- original: '- 情報開示者が限られている

    – Switch 版の開発メンバー全員が情報にアクセスでき

    るわけではない

    – 一部のメンバーだけで、こっそりとSwitch 2 対応を

    行う必要がある

    - Switch 版と差別化が必要

    – より魅力的にする必要がある

    課題 ／ 機密保持 ／ 品質向上'
  translation: '- 信息知情人有限

    – 并非所有Switch版开发成员都能访问信息

    – 需要仅由部分成员秘密进行Switch 2支持

    - 需要与Switch版差异化

    – 需要使其更具吸引力

    课题 ／ 机密保持 ／ 质量提升'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-69.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第69页
- original: '- 作業場所として施錠可能な会議室を占有

    – 4人が常駐

    – 明るさが足りなかったため、LED投光器を2基設置

    - 情報はSlack に集約

    – Confluence / Jira 管理者に非開示者が

    含まれていたため（後日解消） ／ 開発準備 ／ 機密保持'
  translation: '- 占用可上锁的会议室作为工作场所

    – 4人常驻

    – 因亮度不足，设置了2台LED投光灯

    - 信息集中到Slack

    – 由于Confluence / Jira管理员中包含非知情人

    （日后解决） ／ 开发准备 ／ 机密保持'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-70.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第70页
- original: '- Switch 版のソリューションをSwitch 2 版に

    変換するスクリプトを作成

    – sln / vcxproj を文字列置換

    – Switch 2 版のライブラリを配置

    – システム用テクスチャを変換・差し替え

    – 誤push 防止のため、gitignore 設定

    Switch 2 版の自動生成

    機密保持'
  translation: '- 创建将Switch版解决方案转换为Switch 2版

    的脚本

    – 对sln / vcxproj进行字符串替换

    – 配置Switch 2版的库

    – 转换・替换系统用纹理

    – 为防止误push，设置gitignore

    Switch 2版的自动生成

    机密保持'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-71.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第71页
- original: '- GitLab プロジェクト（検証用）

    – Switch 版のプロジェクトを基に生成

    – 誤操作防止のため、フォーク関係を解除

    - IncrediBuild

    – 専用のBuild Group を作成

    ソース管理とビルド ／ 機密保持'
  translation: '- GitLab项目（验证用）

    – 基于Switch版项目生成

    – 为防止误操作，解除fork关系

    - IncrediBuild

    – 创建专用的Build Group

    源代码管理与构建 ／ 机密保持'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-72.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第72页
- original: '- Jenkins 環境を二重化

    – Switch 用/ Switch 2 用

    - P4 環境の切り分けは、p4 protect で制御

    – ワークスペースはそれぞれ保持

    - Switch 版をベースにSwitch 2 版が

    デイリー生成されるよう、環境を構築

    – テクスチャは高解像度に ／ CI/CD 環境の整備 ／ 機密保持'
  translation: '- Jenkins环境双重化

    – Switch用/ Switch 2用

    - P4环境的划分通过p4 protect控制

    – 各自保持工作区

    - 构建环境，使基于Switch版的Switch 2版

    每日生成

    – 纹理高分辨率化 ／ CI/CD环境的整备 ／ 机密保持'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-73.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第73页
- original: '- テクスチャのマスターデータは高解像度

    – Switch 版では、コンバート時にダウンスケールして

    いる

    - Switch 2 版はそのままコンバートするよう、

    引数で分岐 ／ テクスチャ解像度の分岐 ／ 品質向上'
  translation: '- 纹理的母版数据为高分辨率

    – Switch 版在转换时会进行降采样

    - Switch 2 版则通过参数分支直接转换 ／ 纹理分辨率的分支 ／ 品质提升'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-74.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第74页
- original: '- 試してみたら、そこそこ動いた

    - おかしなところを直していった

    – はしごを昇ると屋根に上がろうとするところで落下す

    る

    – UIのリストでスクロール時にカーソルが滑る

    – メッセージ送り音が2連続で再生される

    – ボール投げすると、1投で2個減る

    60 fps 対応 ／ 品質向上'
  translation: '- 试着一跑，居然还能跑起来

    - 把奇怪的地方逐个修掉了

    – 爬梯子上屋顶时会在半途掉落

    – UI 列表滚动时光标会打滑

    – 消息推进音会连续播放两次

    – 投球时，投一次会减少两个

    60 fps 支持 ／ 品质提升'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-75.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第75页
- original: 'DLSS OFF (Switch)

    品質向上'
  translation: 'DLSS OFF (Switch)

    品质提升'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-76.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第76页
- original: 'DLSS ON (Switch 2)

    品質向上'
  translation: 'DLSS ON (Switch 2)

    品质提升'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-77.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第77页
- original: 'SSAO OFF (Switch)

    品質向上'
  translation: 'SSAO OFF (Switch)

    品质提升'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-78.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第78页
- original: 'SSAO ON (Switch 2)

    品質向上'
  translation: 'SSAO ON (Switch 2)

    品质提升'
- type: heading
  level: 2
  original: まとめ
  translation: 总结
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-80.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第80页
- original: '- 都市空間について

    – 効率的に描画する仕組み ／ – 景観表現

    - キャラクターについて

    – 描画の仕組み（ちょっとだけ）

    – リグの取り組み

    - Nintendo Switch 2 対応

    まとめ'
  translation: '- 关于都市空间

    – 高效渲染的机制 ／ – 景观表现

    - 关于角色

    – 渲染机制（只讲一点点）

    – 骨骼绑定的举措

    - Nintendo Switch 2 支持

    总结'
- type: image
  image: /assets/img/interviews/2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck/slide-81.jpg
  alt: ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術 - 第81页
---
