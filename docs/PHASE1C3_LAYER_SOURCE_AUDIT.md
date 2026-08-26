# Phase 1C-3 Layer Source Audit

The yellow/orange visual points are not assigned new geographic meaning.
Known sources are the presentation SVG's existing linework styling, the
explicit city marker pins, and the supplied background texture. The solar
Canvas only renders low-opacity cells from calculated solar altitude. No layer
is used to infer a city or redraw a boundary.

The South China Sea SVG remains a separate image layer. Its geometry and short
line semantics are unchanged; it is not included in the mainland city layer
or solar sampling domain.
