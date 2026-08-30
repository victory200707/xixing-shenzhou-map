# Phase 1C-27: Reference Visual Convergence

## Scope

This phase responds to the reference comparison while keeping the map scale
unchanged. Only presentation parameters were adjusted; official SVG/EPS
geometry, city coordinates, astronomical formulas, LCC, SpatialBridge, and
the same-source visual mask remain unchanged.

## Changes

- Increased saturation and alpha only in the `-2°` to daylight solar bands so
  the 05:00 eastern land reads as warm gold rather than gray-brown.
- Kept the six-stage altitude ramp and the wider twilight transition.
- Reduced the global DEM canvas opacity from `.92` to `.78` so terrain supports
  the solar story instead of dominating it.
- Reduced the official map's blue drop-shadow strength to avoid a neon outline.
- Did not change `.map-visual` scale or transform origin.

## Verification

Checked `2026-06-21` at `05:00`, `06:00`, and `08:00` BJT in a 1536x1024
browser viewport. The warm region advances east-to-west with time, western
terrain remains cool and readable, and eastern terrain retains relief under
the warm tint. Tibet south, Hainan, and Taiwan remain covered without a visible
mask gap. Browser console `error` and `warn` counts were zero.

## Remaining gap to the reference

The reference contains higher-resolution, photographic terrain and a more
directional atmospheric glow. The current result is the closest practical
version using the existing z5 DEM and official linework. Further similarity
requires a higher-resolution terrain raster or a separate licensed imagery
source; it is not a map-scale or astronomy-formula issue.
