$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$venvMineru = Join-Path $root ".venv-mineru\Scripts\mineru.exe"
$inputPath = Join-Path $root "DREAM 2008.12\page001.jpg"
$outputPath = Join-Path $root ("ocr-output-mineru-dream2008-page001-pipeline-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
$cacheRoot = Join-Path $root ".mineru-cache"

New-Item -ItemType Directory -Force `
  -Path `
    (Join-Path $cacheRoot "modelscope"), `
    (Join-Path $cacheRoot "modelscope-credentials"), `
    (Join-Path $cacheRoot "huggingface") | Out-Null

$env:MODELSCOPE_CACHE = Join-Path $cacheRoot "modelscope"
$env:MODELSCOPE_CREDENTIALS_PATH = Join-Path $cacheRoot "modelscope-credentials"
$env:HF_HOME = Join-Path $cacheRoot "huggingface"
$env:HUGGINGFACE_HUB_CACHE = Join-Path $env:HF_HOME "hub"
$env:MINERU_TOOLS_CONFIG_JSON = Join-Path $cacheRoot "mineru.json"
$env:MINERU_MODEL_SOURCE = "local"
$env:MINERU_API_MAX_CONCURRENT_REQUESTS = "1"
$env:MINERU_LOG_LEVEL = "INFO"

Write-Host "Input:  $inputPath"
Write-Host "Output: $outputPath"
Write-Host "Cache:  $cacheRoot"
Write-Host "Backend: pipeline OCR"
Write-Host "Model source: local"

& $venvMineru -p $inputPath -o $outputPath -b pipeline -m ocr -l ch -f false -t false
