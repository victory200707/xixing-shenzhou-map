param(
  [string]$Source = (Join-Path $PSScriptRoot '..\assets\map\source\terrain-reference-gs2016-1609.jpg'),
  [string]$Registration = (Join-Path $PSScriptRoot '..\assets\map\metadata\terrain-registration.json'),
  [string]$Output = (Join-Path $PSScriptRoot '..\assets\map\raster\terrain-texture-registered-v.png'),
  [string]$Metadata = (Join-Path $PSScriptRoot '..\assets\map\metadata\terrain-texture-registered.json')
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

function Get-Hash([string]$Path) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash }
function Clamp([double]$Value, [double]$Min, [double]$Max) { return [Math]::Max($Min, [Math]::Min($Max, $Value)) }

$registrationData = Get-Content -LiteralPath $Registration -Raw | ConvertFrom-Json
if ($registrationData.status -ne 'FIT_ACCEPTABLE_FOR_VISUAL_REVIEW') { throw "Registration status must be FIT_ACCEPTABLE_FOR_VISUAL_REVIEW; found $($registrationData.status)." }
if ((Get-Hash $Source) -ne $registrationData.sourceImageSha256) { throw 'Source JPG hash differs from the approved registration input.' }

$outputDirectory = Split-Path -Parent $Output
$metadataDirectory = Split-Path -Parent $Metadata
New-Item -ItemType Directory -Force -Path $outputDirectory, $metadataDirectory | Out-Null

$sourceBitmap = [System.Drawing.Bitmap]::new($Source)
$sanitized = $null
$registered = $null
$low = $null
$final = $null
try {
  $sanitized = [System.Drawing.Bitmap]::new($sourceBitmap.Width, $sourceBitmap.Height, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $sanitizedGraphics = [System.Drawing.Graphics]::FromImage($sanitized)
  try {
    $sanitizedGraphics.DrawImageUnscaled($sourceBitmap, 0, 0)

    # These are source-page print-furniture zones only. They remove the legend
    # and the separate source-map inset before the main-map affine transform.
    # They do not remove or rewrite any official SVG geometry.
    $legendColour = $sourceBitmap.GetPixel(900, 2840)
    $insetColour = $sourceBitmap.GetPixel(3920, 2210)
    $sanitizedGraphics.FillRectangle([System.Drawing.SolidBrush]::new($legendColour), 300, 2610, 600, 650)
    $sanitizedGraphics.FillRectangle([System.Drawing.SolidBrush]::new($insetColour), 3940, 2290, 760, 970)
  } finally { $sanitizedGraphics.Dispose() }

  $targetWidth = 3025
  $targetHeight = 2137
  $matrix = $registrationData.matrix
  $a = [double]$matrix[0][0]; $b = [double]$matrix[0][1]; $c = [double]$matrix[0][2]
  $d = [double]$matrix[1][0]; $e = [double]$matrix[1][1]; $f = [double]$matrix[1][2]
  $sourceWidth = $sourceBitmap.Width; $sourceHeight = $sourceBitmap.Height
  $destination = [System.Drawing.PointF[]]@(
    [System.Drawing.PointF]::new($c, $f),
    [System.Drawing.PointF]::new($a * $sourceWidth + $c, $d * $sourceWidth + $f),
    [System.Drawing.PointF]::new($b * $sourceHeight + $c, $e * $sourceHeight + $f)
  )
  $registered = [System.Drawing.Bitmap]::new($targetWidth, $targetHeight, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $registrationGraphics = [System.Drawing.Graphics]::FromImage($registered)
  try {
    $registrationGraphics.Clear([System.Drawing.Color]::FromArgb(7, 24, 44))
    $registrationGraphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $registrationGraphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $registrationGraphics.DrawImage($sanitized, $destination)
  } finally { $registrationGraphics.Dispose() }

  # Low-pass resampling deliberately removes labels, fine graticules, and
  # political linework before the source is converted into an abstract texture.
  $lowWidth = 605; $lowHeight = 427
  $low = [System.Drawing.Bitmap]::new($lowWidth, $lowHeight, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $lowGraphics = [System.Drawing.Graphics]::FromImage($low)
  try {
    $lowGraphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $lowGraphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $lowGraphics.DrawImage(
      $registered,
      [System.Drawing.Rectangle]::new(0, 0, $lowWidth, $lowHeight),
      0, 0, $registered.Width, $registered.Height,
      [System.Drawing.GraphicsUnit]::Pixel
    )
  } finally { $lowGraphics.Dispose() }

  for ($y = 0; $y -lt $lowHeight; $y++) {
    for ($x = 0; $x -lt $lowWidth; $x++) {
      $colour = $low.GetPixel($x, $y)
      $luminance = 0.299 * $colour.R + 0.587 * $colour.G + 0.114 * $colour.B
      $value = Clamp (($luminance - 60.0) / 180.0) 0.0 1.0
      $value = 0.5 + (($value - 0.5) * 0.34)
      $red = [int][Math]::Round(5 + 14 * $value)
      $green = [int][Math]::Round(18 + 29 * $value)
      $blue = [int][Math]::Round(37 + 54 * $value)
      $low.SetPixel($x, $y, [System.Drawing.Color]::FromArgb($red, $green, $blue))
    }
  }

  $final = [System.Drawing.Bitmap]::new($targetWidth, $targetHeight, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $finalGraphics = [System.Drawing.Graphics]::FromImage($final)
  try {
    $finalGraphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $finalGraphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $finalGraphics.DrawImage(
      $low,
      [System.Drawing.Rectangle]::new(0, 0, $targetWidth, $targetHeight),
      0, 0, $low.Width, $low.Height,
      [System.Drawing.GraphicsUnit]::Pixel
    )
  } finally { $finalGraphics.Dispose() }
  $final.Save($Output, [System.Drawing.Imaging.ImageFormat]::Png)

  $metadataObject = [ordered]@{
    schemaVersion = '1.0'
    status = 'REJECTED_FOR_RENDER_WITHOUT_OFFICIAL_LAND_MASK'
    purpose = 'Registered, low-contrast visual texture below the unchanged official SVG; not a DEM or geographic-fact source.'
    sourceImage = 'assets/map/source/terrain-reference-gs2016-1609.jpg'
    sourceImageSha256 = Get-Hash $Source
    registration = 'assets/map/metadata/terrain-registration.json'
    registrationSha256 = Get-Hash $Registration
    controlPointCount = $registrationData.metrics.pointCount
    controlPointRmsePx = $registrationData.metrics.rmsePx
    sourcePixelToVMatrix = $registrationData.matrix
    outputFile = 'assets/map/raster/terrain-texture-registered-v.png'
    outputSha256 = Get-Hash $Output
    outputDimensions = [ordered]@{ width = $targetWidth; height = $targetHeight }
    outputViewBox = '0 0 3025.3333 2137.3333'
    processing = @(
      'main-map affine registration using human-captured graticule control points',
      'source legend and source South China Sea inset suppressed before transform',
      'five-times low-pass resampling to suppress labels, graticule, rivers, and linework',
      'cold low-contrast navy remap',
      'not loaded by index.html',
      'rejected for webpage rendering: source-page furniture remains visible outside a verified official land mask',
      'no official SVG geometry changed'
    )
    knownLimitations = @(
      'The raster is a visual texture, not measured elevation.',
      'The source JPG has no embedded CRS or elevation values.',
      'A human must verify visual agreement with the official SVG before page use.'
    )
    generatedAt = (Get-Date).ToUniversalTime().ToString('o')
  }
  $metadataObject | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Metadata -Encoding UTF8
  Write-Output "Generated registered terrain draft: $Output ($targetWidth x $targetHeight)"
  Write-Output "Source-to-V RMSE: $($registrationData.metrics.rmsePx) px"
  Write-Output "Output SHA-256: $((Get-Hash $Output))"
} finally {
  if ($sanitized) { $sanitized.Dispose() }
  if ($registered) { $registered.Dispose() }
  if ($low) { $low.Dispose() }
  if ($final) { $final.Dispose() }
  $sourceBitmap.Dispose()
}
