param(
  [string]$Source = (Join-Path $PSScriptRoot '..\assets\map\source\terrain-reference-gs2016-1609.jpg'),
  [string]$Output = (Join-Path $PSScriptRoot '..\assets\map\raster\terrain-texture-v.png'),
  [string]$Metadata = (Join-Path $PSScriptRoot '..\assets\map\metadata\terrain-texture.json')
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$outDir = Split-Path -Parent $Output
$metaDir = Split-Path -Parent $Metadata
New-Item -ItemType Directory -Force -Path $outDir, $metaDir | Out-Null

$sourceBitmap = [System.Drawing.Bitmap]::new($Source)
try {
  # Interior of the standard-map frame. The crop excludes the title and bottom
  # audit strip; the remaining map furniture is suppressed by low contrast.
  $crop = [System.Drawing.Rectangle]::new(300, 220, 4350, 3040)
  if ($crop.Right -gt $sourceBitmap.Width -or $crop.Bottom -gt $sourceBitmap.Height) {
    throw "Crop $crop exceeds source image $($sourceBitmap.Width)x$($sourceBitmap.Height)."
  }

  $smallW = 504
  $smallH = 356
  $small = [System.Drawing.Bitmap]::new($smallW, $smallH, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $g = [System.Drawing.Graphics]::FromImage($small)
  try {
    $g.Clear([System.Drawing.Color]::Black)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $g.DrawImage($sourceBitmap, [System.Drawing.Rectangle]::new(0, 0, $smallW, $smallH), $crop, [System.Drawing.GraphicsUnit]::Pixel)
  } finally { $g.Dispose() }

  # Remove the source map's print furniture from the texture. These regions
  # are only visual artefacts (legend and inset), never geographic geometry.
  $legendFill = $small.GetPixel(140, 220)
  $insetFill = $small.GetPixel(260, 220)
  for ($y = 267; $y -lt $smallH; $y++) {
    for ($x = 0; $x -lt 86; $x++) { $small.SetPixel($x, $y, $legendFill) }
  }
  for ($y = 233; $y -lt $smallH; $y++) {
    for ($x = 407; $x -lt $smallW; $x++) { $small.SetPixel($x, $y, $insetFill) }
  }

  # Compress colour and contrast into a cool navy relief. This deliberately
  # removes the source map's colour conventions; it is not a geographic layer.
  for ($y = 0; $y -lt $smallH; $y++) {
    for ($x = 0; $x -lt $smallW; $x++) {
      $c = $small.GetPixel($x, $y)
      $lum = (0.299 * $c.R) + (0.587 * $c.G) + (0.114 * $c.B)
      $v = [Math]::Max(0.0, [Math]::Min(1.0, ($lum - 35.0) / 210.0))
      $v = 0.5 + (($v - 0.5) * 0.42)
      $r = [int][Math]::Round(5 + (17 * $v))
      $gg = [int][Math]::Round(18 + (33 * $v))
      $b = [int][Math]::Round(34 + (52 * $v))
      $small.SetPixel($x, $y, [System.Drawing.Color]::FromArgb($r, $gg, $b))
    }
  }

  $finalW = 3025
  $finalH = 2137
  $final = [System.Drawing.Bitmap]::new($finalW, $finalH, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
  $gf = [System.Drawing.Graphics]::FromImage($final)
  try {
    $gf.Clear([System.Drawing.Color]::FromArgb(7, 24, 44))
    $gf.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $gf.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $gf.DrawImage($small, [System.Drawing.Rectangle]::new(0, 0, $finalW, $finalH))
  } finally { $gf.Dispose() }

  $final.Save($Output, [System.Drawing.Imaging.ImageFormat]::Png)
  $sourceHash = (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash
  $outputHash = (Get-FileHash -LiteralPath $Output -Algorithm SHA256).Hash
  $metadataObject = [ordered]@{
    asset = 'terrain-texture-v'
    status = 'DRAFT_NOT_APPROVED_FOR_RENDER'
    sourceFile = (Resolve-Path -LiteralPath $Source).Path
    sourceSha256 = $sourceHash
    sourceDimensions = [ordered]@{ width = $sourceBitmap.Width; height = $sourceBitmap.Height }
    cropPixels = [ordered]@{ x = $crop.X; y = $crop.Y; width = $crop.Width; height = $crop.Height }
    outputFile = (Resolve-Path -LiteralPath $Output).Path
    outputSha256 = $outputHash
    outputDimensions = [ordered]@{ width = $finalW; height = $finalH }
    outputViewBox = '0 0 3025.3333 2137.3333'
    processing = @(
      'high-quality crop and resample',
      'luminance extraction',
      'cool navy remap with reduced contrast and print-furniture suppression',
      'no geographic geometry or CRS assigned',
      'not spatially registered to V; do not load into the website'
    )
    sourceMapApproval = 'GS(2016)1609'
    landMaskApplied = $false
    insetIncluded = $false
    generatedAt = (Get-Date).ToUniversalTime().ToString('o')
  }
  $metadataObject | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $Metadata -Encoding UTF8
  Write-Output "Generated $Output ($finalW x $finalH)"
  Write-Output "Output SHA-256: $outputHash"
} finally {
  if ($small) { $small.Dispose() }
  if ($final) { $final.Dispose() }
  $sourceBitmap.Dispose()
}
