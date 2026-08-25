param(
  [switch]$WhatIfOnly
)

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$patterns = @(
  "paddle_ocr_vl_test.py",
  "paddle_ocr_test.py",
  "ocr_regions_from_annotation.py",
  "deepseek_correct_region_ocr.py",
  "mineru"
)

$processes = Get-CimInstance Win32_Process -Filter "name = 'python.exe'" -ErrorAction SilentlyContinue |
  Where-Object {
    $cmd = $_.CommandLine
    if (-not $cmd) { return $false }
    ($cmd -like "*$root*") -and ($patterns | Where-Object { $cmd -like "*$_*" })
  }

if (-not $processes) {
  Write-Host "No stale OCR Python processes found."
  return
}

foreach ($process in $processes) {
  Write-Host "OCR process: PID=$($process.ProcessId)"
  Write-Host $process.CommandLine
  if (-not $WhatIfOnly) {
    Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
    Write-Host "Stopped PID=$($process.ProcessId)"
  }
}
