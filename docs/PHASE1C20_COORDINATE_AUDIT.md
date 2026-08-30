# Phase 1C-20: Coordinate Alignment Audit

The WGS84 longitude/latitude values remain unchanged. The existing visual V
anchors were audited against the calibrated LCC + SpatialBridge transform and
are retained for city label placement because they represent the pixels a user
sees in the official SVG.

The recorded 17-point affine fit has RMSE 12.1946 V px, mean 10.2852 px,
95th percentile 20.3315 px and maximum 27.6791 px. This is a visual registration
residual, not an error in the city longitude/latitude source.

The top and left graticule labels now use the same LCC + SpatialBridge +
`object-fit: contain` frame as the solar field. They no longer use evenly spaced
CSS distribution, so labels follow the displayed map frame during resize.

See `assets/map/metadata/control-points-v2.json` for the source hashes and
acceptance decision.
