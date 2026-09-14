---
archive_type: interview_translation
layout: interview-editorial
title: GAME FREAK 官方对谈 系统程序员篇：乐于拥抱持续变化的人，将塑造10年后的 GAME FREAK
title_ja: システムプログラマ対談：変化を楽しみ続ける人が、10年後のゲームフリークを作る。
date: 2021-12-27 10:00:00 +0900
era_skin: '2019'
categories:
- interviews
tags:
- Game Freak
- 招聘对谈
- 系统程序员
- 底层架构
- 自研引擎
- CI/CD
- 工具链
- 跨界挑战
source:
  title: システムプログラマ対談｜採用情報｜GAME FREAK 株式会社ゲームフリーク
  url: https://www.gamefreak.co.jp/recruit/crosstalk-system-programmer/
interviewee: K.M., H.T.
summary: GAME FREAK 官方招聘特辑·系统程序员篇！研究开发部副部长 K.M. 与基盘技术开发部部长 H.T. 展开深度对谈。两人解析了系统程序员作为‘幕后英雄’的核心使命：不仅要为全社搭建高性能编译、CI/CD自动化测试和资产管理系统，更要走在所有作品研发的5至10年之前，以技术先导试验驱动下一代宝可梦体验；更敞开怀抱欢迎Web和IT跨行业工程师加入，共同塑造面向2030年代的 GAME FREAK！
entities:
  people:
  - K.M.
  - H.T.
  works:
  - 宝可梦传说 阿尔宙斯
  - 宝可梦 朱·紫
parallel_items:
- type: image
  original: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/mv.jpg
  translation: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/mv.jpg
  caption: GAME FREAK 官方对谈：系统程序员篇
- type: heading
  original: 登壇者プロフィール（受访嘉宾档案）
  translation: 受访嘉宾档案
- type: image
  original: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/member-km.jpg
  translation: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/member-km.jpg
  caption: K.M.（研发部副部长 / 2018年入职）
- type: paragraph
  original: K.M.（2018年入社）：大手ゲームメーカーで描画プログラマを務めた後、技術研究の道を模索する中でゲームフリークと出会う。研究開発部 副部長。描画、アニメーション、テクニカルアーティスト（TA）のチームマネジメントを担当。
  translation: K.M.（2018年入职）：曾在大厂担任渲染图形程序员，在探索技术研发的道路中加入 GAME FREAK。现任研究开发部副部长，统筹负责渲染、动画与技术美术（TA）的团队管理。
- type: image
  original: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/member-ht.jpg
  translation: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/member-ht.jpg
  caption: H.T.（基础技术开发部部长 / 2019年入职）
- type: paragraph
  original: H.T.（2019年入社）：新卒でゲーム会社に入社後、フリーランスとして独立して数社のモバイルゲーム開発を経験。AIスタートアップのCOOを経て、ゲームフリークに入社。基盤技術開発部 部長として、エンジン・インフラ・社内ツール開発を統括。
  translation: H.T.（2019年入职）：毕业后进入游戏公司，后作为自由职业者参与多款手游开发。曾任 AI 创业公司首席运营官（COO），随后加入 GAME FREAK。现任基盘技术开发部部长，全面统括引擎、基础架构及公司内部工具链开发。
- type: heading
  original: 最高のゲームを作るための、最高の開発環境を作る。異業種からの挑戦も、大歓迎。
  translation: 为了打造最顶尖的游戏，构筑最顶级的开发环境。来自跨行业的挑战者也大受欢迎。
- type: image
  original: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-01.jpg
  translation: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-01.jpg
  caption: K.M. 与 H.T. 畅谈 GAME FREAK 底层架构演进
- type: dialogue
  speaker: K.M.
  original: ゲームタイトルそのものの開発を担当するというより、今までにない新しいゲームを作るために開発環境を進化させる。それが、私たちシステムプログラマのミッションです。最先端の技術を取り入れ、新技術を自ら開発し、それをゲーム開発に活用できるように仕組み化していきます。
  translation: 与其说我们负责的是游戏作品本身的开发，不如说是为了让前所未有的新游戏得以诞生而不断进化开发环境。这正是我们系统程序员的使命。我们引进最前沿的技术，自主研发新技术，并将其机制化，使其能够应用于游戏开发之中。
  role: answer
- type: dialogue
  speaker: H.T.
  original: ゲームプログラマには遊びについても考えるプランナー的な要素も求められますが、システムプログラマは必ずしもそうではありません。もちろんゲームが好きであることは大前提ですが、ゲーム業界での経験がなくても活躍できるのがシステムプログラマの大きな特徴ですね。Web業界やIT業界など、異業種出身者もたくさん在籍しています。
  translation: 游戏程序员需要具备类似策划的思维，去思考玩法层面的内容，但系统程序员未必如此。当然，热爱游戏是大前提，但即便没有游戏行业的经验也能大展身手，这正是系统程序员的一大特点。我们这里有许多来自Web行业、IT行业等不同领域的同事。
  role: answer
- type: dialogue
  speaker: K.M.
  original: 縁の下の力持ちとして、高品質なゲーム作りを支えるのが、私たちの役割です。できる限り高性能なPCを用意したり、ビルドやテストを自動化したり、アセットの管理システムを作ったり。クリエイターたちがストレスなく、最高のものづくりに専念できる環境を整えることが、結果としてゲームのクオリティを底上げすることにつながります。
  translation: 作为幕后英雄，支撑高品质游戏的制作，就是我们的职责。尽可能配备高性能的PC，实现构建和测试的自动化，搭建资产管理系统。为创作者们营造一个能够无压力地专注于打造最优秀作品的环境，最终也会带动游戏品质的整体提升。
  role: answer
- type: dialogue
  speaker: H.T.
  original: 一方で、縁の下で支えるだけではなく、タイトル開発を引っ張り、ドライブさせていく側面もありますよね。研究開発チームが新しい表現や技術を先にプロトタイプとして作り、「こんな技術ができたから、次のゲームで使ってみないか？」と開発陣に提案していく。技術起点で新しい遊びを生み出すことも、私たちの重要な使命です。
  translation: 另一方面，我们不仅仅是幕后支撑，也有牵引和驱动作品开发的一面。研究开发团队会率先将新的表现形式和技术做成原型，然后向开发团队提案：“我们做出了这样的技术，要不要在下一款游戏里试试？”以技术为起点催生新的玩法，也是我们的重要使命。
  role: answer
- type: dialogue
  speaker: K.M.
  original: タイトル開発は3～4年のスパンで動く必要がありますが、私たちは5年～10年スパンで物事を考えなければなりません。「10年後のゲームフリークはどうあるべきか？」「その時、どんな技術が必要とされるか？」を常に意識しながら、先行投資としての技術開発を進めています。
  translation: 作品开发需要以3到4年的周期来推进，但我们必须以5年到10年的跨度来思考问题。我们始终意识到“10年后的GAME FREAK应该是什么样子？”“到那时，需要什么样的技术？”，并以此推进作为先行投资的技术开发。
  role: answer
- type: heading
  original: たった1人の入社、1人のアイデアで、組織を大きく変えることもできる。
  translation: 仅仅一位新人的加入、一个灵感的提出，就能彻底重塑整个组织的开发方式。
- type: image
  original: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-02-01.jpg
  translation: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-02-01.jpg
  caption: GAME FREAK 研发技术环境
- type: dialogue
  speaker: H.T.
  original: ゲームフリークのシステム開発は、まだまだ発展途上です。だからこそ、自分の意見や提案がダイレクトに通りやすい。大企業のように分業化が進みすぎて「自分の仕事がどこに役立っているか見えない」ということは一切ありません。たった1人のエンジニアが持ち込んだ新ツールが、全社標準になることだって珍しくないんです。
  translation: GAME FREAK的系统开发还处于发展阶段。正因如此，自己的意见和提案才更容易直接得到采纳。完全不会像大企业那样因为分工过于细化，而出现“看不到自己的工作在哪里发挥作用”的情况。仅仅一位工程师引入的新工具成为全公司标准，这种事也屡见不鲜。
  role: answer
- type: dialogue
  speaker: K.M.
  original: そうですね。裁量が非常に大きい。自分が「これが必要だ」と思ったら、自ら手を挙げてプロジェクトを立ち上げることができます。社内勉強会やR&Dの成果発表会も活発で、新しい技術への知的好奇心が強い人にとっては、これ以上なく刺激的な環境だと思います。
  translation: 是啊。裁量权非常大。只要自己觉得“这个有必要”，就可以主动举手发起项目。公司内部的学习会和研发成果发表会也很活跃，对于对新事物充满求知欲的人来说，这里无疑是再刺激不过的环境了。
  role: answer
- type: dialogue
  speaker: H.T.
  original: 近年はクラウド技術やCI/CDパイプラインの刷新、内製エンジンの強化など、エンジニアリング組織としての足腰を強める取り組みを加速させています。世界中の何千万人ものファンが熱狂するIPを技術で支えるというスケールの大きさと、ベンチャーのような機動力と意思決定の早さが共存しているのが、ゲームフリークの面白さですね。
  translation: 近年来，我们正在加速推进云技术、CI/CD流水线的革新、自研引擎的强化等，以增强作为工程组织的根基。用技术支撑起让全世界数千万粉丝为之狂热的IP，这种规模感，与类似初创企业般的机动性和决策速度并存，正是GAME FREAK的有趣之处。
  role: answer
- type: image
  original: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-02-02.jpg
  translation: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-02-02.jpg
  caption: 自由开放的技术研讨氛围
- type: dialogue
  speaker: K.M.
  original: 失敗を恐れずに挑戦できる文化もあります。「うまくいかなかったらどうしよう」と萎縮するのではなく、「ダメだったら次を試せばいい」という空気がある。研究開発において、失敗は次の成功のための貴重なデータですからね。
  translation: 这里还有一种不怕失败、勇于挑战的文化。不是畏缩地想着“搞砸了怎么办”，而是有一种“不行就再试下一个”的氛围。在研发中，失败是通向下一次成功的宝贵数据。
  role: answer
- type: heading
  original: 2030年代に向けて。ゲームフリークなら、誰もが変化の当事者になれる。
  translation: 面向2030年代。在 GAME FREAK，每一个人都能成为技术变革的主导者。
- type: image
  original: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-03.jpg
  translation: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-03.jpg
  caption: 眺望2030年代的系统架构愿景
- type: dialogue
  speaker: H.T.
  original: ゲームフリークが目指すのは、「世界一のゲーム制作集団」です。そのためには、システム基盤も世界トップクラスでなければなりません。既存のやり方に固執せず、常に変化を楽しみ、自ら組織や技術を変えていける仲間を求めています。
  translation: GAME FREAK的目标是成为“世界第一的游戏制作集团”。为此，系统基础也必须达到世界顶级水平。我们正在寻找不固守既有做法、始终乐于拥抱变化、能够主动改变组织与技术的伙伴。
  role: answer
- type: dialogue
  speaker: K.M.
  original: グラフィックス、物理シミュレーション、アニメーション、AI、ネットワーク、ビルドパイプライン……私たちが挑むべき技術領域は広大です。ゲーム業界の出身かどうかにかかわらず、「最高の体験を届けるために、自分の技術を極めたい」という熱い情熱を持った方と、ぜひ一緒に働きたいですね。
  translation: 图形渲染、物理模拟、动画、AI、网络、构建流水线……我们要挑战的技术领域非常广阔。无论是否出身于游戏行业，我们都非常希望能与那些怀揣着“为了给玩家带来最棒的体验，要把自己的技术磨炼到极致”这一热忱的人一起共事。
  role: answer
- type: dialogue
  speaker: H.T.
  original: 10年後のゲームフリークを作るのは、これから入社される皆さんです。ぜひその変化のプロセスそのものを、思い切り楽しんでほしいと思います。
  translation: 打造10年后GAME FREAK的，正是今后入职的各位。希望大家能尽情享受这个变化的过程本身。
  role: answer
display_title: 乐于拥抱持续变化的人，将塑造10年后的 GAME FREAK。
original_lang: ja
---
