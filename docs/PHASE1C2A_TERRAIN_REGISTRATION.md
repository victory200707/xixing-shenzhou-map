# Phase 1C-2A Terrain JPG Registration

## Status

`HUMAN_CONTROL_POINTS_REQUIRED`.

The supplied 1:16,000,000 terrain-map JPG is a visual-reference source only.
It is not a DEM, cannot replace the official map, and has no embedded
geographic registration. It must not be stretched behind the official SVG
until this registration gate passes.

## Capture

Open `tools/terrain_registration_picker.html` directly in a modern browser.
For at least six labelled graticule intersections inside the terrain map main
frame:

1. Click the intersection in the image.
2. Enter the exact printed longitude and latitude.
3. Record the point.
4. Use points across the full map: west, east, north, south, and centre.

Do not use a coastline, a label, the outer page frame, the legend, or the
South China Sea inset as a main-map control point. Download the completed JSON
and replace `assets/map/metadata/terrain-registration-control-points.json`.

## Fit Gate

Run:

```powershell
powershell -ExecutionPolicy Bypass -File tools/fit_terrain_registration.ps1
```

The script fits only an affine transform from JPG pixel coordinates to the
existing SVG V coordinates and writes `assets/map/metadata/terrain-registration.json`.
It reports every residual. A result whose RMSE is over 15 V pixels is rejected
for page rendering and requires better control-point coverage or a different
fit model.

## Current Capture

On 2026-08-25, eight human-clicked main-map graticule intersections were
captured: 95E/45N, 95E/35N, 95E/30N, 105E/35N, 115E/40N, 115E/30N,
110E/25N, and 120E/45N. The resulting affine fit has an RMSE of 4.686 V
pixels and a maximum residual of 9.952 V pixels. This passes the numerical
gate for visual review only; it does not authorize rendering until a human
checks the transformed relief against the unchanged official map.

## Registered Draft

`tools/render_registered_terrain_texture.ps1` consumes only the approved
control-point fit and writes `assets/map/raster/terrain-texture-registered-v.png`.
It removes the source-page legend and source inset before applying the main-map
affine transform, reduces all content fivefold to suppress print furniture, and
recolors it as a cold, low-contrast texture. The output is deliberately marked
`AWAITING_HUMAN_VISUAL_REVIEW` and is not loaded by `index.html`.

## Preview Decision

The first registered preview was inspected on 2026-08-26. Although its control
point fit passed, it exposed residual page-frame, legend, and source-inset
blocks outside the main terrain area. It is therefore marked
`REJECTED_FOR_RENDER_WITHOUT_OFFICIAL_LAND_MASK` and must not be added to the
website. The registration metadata remains useful; the rejection is solely
about safely clipping a raster texture without inventing or deriving an
unaudited land silhouette.

## After Acceptance

Only after a human visual review confirms that the registered terrain texture
does not visibly disagree with official boundaries may it be used below the
unchanged `clean-map.svg`. The official SVG continues to draw all national,
provincial, coastal, island, and South China Sea geographic facts.
