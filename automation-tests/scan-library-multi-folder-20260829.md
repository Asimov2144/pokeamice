# 扫描图库多文件夹预处理测试

日期：2026-08-29

本轮从 `E:\Pokeamice\scan` 抽取三种版式，每个文件夹处理 5 页。原始扫描文件未修改，输出均写入 `scan-prepared/`。

## 文件夹结果

| 文件夹 | 处理 | 可继续 | 返工 | 分页 | 调色 | 模型调用 | 错误 |
|---|---:|---:|---:|---:|---:|---:|---:|
| DREAM 2008.10 | 5 | 4 | 1 | 0 | 1 | 0 | 0 |
| Continue Vol.31 | 5 | 0 | 5 | 0 | 5 | 5 | 0 |
| DP anime | 5 | 4 | 1 | 0 | 4 | 0 | 0 |

## 返工原因

- DREAM 2008.10：1 页检测到外边缘未完全裁净。
- Continue Vol.31：5 页视觉模型请求失败或置信度不足，全部保留人工复核。
- DP anime：1 页检测到外边缘未完全裁净。

## 自动分区抽检

- DREAM 2008.10 `inpainted/page001.jpg`：10 个分区，2 个图片区。
- Continue Vol.31 `page033.jpg`：8 个分区，检测到 1 个图片/文字混合风险。
- DP anime `out/cache/automask/paper077.jpg`：3 个分区，检测到 1 个图片/文字混合风险。

## 输出

- [DREAM 2008.10 清单](../scan-prepared/dream-2008-10-20260829-sample5/scan-manifest.json)
- [Continue Vol.31 清单](../scan-prepared/continue-vol31-20260829-sample5/scan-manifest.json)
- [DP anime 清单](../scan-prepared/dp-anime-20260829-sample5/scan-manifest.json)
- [DREAM 自动分区](dream-2008-10-current-flow-layout-20260829/magazine-regions.json)
- [Continue 自动分区](continue-vol31-current-flow-layout-20260829/magazine-regions.json)
- [DP anime 自动分区](dp-anime-current-flow-layout-20260829/magazine-regions.json)

## 结论

当前流程对常规 PNG/JPEG 扫描件可以稳定完成裁切、调色和 Web/Archive 输出；视觉模型不可用时会安全进入返工队列。DP anime 的 TIFF 文件存在多层目录，当前会保留原目录结构，后续批处理时应在队列界面显示“原始相对路径”，避免只显示文件名造成混淆。

## 当前 Qwen 付费路由复测

将页面仲裁模型从受免费额度限制的 `qwen3-vl-flash` 切换为当前可用的 `qwen3.7-plus`，并继续使用 `qwen-vl-ocr-latest` 做分区 OCR。

- Continue Vol.31 重新处理 5 页：4 页可继续、1 页返工、3 张跨页自动拆分、0 个 API 错误。
- DREAM 抽检页：10 个分区，9 个可进入翻译，1 个坐标输出风险进入快速复核。
- Continue 抽检页：8 个分区，4 个可进入翻译，4 个因方向冲突、坐标输出或异质竖栏进入返工。
- DP anime 抽检页：3 个分区，其中 1 个图片区、2 个图注区，全部可进入翻译。

输出：

- [Continue qwen3.7-plus 预处理清单](../scan-prepared/continue-vol31-20260829-sample5-qwen37/scan-manifest.json)
- [DREAM Qwen OCR](dream-2008-10-current-flow-ocr-qwen-20260829/regions-ocr.md)
- [Continue Qwen OCR](continue-vol31-current-flow-ocr-qwen-20260829/regions-ocr.md)
- [DP anime Qwen OCR](dp-anime-current-flow-ocr-qwen-20260829/regions-ocr.md)

## 三个目录完整跑批（2026-08-29）

本轮按“预处理 → 页级分页 → Qwen 自动分区 → Qwen OCR → 半自动项目队列”完整执行。原始扫描文件未修改；Vol.23 中的 `out/cache/thumbs` 缩略图也已自动排除，避免重复处理。

| 项目 | 准备页 | 自动分区 | OCR 调用 | 可直接翻译 | 返工队列 | 图片区 |
|---|---:|---:|---:|---:|---:|---:|
| Continue Vol.23 / tuya | 11 | 93 | 72 | 52 | 41 | 21 |
| Continue Vol.31 | 33 | 362 | 253 | 278 | 84 | 109 |
| Continue Vol.32 | 16 | 126 | 112 | 48 | 78 | 14 |

### Vol.23 / tuya

- [预处理清单](../scan-prepared/continue-vol23-tuya-full-20260829/scan-manifest.json)
- [自动分区标注](continue-vol23-full-layout-20260829/magazine-regions.json)
- [OCR Markdown](continue-vol23-full-ocr-20260829/regions-ocr.md)
- [项目队列](continue-vol23-full-ocr-20260829/project-queue.json)

### Vol.31

- [预处理清单](../scan-prepared/continue-vol31-full-20260829/scan-manifest.json)
- [自动分区标注](continue-vol31-full-layout-20260829/magazine-regions.json)
- [OCR Markdown](continue-vol31-full-ocr-20260829/regions-ocr.md)
- [项目队列](continue-vol31-full-ocr-20260829/project-queue.json)

### Vol.32

- [预处理清单](../scan-prepared/continue-vol32-full-20260829/scan-manifest.json)
- [自动分区标注](continue-vol32-full-layout-20260829/magazine-regions.json)
- [OCR Markdown](continue-vol32-full-ocr-20260829/regions-ocr.md)
- [项目队列](continue-vol32-full-ocr-20260829/project-queue.json)

本轮使用 `qwen3.7-plus` 做页面/分区判断，使用 `qwen-vl-ocr-latest` 做区域 OCR；方向冲突、重复文本、坐标倾向、竖栏不完整和图文混框等风险均保留在队列中，未自动替换为“可靠”结果。翻译模板 YAML 已随 OCR 同步生成，后续可在工作台按队列批量翻译或先处理返工项。
