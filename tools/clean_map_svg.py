#!/usr/bin/env python3
"""Create the presentation-only clean map derivative from the audited SVG.

The source SVG remains immutable. This pass removes converted annotations and
restyles existing stroked geometry; it never rewrites path data or transforms.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
ET.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")
ET.register_namespace("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")

RED_TEXT_FILLS = {"#ed1c24", "#ec008c"}
HALO_FILLS = {"#cbcdeb", "#b2a5d9"}
BLUE_STROKES = {"#00adef", "#66cef5"}
DARK_STROKES = {"#231f20", "#656263", "#7b7979"}
STYLE_COLOR = re.compile(r"(?:^|;)\s*(fill|stroke)\s*:\s*([^;]+)", re.I)


def parse_style(style: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for key, value in STYLE_COLOR.findall(style or ""):
        values[key.lower()] = value.strip().lower()
    return values


def has_long_straight_geometry(d: str) -> bool:
    """Detect long axis-aligned decoration paths, not curved map boundaries.

    EPS exports grid/legend rules as move/line/horizontal/vertical-only paths.
    Curved geographic geometry contains c/s/q/a commands and is retained.
    """

    if not d:
        return False
    commands = re.findall(r"[A-Za-z]", d)
    if not commands or any(command.lower() in {"c", "s", "q", "t", "a"} for command in commands):
        return False
    if not all(command.lower() in {"m", "l", "h", "v", "z"} for command in commands):
        return False
    values = [float(value) for value in re.findall(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?", d)]
    return any(abs(value) >= 9000 for value in values)


def is_legend_rule(element: ET.Element) -> bool:
    """Match the two printed scale-bar rules in the source legend block."""

    if element.get("id") in {"path3623", "path3624", "path3645", "path3646"}:
        return True
    d = element.get("d", "")
    commands = re.findall(r"[A-Za-z]", d)
    if not commands or any(command.lower() not in {"m", "l", "h", "v", "z"} for command in commands):
        return False
    values = [float(value) for value in re.findall(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?", d)]
    if len(values) < 4:
        return False
    min_x, max_x = min(values[0::2]), max(values[0::2])
    min_y, max_y = min(values[1::2]), max(values[1::2])
    return 4_500 <= min_x <= 5_500 and max_x <= 5_700 and 1_100 <= min_y <= 1_800 and max_y <= 1_900


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("assets/map/svg/official-audit.svg"))
    parser.add_argument("--output", type=Path, default=Path("assets/map/svg/clean-map.svg"))
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    if source == output:
        raise SystemExit("Refusing to overwrite official-audit.svg; choose a derived output path.")

    tree = ET.parse(source)
    root = tree.getroot()
    paths = [element for element in root.iter() if element.tag == f"{{{SVG_NS}}}path"]

    # Keep the smaller of the two large land silhouettes as a dark fill. The
    # larger duplicate is the print halo that caused the coarse white outline.
    land_candidates = [
        element
        for element in paths
        if parse_style(element.get("style", "")).get("fill") in HALO_FILLS
        and len(element.get("d", "")) > 50_000
    ]
    land_fill = min(land_candidates, key=lambda element: len(element.get("d", ""))) if land_candidates else None

    kept = 0
    removed_red = 0
    removed_halo = 0
    removed_fill_annotation = 0
    removed_grid = 0
    restyled_strokes = 0

    for element in paths:
        style = parse_style(element.get("style", ""))
        fill = style.get("fill", "none")
        stroke = style.get("stroke", "none")
        d = element.get("d", "")

        if fill in RED_TEXT_FILLS:
            parent = next((candidate for candidate in root.iter() if element in list(candidate)), None)
            if parent is not None:
                parent.remove(element)
            removed_red += 1
            continue

        if fill in HALO_FILLS:
            if element is land_fill:
                element.set(
                    "style",
                    "fill:#091b2c;fill-opacity:0.72;fill-rule:evenodd;stroke:none",
                )
                kept += 1
            else:
                parent = next((candidate for candidate in root.iter() if element in list(candidate)), None)
                if parent is not None:
                    parent.remove(element)
                removed_halo += 1
            continue

        # Scale-bar rules are stroked in the source, while converted grid
        # ornaments are often fill/stroke-less. Match both without touching
        # geographic curves or the South China Sea inset frame.
        if is_legend_rule(element) or (has_long_straight_geometry(d) and stroke == "none" and fill == "none"):
            parent = next((candidate for candidate in root.iter() if element in list(candidate)), None)
            if parent is not None:
                parent.remove(element)
            removed_grid += 1
            continue

        if stroke != "none":
            if stroke in BLUE_STROKES:
                stroke_value = "#4b7892"
                width = "0.72"
                opacity = "0.7"
            elif stroke in DARK_STROKES:
                stroke_value = "#d2b472"
                width = "1"
                opacity = "0.88"
            else:
                stroke_value = "#a9976f"
                width = "0.85"
                opacity = "0.72"
            element.set(
                "style",
                f"fill:none;stroke:{stroke_value};stroke-width:{width};"
                "stroke-linecap:round;stroke-linejoin:round;"
                f"stroke-opacity:{opacity};vector-effect:non-scaling-stroke",
            )
            restyled_strokes += 1
            kept += 1
            continue

        # Fill-only paths are converted labels, symbols, legends or print
        # ornaments. The single dark land silhouette above is the exception.
        parent = next((candidate for candidate in root.iter() if element in list(candidate)), None)
        if parent is not None:
            parent.remove(element)
        removed_fill_annotation += 1

    output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output, encoding="utf-8", xml_declaration=True)

    print(f"source={source}")
    print(f"source_sha256={sha256(source)}")
    print(f"output={output}")
    print(f"output_sha256={sha256(output)}")
    print(f"original_paths={len(paths)}")
    print(f"kept_paths={kept}")
    print(f"removed_red_or_magenta_text={removed_red}")
    print(f"removed_halo_paths={removed_halo}")
    print(f"removed_long_straight_rules={removed_grid}")
    print(f"removed_fill_annotations={removed_fill_annotation}")
    print(f"restyled_strokes={restyled_strokes}")
    print("geometry_policy=path d and transform attributes retained; viewBox unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
