# Phase 1C-2A Static Base Refine

## Scope

This pass corrects the static presentation layer only. It does not modify, derive,
or reinterpret official geographic geometry.

## Changes

- Restored external HTML-only longitude labels: `70°E` through `140°E`.
- Restored external HTML-only latitude labels: `50°N` through `10°N`.
- Removed the warm Canvas east field and diagonal warm light field.
- Disabled the former map pseudo-element light overlay.
- Reduced the Canvas layer to low-opacity cool blue-grey material, transparent-edge
  depth fields, and deterministic low-amplitude grain.
- Kept the official clean SVG above the Canvas, with cool outline shadow only.

## Validation

- Validated through `http://127.0.0.1:4173/index.html`, not `file://`.
- Desktop layout displays 8 longitude labels and 5 latitude labels outside the map.
- The Canvas is aligned to the rendered SVG bounds and has `opacity: 0.27`.
- Eleven existing city markers render from the approved control-point V coordinates.
- The official main map, Hainan, Taiwan, and South China Sea inset remained visible.
- No internal grid path was restored.

## Boundary

No DEM, land mask, solar calculation, terminator, animation, or new geographic
geometry was introduced. The Canvas remains an abstract visual relief layer, not
real elevation data.

## Official Asset Integrity

- `official-master.eps`: unchanged
- `official-audit.svg`: unchanged
- `clean-map.svg`: unchanged
