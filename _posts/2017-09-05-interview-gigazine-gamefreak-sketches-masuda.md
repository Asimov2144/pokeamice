---
layout: parallel-translation
title: GIGAZINE 独家特写 GAME FREAK 档案库：从《红／绿》到《日月》绝密手稿大公开——增田顺一与大森滋谈初代汇编极限优化与宝可梦设计原案
subtitle: Game Informer 珍贵影像纪实：盖有「圆秘」印章的特殊球原案、电脑崩溃两天的开发惨剧、8字节控制正弦波与40种波形拼出151只叫声的极客奇迹
date: 2017-09-05 12:37:00 +0900
author: GIGAZINE 編集部 / Game Informer
source_url: https://gigazine.net/news/20170905-pokemon-early-design-documents/
categories:
- developer-interviews
- official-archives
tags:
- 増田順一
- 大森滋
- GAME FREAK
- GIGAZINE
- Game Informer
- 开发手稿
- 汇编语言
- 叫声合成
- 初代红绿
- 太阳月亮
- 底层架构
era_skin: '2016'
original_lang: ja
interview_id: PKMN-0070
parallel_items:
- type: heading
  level: 2
  original: プロローグ：Game Informer × GAME FREAK――封印された開発資料の解禁
  translation: 序章：Game Informer × GAME FREAK——尘封开发手稿的破例解禁
- original: シリーズ累計販売本数が2億本を突破したゲーム「ポケットモンスター」のゲーム音楽を作曲したりディレクターやプロデューサーを務めてきた増田順一さんに、ポケットモンスター
    赤・緑やポケットモンスターブラック・ホワイト、ポケットモンスター サン・ムーンなどの開発秘話を聞いたり初期デザインやアイデアスケッチなどを見せてもらう、という貴重なムービーが公開されています。An
    Exclusive Look At Pokémon’s Early Design Documents - YouTube
  translation: Game Informer探访GAME FREAK，增田顺一公开早期手稿与采访视频系列累计销量突破2亿份的游戏《宝可梦》系列中，曾担任游戏音乐作曲、总监及制作人的增田顺一先生，近日接受了一次珍贵采访，谈及《宝可梦
    红／绿》《宝可梦 黑／白》《宝可梦 太阳／月亮》等作品的开发秘辛，并展示了早期设计稿与创意草图。这段珍贵影像现已公开。An Exclusive Look At
    Pokémon’s Early Design Documents - YouTube
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/yt_thumb.jpg
  caption: Game Informer 独家视频专访：增田顺一与大森滋展示宝可梦早期珍贵企划手稿与开发档案。
  alt: Game Informer 独家专访封面
- original: インタビューに応えてくれるのはゲームフリークの増田順一さん。
  translation: 接受采访的是GAME FREAK的增田顺一先生。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s01.jpg
  caption: 增田顺一谈及早期档案管理：在传真与纸质办公的红绿时代，从未想过未来会向公众展示这些草稿。
  alt: 增田顺一受访微笑
- type: heading
  level: 2
  original: 第1章：伝票とFAXの時代――『金・銀』ガンテツボールと「丸秘」印章
  translation: 第1章：传真与纸质办公时代——《金／银》柑果球企划与「圆秘」印章
- speaker: 增田顺一
  original: ゲーム開発における資料などのアーカイブについて質問され、増田さんは「最近は保管プロセスがあるけど、昔はFAXとかで送信しているような紙ベースでやっていたもので、コンピューターで絵を描いたりもしていなかったのでなかなかものが残っていないですよね。特に赤・緑時代とかルビー・サファイア時代はこういうものを見せるとも思っていなかったのでね」と笑いながら回答。
  translation: 当被问及游戏开发过程中资料等内容的存档管理时，增田先生笑着回答道：“如今是有保管流程的，但过去都是靠传真机传送之类的纸质办公方式，也没有用电脑来画画，所以很多东西都没能留存下来。尤其是《宝可梦
    红／绿》时代和《宝可梦 红宝石／蓝宝石》时代，当时压根没想过会把这些东西拿出来给人看呢。”
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s02.jpg
  caption: 《宝可梦 金／银》钢铁先生柑果球设定手稿：纸张右上角清晰盖有“丸秘（绝密）”红色印章，详细记录了各色球的材质与捕获机能。
  alt: 金银钢铁先生特殊球圆秘手稿
- original: ポケットモンスター 金・銀に登場するガンテツボールの種類やボールの材料などが書かれた資料。紙の右上には丸秘のはんこが押されています。
  translation: 记载了《宝可梦 金／银》中登场的桧皮镇钢铁先生的柑果球（特殊球）种类及制球材料等内容的资料。纸张右上角盖有“丸秘”印章。
- type: heading
  level: 2
  original: 第2章：クラッシュとメモリ配分――『赤・緑』開発日誌と2日の消失
  translation: 第2章：崩溃日记与内存分配——《红／绿》开发手账与“丢失两日”
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s03.jpg
  caption: 增田顺一手指指出的是《宝可梦 红／绿》时代的汇编程序内存银行（Bank）空间分配手写便签。
  alt: 红绿时代内存分配便签
- original: 手で示している部分にあるのは、赤・緑時代のプログラムのバックの何がどこに入っているのかを示すメモ。
  translation: 他手指的位置，是一张标注《红／绿》时代程序Bank中各处存放内容的便签。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s04.jpg
  caption: 1990年代GAME FREAK开发周报残卷：赫然写着“电脑系统崩溃导致损失2天进度”。增田感叹万幸当时宝可梦数据没有彻底灰飞烟灭。
  alt: 电脑崩溃损失2天开发报告
- speaker: 增田顺一
  original: さらに、開発当時の報告書には「コンピューターのクラッシュにより2日のロス」と書かれているそうです。当時の報告書を見ながら増田さんは、「昔はコンピューターがよくクラッシュしていたので、ポケモン消えなくてよかったと思います」と語ります。
  translation: 此外，当时的开发报告中还写着“因电脑崩溃损失了两天工期”。增田一边看着当时的报告，一边说道：“以前电脑经常崩溃，所以我觉得宝可梦没有彻底消失真是太好了。”
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s05.jpg
  caption: 《宝可梦 红宝石／蓝宝石》雷吉洛克、雷吉艾斯、雷吉斯奇鲁三神柱捕捉事件的盲文（点字）系统设计原案草稿。
  alt: 宝石版盲文三神柱企划案
- original: ルビー・サファイアの資料には、レジロック・レジアイス・レジスチルという3体のポケモンをゲットするためのイベントに点字を盛り込む、というアイデアについて書かれています。
  translation: 《红宝石／蓝宝石》的资料中，记载了这样一项创意：在获取雷吉洛克、雷吉艾斯、雷吉斯奇鲁这三只宝可梦的事件中，加入盲文（点字）解谜要素。
- type: heading
  level: 2
  original: 第3章：アイデアの積層――『ブラック・ホワイト』からのスケッチブック革命
  translation: 第3章：灵感的层叠累加——从《黑／白》开始的速写本档案革命
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s06.jpg
  caption: 从2010年《宝可梦 黑／白》开发起，GAME FREAK开始规范化档案管理，团队成员在大型素描本上记录灵感并标明具体日期。
  alt: 黑白开发速写本手稿
- original: 資料のアーカイブを意識し始めたのは2010年に発売されたブラック・ホワイトの開発からだそうで、そこからはアイデアスケッチなどに日にちも書き込むようになったそうです。また、手書きでのアイデア出しも続けており、紙の資料としてまとめやすいからか、スケッチブックを使うようになっていったとのこと。
  translation: 据称，GAME FREAK开始有意识地建立资料档案，是从2010年发售的《宝可梦 黑／白》开发时期开始的，自那之后，他们也会在创意素描等资料上标注日期。此外，手写构思创意的做法也一直延续至今，或许是因为这样更容易整理成纸质资料，他们逐渐开始使用素描本。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s08.jpg
  caption: 关于游戏内UI窗口系统与菜单排版的随想手绘草图，哪怕转瞬即逝的微小灵感也随时落在纸面上。
  alt: UI窗口系统草图
- original: 「ウインドウのシステムがどう」といった具合に、ちょっとしたことでも思いついたことを書き込んでいる模様。
  translation: “窗口系统该如何如何”——看来即便是些琐碎小事，只要灵光一现，他都会随手记录下来。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s09.jpg
  caption: 为简化多国语言本地化难题而构想的“图章戳印（Stamp）拼词交流”手稿，这也成为后续世代在线表情包交流的原型构想。
  alt: 图章替代长文本本地化交流草稿
- original: 人と会話するというのはローカライズが大変なので、文章の組合わせをやめてスタンプにできないか、と考えたメモ。
  translation: 与人对话的本地化工作极为繁重，因此曾考虑放弃文章组合的方式，改用图章印章来替代的备忘录。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s11.jpg
  caption: 增田顺一动情阐述“保留纸质手稿”的真谛：唯有让过去的想法留下实体痕迹，才能在旧灵感之上不断堆叠进化出全新奇迹。
  alt: 增田讲述灵感累加哲学
- speaker: 增田顺一
  original: 「こういうの(紙に)に書いておくと、このアイデアから次のアイデアに進められるというか、アイデアにアイデアを重ねられるので。イラストとかもそうだし、こういうもの(紙にアイデアが残されている)があったときに、それじゃあこういうもの(新しいアイデア)が出せるね、と次々プラスに転じていける」と、アイデアを残しておくことの重要性を語る増田さん。
  translation: “像这样（写在纸上）留下来的话，就能从这个点子推进到下一个点子，或者说，能在点子上不断叠加新的点子。插画之类的也是一样，当这些（留在纸上的点子）摆在那里的时候，就会想‘那么这样的东西（新点子）也能做出来了吧’，于是一步步不断转化为加法。”增田先生如此讲述了留下点子记录的重要性。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s12.jpg
  caption: 黑白时期构思的“宝可梦在对战中回头看训练家”的分镜草图（未能在BW硬件中实现）。
  alt: 对战宝可梦回头动作草图
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s13.jpg
  caption: 回头机制手稿笔记：原案曾设想根据性格决定是否回头，最终在《X／Y》中演化为结合“宝友会”羁绊好感度的回头互动机制。
  alt: 回头机制演化笔记
- original: 例えば、バトルで自分の手持ちポケモンが振り向くというアイデアをブラック・ホワイト時代に考案したそうですが、これはブラック・ホワイトには実装できなかったそうです。また、メモにはポケモンの性格で振り向くかどうかを決めると書いてあるそうですが、実際にはポケモンをかわいがると振り向くようになるという仕様にして、X・Yで実装することになったとのこと。
  translation: 例如，在《宝可梦 黑／白》时代，他们曾构思过让己方手持宝可梦在战斗中回头望向训练家的点子，但据说这一想法未能在《宝可梦 黑／白》中实现。此外，笔记中还写着要根据宝可梦的性格来决定它是否会回头，但实际做法改成了只要善待、疼爱宝可梦它就会回头，并最终在《宝可梦
    X／Y》中实现了这一机制。
- type: heading
  level: 2
  original: 第4章：大森滋のA3スケッチ――『サン・ムーン』対戦演出とポケリフレ
  translation: 第4章：大森滋的A3大型速写——《太阳／月亮》对战运镜与宝可清爽乐
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s14.jpg
  caption: 《宝可梦 太阳／月亮》总监大森滋登场，手持开会时用于团队概念对齐的巨大A3速写本。
  alt: 大森滋展示大型速写本
- original: サン・ムーンでディレクターを務めた大森滋さんも登場。
  translation: 《太阳／月亮》总监大森滋也登场了。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s16.jpg
  caption: 《太阳／月亮》对战开场分镜脚本：训练家抛球姿态、镜头机位推进与宝可梦跃出光芒的动态连环草图。
  alt: 日月对战开场镜头分镜
- original: 実際に会議をしながらスケッチブックにアイデアやスケッチを書くそうで、イメージを共有するために大きなスケッチブックを使用しているとのこと。以下のスケッチブックに描かれているのはサン・ムーンの、バトル開始時のトレーナーやポケモンの登場シーンの流れを記したもの。
  translation: 实际上，他们在开会的同时会在速写本上写下点子和草图，据说为了共享构想，会使用大开本的速写本。下面这本速写本上画的，是《宝可梦 太阳／月亮》中战斗开始时训练家和宝可梦登场场景的流程分镜。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s17.jpg
  caption: 《太阳／月亮》“宝可清爽乐（Pokémon Refresh）”系统设计笔记：从触碰、梳理、喂食到亲密度提升状态反馈的详细流程规划。
  alt: 宝可清爽乐互动流程笔记
- original: さらに、サン・ムーンで実装されたポケリフについてのアイデアメモ。ポケリフレを通してどうやってポケモンと仲良くなるのかのプロセスや、各動作に至るまで細かくアイデアがメモされています。
  translation: 此外，还有一份关于《太阳／月亮》中实装的宝可清爽乐（Pokemon Refresh）的创意笔记。笔记中详细记录了如何通过宝可清爽乐与宝可梦变得亲密的过程，乃至每一个具体动作的细致构想。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s18.jpg
  caption: 对战伤害计算公式与数值参数平衡手稿。增田笑称程序敲着敲着数值天天都在改，纸上数字只是当时的一个快照。
  alt: 对战伤害参数计算稿纸
- original: 以下の資料は戦闘時に与えるダメージに関するパラメーター。しかし、「プログラムしながらどんどん数字とか変えてるから、ここに書かれてる数字が正しいかは別になってくる」とのこと。
  translation: 以下资料涉及战斗时造成伤害的相关参数。不过，据称“因为是一边写程序一边不断改动数字的，所以这里写着的数字是否正确就不一定了”。
- type: heading
  level: 2
  original: 第5章：8ビットの極限芸術――加算による乗算・正弦波圧縮・40の波形魔法
  translation: 第5章：8比特的极限艺术——累加模拟乘法、正弦波极限压缩与40种叫声魔法
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s19.jpg
  caption: 增田顺一回忆初代Game Boy的Z80变体汇编开发：CPU底层连硬件乘法指令都没有，一切乘法全靠循环累加硬算！
  alt: 增田顺一回忆汇编开发
- speaker: 增田顺一
  original: また、「赤・緑時代はアセンブリ言語で書いてるので、かけ算もない言語なので、足し算を回数することでかけ算にしている」と、赤・緑の開発当初を振り返りながら懐かしむ増田さん。
  translation: 此外，增田顺一还回顾并怀念了《红／绿》开发初期的情形：“红绿时代是用汇编语言编写的，那种语言连乘法都没有，所以只能通过反复累加来实现乘法。”
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s20.jpg
  caption: 现代计算机能够轻而易举生成平滑的高精度正弦波曲线，但在1990年代的Game Boy上完全是天文数字。
  alt: 正弦波曲线图解
- original: 現在ならばサインカーブを使えばいくらでも細かくデータをとれますが……
  translation: 如今若使用正弦波曲线，数据取样可以做到要多精细有多精细，但当年完全做不到……
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s21.jpg
  caption: 在寸土寸金的初代ROM中，根本无法像现代一样连续记录曲线上的每一个离散数值点。
  alt: 当年无法存储无尽曲线数据
- original: 昔は曲線に沿って無数のデータを記録するということはできませんでした。
  translation: 以前，人们无法沿着曲线记录海量的数据。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s22.jpg
  caption: 极限优化方案一：将正半周期的波形精简提炼为仅仅8个采样点数据进行简易表达……
  alt: 正弦波正半周提炼为8个数据点
- original: そこで、データの数を減らすためにプラス部分を8つのデータで簡易に表し……
  translation: 于是，为了减少数据量，便将正向部分用8个数据点加以简化表示……
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s23.jpg
  caption: 极限优化方案二：负半周期直接将正半周数据按位取反（Invert）翻转！整条完整的正弦波曲线仅用8字节+1比特标志位就完全掌控！
  alt: 负半周镜像翻转：8字节加1比特掌控正弦波
- speaker: 增田顺一
  original: マイナス部分はプラス部分を反転させること表現したそうです。これにより、サインカーブを8バイトと1ビットでコントロールできたとのこと。
  translation: 负半部则通过将正半部直接翻转来表示。由此，仅凭8字节加1比特便能掌控整条正弦波曲线。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s24.jpg
  caption: 增田顺一亲手编写声音驱动并用彩色马克笔绘制的叫声波形示意图：通过交替组合基础波形切片合成宝可梦音效。
  alt: 增田手绘叫声波形图
- original: また、ポケモンのサウンドプログラムも、赤・緑時代は増田さんが自身で書いていたそうです。鳴き声は以下のように複数の波形を作って表現していたそうです。
  translation: 此外，宝可梦的音频驱动程序在《红／绿》时代也是由增田亲自编写的。宝可梦叫声据说就是通过合成多种波形来表现的，具体如下。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s25.jpg
  caption: 增田手指指向的是A模式波形：这一特定脉宽波形会发出短促明亮的“噗——（Pu-）”声。
  alt: A模式波形说明
- speaker: 增田顺一
  original: 指で示しているのがAパターンの波形。この波形が「プー」という音を鳴らすとします。
  translation: 手指所指的便是A模式波形。假设该波形发出的声音是“噗——”。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s27.jpg
  caption: 紧接着是指向B模式波形：这一较长波形则会发出低沉圆润的“珀——（Po-）”声。
  alt: B模式波形说明
- speaker: 增田顺一
  original: こちらはBパターンの波形で、「ポー」という音を鳴らします。
  translation: 这边展示的是B模式的波形，会发出“啵——”的叫声。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s28.jpg
  caption: 用马克笔色块标明的物理长度差异：直观展示A模式与B模式在占空比与脉冲持续时间上的微秒级微调。
  alt: 马克笔展示波形长度差异
- original: AとBの違いはマジックで書いている部分の長さの違いです。
  translation: A与B的区别在于马克笔所画部分的长度不同。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s26.jpg
  caption: “噗珀珀噗珀”的叫声拼接奇迹：初代总共仅有约40种基础波形音源，增田通过改变播放时长、包络与音高，神奇变幻出151只宝可梦的全套叫声！
  alt: 波形交替拼接合成叫声
- original: 赤・緑ではこの異なる波形を切替えて、「プポポプポ」といった具合にポケモンの鳴き声を表現したそうです。ベースとなる音は40種類ほどしか存在しないそうで、音の長さと音程を変えることで各ポケモンの進化形の鳴き声なども作ったとのこと。
  translation: 在《红／绿》中，正是通过交替切换这些不同的波形，才实现了“噗啵啵噗啵”这般宝可梦叫声的表现。据说作为基础音源的声音仅有约40种，而通过改变声音的长度与音高，连各宝可梦进化形的叫声等也得以制作出来。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s29.jpg
  caption: 增田顺一解开20年之谜：玩家总觉得某些宝可梦叫声有一种莫名亲切的家族相似感，正是因为它们共享了同一套波形基因！
  alt: 增田解开叫声相似之谜
- speaker: 增田顺一
  original: 最後は「ポケモンの鳴き声がどこか似ているように感じるのはそういった理由から」と増田さんが語り、ムービーは終了です。
  translation: 最后，增田顺一总结道：“玩家之所以会觉得某些宝可梦的叫声听起来有些相似，正是出于这样的原因。”视频至此圆满结束。
- type: image
  image: /assets/img/interviews/2017-09-05-interview-gigazine-gamefreak-sketches-masuda/s30.jpg
  caption: Game Informer 独家专访落幕：GAME FREAK用一张张泛黄的手稿，铭刻下了游戏工匠们在技术荒原上拓荒的奇迹之路。
  alt: Game Freak档案特辑落幕
interviewee: 增田顺一
source:
  title: ポケットモンスターがどうやって作られているのかが垣間見えるデザイン・アイデアスケッチなどの貴重な資料＆インタビューが聞けるムービーが公開中
  url: https://gigazine.net/news/20170905-pokemon-early-design-documents/
---
