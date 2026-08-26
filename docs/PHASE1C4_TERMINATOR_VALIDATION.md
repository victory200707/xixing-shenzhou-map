# Phase 1C-4: Terminator Validation

Date: 2026-08-26

The following preview checks use 2026-06-21, Beijing time, converted to the
corresponding UTC instant. Values are from the same deterministic solar-altitude
formula used by the dense Canvas field. Screen positions remain the audited V
coordinates passed through the displayed SVG `object-fit: contain` transform;
the calculation never uses screen pixels as solar inputs.

| BJT | 漠河 | 抚远 | 喀什 | 乌鲁木齐 | 北京 | 上海 | 广州 | 海口 | 台北 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 05:00 | 11.3 D | 16.6 D | -20.9 N | -12.4 A | 1.5 D | 1.0 D | -9.3 H | -13.3 A | -1.7 C |
| 06:00 | 19.8 D | 26.4 D | -14.0 A | -4.7 C | 11.9 D | 12.8 D | 3.0 D | -0.9 C | 10.7 D |
| 08:00 | 37.8 D | 46.1 D | 4.5 D | 14.2 D | 34.4 D | 37.8 D | 29.0 D | 25.4 D | 36.9 D |
| 12:00 | 60.4 D | 62.7 D | 49.4 D | 56.4 D | 73.2 D | 82.2 D | 83.5 D | 80.0 D | 88.1 D |
| 18:00 | 17.3 D | 8.7 D | 48.4 D | 39.3 D | 17.7 D | 11.0 D | 15.1 D | 16.8 D | 8.7 D |

Legend: `N` astronomical night (`<-18°`), `A` astronomical twilight,
`H` nautical twilight, `C` civil twilight, `D` daylight (`>= -0.833°`). The
longitude-dependent progression is visible at 05:00 and 06:00; by 08:00 the
selected sample cities are all above the sunrise threshold.

## Browser verification

- Local URL: `http://127.0.0.1:4173/index.html`
- 14 city markers remained present after the renderer replacement.
- The page reloaded with no browser console errors.
- The field changed when the timeline date/time state changed; the two
  terminator curves remained below the official presentation SVG.
- The south-sea inset remained visible as an independent layer.

## Acceptance status

Continuous light-field and geographic terminator math: **PASS for preview**.
Formal official-land clipping: **BLOCKED** pending an audited land mask.
