param(
  [ValidateSet("turbomind", "pytorch")]
  [string]$Backend = "turbomind",
  [int]$Port = 5066
)

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$python = Join-Path $root ".venv-mineru\Scripts\python.exe"
$cacheRoot = Join-Path $root ".mineru-cache"

$env:MODELSCOPE_CACHE = Join-Path $cacheRoot "modelscope"
$env:MODELSCOPE_CREDENTIALS_PATH = Join-Path $cacheRoot "modelscope-credentials"
$env:HF_HOME = Join-Path $cacheRoot "huggingface"
$env:HUGGINGFACE_HUB_CACHE = Join-Path $env:HF_HOME "hub"
$env:MINERU_TOOLS_CONFIG_JSON = Join-Path $cacheRoot "mineru.json"
$env:MINERU_MODEL_SOURCE = "local"
$env:MINERU_API_MAX_CONCURRENT_REQUESTS = "1"
$env:MINERU_LMDEPLOY_BACKEND = $Backend
$env:MINERU_LMDEPLOY_DEVICE = "cuda"
$env:MINERU_LOG_LEVEL = "DEBUG"
$env:PYTORCH_CUDA_ALLOC_CONF = "expandable_segments:True"

Write-Host "Starting MinerU API with VLM preload"
Write-Host "URL: http://127.0.0.1:$Port"
Write-Host "Backend: $Backend"
Write-Host "Press Ctrl+C to stop."

& $python -m mineru.cli.fast_api --host 127.0.0.1 --port $Port --enable-vlm-preload true
