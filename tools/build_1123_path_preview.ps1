$s = Get-Content -Raw -LiteralPath 'assets/map/source/1123.svg'
$paths = [regex]::Matches($s, '<path\b[^>]*>')
$selected = New-Object System.Collections.Generic.List[string]
$seen = @{}
foreach ($m in $paths) {
  $a = $m.Value
  $d = ([regex]::Match($a, '\bd="([^"]*)"')).Groups[1].Value
  if (-not $d) { continue }
  $n = ([regex]::Matches($d, '-?\d+(?:\.\d+)?')).Count
  if ($n -lt 10000) { continue }
  if ($seen.ContainsKey($d)) { continue }
  $seen[$d] = $true
  $selected.Add(('  <path d="' + $d + '" fill="#ffffff" fill-rule="evenodd"/>'))
}
$svg = "<?xml version=`"1.0`" encoding=`"UTF-8`"?><svg xmlns=`"http://www.w3.org/2000/svg`" viewBox=`"0 0 210 297`"><g transform=`"translate(-49.349798,-28.696144)`">`n" + [string]::Join("`n", $selected) + "`n</g></svg>"
Set-Content -LiteralPath 'analysis/1123-large-paths.svg' -Value $svg -Encoding utf8
Write-Output "selected=$($selected.Count)"
