param(
  [string]$CsvPath = "",
  [string]$ApiUrl = "",
  [string]$ApiKey = "",
  [switch]$Raw
)

if ($CsvPath) {
  $resolved = Resolve-Path -LiteralPath $CsvPath -ErrorAction Stop
  $rows = Import-Csv -LiteralPath $resolved.Path
  $valueColumn = ($rows[0].PSObject.Properties.Name | Where-Object { $_ -ne "id" } | Select-Object -First 1)
  $map = @{}
  foreach ($row in $rows) {
    if ($row.id) { $map[[string]$row.id] = [string]$row.$valueColumn }
  }
  if (-not $ApiKey) { $ApiKey = ([string]$map["apiKey"]).Trim() }
  if (-not $ApiUrl) { $ApiUrl = ([string]$map["openAiCompatible"]).Trim() }
}

if (-not $ApiUrl) { $ApiUrl = $env:VLM_OCR_API_URL }
if (-not $ApiKey) { $ApiKey = $env:VLM_OCR_API_KEY }
if (-not $ApiKey) { $ApiKey = $env:DASHSCOPE_API_KEY }
if (-not $ApiKey) { $ApiKey = $env:QWEN_API_KEY }

if (-not $ApiUrl) { throw "Missing ApiUrl. Pass -ApiUrl, -CsvPath, or set VLM_OCR_API_URL." }
if (-not $ApiKey) { throw "Missing ApiKey. Pass -ApiKey, -CsvPath, or set VLM_OCR_API_KEY/DASHSCOPE_API_KEY." }

$endpoint = $ApiUrl.TrimEnd("/") + "/models"
$headers = @{ Authorization = "Bearer $ApiKey" }

try {
  $response = Invoke-RestMethod -Method Get -Uri $endpoint -Headers $headers -TimeoutSec 60
  if ($Raw) {
    $response | ConvertTo-Json -Depth 12
    exit 0
  }

  $models = @()
  if ($response.data) { $models = @($response.data) }
  elseif ($response.models) { $models = @($response.models) }
  elseif ($response -is [array]) { $models = @($response) }

  if (-not $models -or $models.Count -eq 0) {
    Write-Host "No model list found in response. Use -Raw to inspect the response shape."
    exit 0
  }

  $models |
    ForEach-Object {
      [pscustomobject]@{
        id = $_.id
        object = $_.object
        owned_by = $_.owned_by
      }
    } |
    Sort-Object id |
    Format-Table -AutoSize
} catch {
  $resp = $_.Exception.Response
  if ($resp) {
    $reader = [System.IO.StreamReader]::new($resp.GetResponseStream())
    $body = $reader.ReadToEnd()
    throw "Model list request failed: HTTP $([int]$resp.StatusCode) $body"
  }
  throw
}
