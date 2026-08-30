# Phase 1C-32: DEM Elevation-Driven Terrain Lighting

## Completed

- Generated `assets/map/raster/dem-elevation-v.png` from the existing 35
  Terrarium elevation tiles.
- Registered the raster through the same WGS84, inverse LCC, SpatialBridge and
  SVG V coordinate chain used by the map and solar field.
- Updated `solar-field.js` to use the elevation raster's local gradient for
  visual slope/aspect estimation, with the existing hillshade retained as the
  independent terrain texture layer.
- Increased directional relief and warm daylight range within controlled
  limits to better match the reference image.
- Official SVG/EPS geometry, city coordinates, astronomical formulas, map
  scale, and South Sea inset remain unchanged.

## Browser acceptance

Target: `http://127.0.0.1:8766/index.html?phase1c32`

- 05:00: west remains deep blue; the east has continuous warm light and the
  transition band is visible across the mainland.
- 06:00: the boundary advances westward and terrain relief varies with the
  estimated solar-facing direction.
- 08:00: daylight remains continuous while the terrain texture is still
  readable beneath the warm layer.
- Tibet south, Taiwan and Hainan show no obvious missing-light gap.
- South Sea inset remains dark and independent.
- Console errors/warnings: 0.

Screenshots:

- `docs/screenshots/phase1c32-art-directed-0500.png`
- `docs/screenshots/phase1c32-art-directed-0600.png`
- `docs/screenshots/phase1c32-art-directed-0800.png`

## Limitation

The current source is z5 Terrarium elevation coverage and the generated
analysis raster is 8-bit normalized for visual gradients. It is suitable for
the reference-like presentation but not for quantitative terrain analysis.
Copernicus GLO-30 or SRTM 30m can replace this asset later without changing
the rendering interface.
