# Phase 1B-1: Official EPS to Audited SVG

## Status

**AUDIT_PASSED.** The externally converted SVG was reviewed against the
official EPS PNG by a human reviewer. The mainland, boundaries, islands, and
South China Sea inset were confirmed visually without path loss. The converted
file is now archived as `assets/map/svg/official-audit.svg`.

Generating a raster-backed SVG, manually tracing the preview, or embedding an
unrenderable EPS payload would not satisfy the audit requirement and would make
the result non-auditable.

## Source registered

- Source: `assets/map/source/official-master.eps`
- SHA-256: `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC`
- Size: `20,165,997` bytes
- Corel creator: `CorelDRAW X8`
- EPS creation date: `2023-08-08 14:30:03`
- Printed review number: `GS(2023)2767号`
- EPS bounding box: `538 439 2807 2042`

## Archived Audit SVG

- File: `assets/map/svg/official-audit.svg`
- SHA-256: `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0`
- Size: `5,624,733` bytes
- SVG `viewBox`: `0 0 3025.3333 2137.3333`
- Width/height: `3025.3333 × 2137.3333`
- Non-empty path elements: `3730`
- Embedded raster images: `0`
- SVG text elements: `0` (text is outlined as paths)
- Conversion tool: Inkscape (recorded in the SVG header; exact version and
  command were not embedded in the supplied file)

## Available visual baseline

The existing source preview is retained for comparison only:

- File: `analysis/phase1a/4o28b0625501ad13015501ad2bfc2187b/preview.png`
- Size: `3025 x 2137` RGB
- SHA-256: `1340B371FE21B82ADDF58C87CC05BA8BA43E9AA0315A1D13F7C3DDA02AA7F769`

Ghostscript reproduced this preview exactly: `3025 x 2137`, identical SHA-256,
and zero pixel difference. The human reviewer then confirmed the archived SVG
against this reference for the required geographic features.

## Conversion and acceptance check

Checked tools on 2026-08-23:

- `pdftoppm`: available, raster-only
- Ghostscript 10.07.1 (bundled with QGIS 3.44.12): used for EPS rendering and
  raster reference verification
- Inkscape: external conversion tool declared by the SVG header
- `pdftocairo` / `rsvg-convert`: unavailable

## Recorded acceptance

The external conversion was accepted after human visual comparison. The
following checks were recorded:

1. record the output SHA-256, SVG `viewBox`, dimensions, and object counts;
2. classify objects conservatively, using `UNKNOWN` where semantics cannot be
   proven;
3. render the SVG at the source-preview dimensions;
4. compare mainland outline, borders, coast, Hainan, Taiwan, and South China
   Sea inset for missing paths, clipping, scaling, mirroring, and text changes;
5. update `assets/map/metadata/audit-svg.json` after these checks passed.

Phase 1B-1 is complete. The next permitted work is the Phase 1B-2 coordinate
picker and control-point capture; no Clean SVG, GeoJSON, Mask, DEM, UI, or
dynamic layer is part of this archive step.
