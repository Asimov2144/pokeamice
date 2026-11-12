---
archive_type: interview_translation
layout: interview-editorial
title: GIGAZINE 独家特写 GAME FREAK 档案库：从《红／绿》到《日月》绝密手稿大公开——增田顺一与大森滋谈初代汇编极限优化与宝可梦设计原案
subtitle: Game Informer 珍贵影像纪实：盖有「圆秘」印章的特殊球原案、电脑崩溃两天的开发惨剧、8字节控制正弦波与40种波形拼出151只叫声的极客奇迹
date: 2017-09-05 12:37:00 +0900
author: GIGAZINE 編集部 / Game Informer
source_url: https://gigazine.net/news/20170905-pokemon-early-design-documents/
categories:
- developer-interviews
- official-archives
tags:
- '増田順一'
- '大森滋'
- 'Game Freak'
- 'GIGAZINE'
- 'Game Informer'
- '开发手稿'
- '汇编语言'
- '叫声合成'
- '初代红绿'
- '宝可梦 太阳·月亮'
- '底层架构'
era_skin: '2016'
original_lang: ja
interview_id: PKMN-0070
parallel_items:
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/00_m.jpg
  alt: 原文所介绍的宝可梦开发资料视频
- type: heading
  level: 2
  translation: 开发资料与采访视频
- original: シリーズ累計販売本数が2億本を突破したゲーム「ポケットモンスター」のゲーム音楽を作曲したりディレクターやプロデューサーを務めてきた増田順一さんに、ポケットモンスター 赤・緑やポケットモンスターブラック・ホワイト、ポケットモンスター サン・ムーンなどの開発秘話を聞いたり初期デザインやアイデアスケッチなどを見せてもらう、という貴重なムービーが公開されています。An Exclusive Look At Pokémon’s Early Design Documents - YouTube
  translation: Game Informer探访GAME FREAK，增田顺一公开早期手稿与采访视频系列累计销量突破2亿份的游戏《宝可梦》系列中，曾担任游戏音乐作曲、总监及制作人的增田顺一先生，近日接受了一次珍贵采访，谈及《宝可梦 红／绿》《宝可梦 黑／白》《宝可梦 太阳／月亮》等作品的开发秘辛，并展示了早期设计稿与创意草图。这段珍贵影像现已公开。An Exclusive Look At Pokémon’s Early Design Documents - YouTube
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/yt_thumb.jpg
  alt: 原文所介绍的宝可梦开发资料视频
- original: 'Game Informer が公開しているインタビュー動画：[An Exclusive Look At Pokémon’s Early Design Documents (YouTube)](https://www.youtube.com/watch?v=9l8V_eQ6wGQ)'
  translation: 'Game Informer 公开的采访视频：[An Exclusive Look At Pokémon’s Early Design Documents（YouTube）](https://www.youtube.com/watch?v=9l8V_eQ6wGQ)——本文即 GIGAZINE 对这段视频的图文整理。'
- original: インタビューに応えてくれるのはゲームフリークの増田順一さん。
  translation: 接受采访的是GAME FREAK的增田顺一先生。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s01.jpg
  alt: Game Informer 开发资料访谈视频截图
- type: heading
  level: 2
  translation: 《金／银》的纸质企划资料
- speaker: 增田顺一
  original: ゲーム開発における資料などのアーカイブについて質問され、増田さんは「最近は保管プロセスがあるけど、昔はFAXとかで送信しているような紙ベースでやっていたもので、コンピューターで絵を描いたりもしていなかったのでなかなかものが残っていないですよね。特に赤・緑時代とかルビー・サファイア時代はこういうものを見せるとも思っていなかったのでね」と笑いながら回答。
  translation: 当被问及游戏开发过程中资料等内容的存档管理时，增田先生笑着回答道：“如今是有保管流程的，但过去都是靠传真机传送之类的纸质办公方式，也没有用电脑来画画，所以很多东西都没能留存下来。尤其是《宝可梦 红／绿》时代和《宝可梦 红宝石／蓝宝石》时代，当时压根没想过会把这些东西拿出来给人看呢。”
  role: answer
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s02.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: ポケットモンスター 金・銀に登場するガンテツボールの種類やボールの材料などが書かれた資料。紙の右上には丸秘のはんこが押されています。
  translation: 记载了《宝可梦 金／银》中登场的桧皮镇钢铁先生的柑果球（特殊球）种类及制球材料等内容的资料。纸张右上角盖有“丸秘”印章。
- type: heading
  level: 2
  translation: 《红／绿》的开发日记与内存分配
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s03.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: 手で示している部分にあるのは、赤・緑時代のプログラムのバックの何がどこに入っているのかを示すメモ。
  translation: 他手指的位置，是一张标注《红／绿》时代程序Bank中各处存放内容的便签。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s04.jpg
  alt: Game Informer 开发资料访谈视频截图
- speaker: 增田顺一
  original: さらに、開発当時の報告書には「コンピューターのクラッシュにより2日のロス」と書かれているそうです。当時の報告書を見ながら増田さんは、「昔はコンピューターがよくクラッシュしていたので、ポケモン消えなくてよかったと思います」と語ります。
  translation: 此外，当时的开发报告中还写着“因电脑崩溃损失了两天工期”。增田一边看着当时的报告，一边说道：“以前电脑经常崩溃，所以我觉得宝可梦没有彻底消失真是太好了。”
  role: answer
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s05.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: ルビー・サファイアの資料には、レジロック・レジアイス・レジスチルという3体のポケモンをゲットするためのイベントに点字を盛り込む、というアイデアについて書かれています。
  translation: 《红宝石／蓝宝石》的资料中，记载了这样一项创意：在获取雷吉洛克、雷吉艾斯、雷吉斯奇鲁这三只宝可梦的事件中，加入盲文（点字）解谜要素。
- type: heading
  level: 2
  translation: 《黑／白》时期的速写本
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s06.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: 資料のアーカイブを意識し始めたのは2010年に発売されたブラック・ホワイトの開発からだそうで、そこからはアイデアスケッチなどに日にちも書き込むようになったそうです。また、手書きでのアイデア出しも続けており、紙の資料としてまとめやすいからか、スケッチブックを使うようになっていったとのこと。
  translation: 据称，GAME FREAK开始有意识地建立资料档案，是从2010年发售的《宝可梦 黑／白》开发时期开始的，自那之后，他们也会在创意素描等资料上标注日期。此外，手写构思创意的做法也一直延续至今，或许是因为这样更容易整理成纸质资料，他们逐渐开始使用素描本。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s08.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: 「ウインドウのシステムがどう」といった具合に、ちょっとしたことでも思いついたことを書き込んでいる模様。
  translation: “窗口系统该如何如何”——看来即便是些琐碎小事，只要灵光一现，他都会随手记录下来。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s09.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: 人と会話するというのはローカライズが大変なので、文章の組合わせをやめてスタンプにできないか、と考えたメモ。
  translation: 与人对话的本地化工作极为繁重，因此曾考虑放弃文章组合的方式，改用图章印章来替代的备忘录。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s11.jpg
  alt: Game Informer 开发资料访谈视频截图
- speaker: 增田顺一
  original: 「こういうの(紙に)に書いておくと、このアイデアから次のアイデアに進められるというか、アイデアにアイデアを重ねられるので。イラストとかもそうだし、こういうもの(紙にアイデアが残されている)があったときに、それじゃあこういうもの(新しいアイデア)が出せるね、と次々プラスに転じていける」と、アイデアを残しておくことの重要性を語る増田さん。
  translation: “像这样（写在纸上）留下来的话，就能从这个点子推进到下一个点子，或者说，能在点子上不断叠加新的点子。插画之类的也是一样，当这些（留在纸上的点子）摆在那里的时候，就会想‘那么这样的东西（新点子）也能做出来了吧’，于是一步步不断转化为加法。”增田先生如此讲述了留下点子记录的重要性。
  role: answer
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s12.jpg
  alt: Game Informer 开发资料访谈视频截图
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s13.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: 例えば、バトルで自分の手持ちポケモンが振り向くというアイデアをブラック・ホワイト時代に考案したそうですが、これはブラック・ホワイトには実装できなかったそうです。また、メモにはポケモンの性格で振り向くかどうかを決めると書いてあるそうですが、実際にはポケモンをかわいがると振り向くようになるという仕様にして、X・Yで実装することになったとのこと。
  translation: 例如，在《宝可梦 黑／白》时代，他们曾构思过让己方手持宝可梦在战斗中回头望向训练家的点子，但据说这一想法未能在《宝可梦 黑／白》中实现。此外，笔记中还写着要根据宝可梦的性格来决定它是否会回头，但实际做法改成了只要善待、疼爱宝可梦它就会回头，并最终在《宝可梦 X／Y》中实现了这一机制。
- type: heading
  level: 2
  translation: 大森滋的《太阳／月亮》速写
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s14.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: サン・ムーンでディレクターを務めた大森滋さんも登場。
  translation: 《太阳／月亮》总监大森滋也登场了。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s16.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: 実際に会議をしながらスケッチブックにアイデアやスケッチを書くそうで、イメージを共有するために大きなスケッチブックを使用しているとのこと。以下のスケッチブックに描かれているのはサン・ムーンの、バトル開始時のトレーナーやポケモンの登場シーンの流れを記したもの。
  translation: 实际上，他们在开会的同时会在速写本上写下点子和草图，据说为了共享构想，会使用大开本的速写本。下面这本速写本上画的，是《宝可梦 太阳／月亮》中战斗开始时训练家和宝可梦登场场景的流程分镜。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s17.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: さらに、サン・ムーンで実装されたポケリフについてのアイデアメモ。ポケリフレを通してどうやってポケモンと仲良くなるのかのプロセスや、各動作に至るまで細かくアイデアがメモされています。
  translation: 此外，还有一份关于《太阳／月亮》中实装的宝可清爽乐（Pokemon Refresh）的创意笔记。笔记中详细记录了如何通过宝可清爽乐与宝可梦变得亲密的过程，乃至每一个具体动作的细致构想。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s18.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: 以下の資料は戦闘時に与えるダメージに関するパラメーター。しかし、「プログラムしながらどんどん数字とか変えてるから、ここに書かれてる数字が正しいかは別になってくる」とのこと。
  translation: 以下资料涉及战斗时造成伤害的相关参数。不过，据称“因为是一边写程序一边不断改动数字的，所以这里写着的数字是否正确就不一定了”。
- type: heading
  level: 2
  translation: 声音程序与宝可梦叫声
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s19.jpg
  alt: Game Informer 开发资料访谈视频截图
- speaker: 增田顺一
  original: また、「赤・緑時代はアセンブリ言語で書いてるので、かけ算もない言語なので、足し算を回数することでかけ算にしている」と、赤・緑の開発当初を振り返りながら懐かしむ増田さん。
  translation: 此外，增田顺一还回顾并怀念了《红／绿》开发初期的情形：“红绿时代是用汇编语言编写的，那种语言连乘法都没有，所以只能通过反复累加来实现乘法。”
  role: answer
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s20.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: 現在ならばサインカーブを使えばいくらでも細かくデータをとれますが……
  translation: 如今若使用正弦波曲线，数据取样可以做到要多精细有多精细，但当年完全做不到……
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s21.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: 昔は曲線に沿って無数のデータを記録するということはできませんでした。
  translation: 以前，人们无法沿着曲线记录海量的数据。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s22.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: そこで、データの数を減らすためにプラス部分を8つのデータで簡易に表し……
  translation: 于是，为了减少数据量，便将正向部分用8个数据点加以简化表示……
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s23.jpg
  alt: Game Informer 开发资料访谈视频截图
- speaker: 增田顺一
  original: マイナス部分はプラス部分を反転させること表現したそうです。これにより、サインカーブを8バイトと1ビットでコントロールできたとのこと。
  translation: 负半部则通过将正半部直接翻转来表示。由此，仅凭8字节加1比特便能掌控整条正弦波曲线。
  role: answer
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s24.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: また、ポケモンのサウンドプログラムも、赤・緑時代は増田さんが自身で書いていたそうです。鳴き声は以下のように複数の波形を作って表現していたそうです。
  translation: 此外，宝可梦的音频驱动程序在《红／绿》时代也是由增田亲自编写的。宝可梦叫声据说就是通过合成多种波形来表现的，具体如下。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s25.jpg
  alt: Game Informer 开发资料访谈视频截图
- speaker: 增田顺一
  original: 指で示しているのがAパターンの波形。この波形が「プー」という音を鳴らすとします。
  translation: 手指所指的便是A模式波形。假设该波形发出的声音是“噗——”。
  role: answer
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s27.jpg
  alt: Game Informer 开发资料访谈视频截图
- speaker: 增田顺一
  original: こちらはBパターンの波形で、「ポー」という音を鳴らします。
  translation: 这边展示的是B模式的波形，会发出“啵——”的叫声。
  role: answer
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s28.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: AとBの違いはマジックで書いている部分の長さの違いです。
  translation: A与B的区别在于马克笔所画部分的长度不同。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s26.jpg
  alt: Game Informer 开发资料访谈视频截图
- original: 赤・緑ではこの異なる波形を切替えて、「プポポプポ」といった具合にポケモンの鳴き声を表現したそうです。ベースとなる音は40種類ほどしか存在しないそうで、音の長さと音程を変えることで各ポケモンの進化形の鳴き声なども作ったとのこと。
  translation: 在《红／绿》中，正是通过交替切换这些不同的波形，才实现了“噗啵啵噗啵”这般宝可梦叫声的表现。据说作为基础音源的声音仅有约40种，而通过改变声音的长度与音高，连各宝可梦进化形的叫声等也得以制作出来。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s29.jpg
  alt: Game Informer 开发资料访谈视频截图
- speaker: 增田顺一
  original: 最後は「ポケモンの鳴き声がどこか似ているように感じるのはそういった理由から」と増田さんが語り、ムービーは終了です。
  translation: 最后，增田顺一总结道：“玩家之所以会觉得某些宝可梦的叫声听起来有些相似，正是出于这样的原因。”视频至此圆满结束。
  role: answer
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s30.jpg
  alt: Game Informer 开发资料访谈视频截图
interviewee: 增田顺一
source:
  title: ポケットモンスターがどうやって作られているのかが垣間見えるデザイン・アイデアスケッチなどの貴重な資料＆インタビューが聞けるムービーが公開中
  url: https://gigazine.net/news/20170905-pokemon-early-design-documents/
entities:
  people:
  - "增田顺一"
  works:
  - 宝可梦 红·绿
  - 宝可梦 太阳·月亮
summary: "Game Informer 探访 GAME FREAK，增田顺一公开早期开发手稿并接受采访，谈及《宝可梦 红／绿》《宝可梦 金／银》《宝可梦 红宝石／蓝宝石》《宝可梦 黑／白》《宝可梦 太阳／月亮》等作品。他提到《红／绿》以汇编语言开发、无乘法指令只能累加实现，正弦波以 8 个数据点加 1 比特表示，叫声基础音源约 40 种；《金／银》柑果球资料盖有「丸秘」印章；《红宝石／蓝宝石》雷吉三兄弟事件曾构思盲文解谜；档案管理自 2010 年《黑／白》起有意识建立。总监大森滋展示《太阳／月亮》对战登场分镜与宝可清爽乐笔记。"
dek: "增田顺一与大森滋公开《宝可梦》早期手稿与开发细节"
topics:
- "开发流程"
- "系统设计"
- "角色设计"
- "音乐制作"
- "地区设定"
mentions:
  people:
  - "增田顺一"
  - "大森滋"
  works:
  - "宝可梦 金·银"
  - "宝可梦 红宝石·蓝宝石"
  - "宝可梦 黑·白"
  - "宝可梦 X·Y"
---

编译说明：小标题为便于阅读所加；正文依据 GIGAZINE 对采访视频的图文介绍整理。
