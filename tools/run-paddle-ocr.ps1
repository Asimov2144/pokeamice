param(
  [string]$InputPath = "",
  [switch]$Structure,
  [switch]$Fast,
  [switch]$QualityRec,
  [switch]$JapanRec,
  [string]$Out = "ocr-output",
  [string]$Lang = "japan",
  [string]$Device = "cpu",
  [switch]$GpuEnv,
  [int]$Start = 1,
  [int]$Limit = 0,
  [switch]$RestartEach,
  [switch]$ContinueOnError
)

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$env:HOME = Join-Path $root ".ocr-home"
$env:USERPROFILE = $env:HOME
$env:PADDLE_HOME = Join-Path $root ".ocr-home\paddle"
$env:XDG_CACHE_HOME = Join-Path $root ".ocr-home\cache"
$env:PADDLE_PDX_CACHE_HOME = Join-Path $root ".paddlex-cache"
$env:PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT = "False"
$env:FLAGS_use_mkldnn = "false"
$venvName = if ($GpuEnv) { ".venv-ocr-gpu" } else { ".venv-ocr" }
if ($GpuEnv -and $Device -eq "cpu") {
  $Device = "gpu:0"
}
$python = Join-Path $root "$venvName\Scripts\python.exe"
$script = Join-Path $root "tools\paddle_ocr_test.py"

$argsList = @($script)
if ($InputPath) {
  $argsList += $InputPath
}
$argsList += @("--out", $Out, "--lang", $Lang, "--device", $Device)
$argsList += @("--start", $Start, "--limit", $Limit)
if ($Structure) {
  $argsList += "--structure"
}
if ($Fast) {
  $argsList += "--fast"
}
if ($QualityRec) {
  $argsList += "--quality-rec"
}
if ($JapanRec) {
  $argsList += "--japan-rec"
}
if ($RestartEach) {
  $argsList += "--restart-each"
}
if ($ContinueOnError) {
  $argsList += "--continue-on-error"
}

& $python @argsList
