# Phase 1C-40: Art-directed terrain lighting

## Outcome

The map now combines the existing WGS84 -> LCC -> SpatialBridge -> SVG V solar
field with a higher-contrast, multi-scale terrain appearance. The target is the
provided reference's cinematic relief: cool night land, a continuous warm dawn
band, and visible ridges and valleys after sunrise.

## Changes

- Kept the official `presentation-coastline.svg` and all map geometry unchanged.
- Kept the solar altitude/azimuth calculation and terminator thresholds unchanged.
- Added `dem-hillshade-z7-art-v.png`, a registered visual-only derivative of the
  z7 Terrarium hillshade. It applies a bounded contrast/gamma remap only; no
  pixels are relocated and no boundary is created.
- Added high-pass ridge contrast and hillshade modulation to the solar Canvas.
- Increased directional normal response so sun-facing slopes and back-facing
  valleys remain legible beneath the solar tint.
- Added a low-strength multiply pass for sharp ridge/valley separation. It is
  clipped by the same mainland visual mask as the solar field.
- Kept the independent terrain Canvas beneath the official SVG and kept the
  South Sea inset as a separate layer.

## Asset record

`assets/map/raster/dem-hillshade-z7-v.png` remains the source hillshade.
The art-directed derivative is:

- File: `assets/map/raster/dem-hillshade-z7-art-v.png`
- Dimensions: `1513 x 1069`
- SHA-256: `C831E26F4ACB090E97E500AB2D800111F43D37260AF4630F209E4ADD3D13D71A`
- Source: AWS elevation-tiles-prod Terrarium z7 mosaic already recorded in
  `assets/map/metadata/dem-z7-v.json`
- Limitation: `APPROXIMATE_DEM_MULTISCALE_VISUAL_ASSET`, not a geographic
  boundary or quantitative elevation product.

## Browser acceptance

URL: `http://127.0.0.1:8766/index.html?phase1c40`

Verified at summer solstice 2026-06-21:

- 05:00: western land remains cool/dark while the eastern side is in warm
  transition; the terminator is continuous across the mainland.
- 06:00: the warm region advances westward and terrain relief remains visible.
- 08:00: the mainland is continuously lit with clear multi-scale ridges and
  valleys; Tibet south, Taiwan and Hainan remain covered.
- South Sea inset is not tinted by the mainland field.
- Console error/warning count: 0.

Screenshots:

- `docs/screenshots/phase1c40-terrain-0500.png`
- `docs/screenshots/phase1c40-terrain-0600.png`
- `docs/screenshots/phase1c40-terrain-0800.png`

## Status

`TECHNICAL SOLAR FIELD PREVIEW — NOT FORMAL LAND MASK`

The effect is an art-directed visualization layered on the official map; the
derived DEM asset must not be interpreted as a replacement for official map
geometry.
