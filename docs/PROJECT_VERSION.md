# Project Version

- Current version: `v0.1.0`
- Current phase: Phase 1C-1 static frontend skeleton
- Last stable version: `v0.1.0`
- Map source status: official source retained locally; publication scope pending confirmation
- Audit SVG status: immutable, visually verified, retained locally outside the baseline commit
- Clean map status: derived presentation asset retained locally pending source publication confirmation
- SpatialBridge status: fitted; precision improvement required before real DEM alignment
- Terrain status: Mock pipeline verified; real DEM blocked pending source data
- Solar system status: not started

## Baseline Scope

The baseline commit contains code, documentation, metadata, processing scripts,
lightweight reproducible assets, Mock output, and visual verification material.

The following remain local and are intentionally not tracked in this baseline:

- `assets/map/source/official-master.eps`
- `assets/map/svg/official-audit.svg`
- `assets/map/svg/clean-map.svg`
- historical EPS/PDF/PS candidates under `analysis/phase1a/`
- any future real DEM such as `assets/map/source/dem.tif`

The official source EPS SHA-256 is:

`8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC`

The Audit SVG SHA-256 is:

`D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0`

These files remain byte-preserved in the local workspace. They are excluded
because formal publication and redistribution permission has not been confirmed;
Git LFS would manage size only and would not resolve that licensing question.

## Remote Policy

No remote repository, GitHub repository, visibility, or upload scope has been
configured. Remote setup requires a separate confirmation of repository URL,
visibility, and official map/DEM asset policy.

