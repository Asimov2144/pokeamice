---
layout: interview-editorial
archive_type: interview_translation
title: GAME FREAK 官方访谈 齿轮企划第2弹：Steam 物理破坏动作神作『GIGA WRECKER』开发秘话（M.O. × H.I.）
display_title: 员工访谈《GIGA WRECKER》
title_ja: ギアプロジェクト『GIGA WRECKER』開発秘話
date: 2017-01-28 10:00:00 +0900
era: '2017'
categories:
- developer-interviews
- gamefreak-recruit
tags:
- Game Freak
- Gear Project
- 齿轮企划
- GIGA WRECKER
- Steam
- 物理引擎
- 物理破坏解谜
- Indie Stream
- 招聘访谈
- Wayback历史存档
publication: Game Freak 採用情報 (Wayback 历史存档)
original_link: https://www.gamefreak.co.jp/recruit/interview_01.html
source_url: https://web.archive.org/web/20170128021506/https://www.gamefreak.co.jp/recruit/interview_01.html
source:
  title: ギアプロジェクト『GIGA WRECKER』開発秘話
  url: https://www.gamefreak.co.jp/recruit/interview_01.html
  language: ja
  source_type: official_interview
author: Game Freak 採用チーム
interviewee: M.O.、H.I.
original_lang: ja
translation_lang: zh-CN
translator: PokeAmice（DeepSeek 初译）
summary: 2016年8月《GIGA WRECKER》在Steam开启抢先体验。程序员M.O.与策划H.I.受访，讲述参加Gear Project的经过、物理引擎的运用、游戏看点和项目中的经验，以及今后的目标。
dek: 2016年8月《GIGA WRECKER》在Steam开启抢先体验，我们采访了发起该项目的程序员M.O.和策划H.I.。
entities:
  people:
  - M.O.
  - H.I.
  works:
  - GIGA WRECKER
  - TEMBO THE BADASS ELEPHANT
  - 宝可梦 黑·白
  - 宝可梦 X·Y
  - Gear Project（齿轮企划）
  organizations:
  - 株式会社ゲームフリーク
  - Steam（Valve）
recruit:
  page: interview_01
  version: '2017-01-28'
  capture: '20170128021506'
  date_basis: 同一网址 2016-11-22 的快照仍是《TEMBO》的访谈，2017-01-28 已是这一篇
parallel_items:
- type: image
  src: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/keyvisual.png
- type: text
  original: '2016年8月にSteamで早期アクセス版を配信開始した『GIGA WRECKER』。

    ギアプロジェクトとしてこのゲームを立ち上げたプログラマのM.O.とプランナーのH.I.に話を聞きました。'
  translation: 2016年8月，《GIGA WRECKER》在Steam上开始发行抢先体验版。我们采访了作为Gear Project发起这款游戏的程序员M.O.和策划H.I.。
- type: heading
  level: 2
  original: 社員紹介
  translation: 员工介绍
- type: image
  src: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/profile_01.png
  caption: J.T. デザイナー
- type: image
  src: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/profile_02.png
  caption: T.M. 3Dグラフィックデザイナー
- type: text
  original: '2010年に、新卒で入社したプログラマ&プランナーです。

    『ポケットモンスターブラック・ホワイト』から『ポケットモンスター』シリーズに携わり、その後ギアプロジェクトに手を挙げて、現在『GIGA WRECKER』を開発しています。'
  translation: 2010年以应届生身份入职的程序员兼策划。从《宝可梦 黑·白》开始参与《宝可梦》系列，之后主动报名参加Gear Project，目前正在开发《GIGA WRECKER》。
- type: heading
  level: 2
  original: 同期で組んでギアプロジェクトに参加
  translation: 同期搭档参加Gear Project
- type: heading
  level: 3
  original: どういった経緯でギアプロジェクトに参加しようと思ったのですか？
  translation: 你们是经过怎样的过程决定参加Gear Project的？
- type: text
  speaker: M.O.
  speaker_orig: M.O
  original: 私達が入社した2010年は、ちょうどギアプロジェクト制度が運用を開始した年なんです。その頃から参加したいとは思っていたのですが、まずは『ポケットモンスター』シリーズで完全新作を丸々一本経験してからにしよう、と。『ポケットモンスター X・Y』が終わったら募集があると聞いていたので、それに参加したくて、一緒にやろうとH.I.に声をかけました。
  role: answer
  translation: 我们入职的2010年，正好是Gear Project制度开始运行的那一年。当时我就想参加，但觉得还是先在《宝可梦》系列里完整经历一款全新作品之后再说。听说《宝可梦 X·Y》结束后会招募，我想参加，就邀请H.I.一起做。
- type: text
  speaker: H.I.
  speaker_orig: H.I
  original: 私は一度新規タイトルも開発してみたいな、くらいの軽い気持ちで。『ポケットモンスター X・Y』の終盤からゲーム完成リフレッシュ休暇のときに2人で話して新規タイトル案を練り始めました。
  role: answer
  translation: 我嘛，就是觉得想试着开发一款新作品，心态比较轻松。从《宝可梦 X·Y》后期到游戏完成后的焕然一新假期期间，我们两个人聊着聊着就开始构思新作品的方案了。
- type: text
  speaker: M.O.
  speaker_orig: M.O
  original: 'ディレクターは私ということになっていますが、今のゲームシステムの根幹となる着想がどちらから出たかも定かではないぐらい2人で練り上げた感じです。

    私はとにかく物理エンジンを使ってしっかりしたゲームを作ってみたいという気持ちがあって。物理エンジンは学生の時からかじっていたのですが、その頃の作品はもちろん製品レベルではないですから、改めて完成したものを作りたいと考えていました。'
  role: answer
  translation: 虽然总监名义上是我，但就连现在游戏系统的核心构想是谁先提出的都不太确定，感觉是两个人一起琢磨出来的。我反正就是很想用物理引擎做一款扎实的游戏。物理引擎我从学生时代就开始接触，但当时的作品当然达不到产品级别，所以我想重新做出一款完成度高的作品。
- type: image
  src: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/photo_01.png
- type: text
  speaker: H.I.
  speaker_orig: H.I
  original: 私はロボットが出てくるゲームが作りたいと思って、前からいろいろネタを考えていました。単純にロボットが好きでして。
  role: answer
  translation: 我想做一款有机器人出场的游戏，之前就一直在想各种点子。纯粹是因为我喜欢机器人。
- type: heading
  level: 2
  original: 物理エンジンの活用
  translation: 物理引擎的运用
- type: heading
  level: 3
  original: どのような経緯で今の形になったのですか？
  translation: 经过怎样的过程变成了现在的形式？
- type: image
  src: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/photo_02.png
- type: text
  speaker: H.I.
  speaker_orig: H.I
  original: 当初の企画では主人公は磁力を操る超能力を持っていて、壊したロボットの破片を集められる、という設定でした。それをデザイナーに伝えて、今につながるメインビジュアルを決定しました。
  role: answer
  translation: 当初的企划中，主角拥有操控磁力的超能力，可以收集破坏掉的机器人的碎片，是这样的设定。把这个告诉设计师后，决定了延续至今的主视觉图。
- type: text
  speaker: M.O.
  speaker_orig: M.O
  original: そのメインビジュアルがいかにも戦闘に向いている印象を与えるものだったので、最初はアクションゲームにしようと思っていたんですよ。物理エンジンも活かせますしね。
  role: answer
  translation: 那个主视觉图给人一种很适合战斗的印象，所以一开始是想做成动作游戏的。物理引擎也能派上用场。
- type: text
  speaker: H.I.
  speaker_orig: H.I
  original: パズルメインのゲームに変更したのは、『TEMBO THE BADASS ELEPHANT』と似てしまうから。「物を壊す快感を売りにしたアクションゲーム」を連続で発売するのはちょっとおもしろくないかな、と。
  role: answer
  translation: 改成以解谜为主的游戏，是因为会跟《TEMBO THE BADASS ELEPHANT》相似。连续发售“以破坏东西的快感为卖点的动作游戏”感觉有点没意思。
- type: text
  speaker: M.O.
  speaker_orig: M.O
  original: ターゲットハードも最初はゲーム専用機で考えていました。でも、何かとオブジェクトの制限が厳しくて、PCのほうがやりたい表現ができるということで、PC向けに方針転換しました。
  role: answer
  translation: 目标硬件最初也考虑的是游戏专用机。但是，各种物体的限制很严格，而PC能实现我们想做的表现，所以方针转向了PC。
- type: heading
  level: 3
  original: 『GIGA WRECKER』の見所は何ですか？
  translation: 《GIGA WRECKER》的看点是什么？
- type: text
  speaker: H.I.
  speaker_orig: H.I
  original: 物理エンジンを上手く活かせたと思います。
  role: answer
  translation: 我觉得是很好地运用了物理引擎。
- type: text
  speaker: M.O.
  speaker_orig: M.O
  original: INDIE STREAM AWARDS 2016のBest of TECHNICAL ARTSという賞を頂いています。物理エンジンをただ使うだけだとファジーな挙動になってしまいがちなのですが、そこをきちんと調整できているというところが評価されました。
  role: answer
  translation: 获得了INDIE STREAM AWARDS 2016的Best of TECHNICAL ARTS奖。物理引擎如果只是单纯使用，容易变成模糊的行为，而这一点我们调整得很好，得到了好评。
- type: heading
  level: 2
  original: ギアプロジェクトだからこそできる経験
  translation: 只有齿轮项目才能获得的经验
- type: heading
  level: 3
  original: ギアプロジェクトに参加するおもしろみと難しさを教えてください。
  translation: 请告诉我们参加齿轮项目的趣味和难点。
- type: text
  speaker: M.O.
  speaker_orig: M.O
  original: とにかく全部自分達でやらなければならないのが、おもしろくて、且つ難しいところです。『ポケットモンスター』シリーズなら、いかにおもしろくするか、のみ考えていればいいのですが、ギアプロジェクトだと、社外の方にプロモーションについて相談したり、しかもその相談を英語でしなければならなかったり。開発ではない仕事を経験できます。
  role: answer
  translation: 总之，所有事情都必须自己来做，这一点既有趣又困难。如果是《宝可梦》系列，只需要考虑如何做得有趣就行，但Gear Project的话，还得和公司外的人商量推广的事，而且商量还得用英语。能体验到非开发的工作。
- type: text
  speaker: H.I.
  speaker_orig: H.I
  original: '本当に何の制限もなく、新しいものを作ることにチャレンジできることが、単純にわくわくします。

    難しいのは、当たり前のことながら本当に知名度がないこと。なので、知名度を上げるような仕組みをゲーム内に入れようとしています。広告等を用いたマーケティングには造詣が深くないので、ゲームの中身で知名度を向上させなければならないんですよ。たとえば、今回マップエディタを入れたのは、それが目的です。マーケティングがゲームの内容や機能に還流してくる感じは、『ポケットモンスター』シリーズのいちプランナーとしてゲームを作っていただけでは、味わうことのないものでした。'
  role: answer
  translation: '真的没有任何限制，能挑战创造新东西，单纯让人兴奋。

    困难的是，理所当然地，真的毫无知名度。所以，我们正尝试在游戏内加入能提升知名度的机制。因为对利用广告等的营销并不擅长，所以必须通过游戏内容本身来提升知名度。比如，这次加入地图编辑器，就是为了这个目的。营销反馈到游戏内容和功能中的感觉，是作为《宝可梦》系列的一名策划制作游戏时，绝对体验不到的。'
- type: image
  src: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/photo_03.png
- type: heading
  level: 3
  original: これからやりたいことは何ですか？
  translation: 今后想做什么？
- type: text
  speaker: M.O.
  speaker_orig: M.O
  original: 私は今目の前のことで手一杯なんですが、ひとつ思っていることは、ギアプロジェクト間でのノウハウ共有を洗練させていきたいということですね。それを通して、ゲームフリークのギアプロジェクト全般をもっと盛り上げていきたいです。
  role: answer
  translation: 我现在光是应付眼前的事就忙不过来了，但有一个想法，就是想完善Gear Project之间的经验共享。通过这个，让GAME FREAK的Gear Project整体更加活跃。
- type: text
  speaker: H.I.
  speaker_orig: H.I
  original: 私はオリジナルタイトルをビジネスとして軌道に乗せて、シリーズ化したいです。理想論だと思われるかも知れませんが、第2の『ポケットモンスター』シリーズのようなゲームを創ることを、本気で目指しています。
  role: answer
  translation: 我想把原创作品作为业务走上正轨，并系列化。可能听起来像理想论，但我真心以创造出第二个《宝可梦》系列那样的游戏为目标。
interview_id: PKMN-1028
---
