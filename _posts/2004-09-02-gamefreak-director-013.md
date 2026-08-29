---
layout: gamefreak-director
title: '[GameFreak部长专栏] 第13回'
date: '2004-09-02'
permalink: /gamefreak-director/entry-013/
categories:
- 官方博客
- Game Freak
- 翻译资料
tags:
- Game Freak
- 增田顺一
- 宝可梦
- 官方博客
archive_type: gamefreak_director_column
gf_entry_no: 13
gf_entry_title: 【开发日记】2004年 UNIX 故障往事
gf_archive: 2004-09
gf_categories:
- 日記
summary: 增田回忆开发《宝可梦 红·绿》时使用 UNIX 工作站的经历，以及机器频繁死机、备份不易带来的惊险日常。
gf_translation_title: 【开发日记】2004年 UNIX 故障往事
gf_translation_summary: 增田回忆开发《宝可梦 红·绿》时使用 UNIX 工作站的经历，以及机器频繁死机、备份不易带来的惊险日常。
search: true
source:
  title: 増田部長のめざめるパワー 第13回
  url: https://www.gamefreak.co.jp/blog/dir/2004/09/index.html
  archive_url: https://web.archive.org/web/*/https://www.gamefreak.co.jp/blog/dir/2004/09/index.html
  source_type: official_blog
gf_archive_id: masuda-013
translation_status: openai-machine-translated
proofread_confidence: null
glossary_match_count: 2
glossary_missing_targets: []
entities:
  people:
    - "增田顺一"
  works:
    - "宝可梦 红·绿"
  organizations:
    - "Game Freak"
    - "Allied Telesis"
    - "DEC"
    - "Nifty"

---

<aside class="gf-director-translation-note"><strong>中文译稿已完成校对</strong><span>译文按原文段落、换行和图片位置整理；术语表检查结果记录在来源信息中。</span></aside>

## 中文译文

这次来讲点内容比较深的往事吧。

开始开发《宝可梦 红·绿》的时候，GAME FREAK 也是下定决心，

买了一台名为 SUN SPARCstation 1 的 UNIX 机器。

贵得让人觉得：“居然真买得起啊。”

然后，我们还把 Allied Telesis 公司的板卡装到 PC9801Xa、EPSON 等电脑上，

搭建了局域网环境。当时用的是 10BASE-T。

于是，大家从各台电脑登录上去，四五个人一起工作。不过……

真的特别慢。

因为我在专科学校读书时，曾用 DEC 的中型计算机学习 CG 和 C 语言，

所以不知不觉间，就成了一个最喜欢 UNIX 的少年。

也正因为如此，我觉得 SUN 非常好用，可是……

它偶尔会系统崩溃……让人目瞪口呆。

有时还会就这样彻底启动不了……令人茫然。

每次我都会像祈祷一样使劲给自己打气，大喊：“快启动啊——！！！拜托了！”

当时，我们会把备份存到一种叫作流式磁带的东西上，体积大得像 VHS 录像带那么大，

但因为花的时间很长，所以也没法经常备份。

最糟糕的时候，所有人一个多月的工作都有可能化为乌有。

所以，为了让它启动，我真是拼了命，把能想到的办法全都试了一遍。

读英文说明书，没日没夜地啃那些厚得吓人的书，

我甚至还去 Nifty 的留言板发过求助帖。

机器迟迟启动不了的时候（比如启动到 BOOT 中途突然 REBOOT），

我真的满脑子想的都是这件事，

甚至还梦见过“机器启动起来了！”。

不过，现在回想起来，我觉得这确实是一次非常好的学习经历。

我是个 vi 狂热者，增田。


<details class="gf-director-language"><summary>查看日文原文</summary>

今回はちょっと濃い昔話でも。

ポケモン赤緑の開発を始めたころ、ゲームフリークでは思い切って、

ＳＵＮ　ＳＰＡＲＣステーション１というＵＮＩＸマシンを購入しました。

よく買ったなぁ。と思うぐらい高価な物でした。

そして、アライドテレシス社のボードをＰＣ９８０１ＸａやＥＰＳＯＮなどに載せて、

ＬＡＮ環境を構築していました。当時１０ＢＡＳＥ?Ｔでした。

で、各パソコンからログインして４、５人で作業してました。が、、

すごーく遅かったです。

専門学校時代にＣＧとＣ言語をＤＥＣの中型コンピュータを使って勉強していたので、

いつの間にかＵＮＩＸ大好き少年になってました。

そんな訳で、ＳＵＮはすごく使いやすかったんですが、、、

たまにシステムダウンして、、、唖然。

そのまま立ち上がらなくなることがあって、、、呆然。

毎回、祈るように気合いを入れて「立ち上がれー！！！たのむ！」と叫んでました。

当時、ＶＨＳテープのようなでかいストリーマテープというものにバックアップはしてたんですが、

時間が掛かるので、そんなにこまめには録ってなかったんですよね。

最悪１ヶ月以上の全員の作業が水の泡となってしまう危険性があったんです。

もう、必死で立ち上げるために、ありとあらゆる手を尽くしました。

英語のマニュアルを読んだり、すごい分厚い本を読みまくったり、

ニフティの掲示板にヘルプを出したこともありました。

マシンが立ち上がらない（ＢＯＯＴの途中でＲＥＢＯＯＴとかね）状況が続いたときは、

ほんとそのことばかり考えていて、

「マシンが立ち上がった！」という夢を見たこともあります。

まあ、今となっては非常に良い勉強になったと思ってます。

ｖｉマニアの増田でした。


</details>

<details class="gf-director-language"><summary>查看官方英文版</summary>

Today I’ll write about some geeky stories of old days.

When we started developing for Pokemon Red and Blue,

we at Game Freak took a plunge and bought a UNIX machine

called SUN SPARCstation 1.

Even now I think it was such a bold step because

it was very very expensive.

We also installed LAN boards from Allied Telesis

in our PC9801Xa and Epson computers in order to set up a LAN environment.

Four or five of us logged into the network from different

computers so that we could work together, but it was so slow.

When I was in technical school I studied CG and C language

using a medium-sized computer by DEC, and before I knew it

I was really into UNIX.

For someone like me, therefore, SUN was such an easy-to-use

machine…

But it sometimes crashed.ﾂ? “What on earth is going on?”

Then there were times it never rebooted… “Oh my goodness!”

Whenever this happened I used to yell at the computer

“Start up!!! Please!”ﾂ? It was almost like a prayer.

These days we used streamer tapes that were as large

as VHS cassettes for backups.

But they took so long that we didn’t back up as

often as we should have.

So when computers crashed there was a possibility that

more than a month’s worth of all of our contributions

might go down the drain.

We tried every possible means to rescue the computers.

We read manuals in English and impossibly thick books on computers.

We also asked for help on Nifty Serve’s bulletin board.

When a machine didn’t start up for a continuos period

(like reboots during startup),

I was so completely preoccupied with the problem

that I even had a dream of my machine starting up!

Looking back it was a very good learning experience.

From Masuda, a vi mania.


</details>
