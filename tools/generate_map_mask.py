#!/usr/bin/env python3
"""Derive a raster clip mask from the existing clean-map SVG land fill.

This tool is deliberately conservative. It accepts only a clean SVG with one
visible filled path and M/C geometry, then samples that already-existing path
into a PNG alpha mask. It does not write any SVG and does not invent geometry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw

SVG_NS = "http://www.w3.org/2000/svg"
NUMBER = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
COMMAND = re.compile(r"[A-Za-z]")
TOOL_VERSION = "1.0.1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def style_value(element: ET.Element, key: str, default: str = "") -> str:
    if element.get(key):
        return element.get(key, default).strip().lower()
    for item in element.get("style", "").split(";"):
        if ":" not in item:
            continue
        name, value = item.split(":", 1)
        if name.strip().lower() == key:
            return value.strip().lower()
    return default


def parse_viewbox(value: str | None) -> tuple[float, float, float, float]:
    if not value:
        raise ValueError("SVG has no viewBox")
    numbers = [float(item) for item in NUMBER.findall(value)]
    if len(numbers) != 4 or numbers[2] <= 0 or numbers[3] <= 0:
        raise ValueError(f"invalid SVG viewBox: {value!r}")
    return tuple(numbers)  # type: ignore[return-value]


def parse_matrix(value: str | None) -> tuple[float, float, float, float, float, float]:
    if not value:
        return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    if not value.strip().startswith("matrix("):
        raise ValueError(f"unsupported path transform: {value!r}")
    numbers = [float(item) for item in NUMBER.findall(value)]
    if len(numbers) != 6:
        raise ValueError(f"invalid matrix transform: {value!r}")
    return tuple(numbers)  # type: ignore[return-value]


def transform(point: tuple[float, float], matrix: tuple[float, float, float, float, float, float]) -> tuple[float, float]:
    x, y = point
    a, b, c, d, e, f = matrix
    return (a * x + c * y + e, b * x + d * y + f)


def point_line_distance(point: tuple[float, float], start: tuple[float, float], end: tuple[float, float]) -> float:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return math.hypot(point[0] - start[0], point[1] - start[1])
    return abs(dx * (start[1] - point[1]) - (start[0] - point[0]) * dy) / length


def split_cubic(points: tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]) -> tuple[tuple[tuple[float, float], ...], tuple[tuple[float, float], ...]]:
    p0, p1, p2, p3 = points
    p01 = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    p12 = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    p23 = ((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2)
    p012 = ((p01[0] + p12[0]) / 2, (p01[1] + p12[1]) / 2)
    p123 = ((p12[0] + p23[0]) / 2, (p12[1] + p23[1]) / 2)
    mid = ((p012[0] + p123[0]) / 2, (p012[1] + p123[1]) / 2)
    return ((p0, p01, p012, mid), (mid, p123, p23, p3))


def flatten_cubic(points: tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]], output: list[tuple[float, float]], tolerance: float = 0.20, depth: int = 0) -> None:
    p0, p1, p2, p3 = points
    if depth >= 16 or max(point_line_distance(p1, p0, p3), point_line_distance(p2, p0, p3)) <= tolerance:
        output.append(p3)
        return
    left, right = split_cubic(points)
    flatten_cubic(left, output, tolerance, depth + 1)
    flatten_cubic(right, output, tolerance, depth + 1)


def parse_cubic_path(path_data: str, matrix: tuple[float, float, float, float, float, float]) -> list[tuple[float, float]]:
    commands = {item.lower() for item in COMMAND.findall(path_data)}
    if commands != {"m", "c"}:
        raise ValueError(f"path commands are not limited to M/C: {sorted(commands)}")
    tokens = re.findall(r"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?", path_data)
    if not tokens or tokens[0].lower() != "m":
        raise ValueError("path does not begin with moveto")
    index = 1
    if index + 2 > len(tokens):
        raise ValueError("moveto is incomplete")
    current = transform((float(tokens[index]), float(tokens[index + 1])), matrix)
    output = [current]
    index += 2
    if index >= len(tokens) or tokens[index].lower() != "c":
        raise ValueError("moveto is not followed by cubic geometry")
    index += 1
    while index < len(tokens):
        if tokens[index].isalpha():
            if tokens[index].lower() != "c":
                raise ValueError(f"unexpected command {tokens[index]!r}")
            index += 1
            continue
        if index + 6 > len(tokens):
            raise ValueError("incomplete cubic coordinate sequence")
        relative = [float(tokens[index + offset]) for offset in range(6)]
        controls = (
            (current[0] + relative[0] * matrix[0] + relative[1] * matrix[2], current[1] + relative[0] * matrix[1] + relative[1] * matrix[3]),
            (current[0] + relative[2] * matrix[0] + relative[3] * matrix[2], current[1] + relative[2] * matrix[1] + relative[3] * matrix[3]),
            (current[0] + relative[4] * matrix[0] + relative[5] * matrix[2], current[1] + relative[4] * matrix[1] + relative[5] * matrix[3]),
        )
        flatten_cubic((current, controls[0], controls[1], controls[2]), output)
        current = controls[2]
        index += 6
    return output


def visible_land_candidates(root: ET.Element) -> tuple[list[ET.Element], int, int]:
    paths = [element for element in root.iter() if element.tag == f"{{{SVG_NS}}}path"]
    candidates: list[ET.Element] = []
    for path in paths:
        if path.get("display") == "none" or path.get("visibility") == "hidden":
            continue
        fill = style_value(path, "fill", "none")
        stroke = style_value(path, "stroke", "none")
        if fill not in {"", "none", "transparent"}:
            candidates.append(path)
    # No remaining path carries a semantic layer/object identifier. The styles
    # show paint behavior only, not whether a path is land, coast or a label.
    return candidates, len(paths), len(paths)


def inspect(source: Path) -> dict[str, object]:
    root = ET.parse(source).getroot()
    viewbox = parse_viewbox(root.get("viewBox"))
    candidates, path_count, unknown_count = visible_land_candidates(root)
    report: dict[str, object] = {
        "source": str(source).replace("\\", "/"),
        "sourceSha256": sha256(source),
        "viewBox": list(viewbox),
        "rootWidth": root.get("width"),
        "rootHeight": root.get("height"),
        "pathCount": path_count,
        "unknownObjectCount": unknown_count,
        "filledCandidateCount": len(candidates),
        "filledCandidates": [],
    }
    details = []
    for candidate in candidates:
        points = parse_cubic_path(candidate.get("d", ""), parse_matrix(candidate.get("transform")))
        bbox = {
            "minX": min(point[0] for point in points),
            "minY": min(point[1] for point in points),
            "maxX": max(point[0] for point in points),
            "maxY": max(point[1] for point in points),
        }
        details.append({"id": candidate.get("id"), "style": candidate.get("style"), "transform": candidate.get("transform"), "pointCount": len(points), "bboxV": bbox})
    report["filledCandidates"] = details
    return report


def build_mask(source: Path, output: Path, metadata: Path) -> dict[str, object]:
    report = inspect(source)
    candidates = report["filledCandidates"]
    if report["filledCandidateCount"] != 1:
        raise ValueError("refusing to choose a land path: expected exactly one visible filled candidate")
    root = ET.parse(source).getroot()
    candidate_id = candidates[0]["id"]
    path = next(element for element in root.iter(f"{{{SVG_NS}}}path") if element.get("id") == candidate_id)
    viewbox = tuple(report["viewBox"])
    _, _, view_width, view_height = viewbox
    width = round(view_width)
    height = round(view_height)
    points = parse_cubic_path(path.get("d", ""), parse_matrix(path.get("transform")))
    # This is only the unavoidable V-space-to-integer-pixel sampling step.
    pixel_points = [((x - viewbox[0]) * width / view_width, (y - viewbox[1]) * height / view_height) for x, y in points]
    image = Image.new("L", (width, height), 0)
    ImageDraw.Draw(image).polygon(pixel_points, fill=255)
    covered_pixels = image.histogram()[255]
    coverage_ratio = covered_pixels / (width * height)
    # A thin print halo can also be represented as a filled path. It is not a
    # land silhouette and must never become a terrain clip mask. This threshold
    # is a conservative structural guard, not a geographic classification.
    if coverage_ratio < 0.10:
        raise ValueError(
            "refusing to generate a land mask: the sole filled path covers "
            f"only {coverage_ratio:.4%} of the V-space raster and is not a solid land silhouette"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=False)
    output_hash = sha256(output)
    manifest = {
        "schemaVersion": "1.0",
        "status": "DERIVED_PENDING_VISUAL_ACCEPTANCE",
        "purpose": "Texture clipping only; not a geographic fact source.",
        "source": {"path": str(source).replace("\\", "/"), "sha256": report["sourceSha256"], "immutableAuditSource": "assets/map/svg/official-audit.svg"},
        "output": {"path": str(output).replace("\\", "/"), "sha256": output_hash, "format": "PNG grayscale alpha-equivalent", "width": width, "height": height, "coverageRatio": coverage_ratio},
        "coordinateSpace": {"svgViewBox": report["viewBox"], "rasterSampling": {"scaleX": width / view_width, "scaleY": height / view_height, "translation": [0, 0], "crop": False, "mirror": False}},
        "extraction": {"tool": "tools/generate_map_mask.py", "toolVersion": TOOL_VERSION, "date": date.today().isoformat(), "method": "single existing visible filled path sampled from original M/C commands", "selectedObject": candidates[0], "pathDataRewritten": False, "svgRewritten": False, "geometrySimplified": False},
        "mainMap": {"status": "CANDIDATE_MASK_GENERATED_FROM_SINGLE_FILL", "bboxV": candidates[0]["bboxV"]},
        "southSeaInset": {"status": "LOGICALLY_SEPARATE_NOT_INCLUDED", "reason": "The clean SVG exposes no independently identifiable inset fill path; inset geometry remains stroke-only and UNKNOWN for mask extraction."},
        "unknownObjects": {"count": report["unknownObjectCount"], "policy": "No unknown SVG object is included in the mask."},
        "limitations": ["A single fill path has no internal semantic identifier in the clean SVG.", "Hainan, Taiwan and the South China Sea inset require rendered comparison before acceptance; no semantic inference is made by this tool.", "No crop, re-projection, CRS assignment or geographic analysis is performed."],
    }
    metadata.parent.mkdir(parents=True, exist_ok=True)
    metadata.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("assets/map/svg/clean-map.svg"))
    parser.add_argument("--output", type=Path, default=Path("assets/map/raster/official-land-mask.png"))
    parser.add_argument("--metadata", type=Path, default=Path("assets/map/metadata/map-mask.json"))
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    report = inspect(args.source)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.audit_only:
        return 0
    manifest = build_mask(args.source, args.output, args.metadata)
    print(json.dumps({"output": manifest["output"], "metadata": str(args.metadata).replace("\\", "/")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
