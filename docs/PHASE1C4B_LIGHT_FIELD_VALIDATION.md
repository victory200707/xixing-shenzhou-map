# Phase 1C-4B: Light Field Validation

Date: 2026-08-26

## Browser checks

- URL: `http://127.0.0.1:4173/index.html`
- Seasonal switch to winter and spring re-rendered the field.
- Timeline range remained `03:00–10:00` and re-rendered the field on input.
- 14 main city markers remained visible.
- Browser error log was empty after reload and seasonal interaction.
- South-sea inset remained a separate official layer.

## Sample altitude states

For 2026-06-21 BJT, the preview samples show geographic variation rather than
a fixed screen line:

| Time | West sample | Central sample | East/south sample |
|---|---|---|---|
| 05:00 | 喀什 -20.9° 深夜 | 北京 1.5° 白昼 | 台北 -1.7° 民用晨光 |
| 06:00 | 喀什 -14.0° 天文晨光 | 北京 11.9° 白昼 | 海口 -0.9° 民用晨光 |
| 08:00 | 喀什 4.5° 白昼 | 北京 34.4° 白昼 | 上海 37.8° 白昼 |

Each city's audited V coordinate is still the source for its screen position;
the renderer never computes solar state from screen pixels.

## Acceptance

- Continuous field: **PASS for visual preview**.
- Fixed rectangular/trapezoid sampling edge: **REMOVED from renderer**.
- Formal official-land clipping: **BLOCKED** because `map-mask.json` remains
  `BLOCKED_INSUFFICIENT_IDENTIFIABLE_LAND_GEOMETRY`.
- High-precision field cross-check: **PENDING**; SPA remains authoritative for
  event readouts while the dense field uses the documented low-order formula.
