param(
  [string]$Source = "assets/map/svg/clean-map.svg",
  [string]$Output = "assets/map/svg/presentation-map.svg"
)

$ErrorActionPreference = "Stop"
$sourcePath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Source))
$outputPath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Output))
if ($sourcePath -eq $outputPath) { throw "Refusing to overwrite the source SVG." }

function Get-Sha256([string]$Path) {
  return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

$xml = [System.Xml.XmlDocument]::new()
$xml.PreserveWhitespace = $true
$xml.Load($sourcePath)
$ns = [System.Xml.XmlNamespaceManager]::new($xml.NameTable)
$ns.AddNamespace("svg", "http://www.w3.org/2000/svg")
$paths = $xml.SelectNodes("//svg:path", $ns)
$primaryCount = 0
$secondaryCount = 0
$accentCount = 0
$fillCount = 0
$unknownCount = 0

foreach ($path in $paths) {
  $style = [string]$path.GetAttribute("style")
  if ($style -match "stroke:#d2b472") {
    $path.SetAttribute("class", "presentation-primary-linework")
    $path.SetAttribute("style", "fill:none;stroke:#c4b38e;stroke-width:1.10;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:0.72;vector-effect:non-scaling-stroke")
    $primaryCount++
    continue
  }
  if ($style -match "stroke:#4b7892") {
    $path.SetAttribute("class", "presentation-secondary-linework")
    $path.SetAttribute("style", "fill:none;stroke:#647f95;stroke-width:0.72;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:0.40;vector-effect:non-scaling-stroke")
    $secondaryCount++
    continue
  }
  if ($style -match "stroke:#a9976f") {
    $path.SetAttribute("class", "presentation-accent-linework")
    $path.SetAttribute("style", "fill:none;stroke:#a99570;stroke-width:0.82;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:0.52;vector-effect:non-scaling-stroke")
    $accentCount++
    continue
  }
  if ($style -match "fill:#091b2c;fill-opacity:0.72") {
    $path.SetAttribute("class", "presentation-body-fill-unknown")
    $path.SetAttribute("style", "fill:#091b2c;fill-opacity:0.80;fill-rule:evenodd;stroke:none")
    $fillCount++
    continue
  }
  $path.SetAttribute("class", "presentation-unknown-linework")
  $unknownCount++
}

$outputDirectory = Split-Path -Parent $outputPath
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
$xml.Save($outputPath)

Write-Output "source=$sourcePath"
Write-Output "source_sha256=$(Get-Sha256 $sourcePath)"
Write-Output "output=$outputPath"
Write-Output "output_sha256=$(Get-Sha256 $outputPath)"
Write-Output "path_count=$($paths.Count)"
Write-Output "primary_linework=$primaryCount"
Write-Output "secondary_linework=$secondaryCount"
Write-Output "accent_linework=$accentCount"
Write-Output "body_fill_unknown=$fillCount"
Write-Output "unknown_linework=$unknownCount"
Write-Output "geometry_policy=path d, transform, viewBox, and path order retained"
