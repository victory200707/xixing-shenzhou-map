# Phase 1C-9D: Solar Warm/Cool Transition

Status: `TECHNICAL SOLAR FIELD PREVIEW — NOT FORMAL LAND MASK`

Date: 2026-08-26

## Scope

This sprint only strengthens the existing continuous solar light field. No
official map SVG, South Sea asset, city coordinate, panel structure, or UI
layout was changed. The field remains a preview over the displayed map
rectangle because no verified official solid-land mask is available.

## Scientific linkage

Each Canvas sample follows the existing chain:

`UTC Date -> inverse SpatialBridge -> inverse LCC -> WGS84 longitude/latitude -> NOAA-style solar altitude -> smooth color/alpha`

The existing thresholds remain authoritative for the visual states:

- below `-6 deg`: astronomical night / deep navy;
- `-6 deg` to `-0.833 deg`: continuous twilight transition;
- above `-0.833 deg`: post-sunrise daylight.

The 0-degree geometric day/night terminator and the `-0.833 deg` sunrise
reference line remain computed from the same solar altitude function. Their
line opacity was reduced so the continuous field, rather than an isolated
line, carries the visual state.

## Visual parameters

| Parameter | Value | Meaning |
| --- | ---: | --- |
| nightOpacity | 0.40 | deep navy night contrast |
| twilightOpacity | 0.24 | blue-violet to dark-gold transition start |
| warmBandOpacity | 0.30 | civil twilight / sunrise warmth |
| daylightOpacity | 0.22 | low-saturation daytime lift |
| terminatorGlow | 0.16 | restrained geometric reference lines |
| sample grid | 180-320 x 120-220 | low-resolution smooth preview |

Night colors remain blue-black rather than pure black. Twilight interpolates
from approximately `(38,56,101)` to `(132,91,58)`. Daylight uses a restrained
warm base that fades toward blue-grey as altitude rises; this keeps 08:00
regions brighter without turning the map yellow.

## Layer order

`background -> terrain canvas -> solar field canvas -> official coastline SVG -> South Sea SVG -> cities -> UI`

The Canvas layer is below the unchanged official linework, city labels,
selection markers, side rail, and timeline.

## Browser validation

HTTP entry: `http://127.0.0.1:4173/index.html`

Verified in the in-app browser at `1440 x 900`:

- Summer solstice 2026-06-21 05:00, 06:00, and 08:00;
- Spring equinox 2026-03-20 06:00;
- Winter solstice 2026-12-22 06:00;
- city states and timeline updated at each change;
- browser console error/warning count: `0` for all checked states;
- official boundaries, province lines, city labels, South Sea inset, right rail,
  and timeline remained visible.

Screenshots:

- `docs/screenshots/phase1c9d-solar-warm-cool-1440.png` (summer 05:00 final)
- `docs/screenshots/phase1c9d-solar-warm-cool-0500.png`
- `docs/screenshots/phase1c9d-solar-warm-cool-0600.png`
- `docs/screenshots/phase1c9d-solar-warm-cool-0800.png`

Screenshot SHA-256:

- 1440 / 05:00: `E7F1974FF3586B8C63CCD4DA26859D8966F33BA7974875AF5F83E1C079506256`
- 06:00: `82E48F9C8E34E2A944F61B6EA6F64D27A7C00C35B14A88CE8809706F35AB1EBF`
- 08:00: `066A90197518931D722E41C0A25597355E47FBDFF10916A1061E4FB1AA397A67`

The browser runtime rendered the requested 1440 x 900 viewport. A 1920-wide
capture was not required in this final sprint and was not substituted with a
different claimed size.

## Tests and limitations

`node --check src/astronomy/solar-field.js` passed. The repository solar test
command could not start because the local `suncalc` package is not installed;
this is recorded as a dependency gap, not as a passing numerical acceptance.

The current field is explicitly a technical rectangle preview. It is not a
formal land mask, DEM, terrain fact layer, or official map base. Approximate
visual land masking remains a separate future task and must not be inferred
from this preview.

## Protected map assets

No official EPS/SVG geometry was edited in this sprint. Recompute the project
asset hashes before release acceptance. Hashes observed after the change:

| Asset | SHA-256 |
| --- | --- |
| `official-master.eps` | `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC` |
| `official-audit.svg` | `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0` |
| `clean-map.svg` | `51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72` |
| `presentation-map.svg` | `6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F` |
| `presentation-coastline.svg` | `AFDADE73B26560432D66015434C1B2F9A417D2562C0415554669CEA562D18A89` |
| `official-south-sea.svg` | `2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D` |
| `south-sea-presentation.svg` | `D5086F7C6A6C8EA5424F95558F1794712CD33565C0C8C41D9697B2B2ECA493A6` |
