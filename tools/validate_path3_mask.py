"""Validate whether official path3 renders as an interior fill.

This deliberately does not flood-fill, dilate, close, or otherwise repair the
path. It samples the exact rasterization of the independent path3 copy only.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps


RENDER = Path("tools/path3-render-original.png")
MASK = Path("docs/screenshots/phase1c9e-path3-mask-bw.png")
SAMPLES = Path("docs/phase1c9e-path3-samples.json")

SAMPLE_POINTS = {
    "beijing": (1958.1115, 860.7744),
    "urumqi": (789.5632, 547.7053),
    "guangzhou": (1856.1821, 1823.4782),
    "haikou_hainan": (1699.6476, 2011.121),
    "taiwan_taipei": (2271.1805, 1683.4906),
    "western_mainland_lhasa": (771.3615, 1376.7095),
    "northeastern_mainland_harbin": (2293.3535, 478.5389),
    "ocean_east": (2600.0, 1200.0),
    "ocean_south": (2200.0, 2000.0),
    "south_sea_inset": (2777.1875, 1672.5696),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sample_alpha(gray: np.ndarray, x: float, y: float, radius: int = 2) -> float:
    ix, iy = round(x), round(y)
    crop = gray[max(0, iy - radius):iy + radius + 1, max(0, ix - radius):ix + radius + 1]
    return float(crop.mean() / 255.0) if crop.size else 0.0


def main() -> None:
    image = Image.open(RENDER).convert("RGB")
    gray = np.asarray(ImageOps.grayscale(image), dtype=np.uint8)
    # Screenshot is opaque black background plus the exact white path3 render.
    # Threshold only; no morphology or filling is applied.
    bw = Image.fromarray((gray >= 128).astype(np.uint8) * 255, mode="L")
    MASK.parent.mkdir(parents=True, exist_ok=True)
    bw.save(MASK, format="PNG", optimize=True)
    mask_gray = np.asarray(bw, dtype=np.uint8)
    samples = {
        name: {
            "v": [x, y],
            "alpha": sample_alpha(mask_gray, x, y),
            "window": "5x5 mean",
        }
        for name, (x, y) in SAMPLE_POINTS.items()
    }
    interior = [v["alpha"] for k, v in samples.items() if k not in {"ocean_east", "ocean_south", "south_sea_inset"}]
    ocean = [samples[k]["alpha"] for k in ("ocean_east", "ocean_south", "south_sea_inset")]
    result = {
        "status": "BLOCKED_PATH3_IS_OUTLINE_ONLY" if max(interior, default=0) < 0.95 else "INTERIOR_FILL_PRESENT",
        "sourcePathId": "path3",
        "renderDimensions": {"width": image.width, "height": image.height},
        "maskFile": str(MASK).replace("\\", "/"),
        "maskSha256": sha256(MASK),
        "interiorSampleResults": samples,
        "interiorAlphaMean": float(np.mean(interior)) if interior else 0.0,
        "oceanAlphaMean": float(np.mean(ocean)) if ocean else 0.0,
        "southSeaIncluded": samples["south_sea_inset"]["alpha"] > 0.05,
        "method": "exact path3 render; threshold only; no flood fill, dilation, closure, or hand drawing",
    }
    SAMPLES.parent.mkdir(parents=True, exist_ok=True)
    SAMPLES.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
