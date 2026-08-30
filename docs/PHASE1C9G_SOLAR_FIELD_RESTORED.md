# Phase 1C-9G Continuous Solar Field Restored

## Status

`TECHNICAL SOLAR FIELD PREVIEW — NOT FORMAL LAND MASK`

The continuous solar field is restored after the rollback that had left only nearly invisible reference lines. It remains a rectangular technical preview because no valid land-fill Mask exists. The failed `approx-land-mask.png`, `terrain-registered.png`, and JPG candidate are not loaded or used by the page.

## Scientific chain

Each low-resolution Canvas sample performs:

`BJT input -> real UTC Date -> inverse display rectangle -> SVG V -> SpatialBridge inverse -> LCC inverse -> WGS84 longitude/latitude -> solar altitude -> color/alpha`

No screen-left/right rule, fixed longitude, fixed vertical line, JPG overlay, mask outline, flood fill, or hand-drawn geometry is involved.

## Visual parameters

| State | Solar altitude | Treatment |
| --- | --- | --- |
| night | `< -6 deg` | deep navy `(6,24,51)`, alpha about `0.17` |
| twilight | `-6 deg to -0.833 deg` | cool blue `(23,54,83)` -> blue-violet `(48,71,102)` -> warm gold `(211,157,89)`, alpha about `0.24` |
| daylight | `> -0.833 deg` | continuous low-saturation warm gold, settling toward `(194,151,94)`, alpha `0.21` to `0.18` |

The twilight ramp is intentionally wider (`-10 deg` to `0.5 deg`) to avoid a visible color jump at the civil sunrise threshold. A single low-opacity `-0.833 deg` auxiliary line remains; the former isolated dual dashed-line branch was removed.

Sampling uses a smoothed `220-360 x 150-250` offscreen grid and a 0.7 px Canvas blur. This is a visual preview only; it is not a land clip or formal map fill.

## Browser verification

HTTP entry: `http://127.0.0.1:4173/index.html`

| BJT | Result |
| --- | --- |
| 2026-06-21 05:00 | East/central area visibly warmer while far west remains deep blue; no hard rectangle or fixed vertical split |
| 2026-06-21 06:00 | Warm transition expands westward; official lines, labels, cities and South Sea inset remain readable |
| 2026-06-21 08:00 | Most displayed extent is brighter and warm-neutral; no grid, trapezoid or hard edge |

All three states loaded 14 city markers, did not contain an approximate-mask image element, and produced zero browser console errors/warnings.

Screenshots (browser viewport 1280 x 720 in the current runtime):

| Time | File | SHA-256 |
| --- | --- | --- |
| 05:00 | `docs/screenshots/phase1c9g-solar-0500.png` | `401826D7E03D47F15D4F70EF3E7FE734C9416DFDBED651BDA9B1471633333CC8` |
| 06:00 | `docs/screenshots/phase1c9g-solar-0600.png` | `33E6A2C6B879E813862C8583C2504904CDA7AC016CCFDF60C36DE82B763FBE78` |
| 08:00 | `docs/screenshots/phase1c9g-solar-0800.png` | `7F25F6046A882BA379BD915894459C289E8D2ADCC706B70BD8021ACA1083D2D8` |

## Protected assets

Official map files were not modified:

| File | SHA-256 |
| --- | --- |
| `official-master.eps` | `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC` |
| `official-audit.svg` | `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0` |
| `clean-map.svg` | `51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72` |
| `presentation-map.svg` | `6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F` |
| `official-south-sea.svg` | `2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D` |

## Limitation

The solar field affects the full displayed map rectangle, including sea, because a verified land alpha source is unavailable. It must continue to be labeled a technical preview and must not be presented as formal Chinese land illumination.
