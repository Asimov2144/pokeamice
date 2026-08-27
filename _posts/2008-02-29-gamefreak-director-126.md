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
gf_entry_title: １２周年記念企画第二弾！
gf_archive: 2008-02
gf_categories:
- ポケモン
summary: 日文原文已归档；中文译稿待校对，官方英文版按原站可用性提供。
search: true
source:
  title: 増田部長のめざめるパワー 第126回
  url: https://www.gamefreak.co.jp/blog/dir/2008/02/index.html
  source_type: official_blog
gf_archive_id: masuda-126
---

<aside class="gf-director-translation-note"><strong>中文翻译待完成</strong><span>以下为保留原始换行与图片位置的日文原文。</span></aside>

## 日文原文

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
