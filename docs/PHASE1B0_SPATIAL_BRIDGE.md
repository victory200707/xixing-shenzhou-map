# Phase 1B-0: Spatial Bridge Architecture

## Status and Boundary

This document defines the bridge between the official visual map candidate and
the geographic calculation system. It does **not** freeze `MASTER_MAP`, change
the EPS, download DEM data, generate SVG/GeoJSON/Mask assets, or begin website
implementation.

The central decision is to maintain two coordinate domains:

```text
Official Visual Domain (V)
  EPS -> future audit SVG -> fixed visual viewBox

Geographic Calculation Domain (G)
  WGS84 longitude/latitude -> DEM, cities, solar calculations

G -> display projection P -> calibrated bridge B -> V
```

The EPS is authoritative for the visual geographic facts it contains, but is
not treated as a GIS dataset merely because it is vector artwork.

## 1. Two Map Systems

### A. Official Visual Map

Source: the user-provided 1:7,400,000 CorelDRAW EPS candidate, retained as an
immutable source file.

Responsibilities:

- national outline and coast as supplied;
- national and provincial boundary linework as supplied;
- Hainan, Taiwan, islands, and the supplied South China Sea inset;
- the official visual arrangement and print coordinate relationships.

The eventual browser representation is an audit-preserving SVG (and masks or
Canvas clips derived from it only after the source and permissions are closed).
Its coordinates are called `V` coordinates. They are not longitude/latitude.

### B. Geographic Calculation Layer

Responsibilities:

- WGS84 longitude/latitude for cities and scientific calculations;
- DEM sampling and hillshade generation;
- solar altitude, azimuth, sunrise/sunset, dawn, and terminator geometry;
- geographic graticule and any future spatial query.

This layer is independent of EPS object coordinates. Its primary data contract
is `GeoPoint { longitudeDeg, latitudeDeg }` in WGS84 (`EPSG:4326`) unless a
source explicitly documents another datum.

## 2. Route Comparison

Scores use 1 (poor) to 5 (good) for this product. “Accuracy” refers to the
ability to preserve a documented geographic relationship; it does not imply
that an unreferenced EPS becomes accurate GIS data.

| Criterion | A. Matching official/authorized GIS | B. Georeference the EPS | C. Visual EPS + independent geo layer + bridge |
| --- | ---: | ---: | ---: |
| Implementation difficulty | 2 | 2 | 4 |
| Geographic precision | 5 if exact same edition/source | 2-4; depends on control points and cartographic generalization | 4 for calculations; visual alignment depends on calibration |
| Reference-image consistency | 3 | 2-3; forcing a sheet into GIS can distort the target composition | **5**; V preserves the reference composition |
| DEM registration | 5 when CRS/source match | 2-3; inset and generalized linework are problematic | **4** with a documented bridge and V-aligned raster |
| Browser performance | 3 | 3 | **5**; static SVG plus low-resolution Canvas |
| Maintenance | 2-3; source updates can change geometry/CRS | 2; every edition needs new control-point work | **4**; update V asset and bridge manifest independently |
| Actual necessity for this project | 3 | 2 | **5** |

### Route A: Matching GIS Data

Find an official or explicitly authorized GIS dataset that documents the same
map edition, boundary source, datum, projection, and South China Sea treatment.
Use it for calculations and possibly for a separate geospatial layer. This is
the most rigorous route when such a dataset exists, but a GIS dataset may have
different generalization, mainland framing, labels, or inset construction than
the printed EPS. It does not automatically reproduce the reference image.

Recommendation: use A as the preferred **data provenance strategy** for the
geographic layer, not as a reason to discard the official visual map.

### Route B: Georeference the EPS

Use documented control points to estimate a transform from EPS coordinates to a
geographic CRS. This is useful for audit and alignment experiments, but it is
not safe to assume that a 1:7,400,000 print map uses a single transform for the
mainland, islands, labels, and a separately framed South China Sea inset. A
high-order warp can reduce residuals while silently changing the visual
geometry; that would violate the project boundary if applied to the official
paths.

Recommendation: do not publish the EPS as GeoJSON or modify its geometry under
Route B. Use control points only to calibrate dynamic layers, and only in a
separate bridge manifest.

### Route C: Visual EPS with an Independent Geographic Layer

Keep the EPS/SVG in its own fixed visual coordinate system. Store DEM, cities,
and solar inputs in WGS84. Project them through a documented display projection
and then map the result into the EPS viewBox with a calibration transform or
mesh. The official paths are never warped.

This route matches the product's actual need: a fixed, highly art-directed
national view with geographic calculations rendered on top. It also means the
project does not need to derive GeoJSON from the EPS for the MVP.

**Recommendation: Route C, using Route A data where an authoritative GIS source
is available.** Route B is a calibration technique inside C, not a license to
turn the EPS into a geospatial source.

## 3. Recommended Coordinate Systems

### G: Geographic coordinates

- Datum: WGS84, `EPSG:4326`.
- Units: decimal degrees.
- Cities retain their source longitude/latitude and source metadata.
- Solar functions accept UTC instants plus `GeoPoint`; they never accept screen
  pixels.

### P: Canonical calculation/display projection

Use a manifest-defined Lambert Conformal Conic projection for the China-wide
main view, with parameters selected and frozen before implementation:

- central meridian: 105 degrees E;
- standard parallels: 25 degrees N and 47 degrees N;
- latitude of origin: 0 degrees N;
- datum: WGS84;
- units: metres (or a documented normalized equivalent).

This is a display/calculation projection chosen for the project's geographic
layer. It is **not** a claim about the EPS source projection. The exact PROJ
definition and parameter values must be recorded in `map-manifest.json` before
Phase 1B execution. EPSG:3857 remains a fallback for tooling compatibility,
not the preferred China-wide display projection because of its high-latitude
scale distortion.

### V: Official visual coordinates

V is the future audit SVG's `viewBox`, inherited from the EPS conversion without
geometric simplification. It may be normalized to `[0,1] x [0,1]` for browser
layout, but the original viewBox and conversion scale must remain in metadata.

The South China Sea inset has a separate visual subdomain `V_inset`. It is a
framed official composition, not a continuous geographic extension of the main
map. Unless a separately authorized geospatial inset is obtained, DEM and solar
fields are clipped to the main map and are not calculated inside `V_inset`.

## 4. Bridge Function

The runtime contract is:

```ts
type GeoPoint = {
  longitudeDeg: number;
  latitudeDeg: number;
};

type VisualPoint = {
  x: number;
  y: number;
  domain: "main" | "south-sea-inset";
};

type SpatialBridge = {
  geoToProjected(p: GeoPoint): { x: number; y: number };
  projectedToGeo(p: { x: number; y: number }): GeoPoint;
  projectedToVisual(p: { x: number; y: number }): VisualPoint;
  visualToProjected(p: { x: number; y: number }): { x: number; y: number };
  geoToVisual(p: GeoPoint): VisualPoint;
  visualToGeo(p: VisualPoint): GeoPoint | null;
};
```

`geoToVisual()` is the only path used by cities and graticule labels. The
Canvas renderer uses `visualToGeo()` for inverse sampling. All SVG, Canvas,
city, graticule, and terminator positions pass through this shared bridge; no
component may implement its own `minLon/maxLon` mapping.

### Calibration model

The bridge manifest contains a table of correspondences:

```text
controlPointId
longitudeDeg, latitudeDeg        # authoritative G coordinate
projectedX, projectedY          # P coordinate
visualX, visualY                # observed V coordinate
sourceAuthority                 # GIS/product/official control-point source
role                             # coast, boundary junction, island, etc.
residualPx                      # fitted residual at the target viewport
```

Use at least 12 well-distributed mainland/coast/island anchors for a first
calibration, with separate hold-out points for validation. Candidate models are
tested in this order:

1. similarity/affine;
2. projective transform if the print frame requires it;
3. piecewise-affine calibration mesh only for dynamic layers if a single model
   cannot meet the error budget.

Do not use a high-order transform to warp or rewrite the official SVG paths.
The bridge transforms geographic samples into V; the official map remains
unchanged.

## 5. DEM Processing and Registration

### Source and preprocessing

The DEM remains a georeferenced raster in its documented source CRS. For
processing, reproject a licensed source to P over the main China extent plus a
small documented buffer. Preserve vertical datum, no-data values, source hash,
resampling method, and licence in the asset manifest.

Do not use DEM-derived coastlines, administrative boundaries, or island
outlines to repair the EPS. DEM supplies elevation texture only.

### Rendering approach

Two equivalent implementations are allowed:

1. **Prebaked V-aligned texture:** for each output texture pixel in V, apply
   `visualToProjected()` then inverse-project to G/P and bilinearly sample the
   reprojected DEM. Store the resulting hillshade/normalized elevation texture
   with the bridge version.
2. **Low-resolution inverse sampling:** at runtime, Canvas samples a low-
   resolution P/DEM grid through `visualToProjected()` and caches the result.

The first is preferred for the fixed national view. It makes SVG and Canvas
share exactly the same V frame and keeps playback inexpensive.

### Masking

The official main-land mask is evaluated in V. Apply the mask after the DEM
texture has been mapped into V. This prevents the DEM from replacing or
correcting official coast/island geometry. The South China Sea inset is masked
and rendered separately as static official content unless an authorized
geographic inset is later supplied.

## 6. Cities and Geographic Points

City records retain WGS84 coordinates:

```ts
type Place = {
  id: string;
  name: string;
  longitudeDeg: number;
  latitudeDeg: number;
  source: string;
  coordinateEpoch?: string;
};
```

At render time:

```text
city GeoPoint (G)
  -> canonical LCC projection (P)
  -> SpatialBridge.projectedToVisual() (V)
  -> viewport transform (screen/CSS pixels)
```

The source coordinate remains the truth. A city marker may be visually nudged
for label collision only in a separate label-offset field; the marker anchor
must stay at `geoToVisual(city)`.

## 7. Solar Field and Terminator

The solar engine accepts UTC time and geographic coordinates. For every map
sample:

```text
visual pixel (V)
  -> bridge inverse (P)
  -> inverse LCC (G)
  -> solar altitude/azimuth in G
  -> colour/phase
```

The terminator is generated as a geographic isoline of a documented solar
altitude threshold (for example 0 degrees for the geometric horizon or
-0.833 degrees for theoretical sunrise), then transformed point-by-point:

```text
G isoline -> P -> V -> SVG/Canvas polyline
```

It is never drawn as an arbitrary screen-space curve. The same UTC instant and
solar model drive the field, city readings, timeline, and boundary line.

## 8. SVG/Canvas Spatial Contract

The static SVG and all dynamic Canvas layers share the same V `viewBox` and
the same viewport matrix:

```text
V -> screen: viewportMatrix
screen -> V: inverse(viewportMatrix)
```

The recommended compositing order is:

1. background and sea field;
2. V-aligned DEM texture clipped by the official main mask;
3. official SVG land/coast/boundary/island paths;
4. dynamic dawn field and geographic terminator;
5. city markers, graticule, and annotations;
6. static official South China Sea inset in `V_inset`;
7. UI panels and timeline outside the map coordinate domain.

The order may change for visual polish, but coordinate transforms must not.

## 9. Validation and Error Budget

No bridge is accepted solely because a screenshot looks plausible. Phase 1B
must produce a validation report containing:

1. control-point table and source citations;
2. fitted model, parameters, and residual statistics;
3. hold-out residuals, including western, eastern, northern, southern, coastal,
   Hainan, and Taiwan checks;
4. overlay of an independently projected authoritative coastline/boundary on
   the visual SVG;
5. DEM hillshade and official coast mask edge comparison;
6. city marker spot checks against known coast/island positions;
7. screenshots at the reference viewport and a second desktop viewport.

Initial engineering targets for the fixed reference viewport:

- median control-point residual <= 1.5 px;
- 95th-percentile residual <= 3 px;
- no systematic drift larger than 0.1% of the main map width;
- Hainan and Taiwan anchor residual <= 3 px;
- no DEM texture visible outside the official main mask.

These are visual alignment tolerances, not a claim that the generalized EPS has
survey-grade geographic accuracy. If hold-out errors exceed the budget, the
project must either refine the bridge with documented anchors or keep dynamic
layers visually subordinate; it must not warp the official geometry.

## 10. When GeoJSON Is Actually Needed

GeoJSON is not required for the MVP if the website only needs:

- fixed-view SVG paths;
- Canvas terrain and light fields;
- city points from WGS84;
- geographic solar calculations;
- a fixed official South China Sea inset.

GeoJSON becomes justified only for future features such as geographic hit
testing, arbitrary zoom/pan, spatial queries, or a formally georeferenced
official GIS layer. It must then come from an authorized geographic source or
from the EPS only after documented registration and permission. It must never be
created merely to satisfy a file-format preference.

## 11. Phase 1B Formal Implementation Sequence

This is a plan only; none of these assets are generated in Phase 1B-0.

1. Confirm the official EPS source, usage terms, South China Sea semantics, and
   whether a matching authorized GIS dataset exists.
2. Register immutable EPS metadata and its future SVG viewBox contract.
3. Select and document the geographic data CRS/datum and the China LCC display
   projection parameters.
4. Obtain or identify at least 12 authoritative visual/geographic control
   points; reserve hold-out points.
5. Fit the simplest bridge model that meets the error budget; publish its
   manifest and residual report.
6. Convert a working copy of EPS to audit SVG, preserving paths and the source
   hash; classify the main map and the separate inset conservatively.
7. Preprocess DEM into a bridge-versioned V-aligned texture; generate the
   official mask without changing geometry.
8. Implement one shared `SpatialBridge` for cities, graticule, solar samples,
   terminator, and Canvas/SVG alignment.
9. Validate overlays, edge masks, city points, and four seasonal snapshots.
10. Only after the validation report is accepted, proceed to the broader UI and
    dynamic interaction implementation.

## Final Recommendation

Adopt **Route C** as the product architecture:

```text
Official EPS (immutable visual facts)
  -> future audit SVG / V mask

Authorized GIS/DEM + WGS84 cities
  -> LCC display projection P
  -> calibrated SpatialBridge B
  -> V-aligned Canvas textures and dynamic geometry

UTC solar engine + geographic samples
  -> P -> V -> SVG/Canvas
```

This preserves the reference composition, avoids inventing a CRS for the EPS,
keeps the scientific layer genuinely geographic, and leaves a measurable path
to detect and correct DEM/map misalignment without modifying official map
geometry.

