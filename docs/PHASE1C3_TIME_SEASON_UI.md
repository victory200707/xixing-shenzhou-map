# Phase 1C-3B: Season and Sunrise Timeline UI

Date: 2026-08-26

## Implemented

- Seasonal cards now select the fixed 2026 dates: spring equinox (2026-03-20), summer solstice (2026-06-21), autumn equinox (2026-09-23), and winter solstice (2026-12-22).
- The timeline range is Beijing time from 03:00 to 10:00 (`180..600` minutes). The visual position is `((minute - 180) / 420) * 100` and is clamped to the track.
- Sunrise markers and labels are calculated from the selected cities' NREL SPA events. They use the same Beijing-date/UTC conversion as the solar field.
- The current-time overview is placed in the right rail and updated from the active time and selected city pair.
- The custom-city placeholder was removed. The Kunming shortcut was removed because no audited V coordinate exists.

## Validation

- Browser URL: `http://127.0.0.1:4173/index.html`
- 14 main markers are present: 11 ordinary cities plus Mohe, Fuyuan, and Kashi.
- Spring equinox click changed the header to `春分 / 2026.03.20`, updated sunrise to `06:16`, and updated civil dawn to `05:51`.
- Selecting Kashi after Beijing changed both timeline labels to Beijing and Kashi; the Urumqi label was removed.
- The range advanced to 10:00 and moved the current handle to 100%.
- Location compare, astronomy stage, and dawn progress modes all switched successfully.
- Browser console error log was empty during the checks.

## Known limits

The page still uses the existing audited SPA adapter and existing solar-field renderer. The south-sea inset remains an independent visual layer and is not included in the main-map solar field.
