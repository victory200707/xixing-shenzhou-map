# Phase 1C-4B: Morning China Research

Date: 2026-08-26

## Source

The reference snapshot is the locally archived
`C:\Users\HUAWEI\Downloads\morning-china-0.2.1.zip`, corresponding to
`https://github.com/victory200707/morning-china` (`main`). The snapshot includes
`src/domain/solar.ts` and records `astronomy-engine` 2.1.19 (MIT) as the primary
solar engine and `suncalc` 2.0.1 (BSD-2-Clause) for independent event checks.
No old map or UI files were imported into this project. The current project
retains its own vendored NREL SPA adapter for browser event readouts.

## Reusable algorithmic ideas

- Validate WGS84 latitude/longitude before calculation.
- Build a Beijing-local calendar date as a real UTC `Date`.
- Classify geometric solar altitude at -18°, -12°, -6°, and -0.833°.
- Generate terminators as geographic altitude isolines, then project them.

These ideas are reimplemented in the current module boundary. The old page
structure, `@svg-maps/china` geometry, old inset, and old UI are not reused.

## Adaptation boundary

Current chain:

`UTC + WGS84 → solar altitude → inverse/forward LCC → SpatialBridge → SVG V → Canvas`

The continuous field uses the same mathematical thresholds but keeps the
current official map and layer architecture intact.
The archive contains dependency notices but no separate repository-level
license file for the application code. Therefore this project reimplemented
the documented equations and did not copy source code; dependency licenses are
recorded in `THIRD_PARTY_NOTICES.md`.
