# 多栏阅读顺序检测 V3：两轮情景测试

测试日期：2026-08-25  
布局模型：`qwen3.7-plus`  
OCR 模型：`qwen-vl-ocr-latest`

## 本次增强

- 使用图像文字结构保守复核横排/竖排方向；置信度不足时保留人工/分区标记，不强行纠正。
- 检出物理栏后实际裁成独立输入，而不是只要求模型在整框中自行判断列序。
- 竖排栏按视觉位置从右到左合并；横排版面栏按左到右合并。
- 将自动修正后的有效方向和物理栏数写入 OCR JSON、Markdown、翻译工作台 YAML 与项目队列。
- 栏数超过上限、逐栏 OCR 有空结果、栏宽差异过大、坐标输出等情况进入返工队列。
- 短输出中的单行坐标现在也会被识别、清除并送入快速复核。
- 分区提示进一步禁止跨越栏间空白的巨大正文框，并要求在竖排列间留白处分界，区分大标题、正文和栏外注。

## 第一轮：高密度日文竖排

### 样本

5 张页面：

- `谎言的真相 2000.5/page003.jpg`
- `谎言的真相 2000.5/page004.jpg`
- `谎言的真相 2001.4/page009.jpg`
- `谎言的真相 2001.4/page010.jpg`
- `DP anime/paper075.jpg`

包含跨页中缝、超长竖列、大标题、图片插入和座谈正文。

### 全页分区审计

- 71 个区域：65 个文字/图注/附注，6 个图片
- 47 个文字区域检测到多栏
- 42 个可在 16 栏上限内自动拆分
- 5 个区域检测到 23–25 栏，超出合理自动调用范围，应重新划成较小区域
- 没有出现高置信度的方向误标冲突

若将全部多栏逐栏调用，约需识别 315 个物理栏。因此 A/B 采用“全页分区审计 + 每页一个代表性区域”的方式，避免为了测试产生不必要调用。

### 代表区域 A/B

5 个代表区域分别含 5、3、6、2、8 个物理栏。

| 方案 | 自动逐栏 | 直接进入翻译 | 进入返工 | 说明 |
| --- | ---: | ---: | ---: | --- |
| 原整框 OCR | 0/5 | 4 | 1 | 模型自行猜列序；一个区域出现坐标输出 |
| V3 逐栏 OCR | 5/5 | 2 | 3 | 明确右→左合并；3 个混有残列/大标题或严重振假名的区域被识别为高风险 |

重要观察：

- 老杂志 `page003` 的代表区域中，整框 OCR 从视觉最左列开始；V3 从正确的视觉最右列开始，并按右→左继续。
- `paper075` 中 V3 保持了右→左顺序，同时去掉了整框 OCR 末尾出现的重复段。
- 三个旧扫描区域的栏宽差异很大，实际混入了裁断边缘列、大标题或不同字号。V3 没有把它们误当成安全结果，而是继续保留 OCR 文本并送入返工。
- 因此 V3 的“直接放行数”下降并不是退化，而是风险路由更准确。

## 第二轮：现代横排图文混排

### 样本

`FAMI 2013.11.14` 的 `page002`、`page003`、`page008`、`page011`、`page012`，覆盖新闻照片拼贴、销售图表、攻略卡片、三栏访谈、人物照片与角色图。

### 全页分区审计

- 100 个区域：73 个文字/图注/附注，27 个图片
- 5 个文字区域检测到多栏，全部在自动拆分上限内
- 没有栏数超限
- 没有高置信度方向冲突，说明保守阈值没有把规则网格和横排正文误改成竖排

### 代表区域 A/B

每页抽取一个区域；其中 3 个是多栏，2 个是普通单栏控制区。

| 方案 | 自动逐栏 | 直接进入翻译 | 进入返工 | 说明 |
| --- | ---: | ---: | ---: | --- |
| 原整框 OCR | 0/5 | 5 | 0 | 无高风险提示 |
| V3 逐栏 OCR | 3/5 | 4 | 1 | 两个普通控制区不拆分；短注释的坐标输出已自动清理并进入快速复核 |

重要观察：

- 三个横排卡片的内容按 1→2→3 保持左→右顺序。
- 两个普通正文控制区没有被错误拆栏，文字量与基线基本一致。
- 页码/“次ページへ続く”短注释首次返回坐标；修正规则后最终文本恢复为 `次ページへ続く / 129`，同时项目队列保留坐标恢复标记以便快速核对。

## 结论

V3 已解决上一轮最核心的“模型在整框里自行猜列序”问题，并且没有在现代横排版式中造成明显误纠正。当前最可靠的自动化边界是：

1. 2–16 栏、字号接近、边界完整的区域可以逐栏 OCR 后自动合并。
2. 超过 16 栏的区域不应直接产生大量 API 请求，应回到分区阶段拆小。
3. 栏宽差异很大、边缘残列、大标题与正文同框时，即使逐栏 OCR 成功，也应进入返工。
4. 项目队列的“ready”表示未触发当前高风险规则，不代表出版级校对完成。

## 调用量

- 10 页布局分析：10 次成功页面分析
- 第一轮 OCR：基线约 6 次（含一次坐标恢复），V3 24 次
- 第二轮 OCR：基线 5 次，V3 首轮约 11 次；短注释定点复测约 3 次
- 本轮总计约 59 次模型请求。布局接口内部若因 JSON 解析自动重试，服务端当前不会回传该次数，因此这里记录的是可观测/可推算调用量。

## 产物

### 第一轮

- `automation-tests/multicol-v3-round-a-vertical-20260825/layout-results.json`
- `automation-tests/multicol-v3-round-a-vertical-20260825/column-audit.json`
- `automation-tests/multicol-v3-round-a-vertical-20260825/baseline-whole-region/regions-ocr.md`
- `automation-tests/multicol-v3-round-a-vertical-20260825/enhanced-column-split/regions-ocr.md`
- `automation-tests/multicol-v3-round-a-vertical-20260825/enhanced-column-split/translation-segments.yml`
- `automation-tests/multicol-v3-round-a-vertical-20260825/enhanced-column-split/project-queue.json`

### 第二轮

- `automation-tests/multicol-v3-round-b-horizontal-mixed-20260825/layout-results.json`
- `automation-tests/multicol-v3-round-b-horizontal-mixed-20260825/column-audit.json`
- `automation-tests/multicol-v3-round-b-horizontal-mixed-20260825/baseline-whole-region/regions-ocr.md`
- `automation-tests/multicol-v3-round-b-horizontal-mixed-20260825/enhanced-column-split/regions-ocr.md`
- `automation-tests/multicol-v3-round-b-horizontal-mixed-20260825/enhanced-column-split/translation-segments.yml`
- `automation-tests/multicol-v3-round-b-horizontal-mixed-20260825/enhanced-column-split/project-queue.json`

## 验证

- 22 项 Python 自动测试全部通过
- PowerShell 批处理脚本语法检查通过
- 翻译工作台 YAML 导入兼容测试通过
