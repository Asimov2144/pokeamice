---
layout: parallel-translation
title: GAME FREAK 官方专访：研究开发部（R&D）正式始动！「解决所有“困难”，实现所有“极致考究”」（田谷正夫 × M.I.）
title_ja: 研究開発部、始動！「“難しい”を解決し、“作り込みたい”を実現する」
date: 2015-09-01 10:00:00 +0900
era: '2015'
categories:
- developer-interviews
- gamefreak-recruit
tags:
- GAME FREAK
- R&D
- 研究开发部
- 田谷正夫
- 渲染引擎
- Shader
- 技术中台
- 自动化测试
- 招聘访谈
- Wayback历史存档
interview_id: PKMN-1024
publication: GAME FREAK 採用情報 (Wayback 历史存档)
original_link: http://web.archive.org/web/20160330115800/http://www.gamefreak.co.jp/recruit/interview_02.html
author: GAME FREAK 採用チーム
interviewee: 田谷正夫（S.T. / 研究開発部部長）, M.I.（描画プログラマ）
original_lang: ja
translation_lang: zh-CN
summary: 2015 年 GAME FREAK 发展史上里程碑式的技术架构专访：伴随《宝可梦 X·Y》全 3D 化带来的生产管线剧变，GAME FREAK 正式设立独立的研究开发部（R&D）。创设部长田谷正夫（S.T.，自《宝可梦 青》以来执掌系统底层的元老）与资深描画程序员 M.I. 深度披露：为何必须将中长期技术攻关与常规游戏产线彻底解耦；如何在极少人数编制下集中火力解决最卡脖子的渲染与自动化瓶颈；以及面向次世代全新硬件架构，GAME FREAK 如何以“对尖端技术无条件的心潮澎湃”重塑技术立社的工程师文化。
entities:
  people:
  - 田谷正夫
  - M.I.
  works:
  - 宝可梦 X／Y
  - 宝可梦 青
  - Gear Project（齿轮企划）
  organizations:
  - 株式会社ゲームフリーク
parallel_items:
- type: image
  src: /assets/img/interviews/2015-gamefreak-rnd-launch/keyvisual.png
  caption: GAME FREAK 官方专访：研究开发部（R&D）正式始动！
- type: heading
  level: 2
  original: 社員紹介
  translation: 受访员工简介
- type: profile
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/profile_01.png
  role_ja: 研究開発部部長（1996年入社）
  role_zh: 研究开发部部长（田谷正夫 / 1996年入社）
  original: 研究開発部部長のS.T.です。1996年に入社して以来、『ポケットモンスター 青』以降のシリーズ作品にずっと関わってきました。メインの担当部分はシステムや内部設計。
  translation: 我是研究开发部部长 S.T.（田谷正夫）。自 1996 年加入 GAME FREAK 以来，从《宝可梦 青》开始全程参与了后续每一代正统系列作的研发。我主要负责的专业领域是系统底层构建与核心内部软件架构设计。
- type: profile
  speaker: M.I.
  speaker_orig: プログラマ M.I.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/profile_02.png
  role_ja: プログラマ（2010年入社）
  role_zh: 程序员（2010年入社）
  original: 2010年に入社したプログラマのM.I.です。ゲームフリークに入社する以前からずっと、ゲーム作品の描画まわりを専門にキャリアを積んできました。ゲームフリークでの開発には、『ポケットモンスター』シリーズが本格的に3D化した『ポケットモンスター Ｘ・Ｙ』から参戦。現在は、Maya等のツールのプラグインの開発、キャラクターのレンダリングや、シェーダーのプログラミングを行っています。
  translation: 我是 2010 年入社的程序员 M.I.。在加入 GAME FREAK 之前，我便一直专注于游戏图形渲染与描画管线的深耕。加入公司后，我从《宝可梦》系列正式迈入全 3D 时代的里程碑作品《宝可梦 X·Y》开始参战。目前主要负责自主研发 Maya 等 DCC 美术工具的定制插件、角色实时渲染管线架构以及定制着色器（Shader）的编程攻坚。
- type: heading
  level: 2
  original: 「“難しい”を解決し、“作り込みたい”を実現する」
  translation: 「攻克一切“困难”，实现所有“极致考究”」
- type: heading
  level: 3
  original: 研究開発部創設の経緯を教えてください。
  translation: 请首先谈谈为何要在 GAME FREAK 内部正式创设“研究开发部（R&D）”？
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 研究開発部の必要性を痛感したのは、『ポケットモンスター Ｘ・Ｙ』の開発の時でした。この作品は『ポケットモンスター』シリーズで初めての、フル3Dによるゲーム作品だったんですね。ドット絵からフル3Dになるということで、ゲームを作るためのノウハウやインフラが全く足りていませんでした。それまでは、ゲーム開発のラインが動く中で、並行して必要な技術の研究開発を行っていたんです。でも、ゲーム開発そのものがどんどん高度化・大規模化していく中で、ラインに乗っている人間が新しい技術の研究開発まで同時に行うのは、さすがに無理があるなと。そこで、ゲーム開発のラインとは別に、中長期的な視点で技術の先行投資や基盤づくりを行う専任の組織として、研究開発部を立ち上げることになりました。
  translation: 让我们痛彻心扉意识到必须建立专门 R&D 部门的转折点，正是当年《宝可梦 X·Y》的开发战役。那是整个正统系列史上第一次挑战全 3D 呈现。从延续了十几年的 2D 点阵像素画跨越到全 3D 建模，我们在技术储备、工具链体系与基础设施资产管线上都面临着巨大的缺口。在此之前，我们往往是在具体游戏项目紧锣密鼓推进的同时，由一线项目组人员‘顺便’兼顾新技术的前期摸索。然而随着现代游戏工业体系的高度化与规模急速膨胀，让身处火线交付压力下的开发人员再去分心攻克未知的底层尖端技术，显然已经达到了生理与组织的极限。因此，我们痛下决心设立研究开发部——一个独立于具体游戏生产管线之外，完全立足于中长期战略视角、专事底层技术先行投资与核心基座搭建的专职精锐军团。
- type: heading
  level: 3
  original: 研究開発部が目標としていることは何ですか？
  translation: 研究开发部所确立的核心宗旨与奋斗目标是什么？
- type: image
  src: /assets/img/interviews/2015-gamefreak-rnd-launch/photo_01.png
  caption: 田谷正夫部长畅谈 R&D 部门如何为一线游戏生产线扫除技术路障、赋能极致创意
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 「“難しい”を解決し、“作り込みたい”を実現する」を標榜しています。『ポケットモンスター』という巨大なコンテンツを支えるため、開発現場には「こういう表現をやってみたいけれど、技術的に難しくて諦めざるを得ない」「もっとクオリティを高めたいけれど、ツールの制限があって作り込めない」という悩みがどうしても生まれてしまう。そうした現場のクリエイターたちの「難しい」を技術力でクリアし、「作り込みたい」というこだわりをとことん形にしてあげることが、私達の最大のミッションです。
  translation: 我们的核心旗帜就是「攻克一切“困难”，实现所有“极致考究”」。为了支撑起《宝可梦》这样庞大体量的内容创作，一线开发工地上不可避免地会诞生各种痛点——“我们非常想实现某种全新的视觉或交互，但因为技术门槛太高只能忍痛割爱”、“我们渴望把场景生态打磨得更细致，却受限于现有 DCC 工具与引擎性能而无法继续深入”。面对一线创作者们遭遇的各种硬壁，用绝对扎实的底层技术力帮他们彻底扫除阻碍，让他们心中那份对细节死磕到底的“极致考究”能够无拘无束地在屏幕上化为现实，这正是我们身为研发中台最崇高的神圣使命。
- type: heading
  level: 2
  original: 『ポケットモンスター』にとっての理想の表現を追求
  translation: 为『宝可梦』追求无与伦比的理想图形表现
- type: heading
  level: 3
  original: 研究開発部でやっていることを、もう少し具体的に教えてもらえますか？
  translation: 能否向我们更具体地介绍一下研究开发部目前正在攻坚推进的核心课题？
- type: image
  src: /assets/img/interviews/2015-gamefreak-rnd-launch/photo_02.png
  caption: 描画专家 M.I. 讲解跨平台着色器管线与针对《宝可梦》手绘插画风的定制渲染算法
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 新しいハードにおける表現方法の研究に力を入れています。もう少し具体的に言うと、キャラクターや背景のレンダリング技術、物理シミュレーション、シェーダーの開発などですね。また、開発環境の改善にも力を入れていて、プログラマやデザイナーが日々の作業をよりスムーズに行えるような内製ツールの開発や、アセットパイプラインの整備も進めています。
  translation: 我们目前正倾注全力在全新次世代硬件架构上的先锋表现力研究。具体而言，包括角色与庞大自然生态背景的实时渲染底层技术、高拟真物理碰撞与软体模拟、以及独门定制着色器（Shader）的攻坚开发。同时，我们高度重视开发环境的现代化重构，持续自主研发能够让一线程序员与设计师更丝滑协作的专用生产力工具，并全面革新全自动化资产导入与烘焙管线（Asset Pipeline）。
- type: heading
  level: 3
  original: 研究開発部に所属したからにはこういうことがやりたい、というのはありますか。
  translation: 置身于研究开发部这个先锋阵地，两位心中各自有着怎样不可动摇的野心与目标？
- type: text
  speaker: M.I.
  speaker_orig: プログラマ M.I.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_02.png
  original: 進化して制限の少なくなっていくハードのスペックをフルに活かし、ベストな表現を提案していきたいですね。単にフォトリアルを追求するのではなく、『ポケットモンスター』の世界観にマッチした、手触り感のある魅力的なグラフィックとは何か。それを数学的・技術的なアプローチから突き詰めていくのが、私のやりたいことです。
  translation: 随着游戏硬件的跨越式进化与算力枷锁的不断打破，我渴望能够百分之百榨干未来硬件的极限性能，主动向全公司提出最具前瞻性的颠覆式表现方案。我们所追求的绝不是随波逐流去堆砌毫无灵魂的工业化写实画风（Photorealism），而是去深究：究竟什么是与《宝可梦》那温暖世界观最为契合、饱含生物呼吸感与手绘触感温度的终极视觉语言？用严密的数学算法与底层图形技术架构去无限逼近并揭开这一终极命题，正是我全力以赴的毕生追求。
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 私は全体の効率化に興味を持っています。例えば、今もデバッグの自動化を段階的に進めていますが、人の手で行うと何週間もかかるテストプレイを、プログラムによって自動で回せるようにする。それによって浮いた時間を、人間でしかできない「ゲームの面白さの追求」に充ててもらう。会社全体のクリエイティビティを技術で底上げすることを目指しています。
  translation: 而我则对整个研发全流程的体系化极致提效抱有极其深厚的热情。比如我们正在分阶段强力推进的“自动化回归测试与自动化 Debug 体系”——过去需要耗费整整几周时间由测试人员纯人工机械重复的验证流程，通过我们自研的自动化脚本与机器集群即可在后台彻夜不休地自动跑通并精准捕获崩溃隐患。通过技术把一线员工从枯燥繁琐的低效消耗中解放出来，省下来的海量时间便能让他们百分之百投入到只有人类才能完成的核心工作——“对游戏本质乐趣的纯粹推敲”。用底层前沿科技从根基上成倍放大整座公司的创造力，正是我的终极诉求。
- type: heading
  level: 2
  original: 少数精鋭の組織でインパクトの大きい仕事をする
  translation: 在少数精锐组织中，创造具有震撼影响力的卓越战果
- type: heading
  level: 3
  original: ゲーム業界にいらっしゃる多くのプログラマが、最初は「ゲームを作ろう」と思ってこの業界に飛び込みますよね。でもその中から、プロダクトのラインを離れ、研究開発の道に進む方々がいらっしゃいます。研究開発のやりがいは何ですか？
  translation: 游戏行业里的绝大多数程序员，最初想必都是抱着“我想亲手做游戏”的赤诚冲进这个领域的。然而其中一部分顶尖人才却选择脱离一线产品工期，走上研究开发这门苦行僧般的深水区。在你们看来，投身 R&D 研发最纯粹的成就感与意义是什么？
- type: image
  src: /assets/img/interviews/2015-gamefreak-rnd-launch/photo_03.png
  caption: 在自由而严苛的研发土壤中，用扎实的代码为全球数亿玩家的奇幻世界奠定稳固基石
- type: text
  speaker: M.I.
  speaker_orig: プログラマ M.I.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_02.png
  original: プロダクトのラインを離れても、ゲームをよくしていきたいという根本的な思いは同じです。むしろ、ひとつのタイトルに縛られず、会社全体、ひいてはシリーズ全体の未来を支える基盤を作れるという点に、非常に大きなやりがいを感じています。自分が開発した技術が、次の新しいタイトルで全世界の何千万というプレイヤーに届けられる。そのインパクトの大きさが、日々の研究の原動力になっています。
  translation: 即便在组织编制上脱离了某个具体的单款产品产线，但我们内心深处想要把游戏做到极致的根源热爱，与一线将士没有任何区别。倒不如说，正因为不被单一作品眼前的交付工期所束缚，我们反而能够站上俯瞰整个全局的高度，亲手打造支撑起全公司跨代、支撑起整个正统系列未来十数年发展演进的宏伟技术基石。我亲手编写的一段着色器算法、搭建的一套管线工具，将在未来的全新作品中直接承载并传递给全世界数千万甚至上亿玩家——这种超越单一项目的巨大影响力，正是驱动我们在底层代码世界中不知疲倦、日夜攻坚的最强引擎。
- type: heading
  level: 3
  original: ゲームフリークの研究開発部に向いているのはどんな方だと思いますか？
  translation: 两位认为什么样特质与技术背景的人才，最适合加入 GAME FREAK 的研究开发部？
- type: text
  speaker: M.I.
  speaker_orig: プログラマ M.I.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_02.png
  original: 弊社の研究開発部は少数精鋭の組織です。自由度が高く、自分の頑張りに応じて任せてもらえる裁量がどんどん大きくなります。ですから、「指示されたものを作る」のではなく、「何が本当に必要なのか」を自分で見極め、自律的に動ける人が合っていると思いますね。
  translation: 我们 GAME FREAK 的研究开发部是一个极度精干的少数精锐团队。这里没有任何官僚教条，探索自由度极高，只要你拿出硬核过硬的战果，公司赋予你的技术裁量权和试错空间就会成倍剧增。因此，我们最需要的绝不是那种只会等待领导拆解需求、被动交差的“螺丝钉”，而是能够时刻保持敏锐洞察力，自己去主动洞悉全流程中最迫切需要攻克的软肋与机遇、能够极度自律自驱推进战役的独立研究员。
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 向いているのはやっぱり、新しい技術に無条件にわくわくできる人。それに加えて、ゲームフリークは決して大企業ではありませんから、「自分はこの専門だからそれ以外はやらない」と壁を作る人よりも、必要とあれば領域を越えて幅広く首を突っ込める好奇心と柔軟性を持った人と一緒に働きたいですね。技術で新しい地平を切り拓きたい方からの挑戦を、心から待っています。
  translation: 最契合这里的灵魂，归根结底必须是那种一看到未曾探索过的新技术就会无条件心潮澎湃、两眼放光的人！在此之上必须认清的是，GAME FREAK 虽然打造了举世闻名的超级 IP，但我们的团队规模始终极其精简克制，本质上绝不是人员冗余的臃肿大企业。因此，相比于那些划地自限说“我只负责我这一亩三分地、其他一概不管”的狭隘匠人，我们由衷期待与那些当团队需要时能够毫不犹豫打破专业壁垒、带着无尽好奇心与极高适应力在各个未知领域横冲直撞的开拓者并肩作战。如果你渴望用颠覆性的硬核技术为全球玩家开拓前所未见的奇迹地平线，GAME FREAK 研究开发部随时敞开大门等待你的加入！
---

<div class="interview-profiles my-5 p-4 bg-light rounded shadow-sm">
  <h3 class="border-bottom pb-2 mb-4 text-primary fw-bold">受访核心技术主管背景档案</h3>
  <div class="row g-4">
    <div class="col-md-6 border-end">
      <h4 class="fw-bold mb-1">田谷 正夫（S.T.）</h4>
      <p class="text-muted small mb-1"><strong>入职：</strong>1996年入社（GAME FREAK 元老级系统总监）</p>
      <p class="text-muted small mb-2"><strong>职务：</strong>研究开发部部长 / 核心系统架构师</p>
      <p class="small text-secondary mb-0">从 1996 年《宝可梦 青》时代起统管整个正统系列的游戏系统底座与内部架构设计；在全 3D 转型期主导创设 GAME FREAK 独立研究开发部（R&D），确立自动化测试与次世代管线基石。</p>
    </div>
    <div class="col-md-6 ps-md-4">
      <h4 class="fw-bold mb-1">M.I.</h4>
      <p class="text-muted small mb-1"><strong>入职：</strong>2010年中途入社</p>
      <p class="text-muted small mb-2"><strong>职务：</strong>图形渲染程序员（描画プログラマ）/ Shader 专家</p>
      <p class="small text-secondary mb-0">资深游戏图形渲染专家，经历《宝可梦 X·Y》全 3D 化大攻坚，深度主导 Maya 定制插件开发、宝可梦角色实时渲染管线架构与独门手绘水彩风格 Shader 算法攻关。</p>
    </div>
  </div>
</div>
