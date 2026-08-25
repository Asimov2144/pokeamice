param(
  [string]$Model = "qwen3-vl-flash",
  [string]$ApiUrl = ""
)

if (-not $ApiUrl -and $env:VLM_OCR_API_URL) { $ApiUrl = $env:VLM_OCR_API_URL }
if (-not $ApiUrl -and $Model -match "qwen") { $ApiUrl = "https://dashscope.aliyuncs.com/compatible-mode/v1" }

$candidates = @(
  @{ Name = "VLM_OCR_API_KEY"; Value = $env:VLM_OCR_API_KEY },
  @{ Name = "DASHSCOPE_API_KEY"; Value = $env:DASHSCOPE_API_KEY },
  @{ Name = "QWEN_API_KEY"; Value = $env:QWEN_API_KEY }
)

Write-Host "Model: $Model"
Write-Host "API URL: $ApiUrl"

$found = $false
foreach ($item in $candidates) {
  $value = [string]$item.Value
  if ($value) {
    $trimmed = $value.Trim()
    $prefix = if ($trimmed.Length -ge 6) { $trimmed.Substring(0, 6) } else { $trimmed }
    $suffix = if ($trimmed.Length -ge 4) { $trimmed.Substring($trimmed.Length - 4) } else { $trimmed }
    $hasOuterQuotes = ($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))
    Write-Host "$($item.Name): SET length=$($trimmed.Length) preview=$prefix...$suffix outerQuotes=$hasOuterQuotes surroundingSpaces=$($value -ne $trimmed)"
    $found = $true
  } else {
    Write-Host "$($item.Name): empty"
  }
}

if (-not $found) {
  Write-Host "No API key found. Set DASHSCOPE_API_KEY or VLM_OCR_API_KEY in this PowerShell session."
}
