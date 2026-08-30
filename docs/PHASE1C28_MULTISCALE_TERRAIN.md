# Phase 1C-28: Existing DEM Multiscale Terrain

This phase keeps the current map, Mask, projection, and solar calculations. The
existing DEM hillshade is rendered at two spatial scales: a broad low-frequency
component for plateaus and mountain systems, plus the original higher-frequency
component for ridge detail. The components are blended before the cool terrain
palette is applied, reducing uniform noise while retaining relief.

Solar opacity now varies continuously within each altitude interval. Twilight
and daylight therefore build progressively rather than appearing as a fixed
opaque band. The map scale remains unchanged.

Verification target: `http://127.0.0.1:8766/index.html?phase1c28` at summer
solstice `05:00`, `06:00`, and `08:00` BJT. The layer remains clipped by the
same-source visual Mask and the official SVG remains above it.

Status: `EXISTING_DATA_VISUAL_APPROXIMATION`.
