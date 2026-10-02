---
archive_type: interview_translation
layout: interview-editorial
title: GAME FREAK 官方专访：研究开发部（R&D）正式始动！「解决所有“困难”，实现所有“极致考究”」（田谷正夫 × M.I.）
title_ja: 研究開発部、始動！「“難しい”を解決し、“作り込みたい”を実現する」
date: 2015-09-01 10:00:00 +0900
era: '2015'
categories:
- developer-interviews
- gamefreak-recruit
tags:
- Game Freak
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
publication: Game Freak 採用情報 (Wayback 历史存档)
original_link: http://web.archive.org/web/20160330115800/http://www.gamefreak.co.jp/recruit/interview_02.html
author: Game Freak 採用チーム
interviewee: 田谷正夫（S.T. / 研究開発部部長）, M.I.（描画プログラマ）
original_lang: ja
translation_lang: zh-CN
summary: 2015 年 GAME FREAK 发展史上里程碑式的技术架构专访：伴随《宝可梦 X·Y》全 3D 化带来的生产管线剧变，GAME FREAK 正式设立独立的研究开发部（R&D）。创设部长田谷正夫（S.T.，自《宝可梦 青》以来执掌系统底层的元老）与资深描画程序员 M.I. 深度披露：为何必须将中长期技术攻关与常规游戏产线彻底解耦；如何在极少人数编制下集中火力解决最卡脖子的渲染与自动化瓶颈；以及面向次世代全新硬件架构，GAME FREAK 如何以“对尖端技术无条件的心潮澎湃”重塑技术立社的工程师文化。
entities:
  people:
  - 田谷正夫
  - M.I.
  works:
  - 宝可梦 X·Y
  - 宝可梦 蓝
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
  translation: 员工介绍
- type: profile
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/profile_01.png
  role_ja: 研究開発部部長（1996年入社）
  role_zh: 研究开发部部长（田谷正夫 / 1996年入社）
  original: 研究開発部部長のS.T.です。1996年に入社して以来、『ポケットモンスター 青』以降のシリーズ作品にずっと関わってきました。メインの担当部分はシステムや内部設計。
  translation: 我是研究开发部部长S.T.。自1996年入社以来，从《宝可梦 青》开始的系列作品我都有参与。主要负责系统和内部设计。
  role: answer
- type: profile
  speaker: M.I.
  speaker_orig: プログラマ M.I.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/profile_02.png
  role_ja: プログラマ（2010年入社）
  role_zh: 程序员（2010年入社）
  original: 2010年に入社したプログラマのM.I.です。ゲームフリークに入社する以前からずっと、ゲーム作品の描画まわりを専門にキャリアを積んできました。ゲームフリークでの開発には、『ポケットモンスター』シリーズが本格的に3D化した『ポケットモンスター Ｘ・Ｙ』から参戦。現在は、Maya等のツールのプラグインの開発、キャラクターのレンダリングや、シェーダーのプログラミングを行っています。
  translation: 我是2010年入社的程序员M.I.。在加入GAME FREAK之前，我便一直专注于游戏作品的渲染相关工作。在GAME FREAK的开发经历中，我是从《宝可梦》系列正式3D化的《宝可梦 X·Y》开始参与的。目前主要进行Maya等工具的插件开发、角色的渲染以及着色器的编程工作。
  role: answer
- type: heading
  level: 2
  original: 「“難しい”を解決し、“作り込みたい”を実現する」
  translation: 「解决“困难”，实现“想要深入打磨的细节”」
- type: heading
  level: 3
  original: 研究開発部創設の経緯を教えてください。
  translation: 请谈谈创立研究开发部的经过。
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 研究開発部の必要性を痛感したのは、『ポケットモンスター Ｘ・Ｙ』の開発の時でした。この作品は『ポケットモンスター』シリーズで初めての、フル3Dによるゲーム作品だったんですね。ドット絵からフル3Dになるということで、ゲームを作るためのノウハウやインフラが全く足りていませんでした。それまでは、ゲーム開発のラインが動く中で、並行して必要な技術の研究開発を行っていたんです。でも、ゲーム開発そのものがどんどん高度化・大規模化していく中で、ラインに乗っている人間が新しい技術の研究開発まで同時に行うのは、さすがに無理があるなと。そこで、ゲーム開発のラインとは別に、中長期的な視点で技術の先行投資や基盤づくりを行う専任の組織として、研究開発部を立ち上げることになりました。
  translation: 让我们切实感到需要研究开发部的，是在《宝可梦 X·Y》开发的时候。这部作品是《宝可梦》系列首部全3D的游戏作品。从点阵图转向全3D，我们在制作游戏的知识经验和基础设施上都存在不足。在此之前，我们是在游戏开发管线运行的同时，并行推进所需技术的研究开发。但是，随着游戏开发本身越来越高度化、大规模化，让处于生产线上的员工同时进行新技术的研发，确实有些勉强了。因此，作为独立于游戏开发管线之外、以中长期视角进行技术前期投资和基础建设的专职组织，我们成立了研究开发部。
  role: answer
- type: heading
  level: 3
  original: 研究開発部が目標としていることは何ですか？
  translation: 研究开发部的目标是什么？
- type: image
  src: /assets/img/interviews/2015-gamefreak-rnd-launch/photo_01.png
  caption: 田谷正夫部长畅谈 R&D 部门如何为一线游戏生产线扫除技术路障、赋能极致创意
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 「“難しい”を解決し、“作り込みたい”を実現する」を標榜しています。『ポケットモンスター』という巨大なコンテンツを支えるため、開発現場には「こういう表現をやってみたいけれど、技術的に難しくて諦めざるを得ない」「もっとクオリティを高めたいけれど、ツールの制限があって作り込めない」という悩みがどうしても生まれてしまう。そうした現場のクリエイターたちの「難しい」を技術力でクリアし、「作り込みたい」というこだわりをとことん形にしてあげることが、私達の最大のミッションです。
  translation: 我们以「解决“困难”，实现“想要深入打磨的细节”」为标语。为了支撑《宝可梦》这一庞大的内容，开发一线难免会产生诸如“虽然想尝试这种表现形式，但因为技术上有难度只能放弃”、“希望能进一步提升品质，但受到工具的限制而无法深入打磨”这样的烦恼。通过技术力量解决一线创作者们的“困难”，将他们“想要深入打磨”的追求彻底化为现实，这是我们最大的使命。
  role: answer
- type: heading
  level: 2
  original: 『ポケットモンスター』にとっての理想の表現を追求
  translation: 追求对《宝可梦》而言理想的表现形式
- type: heading
  level: 3
  original: 研究開発部でやっていることを、もう少し具体的に教えてもらえますか？
  translation: 能再具体谈谈研究开发部正在做的事情吗？
- type: image
  src: /assets/img/interviews/2015-gamefreak-rnd-launch/photo_02.png
  caption: 描画专家 M.I. 讲解跨平台着色器管线与针对《宝可梦》手绘插画风的定制渲染算法
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 新しいハードにおける表現方法の研究に力を入れています。もう少し具体的に言うと、キャラクターや背景のレンダリング技術、物理シミュレーション、シェーダーの開発などですね。また、開発環境の改善にも力を入れていて、プログラマやデザイナーが日々の作業をよりスムーズに行えるような内製ツールの開発や、アセットパイプラインの整備も進めています。
  translation: 我们正致力于研究新硬件上的表现方法。具体来说，包括角色和背景的渲染技术、物理模拟、着色器的开发等。此外，我们也致力于改善开发环境，推进能让程序员和设计师日常工作更顺畅的内部工具开发，以及资产管线的整备。
  role: answer
- type: heading
  level: 3
  original: 研究開発部に所属したからにはこういうことがやりたい、というのはありますか。
  translation: 既然加入了研究开发部，有什么特别想做的事情吗？
- type: text
  speaker: M.I.
  speaker_orig: プログラマ M.I.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_02.png
  original: 進化して制限の少なくなっていくハードのスペックをフルに活かし、ベストな表現を提案していきたいですね。単にフォトリアルを追求するのではなく、『ポケットモンスター』の世界観にマッチした、手触り感のある魅力的なグラフィックとは何か。それを数学的・技術的なアプローチから突き詰めていくのが、私のやりたいことです。
  translation: 我希望能充分利用不断进化、限制越来越少的硬件性能，提出最佳的表现方案。不是单纯地追求写实，而是要去探究什么是契合《宝可梦》世界观、具有触感的极具魅力的画面。通过数学和技术的方法将其追根究底，这就是我想做的事情。
  role: answer
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 私は全体の効率化に興味を持っています。例えば、今もデバッグの自動化を段階的に進めていますが、人の手で行うと何週間もかかるテストプレイを、プログラムによって自動で回せるようにする。それによって浮いた時間を、人間でしかできない「ゲームの面白さの追求」に充ててもらう。会社全体のクリエイティビティを技術で底上げすることを目指しています。
  translation: 我对整体的效率化很感兴趣。例如，现在我们也在分阶段推进调试的自动化。过去需要人工耗费数周时间进行的测试游玩，现在可以通过程序自动运行。这样省下来的时间，就能让大家投入到只有人类才能完成的“追求游戏的趣味性”上。我的目标是通过技术提升全公司的创造力。
  role: answer
- type: heading
  level: 2
  original: 少数精鋭の組織でインパクトの大きい仕事をする
  translation: 在少数精锐的组织中从事具有较大影响力的工作
- type: heading
  level: 3
  original: ゲーム業界にいらっしゃる多くのプログラマが、最初は「ゲームを作ろう」と思ってこの業界に飛び込みますよね。でもその中から、プロダクトのラインを離れ、研究開発の道に進む方々がいらっしゃいます。研究開発のやりがいは何ですか？
  translation: 游戏行业的许多程序员，最初都是抱着“制作游戏”的想法进入这个行业的吧。但其中也有一部分人脱离了产品管线，走上了研究开发的道路。研究开发的成就感体现在哪里？
- type: image
  src: /assets/img/interviews/2015-gamefreak-rnd-launch/photo_03.png
  caption: 在自由而严苛的研发土壤中，用扎实的代码为全球数亿玩家的奇幻世界奠定稳固基石
- type: text
  speaker: M.I.
  speaker_orig: プログラマ M.I.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_02.png
  original: プロダクトのラインを離れても、ゲームをよくしていきたいという根本的な思いは同じです。むしろ、ひとつのタイトルに縛られず、会社全体、ひいてはシリーズ全体の未来を支える基盤を作れるという点に、非常に大きなやりがいを感じています。自分が開発した技術が、次の新しいタイトルで全世界の何千万というプレイヤーに届けられる。そのインパクトの大きさが、日々の研究の原動力になっています。
  translation: 即使脱离了产品管线，想要把游戏做好的根本想法是一样的。不如说，不被单一作品所束缚，能够打造支撑全公司甚至整个系列未来的基础，这一点让我感到非常有价值。自己开发的技术，能够通过下一部新作品传递给全世界数以千万计的玩家。这种巨大的影响力，正是日常研究的动力。
  role: answer
- type: heading
  level: 3
  original: ゲームフリークの研究開発部に向いているのはどんな方だと思いますか？
  translation: 你们认为什么样的人适合GAME FREAK的研究开发部？
- type: text
  speaker: M.I.
  speaker_orig: プログラマ M.I.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_02.png
  original: 弊社の研究開発部は少数精鋭の組織です。自由度が高く、自分の頑張りに応じて任せてもらえる裁量がどんどん大きくなります。ですから、「指示されたものを作る」のではなく、「何が本当に必要なのか」を自分で見極め、自律的に動ける人が合っていると思いますね。
  translation: 我们的研究开发部是少数精锐的组织。自由度很高，根据自己的努力程度，被赋予的裁量权也会越来越大。因此，我认为这里不适合只会“制作被指示的内容”的人，而是适合那些能自己看清“真正需要什么”并自律行动的人。
  role: answer
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 向いているのはやっぱり、新しい技術に無条件にわくわくできる人。それに加えて、ゲームフリークは決して大企業ではありませんから、「自分はこの専門だからそれ以外はやらない」と壁を作る人よりも、必要とあれば領域を越えて幅広く首を突っ込める好奇心と柔軟性を持った人と一緒に働きたいですね。技術で新しい地平を切り拓きたい方からの挑戦を、心から待っています。
  translation: 适合这里的人，归根结底是那种对新技术能无条件感到兴奋的人。除此之外，因为GAME FREAK绝不是大企业，相比于竖起“这是我的专业所以我不做其他事”这样高墙的人，我们更希望能与在必要时跨越领域、有着广泛好奇心和灵活性的同伴一起工作。我们衷心期待那些渴望用技术开拓新境界的人来挑战。
  role: answer
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
