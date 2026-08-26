"""Build and validate a non-deployable visual land-mask candidate from the terrain JPG.

The JPG is the only geometry-bearing input for segmentation. The registered
official SVG raster is used only to create a review overlay after the candidate
is built; no SVG path, outline, or coordinate geometry is read by the mask
algorithm.
"""
from __future__ import annotations

import hashlib
import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
VIEWBOX = (3025, 2137)
SOURCE = ROOT / "assets/map/source/terrain-reference-gs2016-1609.jpg"
REGISTRATION = ROOT / "assets/map/metadata/terrain-registration.json"
REGISTERED = ROOT / "assets/map/raster/terrain-registered.png"
CANDIDATE = ROOT / "tools/phase1c9f-terrain-jpg-mask-candidate.png"
PREVIEW = ROOT / "docs/screenshots/phase1c9f-terrain-jpg-mask-bw.png"
OVERLAY = ROOT / "docs/screenshots/phase1c9f-terrain-jpg-mask-overlay.png"
SAMPLES = ROOT / "docs/phase1c9f-terrain-jpg-mask-samples.json"
OFFICIAL_RENDER = ROOT / "tools/presentation-map-render.png"

# Existing V coordinates are only interior seed locations and acceptance probes.
# They do not contribute linework or alter any official map geometry.
SAMPLES_V = {
    "mohe": (2121.9267, 110.8648, "land"),
    "beijing": (1958.1115, 860.7744, "land"),
    "urumqi": (789.5632, 547.7053, "land"),
    "kashi": (243.5125, 656.9155, "land"),
    "guangzhou": (1856.1821, 1823.4782, "land"),
    "haikou_hainan": (1699.6476, 2011.121, "land"),
    "taipei_taiwan": (2271.1805, 1683.4906, "land"),
    "western_mainland_lhasa": (771.3615, 1376.7095, "land"),
    "northeastern_mainland_harbin": (2293.3535, 478.5389, "land"),
    "east_offshore": (2600.0, 1200.0, "ocean"),
    "south_offshore": (2200.0, 2000.0, "ocean"),
    "south_sea_inset": (2777.1875, 1672.5696, "ocean"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def inverse_affine(registration: dict) -> tuple[float, float, float, float, float, float]:
    matrix = np.asarray(registration["matrix"], dtype=float)
    linear = matrix[:2, :2]
    translation = matrix[:2, 2]
    inverse = np.linalg.inv(linear)
    offset = -inverse @ translation
    return (inverse[0, 0], inverse[0, 1], offset[0], inverse[1, 0], inverse[1, 1], offset[1])


def registered_jpg(source: Image.Image, inverse: tuple[float, ...]) -> Image.Image:
    return source.transform(VIEWBOX, Image.Transform.AFFINE, inverse, resample=Image.Resampling.BICUBIC, fillcolor=(0, 0, 0))


def find_seed(passable: np.ndarray, x: int, y: int) -> tuple[int, int] | None:
    height, width = passable.shape
    for radius in range(0, 18):
        for yy in range(max(0, y - radius), min(height, y + radius + 1)):
            for xx in range(max(0, x - radius), min(width, x + radius + 1)):
                if passable[yy, xx]:
                    return yy, xx
    return None


def connected_from_seeds(passable: np.ndarray) -> np.ndarray:
    reached = np.zeros_like(passable, dtype=bool)
    queue: deque[tuple[int, int]] = deque()
    for x, y, kind in SAMPLES_V.values():
        if kind != "land":
            continue
        seed = find_seed(passable, round(x), round(y))
        if seed is not None and not reached[seed]:
            reached[seed] = True
            queue.append(seed)
    while queue:
        y, x = queue.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < reached.shape[0] and 0 <= nx < reached.shape[1] and passable[ny, nx] and not reached[ny, nx]:
                reached[ny, nx] = True
                queue.append((ny, nx))
    return reached


def derive_candidate(registered: Image.Image) -> Image.Image:
    rgb = np.asarray(registered.convert("RGB"), dtype=np.int16)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]

    # Cyan ocean is detected from the source image itself. The printed national
    # boundary band is a blue-purple, low-red/high-blue feature. Both become
    # non-passable; neither is painted into the output Mask.
    water = (b - r > 22) & (b - g > 2) & (g > 110)
    purple_boundary = (b - r > 28) & (b - g > 18) & (r >= 85) & (r <= 225) & (g >= 75) & (g <= 225)
    black_page_margin = (r < 9) & (g < 9) & (b < 9)
    passable = ~(water | purple_boundary | black_page_margin)

    # Never seed or retain the printed South Sea inset area in the mainland mask.
    passable[1500:, 2450:] = False
    land = connected_from_seeds(passable)

    # A single, small alpha blur is edge feathering only. It neither closes
    # gaps nor expands an outline into an area.
    alpha = Image.fromarray((land.astype(np.uint8) * 255), mode="L")
    return alpha.filter(ImageFilter.GaussianBlur(2.0))


def sample_alpha(mask: Image.Image) -> dict:
    values = np.asarray(mask, dtype=np.float32) / 255.0
    results = {}
    for name, (x, y, kind) in SAMPLES_V.items():
        xi, yi = round(x), round(y)
        window = values[max(0, yi - 2):yi + 3, max(0, xi - 2):xi + 3]
        results[name] = {"v": [x, y], "kind": kind, "alpha": round(float(window.mean()), 5), "window": "5x5 mean"}
    return results


def write_overlay(mask: Image.Image) -> None:
    if not OFFICIAL_RENDER.exists():
        return
    base = Image.open(OFFICIAL_RENDER).convert("RGBA").resize(VIEWBOX, Image.Resampling.LANCZOS)
    tint = Image.new("RGBA", VIEWBOX, (231, 193, 112, 0))
    tint.putalpha(mask.point(lambda value: round(value * 0.42)))
    Image.alpha_composite(base, tint).convert("RGB").save(OVERLAY, optimize=True)


def main() -> None:
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    if registration.get("status") != "FIT_ACCEPTABLE_FOR_VISUAL_REVIEW":
        raise SystemExit("Registration has not passed visual review")
    source = Image.open(SOURCE).convert("RGB")
    registered = registered_jpg(source, inverse_affine(registration))
    REGISTERED.parent.mkdir(parents=True, exist_ok=True)
    registered.save(REGISTERED, optimize=True)
    mask = derive_candidate(registered)
    CANDIDATE.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    mask.save(CANDIDATE, optimize=True)
    mask.point(lambda value: 255 if value >= 128 else 0).save(PREVIEW, optimize=True)
    write_overlay(mask)
    samples = sample_alpha(mask)
    land_values = [item["alpha"] for item in samples.values() if item["kind"] == "land"]
    ocean_values = [item["alpha"] for item in samples.values() if item["kind"] == "ocean"]
    passed = min(land_values) >= 0.9 and max(ocean_values) <= 0.05
    report = {
        "status": "PASS_CANDIDATE_READY_FOR_HUMAN_OVERLAY_REVIEW" if passed else "BLOCKED_TERRAIN_JPG_MASK",
        "maskType": "APPROXIMATE_VISUAL_MASK",
        "sourceFile": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "sourceSha256": sha256(SOURCE),
        "sourceDimensions": {"width": source.width, "height": source.height},
        "registrationFile": str(REGISTRATION.relative_to(ROOT)).replace("\\", "/"),
        "registrationSha256": sha256(REGISTRATION),
        "registrationMatrix": registration["matrix"],
        "viewBox": "0 0 3025.3333 2137.3333",
        "registeredOutput": str(REGISTERED.relative_to(ROOT)).replace("\\", "/"),
        "registeredOutputSha256": sha256(REGISTERED),
        "candidateOutput": str(CANDIDATE.relative_to(ROOT)).replace("\\", "/"),
        "candidateOutputSha256": sha256(CANDIDATE),
        "featherRadius": 2.0,
        "sourceOnlySegmentation": "JPG water and printed blue-purple boundary pixels; seed-connected interior components; no SVG path source, no manual geometry.",
        "southSeaIncluded": False,
        "samples": samples,
        "landAlphaMinimum": min(land_values),
        "oceanAlphaMaximum": max(ocean_values),
        "acceptance": {"landAlphaMinimum": 0.9, "oceanAlphaMaximum": 0.05},
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
    SAMPLES.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
