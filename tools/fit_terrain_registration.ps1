param(
  [string]$ControlPoints = (Join-Path $PSScriptRoot '..\assets\map\metadata\terrain-registration-control-points.json'),
  [string]$Output = (Join-Path $PSScriptRoot '..\assets\map\metadata\terrain-registration.json')
)

$ErrorActionPreference = 'Stop'

function Get-FileSha256([string]$Path) {
  return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

function Solve-LinearSystem([double[,]]$Matrix, [double[]]$Vector) {
  $n = $Vector.Length
  for ($pivot = 0; $pivot -lt $n; $pivot++) {
    $maxRow = $pivot
    for ($row = $pivot + 1; $row -lt $n; $row++) {
      if ([Math]::Abs($Matrix[$row, $pivot]) -gt [Math]::Abs($Matrix[$maxRow, $pivot])) { $maxRow = $row }
    }
    if ([Math]::Abs($Matrix[$maxRow, $pivot]) -lt 1e-12) { throw 'Control points cannot determine a stable affine transform.' }
    if ($maxRow -ne $pivot) {
      for ($col = $pivot; $col -lt $n; $col++) { $temp = $Matrix[$pivot, $col]; $Matrix[$pivot, $col] = $Matrix[$maxRow, $col]; $Matrix[$maxRow, $col] = $temp }
      $tempV = $Vector[$pivot]; $Vector[$pivot] = $Vector[$maxRow]; $Vector[$maxRow] = $tempV
    }
    $divisor = $Matrix[$pivot, $pivot]
    for ($col = $pivot; $col -lt $n; $col++) { $Matrix[$pivot, $col] /= $divisor }
    $Vector[$pivot] /= $divisor
    for ($row = 0; $row -lt $n; $row++) {
      if ($row -eq $pivot) { continue }
      $factor = $Matrix[$row, $pivot]
      for ($col = $pivot; $col -lt $n; $col++) { $Matrix[$row, $col] -= $factor * $Matrix[$pivot, $col] }
      $Vector[$row] -= $factor * $Vector[$pivot]
    }
  }
  return $Vector
}

function Fit-Affine($Points) {
  $normal = [double[,]]::new(3, 3)
  $rhsX = [double[]]::new(3)
  $rhsY = [double[]]::new(3)
  foreach ($point in $Points) {
    $row = [double[]]@([double]$point.sourcePixel[0], [double]$point.sourcePixel[1], 1.0)
    for ($i = 0; $i -lt 3; $i++) {
      $rhsX[$i] += $row[$i] * [double]$point.expectedV[0]
      $rhsY[$i] += $row[$i] * [double]$point.expectedV[1]
      for ($j = 0; $j -lt 3; $j++) { $normal[$i, $j] += $row[$i] * $row[$j] }
    }
  }
  $copyX = [double[,]]::new(3, 3); $copyY = [double[,]]::new(3, 3)
  for ($i = 0; $i -lt 3; $i++) { for ($j = 0; $j -lt 3; $j++) { $copyX[$i, $j] = $normal[$i, $j]; $copyY[$i, $j] = $normal[$i, $j] } }
  $coeffX = Solve-LinearSystem $copyX $rhsX
  $coeffY = Solve-LinearSystem $copyY $rhsY
  return @($coeffX, $coeffY)
}

$input = Get-Content -LiteralPath $ControlPoints -Raw | ConvertFrom-Json
$points = @($input.controlPoints)
if ($points.Count -lt 6) { throw "At least six control points are required; found $($points.Count)." }
$errors = @()
foreach ($point in $points) {
  if ($null -eq $point.sourcePixel -or $point.sourcePixel.Count -ne 2 -or $null -eq $point.expectedV -or $point.expectedV.Count -ne 2) { $errors += "$( $point.id ): sourcePixel and expectedV must each have two values."; continue }
  foreach ($field in @('longitudeDeg', 'latitudeDeg')) { if ($null -eq $point.$field) { $errors += "$( $point.id ): missing $field." } }
}
if ($errors.Count) { throw "Input validation failed:`n- $($errors -join "`n- ")" }

$fit = Fit-Affine $points
$residuals = @()
foreach ($point in $points) {
  $x = [double]$point.sourcePixel[0]; $y = [double]$point.sourcePixel[1]
  $predictedX = $fit[0][0] * $x + $fit[0][1] * $y + $fit[0][2]
  $predictedY = $fit[1][0] * $x + $fit[1][1] * $y + $fit[1][2]
  $dx = $predictedX - [double]$point.expectedV[0]; $dy = $predictedY - [double]$point.expectedV[1]
  $error = [Math]::Sqrt($dx * $dx + $dy * $dy)
  $residuals += [ordered]@{ id = $point.id; name = $point.name; deltaV = @([Math]::Round($dx, 3), [Math]::Round($dy, 3)); errorPx = [Math]::Round($error, 3) }
}
$sumSquares = ($residuals | ForEach-Object { $_.errorPx * $_.errorPx } | Measure-Object -Sum).Sum
$rmse = [Math]::Sqrt($sumSquares / $residuals.Count)
$max = ($residuals | ForEach-Object { [double]$_.errorPx } | Measure-Object -Maximum).Maximum
$status = if ($rmse -le 15) { 'FIT_ACCEPTABLE_FOR_VISUAL_REVIEW' } else { 'REJECT_OR_RECAPTURE' }
$outputObject = [ordered]@{
  schemaVersion = '1.0'
  status = $status
  purpose = 'Image-pixel to existing V-coordinate registration for a terrain visual texture. Not a source of geographic facts.'
  controlPointsFile = 'assets/map/metadata/terrain-registration-control-points.json'
  controlPointsSha256 = Get-FileSha256 $ControlPoints
  sourceImage = $input.sourceImage
  sourceImageSha256 = $input.sourceImageSha256
  spatialBridge = $input.spatialBridge
  spatialBridgeSha256 = $input.spatialBridgeSha256
  model = 'affine_source_pixel_to_V'
  matrix = @(@($fit[0][0], $fit[0][1], $fit[0][2]), @($fit[1][0], $fit[1][1], $fit[1][2]), @(0.0, 0.0, 1.0))
  metrics = [ordered]@{ pointCount = $points.Count; rmsePx = [Math]::Round($rmse, 3); maxErrorPx = [Math]::Round($max, 3); acceptanceThresholdPx = 15 }
  residuals = $residuals
  generatedAt = (Get-Date).ToUniversalTime().ToString('o')
}
$outputObject | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Output -Encoding utf8
Write-Output "Terrain registration fit: $status"
Write-Output "Points: $($points.Count) | RMSE: $([Math]::Round($rmse, 3)) px | maximum: $([Math]::Round($max, 3)) px"
foreach ($entry in $residuals) { Write-Output ("{0}: delta=({1}, {2}) px, error={3} px" -f $entry.id, $entry.deltaV[0], $entry.deltaV[1], $entry.errorPx) }
