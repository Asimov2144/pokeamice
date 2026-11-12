---
archive_type: interview_translation
layout: interview-editorial
title: Fami通 CEDEC 2022 报道：两款宝可梦作品并行开发的模型与动画制作流程
original_title: 『ポケモン スカーレット・バイオレット』のピカチュウはシリーズ史上最高のふさふさ感を実現。『ポケモンレジェンズ アルセウス』との同時制作における制作環境を解説【CEDEC2022】
date: 2022-08-27 12:00:00 +0900
era_skin: 2022
source_url: https://www.famitsu.com/news/202208/27273621.html
source:
  title: 『ポケモン スカーレット・バイオレット』のピカチュウはシリーズ史上最高のふさふさ感を実現。『ポケモンレジェンズ アルセウス』との同時制作における制作環境を解説【CEDEC2022】
  url: https://www.famitsu.com/news/202208/27273621.html
  language: ja
  source_type: web_article
original_language: ja
categories:
- 访谈
- 技术解析
tags:
- 宝可梦 朱·紫
- 宝可梦传说 阿尔宙斯
- CEDEC
- Game Freak
- 3D建模
- 着色器
- 皮卡丘
- 开放世界
author: ファミ通.com 編集部
interviewee: 前泽圭一（GAME FREAK 研究开发部 CG 技术总监）
cast:
- id: maezawa
  name: 前泽圭一
  role: GAME FREAK 研究开发部 CG 技术总监
parallel_items:
- type: paragraph
  speaker: 原文作者
  original: 2022年8月23日～25日の期間に開催された、日本最大のコンピュータエンターテインメント開発者向けカンファレンス“CEDEC 2022”。本稿では、8月25日に行われたセッション“【アルセウス＋スカーレット・バイオレット】ポケモン2つを同時に作る、ポケモンモデル制作環境”の模様をお届け。
  translation: 日本规模最大的计算机娱乐开发者大会 CEDEC 2022 于8月23日至25日举行。本文介绍8月25日的讲演“【阿尔宙斯＋朱／紫】同时开发两款宝可梦游戏：宝可梦模型的制作环境”。
  role: commentary
- type: heading
  level: 2
  original: 1年で2タイトルを制作するため、1000種類以上のポケモンモデルを共通化
  translation: 为在一年内制作两款游戏，让一千多种宝可梦模型能够共用
- type: paragraph
  speaker: 原文作者
  original: セッションではまず、ポケモンのモデルの制作体制について紹介。前澤氏の所属するR＆D（研究開発部）では、ゲームエンジンやグラフィックの表現を実現するためのシステムを開発し、各タイトルの開発チームに提供する。その際、ゲームフリーク内部や外部の協力会社にある納品チームのチェックが行われている。
  translation: 讲演首先介绍了宝可梦模型的制作体制。前泽所在的研发部（R&D）负责开发游戏引擎、图形表现等所需的系统，提供给各作品的开发团队。在这一流程中，GAME FREAK 内部及外部合作公司的素材交付团队也会进行检查。
  role: commentary
- type: paragraph
  speaker: 原文作者
  original: なお、R＆Dにはグラフィック、アニメーション関係のエンジニアが集約している。
  translation: 图形和动画方面的工程师也集中在研发部。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/001.jpg
  alt: PH01
  caption: GAME FREAK 研究开发部 CG 技术总监前泽圭一。
  caption_original: ゲームフリーク 研究開発部 CGテクノロジーディレクター・前澤圭一氏。
- type: paragraph
  speaker: 原文作者
  original: 本セッションでは、『ポケットモンスター』シリーズを開発するゲームフリークの研究開発部 CGテクノロジーディレクターの前澤圭一氏が登壇。
  translation: 主讲人是《宝可梦》系列开发商 GAME FREAK 研发部的 CG 技术总监前泽圭一。
  role: commentary
- type: paragraph
  speaker: 原文作者
  original: 2022年1月28日に発売された『Pokémon LEGENDS アルセウス』（以下、『アルセウス』）と、同じく2022年11月18日に発売予定の『ポケットモンスター スカーレット・バイオレット』（以下、『スカーレット・バイオレット』）、ゲーム性も見た目の方向性も異なるふたつのタイトルを同時に開発するにあたって行った“環境・フローの見直し”について解説された。
  translation: 《宝可梦传说 阿尔宙斯》（以下简称《阿尔宙斯》）已于2022年1月28日发售，《宝可梦 朱／紫》（以下简称《朱／紫》）则计划于同年11月18日发售。为了同时开发这两款玩法和视觉风格各不相同的作品，团队重新调整了制作环境与流程，本次讲演介绍的就是这些调整。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/002.jpg
  alt: PH02
- type: paragraph
  speaker: 原文作者
  original: 『ポケットモンスター ソード・シールド』（以下、『ソード・シールド』）までは、各タイトルごとの仕様・環境に合わせて、「どのような要素が必要か」、「どのような表現をするのか」という点をもとにシステムを開発し、提供していたという。
  translation: 截至《宝可梦 剑／盾》（以下简称《剑／盾》），团队一直根据每款作品各自的规格和制作环境，先确定需要哪些要素、希望实现怎样的表现，再开发并提供相应的系统。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/003.jpg
  alt: PH03
- type: paragraph
  speaker: 原文作者
  original: しかし、初代の『ポケットモンスター 赤・緑』から近年の『ソード・シールド』までのポケモンモデルの総数は1000種類を超えている。これを各タイトルごとに仕様から練り直して揃えていくのは、そろそろ厳しいものがあったという。それは、2018年ごろから感じていたそうだ。
  translation: 然而，涵盖初代《宝可梦 红／绿》至《剑／盾》的宝可梦模型，已经超过一千种。如果每开发一款游戏，都重新考虑规格、准备整套模型，工作就越来越难以完成。据介绍，团队从2018年前后便开始感受到这一问题。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/004.jpg
  alt: PH04
- type: paragraph
  speaker: 原文作者
  original: 1タイトルでも厳しいというときに、版画テイストでアクション寄りの『アルセウス』と、リアルテイストでオープンワールド調の『スカーレット・バイオレット』、ルックの異なる2タイトルを同時制作するのは限界がある。そのため、環境・フローの見直しが行われた。
  translation: 仅制作一款游戏就已吃力，还要同时开发两款风格迥异的作品，原有做法便难以为继：《阿尔宙斯》采用版画风格，玩法偏向动作；《朱／紫》则更写实，采用开放世界的形式。为此，团队重新调整了制作环境与流程。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/005.jpg
  alt: PH05
- type: heading
  level: 2
  original: 共通の環境・仕様を提供し、後工程でタイトルに合ったポケモンモデルに
  translation: 统一制作环境与规格，再由各作品团队进行后续调整
- type: paragraph
  speaker: 原文作者
  original: 環境・フローの見直しとして最初に行われたのは“納品仕様の共通化”。これまで各タイトルごとに環境・仕様を制作してきたところの共通化を図った。この共通環境・仕様に則り、アセット制作・納品の工程を経てそれぞれのタイトル開発チームへ提供を行う。納品時には、標準マテリアル・基本骨格が設定されたものが引き渡され、各チームの後工程でタイトルごとに調整される。
  translation: 第一步是统一素材的交付规范。过去各作品使用不同的环境与规格，现在改为共用一套标准。美术素材按照这套标准制作、交付，再提供给各作品的开发团队。交付时，模型已经设好标准材质和基础骨骼，之后由各团队根据作品需求进一步调整。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/006.jpg
  alt: PH06
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/source-l_6308ecf0e74f0.jpg
  alt: CEDEC 2022 宝可梦模型制作环境讲演幻灯片
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/007.jpg
  alt: PH08
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/source-l_6308ecf0c5b82.jpg
  alt: CEDEC 2022 宝可梦模型制作环境讲演幻灯片
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/008.jpg
  alt: PH10
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/source-l_6308ecf079b54.jpg
  alt: CEDEC 2022 宝可梦模型制作环境讲演幻灯片
- type: paragraph
  speaker: 原文作者
  original: 検品は、自動チェックと目視チェックによって、見た目や負荷に問題がないかをチェック。負荷については、首の付け根や耳の付け根などはポリゴンが重なり負荷が大きくなりやすいので、軽くするために削減しているという。
  translation: 检查分为自动检查和人工目视检查，用来确认模型外观及性能开销是否存在问题。例如，颈部、耳根等位置的多边形容易重叠，增加性能负担，因此会适当减少这些部位的多边形数量。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/009.jpg
  alt: PH12
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/010.jpg
  alt: PH13
- type: paragraph
  speaker: 原文作者
  original: 続く後工程では、ポケモンのモデルに細かい調整が実施されるが、すべてのポケモンに一括して設定するものと、各ポケモンに個別で調整するものがある。たとえば『アルセウス』でいうと、後光の出かたや食事の際の食べ物の位置、ZLボタンを押して注目したときにどこを向くか、といったところはゲームのルールに紐づいているため、タイトル側で設定する。
  translation: 在后续制作阶段，团队会继续微调宝可梦模型。有些设定会统一应用到所有宝可梦，也有些需要逐只调整。例如在《阿尔宙斯》中，宝可梦周围光芒的表现、进食时食物摆放的位置，以及按下ZL键注视时的朝向，都与具体的游戏规则有关，因此由该作品的开发团队设定。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/011.jpg
  alt: PH14
- type: paragraph
  speaker: 原文作者
  original: そのほかには、IK（インバース・キネマティクス）や視線制御などの動的処理もタイトル依存のものとして後付けしていく。
  translation: IK（反向运动学）、视线控制等动态处理，也会根据各作品的需要，在后续阶段加入。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/012.jpg
  alt: PH15
- type: heading
  level: 2
  original: 各タイトルの世界観に合ったグラフィックに調整。『スカーレット・バイオレット』のピカチュウは“『ポケモン』史上最高のふさふさ感”を表現
  translation: 让画面适应各作品的世界观：《朱／紫》的皮卡丘呈现系列最蓬松的毛发质感
- type: paragraph
  speaker: 原文作者
  original: 環境・フローの見直しとして、グラフィックスライブラリも一新。各タイトルの後工程によってルックの後付けなど加工を行い、グラフィックのさらなるクオリティーアップも図れるようになった。
  translation: 作为此次流程调整的一部分，团队还更新了图形库。各作品可以在后续制作阶段添加、调整自己的视觉风格，进一步提升画面品质。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/013.jpg
  alt: PH16
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/014.jpg
  alt: PH17
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/015.jpg
  alt: PH18
- type: paragraph
  speaker: 原文作者
  original: 以下の画像では、左が納品環境のピカチュウで右は『アルセウス』のピカチュウ。納品データは共通のものだが、人物や背景などはタイトルに合わせて制作されているため、その間のイメージの差を埋めるべく、色合わせや質感の調整などが行われる。
  translation: 下图左侧是交付环境中的皮卡丘，右侧是《阿尔宙斯》中的皮卡丘。虽然交付的基础数据相同，但人物和背景会按照各作品的风格制作，因此需要调整配色和材质质感，让宝可梦与周围画面协调一致。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/016.jpg
  alt: PH19
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/017.jpg
  alt: PH20
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/018.jpg
  alt: PH21
  caption: 针对各作品进行调整，例如把三蜜蜂等虫宝可梦的翅膀改为不透明，或只让花岩怪的背面不透明。
  caption_original: ミツハニーのようなむしポケモンの羽根を不透明にしたり、ミカルゲのようなポケモンの場合は背面だけを不透明にしたりするといった、タイトルにあった調整が実施されている。
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/019.jpg
  alt: PH22
  caption: 火花和烟雾等效果通过粒子实现。
  caption_original: 火の粉や煙などを表現する際には、パーティクルで対応。
- type: paragraph
  speaker: 原文作者
  original: 各タイトルのコンセプトにあったグラフィックにするため、『アルセウス』では版画風のニュアンスを追加。また、空や水などをコンセプトに合わせた景観表現を行ったり、色調補正を行って淡い色調に加工したりしている。
  translation: 为了配合作品的视觉概念，《阿尔宙斯》加入了版画般的质感。天空、水面等景观也按照这一方向制作，并通过色调校正，形成较为淡雅的色彩。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/020.jpg
  alt: PH23
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/021.jpg
  alt: PH24
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/022.jpg
  alt: PH25
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/023.jpg
  alt: PH26
- type: paragraph
  speaker: 原文作者
  original: セッションでは、『スカーレット・バイオレット』における後工程での調整についても紹介。たとえば、ピカチュウは“『ポケモン』史上最高のふさふさ感”を表現。新ポケモン・クワッサのジェル部位、ミライドンの発光粒子、新要素“テラスタル”の質感も演出。そのほか、空・海・街並みもリアル寄りの表現となっている。
  translation: 讲演还介绍了《朱／紫》在后续制作阶段的调整。比如，皮卡丘呈现出“《宝可梦》系列至今最蓬松的毛发质感”；润水鸭的凝胶状部位、密勒顿的发光粒子，以及新要素“太晶化”的质感，也都有相应的表现。天空、海洋和街景则采用了更偏写实的风格。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/024.jpg
  alt: PH27
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/025.jpg
  alt: PH28
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/026.jpg
  alt: PH29
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/027.jpg
  alt: PH30
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/028.jpg
  alt: PH31
- type: heading
  level: 2
  original: ポケモンたちの膨大なアニメーションは、“モーションコピーツール”で共通化。ときにはモーションキャプチャーも活用
  translation: 用“动作复制工具”共用大量动画，也会采用动作捕捉
- type: paragraph
  speaker: 原文作者
  original: 『ポケモン』作品において、各ポケモンの特徴にあった動きというのも重要だが、それをひとつずつアニメーションで制作するとなると、膨大な物量となってくる。一方で、体形の似たポケモンも複数存在している。
  translation: 让每只宝可梦的动作符合自身特点很重要，但如果逐只制作所有动画，工作量会非常庞大。而宝可梦之中，也有不少体形相似的种类。
  role: commentary
- type: paragraph
  speaker: 原文作者
  original: であれば、「ベースとなる動きを共通化してから個性付けをしていけば開発の労力が減るのではないか？」という考えが生まれた。これをきっかけに、アニメーションの物量対策を実施することになる。
  translation: 于是团队想到，能不能先共用一套基础动作，再加入各自的特点，以减少开发工作？动画制作流程的调整就从这里开始。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/029.jpg
  alt: PH32
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/030.jpg
  alt: PH33
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/031.jpg
  alt: PH34
- type: paragraph
  speaker: 原文作者
  original: まずはポケモンを人型、犬猫型、ヘビ型、ドラゴン型などで体型を分類。そこからモーションを共通化するための“モーションコピーツール”が開発された。
  translation: 团队先按照体形，把宝可梦分为人形、犬猫形、蛇形、龙形等类别，再开发“动作复制工具”，让它们能够共用动作。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/032.jpg
  alt: PH35
- type: paragraph
  speaker: 原文作者
  original: “モーションコピーツール”では、基本的に骨と骨をマッピングして同じ部位に該当するものをコピー。大きさが違う場合にも補正をかけてコピーが可能。骨構造が異なる場合でも、手が2本、足が2本と構造が似ていれば、リターゲットによって対応できる。
  translation: “动作复制工具”会先建立骨骼之间的对应关系，再复制相应部位的动作。即使体形大小不同，也可以先校正再复制。即便骨骼结构不完全相同，只要都具有两条手臂、两条腿等相似结构，也能通过动画重定向来处理。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/033.jpg
  alt: PH36
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/034.jpg
  alt: PH37
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/035.jpg
  alt: PH38
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/036.jpg
  alt: PH39
  caption: 龙型宝可梦除了步态，还可以复制翅膀和尾巴的动作。
  caption_original: ドラゴン型の場合、歩きかたのほかに翼や尻尾の動きをコピーできる。
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/037.jpg
  alt: PH40
  caption: 蛇型宝可梦则可以复制蜿蜒扭动的动作。
  caption_original: ヘビ型の場合、うねうねとした動きがコピー可能だ。
- type: paragraph
  speaker: 原文作者
  original: コピーのもととなるポケモンがいない場合には、ゲームフリーク内部のモーションキャプチャーを導入。撮影したデータをそのままポケモンに流しこむことでイメージをつかむことができ、大幅な工数削減ができるそうだ。
  translation: 如果没有合适的宝可梦可以作为动作来源，团队就会使用 GAME FREAK 内部的动作捕捉设备。把捕捉到的数据导入宝可梦模型，便能快速确认动作的大致效果，据介绍，这可以大幅减少制作工时。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/038.jpg
  alt: PH41
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/039.jpg
  alt: PH42
- type: paragraph
  speaker: 原文作者
  original: 一方、課題として、リガ―（※）が不足していることが挙げられるという。これについては、“ポケリグ”を開発して構造の標準化を行うことで、アニメーション制作の効率化を図ることができたそうだ。
  translation: 另一个问题是骨骼绑定师【※】人手不足。对此，团队开发了名为“ポケリグ”的工具，将绑定结构标准化，从而提高动画制作效率。
  role: commentary
- type: note
  original: ※CGキャラクターにアニメーションを付けるための“リグ（動かす仕組み）”を設定する人。
  translation: ※骨骼绑定师：为CG角色设置“绑定”，也就是用于控制角色动画的一套结构的人员。
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/040.jpg
  alt: PH43
- type: paragraph
  speaker: 原文作者
  original: また、ランタイムでの動的制御を行う場合も。ポケモンの背骨をシミュレーションすることで、アーボのうねうねとした動きや、レントラーなどの四足歩行のポケモンの傾斜歩行を自然と行えるようにしている。
  translation: 有些动作还会在游戏运行时动态控制。例如，通过模拟宝可梦的脊柱，让阿柏蛇的蜿蜒扭动，以及伦琴猫等四足宝可梦在斜坡上行走的动作，看起来更自然。
  role: commentary
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/041.jpg
  alt: PH44
- type: image
  image: /assets/img/interviews/2022-08-27-interview-famitsu-sv-arceus-cedec2022-shader-pipeline/042.jpg
  alt: PH45
- type: paragraph
  speaker: 原文作者
  original: 共通の環境・仕様を用意することで各タイトルに合わせて制作する必要がなくなり、納品までの制作時間の短縮に成功。そして、後工程によってタイトルごとによる異なるルックとゲーム性を高い品質で実現。アニメーション制作の効率化も図られたことで、『アルセウス』と『スカーレット・バイオレット』の2タイトル同時制作が可能となった。
  translation: 统一制作环境与规格之后，团队不必再为每款作品分别制作一套基础素材，交付前的制作时间因此缩短。随后，各作品团队再进行调整，以较高品质实现各自的视觉风格和玩法需求。再加上动画制作效率的提升，团队才得以同时开发《阿尔宙斯》和《朱／紫》。
  role: commentary
- type: paragraph
  speaker: 原文作者
  original: 我々が大きな間を置かずに高品質なゲームを手にできるのは、こうした企業努力のおかげ。日々感謝しつつ楽しみたいところだ。
  translation: 我们能相隔不久就玩到高品质的游戏，背后离不开企业在这些环节上的努力。享受游戏时，也不妨记得这些付出。
  role: commentary
entities:
  works:
  - 宝可梦传说 阿尔宙斯
  - 宝可梦 朱·紫
source_kind: technical_report
summary: CEDEC 2022 讲演介绍《宝可梦传说 阿尔宙斯》与《宝可梦 朱／紫》同时开发时的制作流程：统一素材交付规范，再按各作品调整视觉风格，并利用动作复制、动作捕捉和绑定工具提高动画制作效率。
dek: GAME FREAK 介绍两款宝可梦作品并行开发时，如何共用模型素材和动画。
topics:
- "开发流程"
- "角色设计"
- "动画制作"
- "系统设计"
- "图形技术"
mentions:
  people:
  - "前泽圭一"
  works:
  - "宝可梦 红·绿"
  - "宝可梦 剑·盾"
  - "宝可梦 传说 阿尔宙斯"
---
