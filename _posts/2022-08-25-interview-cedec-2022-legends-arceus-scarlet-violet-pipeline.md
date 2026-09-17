---
layout: interview-editorial
archive_type: interview_translation
title: 电Fami Nico Gamer 2022：GAME FREAK前泽圭一谈《阿尔宙斯》与《朱·紫》的宝可梦模型共通化
display_title: 两款宝可梦同时开发的模型共通化
dek: GAME FREAK的CG技术总监前泽圭一在CEDEC 2022讲解《阿尔宙斯》与《朱·紫》同时开发时的模型制作环境。
original_title: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？ 共通化されたポケモンモデルにタイトルごとの個性をつけていく【CEDEC 2022】
date: '2022-08-25'
era_skin: '2026'
categories:
- 访谈翻译
- 翻译
- 访谈整理
tags:
- 访谈
- Game Freak
- 電ファミニコゲーマー
- CEDEC 2022
- 宝可梦传说 阿尔宙斯
- 宝可梦 朱·紫
- 前泽圭一
- 模型制作
- 技术专题
publication: 电Fami Nico Gamer（2022-08-25）
source_kind: lecture_report
author: 柳本マリエ
interviewer: 柳本マリエ
interviewee: 前泽圭一
translator: PokeAmice（DeepSeek 初译）
original_lang: ja
translation_lang: zh-CN
source:
  title: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？ 共通化されたポケモンモデルにタイトルごとの個性をつけていく【CEDEC 2022】
  url: https://news.denfaminicogamer.jp/kikakuthetower/220825t
  language: ja
  source_type: media_interview
original_link: https://news.denfaminicogamer.jp/kikakuthetower/220825t
summary: CEDEC 2022讲座中，GAME FREAK的CG技术总监前泽圭一介绍《宝可梦传说 阿尔宙斯》与《宝可梦 朱·紫》同时开发时对宝可梦模型制作环境与流程的重新审视，包括交付规格共通化、图形库更新、动作复制与动态捕捉的引入。
entities:
  people:
  - 前泽圭一
  works:
  - 宝可梦传说 阿尔宙斯
  - 宝可梦 朱·紫
  - 宝可梦 剑·盾
workflow:
  fetch: live
  translation: deepseek-chat
  proofreading: pending
  published: draft
parallel_items:
- original: 8月23日から25日の3日間にわたり、ゲーム開発者向けカンファレンス「CEDEC2022」が今年もオンラインで開催されている。
  translation: 8月23日至25日的3天期间，面向游戏开发者的会议“CEDEC2022”今年也在线上举办。
- original: 今回は3日目に行われたセッション『Pokémon LEGENDS アルセウス』（以下、『アルセウス』）と『ポケットモンスター スカーレット・バイオレット』（以下、『スカーレット・バイオレット』）において、「ポケモン2つを同時に作る、ポケモンモデル制作環境」についてレポートしていく。
  translation: 本次将报道第3天举行的讲座“《宝可梦传说 阿尔宙斯》（以下简称《阿尔宙斯》）与《宝可梦 朱·紫》（以下简称《朱·紫》）”中关于“同时制作两款宝可梦的宝可梦模型制作环境”的内容。
- original: 本セッションには、株式会社ゲームフリークのCGテクノロジーディレクターである前澤圭一氏が登壇。
  translation: 本讲座由株式会社GAME FREAK的CG技术总监前泽圭一登台。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/001.jpg
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _001
- original: 『アルセウス』と『スカーレット・バイオレット』はゲーム性もルックの方向性も異なる2つのタイトル。本セッションでは同時に開発するにあたって取り組んだ、環境・フローの見直しについて語られた。
  translation: 《阿尔宙斯》与《朱·紫》是游戏性和视觉方向性都不同的两款作品。本讲座讲述了在同时开发时所做的环境与流程的重新审视。
- type: heading
  level: 2
  original: ポケモンモデルの総数が1000種を超え、限界を迎える
  translation: 宝可梦模型总数超过1000种，迎来极限
- original: 株式会社ゲームフリークはゲームソフトの企画、開発、販売を行っており、『ポケットモンスター』シリーズを開発している会社である。
  translation: 株式会社GAME FREAK从事游戏软件的企划、开发和销售，是开发《宝可梦》系列的公司。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/002.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _002
- original: 上記すべて3Dのゲームとなっているため、キャラクターとなるポケモンの「3Dモデル」が存在する。
  translation: 上述全部都是3D游戏，因此存在作为角色的宝可梦的“3D模型”。
- original: 同社におけるポケモンモデル制作の体制は下記のとおり。
  translation: 该公司宝可梦模型制作的体制如下。
- original: 本セッションでは、R&D（研究開発部）の部分を中心に解説された。R&Dにはアニメーション関係のエンジニアが集約されているという。
  translation: 本讲座以R&D（研究开发部）的部分为中心进行了解说。据说动画相关的工程师都集中在R&D。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/003.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _003
- original: 『ソード・シールド』までの仕様・環境は、タイトルごとに分かれていたとのこと。
  translation: 据说直到《剑·盾》为止的规格和环境都是按作品分开的。
- original: タイトルごとに「どのような要素が必要なのか」、「どのような表現をするのだろうか」という点をもとに仕様や環境を決め、それぞれ開発されている。
  translation: 每个作品都基于“需要哪些要素”、“要做出怎样的表现”来决定规格和环境，并分别进行开发。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/004.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _004
- original: しかしながら『赤・緑』から『ソード・シールド』まで、ポケモンモデルの総数は1000種類を超えている。タイトルごとに仕様から練り直して揃えていくのはそろそろ厳しい。それが2018年くらいのことだったという。
  translation: 然而从《红·绿》到《剑·盾》，宝可梦模型的总数已超过1000种。每个作品都从头重新梳理规格并逐一备齐，已经逐渐变得困难。据说这大约是在2018年前后的事。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/005.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _005
- original: 1タイトルでも厳しいという状況の中で、ルックの異なる2つのタイトル『アルセウス』と『スカーレット・バイオレット』が2022年に発売されることとなり、いよいよ課題解決が急務となった。
  translation: 在仅一个作品就已艰难的情况下，外观风格不同的两款作品《阿尔宙斯》与《朱·紫》将于2022年发售，解决这一课题终于成了当务之急。
- original: そこで、ポケモンモデル制作体制の環境・フローの見直しが行われることとなった。
  translation: 于是，宝可梦模型制作体制的环境与流程被重新审视。
- type: heading
  level: 2
  original: 納品仕様の共通化
  translation: 交付规格的共通化
- original: 環境・フローの見直しによって、納品物の共通化が行われた。
  translation: 通过重新审视环境与流程，交付物的共通化得以实现。
- original: これまでタイトルごとに納品してきたのであれば、共通の仕様・環境にすればいいのではないか、という発想だ。
  translation: 其思路是：既然此前都是按作品分别交付，那不如改为共通的规格与环境。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/006.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _006
- original: 標準マテリアル・基本骨格にて納品し、各タイトルの開発チームに引き渡す。納品後、後工程で手を加え、タイトルごとのグラフィックに整える。
  translation: 以标准材质与基本骨架进行交付，并移交给各作品的开发团队。交付后，在后续工序中加以调整，整理成符合作品风格的图形表现。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/007.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _007
- original: また、ライティングもプリセットを用意することで時間や天候に応じて変えていく。
  translation: 此外，光照也通过准备预设，来根据时间与天气进行变化。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/008.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _008
- original: このように納品することで、これまでかかっていた工数を削減することができる。
  translation: 通过以这种方式交付，可以削减此前所需的工时。
- original: 検品については、自動チェックと目視チェックの2段構えになっているとのこと。見た目や負荷をチェックしていく。
  translation: 关于检查，据说采用自动检查和目视检查的双重体制。会检查外观和负载。
- original: 足の付け根や耳の付け根などはポリゴンが重なり負荷がかかりやすく、必要であれば削減しているという。
  translation: 据说脚根和耳根等部位多边形容易重叠并产生负载，必要时会进行削减。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/009.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _009
- type: heading
  level: 2
  original: グラフィックスライブラリの一新
  translation: 图形库的全面更新
- original: では、共通マテリアル・基本骨格を引き渡したあとの「後工程」ではどのようなことを行っているのか。
  translation: 那么，在交付共通材质和基本骨架之后的“后续工序”中，会进行哪些工作呢？
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/010.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _010
- original: すべてのポケモンに一括して設定するものと、各ポケモンに個別で調整するものがあるとのこと。
  translation: 据说既有对所有宝可梦统一设置的项目，也有对每只宝可梦单独调整的项目。
- original: たとえば、後光の出方、食べ物の配置、ZLで注目したときにどこを見るか、などはゲームのルールに基づいているためタイトル側で設定していく。
  translation: 例如，光晕的出现方式、食物的配置、用ZL键注目时看向哪里等，因为这些都基于游戏规则，所以会由各作品侧进行设置。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/011.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _011
- original: そのほか、IK（インバース・キネマティクス）などの動的な処理やルックなどもタイトル依存で後付け設定をする。
  translation: 此外，IK（反向运动学）等动态处理和外观等也依赖于作品，会进行追加设置。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/012.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _012
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/013.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _013
- original: 下記画像の左は納品データのピカチュウ、右は『アルセウス』のピカチュウである。人物や背景はタイトルに合わせて制作されているため、もとの納品データとタイトルのイメージを埋めるため色合わせや質感の調整を行っている。
  translation: 下图中左侧是交付数据的皮卡丘，右侧是《阿尔宙斯》的皮卡丘。由于人物和背景是根据作品制作的，为了填补原始交付数据与作品印象之间的差距，进行了颜色匹配和质感调整。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/014.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _014
- original: 版画風の『アルセウス』では淡い色味、リアル寄りの『スカーレット・バイオレット』ではハッキリとした色味になっている。
  translation: 版画风格的《阿尔宙斯》采用淡雅色调，偏写实的《朱／紫》则采用鲜明的色调。
- original: また、『スカーレット・バイオレット』のピカチュウはポケモン史上最高のふさふさ感を出しているという。ピカチュウファンにはたまらないのではないだろうか。
  translation: 此外，据说《朱／紫》的皮卡丘展现了宝可梦史上最蓬松的质感。皮卡丘的粉丝们想必会爱不释手吧。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/015.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _017
- original: そのほかにも、ジェル状の部位や発光粒子、新しい「テラスタイル」など『スカーレット・バイオレット』ではさまざまな質感が施されている。
  translation: 除此之外，凝胶状的部位、发光粒子，以及新的「太晶属性」等，《朱／紫》中还加入了各种各样的质感表现。
  note: 太晶属性（テラスタイル）是《宝可梦 朱／紫》中宝可梦太晶化后呈现的属性类型。
- type: heading
  level: 2
  original: アニメーションも「モーションコピー」で共通化する
  translation: 动画也通过「动作复制」实现共通化
- original: アニメーションについても、本当に作るべきものが精査された。というのも、体型の似たポケモンが複数存在しているからだ。すると、「ベースの動きは共通化できるのではないか」という仮説が生まれる。
  translation: 关于动画，也重新审视了真正需要制作的部分。这是因为存在多只体型相似的宝可梦。于是便产生了「基础动作是否可以共通化」的假设。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/016.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _020
- original: まずは「人型」、「犬猫型」、「ヘビ型」、「ドラゴン型」などポケモンの体型分類を行う。そこで分類されたポケモン同士を「モーションコピー」してみると、共通化ができるという。
  translation: 首先按「人型」「犬猫型」「蛇型」「龙型」等对宝可梦的体型进行分类。将这样分类出的宝可梦之间进行「动作复制」，就可以实现共通化。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/017.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _021
- original: 基本的には骨と骨をマッピングして同じ部位に該当するものをコピーするシンプルなものとなっている。
  translation: 基本上是将骨骼与骨骼进行映射，把对应相同部位的部分复制过去的简单做法。
- original: 大きさや骨構造が異なっていても、似ていれば対応ができるとのこと。
  translation: 即便大小和骨骼结构不同，只要相似就能对应。
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/018.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _022
- type: image
  image: /assets/img/interviews/2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline/019.png
  alt: 『アルセウス』と『スカーレット・バイオレット』を同時に作るポケモンモデルの制作環境とは？  _023
- original: 実際にモーションコピーを使った例は下記のとおり。ドラゴン型の歩き方やしっぽの動かし方、ヘビ型のうねうね感などがコピーできる。
  translation: 实际使用动作复制的例子如下。龙型的走路方式和尾巴的摆动方式、蛇型那种蜿蜒扭动的感觉等都可以复制。
- original: このようにポケモンからポケモンへモーションの流し込みをすることで工数を減らすことができる。
  translation: 像这样把动作从一只宝可梦套用到另一只宝可梦上，就能减少工时。
- original: しかし、もととなるポケモンがいない場合はコピーが使えない。
  translation: 但是，如果没有可作为来源的宝可梦，就无法使用复制。
- original: その場合は社内のモーションキャプチャを導入しているという。撮影したデータをポケモンに流しこむことでイメージをつかみやすくなり、工数を減らすことができるとのこと。
  translation: 这种情况下则引入公司内部的动态捕捉。将拍摄的数据套用到宝可梦上，就更容易把握整体感觉，从而减少工时。
- original: こうした仕組みの導入によってアニメーションの効率化を図ることに成功している。
  translation: 通过引入这样的机制，成功实现了动画的效率化。
- original: ポケモン2タイトルを同時に作るため、納品物を共通化するという抜本的な見直しが行われていた。
  translation: 为了同时制作两款宝可梦作品，进行了将交付物共通化的根本性调整。
- original: 個人的には、これまでのポケモンモデル1000種類以上がタイトルごとに作られていたことにも驚いている。
  translation: 就我个人而言，至今为止1000多种宝可梦模型都是按作品分别制作的，这一点也让我感到惊讶。
- original: 共通化の仕組みが導入されたことにより工数を減らすことができたということは、今後の『ポケモン』シリーズの発売スパン短縮にも繋がるかもしれない。 もしそうであればファンにとっては朗報となるだろう。
  translation: 通过引入共通化机制减少了工作量，这或许也会关系到今后《宝可梦》系列发售间隔的缩短。如果真是这样，对粉丝来说将是个好消息。
- original: そして、ポケモン史上最高のふさふさ感を出したという『バイオレット・スカーレット』のピカチュウが楽しみでならない。
  translation: 而且，据说展现了宝可梦史上最强蓬松感的《朱・紫》皮卡丘，实在令人期待。
era: 2019–2026 · Expansion / 极巨化与开放世界
---
