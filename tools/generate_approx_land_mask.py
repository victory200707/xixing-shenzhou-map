"""Generate an approximate visual land mask from the supplied terrain JPG.

This output is a rendering aid only. It is never a source for borders,
coordinates, cities, or other geographic facts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from xml.etree import ElementTree as ET


VIEWBOX = (3025.3333, 2137.3333)
DEFAULT_SOURCE = Path("assets/map/source/terrain-reference-gs2016-1609.jpg")
DEFAULT_REGISTRATION = Path("assets/map/metadata/terrain-registration.json")
DEFAULT_OUTPUT = Path("assets/map/raster/approx-land-mask.png")
DEFAULT_METADATA = Path("assets/map/metadata/approx-land-mask.json")
DEFAULT_SOURCE_SVG = Path("assets/map/svg/approx-land-mask-source.svg")
DEFAULT_RENDER = Path("tools/presentation-map-render.png")
OFFICIAL_BODY_SOURCE = Path("assets/map/svg/presentation-map.svg")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_official_path_source(path: Path, output: Path) -> None:
    """Create an independent visual-only fill copy of the audited body path.

    path3 contains nested subpaths, so its even-odd fill rule must be retained.
    """
    root = ET.parse(path).getroot()
    ns = "{http://www.w3.org/2000/svg}"
    source_path = root.find(f".//{ns}path[@id='path3']")
    if source_path is None or not source_path.get("d"):
        raise ValueError("Official coastline path3 was not found")
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="3025.3333" height="2137.3333" '
        'viewBox="0 0 3025.3333 2137.3333">'
        '<path id="path3" d="' + source_path.get("d") + '" '
        'transform="' + source_path.get("transform", "") + '" '
        'fill="#ffffff" fill-opacity="1" stroke="none" stroke-width="0" '
        'fill-rule="evenodd"/></svg>\n'
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")


def affine_inverse(matrix: list[list[float]]) -> tuple[float, ...]:
    a, b, tx = matrix[0]
    c, d, ty = matrix[1]
    det = a * d - b * c
    if abs(det) < 1e-12:
        raise ValueError("Registration matrix is singular")
    ia, ib = d / det, -b / det
    ic, id_ = -c / det, a / det
    return (
        ia,
        ib,
        -ia * tx - ib * ty,
        ic,
        id_,
        -ic * tx - id_ * ty,
    )


def mask_from_rendered_outline(rendered: Image.Image) -> Image.Image:
    """Fill the interior of the rasterized path3 outline, with feathering."""
    gray = rendered.convert("L")
    line = np.asarray(gray) > 185
    # Close small raster gaps in the displayed outline before flood filling.
    line_img = Image.fromarray((line.astype(np.uint8) * 255), mode="L")
    # The source display path has a few open raster joins. A broad closing
    # operation bridges only those joins before flood fill; the result remains
    # a soft visual clip, not a new boundary asset.
    line_img = line_img.filter(ImageFilter.MaxFilter(51)).filter(ImageFilter.MinFilter(25))
    line = np.asarray(line_img) > 120
    height, width = line.shape
    # Scanline even/odd fill is tolerant of the source path's open joins and
    # avoids a flood-fill leak through a single coastline gap.
    inside = np.zeros_like(line, dtype=bool)
    previous_hits: list[int] = []
    for y in range(height):
        xs = np.flatnonzero(line[y])
        groups: list[tuple[int, int]] = []
        if xs.size:
            start = int(xs[0])
            last = start
            for x in xs[1:]:
                x = int(x)
                if x > last + 1:
                    groups.append((start, last))
                    start = x
                last = x
            groups.append((start, last))
        hits = [int((a + b) / 2) for a, b in groups]
        if len(hits) < 2 and previous_hits:
            hits = previous_hits
        if len(hits) >= 2:
            for left, right in zip(hits[0::2], hits[1::2]):
                if right > left:
                    inside[y, left:right + 1] = True
            previous_hits = hits
    inside = Image.fromarray((inside.astype(np.uint8) * 230), mode="L")
    inside = inside.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(5))
    return inside.filter(ImageFilter.GaussianBlur(1.25))


def mask_from_rendered_body(rendered: Image.Image) -> Image.Image:
    """Extract the dark blue body-fill pixels from the official display render."""
    rgb = np.asarray(rendered.convert("RGB"), dtype=np.int16)
    red, green, blue = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    body = (red <= 32) & (green >= 8) & (green <= 52) & (blue >= 14) & (blue <= 78) & (blue > green)
    height, width = body.shape
    # The source render includes the independent South Sea inset at lower
    # right. It is never part of the mainland mask.
    body[round(height * 0.66):, round(width * 0.81):] = False
    alpha = Image.fromarray((body.astype(np.uint8) * 230), mode="L")
    return alpha.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.25))


def build_source_mask(source: Image.Image, registration: dict, sample_width: int = 1240) -> Image.Image:
    """Segment cyan water from the terrain page, then close small holes."""
    source = source.convert("RGB")
    scale = sample_width / source.width
    sample_height = round(source.height * scale)
    small = source.resize((sample_width, sample_height), Image.Resampling.LANCZOS)
    rgb = np.asarray(small, dtype=np.int16)
    red, green, blue = rgb[..., 0], rgb[..., 1], rgb[..., 2]

    # The terrain page's water is cyan/blue: its blue channel is materially
    # above red. Snow and pale terrain remain land because their channels are
    # near neutral. This is deliberately a visual segmentation heuristic.
    water = (blue - red > 24) & (blue - green > 3) & (green > 115)
    land = (~water).astype(np.uint8)

    # Restrict processing to the printed main-map frame and remove source-page
    # furniture. These are source image regions, not SVG geometry edits.
    x0, y0, x1, y1 = [round(v * scale) for v in (300, 220, 4650, 3260)]
    keep = np.zeros_like(land, dtype=bool)
    keep[max(0, y0):min(sample_height, y1), max(0, x0):min(sample_width, x1)] = True
    land &= keep
    legend = (slice(round(2580 * scale), min(sample_height, round(3260 * scale))), slice(round(300 * scale), round(1050 * scale)))
    inset = (slice(round(2180 * scale), min(sample_height, round(3260 * scale))), slice(round(3900 * scale), min(sample_width, round(4700 * scale))))
    land[legend] = 0
    land[inset] = 0

    # The reference image draws the national/coastal boundary with a broad
    # lavender band. Treat that image-derived band as a flood-fill barrier.
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lavender = (np.abs(r - g) < 24) & (b - r > 30) & (r > 105) & (r < 225) & (g > 95) & (g < 225)
    lavender &= keep
    # Close only tiny raster gaps in the source's broad boundary band. The
    # band is evidence from the supplied map image, not a hand-drawn outline.
    barrier_img = Image.fromarray((lavender.astype(np.uint8) * 255), mode="L")
    barrier_img = barrier_img.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(5))
    barrier = np.asarray(barrier_img) > 96
    passable = keep & ~barrier

    matrix = np.asarray(registration["matrix"], dtype=float)
    inv = np.linalg.inv(matrix[:2, :2])
    offset = np.asarray(matrix[:2, 2], dtype=float)
    # Existing audited city V coordinates are used only as interior seeds.
    seed_v = [(1958.1115, 860.7744), (2231.1368, 1342.9536),
              (1856.1821, 1823.4782), (2271.1805, 1683.4906),
              (1699.6476, 2011.121)]
    seeds = []
    for vx, vy in seed_v:
        sx, sy = inv @ (np.asarray((vx, vy), dtype=float) - offset)
        seeds.append((round(float(sy * scale)), round(float(sx * scale))))
    reached = np.zeros_like(passable, dtype=bool)
    q: deque[tuple[int, int]] = deque()
    for sy, sx in seeds:
        found = None
        for radius in range(0, 18):
            for yy in range(max(0, sy - radius), min(sample_height, sy + radius + 1)):
                for xx in range(max(0, sx - radius), min(sample_width, sx + radius + 1)):
                    if passable[yy, xx]:
                        found = (yy, xx)
                        break
                if found:
                    break
            if found:
                break
        if found and not reached[found]:
            reached[found] = True
            q.append(found)
    while q:
        yy, xx = q.popleft()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if not dx and not dy:
                    continue
                ny, nx = yy + dy, xx + dx
                if 0 <= ny < sample_height and 0 <= nx < sample_width and passable[ny, nx] and not reached[ny, nx]:
                    reached[ny, nx] = True
                    q.append((ny, nx))
    if reached.sum() > 0:
        land = reached

    # Vectorized majority closing smooths print noise, labels, and tiny holes
    # without drawing a boundary or inventing a polygon.
    padded = np.pad(land, 2, mode="constant")
    neighbours = sum(
        padded[dy:dy + land.shape[0], dx:dx + land.shape[1]]
        for dy in range(5) for dx in range(5)
    )
    land = (neighbours >= 14) & keep
    padded = np.pad(land, 1, mode="constant")
    neighbours3 = sum(
        padded[dy:dy + land.shape[0], dx:dx + land.shape[1]]
        for dy in range(3) for dx in range(3)
    )
    land = (land & (neighbours3 >= 3)) | (neighbours3 >= 7)
    land &= keep

    alpha = Image.fromarray((land.astype(np.uint8) * 230), mode="L")
    # Low-resolution resampling plus a small blur produces feathered edges.
    return alpha.resize(source.size, Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(1.35))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--registration", type=Path, default=DEFAULT_REGISTRATION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--source-svg", type=Path, default=DEFAULT_SOURCE_SVG)
    parser.add_argument("--official-coastline", type=Path, default=OFFICIAL_BODY_SOURCE)
    parser.add_argument("--render", type=Path, default=DEFAULT_RENDER)
    args = parser.parse_args()

    registration = json.loads(args.registration.read_text(encoding="utf-8"))
    if registration.get("status") != "FIT_ACCEPTABLE_FOR_VISUAL_REVIEW":
        raise SystemExit(f"Registration status is not acceptable: {registration.get('status')}")
    source = Image.open(args.source).convert("RGB")
    write_official_path_source(args.official_coastline, args.source_svg)
    rendered_in_v = args.render.exists()
    if rendered_in_v:
        if args.render.name == "presentation-map-render.png":
            source_mask = mask_from_rendered_body(Image.open(args.render))
            maskMethod = "rasterized official presentation-map body-fill pixels"
        else:
            source_mask = mask_from_rendered_outline(Image.open(args.render))
            maskMethod = "rasterized official display path3 outline with flood-fill interior"
    else:
        source_mask = build_source_mask(source, registration)
        maskMethod = "terrain JPG cyan-water segmentation with seeded connected components"
    inverse = affine_inverse(registration["matrix"])
    if rendered_in_v:
        # Browser rasterization already used the SVG viewBox; do not apply the
        # terrain JPG affine a second time.
        v_mask = source_mask.resize((round(VIEWBOX[0]), round(VIEWBOX[1])), Image.Resampling.LANCZOS)
    else:
        v_mask = source_mask.transform(
            (round(VIEWBOX[0]), round(VIEWBOX[1])),
            Image.Transform.AFFINE,
            inverse,
            resample=Image.Resampling.BICUBIC,
            fillcolor=0,
        )
    # Keep an explicit alpha channel and no visible RGB color. Canvas uses the
    # alpha channel with destination-in; the PNG itself is not a map layer.
    rgba = Image.merge("RGBA", (Image.new("L", v_mask.size, 255),) * 3 + (v_mask,))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(args.output, format="PNG", optimize=True)

    metadata = {
        "schemaVersion": "1.0",
        "status": "APPROXIMATE_VISUAL_MASK",
        "purpose": "Visual clipping for terrain and solar Canvas layers only; not a geographic source.",
        "sourceFile": str(args.source).replace("\\", "/"),
        "sourceSha256": sha256(args.source),
        "officialDisplaySource": str(args.official_coastline).replace("\\", "/"),
        "officialDisplaySourceSha256": sha256(args.official_coastline),
        "displayPathId": "path3",
        "displayPathSourceCopy": str(args.source_svg).replace("\\", "/"),
        "sourceDimensions": {"width": source.width, "height": source.height},
        "registrationFile": str(args.registration).replace("\\", "/"),
        "registrationSha256": sha256(args.registration),
        "registrationModel": "affine_source_pixel_to_V",
        "sourcePixelToV": registration["matrix"],
        "inverseVToSourcePixel": inverse,
        "outputFile": str(args.output).replace("\\", "/"),
        "outputSha256": sha256(args.output),
        "outputDimensions": {"width": rgba.width, "height": rgba.height},
        "viewBox": "0 0 3025.3333 2137.3333",
        "southSeaInset": {"included": False, "sourceRegionSuppressed": "x=3900..4700, y=2180..3260"},
        "processing": [
            "terrain JPG only; no webpage screenshot",
            "presentation-map path3 copied to an independent visual-only fill source with fill-rule=evenodd",
            "cyan-water color segmentation at low resolution",
            "majority closing and low-pass resampling",
            "1.35px alpha feather",
            "source legend and source South Sea inset suppressed",
            "no hand-drawn Chinese outline",
        ],
        "maskMethod": maskMethod,
        "approximation": {
            "maximumAlpha": 230,
            "edgeError": "Not an authoritative coastline comparison; official SVG has no reliable solid land fill.",
            "knownErrors": [
                "neighboring land in the terrain reference can be conservatively included",
                "small islands may be softened by low-resolution segmentation",
                "this mask must not be used for borders, cities, coordinates, or map facts",
            ],
        },
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
    args.metadata.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "sha256": metadata["outputSha256"], "size": metadata["outputDimensions"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
