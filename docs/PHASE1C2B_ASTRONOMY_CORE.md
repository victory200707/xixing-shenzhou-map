# Phase 1C-2B: Astronomy Core

## Scope

This phase ports the validated pure solar-calculation boundary from the read-only
`morning-china-0.2.1` archive. It does not modify or load any map geometry, render
a terminator, create warm light, add animation, or alter the existing static UI.

## Implementation

- `src/astronomy/solar.js` owns UTC/Beijing-date conversion, solar positions,
  solar field state, light-stage classification, twilight, rise/set, and seasons.
- `src/data/places.js` contains a limited WGS84 city reference list sourced from
  the verified Phase 1B-2 control-point metadata. It does not create geometry.
- `test/solar.test.mjs` compares the field-altitude formula with direct
  `astronomy-engine` calculations across a China-wide grid and compares event
  times with `suncalc`.

## Numerical Acceptance Criteria

- Solar field vs. direct engine altitude: at most `0.01 deg`.
- Sunrise, sunset, and dawn vs. SunCalc: at most `1 minute`.
- All internal instants: UTC `Date`; all calendar dates displayed as
  `Asia/Shanghai` / Beijing time.

## Deliberate Boundary

The browser UI remains static until these tests pass. A later renderer may read
only the output of this module and the existing G-to-V SpatialBridge; it must
not infer solar values from screen pixels or modify official SVG paths.
