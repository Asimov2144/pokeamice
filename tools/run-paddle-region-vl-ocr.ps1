param(
  [Parameter(Mandatory = $true)]
  [string]$AnnotationJson,
  [Parameter(Mandatory = $true)]
  [string]$ImageDir,
  [string]$Out = "ocr-output-region-paddle-vl",
  [string]$Device = "gpu:0",
  [ValidateSet("v1", "v1.5", "v1.6")]
  [string]$PipelineVersion = "v1.6",
  [int]$Padding = 16,
  [int]$CropMaxPixels = 250000,
  [int]$MaxNewTokens = 256,
  [int]$MaxPixels = 250000,
  [int]$HeartbeatSeconds = 30,
  [int]$TimeoutSeconds = 180,
  [int]$Retries = 1,
  [int]$CooldownSeconds = 6,
  [int]$MinFreeMemoryMb = 0,
  [int]$GpuWaitSeconds = 90,
  [switch]$NoLayout,
  [switch]$SkipExisting,
  [switch]$DeepSeek,
  [string]$DeepSeekModel = "deepseek-chat",
  [int]$DeepSeekLimit = 0
)

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv-ocr-gpu\Scripts\python.exe"
$outPath = if ([System.IO.Path]::IsPathRooted($Out)) {
  $Out
} else {
  Join-Path $root $Out
}
$cropScript = Join-Path $root "tools\ocr_regions_from_annotation.py"
$vlScript = Join-Path $root "tools\paddle_ocr_vl_test.py"
$cropsDir = Join-Path $outPath "crops"
$ocrDir = Join-Path $outPath "ocr-vl"

$env:HOME = Join-Path $root ".ocr-home"
$env:USERPROFILE = $env:HOME
$env:PADDLE_HOME = Join-Path $root ".ocr-home\paddle"
$env:XDG_CACHE_HOME = Join-Path $root ".ocr-home\cache"
$env:PADDLE_PDX_CACHE_HOME = Join-Path $root ".paddlex-cache"
$env:PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT = "False"
$env:FLAGS_use_mkldnn = "false"
$env:PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK = "False"
$env:FLAGS_allocator_strategy = "auto_growth"
$env:FLAGS_fraction_of_gpu_memory_to_use = "0.82"

New-Item -ItemType Directory -Force -Path $outPath, $ocrDir | Out-Null

Write-Host "1/3 裁切分区..."
& $python $cropScript --annotation $AnnotationJson --images $ImageDir --out $outPath --padding $Padding --max-crop-pixels $CropMaxPixels
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "2/3 PaddleOCR-VL 安全批处理识别分区..."
$vlBatchParams = @{
  InputPath = $cropsDir
  Out = $ocrDir
  Device = $Device
  PipelineVersion = $PipelineVersion
  MaxNewTokens = $MaxNewTokens
  MaxPixels = $MaxPixels
  HeartbeatSeconds = $HeartbeatSeconds
  TimeoutSeconds = $TimeoutSeconds
  Retries = $Retries
  CooldownSeconds = $CooldownSeconds
  MinFreeMemoryMb = $MinFreeMemoryMb
  GpuWaitSeconds = $GpuWaitSeconds
}
if ($NoLayout) { $vlBatchParams.NoLayout = $true }
if ($SkipExisting) { $vlBatchParams.SkipExisting = $true }
& (Join-Path $PSScriptRoot "run-paddle-vl-safe-batch.ps1") @vlBatchParams

Write-Host "3/3 合并 Markdown / 模板 YAML..."
& $python $cropScript --annotation $AnnotationJson --images $ImageDir --out $outPath --ocr-dir $ocrDir --merge-only

if ($DeepSeek) {
  Write-Host "4/4 DeepSeek 校对 / 翻译..."
  $deepSeekScript = Join-Path $root "tools\deepseek_correct_region_ocr.py"
  $deepSeekArgs = @(
    $deepSeekScript,
    "--out", $outPath,
    "--ocr-dir", $ocrDir,
    "--model", $DeepSeekModel
  )
  if ($DeepSeekLimit -gt 0) {
    $deepSeekArgs += @("--limit", $DeepSeekLimit)
  }
  & $python @deepSeekArgs
}
