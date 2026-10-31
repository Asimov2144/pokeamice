---
archive_type: interview_translation
layout: interview-editorial
title: GAME FREAK 官方专访 程序员特辑：从『日月』自研碰撞引擎到 R&D 前沿技术追求（Y.I.）
title_ja: 新作タイトルを開発。R&Dで最新技術を追求。両方できる。（プログラマ Y.I.）
date: 2019-12-11 10:00:00 +0900
recruit:
  page: interview-pg-yi
  version: '2019-12-11'
  capture: '20191211222205'
  date_basis: 2019 年 12 月招聘站改版时的首批人物页（Wayback 首见 2019-12-11）；2020-10-24 至 12-16 之间，招聘首页上换成了程序员 H.T. 的页面
era: '2019'
categories:
- developer-interviews
- gamefreak-recruit
tags:
- 'Game Freak'
- '招聘专访'
- '程序员'
- 'R&D'
- '宝可梦 太阳·月亮'
- '宝可梦 Let''s Go！皮卡丘·Let''s Go！伊布'
- '碰撞引擎'
- '跟随系统'
- '明雷遇敌'
- '流式加载'
- 'Wayback历史存档'
- '招聘访谈'
interview_id: PKMN-1031
publication: Game Freak 採用情報 (Wayback 历史存档)
original_link: http://web.archive.org/web/20200804213450/https://www.gamefreak.co.jp/recruit/interview/yi/
author: Game Freak 採用チーム
interviewee: Y.I.（程序员 / 研究开发部）
original_lang: ja
translation_lang: zh-CN
summary: 2019年 GAME FREAK 官方中途招聘核心专访：曾在家用机大作与游戏中间件领域深耕6年的资深工程师 Y.I.，深度复盘加入 GAME FREAK 后的技术进阶历程。入社伊始便在 3DS《宝可梦 太阳／月亮》中从零全自研碰撞引擎，入社第3年担纲 Switch 首作《宝可梦 走吧！皮卡丘／走吧！伊布》程序员部门总监，攻坚 150+ 宝可梦大地图跟随行走系统、野外明雷系统与流式加载。随后调任 R&D 研究开发部主导新一代通用引擎研发，揭秘 GAME FREAK 兼顾商业正作落地与前沿尖端技术探索的双轮驱动架构。
entities:
  people:
  - Y.I.
  works:
  - 宝可梦 太阳·月亮
  - 宝可梦 Let's Go！皮卡丘·Let's Go！伊布
  organizations:
  - 株式会社ゲームフリーク
parallel_items:
- type: image
  src: /assets/img/interviews/2019-gamefreak-recruit-pg-yi/mv.jpg
  caption: GAME FREAK 官方访谈：程序员特辑（Y.I.）
- type: heading
  level: 2
  original: 社員紹介
  translation: 受访员工简介
- type: profile
  speaker: Y.I.
  speaker_orig: Y.I. プログラマ
  avatar: /assets/img/interviews/2019-gamefreak-recruit-pg-yi/thumb-yi.jpg
  role_ja: プログラマ（開発二部 在籍後、研究開発部へ）
  role_zh: 程序员（曾任职开发二部，现调任研究开发部 R&D）
  original: コンシューマーゲームの開発会社とミドルウェア開発会社を経て、ゲームフリークに中途入社。開発二部に在籍後、研究開発部へ。
  translation: "曾在家用机游戏开发公司和中间件开发公司工作后，中途加入 GAME FREAK。在开发二部任职后，调入研究开发部。"
  role: answer
- type: heading
  level: 2
  original: 新作タイトルを開発。R&Dで最新技術を追求。両方できる。
  translation: "开发新作。在R&D追求最新技术。两方面都能做。"
- type: heading
  level: 3
  original: ワールドワイドなタイトルをつくりたい。
  translation: "想制作面向全世界的作品。"
- type: image
  src: /assets/img/interviews/2019-gamefreak-recruit-pg-yi/img-01.jpg
  caption: "为 3DS《宝可梦 太阳·月亮》从零全量自研碰撞检测引擎"
- type: text
  speaker: Y.I.
  avatar: /assets/img/interviews/2019-gamefreak-recruit-pg-yi/thumb-yi.jpg
  original: "Play Station® 3やXbox 360といったコンシューマーゲームの開発会社に2年。その後、ミドルウェア開発会社に4年勤めました。充実した毎日でしたが、やっぱり、もう一度ゲームソフトがつくりたい。そんな気持ちが抑えきれなくなり、転職を決意しました。ワールドワイドなタイトルを持っていて、その制作に携われる可能性が高い会社を探したところ、ゲームフリークと出会いました。\n\n入社早々に参画したのは、ニンテンドー3DSの『ポケットモンスター サン・ムーン』。プレイヤーやNPCの動作を担当し、コリジョンエンジンをフルスクラッチでつくりました。これまで据置型ゲーム機向けの開発をしていたため、ハードがニンテンドー3DSとなったことで今までとは違ったチューニングが必要となり、最初は戸惑いました。しかし、社員全員にトライアンドエラーを繰り返して成果を出そうとする意識があったため、私自身も思いきって新しい環境で挑戦することができました。作品をリリースするハードの性能を1ミリも残さず使い切ろうと試行錯誤するところも、ゲームフリークの強さだと感じました。"
  translation: "我先在开发 PlayStation 3、Xbox 360 等家用机游戏的公司工作了2年，之后在中间件开发公司工作了4年。每天都很充实，但我还是想再做一次游戏软件。这种心情越来越抑制不住，于是下定决心转职。我寻找的是拥有面向全世界的作品、并且很有可能参与其制作的公司，就这样遇到了 GAME FREAK。\n\n入社后不久，我就参与了 Nintendo 3DS 的《宝可梦 太阳·月亮》。我负责玩家和NPC的动作，从零开始制作了碰撞引擎（Collision Engine）。我之前一直做面向家用主机的开发，硬件换成 Nintendo 3DS 之后需要和以往不同的调优，起初感到很困惑。不过，因为全体员工都有通过反复试错来做出成果的意识，我自己也得以放手在新的环境中挑战。为了把发售作品所用硬件的性能一点不剩地用尽而反复尝试，我觉得这也是 GAME FREAK 的强项。"
  role: answer
- type: heading
  level: 3
  original: 『ポケモン』が持つ膨大なデータ量に、チームで挑む。
  translation: "与团队一起，挑战『宝可梦』庞大的数据量。"
- type: image
  src: /assets/img/interviews/2019-gamefreak-recruit-pg-yi/img-02.jpg
  caption: 在 Switch 首作《走吧！皮卡丘／走吧！伊布》中担任程序员部门总监
- type: text
  speaker: Y.I.
  avatar: /assets/img/interviews/2019-gamefreak-recruit-pg-yi/thumb-yi.jpg
  original: "ゲームフリークで活躍することに、年齢や経歴は関係ありません。大切なのはプロジェクトが求めるスキルセットを持っているかどうかなんです。私自身、入社1年半でチームリーダーを、3年目でプログラマのセクションディレクターを経験することができました。すごいスピード感だと思います。\n\nセクションディレクターを務めたのは、『ポケットモンスター Let’s Go！ピカチュウ・Let’s Go！イーブイ』という当社初のNintendo Switchのタイトル。基礎技術の面では、『ポケットモンスター サン・ムーン』で作成したコリジョンエンジンの拡張、ゲーム内におけるストリーミングロードシステム、アセットビルドパイプラインの作成等を担当し、遊びの面では、150匹以上ものポケモンの連れ歩き機能や、野生のポケモンのシンボルエンカウント、大きなポケモンの上に乗ったり、小さなポケモンを肩に乗せたりできる機能を構築しました。\n\nポケモンは種類が多く、一つひとつの形状や大きさが異なります。本来ならポケモンそれぞれ固有の動作プログラムをつくらなければならないのですが、データが大規模化しすぎてしまうため、いくつかの類型に集約させて効率化を図ったのはチャレンジングな試みだったと思います。セクションディレクターとして総勢20人近いメンバーの得手不得手を見極め、役割を割り振り、意思統一を図るというマネジメントの仕事は、前職でも経験したことがなくとても難しいものがありました。でもその分、自分一人の力では到達できない規模の大きな企画を実現でき、チームで挑む面白さも実感しました。発売日イベントでは、ファンの皆さんがカウントダウンでとても盛り上がっているのを目の当たりにして、大きな達成感も得られました。"
  translation: "在 GAME FREAK 要活跃，与年龄和经历无关。重要的是是否具备项目所需要的技能。就我自己而言，入社1年半就担任了团队负责人（Team Leader），第3年担任了程序员的部门总监（Section Director）。我觉得速度非常快。\n\n我担任部门总监的，是本公司首款 Nintendo Switch 作品《宝可梦 Let's Go！皮卡丘·Let's Go！伊布》。基础技术方面，我负责扩展《宝可梦 太阳·月亮》中制作的碰撞引擎、游戏内的流式加载系统（Streaming Load System）、资源构建管线（Asset Build Pipeline）的制作等；玩法方面，我构建了让150只以上宝可梦跟随行走的功能、野生宝可梦的明雷遇敌（Symbol Encounter），以及可以骑到大型宝可梦身上、把小型宝可梦放在肩膀上的功能。\n\n宝可梦种类很多，每一只的形状和大小都不一样。本来应该为每只宝可梦编写各自专用的动作程序，但那样数据会变得过于庞大，所以把它们归并为几个类型来提高效率，我觉得这是一次有挑战性的尝试。作为部门总监，要看清近20名成员各自的擅长与不擅长，分配职责，统一意志，这样的管理工作我在上一份工作里也没有经历过，非常困难。不过正因如此，我们实现了凭自己一个人的力量无法达到的大规模企划，也切实感受到了与团队一起挑战的乐趣。在发售日活动上，亲眼看到粉丝们围绕倒计时热烈欢庆的情景，我也获得了很大的成就感。"
  role: answer
- type: heading
  level: 3
  original: 尖った技術や最新技術を持った人と働きたい。
  translation: "想和拥有尖端技术、最新技术的人一起工作。"
- type: image
  src: /assets/img/interviews/2019-gamefreak-recruit-pg-yi/img-03.jpg
  caption: 在研究开发部主导新一代通用引擎研发与技术管理
- type: text
  speaker: Y.I.
  avatar: /assets/img/interviews/2019-gamefreak-recruit-pg-yi/thumb-yi.jpg
  original: "私は今、研究開発部で新しいエンジンの研究開発とマネジメントをおこなっています。前職でのミドルウェア開発経験と、これまでの『ポケモン』開発の経験を生かして、より世界観を構築するための一助となるエンジン開発をしたいと考えています。現在の計画では『ポケモン』シリーズに限ったものですが、ゆくゆくは社内で開発する他のタイトルにも活かせるようなエンジンを開発したいですね。毎日がチャレンジです。\n\n研究開発部では、シェーダー、3Dアニメーション、AI、ネットワーク、物理といった領域における尖った技術や最新技術を持つ仲間を求めています。出身業界はどこでもいい。さまざまなスキルを生かせる場があります。新しい風を巻き起こし、同僚とのコラボレーションにより良いシナジーを起こせる人と一緒に働きたいですね。"
  translation: "我现在在研究开发部进行新引擎的研究开发和管理工作。我想发挥此前在中间件开发中的经验和迄今为止《宝可梦》开发的经验，开发出有助于更好地构建世界观的引擎。按目前的计划，它仅限于《宝可梦》系列，但将来我想开发出也能用于公司内部开发的其他作品的引擎。每天都是挑战。\n\n研究开发部正在寻找在着色器、3D动画、AI、网络、物理等领域拥有尖端技术或最新技术的伙伴。出身于哪个行业都可以，这里有能发挥各种技能的舞台。我想和能带来新风气、通过与同事的合作产生更好协同效应的人一起工作。"
  role: answer
---
