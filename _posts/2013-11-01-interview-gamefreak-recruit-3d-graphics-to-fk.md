---
archive_type: interview_translation
layout: interview-editorial
title: GAME FREAK 官方访谈 3D图形设计师篇：『宝可梦』系列首度全面3D化的巨大变革（T.O. × F.K.）
title_ja: 社員インタビュー 「最近、どう？」 vol.1 3Dグラフィック デザイナー篇 「ポケットモンスター」初のフル３Ｄ
date: 2013-10-20 10:00:00 +0900
recruit:
  page: interview_1
  version: '2013-10-22'
  capture: '20131022004448'
  date_basis: 招聘首页 2013-04-03 的快照还没有、2013-10-20 的已有；2016-11 至 2017-01 之间撤下
era: '2013'
categories:
- developer-interviews
- gamefreak-recruit
tags:
- 'Game Freak'
- '宝可梦 X·Y'
- '3D图形'
- '杉森建'
- '角色建模'
- '动作设计'
- 'Gear Project'
- '招聘访谈'
- 'Wayback历史存档'
interview_id: PKMN-1021
publication: Game Freak 採用情報 (Wayback 历史存档)
original_link: http://web.archive.org/web/20140209100018/http://www.gamefreak.co.jp/recruit/interview_1.html
author: Game Freak 採用チーム
interviewee: F.K., T.O.
original_lang: ja
translation_lang: zh-CN
summary: 《宝可梦 X·Y》发售后 GAME FREAK 官方绝版一线技术专访：主角建模组长 T.O. 与动作设计组长 F.K. 深入复盘系列首次迈入全 3D 时代的研发攻坚。专访首次披露了如何打破常规物理光影、与程序员协同定制着色器以完美还原杉森建 2D 插画手绘笔触的渲染秘诀；探讨了纯手工 K 帧（手付け）在捕捉宝可梦神韵上的无可替代性；详述了 GAME FREAK 招聘从“全能通才”向“极致专精”的战略转型，以及创作者在“交差做素材”与“亲手创造游戏本身”之间的核心认知差异。
entities:
  people:
  - T.O.
  - F.K.
  - 杉森建
  works:
  - 宝可梦 X·Y
  - Gear Project（齿轮企划）
  organizations:
  - 株式会社ゲームフリーク
parallel_items:
- type: image
  src: /assets/img/interviews/2013-gamefreak-recruit-3d-graphics/top_image.png
  caption: GAME FREAK 官方访谈：3D图形设计师篇「宝可梦」首次全3D化
- type: heading
  level: 2
  original: 「ポケットモンスター」初のフル３Ｄ
  translation: "『宝可梦』系列首部全3D作品"
- type: heading
  level: 3
  original: ― まずはおふたりのことを教えてください。
  translation: "― 首先请两位介绍一下自己。"
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: 僕は４年前に中途で入社しました。直近のプロジェクト（ポケットモンスターX・Y）ではキャラクターモデルチームのリーダーとして、主人公のモデル作成やモデルの管理をしていました。ゲーム業界に入った時からモデラーでしたけど、主人公のモデルを１から作ったというのは今回が初めてです。
  translation: "我是4年前中途入职的。在最近的项目（《宝可梦 X·Y》）中，我担任角色模型团队的组长，负责主角的模型制作和模型管理。从进入游戏行业起我就是建模师，但从零开始制作主角模型，这次是第一次。"
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: 僕は職種としてはモーションデザイナーで、立場はＯさんと同じです。２年前に入社して、いまはキャラクターモーションチームのリーダーとして実際のモーション開発と管理をしています。
  translation: "我的职种是动作设计师，职位和O先生相同。2年前入职，现在作为角色动作团队的组长，负责实际的动作开发和管理。"
  role: answer
- type: heading
  level: 3
  original: ― 今回はポケモンが初めてフル３Dになったので、デザイナーとしては色々と苦労が多かったのではないですか？
  translation: "― 这次宝可梦首次全3D化，对设计师来说应该有很多辛苦之处吧？"
- type: image
  src: /assets/img/interviews/2013-gamefreak-recruit-3d-graphics/pic_01.png
  caption: 在白纸上开辟道路：XY 全 3D 角色建模与动作资产制作
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: デザイナーだけでなく、プランナーもプログラマーも色々ありましたよ。白紙の状態から作り上げていくので面白い、けどその未踏の地に道を造る為の苦労はすごかったですね。
  translation: "不只是设计师，策划和程序员也都遇到了各种事。因为是从白纸状态开始搭建，所以很有意思，但为在未踏之地开路而付出的辛苦也相当大。"
  role: answer
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: キャラクターモデルに関しては、他社から協力を受けたおかげで、一気に最新の技術を手に入れることが出来たんですよ。外部と技術交流をすることで教わることも多く、本当に有意義でした。それでもやっぱり、現状のものに「これで完璧だ！！」とは言えないと思っています。
  translation: "关于角色模型，多亏得到其他公司的协助，我们一下子获得了最新的技术。通过与外部的技术交流，学到了很多东西，真的很有意义。即便如此，我还是觉得现状还不能说“这样就完美了！！”"
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: うん、出来ることはまだたくさんあるでしょうね。モーションはポケモンの世界観を表現するためにはやっぱり手付けが適していると考えているけれど、デモにリアルさを出すならモーションキャプチャーを使ってもいいし、表情にはジョイントだけでなく、モーフィングを使うのもあり。そうやって「思い描いている表現」に近づけるために、工夫するのが面白いなと。僕個人はそう思います。
  translation: "嗯，能做的事应该还有很多。我认为动作要表现宝可梦的世界观还是手动制作（手付け）比较合适，但如果想让演示更真实，也可以使用动作捕捉；表情方面也可以不只用关节，还用变形（morphing）。为了接近“心中所想的表现”而下功夫，我觉得很有意思。这是我个人的想法。"
  role: answer
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: 今回は杉森（ゲームフリークデザイングループ、アートディレクター）のイラストを３Dで再現するっていうのがグラフィック表現の、ひとつの大きな方針だったから、それについてはかなり面白いことをしてますよ。普通は立体に対して影が入るところをイラストのタッチに合わせて、そうではない出し方をしているんです。
  translation: "这次把杉森（GAME FREAK设计组、美术总监）的插画用3D再现，是图形表现的一个大方针，所以在这方面我们做了相当有意思的事。通常立体物会出现阴影的地方，我们配合插画的笔触，用了不同的呈现方式。"
  role: answer
- type: heading
  level: 3
  original: ― それは具体的にどういうことを？
  translation: "― 具体是怎么做的？"
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: プレイしながら、ポケモンのモデルをよーく見てもらえればわかります（笑）。あれは普通のシェーディングではなくかなり面白いことをプログラマーと一緒にやっています。（「CGWORLD」10月10日発売号掲載記事参照）
  translation: "边玩边仔细看宝可梦的模型就会明白（笑）。那不是普通的着色，而是和程序员一起做了相当有意思的事。（参见《CGWORLD》10月10日发售号刊载的文章）"
  note: '详见当年《CGWORLD》10月10日发售刊专访'
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: そういう「えっ？」って言われるようなことを、どんどんやっていけるうちの環境が、僕にとっては魅力的です。ゲームの大方針はもちろんあるんですが、そこにたどり着くための手段は本当に自由。今回フル３Dになったことで、ゲームの作り方も大きく変わりましたよ。そこをどうやっていくかが面白いというか、腕の見せ所じゃないですかね。
  translation: "能不断做出让人“诶？”一声的事情，这样的环境对我来说很有魅力。游戏的大方针当然有，但到达那里的手段真的很自由。这次全3D化后，游戏的制作方式也发生了很大变化。怎么去做，既有意思，也是展示本事的地方吧。"
  role: answer
- type: heading
  level: 2
  original: ゲームフリークで働くとは思わなかった
  translation: 未曾想过自己竟会在 GAME FREAK 工作
- type: heading
  level: 3
  original: ― 作り方が変わるということは、求められるスキルも異なってきますか？
  translation: "― 制作方式变了，所需要的技能也会不同吗？"
- type: image
  src: /assets/img/interviews/2013-gamefreak-recruit-3d-graphics/pic_02.png
  caption: 从通才到专精：追求极致专业度与角色人体骨骼理解
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: そうですね。うちは長年「色々なことが幅広く出来る人材」をずっと求めてきた会社だと思うんです。グラフィックなら２Dのイラストも描けてモデルも作れて、っていうマルチタイプを。でも個人的にはひとつの分野に対しての強い熱意があっても面白いと思うんですよね。ゲームの中でも、きれいにまとまっているより「ここ、こだわってんなー！」と思われるような小粋なこと、小憎らしいようなことがあってもいいんじゃないかと。
  translation: "是的。我认为我们公司长年以来一直在寻求“能广泛做各种事的人才”。比如图形方面，既能画2D插画又能做模型的多面手。但我个人觉得，对某一领域抱有强烈热情的人也很有意思。游戏里也是，比起整整齐齐，如果有让人觉得“这里下了功夫啊！”的小巧思、让人又羡又恨的地方也不错。"
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: 汎用性より専門性が重視されるようになってきた感じがします。新しく入社してくる人達をみていると特にそう。でも専門性の高い人が「応募しよう」って気にはなりにくいんじゃないかって危惧する思いもあるよ。「ゲームフリーク＝ポケモンを作っている会社」という事実から連想される、「モンスターデザインを描けないと働けないだろう」、「３Dは重視されていないだろう」、っていうイメージは持っている人多いと思うんだよね。自分も２年前に応募した時は実はそう思っていたし。だからダメ元だったんです（笑）。
  translation: "我感觉比起通用性，现在更重视专业性，看新入职的人时尤其如此。但我也担心，专业性高的人不太会想要“去应征”。从“GAME FREAK＝制作宝可梦的公司”联想到“不会画怪物设计就没法在那里工作吧”“应该不重视3D吧”，我想有这种印象的人很多。我自己2年前应征时其实也这么想，所以是抱着死马当活马医的心态（笑）。"
  role: answer
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: そういう人って実はすごく求められているのにね。どうすれば伝わるのかな～。今まで「画力」と「発想力」が重要だったけど、例えばキャラクターモデラーなら人体デッサンを理解していることのほうが重要だし。
  translation: "那样的人其实非常被需要啊。该怎么才能传达出去呢～。以往“画力”和“想象力”很重要，但比如角色建模师，理解人体素描反而更重要。"
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: 技術的な部分はそうなっていくだろうね。でも、自分で考えて、自分で動ける主体的な人物を求めているっていうのは変わらないところだと思うな。
  translation: "技术方面会变成那样吧。但我认为，寻求能自己思考、自己行动的主动型人才，这一点是不变的。"
  role: answer
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: 確かに。この会社にいると、「ゲームの素材」じゃなくて「ゲームそのもの」を作っているって感じがするんですよね。その分仕組みまで気にしなきゃいけないから苦労も多いですが…でも「俺はこのゲームを作っている」と強く思えるんです。そういう会社なんで、やりたい人にはいいでしょうね。
  translation: "确实。在这家公司，会觉得自己做的不是“游戏的素材”而是“游戏本身”。因此连机制都必须关心，辛苦也多……但能强烈地觉得“我在做这个游戏”。这是这样的公司，所以对想做的人来说应该不错。"
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: 自分でやりたいとかやりたくないとか、考えないままにキャリアを積んできた人も世の中にはいると思うけど…一遍、ちょっと見に来て欲しいと思いますね。
  translation: "世上也有人在没想过自己想做什么、不想做什么的情况下积累着职业经历……我希望他们来看一看。"
  role: answer
- type: heading
  level: 2
  original: デザイナーとして向かう先
  translation: "作为设计师的前进方向"
- type: heading
  level: 3
  original: ― 今後やっていきたいことは？
  translation: "― 今后想做什么？"
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: デザイナーとしてゲームの表現の方向性を決定付けられるようになりたいです。そしてこの会社ならではの、キャラクターモデルの形を確立させたいですね。シルエットを見ただけで、「ああ、これはゲームフリークだな」ってわかるようにしたいんです。出来れば「あそこが作るのは、やっぱり違うね」と思わせられたらなと。キャラクターモデルに関してはまだまだ適用させられる技術がたくさんあるので、やりがいありますよ！
  translation: "我想成为能作为设计师决定游戏表现方向的人。还想确立这家公司独有的角色模型的样式。希望只看剪影就能让人觉得“啊，这是GAME FREAK”。如果能让人觉得“那家公司做的果然不一样”就好了。角色模型方面还有很多可以应用的技术，所以很有干劲！"
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: モーションもそうですね。「より気持ちのいい動き」を追求していきたいです。僕の場合、今後やっていきたいことはそれに尽きるかな。後、もっと大きなところではポケモンと並ぶ作品を生み出したいって思ってます。
  translation: "动作也是一样。我想追求“更舒服的动作”。就我而言，今后想做的就是这个。还有，在更大的方面，我想做出能与宝可梦并列的作品。"
  role: answer
- type: heading
  level: 3
  original: ― それはギア・プロジェクト制度（社員が自ら企画を立て、プロジェクト化する開発制度）を利用して、ということですか？
  translation: ― 这意味着您打算借助公司的“齿轮企划（Gear Project）制度”（由员工自主立项提案、孵化为正式项目的内部创新开发机制）来实现这一宏愿吗？
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: 厳密には違うかな。 "自分でアイデア出したゲームを作りたい" というだけでなく、そこで生まれたプロジェクトが大規模になった時に上手く走らせられるような組織にもしていきたいんです。
  translation: "严格来说不是。不只是“想做自己想出创意的游戏”，我还想把组织建设成当那里诞生的项目变大规模时也能顺利运转。"
  role: answer
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: そうなんだ…。僕はグラフィックから離れて考えることがまだ出来てないな～。
  translation: "原来如此……我还没法脱离图形去思考啊～。"
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: いやいや、もちろん自分だって組織の枠組みだけでなく、グラフィックをしっかり見つめていきたいと思ってますよ！
  translation: "不不，我当然也不只是组织的框架，也想认真地盯着图形！"
  role: answer
- type: heading
  level: 3
  original: ― 楽しみですね！ありがとうございました！
  translation: "― 令人期待呢！谢谢！"
source:
  title: 社員インタビュー 「最近、どう？」 vol.1 3Dグラフィック デザイナー篇 「ポケットモンスター」初のフル３Ｄ
  url: http://web.archive.org/web/20140209100018/http://www.gamefreak.co.jp/recruit/interview_1.html
---
<!-- 底部人物背景说明 -->
<div class="interview-profile-card mt-4 p-4 rounded bg-light border">
  <div class="row align-items-center">
    <div class="col-md-6 border-end">
      <h4 class="fw-bold mb-1">T.O.</h4>
      <p class="text-muted small mb-1"><strong>入职：</strong>2009年中途入社</p>
      <p class="text-muted small mb-2"><strong>职务：</strong>《宝可梦 X·Y》角色模型团队组长（Character Model Leader）</p>
      <p class="small text-secondary mb-0">自进入游戏行业起便深耕 3D 建模，在《宝可梦 X·Y》中首次从零主导主角 3D 模型的设计制作与模型管线管理，攻克定制手绘水彩 Shader 渲染。</p>
    </div>
    <div class="col-md-6 ps-md-4">
      <h4 class="fw-bold mb-1">F.K.</h4>
      <p class="text-muted small mb-1"><strong>入职：</strong>2011年中途入社</p>
      <p class="text-muted small mb-2"><strong>职务：</strong>《宝可梦 X·Y》角色动作团队组长（Character Motion Leader）</p>
      <p class="small text-secondary mb-0">资深动作设计师，统领《宝可梦 X·Y》全 3D 动作开发，主张手工逐帧 K 帧的生物神韵，并积极倡导齿轮企划（Gear Project）推动公司大规模研发体系进化。</p>
    </div>
  </div>
</div>

