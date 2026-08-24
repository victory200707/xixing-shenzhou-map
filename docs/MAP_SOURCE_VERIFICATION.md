# Phase 1A.6: Official Master Map Source Verification

## Decision

**Do not freeze `MASTER_MAP` yet.** The candidate is the strongest technical and
reference-fit candidate, but the evidence required to make it a traceable,
web-publishable official geographic master is incomplete.

This is not a rejection of the file's visual or geometric quality. It is a
strict provenance and publication-rights gate. No SVG, GeoJSON, Mask, or other
derived map asset has been generated.

## Candidate Registry

| Field | Recorded value | Evidence status |
| --- | --- | --- |
| Candidate file | `中国地图 1∶740万 (界线版 无邻国 无河流 线划(一).eps` | Local file and EPS title header |
| Archive | `C:\Users\HUAWEI\Downloads\4o28b0625501ad13015501ad2bfc2187b.zip` | Local user-provided archive |
| ZIP SHA-256 | `1C8F7F8B0402D5D3A32A917E16F6347A4220A05D2F56F55D4E473783D3770F40` | Locally computed |
| EPS SHA-256 | `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC` | Locally computed |
| EPS creator/date | CorelDRAW X8; 2023-08-08 14:30:03 | EPS header only; not publication evidence |
| File modification timestamp | 2023-08-15 11:32:58 | Local ZIP entry metadata only; not publication evidence |
| Claimed scale | 1:7,400,000 | File title; requires official catalog confirmation |
| Review number visible on rendered sheet | `GS(2023)2767号` | Visual verification of the rendered sheet; requires official record confirmation |
| Formal publisher | Not confirmed for this exact file | Blocking |
| Official product/download record | Not confirmed for this exact file | Blocking |
| Publication/derivative-use terms | Not confirmed | Blocking |

The ZIP and EPS are immutable source candidates. Any future derivation must
reference the EPS hash above and record its toolchain, options, output hash,
and legal basis.

## Official Source Verification

### Evidence obtained

1. The intended official service endpoint is the Ministry of Natural Resources
   domain `https://bzdt.ch.mnr.gov.cn/` (Standard Map Service System). This is
   a plausible authoritative system for the requested product, but a domain
   name alone does **not** link this particular SHA-256 to a published catalog
   record.
2. On 2026-08-23, the endpoint could not be read in the available browser due
   to `ERR_CERT_AUTHORITY_INVALID`. The security interstitial was not bypassed.
3. A search-result snippet states that standard maps are compiled according to
   Chinese/world boundary drawing standards, may be browsed/downloaded by the
   public, and that direct use should show the review number. Search snippets
   are discovery leads only; they are not retained as legal or product-record
   evidence.

### Required but unverified fields

The following must be copied from an accessible official product detail page,
official download response, or written authorization for the exact file:

| Requirement | Status | Why it matters |
| --- | --- | --- |
| Issuing/publishing body | Unverified | Confirms that the file, not merely the service domain, is official |
| Exact catalog title and scale | Unverified | Binds the local EPS to the official product record |
| Issue/update date and version | Unverified | Prevents use of a superseded edition |
| `GS(2023)2767号` record | Unverified | The visual number must match the official record |
| Official map description/legend | Unverified | Required to identify South China Sea inset elements accurately |
| Direct-use terms | Unverified | A website is a public publication context |
| Derivative-format/distribution permission | Unverified | Download permission does not itself authorize publishing SVG, GeoJSON, or Mask derivatives |

### Consequence for use

The EPS can remain in the repository's **candidate registry** and be used for
offline inspection. It cannot yet be declared the legal/geographic basis of a
public web map. No conclusion is made that public use, SVG conversion, GeoJSON
conversion, Mask generation, or redistribution is allowed until the official
terms expressly cover the intended use or written authorization is obtained.

## South China Sea Inset Verification

### What the file proves

Successful rendering and object-structure inspection establish that the sheet
contains a lower-right framed inset headed `南海诸岛`, with island groups,
labels, scale information, and repeated short line-segment objects. It is
integrated in this single printed sheet rather than added by the project.

### What remains unproven

The EPS has no semantic object/layer names that identify those short segments.
Accordingly:

- The inset is a verified component of the supplied EPS, but its inclusion in
  an official published product remains pending the exact official record.
- The short segments are **not** called `九段线` in this project record.
- Their formal cartographic/legal meaning, any line-style rules, and the
  complete set of required South China Sea features need an official legend,
  product description, or metadata record.
- The inset must not be independently extracted, relabeled, redrawn, or
  repositioned as a purported geographic layer before that meaning and the
  reuse terms are verified.

### Conditional future handling

If the official record confirms the inset and its terms permit derivation,
preserve it as a self-contained `official-south-sea` visual domain with its
own source bounding box and source hash. Do not transform it into the main-map
coordinate system and do not infer missing segments or islands.

## Coordinate and Projection Verification

The EPS provides PostScript/print coordinates only:

- EPS header bounding box: `538 439 2807 2042`.
- Embedded page bounding box: `0 0 841 595`.
- No EPSG identifier, WKT/PROJ definition, longitude/latitude coordinate list,
  or verifiable geographic control-point metadata was found in the file.

Therefore it is an illustration/print coordinate system, not a confirmed GIS
dataset. It may be used later as a fixed-view visual geometry source after the
rights gate passes, but it cannot directly support distance/area analysis,
spatial joins, solar-field sampling, DEM reprojection, or authoritative city
placement in longitude/latitude.

If geographic registration is subsequently required, use official control
points or a separately authorized authoritative GIS source with documented
CRS. Record the transform and residual error in a manifest. Do not guess a
projection from the apparent national outline, and do not freely warp the
official paths to make a DEM fit.

## Conditional Derivative Asset Assessment

| Intended asset | Current status | Preconditions for Phase 1B |
| --- | --- | --- |
| `official-mainland` | Technically extractable, not authorized | Official product and derivative-use confirmation; conservative object classification |
| `official-boundaries` | Technically classifiable, not semantically named | Same; preserve original paths and record selection rules |
| `official-coastline` | Technically classifiable, not semantically named | Same; manual review of coastal/island objects |
| `official-islands` | Requires manual review | Same; do not merge, redraw, or discard small features automatically |
| `official-south-sea` | Visually delimited inset; semantics pending | Official inset/line-symbol explanation and derivative-use confirmation |
| `china-mask` | Can only be generated after boundary classification | Must derive from confirmed official land geometry with no repairs or inferred closure |
| `GeoJSON` | Not currently valid | Requires authoritative CRS/control points and explicit publication permission |
| `metadata` | May be drafted now, not finalized | Must include official URL, access date, version, review number, terms, hashes, and derivation history |

Regardless of Phase 1B outcomes, the original EPS must remain unmodified and
must be the traceability anchor. Programmatic conversion may change file
syntax, but it must not simplify, repair, reconnect, add, delete, or otherwise
change the official geographic geometry.

## Relationship to the Final Reference

The final reference controls the web composition and rendering: a dark map,
terrain, hillshade, dawn field, terminator, cloud/background effects,
graticule, and UI may all be recreated outside the official EPS. The EPS is
not a visual style constraint. Its protected scope is the geographic facts and
the verified official South China Sea inset content. The visual system must
never invent or alter those facts.

## Freeze Gate

The freeze condition is deliberately narrow. The candidate may be frozen as:

```text
MASTER_MAP = 中国地图 1∶740万 (界线版 无邻国 无河流 线划(一).eps
```

only after these three evidence items are attached to this report:

1. An accessible official product/download record tying the exact title, scale,
   version, and `GS(2023)2767号` to the formal issuer.
2. Official written usage terms or authorization covering the proposed public
   web use and the intended non-geometry-changing derivatives (SVG, Mask, and,
   only if georeferencing is separately established, GeoJSON).
3. Official legend, product notes, or metadata defining the `南海诸岛` inset
   and its short-segment objects.

These are substantive blockers named in the Phase 1A.6 request: source,
permission, and critical South China Sea semantics. They are not minor
technical imperfections.

## Phase 1B, After a Valid Freeze

No Phase 1B work starts now. Once the above evidence is recorded and the user
confirms the freeze, the next phase is limited to a reproducible derivation
plan and then execution:

1. Register the immutable EPS, official URL, publisher, version, review
   number, terms, source hash, and any CRS/control-point evidence.
2. Convert a copy to an audit SVG/PDF without geometry simplification; compare
   rendering against the source.
3. Classify and manually review mainland, boundaries, coastline, islands, and
   the self-contained South China Sea inset.
4. Produce source-linked SVG and Mask assets. Produce GeoJSON only if a
   documented authoritative geographic registration is available.
5. Create per-asset metadata with source hash, selection rules, conversion
   tool/version/options, output hash, and validation screenshot.

