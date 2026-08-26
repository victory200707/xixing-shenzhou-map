# Phase 1C-2A Terrain Reference Audit

## Scope

This record covers a **visual-reference** processing experiment only. It does
not add a terrain layer to the website and does not modify any official map
geometry.

## Source

- Source asset: `assets/map/source/terrain-reference-gs2016-1609.jpg`
- Displayed title: China Terrain Map, 1:16,000,000
- Source approval number visible in the source: `GS(2016)1609`
- Source dimensions: `4961 x 3508` px
- Source SHA-256: `4DE0617DC3A1D457C09E4BA24480331E85CE3F1615FBE0EA61340F5FE996A1AC`
- Geographic reference: no embedded EPSG, WKT, ground-control-point metadata,
  or declared projection was supplied with the JPG.

## Derived Draft

- Generator: `tools/process_terrain_texture.ps1`
- Output: `assets/map/raster/terrain-texture-v.png`
- Output dimensions: `3025 x 2137` px
- Intended V canvas: `0 0 3025.3333 2137.3333`
- Output SHA-256: recorded in `assets/map/metadata/terrain-texture.json`
- Processing: frame crop, downsampling, luminance extraction, reduced-contrast
  navy remap, and suppression of the source legend/inset print regions.

## Decision

`DRAFT_NOT_APPROVED_FOR_RENDER`.

The JPG includes a separate map frame, labels, boundaries, graticule, rivers,
legend, and South China Sea inset. Its raw pixel coordinates have **not** been
registered to the existing G-P-V SpatialBridge. The draft must not be loaded
as a website layer yet: fitting it directly to the V canvas would create an
unverified second map alignment.

The official map remains the only geographic-fact layer:

- `assets/map/source/official-master.eps` is unchanged.
- `assets/map/svg/official-audit.svg` is unchanged.
- `assets/map/svg/clean-map.svg` is unchanged.

## Required Gate Before Render Use

1. Capture source-image pixel coordinates for at least six labelled
   graticule intersections, distributed across the main frame.
2. Map those longitude/latitude values through the existing G-P-V bridge.
3. Fit and report an image-pixel-to-V transform with residuals.
4. Reject the source if residuals show visible coast/boundary disagreement.
5. Suppress all non-relief map furniture, then place the official Clean SVG
   above the registered texture.

No solar field, sunrise calculation, DEM, mask, or animation was added.
