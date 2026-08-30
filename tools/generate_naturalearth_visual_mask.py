"""Rasterize Natural Earth China geometry into a visual-only project mask."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

RAD = math.pi / 180
EARTH_RADIUS = 6378137.0
VIEW_W, VIEW_H = 3025.3333, 2137.3333
BRIDGE = ((0.0005049096535585887, 0.000022454384736449136, 1361.601054864795),
          (0.000025236110567069284, -0.0005152163553260364, 3246.205083005489))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def to_v(lon: float, lat: float) -> tuple[float, float]:
    p1, p2 = 25 * RAD, 47 * RAD
    lon0 = 105 * RAD
    n = math.log(math.cos(p1) / math.cos(p2)) / math.log(math.tan(math.pi / 4 + p2 / 2) / math.tan(math.pi / 4 + p1 / 2))
    f = math.cos(p1) * math.pow(math.tan(math.pi / 4 + p1 / 2), n) / n
    rho0 = f
    phi = lat * RAD
    rho = f / math.pow(math.tan(math.pi / 4 + phi / 2), n)
    theta = n * (lon * RAD - lon0)
    px = rho * math.sin(theta) * EARTH_RADIUS
    py = (rho0 - rho * math.cos(theta)) * EARTH_RADIUS
    return (BRIDGE[0][0] * px + BRIDGE[0][1] * py + BRIDGE[0][2],
            BRIDGE[1][0] * px + BRIDGE[1][1] * py + BRIDGE[1][2])


def draw_polygon(draw: ImageDraw.ImageDraw, coords, scale: float, fill: int) -> None:
    points = []
    for lon, lat in coords:
        x, y = to_v(float(lon), float(lat))
        points.append((round(x * scale), round(y * scale)))
    if len(points) >= 3:
        draw.polygon(points, fill=fill)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=Path("assets/map/source/ne_10m_admin_0_countries.geojson"))
    ap.add_argument("--output", type=Path, default=Path("assets/map/raster/ne-china-visual-mask.png"))
    ap.add_argument("--metadata", type=Path, default=Path("assets/map/metadata/ne-china-visual-mask.json"))
    ap.add_argument("--diagnostic", type=Path, default=Path("docs/screenshots/ne-china-visual-mask-bw.png"))
    args = ap.parse_args()
    source = json.loads(args.source.read_text(encoding="utf-8"))
    features = [f for f in source["features"] if f.get("properties", {}).get("ADMIN") == "China"]
    if not features:
        raise SystemExit("Natural Earth China feature not found")
    scale = 0.5
    w, h = round(VIEW_W * scale), round(VIEW_H * scale)
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    polygon_count = 0
    for feature in features:
        geometry = feature["geometry"]
        for polygon in geometry.get("coordinates", []):
            if not polygon:
                continue
            draw_polygon(draw, polygon[0], scale, 230)
            polygon_count += 1
            for hole in polygon[1:]:
                draw_polygon(draw, hole, scale, 0)
    mask = mask.filter(ImageFilter.GaussianBlur(0.8))
    full = mask.resize((round(VIEW_W), round(VIEW_H)), Image.Resampling.BICUBIC)
    rgba = Image.merge("RGBA", (Image.new("L", full.size, 255),) * 3 + (full,))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.diagnostic.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(args.output, "PNG", optimize=True)
    full.point(lambda x: 255 if x > 30 else 0).save(args.diagnostic, "PNG", optimize=True)
    meta = {
        "schemaVersion": "1.0",
        "status": "APPROXIMATE_VISUAL_MASK",
        "label": "APPROXIMATE_VISUAL_MASK - NOT A GEOGRAPHIC SOURCE",
        "purpose": "Visual clipping for the solar land-color layer only; never a replacement for official map geometry.",
        "sourceFile": str(args.source).replace("\\", "/"),
        "sourceSha256": sha256(args.source),
        "sourceDataset": "Natural Earth 10m Admin 0 Countries",
        "sourceFeature": "ADMIN=China",
        "outputFile": str(args.output).replace("\\", "/"),
        "outputSha256": sha256(args.output),
        "outputDimensions": {"width": full.width, "height": full.height},
        "viewBox": "0 0 3025.3333 2137.3333",
        "projection": "WGS84 geographic -> China LCC -> existing SpatialBridge affine -> V",
        "polygonCount": polygon_count,
        "southSeaInset": {"included": False, "reason": "South Sea inset remains an independent official layer."},
        "knownLimitations": [
            "Natural Earth political geometry is approximate and not an official Chinese map source.",
            "This layer must not define borders, province lines, city positions, or map facts.",
            "Use only for low-contrast visual color clipping beneath the unchanged official SVG.",
        ],
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
    args.metadata.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "sha256": meta["outputSha256"], "polygons": polygon_count}, ensure_ascii=False))


if __name__ == "__main__":
    main()
