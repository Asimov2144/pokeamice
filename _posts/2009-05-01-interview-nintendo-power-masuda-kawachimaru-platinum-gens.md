---
layout: parallel-translation
title: '[访谈翻译] 《任天堂力量》(Nintendo Power) 独家专访：增田顺一与河内丸武史复盘前四世代演化与《宝可梦 白金》破灭的世界（从芯片音效程序员到全系列总监的破局之道）'
original_title: 'Nintendo Power Issue 240/241: Junichi Masuda and Takeshi Kawachimaru on Developing Gens 1-4 & Pokémon Platinum'
date: '2009-05-01'
era: 2006–2010 · NDS / 触控与 Wi-Fi 联机时代
era_skin: '2007'
publication: 《Nintendo Power》第240/241期 (2009年4/5月号)
source_kind: magazine
author: Nintendo Power 独家特写 / 存档整理：Dr. Lava (Lava Cut Content)
translator: Poke Amice Studio
interviewee: Dr. Lava, Nintendo Power, 增田顺一, 河内丸武史
toc: true
toc_sticky: true
parallel_view: translation
categories:
- 访谈翻译
- 翻译
- 访谈整理
tags:
- Pokemon
- 访谈
- 开发者访谈
- 增田顺一
- 河内丸武史
- 第四世代
- 宝可梦 白金
- 钻石珍珠
- 反转世界
- Nintendo Power
archive_type: interview_translation
source:
  title: 'Interview: Masuda on Developing Gens 1-4'
  url: https://lavacutcontent.com/masuda-interview-pokemon-platinum/
  language: en
  source_type: magazine_interview
original_link: https://lavacutcontent.com/masuda-interview-pokemon-platinum/
summary: 2009年春《Nintendo Power》对 Game Freak 核心领导增田顺一与总监河内丸武史的独家深度特写。增田顺一详细回顾了自己从初代《红·绿》自主编写‘Sound Driver’音频底层程序，到《水晶版》《红宝石·蓝宝石》及《钻石·珍珠》担任总监的创作演变；深度揭秘《白金》反转世界（破灭的世界）打破欧几里得几何与重力法则的开发哲学；披露全球贸易中心（GTS）连接全球训练家的惊喜、对战开拓区新挑战、以及为寻找‘下一个皮卡丘’而精心企划皮丘的幕后轶事。
entities:
  people:
  - 增田顺一
  - 河内丸武史
  - 杉森建
  - 田尻智
  games:
  - 宝可梦 白金
  - 宝可梦 钻石·珍珠
  - 宝可梦 红·绿
  - 宝可梦 金·银
  - 宝可梦 水晶版
  - 宝可梦 红宝石·蓝宝石
parallel_items:
- type: heading
  level: 2
  original: 'Part 1: From Sound Driver and Chiptunes to Game Director'
  translation: 第1章：从底层声音驱动、电音与斯特拉文斯基，到执掌全局的总监之路
- speaker: ''
  original: The following interview was published in the April 2009 issue of Nintendo Power magazine, arriving in subscribers’ mailboxes a few weeks before Pokemon Platinum released in the United States. The interviewees are Junichi Masuda, Diamond & Pearl’s director; and Takeshi Kawachimaru, Platinum’s director. Platinum was the first Pokemon game Kawachimaru ever directed, but it was also his last — he served smaller roles in future generations, mostly dealing with online features. So perhaps Game Freak wasn’t satisfied with his performance on Platinum.
  translation: 以下访谈刊载于《任天堂力量》2009年4月号，在《宝可梦 白金》于美国发售前数周寄达订户手中。受访者为《钻石／珍珠》的总监增田顺一，以及《白金》的总监河内丸武史。《白金》是河内丸首次担任总监的宝可梦游戏，却也是他最后一次——在后续世代中，他只担任次要职务，主要负责线上功能。或许Game Freak对他《白金》的表现并不满意。
  note: 编者按/背景注释
- speaker: ''
  original: The purpose of this interview discussing Platinum’s development, but in the process, Masuda and Kawachimaru ended up discussing the franchise as a whole. Highlights include some glimpses behind-the-scenes, an explanation of the series’ musical inspirations, and how the Distortion World was conceptualized. They also provide some candid replies about the development process… maybe even a little too candid in some instances. For example, Masuda makes it clear his directorial focus is attracting new fans, even if it’s at the expense of satisfying the established fanbase.
  translation: 本次访谈旨在讨论《白金》的开发过程，但在此过程中，增田与河内丸最终谈到了整个系列。亮点包括一些幕后花絮、系列音乐灵感的阐释，以及毁坏的世界是如何构思的。他们还对开发过程给出了一些坦诚的回答……有时甚至过于坦诚。例如，增田明确表示，他的执导重点是吸引新粉丝，即使以牺牲老粉丝的满意度为代价。
  note: ''
- speaker: ''
  original: I’ve added some of my own commentary to provide additional information and context — it’ll be clearly labeled so it’s clear who’s saying what. Okay, without further adieu, here’s the interview.
  translation: 我加入了一些自己的评论，以提供额外的信息和背景——这些评论会明确标注，以便清楚谁在说什么。好了，闲话少说，以下是访谈内容。
  note: ''
- speaker: Nintendo Power
  original: How did you get your start working on video games?
  translation: 你们是如何起步进入电子游戏行业的？
  note: ''
- speaker: 增田顺一
  original: Ever since the time when games were first in arcades, I was interested in video games and their gameplay mechanism. By the time I was in high school, I went to the arcades on a daily basis. At one point I took an ordinary corporate job, but then I was approached by [Pokemon creator Satoshi] Tajiri to create a game called Mendel Palace and became a game music composer. I was 21 years old then. Because I had created games on PCs since high school and was able to understand the joy of game making, I told him, ‘I’ll gladly be taken into your care’ (laughs) and that’s when my hobby turned into a career.
  translation: 自从游戏最初出现在街机厅时起，我就对电子游戏及其玩法机制产生了兴趣。到了高中时，我几乎每天都去街机厅。我曾一度从事普通公司职员的工作，但后来[宝可梦之父]田尻智找到我，让我参与制作一款名为《孟德尔宫殿》的游戏，我便成为了一名游戏音乐作曲家。那时我21岁。因为从高中起我就在个人电脑上制作游戏，能够体会到制作游戏的乐趣，所以我告诉他：‘我很乐意承蒙关照’（笑），从那时起，我的爱好变成了职业。
  note: ''
- speaker: 河内丸武史
  original: My background is similar to Masuda’s. I’ve always loved games since I was little and I also started to go to arcades in high school. One big difference from Masuda is that he grew up in an inner-city area of Yokohama, but I grew up in the country side of Kyushu (including Fukuoka and Nagasaki prefectures). I never had a chance to meet any game developers, and I was about ready to give up and took another job that didn’t relate to game development. At that time, there was a convenient online message board called “PC Communication (PC Tsu-shin)”, where I got an opportunity to meet game developers. I saw a posting for a position, so I decided to apply for it as a last chance. I quit the job and moved out to Tokyo and eventually came to work for GAME FREAK, which wasn’t called GAME FREAK at the time. I was 24 years old.
  translation: 我的背景与增田相似。我从小就热爱游戏，高中时也开始去街机厅。与增田的一个重大区别是，他在横滨的市中心长大，而我则在九州的乡下长大（包括福冈县和长崎县）。我从未有机会结识任何游戏开发者，几乎准备放弃，转而从事了一份与游戏开发无关的工作。那时，有一个便捷的在线留言板，叫做“PC通信”，我在那里有机会结识了游戏开发者。我看到了一则招聘启事，于是决定作为最后一次机会去应聘。我辞掉了工作，搬到东京，最终来到了Game Freak工作——当时它还并不叫Game Freak。那时我24岁。
  note: ''
- speaker: ''
  original: 'Dr Lava’s notes: Action-puzzler Mendel Palace was the first game Game Freak ever produced. It released under the title “Quinty” on the Famicom in 1989, then was localized as “Mendel Palace” when it released stateside on the NES one year later. At the time, Game Freak’s core developers were Satoshi Tajiri, the company’s founder; Ken Sugimori, who later became the Pokemon series’ art director; and Junichi Masuda, who composed and programmed for Gen 1, then became the series’ director.'
  translation: Dr. Lava 注：动作解谜游戏《孟德尔宫殿》是Game Freak制作的第一款游戏。它于1989年以《Quinty》之名在红白机（FC）上发售，一年后以《孟德尔宫殿》之名在北美NES上发售。当时，Game Freak的核心开发者包括公司创始人田尻智、后来成为宝可梦系列艺术总监的杉森建，以及增田顺一——他曾为第一世代作曲和编程，后来成为该系列的总监。
  note: 编者按/背景注释
- speaker: ''
  original: Masuda grew up in Yokohama in the Kanto region, but his parents were originally from Kyushu, the real-world inspirations for the Pokemon games’ Kanto and Hoenn regions — which is no coincidence. Likewise, Tajiri grew up in the rural town of Machida, which served as inspiration for Pallet Town.
  translation: 增田在关都地区的横滨长大，但他的父母来自九州——这正是宝可梦游戏中关都和丰缘地区的现实灵感来源，这并非巧合。同样，田尻在町田的乡村小镇长大，那里是真新镇的灵感来源。
  note: 编者按/背景注释
- speaker: Nintendo Power
  original: How do people react when they learn that you work on Pokemon games?
  translation: 当人们得知你们参与制作宝可梦游戏时，他们作何反应？
  note: ''
- speaker: 增田顺一
  original: Kids in elementary school think it’s awesome. But middle school and high school students get embarrassed and run away right after shaking my hand (laughs). People close to me tend to say things like ‘Sounds like a lot of work.’ They say they have no idea what I am doing, but that I seem busy.
  translation: 小学生们觉得这很酷。但中学生和高中生会感到难为情，握完手就立刻跑开（笑）。亲近我的人往往会说‘听起来工作很辛苦’之类的话。他们表示不知道我在做什么，但觉得我似乎很忙。
  note: ''
- speaker: 河内丸武史
  original: I’m always surrounded by gamers, so everyone thinks it’s great. They are usually shocked at first because they think Pokemon is kids’ stuff and then they’re impressed afterwards when they realize how successful it is.
  translation: 我身边总是围绕着游戏玩家，所以大家都觉得这很棒。他们起初通常会感到震惊，因为他们认为宝可梦是小孩玩的东西，但之后当他们意识到它有多成功时，又会留下深刻印象。
  note: ''
- speaker: Nintendo Power
  original: How did you come to work on the original Pokemon games, and what was your first reaction when you learned of the Pokemon concepts?
  translation: 你们是如何参与到最初的宝可梦游戏开发中的？当你们得知宝可梦的概念时，第一反应是什么？
  note: ''
- speaker: 增田顺一
  original: I developed a program we called ‘Sound Driver’ in order to play music and sound in the games, and also oversaw all the Pokemon voices and other sound effects. Soon after, I started to program the actual game as well. As for the concept, Tajiri asked ‘What if you could exchange creatures?’, and it sounded quite exciting. Back in the day, there were only games where you could battle against each other, so the concept of ‘trading’ was intriguing. At the time, trading was done by a link cable. The idea of transferring a creature through the cable cord was exciting, and it’s actually depicted in the game as well.
  translation: 我开发了一个我们称之为‘声音驱动’的程序，用于在游戏中播放音乐和声音，并负责所有宝可梦的叫声和其他音效。不久之后，我也开始编写实际游戏程序。至于概念，田尻先生问‘如果你们能交换生物会怎样？’，这听起来非常令人兴奋。在那个年代，只有玩家之间对战的游戏，所以‘交换’的概念引人入胜。当时，交换是通过连接线完成的。通过线缆传递生物的想法令人兴奋，这在游戏中也有体现。
  note: 田尻智提出了交换宝可梦的核心概念，这一机制成为系列特色。
- speaker: Nintendo Power
  original: How did you approach creating music for the series? Did you find that composing for handheld systems was limiting or inspiring?
  translation: 你们是如何着手为系列创作音乐的？你们是否觉得为掌上游戏机作曲既有限制又激发灵感？
  note: ''
- speaker: 增田顺一
  original: For the Kanto region in the original Red & Green, I wanted to leave the Asian feel to it. I’m a Kanto local. I also had classical music in mind. I felt the music should be unique but not too ‘orchestra,’ not too ‘pop,’ not too ‘Asian.’ I wanted to create a new world by incorporating all the elements of all types of music. As far as portable game devices went back then, you could only use three music scales and a sound effect. It was much more challenging — yet gratifying — to compose music. It was also much quicker to come up with music with these limitations (laughs). Now there are 10 types of music scales! When I tried to express the melody I wanted, the music [for a portable game system] couldn’t be composed on an instrument like a piano. I played around with the program in order to add a musical effect to the sound effects — for instance, by removing ‘static,’ I could create a unique sound. For example, I would create a shattering sound and make it sound interesting by repeating
    it several times, without separating all the instruments. I remembered to always come up with music that’s unique to video games in general. For this reason, there are many video game scores that can’t be written as traditional music notes.
  translation: 对于最初《红／绿》中的关都地区，我想保留亚洲风情。我是关都本地人。我也有古典音乐的考量。我觉得音乐应该独特，但不要太‘管弦乐’，不要太‘流行’，也不要太‘亚洲’。我想通过融合所有类型音乐的元素来创造一个全新的世界。就当时的便携式游戏设备而言，你只能使用三个音阶和一个音效。作曲更具挑战性，但也更有满足感。在这些限制下，构思音乐也更快（笑）。现在有十种音阶了！当我试图表达我想要的旋律时，[便携式游戏机的]音乐无法用像钢琴这样的乐器来创作。我摆弄程序，以便为音效添加音乐效果——例如，通过去除‘静电’，我可以创造出独特的声音。比如，我会创造一种碎裂声，并通过重复几次使其听起来有趣，而不分离所有乐器。我始终记得要创作出总体上独一无二的电子游戏音乐。因此，许多电子游戏配乐无法用传统音符来谱写。
  note: 增田顺一提到早期硬件限制（三个音阶）反而激发创造力，体现了Game Boy时代的音乐创作特点。
- speaker: Nintendo Power
  original: What kinds of music do you enjoy listening to or performing, and have any music styles influenced your work on Pokemon?
  translation: 你们喜欢听或演奏哪种类型的音乐？是否有某种音乐风格影响了你们在宝可梦上的工作？
  note: ''
- speaker: 增田顺一
  original: I usually listen to alternative and techno. I’ve been listening to import music — mostly from Europe — since middle school, so I hardly listen to Japanese music. I’m a techno lover at heart. I’m into German ‘drum n bass’ types.
  translation: 我通常听另类音乐和电子乐。从中学开始，我就一直在听进口音乐——大部分来自欧洲——所以我几乎不听日本音乐。我骨子里是个电子乐爱好者。我很喜欢德国的“鼓打贝斯”风格。
  note: ''
- speaker: 河内丸武史
  original: When I go over to Masuda’s desk, I sometimes can hear ‘ntsk ntsk ntsk…’ [music thumping] from his earphones (laughs). In the office, we share our iTunes music and many songs that Masuda uploads are that kind of music.
  translation: 当我走到增田的办公桌前时，有时能听到他的耳机里传出“咚咚咚……”的音乐声（笑）。在办公室里，我们会共享 iTunes 音乐，而增田上传的许多歌曲都是那种类型的音乐。
  note: ''
- type: heading
  level: 2
  original: 'Part 2: Diamond & Pearl''s ''Ultimate'' Theme and the Worldwide GTS Miracle'
  translation: 第2章：《钻石·珍珠》的‘终极’命题与全球贸易中心（GTS）的世界奇迹
- speaker: 增田顺一
  original: And I don’t really play any instruments. I played trombone in high school, but I gave up on piano. It was impossible (laughs). As for the style of music that inspires me, people have told me — and I think they’re right — that Stravinsky is my favorite classical music composer, and then Shostakovich, Hoist, and Ravel. I think some of the sound from these composers can be heard in my music, too. You might especially be able to hear Stravinsky and Hoist in the battle scenes. Adding beats or crashing sounds like Stravinsky and Hoist is difficult for video games, though you can still hear their influence in the rhythm.
  translation: 而且我其实并不会演奏什么乐器。高中时我吹过长号，但钢琴我放弃了。那太难了（笑）。至于启发我的音乐风格，有人告诉我——我也觉得他们说得对——斯特拉文斯基是我最喜欢的古典音乐作曲家，然后是肖斯塔科维奇、霍尔斯特和拉威尔。我想我的音乐里也能听到这些作曲家的影子。你或许尤其能在战斗场景中听到斯特拉文斯基和霍尔斯特的影响。不过，要在电子游戏中加入像斯特拉文斯基和霍尔斯特那样的节拍或撞击声是很困难的，但你仍然能在节奏中感受到他们的影响。
  note: ''
- speaker: ''
  original: 'Dr Lava’s notes: Igor Stravinsky was a Russian composer most famous for “The Rite of Spring,” a piece of music so unnerving it caused a riot the first time it was performed, although details of the riot have been in dispute ever since. If you’re fan of classical music, I encourage you to listen to Stravinsky’s compositions — like Masuda said, you can hear its influence on Pokemon’s battle themes. If it wasn’t for Masuda’s love of Stravinsky — who performed and eventually died in New York — Gen 5’s Unova region might not have been based on New York… which would’ve made Unova and its Pokemon completely different. But that’s too long a story to cover here — but if you wanna hear it, check out this video I wrote about the history of Gen 5.'
  translation: Dr. Lava 的注释：伊戈尔·斯特拉文斯基是一位俄罗斯作曲家，最著名的作品是《春之祭》，这首曲子首次演出时因其令人不安的氛围引发了骚乱，尽管此后关于骚乱的细节一直存在争议。如果你是古典音乐爱好者，我鼓励你去听听斯特拉文斯基的作品——正如增田所说，你能在宝可梦的战斗主题曲中听到它的影响。如果不是因为增田对斯特拉文斯基的热爱——斯特拉文斯基曾在纽约演出并最终在纽约去世——第五世代的合众地区可能就不会以纽约为原型……那样的话，合众地区和它的宝可梦将会完全不同。但这个故事太长，这里就不展开了——如果你想听，可以看看我写的关于第五世代历史的视频。
  note: 编者按/背景注释
- speaker: Nintendo Power
  original: Mr Masuda, what was it like to move from music composer to director of Pokemon Diamond & Pokemon Pearl?
  translation: 增田先生，从音乐作曲家转变为《宝可梦 钻石》和《宝可梦 珍珠》的导演，您有什么感受？
  note: ''
- speaker: 增田顺一
  original: I became sub-director for Gold & Silver versions, and then director from Crystal version on. My perception completely changed, and I started to think about how to make the game more fun. In addition to that, I started to make more decisions. I started to have more conviction in what I expressed. I’m much more affirmative with what I like now, even though I expressed my opinions when I was only in charge of music (laughs). As far as the development goes, I think about the storyline, music, and the rest individually. I think I’m using different parts of my brain for each element.
  translation: 我在《金／银》版本中担任副导演，从《水晶》版本开始担任导演。我的观念完全改变了，我开始思考如何让游戏变得更有趣。除此之外，我开始做出更多决策。我对自己表达的内容更加坚定。现在我对自己的喜好更加肯定，尽管在我只负责音乐时我也会表达自己的意见（笑）。就开发而言，我会分别思考故事情节、音乐和其他部分。我想我在为每个元素使用大脑的不同部分。
  note: ''
- speaker: Nintendo Power
  original: What do you feel is the main theme, or ‘spirit,’ of the Pokemon series, and how did you embody this in both your music compositions and as a director?
  translation: 您认为宝可梦系列的主要主题或“精神”是什么？您如何在音乐创作和作为导演时体现这一点？
  note: ''
- speaker: 增田顺一
  original: Overall, I wanted to depict an ideal world, which was peaceful with no environmental issues or racism. The relationship between human beings and Pokemon characters is much closer than the owner-pet relationship, which is what I envision to be the ideal relationship. I want everyone to feel something when interacting with this world. In Japan, people sometimes don’t give up their seats for the elderly on a train. I wanted to show a world of kindness. It’s not just about what’s good and what’s bad, I wanted to show that there are even better ways to act than normal. For instance, the Pokemon Celebi is said to only appear when you help nature to flourish in a forest in the Pokemon world. Another example I’ve imagined is despite the normal reputation that electronics like refrigerators and trucks damage the environment or waste energy, these devices would be something closer to nature in the Pokemon world.
  translation: 总的来说，我想描绘一个理想的世界，那里和平安宁，没有环境问题，也没有种族歧视。人类与宝可梦之间的关系比主人与宠物的关系要亲密得多，这正是我所设想的理想关系。我希望每个人在与这个世界互动时都能有所感触。在日本，人们有时在火车上不会给老人让座。我想展现一个充满善意的世界。这不仅仅是关于什么是对什么是错，我想展示的是，还有比平常更好的行为方式。例如，据说宝可梦时拉比只会在你帮助宝可梦世界的森林繁荣生长时出现。另一个我想象的例子是，尽管通常人们认为冰箱和卡车等电子产品会破坏环境或浪费能源，但在宝可梦世界里，这些设备会更接近自然。
  note: ''
- speaker: Nintendo Power
  original: When you first began work on Pokemon Diamond & Pokemon Pearl, what were your main goals? What do you think were the key elements to those games?
  translation: 在你们最初开始制作《宝可梦 钻石》与《宝可梦 珍珠》时，主要目标是什么？你认为那些游戏的关键要素是什么？
  note: ''
- speaker: 增田顺一
  original: I decided that ‘ultimate’ was the theme in the beginning. I set myself a task to pursue what was the ‘ultimate’ for Pokemon games, and started to act on this theme when making the games. When I asked myself what is ‘ultimate,’ I immediately knew I wanted to improve the level of communication, which is a core element of Pokemon games. In the games, players receive the Pokedex and start collecting Pokemon, which you need to do in order to trade with others. At the time of Ruby & Sapphire, people could trade their Pokemon with someone close by, but not with anyone overseas. I really wanted to do something about this. And that’s why I came up with the Global Trade Station (GTS). That’s what my goal was in the beginning — to create a user network. I want users to be able to connect to the world. That’s the ultimate style of trading for Pokemon. That was the goal. The key element was to create the storyline around the Pokemon in Sinnoh mythology. The relationship between all these
    Pokemon is the key element. I wanted to express the importance of the balance between substance — Dialga, the ruler of Time, and Palkia, the ruler of Space — and spirit — Uxie, Mesprit, Azelf. If the substance becomes too large, the balance of the spirit collapses. I wanted Dialga and Palkia to become counterparts for a sense of balance. Infinite time and infinite space — that to me is the ‘ultimate.'
  translation: 最初，我确定“终极”为主题。我给自己设定了一个任务，去追求宝可梦游戏的“终极”形态，并在制作游戏时开始围绕这一主题行动。当我自问什么是“终极”时，我立刻意识到我想提升交流的层次，这是宝可梦游戏的核心要素。在游戏中，玩家获得宝可梦图鉴并开始收集宝可梦，而收集宝可梦是为了与他人交换。在《红宝石》与《蓝宝石》的时代，人们只能与附近的人交换宝可梦，无法与海外玩家交换。我非常想改变这一点。因此，我构思了全球贸易中心（GTS）。这就是我最初的目标——建立一个用户网络。我希望用户能够与世界相连。那是宝可梦交换的终极形态。这就是目标。关键要素是围绕神奥地区神话中的宝可梦构建故事情节。这些宝可梦之间的关系是关键要素。我想表达物质——时间之王帝牙卢卡与空间之王帕路奇亚——与精神——由克希、艾姆利多、亚克诺姆——之间平衡的重要性。如果物质过于膨胀，精神的平衡就会崩溃。我希望帝牙卢卡与帕路奇亚成为对应，以体现平衡感。无限的时间与无限的空间——对我来说，那就是“终极”。
  note: ''
- speaker: Nintendo Power
  original: As the series progresses, how do you manage to keep the games accessible to new users while also appealing to core Pokemon fans?
  translation: 随着系列的发展，你们如何做到既让新玩家容易上手，又吸引核心宝可梦粉丝？
  note: ''
- speaker: 增田顺一
  original: As an RPG, the beginning of the game is designed for new users so it’s easy for anyone to understand and play. At the same time, it attracts our core fans because although it may seem random, the battle system has deep elements due to the complex parameters for battling. We care most about the new user. Will they understand how to step out of the house? So, a message appears as you approach the steps, and the shape of the dirt in front of your house is indented to indicate that you are supposed to walk into it. Messages automatically appear as you approach signs. Things that fans are already familiar with can be confusing to the new users, so we need to make sure that the game is inclusive for everyone.
  translation: 作为一款角色扮演游戏，游戏的开头是为新玩家设计的，因此任何人都能轻松理解和游玩。同时，它也能吸引核心粉丝，因为尽管战斗系统看似随机，但由于战斗参数的复杂性，它有着深层的元素。我们最关心的是新玩家。他们能理解如何走出家门吗？因此，当你接近台阶时会出现提示信息，而你家门前泥土的形状是凹陷的，以指示你应该走进去。当你接近标志时，消息会自动出现。粉丝们已经熟悉的东西可能会让新玩家感到困惑，所以我们需要确保游戏对每个人都具有包容性。
  note: ''
- speaker: 河内丸武史
  original: One of the key ideas that I value is the sense of ‘play control’ in the game. Through the game screens and game buttons, I pay attention to how I can feel that I’m doing something in the Pokemon world. It should be instinctive. It should show how easily you can get into the game. If you’re a huge Pokemon fan, you’ll be willing to get into the world more and more, so I think that’s where the hook is. So for example, when you stored your Pokemon in the PC in the Ruby & Sapphire versions, we wanted to make it so that you could literally pull out your Pokemon and store them in a box, thinking that it would help by visualizing your Pokemon being organized in a box.
  translation: 我珍视的关键理念之一是游戏中的“操作感”。通过游戏画面和按键，我注重如何能感受到自己在宝可梦世界中行动。这应该是本能的。它应该展示你进入游戏是多么容易。如果你是一个狂热的宝可梦粉丝，你会越来越愿意进入这个世界，所以我认为这就是吸引点。例如，在《红宝石》与《蓝宝石》版本中，当你在电脑中存放宝可梦时，我们想让你能真正地取出宝可梦并将它们存放在盒子里，认为这样通过可视化宝可梦在盒子中的整理会有所帮助。
  note: ''
- speaker: 增田顺一
  original: I reboot my mind for every single game. I get back in touch with the elementary school student mentality, and I realize I can’t carry on with any complex gameplay anymore. It’s really important to remember how it feels to be a new user.
  translation: 每制作一款游戏，我都会重启我的思维。我重新回到小学生的心理状态，并意识到我不能再承受任何复杂的游戏玩法。记住作为新玩家的感受非常重要。
  note: ''
- speaker: Nintendo Power
  original: Thanks to the Wi-Fi capabilities introduced in Pokemon Diamond & Pokemon Pearl, an amazing community has sprung up around those games. Has anything surprised you with regards to how players use the online functionality?
  translation: 得益于《宝可梦 钻石》与《宝可梦 珍珠》中引入的 Wi-Fi 功能，围绕这些游戏涌现了一个令人惊叹的社区。关于玩家如何使用在线功能，有什么让你们感到惊讶的吗？
  note: ''
- speaker: 增田顺一
  original: The result is as we planned.
  translation: 结果正如我们所计划的那样。
  note: ''
- type: heading
  level: 2
  original: 'Part 3: Pokémon Platinum, Giratina''s Distortion World & Battle Frontier'
  translation: 第3章：《宝可梦 白金》骑拉帝纳破灭的世界与对战开拓区
- speaker: 河内丸武史
  original: As we expected (laughs).
  translation: 正如我们所料（笑）。
  note: ''
- speaker: 增田顺一
  original: You know the GTS site? I thought it was incredible when I saw people in Finland and Northern Europe trading Pokemon on the site. If you go to Europe, you may not see people actually playing the game in the public. But on the internet, you know for sure that people in Europe are actually interacting and exchanging Pokemon. I find that awesome. That’s why I really want it to evolve more. I will make it happen (laughs)!
  translation: 你知道GTS网站吗？当我看到芬兰和北欧的人们在网站上交易宝可梦时，我觉得太不可思议了。如果你去欧洲，可能看不到人们在公共场合玩这个游戏。但在互联网上，你确知欧洲的人们确实在互动和交换宝可梦。我觉得这太棒了。这就是为什么我真的很想让它进一步发展。我会让它实现的（笑）！
  note: ''
- speaker: 河内丸武史
  original: I think things are going in the direction I want them to.
  translation: 我认为事情正朝着我所希望的方向发展。
  note: ''
- speaker: 增田顺一
  original: I was really worried whether people were actually going to use it.
  translation: 我真的很担心人们是否真的会使用它。
  note: ''
- speaker: 河内丸武史
  original: Posting Pokemon for free [on the GTS] was a risky concept. At first we thought we should give out something in return for posting. It turns out we didn’t even have to bother, as a lot of people ended up posting their Pokemon on the GTS. I was pleasantly surprised by that.
  translation: 在GTS上免费发布宝可梦是一个有风险的概念。起初我们认为应该为发布提供一些回报。结果我们根本不必费心，因为很多人最终都在GTS上发布了他们的宝可梦。对此我感到惊喜。
  note: ''
- speaker: Nintendo Power
  original: Do you ever have time to compete online yourself? If so, which Pokemon do you use?
  translation: 您自己有时间在线对战吗？如果有，您使用哪些宝可梦？
  note: ''
- speaker: 增田顺一
  original: Yes, I have. With Dialga or Palkia just like everyone else. I think I had the three starter Pokemon. I can’t remember the opponent’s name unfortunately. Mostly, I battle while developing the game.
  translation: 是的，我有。和所有人一样，使用帝牙卢卡或帕路奇亚。我想我有三只初始宝可梦。可惜我记不起对手的名字了。大多数时候，我是在开发游戏的过程中进行对战的。
  note: ''
- speaker: 河内丸武史
  original: I too play a lot during the game development.
  translation: 我在游戏开发过程中也玩很多。
  note: ''
- speaker: 增田顺一
  original: I’m fully focused when I’m battling. After that, I go back to my natural state and feel at ease.
  translation: 对战时我会全神贯注。之后，我便回归自然状态，感到轻松自在。
  note: ''
- speaker: 河内丸武史
  original: I play with my colleagues mostly since I battle like crazy while we are developing.
  translation: 我主要和同事对战，因为在开发期间我会疯狂地战斗。
  note: ''
- speaker: Nintendo Power
  original: Pokemon Platinum appears to add some significant new features. What new aspects of the game do you think are the most exciting?
  translation: 《宝可梦 白金》似乎增加了不少重要的新功能。您认为游戏中最令人兴奋的新元素是什么？
  note: ''
- speaker: 河内丸武史
  original: What’s most exciting is the new Battle Video feature. This is a function I personally wanted. I’ve always wanted to know how other people play the games, because my blood burns with excitement when I watch that. Other than that, the Battle Frontier, which was also in Emerald, is something I focused on. It’s significant in that two players can play at the facilities. The Pokemon series has been around for more than 10 years, so the first generation of fans is starting to become parents. It’s becoming common for parents to play Pokemon with their children, so we included the feature for children and their fathers or mothers to pair up and challenge the Battle Frontier as a team. When I actually tested it out, it was a lot more entertaining than I thought… There are so many other elements I want to talk about (laughs). The Distortion World was tough to create. It’s visually radical, too.
  translation: 最令人兴奋的是新的对战视频功能。这是我个人一直想要的功能。我一直想知道别人是怎么玩这个游戏的，因为观看时我会热血沸腾。除此之外，我也着重于对战开拓区，它在《绿宝石》中也出现过。其意义在于两名玩家可以在这些设施中共同游戏。宝可梦系列已经走过十多年，第一代粉丝们开始为人父母。父母与孩子一起玩宝可梦已变得普遍，因此我们加入了让父母与孩子组队挑战对战开拓区的功能。当我实际测试时，发现它比我想象的更有趣……还有很多其他元素我想谈（笑）。毁坏的世界很难创造，视觉上也很激进。
  note: 对战视频：允许玩家录制并分享对战过程的功能。对战开拓区：首次出现于《宝可梦 绿宝石》，提供多种对战设施。毁坏的世界：骑拉帝纳的栖息地，具有扭曲的物理规则。
- speaker: Nintendo Power
  original: Are there new battle aspects to Pokemon Platinum that top competitive players should be sure to take note of?
  translation: 《宝可梦 白金》中是否有顶级对战玩家需要注意的新对战要素？
  note: ''
- speaker: 河内丸武史
  original: You now can challenge the Battle Frontier and try to achieve new heights. The Battle Frontier was in Emerald but this one is different with new rules. I want everyone to play Platinum and try to break the Battle Tower record. I think Battle Frontier is the final destination after all.
  translation: 现在你可以挑战对战开拓区，尝试达到新的高度。对战开拓区在《绿宝石》中出现过，但这次不同，有新的规则。我希望大家玩《白金》，尝试打破对战塔的记录。我认为对战开拓区终究是最终的目的地。
  note: 对战塔：对战开拓区中的设施之一，玩家需连续挑战多位训练家。
- speaker: Nintendo Power
  original: Did you have the ideas for Pokemon Platinum in mind while working on Pokemon Diamond & Pokemon Pearl, or did they come about later?
  translation: 在开发《宝可梦 钻石》和《宝可梦 珍珠》时，你们是否已经构思了《宝可梦 白金》的想法，还是后来才想到的？
  note: ''
- speaker: 增田顺一
  original: While developing Diamond & Pearl, Giratina originally embodied the idea of an ‘antiworld,’ which is a paradox of Time and Space. It exists in relation to Dialga and Palkia. That’s what I had in mind when I was developing Diamond & Pearl.
  translation: 在开发《钻石》和《珍珠》时，骑拉帝纳最初体现了“反世界”的概念，那是时间与空间的悖论。它与帝牙卢卡和帕路奇亚相关联。这就是我在开发《钻石》和《珍珠》时的想法。
  note: 反世界：指毁坏的世界，与帝牙卢卡（时间）和帕路奇亚（空间）相对。
- type: heading
  level: 2
  original: 'Part 4: Pichu as the Strategic ''Next Pikachu'' & What Makes Pokémon Endure'
  translation: 第4章：作为战略企划的‘第二代皮卡丘’皮丘，与宝可梦历久弥新的根基
- speaker: 河内丸武史
  original: I was not aware of any of that during the Diamond & Pearl’s development. Masuda told me about it when we started developing Platinum. So it was after Diamond & Pearl for me (laughs). I normally receive key terms from Masuda in the first stage of development, but there were many random terms like ‘antimatter’ and ‘e=mc2,’ ‘Reversed Mt. Fuji’ (‘Sakasa Fuji’) and so on. He explained that ‘Sakasa Fuji’ is the reflection of Mt Fuji on the lake, and it’s the antimatter world. It was challenging to put that concept into the game, so we did extensive research. I didn’t know what exactly ‘antimatter’ was either. I personally think I comprehend it well, but I wonder….
  translation: 在《钻石／珍珠》开发期间，我对此一无所知。直到我们开始开发《白金》时，增田才告诉我这些。所以对我来说，那是在《钻石／珍珠》之后的事了（笑）。通常我会在开发初期从增田那里收到一些关键术语，但当时出现了许多零散的词，比如“反物质”、“e=mc²”、“逆富士”（Sakasa Fuji）等等。他解释说，“逆富士”是富士山在湖面上的倒影，那就是反物质世界。要把这个概念融入游戏颇具挑战性，所以我们做了大量研究。我当时也不完全明白“反物质”究竟是什么。我个人认为自己理解得不错，但……我也不确定。
  note: ''
- speaker: 增田顺一
  original: Yes. It exists but it actually doesn’t. It doesn’t exist but it does. That sort of thing. The mountain exists on the lake through human eyes, but it’s only a reflection and doesn’t exist. It’s a diverse world. You see it only because you are looking at it with your eyes. I’m impressed [with Kawachimaru] for being able to take ingredients that were not substantial and incorporate them into Platinum.
  translation: 是的。它存在，但实际上并不存在；它不存在，却又存在。就是那种感觉。在人类眼中，山存在于湖面上，但那只是倒影，并不真实存在。这是一个多元的世界。你之所以能看到它，只是因为你在用眼睛看。我很佩服（河内丸）能够将这些虚无缥缈的元素融入《白金》之中。
  note: ''
- speaker: Nintendo Power
  original: With so many passionate fans to please with each new installment, does the development team feel a lot of pressure when working on new Pokemon titles?
  translation: 每一部新作都要取悦众多热情的粉丝，开发团队在制作新的宝可梦作品时是否会感到很大的压力？
  note: ''
- speaker: 增田顺一
  original: I personally didn’t feel any pressure at the time of Ruby & Sapphire. I did with Platinum though. During the Ruby & Sapphire period, Pokemon’s popularity had slowed down a little, and people were concerned. I wanted to prove them wrong. Then Ruby & Sapphire were a success so there were higher expectations for Platinum. I can only focus on the quality of each individual game and be content with what we accomplish, but you also can’t avoid the question about the sales numbers. As a developer, I want more people to play the game, but the more games that are sold, the more concerned I become about whether everyone is playing the game without any problems. I do wonder if the new users will play a Pokemon game, or if they’ll buy another game. I don’t feel as pressured about the existing fans — I feel as though I simply hand them what we just came up with for them to check out (laughs).
  translation: 就我个人而言，在《红宝石／蓝宝石》时期并没有感到压力，但制作《白金》时确实感到了压力。在《红宝石／蓝宝石》时期，宝可梦的人气有所下滑，人们对此感到担忧。我想证明他们是错的。后来《红宝石／蓝宝石》取得了成功，因此人们对《白金》的期望更高了。我只能专注于每款游戏的质量，并对我们所取得的成就感到满足，但你也无法回避销量数字的问题。作为开发者，我希望有更多人玩这款游戏，但游戏卖得越多，我就越担心大家是否都能顺利游玩。我会想，新玩家是否会选择宝可梦游戏，还是会去买别的游戏。对于现有粉丝，我倒没那么大压力——我觉得就像是把新作直接交给他们去检验一样（笑）。
  note: ''
- speaker: 河内丸武史
  original: I actually didn’t feel pressured at all about creating Platinum or how it would be received. But as I mentioned earlier, I was concerned about whether or not GTS would take off and be utilized. I was confident with what we created but there would have been no point to have GTS unless people actually participated and posted Pokemon. I handle anything related to communication, so the Mystery Gift that was distributed a few months after the release was another pressure I felt. I was uncertain until I confirmed that it was a success. Rather than feeling obligated to entertain people, I was presenting ideas like, ‘wouldn’t it be fun if we make it this way?’ I have to be confident in my ideas and that’s why I didn’t feel as pressured.
  translation: 实际上，在制作《白金》或考虑其反响时，我完全没有感到压力。但正如我之前提到的，我担心GTS能否成功启动并得到利用。我对我们创造的内容很有信心，但除非人们真正参与并上传宝可梦，否则GTS就毫无意义。我负责所有与通信相关的内容，所以发售几个月后配信的“神秘礼物”也让我感到压力。在确认成功之前，我一直心存不安。与其说我是为了取悦玩家而感到责任重大，不如说我是在提出一些想法，比如“如果我们这样做会不会很有趣？”我必须对自己的想法有信心，所以压力并不大。
  note: ''
- speaker: 增田顺一
  original: I occasionally hear film directors say that their fear is that no one will be in line on opening day. I relate to that, and I get concerned if there will be a line on the release date. It’s the same for every title release. Basically a million people start to debug the game once it gets sold, so we need to make sure to be ready for any bugs that will be found by the users. I also want to further understand the US and European users, and make it more entertaining for them.
  translation: 我偶尔会听到电影导演说，他们最害怕的是首映日没有人排队。我对此深有同感，我会担心发售日是否会有人排队。每款作品发售时都是如此。基本上，游戏一旦售出，就有上百万人开始帮忙调试，所以我们必须准备好应对玩家可能发现的任何漏洞。此外，我也希望更深入地了解美国和欧洲的玩家，为他们带来更多乐趣。
  note: ''
- speaker: Dr. Lava
  original: 'Doctor Lava’s notes: Masuda’s controversial strategy of focusing on attracting new fans at the expense of series veterans hasn’t earned him a lot of love in recent years. Dissatisfaction with Masuda’s directorship gradually increased over the generations, finally coming to a head in the Let’s Go Pikachu era. Many longtime fans weren’t happy that so many classic features were cut from Let’s Go — for example, the lack of a breeding mechanic. One month before the games’ release, Masuda addressed the controversy by saying: “I know that a lot of people and fans have spent a lot of time hatching eggs, they’ve hatched… a lot of eggs, but we want them to kind of discover new ways to enjoy Pokémon games, you know I’d be really sad to think that for them, Pokémon is hatching eggs, so with this one we’re trying to show them a different side of the game.” Fans slammed Masuda for his perceived condescension and being “out of touch” — that was the point when backlash reached its climax, and
    two weeks later Masuda announced he’d no longer serve as the series’ director. Nowadays he’s much less hands-on with the franchise, serving instead as one of several producers.'
  translation: Dr. Lava 的注释：增田顺一颇具争议的策略——以牺牲系列老玩家为代价来吸引新粉丝——近年来并未为他赢得多少好感。随着世代更迭，玩家对增田担任总监的不满逐渐累积，最终在《Let’s Go 皮卡丘》时代达到顶峰。许多老玩家对《Let’s Go》中删除了大量经典要素感到不满，例如缺乏孵蛋机制。在游戏发售前一个月，增田回应了这一争议，他说：“我知道很多玩家和粉丝花了很多时间孵蛋，他们孵了……很多蛋，但我们希望他们能发现享受宝可梦游戏的新方式，你知道，如果对他们来说宝可梦就是孵蛋，我会很难过，所以这一作我们想展示游戏的不同侧面。”粉丝们抨击增田，认为他居高临下且“脱离群众”——那时反对声浪达到高潮，两周后，增田宣布不再担任系列总监。如今，他已不再深度参与该系列，而是担任众多制作人之一。
  note: 编者按/背景注释
- speaker: Nintendo Power
  original: Do you have a favorite Pokemon?
  translation: 你有最喜欢的宝可梦吗？
  note: ''
- speaker: 增田顺一
  original: Pichu. It’s the Pokemon Ken Sugimori came up with when we were trying to figure out who would be the ‘next’ Pikachu, so the character was strategically thought out. It clicked in my mind when Pichu was created and we strategically came up with the idea of the Pichu Bros.
  translation: 皮丘。这是我们在思考谁会成为“下一个皮卡丘”时，由杉森建构思出来的宝可梦，所以这个角色是经过深思熟虑的。当皮丘诞生时，我灵光一闪，我们便策略性地构思出了皮丘兄弟的点子。
  note: ''
- speaker: 河内丸武史
  original: You also like hot new singers who can’t sing well but are overly promoted on TV.
  translation: 你还喜欢那些唱功不佳却在电视上被过度炒作的人气新歌手。
  note: ''
- speaker: 增田顺一
  original: Yes I do (laughs). The singer actually has to sing badly. I like artists with marketing strategies.
  translation: 确实如此（笑）。歌手实际上必须唱得糟糕。我喜欢有营销策略的艺人。
  note: ''
- speaker: Dr. Lava
  original: 'Dr Lava’s notes: The idea of “the next Pikachu” obviously continued into future generations — Plusle, Minun, Pachirisu, Emolga, etc. Interestingly, Game Freak almost made White Pichu a special event Pokemon for HeartGold & SoulSilver, but ended up replacing it with Spiky-eared Pichu. You can read that full story here.'
  translation: Dr. Lava 的注释：“下一个皮卡丘”的想法显然延续到了后续世代——正电拍拍、负电拍拍、帕奇利兹、电飞鼠等等。有趣的是，Game Freak 几乎将白色皮丘作为《心金／魂银》的特殊活动宝可梦，但最终用刺刺耳皮丘取而代之。你可以在这里阅读完整故事。
  note: 编者按/背景注释
- speaker: 河内丸武史
  original: I like Bulbasaur. Before I started to work for GAME FREAK, I purchased Pokemon Green Version and I chose it as my starter. It was love at first sight. It’s four-legged and stubby. It’s the same for dogs. I like Corgis because of their stubby legs.
  translation: 我喜欢妙蛙种子。在为 Game Freak 工作之前，我购买了《宝可梦 绿》并选择了它作为我的初始宝可梦。那是一见钟情。它四足行走，身材矮胖。狗也是如此。我喜欢柯基犬，因为它们腿短。
  note: ''
- speaker: Nintendo Power
  original: With any Pokemon game, I imagine that creating new Pokemon character designs must be a long and challenging process. What qualities do the developers look for in new Pokemon while narrowing down the final roster?
  translation: 对于任何宝可梦游戏，我猜想创造新的宝可梦角色设计必定是一个漫长而充满挑战的过程。在筛选最终阵容时，开发者在新的宝可梦身上寻找哪些特质？
  note: ''
- speaker: 增田顺一
  original: I look at the type of the character and its overall characteristics — what its appeal is, if it’s an endearing character…. I obviously check the features but I feel the ones that convey their habitat and lifestyle are the most appealing. I think it’s important that you get a good idea of what type of Pokemon they are without looking them up in the Pokedex. None of the characters initially have names so it’s important to be very descriptive to visualize what they are. So with Pikachu it would be, ‘it’s yellow, it has a tail in a shape of lightning bolt, and it’s an electric mouse,’ so it’s easy to assume that it will have Electric-type moves; it probably gets struck by lightning. I think about where they live and what they eat. I focus on whether or not the character evokes its lifestyle. If it has a mouth, it probably eats, if it has eyes, it can look at something, if it has a nose, it can smell things. I believe it is important to be able to conjure up an image of creatures
    that are very close to real ones.
  translation: 我会审视角色的属性及其整体特征——它的吸引力何在，是否是一个惹人喜爱的角色……我显然会检查外观，但我认为那些能传达其栖息地和生活方式的设计最具吸引力。我认为重要的是，无需查阅图鉴就能对宝可梦的类型有一个清晰的认知。所有角色最初都没有名字，因此通过描述性来具象化它们至关重要。以皮卡丘为例，“它是黄色的，尾巴呈闪电状，是一只电老鼠”，所以很容易推断它拥有电属性的招式；它可能被闪电击中。我会思考它们住在哪里、吃什么。我关注角色是否能唤起对其生活方式的联想。如果它有嘴，它可能会吃东西；如果有眼睛，它能看东西；如果有鼻子，它能闻气味。我相信能够勾勒出与真实生物非常接近的形象是很重要的。
  note: ''
- speaker: Nintendo Power
  original: Why do you think that the Pokemon series continues to receive so much fan support and enthusiasm after more than a decade since its introduction?
  translation: 您认为为什么宝可梦系列在问世十多年后依然能获得如此多的粉丝支持和热情？
  note: ''
- speaker: 河内丸武史
  original: Perhaps because there is no other game to replace it. There are many games that are similar, but as far as Pokemon goes, I think there is no other game that could replace it — there is something about a Pokemon game that uniquely identifies it as a Pokemon game.
  translation: 也许是因为没有其他游戏可以取代它。有许多类似的游戏，但就宝可梦而言，我认为没有其他游戏能够取代它——宝可梦游戏中有某种东西使其独一无二地成为宝可梦游戏。
  note: ''
- speaker: 增田顺一
  original: Because we are so dedicated in developing the game, it’s quite deep. And because it’s deep, you can look at it in different ways with different perspectives. All the elements, including Pokedex descriptions and Pokemon types, continue to be interesting and fun. Other than that, perhaps it’s because you can battle and trade with the next version that comes out that makes it so appealing. They are all connected. For instance you can bring your Pokemon from Diamond & Pearl to Platinum, or you could insert the Ruby & Sapphire cartridges at the dual slot of the DS. I think that type of mechanism is what’s appealing.
  translation: 因为我们如此专注于开发游戏，所以它相当有深度。正因为有深度，你可以从不同的角度、以不同的视角来看待它。所有元素，包括图鉴描述和宝可梦属性，都持续有趣且好玩。除此之外，也许是因为你可以与下一版本进行对战和交换，这使它如此吸引人。它们都是相连的。例如，你可以将宝可梦从《钻石／珍珠》带到《白金》，或者将《红宝石／蓝宝石》卡带插入DS的双插槽中。我认为这种机制正是其魅力所在。
  note: ''
- speaker: Nintendo Power
  original: In general terms, what do you think will be the key to ensuring that the Pokemon series continues to excite and engage its millions of fans for years to come?
  translation: 总的来说，您认为确保宝可梦系列在未来数年继续令数百万粉丝兴奋和投入的关键是什么？
  note: ''
- speaker: 增田顺一
  original: I think it’s the core element of Pokemon, which is trading and bringing your Pokemon from previous games to each new one. The feeling of connecting different ‘generations’ and ‘expansions’ — namely compatibility with previous games — is important.
  translation: 我认为是宝可梦的核心要素，即交换以及将你从前作中获得的宝可梦带到每一款新作中。连接不同“世代”和“扩展”的感觉——即与前代游戏的兼容性——非常重要。
  note: ''
- speaker: 河内丸武史
  original: Also, interactions between players using Pokemon as a medium. There was trading [through a link cable] in the beginning, and now we can trade with a Wi-Fi Connection. How much we evolve this trading method is the key.
  translation: 此外，玩家之间以宝可梦为媒介的互动也很重要。最初有（通过连接线的）交换，现在我们可以通过Wi-Fi连接进行交换。我们如何发展这种交换方式才是关键。
  note: ''
- speaker: Nintendo Power
  original: Finally, is there anything else that you would like to say to our readers about Pokemon Platinum?
  translation: 最后，关于《宝可梦 白金》，您还有什么想对我们的读者说的吗？
  note: ''
- speaker: 增田顺一
  original: It’s got all the core elements of the Pokemon games — we want everyone to experience an excitement that you never have before.
  translation: 它包含了宝可梦游戏的所有核心要素——我们希望每个人都能体验到前所未有的兴奋。
  note: ''
- speaker: 河内丸武史
  original: Check out the new functionality to play with your friends.
  translation: 请务必体验与朋友一起游玩的新功能。
  note: ''
---





