# Phase 1C-2A Map Hierarchy Refine

## Scope

This pass adjusts only the static presentation layer. The official EPS,
`official-audit.svg`, and `clean-map.svg` remain immutable.

## Audit Findings

- The page loads an external SVG through `<img>`.
- `clean-map.svg` contains one filled candidate and 858 stroked paths.
- The mask audit marks the filled candidate as a thin print-outline band, not a
  reliable land silhouette.
- SVG objects have no authoritative semantic IDs for mainland, national border,
  provincial border, coastline, Hainan, Taiwan, or inset semantics.
- Therefore all automatic semantic names remain `UNKNOWN`.

## Presentation Derivative

`assets/map/svg/presentation-map.svg` is derived from `clean-map.svg` by
`tools/create_presentation_map.ps1`. The script changes only presentation
attributes (`style` and `class`); it retains every path `d`, transform, viewBox,
and source order.

Existing style groups are treated as visual groups only:

- primary linework: the existing `#d2b472` group, 1.10px, opacity 0.72;
- secondary linework: the existing `#4b7892` group, 0.72px, opacity 0.40;
- accent linework: the existing `#a9976f` group, 0.82px, opacity 0.52;
- body-fill candidate: existing `#091b2c` fill, opacity 0.80, semantic UNKNOWN.

These groups must not be interpreted as verified national or provincial
boundaries. The stronger group is only a presentation hierarchy.

The requested national-boundary-only brightening is intentionally not applied:
the source does not provide a reliable national/provincial/coastline semantic
identifier. The current result reduces the overly bright province-like linework
and preserves a stronger-vs-secondary visual contrast without inventing a
national outline. A dedicated national-boundary style requires an audited
semantic layer.

## Verification Boundary

No official path geometry, DEM, mask, solar calculation, warm field, or map
reprojection was introduced. Hainan, Taiwan, South China Sea inset, cities, and
all other official linework remain supplied by the source-derived SVG.

## Integrity And Browser Check

- `clean-map.svg` SHA-256: `51d3eb706ecab3e0c07878ecc203bdd81df52a4a9474766bf3b05515043c9d72`
- `presentation-map.svg` SHA-256: recorded in `assets/map/metadata/presentation-map.json` after regeneration.
- Geometry fingerprint (`id`, `d`, `transform`) is identical before and after:
  `0e954d47738601eaa32b063db765d72d712cf8dbba0e454dcbfa980a3a9e8ace`.
- Official source hashes remain unchanged:
  - EPS: `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC`
  - Audit SVG: `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0`
- Browser check URL: `http://127.0.0.1:4173/index.html`.
- The presentation SVG loaded successfully, the axes remained external HTML,
  and 11 city markers remained present. Main map, Hainan, Taiwan, and the
  South China Sea inset were visible in the screenshot at
  `docs/screenshots/phase1c2a-map-hierarchy-refine.png`.
