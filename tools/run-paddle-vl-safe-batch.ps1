param(
  [Parameter(Mandatory = $true)]
  [string]$InputPath,
  [string]$Out = "ocr-output-paddle-vl",
  [string]$Device = "gpu:0",
  [ValidateSet("v1", "v1.5", "v1.6")]
  [string]$PipelineVersion = "v1.6",
  [int]$MaxNewTokens = 256,
  [int]$MaxPixels = 250000,
  [int]$HeartbeatSeconds = 10,
  [int]$TimeoutSeconds = 180,
  [int]$Retries = 1,
  [int]$CooldownSeconds = 6,
  [int]$MinFreeMemoryMb = 0,
  [int]$GpuWaitSeconds = 90,
  [switch]$NoLayout,
  [switch]$SkipExisting
)

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv-ocr-gpu\Scripts\python.exe"
$vlScript = Join-Path $root "tools\paddle_ocr_vl_test.py"
$inputResolved = Resolve-Path -LiteralPath $InputPath
$outDir = if ([System.IO.Path]::IsPathRooted($Out)) { $Out } else { Join-Path $root $Out }
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$env:HOME = Join-Path $root ".ocr-home"
$env:USERPROFILE = $env:HOME
$env:PADDLE_HOME = Join-Path $root ".ocr-home\paddle"
$env:XDG_CACHE_HOME = Join-Path $root ".ocr-home\cache"
$env:PADDLE_PDX_CACHE_HOME = Join-Path $root ".paddlex-cache"
$env:PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT = "False"
$env:FLAGS_use_mkldnn = "false"
$env:PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK = "False"
$env:FLAGS_allocator_strategy = "auto_growth"
$env:FLAGS_fraction_of_gpu_memory_to_use = "0.82"

$extensions = @(".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".pdf")
if ((Get-Item -LiteralPath $inputResolved).PSIsContainer) {
  $files = Get-ChildItem -LiteralPath $inputResolved -File |
    Where-Object { $extensions -contains $_.Extension.ToLowerInvariant() -and $_.BaseName -notlike "*_debug" } |
    Sort-Object Name
} else {
  $files = @(Get-Item -LiteralPath $inputResolved)
}

$logPath = Join-Path $outDir "_vl-batch-log.txt"
$pageLogDir = Join-Path $outDir "_vl-page-logs"
New-Item -ItemType Directory -Force -Path $pageLogDir | Out-Null
"PaddleOCR-VL safe batch started: $(Get-Date -Format s)" | Set-Content -LiteralPath $logPath -Encoding UTF8
"Input: $inputResolved" | Add-Content -LiteralPath $logPath -Encoding UTF8
"Files: $($files.Count)" | Add-Content -LiteralPath $logPath -Encoding UTF8

function Get-NvidiaSmiPath {
  Get-ChildItem -LiteralPath "C:\WINDOWS\System32\DriverStore\FileRepository" -Recurse -Filter nvidia-smi.exe -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty FullName
}

function Get-FreeGpuMemoryMb {
  $nvidiaSmi = Get-NvidiaSmiPath
  if (-not $nvidiaSmi) { return $null }
  $query = & $nvidiaSmi --query-gpu=memory.free --format=csv,noheader,nounits 2>$null
  if (-not $query) { return $null }
  return [int]($query | Select-Object -First 1)
}

function Wait-GpuMemory {
  param(
    [int]$MinFreeMb,
    [int]$MaxWaitSeconds
  )

  if ($MinFreeMb -le 0) { return }
  $started = Get-Date
  while ($true) {
    $free = Get-FreeGpuMemoryMb
    if ($null -eq $free) {
      Write-Host "GPU memory check unavailable; continuing."
      return
    }
    if ($free -ge $MinFreeMb) {
      Write-Host "GPU free memory: ${free}MB"
      return
    }
    $elapsed = [int]((Get-Date) - $started).TotalSeconds
    if ($elapsed -ge $MaxWaitSeconds) {
      Write-Host "GPU free memory still low (${free}MB < ${MinFreeMb}MB); continuing after wait."
      return
    }
    Write-Host "Waiting for GPU memory: ${free}MB free, need ${MinFreeMb}MB..."
    Start-Sleep -Seconds 5
  }
}

function Stop-MatchingOcrPython {
  param(
    [string]$FilePath = ""
  )

  $fileName = if ($FilePath) { Split-Path -Leaf $FilePath } else { "" }
  $matches = Get-CimInstance Win32_Process -Filter "name = 'python.exe'" -ErrorAction SilentlyContinue |
    Where-Object {
      $cmd = $_.CommandLine
      $cmd -and
      $cmd -like "*$root*" -and
      $cmd -like "*paddle_ocr_vl_test.py*" -and (
        -not $FilePath -or
        $cmd -like "*$FilePath*" -or
        $cmd -like "*$fileName*"
      )
    }

  foreach ($process in $matches) {
    Write-Host "Stopping stale PaddleOCR-VL python PID=$($process.ProcessId)"
    "STOP STALE PID=$($process.ProcessId): $($process.CommandLine)" | Add-Content -LiteralPath $logPath -Encoding UTF8
    Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
  }
}

$failed = @()
for ($i = 0; $i -lt $files.Count; $i++) {
  $file = $files[$i]
  $txtPath = Join-Path $outDir ($file.BaseName + ".txt")
  if ($SkipExisting -and (Test-Path -LiteralPath $txtPath)) {
    Write-Host "Skip [$($i + 1)/$($files.Count)]: $($file.Name)"
    continue
  }

  $success = $false
  for ($attempt = 1; $attempt -le ($Retries + 1); $attempt++) {
    Wait-GpuMemory -MinFreeMb $MinFreeMemoryMb -MaxWaitSeconds $GpuWaitSeconds

    $pageLog = Join-Path $pageLogDir ("$($file.BaseName)-try$attempt.log")
    Write-Host "PaddleOCR-VL [$($i + 1)/$($files.Count)] try ${attempt}: $($file.FullName)"
    Write-Host "  Log: $pageLog"
    "TRY ${attempt}: $($file.FullName)" | Add-Content -LiteralPath $logPath -Encoding UTF8

    $pageErrLog = Join-Path $pageLogDir ("$($file.BaseName)-try$attempt.err.log")
    $argsList = @(
      $vlScript,
      $file.FullName,
      "--out", $outDir,
      "--device", $Device,
      "--pipeline-version", $PipelineVersion,
      "--backend", "native",
      "--limit", "1",
      "--max-new-tokens", [string]$MaxNewTokens,
      "--max-pixels", [string]$MaxPixels,
      "--heartbeat-seconds", [string]$HeartbeatSeconds,
      "--flat-output"
    )
    if ($NoLayout) { $argsList += "--no-layout" }

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $python
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    foreach ($arg in $argsList) {
      [void]$startInfo.ArgumentList.Add([string]$arg)
    }
    foreach ($key in @(
      "HOME",
      "USERPROFILE",
      "PADDLE_HOME",
      "XDG_CACHE_HOME",
      "PADDLE_PDX_CACHE_HOME",
      "PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT",
      "FLAGS_use_mkldnn",
      "PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK",
      "FLAGS_allocator_strategy",
      "FLAGS_fraction_of_gpu_memory_to_use"
    )) {
      $value = [Environment]::GetEnvironmentVariable($key, "Process")
      if ($value) {
        $startInfo.Environment[$key] = $value
      }
    }

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    [void]$process.Start()
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()

    "PID ${attempt}: $($process.Id)" | Add-Content -LiteralPath $logPath -Encoding UTF8
    "START PID=$($process.Id) TIME=$(Get-Date -Format s)" | Add-Content -LiteralPath $pageLog -Encoding UTF8

    $startedAt = Get-Date
    $lastBeat = Get-Date
    $completed = $false
    while ($true) {
      if ($process.HasExited) {
        $completed = $true
        break
      }

      $elapsed = [int]((Get-Date) - $startedAt).TotalSeconds
      if ($elapsed -ge $TimeoutSeconds) {
        break
      }

      $sinceBeat = [int]((Get-Date) - $lastBeat).TotalSeconds
      if ($sinceBeat -ge [Math]::Max($HeartbeatSeconds, 5)) {
        $message = "WATCHDOG still running PID=$($process.Id) elapsed=${elapsed}s timeout=${TimeoutSeconds}s"
        Write-Host $message
        $message | Add-Content -LiteralPath $pageLog -Encoding UTF8
        $lastBeat = Get-Date
      }

      Start-Sleep -Seconds 1
    }

    if (-not $completed) {
      "TIMEOUT killing process tree PID=$($process.Id)" | Add-Content -LiteralPath $pageLog -Encoding UTF8
      & taskkill.exe /PID $process.Id /T /F 2>&1 | Add-Content -LiteralPath $pageLog -Encoding UTF8
      Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
      $stdoutTask.Wait(3000) | Out-Null
      $stderrTask.Wait(3000) | Out-Null
      $existingLog = if (Test-Path -LiteralPath $pageLog) { Get-Content -LiteralPath $pageLog -Raw -ErrorAction SilentlyContinue } else { "" }
      ($existingLog + "`n" + $stdoutTask.Result) | Set-Content -LiteralPath $pageLog -Encoding UTF8
      $stderrTask.Result | Set-Content -LiteralPath $pageErrLog -Encoding UTF8
      "TIMEOUT try ${attempt}: $($file.FullName)" | Add-Content -LiteralPath $logPath -Encoding UTF8
      Write-Host "Timeout try ${attempt}: $($file.Name)"
      if (Test-Path -LiteralPath $pageErrLog) {
        Get-Content -LiteralPath $pageErrLog -ErrorAction SilentlyContinue | Add-Content -LiteralPath $pageLog -Encoding UTF8
      }
      Start-Sleep -Seconds $CooldownSeconds
      continue
    }

    $process.WaitForExit()
    $stdoutTask.Wait() | Out-Null
    $stderrTask.Wait() | Out-Null
    $existingLog = if (Test-Path -LiteralPath $pageLog) { Get-Content -LiteralPath $pageLog -Raw -ErrorAction SilentlyContinue } else { "" }
    ($existingLog + "`n" + $stdoutTask.Result) | Set-Content -LiteralPath $pageLog -Encoding UTF8
    $stderrTask.Result | Set-Content -LiteralPath $pageErrLog -Encoding UTF8

    if (Test-Path -LiteralPath $pageErrLog) {
      Get-Content -LiteralPath $pageErrLog -ErrorAction SilentlyContinue | Add-Content -LiteralPath $pageLog -Encoding UTF8
    }

    if ($process.ExitCode -eq 0 -and (Test-Path -LiteralPath $txtPath)) {
      "OK try ${attempt}: $($file.FullName)" | Add-Content -LiteralPath $logPath -Encoding UTF8
      Write-Host "Done: $($file.Name)"
      $success = $true
      if ($CooldownSeconds -gt 0) {
        Write-Host "Cooldown ${CooldownSeconds}s for GPU memory release..."
        Start-Sleep -Seconds $CooldownSeconds
      }
      break
    }

    "FAILED try ${attempt} exit=$($process.ExitCode): $($file.FullName)" | Add-Content -LiteralPath $logPath -Encoding UTF8
    Start-Sleep -Seconds $CooldownSeconds
  }

  if (-not $success) {
    $failed += $file.FullName
  }
}

if ($failed.Count -gt 0) {
  "Failures:" | Add-Content -LiteralPath $logPath -Encoding UTF8
  $failed | Add-Content -LiteralPath $logPath -Encoding UTF8
  Write-Host "Finished with $($failed.Count) failed file(s). Log: $logPath"
  exit 1
}

Write-Host "Finished. Log: $logPath"
