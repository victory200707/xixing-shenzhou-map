param(
  [string]$Source = "assets/map/svg/presentation-map.svg",
  [string]$Output = "assets/map/svg/presentation-coastline.svg",
  [string]$Metadata = "assets/map/metadata/presentation-coastline.json"
)

$ErrorActionPreference = "Stop"
$sourcePath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Source))
$outputPath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Output))
$metadataPath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Metadata))
if ($sourcePath -eq $outputPath) { throw "Refusing to overwrite the source SVG." }

function Get-Sha256([string]$Path) {
  return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

$xml = [System.Xml.XmlDocument]::new()
$xml.PreserveWhitespace = $true
$xml.Load($sourcePath)
$ns = [System.Xml.XmlNamespaceManager]::new($xml.NameTable)
$ns.AddNamespace("svg", "http://www.w3.org/2000/svg")
$insetPath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) "assets/map/svg/official-south-sea.svg"))
$insetXml = [System.Xml.XmlDocument]::new()
$insetXml.Load($insetPath)
$insetIds = @{}
foreach ($node in $insetXml.SelectNodes("//svg:path[@data-source-id]", $ns)) { $insetIds[[string]$node.GetAttribute("data-source-id")] = $true }
$sourcePaths = @($xml.SelectNodes("//svg:path", $ns))

function Get-GeometryFingerprint($paths) {
  $rows = foreach ($path in $paths) { "{0}|{1}|{2}" -f $path.id, $path.d, $path.transform }
  $bytes = [System.Text.Encoding]::UTF8.GetBytes(($rows -join "`n"))
  $digest = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
  return -join ($digest | ForEach-Object { $_.ToString("x2") })
}

$sourceFingerprint = Get-GeometryFingerprint $sourcePaths
$primary = $xml.SelectNodes("//svg:path[@class='presentation-primary-linework']", $ns)
$secondary = $xml.SelectNodes("//svg:path[@class='presentation-secondary-linework']", $ns)

# Semantics remain UNKNOWN: primary is a conservative coastline/national-line
# candidate, while secondary is a conservative province-line candidate.
foreach ($path in $primary) {
  $path.SetAttribute("style", "fill:none;stroke:#c8b98f;stroke-width:1.16;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:0.78;vector-effect:non-scaling-stroke")
}
foreach ($path in $secondary) {
  $path.SetAttribute("style", "fill:none;stroke:#6e8595;stroke-width:0.68;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:0.34;vector-effect:non-scaling-stroke")
}

# The main presentation SVG contains a small subset of inset paths. Keep the
# complete official inset overlay and hide only the duplicated linework here.
# path3 is the shared body-fill candidate and must remain in the main map.
$hiddenPathIds = @()
foreach ($path in @($xml.SelectNodes("//svg:path", $ns))) {
  $id = [string]$path.GetAttribute("id")
  if ($id -and $id -ne "path3" -and $insetIds.ContainsKey($id)) {
    [void]$path.ParentNode.RemoveChild($path)
    $hiddenPathIds += $id
  }
}

$outputDirectory = Split-Path -Parent $outputPath
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
$xml.Save($outputPath)

$sourceHash = Get-Sha256 $sourcePath
$derivedHash = Get-Sha256 $outputPath
$fingerprintHex = Get-GeometryFingerprint @($xml.SelectNodes("//svg:path", $ns))

$record = [ordered]@{
  schemaVersion = "1.0"
  status = "PRESENTATION_DERIVED_STYLE_AND_DUPLICATE_SUPPRESSION"
  sourceFile = $Source.Replace("\", "/")
  sourceSha256 = $sourceHash
  derivedFile = $Output.Replace("\", "/")
  derivedSha256 = $derivedHash
  generatedAt = (Get-Date).ToUniversalTime().ToString("o")
  viewBox = $xml.DocumentElement.GetAttribute("viewBox")
  pathCount = $xml.SelectNodes("//svg:path", $ns).Count
  geometryFingerprint = [ordered]@{ algorithm = "SHA-256"; fields = @("id", "d", "transform"); source = $sourceFingerprint; derived = $fingerprintHex; equal = ($fingerprintHex -eq $sourceFingerprint) }
  stylePolicy = [ordered]@{ primary = "coastline-candidate/national-line candidate: #c8b98f, 1.16px, opacity 0.78"; secondary = "province-line candidate: #6e8595, 0.68px, opacity 0.34"; semantics = "UNKNOWN" }
  hiddenInsetDuplicatePathIds = $hiddenPathIds
  geometryPolicy = [ordered]@{ pathDataChanged = $false; transformChanged = $false; viewBoxChanged = $false; pathOrderChanged = $false; hiddenInsetDuplicates = $hiddenPathIds.Count }
}
$metadataDirectory = Split-Path -Parent $metadataPath
New-Item -ItemType Directory -Force -Path $metadataDirectory | Out-Null
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $metadataPath -Encoding UTF8
Write-Output "source_sha256=$sourceHash"
Write-Output "derived_sha256=$derivedHash"
Write-Output "geometry_fingerprint=$fingerprintHex"
