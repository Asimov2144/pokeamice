---
archive_type: interview_translation
layout: interview-editorial
title: GAME FREAK 官方访谈 程序员篇：「环境构筑」与「玩法创造」（T.T. × M.I.）
title_ja: インタビュー どっち？ vol.1 プログラマー編 「環境づくり」と「遊びづくり」
date: 2013-11-01 10:00:00 +0900
era: '2013'
categories:
- developer-interviews
- gamefreak-recruit
tags:
- Game Freak
- 宝可梦XY
- 程序员
- 3D渲染
- Shader着色器
- 开发管线
- 座谈访谈
- Wayback历史归档
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
  translation: 我是在大学毕业后以应届生身份入职的，今年已经是第9个年头了。之前一直主要专注于创造游戏内部的「玩法」。在最近的项目《宝可梦 X·Y》中，我作为原野系统负责人（Field Leader），主导了各种玩法机制的实验并负责团队推进管理。
  role: answer
- type: text
  speaker: M.I.
  speaker_orig: 'M.I:'
  original: 私は2011年の中途入社です。前職は別のゲーム会社で３DグラフィックスのR&Dの部署で働いていました。現在は主に3Dモデルの描画等の表示制御のプログラムと、社内のゲーム制作環境の構築を行っています。
  translation: 我是2011年社招中途入职的。上一份工作是在另一家游戏公司的3D图形R&D（研发）部门任职。目前在公司主要负责3D模型渲染等显示控制程序的开发，以及搭建和构筑公司内部的游戏制作管线与开发环境。
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
  translation: 从这次（XY）开始，确实能感觉到大家在个人层面上正逐渐细分并专注于专门领域中。我个人就是专门专注于底层图形渲染环境与着色管线的。
  role: answer
- type: text
  speaker: T.T.
  speaker_orig: 'T.T:'
  original: 僕は「遊び」を作りつつ環境構築も行っていた訳ですが、「環境」については反省が多いんです。今回がポケモンにとって初めてのフル３Dだったということで、「遊び」に関する実験のほうを重視してしまったんですよね。例えば3DSに発生する１フレームの遅れを解消する、とか。そういう「操作の気持ちよさ」をつくることに時間をかけていました。今まで通りの姿勢で今回の開発と向き合ってしまったかな、と。遊びたいと思った時に思う存分遊べるように、ユーザーのストレスを減らしていく。そういった部分では満足していますが、リソース環境の点では反省が多いです…。
  translation: 我虽然一边打造「玩法」一边参与搭建环境，但在「环境」这一块我其实有很多反省。因为这次是《宝可梦》系列历史上首次全面迈入全3D时代，我当时就更偏重于「玩法」层面的各种实验。例如怎样消除在3DS硬件上可能产生的哪怕1帧的操作延迟等等。我们把大量时间花在了如何创造出「顺滑愉悦的操作手感」上。或许我还是以过去2D时代的惯性思维在对待这次的3D开发吧。为了让玩家在想玩的时候能无拘无束地尽情游玩，极力减少玩家的阻碍感与压力——在这一层面上我是感到满足的，但在全3D资源环境管线方面，反思真的很多……
  role: answer
- type: text
  speaker: M.I.
  speaker_orig: 'M.I:'
  original: 要はバランスじゃないですかね。今後は環境もしっかり見ていこうと考えています。でないとゲームコンテンツを面白くする時間がなくなってもったいないですから。確かにゲームフリークは「遊び」を追求するほうが好きだという方が多いですし、驚くほど細かい部分まで拘って遊びをつくっていきますが、私は「環境づくり」が好きですよ。素晴らしい環境で、自分たちのパフォーマンスをしっかり出していい仕事する、そういうのって格好いいと思ってます（笑）。
  translation: 归根结底还是一个平衡问题吧。今后我们打算把开发环境也牢牢抓好。否则如果不理顺底层管线，大家就没有足够的时间去打磨充实游戏内容的趣味性，那就太可惜了。确实，GAME FREAK里绝大多数人都更热衷于对「玩法」的极度追求，而且会执着到令人吃惊的极细微之处来雕琢玩法；但我个人却很喜欢「搭建环境」。在一个绝佳的开发环境里，让大家能够充分发挥自己的潜能、做出优秀的工作，我觉得那样特别帅气（笑）。
  role: answer
- type: image
  original: /assets/img/interviews/2013-gamefreak-recruit-programmer/pic_02.png
  translation: /assets/img/interviews/2013-gamefreak-recruit-programmer/pic_02.png
  caption: 在 3D 技术转型中迎头赶上的技术团队
- type: heading
  level: 2
  original: ３Dコンテンツについては小学生だった？
  translation: 在3D技术内容上曾是小学生水平？
- type: text
  speaker: T.T.
  speaker_orig: 'T.T:'
  original: 本当に、Iさんが加入したことにより、表現の幅が広がったと思います。あのね、３Dのコンテンツを作るっていう意味において、ゲームフリークは小学生みたいなものだったと思うんですよ。もちろん中には３Dの技術に長けている人もいるけど、全体としてはね。それで現在は中途入社の方々が加わったり、外部の協力会社さんに入ってもらったりして社会人くらいにはなったんじゃないかなと思っています。
  translation: 说实话，正是因为I先生的加入，我们才真正大幅拓展了画面的表现力与广度。怎么说呢，在制作“全3D游戏内容”这一维度上，以前的GAME FREAK我觉得就跟小学生水平差不多。当然团队里也有个别精通3D技术的人才，但就整体团队的开发管线而言确实如此。之后随着各路社招资深人才的加入，加上外部专业合作公司的深度协同，我觉得我们现在总算是达到了“成年社会人”的水平吧。
  role: answer
- type: heading
  level: 3
  original: ―　小学生だったんですか？
  translation: ——居然曾是小学生水平吗？
- type: text
  speaker: T.T.
  speaker_orig: 'T.T:'
  original: あくまで昔の話ですよ！最先端のフル３Ｄゲームと比較した時の話なので、誤解しないでくださいね（笑）。今までのポケモンにも３Ｄの要素はありましたが、世界観を守るために２Ｄの技術をベースとした作り方をしていたわけですから。ま、それでも一番しんどい部分は越えたと思っています。
  translation: 这完全是指过去啦！而且是跟当时业界最尖端的全3D主机大作相比而言的，可千万别误会了（笑）。以往的《宝可梦》作品虽然也引入过部分3D要素，但为了守护既有的世界观基调，本质上还是基于2D技术的思路来构建的。不过，即便如此，我认为最艰难、最痛苦的一道险峰我们已经跨越过去了。
  role: answer
- type: text
  speaker: M.I.
  speaker_orig: 'M.I:'
  original: 山は越えたでしょうね。これからは先々のことも視野に入れて作って行く開発体制になると思います。考えようによっては今から入る人にはすごくいいと思いますよ。チャンスが多くあるので、腕に自信のある方こそ、来てもらえばいいのかなぁって。
  translation: 确实可以说是翻过最陡峭的山头了。今后我们将建立起能够兼顾未来长远演进的成熟开发体系。换个角度来看，对于现在加入公司的新人来说，正处于一个极其绝妙的时机。因为机会非常多，对自己的技术实力有充分自信的人，现在正是加入的大好时候。
  role: answer
- type: heading
  level: 3
  original: ―　何のチャンスでしょう？
  translation: ——指的是怎样的机会呢？
- type: text
  speaker: M.I.
  speaker_orig: 'M.I:'
  original: 自分が持っている知識スキルがあったとして、それを活かせるチャンスです。プロジェクトの指針が示された後は、かなり自由にやっていいんですよ。だから自分なりに考え抜いたことが実装できる。裁量があるというのはこういう状況じゃないでしょうか。さらに、ポケモン位の大規模プロジェクトにおいて、自分からどんどん提案して、それが叶えられるっていうのはやっぱり珍しいことです。そういった状況ですから、実力のある方には思う存分に実力を発揮していただけると思います。
  translation: 是指将自己所掌握的深厚知识与技能充分发挥出来的机会。在项目指明了宏观大方向之后，具体的研发与技术实现层面拥有极大的自由度。因此你可以把自己深入思考后的构思与方案亲手实现并落地。所谓的“拥有极高的自主裁量权”，不正是指这种情况吗？而且，在像《宝可梦》这样庞大规模的世界级顶级项目中，能够允许普通开发人员主动不断提出技术方案并将其付诸实现，这在业界其实是非常罕见的。正因为拥有这样包容与开放的土壤，有实力的人一定能在这里随心所欲、淋漓尽致地施展拳脚。
  role: answer
- type: text
  speaker: T.T.
  speaker_orig: 'T.T:'
  original: 本当にそうです。なんていうか、今世間に出ているプロダクトが僕たちの理想形だとは思わないでほしいんですよね（笑）。もっともっと良くしていけるはずだと思っているので、足りない部分はしっかり補完して、ゲームのクオリティをしっかりと上げていけたらと思います。
  translation: 确实就是这样。怎么说呢，我不希望大家觉得现在市面上发售的这代作品（XY）就是我们的终极理想形态（笑）。我们深信它还能做得更好、更出色，所以希望能把不足之处扎实地补足，把游戏的品质推向更高的层次。
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
  works:
  - 宝可梦 X·Y
original_lang: ja
---
