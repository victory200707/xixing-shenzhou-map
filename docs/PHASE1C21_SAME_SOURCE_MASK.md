# Phase 1C-21: Same-Source Visual Land Mask

The page now derives a display-only land mask from the exact
`assets/map/svg/presentation-coastline.svg` that is visible in the map. The
linework is rasterized in the SVG V frame, closed only with a small raster
operation, flood-filled from the outside, and reduced to the dominant mainland
plus explicit Hainan/Taiwan components. Natural Earth is no longer used by the
runtime solar or terrain clipping path.

Layer order remains:

`background -> solar/terrain visual layers -> official SVG linework -> South Sea inset -> cities -> UI`

This preserves official borders, labels and the independent South Sea inset.
The output is intentionally a visual aid and must be labeled:

`APPROXIMATE_VISUAL_MASK - NOT A GEOGRAPHIC SOURCE`

The solar field still computes every sample using UTC, WGS84, solar altitude,
LCC and SpatialBridge. The mask supplies only visual clipping and does not
change astronomy, city coordinates or map geometry.
