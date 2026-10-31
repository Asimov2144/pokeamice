---
archive_type: interview_translation
layout: interview-editorial
title: GAME FREAK 官方访谈 程序员篇：「环境构筑」与「玩法创造」（T.T. × M.I.）
title_ja: インタビュー どっち？ vol.1 プログラマー編 「環境づくり」と「遊びづくり」
date: 2013-10-20 10:00:00 +0900
recruit:
  page: interview_2
  version: '2013-12-28'
  capture: '20131228170851'
  date_basis: 招聘首页 2013-04-03 的快照还没有、2013-10-20 的已有（这一页 Wayback 首见 2013-12-28）；2016-11 至 2017-01 之间撤下
era: '2013'
categories:
- developer-interviews
- gamefreak-recruit
tags:
- 'Game Freak'
- '宝可梦 X·Y'
- '程序员'
- '3D渲染'
- 'Shader着色器'
- '开发管线'
- '座谈访谈'
- 'Wayback历史归档'
- '招聘访谈'
original_url: http://web.archive.org/web/20140209100018/http://www.gamefreak.co.jp/recruit/interview_2.html
outlet: Game Freak 官网招聘专栏 (Wayback Machine 历史归档)
interviewee: M.I., T.T.
interviewer: Game Freak 招聘采编团队
parallel_items:
- type: image
  original: /assets/img/interviews/2013-gamefreak-recruit-programmer/top_image.png
  translation: /assets/img/interviews/2013-gamefreak-recruit-programmer/top_image.png
  caption: GAME FREAK 招聘专题：程序员篇 「环境构筑」与「玩法创造」
- type: image
  original: /assets/img/interviews/2013-gamefreak-recruit-programmer/profile.png
  translation: /assets/img/interviews/2013-gamefreak-recruit-programmer/profile.png
  caption: 受访员工档案：T.T.（原野系统开发）与 M.I.（3D图形渲染研发）
- type: heading
  level: 2
  original: 「環境づくり」と「遊びづくり」
  translation: 「环境构筑」与「玩法创造」
- type: heading
  level: 3
  original: ―　お二人のことを教えてください。
  translation: ——能向我们介绍一下两位吗？
- type: image
  original: /assets/img/interviews/2013-gamefreak-recruit-programmer/pic_01.png
  translation: /assets/img/interviews/2013-gamefreak-recruit-programmer/pic_01.png
  caption: 探讨 3D 化变革中的程序开发与分工
- type: text
  speaker: T.T.
  speaker_orig: 'T.T:'
  original: 僕は新卒で入社して、今年で９年目になります。主にゲームの中での「遊び」をつくることをメインにやってきましたね。直近のプロジェクト（ポケットモンスターXY）ではフィールドリーダーとして様々な実験と管理を行っていました。
  translation: "我是应届毕业入职的，今年是第9年。主要一直在做游戏中的“玩法”。在最近的项目（《宝可梦 X·Y》）中，我作为Field（场景）组的组长，负责各种实验和管理。"
  role: answer
- type: text
  speaker: M.I.
  speaker_orig: 'M.I:'
  original: 私は2011年の中途入社です。前職は別のゲーム会社で３DグラフィックスのR&Dの部署で働いていました。現在は主に3Dモデルの描画等の表示制御のプログラムと、社内のゲーム制作環境の構築を行っています。
  translation: "我是2011年中途入职的。之前在另一家游戏公司的3D图形R&D部门工作。现在主要负责3D模型描画等显示控制的程序，以及公司内部游戏制作环境的搭建。"
  role: answer
- type: heading
  level: 3
  original: ―　Tさんは「遊び」、Iさんは「環境」を作っていたということですか？
  translation: ——这是否意味着T先生负责打造「玩法」，而I先生负责搭建「环境」呢？
- type: text
  speaker: T.T.
  speaker_orig: 'T.T:'
  original: いえ、厳密にそう分かれているわけではありません。僕も環境づくりは携わっていますよ。今後は少しずつ変わっていくと思いますが、ゲームフリークはプログラマー皆が「遊び」も「環境」も両方関わる開発体制でしたから。
  translation: 不，其实并没有分得那么绝对。我也参与了开发环境的搭建。虽说今后可能会逐步发生变化，但在此之前，GAME FREAK一直保持着每位程序员都同时深入参与「玩法」和「环境」两方面开发的工作体制。
  role: answer
- type: text
  speaker: M.I.
  speaker_orig: 'M.I:'
  original: 今回から個人ベースで少しずつ専門領域に分かれてきた感はありますね。僕自身は描画の環境に特化していますよ。
  translation: "从这次开始，感觉以个人为单位逐渐分出各自的专业领域了。我自己专门负责描画方面的环境。"
  role: answer
- type: text
  speaker: T.T.
  speaker_orig: 'T.T:'
  original: 僕は「遊び」を作りつつ環境構築も行っていた訳ですが、「環境」については反省が多いんです。今回がポケモンにとって初めてのフル３Dだったということで、「遊び」に関する実験のほうを重視してしまったんですよね。例えば3DSに発生する１フレームの遅れを解消する、とか。そういう「操作の気持ちよさ」をつくることに時間をかけていました。今まで通りの姿勢で今回の開発と向き合ってしまったかな、と。遊びたいと思った時に思う存分遊べるように、ユーザーのストレスを減らしていく。そういった部分では満足していますが、リソース環境の点では反省が多いです…。
  translation: "我一边做“玩法”，一边也在搭建环境，不过在“环境”方面我有很多反省。因为这次是宝可梦第一次完全3D化，我把重点放在了“玩法”相关的实验上。比如消除3DS上会出现的1帧延迟，等等。我花了很多时间去打造这种“操作的舒适感”。我想自己大概是用和以前一样的姿态面对了这次的开发。为了让玩家在想玩的时候能够尽情地玩，要减少玩家的压力。在这些方面我是满意的，但在资源环境方面有很多需要反省的地方……"
  role: answer
- type: text
  speaker: M.I.
  speaker_orig: 'M.I:'
  original: 要はバランスじゃないですかね。今後は環境もしっかり見ていこうと考えています。でないとゲームコンテンツを面白くする時間がなくなってもったいないですから。確かにゲームフリークは「遊び」を追求するほうが好きだという方が多いですし、驚くほど細かい部分まで拘って遊びをつくっていきますが、私は「環境づくり」が好きですよ。素晴らしい環境で、自分たちのパフォーマンスをしっかり出していい仕事する、そういうのって格好いいと思ってます（笑）。
  translation: "总之还是平衡吧。今后我想把环境也好好管起来。不然就没有时间把游戏内容做得有趣了，那就太可惜了。的确，GAME FREAK有很多人更喜欢追求“玩法”，会拘泥于令人吃惊的细节去制作玩法，但我喜欢“搭建环境”。在出色的环境里，充分发挥自己的实力，做出好的工作，我觉得这样很帅（笑）。"
  role: answer
- type: image
  original: /assets/img/interviews/2013-gamefreak-recruit-programmer/pic_02.png
  translation: /assets/img/interviews/2013-gamefreak-recruit-programmer/pic_02.png
  caption: 在 3D 技术转型中迎头赶上的技术团队
- type: heading
  level: 2
  original: ３Dコンテンツについては小学生だった？
  translation: "在3D内容方面曾是小学生？"
- type: text
  speaker: T.T.
  speaker_orig: 'T.T:'
  original: 本当に、Iさんが加入したことにより、表現の幅が広がったと思います。あのね、３Dのコンテンツを作るっていう意味において、ゲームフリークは小学生みたいなものだったと思うんですよ。もちろん中には３Dの技術に長けている人もいるけど、全体としてはね。それで現在は中途入社の方々が加わったり、外部の協力会社さんに入ってもらったりして社会人くらいにはなったんじゃないかなと思っています。
  translation: "真的是因为I先生加入，表现的幅度变宽了。那个啊，就制作3D内容而言，我觉得GAME FREAK以前就像小学生一样。当然其中也有擅长3D技术的人，不过整体上是这样。然后现在有中途入职的人加入，也请外部的合作公司参与进来，我想已经算是长到社会人的程度了吧。"
  role: answer
- type: heading
  level: 3
  original: ―　小学生だったんですか？
  translation: "——曾经是小学生吗？"
- type: text
  speaker: T.T.
  speaker_orig: 'T.T:'
  original: あくまで昔の話ですよ！最先端のフル３Ｄゲームと比較した時の話なので、誤解しないでくださいね（笑）。今までのポケモンにも３Ｄの要素はありましたが、世界観を守るために２Ｄの技術をベースとした作り方をしていたわけですから。ま、それでも一番しんどい部分は越えたと思っています。
  translation: "这终究是以前的事！这是和最先进的全3D游戏相比较而言的，请不要误会哦（笑）。以前的宝可梦也有3D的要素，但为了守护世界观，是以2D技术为基础来制作的。不过即便如此，我认为最辛苦的部分已经越过去了。"
  role: answer
- type: text
  speaker: M.I.
  speaker_orig: 'M.I:'
  original: 山は越えたでしょうね。これからは先々のことも視野に入れて作って行く開発体制になると思います。考えようによっては今から入る人にはすごくいいと思いますよ。チャンスが多くあるので、腕に自信のある方こそ、来てもらえばいいのかなぁって。
  translation: "应该是翻过山了吧。今后会变成把更长远的事情也纳入视野来制作的开发体制。从某种角度来说，我觉得对现在加入的人非常好。机会很多，所以我觉得正是对自己的本事有信心的人，才更适合来。"
  role: answer
- type: heading
  level: 3
  original: ―　何のチャンスでしょう？
  translation: ——指的是怎样的机会呢？
- type: text
  speaker: M.I.
  speaker_orig: 'M.I:'
  original: 自分が持っている知識スキルがあったとして、それを活かせるチャンスです。プロジェクトの指針が示された後は、かなり自由にやっていいんですよ。だから自分なりに考え抜いたことが実装できる。裁量があるというのはこういう状況じゃないでしょうか。さらに、ポケモン位の大規模プロジェクトにおいて、自分からどんどん提案して、それが叶えられるっていうのはやっぱり珍しいことです。そういった状況ですから、実力のある方には思う存分に実力を発揮していただけると思います。
  translation: "是能把自己拥有的知识和技能发挥出来的机会。项目的方针提出之后，可以相当自由地去做。所以能把自己想透的东西实现出来。所谓有裁量权，不就是这样的状况吗？而且，在宝可梦这种规模的大型项目里，能够主动不断地提出建议并且得以实现，毕竟是很少见的。因为是这样的状况，我想有实力的人可以尽情发挥自己的实力。"
  role: answer
- type: text
  speaker: T.T.
  speaker_orig: 'T.T:'
  original: 本当にそうです。なんていうか、今世間に出ているプロダクトが僕たちの理想形だとは思わないでほしいんですよね（笑）。もっともっと良くしていけるはずだと思っているので、足りない部分はしっかり補完して、ゲームのクオリティをしっかりと上げていけたらと思います。
  translation: "真的是这样。怎么说呢，我希望大家不要觉得现在已经面世的产品就是我们的理想形态（笑）。我认为还能做得更好，所以想把不足的部分好好补上，把游戏的品质切实提高。"
  role: answer
- type: image
  original: /assets/img/interviews/2013-gamefreak-recruit-programmer/pic_03.png
  translation: /assets/img/interviews/2013-gamefreak-recruit-programmer/pic_03.png
  caption: 寄语未来技术伙伴：向着更高品质共同进发
- type: heading
  level: 3
  original: ―　ぜひ、上げていきましょう！ありがとうございました。
  translation: ——让我们一起把品质推向更高吧！非常感谢两位接受采访！
source:
  title: インタビュー どっち？ vol.1 プログラマー編 「環境づくり」と「遊びづくり」
  url: http://web.archive.org/web/20140209100018/http://www.gamefreak.co.jp/recruit/interview_2.html
entities:
  people:
  - "T.T."
  - "M.I."
  works:
  - 宝可梦 X·Y
original_lang: ja
summary: "2013年GAME FREAK程序员访谈，入职第9年的T.T.与2011年中途入职的M.I.对谈。T.T.在《宝可梦 X·Y》中担任原野系统负责人，主导玩法机制实验与团队推进，并参与开发环境搭建；M.I.负责3D模型渲染等显示控制程序及公司内部制作管线与开发环境构筑。两人谈到《宝可梦 X·Y》是系列首次全面迈入全3D，T.T.称过去团队在全3D内容制作上如同小学生水平，如今在社招人才与外部合作公司协同下达到成年社会人水平，并强调减少操作延迟、追求顺滑手感，以及公司给予程序员的自主裁量权。"
dek: "GAME FREAK 两位程序员谈《宝可梦 X·Y》全3D开发与分工。"
topics:
- "开发流程"
- "系统设计"
- "3D图形"
- "开发环境"
- "团队体制"
mentions:
  people: []
  works: []
---
