#!/usr/bin/env python3
"""Build the Phase 1B-3 DEM-to-V raster pipeline.

When the licensed GeoTIFF is absent this script runs a deterministic mock
mode. The mock still exercises the real spatial direction:

    V pixel -> inverse affine -> LCC P -> WGS84 G -> synthetic elevation

It never edits the official SVG, clips it, or adds lighting/solar effects.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from pyproj import CRS, Transformer


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BRIDGE = ROOT / "assets/map/metadata/spatial_bridge.json"
DEFAULT_POINTS = ROOT / "assets/map/metadata/control-points.json"
DEFAULT_DEM = ROOT / "assets/map/source/dem.tif"
DEFAULT_OUTPUT = ROOT / "assets/map/raster/mock_base.png"
OUTPUT_WIDTH = 3025
OUTPUT_HEIGHT = 2137
BUFFER_DEGREES = 2.0
BOUNDARY_NAMES = {"漠河", "曾母暗沙", "喀什", "抚远"}
GEBCO_URL = "https://www.gebco.net/data_and_products/gridded_bathymetry_data/"
SRTM_URL = "https://www.earthdata.nasa.gov/data/catalog/lpcloud-srtmgl1-003"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_boundary(points_path: Path) -> tuple[dict[str, float], list[dict[str, Any]]]:
    payload = load_json(points_path)
    points = payload.get("controlPoints", [])
    selected = [point for point in points if point.get("name") in BOUNDARY_NAMES]
    missing = sorted(BOUNDARY_NAMES - {point.get("name") for point in selected})
    if missing:
        raise ValueError(f"Missing required boundary control points: {', '.join(missing)}")
    lons = [float(point["longitudeDeg"]) for point in selected]
    lats = [float(point["latitudeDeg"]) for point in selected]
    bbox = {
        "minLon": min(lons) - BUFFER_DEGREES,
        "maxLon": max(lons) + BUFFER_DEGREES,
        "minLat": min(lats) - BUFFER_DEGREES,
        "maxLat": max(lats) + BUFFER_DEGREES,
        "bufferDegrees": BUFFER_DEGREES,
    }
    return bbox, selected


def inverse_bridge(bridge: dict[str, Any]) -> tuple[np.ndarray, list[float], str]:
    matrix = np.asarray(bridge["mainMap"]["affine"]["matrix"], dtype=float)
    if matrix.shape != (3, 3):
        raise ValueError(f"Expected 3x3 main affine matrix, got {matrix.shape}")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("SpatialBridge matrix contains non-finite values")
    return np.linalg.inv(matrix), bridge["coordinateDomains"]["V"]["viewBox"], bridge["coordinateDomains"]["P"]["proj4"]


def mock_elevation(lon: np.ndarray, lat: np.ndarray, bbox: dict[str, float]) -> np.ndarray:
    """Return a deterministic synthetic elevation-like field in [0, 1]."""
    lon_span = bbox["maxLon"] - bbox["minLon"]
    lat_span = bbox["maxLat"] - bbox["minLat"]
    u = (lon - bbox["minLon"]) / lon_span
    v = (lat - bbox["minLat"]) / lat_span
    broad = 0.5 + 0.22 * np.sin(u * math.pi * 3.1) + 0.18 * np.cos(v * math.pi * 4.7)
    ridges = 0.08 * np.sin((u * 17.0 + v * 5.0) * math.pi) + 0.05 * np.cos((u * 29.0 - v * 11.0) * math.pi)
    slope = 0.08 * (1.0 - v) + 0.04 * u
    return np.clip(broad + ridges + slope, 0.0, 1.0)


def render_mock(bridge: dict[str, Any], bbox: dict[str, float], output_path: Path) -> None:
    inverse_matrix, viewbox, proj4 = inverse_bridge(bridge)
    lcc = CRS.from_proj4(proj4)
    to_geo = Transformer.from_crs(lcc, CRS.from_epsg(4326), always_xy=True)
    min_x, min_y, width, height = [float(value) for value in viewbox]
    output = np.empty((OUTPUT_HEIGHT, OUTPUT_WIDTH), dtype=np.uint8)
    x_values = min_x + (np.arange(OUTPUT_WIDTH, dtype=float) + 0.5) * width / OUTPUT_WIDTH
    homogeneous_x = np.vstack([x_values, np.ones(OUTPUT_WIDTH)])

    for row_start in range(0, OUTPUT_HEIGHT, 128):
        row_end = min(row_start + 128, OUTPUT_HEIGHT)
        y_values = min_y + (np.arange(row_start, row_end, dtype=float) + 0.5) * height / OUTPUT_HEIGHT
        vx = np.broadcast_to(x_values, (row_end - row_start, OUTPUT_WIDTH))
        vy = np.broadcast_to(y_values[:, None], (row_end - row_start, OUTPUT_WIDTH))
        ones = np.ones_like(vx)
        visual = np.stack([vx, vy, ones], axis=0).reshape(3, -1)
        projected = inverse_matrix @ visual
        lon, lat = to_geo.transform(projected[0], projected[1])
        elevation = mock_elevation(np.asarray(lon), np.asarray(lat), bbox).reshape(row_end - row_start, OUTPUT_WIDTH)
        output[row_start:row_end] = np.rint(elevation * 255.0).astype(np.uint8)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(output, mode="L").save(output_path, format="PNG", optimize=False)


def print_download_guide(bbox: dict[str, float]) -> None:
    print("\nDEM download guide (manual; no automatic download is performed)")
    print(f"  Coverage longitude: {bbox['minLon']:.4f}°E to {bbox['maxLon']:.4f}°E")
    print(f"  Coverage latitude : {bbox['minLat']:.4f}°N to {bbox['maxLat']:.4f}°N")
    print(f"  Recommended source: GEBCO gridded bathymetry/topography GeoTIFF or equivalent")
    print(f"  GEBCO: {GEBCO_URL}")
    print(f"  SRTM alternative: {SRTM_URL}")
    print("  Crop/reproject only after recording source version, license, datum, and hash.")
    print("  Expected local path: assets/map/source/dem.tif")
    print("  GEBCO is preferred for this view because it covers both land and offshore South China Sea.")
    print("  SRTM is land elevation only and must not be used to invent offshore bathymetry.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", type=Path, default=DEFAULT_BRIDGE)
    parser.add_argument("--points", type=Path, default=DEFAULT_POINTS)
    parser.add_argument("--dem", type=Path, default=DEFAULT_DEM)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    bridge = load_json(args.bridge)
    bbox, boundary_points = load_boundary(args.points)
    print("Phase 1B-3 DEM pipeline")
    print(f"Bridge: {args.bridge}")
    print(f"Projection: {bridge['coordinateDomains']['P']['proj4']}")
    print(f"Affine matrix source: {args.bridge} -> mainMap.affine.matrix")
    print("Boundary controls: " + ", ".join(point["name"] for point in boundary_points))
    print_download_guide(bbox)

    if args.dem.exists():
        print(f"\nFound real DEM at {args.dem}.", file=sys.stderr)
        print("Real GeoTIFF sampling is intentionally not run in Mock Mode; review its CRS/license before enabling the production branch.", file=sys.stderr)
        return 2

    print("\nMode: MOCK (dem.tif not found)")
    print("Generating a deterministic synthetic elevation array through V -> P -> G inverse sampling…")
    render_mock(bridge, bbox, args.output)
    with Image.open(args.output) as image:
        print(f"Generated: {args.output}")
        print(f"PNG size: {image.size[0]} x {image.size[1]}, mode={image.mode}")
        if image.size != (OUTPUT_WIDTH, OUTPUT_HEIGHT):
            raise RuntimeError(f"Unexpected output size: {image.size}")
    print("Mock render verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
