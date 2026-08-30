# Phase 1C-9H Solar Field and Mask Gate

## Decision

`BLOCKED_TERRAIN_JPG_MASK`

The current JPG-derived candidate fails the required black/white gate: eastern offshore water has alpha `1.0`, while Guangzhou, Hainan, and Taiwan interior samples are below the `0.90` land threshold. Therefore no solar color layer is connected.

`APPROXIMATE_VISUAL_MASK — NOT A GEOGRAPHIC SOURCE`

`TECHNICAL SOLAR FIELD PREVIEW — NOT FORMAL LAND MASK`

## Immediate correction

The rectangular solar color field, gray-brown tint, screen-direction gradient, and all mask/JPG page references are disabled. `terrain-registered.png` and `approx-land-mask.png` are not requested by the page. The solar Canvas is transparent except for one low-opacity `-0.833°` civil-sunrise curve calculated through the existing UTC -> WGS84 -> solar altitude -> LCC -> SpatialBridge -> SVG V chain.

No `path3` outline fill, dilation, flood fill, hand-drawn contour, CSS linear gradient, JPG rectangle, or visible Mask stroke/glow is used.

## Browser baseline verification

At the HTTP entry `http://127.0.0.1:4173/index.html`, summer-solstice states 05:00, 06:00, and 08:00 were loaded. Each state has 14 city markers, no `approx-land-mask` image element, no rectangular color layer, and zero browser console errors/warnings.

| State | Capture | SHA-256 |
| --- | --- | --- |
| 05:00 | `docs/screenshots/phase1c9h-clean-0500.png` | `C02889913084239CED93A16D6A092A82F679A0E091ACE2DD5489CD27986E10FF` |
| 06:00 | `docs/screenshots/phase1c9h-clean-0600.png` | `424475A6187161FDDC45EA5B62C80110F7F5A6DBD960627937AA12A5E03AA7A2` |
| 08:00 | `docs/screenshots/phase1c9h-clean-0800.png` | `F78454E71FAB2B6B4B3F8E7DED126F79C4F4EDF2EA68ED5A5CA748C73E03D1F9` |

These are clean baseline captures, not land-color acceptance captures.

## Offline Mask evidence

The JPG registration and candidate remain available only for audit:

- Black/white preview: `docs/screenshots/phase1c9f-terrain-jpg-mask-bw.png`
- Official overlay: `docs/screenshots/phase1c9f-terrain-jpg-mask-overlay.png`
- Pixel samples: `docs/phase1c9f-terrain-jpg-mask-samples.json`
- Candidate status: `BLOCKED_TERRAIN_JPG_MASK`

No further JPG iteration is performed in this phase. A future integration requires a new trustworthy fill source and a passing overlay/pixel review first.

## Protected official files

`official-master.eps`, `official-audit.svg`, `clean-map.svg`, `presentation-map.svg`, and `official-south-sea.svg` were not modified. No website geometry, city coordinate, UI, or solar formula was changed.
