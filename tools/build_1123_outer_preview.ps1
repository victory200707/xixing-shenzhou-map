$s = Get-Content -Raw -LiteralPath 'assets/map/source/1123.svg'
$paths = [regex]::Matches($s, '<path\b[^>]*>')
$selected = New-Object System.Collections.Generic.List[string]
foreach ($m in $paths) {
  $a = $m.Value
  $st = ([regex]::Match($a, 'style="([^"]*)"')).Groups[1].Value
  if ($st -match 'fill:#d35f5f') {
    $d = ([regex]::Match($a, '\bd="([^"]*)"')).Groups[1].Value
    $selected.Add(('  <path d="' + $d + '" fill="#ffffff" fill-rule="evenodd"/>'))
  }
}
$svg = "<?xml version=`"1.0`"?><svg xmlns=`"http://www.w3.org/2000/svg`" viewBox=`"0 0 210 297`"><g transform=`"translate(-49.349798,-28.696144)`">" + [string]::Join("`n", $selected) + '</g></svg>'
Set-Content -LiteralPath 'analysis/1123-outer-preview.svg' -Value $svg -Encoding utf8
Write-Output "selected=$($selected.Count)"
