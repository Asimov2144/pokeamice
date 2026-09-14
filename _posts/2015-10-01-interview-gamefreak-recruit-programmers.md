---
archive_type: interview_translation
layout: interview-editorial
title: GAME FREAK 官方专访：我加入游戏狂想的理由（程序员篇：Y.I. × M.K.）
title_ja: 私がゲームフリークに入った理由 プログラマー編
date: 2015-10-01 10:00:00 +0900
era: '2015'
categories:
- developer-interviews
- gamefreak-recruit
tags:
- Game Freak
- 程序员
- 中途招聘
- 场地内容程序
- 资产管线
- 自研引擎
- 宝可梦开发
- 招聘访谈
- Wayback历史存档
interview_id: PKMN-1027
publication: Game Freak 採用情報 (Wayback 历史存档)
original_link: http://web.archive.org/web/20160402065701/http://www.gamefreak.co.jp/recruit/interview_05.html
author: Game Freak 採用チーム
interviewee: Y.I.（场地内容程序员 / 玩家控制统括）, M.K.（场地环境程序员 / 管线架构）
original_lang: ja
translation_lang: zh-CN
summary: 2015年 GAME FREAK 官方中途招聘核心程序员深度对谈：曾开发 PS3/Xbox 360 主机动作游戏、以深爱《风之克罗诺亚》著称并主导《宝可梦 太阳·月亮》玩家移动控制与自研碰撞引擎雏形的资深工程师 Y.I.，与工学研究生院计算机辅助工具链出身、矢志通过自研基础设施实现研发提效的 M.K.，倾情分享在 GAME FREAK 编写底层核心代码的技术人生。专访详述了《宝可梦》如何兼顾庞大超长生命周期与极广全年龄受众的双重开发哲学；客观剖析了在急速迈入 3D 过程中面临的技术资产管理痛点；并展现了年轻一线工程师如何在扁平信任体制下迅速挑起核心架构大梁。
entities:
  people:
  - Y.I.
  - M.K.
  works:
  - 宝可梦 X·Y
  - 宝可梦 欧米伽红宝石·阿尔法蓝宝石
  - 风之克罗诺亚
  - 女神异闻录3
  organizations:
  - 株式会社ゲームフリーク
parallel_items:
- type: image
  src: /assets/img/interviews/2015-gamefreak-recruit-programmers/keyvisual.png
  caption: GAME FREAK 官方访谈：我加入游戏狂想的理由（程序员篇）
- type: heading
  level: 2
  original: 社員紹介
  translation: 受访程序员简介
- type: profile
  speaker: Y.I.
  speaker_orig: フィールドコンテンツプログラマ Y.I.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/profile_01.png
  role_ja: フィールドコンテンツプログラマ（2014年入社）
  role_zh: 场地内容程序员（2014年入社）
  original: 2014年度に入社した、フィールドコンテンツプログラマのY.I.です。現在はプレイヤープログラム全般を担当しています。
  translation: 我是 2014 年入社的场地内容程序员 Y.I.。目前在团队中主要统领玩家角色操作手感与移动控制程序（Player Controller）的全般架构。
  role: answer
- type: profile
  speaker: M.K.
  speaker_orig: フィールド環境プログラマ M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/profile_02.png
  role_ja: フィールド環境プログラマ（2014年入社）
  role_zh: 场地环境程序员（2014年入社）
  original: 同じく2014年度入社のフィールド環境プログラマ、M.K.です。主にアセットパイプラインやツールの構築を行っています。
  translation: 我是同样在 2014 年入社的场地环境程序员 M.K.。目前主要负责全公司资产管线（Asset Pipeline）与美术开发工具链的搭建与性能优化。
  role: answer
- type: heading
  level: 2
  original: とにかくゲームが大好き！
  translation: 无论如何，就是对游戏爱得无可救药！
- type: heading
  level: 3
  original: 入社までの経歴を教えてもらえますか？
  translation: 请首先向大家介绍一下两位在敲响 GAME FREAK 大门之前的学术与职业经历。
- type: text
  speaker: Y.I.
  speaker_orig: フィールドコンテンツプログラマ Y.I.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_01.png
  original: 専門学校を卒業後、名古屋のゲーム会社で2年ほどPS3とXbox 360のアクションゲームを開発していました。その後、東京のゲーム会社に移籍してアクションゲームのバトルやイベント周りを担当し、2014年にゲームフリークに入社しました。ずっとハイエンド寄りのアクションゲームのプログラムを手掛けてきました。
  translation: 我从计算机专科学校毕业后，首先在名古屋的一家游戏公司参与了约两年的 PS3 与 Xbox 360 高清动作游戏开发。随后我转战东京的游戏大厂，负责核心动作战斗机制与剧情事件底层逻辑的编程。2014 年，我正式中途加入 GAME FREAK。回望整个职业生涯，我始终深耕在重度动作游戏的代码一线。
  role: answer
- type: text
  speaker: M.K.
  speaker_orig: フィールド環境 M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_02.png
  original: 私は大学院の修士課程で、ゲームクリエイターを支援する仕組みの研究をしていました。修了後、家庭用ゲーム会社でプログラマとして約3年半、主にツール開発やゲームエンジン周りの業務を担当していました。開発現場の効率化にずっと興味を持っています。
  translation: 我在工学研究生院攻读硕士学位期间，专门从事“数字游戏创作者赋能支持体系与工具算法”的前沿研究。毕业后进入家用主机游戏公司担任系统程序员约三年半，主要负责内部专用生产力工具开发与游戏引擎底层架构维护。用软件工程手段彻底革新游戏一线生产效率，是我毕生最大的学术与技术志趣。
  role: answer
- type: heading
  level: 3
  original: ゲーム業界に入った理由は？
  translation: 当初选择踏入游戏行业的最初动力是什么？
- type: text
  speaker: Y.I. & M.K.
  speaker_orig: Y.I. M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_03.png
  original: ゲームが好きだから！（声を揃えて）
  translation: 因为我们打心底里死心塌地深爱着游戏！（两人异口同声脱口而出）
  role: answer
- type: heading
  level: 3
  original: なるほど、それに尽きますよね。ちなみに好きなゲーム・印象に残っているゲームは何ですか？
  translation: 果然如此，对于真正的创作者而言千言万语都不及这一句！顺便八卦一下，两位各自的“人生游戏”是什么？
- type: image
  src: /assets/img/interviews/2015-gamefreak-recruit-programmers/photo_01.png
  caption: 畅谈热爱的游戏与工程代码之间的纯粹共振：从经典动作名作到宏大日式 RPG
- type: text
  speaker: Y.I.
  speaker_orig: フィールドコンテンツプログラマ Y.I.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_01.png
  original: 今までの人生でナンバーワンのゲームは『風のクロノア』です。あの独特の浮遊感、敵を掴んで投げるアクションの気持ちよさ、そして切ない世界観。アクションゲームとしてこれ以上ないほど完成されていて、今でも私のものづくりの原点になっています。
  translation: 如果要评选我这辈子迄今为止的 No.1 殿堂级神作，那绝对非《风之克罗诺亚》（Klonoa）莫属！那股绝妙的跃动浮空手感、抓取敌人当垫脚石投掷的机制快感，以及美妙中带着丝丝感伤的末世物语——作为一款动作游戏，它的纯粹度与完成度高到无以复加，即便到了今天，它依然是我进行任何手感调优时最神圣的基准原点。
  role: answer
- type: text
  speaker: M.K.
  speaker_orig: フィールド環境 M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_02.png
  original: 私はスポーツゲームと恋愛ゲーム以外何でもやるんですが、特に印象に残っているのは『ペルソナ3』と『真・女神転生』シリーズですね。あの洗練されたUI、スタイリッシュなデザイン、悪魔合体の奥深いシステム。ゲームという総合芸術が持つ可能性に圧倒された作品です。
  translation: 除了体育类和恋爱文字类，我几乎把市面上所有类型的游戏全推了个遍；但若论震撼灵魂的烙印，首推《女神异闻录3》（Persona 3）与整个《真·女神转生》系列。那划时代的超洗练 UI 交互美学、极度前卫的潮酷风貌、以及恶魔合体那深不见底的数理策略深度——正是这些作品让我真切领略到了“电子游戏”作为一门终极综合艺术所孕育的无限可能。
  role: answer
- type: heading
  level: 2
  original: 小規模タイトルも大規模タイトルも作ってみたい
  translation: 巨擘与独立并进：兼顾百人航母与十人飞艇的研发向往
- type: heading
  level: 3
  original: 今回転職先にGFを選んだのはなぜですか？
  translation: 两位在职业生涯的新阶段，最终敲定加入 GAME FREAK 的核心动因是什么？
- type: text
  speaker: Y.I.
  speaker_orig: フィールドコンテンツプログラマ Y.I.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_01.png
  original: 私の場合、新卒で入社して最初に作ったタイトル、本当に頑張って作ったんですが、商業的にはあまり売れなかったんです。それがものすごく悔しくて。「自分が心血を注いで作ったゲームを、もっと何百万、何千万人という世界中の人に遊んでもらいたい！」という渇望がずっとありました。ゲームフリークなら、『ポケットモンスター』という世界最高峰のプラットフォームで、自分の技術を世界中に届けることができる。これ以上ない挑戦だと思いました。
  translation: 在我身上有个刻骨铭心的经历：刚毕业入职第一家公司时我拼尽全力打造的处女作，在团队的心血与汗水之下，最终在商业市场上却反响平平、惨遭滑铁卢。那份深入骨髓的不甘心彻底灼痛了我。从那时起我内心深处便时刻咆哮着一个饥渴的呐喊：“我耗尽心血铸就的代码，必须被全世界数百万、数千万乃至上亿玩家握在手心疯狂畅玩啊！”而在 GAME FREAK，坐拥《宝可梦》这一举世无双的超级舞台，我能够直接把自己的工程才华推向全世界每一个角落——这对于任何一个有雄心的程序员而言，都是世上无可替代的最高挑战！
  role: answer
- type: text
  speaker: M.K.
  speaker_orig: フィールド環境 M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_02.png
  original: 私の場合は、第一にパッケージゲームを作りたいというのがありました。それも、ただのパッケージではなく、「サイズの大きい」タイトルに携わりたかった。そして第二に、「ギアプロジェクト」の存在です。世界規模の大作に携わりながら、同時に少人数で尖った新規タイトルに挑戦できる。この二刀流ができる環境は、他には絶対にありませんでした。
  translation: 而在我这方面，最首要的一条原则是我必须做实体的盒装大作。而且不仅仅是普通作品，而是必须深度切入“体量超群”的现象级巨作；其次，正是 GAME FREAK 独步业界的“齿轮企划（Gear Project）”！在操盘世界级航母大作的同时，公司竟然还为你留出了能够在极少人数编制下向最锋芒毕露的全新原创 IP 挥剑的通道——放眼全球游戏工业，能够同时实现这种“巨擘与独立双刀流”的梦幻圣地，绝对绝无仅有！
  role: answer
- type: heading
  level: 3
  original: 「サイズが大きい」とはどういうことですか？　また、それに興味があるのはなぜですか？
  translation: M.K. 先生所说的“尺寸体量极其宏大”，具体指的是什么？为什么会对此抱有如此强烈的执念？
- type: image
  src: /assets/img/interviews/2015-gamefreak-recruit-programmers/photo_02.png
  caption: 剖析《宝可梦》跨越全年龄层的受众厚度，与承载海量资产的系统工程复杂性
- type: text
  speaker: M.K.
  speaker_orig: フィールド環境 M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_02.png
  original: 「長いプレイ時間」と「広いターゲット層」のことです。『ポケットモンスター』は、ストーリーをクリアして終わりではなく、対戦や育成、図鑑集めなど、何百時間、何千時間と遊ばれ続けます。そして、小学生から親世代まで、世界中のあらゆる世代がプレイする。それだけのスケールを支えるプログラムを作るということは、堅牢性やパフォーマンス、拡張性のすべてにおいて最高峰の設計が求められます。システムエンジニアとして、これほど腕の鳴る舞台はありません。
  translation: 我指的是“惊人绵长的游戏时间跨度”以及“横跨全人类的极宽受众圈层”。《宝可梦》绝不是那种通关主线剧情十几小时就能束之高阁的快餐品，它背后的全球联机对战、严选孵蛋培育、全图鉴全闪光收集，会让玩家不吃不喝连续沉浸几百甚至几千个小时！更不可思议的是，它的玩家上至银发老人、下至学龄幼童，覆盖了全球所有的文化与代际。要在极其严苛的掌机硬件上编写能够稳如泰山支撑起这种超维体量的底层程序，对代码的健壮性、吞吐性能与模块解耦扩展性提出了人类工程学的最高要求！对于一名系统架构师来说，再没有比这更能激发斗志的荣誉角斗场了！
  role: answer
- type: heading
  level: 2
  original: 若手も早くから活躍する余地がある組織
  translation: 年轻血液大展宏图：扁平组织下的责任与试炼
- type: heading
  level: 3
  original: 実際入社してみた感想は？
  translation: 真正加入 GAME FREAK 披甲上阵后，一线的真实技术生态带来了怎样的感悟？
- type: text
  speaker: Y.I.
  speaker_orig: フィールドコンテンツプログラマ Y.I.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_01.png
  original: 予想していた以上に、どんどん仕事を任せてもらえて驚いています。今は設計から実装、チューニングまで、プレイヤー挙動のほぼ全般を担当させてもらっています。もちろんプレッシャーは大きいですが、自分の作ったロジックがそのままゲームの骨格になっていく手応えは何物にも代え難いですね。
  translation: 远远超出我的预想，公司放手交办核心任务的速度快得惊人！目前从最前期的软件顶层设计、算法具体实现到极限性能调优，整部新作中关于主角操作手感与行为逻辑的几乎全部代码，都已经全权由我一人挑起大梁。这种高压固然如泰山压顶，但当你亲眼看到自己一行行敲下的逻辑代码直接化为全世界训练家触手可及的骨骼与呼吸，那份沉甸甸的成就感是世上任何褒奖都无法比拟的！
  role: answer
- type: text
  speaker: M.K.
  speaker_orig: フィールド環境 M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_02.png
  original: やっぱり巨大なプロジェクトだなあと思う一方で、意外と原始的な部分、改善の余地がたくさん残されていることにも驚きました。「ゲームフリークって、世界的な大ヒット作を作っているから、開発環境も完全に自動化されて完璧なんだろう」と外からは見えるじゃないですか。でも中に入ってみると、泥臭い手作業が残っていたりする。でもそれは、裏を返せば「自分達の手でいくらでも良くできるフロンティアが広がっている」ということです。エンジニアとしては最高に燃える環境ですよ。
  translation: 一方面我深深惊叹于这部大作背后惊天动地的体量，但另一方面同样让我大吃一惊的是：在它华丽的外表之下，研发底层竟然还残留着不少相当原始、有着海量重构空间的粗糙角落！外界大众往往带有天真的幻想，觉得“GAME FREAK 既然能做出横扫全球的世纪大作，内部的研发工具链肯定是全自动化、完美无瑕的神仙体系吧？”但只有当你真正走进来才会发现，为了赶工期，很多环节依然依靠着极其硬核朴素的人肉泥潭在硬抗。然而这绝非坏事——从工程师的角度反过来看，这意味着你面前正横亘着一片等待你亲手用代码彻底征服并重塑的广袤无人区！对于一个真正的系统极客来说，再没有比这更让人血脉偾张的热土了！
  role: answer
- type: heading
  level: 3
  original: どの辺りが、原始的だと感じますか？
  translation: 能否具体举例说明一下，究竟是哪些具体技术模块让两位感受到了“原始”与巨大的重构机遇？
- type: image
  src: /assets/img/interviews/2015-gamefreak-recruit-programmers/photo_03.png
  caption: 探讨从零搭建全新碰撞物理引擎，以及重塑全自动化资源导入管线的技术野心
- type: text
  speaker: Y.I.
  speaker_orig: フィールドコンテンツプログラマ Y.I.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_01.png
  original: モデルやテクスチャの管理方法は、今後ハードのスペックが上がった時に対応しきれなくなるだろうな、という危機感がありました。また、フィールド上のコリジョン（当たり判定）の処理なども、昔ながらのグリッドベースの思想が残っていたりして。フル3Dの自由な地形をスムーズに移動させるためには、もっと現代的なコリジョンエンジンを自前で組み直す必要があると感じました。今まさにその改革に取り組んでいます。
  translation: 比如美术 3D 模型与高清贴图资产的管理与打包流转方式，我敏锐地察觉到如果未来掌机硬件算力再度大跨步升级，现有的祖传格式必将彻底崩溃。又比如大地图野外的“碰撞判定（Collision）”逻辑，底层竟然还深深烙印着多年前 2D 点阵网格时代（Grid-based）的古老遗风！为了让主角能在全 3D 的起伏山川与复杂地形中如丝般顺滑奔跑穿梭，我们必须彻底抛弃历史包袱，从零自研编写一套完全现代化的全新 3D 碰撞判定引擎！而这正是我目前正在夜以继日攻坚的核心战役。
  role: answer
- type: text
  speaker: M.K.
  speaker_orig: フィールド環境 M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_02.png
  original: コミュニケーション手段や情報管理、アセットパイプラインに利用しているツール類ですね。前職や大学で見てきた最新のCI（継続的インテグレーション）や自動ビルドの仕組みを取り入れれば、もっと開発スピードを跳ね上げられる。そうした改善提案を出すと、先輩たちも「いいね、やってみてよ！」とすぐに背中を押してくれます。若手だからといって意見が抑え込まれることは絶対にありません。
  translation: 我感触最深的则是全员的协同通讯方式、文档知识库体系、以及资产管线（Asset Pipeline）所依赖的各类中间件工具。只要将我在前东家和工学研究生院所验证过的现代化 CI（持续集成）与分布式自动化云编译（Auto-build）体系强力引入，整座公司的研发吞吐速率就能当场翻倍狂飙！而最棒的是，每当我提出这些大刀阔斧的重构方案时，公司的元老技术大牛们从不摆资历架子，反而两眼放光全力拍板支持：“太漂亮了，放手去干吧！”在 GAME FREAK，年轻永远不是借口，任何卓越的工程见地都会被奉若至宝。
  role: answer
- type: heading
  level: 3
  original: これからGFでやりたいことは何ですか？
  translation: 展望未来的技术地平线，两位在 GAME FREAK 怀揣着怎样宏伟的技术宏图？
- type: text
  speaker: Y.I.
  speaker_orig: フィールドコンテンツプログラマ Y.I.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_01.png
  original: 早くマネジメントを任せられるようになりたいですね。あと、前職はミドルウェアを多く使っていたんですが、ゲームフリークは内製技術を非常に大切にする会社です。だからこそ、自分自身の手で新しい技術の基盤を作り、それを社内に根付かせたい。そしてゆくゆくは、ギアプロジェクトで自分がディレクターとなって、世界を唸らせるオリジナルアクションゲームを世に放ちたいです。
  translation: 我的近期目标是尽快成长为能够独当一面的技术管线主管。此外，在前东家时我们大量依赖商业化第三方中间件，而来到 GAME FREAK 后我深受震撼的一点是：这家公司对“核心技术自研（In-house Engine）”怀揣着近乎偏执的神圣敬畏！正因如此，我渴望亲手搭建出一整套能够支撑下一个十年的全新底层技术底座，并在全社落地生根。而在更远的未来，我必将叩响齿轮企划的大门，以总监（Director）身份亲手打造出一部让全世界玩家起立鼓掌的原创动作神作！
  role: answer
- type: text
  speaker: M.K.
  speaker_orig: フィールド環境 M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_02.png
  original: 私は、同じ規模のゲームをより少ない人数で作れるように開発環境を整えていきたいです。ゲームフリークが少数精鋭であり続けるためには、技術による徹底的な効率化が不可欠です。クリエイターが技術的な制約に苦しむことなく、ただ「面白さ」に全エネルギーを注げるような理想郷を作りたい。自分の作ったインフラが会社全体の生産性を何倍にも引き上げる、そんな“縁の下の力持ち”の頂点を目指します。情熱と実力を持ったエンジニアの挑戦を、心から待っています！
  translation: 我的终极宏图是：通过打造超高水准的现代化研发基座，让同样规模体量的世纪大作能够以更精炼的人数高质量诞生！GAME FREAK 之方案在于用底层技术实现彻底的生产力解放。我渴望构筑这样一座理想国——让一线创作者们彻底摆脱一切技术瓶颈与繁琐杂务的折磨，将他们百分之百的脑力与灵魂无损倾注在“纯粹好玩”的终极推敲上！用我搭建的数字基础设施，成倍放大整座公司的创造力，成为支撑起这家伟大公司腾飞的最强幕后基石。如果你拥有滚烫的野心与扎实的真功夫，我们在这里随时等待你的挑战！
  role: answer
---
<div class="interview-profiles my-5 p-4 bg-light rounded shadow-sm">
  <h3 class="border-bottom pb-2 mb-4 text-primary fw-bold">受访核心程序员背景档案</h3>
  <div class="row g-4">
    <div class="col-md-6 border-end">
      <h4 class="fw-bold mb-1">Y.I.</h4>
      <p class="text-muted small mb-1"><strong>入职：</strong>2014年中途入社</p>
      <p class="text-muted small mb-2"><strong>职务：</strong>场地内容程序员 / 玩家控制系统统括</p>
      <p class="small text-secondary mb-0">深耕 PS3/Xbox 360 主机动作底层，在《宝可梦 太阳·月亮》中挑起大梁，独立自研全新 3D 物理碰撞判定引擎，后调任研究开发部（R&D）专攻前沿技术。</p>
    </div>
    <div class="col-md-6 ps-md-4">
      <h4 class="fw-bold mb-1">M.K.</h4>
      <p class="text-muted small mb-1"><strong>入职：</strong>2014年中途入社</p>
      <p class="text-muted small mb-2"><strong>职务：</strong>场地环境程序员 / 资产管线与 CI 架构</p>
      <p class="small text-secondary mb-0">计算机工学研究生院专攻辅助工具链，深谙游戏工业基础设施提效，全面推进全自动化资产导入、持续集成（CI）与分布式编译管线。</p>
    </div>
  </div>
</div>
