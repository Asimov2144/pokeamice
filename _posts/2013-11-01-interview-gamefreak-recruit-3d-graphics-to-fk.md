---
archive_type: interview_translation
layout: interview-editorial
title: GAME FREAK 官方访谈 3D图形设计师篇：『宝可梦』系列首度全面3D化的巨大变革（T.O. × F.K.）
title_ja: 社員インタビュー 「最近、どう？」 vol.1 3Dグラフィック デザイナー篇 「ポケットモンスター」初のフル３Ｄ
date: 2013-11-01 10:00:00 +0900
era: '2013'
categories:
- developer-interviews
- gamefreak-recruit
tags:
- GAME FREAK
- 宝可梦XY
- 3D图形
- 杉森建
- 角色建模
- 动作设计
- Gear Project
- 招聘访谈
- Wayback历史存档
interview_id: PKMN-1021
publication: GAME FREAK 採用情報 (Wayback 历史存档)
original_link: http://web.archive.org/web/20140209100018/http://www.gamefreak.co.jp/recruit/interview_1.html
author: GAME FREAK 採用チーム
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
  translation: 『宝可梦』系列首部全3D作品的黎明破晓
- type: heading
  level: 3
  original: ― まずはおふたりのことを教えてください。
  translation: ― 首先请两位介绍一下各自的履历与在团队中的职责。
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: 僕は４年前に中途で入社しました。直近のプロジェクト（ポケットモンスターX・Y）ではキャラクターモデルチームのリーダーとして、主人公のモデル作成やモデルの管理をしていました。ゲーム業界に入った時からモデラーでしたけど、主人公のモデルを１から作ったというのは今回が初めてです。
  translation: 我是 4 年前通过中途招聘加入公司的。在最近的项目（《宝可梦 X·Y》）中，我担任角色模型团队的组长（Leader），主要负责男女主角的 3D 模型制作以及整体角色模型的生产管理。从我踏入游戏行业起我就一直是一名 3D 建模师，但从零开始把正统大作的主角模型完整建立起来，在我的职业生涯中这还是第一次。
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: 僕は職種としてはモーションデザイナーで、立場はＯさんと同じです。２年前に入社して、いまはキャラクターモーションチームのリーダーとして実際のモーション開発と管理をしています。
  translation: 我的专业职能是动作设计师（Motion Designer），在团队中的职责定位和 O 组长是一样的。我是 2 年前入社的，目前担任角色动作团队的组长，负责具体的动作研发攻坚与全流程动作资产的质量把控。
  role: answer
- type: heading
  level: 3
  original: ― 今回はポケモンが初めてフル３Dになったので、デザイナーとしては色々と苦労が多かったのではないですか？
  translation: ― 本作是『宝可梦』系列首次实现全3D化，作为设计师，想必经历了难以想象的重重艰辛吧？
- type: image
  src: /assets/img/interviews/2013-gamefreak-recruit-3d-graphics/pic_01.png
  caption: 在白纸上开辟道路：XY 全 3D 角色建模与动作资产制作
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: デザイナーだけでなく、プランナーもプログラマーも色々ありましたよ。白紙の状態から作り上げていくので面白い、けどその未踏の地に道を造る為の苦労はすごかったですね。
  translation: 何止是设计师，策划、程序员大家都经历了无数硬仗。一切都是从完全空白的白纸状态开始搭建，这种开拓未知的过程确实充满乐趣；但为了在这片从未踏足过的荒原上硬生生踩出一条路来，背后付出的辛劳也是极其惊人的。
  role: answer
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: キャラクターモデルに関しては、他社から協力を受けたおかげで、一気に最新の技術を手に入れることが出来たんですよ。外部と技術交流をすることで教わることも多く、本当に有意義でした。それでもやっぱり、現状のものに「これで完璧だ！！」とは言えないと思っています。
  translation: 在角色 3D 建模方面，得益于外部业界顶尖合作伙伴的大力协助，我们得以一口气吸收并掌握了行业最前沿的资产生产管线与最新技术。通过与外部展开深度的技术交流，我们汲取了海量宝贵经验，这极具战略意义。然而即便是现在，面对最终呈现在屏幕上的成果，我也依然不敢断言说：“这已经彻底完美了！”
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: うん、出来ることはまだたくさんあるでしょうね。モーションはポケモンの世界観を表現するためにはやっぱり手付けが適していると考えているけれど、デモにリアルさを出すならモーションキャプチャーを使ってもいいし、表情にはジョイントだけでなく、モーフィングを使うのもあり。そうやって「思い描いている表現」に近づけるために、工夫するのが面白いなと。僕個人はそう思います。
  translation: 是的，我们能做、该做的事情还有太多太多。在动作设计上，为了精准传递宝可梦独特的世界观神韵，我们依然坚信纯手工逐帧打磨（手付け / Hand-keyed）是最契合的方式；但如果要在过场剧情演示中展现更具呼吸感的真实动态，引入动作捕捉（Motion Capture）也是完全可行的手段；而在面部表情表现上，除了传统的骨骼绑定（Joints），结合使用变形目标（Morphing / Blendshapes）也大有可为。像这样，为了无限逼近脑海中构想的终极表现力而不断探索创新工法，这正是最吸引人的乐趣所在。
  role: answer
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: 今回は杉森（ゲームフリークデザイングループ、アートディレクター）のイラストを３Dで再現するっていうのがグラフィック表現の、ひとつの大きな方針だったから、それについてはかなり面白いことをしてますよ。普通は立体に対して影が入るところをイラストのタッチに合わせて、そうではない出し方をしているんです。
  translation: 而且在本作中，将杉森建老师（GAME FREAK 设计总监 / 艺术总监）笔下那极富韵味的插画风貌在 3D 空间中完美还原，是我们图形表现最核心的战略大方针。为此，我们做出了极具突破性的尝试。通常在 3D 引擎中，物体是根据物理光照法则自然投射明暗阴影的；但为了完全契合杉森老师水彩插画那独特的通透笔触与高光阴影，我们特意打破了常规物理光影规则，采用了一种非同寻常的方式来呈现光暗关系。
  role: answer
- type: heading
  level: 3
  original: ― それは具体的にどういうことを？
  translation: ― 具体来说，究竟是怎样的一种特殊渲染机制呢？
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: プレイしながら、ポケモンのモデルをよーく見てもらえればわかります（笑）。あれは普通のシェーディングではなくかなり面白いことをプログラマーと一緒にやっています。（「CGWORLD」10月10日発売号掲載記事参照）
  translation: 大家在玩游戏的时候，只要仔仔细细观察宝可梦和角色的模型就能看明白啦（笑）。那绝不是普通的标准光照着色器（Shading），而是我们美术团队与底层程序员紧密协同开发出的极具巧思的定制算法（注：详见当年《CGWORLD》10月10日发售刊专访）。
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: そういう「えっ？」って言われるようなことを、どんどんやっていけるうちの環境が、僕にとっては魅力的です。ゲームの大方針はもちろんあるんですが、そこにたどり着くための手段は本当に自由。今回フル３Dになったことで、ゲームの作り方も大きく変わりましたよ。そこをどうやっていくかが面白いというか、腕の見せ所じゃないですかね。
  translation: 能够不断去挑战这种让业界惊呼“诶？居然还能这么做？！”的前沿尝试，这种自由的开发环境对我来说有着致命的吸引力。游戏宏观的大方针固然明确，但通往终点的实现路径却是完全自由开放的。此次全面迈入全 3D 时代，整个游戏的制作范式发生了翻天覆地的剧变。如何在未知中摸索前行，正是体现创作者真正身手与魄力的舞台。
  role: answer
- type: heading
  level: 2
  original: ゲームフリークで働くとは思わなかった
  translation: 未曾想过自己竟会在 GAME FREAK 工作
- type: heading
  level: 3
  original: ― 作り方が変わるということは、求められるスキルも異なってきますか？
  translation: ― 制作范式的彻底转变，是否意味着团队所索求的核心专业技能也随之发生了变化？
- type: image
  src: /assets/img/interviews/2013-gamefreak-recruit-3d-graphics/pic_02.png
  caption: 从通才到专精：追求极致专业度与角色人体骨骼理解
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: そうですね。うちは長年「色々なことが幅広く出来る人材」をずっと求めてきた会社だと思うんです。グラフィックなら２Dのイラストも描けてモデルも作れて、っていうマルチタイプを。でも個人的にはひとつの分野に対しての強い熱意があっても面白いと思うんですよね。ゲームの中でも、きれいにまとまっているより「ここ、こだわってんなー！」と思われるような小粋なこと、小憎らしいようなことがあってもいいんじゃないかと。
  translation: 确实如此。长年以来，我认为 GAME FREAK 一直是一家倾向于索求“能涉猎多种维度的复合型通才”的公司——比如在图形美术上，既要能画 2D 概念插画，又能自己动手建 3D 模型的多面手。但以我个人的视角来看，如果一个人对某一个极其精深的专业领域抱有狂热的执念，其实也是非常宝贵且有趣的。在一部游戏作品里，比起四平八稳、挑不出错的平庸整合，如果能有一两处让核心玩家由衷惊呼“哇，这里扣得也太狠了吧！”的极致考究与灵光乍现，反而更具灵魂。
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: 汎用性より専門性が重視されるようになってきた感じがします。新しく入社してくる人達をみていると特にそう。でも専門性の高い人が「応募しよう」って気にはなりにくいんじゃないかって危惧する思いもあるよ。「ゲームフリーク＝ポケモンを作っている会社」という事実から連想される、「モンスターデザインを描けないと働けないだろう」、「３Dは重視されていないだろう」、っていうイメージは持っている人多いと思うんだよね。自分も２年前に応募した時は実はそう思っていたし。だからダメ元だったんです（笑）。
  translation: 我切实体会到，相比起万金油式的泛用性，行业深度专精的专业度正变得前所未有的关键。从最近新加入团队的成员身上尤为能感受到这种趋势。然而，我内心也始终存有一种深深的担忧：那些在各自领域造诣极高的一流专业人才，会不会反而不敢轻易投递 GAME FREAK？因为外界只要一听到“GAME FREAK＝制作宝可梦的公司”，往往就会先入为主地产生思维定势：“如果我不会画 2D 宝可梦怪物设计，肯定无法在那里立足吧？”、“这家公司以往以像素和2D见长，应该不怎么重视硬核3D技术吧？”——实不相瞒，我自己 2 年前投简历时内心其实也是这么以为的，当时完全是抱着‘死马当活马医’的心态试一试（笑）。
  role: answer
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: そういう人って実はすごく求められているのにね。どうすれば伝わるのかな～。今まで「画力」と「発想力」が重要だったけど、例えばキャラクターモデラーなら人体デッサンを理解していることのほうが重要だし。
  translation: 可事实上，公司现在最迫切渴求的反而是这类拥有硬核专业造诣的专家啊！该怎么把这个信号清晰地传递给外界呢…… 以往大家总觉得纯粹的“手绘画力”和“脑洞发想力”是最关键的；但以角色建模师为例，能够深刻理解真实人体解剖学（Anatomy）与素描体积骨骼构造的底子，反而比什么都重要。
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: 技術的な部分はそうなっていくだろうね。でも、自分で考えて、自分で動ける主体的な人物を求めているっていうのは変わらないところだと思うな。
  translation: 技术硬实力的评判标准确实在演进。但有一点是永远不曾改变的：那就是 GAME FREAK 始终在寻找能够自己独立深度思考、具备主动出击魄力的人才。
  role: answer
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: 確かに。この会社にいると、「ゲームの素材」じゃなくて「ゲームそのもの」を作っているって感じがするんですよね。その分仕組みまで気にしなきゃいけないから苦労も多いですが…でも「俺はこのゲームを作っている」と強く思えるんです。そういう会社なんで、やりたい人にはいいでしょうね。
  translation: 确实如此。只要身在这间公司，你就会真真切切地感受到：自己并不是在按部就班地生产“游戏的零散素材”，而是在亲手创造“游戏本身”！正因如此，你必须连同底层的游戏运行机制一同通盘考量，伴随而来的思考量与劳累自然成倍增加；但也正因如此，内心才会涌起无可替代的骄傲：“我就是这部伟大游戏的创造者！”对于那些真正渴望倾注心血创造游戏的人而言，没有比这里更棒的舞台了。
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: 自分でやりたいとかやりたくないとか、考えないままにキャリアを積んできた人も世の中にはいると思うけど…一遍、ちょっと見に来て欲しいと思いますね。
  translation: 在这个世界上，或许也有不少人在日复一日的工作中，甚至来不及思考自己内心真正想做的是什么，就浑浑噩噩地累积着履历……对于这样的一线创作者，我真心希望他们能哪怕一次也好，亲自来 GAME FREAK 走一趟、亲眼看一看这里的创作生态。
  role: answer
- type: heading
  level: 2
  original: デザイナーとして向かう先
  translation: 作为设计师的未来航向与组织进化
- type: heading
  level: 3
  original: ― 今後やっていきたいことは？
  translation: ― 请问两位今后各自渴望挑战与实现的目标是什么？
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: デザイナーとしてゲームの表現の方向性を決定付けられるようになりたいです。そしてこの会社ならではの、キャラクターモデルの形を確立させたいですね。シルエットを見ただけで、「ああ、これはゲームフリークだな」ってわかるようにしたいんです。出来れば「あそこが作るのは、やっぱり違うね」と思わせられたらなと。キャラクターモデルに関してはまだまだ適用させられる技術がたくさんあるので、やりがいありますよ！
  translation: 作为设计师，我希望自己未来能够独当一面，执掌并决定一部游戏图形表现的大方向。并且，我渴望确立起唯独属于 GAME FREAK 独家标签的角色 3D 建模范式！哪怕仅仅只是看到一个背光剪影，全世界玩家就能一眼辨认出：“啊，这绝对是 GAME FREAK 的手笔！”甚至由衷感叹：“那家公司塑造的角色，果然有着截然不同的灵魂风骨！” 在角色 3D 建模的疆域里，还有海量我们尚未完全应用的前沿技术，这份挑战的价值无可限量！
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: モーションもそうですね。「より気持ちのいい動き」を追求していきたいです。僕の場合、今後やっていきたいことはそれに尽きるかな。後、もっと大きなところではポケモンと並ぶ作品を生み出したいって思ってます。
  translation: 在动作设计上也是同理，我将一生不懈地去追求“更加让人身心愉悦的灵动韵律”。对我而言，这或许就是我作为动作设计师终身矢志不渝的宿命。而在更宏大的格局上，我内心渴望亲手孕育出能够与《宝可梦》并驾齐驱的崭新原创作品。
  role: answer
- type: heading
  level: 3
  original: ― それはギア・プロジェクト制度（社員が自ら企画を立て、プロジェクト化する開発制度）を利用して、ということですか？
  translation: ― 这意味着您打算借助公司的“齿轮企划（Gear Project）制度”（由员工自主立项提案、孵化为正式项目的内部创新开发机制）来实现这一宏愿吗？
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: 厳密には違うかな。 "自分でアイデア出したゲームを作りたい" というだけでなく、そこで生まれたプロジェクトが大規模になった時に上手く走らせられるような組織にもしていきたいんです。
  translation: 严格说来，并不单纯是那样。我心中的愿景，绝不仅仅停留在“做出由自己提出创意的原创游戏”这一个点上；我更渴望推动整个公司的组织架构进化——当这些内部孵化出的崭新项目未来逐步演变为大规模工业化管线时，我们的组织依然能够如臂使指、极为高效稳健地支撑其全速运转。
  role: answer
- type: text
  speaker: T.O.
  speaker_orig: T.O.
  original: そうなんだ…。僕はグラフィックから離れて考えることがまだ出来てないな～。
  translation: 原来你的志向已经到了这个高度啊……我自己目前的心思，还完全无法离开纯粹的图形美术创作本身呢～（笑）。
  role: answer
- type: text
  speaker: F.K.
  speaker_orig: F.K.
  original: いやいや、もちろん自分だって組織の枠組みだけでなく、グラフィックをしっかり見つめていきたいと思ってますよ！
  translation: 哪里哪里，我当然也不会只盯着组织机制，我自己的立足之本永远是对图形美术的赤诚深耕！
  role: answer
- type: heading
  level: 3
  original: ― 楽しみですね！ありがとうございました！
  translation: ― 真是令人无限期待的未来！非常感谢两位今日带来的精彩分享！
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

