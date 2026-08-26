# Phase 1C-6E: Right Rail Style Refinement

## Location Comparison

The existing narrow glass panel keeps its two-column city layout and central
divider. Sunrise values remain the strongest typography, city A uses warm gold
and city B uses cool blue, and the difference row is centered between subtle
rules. A small `早` to `晚` curve was added as a visual relationship cue; it is
not a replacement for the calculated sunrise values.

The detail area now has a compact `更多信息（城市 A / 城市 B）` heading followed
by four aligned rows: local time, civil dawn, solar altitude, and longitude.
Shortcut cities remain Beijing, Urumqi, Guangzhou, Harbin, Lhasa, and Haikou;
no Kunming or custom-city placeholder was reintroduced.

## Astronomy Stage Summary

The vertical six-stage list remains unchanged in structure. The lower summary
now presents all six stages horizontally with small dot icons, muted labels,
small times, and a one-pixel baseline. Borders, block backgrounds, and button-
like card treatment were removed. The active stage is computed from the current
city altitude and event times and receives only a restrained gold icon, time,
and baseline highlight.

## Dynamic Linkage

Panel values continue to come from the existing SPA adapter and shared state.
City selection, timeline movement, season changes, and mode switches update the
panel, sunrise markers, stage values, and current-stage highlight. No values are
hard-coded and no solar formula or map coordinate transform was changed.

## Wide-Screen Verification

The page was checked at 1280x800, 1440x900, and 1920x1080. The right rail stays
292px wide, the map remains the dominant region, the footer contains only the
timeline, and the South Sea inset remains visible. Automated browser captures:

- `docs/screenshots/phase1c6e-location-compare.png` (141,409 bytes,
  SHA-256 `ACB5A5C31998400E7CA9BE2D7D5939DB2F9E9962A1CF041E1BD050370F7B627E`)
- `docs/screenshots/phase1c6e-astronomy-stage.png` (137,018 bytes,
  SHA-256 `EE2B829BA1F37BF833A1ECD2DCB63E783AEA1B6C323322FA5DD3E72FCCFAACB7`)

## Protected Assets

No official geometry was edited. The protected hashes remain:

- `official-master.eps`: `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC`
- `official-audit.svg`: `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0`
- `clean-map.svg`: `51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72`
- `presentation-map.svg`: `6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F`
- `official-south-sea.svg`: `2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D`

## Known Risk

Six summary items are intentionally compact to fit the 292px rail. At very
narrow mobile widths the rail uses the existing responsive flow and may stack
below the map; no desktop content is clipped or overlapped.
