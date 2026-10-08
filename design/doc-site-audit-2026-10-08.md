# 文档站摘要 / 排版 / 关键词 / 注释 体检（2026-10-08）

范围：`_posts/` 下 1204 篇（仓库 `pokeamice-main (1)/pokeamice-main`）。只读检查，未改任何文件。

方法：解析每篇 front matter（5 篇 YAML 失败的先在内存里修补再查正文），按规则扫描摘要、标签、`parallel_items` 的译文/原文字段与 Markdown 正文；
复用 `tools/audit_reading_integrity.py` 的结果补充单换行与译文缺失。规则命中后逐类抽样核对，误报已在文末说明。

## 总览

| 类别 | 问题 | 篇数 |
|---|---|---|
| 摘要 | 摘要缺失 | 1 |
| 摘要 | 摘要只是标题 / URL / 关键词串 | 5 |
| 摘要 | 摘要是 HTML 残留 | 2 |
| 摘要 | 摘要疑似截断 | 2 |
| 摘要 | 摘要过短（<20 字） | 2 |
| 排版 | front matter YAML 解析失败（整块不生效） | 5 |
| 排版 | 标题缺空格（`##标题`，不渲染为标题） | 1 |
| 排版 | 段内单换行（来自 reading audit） | 48 |
| 排版 | 同一图片在一篇里被引用 ≥3 次 | 1 |
| 排版 | 连续重复段落 | 1 |
| 排版 | 非文章文件混在 `_posts/` | 3 |
| 关键词 | 缺标签 | 20 |
| 关键词 | 标签是日文原词 | 111 个词 / 222 篇 |
| 关键词 | 英文专名写法不统一（Game Freak / Pokemon 等） | 194 个写法 / 1112 篇 |
| 关键词 | 疑似原文 hashtag（全小写英文词） | 11 个 / 5 篇 |
| 关键词 | 同一作品多写法（写法簇） | 25 组 |
| 关键词 | 同篇标签重复 | 9 篇 |
| 注释 | 译文段内的文字型译注（注：/ 译注 / 编者注 等），没有进 `note` 字段 | 25 篇 / 53 段 |
| 注释 | 原文段内的文字型注释，没有进 `note` 字段 | 8 篇 / 12 段 |
| 注释 | 译文段内注释与 `note` 字段同时存在（需核对是否重复） | 7 篇 / 9 段 |
| 注释 | 译文段内只有 ※ 标记、没有 `note` | 59 篇 / 224 段 |

## 一、摘要

layout 会把 `summary` 用作导语（≤140 字）、「提要」（>140 字），扫描帖则用作「编者按」，所以这里的问题直接显示在页面上。

### 1.1 摘要缺失（1）
- 2026-06-24-[整理]-宝扭蛋怎么找.md · [整理] 宝扭蛋怎么找

### 1.2 摘要只是标题 / URL / 关键词串（5）
这些字段有内容，但不是摘要，读者看到的是一个标题或网址。
- 2022-05-31-Updates.md · Poke Amice 更新日志
- 2022-10-10-[采访]-宝可梦传说阿尔宙斯-日本游戏大赏-岩尾获奖感言.md · Pokémon LEGENDS アルセウス
- 2024-12-10-[站点]-建站纪事-Building-Records.md · https://github.com/Asimov2144/pokeamice
- 2024-12-24-[技能机]-卡图下载-查询时间-Download & Inqury.md · 批量下载卡图 查询服务器存档时间
- 2025-01-01-[整理]-GameFreak-Development-TimeLine.md · 近年 Game Freak 开发事件年表

### 1.3 摘要是 HTML 残留（2）
- 2016-05-19-gamefreak-lineblog-3556962.md · <div class="gf-lineblog-line gf-lineblog-line--center"><br><
- 2016-12-24-gamefreak-lineblog-9250993.md · <div class="gf-lineblog-line gf-lineblog-line--center"><br><

### 1.4 摘要疑似截断（2）
句子在中途断开，末尾没有句读。
- 2007-11-01-gamefreak-director-111.md · 文版了！！ 将由我们公司拥有长期海外生活经历的游戏设计师——Hiro Nakamura负责
- 2008-02-27-gamefreak-director-124.md · Game Boy 软件《宝可梦 红·绿》发售了。 这是皮卡丘、妙蛙花、喷火龙、喵喵和超梦来

### 1.5 摘要过短（2）
- 2024-10-24-[长文]-拨云见日-从百代市到水脉图书馆.md · 这段故事将从水脉图书馆一路讲到百代市。
- 2024-12-30-[站点]-2025-新年快乐.md · 公元2025年 农历乙巳年 新年快乐！

## 二、排版

### 2.1 front matter YAML 解析失败（5）
原因相同：未加引号的值里有 ASCII `: `（`ISBN: 978-…`、`JAN: …`），YAML 把它当成键值分隔符。解析失败时 title / summary / tags / parallel_items 全部不生效。
- 2004-09-10-interview-famitsu-823-emerald-masuda-morimoto.md · mapping values are not allowed in this context
- 2013-11-09-interview-xy-guidebook-masuda.md · mapping values are not allowed in this context
- 2014-11-22-interview-oras-guidebook-masuda-ohmori.md · mapping values are not allowed in this context
- 2017-12-06-interview-usum-guidebook-ohmori-iwao.md · mapping values are not allowed in this context
- 2018-12-01-interview-lgpe-guidebook-masuda.md · mapping values are not allowed in this context

### 2.2 标题缺空格（1）
- 2025-01-01-[整理]-GameFreak-Development-TimeLine.md · ##潜在的项目

### 2.3 段内单换行（48 篇，364 处）
来自 `tools/audit_reading_integrity.py`：正文里一句话被硬换行切开，渲染时会丢失段落感。
- 1996-04-05-scan-shodai-zukan-1996-pokemon-journal.md
- 1999-12-01-scan-gs-guidebook-1999-staff-zukan-journal.md
- 2001-11-01-interview-nom-2001-pokemon-card-e-creatures.md
- 2003-02-21-scan-ndream-084-ruby-sapphire-interview.md
- 2004-09-01-interview-nom-emerald-battle-frontier-evolution.md
- 2005-07-15-scan-corocoro-200508-diamond-pearl-scoop.md
- 2005-08-01-interview-nom-xd-gale-of-darkness-pokemon-festa.md
- 2006-10-01-interview-nom-2006-diamond-pearl-ishihara-masuda-sugimori.md
- 2006-10-01-interview-nom-dp-underground-fossil-battle-report.md
- 2006-11-01-continue-vol31-aoi-yu-pikachu.md
- 2008-02-27-interview-takeshi-shudo-pokemon-memoir-ch138.md
- 2008-03-12-interview-takeshi-shudo-pokemon-memoir-ch140.md
- 2008-03-19-interview-takeshi-shudo-pokemon-memoir-ch141.md
- 2008-08-21-scan-ndream-2008-10-platinum-special.md
- 2008-08-21-scan-ndream-2008-10-tajiri-famicom-25th.md
- 2008-10-21-scan-ndream-2008-12-game-freak-interview.md
- 2008-10-21-scan-ndream-2008-12-platinum-battle-dojo.md
- 2009-09-21-scan-ndream-2009-11-hgss-developer-interview.md
- 2010-02-20-scan-ndream-2010-04-creatures-ranger-interview.md
- 2010-02-20-scan-ndream-2010-04-pokemon-bw-first-reveal.md
- 2010-09-16-scan-famitsu-1137-bw-launch-interview.md
- 2010-09-21-scan-ndream-2010-11-five-regions-guide.md
- 2010-09-23-scan-famitsu-1138-bw-secrets-interview.md
- 2010-10-15-scan-dengeki-games-vol14-bw-gamefreak-interview.md
- 2010-11-01-interview-nintendo-joshi-daisei-bw-kiritani-masuda.md
- 2010-11-20-scan-ndream-2011-01-bw-sound-gakkyoku-damashii.md
- 2011-01-20-scan-otonafamily-201103-masuda-bw-adults.md
- 2011-03-21-scan-ndream-2011-05-bw-design-secrets-ex.md
- 2011-03-21-scan-ndream-2011-05-ohmura-character-making.md
- 2011-03-21-scan-ndream-2011-05-pokemon-typing-ds.md
- 2011-05-21-scan-ndream-bw-tanjou-hiwa-2011-popularity-poll.md
- 2012-07-19-scan-famitsu-1233-b2w2-interview.md
- 2012-07-21-scan-ndream-2012-09-b2w2-developer-interview.md
- 2012-07-21-scan-ndream-221-b2w2-developer-interview.md
- 2012-08-21-scan-ndream-2012-10-b2w2-pickup-secrets.md
- 2012-08-21-scan-ndream-222-b2w2-pwt-pokewood.md
- 2013-10-21-scan-ndream-2013-12-xy-character-design-interview.md
- 2013-11-21-scan-ndream-2014-01-lumiose-city-guide.md
- 2013-11-21-scan-ndream-2014-01-mega-evolution-special.md
- 2015-02-16-interview-4gamer-pokken-tournament-harada-hoshino.md
- 2018-03-30-interview-famitsu-detective-pikachu-jinnai-miyashita.md
- 2022-04-17-interview-seafoam-gaming-pokemon-mystery-dungeon-tomie-yamamoto.md
- 2026-06-21-[专栏翻译] 与宝可梦同行的30年【1996年】初代《红·绿》与幻之宝可梦梦幻 前篇.md
- 2026-07-22-interview-cedec-2026-battle-system-deck.md
- 2026-07-22-interview-cedec-2026-za-kubernetes-windows-containers.md
- 2026-07-23-interview-cedec-2026-za-lumiose-rendering-deck.md
- 2026-08-29-continue-vol23-tuya-scan-archive.md
- 2026-08-29-continue-vol31-scan-archive.md

### 2.4 同一图片被引用多次（1）
同一个 URL 在一篇里出现 3 次以上，多半是占位图没替换。
- 2024-10-24-[长文]-拨云见日-从百代市到水脉图书馆.md · 18 · 76bddc80acbe5fee7888c7d11b058304.jpg

### 2.5 连续重复段落（1）
- 2016-06-27-gamefreak-lineblog-4511791.md · <figure class="gf-lineblog-image"><a href="/assets

### 2.6 非文章文件混在 `_posts/`（3）
Jekyll 不会把这些当文章，但它们是误放的产物，建议挪走。
- 76bddc80acbe5fee7888c7d11b058304.jpg
- replace_trans.py
- replace_translations.py

### 2.7 顺带：译文与原文相同 / 译文缺失（来自 reading audit）
- 译文与原文相同：10 篇
- 译文缺失：7 篇
- 译文里混有日文：2 篇
- 原文重复：3 篇

## 三、关键词（标签）

### 3.1 缺标签（20）
- 1997-05-23-interview-famimaga-tajiri-pokemon2-secret.md
- 1997-10-16-interview-gamefreak-official-red-green-staff.md
- 2009-09-18-interview-dengeki-hgss-shigeki-morimoto.md
- 2010-03-31-interview-pokemon-com-hgss-masuda-morimoto.md
- 2013-10-24-interview-onm-xy-sugimori.md
- 2014-08-22-interview-niconico-gamefreak-origins-masuda.md
- 2014-11-01-interview-topofarmer-ideame-masuda-ohmori.md
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md
- 2016-08-25-interview-nikkei-utsunomiya-pokemon-go.md
- 2017-07-10-interview-cgworld-pokemon-sun-moon-3d-pipeline.md
- 2017-07-15-interview-cgworld-creatures-3d-character-life.md
- 2017-11-09-interview-pokemon-com-usum-ohmori-iwao.md
- 2018-02-23-interview-newspicks-pokemon-utsunomiya-kawamoto.md
- 2018-03-30-interview-famitsu-detective-pikachu-jinnai-miyashita.md
- 2018-05-30-interview-gamer-pokemon-press-conference-2018.md
- 2018-09-12-interview-businesslawyers-pokemon-legal.md
- 2018-10-26-interview-eurogamer-masuda-nabana-lets-go.md
- 2019-10-25-interview-famitsu-sword-shield-masuda-ohmori.md
- 2020-07-01-interview-canuch-gamefreak-office-architecture.md
- 2020-12-25-interview-corocoro-coco-okazaki-taiiku.md

### 3.2 标签是日文原词（111 个词）
这些词直接取自日文原文，没有译成中文，站内分类与搜索会对不上。
- ポケモン · 91 · 2016-04-22-gamefreak-lineblog-2957353.md
- ものづくり · 31 · 2016-03-31-gamefreak-lineblog-2463891.md
- イベント · 31 · 2016-04-01-gamefreak-lineblog-2484438.md
- ポケモンセンター · 24 · 2016-04-16-gamefreak-lineblog-2838565.md
- 株式会社ポケモン · 22 · 2001-11-01-interview-nom-2001-ishihara-tsunekazu-pokemon-world.md
- ポケモンGO · 16 · 2017-02-17-gamefreak-lineblog-9261772.md
- 週刊ファミ通 · 13 · 2004-09-10-interview-famitsu-823-emerald-masuda-morimoto.md
- ピカチュウ · 12 · 2016-08-15-gamefreak-lineblog-6022430.md
- ポケットモンスター · 9 · 2016-11-18-gamefreak-lineblog-9242607.md
- アナハイム · 7 · 2017-08-28-gamefreak-lineblog-9295788.md
- 食べもの飲みもの · 5 · 2016-04-04-gamefreak-lineblog-2554691.md
- ムーン · 5 · 2016-12-31-gamefreak-lineblog-9252218.md
- サン · 5 · 2016-12-31-gamefreak-lineblog-9252218.md
- ゲーム · 5 · 2017-01-17-gamefreak-lineblog-9255500.md
- ポケモン世界大会 · 5 · 2017-08-28-gamefreak-lineblog-9295788.md
- ファミ通 · 4 · 2017-04-22-gamefreak-lineblog-9274234.md
- 電ファミニコゲーマー · 4 · 2022-08-25-interview-cedec-2022-legends-arceus-scarlet-violet-pipeline.md
- ファミマガ64 · 3 · 1996-08-23-interview-famimaga64-tajiri-pokemon2-fax.md
- サンムーン · 3 · 2016-11-18-gamefreak-lineblog-9242607.md
- ポケモンサンムーン · 3 · 2016-11-30-gamefreak-lineblog-9245991.md
- ポケモンGo · 3 · 2016-12-31-gamefreak-lineblog-9252218.md
- スイス · 3 · 2017-04-13-gamefreak-lineblog-9272451.md
- 株式会社ゲームフリーク · 3 · 2026-07-22-interview-cedec-2026-battle-system-deck.md
- ポケモン2 · 2 · 1996-08-23-interview-famimaga64-tajiri-pokemon2-fax.md
- ダ・ヴィンチ · 2 · 2010-12-06-scan-davinci-2011-01-masuda-interview.md
- オトナファミ · 2 · 2010-12-20-interview-otonafami-sugimori-starters-victini.md
- ゲームフリーク · 2 · 2016-06-08-gamefreak-lineblog-4006377.md
- お知らせ · 2 · 2016-08-12-gamefreak-lineblog-5460146.md
- サントラ · 2 · 2016-11-30-gamefreak-lineblog-9245991.md
- サイン会 · 2 · 2016-12-10-gamefreak-lineblog-9248123.md
- シアトル · 2 · 2017-03-24-gamefreak-lineblog-9267902.md
- チーズ · 2 · 2017-04-20-gamefreak-lineblog-9272875.md
- アンノーン · 2 · 2017-08-15-gamefreak-lineblog-9293902.md
- よこはま · 2 · 2017-08-15-gamefreak-lineblog-9293902.md
- ポケポケ · 2 · 2024-10-30-interview-creatures-ptcg-pocket-product-planner.md
- ファミマガ · 1 · 1996-06-28-interview-fcm-13-tajiri-sugimori.md
- ゲーセン天国 · 1 · 1998-01-21-interview-famimaga64-28-tajiri-yuki-secret.md
- ポケモン・ストーリー · 1 · 2000-12-10-interview-pokemon-story-chinese-tajiri-ishihara.md
- コロコロコミック · 1 · 2005-07-15-scan-corocoro-200508-diamond-pearl-scoop.md
- 泣かせどころ · 1 · 2009-12-16-interview-takeshi-shudo-pokemon-memoir-ch206.md
- 週刊アスキー · 1 · 2010-09-13-interview-weekly-ascii-masuda-bw-secrets.md
- サウンドトラック · 1 · 2010-10-20-interview-bw-music-collection-liner-notes.md
- ソリティ馬 · 1 · 2013-10-08-interview-4gamer-2013-solitiba.md
- 福嶋ゆかり · 1 · 2014-05-01-interview-tpc-leaders-challenge.md
- 大奈路まりな · 1 · 2014-05-01-interview-tpc-youth-roundtable.md
- ニコニコ · 1 · 2014-08-22-interview-gameatsumaru-masuda-indie-gamefreak-origins.md
- カードゲーム · 1 · 2016-04-22-gamefreak-lineblog-2957353.md
- 遊び · 1 · 2016-04-29-gamefreak-lineblog-3101639.md
- ポッ拳 · 1 · 2016-05-12-interview-inside-pokken-tournament-developers.md
- ラジオ · 1 · 2016-11-15-gamefreak-lineblog-9241915.md
- ポケットモンスターサンムーン · 1 · 2016-11-30-gamefreak-lineblog-9245991.md
- もみじ · 1 · 2016-12-02-gamefreak-lineblog-9246403.md
- ポータル · 1 · 2016-12-02-gamefreak-lineblog-9246403.md
- キャロットタワー · 1 · 2016-12-02-gamefreak-lineblog-9246403.md
- ポケモンファン · 1 · 2016-12-06-gamefreak-lineblog-9247285.md
- コミコン · 1 · 2016-12-10-gamefreak-lineblog-9248123.md
- ポルトガル · 1 · 2016-12-10-gamefreak-lineblog-9248123.md
- ポルト · 1 · 2016-12-10-gamefreak-lineblog-9248123.md
- ねこ · 1 · 2016-12-24-gamefreak-lineblog-9250993.md
- ヒトカゲ · 1 · 2017-01-01-gamefreak-lineblog-9252717.md
- フシギダネ · 1 · 2017-01-01-gamefreak-lineblog-9252717.md
- あけましておめでとう · 1 · 2017-01-01-gamefreak-lineblog-9252717.md
- ゼニガメ · 1 · 2017-01-01-gamefreak-lineblog-9252717.md
- 走る · 1 · 2017-01-17-gamefreak-lineblog-9255500.md
- ラン二ング · 1 · 2017-01-17-gamefreak-lineblog-9255500.md
- シンガポール · 1 · 2017-01-17-gamefreak-lineblog-9255500.md
- 金銀ポケモン · 1 · 2017-02-20-gamefreak-lineblog-9261965.md
- ブログ · 1 · 2017-02-22-gamefreak-lineblog-9262480.md
- 打ち上げ · 1 · 2017-02-25-gamefreak-lineblog-9262888.md
- スタッフ · 1 · 2017-02-25-gamefreak-lineblog-9262888.md
- お祝い · 1 · 2017-03-05-gamefreak-lineblog-9264881.md
- ママ · 1 · 2017-03-05-gamefreak-lineblog-9264881.md
- コイキング · 1 · 2017-03-23-gamefreak-lineblog-9268453.md
- カニ · 1 · 2017-03-24-gamefreak-lineblog-9267902.md
- シーフード · 1 · 2017-03-24-gamefreak-lineblog-9267902.md
- オイスター · 1 · 2017-03-24-gamefreak-lineblog-9267902.md
- ホタテ · 1 · 2017-03-24-gamefreak-lineblog-9267902.md
- インフィオラータ · 1 · 2017-03-27-gamefreak-lineblog-9269086.md
- スタバ · 1 · 2017-03-28-gamefreak-lineblog-9268015.md
- スターバックス · 1 · 2017-03-28-gamefreak-lineblog-9268015.md
- おうじゃのしるし · 1 · 2017-03-29-gamefreak-lineblog-9269424.md
- やどん · 1 · 2017-03-29-gamefreak-lineblog-9269424.md
- ヤドキング · 1 · 2017-03-29-gamefreak-lineblog-9269424.md
- スマホ · 1 · 2017-04-13-gamefreak-lineblog-9272451.md
- スマホケース · 1 · 2017-04-13-gamefreak-lineblog-9272451.md
- モントルー · 1 · 2017-04-20-gamefreak-lineblog-9272875.md
- ディナー · 1 · 2017-04-20-gamefreak-lineblog-9272875.md
- ファミ通アワード2016 · 1 · 2017-04-22-gamefreak-lineblog-9274234.md
- ポケットモンスターサン · 1 · 2017-04-22-gamefreak-lineblog-9274234.md
- ポケットモンスタームーン · 1 · 2017-04-22-gamefreak-lineblog-9274234.md
- グリュイエール · 1 · 2017-04-30-gamefreak-lineblog-9272876.md
- ニャース · 1 · 2017-07-13-gamefreak-lineblog-9288581.md
- ロケット団 · 1 · 2017-07-13-gamefreak-lineblog-9288581.md
- ルギア · 1 · 2017-07-24-gamefreak-lineblog-9290179.md
- フリーザー · 1 · 2017-07-24-gamefreak-lineblog-9290179.md
- 七夕祭り · 1 · 2017-08-11-gamefreak-lineblog-9293254.md
- ジラーチ · 1 · 2017-08-11-gamefreak-lineblog-9293254.md
- はまれぽ · 1 · 2017-08-15-gamefreak-lineblog-9293902.md
- パレード · 1 · 2017-08-15-gamefreak-lineblog-9293902.md
- バリヤード · 1 · 2017-08-15-gamefreak-lineblog-9293902.md
- ミュウツー · 1 · 2017-08-17-gamefreak-lineblog-9293972.md
- 横浜スタジアム · 1 · 2017-08-17-gamefreak-lineblog-9293972.md
- レイド · 1 · 2017-08-17-gamefreak-lineblog-9293972.md
- ポケモンGOスタジアム · 1 · 2017-08-17-gamefreak-lineblog-9293972.md
- ディズニー · 1 · 2017-08-28-gamefreak-lineblog-9295788.md
- ガルーラ · 1 · 2017-09-01-gamefreak-lineblog-9296031.md
- ブロック · 1 · 2017-09-06-gamefreak-lineblog-9296034.md
- メキシコ料理 · 1 · 2017-09-08-gamefreak-lineblog-9297286.md
- ほぼ日 · 1 · 2021-10-25-interview-hobonichi-2021-kubo.md
- ぽこ あ ポケモン · 1 · 2026-02-16-interview-famitsu-2026-pokopia.md
- ガチャ · 1 · 2026-06-24-[整理]-宝扭蛋怎么找.md

### 3.3 英文专名写法不统一（194 个写法，前 30）
多数是专名（Game Freak、LINE BLOG、Pokemon），不一定是错，但与中文站内写法（宝可梦、游戏弗利克）并存，分类页会分裂。
- Game Freak · 850 · 1996-04-05-scan-shodai-zukan-1996-staff-interview.md
- LINE BLOG · 251 · 2016-03-31-gamefreak-lineblog-2413352.md
- Pokemon · 188 · 1999-01-15-interview-1101-hey-you-pikachu-ambrella-ozawa.md
- Nintendo DREAM · 34 · 2003-02-21-scan-ndream-084-ruby-sapphire-interview.md
- Creatures · 22 · 2001-11-01-interview-nom-2001-pokemon-card-e-creatures.md
- N.O.M · 19 · 2000-06-01-interview-nom-2000-kubo-masakazu-pokemon-hit.md
- Pokémon GO · 16 · 2015-09-11-[GameFreak部长专栏]-第244回-Pokemon-GO发布.md
- Game Informer · 15 · 2010-03-19-interview-gameinformer-masuda-morimoto-hgss.md
- WCS · 11 · 2016-05-12-interview-inside-pokken-tournament-developers.md
- JA · 10 · 2000-01-01-interview-2000-01-01-sunanohi-pokemon-game-kaigi.md
- The Pokémon Company · 10 · 2010-05-12-interview-wedge-ishihara-pokemon-disney.md
- 4Gamer · 7 · 2013-10-08-interview-4gamer-2013-solitiba.md
- X·Y · 7 · 2013-10-10-interview-gamasutra-xy-monster-design.md
- CEDEC 2026 · 7 · 2026-07-22-interview-cedec-2026-battle-system-deck.md
- Ambrella · 6 · 1999-01-15-interview-1101-hey-you-pikachu-ambrella-ozawa.md
- CONTINUE · 6 · 2005-08-18-scan-continue-vol23-drill-dozer.md
- Gear Project · 6 · 2013-11-01-interview-gamefreak-recruit-3d-graphics-to-fk.md
- Gen 1 · 5 · 1996-06-28-interview-fcm-13-tajiri-sugimori.md
- XY · 5 · 2013-10-04-interview-nwr-xy-masuda-yoshida.md
- PTCG · 5 · 2016-09-16-interview-pokemon-card-20th-art-collection-ishihara-oyama-arita.md
- Niantic · 5 · 2016-09-30-interview-gnn-pokemon-go-tokyo-roundtable.md
- CGWORLD · 5 · 2017-06-10-scan-cgworld-2017-07-game-graphics-studio-extra.md
- N · 4 · 2010-09-10-interview-iwata-asks-bw-chapter-4-unchanging-pokemon-essence.md
- AR · 4 · 2011-06-16-interview-iwata-asks-pokedex-3d-bw-chapter-3-obvious-animation.md
- Gen 5 · 4 · 2012-06-21-interview-famitsu-1229-b2w2-masuda-unno.md
- JP · 4 · 2013-01-22-interview-staff-tsuruta.md
- R&D · 4 · 2015-09-01-interview-gamefreak-rnd-launch-taya-mi.md
- PokeAmice · 4 · 2022-05-31-Updates.md
- CEDEC 2023 · 4 · 2023-08-24-interview-denfami-2023-cedec-visual.md
- Pokémon LEGENDS Z-A · 4 · 2026-07-22-interview-denfami-2026-cedec-battle.md

### 3.3b 疑似原文 hashtag（全小写英文词，11 个 / 5 篇）
多是 LINE BLOG 原文里的 `#sun`、`#party` 之类话题标签被原样当成标签，应删除或译成中文。
- pokemon · 2 · 2016-11-15-gamefreak-lineblog-9241915.md
- christmas · 1 · 2016-12-04-gamefreak-lineblog-9246836.md
- moon · 1 · 2016-12-04-gamefreak-lineblog-9246836.md
- sun · 1 · 2016-12-04-gamefreak-lineblog-9246836.md
- party · 1 · 2016-12-04-gamefreak-lineblog-9246836.md
- art · 1 · 2016-12-06-gamefreak-lineblog-9247285.md
- tattoo · 1 · 2016-12-06-gamefreak-lineblog-9247285.md
- airport · 1 · 2016-12-06-gamefreak-lineblog-9247285.md
- madrid · 1 · 2016-12-06-gamefreak-lineblog-9247285.md
- architecture · 1 · 2016-12-06-gamefreak-lineblog-9247285.md
- translation · 1 · 2026-06-21-[专栏翻译] 与宝可梦同行的30年【1996年】初代《红·绿》与幻之宝可梦梦幻 前篇.md

### 3.4 标签是域名（4）
- 2012-10-01-interview-pokemon-com-b2w2-masuda-unno.md · Pokemon.com
- 2013-09-19-interview-jv-2013-xy.md · jeuxvideo.com
- 2014-05-14-interview-pokemoncom-2014-maestro.md · Pokemon.com
- 2018-11-01-interview-pokemoncom-2018-letsgo-makers.md · Pokemon.com

### 3.5 同一作品多写法（25 组）
同一对象的写法不统一，会被当成不同标签，分类页会分裂。
- 宝可梦 红·绿 / 宝可梦红绿
- 赤·绿 / 赤绿
- 宝可梦 金·银 / 宝可梦金银
- Pokemon / pokemon
- 金·银 / 金银
- 红宝石·蓝宝石 / 红宝石蓝宝石
- Nintendo DREAM / Nintendo Dream
- 钻石·珍珠 / 钻石珍珠
- 黑·白 / 黑白
- 宝可梦 黑·白 / 宝可梦黑白
- 宝可梦 黑2·白2 / 宝可梦黑2白2
- 宝可梦 XY / 宝可梦 X·Y / 宝可梦XY
- XY / X·Y
- 宝可梦 ORAS / 宝可梦ORAS
- Pokémon GO / PokémonGO
- 宝可梦 太阳·月亮 / 宝可梦 太阳／月亮
- Pokemon GO / pokemonGO
- 太阳·月亮 / 太阳月亮 / 太阳／月亮
- ポケモンGO / ポケモンGo
- 究极之日·究极之月 / 究极之日究极之月
- Let's Go / Lets Go
- 宝可梦 剑·盾 / 宝可梦剑盾
- 剑盾 / 剑／盾
- 宝可梦 朱·紫 / 宝可梦朱紫
- 宝可梦传说 阿尔宙斯 / 宝可梦传说阿尔宙斯

### 3.6 同篇标签重复（9 篇）
- 2013-05-29-interview-glitterberri-early-concept-art.md · 28
- 2009-04-01-interview-nintendo-power-masuda-gens-1-4.md · 20
- 2021-11-08-interview-creatures-history-special-ishihara-tanaka.md · 11
- 2017-08-10-interview-gameinformer-how-game-freak-designs-pokemon-creatures.md · 10
- 2018-06-25-interview-funsproject-atsuko-nishida-shoko-nakagawa-character-design.md · 10
- 2017-08-14-interview-gameinformer-why-ruby-and-sapphire-were-most-challenging.md · 8
- 2006-04-24-interview-gpara-2006-yoshida.md · 1
- 2013-10-08-interview-4gamer-2013-solitiba.md · 1
- 2014-08-22-interview-gameatsumaru-masuda-indie-gamefreak-origins.md · 1

## 四、注释被当成正文

译注写在 `parallel_items` 的 `translation` / `original` 字符串中间时，layout 不会拆出来，读者会直接看到「注：……」。
layout 为 `item.note` 设计了「※ 查看译注」弹层，所以正确做法是把注释移到 `note` 字段。

### 4.1 译文段内注释，没有进 `note`（53 段，25 篇）
- 1997-10-16-interview-gamefreak-official-red-green-staff.md · 注： · ME FREAK里最健康又最黑的人啾～。大家也要学他变得健康皮卡！！注：酒和赌博可不要学哦。
- 1997-10-16-interview-gamefreak-official-red-green-staff.md · （注 · 进行的采访啾。今天的目标是，因为经常去极真空手道场而被叫做“空手王”（注：据说最近升到了二段）的程序员大叔，不对，是大哥啾。那么出发啾！
- 1997-10-16-interview-gamefreak-official-red-green-staff.md · （注 · 林原惠。（注·武藏的配音演员）
- 2000-05-01-interview-2000-05-01-kakeru-pokemon-site-dawn.md · （注 · ttp://www.st.rim.or.jp/~hime-ft-/ （注：现在上述企划已被删除。请在存档中挖掘2004年以前的内容）。
- 2001-01-27-interview-nom-mobile-system-gb-revolution.md · （注 · 在自己家里就能通信对战，非常方便。和住得远的朋友也能轻松对战、交换。（注：点对点只限相同颜色的“移动适配器GB”之间。此外，不同地区的c
- 2008-12-10-interview-takeshi-shudo-pokemon-memoir-ch167.md · （注 · 在正片片头出字幕之前的短短数分钟内，必须完成对超梦的震撼亮相（注：这与后来DVD及录像带发行的完全版不同，完全版在片头前进一步追
- 2009-03-23-interview-gamepro-platinum-masuda-kawachimaru.md · 编辑注 · 【编辑注：书呆子！】
- 2009-05-27-interview-takeshi-shudo-pokemon-memoir-ch186.md · （注 · ，“活下去！（生きろ！）”这句口号被某部著名的动画电影用作了宣传标语（注：指吉卜力《幽灵公主》）。考虑到那部动画真正想表达的母题其实压根
- 2009-07-22-interview-takeshi-shudo-pokemon-memoir-ch191.md · （注 · 在他另外的作品里（注：指《椿三十郎》），也冒出过诸如“真正锋利的宝刀必须安稳藏在刀鞘
- 2009-08-05-interview-takeshi-shudo-pokemon-memoir-ch193.md · （注 · 在日本本土市场上，横亘着斩获过匪夷所思天文数字票房的“国民级动画巨著（注：指宫崎骏与吉卜力动画，如《幽灵公主》）”。
- 2009-08-05-interview-takeshi-shudo-pokemon-memoir-ch193.md · （注 · 那是一颗纯粹为了制造炒作噱头而硬塞进去的预告专用精灵球（注：即GS球）。
- 2009-08-05-interview-takeshi-shudo-pokemon-memoir-ch193.md · （注 · 在后来那部以鱼之少女为主角的国民级动画（注：指宫崎骏2008年《悬崖上的金鱼姬》）里，在全行业CG动画泛滥
- 2009-09-18-interview-dengeki-hgss-shigeki-morimoto.md · 注： · 注：文中表述·《宝可梦 蓝》……《蓝》·《宝可梦 皮卡丘》……《皮卡
- 2010-03-31-interview-takeshi-shudo-pokemon-memoir-ch218.md · 编者注 · 掌生杀大权的御前样，内心一直将日本另一部具有国民级声誉的殿堂级动画（编者注：普遍推测为宫崎骏/吉卜力作品）视作最大的假想敌暗暗较劲。
- 2010-03-31-interview-takeshi-shudo-pokemon-memoir-ch218.md · 编者注 · 斯拉》，赫然是一部硬生生塞进一个美国人当男主角的魔改美版《哥斯拉》（编者注：1956年美版《怪兽王哥斯拉》）。
- 2010-04-28-interview-takeshi-shudo-pokemon-memoir-ch220.md · 编者注 · 而是一部聚焦美国哈佛大学传奇公开课的特别节目（编者注：迈克尔·桑德尔教授的《正义：一场思辨之旅》/《哈佛白热教室》
- 2010-05-12-interview-takeshi-shudo-pokemon-memoir-ch221.md · 编者注 · 比起东京原宿的知名玩具城Kiddy Land还要庞大数倍的宏伟殿堂（编者注：普遍指代时代广场著名的反斗城旗舰店或FAO Schwarz）
- 2010-05-12-interview-takeshi-shudo-pokemon-memoir-ch221.md · 编者注 · 言，《数码宝贝》的摇篮中确实孕育出了出类拔萃的顶尖天才动画电影作家（编者注：指细田守监督执导的《滚球兽的诞生》《我们的战争游戏》）。
- 2010-05-12-interview-takeshi-shudo-pokemon-memoir-ch221.md · 编者注 · 听说今年《数码宝贝》又将以崭新的动画姿态重新启航（编者注：指2010年的《数码兽合体战争》），我由衷期盼他们能全力以赴
- 2010-05-12-interview-takeshi-shudo-pokemon-memoir-ch221.md · 编者注 · 容易由猿进化成了人却又愚蠢地倒退回猿猴返祖老路的‘某魔法少女作品’（编者注：首藤痛斥某侵权山寨甜甜仙子企划），二者都绝不至于堕落至此。
- 2010-05-19-interview-takeshi-shudo-pokemon-memoir-ch222.md · （注 · 、长年执拗于在‘虚构与现实的界限模糊’中故弄玄虚的知名动画大导演泰斗（注：指押井守及其编剧作品《宫本武藏：双剑飞驰之梦》），不知哪根筋搭
- 2010-05-19-interview-takeshi-shudo-pokemon-memoir-ch222.md · （注 · 原来通通都只是这出大戏的漫长预告片，真正的重头戏正本全都在剧场版之中（注：指京都动画名作《凉宫春日的消失》）。整整两个半小时的超长片长，
- 2010-05-19-interview-takeshi-shudo-pokemon-memoir-ch222.md · （注 · 期深夜档正在热播的那部将京都大学生的荒诞大学生活描摹得惟妙惟肖的动画（注：指汤浅政明执导、森见登美彦原著的《四叠半神话大系》），其让人拍
- 2010-05-26-interview-takeshi-shudo-pokemon-memoir-ch223.md · （注 · 就连那位被戏称为‘御前样’的最高决策层实权人物（注：指小学馆或角川高层），后来在某位业界的告别仪式上与我不期而遇时
- 2010-06-30-interview-takeshi-shudo-pokemon-memoir-ch226.md · （注 · 位上的节目总监修顾问，正是全日本赫赫有名、泰山北斗级的殿堂级科幻巨擘（注：即写下《日本沉没》《复活之日》的日本科幻教父小松左京）。
- 2010-06-30-interview-takeshi-shudo-pokemon-memoir-ch226.md · （注 · 讲述所谓‘Newtype新人类觉醒’的划时代机器人大作亦悄然破土公映（注：指富野由悠季执导的《机动战士高达0079》初代于土曜午后五点半
- 2010-09-10-interview-pokemon-peer-sugimori-ohmori-designers.md · [注 · 总共有17个人。每个人设计了大约10只宝可梦。[注：17x10 = 170！]
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-05-29-interview-glitterberri-early-concept-art.md · 译者注 · 译者注
- 2013-09-19-interview-jv-2013-xy.md · 编者注 · 这还没有正式公布。无论如何，在日本，价格将是每年500日元（编者注：在欧洲，最终将是每年5欧元）。我还要补充一点，我们意识到玩家
- 2013-11-01-interview-gamefreak-recruit-3d-graphics-to-fk.md · （注 · g），而是我们美术团队与底层程序员紧密协同开发出的极具巧思的定制算法（注：详见当年《CGWORLD》10月10日发售刊专访）。
- 2014-05-01-interview-tpc-global-business-hirobe.md · （注 · 话说回来，像在美国那边，虽然发售时对应掌机的普及率跟以前比有不小差距（注1），可因为我们在发售前把氛围彻底炒热了，预约量硬是追平了《宝可
- 2016-08-25-interview-nikkei-utsunomiya-pokemon-go.md · （注 · 非常像《Ingress》。就像在Ingress中被称为“Portal（注：与史迹、招牌等现实世界相对应的游戏内据点）”的所有地点都配置宝
- 2017-05-10-interview-pokemon-recruit-passion.md · （注 · 个最真正需要你的地方吧。”宝可梦公司内部并没有专门写代码的技术研发岗（注：技术开发主要依托GF/Creatures及合作技术公司）。但正
- 2019-10-25-interview-famitsu-2019-swsh-autosave.md · 注： · 您能这么觉得，我很高兴。而且，去到旷野地带（编注：本作中登场的、一望无际的自然区域）后，会有很多宝可梦，也会显示广
- 2019-10-25-interview-famitsu-2019-swsh-autosave.md · 注： · 大的地方在于，加入了可以更改因“性格”而容易提升的能力（编注：宝可梦会因各自拥有的“性格”不同，各项能力提升的难易度也不同）的
- 2019-10-25-interview-famitsu-sword-shield-masuda-ohmori.md · 注： · 您能这么想，我们深感荣幸。而且，前往旷野地带（编注：本作中登场的，一望无际的自然风光区域）的话，能看到许多宝可梦，以
- 2019-10-25-interview-famitsu-sword-shield-masuda-ohmori.md · 编者注 · 大的方面来说，我们加入了可以改变因“性格”而容易提升的能力（编者注：每只宝可梦因各自的“性格”不同，各项能力的提升难易度也会有所
- 2021-12-27-interview-gamefreak-recruit-concept-artist-fk.md · （注 · 当时分派给我的课题是设定一个“非地球的某个异星球”（注：即究极空间与异世界异兽栖息地）。上级给我的要求是：连企划案上完

### 4.2 原文段内注释，没有进 `note`（12 段，8 篇）
原文在折叠的「原文」区里，影响小于译文，但同样是注释混入正文。
- 1997-10-16-interview-gamefreak-official-red-green-staff.md · 注： · まってみましたでちゅう～。みんなも彼を見習って健康になるでちゃー！！注：お酒とギャンブルは見習わないで下さい。
- 1997-10-16-interview-gamefreak-official-red-green-staff.md · （注 · ちゅう。今日のターゲットは、極真空手の道場に通っているために「空手王（注・最近二段に昇段したらしい）」と呼ばれてるプログラマーのおじさん
- 1997-10-16-interview-gamefreak-official-red-green-staff.md · （注 · 林原めぐみ。（注・ムサシ役の声優）
- 2000-05-01-interview-2000-05-01-kakeru-pokemon-site-dawn.md · （注 · ttp://www.st.rim.or.jp/~hime-ft-/ （注：現在では上記企画は削除済み。アーカイブで2004年以前を掘ろう
- 2001-01-27-interview-nom-mobile-system-gb-revolution.md · （注 · とっても便利。遠くに住んでるお友達とも気軽に対戦や交換ができますよ。（注：ピアｔｏピアができるのは必ず、同じ色の「モバイルアダプタＧＢ」
- 2009-09-18-interview-dengeki-hgss-shigeki-morimoto.md · 注： · 注：記事中の表記・『ポケットモンスター 青』……『青』・『ポケットモ
- 2014-05-01-interview-tpc-global-business-hirobe.md · （注 · アメリカでは、ゲームソフト発売時点での対応機種の普及台数に差があった（注１）にもかかわらず、発売前に大きな盛り上がりをつくりだしたことに
- 2016-08-25-interview-nikkei-utsunomiya-pokemon-go.md · （注 · s（イングレス）」っぽいんですよ。イングレスで言うところの「ポータル（注：史跡や看板など現実世界に即したゲーム内の拠点）」すべてにポケモ
- 2019-10-25-interview-famitsu-2019-swsh-autosave.md · 注： · そう感じていただけるとありがたいです。さらに、ワイルドエリア（編注：本作で登場する、見渡す限りの自然が広がるエリア）へ行くと、ポケモ
- 2019-10-25-interview-famitsu-2019-swsh-autosave.md · 注： · 大きなところでは、“せいかく”によって上がりやすい能力（編注：ポケモンはそれぞれが持つ“せいかく”によって、各種能力の上がりや
- 2019-10-25-interview-famitsu-sword-shield-masuda-ohmori.md · 注： · そう感じていただけるとありがたいです。さらに、ワイルドエリア（編注：本作で登場する、見渡す限りの自然が広がるエリア）へ行くと、ポケモ
- 2019-10-25-interview-famitsu-sword-shield-masuda-ohmori.md · 注： · 大きなところでは、“せいかく”によって上がりやすい能力（編注：ポケモンはそれぞれが持つ“せいかく”によって、各種能力の上がりや

### 4.3 译文段内注释与 `note` 同时存在（9 段）
另有 41 篇 / 95 段是 ※ 标记且已有 `note`，多为 `（※1）` 这类引用标记（保留即可）。
需要逐条核对：有的是 `（※1）` 这类引用标记（保留即可），有的是注释内容被写了两遍。
- 2000-01-01-interview-2000-01-01-sunanohi-pokemon-game-kaigi.md · 备注： · 备注：1997年小学馆发行的文库本《宝可梦的秘密》（Amazon）第
- 2003-05-30-interview-cvg-ruby-sapphire-gamefreak-masuda-sugimori-morimoto.md · （注 · 并非如此，我们仍然得到了粉丝的支持，我相信我们还会继续得到这种支持。（注：迄今为止《宝可梦 红宝石／蓝宝石》在日本售出440万份）
- 2009-03-23-interview-gamepro-platinum-masuda-kawachimaru.md · 注： · 【作者注：在《宝可梦 白金》中，道馆馆主和道馆训练家不再携带任何与各自道馆
- 2010-03-19-interview-gameinformer-masuda-morimoto-hgss.md · 编者注 · 带着各自的创意参加由杉森建（GAME FREAK 艺术总监兼董事——编者注）主持的设计会议。基本上，每位设计师都会提出自己的想法，经过讨
- 2010-05-12-interview-wedge-ishihara-pokemon-disney.md · （注 · 黑泽明导演似乎也有过类似的经历（注：滨野氏与已故黑泽导演的关系请参照本系列上一回）。
- 2010-09-10-interview-pokemon-peer-sugimori-ohmori-designers.md · [注 · ？我在这里卡住了。最后我说，如果海獭要进化，它会变成完全不同的东西。[注：几天前传闻的水水獭的第三阶段进化看起来和水水獭完全不同。]
- 2011-03-01-interview-nintendo-power-bw-masuda-sugimori.md · 编者注 · 站，将于今年春季上线，允许玩家关联游戏数据以体验额外的在线功能。——编者注]
- 2011-03-01-interview-nintendo-power-bw-masuda-sugimori.md · 编者注 · 预计在假期期间，更年轻玩家的比例会增加。”【本访谈在假期前进行。——编者注】“一般来说，年长玩家对系列更熟悉，而年轻玩家则是新接触。然而
- 2011-03-01-interview-nintendo-power-bw-masuda-sugimori.md · 注： · Dr Lava 注：尽管《黑／白》是第一款提供通过 Wi-Fi 交换和对战的宝可梦游

### 4.4 译文段内只有 ※，没有 `note`（224 段，59 篇）
多数是原作的 ※ 附注（例如「※ 画面为开发中内容」），需要人工判断是否升格为 `note`。
- 1997-05-23-interview-famimaga-tajiri-pokemon2-secret.md · ※ · 12月15日号提及的内容外，文章内还介绍了战斗、捕获以及道馆馆主。 ※ 如果是隔周发行的FamiMaga，96年3月8日号的发售日是2月
- 1997-05-23-interview-famimaga-tajiri-pokemon2-secret.md · ※ · 介绍，在主要采访中，田尻主要讲述了宝可梦的开发故事和对续作的热情。 ※ 杉森也参加了采访，但发言较少，编辑部评论称其“温和守护着田尻先生
- 1997-05-23-interview-famimaga-tajiri-pokemon2-secret.md · ※ · 息。编辑部通过传真向田尻提问，田尻以此方式手书回答了8大核心问题。（※ 本篇手书传真全8问一问一答完整双语译文已作为独立 Article
- 1997-05-23-interview-famimaga-tajiri-pokemon2-secret.md · ※ · 不看的人，自己玩的时候，如果不看那些就无法推进游戏，会相当焦躁呢。 ※ 以下省略，关于“亲切设计”，增田先生和森本先生也各自发表了看法。
- 1997-05-23-interview-famimaga-tajiri-pokemon2-secret.md · ※ · ※ 以下省略，关于“亲切设计”，增田先生和森本先生也各自发表了看法。
- 2000-01-01-interview-2000-01-01-sunanohi-pokemon-game-kaigi.md · ※ · 《游戏会议》 Vol.9 1997年8月20日发行 ※第2页及以后
- 2004-09-01-interview-nom-emerald-battle-frontier-evolution.md · ※ · 《宝可梦 皮卡丘》《金·银》《水晶版》，这些软件之间可以互相通信。 ※只有《宝可梦 水晶版》支持 Mobile System GB（现已
- 2004-09-01-interview-nom-emerald-battle-frontier-evolution.md · ※ · 1日）／——／欧雷地区／可用 GBA 连接线与 GBA 卡带通信。 ※GBA 软件《火红》《叶绿》分别是把《红·绿》改编到 Game B
- 2004-09-01-interview-nom-emerald-battle-frontier-evolution.md · ※ · 22日），观影人数竟达364万人！厉害！顺便一提，电影的特别预售券（※）附带“极光票兑换券”，曾有机会在《宝可梦 火红·叶绿》里获得电影
- 2009-09-18-interview-dengeki-hgss-shigeki-morimoto.md · ※ · 关于《金·银》的重制，由于《钻石·珍珠》中出现了蜜柑（※1），这在粉丝之间成为了话题。在制作《钻石·珍珠》的阶段，就已经有
- 2009-09-18-interview-dengeki-hgss-shigeki-morimoto.md · ※ · 只。游戏中的跟随行走图形虽然有点难，但在“宝可步数计”里，连晃晃斑（※2）的花纹差异都能正确再现哦。
- 2009-09-18-interview-dengeki-hgss-shigeki-morimoto.md · ※ · 当然也谈到了那些要素。在这样的讨论中诞生的，比如取代“口袋皮卡丘”（※3）的“宝可步数计”。“宝可步数计”是通过红外线在游戏软件端获得道
- 2009-09-18-interview-dengeki-hgss-shigeki-morimoto.md · ※ · 不能做点什么这样的“附加价值”，这时《走一走就明白 生活节奏DS》（※4）发售了。看到那个的时候，我就想如果用它来重现“口袋皮卡丘”，是
- 2009-09-18-interview-dengeki-hgss-shigeki-morimoto.md · ※ · ※4……2008年11月1日由任天堂发售的软件。同捆有计量步数的“生
- 2009-09-18-interview-dengeki-hgss-shigeki-morimoto.md · ※ · 在过去官方大会中，能使用传说的宝可梦的，我想只有2004年的三重奏（※5），我有点担心会不会像那时一样对战平衡被打破……。
- 2009-09-18-interview-dengeki-hgss-shigeki-morimoto.md · ※ · ※5……使用《红宝石·蓝宝石》进行的双打对战大会。采用淘汰赛（所谓的
- 2010-09-13-interview-weekly-ascii-masuda-bw-secrets.md · ※ · ※画面为开发中内容。
- 2010-09-13-interview-weekly-ascii-masuda-bw-secrets.md · ※ · ※画面为开发中的内容。
- 2010-09-13-interview-weekly-ascii-masuda-bw-secrets.md · ※ · ※画面为开发中内容。
- 2010-09-13-interview-weekly-ascii-masuda-bw-secrets.md · ※ · (※2)宝可梦世界锦标赛●使用游戏软件决定“宝可梦对战”世界第一的官方
- 2010-09-13-interview-weekly-ascii-masuda-bw.md · ※ · 最初考虑3对3的“三打对战”时，是因为看了“宝可梦世界锦标赛”(※2)，心想“能不能让比赛更加热烈呢？”。比如，增加“双打对战”的世
- 2010-09-13-interview-weekly-ascii-masuda-bw.md · ※ · (※1)三枝成彰●作曲家。东京音乐大学教授。担任社团法人日本音乐著作权
- 2010-11-01-interview-nintendo-joshi-daisei-bw-kiritani-masuda.md · ※ · 输掉之后灰头土脸重来确实很让人懊恼。另外还可以去大竞技场（※8）挑战。是在哪座城市来着……
- 2010-11-01-interview-nintendo-joshi-daisei-bw-kiritani-masuda.md · ※ · 最后，我们来挑战一下实机视讯通话‘即时通’（※16）吧！
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 请多关照。 ※1 宝可梦中心TOKYO＝位于东京滨松町的官方商店，销售《宝可梦》
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 初次见面。我是担任《宝可梦 黑·白》总监的GAME FREAK（※2）的增田。
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 我是担任美术总监的杉森。 ※2 GAME FREAK＝开发《宝可梦》系列等游戏软件的开发公司。
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 次的《宝可梦 黑·白》，故事主题和以往不同吧。以往都是“因为火箭队（※3）做坏事，所以战斗并打倒他们”这样的流程，但这次是“解放宝可梦”
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 样的模式也不太好……反而想创造一个“极其喜欢宝可梦的家伙”。那就是（※4），他极端地爱着宝可梦。像这样，当把敌人的立场与以往180度转变
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 合众地区右侧的区域（※5）你都去过了吗？
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 去过了。 ※5 右侧区域＝通关主线后首次可以到访的区域。
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 和四天王（※7）再战的话等级就会提升哦。 ※7 四天王＝宝可梦联盟中四位强大的
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 输了还要反复打，确实很不甘心呢。还有就是挑战大竞技场（※8）。是哪个城市来着……
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 我很喜欢飞云市和雷文市（笑）。※8 大竞技场＝位于雷文市的体育巨蛋。每天可以更换训练家进行对战。
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 啊，雷吉奇卡斯是在《钻石·珍珠》中登场的“雷吉”洛克（※9）等“雷吉”这个词上，加上了意为巨人的“奇卡斯”。
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 其实通信功能，我还没用惯呢。C装置（※10）不太会用……。 ※10 C装置＝推进《宝可梦 黑·白》后可在
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 瞬间交错日志（※11），你在用吗？
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 擅长，不管读多少遍说明书都搞不懂，觉得自己肯定不行，所以就没去弄。 ※11 瞬间交错日志＝在游玩《宝可梦 黑·白》时，与周围的玩家进行瞬
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 桐谷小姐，你去过白森林（※12）吗？ ※12 白森林＝在《宝可梦 白》中通关后可以前往的城镇
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 用连入（※13）的功能增加居民后，就会变得热闹起来哦！
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 连入我也完全没体验过。 ※13 连入＝可以与其他玩家的世界往来的功能。和对方世界的居民搭话，
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 机会难得，要不要来黑色市（※14）看看？ ※14 黑色市＝在《宝可梦 黑》中通关后可以前往的城
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 嗯。首先得完成一个任务（※15）才行。 ※15 任务＝在连入中帮助连接的人冒险，或一起游玩。
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 最后来挑战一下即时通讯器（※16）吧。
- 2010-12-24-interview-nintendo-joshidaisei-masuda-sugimori-bw.md · ※ · 即时通讯器！ 【启动即时通讯器】 ※16 即时通讯器＝如果用DSi、DSi LL游玩，朋友之间最多4人
- 2011-06-16-interview-iwata-asks-pokedex-3d-bw-chapter-4-ambition-for-all.md · ※ · 好的……啊对了对了！关于那款《超级宝可梦乱战》的早期购入特典（※13），当时我们商量着想附赠点什么独家赠品……
- 2012-11-22-interview-iwata-asks-gates-to-infinity-chapter-3-definitive-edition.md · ※ · 受故事的游玩、寻找圆形物体进行冒险的游玩、大家协作的游玩、擦肩通信（※15）的游玩，总之加入了各种各样的要素。因此作为“决定版”，我认为
- 2013-10-08-interview-4gamer-2013-solitiba.md · ※ · 嗯，3个人里的一之濑（※1）算是相当老资格了。从制作《宝可梦 红·绿》的时候起就在公司，所
- 2013-10-08-interview-4gamer-2013-solitiba.md · ※ · ※1 一之濑刚（いちのせごう）：GAME FREAK 开发部 声音设
- 2013-10-08-interview-4gamer-2013-solitiba.md · ※ · ※2 田尻智（たじりさとし）：GAME FREAK的代表董事社长。作
- 2013-10-08-interview-4gamer-2013-solitiba.md · ※ · 这次担任总监的田谷（※3）也差不多有10年了吧？
- 2013-10-08-interview-4gamer-2013-solitiba.md · ※ · ※3 田谷正夫（たやまさお）：GAME FREAK 开发部 程序员。
- 2013-10-08-interview-4gamer-2013-solitiba.md · ※ · 是啊，我觉得差不多就是这样。剩下的一个人小幡（※4）还相当年轻。
- 2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras.md · ※ · 确实如此。比如说，宝可梦的叫声并没有采用普通的PSG（※）用法。我是自己编写程序来扭曲PSG的波形，从而表现出那些叫声的，
- 2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras.md · ※ · （※）PSG……一种生成声音的电子电路。在游戏中，被用于红白机、Gam
- 2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras.md · ※ · 蓝宝石》并因此喜欢上其中音乐的人，会表示自己非常喜欢PSG与PCM（※）混合在一起的声音。从《宝可梦 红宝石·蓝宝石》开始接触这个系列的
- 2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras.md · ※ · （※）PCM……一种生成声音的电子电路。在游戏中，被用于Game Bo
- 2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras.md · ※ · 确实是这样！当齐藤先生跟我说想在演唱会上演奏（※）的时候，我还以为他在开玩笑呢（笑）。因为那是个下载专用游戏，我还
- 2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras.md · ※ · （※）现场演奏……在2013年除夕举办的2083主办现场演出“Deep
- 2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras.md · ※ · 玩家的反响也非常热烈，而且在“2083研讨班”（※）中，《纸牌跑马》还被选为“2083研讨班评选的年度游戏音乐！”第
- 2014-10-31-interview-2083-gamefreak-sound-team-red-green-to-oras.md · ※ · （※）2083研讨班……由2083齐藤担任代表的游戏音乐研究团体。虽然
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · 是在新宿的游戏中心呢。我记得，《GAME FREAK》创刊号（※）做了《铁板阵》的特辑时，我就已经知道他了。当时风营法还没修订，游
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · 本同人志确实很显眼。因为连音乐家细野晴臣先生和宗教学者中泽新一先生（※）都买过。中泽先生当时从文化人类学的角度为游戏的新颖性辩护过。那对
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · 玩呢”之类的话，信息就这样通过口口相传扩散开来。另外，街机厅笔记本（※）的存在也很重要。我记得那大概是82年或83年出现的吧。
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · ……也就是说，《迷宫塔》（※）是以当时的街机厅文化为前提制作的吧（笑）。
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · 时候，街机厅笔记本就已经存在了。但《铁板阵》的情况是，うる星あんず（※）制作攻略本的速度实在太快了。
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · 这些机械的设计者是现在还在搞“远山式立体显示法”的远山茂树君（※）。他现在依然活跃，真是个出色的设计师。我做的开发版本为了对外发布
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · 自命不凡的人，觉得“他们在做无聊的东西”。因为动画界里，富野由悠季（※）已经推出了《高达》。尽管如此，当时游戏里的机器人却尽是红白蓝、像
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · 嘛，结果来说，那是非常正确的选择。南梦宫对制作的游戏没有设数量限制（※）。如果是其他公司，大概就不会让我们出了吧。
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · ……是啊。我正是从社长（※）和杉森那里直接学到了“GAME FREAK主义”的那一代人，所以
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · ，为什么您一直在玩《大金刚》？”——他回答说：“已故的横井军平先生（※）说过‘北美版的《大金刚》做得完美无缺’，我想亲自验证一下。”
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · 的尝试。而且每次都能成功，这真的很了不起。最近的编号作品是由藤泽君（※）——堀井先生手下的年轻人——负责制作的，他作为导演也很有能力吧。
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · 年龄段里，他可以说是顶尖的吧。年轻一代中，《智龙迷城》的山本大介君（※）能那样打造出爆款作品，也很了不起。不过，如今已经进入了很难看清到
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · 比如，《恶魔之魂》的宫崎英高先生（※）我觉得也是一位才华闪耀的人……
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · 步，取得博士学位才行。我正打算成为第一个这样做的人。这是在饭野贤治（※）去世时，我下定的决心——我要将余生奉献给为这件事正名。
- 2016-02-17-interview-denfami-xevious-tajiri-sugimori-endo.md · ※ · 项技术”，再思考如何将其融入游戏。在我参与过的游戏中，《动物番长》（※）就意识到了这一点。为了体验“大口咬下”那种感觉的震撼，我把它做成
- 2016-02-27-interview-inside-2016-ishihara-20th.md · ※ · (※)田尻智氏
- 2016-02-27-interview-inside-2016-ishihara-20th.md · ※ · ※岩田聪
- 2016-02-27-interview-inside-2016-ishihara-20th.md · ※ · ※在石原也出演的4Gamer.net岩田追悼特辑中，详细讲述了岩田在
- 2016-02-27-interview-inside-2016-ishihara-20th.md · ※ · ※超级碗
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 机正是《德比骏马》及其周边文化。当时，在名为NIFTY-Serve（※）的电脑通信网络上，《德比骏马》的攻略信息和免费工具等非常热闹。我
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ※NIFTY-Serve：1987年至2006年由NIFTY株式会社
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 于是，我买了一台叫FM-7（※）的电脑。当时的电脑非常昂贵，FM-8要20万日元左右，但这款FM
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ※FM-7：富士通发售的8位电脑。作为FM-8的下位机型，削减了功能
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 比骏马》，如果我没有遇到这款游戏，大概不会攒下这么多“JRA银行”（※）的存款（笑）。这只能说是托了薗部先生的福。当然，《宝可骑行》也深
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ※JRA银行：JRA指日本中央竞马会。买了马券却没中，当然会失去钱，
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 100%。“为什么会想到和纸牌结合起来？”（薗部先生）“《高尔夫》（※纸牌游戏的一种，《宝可骑行》中采用了这一玩法）那种快速判断的乐趣，
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ——《最佳职业棒球》（※）对吧。
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ※《最佳职业棒球》是1988年由ASCII发售的棒球模拟游戏。ASC
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 果然还是很开心。于是又想要挑战，瞄准了艾尼克斯的游戏·爱好程序大赛（※）第2届还是第3届，开始了下一部作品的制作。
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ※游戏·爱好程序大赛：艾尼克斯从1982年开始举办的比赛。奖金总额高
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 是的，至少那时候没有进行正式的开发。不过后来ASCII推出MSX（※1）的时候，作为初期标题做了大约50款。召集了一堆兼职的人，大概一
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 没参与那些。我一个人零零散散地做（笑）。而且MSX用的是“Z80”（※2），FM-7用的是“MC6809”（※3）。所以连语言都不一样。
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ※1 MSX：1983年由美国微软和当时的ASCII共同提出的8位/
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 《昆蒂》了。不过我觉得出版和游戏制作在经验技巧方面有很多共通之处呢（※）。
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ※GAME FREAK的出身 GAME FREAK原本是从游戏攻略的
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 游戏呢。我出的那款叫《牛奶猫》的游戏，在我心里就是模仿《企鹅推砖》（※）做出来的。所以其实我觉得名字叫《喵鹅推砖》更好，但公司说“这也太
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ※《企鹅推砖》 世嘉于1982年发行的动作益智游戏，操控企鹅击败敌人
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 有一年，他兴奋地跟我说有一匹叫小栗帽（※1）的强马。他说还有一匹叫玉藻十字（※2）的 older 马也很强
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ※1 小栗帽——缔造第二次赛马热潮的名马。全盛时期甚至出现了追星族般
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 不一定在有马纪念2500米也很强。但当时我根本不知道“距离适应性”（※）这个概念。最后，我勉强减少了金额，押了足球小子10万日元。
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ※距离适应性：在赛马中，每场比赛都会设定不同的赛程距离，如1000米
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 果却没赶上小栗帽的热潮。最后连6岁小栗帽退役战都没赶上，是在大勇作（※）夺得有马纪念冠军的1991年才发售的。这么一想，整整花了3年多的
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ※大勇作：拥有“史上最强一发屋”异名的赛马。在1991年的有马纪念中
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 我买马券的时候会看血统，如果里面有纳斯鲁拉系（※）的话，就会想“没问题吧？”
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ※纳斯鲁拉：英国生产的种公马。现役赛马时代以极快的速度和暴躁的脾气闻
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 从这个意义上说，我的原点就是《生命游戏》（※）。刚才聊程序的时候忘了说，我写的第一段代码就是这个。
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ※《生命游戏》是1970年由英国数学家约翰·何顿·康威（John H
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · 多关注。我觉得正是那个时候，赛马全新的魅力才被凸显出来。而成泽先生（※）将其挖掘出来这件事，包括其中也有两位计划推动的一面……
- 2016-04-18-interview-denfami-sonobe-gamefreak-morimoto.md · ※ · ※成泽大辅，游戏评论家。从早期开始就撰写了大量《德比骏马》的攻略本，
- 2017-07-03-interview-denfami-ohmori-onoue-gamefreak-heritage.md · ※ · 2001年应届毕业入职，担任策划【※1】。最初制作的是《宝可梦 红宝石·蓝宝石》【※2】。
- 2017-07-03-interview-denfami-ohmori-onoue-gamefreak-heritage.md · ※ · ，在25岁时担任了《宝可梦 钻石·珍珠》（以下简称《钻石·珍珠》）【※3】的策划组长。接着，在《宝可梦 X·Y》（以下简称《X·Y》）【
- 2017-07-03-interview-denfami-ohmori-onoue-gamefreak-heritage.md · ※ · ※1 策划：一般指负责制定企划或计划职位的人。立案者。
- 2017-07-03-interview-denfami-ohmori-onoue-gamefreak-heritage.md · ※ · ※4 《宝可梦 X・Y》：2013年由株式会社宝可梦发售。《宝可梦》
- 2017-07-03-interview-denfami-ohmori-onoue-gamefreak-heritage.md · ※ · 宝可梦 心金／魂银》中负责了「宝可运动」这个小游戏和「宝可计步器」【※1】这个通过行走步数来捕捉宝可梦的企划，在《宝可梦 黑／白》中负责
- 2017-07-03-interview-denfami-ohmori-onoue-gamefreak-heritage.md · ※ · ※2 联合房间：在《宝可梦 黑／白》的舞台「合众地区」中央作为「神秘
- 2017-07-03-interview-denfami-ohmori-onoue-gamefreak-heritage.md · ※ · T》（以下简称《TEMBO》）这款2D横版动作游戏发布到Steam【※】、PS4和Xbox One的项目。虽然这是别人的企划，但程序员有
- 2017-07-03-interview-denfami-ohmori-onoue-gamefreak-heritage.md · ※ · ※Steam：美国游戏公司Valve于2003年开始服务的平台，旨在
- 2017-07-03-interview-denfami-ohmori-onoue-gamefreak-heritage.md · ※ · 过《红·绿》的孩子们长大成人，可能会再次回归。但是，如果还是道馆战【※】的话，新玩家和有经验的玩家之间，无论如何都会在「技术」上产生差距
- 2017-07-03-interview-denfami-ohmori-onoue-gamefreak-heritage.md · ※ · ※道馆战：《宝可梦》系列中登场的几个地区里，训练家挑战的内容。每个地

### 4.5 Markdown 正文里以 ※ 开头的段落（44 篇）
2004–2011 年 GAME FREAK 社长 / 员工博客的译文，※ 是作者本人的附言，属于正文，保留即可，列在这里只为完整。
- 2004-12-27-gamefreak-director-029.md · ※打个音乐方面的比方，就算硬件从唱片变成了ＣＤ，
- 2005-06-03-gamefreak-director-040.md · ※顺带一提，我会从车内广告里构思点子，也会在脑内作曲，
- 2005-08-03-gamefreak-director-048.md · ※「TV remotes」としておきましょう。
- 2007-01-12-gamefreak-director-066.md · ※明天13日（周六）发售的月刊《King》杂志上，会刊登我和GF员工的内容。
- 2007-01-16-gamefreak-director-067.md · ※所以说……本月发售的《Invitation》杂志上有我增田哦——。
- 2007-02-01-gamefreak-director-074.md · ※1月28日（星期日）的《宝可梦星期天》里，GAME FREAK又一次露脸了哦！
- 2007-08-01-gamefreak-art-5.md · ※由于是原案设计，实际使用的角色在<br>
- 2007-11-07-gamefreak-director-113.md · ※现在日本是晚上 7 点，而我这里是凌晨 2 点……
- 2007-11-22-gamefreak-director-115.md · ※这张照片是从我的座位向前拍摄的。
- 2008-02-28-gamefreak-director-125.md · ※这里只放了曲子的一部分，其中还加入了演出时的音效。还请谅解。
- 2008-02-29-gamefreak-director-126.md · ※这个波形是帝牙卢卡的叫声。波形大概会呈现出这种感觉。
- 2008-02-29-gamefreak-staff-60.md · ※这是在任天堂之前于北美发售的、可以更换卡带的家用游戏机。<br>
- 2008-05-16-gamefreak-director-127.md · ※也请大家务必通过电影预售票拿到雷吉奇卡斯，在电影院拿到谢米，
- 2008-06-02-gamefreak-director-128.md · ※只要能参加预选赛（洛杉矶或纽约）和正式比赛，哪个国家的人都可以！
- 2008-06-27-gamefreak-director-129.md · ※Sorry, this promotion will be held only in Japan…
- 2008-08-01-gamefreak-art-6.md · ※由于是原案设计，和实际使用的角色在<br>
- 2009-03-12-gamefreak-director-141.md · ※在最初阶段，其实还没有图鉴、属性、钓鱼、和朋友对战等许多要素。
- 2009-03-13-gamefreak-director-142.md · ※我之前还说过，自己绝对会把“执行制作人”这个词说得磕巴，
- 2009-03-17-gamefreak-director-143.md · ※啊，我还去了金门大桥！
- 2009-08-03-gamefreak-art-7.md · ※由于是原案设计，和实际使用的角色在<br>
- 2009-10-01-gamefreak-staff-146.md · ※报名请通过[招聘网站2011](http://job.rikunabi.com/2011/comp
- 2009-11-16-gamefreak-director-152.md · ※前几天我去了宝可梦中心东京，看到CD整齐地摆在那里，着实有点感动。
- 2009-11-27-gamefreak-director-154.md · ※如果你还没看过《星际迷航》，
- 2010-05-14-gamefreak-staff-182.md · ※这张照片只是为了营造效果，卡斯特拉蛋糕已经由工作人员美味地享用了。
- 2010-05-29-gamefreak-director-161.md · ※可以通过“SELECT　LANGUAGE”切换语言！声音也很帅气！
- 2010-07-28-gamefreak-director-166.md · ※能够在电影中领取宝可梦的，是所有可以在 DS 上游玩的宝可梦软件！
- 2010-08-04-gamefreak-director-171.md · ※这种情况，换作任何人，绝对都会紧张的！！
- 2010-08-06-gamefreak-art-8.md · ※由于是原案设计，实际使用的角色在<br>
- 2010-08-06-gamefreak-staff-194.md · ※爬富士山其实相当艰苦，真的不能抱着这么轻松的心态去。<br>
- 2010-09-01-gamefreak-director-174.md · ※远处那些看起来像小颗粒的东西……是人！！
- 2011-01-14-gamefreak-staff-215.md · ※不过因为还是初学者，所以没能在海里拍照。真遗憾！
- 2011-04-25-gamefreak-director-191.md · ※韩国活动的情况，我会整理好照片后写在下一篇专栏里。
- 2011-08-01-gamefreak-art-226.md · ※由于是原案设计，和实际使用的角色在<br>
- 2011-08-08-gamefreak-director-201.md · ※游戏中不需要在船上表现缆绳（不会显示）。
- 2011-08-09-gamefreak-director-202.md · ※内容来自 Creatures 公司的博客。
- 2011-08-25-gamefreak-director-207.md · ※主要用色彩来表现当季蔬菜。
- 2012-03-06-gamefreak-director-224.md · ※其中有些照片有点模糊、、、
- 2013-01-24-gamefreak-director-234.md · ※日语读法为「哲尔尼亚斯」　「伊裴尔塔尔」
- 2013-02-05-gamefreak-director-235.md · ※■”Pokémon Dream Radar” Game flow
- 2016-04-02-gamefreak-lineblog-2502729.md · ※听说最终参加人数一共200人，
- 2016-04-29-gamefreak-lineblog-2777075.md · ※读过<a class="gf-lineblog-source-link" href="http:/
- 2016-05-22-gamefreak-lineblog-3606850.md · ※这张照片来自2015年横滨皮卡丘大量发生中
- 2016-05-24-gamefreak-lineblog-3670399.md · ※我试着把肉以外的地方调暗了（笑）
- 2016-08-12-gamefreak-lineblog-5460146.md · ※如需咨询

## 误报与未纳入的检查

- `gf-director-translation-note`（244 篇）：校对说明块，`_sass/minimal-mistakes/_gamefreak-director.scss:1077` 设了 `display: none`，读者看不到，不算问题。
- 「广告」「上一篇 / 下一篇」等站点残留：命中都是正文里的真实用语（如「电视广告」「上一篇员工博客」），不计入。
- 「！！」「！！！」：博客作者的文风，不计入。
- 标签「宝可梦」不在正文里：GAME FREAK 社长博客本身不谈宝可梦，这是站点分类标签，不计入。
- 实体（people / works / organizations）与正文对不上的约 1400 条，多数是中日文写法不同导致的字符串不匹配，无法直接判断对错，未纳入结论。
- `&lt;` / `&amp;` 等实体（lineblog 约 15 篇）：渲染正常，不计入。

## 建议的处理顺序

1. 先修 YAML：给 2.1 的 5 篇 `ISBN:` / `JAN:` 值加引号，这是唯一会让整篇内容失效的问题。
2. 修摘要：1.1、1.2、1.3 直接写新摘要；1.4 补全句子。
3. 把 4.1、4.2 的注释移到 `note` 字段，4.3 逐条核对去重。
4. 标签：统一 3.5 的写法；3.2 的日文词、3.3b 的原文 hashtag 译成中文或删除；3.3 的英文专名按站内写法统一；3.1 补标签。
5. 排版：2.2 的标题补空格，2.4 替换占位图，2.6 挪走误放文件，2.3 的单换行逐篇合并段落。

