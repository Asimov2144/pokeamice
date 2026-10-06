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
  translation: 员工介绍
- type: profile
  speaker: Y.I.
  speaker_orig: フィールドコンテンツプログラマ Y.I.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/profile_01.png
  role_ja: フィールドコンテンツプログラマ（2014年入社）
  role_zh: 场地内容程序员（2014年入社）
  original: 2014年度に入社した、フィールドコンテンツプログラマのY.I.です。現在はプレイヤープログラム全般を担当しています。
  translation: 我是2014年入职的场地内容程序员Y.I.。目前主要负责玩家相关的全部程序。
  role: answer
- type: profile
  speaker: M.K.
  speaker_orig: フィールド環境プログラマ M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/profile_02.png
  role_ja: フィールド環境プログラマ（2014年入社）
  role_zh: 场地环境程序员（2014年入社）
  original: 同じく2014年度入社のフィールド環境プログラマ、M.K.です。主にアセットパイプラインやツールの構築を行っています。
  translation: 我是同样在2014年入职的场地环境程序员M.K.。平时主要负责搭建资产管线和各种开发工具。
  role: answer
- type: heading
  level: 2
  original: とにかくゲームが大好き！
  translation: 总之就是超爱游戏！
- type: heading
  level: 3
  original: 入社までの経歴を教えてもらえますか？
  translation: 能先聊聊两位入职前的经历吗？
- type: text
  speaker: Y.I.
  speaker_orig: フィールドコンテンツプログラマ Y.I.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_01.png
  original: 専門学校を卒業後、名古屋のゲーム会社で2年ほどPS3とXbox 360のアクションゲームを開発していました。その後、東京のゲーム会社に移籍してアクションゲームのバトルやイベント周りを担当し、2014年にゲームフリークに入社しました。ずっとハイエンド寄りのアクションゲームのプログラムを手掛けてきました。
  translation: 我从专科学校毕业后，先在名古屋的一家游戏公司做了两年左右的PS3和Xbox 360动作游戏。之后转到了东京的游戏公司，主要负责动作游戏的战斗和事件逻辑，然后在2014年加入了GAME FREAK。一路走来，我一直都在做比较偏高端机能的动作游戏程序。
  role: answer
- type: text
  speaker: M.K.
  speaker_orig: フィールド環境 M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_02.png
  original: 私は大学院の修士課程で、ゲームクリエイターを支援する仕組みの研究をしていました。修了後、家庭用ゲーム会社でプログラマとして約3年半、主にツール開発やゲームエンジン周りの業務を担当していました。開発現場の効率化にずっと興味を持っています。
  translation: 我读研的时候，研究的课题是怎么做一套系统来辅助游戏创作者。毕业后，我在一家家用机游戏公司当了差不多三年半的程序员，主要负责工具开发和游戏引擎相关的业务。我一直对怎么提高开发现场的效率很感兴趣。
  role: answer
- type: heading
  level: 3
  original: ゲーム業界に入った理由は？
  translation: 进游戏行业的理由是什么呢？
- type: text
  speaker: Y.I. & M.K.
  speaker_orig: Y.I. M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_03.png
  original: ゲームが好きだから！（声を揃えて）
  translation: 因为喜欢游戏啊！（两人异口同声）
  role: answer
- type: heading
  level: 3
  original: なるほど、それに尽きますよね。ちなみに好きなゲーム・印象に残っているゲームは何ですか？
  translation: 确实，理由就这一个呢。顺便问下，你们喜欢或者印象比较深的游戏有哪些？
- type: image
  src: /assets/img/interviews/2015-gamefreak-recruit-programmers/photo_01.png
  caption: 畅谈热爱的游戏与工程代码之间的纯粹共振：从经典动作名作到宏大日式 RPG
- type: text
  speaker: Y.I.
  speaker_orig: フィールドコンテンツプログラマ Y.I.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_01.png
  original: 今までの人生でナンバーワンのゲームは『風のクロノア』です。あの独特の浮遊感、敵を掴んで投げるアクションの気持ちよさ、そして切ない世界観。アクションゲームとしてこれ以上ないほど完成されていて、今でも私のものづくりの原点になっています。
  translation: 目前为止我人生的No.1游戏绝对是《风之克罗诺亚》。那种独特的漂浮感、抓起敌人扔出去的爽快动作，还有略带伤感的世界观。作为一款动作游戏，它的完成度简直无可挑剔，直到现在依然是我做游戏的初心。
  role: answer
- type: text
  speaker: M.K.
  speaker_orig: フィールド環境 M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_02.png
  original: 私はスポーツゲームと恋愛ゲーム以外何でもやるんですが、特に印象に残っているのは『ペルソナ3』と『真・女神転生』シリーズですね。あの洗練されたUI、スタイリッシュなデザイン、悪魔合体の奥深いシステム。ゲームという総合芸術が持つ可能性に圧倒された作品です。
  translation: 我除了体育和恋爱游戏之外什么都玩，印象最深的应该是《女神异闻录3》和《真·女神转生》系列吧。那种洗练的UI、时髦的设计，还有充满深度的恶魔合体系统。这些作品让我深深感受到了游戏作为一门综合艺术的潜力。
  role: answer
- type: heading
  level: 2
  original: 小規模タイトルも大規模タイトルも作ってみたい
  translation: 小规模和大规模的项目都想尝试
- type: heading
  level: 3
  original: 今回転職先にGFを選んだのはなぜですか？
  translation: 这次跳槽为什么会选择GAME FREAK呢？
- type: text
  speaker: Y.I.
  speaker_orig: フィールドコンテンツプログラマ Y.I.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_01.png
  original: 私の場合、新卒で入社して最初に作ったタイトル、本当に頑張って作ったんですが、商業的にはあまり売れなかったんです。それがものすごく悔しくて。「自分が心血を注いで作ったゲームを、もっと何百万、何千万人という世界中の人に遊んでもらいたい！」という渇望がずっとありました。ゲームフリークなら、『ポケットモンスター』という世界最高峰のプラットフォームで、自分の技術を世界中に届けることができる。これ以上ない挑戦だと思いました。
  translation: 我的话，刚毕业时拼尽全力做出来的第一款游戏，在商业上并没有卖得很好。当时真的非常不甘心。所以我心里一直有一种渴望：“想让我倾注心血做出来的游戏，能被全世界几百万、几千万的人玩到！”如果是在GAME FREAK，不仅有《宝可梦》这个世界顶级的平台，还能把自己的技术成果传达到全世界。我觉得没有比这更棒的挑战了。
  role: answer
- type: text
  speaker: M.K.
  speaker_orig: フィールド環境 M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_02.png
  original: 私の場合は、第一にパッケージゲームを作りたいというのがありました。それも、ただのパッケージではなく、「サイズの大きい」タイトルに携わりたかった。そして第二に、「ギアプロジェクト」の存在です。世界規模の大作に携わりながら、同時に少人数で尖った新規タイトルに挑戦できる。この二刀流ができる環境は、他には絶対にありませんでした。
  translation: 我的话，首先是想做实体包装游戏。而且不仅是普通游戏，我还想参与那种“体量很大”的作品。其次就是“齿轮企划”的存在了。在参与世界级大作的同时，还能以小团队去挑战非常硬核的全新原创游戏。能同时兼顾这两种路线的环境，其他地方绝对找不到。
  role: answer
- type: heading
  level: 3
  original: 「サイズが大きい」とはどういうことですか？　また、それに興味があるのはなぜですか？
  translation: “体量很大”具体是指什么呢？又为什么会对这个感兴趣呢？
- type: image
  src: /assets/img/interviews/2015-gamefreak-recruit-programmers/photo_02.png
  caption: 剖析《宝可梦》跨越全年龄层的受众厚度，与承载海量资产的系统工程复杂性
- type: text
  speaker: M.K.
  speaker_orig: フィールド環境 M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_02.png
  original: 「長いプレイ時間」と「広いターゲット層」のことです。『ポケットモンスター』は、ストーリーをクリアして終わりではなく、対戦や育成、図鑑集めなど、何百時間、何千時間と遊ばれ続けます。そして、小学生から親世代まで、世界中のあらゆる世代がプレイする。それだけのスケールを支えるプログラムを作るということは、堅牢性やパフォーマンス、拡張性のすべてにおいて最高峰の設計が求められます。システムエンジニアとして、これほど腕の鳴る舞台はありません。
  translation: 指的是“很长的游玩时间”和“广泛的受众群体”。《宝可梦》并不是通关剧情就结束了，大家还会花几百上千个小时去对战、培育和收集图鉴。而且玩家从小学生到家长，涵盖了全世界各个年龄层。想要写出能支撑起这种规模的程序，在稳定性、性能和扩展性上都需要非常顶级的架构设计。对于一个系统工程师来说，这绝对是最让人跃跃欲试的舞台了。
  role: answer
- type: heading
  level: 2
  original: 若手も早くから活躍する余地がある組織
  translation: 年轻人也能尽早大展身手的团队
- type: heading
  level: 3
  original: 実際入社してみた感想は？
  translation: 实际入职后的感想如何？
- type: text
  speaker: Y.I.
  speaker_orig: フィールドコンテンツプログラマ Y.I.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_01.png
  original: 予想していた以上に、どんどん仕事を任せてもらえて驚いています。今は設計から実装、チューニングまで、プレイヤー挙動のほぼ全般を担当させてもらっています。もちろんプレッシャーは大きいですが、自分の作ったロジックがそのままゲームの骨格になっていく手応えは何物にも代え難いですね。
  translation: 让我挺惊讶的是，公司比我预想的还要敢于放手让人去做。现在从设计、实现到调优，玩家行为逻辑这块基本都是我在负责。当然压力也是挺大的，但看到自己写的逻辑直接变成了游戏的骨架，那种真实感是其他任何东西都无法代替的。
  role: answer
- type: text
  speaker: M.K.
  speaker_orig: フィールド環境 M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_02.png
  original: やっぱり巨大なプロジェクトだなあと思う一方で、意外と原始的な部分、改善の余地がたくさん残されていることにも驚きました。「ゲームフリークって、世界的な大ヒット作を作っているから、開発環境も完全に自動化されて完璧なんだろう」と外からは見えるじゃないですか。でも中に入ってみると、泥臭い手作業が残っていたりする。でもそれは、裏を返せば「自分達の手でいくらでも良くできるフロンティアが広がっている」ということです。エンジニアとしては最高に燃える環境ですよ。
  translation: 一方面确实觉得这真的是个巨大的项目，但另一方面我也挺惊讶的，因为里面意外地保留了很多挺原始的地方，还有很多改善的空间。大家在外面看可能都会觉得“GAME FREAK既然在做世界级的大作，那开发环境肯定也都是全自动化、很完美了吧”。但实际进去一看，其实还留着不少很踏实的手工作业。不过换个角度想，这也意味着“我们可以亲手把它改得更好的空间非常大”。作为一名工程师，这真的是让人超级热血沸腾的环境了。
  role: answer
- type: heading
  level: 3
  original: どの辺りが、原始的だと感じますか？
  translation: 主要是哪些地方让你觉得比较原始呢？
- type: image
  src: /assets/img/interviews/2015-gamefreak-recruit-programmers/photo_03.png
  caption: 探讨从零搭建全新碰撞物理引擎，以及重塑全自动化资源导入管线的技术野心
- type: text
  speaker: Y.I.
  speaker_orig: フィールドコンテンツプログラマ Y.I.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_01.png
  original: モデルやテクスチャの管理方法は、今後ハードのスペックが上がった時に対応しきれなくなるだろうな、という危機感がありました。また、フィールド上のコリジョン（当たり判定）の処理なども、昔ながらのグリッドベースの思想が残っていたりして。フル3Dの自由な地形をスムーズに移動させるためには、もっと現代的なコリジョンエンジンを自前で組み直す必要があると感じました。今まさにその改革に取り組んでいます。
  translation: 比如模型和贴图的管理方式，我就有一种危机感，觉得以后如果硬件性能提升了，现在的这套可能就应付不过来了。另外像地图上的碰撞判定等处理，其实还残留着以前那种基于网格（Grid-based）的思路。为了能在全3D的自由地形上顺畅移动，我觉得还是得自己重写一套更现代的碰撞引擎才行。现在我们刚好就在推动这项改革。
  role: answer
- type: text
  speaker: M.K.
  speaker_orig: フィールド環境 M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_02.png
  original: コミュニケーション手段や情報管理、アセットパイプラインに利用しているツール類ですね。前職や大学で見てきた最新のCI（継続的インテグレーション）や自動ビルドの仕組みを取り入れれば、もっと開発スピードを跳ね上げられる。そうした改善提案を出すと、先輩たちも「いいね、やってみてよ！」とすぐに背中を押してくれます。若手だからといって意見が抑え込まれることは絶対にありません。
  translation: 就是沟通方式、信息管理，还有资产管线所用的一些工具吧。如果能把我在前公司和大学里看到的最新的CI（持续集成）和自动构建机制引进来，开发速度绝对能大幅提升。每次我提出这种改善建议，前辈们也都会马上支持我说：“挺好的，去试试吧！”绝对不会因为你是新人就打压你的意见。
  role: answer
- type: heading
  level: 3
  original: これからGFでやりたいことは何ですか？
  translation: 今后在GAME FREAK有什么想做的事吗？
- type: text
  speaker: Y.I.
  speaker_orig: フィールドコンテンツプログラマ Y.I.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_01.png
  original: 早くマネジメントを任せられるようになりたいですね。あと、前職はミドルウェアを多く使っていたんですが、ゲームフリークは内製技術を非常に大切にする会社です。だからこそ、自分自身の手で新しい技術の基盤を作り、それを社内に根付かせたい。そしてゆくゆくは、ギアプロジェクトで自分がディレクターとなって、世界を唸らせるオリジナルアクションゲームを世に放ちたいです。
  translation: 想早点成为能带团队的管理者呢。另外，我上一份工作用了很多中间件，但GAME FREAK是一家非常看重自研技术的公司。正因如此，我才想亲手打造出新的技术基盘，并让它在公司内部扎根。然后希望将来能在齿轮企划里当上总监，做出一款能让全世界惊叹的原创动作游戏。
  role: answer
- type: text
  speaker: M.K.
  speaker_orig: フィールド環境 M.K.
  avatar: /assets/img/interviews/2015-gamefreak-recruit-programmers/people_02.png
  original: 私は、同じ規模のゲームをより少ない人数で作れるように開発環境を整えていきたいです。ゲームフリークが少数精鋭であり続けるためには、技術による徹底的な効率化が不可欠です。クリエイターが技術的な制約に苦しむことなく、ただ「面白さ」に全エネルギーを注げるような理想郷を作りたい。自分の作ったインフラが会社全体の生産性を何倍にも引き上げる、そんな“縁の下の力持ち”の頂点を目指します。情熱と実力を持ったエンジニアの挑戦を、心から待っています！
  translation: 我的话，是想把开发环境整顿好，让大家能用更少的人数做同样规模的游戏。为了让GAME FREAK能继续保持少数精锐的传统，通过技术来彻底提高效率是必不可少的。我想打造一个理想的环境，让创作者不用再被技术限制所苦，能够把所有的精力都倾注在“好玩”上。我希望自己打造的基础设施能把全公司的生产力提升好几倍，想成为这样一个顶级的“幕后英雄”。真心期待充满热情和实力的工程师们来挑战！
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
