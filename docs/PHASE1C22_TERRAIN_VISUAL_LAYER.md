# Phase 1C-22: Registered Terrain Visual Layer

## Scope

This phase adds a separate visual terrain-relief layer using the registered
GS(2016)1609 terrain image. It is a presentation texture only, not a DEM and
not a source of geographic facts.

## Layer order

`background -> terrain texture x same-source visual mask -> solar color field x same-source visual mask -> unchanged official SVG -> South Sea inset -> cities -> UI`

The terrain and solar layers use the same SVG V contain frame and the same
approximate visual land mask. Official map geometry and astronomical formulas
are unchanged.

## Source and limitations

- Source: `assets/map/source/terrain-reference-gs2016-1609.jpg`
- Registered texture: `assets/map/raster/terrain-texture-registered-v.png`
- Registration RMSE: approximately 4.686 px; maximum residual approximately 9.952 px.
- The source contains visual relief, labels, and map furniture. Rendering applies
  grayscale, blur, percentile normalization, and a cool blue-gray remap before
  masking. It must not be interpreted as elevation or DEM data.
- Status: `APPROXIMATE_VISUAL_TERRAIN_TEXTURE - NOT DEM`

## Runtime changes

- `renderRelief()` now delegates to `renderTerrainRelief()`.
- The old radial-gradient placeholder was removed.
- The high-resolution registered texture replaces the 202 x 143 low-frequency
  preview asset.
- Solar colors remain driven by UTC, WGS84, solar altitude, LCC, and
  SpatialBridge, and remain above the terrain texture.

## Acceptance

Checked at 05:00, 06:00, and 08:00 BJT on a wide viewport. Screenshots:

- `docs/screenshots/phase1c22-terrain-0500.png`
- `docs/screenshots/phase1c22-terrain-0600.png`
- `docs/screenshots/phase1c22-terrain-0800.png`

The map remains interactive with no console errors or warnings. Mainland,
Hainan, and Taiwan use the same visual clipping path; the South Sea inset and
official labels are not used as terrain-mask data.
