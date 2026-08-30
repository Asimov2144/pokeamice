param(
  [Parameter(Mandatory = $true)]
  [string]$AnnotationJson,
  [Parameter(Mandatory = $true)]
  [string]$ImageDir,
  [string]$Out = "ocr-output-region-vlm-api",
  [string]$ApiUrl = "",
  [string]$ApiKey = "",
  [string]$Model = "qwen-vl-ocr-latest",
  [int]$Padding = 16,
  [int]$CropMaxPixels = 0,
  [int]$MaxTokens = 768,
  [int]$Retries = 1,
  [int]$RetryDelaySeconds = 4,
  [int]$MaxAutoColumns = 16,
  [string]$Prompt = "",
  [string]$PromptFile = "",
  [switch]$ContinueOnError,
  [switch]$EnableThinking,
  [int]$ThinkingBudget = 0,
  [ValidateSet("auto", "low", "high", "original")]
  [string]$ImageDetail = "auto",
  [switch]$DisableThinking,
  [switch]$SkipExisting,
  [switch]$DisableAutoColumnSplit,
  [switch]$SkipQueue,
  [switch]$DeepSeek,
  [string]$DeepSeekModel = "deepseek-chat",
  [int]$DeepSeekLimit = 0
)

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv-ocr\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
  $python = Join-Path $root ".venv-ocr-gpu\Scripts\python.exe"
}
$outPath = if ([System.IO.Path]::IsPathRooted($Out)) { $Out } else { Join-Path $root $Out }
$cropScript = Join-Path $root "tools\ocr_regions_from_annotation.py"
$vlmScript = Join-Path $root "tools\vlm_api_ocr_regions.py"
$cropsDir = Join-Path $outPath "crops"
$ocrDir = Join-Path $outPath "ocr-vlm-api"
$manifestPath = Join-Path $outPath "region-manifest.json"
$apiKeyWasExplicit = [bool]$ApiKey

if (-not $ApiUrl) { $ApiUrl = $env:VLM_OCR_API_URL }
if (-not $ApiKey -and $Model -match 'deepseek') { $ApiKey = $env:DEEPSEEK_API_KEY }
if (-not $ApiKey -and $Model -notmatch 'deepseek') { $ApiKey = $env:VLM_OCR_API_KEY }
if (-not $ApiKey -and $Model -notmatch 'deepseek') { $ApiKey = $env:DASHSCOPE_API_KEY }
if (-not $ApiKey -and $Model -notmatch 'deepseek') { $ApiKey = $env:QWEN_API_KEY }
if (-not $Model -and $env:VLM_OCR_MODEL) { $Model = $env:VLM_OCR_MODEL }
if (-not $ApiUrl -and $Model -match 'qwen') {
  $ApiUrl = "https://dashscope.aliyuncs.com/compatible-mode/v1"
}
if (-not $ApiUrl -and $Model -match 'deepseek') {
  $ApiUrl = "https://api.deepseek.com"
}
if ($CropMaxPixels -le 0 -and $Model -match 'qwen') {
  $CropMaxPixels = 900000
}
if (-not $Prompt -and $PromptFile) {
  $Prompt = Get-Content -LiteralPath $PromptFile -Raw -Encoding UTF8
}

New-Item -ItemType Directory -Force -Path $outPath, $ocrDir | Out-Null

Write-Host "1/4 裁切分区..."
& $python $cropScript --annotation $AnnotationJson --images $ImageDir --out $outPath --padding $Padding --max-crop-pixels $CropMaxPixels
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "2/4 VLM API OCR..."
$vlmArgs = @(
  $vlmScript,
  $cropsDir,
  "--out", $ocrDir,
  "--api-url", $ApiUrl,
  "--model", $Model,
  "--max-tokens", $MaxTokens,
  "--retries", $Retries,
  "--retry-delay", $RetryDelaySeconds
  "--manifest", $manifestPath
  "--image-detail", $ImageDetail
  "--max-auto-columns", $MaxAutoColumns
)
if ($Prompt) { $vlmArgs += @("--prompt", $Prompt) }
# Environment-configured keys are read directly by the Python worker. Avoid
# copying them into the process command line where diagnostics can expose them.
if ($apiKeyWasExplicit) { $vlmArgs += @("--api-key", $ApiKey) }
if ($SkipExisting) { $vlmArgs += "--skip-existing" }
if ($DisableAutoColumnSplit) { $vlmArgs += "--disable-auto-column-split" }
if ($ContinueOnError) { $vlmArgs += "--continue-on-error" }
if ($EnableThinking) {
  $vlmArgs += "--enable-thinking"
  if ($ThinkingBudget -gt 0) {
    $vlmArgs += @("--thinking-budget", $ThinkingBudget)
  }
}
if ($DisableThinking) { $vlmArgs += "--disable-thinking" }
& $python @vlmArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "3/4 合并 Markdown / 模板 YAML..."
& $python $cropScript --annotation $AnnotationJson --images $ImageDir --out $outPath --ocr-dir $ocrDir --merge-only
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $SkipQueue) {
  Write-Host "4/4 生成半自动项目队列..."
  $queueScript = Join-Path $root "tools\build_ocr_project_queue.py"
  & $python $queueScript --out $outPath --ocr-dir $ocrDir
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
  Write-Host "4/4 Targeted rerun: skip standalone project queue."
}

if ($DeepSeek) {
  if ($SkipQueue) {
    throw "DeepSeek 翻译前必须先生成项目队列；请移除 -SkipQueue。"
  }
  Write-Host "附加步骤：仅校对 / 翻译已通过 OCR 队列的区域..."
  $deepSeekScript = Join-Path $root "tools\deepseek_correct_region_ocr.py"
  $deepSeekArgs = @(
    $deepSeekScript,
    "--out", $outPath,
    "--ocr-dir", $ocrDir,
    "--queue", (Join-Path $outPath "project-queue.json"),
    "--model", $DeepSeekModel
  )
  if ($DeepSeekLimit -gt 0) {
    $deepSeekArgs += @("--limit", $DeepSeekLimit)
  }
  & $python @deepSeekArgs
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
