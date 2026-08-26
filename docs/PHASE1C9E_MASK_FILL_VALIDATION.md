# Phase 1C-9E Mask Fill Validation

## Result

`BLOCKED_MASK_IS_OUTLINE_ONLY`

`presentation-map.svg:path3` cannot provide a land-fill mask through permitted rasterization. The prior `assets/map/raster/approx-land-mask.png` remains a rejected diagnostic artifact. It is not loaded by the page and must not be used by the terrain or solar layers.

`APPROXIMATE_VISUAL_MASK — NOT A GEOGRAPHIC SOURCE`

## Exact path3 validation

The source path was copied into `assets/map/svg/approx-land-mask-source.svg` without changing its `id`, raw `d`, transform, or the SVG viewBox.

| Property | Value |
| --- | --- |
| Source path | `presentation-map.svg:path3` |
| Source viewBox | `0 0 3025.3333 2137.3333` |
| Path transform | `matrix(0.13333333,0,0,-0.13333333,0,2137.3333)` |
| Rendering | `fill: #ffffff; fill-opacity: 1; stroke: none; fill-rule: evenodd` |
| Path closure evidence | 1 `M`; 0 `Z` commands |
| Permitted processing | direct rasterization and threshold-only black/white diagnostic |
| Explicitly not used | path closure, flood fill, dilation, morphology, outline glow, manual drawing |

The direct render produces a narrow white contour only. It does not fill the Chinese mainland interior.

## Pixel samples

All values are 5x5 alpha means on the direct, white-fill/no-stroke `path3` render. Full machine-readable evidence is in `docs/phase1c9e-path3-samples.json`.

| Location | Expected for a usable fill mask | Alpha |
| --- | --- | --- |
| Beijing | near 1 | 0.0 |
| Urumqi | near 1 | 0.0 |
| Guangzhou | near 1 | 0.0 |
| Haikou / Hainan | near 1 | 0.0 |
| Taipei / Taiwan | near 1 | 0.0 |
| Lhasa / western mainland | near 1 | 0.0 |
| Harbin / northeastern mainland | near 1 | 0.0 |
| Eastern offshore water | near 0 | 0.0 |
| Southern offshore water | near 0 | 0.0 |
| South Sea inset | near 0 | 0.0 |

The ocean and South Sea tests are correctly transparent, but every required mainland and island interior test is also transparent. This fails the essential fill requirement.

## Diagnostics

| Artifact | SHA-256 | Finding |
| --- | --- | --- |
| `tools/path3-render-original.png` | `18EB445DAFF1496107592446391B00039BA383A707870A915AE55FB120B7CD35` | Raw white-fill path render: contour only |
| `docs/screenshots/phase1c9e-path3-mask-bw.png` | `F4AB5BC43154B3B0F3D945A4CDAD7E6AEE221F8A14C058683595A0E0FD73BE66` | Threshold-only black/white diagnostic: no mainland fill |
| `docs/screenshots/phase1c9e-path3-overlay.png` | `0B411A0AEEC0175266AD0AB41875107A845F9B94A873A6D6A0B0C37C5A85FB9A` | Official display overlay: contour aligns as linework, not an area |

## Page recovery

The page no longer requests `approx-land-mask.png`, applies no mask clipping, and has no visible Mask outline, stroke, glow, or shadow. `terrainVisualLayer` and `solarFieldLayer` remain below the official SVG. The current solar display is restored to its existing technical geographic-extent preview rather than claiming land clipping.

Browser verification at `http://127.0.0.1:4173/index.html` found no Mask image element and no browser-console entries. The brown contour leak is absent.

`CURRENT_MASK_RENDERING_DISABLED_DUE_TO_OUTLINE_LEAK`

## Official assets unchanged

| File | SHA-256 |
| --- | --- |
| `assets/map/source/official-master.eps` | `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC` |
| `assets/map/svg/official-audit.svg` | `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0` |
| `assets/map/svg/clean-map.svg` | `51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72` |
| `assets/map/svg/presentation-map.svg` | `6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F` |
| `assets/map/svg/official-south-sea.svg` | `2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D` |

## Gate

No land color layer may be connected until a distinct, verifiable source contains actual land-fill geometry or independently supports a valid non-hand-drawn visual mask. This validation does not authorize `landColor = baseLandColor x solarColor x landMaskAlpha`.
