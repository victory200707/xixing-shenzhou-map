param(
  [string]$Source = "assets/map/source/1123.svg",
  [string]$Output = "assets/map/svg/1123-land-mask-v.svg",
  [string]$Metadata = "assets/map/metadata/1123-land-mask-v.json"
)

$ErrorActionPreference = "Stop"
$sourcePath = [IO.Path]::GetFullPath($Source)
$outputPath = [IO.Path]::GetFullPath($Output)
$metadataPath = [IO.Path]::GetFullPath($Metadata)
$xml = Get-Content -Raw -LiteralPath $sourcePath

# The source repeats the same outer boundary in several print layers. Select
# the large red boundary path only; no geometry is rewritten or simplified.
$candidate = $null
foreach ($match in [regex]::Matches($xml, '<path\b[^>]*>')) {
  $tag = $match.Value
  $style = ([regex]::Match($tag, 'style="([^"]*)"')).Groups[1].Value
  if ($style -notmatch 'fill:#d35f5f') { continue }
  $d = ([regex]::Match($tag, '\bd="([^"]*)"')).Groups[1].Value
  if ($d.Length -gt 250000) { $candidate = $d; break }
}
if (-not $candidate) { throw "Could not locate the 1123 outer boundary path" }

# This affine is the audited visual registration used by the existing 1123
# previews. The source group transform is retained exactly.
$svg = @"
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="3025.3333" height="2137.3333" viewBox="0 0 3025.3333 2137.3333" preserveAspectRatio="none">
  <g transform="matrix(8.97 0 0 7.18 1323 1022)">
    <g transform="translate(-49.349798,-28.696144)">
      <path d="$candidate" fill="#ffffff" fill-opacity="1" fill-rule="evenodd" clip-rule="evenodd" stroke="none"/>
    </g>
  </g>
</svg>
"@
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outputPath) | Out-Null
$svg.Trim() + "`n" | Set-Content -LiteralPath $outputPath -Encoding utf8
$sha = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
$outSha = (Get-FileHash -LiteralPath $outputPath -Algorithm SHA256).Hash
$metadata = [ordered]@{
  schemaVersion = "1.0"
  status = "APPROXIMATE_VISUAL_MASK"
  label = "APPROXIMATE_VISUAL_MASK - NOT A GEOGRAPHIC SOURCE"
  purpose = "Visual clipping for the solar land-color layer only."
  sourceFile = $Source.Replace('\','/')
  sourceSha256 = $sha
  outputFile = $Output.Replace('\','/')
  outputSha256 = $outSha
  sourceViewBox = "0 0 210 297"
  outputViewBox = "0 0 3025.3333 2137.3333"
  method = "Single same-source outer boundary path from 1123.svg, rendered with audited preview affine; original path data retained."
  transform = "matrix(8.97 0 0 7.18 1323 1022) translate(-49.349798 -28.696144)"
  pathLength = $candidate.Length
  limitations = @(
    "Visual-only clipping layer; not a geographic source.",
    "The source path is print artwork and its implicit closure is a display approximation.",
    "Must not define borders, city coordinates, South Sea content, or map facts."
  )
}
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $metadataPath) | Out-Null
$json = ConvertTo-Json -InputObject $metadata -Depth 5
$json | Set-Content -LiteralPath $metadataPath -Encoding utf8
Write-Output $json
