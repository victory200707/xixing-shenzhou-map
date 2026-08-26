# Phase 1C-3 Frontend Baseline

## Audit

The previous page loaded `src/js/main.js` as a classic script although it
contained an ES-module import. The browser stopped at the import syntax error,
so no marker or panel event handlers ran. The control-point adapter also read
`x/y` only, while the audited JSON may provide `pickedV` plus
`longitudeDeg/latitudeDeg`.

## Repair

`main.js` is now loaded as a module and adapts `pickedV[0..1]` to visual `x/y`
and the degree fields to WGS84 longitude/latitude. Marker placement uses the
3025.3333 x 2137.3333 viewBox and the rendered `object-fit: contain` rectangle.
Eleven ordinary cities and the three mainland extreme reference points are
shown. South China Sea landmarks are kept out of the mainland city layer.

The existing panel modes, close action, shortcuts, season buttons and play
control are wired to one state object. The time slider and play control pass a
UTC `Date` to the existing solar field renderer; display text is formatted in
`Asia/Shanghai`.

## Boundary

`solar.js` remains the authoritative high-precision event module. The browser
field uses the existing NOAA-style altitude function in `solar-field.js` and
the audited LCC/affine bridge. No map geometry is changed and no third-party
algorithm is copied.
