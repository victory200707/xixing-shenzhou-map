# Phase 1C-33: High-Resolution Normal Asset and Multiscale Lighting

## Completed

- Generated `assets/map/raster/dem-normal-v.png` at `3025 x 2137` from the
  existing raw Terrarium elevation tiles before grayscale normalization.
- Encoded an ENU terrain normal per V-space pixel; the asset is used only for
  visual slope lighting and never as a map boundary.
- Updated `solar-field.js` to calculate directional light from the terrain
  normal and the existing solar azimuth/elevation.
- Kept the existing low-frequency terrain layer and ridge-detail texture as
  separate visual scales beneath the dynamic solar layer.
- Copernicus GLO-30 was not downloaded or introduced in this phase.

## Acceptance

Target: `http://127.0.0.1:8766/index.html?phase1c33`

- `05:00`, `06:00`, and `08:00` show continuous west-to-east solar movement;
- the daylight region keeps warm terrain brightness rather than a single narrow
  line;
- terrain remains visible in both night and daylight regions;
- the official map, Taiwan, Hainan, Tibet south and South Sea inset remain
  aligned;
- console errors/warnings: 0.

Screenshots:

- `docs/screenshots/phase1c33-normal-0500.png`
- `docs/screenshots/phase1c33-normal-0600.png`
- `docs/screenshots/phase1c33-normal-0800.png`

## Limitation

The source elevation coverage is still z5 Terrarium, so the normal asset is
higher-resolution in the render frame but cannot invent terrain detail absent
from the source. Replacing the source with Copernicus GLO-30 later only changes
the asset-generation step and does not require a new browser rendering API.
