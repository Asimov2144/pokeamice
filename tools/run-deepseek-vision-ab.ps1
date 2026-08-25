param(
  [string]$InputDir = "ocr-ab-tests\deepseek-vision-dream-5\input",
  [string]$OutDir = "ocr-ab-tests\deepseek-vision-dream-5\deepseek",
  [string]$Model = "deepseek-v4-flash-vision-exp",
  [int]$MaxTokens = 4096,
  [switch]$SkipExisting
)

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv-ocr\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
  $python = Join-Path $root ".venv-ocr-gpu\Scripts\python.exe"
}
if (-not (Test-Path -LiteralPath $python)) {
  throw "OCR Python environment was not found."
}
if (-not $env:DEEPSEEK_API_KEY) {
  throw "DEEPSEEK_API_KEY is not configured. Configure it locally, then rerun this command."
}

$resolvedInput = if ([System.IO.Path]::IsPathRooted($InputDir)) { $InputDir } else { Join-Path $root $InputDir }
$resolvedOut = if ([System.IO.Path]::IsPathRooted($OutDir)) { $OutDir } else { Join-Path $root $OutDir }
$prompt = Get-Content -LiteralPath (Join-Path $root "tools\prompts\magazine-ocr-layout-ja.txt") -Raw -Encoding UTF8

$arguments = @(
  (Join-Path $root "tools\vlm_api_ocr_regions.py"),
  $resolvedInput,
  "--out", $resolvedOut,
  "--api-url", "https://api.deepseek.com",
  "--model", $Model,
  "--image-detail", "original",
  "--disable-thinking",
  "--max-tokens", $MaxTokens,
  "--temperature", 0,
  "--retries", 2,
  "--prompt", $prompt
)
if ($SkipExisting) { $arguments += "--skip-existing" }

& $python @arguments
exit $LASTEXITCODE
