---
layout: interview-editorial
archive_type: interview_translation
title: 电Fami Nico Gamer（電ファミニコゲーマー） 2026：Game Freak谈《宝可梦传说 Z-A》密阿雷市渲染技术
display_title: 密阿雷市的渲染技术
dek: Game Freak在CEDEC2026讲解《宝可梦传说 Z-A》如何渲染密阿雷市。
original_title: 「1000種類を超えるポケモン＋人間」という圧倒的物量に対応するために開発された「ポケリグ」とは？【CEDEC2026】
date: '2026-07-23'
era_skin: '2026'
categories:
- 访谈翻译
- 翻译
- 访谈整理
tags:
- 访谈
- Game Freak
- 電ファミニコゲーマー
- CEDEC 2026
- Pokémon LEGENDS Z-A
- 前泽圭一
- 描画技术
- 技术专题
publication: 电Fami Nico Gamer（2026-07-23）
source_kind: lecture_report
interviewer: 電ファミ
interviewee: Alfredo Spadafina、前泽圭一、赤木达也
translator: PokeAmice（DeepSeek 初译）
original_lang: ja
translation_lang: zh-CN
source:
  title: 「1000種類を超えるポケモン＋人間」という圧倒的物量に対応するために開発された「ポケリグ」とは？【CEDEC2026】
  url: https://news.denfaminicogamer.jp/kikakuthetower/2607233k
  language: ja
  source_type: media_interview
original_link: https://news.denfaminicogamer.jp/kikakuthetower/2607233k
summary: Game Freak在CEDEC2026介绍《宝可梦传说 Z-A》的渲染技术，包括城市批量绘制与剔除、天空水面与远景阴影表现、宝可梦绑定与角色绘制，以及对Nintendo Switch2的支持与两版本差异处理。
entities:
  people:
  - Alfredo Spadafina
  - 前泽圭一
  - 赤木达也
  works:
  - Pokémon LEGENDS Z-A
workflow:
  fetch: live
  translation: deepseek-chat
  proofreading: pending
  published: draft
parallel_items:
- original: 『ポケットモンスター X・Y』（以下、 X・Y）や『Pokémon LEGENDS Z-A』（以下、Z-A）の舞台となっている「ミアレシティ」。『X・Y』最大の都市として登場したこの街は、『Z-A』でメガシンカのような変貌をとげた。
  translation: 《宝可梦 X·Y》（以下简称 X・Y）与《Pokémon LEGENDS Z-A》（以下简称 Z-A）的舞台都是“密阿雷市”。这座在《X・Y》中作为最大都市登场的城市，在《Z-A》中经历了类似超级进化般的蜕变。
- original: 果たして開発チームは、前作で描かれた大自然とは異なる「建物ばかりの都市空間」を、どのように表現したのであろうか？
  translation: 那么，开发团队究竟是如何表现与前作所描绘的大自然不同的“尽是建筑的城市空间”的呢？
- original: 国内最大級のゲームカンファレンス「CEDEC2026」のセッション「ミアレシティがメガシンカ!? 『Pokémon LEGENDS Z-A』の描画技術」では株式会社ゲームフリークの前泽圭一氏、スパダフィーナ・アルフレド氏、赤木達也氏の3名により『Z-A』の描画技術について語られた。
  translation: 在国内最大级别的游戏会议“CEDEC2026”的讲座“密阿雷市超级进化!? 《Pokémon LEGENDS Z-A》的渲染技术”中，株式会社GAME FREAK的前泽圭一、斯帕达菲娜·阿尔弗雷多、赤木达也三人讲述了《Z-A》的渲染技术。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-denfami-2026-cedec-pokerig/001.jpg
  alt: 「1000種類を超えるポケモン＋人間」という圧倒的物量に対応するために開発された「ポケリグ」とは？【CEDEC2026】_001
- original: 本稿ではそのレポートをお届けする。
  translation: 本文将为各位带来该讲座的报道。
- type: heading
  level: 2
  original: 都市を効率的に描画する
  translation: 高效地渲染城市
- original: スパダフィーナ氏は、「同じデザインの建物や物がたくさん立ち並び、さらに物陰に隠れて見えない部分も多い」ことがミアレシティの特徴であると語る。
  translation: 斯帕达菲娜表示，密阿雷市的特征在于“相同设计的建筑和物件大量林立，而且被遮挡而看不见的部分也很多”。
- original: 効率的な描画には、同じ形の3Dモデルを一括で大量表示する「InstancedDraw」と画面に映らないオブジェクトの描画を省き最適化する「カリング」が重要だとした。
  translation: 他指出，要实现高效渲染，将相同形状的3D模型批量大量显示的“InstancedDraw”，以及省略画面中不显示的对象绘制以进行优化的“剔除（Culling）”十分重要。
- original: 『Z-A』は、「InstancedDraw」をもっとも活用したタイトルという。
  translation: 据说《Z-A》是运用“InstancedDraw”最多的作品。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-denfami-2026-cedec-pokerig/002.jpg
  alt: 「1000種類を超えるポケモン＋人間」という圧倒的物量に対応するために開発された「ポケリグ」とは？【CEDEC2026】_002
- original: 本作では2種類のカリングが用いられ、視野外をカリングするフラスタムカリングの実演と、モデルにより処理方法が異なると紹介された。
  translation: 本作采用了两种剔除，讲座中演示了剔除视野之外的视锥体剔除，并介绍了不同模型的处理方法有所不同。
- original: 遮蔽物をカリングするオクルージョンカリングでは、「DeapthPrePass」や「Hierarchical-Z カリング」という描画最適化技術を採用し、モデルによって異なる処理をしたという。
  translation: 在剔除遮挡物的遮挡剔除中，采用了“DeapthPrePass”和“Hierarchical-Z 剔除”这类渲染优化技术，并根据模型采用了不同的处理。
- original: また、動くキャラクターは、余裕のある描画範囲を設定したとのこと。
  translation: 此外，对于会动的角色，据说设置了留有余地的绘制范围。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-denfami-2026-cedec-pokerig/003.jpg
  alt: 「1000種類を超えるポケモン＋人間」という圧倒的物量に対応するために開発された「ポケリグ」とは？【CEDEC2026】_003
- original: 『Z-A』では、ライトにもカリングを導入している。効率アップのため無駄な計算を省く仕組みを作ったと、スパダフィーナ氏は語った。
  translation: 在《Z-A》中，光照也引入了剔除。斯帕达菲娜表示，为提高效率，他们构建了省去无用计算的机制。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-denfami-2026-cedec-pokerig/004.jpg
  alt: 「1000種類を超えるポケモン＋人間」という圧倒的物量に対応するために開発された「ポケリグ」とは？【CEDEC2026】_004
- type: heading
  level: 2
  original: 都市の景観を表現するために
  translation: 为了表现城市景观
- original: 時間帯や天候で変わる空は、天球モデルと空シェーダーを使って表現したという。
  translation: 随时间段和天气变化的天空，据说是用天球模型和天空着色器来表现的。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-denfami-2026-cedec-pokerig/005.jpg
  alt: 「1000種類を超えるポケモン＋人間」という圧倒的物量に対応するために開発された「ポケリグ」とは？【CEDEC2026】_005
- original: より自然な雲のための工夫をし、夕焼けの改善のため大気散乱の演算としてMie散乱を導入したとのこと。
  translation: 据说他们为让云更自然下了功夫，并为改善晚霞，作为大气散射的运算引入了米氏散射。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-denfami-2026-cedec-pokerig/006.jpg
  alt: 「1000種類を超えるポケモン＋人間」という圧倒的物量に対応するために開発された「ポケリグ」とは？【CEDEC2026】_006
- original: フローマップテクスチャで水面を表現し、水面の反射には、負荷の大きさから、多く用いられる反射の計算ソフト、SSR（Screen Space Reflections）ではなく、SSPR（Screen Space Planar Reflections）を採用したという。
  translation: 水面用流图纹理来表现，而水面反射由于负荷较大，据说没有采用常用的反射计算方案SSR（屏幕空间反射），而是采用了SSPR（屏幕空间平面反射）。
- original: SSPRは低負荷だが、水面の高さを固定する必要があり、テクスチャを3つに絞って実装したという。
  translation: SSPR负荷虽低，但需要固定水面的高度，据说实现时将纹理缩减到了3张。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-denfami-2026-cedec-pokerig/007.jpg
  alt: 「1000種類を超えるポケモン＋人間」という圧倒的物量に対応するために開発された「ポケリグ」とは？【CEDEC2026】_007
- original: 『Z-A』では遠くの影の表現も求められた。影の演算ソフトCSMは遠くなると負荷が跳ね上がるため、遠景には「ベイク影」を用いた。
  translation: 在《Z-A》中，还需要表现远处的影子。影子的运算方案CSM在距离变远时负荷会骤增，因此远景采用了“烘焙阴影”。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-denfami-2026-cedec-pokerig/008.jpg
  alt: 「1000種類を超えるポケモン＋人間」という圧倒的物量に対応するために開発された「ポケリグ」とは？【CEDEC2026】_008
- original: 4方向の太陽の影を計算した結果をあらかじめ保存（ベイク）し、時間帯ごとに混ぜて影を表現した。夜は光源が太陽から月へ変化するため、夜用のテクスチャを別個作成したとのこと。
  translation: 他们预先保存（烘焙）了计算4个方向太阳阴影的结果，并按时间段混合来表现阴影。据说夜间光源会从太阳变为月亮，因此另外制作了夜间专用的纹理。
- original: また、ミアレシティの半分近くを覆ってしまうプリズムタワーの影は除外したそうだ。
  translation: 此外，据说覆盖了密阿雷市近一半的棱镜塔的阴影被排除在外。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-denfami-2026-cedec-pokerig/009.jpg
  alt: 「1000種類を超えるポケモン＋人間」という圧倒的物量に対応するために開発された「ポケリグ」とは？【CEDEC2026】_009
- original: そして、ベイク影によって発生した不自然な点は緩和措置をし、対処の難しい問題は許容したとのこと。
  translation: 此外，对于因烘焙阴影而产生的不自然之处采取了缓解措施，而难以处理的问题则予以容许。
- type: image
  image: /assets/img/interviews/2026-07-23-interview-denfami-2026-cedec-pokerig/010.jpg
  alt: 「1000種類を超えるポケモン＋人間」という圧倒的物量に対応するために開発された「ポケリグ」とは？【CEDEC2026】_010
- original: 『Z-A』は街灯にもこだわり、灯りによって表現方法を変え、スポットライトが円錐モデルだと気づかせない様々な処理をしたと、スパダフィーナ氏は語った。
  translation: 斯帕达菲娜表示，《Z-A》连街灯也十分讲究，会根据灯光改变表现手法，并做了各种处理，让人察觉不到聚光灯是圆锥模型。
- type: heading
  level: 2
  original: キャラクターの描画と「ポケリグ」
  translation: 角色的绘制与「宝可梦绑定」
- original: 今作のキャラはディファードとフォワードを用いて時間帯ごとに表現し、メガシンカのエフェクトは、ポケモンのサイズごとに設定したとスパダフィーナ氏は語った。
  translation: 斯帕达菲娜表示，本作的角色使用延迟渲染与前向渲染按时间段分别表现，超级进化的特效则按宝可梦的体型分别进行了设置。
- original: 続いて「ポケリグ」の取り組みが紹介された。ポケモンの最大の課題は「物量」であり、この解決策が「ポケリグ」だという。
  translation: 接着介绍了「宝可梦绑定」的相关举措。宝可梦最大的课题是「物量」，而解决这一问题的方案就是「宝可梦绑定」。
- original: 「ポケリグ」には、リグ（骨組み）を知らない人でも使えるシステムや、効率的にデータ再利用が可能なモーションリターゲットがあるという。
  translation: 据说「宝可梦绑定」包含即使不懂绑定（骨骼结构）的人也能使用的系统，以及能够高效复用数据的动作重定向功能。
- original: ポケリグは段階的に導入され、本作では人物への対応が大きなポイントであり、大量のデータを扱うため、可能な限り共通フローを用いる方針を掲げたとのこと。
  translation: 宝可梦绑定是分阶段引入的，在本作中对应人物是一大重点，由于要处理大量数据，因此提出了尽可能采用共通流程的方针。
- original: 人物の作成には服と顔それぞれのリグを統合し、モーションはポケモンのリターゲットの派生で対応したと赤木氏は語った。過去作からのリターゲットも共通フローで対応することでスムーズに処理ができたという。
  translation: 赤木表示，人物的制作整合了服装与脸部各自的绑定，动作则通过宝可梦重定向的派生方式来对应。据说来自过去作品的重定向也通过共通流程处理，从而得以顺畅完成。
- original: 赤木氏は、全ポケモンのポケリグ化が目標と語った。
  translation: 赤木表示，目标是将所有宝可梦都实现宝可梦绑定化。
- type: heading
  level: 2
  original: Nintendo Switch2への対応
  translation: 对Nintendo Switch2的支持
- original: 『Z-A』は、Nintendo Switch版とNintendo Switch2版が発売されたが、開発は新ハード発表前から進んでいた。このときの課題として、「情報開示者が限られている」「差別化」の二点を前澤氏は挙げた。
  translation: 《Z-A》发售了Nintendo Switch版和Nintendo Switch2版，但开发在新硬件发布前就已经推进。前泽氏列举了此时的两个课题：“信息知悉者有限”和“差异化”。
- original: 作業は施錠した会議室で進められ、情報は開示者のみのSlackに集約していたが、「こういう事態に備えた管理者の整備が大切だ」と前澤氏は知見を述べた。
  translation: 作业在上了锁的会议室中进行，信息集中在仅限知悉者加入的Slack里，但前泽氏表达了见解：“为应对这种情况，管理者的整备很重要。”
- original: 毎日進むNintendo Switch版の開発に少数で対応するための、Nintendo Switch版を自動的にNintendo Switch2版に変換する環境が紹介された。
  translation: 为了以少数人应对每天都在推进的Nintendo Switch版开发，介绍了将Nintendo Switch版自动转换为Nintendo Switch2版的环境。
- original: 高解像度マスターデータの実装処理を変えることで、2つのバージョンを差別化し、60fpsでも大きな問題は起きなかったため、発生したバグを消す形で開発したと前澤氏は語った。
  translation: 前泽氏表示，通过改变高分辨率主数据的实现处理，使两个版本形成差异，即使60fps也没有出现大问题，因此以消除已产生bug的形式进行了开发。
- original: 本講演では、ミアレシティを中心に、ポケモン世界の構築方法が紹介された。
  translation: 本演讲以密阿雷市为中心，介绍了宝可梦世界的构建方法。
- original: ミアレシティがどのようにメガシンカしたのか気になる方は、『Z-A』をプレイしてみてはいかがだろうか。
  translation: 想知道密阿雷市是如何超级进化的读者，不妨玩一玩《Z-A》。
---
