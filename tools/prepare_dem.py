#!/usr/bin/env python3
"""Validate and register the real DEM input before terrain rendering.

This is intentionally a gate, not a downloader. It refuses to create formal
terrain assets until the GeoTIFF and its provenance metadata are present.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEM = ROOT / "assets/map/source/dem.tif"
DEFAULT_MANIFEST = ROOT / "assets/terrain/metadata/terrain-manifest.json"
REQUIRED = ("name", "publisher", "version", "downloadUrl", "license", "downloadDate")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dem", type=Path, default=DEFAULT_DEM)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    if not args.dem.exists():
        print(f"BLOCKED: DEM not found: {args.dem}", file=sys.stderr)
        print("Place the licensed Copernicus DEM GeoTIFF at assets/map/source/dem.tif.", file=sys.stderr)
        return 2

    try:
        import rasterio  # type: ignore
    except ImportError:
        print("BLOCKED: rasterio is required to inspect GeoTIFF CRS, bounds and NoData.", file=sys.stderr)
        print("Install rasterio in the project Python environment, then rerun this script.", file=sys.stderr)
        return 3

    manifest = {}
    if args.manifest.exists():
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED if not manifest.get(key)]
    if missing:
        print("BLOCKED: provenance manifest is incomplete: " + ", ".join(missing), file=sys.stderr)
        return 4

    with rasterio.open(args.dem) as dataset:
        metadata = {
            "path": str(args.dem.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(args.dem),
            "width": dataset.width,
            "height": dataset.height,
            "count": dataset.count,
            "dtype": dataset.dtypes[0],
            "crs": dataset.crs.to_string() if dataset.crs else None,
            "bounds": [dataset.bounds.left, dataset.bounds.bottom, dataset.bounds.right, dataset.bounds.top],
            "resolution": list(dataset.res),
            "nodata": dataset.nodata,
            "checkedAt": datetime.now(timezone.utc).isoformat(),
        }
    if not metadata["crs"]:
        print("BLOCKED: DEM has no CRS; do not guess one.", file=sys.stderr)
        return 5
    manifest["input"] = metadata
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    print(f"PASS: provenance and GeoTIFF metadata recorded in {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
