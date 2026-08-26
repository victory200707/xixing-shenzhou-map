# Phase 1C-2B: Initial Solar Field

## Status

Implemented as an isolated browser Canvas layer using the fixed demonstration
instant `2026-06-21 05:00` Beijing time (`2026-06-20T21:00:00Z`). The layer is
inserted below the official presentation SVG and above the cool abstract relief.
The official EPS, Audit SVG, Clean SVG, and South China Sea derivative are not
modified.

## Coordinate path

Solar altitude is evaluated from UTC instant, WGS84 longitude/latitude, solar
declination and equation-of-time. Each sample is then transformed through the
existing Lambert Conformal Conic (25/47 degree standard parallels, 105 degree
central meridian) and the calibrated affine P-to-V matrix in
`spatial_bridge.json`. V coordinates are converted to the rendered SVG
`object-fit: contain` rectangle before drawing.

## Visual scope

The renderer draws only low-opacity twilight and near-horizon warm cells. It is
not a DEM, does not infer elevation, and does not draw a pixel-space longitude
line. The South China Sea inset remains a separate visual domain and is not
reprojected by this main-map field.

## Verification and limitations

`solar-field.js` passes Node syntax checking and produces finite solar altitude
values. High-precision event and altitude validation remains owned by
`src/astronomy/solar.js` and its tests; the local Windows dependency install is
currently blocked by pnpm symlink permissions, so those tests must be run once
`astronomy-engine` and `suncalc` are available. The field is intentionally fixed
until a reviewed timeline state is connected.
