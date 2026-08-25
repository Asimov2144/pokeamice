param(
  [Parameter(Mandatory = $true)]
  [string]$InputPath,
  [string]$Out = "ocr-output-paddle-vl",
  [string]$Device = "gpu:0",
  [ValidateSet("v1", "v1.5", "v1.6")]
  [string]$PipelineVersion = "v1.6",
  [ValidateSet("native", "vllm-server", "sglang-server", "fastdeploy-server", "mlx-vlm-server", "llama-cpp-server")]
  [string]$Backend = "native",
  [int]$Limit = 0,
  [switch]$NoLayout,
  [int]$MaxNewTokens = 256,
  [int]$MaxPixels = 250000,
  [int]$HeartbeatSeconds = 30,
  [switch]$FlatOutput,
  [int]$InputMaxPixels = 0
)

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv-ocr-gpu\Scripts\python.exe"

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

$actualInput = $InputPath
if ($InputMaxPixels -gt 0) {
  $tmpDir = Join-Path $root ".paddlex-cache\vl-test-inputs"
  New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null
  $tmpInput = Join-Path $tmpDir (([IO.Path]::GetFileNameWithoutExtension($InputPath)) + "_max${InputMaxPixels}.jpg")
  & $python -c @"
from pathlib import Path
from PIL import Image
src = Path(r"$InputPath")
dst = Path(r"$tmpInput")
img = Image.open(src).convert("RGB")
pixels = img.width * img.height
limit = int("$InputMaxPixels")
if pixels > limit:
    scale = (limit / pixels) ** 0.5
    img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.Resampling.LANCZOS)
img.save(dst, quality=95)
print(dst)
"@
  $actualInput = $tmpInput
}

$argsList = @(
  (Join-Path $root "tools\paddle_ocr_vl_test.py"),
  $actualInput,
  "--out", $Out,
  "--device", $Device,
  "--pipeline-version", $PipelineVersion,
  "--backend", $Backend,
  "--limit", $Limit,
  "--max-new-tokens", $MaxNewTokens,
  "--max-pixels", $MaxPixels,
  "--heartbeat-seconds", $HeartbeatSeconds
)
if ($NoLayout) {
  $argsList += "--no-layout"
}
if ($FlatOutput) {
  $argsList += "--flat-output"
}

& $python @argsList
