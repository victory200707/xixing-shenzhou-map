# Phase 1C-29: Directional Relief Approximation

The existing DEM-derived hillshade now participates in the solar field as a
visual slope proxy. For every sampled WGS84 location, the existing solar
position calculation supplies altitude and azimuth; the local luminance
gradient of the registered hillshade supplies a visual aspect and slope term.
The resulting factor modulates the solar tint before the same-source land mask
is applied.

The sunrise boundary also receives a broad, low-alpha glow behind the existing
thin terminator line. This is a presentation effect only; it does not alter the
scientific event threshold or map geometry.

No official SVG/EPS, city coordinates, Mask source, LCC, SpatialBridge, or map
scale was changed. The effect remains an approximation because the current
input is a z5 hillshade, not a native elevation grid.

Verification target: `http://127.0.0.1:8766/index.html?phase1c29`, summer
solstice `05:00`, `06:00`, `08:00` BJT.
