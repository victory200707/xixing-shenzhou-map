# Phase 1C-4: Solar Light Field

Date: 2026-08-26

## Audit findings

The previous trapezoid/block appearance came from 1 degree WGS84 cells being
filled directly after LCC projection. The geographic extent was then clipped
only by the rectangular Canvas, so projected cell edges were visible. The
official SVG and SpatialBridge were not the source of the distortion.

## Implementation

`src/astronomy/solar-field.js` now performs a dense offscreen resampling pass.
Each sample is converted from the displayed SVG rectangle back through the
inverse P-to-V affine bridge and inverse LCC to WGS84, then evaluated with the
NOAA solar-altitude formula. The low-resolution field is enlarged with browser
image smoothing, removing visible cell boundaries. No path data is written to
the SVG.

Solar classes are based on the following altitude thresholds:

- `< -18°`: astronomical night
- `-18° .. -12°`: astronomical twilight
- `-12° .. -6°`: nautical twilight
- `-6° .. -0.833°`: civil twilight
- `>= -0.833°`: daylight after sunrise

Two separate geographic curves are rendered: a subdued dashed `0°` geometric
day/night boundary and a warmer dashed `-0.833°` sunrise boundary. They are
sampled in WGS84 and projected through SpatialBridge, not drawn as fixed screen
lines.

## Mask and inset policy

`assets/map/metadata/map-mask.json` remains
`BLOCKED_INSUFFICIENT_IDENTIFIABLE_LAND_GEOMETRY`. No reliable official land
mask was available, so formal China-land clipping was not performed. The field
is limited to the actual rendered map-image rectangle and uses only a soft
Canvas-edge fade. It does not use a projected longitude/latitude bounding box,
so the fallback cannot create a trapezoid-shaped extent. It is explicitly a
visual preview, not a land polygon. The south-sea inset stays
in its independent official layer and is not processed by the main-map field.

## Parameters

```js
{
  nightOpacity: 0.105,
  twilightOpacity: 0.105,
  daylightOpacity: 0.105,
  warmBandOpacity: 0.115,
  terminatorGlow: 0.34,
  boundaryPreservation: 0.86
}
```

Warm tones are restricted to solar altitudes near the horizon and remain below
the official linework layer. No DEM, elevation claim, solar animation, or
official geometry modification is introduced.

## Known risk

Until an independently audited land silhouette is supplied, the field cannot
be declared a formally clipped China-only light field. This is the only blocker
to the final clipping acceptance gate.
