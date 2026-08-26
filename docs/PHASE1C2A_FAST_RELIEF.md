# Phase 1C-2A-Fast: Abstract Map Relief Layer

## Status

Implemented as a static, replaceable browser Canvas layer. This is an abstract visual relief layer, not real elevation data.

### Static Base Refine

The static-base refinement removes all warm Canvas and CSS light fields. The Canvas now contains only cool blue-grey material, transparent-edge depth fields, and low-amplitude grain. Each field fades fully before the Canvas edge, so it cannot create a hard horizontal or rectangular colour band.

The longitude and latitude labels are separate HTML-only visual markers outside the map container. They do not restore SVG grid paths, assign CRS, or alter official geometry.

## Scope And Controls

- The layer uses only low-frequency colour, soft fixed-direction illumination, transparent-edge depth fields, and deterministic low-opacity grain.
- It does not use DEM data, a land mask, solar calculations, animation, contours, rivers, mountains, or inferred geographical features.
- The Canvas is a rectangular visual-stage layer aligned to the displayed `clean-map.svg` bounds. It makes no claim that the texture is clipped to land.
- No official map file or official path geometry was modified: `official-master.eps`, `official-audit.svg`, and `clean-map.svg` remain separate, unchanged source/derived assets.

## Layer Order

1. Page background
2. Abstract Canvas visual layer
3. `clean-map.svg` official geographic linework
4. City markers positioned from verified V coordinates
5. Existing UI panels and timeline

## Responsive Behaviour

The Canvas measures the rendered SVG image rectangle after its existing CSS transform. It uses that same rectangle for CSS placement and dimensions, so it preserves the SVG aspect ratio without a new coordinate transform, stretching, mirroring, CRS assignment, or SpatialBridge rewrite. Rendering occurs only on SVG load and browser resize; it has no continuous animation loop.

## Verification Boundary

This phase does not generate a land mask, process/download real DEM data, or begin astronomy, dawn, terminator, or UI feature work. The official SVG remains on top and must be visually checked for complete boundaries, Hainan, Taiwan, the South China Sea inset, and city-marker alignment before progressing.
