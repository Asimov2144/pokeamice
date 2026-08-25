param(
  [ValidateSet("v1", "v1.5", "v1.6")]
  [string]$PipelineVersion = "v1.6",
  [string]$Device = "gpu:0",
  [switch]$NoLayout
)

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv-ocr-gpu\Scripts\python.exe"
$sample = Join-Path $root "DREAM 2008.12\page001.jpg"
if (-not (Test-Path -LiteralPath $sample)) {
  $sample = "F:\Pokeamice\DREAM 2008.12改\tuya\page001-tuya.jpg"
}

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

Write-Host "Preparing PaddleOCR-VL $PipelineVersion"
Write-Host "Cache: $env:PADDLE_PDX_CACHE_HOME"
Write-Host "Sample: $sample"

$argsList = @(
  (Join-Path $root "tools\paddle_ocr_vl_test.py"),
  $sample,
  "--out", "ocr-output-paddle-vl-warmup",
  "--device", $Device,
  "--pipeline-version", $PipelineVersion,
  "--limit", "1",
  "--max-pixels", "250000",
  "--max-new-tokens", "256",
  "--heartbeat-seconds", "20"
)
if ($NoLayout) {
  $argsList += "--no-layout"
}

& $python @argsList
