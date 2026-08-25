param(
  [Parameter(Mandatory = $true)]
  [string]$NotebookPath,
  [string]$Model = "qwen-vl-ocr-latest",
  [switch]$PersistUser
)

$resolved = Resolve-Path -LiteralPath $NotebookPath -ErrorAction Stop
$notebook = Get-Content -LiteralPath $resolved.Path -Raw -Encoding UTF8 | ConvertFrom-Json
$text = (($notebook.cells | ForEach-Object { $_.source }) -join "`n")

$apiKey = [regex]::Match($text, "sk-ws-[A-Za-z0-9._\-]+").Value.Trim()
$apiUrl = [regex]::Match($text, "https://[^\s]+/compatible-mode/v1").Value.Trim()

if (-not $apiKey) {
  throw "Cannot find sk-ws API key in notebook."
}
if (-not $apiUrl) {
  throw "Cannot find compatible-mode/v1 API URL in notebook."
}

$env:VLM_OCR_API_KEY = $apiKey
$env:DASHSCOPE_API_KEY = $apiKey
$env:VLM_OCR_API_URL = $apiUrl
$env:VLM_OCR_MODEL = $Model

if ($PersistUser) {
  [Environment]::SetEnvironmentVariable("VLM_OCR_API_KEY", $apiKey, "User")
  [Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", $apiKey, "User")
  [Environment]::SetEnvironmentVariable("VLM_OCR_API_URL", $apiUrl, "User")
  [Environment]::SetEnvironmentVariable("VLM_OCR_MODEL", $Model, "User")
}

$preview = if ($apiKey.Length -gt 12) { $apiKey.Substring(0, 6) + "..." + $apiKey.Substring($apiKey.Length - 4) } else { "[short]" }
Write-Host "Qwen API configured from notebook."
Write-Host "Model: $Model"
Write-Host "API URL: $apiUrl"
Write-Host "API Key: $preview"
if ($PersistUser) {
  Write-Host "Saved to User environment variables. Restart PowerShell to use it in new windows."
} else {
  Write-Host "Configured for this PowerShell session only."
}
