---
layout: interview-editorial
archive_type: interview_translation
title: '[访谈翻译] 4Gamer CEDEC 2023 报告：前泽圭一详解《宝可梦 朱·紫》帕底亚全开放世界视觉呈现与流式渲染管线'
display_title: 宝可梦SV如何描绘帕底亚
dek: GAME FREAK前泽圭一在CEDEC 2023讲解《宝可梦 朱·紫》从着色器到资源构成的视觉表现机制。
original_title: ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
date: '2023-08-25'
era_skin: '2019'
categories:
- 访谈翻译
- 翻译
- 访谈整理
tags:
- 访谈
- Game Freak
- 4Gamer
- CEDEC 2023
- 前泽圭一
- 朱紫
- 帕底亚
- 图形渲染
- 开放世界
- 技术报告
- Pokemon
- CEDEC
publication: 4Gamer.net（2023-08-25）
source_kind: lecture_report
author: Igarashi
interviewer: Igarashi
interviewee: 前泽圭一
translator: PokeAmice（DeepSeek 初译）
original_lang: ja
translation_lang: zh-CN
source:
  title: ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
  url: https://www.4gamer.net/games/619/G061991/20230823075/
  language: ja
  source_type: media_interview
original_link: https://www.4gamer.net/games/619/G061991/20230823075/
summary: GAME FREAK前泽圭一在CEDEC 2023演讲，介绍《宝可梦 朱·紫》以“真实与变形”为视觉概念，讲解宝可梦的SSS阴影、太晶化材质、主角自定义与表情、帕底亚地区地形、水面与天空等表现手法。
entities:
  people:
  - 前泽圭一
  works:
  - 宝可梦 朱·紫
  - 宝可梦 剑·盾
workflow:
  fetch: live
  translation: deepseek-chat
  proofreading: pending
  published: draft
parallel_items:
- original: 前澤圭一氏
  translation: 前泽圭一
  note: GAME FREAK的开发者，曾参与《宝可梦》系列的技术与图形相关工作。
- original: 2023年8月23日，ゲーム開発者向けカンファレンス「CEDEC 2023」にて，ゲームフリークの前澤圭一氏による講演「【ポケットモンスター スカーレット・バイオレット】 パルデア地方を描き出す――見た目の仕組みを徹底解説！」が行われた。
  translation: 2023年8月23日，在面向游戏开发者的会议“CEDEC 2023”上，GAME FREAK的前泽圭一进行了题为“【宝可梦 朱·紫】描绘帕底亚地区——彻底解说视觉外观的机制！”的演讲。
- original: 本講演は，「絵を見ればどのタイトルかわかる」を前提に開発しているという「ポケットモンスター」シリーズ。本公演は，「ポケットモンスター スカーレット・バイオレット」（以下，ポケモンSV）を例に，ポケモン，主人公，世界のそれぞれについて，シェーダ処理からアセット構成まで徹底的に解説するというものだ。
  translation: 本演讲以“看画面就能知道是哪部作品”为前提进行开发的《宝可梦》系列。本次演讲以《宝可梦 朱·紫》（以下简称宝可梦SV）为例，从着色器处理到资源构成，彻底解说了宝可梦、主角、世界各自的表现方式。
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/002.jpg
  alt: 画像ギャラリー No.002のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/003.jpg
  alt: 画像ギャラリー No.003のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- original: 前澤氏によると，ポケモンSVにおけるルックコンセプトは“リアルとデフォルメ”であり，背景の質感や形状はリアル方面に寄せていくのが目標だったという。しかし，ポケモンや人物キャラクターはデフォルメされているため，それらを統合したときの落としどころを探る必要があったそうだ。
  translation: 据前泽介绍，宝可梦SV的视觉概念是“真实与变形”，目标是让背景的质感和形状偏向真实方向。然而，由于宝可梦和人物角色是变形的，因此需要探索将它们整合时的平衡点。
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/004.jpg
  alt: 画像ギャラリー No.004のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/005.jpg
  alt: 画像ギャラリー No.005のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/006.jpg
  alt: 画像ギャラリー No.006のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/007.jpg
  alt: 画像ギャラリー No.007のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/008.jpg
  alt: 画像ギャラリー No.008のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/009.jpg
  alt: 画像ギャラリー No.009のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/010.jpg
  alt: 画像ギャラリー No.010のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- original: 講演ではまず，マテリアルの構成やライティングなど，作品全体の基本的な表現方法が紹介されたのち，ポケモンに使用されている特殊表現について解説された。
  translation: 演讲首先介绍了材质构成和光照等作品整体的基本表现方法，随后解说了宝可梦所使用的特殊表现。
- original: ポケモンの主な表現としてまず挙げられたのは，SSS（Subsurface Scattering）による陰影表現だ。この表現は体の大きさや密度などに合わせて，さまざまな設定で使い分けられており，ポケモンの個性に大きな影響を与えているようだ。
  translation: 作为宝可梦的主要表现，首先提到的是基于SSS（次表面散射）的阴影表现。这种表现根据身体大小和密度等，以各种设置区分使用，似乎对宝可梦的个性产生了很大影响。
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/011.jpg
  alt: 画像ギャラリー No.011のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/012.jpg
  alt: 画像ギャラリー No.012のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/013.jpg
  alt: 画像ギャラリー No.013のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/014.jpg
  alt: 画像ギャラリー No.014のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/015.jpg
  alt: 画像ギャラリー No.015のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/016.jpg
  alt: 画像ギャラリー No.016のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/017.jpg
  alt: 画像ギャラリー No.017のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- original: ほかにもジェルのような質感の出し方や，構造色の表現，パラドックスポケモンの粒子の表現などさまざまな手法が紹介されつつ，ポケモンSVの大きな特徴となっている「テラスタル」についても触れられた。
  translation: 此外，还介绍了表现凝胶般质感的方法、结构色表现、悖谬宝可梦的粒子表现等各种手法，同时也提到了宝可梦SV的一大特征“太晶化”。
- original: テラスタルでは，本体（ポケモン）部分については元々のモデルそのままにマテリアルを差し替え，ノーマルマップやカラーマップ，ノイズテクスチャを適用することで，宝石の質感を表現しているという。ただ，すべてを宝石化してしまうと見栄えが良くないため，テラスタル“しない”メッシュを指定できるようにもしているとのことだ。
  translation: 在太晶化中，本体（宝可梦）部分保持原有模型不变，通过替换材质并应用法线贴图、颜色贴图和噪声纹理来表现宝石质感。不过，如果全部宝石化会不好看，因此也可以指定“不”太晶化的网格。
- original: また，テラスタル化の際にポケモンの頭上に現れるテラスタルジュエルは，表のメッシュを半透明にしつつ，裏面のメッシュを不透明にすることで，奥行きを生み，立体感を表現しているという。
  translation: 另外，太晶化时出现在宝可梦头顶的太晶宝石，通过将表面网格设为半透明、背面网格设为不透明，从而产生深度，表现出立体感。
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/018.jpg
  alt: 画像ギャラリー No.018のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/019.jpg
  alt: 画像ギャラリー No.019のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/020.jpg
  alt: 画像ギャラリー No.020のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/021.jpg
  alt: 画像ギャラリー No.021のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/022.jpg
  alt: 画像ギャラリー No.022のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- original: 続いては，主人公（人物）キャラクターに関する表現方法だ。まずは，ゲーム開始時にカスタマイズできる主人公の“メイク”をどのように表現しているのかについて。
  translation: 接下来是关于主角（人物）角色的表现方法。首先，介绍了如何表现游戏开始时可以自定义的主角“妆容”。
- original: ポケモンSVでは主人公のキャラメイクで，つり目やたれ目，目の大きさなとを選べるが，これは，Mayaのラティス機能を使って作成されている。この機能を使って目尻の上げ下げや目の大小，口の大きさや唇の厚さなどの制御を可能にしたそうだ。ただ，すべてを細かくいじれるようにすると煩雑になってしまうため，それぞれの変形値の組み合わせをプリセットとして用意したとのこと。
  translation: 在《宝可梦 朱·紫》中，主角的角色创建可以选择吊眼或垂眼、眼睛大小等，这是使用Maya的晶格功能制作的。据说利用该功能，可以控制眼角的上扬或下垂、眼睛大小、嘴巴大小和嘴唇厚度等。不过，如果让所有细节都可调会变得很复杂，因此他们准备了各种变形值的组合作为预设。
- original: 一方で，まゆげは基本的にテクスチャで描写しているが，先端をアルファで階層を持たせることによって，まゆげの長さにバリエーションをつけているという。
  translation: 另一方面，眉毛基本上是用纹理来表现的，但通过给眉梢的alpha赋予层次，来为眉毛的长度增加变化。
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/023.jpg
  alt: 画像ギャラリー No.023のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/024.jpg
  alt: 画像ギャラリー No.024のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/025.jpg
  alt: 画像ギャラリー No.025のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/026.jpg
  alt: 画像ギャラリー No.026のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/027.jpg
  alt: 画像ギャラリー No.027のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- original: なお，表情は顔を五つのパーツに分けたモーフターゲットとして作成。ラインタイムではこれを最初に適応し，次に先程のラティス（メイク）の反映を行うことで，実際のキャラクターの顔形状が実現されているそうだ。
  translation: 此外，表情是将脸分成五个部分作为变形目标来制作的。据说在运行时，首先应用这个，然后反映刚才的晶格（化妆），从而实现实际角色的脸部形状。
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/028.jpg
  alt: 画像ギャラリー No.028のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/029.jpg
  alt: 画像ギャラリー No.029のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/030.jpg
  alt: 画像ギャラリー No.030のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- original: また，肌の表現については，偽装の法線を作成し，素の法線とブレンドしている。そして，顔とカメラの角度，光の方向などさまざまなシチュエーションで，どの割合が一番見栄えが良いのかを調整したり，スペキュラ（光の反射）をなだらかに抑えたりと，さまざまな試行錯誤を繰り返し，ルックコンセプトに見合う出来に仕上げることができたという。
  translation: 另外，关于皮肤的表现，制作了伪装的法线，并与原本的法线进行混合。然后，在脸与相机的角度、光线方向等各种情境下，调整哪种比例看起来最好，或者缓和抑制高光（光的反射）等，反复进行了各种试错，最终达到了符合视觉概念的成品。
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/031.jpg
  alt: 画像ギャラリー No.031のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/032.jpg
  alt: 画像ギャラリー No.032のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/033.jpg
  alt: 画像ギャラリー No.033のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/034.jpg
  alt: 画像ギャラリー No.034のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- original: 最後に，パルデア地方の世界を作り上げる表現についての解説も行われた。
  translation: 最后，还进行了关于构建帕底亚地区世界的表现方式的解说。
- original: まずは大地（マップ）の作り方だ。パルデア地方の大地は，Mayaのメッシュを元にHoudiniでディテールを追加し，HightMapや質感を選択したり，草花を生やすためのMaskを出力したとのこと。また，それだけでは表現しきれないので，Houdiniでプロシージャルモデリングした崖や岩などを後から配置することで，地形を整えていったそうだ。
  translation: 首先是大地（地图）的制作方法。帕底亚地区的大地，是以Maya的网格为基础，在Houdini中添加细节，选择HightMap和质感，并输出用于生长花草的Mask。此外，仅靠这些无法完全表现，因此通过Houdini程序化建模的悬崖和岩石等后续配置，来调整地形。
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/035.jpg
  alt: 画像ギャラリー No.035のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/036.jpg
  alt: 画像ギャラリー No.036のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/037.jpg
  alt: 画像ギャラリー No.037のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/038.jpg
  alt: 画像ギャラリー No.038のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/039.jpg
  alt: 画像ギャラリー No.039のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- original: 続いて海，川といった水辺の表現について。こちらは頂点アニメーションの動き，フローマップによる流れ，水深に応じた透明度の変化，スクリーンスペースの屈折表現を組み合わせ，基本的な処理を行っているという。さらに，波打ち際の白波を表現するため専用モデルを用意し，陸地に近いほど大きく変化するようにすることで“波打ってる感”を強調している。
  translation: 接着是关于海、河等水边的表现。这里结合了顶点动画的运动、基于流图的流动、根据水深变化的透明度、屏幕空间的折射表现，进行基本处理。此外，为了表现拍岸的白浪，准备了专用模型，通过让越靠近陆地变化越大，来强调“波浪拍打感”。
- original: スタッフから「ここ頑張ってるのでぜひ紹介してください」と言われたそう
  translation: 据说工作人员说“这里我们很努力，请务必介绍一下”
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/040.jpg
  alt: 画像ギャラリー No.040のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/041.jpg
  alt: 画像ギャラリー No.041のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/042.jpg
  alt: 画像ギャラリー No.042のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- original: そして空は，水平線にグラデーションをのせるため，Precomputed Atmospheric Scatteringなどの先行技術をベースに表現。また，雲の表現として，モデリングした雲に6方向からライトを当てた結果を2枚のテクスチャにベイクし．実際の世界の光情報をもとに描画色を計算しているとのことだ。
  translation: 然后天空，为了给地平线添加渐变，基于Precomputed Atmospheric Scattering等先行技术进行表现。此外，作为云的表现，将建模的云从6个方向打光的结果烘焙到两张纹理中，并根据实际世界的光信息计算渲染颜色。
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/043.jpg
  alt: 画像ギャラリー No.043のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/044.jpg
  alt: 画像ギャラリー No.044のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/045.jpg
  alt: 画像ギャラリー No.045のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- original: 屋内はシンプルにライトマップで表現
  translation: 室内简单地用光照贴图表现
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/046.jpg
  alt: 画像ギャラリー No.046のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/047.jpg
  alt: 画像ギャラリー No.047のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- original: 以上が「【ポケットモンスター スカーレット・バイオレット】 パルデア地方を描き出す――見た目の仕組みを徹底解説！」の内容だ。これらのさまざまな表現方法を用いることで，ポケモンSVのパルデア地方を描き出すことができたと，前澤氏は講演を締めくくった。
  translation: 以上就是“【宝可梦 朱·紫】描绘帕底亚地区——彻底解说外观机制！”的内容。前泽在演讲最后总结道，通过运用这些多样的表现手法，才得以描绘出宝可梦 朱·紫的帕底亚地区。
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/048.jpg
  alt: 画像ギャラリー No.048のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/049.jpg
  alt: 画像ギャラリー No.049のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/050.jpg
  alt: 画像ギャラリー No.050のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/051.jpg
  alt: 画像ギャラリー No.051のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- type: image
  image: /assets/img/interviews/2023-08-25-interview-cedec-2023-paldea-rendering-pipeline-maeza/052.jpg
  alt: 画像ギャラリー No.052のサムネイル画像 / ［CEDEC 2023］「ポケモンSV」はリアルな世界を目指していた。「パルデア地方を描き出す――見た目の仕組みを徹底解説！」レポート
- original: 「ポケットモンスター スカーレット・バイオレット」公式サイト
  translation: “宝可梦 朱·紫”官方网站
- original: 4Gamerの「CEDEC 2023」記事一覧
  translation: 4Gamer的“CEDEC 2023”文章一览
era: 2019–2026 · Expansion / 极巨化与开放世界
toc: true
toc_sticky: true
---
