#!/usr/bin/env python3
"""Fit the geographic (G) to visual SVG (V) bridge from human control points.

This script never edits the Audit SVG and never changes control-point values.
It fits only dynamic-layer mapping parameters. The South China Sea inset is a
separate visual domain and is not forced into the mainland transform.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from pyproj import CRS, Transformer


VIEWBOX = [0.0, 0.0, 3025.3333, 2137.3333]
LCC_PROJ4 = (
    "+proj=lcc +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 "
    "+datum=WGS84 +units=m +no_defs"
)
INSET_X_THRESHOLD = 2600.0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_inset(point: dict[str, Any]) -> bool:
    domain = str(point.get("domain", point.get("visualDomain", ""))).lower()
    role = str(point.get("role", "")).lower()
    name = str(point.get("name", ""))
    point_id = str(point.get("id", ""))
    if domain in {"inset", "south-sea-inset", "south_sea_inset"}:
        return True
    if "inset" in role or "south" in role or "南海" in role:
        return True
    if "三沙" in name or "sansha" in point_id.lower():
        return True
    return float(point["x"]) >= INSET_X_THRESHOLD


def as_float(point: dict[str, Any], key: str) -> float:
    value = point.get(key)
    if value is None:
        raise ValueError(f"Control point {point.get('id', '<unknown>')} lacks {key}")
    return float(value)


def validate_control_points(payload: dict[str, Any], points: list[dict[str, Any]]) -> dict[str, Any]:
    """Fail before fitting if the human capture file is structurally invalid."""
    errors: list[str] = []
    if payload.get("geographicCoordinateDomain", {}).get("epsg") not in (4326, "4326"):
        errors.append("geographicCoordinateDomain.epsg must be 4326 (WGS84)")
    ids: set[str] = set()
    required = ("id", "longitudeDeg", "latitudeDeg", "x", "y")
    for index, point in enumerate(points):
        prefix = f"controlPoints[{index}]"
        if not isinstance(point, dict):
            errors.append(f"{prefix} must be an object")
            continue
        point_id = point.get("id")
        if not isinstance(point_id, str) or not point_id.strip():
            errors.append(f"{prefix}.id must be a non-empty string")
        elif point_id in ids:
            errors.append(f"{prefix}.id duplicates {point_id}")
        else:
            ids.add(point_id)
        for key in required[1:]:
            value = point.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                errors.append(f"{prefix}.{key} must be a finite number")
        if isinstance(point.get("longitudeDeg"), (int, float)) and not isinstance(point.get("longitudeDeg"), bool):
            if not -180 <= float(point["longitudeDeg"]) <= 180:
                errors.append(f"{prefix}.longitudeDeg outside [-180, 180]")
        if isinstance(point.get("latitudeDeg"), (int, float)) and not isinstance(point.get("latitudeDeg"), bool):
            if not -90 <= float(point["latitudeDeg"]) <= 90:
                errors.append(f"{prefix}.latitudeDeg outside [-90, 90]")
        if isinstance(point.get("x"), (int, float)) and not isinstance(point.get("x"), bool):
            if not VIEWBOX[0] <= float(point["x"]) <= VIEWBOX[2]:
                errors.append(f"{prefix}.x outside SVG viewBox")
        if isinstance(point.get("y"), (int, float)) and not isinstance(point.get("y"), bool):
            if not VIEWBOX[1] <= float(point["y"]) <= VIEWBOX[3]:
                errors.append(f"{prefix}.y outside SVG viewBox")
    if errors:
        message = "Control-point validation failed:\n" + "\n".join(f"- {error}" for error in errors)
        raise ValueError(message)
    return {"status": "PASS", "pointCount": len(points), "errorCount": 0, "errors": []}


def fit_affine(projected: np.ndarray, visual: np.ndarray) -> dict[str, Any]:
    """Fit V = A P + t, with centered/scaled conditioning."""
    origin = projected.mean(axis=0)
    scale = float(np.max(np.ptp(projected, axis=0)))
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("Projected control points have no usable spatial extent")
    normalized = (projected - origin) / scale
    design = np.column_stack([normalized, np.ones(len(normalized))])
    coefficients, _, rank, singular_values = np.linalg.lstsq(design, visual, rcond=None)
    predicted = design @ coefficients
    residual = predicted - visual
    matrix = coefficients[:2, :].T / scale
    translation = coefficients[2, :] - matrix @ origin
    homogeneous = [
        [float(matrix[0, 0]), float(matrix[0, 1]), float(translation[0])],
        [float(matrix[1, 0]), float(matrix[1, 1]), float(translation[1])],
        [0.0, 0.0, 1.0],
    ]
    return {
        "matrix": homogeneous,
        "conditioning": {
            "normalizationOriginP": [float(x) for x in origin],
            "normalizationScaleP": scale,
            "designMatrixRank": int(rank),
            "singularValues": [float(x) for x in singular_values],
        },
        "predicted": predicted,
        "residual": residual,
    }


def fit_axis_aligned(projected: np.ndarray, visual: np.ndarray) -> dict[str, Any]:
    """Fit Vx=sx*Px+tx and Vy=sy*Py+ty for an interpretable scale/translation."""
    params: list[tuple[float, float]] = []
    predicted = np.zeros_like(visual)
    for axis in range(2):
        design = np.column_stack([projected[:, axis], np.ones(len(projected))])
        coeff, _, _, _ = np.linalg.lstsq(design, visual[:, axis], rcond=None)
        params.append((float(coeff[0]), float(coeff[1])))
        predicted[:, axis] = design @ coeff
    residual = predicted - visual
    return {
        "scaleX": params[0][0],
        "scaleY": params[1][0],
        "translationX": params[0][1],
        "translationY": params[1][1],
        "predicted": predicted,
        "residual": residual,
    }


def metric(residual: np.ndarray) -> dict[str, float]:
    errors = np.linalg.norm(residual, axis=1)
    return {
        "rmsePx": float(math.sqrt(np.mean(errors**2))),
        "meanPx": float(np.mean(errors)),
        "maxPx": float(np.max(errors)),
        "p95Px": float(np.percentile(errors, 95)),
    }


def point_reports(points: list[dict[str, Any]], projected: np.ndarray, fit: dict[str, Any]) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for index, point in enumerate(points):
        predicted = fit["predicted"][index]
        residual = fit["residual"][index]
        reports.append(
            {
                "id": point["id"],
                "name": point.get("name", ""),
                "role": point.get("role", ""),
                "longitudeDeg": as_float(point, "longitudeDeg"),
                "latitudeDeg": as_float(point, "latitudeDeg"),
                "projectedP": [float(x) for x in projected[index]],
                "pickedV": [as_float(point, "x"), as_float(point, "y")],
                "fittedV": [float(predicted[0]), float(predicted[1])],
                "deltaPx": [float(residual[0]), float(residual[1])],
                "errorPx": float(np.linalg.norm(residual)),
            }
        )
    return reports


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("assets/map/metadata/control-points.json"))
    parser.add_argument("--output", type=Path, default=Path("assets/map/metadata/spatial_bridge.json"))
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    raw_points = payload.get("controlPoints", [])
    if not isinstance(raw_points, list) or not raw_points:
        raise ValueError("control-points.json has no controlPoints")
    data_quality = validate_control_points(payload, raw_points)

    main_points = [point for point in raw_points if not is_inset(point)]
    inset_points = [point for point in raw_points if is_inset(point)]
    if len(main_points) < 3:
        raise ValueError("At least 3 non-inset points are required for an affine fit")

    projection = CRS.from_proj4(LCC_PROJ4)
    transformer = Transformer.from_crs(CRS.from_epsg(4326), projection, always_xy=True)

    def project(points: list[dict[str, Any]]) -> np.ndarray:
        x, y = transformer.transform(
            [as_float(point, "longitudeDeg") for point in points],
            [as_float(point, "latitudeDeg") for point in points],
        )
        return np.column_stack([x, y]).astype(float)

    projected_main = project(main_points)
    visual_main = np.array([[as_float(point, "x"), as_float(point, "y")] for point in main_points], dtype=float)
    affine = fit_affine(projected_main, visual_main)
    axis = fit_axis_aligned(projected_main, visual_main)
    affine_metrics = metric(affine["residual"])
    axis_metrics = metric(axis["residual"])

    reports = point_reports(main_points, projected_main, affine)
    print("SpatialBridge calibration")
    print(f"Input: {args.input}")
    print(f"Control points: {len(raw_points)} total; {len(main_points)} main; {len(inset_points)} inset")
    print(f"LCC: {LCC_PROJ4}")
    print("\nMain affine matrix P -> V:")
    for row in affine["matrix"]:
        print("  " + "  ".join(f"{value:.12g}" for value in row))
    print(
        "Axis-aligned parameters: "
        f"scaleX={axis['scaleX']:.12g}, scaleY={axis['scaleY']:.12g}, "
        f"Tx={axis['translationX']:.6f}, Ty={axis['translationY']:.6f}"
    )
    print("\nPer-point affine residuals:")
    for report in reports:
        print(
            f"  {report['id']:<16} "
            f"picked=({report['pickedV'][0]:.4f}, {report['pickedV'][1]:.4f}) "
            f"fitted=({report['fittedV'][0]:.4f}, {report['fittedV'][1]:.4f}) "
            f"delta=({report['deltaPx'][0]:+.4f}, {report['deltaPx'][1]:+.4f}) "
            f"error={report['errorPx']:.4f}px"
        )
    print(
        "\nMain affine error: "
        f"RMSE={affine_metrics['rmsePx']:.4f}px, "
        f"mean={affine_metrics['meanPx']:.4f}px, "
        f"p95={affine_metrics['p95Px']:.4f}px, "
        f"max={affine_metrics['maxPx']:.4f}px"
    )
    if affine_metrics["rmsePx"] > 15:
        print("WARNING: RMSE exceeds 15 px; projection parameters or control points may need review.", file=sys.stderr)

    inset_result: dict[str, Any]
    if len(inset_points) < 3:
        inset_result = {
            "status": "INSUFFICIENT_CONTROL_POINTS",
            "count": len(inset_points),
            "pointIds": [point["id"] for point in inset_points],
            "requiredMinimumForIndependentAffine": 3,
            "warning": "No independent inset translation was fitted; do not treat the single inset point as a solved transform.",
        }
        print(
            f"\nSouth China Sea inset: {len(inset_points)} point(s); independent transform not fitted "
            "(minimum 3 required)."
        )
    else:
        projected_inset = project(inset_points)
        visual_inset = np.array([[as_float(point, "x"), as_float(point, "y")] for point in inset_points], dtype=float)
        inset_fit = fit_affine(projected_inset, visual_inset)
        inset_result = {
            "status": "FITTED",
            "count": len(inset_points),
            "pointIds": [point["id"] for point in inset_points],
            "affine": {"matrix": inset_fit["matrix"], "metrics": metric(inset_fit["residual"])},
            "points": point_reports(inset_points, projected_inset, inset_fit),
        }
        print(f"\nSouth China Sea inset affine error: {inset_result['affine']['metrics']}")

    output = {
        "schemaVersion": "1.0",
        "status": "CALIBRATED_MAIN_INSET_PENDING" if inset_result["status"] != "FITTED" else "CALIBRATED",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "controlPointsFile": str(args.input).replace("\\", "/"),
        "controlPointsSha256": sha256_file(args.input),
        "visualSource": payload.get("visualSource"),
        "visualSourceSha256": payload.get("visualSourceSha256"),
        "dataQuality": data_quality,
        "coordinateDomains": {
            "G": {"name": "Geographic", "datum": "WGS84", "epsg": 4326, "units": "degrees"},
            "P": {"name": "China LCC display projection", "proj4": LCC_PROJ4, "units": "metres"},
            "V": {"name": "Official SVG visual coordinates", "viewBox": VIEWBOX, "units": "SVG user units"},
        },
        "mainMap": {
            "pointCount": len(main_points),
            "pointIds": [point["id"] for point in main_points],
            "fitModel": "full_affine_P_to_V",
            "affine": {"matrix": affine["matrix"], "metrics": affine_metrics, "conditioning": affine["conditioning"]},
            "axisAligned": {"scaleX": axis["scaleX"], "scaleY": axis["scaleY"], "Tx": axis["translationX"], "Ty": axis["translationY"], "metrics": axis_metrics},
            "points": reports,
        },
        "southSeaInset": inset_result,
        "policy": {
            "officialSvgUnmodified": True,
            "controlPointsNotDropped": True,
            "crsNotAssignedToEps": True,
            "dynamicLayersMustUseBridge": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
