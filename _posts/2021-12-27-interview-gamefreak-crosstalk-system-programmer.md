---
layout: interview-editorial
archive_type: interview_translation
title: GAME FREAK 官方对谈 系统程序员篇：乐于拥抱持续变化的人，将塑造10年后的 GAME FREAK
display_title: 乐于拥抱持续变化的人，将塑造10年后的 GAME FREAK。
title_ja: システムプログラマ対談：変化を楽しみ続ける人が、10年後のゲームフリークを作る。
date: 2024-02-13 10:00:00 +0900
era: '2024'
categories:
- interviews
- gamefreak-recruit
tags:
- Game Freak
- 招聘对谈
- 系统程序员
- 底层架构
- 自研引擎
- CI/CD
- 工具链
- 跨界挑战
- 招聘访谈
publication: Game Freak 採用情報
original_link: https://www.gamefreak.co.jp/recruit/crosstalk-system-programmer/
source_url: https://web.archive.org/web/20240229104144/https://www.gamefreak.co.jp/recruit/crosstalk-system-programmer/
source:
  title: システムプログラマ対談｜採用情報
  url: https://www.gamefreak.co.jp/recruit/crosstalk-system-programmer/
  language: ja
  source_type: official_interview
author: Game Freak 官方
interviewee: K.M.、J.I.、H.T.
original_lang: ja
translation_lang: zh-CN
translator: PokeAmice（DeepSeek 初译）
summary: 研究开发部三位总监对谈。他们分别来自大型游戏公司、自由职业和AI初创企业，负责渲染、AI、环境等方向，介绍系统程序员优化开发环境、支撑作品开发的工作，以及公司即决即行、建议门槛低、职位可无限增加的文化。
dek: 来自不同行业的系统程序员，讲述为制作前所未有的新游戏而进化开发环境的工作。
entities:
  people:
  - K.M.
  - J.I.
  - H.T.
  works:
  - 宝可梦传说 阿尔宙斯
  - 宝可梦 朱·紫
recruit:
  page: crosstalk-system-programmer
  version: '2024-02-29'
  capture: '20240229104144'
  date_basis: 页面素材批次 ?20240213；Wayback 首见 2024-02-29，2022-10-15 的招聘首页还没有这一篇
parallel_items:
- type: image
  src: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/mv.jpg
- type: profile
  speaker: K.M.
  speaker_orig: K.M.
  role_ja: 2018年入社
  original: 大手ゲームメーカーで描画プログラマを務めた後、技術研究の道を模索する中でゲームフリークと出会う。研究開発部 副部長。描画、アニメーション、テクニカルアーティストを統括するCGテクノロジーラボ ディレクター。
  role: answer
  translation: 在大型游戏公司担任渲染程序员后，在探索技术研究道路的过程中结识了GAME FREAK。研究开发部副部长。统管渲染、动画、技术美术的CG技术实验室总监。
  role_zh: 2018年入职
  avatar: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/member-km.jpg
- type: profile
  speaker: J.I.
  speaker_orig: J.I.
  role_ja: 2020年入社
  original: 研究開発だけでなく、タイトル開発にも携わりたいという思いからゲームフリークへ。研究開発部 AIセクションを設立し、セクションディレクターに就任。開発二部のプログラマセクションディレクターも兼務。
  role: answer
  removed_on: '2025-06-15'
  translation: 因为希望不仅从事研究开发，也能参与作品开发，所以加入了GAME FREAK。设立了研究开发部AI部门，并担任部门总监。同时兼任开发二部的程序员部门总监。
  role_zh: 2020年入职
  avatar: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/member-ji.jpg
- type: profile
  speaker: H.T.
  speaker_orig: H.T.
  role_ja: 2019年入社
  original: 新卒でゲーム会社に入社後、フリーランスとして独立して数社のモバイルゲーム開発を経験。AIスタートアップのCOOを経て、ゲームフリークへ。研究開発部 環境セクションのセクションディレクターを務める。
  role: answer
  translation: 应届毕业后进入游戏公司，之后作为自由职业者独立，经历了多家公司的手机游戏开发。在AI初创企业担任COO后，加入了GAME FREAK。担任研究开发部环境部门的部门总监。
  role_zh: 2019年入职
  avatar: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/member-ht.jpg
- type: heading
  level: 3
  original: 最高のゲームを作るための、最高の開発環境を作る。異業種からの挑戦も、大歓迎。
  translation: 为了制作最好的游戏，打造最好的开发环境。来自不同行业的挑战，也大受欢迎。
- type: text
  speaker: K.M.
  speaker_orig: K.M.
  original: ゲームタイトルそのものの開発を担当するというより、今までにない新しいゲームを作るために開発環境を進化させる。それが、私たちシステムプログラマのミッションです。最先端の技術を取り入れ、新技術を自ら開発し、それをゲーム開発に活用できるように仕組み化していきます。
  role: answer
  translation: 与其说是负责游戏作品本身的开发，不如说是为了制作前所未有的新游戏而进化开发环境。这就是我们系统程序员的使命。引进最先进的技术，自行开发新技术，并将其机制化以便应用于游戏开发。
- type: text
  speaker: H.T.
  speaker_orig: H.T.
  original: ゲームプログラマには遊びについても考えるプランナー的な要素も求められますが、システムプログラマは必ずしもそうではありません。また、私も含め異業種からの転職者が多いのも特徴的です。AIや機械学習、クラウドなど、何かしらの専門分野で強みを持った人が活躍しているイメージですね。
  role: answer
  translation: 游戏程序员也需要有策划般的要素，去思考玩法，但系统程序员未必如此。另外，包括我在内，从其他行业转职过来的人很多，这也是一个特点。感觉是在AI、机器学习、云等某个专业领域有优势的人在这里大显身手。
- type: text
  speaker: J.I.
  speaker_orig: J.I.
  original: 縁の下の力持ちとして、高品質なゲーム作りを支えるのが、私たちの役割です。できる限り高性能なPCを用意し、開発ツールを作り込み、ギリギリまでエンジンの最適化を行う。「開発環境やシステムがよければ、もっと面白いゲームが作れるのに」なんて言い訳は絶対にさせない。それくらいの意気込みで臨んでいます。
  role: answer
  removed_on: '2025-06-15'
  translation: 作为幕后支持者，支撑高品质的游戏制作，是我们的职责。尽可能准备高性能的PC，精心制作开发工具，对引擎进行极限优化。绝不允许有人说“如果开发环境或系统更好的话，就能做出更有趣的游戏了”这种借口。我们就是以这样的决心来面对的。
- type: text
  speaker: H.T.
  speaker_orig: H.T.
  original: 一方で、縁の下で支えるだけではなく、タイトル開発を引っ張り、ドライブさせていく側面もありますよね。研究開発部だからといって、プロジェクトに関わらないわけではない。むしろ密接に関わって、一緒にタイトルを作り上げています。
  role: answer
  translation: 另一方面，不仅仅是幕后支持，也有引领和推动作品开发的一面。虽说属于研究开发部，但并非不参与项目。反而是密切参与，共同打造作品。
- type: text
  speaker: J.I.
  speaker_orig: J.I.
  original: タイトル開発は2～3年のスパンで動く必要がありますが、私たちは5年～10年スパンで物事を考えなければいけない。短期では実現できない技術やアイデアにも挑めるのが、研究開発部として独立していることの意義なのかなと思いますね。
  role: answer
  removed_on: '2025-06-15'
  translation: 作品开发需要在2到3年的跨度内推进，但我们必须以5年到10年的跨度来思考事情。能够挑战短期无法实现的技术和想法，这或许就是研究开发部独立存在的意义吧。
- type: image
  src: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-01.jpg
- type: heading
  level: 3
  original: たった1人の入社、1人のアイデアで、組織を大きく変えることもできる。
  translation: 仅凭一个人的入职、一个人的想法，也能大大改变组织。
- type: text
  speaker: K.M.
  speaker_orig: K.M.
  original: 「こんな機能がほしい」という要望は、全社横断的に各プロジェクトのディレクターと会議をして、優先度を決めて実装しています。実際に機能を使うのはプロジェクトだから当事者同士で要望をすり合わせるべきだ、と、J.I.さんの発案で始めました。「こうしてみたら」というアイデアに対して、「いいね！」と賛同する人が積極的に動けば、組織はどんどん変わっていきます。
  role: answer
  removed_on: '2025-06-15'
  translation: “希望有这样的功能”这类需求，会由全公司跨部门与各项目的总监开会，决定优先级后再实现。实际使用功能的是项目，所以应该由当事者之间来协调需求，这是J.I.提议开始的。对于“这样试试看”的想法，如果有人赞同说“不错！”并积极行动，组织就会不断改变。
- type: text
  speaker: H.T.
  speaker_orig: H.T.
  original: 「前の会社ではこうしたらうまくいったよ」という知見を持っている人に、ぜひ来てほしいですね。実際、中途入社の方のワークフローを取り入れて、あらゆる場所で改善が進んでいる。意思決定が早くて、即決・即実行するカルチャーがありますから。
  role: answer
  translation: 希望有“在前公司这样做很顺利”这类经验的人一定要来。实际上，引入中途入职者的工作流后，各方面都在改善。因为决策快，有即决即行的文化。
- type: text
  speaker: K.M.
  speaker_orig: K.M.
  original: ただそこでも、自らの意志を持って説明できることが重要ですよね。「前の会社ではこうでしたよ」と表面的な話で終わるのではなく、「なぜそうしていたのか？」という本質まではっきりと伝えられないといけません。
  role: answer
  removed_on: '2025-06-15'
  translation: 但即便如此，能够带着自己的意志去说明也很重要。不能只说“前公司是这样的”这种表面话，必须把“为什么那样做”的本质也清楚地传达出来。
- type: text
  speaker: J.I.
  speaker_orig: J.I.
  original: 逆に言えば、仕事の進め方に明確な問題意識を持って提案をしていたけれど、様々な要因で提案が通らなかった人、悔しい想いをしていた人にとっては、ゲームフリークは最高の環境だと思います。「こんな提案、コストがかかり過ぎるから通らないだろうな」と思っていても、メリットを伝えられたら驚くほどあっさり通りますから。提案を実行するハードルは極めて低い。その代わり、「やりたいけれど予算がないから」という言い訳はできませんけど（笑）
  role: answer
  translation: 反过来说，对于那些对工作推进方式有明确问题意识并提出建议，但因各种原因建议没被采纳、感到不甘心的人来说，GAME FREAK是最好的环境。即使觉得“这样的建议成本太高，应该通不过吧”，只要能说明好处，就会意外地轻易通过。执行建议的门槛极低。但相应的，不能找“想做但没预算”这种借口（笑）。
- type: text
  speaker: K.M.
  speaker_orig: K.M.
  original: 組織体制も固定されているわけではないので、例えばリーダーの資質のある人が入ってきたら、その人をリーダーに据えて新たなチームを作れる。会社の課題解決に繋がるなら、ポジションはいくらでも増やせます。上が詰まっているから昇進できないということはないので、キャリア志向の方も安心してください。
  role: answer
  removed_on: '2025-06-15'
  translation: 组织体制也不是固定的，比如有领导素质的人进来，就可以让他当领导组建新团队。如果能有助于解决公司课题，职位可以无限增加。不会因为上面堵着就升不上去，所以有志于职业发展的人也可以放心。
- type: image
  src: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-02-01.jpg
- type: image
  src: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-02-02.jpg
- type: heading
  level: 3
  original: 2030年代に向けて。ゲームフリークなら、誰もが変化の当事者になれる。
  translation: 面向2030年代。在GAME FREAK，任何人都能成为变化的当事者。
- type: text
  speaker: K.M.
  speaker_orig: K.M.
  original: 研究開発部が誕生した頃から比べると、メンバーも増え、開発環境も整ってきました。『ポケットモンスター』シリーズの開発に最適化された独自の取り組みに注力しています。「他社はやらないだろうけれど、将来のゲームフリークと『ポケモン』シリーズには必ず必要」という仕組みや技術。まさに2030年代に向けたチャレンジです。
  role: answer
  translation: 与研发部诞生时相比，成员增加了，开发环境也完善了。我们专注于为《宝可梦》系列开发优化的独特举措。那些“其他公司不会做，但未来的GAME FREAK和《宝可梦》系列必定需要”的机制和技术。这正是面向2030年代的挑战。
- type: text
  speaker: H.T.
  speaker_orig: H.T.
  original: 私のセクションはインフラと強い繋がりがあって、クラウドシフトを継続して進めています。今後はそれをさらに推進し、少ない人員でも効率的に各プロジェクトに環境提供できる体制を作りたいですね。最小効率で最大インパクトを出せるチームが理想です。
  role: answer
  translation: 我的部门与基础设施紧密相关，正在持续推进云迁移。今后要进一步推进，建立即使人员少也能高效为各项目提供环境的体制。理想是能以最小效率产生最大影响的团队。
- type: text
  speaker: J.I.
  speaker_orig: J.I.
  original: 効率化に向けたプロジェクトを多方面で進めているので、そこに注力できる人は直近では重宝されますよね。ただし、そのプロジェクトが成功した後にまた新しい課題を見つけられないといけない。ゲームフリークのめざす理想の姿に『完成』はありません。目の前の課題をクリアしてもすぐに、また新しい課題が立ちふさがる。それを楽しめる人に来てほしいですね。
  role: answer
  removed_on: '2025-06-15'
  translation: 因为正在多方面推进效率化的项目，能专注于此的人近期会很受重视。但是，那个项目成功后，必须能发现新的课题。GAME FREAK所追求的理想形态没有“完成”。即使解决了眼前的课题，马上又会有新课题挡在面前。希望享受这个过程的人来。
- type: text
  speaker: K.M.
  speaker_orig: K.M.
  original: 「ずっと同じことをやり続けるのが安心」というタイプは向いていないかもしれませんね。むしろ、「それは去年やったからもういいや」と、新しいことに貪欲な人がいい。加えて、「すごい会社に入って、自分のスキルを高めていこう」という人よりは、「自分の力でもっとすごい会社にしてやろう」「ここが未成熟だから自分が入ってなんとかしてやろう」というくらいのマインドが必要なのだと思います。
  role: answer
  removed_on: '2025-06-15'
  translation: “一直做同样的事才安心”这种类型可能不适合。反倒是“那个去年做过了，算了”这样对新事物贪婪的人更好。而且，比起“进了厉害的公司，提升自己的技能”的人，更需要“靠自己的力量让公司变得更厉害”“这里还不成熟，我进来想办法解决”这种心态。
- type: text
  speaker: H.T.
  speaker_orig: H.T.
  original: まさにそうですね。例えばいちメンバーであっても、「自分がマネージャーだったら、ディレクターだったらどう考えるか」と、問題意識を持って行動できる人が活躍しています。技術面でも、AIやWEB業界も急速に発展しているので、そうした技術をどんどん取り込んで会社への提案に結び付けていってほしいですね。
  role: answer
  translation: 确实是这样。比如说，就算只是一名普通成员，也有人会带着问题意识去行动，思考“如果我是经理、是总监，会怎么想”，这样的人很活跃。技术方面，AI和WEB行业也在快速发展，希望大家能不断吸收这些技术，并把它和向公司提建议结合起来。
- type: text
  speaker: K.M.
  speaker_orig: K.M.
  original: 新卒とか中途とか入社年次に関係なく、説得力のある提案は即採用される。ゲームフリークなら、誰もが変化の当事者になれるんです。目まぐるしいほどの変化を楽しみ、その可能性にワクワクできる人に来てほしい。10年後のゲームフリークを共に作ってくれる仲間をお待ちしています。
  role: answer
  translation: 不管是应届还是中途入职，也不管入职年份，只要有说服力的建议就会被立刻采纳。在GAME FREAK，谁都可以成为变化的当事者。希望来的是能享受这种眼花缭乱的变化、并对其可能性感到兴奋的人。期待能和我们一起打造10年后GAME FREAK的伙伴。
- type: image
  src: /assets/img/interviews/2021-gamefreak-crosstalk-system-programmer/img-03.jpg
era_skin: '2019'
---
