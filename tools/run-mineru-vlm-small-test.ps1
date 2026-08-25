param(
  [ValidateSet("turbomind", "pytorch")]
  [string]$Backend = "turbomind",
  [int]$MaxSide = 1600
)

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$python = Join-Path $root ".venv-mineru\Scripts\python.exe"
$venvMineru = Join-Path $root ".venv-mineru\Scripts\mineru.exe"
$sourcePath = Join-Path $root "DREAM 2008.12\page001.jpg"
$tmpDir = Join-Path $root ".mineru-cache\test-inputs"
$inputPath = Join-Path $tmpDir "page001-small.jpg"
$outputPath = Join-Path $root ("ocr-output-mineru-dream2008-page001-vlm-small-" + $Backend + "-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
$cacheRoot = Join-Path $root ".mineru-cache"

New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null

& $python -c @"
from PIL import Image
src = r"$sourcePath"
dst = r"$inputPath"
max_side = int("$MaxSide")
img = Image.open(src).convert("RGB")
scale = min(1.0, max_side / max(img.size))
if scale < 1.0:
    img = img.resize((round(img.width * scale), round(img.height * scale)))
img.save(dst, quality=92)
print(dst, img.size)
"@

$env:MODELSCOPE_CACHE = Join-Path $cacheRoot "modelscope"
$env:MODELSCOPE_CREDENTIALS_PATH = Join-Path $cacheRoot "modelscope-credentials"
$env:HF_HOME = Join-Path $cacheRoot "huggingface"
$env:HUGGINGFACE_HUB_CACHE = Join-Path $env:HF_HOME "hub"
$env:MINERU_TOOLS_CONFIG_JSON = Join-Path $cacheRoot "mineru.json"
$env:MINERU_MODEL_SOURCE = "local"
$env:MINERU_API_MAX_CONCURRENT_REQUESTS = "1"
$env:MINERU_LMDEPLOY_BACKEND = $Backend
$env:MINERU_LMDEPLOY_DEVICE = "cuda"
$env:MINERU_LOG_LEVEL = "INFO"
$env:PYTORCH_CUDA_ALLOC_CONF = "expandable_segments:True"

Write-Host "Input:  $inputPath"
Write-Host "Output: $outputPath"
Write-Host "LMDeploy backend: $Backend"

& $venvMineru -p $inputPath -o $outputPath -b vlm-engine --image-analysis false
