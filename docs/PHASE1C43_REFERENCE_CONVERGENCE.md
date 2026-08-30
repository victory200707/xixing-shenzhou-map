# Phase 1C-43: Reference convergence pass

## Objective

Bring the existing map closer to the supplied reference image while preserving
the scientific solar calculation and the official map source.

## Implemented

- Increased the contrast of the blue-night, twilight, and warm-day color ramp.
- Added a computed warmness field and a restrained blurred bloom, derived from
  solar altitude and clipped to the visual mainland mask.
- Strengthened the DEM-driven relief response and the final hillshade multiply
  pass so ridges and valleys remain visible after sunrise.
- Derived a runtime line-only overlay from the same
  `assets/map/svg/presentation-coastline.svg`; the opaque body remains below the
  solar field while official boundaries and coastlines are redrawn above it.
- Kept the South Sea inset independent and above the mainland solar field.
- Kept map scale, city coordinates, UTC/WGS84/LCC/SpatialBridge chain, and all
  official SVG geometry unchanged.

## Visual result

The result now has the reference hierarchy:

`deep blue night -> blue-violet twilight -> amber transition -> warm gold day`

Terrain relief remains directional, with darker western valleys and stronger
sun-facing eastern ridges. The terminator is represented by a broad soft band
plus a thin core line. The overlay no longer washes out the official province
and coastline linework.

## Acceptance

URL: `http://127.0.0.1:8766/index.html?phase1c43`

Screenshots:

- `docs/screenshots/phase1c43-reference-0500.png`
- `docs/screenshots/phase1c43-reference-0600.png`
- `docs/screenshots/phase1c43-reference-0800.png`

Verified in the browser at 05:00, 06:00, and 08:00 on 2026-06-21:

- warm light remains inside the mainland visual region;
- western land stays cool/dark while eastern land becomes warm;
- the transition is continuous and not a rectangular gradient;
- Tibet south, Taiwan, and Hainan remain covered;
- official linework remains visible above the color field;
- South Sea inset remains separate;
- console error/warning count is 0.

## Limitation

The reference contains substantially higher-resolution terrain and cinematic
post-processing than the available z7 visual asset. This pass closes the major
composition and layer-order gap; a true Copernicus GLO-30 replacement would
improve ridge detail further but is not required for the current visual result.

`TECHNICAL SOLAR FIELD PREVIEW — NOT FORMAL LAND MASK`
