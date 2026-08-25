param(
  [Parameter(Mandatory = $true)]
  [string]$InputPath,
  [string]$Out = "ocr-output-paddle-gpu",
  [string]$Lang = "japan",
  [string]$Device = "gpu:0",
  [switch]$GpuEnv,
  [switch]$Fast,
  [switch]$QualityRec,
  [switch]$JapanRec,
  [int]$Start = 1,
  [int]$Limit = 0,
  [switch]$SkipExisting,
  [int]$TimeoutSeconds = 240
)

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$inputResolved = Resolve-Path -LiteralPath $InputPath
$outDir = if ([System.IO.Path]::IsPathRooted($Out)) {
  $Out
} else {
  Join-Path $root $Out
}
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$extensions = @(".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".pdf")
if ((Get-Item -LiteralPath $inputResolved).PSIsContainer) {
  $files = Get-ChildItem -LiteralPath $inputResolved -File |
    Where-Object { $extensions -contains $_.Extension.ToLowerInvariant() -and $_.BaseName -notlike "*_debug" } |
    Sort-Object Name
} else {
  $files = @(Get-Item -LiteralPath $inputResolved)
}

$files = @($files | Select-Object -Skip ([Math]::Max($Start - 1, 0)))
if ($Limit -gt 0) {
  $files = @($files | Select-Object -First $Limit)
}

$logPath = Join-Path $outDir "_batch-log.txt"
$perPageLogDir = Join-Path $outDir "_page-logs"
New-Item -ItemType Directory -Force -Path $perPageLogDir | Out-Null
"PaddleOCR safe batch started: $(Get-Date -Format s)" | Set-Content -LiteralPath $logPath -Encoding UTF8
"Input: $inputResolved" | Add-Content -LiteralPath $logPath -Encoding UTF8
"Files: $($files.Count)" | Add-Content -LiteralPath $logPath -Encoding UTF8

$failed = @()
for ($i = 0; $i -lt $files.Count; $i++) {
  $file = $files[$i]
  $txtPath = Join-Path $outDir ($file.BaseName + ".txt")
  if ($SkipExisting -and (Test-Path -LiteralPath $txtPath)) {
    Write-Host "Skip [$($i + 1)/$($files.Count)]: $($file.Name)"
    continue
  }

  $pageLog = Join-Path $perPageLogDir ($file.BaseName + ".log")
  Write-Host "OCR [$($i + 1)/$($files.Count)]: $($file.FullName)"
  Write-Host "  Log: $pageLog"
  "OCR [$($i + 1)/$($files.Count)]: $($file.FullName)" | Add-Content -LiteralPath $logPath -Encoding UTF8

  $ocrParams = @{
    InputPath = $file.FullName
    Out = $Out
    Lang = $Lang
    Device = $Device
    Limit = 1
  }
  if ($GpuEnv) { $ocrParams.GpuEnv = $true }
  if ($Fast) { $ocrParams.Fast = $true }
  if ($QualityRec) { $ocrParams.QualityRec = $true }
  if ($JapanRec) { $ocrParams.JapanRec = $true }

  $job = Start-Job -ScriptBlock {
    param($scriptPath, $params)
    & $scriptPath @params
  } -ArgumentList (Join-Path $PSScriptRoot "run-paddle-ocr.ps1"), $ocrParams

  $completed = Wait-Job -Job $job -Timeout $TimeoutSeconds
  Receive-Job -Job $job 2>&1 | Tee-Object -FilePath $pageLog | Out-Null

  if (-not $completed) {
    Stop-Job -Job $job -ErrorAction SilentlyContinue
    Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
    $failed += $file.FullName
    "TIMEOUT after ${TimeoutSeconds}s: $($file.FullName)" | Add-Content -LiteralPath $logPath -Encoding UTF8
    Write-Host "Timeout after ${TimeoutSeconds}s: $($file.Name)"
    continue
  }

  $state = $job.State
  Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
  if ($state -ne "Completed") {
    $failed += $file.FullName
    "FAILED ($state): $($file.FullName)" | Add-Content -LiteralPath $logPath -Encoding UTF8
  } else {
    "OK: $($file.FullName)" | Add-Content -LiteralPath $logPath -Encoding UTF8
    Write-Host "Done: $($file.Name)"
  }
}

if ($failed.Count -gt 0) {
  "Failures:" | Add-Content -LiteralPath $logPath -Encoding UTF8
  $failed | Add-Content -LiteralPath $logPath -Encoding UTF8
  Write-Host "Finished with $($failed.Count) failed file(s). Log: $logPath"
  exit 1
}

Write-Host "Finished. Log: $logPath"
