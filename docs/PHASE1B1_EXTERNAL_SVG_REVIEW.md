# Phase 1B-1 External SVG Review

## Decision

The user-supplied SVG is a strong **conversion candidate** and passes the
structural vector checks. It is not yet promoted to
`assets/map/svg/official-audit.svg` because the exact Inkscape version/command
is absent and a local browser render comparison could not be completed in this
environment.

## Evidence

- Candidate: `C:/Users/HUAWEI/Downloads/中国地图 1∶740万 (界线版 无邻国 无河流 线划(一) (1).svg`
- Candidate SHA-256: `d661148e382f91d3972d0825f70ebf2fc45de995cd99d489f865229fdc5514e0`
- Candidate size: `5,624,733` bytes
- SVG version: `1.1`
- Root size/viewBox: `3025.3333 × 2137.3333`, `0 0 3025.3333 2137.3333`
- Source EPS SHA-256: `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC`

The root frame is exactly the EPS PostScript bounding box (`538 439 2807
2042`) converted from points to pixels at 96 dpi. The file contains 3730
non-empty `<path>` elements, all using the same inverse-Y scale transform. It
contains no `<image>`, `<text>`, `<foreignObject>`, `<use>`, `<clipPath>`,
`<mask>`, `<filter>`, or external reference.

## Interpretation

This is a vector conversion, not a PNG/JPG wrapper. Text appears to have been
converted to outlined paths, which is acceptable for an audit SVG but means
semantic labels cannot be recovered from the SVG alone. The 3730 paths versus
the EPS's 3327 Corel object markers is not by itself a defect; one source object
may become multiple SVG paths.

The SVG has no CRS, WKT, or geographic control points, as required. Its
coordinates remain visual/print coordinates only.

## Remaining acceptance check

Render this SVG at `3025 × 2137` and compare with the existing official EPS
preview. Confirm mainland outline, national/provincial boundaries, coastline,
Hainan, Taiwan, and the South China Sea inset. Reject the candidate if any
feature is missing, mirrored, clipped, or materially rescaled.

Until that render comparison is recorded, the existing
`audit-svg.json` remains `blocked-pending-vector-converter`; no Clean SVG,
Mask, GeoJSON, DEM, UI, or dynamic layer is created.
