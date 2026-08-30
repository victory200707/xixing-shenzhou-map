# Phase 1C-30: Solar Layer Stack Correction

## Result

The solar field now renders above the official map body fill and below the
South Sea inset and city layer. This fixes the previous failure where the
official SVG's opaque `#path3` body fill covered the solar Canvas, making the
timeline and astronomical data change without a visible land-light change.

## Layer order

`terrain texture -> official map body/linework -> solar land color -> South Sea inset -> cities/UI`

The solar Canvas remains clipped by the same-source visual land mask in the
shared SVG V display frame. No official SVG/EPS geometry, projection, city
coordinates, or solar formula was changed. The map scale remains unchanged.

## Visual acceptance

- 05:00, summer solstice: west remains deep blue, east is warm gold, with a
  broad blue-purple to gold transition and a visible but soft terminator.
- 06:00: the transition advances westward while daylight areas remain
  continuously warm instead of collapsing to a thin line.
- 08:00: the mainland is predominantly in a stable low-saturation warm layer;
  terrain relief remains visible beneath the tint.
- Taiwan and southern Tibet show no obvious missing-light gap.
- South Sea inset remains an independent dark official layer.
- Browser console: 0 errors, 0 warnings.

## Limitation

The terrain source is the existing registered visual hillshade, not a native
elevation grid. Directional relief is therefore a visual approximation. The
solar field remains a `TECHNICAL SOLAR FIELD PREVIEW — NOT FORMAL LAND MASK`.
