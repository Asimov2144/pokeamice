---
article_id: masuda-126
number: 126
lang: en
date: '2008-02-29'
date_display: 02.29.2008
source: https://www.gamefreak.co.jp/blog/dir_english/2008/02/index.html
permalink_source: https://www.gamefreak.co.jp/blog/dir_english/no126
categories:
- Pokemon
status: source-extracted
---

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

{% image id="126-en-pt0229_01_s_en" %}

*This is the wave of DIALGA’s cry.

Here’s the maximized picture.

{% image id="126-en-pt0229_02_s_en" %}

Enlarged.

{% image id="126-en-pt0229_03_s_en" %}

Almost completely degitalized.

Above waves are numerated as sound data.

Then, convert them into “0″ and “1″.

Detail data are…

{% image id="126-en-pt0229_04_s_en" %}

like above picture.

Since the sound differs depend on

how we set the level of “1″, few different

converting systems were prepared.

Using the Game Boy’s click noise (beep!) to make

“0″ as a silent, and “1″ to sound.

The important part is, to recreate them with very fast speed.

Faster the better. It will give us a nice sound.

Ta-da! “pikachu” is done!

{% image id="126-multi-pt0229_05" %}

{% spacer %}

It still sounds cute…

See ya.

(c)1995,1996,1998 Nintendo/Creatures Inc./GAME FREAK inc.
