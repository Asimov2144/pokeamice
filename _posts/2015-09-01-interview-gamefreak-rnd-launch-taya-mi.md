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
  translation: 我是研究开发部部长S.T.。自1996年进公司以后，从《宝可梦 青》开始的系列作品我都一直在参与。平时主要负责系统和内部设计这块。
  role: answer
- type: profile
  speaker: M.I.
  speaker_orig: プログラマ M.I.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/profile_02.png
  role_ja: プログラマ（2010年入社）
  role_zh: 程序员（2010年入社）
  original: 2010年に入社したプログラマのM.I.です。ゲームフリークに入社する以前からずっと、ゲーム作品の描画まわりを専門にキャリアを積んできました。ゲームフリークでの開発には、『ポケットモンスター』シリーズが本格的に3D化した『ポケットモンスター Ｘ・Ｙ』から参戦。現在は、Maya等のツールのプラグインの開発、キャラクターのレンダリングや、シェーダーのプログラミングを行っています。
  translation: 我是2010年进公司的程序员M.I.。来GAME FREAK之前，我就一直都在专门搞游戏渲染这块的工作。在GAME FREAK这边的开发呢，我是从系列正式3D化的《宝可梦 X·Y》开始加入战局的。目前主要在做Maya等工具的插件开发、角色渲染，还有写写着色器（Shader）之类的。
  role: answer
- type: heading
  level: 2
  original: 「“難しい”を解決し、“作り込みたい”を実現する」
  translation: 「解决“搞不定”，实现“想要死磕到底的细节”」
- type: heading
  level: 3
  original: 研究開発部創設の経緯を教えてください。
  translation: 能和我们聊聊成立研究开发部的来龙去脉吗？
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 研究開発部の必要性を痛感したのは、『ポケットモンスター Ｘ・Ｙ』の開発の時でした。この作品は『ポケットモンスター』シリーズで初めての、フル3Dによるゲーム作品だったんですね。ドット絵からフル3Dになるということで、ゲームを作るためのノウハウやインフラが全く足りていませんでした。それまでは、ゲーム開発のラインが動く中で、並行して必要な技術の研究開発を行っていたんです。でも、ゲーム開発そのものがどんどん高度化・大規模化していく中で、ラインに乗っている人間が新しい技術の研究開発まで同時に行うのは、さすがに無理があるなと。そこで、ゲーム開発のラインとは別に、中長期的な視点で技術の先行投資や基盤づくりを行う専任の組織として、研究開発部を立ち上げることになりました。
  translation: 让我们深切感受到“必须得有个研发部了”的，是在做《宝可梦 X·Y》的时候。这是《宝可梦》系列第一款全3D游戏嘛。从点阵图一下子变成全3D，我们做游戏的经验和基础设施都完全不够用。在那之前，我们都是一边赶项目进度，一边顺手把需要的技术给研发了。但现在游戏开发本身越来越复杂、规模也越来越大，再让生产线上的人同时兼顾新技术研发，实在有点强人所难了。所以呢，我们就决定在游戏生产线之外，专门成立一个立足中长期视角、负责技术前期投资和打地基的专职部门——也就是现在的研究开发部了。
  role: answer
- type: heading
  level: 3
  original: 研究開発部が目標としていることは何ですか？
  translation: 那研究开发部现在的目标是什么呢？
- type: image
  src: /assets/img/interviews/2015-gamefreak-rnd-launch/photo_01.png
  caption: 田谷正夫部长畅谈 R&D 部门如何为一线游戏生产线扫除技术路障、赋能极致创意
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 「“難しい”を解決し、“作り込みたい”を実現する」を標榜しています。『ポケットモンスター』という巨大なコンテンツを支えるため、開発現場には「こういう表現をやってみたいけれど、技術的に難しくて諦めざるを得ない」「もっとクオリティを高めたいけれど、ツールの制限があって作り込めない」という悩みがどうしても生まれてしまう。そうした現場のクリエイターたちの「難しい」を技術力でクリアし、「作り込みたい」というこだわりをとことん形にしてあげることが、私達の最大のミッションです。
  translation: 我们打出的口号是：解决“搞不定”，实现“想要死磕到底的细节”。为了支撑起《宝可梦》这么庞大的内容量，开发一线的同事难免会碰壁，比如“好想试试这种表现手法啊，但技术上太难只能放弃”，或者“想把品质再拔高一点，可工具限制了发挥没法细抠”。用技术实力去帮一线的创作者们扫平这些“搞不定”的障碍，把他们“想要死磕到底”的执念真真切切地做出来，这就是我们最大的使命了。
  role: answer
- type: heading
  level: 2
  original: 『ポケットモンスター』にとっての理想の表現を追求
  translation: 追求对《宝可梦》而言最理想的画面表现
- type: heading
  level: 3
  original: 研究開発部でやっていることを、もう少し具体的に教えてもらえますか？
  translation: 能再具体聊聊研究开发部平时都在忙些什么吗？
- type: image
  src: /assets/img/interviews/2015-gamefreak-rnd-launch/photo_02.png
  caption: 描画专家 M.I. 讲解跨平台着色器管线与针对《宝可梦》手绘插画风的定制渲染算法
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 新しいハードにおける表現方法の研究に力を入れています。もう少し具体的に言うと、キャラクターや背景のレンダリング技術、物理シミュレーション、シェーダーの開発などですね。また、開発環境の改善にも力を入れていて、プログラマやデザイナーが日々の作業をよりスムーズに行えるような内製ツールの開発や、アセットパイプラインの整備も進めています。
  translation: 我们现在正花大力气研究新硬件上的表现手法。具体点说的话，就是角色和背景的渲染技术、物理模拟，还有着色器的开发这些。另外，我们也挺注重改善开发环境的，正在推进内部工具的开发和资产管线的梳理，好让程序员和设计师每天干活能更顺手一点。
  role: answer
- type: heading
  level: 3
  original: 研究開発部に所属したからにはこういうことがやりたい、というのはありますか。
  translation: 既然来到了研究开发部，有没有什么自己特别想搞的东西呢？
- type: text
  speaker: M.I.
  speaker_orig: プログラマ M.I.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_02.png
  original: 進化して制限の少なくなっていくハードのスペックをフルに活かし、ベストな表現を提案していきたいですね。単にフォトリアルを追求するのではなく、『ポケットモンスター』の世界観にマッチした、手触り感のある魅力的なグラフィックとは何か。それを数学的・技術的なアプローチから突き詰めていくのが、私のやりたいことです。
  translation: 现在的硬件性能一直在进化，限制也越来越少了，我希望能充分榨干这些性能，提出最棒的画面表现方案。倒也不是一味地追求逼真写实，而是想去深挖——到底什么才是既符合《宝可梦》世界观、又充满温度和魅力的画面？从数学和技术的角度去把这个问题死磕到底，就是我想干的事儿。
  role: answer
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 私は全体の効率化に興味を持っています。例えば、今もデバッグの自動化を段階的に進めていますが、人の手で行うと何週間もかかるテストプレイを、プログラムによって自動で回せるようにする。それによって浮いた時間を、人間でしかできない「ゲームの面白さの追求」に充ててもらう。会社全体のクリエイティビティを技術で底上げすることを目指しています。
  translation: 我是对整体的效率提升比较感兴趣啦。比如说，我们现在正一步步把测试自动化搞起来。以前靠人工得测上好几个星期的游玩测试，现在直接让程序自动跑就行了。这样省下来的时间，大家就可以拿去干只有人类才能干的事——去“打磨游戏到底好不好玩”。我的目标就是用技术把全公司创造力的下限给抬上去。
  role: answer
- type: heading
  level: 2
  original: 少数精鋭の組織でインパクトの大きい仕事をする
  translation: 在少数精锐的团队里做极具影响力的大事
- type: heading
  level: 3
  original: ゲーム業界にいらっしゃる多くのプログラマが、最初は「ゲームを作ろう」と思ってこの業界に飛び込みますよね。でもその中から、プロダクトのラインを離れ、研究開発の道に進む方々がいらっしゃいます。研究開発のやりがいは何ですか？
  translation: 游戏圈的很多程序员，一开始应该都是怀揣着“我想做游戏”的念头入行的吧。但其中也有一部分人脱离开了具体的产品线，走上了研发的道路。做研发的成就感到底在哪呢？
- type: image
  src: /assets/img/interviews/2015-gamefreak-rnd-launch/photo_03.png
  caption: 在自由而严苛的研发土壤中，用扎实的代码为全球数亿玩家的奇幻世界奠定稳固基石
- type: text
  speaker: M.I.
  speaker_orig: プログラマ M.I.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_02.png
  original: プロダクトのラインを離れても、ゲームをよくしていきたいという根本的な思いは同じです。むしろ、ひとつのタイトルに縛られず、会社全体、ひいてはシリーズ全体の未来を支える基盤を作れるという点に、非常に大きなやりがいを感じています。自分が開発した技術が、次の新しいタイトルで全世界の何千万というプレイヤーに届けられる。そのインパクトの大きさが、日々の研究の原動力になっています。
  translation: 哪怕不直接做产品了，大家“想把游戏做好”的初衷也是一样的。倒不如说，不用被某一款游戏绑死，能去给全公司、甚至给整个系列的未来打地基，这让我觉得特别有价值。想想自己做出来的技术，能跟着下一部新作被送到全世界几千万玩家的手里，这种巨大的影响力，就是我每天搞研究的动力源泉了。
  role: answer
- type: heading
  level: 3
  original: ゲームフリークの研究開発部に向いているのはどんな方だと思いますか？
  translation: 两位觉得，什么样的人会比较适合GAME FREAK的研究开发部呢？
- type: text
  speaker: M.I.
  speaker_orig: プログラマ M.I.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_02.png
  original: 弊社の研究開発部は少数精鋭の組織です。自由度が高く、自分の頑張りに応じて任せてもらえる裁量がどんどん大きくなります。ですから、「指示されたものを作る」のではなく、「何が本当に必要なのか」を自分で見極め、自律的に動ける人が合っていると思いますね。
  translation: 咱们研发部走的是少数精锐路线。自由度挺高的，只要你干得出色，手里的权限也会越给越大。所以我觉得吧，这里不太适合那种“上面说一句就动一下”的人，而是更适合那些能自己琢磨透“现在到底缺什么”，然后主动出击的人。
  role: answer
- type: text
  speaker: S.T.
  speaker_orig: 研究開発部部長 S.T.
  avatar: /assets/img/interviews/2015-gamefreak-rnd-launch/people_01.png
  original: 向いているのはやっぱり、新しい技術に無条件にわくわくできる人。それに加えて、ゲームフリークは決して大企業ではありませんから、「自分はこの専門だからそれ以外はやらない」と壁を作る人よりも、必要とあれば領域を越えて幅広く首を突っ込める好奇心と柔軟性を持った人と一緒に働きたいですね。技術で新しい地平を切り拓きたい方からの挑戦を、心から待っています。
  translation: 说到底，最适合的还是那种一看到新技术就两眼放光、兴奋得不行的人。除此之外嘛，因为GAME FREAK说到底也不是什么超级大厂，所以相比那种画地为牢、觉得“我就懂这个，别的我不管”的人，我们更想和那种必要时能跨界搭把手、好奇心旺盛又懂得变通的小伙伴一起共事。如果你想用技术来开荒新天地，我们可是非常期待你的挑战哦。
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
