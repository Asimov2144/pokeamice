param(
  [Parameter(Mandatory = $true)]
  [string]$AnnotationJson,
  [Parameter(Mandatory = $true)]
  [string]$ImageDir,
  [string]$Out = "ocr-output-region-paddle",
  [string]$Lang = "japan",
  [string]$Device = "gpu:0",
  [switch]$GpuEnv,
  [switch]$Fast,
  [switch]$QualityRec,
  [switch]$JapanRec,
  [switch]$DeepSeek,
  [string]$DeepSeekModel = "deepseek-chat",
  [int]$DeepSeekLimit = 0,
  [int]$Padding = 16,
  [int]$CropMaxPixels = 0,
  [int]$TimeoutSeconds = 180,
  [switch]$SkipExisting
)

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv-ocr\Scripts\python.exe"
if ($GpuEnv) {
  $python = Join-Path $root ".venv-ocr-gpu\Scripts\python.exe"
}
$outPath = if ([System.IO.Path]::IsPathRooted($Out)) {
  $Out
} else {
  Join-Path $root $Out
}
$cropScript = Join-Path $root "tools\ocr_regions_from_annotation.py"
$cropsDir = Join-Path $outPath "crops"
$ocrDir = Join-Path $outPath "ocr"

New-Item -ItemType Directory -Force -Path $outPath, $ocrDir | Out-Null

Write-Host "1/3 裁切分区..."
& $python $cropScript --annotation $AnnotationJson --images $ImageDir --out $outPath --padding $Padding --max-crop-pixels $CropMaxPixels
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "2/3 对分区逐块 OCR..."
$batchParams = @{
  InputPath = $cropsDir
  Out = $ocrDir
  Lang = $Lang
  Device = $Device
  TimeoutSeconds = $TimeoutSeconds
}
if ($GpuEnv) { $batchParams.GpuEnv = $true }
if ($Fast) { $batchParams.Fast = $true }
if ($QualityRec) { $batchParams.QualityRec = $true }
if ($JapanRec) { $batchParams.JapanRec = $true }
if ($SkipExisting) { $batchParams.SkipExisting = $true }
& (Join-Path $PSScriptRoot "run-paddle-ocr-safe-batch.ps1") @batchParams

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
