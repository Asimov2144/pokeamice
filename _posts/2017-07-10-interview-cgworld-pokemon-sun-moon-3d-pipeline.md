---
archive_type: interview_translation
layout: interview-editorial
title: CGWORLD 独家专访 GAME FREAK × Creatures：〈精灵宝可梦 太阳／月亮〉3D 资产构建工业管线与三社协同革新
title_ja: 『ポケットモンスター サン・ムーン』の3Dアセット制作とそれを可能にする高度な3社協業体制
date: 2017-07-10 10:00:00 +0900
era: '2016'
source:
  title: CGWORLD 独家专访 GAME FREAK × Creatures：〈精灵宝可梦 太阳／月亮〉3D 资产构建工业管线与三社协同革新
  url: https://cgworld.jp/feature/201707-cgw227GG-pokemon.html
  source_type: web_interview
source_url: https://cgworld.jp/feature/201707-cgw227GG-pokemon.html
interviewee: 海野隆雄、大森滋、氏家淳子、畠祐貴、中廣健吾、植松俊介
categories:
- developer-interviews
- official-archives
parallel_items:
- type: heading
  level: 2
  original: 『ポケットモンスター サン・ムーン』の3Dアセット制作とそれを可能にする高度な3社協業体制
  translation: 《精灵宝可梦 太阳／月亮》3D 资产制作与实现工业级突破的三社协同开发体系
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_01.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_01.jpg)
  caption: ''
- original: ニンテンドー3DSにおけるシリーズ第3弾『ポケットモンスター サン・ムーン（以下、サン・ムーン）』。本作の開発にはゲームフリーク・クリーチャーズ・ポケモンの3社が高度な連携体制を敷いている。携帯ゲーム機向けに大量のアセットを扱う分散開発と、その工夫に迫る。
  translation: 在任天堂3DS上的系列第三作《宝可梦 太阳／月亮》（以下简称《太阳／月亮》）。本作的开发由GAME FREAK、Creatures、宝可梦三家公司构建了高度协同的体制。本文将深入探讨面向便携式游戏机处理大量资产的分布式开发及其巧思。
- original: ※本記事は月刊「CGWORLD + digital video」vol. 227（2017年7月号）からの転載となります
  translation: ※本文转载自月刊《CGWORLD + digital video》vol. 227（2017年7月号）
- original: information ©2016 Pokémon. ©1995-2016 Nintendo/Creatures Inc. /GAME FREAK inc. ポケットモンスター・ポケモン・Pokémonは任天堂・クリーチャーズ・ゲームフリークの登録商標です。ニンテンドー3DSのロゴ・ニンテンドー3DSは任天堂の商標です。 ※画面は開発中のものです。また、一部画像を加工しています。
  translation: information ©2016 Pokémon. ©1995-2016 Nintendo/Creatures Inc. /GAME FREAK inc. 宝可梦・Pokémon是任天堂・Creatures・GAME FREAK的注册商标。任天堂3DS的标识・任天堂3DS是任天堂的商标。 ※画面为开发中内容。此外，部分图片经过加工。
- type: heading
  level: 2
  original: 20年以上続く人気シリーズを影で支える高度な開発体制
  translation: 支撑20年以上人气系列背后的高度开发体制
- original: 1996年に初代『赤・緑』が発売され、2016年に発売された最新作『サン・ムーン』まで、20年以上にわたって人気を博している『ポケットモンスター』シリーズ。これを支えるのが、ゲーム開発全般を担当するゲームフリーク、プロデュースとブランドマネジメントを行うポケモン、そしてポケモンの3DCGアセット制作を担当するクリーチャーズだ。
  translation: 从1996年初代《红・绿》发售，到2016年发售的最新作《太阳／月亮》，持续20多年高人气的《宝可梦》系列。支撑这一系列的是负责游戏开发整体的GAME FREAK、负责制作与品牌管理的宝可梦公司，以及负责宝可梦3DCG资产制作的Creatures。
- original: 写真右から　アートディレクター：海野隆雄氏、ディレクター：大森 滋氏（以上、ゲームフリーク）、ポケモンキャラクターアートディレクター：氏家淳子氏、ポケモンモーションアドバイザー：畠祐貴氏、キャラクターモデリングアーティスト：中廣健吾氏、ポケモン3Dモデリングリード：植松俊介氏（以上、クリーチャーズ）
  translation: 照片从右起：艺术总监 海野隆雄先生、总监 大森滋先生（以上来自GAME FREAK）、宝可梦角色艺术总监 氏家淳子女士、宝可梦动作顾问 畠祐贵先生、角色建模艺术家 中广健吾先生、宝可梦3D建模主管 植松俊介先生（以上来自Creatures）
  type: note
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_prof.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_prof.jpg)
  caption: ''
- original: 『サン・ムーン』の特徴は3点ある。第1に世界観をより身近に感じてもらうために、バトル中で人物キャラクターとポケモンを同じ画面で表示させたことだ。これにより描画負荷の向上が予想されたため、従来のニンテンドー3DSで汎用的に使われている描画エンジンではなく、ゲームフリーク側で『サン・ムーン』に特化した内製ゲームエンジンを開発。10％の処理負荷削減が達成された。
  translation: 《太阳／月亮》有三大特征。第一，为了让世界观更贴近玩家，在战斗中让人物角色和宝可梦显示在同一画面中。由于这预计会提高渲染负荷，因此没有使用任天堂3DS上通用的渲染引擎，而是由GAME FREAK开发了专门针对《太阳／月亮》的自研游戏引擎。实现了10%的处理负荷削减。
- original: 第2に合計で1,000匹以上にも及んだ、膨大なポケモンのアセットデータへの対応策。過去作で使用されたデータも流用されたが、それでも140匹以上が新規で制作されている。さらに、登場するポケモンには「歩く」に加えて「走る」モーションが追加されたものもある。これをミスなく制作するために、さらなる効率化と自動化の工夫がなされている。
  translation: 第二，应对总计超过1000只的庞大宝可梦资产数据。虽然也沿用了过去作品中使用的数据，但仍有超过140只被全新制作。此外，登场的宝可梦中还有一些在“走路”之外追加了“跑步”动作。为了无误地制作这些内容，进行了进一步的效率化和自动化改进。
- original: 最後にニンテンドー3DSというハードウェア上での実装だ。その一方でポケモンのわざやギミックはタイトルを追うごとに複雑化している。そのため本作の開発においても、制限の中での工夫が強く求められた。これらを分散開発の中で滞りなく進めるために、ワークフローの整備をはじめ、様々な工夫が行われている。
  translation: 最后是在任天堂3DS这一硬件上的实现。另一方面，宝可梦的招式和机制随着作品迭代而日益复杂。因此在本作的开发中，也强烈要求在限制内下功夫。为了在分布式开发中顺利推进这些工作，从工作流程的整备开始，进行了各种改进。
- original: これら作業のあらましについて、主にクリーチャーズ側の視点から深掘りしていく。
  translation: 接下来，将主要从Creatures的视角深入探讨这些工作的概要。
- original: Information
  translation: Information
- original: 発売：ポケモン／開発：ゲームフリーク／販売：任天堂株式会社／発売日：発売中／価格：各5,378円／Platform：ニンテンドー3DS／ジャンル：RPG www.pokemon.co.jp/ex/sun_moon
  translation: 发售：宝可梦／开发：GAME FREAK／销售：任天堂株式会社／发售日：发售中／价格：各5,378日元／平台：任天堂3DS／类型：RPG www.pokemon.co.jp/ex/sun_moon
  type: note
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_info.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_info.jpg)
  caption: ''
- type: heading
  level: 2
  original: 3社協業による開発体制とそれを可能にする管理ツール
  translation: 三家公司协作的开发体制及使其成为可能的管理工具
- original: 『ポケットモンスター』の開発を下支えするのがアセットの管理ツール群だ。会社間をまたいだワークフローと結びついて、高度な分散開発を可能にしている。
  translation: 支撑《宝可梦》开发的是资产的管理工具群。它们与跨公司的工作流程相结合，实现了高度分布式开发。
- original: 3社の分担で進むワークフロー
  translation: 三家公司分担推进的工作流程
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_A01a.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_A01a.jpg)
  caption: ''
- original: 新規ポケモンの3DCGデータ制作フロー。はじめにゲームフリーク側でポケモンの公式イラストと設定資料、CG制作用の三面図が作成され、それを基に3社でミーティングを実施。その後3DCGのモデルとモーションがクリーチャーズで制作され、ゲームフリーク側とポケモン側とで監修が行われる。3DCGモデルにはレンダリング用途や他の作品のリファレンスとなるリファレンスモデルと、本作向けに用いられるゲームモデルがあり、今作ではポリゴン数、メッシュ構造、マテリアル構造、ジョイント数などで、両者の連携がより意識された。その後、クリーチャーズ内での最終チェックを経てゲームフリーク側に納品され、最終検収が行われる
  translation: 新宝可梦的3DCG数据制作流程。首先由GAME FREAK方面制作宝可梦的官方插画、设定资料以及用于CG制作的三视图，并以此为基础进行三社会议。之后，由Creatures制作3DCG模型和动作，再由GAME FREAK方面和宝可梦方面进行监修。3DCG模型包括用于渲染用途及作为其他作品参考的参考模型，以及用于本作的游戏模型。在本作中，多边形的数量、网格结构、材质结构、关节数量等方面，更加注重了两者之间的协作。随后，经过Creatures内部的最终检查后交付给GAME FREAK方面，并进行最终验收。
- original: 他のポケモン作品でも活用されるCGデータ
  translation: 在其他宝可梦作品中也会使用的CG数据
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_A01b.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_A01b.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_A01c.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_A01c.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_A01d.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_A01d.jpg)
  caption: ''
- original: 『ポケットモンスター』シリーズ以外に、他のポケモン作品も数多く展開されている。画像はニンテンドー3DS『名探偵ピカチュウ～新コンビ誕生～』のもので、開発はクリーチャーズが担当。他にもアーケードゲーム『ポケモンガオーレ』、アプリゲーム『ポケモンGO』など、多様なプラットフォームで作品が登場しており、これらで使用される3DCGモデルもクリーチャーズが一手に手がけている
  translation: 除了《宝可梦》系列之外，还有许多其他宝可梦作品展开。图片是任天堂3DS《名侦探皮卡丘～新组合诞生～》的，开发由Creatures负责。此外还有街机游戏《宝可梦加傲乐》、手机应用《宝可梦GO》等，作品在多种平台上登场，这些作品中使用的3DCG模型也由Creatures一手包办。
- original: ミスを減らして効率化を進める管理ツール
  translation: 减少错误并推进效率化的管理工具
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_A02a.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_A02a.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_A02b.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_A02b.jpg)
  caption: ''
- original: クリーチャーズとゲームフリークとの間で監修用にやりとりされるデータ量は膨大なものとなる。そのため前作にひき続いて、納品用のデータチェックを効率化するためのデータベースが活用された
  translation: Creatures与GAME FREAK之间为监修而交换的数据量非常庞大。因此，继前作之后，活用了用于高效检查交付数据的数据库。
- original: その上で本作では、内製ゲームエンジンの採用により、Windows上でモデルを確認できるビューアが実現。開発効率に大きく貢献したこの他、エフェクトなどの制作向けに、統合型わざエディタが制作されている
  translation: 在此基础上，本作采用了自研游戏引擎，实现了可在Windows上确认模型的查看器。对开发效率做出了巨大贡献此外，为制作特效等，还制作了集成型招式编辑器。
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_A02c.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_A02c.jpg)
  caption: ''
- original: その上で本作では、内製ゲームエンジンの採用により、Windows上でモデルを確認できるビューアが実現。開発効率に大きく貢献した
  translation: 在此基础上，本作采用了自研游戏引擎，实现了可在Windows上确认模型的查看器。对开发效率做出了巨大贡献。
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_A02d.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_A02d.jpg)
  caption: ''
- original: この他、エフェクトなどの制作向けに、統合型わざエディタが制作されている
  translation: 此外，为制作特效等，还制作了集成型招式编辑器。
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_A02e.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_A02e.jpg)
  caption: ''
- original: アセットデータの共有にはAlienbrainが使用され、アセット管理とワークフロー管理はクリーチャーズ側のRedmineで実施。他に2週に1回の定例会での進捗確認も行われた
  translation: 资产数据的共享使用了Alienbrain，资产管理和工作流管理在Creatures方面的Redmine中实施。此外，还通过每两周一次的例会进行进度确认。
- type: heading
  level: 2
  original: 魅力の中核を担うモデリングとテクスチャの工夫
  translation: 承担魅力核心的建模与贴图巧思
- original: クリーチャーズ制作のポケモンの3DCG データは様々なコンテンツで使用されるため、段階を踏んで制作が進められる。その上でニンテンドー3DS ならではの工夫が行われるのだ。
  translation: Creatures制作的宝可梦3DCG数据会被用于各种内容，因此制作是分阶段推进的。在此基础上，还进行了任天堂3DS独有的巧思。
- original: ステップを踏んで進むCGデータ作成
  translation: 按步骤推进的CG数据制作
- original: ソルガレオの例
  translation: 索尔迦雷欧的例子
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B01a.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B01a.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B01b.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B01b.jpg)
  caption: ''
- original: ニンテンドー3DSの解像度は400×240で、実機上での表現はいわゆるローポリモデルとなるが【画像左】、リファレンスモデルの制作と監修が並行して進むため、複雑な制作工程が採られている。まず新規ポケモンのデザインが確定すると、ゲームフリークとクリーチャーズ側でポケモン立体化のミーティングが行われ、細部の形状や各々のポケモンがもつ特徴、発光や変形などのギミック、質感や動きのイメージが確認される。その後リファレンスモデルが作成され【画像右】、ゲームフリーク側の監修が行われる
  translation: 任天堂3DS的分辨率为400×240，实机上的表现即为所谓的低多边形模型【图片左】，但由于参考模型的制作与监修并行推进，因此采用了复杂的制作工序。首先，新宝可梦的设计确定后，GAME FREAK与Creatures方面会进行宝可梦立体化的会议，确认细节形状、各宝可梦具有的特征、发光和变形等机制、质感与动作的印象。之后制作参考模型【图片右】，并由GAME FREAK方面进行监修。
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B01c.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B01c.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B01d.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B01d.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B01e.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B01e.jpg)
  caption: ''
- original: 続いてスキニングを施し【画像上】、ゲームの仕様に合わせて簡易化させたモーション作成用ゲームモデルを作成【画像下左】、これをブラッシュアップさせてゲームモデルを完成させる【画像下右】
  translation: 接着进行骨骼绑定（蒙皮）【图上】，并根据游戏规格简化为用于制作动作的游戏模型【图下左】，再对其进行打磨完善，最终完成游戏模型【图下右】。
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B01f.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B01f.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B01g.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B01g.jpg)
  caption: ''
- original: これと並行してリファレンスモデルをブラッシュアップさせたリファレンスモデルシーン内ローモデル【画像左】、このローモデルに調整を加えたサブディビジョンサーフェス用モデル（リファレンスモデルシーン内ハイモデル）【画像左】が制作される。なお、リファレンスモデルとゲームモデルでデータがフォークするとモーションなどの流用性が失われてしまうため、できるかぎり同期が可能になるように、本作では両者でジョイント・リグ構造の共通化やジョイントとメッシュの共通化などが、より意識されている。また必要に応じてモデルを同期する際に、リグとモデルのコネクションが自動的に再セットアップされる内製ツールが用意され、効率化が向上している
  translation: 与此并行，会制作将参考模型打磨后的参考模型场景内低模【图左】，以及在此低模基础上调整后用于细分曲面的模型（参考模型场景内高模）【图左】。此外，如果参考模型和游戏模型的数据分叉，动作等资源的复用性就会丧失，因此在本作中，为了尽可能保持同步，更加注重两者之间关节·绑定结构的共通化以及关节与网格的共通化等。另外，在需要同步模型时，准备了可自动重新设置绑定与模型连接的内制工具，提高了效率。
- original: ルナアーラの例
  translation: 露奈雅拉的例子
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B01h.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B01h.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B01i.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B01i.jpg)
  caption: ''
- original: マッシブーンの例
  translation: 穿着熊的例子
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B01j.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B01j.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B01k.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B01k.jpg)
  caption: ''
- original: ポケモンのテクスチャ構成
  translation: 宝可梦的贴图构成
- original: キテルグマの例
  translation: 穿着熊的例子
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B02e.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B02e.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B02a.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B02a.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B02b.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B02b.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B02c.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B02c.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_B02d.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_B02d.jpg)
  caption: ''
- original: ポケモン1匹の3Dモデルの仕様は『X・Y』と同様で、1匹あたり約1万～2万ポリゴン、一部例外を除いてジョイントは110本まで、テクスチャ1枚の最大解像度は256×512（基本は256×256）だ。テクスチャの基本セットはカラーマップ【画像左上】、ノーマルマップ【画像右上】、影カラーマップ【画像左下】で、ハイライトのかかり方を調整するためにハイライトマップ【画像右下】も併用される。テクスチャの最大数は20枚程度で、UVセットの最大数は3、モーションクリップ数は40となる
  translation: 单只宝可梦的3D模型规格与《X·Y》相同，每只约1万～2万多边形，除部分例外，关节最多110根，单张贴图的最大分辨率为256×512（基本为256×256）。贴图的基本套装包括颜色贴图【图上左】、法线贴图【图上右】、阴影颜色贴图【图下左】，为了调整高光效果，还会并用高光贴图【图下右】。贴图的最大数量约为20张，UV集的最大数量为3，动作剪辑数为40。
- type: heading
  level: 2
  original: タイトルごとに限界突破を続けるシェーディングの工夫
  translation: 每部作品都不断突破极限的着色巧思
- original: 『X・Y』、『オメガルビー・アルファサファイア』に続くニンテンドー3DSで第3弾となる本作。質感の決め手となるシェーダについてもさらなる工夫が施されている。
  translation: 本作是继《X·Y》、《欧米伽红宝石·阿尔法蓝宝石》之后在任天堂3DS上的第三部作品。决定质感的着色器也经过了进一步的巧思。
- original: ソルガレオの発光表現
  translation: 索尔迦雷欧的发光表现
- original: 本作では多数のポケモンを表現する都合上、シェーダは半固定機能の組み合わせのみとし、組み合わせ回数にも上限値が定められたため、ポケモン1匹ごとにシェーダの組み替えが必要となった。トゥーンシェーディングを行うことである程度のリソースを消費するため、特殊な表現を組み込む余地がさらに狭まる一方で、タイトルを追うごとに特殊な表現設定をもつポケモンの比率が高まり、腕の見せどころとなる。本作のパッケージを飾る伝説のポケモン・ソルガレオもそのひとつ。太陽の使者として崇められており、エネルギーを解放すると全身が発光するという設定だ。もともと白い体を白く発光させるために、通常時はグレーがかった白色となっている
  translation: 在本作中，由于需要表现大量宝可梦，着色器仅采用半固定功能的组合，且组合次数也有上限，因此每只宝可梦都需要重新组合着色器。进行卡通着色本身就会消耗一定资源，因此嵌入特殊表现的空间更加狭窄，而随着作品迭代，拥有特殊表现设定的宝可梦比例越来越高，这成为展现技术实力的地方。装饰本作包装的传说的宝可梦·索尔迦雷欧便是其中之一。它被尊为太阳的使者，设定为释放能量时全身会发光。原本白色的身体为了发出白光，平时呈现略带灰色的白色。
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C01a.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C01a.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C01b.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C01b.jpg)
  caption: ''
- original: Maya上と実機上での発光時
  translation: Maya上和实机上的发光时
- original: 基本のカラーマップトゥーンシェーディングの影とハイライトを調整するハイライトマップ
  translation: 基本颜色贴图调整卡通着色阴影和高光的高光贴图
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C01c.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C01c.jpg)
  caption: ''
- original: 基本のカラーマップ
  translation: 基本颜色贴图
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C01d.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C01d.jpg)
  caption: ''
- original: トゥーンシェーディングの影とハイライトを調整するハイライトマップ
  translation: 调整卡通着色阴影和高光的高光贴图
- original: 影を綺麗に出すための法線情報が入ったノーマルマップ落ち影で常に影にしたい部分のマスク
  translation: 用于漂亮地呈现阴影的法线信息法线贴图用于投射阴影中始终希望保持为阴影部分的遮罩
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C01e.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C01e.jpg)
  caption: ''
- original: 影を綺麗に出すための法線情報が入ったノーマルマップ
  translation: 用于漂亮地呈现阴影的法线信息法线贴图
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C01f.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C01f.jpg)
  caption: ''
- original: 落ち影で常に影にしたい部分のマスク
  translation: 用于投射阴影中始终希望保持为阴影部分的遮罩
- original: 発光用コンスタントカラー2色をブレンドするための発光ギミック用マスクライン状に発光する部分のテクスチャとなる
  translation: 用于混合两种发光用常量颜色的发光机关用遮罩成为线状发光部分的贴图
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C01h.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C01h.jpg)
  caption: ''
- original: 発光用コンスタントカラー2色をブレンドするための発光ギミック用マスク
  translation: 用于混合两种发光用常量颜色的发光机关用遮罩
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C01g.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C01g.jpg)
  caption: ''
- original: ライン状に発光する部分のテクスチャとなる
  translation: 成为线状发光部分的贴图
- original: ルナアーラのマジョーラカラー
  translation: 露奈雅拉的变色龙色彩
- original: パッケージを飾るもう1匹の伝説のポケモン、ルナアーラ。『サン・ムーン』というタイトルにあわせて、太陽の使者であるソルガレオに対し、「月の使者」としてデザインされたポケモンだ。最大の特徴は全身が角度や光の当たり方で異なるマジョーラカラーになっていることで、環境マップのフェッチにバイアステクスチャをもたせて表現している。また、発光マップはアニメーションが必要なので、マルチUVを使用している
  translation: 装点包装的另一只传说的宝可梦，露奈雅拉。与《太阳／月亮》这个标题相呼应，相对于太阳的使者索尔迦雷欧，它被设计为“月亮的使者”宝可梦。最大的特征是全身会根据角度和光线照射方式呈现不同的变色龙色彩，通过为环境贴图的获取添加偏置贴图来表现。此外，由于发光贴图需要动画，因此使用了多重UV。
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C02a.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C02a.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C02b.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C02b.jpg)
  caption: ''
- original: Maya上と実機上の完成データで、ベースカラーはテクスチャではなくコンスタントカラーの紫を使用
  translation: 在Maya上和实机上的完成数据中，基础颜色不是使用贴图，而是使用常量颜色的紫色
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C02d.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C02d.jpg)
  caption: ''
- original: ノーマルマップ
  translation: 法线贴图
- original: 環境マップ（スフィアマップ）視差を表現するためのマスクとして使用される環境マップ
  translation: 环境贴图（球面贴图）用作表现视差的环境贴图
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C02f.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C02f.jpg)
  caption: ''
- original: 環境マップ（スフィアマップ）
  translation: 环境贴图（球面贴图）
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C02e.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C02e.jpg)
  caption: ''
- original: 視差を表現するためのマスクとして使用される環境マップ
  translation: 用作表现视差的环境贴图
- original: 視差を表現するための環境マップマスク中央の発光部分のマスク
  translation: 用于表现视差的环境贴图遮罩中央发光部分的遮罩
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C02g.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C02g.jpg)
  caption: ''
- original: 視差を表現するための環境マップマスク
  translation: 用于表现视差的环境贴图遮罩
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C02i.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C02i.jpg)
  caption: ''
- original: 中央の発光部分のマスク
  translation: 中央发光部分的遮罩
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C02h.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C02h.jpg)
  caption: ''
- original: もうひとつの特徴である円月状の変形はモデルの差し替えで対応している
  translation: 另一个特征——圆月状变形，是通过替换模型来应对的
- original: トゥーンシェーディング用ノーマルマップの作成
  translation: 用于卡通着色的法线贴图制作
- original: 『X・Y』で開発され、本作でも踏襲された独自のノーマルマップ作成フロー。実モデルからそのまま生成したノーマルマップでは細部の構造や歪みが出てしまい、イラストのような滑らかさが出ない。そのため本作ではローメッシュをスカルプトしてディテールを追加するのではなく、専用のモデルをゼロから作成して、そこから頂点の法線情報が転写されている
  translation: 在《X・Y》中开发，并被本作继承的独特法线贴图制作流程。直接从实际模型生成的法线贴图会出现细节结构和扭曲，无法呈现出如插画般的平滑感。因此，本作并非通过对低模进行雕刻来添加细节，而是从零开始制作专用模型，并从中转写顶点的法线信息
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C03a.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C03a.jpg)
  caption: ''
- original: 完成図を見比べると、そのちがいがわかるだろう（左が元の法線マップ使用時、右が完成図）
  translation: 对比完成图，就能看出其中的差异（左侧为使用原法线贴图时，右侧为完成图）
- original: 法線転送用に体のパーツごとに作成されたSourceメッシュ（青いワイヤーフレームが法線転送用のSourceメッシュ、黄色がモデルメッシュ） Sourceメッシュから分割を追加したモデルに法線を転送
  translation: 为法线转写而按身体部位制作的Source网格（蓝色线框为用于法线转写的Source网格，黄色为模型网格）从Source网格向添加了细分的模型转写法线
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C03b.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C03b.jpg)
  caption: ''
- original: 法線転送用に体のパーツごとに作成されたSourceメッシュ（青いワイヤーフレームが法線転送用のSourceメッシュ、黄色がモデルメッシュ）
  translation: 为法线转写而按身体部位制作的Source网格（蓝色线框为用于法线转写的Source网格，黄色为模型网格）
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C03c.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C03c.jpg)
  caption: ''
- original: Sourceメッシュから分割を追加したモデルに法線を転送
  translation: 从Source网格向添加了细分的模型转写法线
- original: 修正前のノーマルテクスチャに対して、パーツごとにモデルからベイクしたノーマルテクスチャをレイヤーで重ね合わせマテリアルのカラーにノーマルマップを貼り、凹凸がなめらかになったノーマルマップ
  translation: 针对修正前的法线纹理，将按部位从模型烘焙的法线纹理通过图层进行叠加在材质的颜色上贴上法线贴图，使凹凸变得平滑的法线贴图
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C03d.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C03d.jpg)
  caption: ''
- original: 修正前のノーマルテクスチャに対して、パーツごとにモデルからベイクしたノーマルテクスチャをレイヤーで重ね合わせ
  translation: 针对修正前的法线纹理，将按部位从模型烘焙的法线纹理通过图层进行叠加
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C03e.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C03e.jpg)
  caption: ''
- original: マテリアルのカラーにノーマルマップを貼り、凹凸がなめらかになったノーマルマップ
  translation: 在材质的颜色上贴上法线贴图，使凹凸变得平滑的法线贴图
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_C03f.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_C03f.jpg)
  caption: ''
- original: 最後にライトの当たり具合を調整して完成となる
  translation: 最后调整光照效果即完成
- type: heading
  level: 2
  original: 複雑なポケモンの動きを支えるリギング・アニメーション
  translation: 支撑复杂宝可梦动作的骨骼绑定与动画
- original: 今作では新たに「歩き」「走り」の移動モーションが全ポケモンに追加された。特殊なギミック設定があるポケモンも多く、スケルトン構造も複雑になっている。
  translation: 本作中，所有宝可梦都新增了“行走”和“奔跑”的移动动作。许多宝可梦拥有特殊的机关设定，骨骼结构也变得更加复杂。
- original: キュウコン（アローラのすがた）のリギング
  translation: 九尾（阿罗拉形态）的骨骼绑定
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D01a.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D01a.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D01b.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D01b.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D01c.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D01c.jpg)
  caption: ''
- original: ふわふわとした尻尾が特徴的なアローラ地方のキュウコン【画像左上】と待機ポーズ【画像下】。尻尾の動きを再現するために、多くのジョイントが入っている【画像右上】。110個程度というジョイント制限により、リファレンスモデルとゲームモデルで別々のジョイント構造となった
  translation: 以蓬松尾巴为特征的阿罗拉地区九尾【图片左上】与待机姿势【图片下】。为了再现尾巴的动作，加入了大量关节【图片右上】。由于约110个关节的限制，参考模型与游戏模型采用了不同的关节结构。
- original: ドヒドイデのリギング
  translation: 超坏星的骨骼绑定
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D02a.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D02a.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D02b.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D02b.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D02c.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D02c.jpg)
  caption: ''
- original: 周囲がトーチカでおおわれ、防御に優れたドヒドイデ【画像左上】。待機ポーズ【画像下】では正面の2枚が開き、防御時には閉じるという、他に見られないギミックを有している。そのためジョイント【画像右上】も全周を傘のように覆う特殊な構造となった
  translation: 被碉堡覆盖、防御力优异的超坏星【图片左上】。在待机姿势【图片下】中，正面的两片会打开，防御时则会闭合，拥有其他宝可梦所没有的机关。因此，其关节【图片右上】也形成了如伞一般覆盖全周的特殊结构。
- original: デカグースの「歩き」と「走り」
  translation: 猫鼬少的「走路」与「奔跑」
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D03a.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D03a.jpg)
  caption: ''
- original: 待機時は上体を起こしているが、移動時は4つ足となるデカグース
  translation: 待机时抬起上半身，但移动时变为四足行走的猫鼬少。
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D03b.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D03b.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D03c.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D03c.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D03d.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D03d.jpg)
  caption: ''
- original: 歩行時はペタペタといった感じで移動する
  translation: 步行时以啪嗒啪嗒的感觉移动。
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D03e.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D03e.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D03f.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D03f.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D03g.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D03g.jpg)
  caption: ''
- original: 走行時はピョンピョンといった感じで移動する。ヤングースの進化形で、名前の通りマングースなどの小動物の動きが参考にされている
  translation: 奔跑时以蹦蹦跳跳的感觉移动。作为猫鼬探长的进化前形态，正如其名，参考了猫鼬等小动物的动作。
- original: ツツケラの「歩き」と「走り」
  translation: 小笃儿的「走路」与「奔跑」
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D04a.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D04a.jpg)
  caption: ''
- original: アカゲラのように進行方向に対して上下移動しながら飛翔するツツケラ
  translation: 像赤啄木鸟一样，在飞行时沿着前进方向上下移动的小笃儿。
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D04b.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D04b.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D04c.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D04c.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D04d.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D04d.jpg)
  caption: ''
- original: 歩き（ゆっくり飛ぶ）
  translation: 走路（缓慢飞行）
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D04e.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D04e.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D04f.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D04f.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_D04g.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_D04g.jpg)
  caption: ''
- original: 歩き（ゆっくり飛ぶ）時に比べて、走り（高速に飛ぶ）時は体の上下移動が少なく、羽ばたきもより大きくなっている点に注目
  translation: 与走路（缓慢飞行）时相比，奔跑（高速飞行）时身体的上下移动较少，振翅幅度也更大，这一点值得注意。
- type: heading
  level: 2
  original: ゲームフリーク側でのグラフィックスの工夫
  translation: GAME FREAK 在图形方面的巧思
- original: 人物キャラクターやエフェクトをはじめ、ポケモン以外のアセットはゲームフリーク側で作成されている。ここでも制限に立ち向かうための様々な工夫がみられる。
  translation: 以人物角色和特效为首，宝可梦以外的资产均由 GAME FREAK 制作。在这里也能看到各种为了应对限制而下的功夫。
- original: 内製ツールによるモーション作成効率化
  translation: 通过自研工具提升动作制作效率
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_E01a.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_E01a.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_E01b.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_E01b.jpg)
  caption: ''
- original: 本作では「ポケモンの世界観をより身近に感じてもらう」というコンセプトの下、主人公をはじめとしたキャラクターの頭身が上がり【画像左】、バトル中にも登場する。そのため必要なモーション数が急激に増加することになった。そこで新たにリグでアニメーションを扱うための専用フォーマットが作成され、データのライブラリ化を行うしくみを構築【画像右】
  translation: 本作以“让玩家更切身感受宝可梦的世界观”为概念，包括主角在内的角色头身比提高【图片左】，并在战斗中登场。因此所需的动作数量急剧增加。为此，新创建了用于在骨骼绑定中处理动画的专用格式，并构建了将数据库化的机制【图片右】。
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_E01c.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_E01c.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_E01d.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_E01d.jpg)
  caption: ''
- original: その上で社内専用の人物拡張型リグ【画像左】の構築や、内製のキャラクターアニメーション自動生成ツールを作成し【画像右】、自動化が図られている。キャラクターのモーション数や動きの方向性のちがいで詳細なタイプ分けが行われ、それに基づいたモーションプリセットを読み分け、必要なMayaのシーンデータを自動で構築・保存していくことで、アーティストが行う基礎データの作成やファイル管理コストを大幅に削減するしくみだ。タイプが異なるプリセットを読み込んでもリグが差分を吸収するしくみで、リグのセットアップもこの工程で自動的に行われる
  translation: 在此基础上，构建了公司内部专用的人物扩展型骨骼绑定【图片左】，并制作了自研的角色动画自动生成工具【图片右】，实现了自动化。根据角色动作数量和动作方向性的不同进行详细分类，基于此读取动作预设，自动构建并保存所需的Maya场景数据，从而大幅削减了美术师进行基础数据创建和文件管理的成本。即使读取不同类型的预设，骨骼绑定也能吸收差异，骨骼绑定的设置也在该工序中自动完成。
- original: 主人公キャラクターの着せ替え
  translation: 主角角色的换装
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_E02a.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_E02a.jpg)
  caption: ''
- original: 本作では主人公キャラクターの着せ替えアイテムについて、プログラム側の自動生成でカラーバリエーションを増加させている
  translation: 本作中，关于主角角色的换装道具，通过程序端的自动生成增加了颜色变化。
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_E01f.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_E01f.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_E01g.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_E01g.jpg)
  caption: ''
- original: カラーテクスチャは色が乗っていない状態で作成【画像左】し、肌用・服用の各マスク範囲【画像右】に対応する部分に対して色を合成、結果を1枚のテクスチャとして生成するしくみだ
  translation: 颜色纹理在未上色状态下创建【图片左】，针对皮肤用和服装用的各遮罩范围【图片右】对应的部分合成颜色，并将结果生成为一张纹理的机制。
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_E01e.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_E01e.jpg)
  caption: ''
- original: ビューア上では生成したバリエーションの確認もできる
  translation: 在查看器上也可以确认生成的变化。
- original: FlashとAfter Effectsを用いたエフェクト作成
  translation: 使用Flash和After Effects制作特效
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_E02f.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_E02f.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_E02b.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_E02b.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_E02c.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_E02c.jpg)
  caption: ''
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_E02d.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_E02d.jpg)
  caption: ''
- original: バトル画面での多彩なエフェクト【画像左上】は、Flashで連番素材を作成した後に【画像右上】、After Effectsで連番配置をし【画像左下】、グロー処理を追加した上で1枚のテクスチャとして作成されている【画像右下】
  translation: 战斗画面中的多彩特效【图片左上】，在Flash中创建连续编号素材后【图片右上】，在After Effects中进行连续编号配置【图片左下】，添加辉光处理后，作为一张纹理创建【图片右下】。
- type: image
  image: /assets/img/interviews/2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline/cgworld_sm_pipeline_E02e.jpg
  alt: CGWORLD 宝可梦日月 3D 管线技术图 (cgworld_sm_pipeline_E02e.jpg)
  caption: ''
- original: これらがビルボードで表現されているかたちだ。このほかテクスチャを使用したパーティクル画像【画像上】や、社内シェーダを活用した1メッシュ／1マテリアルのマルチテクスチャも使用されている
  translation: 这些以公告板形式表现。此外，还使用了利用纹理的粒子图像【图片上】，以及活用公司内部着色器的1网格/1材质的多纹理。
era_skin: '2019'
entities:
  works:
  - 宝可梦 太阳·月亮
---
