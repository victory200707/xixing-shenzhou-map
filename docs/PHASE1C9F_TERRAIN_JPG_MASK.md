# Phase 1C-9F Official Terrain JPG Approximate Visual Mask

## Result

`BLOCKED_TERRAIN_JPG_MASK`

The Phase 1C-9F candidate does not pass its pixel gate. It was not promoted to `assets/map/raster/approx-land-mask.png`, and no page, solar-field, CSS, city, or official SVG file was changed.

`APPROXIMATE_VISUAL_MASK — NOT A GEOGRAPHIC SOURCE`

`TECHNICAL LAND COLOR PREVIEW — NOT FORMAL MAP FILL`

## Input and registration

| Item | Value |
| --- | --- |
| Source image | `assets/map/source/terrain-reference-gs2016-1609.jpg` |
| Source dimensions | 4961 x 3508 |
| Source SHA-256 | `4DE0617DC3A1D457C09E4BA24480331E85CE3F1615FBE0EA61340F5FE996A1AC` |
| Source/date record | Existing local GS(2016)1609 source; processed 2026-08-26 UTC; no new download was performed |
| Control points | `assets/map/metadata/terrain-registration-control-points.json` (8 points) |
| Registration model | affine source-pixel to V |
| Registration RMSE / maximum | 4.686 / 9.952 V units |
| Target viewBox | `0 0 3025.3333 2137.3333` |
| Registered JPG | `assets/map/raster/terrain-registered.png` |
| Registered JPG SHA-256 | `7A4E7E595946BE3AFE6918CED4667071E706B352C7B7C43E825B66AB54DD367A` |

## Candidate method

The candidate uses only the registered JPG's cyan-water pixels and visible blue-purple printed boundary band as segmentation evidence. Existing audited V positions were used as interior seeds and pixel probes only; they did not generate or modify any geometry. The South Sea inset rectangle was excluded from the mainland candidate. A 2 px Gaussian feather was applied after segmentation.

No SVG path was used as input. No outline was dilated into an area, no hand-drawn contour was introduced, and there is no stroke, shadow, or glow in the candidate.

## Pixel gate

Acceptance requires every listed mainland/island probe to be at least 0.90 alpha and every ocean/inset probe to be no more than 0.05 alpha. Values below are 5x5 alpha means.

| Probe | Alpha | Gate |
| --- | ---: | --- |
| Mohe | 0.99498 | pass |
| Beijing | 0.98337 | pass |
| Urumqi | 0.91576 | pass |
| Kashi | 1.00000 | pass |
| Guangzhou | 0.83859 | fail |
| Haikou / Hainan | 0.83655 | fail |
| Taipei / Taiwan | 0.84329 | fail |
| Western mainland / Lhasa | 1.00000 | pass |
| Northeastern mainland / Harbin | 1.00000 | pass |
| Eastern offshore water | 1.00000 | fail |
| Southern offshore water | 0.00000 | pass |
| South Sea inset | 0.00000 | pass |

The eastern offshore-water failure is disqualifying. The candidate also fails the required island and Guangzhou interior threshold. This is consistent with the rendered black/white preview: it contains a large erroneous external region and cannot serve as a mainland fill Mask.

## Review artifacts

| Artifact | SHA-256 | Status |
| --- | --- | --- |
| `tools/phase1c9f-terrain-jpg-mask-candidate.png` | `4673887904A2AA9CAB2BB40A1C11FAAE7E2A3A0EAEF0383AEA60529B6F907012` | rejected candidate |
| `docs/screenshots/phase1c9f-terrain-jpg-mask-bw.png` | `2B237CBDFC4CA8157B4413ECA52B4CD8A6C4027778AD40E1AEDAF4AE65BC01AE` | black/white failure evidence |
| `docs/screenshots/phase1c9f-terrain-jpg-mask-overlay.png` | `A242D281C452C359B74D468DB3A24DC1B52654A80D8D0E93F2C6077BCC44BEBE` | official SVG review overlay; not a source input |
| `docs/phase1c9f-terrain-jpg-mask-samples.json` | `C9024D755B988495FE98A9C4D6C2B13F051A0B891A7A033617A3CFF4A9C91F03` | blocked result and pixel samples |

## Integration decision

No land-color layer may be connected. The page retains the recovered Phase 1C-9D technical solar-field preview and has no `approx-land-mask.png` request, image element, Canvas clip, Mask outline, stroke, or glow.

`CURRENT_MASK_RENDERING_DISABLED_DUE_TO_OUTLINE_LEAK`

## Official map protection

No official EPS or SVG was modified. Current SHA-256 checks are:

| File | SHA-256 |
| --- | --- |
| `assets/map/source/official-master.eps` | `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC` |
| `assets/map/svg/official-audit.svg` | `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0` |
| `assets/map/svg/clean-map.svg` | `51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72` |
| `assets/map/svg/presentation-map.svg` | `6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F` |
| `assets/map/svg/official-south-sea.svg` | `2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D` |

The JPG registration output and rejected candidate are independent raster diagnostics only. Further Mask work requires a new reliable source or an explicit change of evidence rules; this phase stops here rather than iterating the failed extraction.
