"""Derive a visual-only land mask from the rendered official boundary layer.

The source is an already-rendered official SVG viewBox image. This tool only
detects the blue outer boundary, closes sub-pixel raster gaps, flood-fills the
inside, and records that the result is an approximate visual clipping layer.
It never edits SVG geometry and never supplies geographic facts.
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

VIEWBOX = (3025.3333, 2137.3333)
SEEDS = {
    "mainland": (1958.1115, 860.7744),
    "hainan": (1699.6476, 2011.121),
    "taiwan": (2271.1805, 1683.4906),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def v_to_pixel(vx: float, vy: float, width: int, height: int) -> tuple[int, int]:
    return round(vx * width / VIEWBOX[0]), round(vy * height / VIEWBOX[1])


def flood_outside(barrier: np.ndarray) -> np.ndarray:
    height, width = barrier.shape
    outside = np.zeros_like(barrier, dtype=bool)
    queue: deque[tuple[int, int]] = deque()
    for x in range(width):
        if not barrier[0, x]: queue.append((0, x)); outside[0, x] = True
        if not barrier[height - 1, x] and not outside[height - 1, x]: queue.append((height - 1, x)); outside[height - 1, x] = True
    for y in range(height):
        if not barrier[y, 0] and not outside[y, 0]: queue.append((y, 0)); outside[y, 0] = True
        if not barrier[y, width - 1] and not outside[y, width - 1]: queue.append((y, width - 1)); outside[y, width - 1] = True
    while queue:
        y, x = queue.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < height and 0 <= nx < width and not barrier[ny, nx] and not outside[ny, nx]:
                outside[ny, nx] = True
                queue.append((ny, nx))
    return outside


def connected_from(seed: tuple[int, int], candidate: np.ndarray) -> np.ndarray:
    height, width = candidate.shape
    sy, sx = seed[1], seed[0]
    if not (0 <= sx < width and 0 <= sy < height):
        return np.zeros_like(candidate)
    if not candidate[sy, sx]:
        for radius in range(1, 20):
            found = None
            for y in range(max(0, sy - radius), min(height, sy + radius + 1)):
                for x in range(max(0, sx - radius), min(width, sx + radius + 1)):
                    if candidate[y, x]: found = (y, x); break
                if found: break
            if found: sx, sy = found; break
    if not candidate[sy, sx]: return np.zeros_like(candidate)
    result = np.zeros_like(candidate, dtype=bool)
    queue: deque[tuple[int, int]] = deque([(sy, sx)])
    result[sy, sx] = True
    while queue:
        y, x = queue.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < height and 0 <= nx < width and candidate[ny, nx] and not result[ny, nx]:
                result[ny, nx] = True
                queue.append((ny, nx))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("tools/presentation-map-render.png"))
    parser.add_argument("--output", type=Path, default=Path("assets/map/raster/official-boundary-visual-mask.png"))
    parser.add_argument("--metadata", type=Path, default=Path("assets/map/metadata/official-boundary-visual-mask.json"))
    parser.add_argument("--diagnostic", type=Path, default=Path("docs/screenshots/official-boundary-mask-bw.png"))
    args = parser.parse_args()
    image = Image.open(args.source).convert("RGB")
    rgb = np.asarray(image, dtype=np.int16)
    red, green, blue = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    # The official coast/body outline is blue-gray; province linework is warm.
    candidate = ((blue > 8) & (blue > red + 3) & (blue > green)) | ((red > 80) & (green > 80) & (blue > 80) & (np.maximum.reduce([red, green, blue]) - np.minimum.reduce([red, green, blue]) < 35))
    barrier_img = Image.fromarray((candidate.astype(np.uint8) * 255), "L")
    # The archived raster is only a display-resolution outline. A larger
    # closing pass bridges anti-aliased coastline joins before filling.
    barrier_img = barrier_img.filter(ImageFilter.MaxFilter(51)).filter(ImageFilter.MinFilter(25))
    barrier = np.asarray(barrier_img) > 100
    # The lower-right inset is a separate map and cannot enter the mainland mask.
    h, w = barrier.shape
    inset = np.zeros_like(barrier)
    inset[round(h * 0.62):, round(w * 0.76):] = True
    barrier[inset] = False
    outside = flood_outside(barrier)
    enclosed = ~outside & ~barrier
    main_seed = v_to_pixel(*SEEDS["mainland"], w, h)
    land = connected_from(main_seed, enclosed)
    # Add only explicitly seeded Hainan/Taiwan islands if their official loops
    # are closed; no other island or inset pixels are inferred.
    for name in ("hainan", "taiwan"):
        seed = v_to_pixel(*SEEDS[name], w, h)
        island = connected_from(seed, enclosed)
        land |= island
    land[inset] = False
    alpha = Image.fromarray((land.astype(np.uint8) * 235), "L").filter(ImageFilter.GaussianBlur(0.7))
    rgba = Image.merge("RGBA", (Image.new("L", (w, h), 255),) * 3 + (alpha,))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.diagnostic.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(args.output, "PNG", optimize=False)
    Image.fromarray((land.astype(np.uint8) * 255), "L").save(args.diagnostic, "PNG", optimize=False)
    samples = {name: int(alpha.getpixel(v_to_pixel(*v, w, h))) for name, v in SEEDS.items()}
    coverage = float(land.mean())
    metadata = {
        "schemaVersion": "1.0",
        "status": "APPROXIMATE_VISUAL_MASK_PENDING_REVIEW",
        "purpose": "Solar and terrain visual clipping only; not a geographic source.",
        "source": {"path": str(args.source).replace("\\", "/"), "sha256": sha256(args.source), "officialSvgViewBox": "0 0 3025.3333 2137.3333"},
        "output": {"path": str(args.output).replace("\\", "/"), "sha256": sha256(args.output), "width": w, "height": h, "coverageRatio": coverage},
        "diagnostic": {"path": str(args.diagnostic).replace("\\", "/"), "sha256": sha256(args.diagnostic), "samples": samples},
        "method": "blue-gray official outer-boundary detection, raster gap closing, outside flood-fill, explicit mainland/Hainan/Taiwan seeds",
        "southSeaInset": {"included": False, "reason": "separate lower-right display region excluded"},
        "limitations": ["Raster source is a visual rendering of the official SVG.", "No official land polygon semantics are asserted.", "Small islands other than explicitly seeded Hainan/Taiwan are not inferred."],
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "label": "APPROXIMATE_VISUAL_MASK — NOT A GEOGRAPHIC SOURCE",
    }
    args.metadata.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"coverageRatio": coverage, "samples": samples, "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
