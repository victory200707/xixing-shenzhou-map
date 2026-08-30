# Phase 1C-25: Luminance-Preserving Solar Composite

## Scope

This phase keeps the existing DEM, map geometry, Mask, astronomical formulas,
and projection chain. It changes only how the solar color field is presented
over the terrain texture.

## Changes

- Replaced the four visually dominant solar colors with a six-stop continuous
  altitude ramp at `-18`, `-12`, `-6`, `-2`, `-0.833`, and positive altitude.
- Tested `soft-light` blending, but rejected it because transparent Canvas
  compositing made the solar tint too weak in the current layer stack.
- Kept `normal` blending with reduced alpha and the six-stop ramp; this
  preserves useful DEM detail while retaining visible day/night color.
- Kept the existing scientific thresholds and WGS84 / LCC / SpatialBridge
  sampling chain unchanged.
- Bumped page and asset query versions to `phase1c26` for deterministic reloads.

## Layer order

```text
background
-> DEM hillshade x same-source visual land mask
-> continuous solar tint x same-source visual land mask
-> official SVG and South Sea inset
-> cities and UI
```

## Verification

The local page was reloaded at the reference desktop size (`1440x900`) and
checked at summer solstice `2026-06-21` for `05:00`, `06:00`, and `08:00` BJT.
The east-to-west transition moves with time, terrain remains visible inside
the warm region, and the browser recorded no `error` or `warn` entries.

## Limitations

The effect is an existing-data visual approximation. The z5 Terrarium-derived
Hillshade is still coarser than the reference image's likely high-resolution
terrain imagery. A photographic match would require a higher-resolution DEM or
licensed terrain raster; that is intentionally outside this phase.
