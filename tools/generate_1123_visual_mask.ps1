param(
  [string]$Source = "assets/map/source/1123.svg",
  [string]$Output = "assets/map/svg/1123-visual-mask.svg",
  [string]$Metadata = "assets/map/metadata/1123-visual-mask.json"
)

$ErrorActionPreference = "Stop"
$sourcePath = [IO.Path]::GetFullPath($Source)
$outputPath = [IO.Path]::GetFullPath($Output)
$metadataPath = [IO.Path]::GetFullPath($Metadata)
$xml = Get-Content -Raw -LiteralPath $sourcePath

# Keep the source viewBox and the source group transform. Remove the embedded
# page furniture and turn every source path into a white visual-only shape.
$viewBox = ([regex]::Match($xml, 'viewBox="([^"]+)"')).Groups[1].Value
$group = [regex]::Match($xml, '<g\s+inkscape:label="图层 1"\s+inkscape:groupmode="layer"[^>]*>([\s\S]*)</g>\s*</svg>')
if (-not $group.Success) { throw "Could not locate the primary source group" }
$inner = $group.Groups[1].Value
$inner = [regex]::Replace($inner, '<g\b([^>]*)>', '<g$1>')
$inner = [regex]::Replace($inner, 'style="[^"]*"', 'style="fill:#ffffff;fill-opacity:1;stroke:none"')
$inner = [regex]::Replace($inner, 'filter:url\([^)]*\)', '')
$inner = [regex]::Replace($inner, '(?<!fill-)opacity:[^;]+;?', '')
$svg = @"
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" viewBox="$viewBox" preserveAspectRatio="xMidYMid meet">
  <g data-source="1123.svg" data-purpose="APPROXIMATE_VISUAL_MASK">$inner</g>
</svg>
"@
$dir = Split-Path -Parent $outputPath
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$svg.Trim() + "`n" | Set-Content -LiteralPath $outputPath -Encoding utf8
$sha = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
$outSha = (Get-FileHash -LiteralPath $outputPath -Algorithm SHA256).Hash
$report = [ordered]@{
  schemaVersion = "1.0"
  status = "APPROXIMATE_VISUAL_MASK"
  label = "APPROXIMATE_VISUAL_MASK - NOT A GEOGRAPHIC SOURCE"
  sourceFile = $Source.Replace('\','/')
  sourceSha256 = $sha
  outputFile = $Output.Replace('\','/')
  outputSha256 = $outSha
  sourceViewBox = $viewBox
  pathCount = ([regex]::Matches($xml, '<path\b')).Count
  imageCount = ([regex]::Matches($xml, '<image\b')).Count
  method = "1123.svg vector paths restyled as independent visual candidate; no geometry rewritten"
  limitations = @(
    "The source has no authoritative object semantics for separating labels, islands, and land fill.",
    "Use only as a low-contrast visual clipping candidate beneath the unchanged official map.",
    "Do not use for borders, cities, coordinates, South Sea content, or formal publication."
  )
}
$report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $metadataPath -Encoding utf8
Write-Output ($report | ConvertTo-Json -Depth 5)
