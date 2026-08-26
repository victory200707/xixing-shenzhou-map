# Phase 1C-6C: Layout And State Refactor

## Seasonal Controls

The existing four seasonal buttons are moved at runtime into the top of the
right rail (`.season-controls-rail`). The footer no longer contains a separate
season row; it is reserved for the time axis and the three-mode switcher. The
buttons remain the same controls and continue to set the confirmed dates:
2026-03-20, 2026-06-21, 2026-09-23, and 2026-12-22.

## Preserved Modes

- Dawn progress: map, solar field, sunrise ruler, timeline, and city sunrise
  markers; no overview or detail panels.
- Location compare: two-city details and current-time overview.
- Astronomy stage: six vertical stages and a four-cell horizontal summary;
  overview remains hidden.

No mode structure or calculation formula was replaced.

## Map And Footer Geometry

The map zone bottom inset was reduced from 126px to 106px after removing the
footer season row. This gives the official SVG a larger available stage while
leaving its `0 0 3025.3333 2137.3333` viewBox and `object-fit: contain`
coordinate conversion untouched. The footer retains the play control, 03:00 to
10:00 timeline, current time, and two city sunrise markers.

## Right-Rail Presentation

The seasonal controls sit above the mode-specific rail content. The comparison
panel remains narrow and two-column; the astronomy panel retains its vertical
list plus horizontal summary. No panel is allowed to cover the map or inset.

## State Linkage And Coordinate Checks

Season clicks update the shared season/date state and call the existing render
path, which refreshes the solar field, sunrise markers, comparison values,
stage events, clock, and timeline. City markers continue to be positioned from
verified V coordinates against the rendered SVG rectangle. The South Sea inset
remains a separate official image layer and is not included in the main-map
coordinate transform.

## Verification

The local HTTP page is verified at `http://127.0.0.1:4173/index.html`.
Expected checks for the target desktop viewport: seasonal controls appear in
the right rail, the footer has no season row, all three modes preserve their
visibility rules, and the map/inset keep their aspect ratio. A narrow browser
preview confirmed 14 city markers, six astronomy stages, working mode switches,
and zero console errors. The captured layout image is
`docs/phase1c6c-browser.png` (SHA-256
`59A9AB8B7D0678B580C895474F7F10D503A15BC0BA2EDA4311219611C0731145`).
Desktop visual acceptance remains a human check.

## Protected Assets

No official geometry was edited. Current SHA-256 values:

- `official-master.eps`: `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC`
- `official-audit.svg`: `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0`
- `clean-map.svg`: `51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72`
- `presentation-map.svg`: `6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F`
- `official-south-sea.svg`: `2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D`

## Known Limitation

The connected browser backend exposes a narrow viewport during automated
checks, so desktop-scale screenshot acceptance must be repeated in a normal
1280px-or-wider browser window. No new DEM, geometry, or astronomy dependency
was introduced in this refactor.
