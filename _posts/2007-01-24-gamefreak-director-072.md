---
layout: gamefreak-director
title: '[GameFreak部长专栏] 第72回'
date: '2007-01-24'
permalink: /gamefreak-director/entry-072/
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
gf_entry_no: 72
gf_entry_title: 【开发日记】2007年战斗界面的设计巧思
gf_archive: 2007-01
gf_categories:
- ものづくりについて
- ポケモン
summary: 增田顺一介绍《宝可梦DP》战斗界面的按钮布局、颜色与触控判定，解释如何让操作更直观顺手。
gf_translation_title: 【开发日记】2007年战斗界面的设计巧思
gf_translation_summary: 增田顺一介绍《宝可梦DP》战斗界面的按钮布局、颜色与触控判定，解释如何让操作更直观顺手。
search: true
source:
  title: 増田部長のめざめるパワー 第72回
  url: https://www.gamefreak.co.jp/blog/dir/2007/01/index.html
  archive_url: https://web.archive.org/web/*/https://www.gamefreak.co.jp/blog/dir/2007/01/index.html
  source_type: official_blog
gf_archive_id: masuda-072
translation_status: openai-machine-translated
proofread_confidence: null
glossary_match_count: 1
glossary_missing_targets:
- 牡丹
entities:
  people:
    - "增田顺一"
  organizations:
    - "Game Freak"

---

<aside class="gf-director-translation-note"><strong>中文译稿已完成校对</strong><span>译文按原文段落、换行和图片位置整理；术语表检查结果记录在来源信息中。</span></aside>

## 中文译文

今天还是DP相关的话题。

战斗时显示在下画面上的“战斗”按钮。

那个按钮，意外地很大吧。

其实是有原因的。

那是因为它和接下来出现的4个招式有关。

按下“战斗”之后，即使不移动手指，

也可以在原来的位置再次按下按钮来选择招式。

也就是说，即使不移动手指，也能连续触摸操作。

我们想要采用的就是这样的设计。

另外，为了让人更容易理解，我们还在“战斗”按钮的后面加上了4个招式的影子。

顺带一提……

即使按下招式影子的部分，也会被视为选择了“战斗”。

看起来的位置和实际的判定范围是不一样的。

这在游戏制作中是经常使用的技巧。

就是尽可能让玩家不必移动手指。

不管是哪一个下画面，我们在设计时都对这一点进行了细致的考虑。

另外，之所以改变颜色，

也是为了让玩家即使一边看着上画面，视野里隐约看到那个红色按钮时，

也能认出那就是“战斗”。

这样一来，即使不用把视线移到下画面，

即使不仔细看，也可以进行操作。

招式也按照属性分别采用了不同的颜色，让人更容易理解。

改变这种颜色看起来似乎是件很简单的事，

但仅仅这样，就能利用符号性，让信息变得更易懂、更明确。

即使是不识字的小孩子，也能玩这个游戏。

从这个意义上来说，颜色也是非常重要的。

那么，再见。


<details class="gf-director-language"><summary>查看日文原文</summary>

今日もDPネタです。

バトルで下画面に表示される「たたかう」というボタン。

意外と大きいですよね、あれ。

それには訳があるんです。

それは、その次に出てくる技４つとの関係性。

「たたかう」を押したあと、指を動かさなくても

そのままの位置でもう一度ボタンを押せば技を選べる。

要するに指を移動させなくても連続タッチが出来る。

そういう設計にしたかったんです。

それで、更に分かりやすいように「たたかう」の後ろに技４つの影もつけてあるんです。

ちなみに、、、

その技の影の部分を押しても「たたかう」を選んだとみなしています。

見た目と実際の判定が違うのです。

ゲーム制作では良くやるテクニックですけどね。

出来るだけ指を動かさなくても良いように。

どの下画面でもそのことを細かく注意して設計しています。

また、色を変えているのも、

上画面を見ながらでも、なんとなく視野にある赤いボタン。

それが「たたかう」だと認識できるようにです。

こうすることで、下画面に目線を合わせなくても、

きっちりと見なくても操作できます。

技もタイプ別に色分けしてあって分かりやすくしています。

こういう色を変える事って単純なように見えますが、

たったそれだけで、記号性があるので分かりやすく明確になる。

文字を読めない小さな子供でも遊べるようになる。

そういう意味でも色はとても重要です。

では。


</details>

<details class="gf-director-language"><summary>查看官方英文版</summary>

I’ll write a bit more about Pokemon Diamond

and Pearl today, too.

When in a battle, the lower screen shows

the “FIGHT” button.

It’s a big button, isn’t it?

There’s a reason.

The button is big because of its relation

with the following four moves.

When you press the ‘FIGHT’ button,

you don’t have to move your finger to select

a move, only press the button once more.

In short, I’d like to enable continuous

touches without moving the finger.

I wanted to design it in such a way.

So, to make it even clearer, behind the

‘FIGHT’ button we added shadows of the four

moves.

Speaking of which…

Even when you touch on the shadow part of

the moves, it means you selected ‘FIGHT.’

How it looks and how it is actually judged

by the game are different.

This is a technique often employed in game development.

In order for players to keep the finger

in the same place as long as possible.

With regard to the lower screen, every scene

is carefully designed with that in mind.

Also, the color is different because,

even when you are looking at the top screen,

that red button is vaguely in sight, and

I want people to remember that it means ‘FIGHT.’

This way, you can keep on playing without

lowering your eyes to the lower screen,

without focusing your eyes.

The moves are labeled with different colors

according to their types so that you

can easily distinguish them.

Using different colors might seem a simple

thing, but it makes a huge difference in

understanding and distinguishing each move,

because colors are symbolic.

Also, little kids with no knowledge of

alphabets can play it.

In that sense colors are very important.

See ya.


</details>
