$s = Get-Content -Raw -LiteralPath 'assets/map/source/1123.svg'
$path = $null
foreach ($m in [regex]::Matches($s, '<path\b[^>]*>')) {
  $a = $m.Value
  $st = ([regex]::Match($a, 'style="([^"]*)"')).Groups[1].Value
  if ($st -match 'fill:#d35f5f') { $path = ([regex]::Match($a, '\bd="([^"]*)"')).Groups[1].Value; break }
}
if (-not $path) { throw '1123 outer boundary path not found' }
$svg = @"
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3025.3333 2137.3333" width="3025.3333" height="2137.3333">
  <rect width="3025.3333" height="2137.3333" fill="#071b38"/>
  <g transform="matrix(8.97 0 0 7.18 1323 1022)">
    <g transform="translate(-49.349798,-28.696144)">
      <path d="$path" fill="none" stroke="#ffffff" stroke-width="1.65" stroke-linejoin="round" stroke-linecap="round"/>
    </g>
  </g>
</svg>
"@
Set-Content -LiteralPath 'analysis/1123-boundary-v.svg' -Value $svg -Encoding utf8
Write-Output 'analysis/1123-boundary-v.svg'
