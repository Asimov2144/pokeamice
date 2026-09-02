param(
  [Parameter(Mandatory = $true)]
  [string[]]$PagePaths,
  [Parameter(Mandatory = $true)]
  [string]$ImageRoot,
  [Parameter(Mandatory = $true)]
  [string]$OutDir,
  [string]$ServerUrl = "http://127.0.0.1:4175",
  [ValidateRange(1, 4)]
  [int]$BatchSize = 4,
  [ValidateRange(40, 95)]
  [int]$VlmJpegQuality = 78,
  [ValidateRange(800, 2400)]
  [int]$VlmMaxEdge = 1600,
  [ValidateSet("none", "suggest", "apply")]
  [string]$OrientationMode = "suggest",
  [switch]$ContinueOnError
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$imageRootPath = (Resolve-Path -LiteralPath $ImageRoot).Path
$outPath = if ([System.IO.Path]::IsPathRooted($OutDir)) { $OutDir } else { Join-Path $root $OutDir }
New-Item -ItemType Directory -Force -Path $outPath | Out-Null

function Get-PagePayload([string]$Path, [int]$Rotation = 0) {
  $resolved = (Resolve-Path -LiteralPath $Path).Path
  if (-not $resolved.StartsWith($imageRootPath, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Page is outside ImageRoot: $resolved"
  }
  $image = [System.Drawing.Image]::FromFile($resolved)
  try {
    $originalWidth = $image.Width
    $originalHeight = $image.Height
    $rotateType = switch ($Rotation) {
      90 { [System.Drawing.RotateFlipType]::Rotate90FlipNone }
      180 { [System.Drawing.RotateFlipType]::Rotate180FlipNone }
      270 { [System.Drawing.RotateFlipType]::Rotate270FlipNone }
      default { [System.Drawing.RotateFlipType]::RotateNoneFlipNone }
    }
    if ($Rotation) { $image.RotateFlip($rotateType) }
    $width = $image.Width
    $height = $image.Height
    $sourceForVlm = $image
    $preview = $null
    if ($VlmMaxEdge -gt 0 -and [Math]::Max($width, $height) -gt $VlmMaxEdge) {
      $scale = $VlmMaxEdge / [double][Math]::Max($width, $height)
      $scaledWidth = [Math]::Max(1, [int][Math]::Round($width * $scale))
      $scaledHeight = [Math]::Max(1, [int][Math]::Round($height * $scale))
      $preview = [System.Drawing.Bitmap]::new($scaledWidth, $scaledHeight)
      $graphics = [System.Drawing.Graphics]::FromImage($preview)
      try {
        $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $graphics.DrawImage($image, 0, 0, $scaledWidth, $scaledHeight)
      }
      finally { $graphics.Dispose() }
      $sourceForVlm = $preview
    }
    # Layout/orientation calls only need a faithful preview. Always encode a
    # temporary JPEG so PNG/TIFF and oversized JPEG inputs do not travel to
    # the VLM at their original byte size. Coordinates remain normalized and
    # the original dimensions are retained below for mapping back to scans.
    $stream = [System.IO.MemoryStream]::new()
    $jpegParams = [System.Drawing.Imaging.EncoderParameters]::new(1)
    $jpegParams.Param[0] = [System.Drawing.Imaging.EncoderParameter]::new(
      [System.Drawing.Imaging.Encoder]::Quality, [long]$VlmJpegQuality)
    try {
      $codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() |
        Where-Object { $_.MimeType -eq "image/jpeg" } |
        Select-Object -First 1
      $sourceForVlm.Save($stream, $codec, $jpegParams)
      $imageBytes = $stream.ToArray()
    }
    finally {
      $jpegParams.Dispose()
      $stream.Dispose()
      if ($preview) { $preview.Dispose() }
    }
  }
  finally {
    $image.Dispose()
  }
  $extension = [System.IO.Path]::GetExtension($resolved).ToLowerInvariant()
  $mime = switch ($extension) {
    ".png" { "image/png" }
    ".webp" { "image/webp" }
    ".tif" { "image/tiff" }
    ".tiff" { "image/tiff" }
    default { "image/jpeg" }
  }
  $mime = "image/jpeg"
  $relative = [System.IO.Path]::GetRelativePath($imageRootPath, $resolved).Replace("\", "/")
  return [ordered]@{
    name = $relative
    dataUrl = "data:$mime;base64,$([Convert]::ToBase64String($imageBytes))"
    width = $width
    height = $height
    originalWidth = $originalWidth
    originalHeight = $originalHeight
    rotationCorrection = $Rotation
  }
}

function Normalize-Angle([double]$Value) {
  while ($Value -gt 180) { $Value -= 360 }
  while ($Value -lt -180) { $Value += 360 }
  return [Math]::Round($Value, 1)
}

function Convert-PointFromRotated([double]$X, [double]$Y, [int]$Rotation, [double]$OriginalWidth, [double]$OriginalHeight) {
  switch ($Rotation) {
    90 { return @($Y, $OriginalHeight - $X) }
    180 { return @($OriginalWidth - $X, $OriginalHeight - $Y) }
    270 { return @($OriginalWidth - $Y, $X) }
    default { return @($X, $Y) }
  }
}

function Convert-BoxFromRotated($Box, [int]$Rotation, [double]$OriginalWidth, [double]$OriginalHeight) {
  $x1, $y1, $x2, $y2 = @($Box | ForEach-Object { [double]$_ })
  $mapped = switch ($Rotation) {
    90 { @($y1, ($OriginalHeight - $x2), $y2, ($OriginalHeight - $x1)) }
    180 { @(($OriginalWidth - $x2), ($OriginalHeight - $y2), ($OriginalWidth - $x1), ($OriginalHeight - $y1)) }
    270 { @(($OriginalWidth - $y2), $x1, ($OriginalWidth - $y1), $x2) }
    default { @($x1, $y1, $x2, $y2) }
  }
  return @($mapped | ForEach-Object { [int][Math]::Round($_) })
}

$pageOrientation = @{}
$payloads = @($PagePaths | ForEach-Object {
  $original = Get-PagePayload $_ 0
  $rotation = 0
  $orientation = $null
  if ($OrientationMode -eq "none") {
    $orientation = [ordered]@{
      rotation = 0
      suggestedRotation = 0
      confidence = 1
      uncertain = $false
      hasReadableText = $true
      reason = "使用已预处理扫描方向"
    }
  }
  else {
    try {
      Write-Host "Page orientation ($OrientationMode): $($original.name)"
      $orientationBody = @{ pages = @($original) } | ConvertTo-Json -Depth 6 -Compress
      $orientationResponse = Invoke-RestMethod -Uri "$($ServerUrl.TrimEnd('/'))/api/analyze-page-orientation" -Method Post -ContentType "application/json; charset=utf-8" -Body $orientationBody -TimeoutSec 300
      $orientation = $orientationResponse.pages[0]
    }
    catch {
      Write-Warning "Page orientation failed for $($original.name); using 0 degrees."
      $orientation = [ordered]@{ rotation = 0; suggestedRotation = 0; confidence = 0; uncertain = $true; hasReadableText = $true; reason = $_.Exception.Message }
    }
  }
  # ?? is PowerShell 7 only, and import-wizard-server.mjs runs these with
  # powershell.exe (5.1), where it is a parse error rather than a fallback.
  $suggestedRotation = if ($null -ne $orientation.suggestedRotation) {
    [int]$orientation.suggestedRotation
  } else {
    [int]$orientation.rotation
  }
  $rotation = if ($OrientationMode -eq "apply") { [int]$orientation.rotation } else { 0 }
  if ($OrientationMode -eq "suggest" -and $suggestedRotation -ne 0) {
    $orientation.uncertain = $true
    $orientation.reason = "建议 $suggestedRotation°，未自动应用；$($orientation.reason)"
  }
  $payload = Get-PagePayload $_ $rotation
  $pageOrientation[$payload.name] = [ordered]@{
    rotation = $rotation
    suggestedRotation = $suggestedRotation
    applied = ($rotation -ne 0)
    mode = $OrientationMode
    confidence = [double]$orientation.confidence
    uncertain = [bool]$orientation.uncertain
    hasReadableText = [bool]$orientation.hasReadableText
    reason = [string]$orientation.reason
    originalWidth = $payload.originalWidth
    originalHeight = $payload.originalHeight
  }
  $payload
})
$results = @()
$failures = @()
$modelName = ""
for ($offset = 0; $offset -lt $payloads.Count; $offset += $BatchSize) {
  $last = [Math]::Min($offset + $BatchSize - 1, $payloads.Count - 1)
  $batch = @($payloads[$offset..$last])
  Write-Host "Qwen layout: pages $($offset + 1)-$($last + 1) / $($payloads.Count)"
  $body = @{ pages = $batch } | ConvertTo-Json -Depth 8 -Compress
  try {
    $response = Invoke-RestMethod -Uri "$($ServerUrl.TrimEnd('/'))/api/analyze-layout" -Method Post -ContentType "application/json; charset=utf-8" -Body $body -TimeoutSec 900
  }
  catch {
    $errorMessage = $_.Exception.Message
    $failures += @($batch | ForEach-Object { [ordered]@{ name = $_.name; error = $errorMessage } })
    if (-not $ContinueOnError) { throw }
    Write-Warning "Layout failed for pages $($offset + 1)-$($last + 1); continuing."
    continue
  }
  $modelName = $response.model
  foreach ($pageResult in @($response.pages)) {
    $orientation = $pageOrientation[$pageResult.name]
    $rotation = [int]$orientation.rotation
    foreach ($region in @($pageResult.regions)) {
      $region.box = Convert-BoxFromRotated $region.box $rotation $orientation.originalWidth $orientation.originalHeight
      $region.angle = Normalize-Angle ([double]$region.angle - $rotation)
      if ($orientation.uncertain -and $orientation.hasReadableText) {
        $region.reviewFlags = @($region.reviewFlags) + "page_rotation_uncertain" | Select-Object -Unique
      }
      if ($rotation) { $region.note = "页面转正 $rotation° / $($region.note)" }
    }
    $pageResult.width = [int]$orientation.originalWidth
    $pageResult.height = [int]$orientation.originalHeight
    $pageResult | Add-Member -NotePropertyName pageOrientation -NotePropertyValue $orientation -Force
    $results += $pageResult
  }
  $partial = [ordered]@{
    createdAt = [DateTimeOffset]::Now.ToString("o")
    model = $modelName
    imageRoot = $imageRootPath
    pages = $results
    failures = $failures
  }
  [IO.File]::WriteAllText((Join-Path $outPath "layout-results.partial.json"), ($partial | ConvertTo-Json -Depth 20), [Text.UTF8Encoding]::new($false))
}

$annotationPages = @($results | ForEach-Object {
  [ordered]@{
    name = $_.name
    width = [int]$_.width
    height = [int]$_.height
    layoutMeta = [ordered]@{
      pageType = $_.pageType
      readingDirection = $_.readingDirection
      pageRotation = [int]$_.pageOrientation.rotation
      suggestedPageRotation = [int]$_.pageOrientation.suggestedRotation
      pageRotationApplied = [bool]$_.pageOrientation.applied
      pageOrientationMode = [string]$_.pageOrientation.mode
      rotationConfidence = [double]$_.pageOrientation.confidence
      rotationUncertain = [bool]$_.pageOrientation.uncertain
      rotationReason = [string]$_.pageOrientation.reason
    }
    regions = @($_.regions)
  }
})
$layoutResult = [ordered]@{
  createdAt = [DateTimeOffset]::Now.ToString("o")
  model = $modelName
  imageRoot = $imageRootPath
  pages = $results
  failures = $failures
}
$annotation = [ordered]@{
  version = 3
  title = Split-Path -Leaf $outPath
  sourceFolder = $imageRootPath
  pages = $annotationPages
}

$layoutPath = Join-Path $outPath "layout-results.json"
$annotationPath = Join-Path $outPath "magazine-regions.json"
[IO.File]::WriteAllText($layoutPath, ($layoutResult | ConvertTo-Json -Depth 20), [Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($annotationPath, ($annotation | ConvertTo-Json -Depth 20), [Text.UTF8Encoding]::new($false))

$regionCount = @($annotationPages | ForEach-Object { $_.regions }).Count
Write-Host "Saved layout: $layoutPath"
Write-Host "Saved annotation: $annotationPath"
Write-Host "Pages: $($annotationPages.Count); regions: $regionCount"
