# Phase 1C-3 Astronomy Integration

Time state is stored as a Beijing calendar date plus a minute-of-day and is
converted to a real UTC `Date` before every solar calculation. WGS84 longitude
and latitude are passed to the solar altitude function. The solar field then
projects samples through LCC and the calibrated P-to-V affine bridge before
converting V to the displayed SVG rectangle.

Layer order remains background, cool relief, solar Canvas, official
presentation SVG, south-sea SVG, city markers, and UI. The south-sea inset is
kept in its independent visual domain. Solar rendering is deliberately low
opacity; it does not alter official paths or claim DEM/elevation accuracy.

The high-precision `solar.js` event API is retained. Its package dependencies
were not available through the current local module links, so browser event
readouts use the existing field formula until the dependency installation is
repaired and the numerical test suite is rerun.

## Reference Repository

The verified reference is https://github.com/victory200707/morning-china,
branch `main`, file `src/domain/solar.ts`. It uses `astronomy-engine` 2.1.19
(MIT) for solar position, seasons, rise/set and twilight events, and `suncalc`
2.0.1 (BSD-2-Clause) for independent checks. The current project keeps its
own implementation boundary and does not copy the repository's page structure.

The comparison panel now exposes local solar time (longitude offset from
120E), civil dawn at the -6 degree threshold, current solar altitude and
longitude for both selected places. Values are calculated from the same UTC
instant used by the map field and formatted in Beijing time.
