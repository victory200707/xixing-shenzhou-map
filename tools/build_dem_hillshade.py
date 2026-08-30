"""Build a V-space Hillshade from public Terrarium elevation tiles.

The output is a visual terrain texture only. It does not replace the official
map geometry and is clipped by the existing same-source visual land mask in
the browser.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TILE_DIR = ROOT / "assets/terrain/source/terrarium-z5"
OUTPUT = ROOT / "assets/map/raster/dem-hillshade-v.png"
ELEVATION_OUTPUT = ROOT / "assets/map/raster/dem-elevation-v.png"
METADATA = ROOT / "assets/map/metadata/dem-hillshade-v.json"
TILE_SIZE = 256
ZOOM = 5
TILE_X_MIN, TILE_X_MAX = 22, 28
TILE_Y_MIN, TILE_Y_MAX = 10, 14
OUT_W, OUT_H = 1513, 1069
VIEW_W, VIEW_H = 3025.3333, 2137.3333
EARTH_RADIUS = 6378137.0
RAD = math.pi / 180.0
DEG = 180.0 / math.pi
BRIDGE = {
    "a": 0.0005049096535585887, "b": 0.000022454384736449136,
    "tx": 1361.601054864795, "c": 0.000025236110567069284,
    "d": -0.0005152163553260364, "ty": 3246.205083005489,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def lcc_constants() -> tuple[float, float, float, float]:
    phi1, phi2, lon0 = 25 * RAD, 47 * RAD, 105 * RAD
    n = math.log(math.cos(phi1) / math.cos(phi2)) / math.log(
        math.tan(math.pi / 4 + phi2 / 2) / math.tan(math.pi / 4 + phi1 / 2)
    )
    f = math.cos(phi1) * math.tan(math.pi / 4 + phi1 / 2) ** n / n
    return n, f, f, lon0


def inverse_v(vx: np.ndarray, vy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    dx, dy = vx - BRIDGE["tx"], vy - BRIDGE["ty"]
    det = BRIDGE["a"] * BRIDGE["d"] - BRIDGE["b"] * BRIDGE["c"]
    px = (BRIDGE["d"] * dx - BRIDGE["b"] * dy) / det
    py = (-BRIDGE["c"] * dx + BRIDGE["a"] * dy) / det
    n, f, rho0, lon0 = lcc_constants()
    rho = np.hypot(px / EARTH_RADIUS, rho0 - py / EARTH_RADIUS)
    theta = np.arctan2(px / EARTH_RADIUS, rho0 - py / EARTH_RADIUS)
    lon = (lon0 + theta / n) * DEG
    lat = (2 * np.arctan(np.power(f / np.maximum(rho, 1e-12), 1 / n)) - math.pi / 2) * DEG
    return lon, lat


def terrarium_mosaic() -> np.ndarray:
    width = (TILE_X_MAX - TILE_X_MIN + 1) * TILE_SIZE
    height = (TILE_Y_MAX - TILE_Y_MIN + 1) * TILE_SIZE
    mosaic = np.zeros((height, width), dtype=np.float32)
    for tx in range(TILE_X_MIN, TILE_X_MAX + 1):
        for ty in range(TILE_Y_MIN, TILE_Y_MAX + 1):
            path = TILE_DIR / f"z5-x{tx}-y{ty}.png"
            if not path.exists():
                raise FileNotFoundError(path)
            rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)
            # Mapzen Terrarium encoding: elevation = R*256 + G + B/256 - 32768.
            elevation = rgb[:, :, 0] * 256.0 + rgb[:, :, 1] + rgb[:, :, 2] / 256.0 - 32768.0
            y0, x0 = (ty - TILE_Y_MIN) * TILE_SIZE, (tx - TILE_X_MIN) * TILE_SIZE
            mosaic[y0:y0 + TILE_SIZE, x0:x0 + TILE_SIZE] = elevation
    return mosaic


def main() -> None:
    mosaic = terrarium_mosaic()
    mosaic_h, mosaic_w = mosaic.shape
    world_size = TILE_SIZE * (2 ** ZOOM)
    output = np.zeros((OUT_H, OUT_W), dtype=np.float32)
    x_values = (np.arange(OUT_W, dtype=np.float64) + 0.5) * VIEW_W / OUT_W
    for row in range(OUT_H):
        y_values = np.full(OUT_W, (row + 0.5) * VIEW_H / OUT_H, dtype=np.float64)
        lon, lat = inverse_v(x_values, y_values)
        lat_clip = np.clip(lat, -85.05112878, 85.05112878)
        gx = (lon + 180.0) / 360.0 * world_size
        gy = (1.0 - np.arcsinh(np.tan(lat_clip * RAD)) / math.pi) / 2.0 * world_size
        mx = np.clip(gx - TILE_X_MIN * TILE_SIZE, 0, mosaic_w - 1.001)
        my = np.clip(gy - TILE_Y_MIN * TILE_SIZE, 0, mosaic_h - 1.001)
        x0, y0 = np.floor(mx).astype(np.int32), np.floor(my).astype(np.int32)
        x1, y1 = np.minimum(x0 + 1, mosaic_w - 1), np.minimum(y0 + 1, mosaic_h - 1)
        fx, fy = mx - x0, my - y0
        output[row] = (
            mosaic[y0, x0] * (1 - fx) * (1 - fy)
            + mosaic[y0, x1] * fx * (1 - fy)
            + mosaic[y1, x0] * (1 - fx) * fy
            + mosaic[y1, x1] * fx * fy
        )

    # Keep the raw sampled elevation as a separate visual-analysis asset. The
    # browser uses its local gradient for directional lighting; it does not
    # use this raster as a geographic boundary or map source.
    elevation_samples = output[np.isfinite(output)]
    elevation_lo = float(np.percentile(elevation_samples, 1.0))
    elevation_hi = float(np.percentile(elevation_samples, 99.0))
    elevation_norm = np.clip((output - elevation_lo) / max(elevation_hi - elevation_lo, 1e-6), 0, 1)
    Image.fromarray(np.rint(elevation_norm * 255).astype(np.uint8), mode="L").save(ELEVATION_OUTPUT, format="PNG", optimize=False)

    # Static northwest hillshade supplies terrain relief; solar color remains a
    # separate dynamic layer in the browser.
    gy, gx = np.gradient(output)
    slope = np.arctan(np.hypot(gx, gy) * 2.2)
    aspect = np.arctan2(-gx, gy)
    azimuth = 315 * RAD
    altitude = 45 * RAD
    shade = np.sin(altitude) * np.cos(slope) + np.cos(altitude) * np.sin(slope) * np.cos(azimuth - aspect)
    shade = np.clip((shade - shade.min()) / max(float(shade.max() - shade.min()), 1e-6), 0, 1)
    Image.fromarray(np.rint(shade * 255).astype(np.uint8), mode="L").save(OUTPUT, format="PNG", optimize=False)
    METADATA.parent.mkdir(parents=True, exist_ok=True)
    tile_hashes = {p.name: sha256(p) for p in sorted(TILE_DIR.glob("*.png"))}
    metadata = {
        "schemaVersion": "1.0",
        "status": "APPROXIMATE_DEM_HILLSHADE_VISUAL_TEXTURE",
        "source": {
            "provider": "AWS elevation-tiles-prod Terrarium tiles",
            "urlTemplate": "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/5/{x}/{y}.png",
            "encoding": "Mapzen Terrarium RGB elevation",
            "zoom": ZOOM,
            "tiles": len(tile_hashes),
            "tileSha256": tile_hashes,
            "licenseNote": "Retain upstream attribution and verify redistribution terms before publication.",
        },
        "outputFile": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "outputSha256": sha256(OUTPUT),
        "elevationAnalysisFile": str(ELEVATION_OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "elevationAnalysisSha256": sha256(ELEVATION_OUTPUT),
        "elevationAnalysisEncoding": "8-bit normalized sampled elevation; visual slope proxy only",
        "elevationPercentileRange": {"p01": elevation_lo, "p99": elevation_hi},
        "outputDimensions": {"width": OUT_W, "height": OUT_H},
        "outputViewBox": f"0 0 {VIEW_W} {VIEW_H}",
        "projectionChain": ["WGS84", "project inverse LCC", "inverse SpatialBridge", "SVG V sampling"],
        "processing": ["bilinear Terrarium elevation sampling", "fixed northwest 315-degree hillshade", "normalized grayscale output", "browser-side same-source visual mask clipping"],
        "knownLimitations": ["not a replacement for the official map geometry", "30m/90m source lineage and vertical datum depend on upstream tile product", "visual Hillshade only; not suitable for quantitative elevation analysis"],
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
    METADATA.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "sha256": metadata["outputSha256"], "dimensions": metadata["outputDimensions"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
