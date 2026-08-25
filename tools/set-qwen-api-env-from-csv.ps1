param(
  [Parameter(Mandatory = $true)]
  [string]$CsvPath,
  [string]$Model = "qwen3-vl-flash",
  [switch]$PersistUser
)

$resolved = Resolve-Path -LiteralPath $CsvPath -ErrorAction Stop
$rows = Import-Csv -LiteralPath $resolved.Path
if (-not $rows) {
  throw "CSV is empty: $CsvPath"
}

$valueColumn = ($rows[0].PSObject.Properties.Name | Where-Object { $_ -ne "id" } | Select-Object -First 1)
if (-not $valueColumn) {
  throw "Cannot find value column in CSV: $CsvPath"
}

$map = @{}
foreach ($row in $rows) {
  $name = [string]$row.id
  if ($name) {
    $map[$name] = [string]$row.$valueColumn
  }
}

$apiKey = ([string]$map["apiKey"]).Trim()
$apiUrl = ([string]$map["openAiCompatible"]).Trim()
if (-not $apiKey) {
  throw "Cannot find apiKey row in CSV."
}
if (-not $apiUrl) {
  throw "Cannot find openAiCompatible row in CSV."
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
Write-Host "Qwen API configured."
Write-Host "Model: $Model"
Write-Host "API URL: $apiUrl"
Write-Host "API Key: $preview"
if ($PersistUser) {
  Write-Host "Saved to User environment variables. Restart PowerShell to use it in new windows."
} else {
  Write-Host "Configured for this PowerShell session only."
}
