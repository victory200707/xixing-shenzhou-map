# Phase 1C-2A-1 Official Map Mask Audit

Date: 2026-08-25  
Status: **BLOCKED - no official land mask generated**

## Scope

Only `assets/map/svg/clean-map.svg` was inspected. `assets/map/source/official-master.eps`, `assets/map/svg/official-audit.svg`, and `assets/map/svg/clean-map.svg` were not modified. No DEM, solar calculation, animation, UI change, CRS assignment, reprojection, or external download was performed.

A future mask is a texture clipping layer only. It is not a geographic-fact source.

## Inputs

| Asset | SHA-256 | V coordinate domain |
| --- | --- | --- |
| `assets/map/source/official-master.eps` | `8709aa9590acaef2926fab9ad6979665c7caf8469ec7186ea33edeb9838368cc` | No GIS CRS assigned |
| `assets/map/svg/official-audit.svg` | `d661148e382f91d3972d0825f70ebf2fc45de995cd99d489f865229fdc5514e0` | `0 0 3025.3333 2137.3333` |
| `assets/map/svg/clean-map.svg` | `51d3eb706ecab3e0c07878ecc203bdd81df52a4a9474766bf3b05515043c9d72` | `0 0 3025.3333 2137.3333` |

The clean SVG root is `3025.3333 x 2137.3333`: 859 visible paths, one group and one `defs` element. No path has `display:none` or `visibility:hidden`.

## Object audit

No path has a semantic ID or layer name identifying mainland, coast, province boundary, island, label, legend or the South China Sea inset. All 859 paths therefore remain semantically **UNKNOWN**.

| Style structure | Count | Decision |
| --- | ---: | --- |
| `fill:#091b2c; stroke:none` | 1 | Candidate inspected and rejected |
| `fill:none; stroke:#d2b472` | 650 | Unknown stroke-only object |
| `fill:none; stroke:#4b7892` | 207 | Unknown stroke-only object |
| `fill:none; stroke:#a9976f` | 1 | Unknown stroke-only object |

The lone filled candidate is `path3`: one `M` with repeated `C` segments, existing transform `matrix(0.13333333,0,0,-0.13333333,0,2137.3333)`, and V bounds `x=125.9217-2631.3399`, `y=58.1034-1941.1546`.

## Rendering test

`tools/generate_map_mask.py` interprets only that existing `M/C` data and the existing transform. It samples curves for rasterization without rewriting SVG data, cropping, mirroring, simplifying, reprojecting or assigning a CRS. Integer PNG sampling would be `3025 / 3025.3333` in X and `2137 / 2137.3333` in Y.

The temporary 3025x2137 audit render was a thin, closed print-outline band. Its coverage was `0.0212407136` (2.124%), not a solid land silhouette. All 17 human-picked controls were outside its alpha region. Its lower bound ends above Haikou at `V=(1699.6476, 2011.1210)`, so it cannot include Hainan. Its maximum `x=2631.3399` is left of the verified South China Sea inset controls `x=2755.3454-2922.8010`, so it cannot include the inset.

No explicit filled object identifies Hainan, Taiwan or the inset. Filling unknown strokes would require semantic inference and is prohibited. The temporary candidate artifacts were discarded; `assets/map/raster/official-land-mask.png` was intentionally not written.

## Results

| Check | Result |
| --- | --- |
| Main map complete | Failed: outline only |
| Hainan complete | Failed: outside candidate extent |
| Taiwan complete | Not safely verifiable |
| South China Sea inset separate | Spatially separate, but not extractable |
| Labels, legend, grid leakage | No unknown stroke was included; no final mask exists |
| Mirror, crop, change to official geometry | None |

`assets/map/metadata/map-mask.json` records the blocked decision. The generator now has a 10% coverage guard and refuses to write a thin-outline candidate as a land mask.

## Required resolution and gate

Provide or authoritatively identify an explicit, audited land-silhouette layer derived from the official source, while retaining the existing EPS, Audit SVG and Clean SVG unchanged. Do not reconstruct a filled surface from unknown outline paths.

**Phase 1C-2A-1 is not accepted. Do not begin Phase 1C-2A-2.**
