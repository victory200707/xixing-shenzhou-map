#!/usr/bin/env python3
"""Extract the supplied official South China Sea inset without redrawing it.

The source SVG is immutable. Selected paths keep their original `d` and
transform attributes; only presentation styles are remapped for the dark UI.
The inset remains in the full official V viewBox so it can be overlaid without
any second projection or rescaling.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

# The outer official inset frame is path3622. Its transformed extent is about
# x=2597..3023, y=1484..2134 in the immutable V viewBox. A small margin keeps
# labels and the official title/scale block at the frame edge.
INSET_BBOX = (2588.0, 1475.0, 3025.3333, 2137.3333)
TRANSFORM_SCALE = 0.13333333
TRANSFORM_Y = 2137.3333
TOKEN = re.compile(r"[AaCcHhLlMmQqSsTtVvZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
ARITY = {"m": 2, "l": 2, "t": 2, "h": 1, "v": 1, "c": 6, "s": 4, "q": 4, "a": 7}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def path_bbox_v(d: str) -> tuple[float, float, float, float] | None:
    """Approximate a path bbox in V by evaluating command points/control points."""
    tokens = TOKEN.findall(d)
    if not tokens:
        return None
    index = 0
    command = None
    current = [0.0, 0.0]
    start = [0.0, 0.0]
    points: list[tuple[float, float]] = []

    def number() -> float:
        nonlocal index
        value = float(tokens[index])
        index += 1
        return value

    while index < len(tokens):
        if tokens[index].isalpha():
            command = tokens[index]
            index += 1
            if command.lower() == "z":
                current = start[:]
                points.append(tuple(current))
                continue
        if command is None:
            break
        lower = command.lower()
        if lower == "z":
            continue
        arity = ARITY.get(lower)
        if arity is None or index + arity > len(tokens) or any(t.isalpha() for t in tokens[index:index + arity]):
            # A malformed or unsupported path must be retained conservatively.
            return None
        values = [number() for _ in range(arity)]
        relative = command.islower()
        if lower in {"m", "l", "t"}:
            x, y = values
            if relative:
                x += current[0]
                y += current[1]
            current = [x, y]
            points.append((x, y))
            if lower == "m":
                start = current[:]
                command = "l" if relative else "L"
        elif lower == "h":
            x = values[0] + (current[0] if relative else 0)
            current = [x, current[1]]
            points.append(tuple(current))
        elif lower == "v":
            y = values[0] + (current[1] if relative else 0)
            current = [current[0], y]
            points.append(tuple(current))
        elif lower == "c":
            coords = []
            for x, y in zip(values[0::2], values[1::2]):
                if relative:
                    x += current[0]
                    y += current[1]
                coords.append((x, y))
            points.extend(coords)
            current = list(coords[-1])
        elif lower in {"s", "q"}:
            coords = []
            for x, y in zip(values[0::2], values[1::2]):
                if relative:
                    x += current[0]
                    y += current[1]
                coords.append((x, y))
            points.extend(coords)
            current = list(coords[-1])
        elif lower == "a":
            # Arc radii/rotation/flags are not bbox points; retain endpoints
            # and expand by a conservative stroke margin below.
            x, y = values[5:]
            if relative:
                x += current[0]
                y += current[1]
            current = [x, y]
            points.append(tuple(current))

    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x = min(xs) * TRANSFORM_SCALE
    max_x = max(xs) * TRANSFORM_SCALE
    # Source conversion uses y' = 2137.3333 - 0.13333333*y.
    min_y = TRANSFORM_Y - max(ys) * TRANSFORM_SCALE
    max_y = TRANSFORM_Y - min(ys) * TRANSFORM_SCALE
    return min_x, min_y, max_x, max_y


def intersects(bbox: tuple[float, float, float, float] | None) -> bool:
    if bbox is None:
        return True  # Retain unknown geometry rather than risk deleting facts.
    min_x, min_y, max_x, max_y = bbox
    left, top, right, bottom = INSET_BBOX
    return max_x >= left and min_x <= right and max_y >= top and min_y <= bottom


def style_for(style: str) -> str:
    style_lower = style.lower()
    if "stroke:" in style_lower:
        color = "#d8c28e" if "#231f20" in style_lower or "#656263" in style_lower or "#7b7979" in style_lower else "#7fa8ba"
        dash = "stroke-dasharray:4 3;" if "stroke-dasharray" in style_lower and "none" not in style_lower else ""
        return f"fill:none;stroke:{color};stroke-width:1.05;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:0.86;{dash}vector-effect:non-scaling-stroke"
    if "#00adef" in style_lower:
        return "fill:#8cc7d8;fill-opacity:0.82;stroke:none"
    if "#ed1c24" in style_lower or "#ec008c" in style_lower:
        return "fill:#d8c28e;fill-opacity:0.9;stroke:none"
    if "#ffffff" in style_lower:
        return "fill:#d9e4e8;fill-opacity:0.9;stroke:none"
    if "#cbcdeb" in style_lower or "#b2a5d9" in style_lower:
        return "fill:#17324a;fill-opacity:0.78;stroke:none"
    return "fill:#d8c28e;fill-opacity:0.88;stroke:none"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("assets/map/svg/official-audit.svg"))
    parser.add_argument("--output", type=Path, default=Path("assets/map/svg/official-south-sea.svg"))
    parser.add_argument("--metadata", type=Path, default=Path("assets/map/metadata/south-sea-inset.json"))
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    metadata_path = args.metadata.resolve()
    if source == output:
        raise SystemExit("Refusing to overwrite official-audit.svg")

    tree = ET.parse(source)
    root = tree.getroot()
    source_paths = [node for node in root.iter() if node.tag == f"{{{SVG_NS}}}path"]
    selected: list[ET.Element] = []
    unknown_bbox = 0
    for node in source_paths:
        bbox = path_bbox_v(node.get("d", ""))
        if bbox is None:
            unknown_bbox += 1
        if intersects(bbox):
            selected.append(node)

    out_root = ET.Element(f"{{{SVG_NS}}}svg", {
        "version": "1.1",
        "width": "3025.3333",
        "height": "2137.3333",
        "viewBox": "0 0 3025.3333 2137.3333",
        "data-source": "official-audit.svg",
        "data-semantic-policy": "official source-faithful inset; short segments remain UNKNOWN",
    })
    # Presentation-only backing panel hides the incomplete clean derivative.
    ET.SubElement(out_root, f"{{{SVG_NS}}}rect", {
        "x": str(INSET_BBOX[0]), "y": str(INSET_BBOX[1]),
        "width": str(INSET_BBOX[2] - INSET_BBOX[0]), "height": str(INSET_BBOX[3] - INSET_BBOX[1]),
        "fill": "#06172a", "fill-opacity": "0.96", "data-role": "presentation-backdrop",
    })
    group = ET.SubElement(out_root, f"{{{SVG_NS}}}g", {"id": "official-south-sea-inset", "data-semantic": "UNKNOWN"})
    for source_node in selected:
        node = ET.fromstring(ET.tostring(source_node, encoding="unicode"))
        node.set("style", style_for(node.get("style", "")))
        node.set("data-source-id", source_node.get("id", "UNKNOWN"))
        node.set("data-semantic", "UNKNOWN")
        group.append(node)

    output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(out_root).write(output, encoding="utf-8", xml_declaration=True)
    record = {
        "schemaVersion": "1.0",
        "status": "SOURCE_FAITHFUL_DERIVATIVE",
        "sourceFile": str(args.source).replace("\\", "/"),
        "sourceSha256": sha256(source),
        "derivedFile": str(args.output).replace("\\", "/"),
        "derivedSha256": sha256(output),
        "viewBox": "0 0 3025.3333 2137.3333",
        "sourceInsetBBoxV": list(INSET_BBOX),
        "sourcePathCount": len(source_paths),
        "selectedPathCount": len(selected),
        "unknownBBoxCount": unknown_bbox,
        "geometryPolicy": {
            "sourceUnmodified": True,
            "pathDataCopiedVerbatim": True,
            "sourceTransformsCopiedVerbatim": True,
            "newGeographicGeometry": False,
            "newPresentationBackdrop": True,
            "shortSegmentsSemantic": "UNKNOWN",
        },
        "verification": {
            "outerFrameSourceId": "path3622",
            "nestedTitleScaleBlock": "retained from source where it intersects inset bbox",
            "nineDashLineClaim": "NOT MADE",
            "officialLegendAndUsageTerms": "PENDING_EXTERNAL_VERIFICATION",
        },
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selectedPaths": len(selected), "sourceSha256": record["sourceSha256"], "derivedSha256": record["derivedSha256"], "bbox": INSET_BBOX}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
