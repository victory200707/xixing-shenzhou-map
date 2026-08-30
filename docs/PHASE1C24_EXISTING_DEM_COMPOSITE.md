# Phase 1C-24: Existing DEM Visual Composite

## Scope

This iteration uses the existing `dem-hillshade-v.png` asset only. No map
geometry, astronomical formula, projection, or city coordinate was changed.
The goal is to expose the existing relief texture while retaining the dynamic
solar color field.

## Changes

- Reduced browser-side terrain blur from `0.65px` to `0.35px`.
- Expanded terrain normalization from the 10th-90th to the 5th-95th percentile
  and applied a mild power curve to preserve mountain contrast.
- Increased the cool terrain texture range while keeping it clipped by the
  same-source visual land mask.
- Reduced solar field alpha so the warm/cool layer tints the terrain instead of
  visually replacing it.
- Bumped asset query versions to `phase1c24` to avoid stale browser resources.

## Layer order

```text
background
-> existing DEM hillshade x same-source visual mask
-> solar altitude color field x same-source visual mask
-> unchanged official SVG
-> South Sea inset
-> cities and UI
```

## Verification

Verified at the local HTTP entry point:

`http://127.0.0.1:8766/index.html?phase1c24`

Checked summer solstice `2026-06-21` at `05:00`, `06:00`, and `08:00` BJT.
The terrain remains visible inside the daytime warm layer, the west/east
transition moves with solar altitude, and no browser `error` or `warn` entries
were recorded.

## Limitations

This is still an `APPROXIMATE_DEM_HILLSHADE_VISUAL_TEXTURE`, not a formal
elevation product. The existing z5 Terrarium-derived raster is coarser and less
photographic than the reference image. Exact reference parity requires a
higher-resolution DEM or licensed terrain imagery and a second pass using
luminance-preserving color blending.
