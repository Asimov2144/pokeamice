---
archive_type: interview_translation
layout: parallel-translation
title: GAME FREAK 官方访谈 齿轮企划第2弹：Steam 物理破坏动作神作『GIGA WRECKER』开发秘话（M.O. × H.I.）
title_ja: ギアプロジェクト『GIGA WRECKER』開発秘話
date: 2017-03-01 10:00:00 +0900
era: '2017'
categories:
- developer-interviews
- gamefreak-recruit
tags:
- GAME FREAK
- Gear Project
- 齿轮企划
- GIGA WRECKER
- Steam
- 物理引擎
- 物理破坏解谜
- Indie Stream
- 招聘访谈
- Wayback历史存档
interview_id: PKMN-1028
publication: GAME FREAK 採用情報 (Wayback 历史存档)
original_link: http://web.archive.org/web/20170719132104/http://www.gamefreak.co.jp/recruit/interview_01.html
author: GAME FREAK 採用チーム
interviewee: M.O.（ディレクター / プランナー）, H.I.（プログラマ）
original_lang: ja
translation_lang: zh-CN
summary: GAME FREAK 罕见直接登陆 Steam 平台并试水 Early Access（抢先体验）的物理破坏动作解谜神作《GIGA WRECKER》官方开发复盘：2010 年新卒同期的策划 M.O. 与程序员 H.I.，在经历《宝可梦 黑·白》与《宝可梦 X·Y》洗礼后，携手向齿轮企划发起冲击。专访深度披露了本作如何从最初的“操纵磁力的机器人动作游戏”逐步演进为将敌人与建筑轰碎、利用残骸瓦砾重组凝聚成重锤、方块与斜坡的硬核物理动作解谜；详述了 GAME FREAK 破天荒直接直面全球 PC 核心玩家社区、并在 INDIE STREAM AWARDS 2016 斩获最佳技术奖与评委会特别奖的幕后全貌；展现了年轻一代创作者在独立闭环开发中所获得的飞跃式成长。
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
parallel_items:
- type: image
  src: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/keyvisual.png
  caption: GAME FREAK 官方访谈：齿轮企划『GIGA WRECKER』开发秘话
- type: heading
  level: 2
  original: 社員紹介
  translation: 受访员工简介
- type: profile
  speaker: M.O. & H.I.
  speaker_orig: M.O. & H.I.
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/profile_01.png
  role_ja: プログラマ＆プランナー（2010年新卒入社）
  role_zh: 程序员与策划搭档（2010年新卒同期入社）
  original: 2010年に、新卒で入社したプログラマ&プランナーです。『ポケットモンスターブラック・ホワイト』から『ポケットモンスター』シリーズに携わり、その後ギアプロジェクトに手を挙げて、現在『GIGA WRECKER』を開発しています。
  translation: 我们是 2010 年以应届毕业生（新卒）身份一同入社的程序员与策划组合。从《宝可梦 黑·白》时代起正式投身正统系列的研发，随后主动向公司的“齿轮企划（Gear Project）”递交提案并获准立项，目前正全力领衔开发 Steam 平台物理动作解谜新作《GIGA WRECKER》。
- type: heading
  level: 2
  original: 同期で組んでギアプロジェクトに参加
  translation: 新卒同期搭档：携手叩响齿轮企划的大门
- type: heading
  level: 3
  original: どういった経緯でギアプロジェクトに参加しようと思ったのですか？
  translation: 最初是出于怎样的契机，让两位决定组队参与齿轮企划的？
- type: text
  speaker: M.O.
  speaker_orig: M.O
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/people_01.png
  original: 私達が入社した2010年は、ちょうどギアプロジェクト制度が運用を開始した年なんです。その頃から参加したいとは思っていたのですが、入社して数年は『ポケットモンスター』の開発に必死で、とても他のことを考える余裕がありませんでした。ようやく仕事のペースを掴み、プロジェクトの谷間のタイミングで「そろそろ挑戦してみようか」と声を掛け合いました。
  translation: 我们俩入社的 2010 年，恰恰正是 GAME FREAK 正式启动推行“齿轮企划”制度的那一年。从那时起，我们内心深处就一直萌生着想要亲自参与挑战的火苗；但刚入社的前几年，我们全副身心都深陷在《宝可梦》正统作庞大工期的惊涛骇浪中，根本没有半点余力去思考别的事情。直到后来我们彻底摸清了一线研发的节奏与工法，恰好赶在两部大作交接的休整空档，我们俩一拍即合：“时机成熟了，我们差不多也该放手去博一次了吧！”
- type: text
  speaker: H.I.
  speaker_orig: H.I
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/people_02.png
  original: 私は一度新規タイトルも開発してみたいな、くらいの軽い気持ちで。『ポケットモンスター X・Y』の終盤からゲーム完成リフレッシュ休暇の期間を使って、2人でアイデアを持ち寄って企画書を作成しました。
  translation: 当时我的心态其实相对很纯粹——“好想在自己的职业生涯里，从零开始打造一部全新的原创作品体验一下啊！”就是怀着这样朴素的冲动。我们利用《宝可梦 X·Y》研发尾声直到项目杀青调休假期那段时间，两个人每天聚在一起交换各种疯狂的脑洞与原型灵感，最终打磨成型了初版企划书。
- type: text
  speaker: M.O.
  speaker_orig: M.O
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/people_01.png
  original: ディレクターは私ということになっていますが、今のゲームシステムの根幹となる着想がどちらから出たかも定かではないぐらい2人で色々アイデアを出し合いましたね。
  translation: 虽然挂名上由我担任总监（Director），但坦白讲，现在游戏最根干的那套物理玩法的核心灵感究竟最初是谁脑海里蹦出来的，甚至连我们自己都已经记不清了——因为在整个立项初期，我们完全是毫无保留、互相交织碰撞出了海量的点子。
- type: text
  speaker: H.I.
  speaker_orig: H.I
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/people_02.png
  original: 私はロボットが出てくるゲームが作りたいと思って、前からいろいろネタを考えていました。単純にロボットが好きでして。
  translation: 我个人很早以前就一直心心念念想做一款有机器人登场的游戏，平时肚子里就囤积了各种设定段子。原因极其单纯：因为我就是个不折不扣的机甲控（笑）。
- type: heading
  level: 2
  original: 物理エンジンの活用
  translation: 硬核物理引擎的创意活用与玩法蜕变
- type: heading
  level: 3
  original: どのような経緯で今の形になったのですか？
  translation: 那么，从最初的机甲构想到如今成型的《GIGA WRECKER》，整个演进过程是怎样的？
- type: image
  src: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/photo_01.png
  caption: 探讨如何将瓦砾物理演算、碎片聚合重构与横版动作解谜进行深度融合
- type: text
  speaker: H.I.
  speaker_orig: H.I
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/people_02.png
  original: 当初の企画では主人公は磁力を操る超能力を持っていて、壊したロボットの破片を集められる、という設定でした。それをデザイナーにイラストにしてもらったところ、瓦礫でできた巨大な腕を持つサイボーグ少女のビジュアルができあがってきたんです。それがすごく魅力的で。
  translation: 在最初的第一版案子里，我们的设定是主角拥有操控磁力的超能力，能够把击毁的敌方机器人碎片吸附聚集起来。当我们把这个点子委托给概念设计师绘制插画时，设计师竟反馈回来一张“机械义肢右臂吸附聚集着海量金属瓦砾残骸、化为巨型毁灭兵器的改造人半机械少女”的主视觉图！那个形象极具视觉冲击力与孤独的美感，让我们所有人瞬间被深深俘获。
- type: text
  speaker: M.O.
  speaker_orig: M.O
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/people_01.png
  original: そのメインビジュアルがいかにも戦闘に向いている印象を与えるものだったので、当初はコンボをつなげて敵を爽快に倒していくようなアクションゲームを想定していました。ですが、開発を進める中で、社内で並行して開発されていた『TEMBO THE BADASS ELEPHANT』の存在が大きくなってきたんです。
  translation: 因为那张主视觉概念图实在太具战斗杀伤力了，所以我们一开始很自然地想做成一款不断打出华丽连招、大杀四方的爽快清版动作游戏。然而在实际推进研发的过程中，同在齿轮企划孵化、由 James Turner 领衔并肩作战的《坏象坦博》（TEMBO THE BADASS ELEPHANT）的存在感变得越来越不容忽视。
- type: text
  speaker: H.I.
  speaker_orig: H.I
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/people_02.png
  original: パズルメインのゲームに変更したのは、『TEMBO THE BADASS ELEPHANT』の存在があったからこそですね。向こうが「爽快なアクション」を極めるなら、こちらは頭を使って物理法則を解き明かす「パズルアクション」へと大きく舵を切ろうと。壊した瓦礫を単なる武器として投げるだけでなく、足場にしたり、斜面を作ったり、スイッチを押す重石にしたりと、物理挙動そのものをギミックの核に据えることにしました。
  translation: 决定将游戏的核心支柱全面转向“硬核解谜”，正是因为《坏象坦博》的刺激！既然那边的坦博大象已经把“纯粹野蛮冲撞与破坏爽快感”做到了极致，那我们同门如果再去硬碰硬做纯动作，就毫无区分度了。于是我们果断彻底调转船头——转向开动脑筋、严密拆解物理法则的“物理动作解谜（Physics Puzzle Action）”。将粉碎生成的瓦砾不再仅仅当作远程投掷武器，而是可以随时聚合成垫脚高台、搭建逃生斜坡、或是充当压下重力机关的配重块。我们决定将实打实的 2D 物理引擎碰撞演算本身，铸造成整个关卡设计的灵魂中枢。
- type: text
  speaker: M.O.
  speaker_orig: M.O
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/people_01.png
  original: ターゲットハードも最初はゲーム専用機で考えていました。でも、何かとオブジェクトを破壊して物理挙動を計算させるゲーム性なので、マシンスペックが要求される。また、開発途中の段階からユーザーのフィードバックを直接得てゲームを磨き上げていきたいという思いがあり、Steamでのアーリーアクセス（早期アクセス）という形を選択しました。ゲームフリークとしては前代未闻の挑戦でしたね。
  translation: 而且关于首发目标硬件，我们最初其实也考虑过传统游戏主机平台。但由于游戏的核心机制充斥着无时无刻不在发生的复杂物体粉碎断裂、物理反弹与刚体碰撞，对于硬件算力与物理运算有着极其严苛的要求。加之我们由衷渴望能够从最初期阶段就直面全球最硬核的玩家群体、汲取第一线社区反馈来反复打磨淬炼关卡手感，因此我们最终做出了极其激进的抉择——登陆 Steam 平台，以 Early Access（抢先体验）的模式面向全球发售！这在整个 GAME FREAK 的历史上都是前所未有的破天荒之举。
- type: heading
  level: 3
  original: 『GIGA WRECKER』の見所は何ですか？
  translation: 在两位看来，《GIGA WRECKER》最引以为傲的看点与特色是什么？
- type: image
  src: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/photo_02.png
  caption: 直面 Steam 核心玩家社群反馈，持续快速迭代手感与关卡物理逻辑
- type: text
  speaker: H.I.
  speaker_orig: H.I
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/people_02.png
  original: 物理エンジンを上手く活かせたと思います。物理エンジンを使うと、開発者が意図していなかった挙動が起きることが多々あります。それを単なる「バグ」や「破绽」として排除するのではなく、プレイヤーが「えっ、こんな裏技みたいな解き方でもクリアできるの？！」と驚き、喜べるような自由度の高い遊びとして昇華させました。解法がひとつではない、プレイヤーごとの創意工夫が報われる設計になっています。
  translation: 我认为我们真正把物理引擎这把双刃剑驯服得恰到好处。但凡深入运用物理引擎，就必然会频繁发生无数开发者预料之外的极端物理行为。我们没有简单粗暴地把这些意外当成“Bug”或“逻辑漏洞”全盘扼杀，反而顺水推舟，将其升华为一种让玩家惊呼“天哪，居然用这种近乎逃课的野路子也能解开？！”并为此拍案叫绝的高自由度玩法。每一个谜题绝不存在唯一的死板标准答案，每位玩家天马行空的创意与物理直觉都能在游戏中得到最正向的奖赏。
- type: text
  speaker: M.O.
  speaker_orig: M.O
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/people_01.png
  original: INDIE STREAM AWARDS 2016のBest of TECHNICAL賞と、審査員特別賞を受賞できたことは、私達にとって大きな自信になりました。Steamのユーザーレビューでも、物理パズルの完成度や、切なくも重厚なストーリーを高く評価していただいています。少人数だからこそ、自分達の「好き」と「こだわり」をとことん詰め込むことができました。
  translation: 本作能够一举斩获日本独立游戏权威奖项 INDIE STREAM AWARDS 2016 的“最佳技术奖（Best of Technical）”以及“评委会特别大奖”，对我们团队而言是难以衡量的巨大肯定！在 Steam 的玩家评测区中，全球硬核玩家对我们物理谜题的精巧严密、以及略带忧伤却宏大厚重的末世科幻叙事都给予了极其罕见的高度评价。正因为是极少人数的小编制，我们才得以把我们内心最深沉的“纯粹所爱”与“毫厘考究”毫无妥协地尽数倾注其中。
- type: heading
  level: 2
  original: ギアプロジェクトだからこそできる経験
  translation: 唯有在齿轮企划（Gear Project）中才能斩获的终身成长
- type: heading
  level: 3
  original: ギアプロジェクトに参加するおもしろみと難しさを教えてください。
  translation: 在两位看来，全程主导参与齿轮企划最大的乐趣与最严峻的考验分别是什么？
- type: image
  src: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/photo_03.png
  caption: 在少数精锐的闭环全流程锤炼中，体验亲手掌控游戏每一处细节的绝对快感
- type: text
  speaker: M.O.
  speaker_orig: M.O
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/people_01.png
  original: とにかく全部自分達でやらなければならないのが、おもしろくて、且つ難しいところですね。普段のプロジェクトであれば、専門のスタッフが担当してくれるようなタスク――例えば、Steamのストアページの文面作成や設定、翻訳会社とのやり取り、PVの編集チェック、果ては海外メディアからの問い合わせ対応まで、すべて自分達で判断して進める必要があります。でも、だからこそ「ゲームを世に送り出す」というビジネス全体の流れを肌身で実感できましたし、視野が何倍にも広がりました。
  translation: 归根结底，就是“所有大大小小的一切琐事都必须自己从头干到尾”，这既是让人欲罢不能的最有趣之处，也是最令人脱层皮的艰难考验。在常规的成熟大作项目中，这些琐事都会有庞大的专业职能部门接管分担；但在这里——从 Steam 商店页的本地化文案撰写与后台配置、与全球多语种翻译公司的对接、宣传片 PV 的剪辑与监修，乃至直接用英文回复海外专业游戏媒体的质询邮件，所有一切生死攸关的决策都必须由我们自己亲自拍板！然而正因如此，我们才第一次真正用自己的血肉之躯完整体验了“将一款商业游戏从零孕育并推向全球大市场”的完整工业链路，个人的宏观视野与战略认知因此得到了成倍的跃迁。
- type: text
  speaker: H.I.
  speaker_orig: H.I
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/people_02.png
  original: 本当に何の制限もなく、新しいものを作ることにチャレンジできることが、単純にものすごく楽しかったです。プログラマとしても、既存のフレームワークに頼らず、自分達で物理エンジンを選定し、シェーダーを書き、パフォーマンスを限界までカリカリにチューニングしていく作業は、最高にエキサイティングでした。自分の書いたコードがそのままゲームの手触りになり、世界中のプレイヤーにダイレクトに伝わる。エンジニアとしてこれ以上の喜びはありません。
  translation: 真正没有任何条条框框的束缚、能够纯粹为了创造出从未面世的全新体验而全力以赴挑战，这种快感单纯而强烈到了极致。作为一名程序员，无需依赖任何既定的祖传框架，完全由我们自己自主调研选型物理引擎架构、通宵手写定制 Shader、把每一丝算力性能死磕调优到极限硬件红线——这个过程刺激得让人彻夜难眠。我敲下的每一行代码，都会直接化为屏幕前玩家指尖最直观的操作手感与物理反馈，直达全球玩家的心底。作为一名软件工程师，世上再没有任何成就感能超越这种极致的浪漫了！
- type: heading
  level: 3
  original: これからやりたいことは何ですか？
  translation: 经历过这一役的淬火洗礼后，两位对未来的全新征程有着怎样的期许？
- type: text
  speaker: M.O.
  speaker_orig: M.O
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/people_01.png
  original: 私は今目の前のことで手一杯なんですが、ひとつ思っていることは、ギアプロジェクトで得た経験を、必ず『ポケットモンスター』をはじめとする他の開発にも還元したいということです。新しいプラットフォームでの開発手法や、少人数でのアジャイルな意思決定スピードなど、還元できる要素は山ほどあります。そして、機会があればまた、世界をあっと言わせる新しいオリジナルゲームに挑みたいですね。
  translation: 虽然我现在为了眼前的更新与运营还在全力冲刺，但内心始终坚信的一点是：在齿轮企划中斩获的全部血汗经验，必将毫无保留地反哺给以《宝可梦》为首的公司各大主机主力项目。全新硬件平台与 PC 架构的高效研发范式、极少人数编制下敏捷极速的决策与迭代节奏，所有这些宝贵资产都能给传统管线注入巨大的活力。如果有下一次机会，我必将再度向全公司亮剑，打造出让全世界再次瞠目结舌的全新原创游戏！
- type: text
  speaker: H.I.
  speaker_orig: H.I
  avatar: /assets/img/interviews/2017-gamefreak-gear-gigawrecker/people_02.png
  original: 私はオリジナルタイトルをビジネスとして軌道に乗せて、シリーズ化したいですね。ゲームフリークといえば『ポケットモンスター』ですが、「ゲームフリークのオリジナルアクションゲームもめちゃくちゃ面白い！」と世界中に認知されるようにしたい。ギアプロジェクトは、そうした夢を本気で実現できる場所です。ものづくりに対して貪欲で、情熱を持った仲間がもっと増えてくれたら嬉しいですね。
  translation: 而我的野心是：让我们的原创独立 IP 在商业上彻底走上正轨，并将其成功系列化！一提到 GAME FREAK，全球大众的第一反应永远是《宝可梦》；但我渴望用我们的实力让全世界彻底树立全新的认知——“GAME FREAK 的原创硬核动作游戏同样神乎其神、好玩到炸裂！”齿轮企划正是能够让你把这样看似遥不可及的狂想化为现实的唯一圣地。由衷期盼有更多对造物怀揣无尽贪婪与狂热野心的新伙伴，能够毫不犹豫加入我们的行列！
---
<div class="interview-profiles my-5 p-4 bg-light rounded shadow-sm">
  <h3 class="border-bottom pb-2 mb-4 text-primary fw-bold">受访核心年轻主创背景档案</h3>
  <div class="row g-4">
    <div class="col-md-6 border-end">
      <h4 class="fw-bold mb-1">M.O.</h4>
      <p class="text-muted small mb-1"><strong>入职：</strong>2010年新卒入社（策划 / 游戏总监）</p>
      <p class="text-muted small mb-2"><strong>职务：</strong>《GIGA WRECKER》总监兼主策划 /《宝可梦》一线策划</p>
      <p class="small text-secondary mb-0">从《宝可梦 黑·白》与《宝可梦 X·Y》历练成长，在齿轮企划中主导立项《GIGA WRECKER》，确立物理动作解谜核心机制，并首次主导推进 Steam Early Access 全球社群敏捷运营，荣获 INDIE STREAM AWARDS 2016 评委会特别奖与最佳技术奖。</p>
    </div>
    <div class="col-md-6 ps-md-4">
      <h4 class="fw-bold mb-1">H.I.</h4>
      <p class="text-muted small mb-1"><strong>入职：</strong>2010年新卒入社（核心程序员）</p>
      <p class="text-muted small mb-2"><strong>职务：</strong>《GIGA WRECKER》主程序员 / 物理引擎与底层系统统括</p>
      <p class="small text-secondary mb-0">资深系统与物理引擎专家，独立实现 2D 复杂刚体物理破坏演算与瓦砾重组交互机制，主导极端性能调优与 Shader 定制开发，志在将 GAME FREAK 原创作品推向全球硬核主机与 PC 领域。</p>
    </div>
  </div>
</div>
