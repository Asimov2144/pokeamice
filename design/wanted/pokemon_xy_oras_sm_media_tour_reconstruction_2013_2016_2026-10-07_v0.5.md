# Pokémon X/Y–ORAS–Sun/Moon 访谈与 2016 全球媒体巡回复原

> 阶段性研究档案 v0.3  
> 日期：2026-10-07  
> 范围：2013–2016  
> 用途：PokeAmice Wanted / Interview Archive / 实体杂志扫描征集

## 1. 2016 Sun/Moon 全球媒体巡回：官方锚点

増田順一的同期记录明确给出两段媒体活动：

- **London：24 家媒体**，来自英国、德国、法国、意大利、荷兰等欧洲国家。
  - 2016-09-28：https://docs.pokeamice.com/gamefreak-director/lineblog-7558415/
  - 2016-10-01：https://docs.pokeamice.com/gamefreak-director/lineblog-7651386/
- **San Francisco：12 家媒体**，在 Nintendo San Francisco office 两天完成。
  - 2016-10-05：https://docs.pokeamice.com/gamefreak-director/lineblog-7840175/
- London + San Francisco = **36 家媒体**。
- 之后 12 月还有 Spain / Portugal 宣传行程，应与这 36 家分开。
  - 年末回顾：https://docs.pokeamice.com/gamefreak-director/lineblog-9252218/

建议结构：

```yaml
series_id: SM_2016_GLOBAL_MEDIA_TOUR
participants: [Junichi Masuda, Shigeru Ohmori]
events:
  - id: SM_2016_LONDON_PRESS
    media_count: 24
    dates: 2016-09-28..2016-10-01
  - id: SM_2016_SAN_FRANCISCO_PRESS
    media_count: 12
    dates: 2016-10-04..2016-10-05
official_total_media: 36
```

### 验证状态

- `CONFIRMED_LOCATION`：原文明确写 London / San Francisco。
- `HIGH_CONFIDENCE_EVENT`：媒体自己的采访，时间、人物与 embargo 高度吻合，但原文未写地点。
- `DIRECT_INTERVIEW_LOCATION_UNKNOWN`：确定为该媒体自己的采访，但暂不能归入 London 24 / SF 12。
- `SECONDARY_ONLY`：转载，不计入 36 家。
- `CANDIDATE`：仍需进一步证明。

---

## 2. San Francisco 12：当前恢复

| 媒体 | 当前判断 | 证据 |
|---|---|---|
| GameSpot | **CONFIRMED_LOCATION** | 原文明确写 Nintendo San Francisco office |
| Game Informer | HIGH_CONFIDENCE_EVENT | 2016-10-19 自采长访 |
| TIME | HIGH_CONFIDENCE_EVENT | 2016-10-19 Masuda × Ohmori transcript |
| USgamer | HIGH_CONFIDENCE_EVENT | 自采 Ohmori / Masuda |
| GamesRadar | HIGH_CONFIDENCE_EVENT | 2016-10-19 视频/文字采访 |
| Eurogamer | HIGH_CONFIDENCE_EVENT | 同日开发者视频采访 |
| GameXplain | HIGH_CONFIDENCE_EVENT | 自采视频 |
| Kotaku | DIRECT_INTERVIEW_LOCATION_UNKNOWN | 电话采访；是否计入 SF 12 未定 |

### GameSpot

主访谈：  
https://www.gamespot.com/articles/pokemon-sunmoon-devs-on-legendaries-pokemon-go-and/1100-6444620/

同一 session 拆稿：  
https://www.gamespot.com/articles/pokemon-go-connection-with-sunmoon-is-still-in-the/1100-6444589/

两篇应算 **1 家媒体 / 1 次 session**。

### Game Informer

https://gameinformer.com/b/features/archive/2016/10/19/burning-questions-for-pokemon-sun-and-moon.aspx

网页采访已确认；纸本是否刊载及页码仍需核验。

### TIME

https://time.com/4536438/pokemon-sun-moon-interview/

### GamesRadar

https://www.gamesradar.com/heres-everything-pokemon-sun-moons-director-told-us-about-z-moves-the-12-hour-delay-and-life-itself/

### Eurogamer

同期引用：  
https://www.nintendolife.com/news/2016/10/the_masuda_method_lives_on_in_pokemon_sun_and_moon

### GameXplain

https://www.youtube.com/watch?v=ght1eKVl070

### Kotaku

https://kotaku.com/asked-for-their-favorite-even-pokemon-sun-and-moons-cr-1787943425  
https://kotaku.com/the-creators-of-pokemon-explain-why-sun-and-moon-has-ri-1788191518

PokeAmice：  
https://docs.pokeamice.com/%E8%AE%BF%E8%B0%88%E7%BF%BB%E8%AF%91/%E7%BF%BB%E8%AF%91/%E8%AE%BF%E8%B0%88%E6%95%B4%E7%90%86/interview-kotaku-2016-designs/

---

## 3. London 24：国家矩阵

### UK / Europe

**Nintendo of Europe** — 同一次采访的多语言本地化只能算 1 家媒体。

- Quick-fire Q&A  
  https://www.nintendo.com/en-gb/News/2016/October/Is-there-anything-taller-than-an-Alolan-Exeggutor-Find-out-in-our-exclusive-Pokemon-Sun-and-Pokemon-Moon-interview--1148574.html
- In-depth interview  
  https://www.nintendo.com/en-gb/News/2016/October/Learn-all-about-Pokemon-Sun-and-Pokemon-Moon-in-our-in-depth-interview-1149779.html

荷兰语本地化示例：  
https://www.nintendo.com/nl-nl/Nieuws/2016/oktober/Kom-alles-te-weten-over-Pokemon-Sun-en-Pokemon-Moon-in-ons-uitgebreide-interview-1149779.html

**GamesMaster #310 / December 2016**

Zinio：  
https://www.zinio.com/es-ca/publications/gamesmaster/2091/issues/347468

目录可确认 Sun/Moon 专题从 **p.44** 开始，共 **10 页（pp.44–53）**，说明包含 developer interviews。具体采访子页仍待核验。

**gamesTM**

采访存在确认：  
https://nintendoeverything.com/pokemon-sunmoon-devs-on-the-drip-feed-of-news-updates-fan-theories-thoughts-on-hardware-more/

Siliconera 同期引用：  
https://www.siliconera.com/pokmon-sun-moon-devs-fan-theories-main-series-stays-handhelds/

具体 issue 仍待确认。

### Germany

**GamePro**

https://www.gamepro.de/artikel/pokemon-sonne-mond-das-neue-rpg-will-alte-fans-ueberraschen%2C3304185.html

自采 Masuda × Ohmori，时间与 London event 高度吻合。

**N-Zone #235 / November 2016**

二手长篇转述：  
https://nintendoeverything.com/pokemon-sun-moon-director-on-poke-ride-time-difference-sidequests-coming-up-with-new-pokemon-more/

期号高度指向 #235；页码待原刊。

### France

**Gameblog — CONFIRMED_LOCATION: London**

https://www.gameblog.fr/jeu-video/ed/dossier_page/96150-1-99303

原文明确写采访在 The Pokémon Company London offices。

**Jeuxvideo.com**

https://www.jeuxvideo.com/news/554183/pokemon-soleil-lune-une-compatibilite-smartphone-ou-nx-nous-allons-continuer-a-nous-developper-aux-cotes-de-nintendo.htm

**La Crème du Gaming**

https://www.lacremedugaming.fr/non-classe/pokemon-soleil-lune-junichi-masuda-et-shigeru-ohmori-nous-donnent-un-max-de-details-50171.html

### Italy

**La Repubblica — CONFIRMED_LOCATION: London**

https://www.repubblica.it/tecnologia/2016/11/14/news/la_sgaga_infinita_dopo_poke_mon_go_ecco_luna_e_sole-302638548/

文章场景指向 The Pokémon Company International HQ, Chiswick, London。

### Spain

**EL PAÍS Tecnología**

https://elpais.com/tecnologia/2016/11/24/actualidad/1480002797_209718.html

属于 London interview 的强证据。

MeriStation 已知采访应优先归入之后的 Spain / Portugal 行程，而非 London 24：  
https://docs.pokeamice.com/interview-meristation-sun-moon-switch-masuda-ohmori/

### Netherlands

**Power Unlimited — HIGH-CONFIDENCE candidate**

2016-10-19 荷兰 Tweakers 讨论把 PU interview 与 GameXplain interview 一起称为当天 embargo 解禁的 Masuda / Ohmori 采访：  
https://gathering.tweakers.net/forum/list_messages/1699321/8

原 PU.nl 页面仍需恢复。

---

## 4. 当前 36 家恢复进度

### London 24

当前 confirmed / high-confidence：

1. Nintendo of Europe
2. Gameblog
3. Jeuxvideo.com
4. La Crème du Gaming
5. GamePro
6. N-Zone
7. La Repubblica
8. EL PAÍS Tecnología
9. GamesMaster
10. gamesTM
11. Power Unlimited

候选：

- Digital Spy（尚缺强证据）

### San Francisco 12

当前 confirmed / high-confidence：

1. GameSpot
2. Game Informer
3. TIME
4. USgamer
5. GamesRadar
6. Eurogamer
7. GameXplain

另有：

- Kotaku：直接电话采访，但地点/是否计入 12 未定

即目前已经能点名约 **18 个独立媒体组织**，但其中若干 event affiliation 仍需强化。

---

# 5. 2013 X/Y 实体杂志

## Nintendo DREAM Vol.235

- 发售：2013-09-21
- 52 页 A5《Nintendoスタジアム》复活别册
- 卷首：**Junichi Masuda × Shigeki Morimoto Long Interview**
- 采访页码：待确认
- 状态：`SCAN_WANTED`

官方：  
https://www.nindori.com/books/nindori/235.html

## Nintendo DREAM Vol.236

- XY Character Design Interview
- 涉及主人公、Shauna、Tierno、Trevor、Professor Sycamore、Gym Leaders 等
- 完整 interviewees / 页码待原刊
- 状态：`SCAN_WANTED`

官方：  
https://www.nindori.com/books/nindori/236.html

## 週刊ファミ通 2013年10月24日号

- 实际发售：2013-10-10
- 増田順一发售直前 Interview
- 页码待确认

https://www.famitsu.com/news/201310/10041343.html

## 週刊ファミ通 2013年11月7・14日合併号

- 实际发售：2013-10-24
- XY 专题共 **9 页**
- 包含 design key-person interview
- Interview 子页待确认

https://www.famitsu.com/news/201310/24042079.html

## XY 官方完全攻略本

Overlap 官方明确包含 **増田順一 Long Interview**：  
https://over-lap.co.jp/book/xy/

状态：`BOOK_CONFIRMED`

---

# 6. 2014–2015 ORAS 实体杂志

## 週刊ファミ通 2014年12月4日増刊号

- ORAS 发售期
- 附 **52 页「冒険ナビBOOK」**
- 册子明确包含 Developer Staff Interview
- 52 页是整个 supplement，不是采访长度
- Interview 子页待确认

https://www.famitsu.com/news/201411/18065949.html  
https://www.famitsu.com/news/201411/20066095.html

## Nintendo DREAM Vol.250

- 发售：2014-12-20
- ORAS Sound Interview
- 増田順一 + development staff
- 页码待确认

https://www.nindori.com/books/nindori/250.html

## Nintendo DREAM Vol.254

- 发售：2015-04-21
- 受访：
  - Shigeru Ohmori
  - Ken Sugimori
  - Shigeki Morimoto
  - Kazumasa Iwao
- 主题：Design / Battle
- 页码待确认
- ORAS 当前最高价值 Wanted 之一

https://www.nindori.com/books/nindori/254.html

---

# 7. 2016 Sun/Moon 日本与欧洲纸本

## 週刊ファミ通 2016年7月28日号

- 实际发售：2016-07-14
- Junichi Masuda × Shigeru Ohmori
- SM 发售前 Interview
- 页码待确认

https://www.famitsu.com/news/201607/14110808.html

## 週刊ファミ通 2016年12月1日号

- 实际发售：2016-11-17
- **14 页 SM 特集**
- 含 Masuda × Ohmori 开发采访
- Interview 子页待确认

https://www.famitsu.com/news/201611/15120668.html

## N-Zone #235

- cover date：2016-11
- release：约 2016-10-19
- Masuda × Ohmori
- 页码待确认
- `SCAN_WANTED`

https://nintendoeverything.com/pokemon-sun-moon-director-on-poke-ride-time-difference-sidequests-coming-up-with-new-pokemon-more/

## GamesMaster #310

- December 2016
- Sun/Moon feature：**pp.44–53**
- 明确含 developer interviews
- interview 子页待确认

https://www.zinio.com/es-ca/publications/gamesmaster/2091/issues/347468

## gamesTM

- Masuda × Ohmori interview 已确认
- issue / pages 待锁定

https://nintendoeverything.com/pokemon-sunmoon-devs-on-the-drip-feed-of-news-updates-fan-theories-thoughts-on-hardware-more/

## Spanish Official Nintendo Magazine

部分原页照片已恢复：  
https://lavacutcontent.com/masuda-ohmori-pokemon-gray/

主题包括 Pokémon Gray / Pokémon Z / Colosseum sequel。

更可能属于 2016 年 12 月 Iberia tour，不应自动算入 London 24。

---

# 8. Wanted 首批新增建议

### S 级

1. Nintendo DREAM Vol.235
2. Nintendo DREAM Vol.236
3. Famitsu 2013-10-24
4. Famitsu 2013-11-7/14
5. Nintendo DREAM Vol.250
6. Nintendo DREAM Vol.254
7. Famitsu 2014-12-4 増刊 / ORAS 52p supplement
8. N-Zone #235
9. GamesMaster #310
10. gamesTM（issue pending）

### A / 原始出版物较容易追

11. XY 官方攻略本
12. ORAS 官方攻略本
13. Famitsu 2016-7-28
14. Famitsu 2016-12-1

### Partial

15. Spanish Official Nintendo Magazine — partial original pages recovered

---

# 9. 去重规则

- Nintendo Europe 多语言本地化：**count = 1**
- GameSpot 长访 + Pokémon GO 拆稿：**count = 1**
- Kotaku 同一电话采访拆两篇：**count = 1**
- Nintendo Everything / Siliconera 等二手转述：**count = 0**
- 不同媒体在同一个 press day 各自采访：媒体各自计数，但共享 event/session 上层节点

---

# 10. 下一轮国家矩阵

London：

```text
UK: GamesMaster / gamesTM / Digital Spy / Nintendo Life / IGN UK
Germany: GamePro / N-Zone / PC Games / Spieletipps / IGN DE
France: Gameblog / Jeuxvideo.com / La Crème du Gaming / Gamekult / JeuxActu
Italy: La Repubblica / Multiplayer.it / Everyeye / IGN Italia
Netherlands: Power Unlimited / Gamer.nl / IGN Benelux / Tweakers
Spain: EL PAÍS / Vandal / 3DJuegos / Hobby Consolas / IGN España
```

San Francisco / North America：

```text
GameSpot / Game Informer / TIME / USgamer / GamesRadar / Eurogamer /
GameXplain / Kotaku / IGN / Polygon / The Verge / Destructoid /
Shacknews / RPG Site / Nintendo World Report
```

检索原则：

> 只有找到 “we interviewed / we spoke with / our interview / sat down with Masuda and Ohmori” 等直接证据，才将媒体升为 direct interview。

---

# 11. 当前研究目标

1. London 24：从当前约 11 家提升到 18–20 家。
2. SF 12：从当前约 7 家提升到 10–12 家。
3. 给所有 2013–2016 纸本目标补齐精确 interview page range。
4. 找到可公开访问的整刊扫描、官方电子版、图书馆或二手书目入口。
5. 将 `article`、`media outlet`、`interview_session`、`press event` 四层拆开，避免媒体拆稿和多语言版本造成虚增。



---

# 12. 国家矩阵第二轮更新（v0.2）

本轮重点不是继续增加“提到 Pokémon 的网页”，而是确认：

1. 媒体是否真的亲自采访了増田順一 / 大森滋；
2. 是否能归入 London 24 或 San Francisco 12；
3. 是否只是同一次采访的拆稿 / 本地化 / 二手转载；
4. 是否存在实体杂志版本以及可取得的数字原刊。

---

## 12.1 London 24：当前恢复到约 12 家强候选

当前可以列为 `CONFIRMED_LOCATION` 或 `HIGH_CONFIDENCE_EVENT` 的独立媒体组织：

| # | 媒体 | 国家 | 状态 | 备注 |
|---:|---|---|---|---|
| 1 | Nintendo of Europe | Europe / UK | DIRECT | 多语言本地化只算 1 家；是否被官方“24家媒体”计数仍待确认 |
| 2 | Gameblog | France | **CONFIRMED_LOCATION** | 原文明确写 The Pokémon Company London offices |
| 3 | Jeuxvideo.com | France | HIGH_CONFIDENCE_EVENT | 自采 Masuda × Ohmori |
| 4 | La Crème du Gaming | France | HIGH_CONFIDENCE_EVENT | 2016-10-19 自采 |
| 5 | GamePro | Germany | HIGH_CONFIDENCE_EVENT | 自称到 TPCI 采访，日期与 London event 一致 |
| 6 | N-Zone | Germany | HIGH_CONFIDENCE_EVENT | 实体杂志采访；高度指向 #235 |
| 7 | La Repubblica | Italy | **CONFIRMED_LOCATION** | 原文明确写 Chiswick, London 的 TPCI HQ |
| 8 | EL PAÍS Tecnología | Spain | **CONFIRMED_LOCATION** | 文章场景在 London |
| 9 | GamesMaster | UK | HIGH_CONFIDENCE_EVENT | #310，Sun/Moon pp.44–53，含 developer interviews |
| 10 | gamesTM | UK | HIGH_CONFIDENCE_EVENT | Masuda × Ohmori 自采；issue 高度指向 #180 |
| 11 | Power Unlimited | Netherlands | HIGH_CONFIDENCE_EVENT | 同期论坛保存原 PU 自采 URL |
| 12 | Hobby Consolas | Spain | HIGH_CONFIDENCE_EVENT | #305 在 Spain tour 之前已上市，纸本已有 Masuda × Ohmori interview |

因此：

```text
London strong media candidates = 12
official total = 24
```

严格计数时要注意：

> Nintendo of Europe 是否属于増田所说的 24 家“media”仍未完全证明。

所以更保守可以写成：

```text
11–12 / 24
```

---

# 13. 新确认：Hobby Consolas #305

这是第二轮最重要的实体杂志发现之一。

## 13.1 纸本采访存在确认

Hobby Consolas 自己在 2021 年回顾 Pokémon 历史时明确写：

> 第 305 期刊载了 Shigeru Ohmori 与 Junichi Masuda 的采访。

回顾：

https://www.hobbyconsolas.com/reportajes/pokemon-hobby-consolas-25-anos-haciendonos-todos-nos-queda-957125

当期发售公告：

https://www.hobbyconsolas.com/noticias/hobby-consolas-numero-305-venta-pokemon-portada-75244

公告发布日期：

> **2016-12-01**

公告当时已经写：

> “hemos podido hablar con sus creadores”

也就是该纸本采访在 12 月 1 日之前已经完成。

## 13.2 为什么它很可能属于 London press event

増田 / 大森真正的 Spain / Madrid 宣传访问发生在 **12 月 6 日以后**。

Hobby Consolas 的 Madrid 网站采访发布日期：

> 2016-12-08

并明确说：

> “están de visita en España”

链接：

https://www.hobbyconsolas.com/reportajes/pokemon-sol-luna-entrevista-masuda-ohmori-creadores-83312

视频：

https://www.youtube.com/watch?v=LbvCUq6GQCw

因此：

- **Hobby Consolas #305 纸本采访**：12/1 已上市，不可能来自 12/8 Madrid 会面；
- **Hobby Consolas web/video 12/8**：是另一场 Spain tour interview。

结合増田明确说 London 24 家包含欧洲媒体，Hobby Consolas #305 高概率是早先的 London press event 产物。

但原刊正文尚未看到地点，因此数据库应写：

```yaml
publication: Hobby Consolas
issue: 305
cover_date: 2016-12
on_sale: 2016-12-01
game: Pokémon Sun / Moon
interviewees:
  - Junichi Masuda
  - Shigeru Ohmori
interview_verified: true
event_affiliation: London_high_confidence
location_verified_from_article: false
pages: pending
```

## 13.3 数字原刊仍可取得

Zinio：

https://www.zinio.com/es/publications/hobby-consolas/1342/issues/19299

PocketMags：

https://pocketmags.com/es/hobby-consolas-magazine/305

因此 Wanted 状态更适合：

```text
DIGITAL_ORIGINAL_AVAILABLE
PAGES_PENDING
```

而不应该只是 `SCAN_WANTED`。

---

# 14. Netherlands：Power Unlimited 原始 URL 已恢复

2016-10-19 的 Tweakers 社区讨论保留了一条非常关键的信息：

> “Die Gamexplain en PU interviews zijn ERG goed  
> (embargo vrijgegeven voor interviews met Masuda en Ohmori)”

并保留原 PU.nl 链接。

同期讨论：

https://gathering.tweakers.net/forum/list_messages/1699321/8

恢复出的旧页面 URL：

http://www.pu.nl/artikelen/feature/pokemon-sun-moon-junichi-masuda-shigeru-ohmori-van-game-freak/

旧 PU 页面目前不可正常访问，但 URL 本身已经明确：

```text
pokemon-sun-moon
junichi-masuda
shigeru-ohmori
van-game-freak
```

再结合：

- 増田明确说 London 24 包括 Netherlands 媒体；
- 2016-10-19 与大量其他 London / SF press interviews 同日 embargo 解禁；
- Tweakers 同期用户明确称它为 PU 自己的 Masuda / Ohmori interview。

因此 Power Unlimited 可以从普通 candidate 升级为：

```text
HIGH_CONFIDENCE_EVENT
```

仍待恢复：

- 原页面 archive
- 编辑 / interviewer
- interview date / location
- 是否存在纸本版本

---

# 15. gamesTM issue 进一步缩小

Nintendo Everything 在 **2016-11-13** 明确写：

> “In the latest issue GamesTM…”

并说明采访对象为：

- Junichi Masuda
- Shigeru Ohmori

来源：

https://nintendoeverything.com/pokemon-sunmoon-devs-on-the-drip-feed-of-news-updates-fan-theories-thoughts-on-hardware-more/

Siliconera 同期引用：

https://www.siliconera.com/pokmon-sun-moon-devs-fan-theories-main-series-stays-handhelds/

Retromags 的期号年月映射为：

- #179 = October 2016
- **#180 = November 2016**
- #181 = December 2016
- #182 = Christmas 2016

索引：

https://www.retromags.com/magazines/uk/games-tm/page/8/

因此截至目前最合理的书目重建是：

```yaml
publication: gamesTM
issue: 180   # high-confidence reconstruction
cover_date: 2016-11
interviewees:
  - Junichi Masuda
  - Shigeru Ohmori
interview_verified: true
issue_verified_from_original_toc: false
pages: pending
verification_grade: A-
```

为什么暂时不写成完全 VERIFIED：

> 尚未直接取得 #180 的 TOC / 原页证明采访就在该期。

所以 Wanted 页面可以显示：

> **gamesTM #180 (?) — issue 高置信，页码待扫**

---

# 16. Spain / Iberia：必须从 London 24 中拆出去的独立系列

第二轮搜索证明，2016 年 12 月的西班牙存在一整组**新的现场采访**。

建议建立：

```yaml
series_id: SM_2016_DECEMBER_IBERIA_TOUR
```

目前确认 / 高置信包括：

### Hobby Consolas web / video

2016-12-08：

https://www.hobbyconsolas.com/reportajes/pokemon-sol-luna-entrevista-masuda-ohmori-creadores-83312

### Vandal

在 Nintendo showroom Madrid 的现场采访：

https://vandal.elespanol.com/reportaje/pokemon-en-plena-forma-20-anos-despues

### 3DJuegos

2016-12-14：

https://www.3djuegos.com/juegos/pokemon-sol-pokemon-luna/noticias/los-creadores-de-pokemon-se-plantean-si-lanzar-o-no-un-161214-66480

### NextN

2016-12-16：

https://www.nextn.es/2016/12/entrevista-masuda-ohmori-pokemon/

### MeriStation

PokeAmice：

https://docs.pokeamice.com/interview-meristation-sun-moon-switch-masuda-ohmori/

### Spanish Official Nintendo Magazine

部分原刊页照片：

https://lavacutcontent.com/masuda-ohmori-pokemon-gray/

因此：

> 上述 12 月 Spain interviews 不应为了凑齐 London 24 而塞入 36 家名单。

---

# 17. Spanish Official Nintendo Magazine：扫描来源进一步明确

目前仍不能把 Lava Cut Content 保存的 Masuda / Ohmori 采访准确钉到具体 issue。

但整刊恢复条件比之前好很多。

Pokémon Project 保存了大量西班牙 Nintendo 官方杂志 PDF：

https://pkproject.net/revista-nintendo-accion

2016 年末重点候选：

```text
Revista Oficial Nintendo #291 — December 2016
Revista Oficial Nintendo #292 — January 2017
```

DeVuego 的 Sun/Moon 杂志索引也列出：

- #291 / December 2016
- #292 / January 2017，Pokémon Sun/Moon cover

https://www.devuego.es/bd/prensa/sol

因此下一步应直接检查这两份 PDF 内：

```text
Junichi Masuda
Shigeru Ohmori
entrevista
Pokémon Gris / Gray
Pokémon Z
Colosseum
```

在核对之前不要猜采访属于 #291 还是 #292。

当前状态：

```yaml
publication: Revista Oficial Nintendo Spain
issue: 291_or_292_pending
interview_verified: true
partial_scan_recovered: true
full_issue_scan_candidates_available: true
```

---

# 18. Famitsu 2016：两期不再属于“找不到原刊”

## 2016年7月28日号

KADOKAWA：

https://www.kadokawa.co.jp/product/301603000581/

BOOK☆WALKER：

https://bookwalker.jp/de7e3ad1a3-3371-4029-861a-90dd877218be/

受访：

- Junichi Masuda
- Shigeru Ohmori

因此 Wanted 状态应改为：

```text
DIGITAL_ORIGINAL_AVAILABLE
INTERVIEW_PAGES_PENDING
```

---

## 2016年12月1日号

KADOKAWA：

https://www.kadokawa.co.jp/product/301611000470/

BOOK☆WALKER：

https://bookwalker.jp/de4d37ef7e-155e-4ba6-b048-2a0875b6e6eb/

已知：

- 2016-11-17 发售
- 232 pages total
- Pokémon Sun/Moon **14页特集**
- 含 Masuda × Ohmori 开发采访

状态：

```text
DIGITAL_ORIGINAL_AVAILABLE
14P_FEATURE_VERIFIED
INTERVIEW_SUBPAGES_PENDING
```

这两期的工作已经不是“找扫描”，而是：

> 取得/查看数字原版 → 记录精确页码 → 截取可引用原页。

---

# 19. 当前实体纸媒状态表（v0.2）

| 目标 | Interview | 已知页数 | 原刊来源状态 |
|---|---|---:|---|
| Nintendo DREAM Vol.235 | Masuda × Morimoto | 别册 52p；采访子页未知 | Scan Wanted |
| Nintendo DREAM Vol.236 | XY Character Design | 未知 | Scan Wanted |
| Famitsu 2013-10-24 | Masuda | 未知 | 原刊/数字版继续追 |
| Famitsu 2013-11-7/14 | Design Key Person | **专题9p** | Interview 子页待确认 |
| XY Official Guide | Masuda Long Interview | 待查 | Official book available |
| Famitsu XY Sound | Masuda × Kageyama | issue/pages需重新核 | PokeAmice已有内容 |
| Famitsu 2014-12-4増刊 | ORAS developer | **supplement 52p** | Scan Wanted |
| Nintendo DREAM Vol.250 | ORAS Sound | 未知 | Scan Wanted |
| Nintendo DREAM Vol.254 | Ohmori/Sugimori/Morimoto/Iwao | 未知 | Scan Wanted |
| Famitsu 2016-7-28 | Masuda × Ohmori | 未知 | **Digital original available** |
| Famitsu 2016-12-1 | Masuda × Ohmori | **专题14p** | **Digital original available** |
| N-Zone #235 | Masuda × Ohmori | 未知 | Scan Wanted |
| GamesMaster #310 | developer interviews | **pp.44–53专题** | Digital back issue source |
| gamesTM #180 (?) | Masuda × Ohmori | 未知 | Issue high-confidence; pages pending |
| Hobby Consolas #305 | Masuda × Ohmori | 未知 | **Digital original available** |
| Revista Oficial Nintendo ES | Masuda × Ohmori | 未知 | Partial pages + candidate full PDFs |

---

# 20. 当前 36 家媒体恢复度（v0.2）

当前最保守的统计：

```text
London:
  11–12 strong/direct candidates / 24

San Francisco:
  7 strong candidates / 12
  + Kotaku direct phone interview, event membership unresolved

Total named direct/high-confidence outlets plausibly linked to the 36:
  about 18–19
```

之所以不简单写 `19 / 36`：

1. Nintendo of Europe 是否属于増田统计的 24 家媒体未证实；
2. 部分媒体虽为 direct interview，但地点仍靠时间 / embargo / 国家信息重建；
3. Kotaku 是电话采访，可能与 press event 同期但不一定计入现场 12 家。

因此当前阶段可以认为：

> **2016 SM 36 家媒体已经恢复到约一半，且欧洲国家矩阵的结构已经基本建立。**

---

# 21. 第二轮排除项

以下类型即使有“采访内容”，也不能算作新增媒体：

### AkibaGamers

2016-10-20 的意大利文页面实际上开头就说明来源为 Game Informer。

所以：

```text
SECONDARY_ONLY
count_in_24 = false
```

### Nintendo Everything

对 N-Zone / gamesTM / USgamer 等的翻译和整理很有价值，但：

```text
source_secondary = true
count_in_36 = false
```

### Siliconera

同理，大量文章是在转述 gamesTM / N-Zone 等纸本：

```text
source_secondary = true
count_in_36 = false
```

---

# 22. 下一轮剩余的高价值矩阵

目前最值得继续追：

```text
UK:
  Digital Spy
  Nintendo Life
  IGN UK
  other Future / Imagine outlets

Germany:
  PC Games
  Spieletipps
  Eurogamer.de
  IGN Deutschland

France:
  Gamekult
  JeuxActu
  IGN France

Italy:
  Multiplayer.it
  Everyeye
  IGN Italia
  Eurogamer.it

Netherlands:
  Gamer.nl
  IGN Benelux
  Power Unlimited original archive

North America:
  IGN
  Polygon
  The Verge
  RPG Site
  Nintendo World Report
  Destructoid
```

但从第二轮结果看，后续搜索应优先使用：

```text
"we interviewed"
"we spoke with"
"our interview"
"met with"
"at The Pokémon Company"
"London"
"San Francisco"
```

而不再只搜：

```text
Masuda Ohmori interview 2016
```

这样能显著减少转载噪声。

---

# 23. 国家矩阵第三轮更新（v0.3）

> 本轮目标：继续清理 2016 Sun/Moon 的 London 24 / San Francisco 12，同时验证这套“国家矩阵 + 同一媒体日 + embargo 解禁日”的方法能否反向复原 2014 ORAS 媒体活动。

## 23.1 UK：Digital Spy 从候选升级

### Digital Spy — HIGH_CONFIDENCE_DIRECT / London affiliation still inferred

已恢复文章标题与书目信息：

- Sam Loveridge, **“Want to know how The Pokémon Company designs Pokémon?”**
- publication date: **2016-10-20**
- 原页后来失效，但多份参考资料保留了题名、作者、日期和 archive 记录。

可恢复的旧 URL 形态：

```text
http://www.digitalspy.com/gaming/pokemon/feature/a811646/heres-how-the-pokemon-company-design-pokemon/
```

关键判断：

1. 内容直接引用 Shigeru Ohmori 对 Pokémon 设计流程的回答，不是普通新闻稿；
2. 时间为 2016-10-20，正好紧接 10/19 大批 Masuda / Ohmori 媒体稿统一解禁；
3. Digital Spy 为英国媒体，且同期还参加了 Sun/Moon 两小时 preview；
4. 目前仍没有一份可见原页明确写出 “London / Chiswick”。

因此状态升级为：

```text
DIRECT_INTERVIEW = true
HIGH_CONFIDENCE_EVENT = true
CONFIRMED_LOCATION = false
likely_event = SM_2016_LONDON_PRESS
```

这使 London 强候选从此前的 **11 家**提升到 **12 家左右**。

### Nintendo Life — 暂不升级

2016 年可检索到的大量 Sun/Moon 新闻主要引用 GameSpot、Nintendo of Europe 等来源；本轮没有找到一篇能证明 Nintendo Life 自己在 2016 London press event 采访 Masuda / Ohmori 的原始稿。

状态维持：

```text
CANDIDATE / NOT YET PROVEN
```

---

# 24. Spain / Portugal：进一步与 London 24 切割

## 24.1 3DJuegos — CONFIRMED DIRECT, BUT DECEMBER IBERIA TOUR

2016-12-14 的 3DJuegos 页面明确写：

- 编辑部最近有机会与 Junichi Masuda 交谈；
- Masuda 与 Shigeru Ohmori 正在多个国家巡回；
- 该采访围绕刚发售的 Pokémon Sun / Moon；
- 随后会刊出完整采访。

这与 Masuda 年末记录中的 Spain / Portugal 行程吻合，因此：

```text
DIRECT_INTERVIEW = true
count_in_London24 = false
count_in_SF12 = false
series = SM_2016_IBERIA_DECEMBER_TOUR
```

来源：

https://www.3djuegos.com/juegos/pokemon-sol-pokemon-luna/noticias/los-creadores-de-pokemon-se-plantean-si-lanzar-o-no-un-161214-66480

## 24.2 Vandal — CONFIRMED Madrid showroom

Vandal 2016-12-10 专访明确写：

- 借 Masuda / Ohmori 到访西班牙之机采访；
- 采访地点为 **Nintendo showroom in Madrid**。

所以这篇可以直接锁到 12 月西班牙行程，而不是 London 24。

```text
DIRECT_INTERVIEW = true
CONFIRMED_LOCATION = Madrid
count_in_36 = false
```

来源：

https://vandal.elespanol.com/reportaje/pokemon-en-plena-forma-20-anos-despues

### 对 Spain 行的意义

此前 Spain 栏最容易混淆的是：

- EL PAÍS Tecnología：强证据指向 London；
- Hobby Consolas：需按刊期与采访语境继续判定；
- MeriStation：已知属于年末西班牙宣传行程；
- 3DJuegos：本轮确认属于年末西班牙宣传行程；
- Vandal：本轮确认属于 Madrid showroom 行程。

因此后续不应再把“西班牙媒体 + Masuda/Ohmori 采访”自动塞入 London 24。

---

# 25. 2016 Italy / France / Germany：本轮未升级项

## Italy

### AkibaGamers

再次确认 2016-10-20 页面开头直接说明其内容来自 Game Informer。

```text
SECONDARY_ONLY
```

### Everyeye

搜索可见 2016-10-26 有“Sun/Moon director talks about design of new Pokémon”类报道，但当前没有足够证据证明是 Everyeye 自采。

```text
CANDIDATE / SOURCE_CHAIN_PENDING
```

### Multiplayer.it

本轮未恢复到 2016 Sun/Moon London 自采，但恢复出 2014 ORAS 的重要直接采访，见第 27 节。

## France

Gameblog 仍是本轮最硬的 London 锚点之一；Gamekult / JeuxActu 本轮没有找到足以升级为 direct interview 的 2016 原始稿。

## Germany

GamePro / N-Zone 保持原判断；PC Games / Spieletipps 本轮未得到 direct-interview 证据。

---

# 26. 2016 Sun/Moon 36 家恢复度更新（v0.3）

## London 24

当前可列为 confirmed / high-confidence 的独立媒体组织：

1. Nintendo of Europe
2. Gameblog
3. Jeuxvideo.com
4. La Crème du Gaming
5. GamePro
6. N-Zone
7. La Repubblica
8. EL PAÍS Tecnología
9. GamesMaster
10. gamesTM
11. Power Unlimited
12. **Digital Spy** ← 本轮升级

仍需继续追：

```text
UK: IGN UK / other Future-Imagine outlets
Germany: PC Games / Spieletipps / Eurogamer.de / IGN DE
France: Gamekult / JeuxActu / IGN FR
Italy: Multiplayer.it / Everyeye / IGN Italia / Eurogamer.it
Netherlands: Gamer.nl / IGN Benelux / PU original archive
```

保守计数：

```text
London strong/direct candidates: ~12 / 24
```

## San Francisco 12

本轮没有新增一个足够硬的新名字。

维持：

1. GameSpot — confirmed San Francisco office
2. Game Informer
3. TIME
4. USgamer
5. GamesRadar
6. Eurogamer
7. GameXplain

另：

- Kotaku = direct phone interview，event membership unresolved

所以：

```text
SF strong candidates: 7 / 12
+ Kotaku direct, but not safely countable
```

### 当前总体

```text
London ~12
SF ~7
= ~19 strong/direct organizations plausibly tied to the official 36
```

仍不能机械写成 19/36，因为 Nintendo of Europe、Power Unlimited 等的官方计数归属仍需最终证明。

---

# 27. 同一国家矩阵方法向 2014 ORAS 反推：发现 Frankfurt press node

本轮最重要的结构性发现之一，是 2014-10-14 左右存在非常清楚的 **Nintendo of Europe / Frankfurt** 媒体活动。

## 27.1 Germany — ntower

ntower 在 **2014-10-14** 发布 Junichi Masuda × Shigeru Ohmori 完整采访，正文为自采 Q&A。

来源：

https://www.ntower.de/bericht/271-interview-mit-junichi-masuda-und-shigeru-ohmori-game-freak/

状态：

```text
DIRECT_INTERVIEW
ORAS_2014_EU_PRESS
```

## 27.2 France — Gameblog

Gameblog 2014-10-14 的 preview 明确写：

> 数日前在 Nintendo 位于 Frankfurt 的办公室再次见到 Junichi Masuda。

来源：

https://www.gameblog.fr/jeu-video/ed/impressions/pokemon-saphir-alpha-et-rubis-omega-sur-3ds-nous-y-avons-joue-42479

状态：

```text
DIRECT_CONTACT
CONFIRMED_LOCATION = Frankfurt / Nintendo offices
```

## 27.3 Italy — Multiplayer.it

Multiplayer.it 同日文章明确写：

- 身处 **Francoforte**；
- 地点为 **Nintendo of Europe headquarters**；
- 试玩 ORAS 数小时；
- 随后采访 Junichi Masuda 与 Shigeru Ohmori。

来源：

https://multiplayer.it/articoli/138469-pokemon-rubino-omega-ritorno-a-hoenn.html

状态：

```text
DIRECT_INTERVIEW
CONFIRMED_LOCATION = Frankfurt / Nintendo of Europe
```

## 27.4 法国 Millenium

Millenium 2014-11-28 也发布了 Masuda × Ohmori exclusive interview：

https://www.millenium.org/news/176827.html

但当前页面本身未明确 Frankfurt，因此暂先记录为：

```text
DIRECT_INTERVIEW
LOCATION_PENDING
```

## 27.5 Germany / France / Italy 三国同步的意义

2014-10-14 同一天至少出现：

```text
Germany: ntower
France: Gameblog
Italy: Multiplayer.it
```

其中 Gameblog 与 Multiplayer.it 都把地点锁到 Frankfurt / Nintendo of Europe。

这说明 PokeAmice 在复原历史媒体采访时可以新增一个事件层：

```yaml
series_id: ORAS_2014_EU_MEDIA_DAY
location: Nintendo of Europe, Frankfurt
approx_date: 2014-10
participants:
  - Junichi Masuda
  - Shigeru Ohmori
confirmed_media:
  - ntower
  - Gameblog
  - Multiplayer.it
candidate_media:
  - Millenium
```

下一轮可以用与 SM London 24 完全相同的方法，反搜：

```text
UK / Spain / Netherlands / other Germany / other France / other Italy
```

并检查 2014-10-14~16 的同步 embargo。

---

# 28. 研究优先级更新

下一轮建议优先级调整为：

1. **继续补 2016 London 24**：重点盯 Italy / Netherlands / Germany 的原始媒体页；
2. **继续补 SF 12**：利用 2016-10-19 的统一发布时间反查美国媒体；
3. **建立 ORAS 2014 Frankfurt 国家矩阵**：这是本轮新增的第二个可复原 press-event；
4. 对 2016 Spain / Portugal 建立独立事件，不再污染 London 24；
5. 纸本方面继续锁 Nintendo DREAM / N-Zone / gamesTM 的精确页码。

建议事件拆分更新为：

```yaml
press_events:
  - XY_2013_GLOBAL_MEDIA
  - ORAS_2014_EU_MEDIA_DAY_FRANKFURT
  - SM_2016_LONDON_PRESS
  - SM_2016_SAN_FRANCISCO_PRESS
  - SM_2016_IBERIA_DECEMBER_TOUR
```

这样后续 Wanted 页面不只是“缺一篇文章”，而是能显示：

- 已知某次媒体活动存在；
- 已恢复多少家媒体；
- 哪些国家仍空缺；
- 哪些网页已死但书目信息存在；
- 哪些实体杂志仍需要扫描。

---

# 13. 国家矩阵第三轮更新（v0.4）

> 本轮重点：  
> 1. 继续压实 2016 London 的 Italy / Netherlands / Germany；  
> 2. 利用 2016-10-19 同日 embargo 反查 San Francisco 12；  
> 3. 将 2014 ORAS Frankfurt / Nintendo of Europe 单独建成事件节点，避免把“同日发布”误判成“同一地点”。

---

## 13.1 2016 London — Germany

### GamePro — CONFIRMED / HIGH-CONFIDENCE LONDON EVENT

主文：

https://www.gamepro.de/artikel/pokemon-sonne-mond-das-neue-rpg-will-alte-fans-ueberraschen%2C3304185.html

- 发布：2016-10-19
- 作者：Linda Sprenger
- 文中明确为 GamePro 自己向 Shigeru Ohmori / Junichi Masuda 提问。
- 同一作者在此前试玩稿明确写：
  > “Wir haben in London …”
- 因此 GamePro 可稳定保留在 London 24。

配套试玩：

https://www.gamepro.de/artikel/pokemon-sonnemond-frischer-wind-im-verstaubten-franchise%2C3303825.html

### N-ZONE #235 — DIRECT INTERVIEW，issue 已锁定

二手全文译载：

https://nintendoeverything.com/pokemon-sun-moon-director-on-poke-ride-time-difference-sidequests-coming-up-with-new-pokemon-more/

关键信息：

- N-ZONE #235
- 期号：11/2016
- 发售：**2016-10-19**
- Masuda × Ohmori 直接问答
- 主题包括：
  - Island Trial / Gym replacement
  - Poké Ride
  - Alola Forms
  - time difference
  - Pokémon Refresh
  - side quests
  - post-game / Mega Evolution

期号时间表：

https://de.wiki.li//N-Zone

当前判断：

`HIGH_CONFIDENCE_EVENT`

原因：采访与 London press tour 时间、人物、欧洲媒体批量 embargo 高度吻合，但本轮仍未找到原刊中直接写 London / Chiswick 的句子。

下一步重点：

- 找 #235 数字版 / Internet Archive / Readly / Zinio / Google Books 预览；
- 确认采访具体页码；
- 查看正文页眉、图片说明是否注明 London。

---

## 13.2 2016 London — Italy

### La Repubblica — CONFIRMED_LOCATION

原文：

https://www.repubblica.it/tecnologia/2016/11/14/news/la_sgaga_infinita_dopo_poke_mon_go_ecco_luna_e_sole-302638548/

这是目前欧洲矩阵中最硬的地点证据之一。

原文明确写记者到达：

> The Pokémon Company International  
> Chiswick, London

随后描述 Masuda / Ohmori 坐在椭圆桌旁接受采访，并提到现场有翻译与 Nintendo / Pokémon Company 人员。

状态：

`CONFIRMED_LOCATION`

### Multiplayer.it — 本轮暂不计入 London 24

本轮搜索到的 2016-10-12 试玩稿：

https://multiplayer.it/articoli/175038-pokemon-sole-un-nuovo-giorno-per-i-pokemon.html

它明确写：

> siamo quindi volati a Francoforte

即该试玩 session 在 Frankfurt。

因此：

- 不能因为 Multiplayer.it 是意大利媒体就自动塞入 London 24；
- 2016 年本身可能同时存在 **Frankfurt hands-on** 与 **London developer interview** 两种节点；
- 若后续发现 Multiplayer.it 的 Masuda / Ohmori 直接采访，需要单独看地点。

当前状态：

`NOT_YET_LONDON`

### Everyeye / SpazioGames

本轮仍未找到可证明其亲自参加 London Masuda × Ohmori interview 的原始证据。

SpazioGames 目前命中的多为二手转述 / 新闻，不升级。

Everyeye 2016-10-19 有 demo hands-on：

https://www.everyeye.it/articoli/provato-pokemon-sole-luna-provata-demo-per-nintendo-3ds-31227.html

但不是本轮目标中的开发者直接采访。

状态：

`CANDIDATE / INSUFFICIENT_DIRECT_EVIDENCE`

---

## 13.3 2016 London — Netherlands

### Power Unlimited — 仍然是最强荷兰候选

关键同期证据来自 Tweakers 论坛 2016-10-19：

https://gathering.tweakers.net/forum/list_messages/1699321/8

当时用户明确写：

> “Die GameXplain en PU interviews zijn ERG goed  
> (embargo vrijgegeven voor interviews met Masuda en Ohmori)”

并同时贴出：

- PU interview
- Kotaku interview
- GameXplain interview

这说明：

1. PU 确实有自己的 Masuda × Ohmori interview；
2. 2016-10-19 是统一 embargo 解禁日；
3. PU 不应被当作转载媒体。

状态：

`HIGH_CONFIDENCE_DIRECT`

仍缺：

- 原 PU.nl 页面恢复；
- 地点是否为 London / Chiswick；
- 作者与发布日期；
- 是否还有纸本 Power Unlimited magazine 版本。

### Nintendo NL 不应重复计数

Nintendo of Europe 的荷兰语本地化：

https://www.nintendo.com/nl-nl/Nieuws/2016/oktober/Wat-is-langer-dan-een-Alolan-Exeggutor-Je-leest-het-in-ons-exclusieve-interview-over-Pokemon-Sun-en-Pokemon-Moon--1148574.html

与 UK / IT / ES / PT 等页面属于同一 Nintendo of Europe interview 的本地化。

因此：

**只能算 1 个 media organization / interview session，不能按语言虚增。**

---

# 14. 2016-10-19 Embargo Cluster：反查 San Francisco 12

## 14.1 已知同日大规模上线

2016-10-19 可以明确看到大量 Masuda × Ohmori 内容集中发布：

- GameSpot
- Game Informer
- TIME
- USgamer
- GamesRadar
- Eurogamer
- GameXplain
- Kotaku
- IGN
- Nintendo of Europe
- Power Unlimited
- N-ZONE

其中并不是全部属于 San Francisco。

因此“10 月 19 日上线”只能作为 **embargo cluster 证据**，不能单独等同于 SF event。

---

## 14.2 GameSpot — SF 最强锚点

https://www.gamespot.com/articles/pokemon-sunmoon-devs-on-legendaries-pokemon-go-and/1100-6444620/

原文：

> Nintendo’s San Francisco office

同一 session 拆稿：

https://www.gamespot.com/articles/pokemon-go-connection-with-sunmoon-is-still-in-the/1100-6444589/

状态：

`CONFIRMED_LOCATION = SAN FRANCISCO`

---

## 14.3 IGN — 新增强候选

同期二手锚点：

https://nintendoeverything.com/video-game-freaks-junichi-masuda-picks-six-of-his-favorite-pokemon/

2016-10-19：

> IGN recently caught up with Game Freak’s Junichi Masuda

内容是 Masuda 选择六只自己最喜欢的 Pokémon。

这能确认：

- IGN 在该 embargo cluster 中有 **直接接触 Masuda** 的原创内容；
- 不只是二手引用。

但当前不足以证明：

- 是否同一次 SF office session；
- 是否只有 Masuda，还是也采访 Ohmori；
- 是否应该计入官方 12 家。

当前状态：

`DIRECT_INTERVIEW_LOCATION_UNKNOWN`

这是本轮 SF 反查最重要的新候选之一。

---

## 14.4 Kotaku — 仍不建议直接计入 SF 12

https://kotaku.com/asked-for-their-favorite-even-pokemon-sun-and-moons-cr-1787943425

Kotaku 明确写：

> speak over the phone

因此它是直接采访无疑，但形式为电话。

状态保持：

`DIRECT_INTERVIEW_LOCATION_UNKNOWN`

在找到 Nintendo SF office / in-person 证据前，不计入 SF 12。

---

## 14.5 Nintendo of Europe：同日发布 ≠ SF

https://www.nintendo.com/en-gb/News/2016/October/Is-there-anything-taller-than-an-Alolan-Exeggutor-Find-out-in-our-exclusive-Pokemon-Sun-and-Pokemon-Moon-interview--1148574.html

发布日期也是 2016-10-19。

但采访主体明确写为：

> Nintendo of Europe

而且同内容存在英国、荷兰、意大利、西班牙、葡萄牙等本地化页面。

这说明：

**2016-10-19 是跨区域 embargo，而不是单纯 SF embargo。**

这是本轮对 SF 12 复原方法的重要修正。

---

## 14.6 SF 12 当前结构

### 已有强候选 / confirmed

1. GameSpot — CONFIRMED_LOCATION
2. Game Informer — HIGH_CONFIDENCE
3. TIME — HIGH_CONFIDENCE
4. USgamer — HIGH_CONFIDENCE
5. GamesRadar — HIGH_CONFIDENCE
6. Eurogamer — HIGH_CONFIDENCE
7. GameXplain — HIGH_CONFIDENCE

### 新增重点候选

8. **IGN — DIRECT_INTERVIEW_LOCATION_UNKNOWN**

### 暂不计入

- Kotaku — phone interview
- Nintendo of Europe — European session
- Power Unlimited — European / likely London
- N-ZONE — European / likely London

### 因此

SF 侧现在可以从“7 家强候选”提升成：

**7 confirmed/high-confidence + 1 strong direct candidate (IGN)**

但离可靠恢复 12 家仍差约 4 家。

下一轮 North America 应优先查：

- Polygon
- The Verge
- Mashable
- VentureBeat
- Ars Technica
- CNET
- Engadget
- TechCrunch
- Vice / Waypoint
- Paste
- EGM
- Nintendo-focused outlets

检索必须带：

```text
"Oct 19 2016" + Masuda + Ohmori
"San Francisco" + Pokemon Sun Moon + interview
"Nintendo's San Francisco office"
"we sat down with"
"we spoke with"
"our interview"
```

---

# 15. 2014 ORAS Frankfurt：独立事件节点

## 15.1 已确认地点媒体

### Multiplayer.it — CONFIRMED_LOCATION

https://multiplayer.it/articoli/138469-pokemon-rubino-omega-ritorno-a-hoenn.html

原文直接写：

> Ci troviamo a Francoforte, all'interno della sede di Nintendo of Europe

并写正在等待采访：

> Junichi Masuda e Shigeru Ohmori

因此：

`CONFIRMED_LOCATION = FRANKFURT / NINTENDO OF EUROPE`

### ntower — DIRECT，同日 Frankfurt 高置信

https://www.ntower.de/community/thread/39174-interview-mit-junichi-masuda-und-shigeru-ohmori-von-game-freak/

- 发布：2014-10-14
- 直接 video + text interview
- Masuda × Ohmori

结合德国本地媒体与同日 Nintendo of Europe Frankfurt hands-on 节点：

`HIGH_CONFIDENCE_FRANKFURT`

### Gameblog France

上一轮已确认属于这一 Frankfurt / Nintendo of Europe 节点，继续保留。

---

# 16. 2014 Frankfurt — UK 逆向矩阵

## 16.1 Nintendo Life

Nintendo Life 在 2014-10-15 报道：

https://www.nintendolife.com/news/2014/10/pokemon_x_and_y_wont_be_patched_to_accommodate_new_mega_evolutions

文中明确引用：

> In a recent interview, Junichi Masuda and Shigeru Ohmori...

但当前页面本身更像对其他 interview 的转述，不能证明 Nintendo Life 自己在 Frankfurt。

状态：

`SECONDARY / NEED SOURCE TRACE`

## 16.2 WIRED UK — direct interview，但时间节点不同

https://www.wired.com/story/pokemon-interview/

发布：2014-12-11

WIRED.co.uk 直接采访 Masuda × Ohmori。

这是很重要的 UK direct interview，但日期远晚于 10 月 Frankfurt press day。

状态：

`DIRECT_INTERVIEW_SEPARATE_EVENT`

暂不塞入 Frankfurt。

## 16.3 Pocket Gamer — direct interview，12 月

https://www.pocketgamer.com/pokemon-omega-ruby-and-alpha-sapphire/game-freak-on-pokemon-well-make-the-games-we-want-to-make-then-choose-the-hardwa/

发布：2014-12-10

作者写：

> Last week ... I met up with Junichi Masuda and Shigeru Ohmori.

也是直接 interview，但属于 12 月欧洲宣传期。

状态：

`DIRECT_INTERVIEW_SEPARATE_EVENT`

---

# 17. 2014 Frankfurt — Spain 逆向矩阵

## Centro Pokémon — 聚合源，不是原始采访

https://www.centropkmn.com/2014/10/15/entrevista-a-junichi-masuda-y-shigeru-ohmori-nuevos-detalles-de-pokemon-rubi-omega-y-zafiro-alfa/

文章明确说：

> diferentes medios han tenido la oportunidad...

随后汇总多个媒体答案。

因此 Centro Pokémon 是非常有价值的 **source map / quote aggregator**，但不应被计作 Frankfurt 参会媒体。

状态：

`SECONDARY_AGGREGATOR`

### 目前西班牙 Frankfurt direct outlet

本轮仍未锁定。

下一轮重点：

- Vandal
- 3DJuegos
- MeriStation
- Hobby Consolas
- IGN España
- Nintendo Acción

日期窗口优先：

**2014-10-13 ~ 2014-10-20**

---

# 18. 2014 Frankfurt — Netherlands 逆向矩阵

本轮没有找到足够证据把 Gamer.nl / Power Unlimited / Tweakers 中任一家升级为 Frankfurt direct interview。

但 Nintendo 的区域宣传网络说明荷比市场当时高度活跃：

https://bulbanews.bulbagarden.net/wiki/Junichi_Masuda%2C_Shigeru_Ohmori_Miis_available_at_GAME_in_UK

其中记录：

- Netherlands / Belgium 的 Game Mania 参与 Masuda / Ohmori Mii 分发；
- 与 Germany / Italy / UK 同属 ORAS 欧洲宣传周期。

这只能作为**区域活动背景**，不能当采访证据。

当前：

- Power Unlimited — `CANDIDATE`
- Gamer.nl — `CANDIDATE`
- Tweakers — `CANDIDATE`

---

# 19. 2014 的重要方法修正：同日 ≠ 同地点

Game Informer 也在 2014-10-14 发布 Masuda × Ohmori interview：

https://gameinformer.com/b/features/archive/2014/10/14/pok-233-mon-s-developers-on-virtual-console-absences-twitch-and-super-smash-bros

这和 Frankfurt press day 是同日。

但是页面没有 Frankfurt / Nintendo of Europe 地点证据。

因此 2014 也出现和 2016 一样的问题：

```text
same publication date
    ≠
same press location
```

后续数据库建议把以下字段拆开：

```yaml
publication_date:
embargo_cluster:
interview_date:
interview_location:
event_affiliation:
evidence_location:
```

避免把 embargo batch 当成实体活动名单。

---

# 20. 本轮后矩阵状态

## 2016 London 24

强候选维持 / 提升：

1. Nintendo of Europe
2. Gameblog
3. Jeuxvideo.com
4. La Crème du Gaming
5. GamePro
6. N-ZONE
7. La Repubblica
8. EL PAÍS Tecnología
9. GamesMaster
10. gamesTM
11. Power Unlimited
12. Digital Spy

约：

**12 / 24**

意大利目前真正硬证据仍以 La Repubblica 为主。

## 2016 San Francisco 12

强候选：

1. GameSpot
2. Game Informer
3. TIME
4. USgamer
5. GamesRadar
6. Eurogamer
7. GameXplain

新强候选：

8. IGN

约：

**7 confirmed/high-confidence + 1 strong direct candidate / 12**

## 2014 Frankfurt

已确认 / 高置信：

- Multiplayer.it
- ntower
- Gameblog
- 以及上一轮已找到的 Frankfurt 节点媒体

但 UK / Spain / Netherlands 仍明显不足。

---

# 21. 下一轮建议

优先级 A：SF 12

直接对 2016-10-19 美国媒体做 outlet-by-outlet 反查，目标把 IGN 后面的 4 家找出来。

优先级 B：London Netherlands

恢复 PU.nl 原文 URL / archive snapshot，是目前最可能直接增加证据强度的一项。

优先级 C：2014 Frankfurt Spain

用 Centro Pokémon 的汇总文本反向做 **quote fingerprinting**：
把每一条回答原句拿去搜索，往往能找回被它汇总掉的原始媒体。

优先级 D：2014 Frankfurt Netherlands

优先旧纸媒 / 游戏站：

- Power Unlimited
- Gamer.nl
- [N]Gamer
- Nintendo Power / Official Nintendo Magazine regional editions
- InsideGamer

---

> v0.4 结论：
>
> 当前最大的进展不是简单“又找到几家”，而是确认了  
> **2016-10-19 和 2014-10-14 都是跨地点 embargo cluster**。  
> 从现在开始，恢复官方媒体数量必须以“直接采访 + 地点/活动归属”双证据为准。

---

# 22. 国家矩阵第四轮更新（v0.5）

> 本轮重点：
> - 2016 San Francisco 12：继续反查 2016-10-19 北美媒体；
> - 2014 Frankfurt：Spain 取得硬地点证据；
> - 从 Centro Pokémon 2014 汇总稿恢复原始来源池，作为下一轮 quote-fingerprinting 清单。

---

## 22.1 2014 Frankfurt — Spain：3DJuegos 升级为 CONFIRMED_LOCATION

原文：

https://www.3djuegos.com/juegos/pokemon-rubi-omega-pokemon-zafiro-alfa/noticias/pokemon-rubi-omega-zafiro-alfa-dos-megaremakes-141014-4343

发布日期：

**2014-10-14**

关键证据非常明确：

- 文章开头写“Viajamos hasta la sede de Nintendo Europa”
- 随后进一步写：
  - Nintendo 在 **Frankfurt 的总部办公室**举办活动；
  - 记者在活动中试玩约两小时；
  - 正文多处直接引用 Junichi Masuda / Shigeru Ohmori；
  - 图片说明写“Durante la presentación tuvimos ocasión de charlar un rato con Junichi Masuda y Shigeru Ohmori”。

因此 3DJuegos 不再只是 `DIRECT_INTERVIEW`，而应升级为：

`CONFIRMED_LOCATION = FRANKFURT / NINTENDO OF EUROPE`

这意味着 2014 Frankfurt 当前至少已有：

- Multiplayer.it — Italy — CONFIRMED_LOCATION
- 3DJuegos — Spain — CONFIRMED_LOCATION
- ntower — Germany — HIGH_CONFIDENCE_FRANKFURT
- Gameblog — France — HIGH_CONFIDENCE / previously recovered

### 2014 Frankfurt 国家覆盖由此扩展为

```text
Germany
France
Italy
Spain
```

UK / Netherlands 仍待恢复。

---

## 22.2 Centro Pokémon 2014 汇总稿：恢复原始 source pool

页面：

https://www.centropkmn.com/2014/10/15/entrevista-a-junichi-masuda-y-shigeru-ohmori-nuevos-detalles-de-pokemon-rubi-omega-y-zafiro-alfa/

该页不是独立采访，而是对多个媒体问题和回答的聚合。

最重要的新发现是页面底部明确保留来源：

```text
CVG
USgamer
GameSpot
Kotaku
GoNintendo
GameInformer
IGN
```

因此该页面应从“西班牙媒体候选”重新定义为：

`SECONDARY_AGGREGATOR / SOURCE_MAP`

但它的研究价值非常高：这 7 个媒体构成 2014-10-14 前后的原始采访/报道反查池。

---

## 22.3 2014 embargo cluster：USgamer 已确认是原创 interview source

原 USgamer URL：

http://www.usgamer.net/articles/so-does-pokemon-omega-ruby-and-alpha-include-trainer-customization

虽然原站迁移/失效，但同期引用非常丰富。

Nintendo Everything：

https://nintendoeverything.com/no-trainer-customization-in-pokemon-omega-rubyalpha-sapphire-game-freak-keen-on-keeping-random-encounters/

明确写：

> Junichi Masuda explained why this is so to USGamer

并完整引用其关于：

- Trainer customization
- Kalos / fashion
- Hoenn regional identity
- random encounters

的回答。

同期论坛也将该文标记为 **Oct 14, 2014 USGamer interview**。

因此：

`USGAMER_2014_ORAS = DIRECT_INTERVIEW`

但地点：

`LOCATION_UNKNOWN`

暂时不能直接归入 Frankfurt。

---

## 22.4 2014 embargo cluster：GameSpot 是独立原创采访，不是转载

GameSpot 同期至少有三篇由 interview 拆出的文章：

### What Exactly is New in Pokémon Omega Ruby and Alpha Sapphire?

https://www.gamespot.com/articles/what-exactly-is-new-in-pokemon-omega-ruby-and-alph/1100-6422933/

发布时间：2014-10-13 / 14 左右

正文：

> We recently spoke to game director Shigeru Ohmori

### Pokémon Director Explains Why Series is Becoming Easier

https://www.gamespot.com/articles/pokemon-director-explains-why-series-is-becoming-e/1100-6422945/

正文：

> We recently caught up with Masuda

### Pokémon Exec Interested in Amiibo Support

https://www.gamespot.com/articles/pokemon-exec-interested-in-amiibo-support/1100-6422946/

正文：

> Masuda told GameSpot

所以 GameSpot 明确属于：

`DIRECT_INTERVIEW`

但当前仍未找到正文明确写 Frankfurt / Nintendo of Europe。

由于作者包括 GameSpot UK Editor Rob Crossley 等欧洲团队成员，存在 Frankfurt 可能性，但不能仅凭编辑部身份推断。

状态：

`DIRECT_INTERVIEW_LOCATION_UNKNOWN`

---

# 23. 2014 Frankfurt 现在应改成“confirmed core + embargo satellites”

## Confirmed / high-confidence Frankfurt core

| 媒体 | 国家 | 状态 |
|---|---|---|
| Multiplayer.it | Italy | CONFIRMED_LOCATION |
| 3DJuegos | Spain | **CONFIRMED_LOCATION** |
| ntower | Germany | HIGH_CONFIDENCE_FRANKFURT |
| Gameblog | France | HIGH_CONFIDENCE / recovered previously |

## Same-cluster direct interviews, location still unknown

- USgamer
- GameSpot
- Game Informer

## Source-map candidates from Centro Pokémon

- CVG
- Kotaku
- GoNintendo
- IGN

这一步很重要：不能把 Centro Pokémon source list 自动等同于 Frankfurt attendee list。

---

# 24. 2016 San Francisco 12：本轮复核

## GameSpot remains the anchor

GameSpot 原文继续是 SF 事件最硬地点证据：

https://www.gamespot.com/articles/pokemon-sunmoon-devs-on-legendaries-pokemon-go-and/1100-6444620/

并明确：

> Nintendo’s San Francisco office

拆稿：

https://www.gamespot.com/articles/pokemon-go-connection-with-sunmoon-is-still-in-the/1100-6444589/

后者再次明确：

> interview at Nintendo’s San Francisco office

因此 GameSpot 可以作为 SF quote / session fingerprint 的核心比对对象。

---

## TIME 日期重新锁定为 2016-10-19

TIME：

https://time.com/4536438/pokemon-sun-moon-interview/

TIME 的 Pokémon archive 明确列：

**Oct 19, 2016 — Why the New Pokémon Are Called 'Sun and Moon'**

因此之前一些二手页面出现的 10/29 应视作元数据差异或错误，不应继续用作主要日期。

状态仍为：

`DIRECT_INTERVIEW / HIGH_CONFIDENCE_EVENT`

地点仍待独立证明。

---

## USgamer 日期锁定为 2016-10-19

原题：

**Interview: First-time Pokémon Director Shigeru Ohmori Opens Up About Sun and Moon**

作者：

Kat Bailey

日期：

**2016-10-19**

USgamer 后续内容已迁移/被 VG247 体系继承，但大量可靠引用保存了原题、作者、日期。

状态：

`DIRECT_INTERVIEW / HIGH_CONFIDENCE_EVENT`

地点仍未恢复。

---

## Polygon / The Verge：本轮暂未发现 2016-10-19 direct interview

搜索结果中：

- Polygon 的相关 Sun/Moon 内容主要是 9 月角色新闻、评测等；
- The Verge 明确的 Ohmori interview 高价值结果集中在 **2017 Ultra Sun / Ultra Moon**。

因此本轮暂不把二者列为 SF 12 强候选。

状态：

`NO_DIRECT_EVIDENCE_FOUND_THIS_ROUND`

---

## VentureBeat / GamesBeat

本轮找到 Dean Takahashi 在 2016 San Francisco Pokémon World Championships 对 TPCI J.C. Smith 的采访：

https://gamesbeat.com/how-pokemon-go-is-boosting-the-pokemon-world-championships/

但采访对象不是 Masuda / Ohmori，时间也在 8 月。

因此：

`EXCLUDE_FROM_SF12`

---

# 25. 一个新的反查方向：2014 与 2016 都应使用“quote family”而不是仅搜媒体名

2014 Centro Pokémon 已经证明，同一个 press day 的回答会被拆散到：

- trainer customization
- difficulty
- random encounters
- New 3DS
- Amiibo
- Mega Evolution
- post-game
- Virtual Console

所以检索原媒体时，应该用“答案句子”而不是单纯：

```text
Masuda Ohmori interview
```

建议建立 quote fingerprints：

```text
"kids these days ... much more busy"
"free games you can play on your phone"
"special thing for the Kalos region"
"competition, imitation, surprise"
"if we can find some really cool way to use Amiibo"
"November 21 2012"
"remakes exactly 12 years after"
```

然后分别限定：

```text
site:ign.com
site:computerandvideogames.com / CVG
site:kotaku.com
site:gonintendo.com
site:usgamer.net
```

同理，2016 SF 可建立：

```text
"meaning of Pokemon"
"least favorite Pokemon"
"Hawaii"
"Pokemon Go connectivity"
"Yungoos Trump"
"too much water"
"Masuda Method"
```

用回答组合判断是否来自同一 interview session。

---

# 26. 本轮后的恢复度

## 2014 Frankfurt

相比 v0.4：

**Spain 已从未知 → 3DJuegos CONFIRMED_LOCATION**

目前强核心至少：

1. Multiplayer.it — Italy
2. 3DJuegos — Spain
3. ntower — Germany
4. Gameblog — France

另有同日 direct：

- USgamer
- GameSpot
- Game Informer

但地点未定。

## 2016 SF 12

本轮没有为了数量强行新增媒体。

保持：

- 7 confirmed / high-confidence
- IGN = strong direct candidate
- Kotaku = direct phone interview, not yet counted

即：

**7 + 1 strong candidate / 12**

这是比把 10/19 所有采访一股脑算成 SF 更可靠的状态。

---

# 27. 下一轮最优检索顺序

## A. 2014 Frankfurt：从 4 国扩到 UK / Netherlands

优先恢复：

### UK
- CVG
- Official Nintendo Magazine UK
- GamesMaster
- Eurogamer
- Nintendo Life

### Netherlands
- Power Unlimited
- Gamer.nl
- InsideGamer
- [N]Gamer
- IGN Benelux

## B. 对 Centro Pokémon source pool 做逐条 fingerprint

尤其是：

- CVG
- IGN
- Kotaku
- GoNintendo

目标不是证明“它们报道过”，而是判断：
**哪些问题是各媒体自己问的，哪些只是转载。**

## C. SF 12

下一轮应放弃 Polygon / Verge 泛搜，转向：

- IGN 2016 原视频 / 页面缓存
- TIME 作者 Matt Peckham 的采访地点线索
- USgamer / Kat Bailey 的行程与原始页面缓存
- Game Informer 作者 Kyle Hilliard 的采访地点线索
- GamesRadar / Eurogamer / GameXplain 视频背景与上传说明

这几个已经是 direct interview，找到地点证据的收益远高于继续寻找全新媒体。

---

> v0.5 的核心进展：
>
> **2014 Frankfurt 已确认覆盖 Germany / France / Italy / Spain 四个国家；3DJuegos 是本轮最重要的新 confirmed attendee。**
>
> 同时 Centro Pokémon 的 source footer 恢复出一批 2014 原始媒体池，为下一轮 UK / North America 的逆向复原提供了明确入口。

