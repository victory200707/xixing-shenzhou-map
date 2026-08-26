# Phase 1C-6D: Desktop Acceptance And Selection Status

## Actual Rendered Layout

The browser was checked at all requested desktop sizes. Controls are positioned
from the rendered DOM, not inferred from source order:

| Viewport | Map zone (w x h) | Right rail x / width | Footer contents | Overflow |
| --- | ---: | ---: | --- | --- |
| 1280 x 800 | 930 x 616 | 950 / 292 | timeline only | none |
| 1440 x 900 | 1090 x 716 | 1110 / 292 | timeline only | none |
| 1920 x 1080 | 1570 x 896 | 1590 / 292 | timeline only | none |

The right rail order is:

```text
season-cards
mode-switcher
selectionHint
sunrise-ruler / analysis-panel / overview
```

The map image remains `object-fit: contain`; its rendered rectangle is used by
the existing V-coordinate marker conversion. The official South Sea inset is a
separate layer.

## Selection Status Migration

`#selectionHint` is moved from the map zone to the right rail below mode
buttons. It uses a small muted blue-grey line with a low-opacity divider and no
large card or glow.

Messages are state-driven:

- No user selection: `选择一座城市，开始比较`
- One selection: `${city}已选中，再选择一座城市进行对比`
- Two selections: `${cityA}与${cityB}对比中`
- Astronomy stage: `当前分析城市：${city}` or `当前阶段参考：${cityA} / ${cityB}`

The default Beijing/Urumqi readouts no longer consume a user selection slot.
The first click therefore produces the one-city state, and the second click
opens location comparison in the actual selection order.

## Desktop Screenshots

- `docs/screenshots/phase1c6d-desktop-1280.png` 110,678 bytes,
  SHA-256 `8468BFA8047C9D3C5ABA940D306A7E3F11C076507B7187859C92495A17890938`
- `docs/screenshots/phase1c6d-desktop-1440.png` 130,142 bytes,
  SHA-256 `3D022C7AD9E27408584FA84FAC467B60BC8EA498881CD49F8F2454D094F085AD`
- `docs/screenshots/phase1c6d-desktop-1920.png` 158,583 bytes,
  SHA-256 `25AE9095DFC6263C3871B4D9FED8E81D42C010B82D07F6180771C71663A60AC7`

The 1440px capture visibly includes the map, right rail, migrated status line,
season buttons, mode buttons, South Sea inset, and timeline. The browser
automation backend captures the 1920px viewport with a narrower physical image
surface, but the DOM viewport and layout rectangles remain 1920 x 1080 and
were checked without overflow.

## Interaction Checks

- 14 city markers load; Beijing, Urumqi, Mohe, Fuyuan, Kashgar, Harbin, Lhasa,
  Shanghai, Guangzhou, Haikou, and Taipei have visible rendered positions.
- First city click, second city click, automatic comparison mode, and astronomy
  reference text were verified.
- Timeline and city sunrise markers remain in the footer; no season row is
  present there.
- Browser console reported no errors or warnings during the checks.

## Protected Asset Hashes

- `official-master.eps`: `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC`
- `official-audit.svg`: `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0`
- `clean-map.svg`: `51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72`
- `presentation-map.svg`: `6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F`
- `official-south-sea.svg`: `2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D`

## Known Issue

The automated screenshot surface does not expose the full physical width at
1920px, so final visual review of that capture should be repeated in a normal
1920px browser window. No map geometry, projection, DEM, or solar formula was
changed in this phase.
