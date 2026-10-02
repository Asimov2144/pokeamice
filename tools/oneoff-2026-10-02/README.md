# 2026-10-02 新帖核对用的一次性脚本

背景与结论见 `design/new-posts-audit-2026-10-02.md`。这里只放留档，路径是写死的（`P:/WEBSITE/pokeamice-main (1)/app-data-export`），再用时先改路径。

| 脚本 | 干什么 |
|---|---|
| import_iwata2011.py | 读 2011 年版式的社長が訊く（int-box / int-name / int-text / notes-box），翻译和写帖用 import-web 自己的函数 |
| import_recruit_old.py | GAME FREAK 2015 / 宝可梦公司 2014 两个老招聘页（dt 里图片 alt 是说话人；p.question / p.answer）；`--fill-pictures` 把 Wayback 429 掉的图用旧文件夹补回 |
| fix_creatures.py / fix_hobonichi.py / fix_denfami.py | 重导后的版式修整：简介并成一行、栏目标题升成小标题、员工旁白的说话人、※ 注释并成「编者注」 |
| review_ds2.py | review-translations.py 的同一套提示词换成 DeepSeek reasoner（max_tokens 32000、每批 14 行，否则推理把输出吃光返回空），批次并行；缓存 data/cache_review_ds/（不提交） |
| review_qwen.py | 同上，用 Qwen（工具原本的模型），缓存 data/cache_review_qwen/（不提交） |
| show_diff.py | 把审校结果按「现→改」的差异段列出来，逐条读 |
| apply_review.py + decisions_*.json | 按我逐条定下的采纳 / 驳回 / 自拟改法，用 rowedit 写回；译文在审校之后又被改过的行跳过 |
| retranslate.py | 整篇按原文重译（import-web 的译法），用于三分之一以上的行被改写的帖子 |
| multipage.py / reverse.py | 来源核对：多页一起当来源；反向看原页哪些段没进帖子 |
