---
layout: gamefreak-director
title: '[GameFreak部长专栏] 第126回'
date: '2008-02-29'
permalink: /gamefreak-director/entry-126/
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
gf_entry_no: 126
gf_entry_title: 【开发日记】宝可梦皮卡丘叫声诞生记
gf_archive: 2008-02
gf_categories:
- ポケモン
summary: 增田回顾《宝可梦皮卡丘版》中皮卡丘叫声的制作过程，以及用一比特数据实现声音播放的巧妙方法。
gf_translation_title: 【开发日记】宝可梦皮卡丘叫声诞生记
gf_translation_summary: 增田回顾《宝可梦皮卡丘版》中皮卡丘叫声的制作过程，以及用一比特数据实现声音播放的巧妙方法。
search: true
source:
  title: 増田部長のめざめるパワー 第126回
  url: https://www.gamefreak.co.jp/blog/dir/2008/02/index.html
  archive_url: https://web.archive.org/web/*/https://www.gamefreak.co.jp/blog/dir/2008/02/index.html
  source_type: official_blog
gf_archive_id: masuda-126
translation_status: openai-machine-translated
proofread_confidence: null
glossary_match_count: 4
glossary_missing_targets: []
entities:
  people:
    - "增田顺一"
  works:
    - "宝可梦 皮卡丘版"
  organizations:
    - "任天堂"
    - "Creatures"
    - "Game Freak"

---

<aside class="gf-director-translation-note"><strong>中文译稿已完成校对</strong><span>译文按原文段落、换行和图片位置整理；术语表检查结果记录在来源信息中。</span></aside>

## 中文译文

12周年纪念企划第二弹！

“宝可梦 皮卡丘版”

像动画里的皮卡丘一样，皮卡丘会叫出“皮卡丘”。

Game Boy没有高性能的采样功能，

所以无论如何，都得想办法让它叫出“皮卡丘”。

于是，当时还是程序员的我，

制作了一个把声音转换成1比特数据的转换器，

并编写了播放这些数据的程序。

原理是这样……

首先，用采样器之类的设备把声音数字化。

<img src="/assets/images/gamefreak-director/archive/126/ja/pt0229_01_s.jpg" alt="" loading="lazy">

※这个波形是帝牙卢卡的叫声。波形大概会呈现出这种感觉。

放大后，是这个样子。

<img src="/assets/images/gamefreak-director/archive/126/ja/pt0229_02_s.gif" alt="" loading="lazy">

再放大一些，

<img src="/assets/images/gamefreak-director/archive/126/ja/pt0229_03_s.gif" alt="" loading="lazy">

就几乎变成数字状态了。波形已经作为音量数据被数值化。

接着，用转换器把它转换成0和1。

数据大概是这样……

<img src="/assets/images/gamefreak-director/archive/126/ja/pt0229_04_s.gif" alt="" loading="lazy">

就是这种感觉。（图片中红色的0和1）

把哪个电平设为1也会影响声音，所以我在转换器里准备了几种转换方式。

然后利用 Game Boy 的点击噪声（啪嗞！）来高速执行这样的操作：0不发声，1发声。

高速执行这一点才是关键。

越快，声音就越好听。

“皮卡丘”就这样完成了。

<img src="/assets/images/gamefreak-director/archive/126/multi/pt0229_05.jpg" alt="" loading="lazy">

<p class="gf-director-spacer"></p>

现在听起来也还是很可爱……

那么，下次见。

(c)1995,1996,1998 Nintendo/Creatures Inc./GAME FREAK inc.


<details class="gf-director-language"><summary>查看日文原文</summary>

１２周年記念企画第二弾！

「ポケットモンスター　ピカチュウバージョン」

アニメのピカチュウのように、ピカチュウが”ピカチュウ”と鳴きます。

ゲームボーイでは高性能なサンプリングの機能はありませんから、

どうにかして、”ピカチュウ”と鳴かせなければなりません。

そこで、当時プログラマでもあったマスダは、

音声を１ビットデータにするコンバータを作成し、

それを再生するプログラムを組みました。

仕組みとしては、、

まず、サンプラーなどの機材で音をデジタル化します。

<img src="/assets/images/gamefreak-director/archive/126/ja/pt0229_01_s.jpg" alt="" loading="lazy">

※この波形はディアルガの鳴き声です。波形ではこんな感じになります。

拡大すると、こんな感じ。

<img src="/assets/images/gamefreak-director/archive/126/ja/pt0229_02_s.gif" alt="" loading="lazy">

さらに拡大すると、

<img src="/assets/images/gamefreak-director/archive/126/ja/pt0229_03_s.gif" alt="" loading="lazy">

ほぼ、デジタルな状態に。波形は音量データとして数値化されています。

これをコンバーターで、０と１に。

データとしては、、、

<img src="/assets/images/gamefreak-director/archive/126/ja/pt0229_04_s.gif" alt="" loading="lazy">

こんな感じに。（画像の赤い０と１）

どのレベルを１にするかでも音に影響するので、コンバーターには変換方式をいくつか用意しておきます。

この０と１をゲームボーイのクリックノイズ（ブチツ！）といった音で、

０は鳴らさない。１は鳴らす。というのを高速に行います。

この高速に行う、というのがポイント。

早いほど良い音になります。

”ピカチュウ”の完成です。

<img src="/assets/images/gamefreak-director/archive/126/multi/pt0229_05.jpg" alt="" loading="lazy">

<p class="gf-director-spacer"></p>

いま聞いても可愛い。。。

では。

(c)1995,1996,1998 Nintendo/Creatures Inc./GAME FREAK inc.


</details>

<details class="gf-director-language"><summary>查看官方英文版</summary>

Pokemon 12th anniversary column PART 2!

“Pokemon YELLOW”

In this game, Pikachu cries “pikachu!”, like TV animation.

Of course, there is no such high quality sampling function

on the Game Boy hardware.

Therefore, we must think different way to recreate

the cry of “pikachu!”.

At that time, I was a programmer and I came up with

following idea to solve this problem.

Program the converter to make the sound into

one bit data, and recreating the sound.

The structure is as follows.

First of all, make the sound degitalize using

the equipment, suich as a sampler.

<img src="/assets/images/gamefreak-director/archive/126/en/pt0229_01_s_en.jpg" alt="" loading="lazy">

*This is the wave of DIALGA’s cry.

Here’s the maximized picture.

<img src="/assets/images/gamefreak-director/archive/126/en/pt0229_02_s_en.gif" alt="" loading="lazy">

Enlarged.

<img src="/assets/images/gamefreak-director/archive/126/en/pt0229_03_s_en.gif" alt="" loading="lazy">

Almost completely degitalized.

Above waves are numerated as sound data.

Then, convert them into “0″ and “1″.

Detail data are…

<img src="/assets/images/gamefreak-director/archive/126/en/pt0229_04_s_en.gif" alt="" loading="lazy">

like above picture.

Since the sound differs depend on

how we set the level of “1″, few different

converting systems were prepared.

Using the Game Boy’s click noise (beep!) to make

“0″ as a silent, and “1″ to sound.

The important part is, to recreate them with very fast speed.

Faster the better. It will give us a nice sound.

Ta-da! “pikachu” is done!

<img src="/assets/images/gamefreak-director/archive/126/multi/pt0229_05.jpg" alt="" loading="lazy">

<p class="gf-director-spacer"></p>

It still sounds cute…

See ya.

(c)1995,1996,1998 Nintendo/Creatures Inc./GAME FREAK inc.


</details>
