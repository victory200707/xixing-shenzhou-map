# Project Version

- Current version: `v0.1.0`
- Current phase: Phase 1C-1 static frontend skeleton
- Last stable version: `v0.1.0`
- Map source status: official source retained in local Git under the approved private-repository policy
- Audit SVG status: immutable, visually verified, retained in local Git under the approved private-repository policy
- Clean map status: derived presentation asset retained in local Git under the approved private-repository policy
- SpatialBridge status: fitted; precision improvement required before real DEM alignment
- Terrain status: Mock pipeline verified; real DEM blocked pending source data
- Solar system status: not started

## Baseline Scope

The `v0.1.0` baseline commit contains code, documentation, metadata, processing
scripts, lightweight reproducible assets, Mock output, and visual verification
material. The next local commit records the approved addition of the map assets
that were intentionally excluded from `v0.1.0`.

The following map assets are retained in local Git under the approved
private-repository policy:

- `assets/map/source/official-master.eps`
- `assets/map/svg/official-audit.svg`
- `assets/map/svg/clean-map.svg`
- historical EPS/PDF/PS candidates under `analysis/phase1a/`

Future real DEM files such as `assets/map/source/dem.tif` remain untracked
until a traceable source, licence, and approved storage policy are recorded.

The official source EPS SHA-256 is:

`8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC`

The Audit SVG SHA-256 is:

`D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0`

These map files remain byte-preserved and must not be modified. Their source,
SHA-256, review status, and derivation history are recorded in map metadata.
Private repository visibility is an access control, not a substitute for any
future publication or redistribution review.

## Remote Policy

No remote repository or GitHub repository URL has been configured. The approved
remote policy is private visibility with the current official map assets included.
Remote setup and push require the user to provide or confirm the target URL.
