# Phase 1C-9F Solar Field Rollback

## Result

`TECHNICAL SOLAR FIELD PREVIEW`

The failed Mask and JPG candidate remain offline diagnostics. The page does not load `terrain-registered.png` or `approx-land-mask.png`, and no land-color layer is connected.

## Correction

The visual regression came from a rectangular Canvas-wide solar colour fill in `src/astronomy/solar-field.js`, not from an accepted land Mask. That fill, its radial edge treatment, and its per-pixel warm/cool compositing have been removed.

The transparent Canvas now renders only low-opacity reference curves calculated by this unchanged chain:

`UTC -> WGS84 longitude/latitude -> solar altitude -> LCC -> SpatialBridge -> SVG V -> page pixel`

The 0 degree geometric boundary and -0.833 degree sunrise boundary remain. No fixed screen line, fixed longitude, CSS map gradient, rectangle fill, trapezoid, Mask stroke, outline, or glow is used.

## Verification

| Summer solstice BJT | Result |
| --- | --- |
| 05:00 | No hard vertical division, rectangular colour block, or broad warm sea tint |
| 06:00 | No hard vertical division, rectangular colour block, or broad warm sea tint |
| 08:00 | No hard vertical division, rectangular colour block, or broad warm sea tint |

At all three times the official main SVG and South Sea inset remain above the transparent solar Canvas. City markers remain present (14), and the browser console has zero errors and warnings.

## Integration gate

No JPG or Mask processing was continued during this rollback. A future land-colour layer may be considered only after a black/white review proves continuous mainland white fill, black sea, retained Hainan and Taiwan, and an excluded South Sea inset.

`CURRENT_MASK_RENDERING_DISABLED_DUE_TO_OUTLINE_LEAK`

`APPROXIMATE_VISUAL_MASK — NOT A GEOGRAPHIC SOURCE`

## Protected assets

| File | SHA-256 |
| --- | --- |
| `assets/map/source/official-master.eps` | `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC` |
| `assets/map/svg/official-audit.svg` | `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0` |
| `assets/map/svg/clean-map.svg` | `51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72` |
| `assets/map/svg/presentation-map.svg` | `6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F` |
| `assets/map/svg/official-south-sea.svg` | `2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D` |
