# 2010–2017：黑白 → 究极日月 的团队演变（分析叙述）

材料：`era-2-2010-2017.md`（Bulbapedia + ポケモンWiki staff credits 算出的逐作变动表、职务矩阵、类别人数），辅以 `people.json` 里每人每作的全部职务串（不只主职）、`sections.md`、`era-3-2018-2026.md` 的 lets-go 一节（用来判断谁在 USUM 之后再没回来）。不使用任何表外来源；凡是"可能在做什么"的推断，都只依据表里同期另一作 / 外传的出现记录。

## 一、总规模与"内核"规模：150 → 467 的膨胀主要在表外团队

六作参与人数：黑白 136、黑白2 150、X·Y 467、ORAS 335、日月 449、究极日月 332。类别（主职）：

| 作品 | 总 | Plan | Prog | Art | Sound | Mgmt | Debug | Loc/QA |
|---|---|---|---|---|---|---|---|---|
| 黑白 2010 | 136 | 15 | 24 | 27 | 4 | 9 | 6 | 43 |
| 黑白2 2012 | 150 | 23 | 29 | 27 | 5 | 13 | 6 | 40 |
| X·Y 2013 | 467 | 18 | 81 | 179 | 6 | 7 | 9 | 160 |
| ORAS 2014 | 335 | 15 | 49 | 92 | 4 | 7 | 10 | 149 |
| 日月 2016 | 449 | 34 | 71 | 151 | 13 | 10 | 9 | 150 |
| 究极日月 2017 | 332 | 25 | 44 | 84 | 6 | 11 | 6 | 129 |

X·Y 是分水岭，但拆开看，467 里 Game Freak 本部式的人并不多。X·Y 新出现的 section 里，"Pokémon Character Motion" 53 人、"Pokémon Character Modeling" 46 人、"Pokémon 3-D Modeling" 11 人、"Pokémon 3-D Model Management" 3 人——合计 113 人的宝可梦 3D 模型/动作团队；"Pokémon Global Link" 35 人 + "Server Development" 8 人是 TPC 侧的网络服务团队；Loc/QA 从 40 涨到 160（NOE 各语种翻译、NOA/NOE QA、韩语组一次性进表）。把 Plan/Prog/Art/Sound/Mgmt 主职里这些外部型 section（宝可梦 3D 模型·动作·检查、PGL、Server、Technical Support、Z-Ring 企划、录音乐手等）剔掉后估算的"内核"：HGSS 79 → 黑白 68 → 黑白2 83 → X·Y 127 → ORAS 100 → 日月 179 → 究极日月 114。也就是说 GF 内部团队在 3DS 时代大约翻了一倍（80 → 130 → 180），而不是三倍；三倍是外包 3D、TPC 网络组和本地化一起被写进名单的结果。

3D 宝可梦模型团队的规模随"要不要做新模型"起落：X·Y 113 人，ORAS 复用模型缩到 31（Modeling 14、3D Modeling 10、Motion 7），日月新增阿罗拉宝可梦回到 48（含新设的 "Pokémon Model Inspection" 8 人），究极日月 19。带这支队伍的 lead 从头到尾是同两人：Masamichi Anazawa（穴澤匡道）和 Atsuko Ujiie（氏家淳子）在 X·Y、ORAS、日月、究极日月四作都是 Art* Pokémon 3-D Modeling；两人"此前外传"都是 Stadium / Snap / XD / Battle Revolution / PokéPark / Pokédex 3D 一脉的 3D 宝可梦作品，Anazawa 还在 Dream Radar（2012）做 Production Management——表里的证据指向这是一支专做宝可梦 3D 模型的外部专业团队被整体接进正传，而不是 GF 内部扩编（具体公司归属需人工核对）。

## 二、逐作结构与新 section：从"一块 credits"到"Section Director 制"

**黑白（2010）**：相对 HGSS 留任 83、新人 42、回归 11，规模持平但结构翻新。新 section 名反映 DS 末期的技术分工：3-D Map Graphics（7 人）与 2-D Dot Graphics（7 人）并列、Field Programming / System Programming / User Interface Programming、Online, Wireless and IR Programming、Wi-Fi Server Development（5 人，外部）、Linked Website Design（Pokémon Global Link 网站，5 人）、Interactive Sound System Design（一之瀬剛、景山将太）；企划侧首次出现 Pokémon & Trainer Parameter Design、Battle Subway Parameter Design、Action Script Design、Game Design of Special Elements（とくしゅシステム）。领导层：増田順一 Director 兼 Producers；渡辺哲也 Prog^ Program Director（从 HGSS 的 Programming Support 直升）；川内丸武史 Plan^ Planning Director 兼 Dir^ Director of Linked Websites；杉森建 2-D Art Director 兼 Director of Pokémon Characters；海野隆雄 3-D Art Director；中津井優 Art^ Map Supervisor & Map Set Design。注意黑白是 Debug 类别常设化的起点（Debug Management 6 人）。

**黑白2（2012）**：留任 108、新人 39。credits 结构上最特殊的一作：大量职务写成 "Pokémon Black and White Version Programming / Game Design / Graphics Design / Music"（Prog 13、Plan 9、Art 6、Sound 3）——也就是把黑白原班以"前作班底"整块列出，新作实际分工只留了 Planning Director 斉藤優史、Program Director 玉田荘介、Art Director 海野隆雄、3-D Map Graphics lead 大久保智彦。新 section：Pokémon Global Link Design（3）、Nintendo 3DS Link Design（Dream Radar 联动）、Pokémon World Tournament Design、Information Management（Mgmt 涨到 13）。领导层换血：Director 从増田换成海野隆雄（増田只留 Producers），Program Director 渡辺→玉田，Planning Director 川内丸→斉藤。同年 Dream Radar 也由海野任 Directors、斉藤 Planning、玉田 Programming、松宮稔展 Concept Design、佐藤仁美 Sound——黑白2 与 Dream Radar 是同一支小班底。

**X·Y（2013）**：留任 116、新人 335、回归 16。除上面说的 3D/PGL/Loc 三块之外，GF 内部也第一次出现清晰的职能 lead 层（"*"）：藤原麻衣子 Art* 3-D Map Graphics、吉田宏信 Art* UI Graphic Design、James Turner Art* Digital Movie Design、大久保智彦 Art* Character Modeling、松宮稔展 Art* Game Dialogue Design、岩尾和昌 Plan* Game Map Design、斉藤優史 Plan* All-Round Game Design（なんでもゲームデザイン，X·Y 新设）/ Game Action Script Design、玉田荘介 Prog* Battle System Programming and Pokémon Data Programming / Script Programming、高橋友也 Prog* Field System Programming、森本茂樹 Prog* Game Battle System Design、下山田照幸 Prog* Network System Game Design、Hiroyuki Nakamura Prog* UI System Programming、Hisanao Suzuki Prog* Network Programming（只此一作）。新 section 还有 Pokémon Design Coordination（大森、海野、杉森、吉田、松島、大村，6 人）、Effect Design、Battlefield Graphic Design、Pokémon Draw Programming、Voice Recording Director（三間雅文）/ Pikachu Voice（大谷育江）、Technical Support（任天堂侧）。"Producers" 改写为 "Produced By"，并第一次列入 TPC 的宇都宮崇人。

**ORAS（2014）**：留任 226、新人 103，缺席但之后回来 67，之后再没出现 174。新 section 少（19 个）：Digital Movie Design and Character Motion Design（11 人，合并组）、Game Design Balancing（チューニング，5 人，X·Y 的 Special Elements 组转过来）、Trainer Character Concept、Lead Technical Artist（植松俊介，Prog 类）、Sound Management（景山）。领导层见第三节。

**日月（2016）**：留任 195、新人 207、回归 47。命名制度改变：中层头衔统一为 "Section Director"（Sound Section Director 一之瀬剛、UI Graphic Design Section Director 吉田宏信、Digital Movie Design Section Director / Effect Design Section Director James Turner、Game Battle System Design Section Director 岩尾和昌、Network System Section Director / Game Design Section Director 川内丸武史），再往上是 Program Director 玉田、Graphics Director 海野、Planning Director 兼 Director 大森。Plan 从 15 涨到 34（新设 Z-Ring and QR Scan Planning 10 人、Event Planning / Video Direction 6、Battle Planning、Communication Features Planning、Concept Planning、Field System Design），Prog 细分为 Field Contents / Field Environment / Event / Tool / Pokémon Drawing Programming，Sound 13 人里有 Vocal Recording 5、Recording Engineer 2、Instrumental Recording 2（第一次把录音团队写进来）。Art 新增 Pokémon Model Inspection（12 人）、Concept Illustration / Item Design。任天堂侧换人：岩田聡（Executive Producers，HGSS 起 6 作）最后一次是 ORAS；日月起 君島達己 Executive Producers、高橋伸也 General Producer；TPC 侧 上井伸 从 PGL 程序名单升到 Produced By。

**究极日月（2017）**：留任 234、新人 95、缺席但之后回来 85。Section Director 制继续但换了一批人：Programming Section Director 高橋友也、System Planning Section Director 森本茂樹、Story Planning Section Director 杉中克考、Graphics Section Director 藤原麻衣子。新 section：Pokémon Model Creation Coordinators（海野隆雄带，6 人）、Movies / Special Effects、Design Art（杉森等 4 人）、Sub Scenario、Scenario Movie Graphics、Field Data Design、Battle Data Design、Z-Power Ring / Rotom Dex Planning；Other 16 人是管弦乐手（Chorus 4、Trumpet 3、Horn 2、String Section 2、Trombone 2），是正传第一次为乐手署名。Loc/QA 里 Keisuke Fukushima 从 Debug Management 转 Chinese Localization，对应中文版首次加入。TPC 新增 曽羽孝則 Produced By。

## 三、领导层交接：増田 → 大森 → 岩尾

- **増田順一**：黑白 Director + Producers；黑白2 只留 Producers（Director 让给海野）；X·Y Director + Produced By；ORAS、日月、究极日月只有 Produced By（同时挂 Music / Sound）；lets-go 重回 Director。六作里他亲自任 Director 的只有黑白与 X·Y。
- **大森滋**：RS/FRLG/Emerald Plan Game Designers → DP Plan Game Design Leader → Pt/HGSS Plan → 黑白 Plan Game Design of Special Elements / Map Design → 黑白2 Plan → X·Y Plan^ Planning Director（兼 Pokémon Design Coordination）→ ORAS Dir! Director（兼 "Concept & Plot"）→ 日月 Director 兼 Planning Director → 究极日月 Produced By → lets-go Produced By。路径是"企划 lead → Planning Director → 姊妹作 Director → 正传 Director → 制作人"，用 ORAS 做了一次正传总监的预演。
- **岩尾和昌**：黑白 Plan Map Design / Pokémon & Trainer Parameter Design / Battle Subway Parameter Design → 黑白2 Plan → X·Y Plan* Game Map Design → ORAS Plan* Game Battle & Contest System Design（表里被记成 Debug*，见第八节）→ 日月 Prog^ Game Battle System Design Section Director → 究极日月 Dir! Director（兼 "Pokémon Ultra Sun & Ultra Moon Concept"）→ sword-shield Plan^ Planning Section Director。与大森一样，第一次 Director 给的是姊妹作。
- **海野隆雄**：HGSS Art^ Art Director → 黑白 Art^ 3-D Art Director → 黑白2 Dir! Director（同年 Dream Radar Directors）→ X·Y 回到 Art^ 3-D Art Director → ORAS 只剩 Art Pokémon Characters Design（无 lead）→ 日月 Art^ Graphics Director → 究极日月 Art* Pokémon Model Creation Coordinators → lets-go Art^ Graphics Section Director。是本段唯一"当过 Director 又回到美术线"的人。
- **杉森建**：黑白 Art^ 2-D Art Director / Director of Pokémon Characters → 黑白2 Director of Pokémon Characters → X·Y、ORAS Art^ Character Art Director（兼 Art* Pokémon Characters Design）→ 日月 只剩 Art* Trainer Graphics Design + Pokémon Characters Design → 究极日月 Art Design Art（无级别）→ lets-go Dir^ Creative Supervisor。表面是降级，实际是从"角色美术总监"退到监修位置；日月起角色美术没有 ^ 级 Director，Pokémon Characters Design lead 由大村祐介接（日月 Art*）。
- **制作人层**：TPC 的 江上周作 HGSS–ORAS Producers/Produced By，日月起只列 Pokémon Global Link（Prog），lets-go 转 Special Thanks；鶴宏明 最后一作黑白（黑白2 转 Thanks，之后 Ranger/PokéPark/Conquest 等外传）；宇都宮崇人 X·Y 起 Produced By；上井伸 黑白2–ORAS PGL → 日月 Produced By；任天堂 山上仁志 六作全程 Producers。

## 四、中层升迁路径（逐人）

**程序线**
- 渡辺哲也：黑白 Prog^ Program Director → 黑白2 普通 Prog（BW Version Programming）→ X·Y Prog Support Programming → ORAS 缺席 → 日月、究极日月 Special Thanks → lets-go Art* Pokémon Model Creation Coordinators。缺席期间他在 rumble-u(2013)、detective-pikachu(2016) 是 "Game-Design Advisors"，在 quest(2018) 是 Dir^ Producer/Director——从 X·Y 起他实际转去做 GF 对外传的顾问与 Pokémon Quest 的总监。
- 玉田荘介：黑白 Prog Field / System → 黑白2 Prog^ Program Director → X·Y Prog* Battle System Programming and Pokémon Data / Script Programming → ORAS 缺席 → 日月 Prog^ Program Director → 究极日月 Special Thanks → lets-go Prog* Library Tool Programming。
- 大野克己：黑白 Prog Online, Wireless and IR / System → 黑白2 Prog → X·Y Prog^ Program Director → ORAS 缺席（同期只在 the-thieves-and-the-1000-pokemon(2014) 出现，且是 Special Thanks）→ 日月 Prog* UI System Programming → 究极日月 缺席 → lets-go 普通 Prog Communication Features / UI Programming。X·Y 之后逐级下行。
- 高橋友也：黑白 Prog Field / Rail System → 黑白2 Prog → X·Y Prog* Field System Programming → ORAS Prog^ Program Director → 日月 Prog* Field Contents Programming → 究极日月 Prog^ Programming Section Director → sword-shield Prog^ Programming Section Director。与玉田正好交错：玉田带 X·Y、日月，高橋带 ORAS、究极日月。
- 一楽克彦：黑白 Special Thanks → 黑白2 Prog Programming → X·Y Prog Network Programming → ORAS 缺席 → 日月 Prog Network Programming → 究极日月 Prog* Communication Features UI Programming → sword-shield Prog* Network Programming。本段内刚到 lead。
- 其他首次带 lead：Miyuki Iwasawa（ORAS Prog* Field System、日月 Prog* Event Programming，之后 lets-go 同职）；Nozomu Saitō（日月 Prog* Field Environment、究极日月 Prog* Field / Event Programming）；Shin Kōsaka（日月 Prog* Network）；Masateru Ishiguro（日月 Prog* Pokémon Drawing Programming）；Hiroyuki Nakamura（X·Y Prog* UI System，之后一直普通 Prog）；谷博行（究极日月 Prog* Field System Design）。名木橋徹（黑白–日月普通 Prog）和 Yuya Ikeuchi（日月普通 Prog）在 lets-go 直接成为 Prog^ System Programming / Field Programming Section Director。

**企划线**
- 斉藤優史：HGSS Plan 多项 → 黑白 Plan Action Script Design → 黑白2 Plan^ Planning Director → X·Y Plan* All-Round / Action Script → ORAS Plan^ Planning Director → 日月、究极日月 缺席 → lets-go Plan^ Planning Section Director。三次 Planning Director 全在"第二团队"作品（黑白2、ORAS、lets-go）。
- 川内丸武史：黑白 Plan^ Planning Director + Dir^ Director of Linked Websites → 黑白2 Plan → X·Y Prog Network System Game Design → ORAS 缺席 → 日月 Prog^ Network System Section Director / Game Design Section Director → 究极日月 缺席（quest(2018) Planning）→ sword-shield Plan Communication Features Planning。
- 森本茂樹：HGSS Dir! Director → 黑白 Prog Battle System Design（普通）→ 黑白2 Plan → X·Y Prog* Game Battle System Design → ORAS 缺席 → 日月 Plan* Battle Planning → 究极日月 Prog^ System Planning Section Director → sword-shield Plan* Battle Planning。
- 下山田照幸：黑白 UI System Design / Wi-Fi Battle System → 黑白2 Plan Game Design / Join Avenue Design → X·Y Prog* Network System Game Design → ORAS 缺席 → 日月 Plan* Communication Features Planning → 究极日月 Special Thanks → lets-go Plan。
- 杉中克考：黑白–ORAS 一直是 Plan（Action Script、Map Design、PWT Design）→ 日月 Plan* Event Planning / Video Direction → 究极日月 Plan^ Story Planning Section Director（兼 Sound Manager）→ lets-go Plan* Story Planning。
- 中津井優：黑白 Art^ Map Supervisor → 黑白2、X·Y Plan → ORAS Plan* Game Map Design → 日月 Art* Game Dialogue Design → 究极日月 Art* Pokémon Characters Design & Concept → sword-shield Plan* World Concept。林千尋 X·Y Plan → 日月 Plan* Game Map Design → 究极日月降回 Plan。貫田将文 X·Y Plan → ORAS Art* Game Dialogue Design（兼 Scenario）→ 日月 Prog* Field System Design，日月是最后一作。

**美术线**
- 藤原麻衣子：HGSS Graphic Design → 黑白、黑白2 3-D Map Graphics → X·Y Art* 3-D Map Graphics → ORAS 缺席 → 日月 Art* 3D Map Graphics → 究极日月 Art^ Graphics Section Director → lets-go 普通 Art。
- 井部真那：黑白–X·Y 普通 Art → ORAS Art^ 3D Art Director → 日月 普通 Art → 究极日月 Art* 3D Map Graphics → sword-shield Art* 3D Map Graphics。ORAS 的 3D Art Director 位是海野缺位（他在 ORAS 无 lead）时顶上的。
- 吉田宏信：黑白、黑白2 2-D Dot Graphics / Battle Graphics → X·Y、ORAS Art* UI Graphic Design → 日月 Art^ UI Graphic Design Section Director → 究极日月 普通 Art（UI lead 让给 久我絵理佳 Art*）。
- James Turner：黑白、黑白2 Pokémon Character Design / Digital Movie → X·Y Art* Digital Movie Design → ORAS 缺席 → 日月 Art^ Digital Movie Design / Effect Design Section Director → 究极日月 普通 Art → sword-shield Art^ Art Director。
- 大久保智彦：黑白2 Art* 3-D Map Graphics → X·Y Art* Character Modeling → ORAS 普通 → 日月 Art* Character Modeling / Pokémon Model Inspection，日月是最后一作。大村祐介：HGSS–ORAS 普通 Art（黑白、黑白2 Trainer Graphics—Main Design）→ 日月 Art* Pokémon Characters Design → 究极日月缺席 → sword-shield Plan Character Design。

**音乐线**：一之瀬剛 HGSS Sound* Music Leader → 黑白、黑白2 普通 Sound → X·Y、ORAS 缺席 → 日月 Sound^ Sound Section Director → 究极日月 普通 Sound。景山将太 黑白、黑白2 Sound → X·Y Sound^ Sound Director → ORAS Sound Music + Sound Management → 日月、究极日月缺席（pokken-tournament(2015) 是 BANDAI NAMCO 侧 Guest Music Composer，duel(2016) 是 Sound Director / Music Composer）→ lets-go 普通 Sound Music。佐藤仁美 在 Sound / Plan / Art（Game Dialogue Design）之间六作换了五次主职，实际一直是"作曲 + 文本企划"两栖。足立美奈子 六作稳定 Sound。

**管理线**：木梨玲 黑白 Mgmt Globalization Coordinators → 黑白2–究极日月 Mgmt Coordinators → lets-go Dir! Produced By；小堀俊介 六作 Coordinators；Shiho Haraguchi Information Coordinators 黑白2–究极日月（12 作，之后不再出现）。

## 五、平行企划信号：谁在缺席的那一作在做什么

**黑白2 → X·Y 之间（黑白2 在、X·Y 缺、之后回来，6 人）**：GF 侧只有 一之瀬剛（Sound，2016 日月回来直接是 Sound Section Director）、谷口輝雄（Sound Effects → legends-arceus）、Yuichiro Takao（3-D Map → sword-shield）。表里 X·Y、ORAS 期间没有任何宝可梦外传记录到一之瀬，说明他 2013–2014 在做的东西不在这个数据集里（数据集只收宝可梦作品），最合理的读法是 GF 的非宝可梦项目；这一点需人工核对。

**X·Y → ORAS 之间（X·Y 在、ORAS 缺、之后回来，67 人）**：按 X·Y 主职分 Art 33、Prog 16、Loc/QA 12、Debug 3、Plan 1、Mgmt 1、Sound 1；67 人里 43 人首次回来就是日月。回来的人几乎都带着头衔：玉田荘介（→ 日月 Prog^ Program Director）、川内丸武史（→ Prog^ Network System / Game Design Section Director）、森本茂樹（→ Plan* Battle Planning）、下山田照幸（→ Plan* Communication Features Planning）、藤原麻衣子（→ Art* 3D Map）、James Turner（→ Art^ Section Director）、Nozomu Saitō（→ Prog* Field Environment）、大野克己（→ Prog* UI System）、松宮稔展（→ Plan Scenario）、にしだあつこ、田谷正夫、小幡敏宏、一楽克彦、名木橋徹、尾上将之。这 16 位 X·Y 主力程序/企划在 ORAS 期间没有任何外传出现（只有大野的 the-thieves Special Thanks、渡辺的顾问名单），却在日月全部以 lead 或 Section Director 身份回归——表能支持的推断是：日月的领导核心在 2014 年就已经从 X·Y 班底里分出来另起炉灶，ORAS 由 高橋友也（Program Director）、斉藤優史（Planning Director）、井部真那（3D Art Director）带一支较小的队伍完成。Art 33 人里大部分是 X·Y 的宝可梦 Modeling / Motion 人员（Hidaka、Yousuke Takahashi、Koizumi、Kuwabara、Nakano、Kitada、Koga、Komagata、Sugiyama 等），ORAS 复用模型不需要他们，日月要做新宝可梦才回来；其中 Fujishiro、Sugiyama、Komagata、Nagao、T. Yoshida、Mori、Fujita 等在 detective-pikachu(2016) 出现，说明这支 3D 团队 2015–2016 同时在为名侦探皮卡丘做模型。

**ORAS → 日月之间（ORAS 在、日月缺、之后回来，19 人）**：GF 侧 斉藤優史（→ lets-go Plan^ Planning Section Director）、景山将太（→ lets-go Sound，期间 pokken/duel）、藤原基史（→ sword-shield Plan Pokémon Design）、Gen'ya Hosaka（→ sword-shield，期间 quest(2018) Programming）、Hiroyuki Namiki（→ scarlet-violet）。斉藤在日月、究极日月两作全缺、2018 直接带 lets-go 的企划，与 伊藤博人（X·Y Plan → ORAS/日月/究极日月三作全缺 → lets-go Plan* Catch & Battle Game Design）一致，指向 lets-go 的企划从 2015–2016 就在并行。

**日月 → 究极日月之间（日月在、究极日月缺、之后回来，85 人）**：按主职 Art 41、Prog 22、Loc/QA 17、Plan 5；首次回来的作品 lets-go 28 人、sword-shield 45 人。这是本段最清楚的"两条线"信号：
- **lets-go 组（2018）**：玉田荘介（日月 Program Director → lets-go Prog* Library Tool）、Miyuki Iwasawa（Prog* Event）、大野克己、Shin Kōsaka、Masateru Ishiguro、Makoto Takebe、Morihiko Kiryu、Syo Araki、Naoya Uematsu（日月 Pokémon Drawing / Tool Programming → lets-go Library Tool Programming）、名木橋徹（→ Prog^ System Programming Section Director）、Yuya Ikeuchi（→ Prog^ Field Programming Section Director）、尾上将之（→ Prog* System）、Masanori Kanamaru、Koji Kawada、小幡敏宏、太田哲司、下山田照幸、栃木遥、Kojiro Matsuyama（→ Art* Movies / Special Effects）、Natsumi Inoue（→ Art* Motion Design）、水谷恵、吉川麻由花、Naoki Goda、Yoshihiro Ohtsuka。日月的 Program Director 加上几乎整个 Tool / Drawing Programming 组同时缺席究极日月，之后一起出现在 lets-go 的 Library Tool Programming——lets-go 的底层引擎/工具在 2017 年就由这批人在做。
- **sword-shield 组（2019）**：川内丸武史、大村祐介（→ Plan Character Design）、松島賢二、にしだあつこ、江尾可奈子、つるたさや、Take（竹）、佐久間さのすけ（→ Plan World Concept Section）——日月的宝可梦设计组几乎整体缺席究极日月；加上 Tomomi Sakuma、Hidaka、Yousuke Takahashi、Miyagawa、Fukaya、Takayama、Furukubo、Atsushi Watanabe、Mai Takai、Kitada、Koga、Ishizuka、Chisato Fujita、Sugiyama、Hiromi Koda（→ sword-shield Pokémon 3D Modeling）、Kazuki Saita（→ Prog* Event System）、Yohei Asaoka（→ Story Planning）、Akira Endo（Network）、Tsukada、Haruyasu Akagi、Jun Arai、Shinobu Ueki（Character Modeling）、Erena Maruya、Koichi Yasuda（Effect → VFX·UI Section）、Stephen Redmond、Yuki Kanayama。新世代的宝可梦设计与建模 2017 年已开工。
- **quest(2018) 组**：85 人中带 "期间外传 quest(2018)" 的 GF 侧有 川内丸武史（quest Planning）、松島賢二、Kazuki Saita（quest Programming）、松崎翼（quest Art Director）；再加缺席更早的 Hosaka（quest Programming）、渡辺哲也（quest Producer/Director）、Masayuki Wada、Noriko Nakagawa（quest Coordinators）。Pokémon Quest 是由渡辺带的一支小队，成员是从日月/ORAS 抽出来的中层。

## 六、离开：连续多作后不再出现的骨干

判断标准：lead 以上，或 ≥3 作；且在链上之后所有作品（含 era-3）都不再以非 Thanks 身份出现。

- **HGSS 之后不再出现（黑白一节，44 人）**：这是 GBA/DS 时代美术班底的整体退场——太田敏（Art Graphic Design，10 作，1996–）、吉川玲奈（Art Pokémon Design，8 作，1996–）、斉藤むねお、岩下明日香、奥谷順（Art Pokémon Design，各 6 作，1999–）、富田愛美（4 作）、後藤浩之、八木裕之（3 作）；程序侧 太田智道（7 作，1996–）、野原悟史（6 作，2002–）；管理侧 Masaru Shimomura（Mgmt* Project Manager，只 HGSS 一作）、Naoko Yanase（Dir^ Information Supervisors，5 作）、Masahiko Oota（Dir^ Mechanical Director，Pokéwalker）。黑白 Art 从 35 降到 27，就是这批人走了、X·Y 之前没有补足。
- **黑白之后不再出现（17 人）**：鶴宏明（TPC Producers，9 作）、Kazuki Yoshihara（Mgmt，6 作）、Kaori Andō（Mgmt，之后 17 部外传，属 TPC 协调而非 GF）、Yoshikazu Tanaka（Debug，3 作）。
- **黑白2 之后不再出现（28 人）**：Keita Kagaya、Yoshinori Matsuda（Prog，各 8 作，2000–）、Tadashi Takahashi（Plan，8 作，2002–）、Mikihiro Ishikawa、Takahiro Yamaguchi（Wi-Fi Server，外部）、Yuuri Sakurai（Mgmt Information，8 作）、Noriko Nakao、Ayako Kajiwara、Hideaki Araki（Mgmt）、森次慶子（Art Pokémon Character Design，3 作）、Naoto Murakami（Plan，3 作）。DS 末期的程序/企划老人在 3DS 转换点离开。
- **X·Y 之后不再出现（174 人，多为 Loc/QA 与 3D 外包）**：GF 侧 曽我部仙史（Prog，11 作，2000–）、森昭人（Prog，11 作，1999–，HGSS 的 Programming Leader）、Ryō Yamaguchi（Server，6 作）、Yukiko Hozumi（Plan Game Design of Special Elements，4 作）、Mayo Otani（Art，3 作）、Hisanao Suzuki（Prog* Network，仅 X·Y）。
- **ORAS 之后不再出现（121 人）**：岩田聡（Executive Producers，15 作）、外山健吉（Art Pokémon Characters Design，9 作，2004–）、田上怜子（Art，5 作）、Mai Mizuguchi（Plan/Prog UI System Design，4 作）、Makiko Takahashi（PGL，4 作）、Yuki Kawamoto（Art 3D Map，3 作）、Kiyomi Itani（Art/Loc，7 作）、Hideaki Kuroda 不算（他到日月）。"Hiro Nakamura*（15 作）"是两个人被合并，见第八节。
- **日月之后不再出现（130 人）**：大久保智彦（Art* Character Modeling，5 作）、貫田将文（Prog* Field System Design，4 作）、田谷正夫（Prog Battle System Programming，11 作，2002–）、江上周作（TPC，12 作）、Sachiko Nakamichi（Art Artwork Support，10 作）、Yuki Tanikawa（Debug Management，9 作）、Tōya Yoneda（Mgmt Information，6 作）、寺地惇（Plan Communication Features Planning，6 作）、Keiichi Yoshikawa（PGL）、Futoshi Kajita（Art，X·Y 时 Art* Character Motion Design）、黒田英明（Sound，3 作）、Akira Sakawa、Yuichi Ishizaki、Tomoka Ogura、Joe Naha（3D，各 3 作）、Masayuki Wada（Mgmt，之后 quest 等外传）。
- **究极日月之后不再出现（依 era-3 lets-go 一节，97 人）**：植松俊介（X·Y Art* Pokémon Character Modeling → ORAS Prog Lead Technical Artist → 日月 Art* → 究极日月普通 Art，4 作后离开）、Shiho Haraguchi（Mgmt Information Coordinators，12 作）、Takahiro O-nishi（PGL，13 作）、Yasuko Sugiyama（Art Artwork Support，6 作）、Ken'ichi Koga（Art Artwork，5 作）以及 PGL 组的一批（Youko Nakayama、Dai Okuyama、Uehara、Ozono、Iwamoto、Yang Rong 等，全是 TPC 网络组）。此外 君島達己 两作后不再出现属任天堂人事。

## 七、两部姊妹作缩编时谁没参加

**ORAS（335 vs X·Y 467）**：缺席的 X·Y 主力见第五节——Program Director 大野、玉田、森本、下山田、川内丸、藤原麻衣子、Turner、Nozomu Saitō、田谷、小幡、一楽、名木橋、尾上、にしだ，加上大部分 3D Modeling / Motion 人员和 12 名 Loc/QA。留下的领导层：大森（Director）、斉藤優史（Planning Director）、高橋友也（Program Director）、井部真那（3D Art Director）、杉森（Character Art Director）；lead 层 岩尾（Battle & Contest Game Design）、中津井（Game Map Design）、Iwasawa（Field System Programming）、Ariizumi（Battle & Contest System Programming）、貫田（Game Dialogue Design）、吉田（UI）、吉川麻由花（Digital Movie / Motion）、Hiroki Fujiwara（Pokémon Character Modeling）、新人 栃木遥（3D Map Graphics，直接带 lead）。程序 lead 从 X·Y 的 8 人降到 3 人。

**究极日月（332 vs 日月 449）**：缺席的日月主力 = lets-go 组 + sword-shield 组（第五节）。留下的：岩尾（Director）、高橋友也（Programming Section Director）、森本（System Planning Section Director）、杉中（Story Planning Section Director）、藤原麻衣子（Graphics Section Director）；lead 层 一楽（Communication Features UI Programming，首次）、Nozomu Saitō（Field / Event Programming）、谷博行（Field System Design，首次）、久我絵理佳（UI Graphic Design，首次）、Junsei Kuninobu（Character Modeling / Motion，首次）、中廣健吾（Pokémon Character Modeling，首次）、Yosuke Uematsu（Movies / Special Effects，首次）、井部（3D Map）、畠祐貴（Pokémon Character Motion）、海野（Pokémon Model Creation Coordinators）。日月的 Section Director 里 玉田、川内丸、一之瀬（降为普通 Sound）、Turner、吉田（后两位降为普通 Art）都不再带队；日月的 Sound Section Director 位在究极日月空缺，杉中兼 "Sound Manager"。两部姊妹作的共同模式：Program Director 都是高橋友也，Planning 侧都由斉藤/杉中而不是大森的 Planning Director 线；究极日月的新 lead 几乎全是首次带队的人。

## 八、数据问题

1. **"Contest" 被当成 "test" 归入 Debug**：ORAS 的 "Game Battle & Contest System Design"（岩尾和昌 lead、西野弘二）、"Battle&Contest System Programming"（Nobuhiko Ariizumi lead、斉田和生）全部记为 Debug，日文原文是 バトル&コンテスト ゲームデザイン / システム プログラム，应为 Plan / Prog。这直接导致 ORAS Debug 10 人虚高、Plan/Prog 偏低，也让岩尾的路径多出一个假的 "Debug*"。
2. **企划性 "…Design" 被归 Art 或 Prog**：Game Dialogue Design（シナリオ ゲームデザイン）→ Art；Battle System Design、Network System Game Design、UI System Design、Field System Design（日文均为 ゲームデザイン / システムせっけい）→ Prog；Parametric Design（パラメーター せってい）、Survey Radar & Tag Mode Design、Join Avenue Design、Pokéstar Studios Design、Pokémon World Tournament Design、Nintendo 3DS Link Design（せっけい）→ Art。这使黑白–日月的 Plan 明显被低估，也制造了大量假"跨类别变动"（松宮稔展 "Plan Scenario ↑ Art* Game Dialogue Design"、森本 "Plan → Prog* Game Battle System Design"、貫田 "Art* → Prog*"）。建议对 role_ja 含 ゲームデザイン / せっけい / せってい 的条目强制 Plan。
3. **外部团队与 GF 混计**：Pokémon Global Link（X·Y 35 人）、Server Development、Wi-Fi Server Development 是 TPC/任天堂网络组；Pokémon Character Modeling / Motion / 3-D Modeling / Model Inspection（X·Y 113 人）是外部 3D 团队；Z-Ring and QR Scan Planning、Z-Power Ring / Rotom Dex Planning 是周边企划；Technical Support 是任天堂 SDK 支持（Tōru Inage 的外传全是任天堂系）。建议单列 "External" 或至少在类别人数表里分开，否则 "Prog 81 / Art 179" 会被读成 GF 内部规模。
4. **同名合并错误**：
   - "Hiro Nakamura*"：1998–2004 的 NOA "US Coordination" 与 2008–2014 的 GF 企划（Platinum Game Design → 黑白 UI System Design → ORAS Game Design Balancing）被合并成一人 15 作。
   - "Leslie Swan（橋本徹）"：NOA 的 Leslie Swan（金银、水晶 Product Testing）与 X·Y 的 3D 建模师 Tōru Hashimoto 合并，汉字挂错人。X·Y "Leslie Swan: Art Pokémon Character Modeling" 是这个错误的产物。
   - 疑似：Akira Nakamura（黑白–ORAS Plan Game Map Design → 日月 Prog Field System Design → area-zero Art Pokémon Character Motion）；Jun ITO（日月 Plan Game Design Balancing → legends-arceus Prog^ CG Technology Section Director）；Keisuke Fukushima（Debug Management → 究极日月 Chinese Localization）；Osamu Fujita（DP Plan Battle Tower Data → ORAS PGL → sword-shield Mgmt）。
5. **名字里的 "*" 与 lead 标记冲突**：Kathy Huguenard*、Teruki Murakawa*、Tomoko Mikami*、Elena Nardo*、Noriko Netley*、Randy Shoemake*、Joel Simon*、Teresa Lillygren*、Michaël Hugot*、Masami Tanaka*、Tomotaka Komura*、Atsushi Sugimoto*、Hiroshi Akune* 的规范名带 Bulbapedia 脚注星号，在表里读起来像 lead。应在归一时剥掉。
6. **罗马字/汉字字段解析残留**：Mana geemufuriiku Ibe（井部真那，ゲームフリーク 消歧义串混进名字）、Shigeru geemufuriiku Oomori 变体、Tanaka hirokazu Sakuhenkyoku（田中宏和，作編曲）、"w:高橋伸也 (ゲームクリエイター)"、"w:とみさわ昭仁"（Wikipedia 链接前缀进了汉字字段）；拼写错误 Hiroyuiki Jinnai、Kenijro Ito、Sususmu Fukunaga；姓名倒置 Shinkai Chiaki、Ishizuka Masaya；Jun ITO / ROMANOV HIGA / MIYAGUCHI TOMOHIRO 等全大写；Takahiro O-nishi。
7. **"期间外传" 含 Thanks 级出现**：大野克己 the-thieves-and-the-1000-pokemon(2014)、Mitsuyo Matsunaga detective-pikachu(2016) 都只是 Special Thanks，却被列为"期间外传"，会误导平行企划推断。应与正传一样排除 Thanks。
8. **黑白2 的 "Pokémon Black and White Version …" 块**：这是黑白原班的整体署名，被当成黑白2 的实际分工后，玉田/渡辺/大野等在黑白2→X·Y 的"职务变动"多数是名义上的，不宜解读为升降。
9. **Bulbapedia 与日文页职务出入**：木梨玲 HGSS 英页 Localization / 日页 スペシャルサンクス；黑白 Akira Kinashi、Teruki Murakawa 英页 Localization / 日页 グローバライズ（管理协调）。日文 グローバライズ 更接近 Mgmt，与红绿的 Miyamoto / Kawaguchi / Ishihara 一类问题同源。
10. **杉森建 日月/究极日月 级别下降**是否为解析问题：日月只解析到 Pokémon Characters Design + Trainer Graphics Design（lead），究极日月只有 Design Art / Pokémon Characters Design & Concept，需对照原 credits 核对是否漏了 Art Director 类头衔。

## 需人工核对的人

Anazawa / Ujiie 团队归属；一之瀬剛 2013–2014 去向；Hiro Nakamura（GF 企划那一位的真名与汉字）；Tōru Hashimoto（X·Y 3D）；Akira Nakamura、Jun ITO、Keisuke Fukushima、Osamu Fujita 是否同人；渡辺哲也 外传 "Game-Design Advisors" 与 quest Producer/Director 是否同一人；Hisanao Suzuki（X·Y 唯一一作 Prog* Network Programming）来路；Masaru Shimomura（HGSS Project Manager）去向。
