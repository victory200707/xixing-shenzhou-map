"""Fill the existing approximate coastline outline into a visual-only mask.

The input is an archived raster outline derived from the supplied map artwork.
This script performs only raster topology operations; it does not create or
edit geographic vectors and the output is not a geographic data source.
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def flood_outside(barrier: np.ndarray) -> np.ndarray:
    h, w = barrier.shape
    outside = np.zeros_like(barrier, dtype=bool)
    queue: deque[tuple[int, int]] = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not barrier[y, x] and not outside[y, x]:
                outside[y, x] = True
                queue.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if not barrier[y, x] and not outside[y, x]:
                outside[y, x] = True
                queue.append((y, x))
    while queue:
        y, x = queue.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not barrier[ny, nx] and not outside[ny, nx]:
                outside[ny, nx] = True
                queue.append((ny, nx))
    return outside


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("assets/map/raster/approx-land-mask.png"))
    parser.add_argument("--output", type=Path, default=Path("assets/map/raster/approx-land-fill-mask.png"))
    parser.add_argument("--diagnostic", type=Path, default=Path("docs/screenshots/approx-land-fill-mask-bw.png"))
    parser.add_argument("--metadata", type=Path, default=Path("assets/map/metadata/approx-land-fill-mask.json"))
    args = parser.parse_args()

    source = Image.open(args.input).convert("RGBA")
    alpha = np.asarray(source)[..., 3]
    # Close only tiny anti-aliased breaks in the supplied outline.
    barrier_img = Image.fromarray((alpha > 40).astype(np.uint8) * 255, "L")
    barrier_img = barrier_img.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(5))
    barrier = np.asarray(barrier_img) > 80
    # The supplied outline has small anti-aliased breaks, so use a scanline
    # envelope after closing it. This fills the dominant China body without
    # inventing a vector boundary; isolated labels and inset fragments are not
    # selected because they do not span a row.
    h, w = barrier.shape
    land = np.zeros_like(barrier, dtype=bool)
    for y in range(h):
        xs = np.flatnonzero(barrier[y])
        if xs.size < 2:
            continue
        # Ignore tiny annotation dots and use the outer envelope of the map.
        left, right = int(xs[0]), int(xs[-1])
        if right - left >= 80:
            land[y, left:right + 1] = True
    # Constrain to the observed body envelope and remove the lower-right inset.
    land[:35] = False
    land[2050:] = False
    land[:, :70] = False
    land[:, 2860:] = False
    land[int(h * 0.67):, int(w * 0.80):] = False
    land = np.asarray(Image.fromarray((land.astype(np.uint8) * 255), "L").filter(ImageFilter.MinFilter(5))) > 80
    land |= barrier & (np.indices(barrier.shape)[1] < 2860)
    alpha_out = Image.fromarray((land.astype(np.uint8) * 225), "L").filter(ImageFilter.GaussianBlur(1.2))
    rgba = Image.merge("RGBA", (Image.new("L", source.size, 255),) * 3 + (alpha_out,))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.diagnostic.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(args.output, "PNG", optimize=True)
    Image.fromarray((land.astype(np.uint8) * 255), "L").save(args.diagnostic, "PNG", optimize=True)
    metadata = {
        "schemaVersion": "1.0",
        "status": "APPROXIMATE_VISUAL_MASK",
        "label": "APPROXIMATE_VISUAL_MASK - NOT A GEOGRAPHIC SOURCE",
        "purpose": "Visual clipping for the solar land-color layer only.",
        "sourceFile": str(args.input).replace("\\", "/"),
        "sourceSha256": sha256(args.input),
        "outputFile": str(args.output).replace("\\", "/"),
        "outputSha256": sha256(args.output),
        "outputDimensions": {"width": source.width, "height": source.height},
        "viewBox": "0 0 3025.3333 2137.3333",
        "method": "Raster outline gap-closing, outside flood-fill, dominant enclosed component selection, and 1.2px feathering.",
        "southSeaInset": {"included": False, "reason": "Only dominant main-map enclosed component retained."},
        "knownLimitations": [
            "Derived from a visual raster outline, not a geographic polygon.",
            "Small islands and narrow coastal features may be omitted or softened.",
            "Never use for borders, city coordinates, map facts, or formal publication.",
        ],
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
    args.metadata.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "coverage": float(land.mean())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
