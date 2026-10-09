---
layout: interview-editorial
archive_type: interview_translation
title: GAME FREAK 官方对谈 新人程序员篇：不是「只是实现」，而是「解决问题」（T.K. × R.H.）
display_title: 程序员说「做不到」，再好的点子也实现不了
title_ja: 新卒プログラマ対談｜採用情報
date: 2021-12-27 10:00:00 +0900
era: '2021'
categories:
- developer-interviews
- gamefreak-recruit
tags:
- Game Freak
- 招聘访谈
publication: Game Freak 採用情報
original_link: https://www.gamefreak.co.jp/recruit/crosstalk-new-programmer/
source_url: https://web.archive.org/web/20220425080732/https://www.gamefreak.co.jp/recruit/crosstalk-new-programmer/
source:
  title: 新卒プログラマ対談｜採用情報
  url: https://www.gamefreak.co.jp/recruit/crosstalk-new-programmer/
  language: ja
  source_type: official_interview
author: Game Freak 官方
interviewee: T.K.、R.H.
original_lang: ja
translation_lang: zh-CN
translator: PokeAmice（DeepSeek 初译）
summary: T.K.在《宝可梦 剑·盾》负责宝可梦露营小游戏，在《Pokémon LEGENDS 阿尔宙斯》担任玩家行为实现的主要负责人；R.H.隶属研究开发部，负责渲染相关工具开发和功能完善。两人谈到工具环境、跨岗位协作，以及从零开始挑战动作要素的经历，并强调程序员要持续学习、不轻易说做不到。
dek: 有专才，也有通才。能最大化这种团队实力的工具环境是什么样的。
entities:
  people:
  - T.K.
  - R.H.
  works:
  - 宝可梦 剑／盾
  - 宝可梦传说 阿尔宙斯
  organizations:
  - 株式会社ゲームフリーク
recruit:
  page: crosstalk-new-programmer
  version: '2022-04-25'
  capture: '20220425080732'
  date_basis: 招聘首页 2021-12-13 的快照还没有、2022-03-11 的已有，与策划对谈（首见 2022-01-25）同批；2025-03 起首页已不再列出
parallel_items:
- type: image
  src: /assets/img/interviews/gamefreak-crosstalk-new-programmer/mv.jpg
- type: profile
  speaker: T.K.
  speaker_orig: T.K.
  role_ja: 2018年新卒入社
  original: 『ポケットモンスター ソード・シールド』で「ポケモンキャンプ」のミニゲーム開発を担当。『Pokémon LEGENDS アルセウス』ではプレイヤー挙動実装の主担当となる。
  role: answer
  translation: 在《宝可梦 剑·盾》中负责「宝可梦露营」小游戏的开发。在《Pokémon LEGENDS 阿尔宙斯》中担任玩家行为实现的主要负责人。
  role_zh: 2018年应届入职
  avatar: /assets/img/interviews/gamefreak-crosstalk-new-programmer/member-tk.jpg
- type: profile
  speaker: R.H.
  speaker_orig: R.H.
  role_ja: 2019年新卒入社
  original: 専門学校卒業後、ゲームフリークへ入社。研究開発部に所属し、『Pokémon LEGENDS アルセウス』では主に描画周りのツール開発と機能整備を担当。
  role: answer
  translation: 专门学校毕业后入职GAME FREAK。隶属研究开发部，在《Pokémon LEGENDS 阿尔宙斯》中主要负责渲染相关工具开发和功能完善。
  role_zh: 2019年应届入职
  avatar: /assets/img/interviews/gamefreak-crosstalk-new-programmer/member-rh.jpg
- type: heading
  level: 3
  original: スペシャリストもいる。ジェネラリストもいる。そんなチーム力を最大化するツール環境とは。
  translation: 有专才，也有通才。能最大化这种团队实力的工具环境是什么样的。
- type: text
  speaker: T.K.
  speaker_orig: T.K.
  original: 私がゲームフリークに入社したのは、技術的な視点で『ポケットモンスター』シリーズがどのように作られているのか興味があったからです。2-3年スパンで新作が発売され、世界中で評価され続けている。その技術や、開発方法を吸収したいと思いました。
  role: answer
  translation: 我进GAME FREAK，是因为从技术角度对《宝可梦》系列是怎么做出来的感兴趣。新作两三年出一部，一直在全世界受到好评。我想吸收它的技术和开发方法。
- type: text
  speaker: R.H.
  speaker_orig: R.H.
  original: 私はインターンに参加した際、ちょっとした提案にプログラマやプランナーの皆さんが、ものすごい量のアイデアや意見を返してくれたことが印象に残り、成長できそうな環境だと思って入社しました。研究開発部は専門分野の技術に尖った先輩が多くて、まるで研究者みたいな人もいる。最新の技術をフォローし続けているので、常に学びがありますね。
  role: answer
  translation: 我参加实习的时候，自己提了个小建议，程序员和策划们就回了大量的点子和意见，这让我印象很深，觉得这里能让人成长，就入职了。研究开发部里在专业领域技术上很尖的前辈很多，还有人简直像研究者。他们一直在跟进最新技术，所以总有可学的东西。
- type: text
  speaker: T.K.
  speaker_orig: T.K.
  original: 研究開発部と比べると、タイトル開発側のプログラマはジェネラリストと言えるかもしれません。何かに特化しているというより、幅広く知識を備えてゲームを面白くするためには何でもやる人が多い。仕様策定に関わったり、企画書を書くプログラマもいますし、プロジェクトマネジメントまでやっている人もたくさんいます。
  role: answer
  translation: 和研究开发部相比，做具体作品的程序员也许可以说是通才。与其说专精某一样，不如说很多人知识面广，为了让游戏好玩什么都做。有人参与规格制定，有人写企划书，还有很多人连项目管理都做。
- type: text
  speaker: R.H.
  speaker_orig: R.H.
  original: 社内のコミュニケーションもとても活発ですよね。プランナーからの相談をタイトル側のプログラマを通して受けたり、デザイナーとツールについての話をしたり。一人で黙々と作業するのは最終段階だけで、実はチームプレーが多い仕事だと思います。
  role: answer
  translation: 公司内部的沟通也很活跃。策划的咨询会通过做具体作品的程序员传过来，也会和设计师聊工具的事。一个人闷头干活只在最后阶段，其实这工作团队协作的部分很多。
- type: text
  speaker: T.K.
  speaker_orig: T.K.
  original: 1人で作っていると何が正解なのか分からなくなることも多いので、やっぱり相談は大切ですよね。プロジェクト開始時にはキックオフMTGをしますし、動き出してからもプランナーやデザイナーと話し合って、仕様を調整していきます。ツールでいうと、会議はGoogleカレンダーで設定してGoogle Meetで。議事録や仕様書はConfluenceに集約して残しています。細かい相談事は、Slackもしくは口頭で随時やり取りしています。
  role: answer
  translation: 一个人做的话，很多时候会搞不清什么才是对的，所以商量还是很重要的。项目开始时会开kick-off会议，动起来之后也会和策划、设计师讨论，调整规格。工具方面，会议用Google日历安排，用Google Meet开。会议记录和规格书汇总保存在Confluence里。细碎的商量用Slack或者口头随时沟通。
- type: text
  speaker: R.H.
  speaker_orig: R.H.
  original: 進捗管理にはJiraを使っています。研究開発部では毎月のようにリリースがあるので、スケジュール管理がとても重要です。私たちがまずツールの機能を作らないことには、ゲーム作りが始まらないというケースも多いので。自分の工数を正確に見積もれないと、他の人の業務に影響を与えてしまいます。常に仕事の優先度を考えて、調整するクセがつきましたね。
  role: answer
  translation: 进度管理用Jira。研究开发部每个月都有发布，所以日程管理非常重要。很多时候我们不先把工具功能做出来，游戏制作就没法开始。如果自己的工时估不准，就会影响到别人的工作。我养成了随时考虑工作优先级并做调整的习惯。
- type: image
  src: /assets/img/interviews/gamefreak-crosstalk-new-programmer/img-01.jpg
- type: heading
  level: 3
  original: ゼロからの挑戦の連続。アクション要素を取り入れた『Pokémon LEGENDS アルセウス』。
  translation: 从零开始的挑战接连不断。加入了动作要素的《Pokémon LEGENDS 阿尔宙斯》。
- type: text
  speaker: T.K.
  speaker_orig: T.K.
  original: 『Pokémon LEGENDS アルセウス』は、これまでゲームフリークが培ってきた経験をそのまま転用することができず、ゼロから積み上げるような新しい挑戦の連続でした。フィールドの規模も大きくなったし、オブジェクトも増えた。物理挙動やAIを安定して処理するためにHavokを導入したのですが、使いこなしていくために研究開発部と協力して調査していきました。
  role: answer
  translation: 《宝可梦传说 阿尔宙斯》没法直接沿用GAME FREAK以往积累的经验，是从零开始积累，接连面对新的挑战。场景规模变大了，物体也增多了。为了稳定处理物理行为和AI，我们引入了Havok，为了用好它，和研究开发部合作进行了调查。
  note: Havok是用于物理模拟和AI的中间件。
- type: text
  speaker: R.H.
  speaker_orig: R.H.
  original: 私は初期のワークフロー構築の段階から関わり、エフェクト作成ツールを作ったり、SDKの研究をして使いやすいように工夫したりしていました。ツールを実装し終わった後もプログラマやデザイナーからの要望に合わせて改修やサポートを続けて、リリースまでずっと伴走し続けたという感じです。継続的に使って見つかる改善点や不具合も多いので、随時フィードバックをもらえるのは開発者としても嬉しいですね。
  role: answer
  translation: 我从初期构建工作流的阶段就参与进来，制作特效创建工具，研究SDK并想办法让它更好用。工具实现后也根据程序员和设计师的需求继续修改和支持，感觉一直陪跑到发布。持续使用会发现很多改进点和问题，能随时收到反馈，作为开发者也很高兴。
- type: image
  src: /assets/img/interviews/gamefreak-crosstalk-new-programmer/img-02-01.jpg
- type: text
  speaker: T.K.
  speaker_orig: T.K.
  original: 私からR.H.さんに機能に関する要望を出したこともありましたね。システムのことだからと研究開発部に任せっきりにするのではなく、最後まで一緒に作り上げていったのが『Pokémon LEGENDS アルセウス』ならではの経験でした。大変なことが多かったですが、同時にこれまでにない大きなやりがいもありました。
  role: answer
  translation: 我也向R.H.提出过关于功能的需求。不是因为是系统的事就全交给研究开发部，而是直到最后都一起完成，这是《宝可梦传说 阿尔宙斯》独有的经验。虽然辛苦的事很多，但同时也有前所未有的巨大价值。
- type: text
  speaker: R.H.
  speaker_orig: R.H.
  original: T.K.さんはプレイヤー挙動のメイン担当だったから色々な苦労があったと思います。私は断片的にツールや機能を開発しているのでゲームの全体像は見ていなくて、最後に出来上がったゲーム内の派手なエフェクトを、「これ、根幹は自分がやったんだよな〜」と密かに嬉しく思いながら見ていました。
  role: answer
  translation: T.K.是玩家行为的主要负责人，我想他吃了不少苦。我因为只零散地开发工具和功能，没看游戏的整体，最后看到游戏里华丽的特效时，会暗自高兴地想“这核心部分是我做的啊”。
- type: text
  speaker: T.K.
  speaker_orig: T.K.
  original: 最初期はHavokの物理を全く制御できず、キャラクターを坂に立たせたいのにどこまでも滑って飛んで行ってしまいました。そこから始まったことを考えると、本当に感動しますね。開発途中ではカクカクした動きに心配になったこともありましたが、最終的には処理負荷を抑えてきれいなビジュアルとアクションになりました。ブラッシュアップできる間にできることは全部やろう！と、後悔がないレベルに到達できました。ユーザーの方々に楽しんでもらえるクオリティになったと思います。
  role: answer
  translation: 最初完全无法控制Havok的物理，想让角色站在坡上，结果却一直滑着飞出去。想到是从那种状态开始的，真的很感动。开发途中也担心过动作卡顿，但最终在抑制处理负荷的同时实现了漂亮的视觉效果和动作。在能打磨的期间把能做的都做了！达到了没有遗憾的程度。我觉得品质已经能让用户享受了。
- type: image
  src: /assets/img/interviews/gamefreak-crosstalk-new-programmer/img-02-02.jpg
- type: heading
  level: 3
  original: 「ただ実装する」のではなく「課題を解決する」。そのために、業界最先端を目指し、学び続ける。
  translation: 不是“只是实现”，而是“解决问题”。为此，要瞄准业界最前沿，持续学习。
- type: text
  speaker: R.H.
  speaker_orig: R.H.
  original: プログラマとして大切にしているのは、ただ要望のまま実装しないということです。例えば、グラフィックデザイナーから「こんな機能がほしい」という相談が来たとします。その場合、どういう経緯でそれが必要になったのかを深く掘り下げるようにしています。そうすると、当初の要望とは全く違う解決策を提案できることがよくあるんです。「実装する」というより、「課題を根っこから解決する」という意識が大事ですね。
  role: answer
  translation: 作为程序员，我重视的是不按需求直接实现。比如，图形设计师来商量“想要这样的功能”。这种情况下，我会深入挖掘为什么需要它。这样常常能提出和当初需求完全不同的解决方案。比起“实现”，我觉得“从根源解决问题”的意识很重要。
- type: text
  speaker: T.K.
  speaker_orig: T.K.
  original: 対話を何回も繰り返しながら作っていく感じですよね。開発初期にプランナーとプログラマとグラフィックデザイナーが集まって、実装キックオフMTGを開きます。プランナーの仕様書と企画意図を元に各職種の観点から、「それを実現したいなら、こういう実装にした方がいい」とアイデアを出して、実現するためにはどうすれば良いのか分担を決めていきます。仕様書も、内容によってはプログラマやグラフィックデザイナーが書く場合もあります。本当に職種の垣根なく相談ができる、フラットな環境です。
  role: answer
  translation: 感觉是在反复对话中制作。开发初期，策划、程序员和图形设计师会聚在一起，召开实现启动会议。基于策划的规格书和企划意图，从各岗位的角度提出“如果想实现那个，这样做实现更好”的想法，并决定为了实现该如何分工。规格书根据内容，有时也会由程序员或图形设计师来写。真的是能不分岗位界限商量事情的扁平环境。
- type: text
  speaker: R.H.
  speaker_orig: R.H.
  original: これからは、プロジェクトの中で何かやりたいことが出てきた時に、真っ先に相談してもらえるプログラマになりたい。そのために最新の技術を追い続け、勉強し続けたいですね。困った時に研究開発部の先輩たちに相談すると、必ず何か解決案をくれるんです。いろいろなバックグラウンドを持つ優秀な先輩に囲まれて、すごく恵まれた環境だと思います。いつ先輩たちの領域まで到達できるか分かりませんが、自分も頼られる存在を目指し続けたいですね。
  role: answer
  translation: 今后，我想成为在项目中出现想做的事时，能最先被咨询的程序员。为此，我想持续追踪最新技术，不断学习。遇到困难时和研究开发部的前辈商量，他们一定会给出某种解决方案。被拥有各种背景的优秀前辈包围，我觉得是非常幸运的环境。虽然不知道什么时候能到达前辈们的领域，但我也想继续以被依赖的存在为目标。
- type: text
  speaker: T.K.
  speaker_orig: T.K.
  original: やっぱり勉強熱心であることがプログラマの条件ですよね。今まで自分が身につけていない技術でも恐れず、学べる人がいい。私自身、「ゲームフリークの技術を業界の最先端と言われるレベルまで押し上げたい」という気持ちはすごく強いですね。ゲーム作りって、プログラマが「無理」と言ってしまうとどんな素晴らしいアイデアも無理になってしまうんです。だからこそ簡単に諦めずに、何とかできる方法を粘り強く考えて、勉強して。絶対に「無理」と言わないプログラマを目指したいですし、そういう人に入社してもらいたいですね。
  role: answer
  translation: 果然好学是程序员的条件。即使是自己没掌握的技术也不害怕，能学习的人更好。我自己“想把GAME FREAK的技术提升到被称为业界最前沿的水平”这种想法非常强烈。做游戏，如果程序员说“做不到”，再好的点子也会变得不可能。所以不要轻易放弃，要顽强地思考能做到的方法，去学习。我想以绝对不说“做不到”的程序员为目标，也希望这样的人入职。
- type: image
  src: /assets/img/interviews/gamefreak-crosstalk-new-programmer/img-03.jpg
era_skin: '2019'
---
