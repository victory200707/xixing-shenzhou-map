# Phase 1C-3 Solar Library Evaluation

## Recommended Independent Library

Repository: https://github.com/udivankin/sunrise-sunset-js

The project is a dedicated JavaScript/TypeScript solar calculator based on the
National Renewable Energy Laboratory Solar Position Algorithm (NREL SPA). Its
documented API covers solar position, sunrise, sunset, solar noon, civil,
nautical and astronomical twilight, golden/blue hour, timezone handling and
polar day/night null results. The README states an uncertainty of about
0.0003 degrees and cites Reda & Andreas (2004) and NREL report TP-560-34302.

The repository is public, actively maintained, browser-compatible (ESM and
CommonJS), and has no runtime dependencies. The package metadata currently
reports version `3.3.1`; its README states MIT licensing. The package metadata
lists ISC, so the exact published package license should be rechecked at the
version lock point and its license text retained in third-party notices.

## Why It Fits

`getSolarPosition()` supplies the altitude/azimuth needed by the geographic
solar field and terminator. `getSunTimes()` / `getTwilight()` supply the event
times needed by the comparison panel, including civil dawn at the -6 degree
threshold. Every result is a JavaScript `Date` instant and can therefore pass
through the project's UTC state and `Asia/Shanghai` display formatter.

## Integration Status

The 3.3.1 browser bundle is now archived under `vendor/sunrise-sunset-js/`
with a SHA-256 manifest in `assets/astronomy/metadata/sunrise-sunset-js.json`.
`src/astronomy/solar-spa.js` adapts its `getSolarPosition` and `getSunTimes`
APIs to the project's UTC/WGS84 contracts. The comparison panel now uses SPA
for sunrise, civil dawn and current altitude. The existing `solar.js` remains
available for cross-checks.

## Next Implementation Step

Run the numerical cross-check suite against representative Chinese cities and
resolve the README MIT versus package metadata ISC license discrepancy before
public redistribution.
