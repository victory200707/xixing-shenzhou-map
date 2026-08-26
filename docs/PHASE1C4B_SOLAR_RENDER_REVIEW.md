# Phase 1C-4B: Solar Render Review

Date: 2026-08-26

## Root cause

The earlier visual trapezoid was a projected sampling extent, not a solar
terminator. Directly filling geographic cells made their LCC edges visible. A
geographic extent fade repeated the same problem in softer form.

## Revised renderer

`src/astronomy/solar-field.js` now samples the actual rendered map-image
rectangle, inverse-maps each sample to WGS84, calculates solar altitude, and
smoothly enlarges an offscreen field. The only edge fade is based on distance to
the displayed Canvas edges. No longitude/latitude bounding-box edge is drawn.

The renderer draws two independently computed curves:

- `0°`: geometric day/night boundary, cool and very subdued.
- `-0.833°`: sunrise boundary, warm dashed line with restrained glow.

The light field remains below the official presentation SVG and above the cool
relief layer. City markers, labels, UI, and the independent south-sea inset are
not recolored by the field.

## Preview flags

`PREVIEW_MAP_EXTENT_ONLY` and `FORMAL_LAND_MASK_PENDING` remain active. No
unverified path is promoted to a land mask.
