import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import { PNG } from 'pngjs';

const sourcePath = 'assets/map/source/ne_10m_admin_0_countries.geojson';
const outputPath = 'assets/map/raster/ne-taiwan-visual-mask.png';
const metadataPath = 'assets/map/metadata/ne-taiwan-visual-mask.json';
const WIDTH = 3025;
const HEIGHT = 2137;
const RAD = Math.PI / 180;
const EARTH_RADIUS = 6378137;
const BRIDGE = {
  a: 0.0005049096535585887, b: 0.000022454384736449136, tx: 1361.601054864795,
  c: 0.000025236110567069284, d: -0.0005152163553260364, ty: 3246.205083005489,
};

function sha256(buffer) {
  return crypto.createHash('sha256').update(buffer).digest('hex').toUpperCase();
}

function toV(lon, lat) {
  const phi1 = 25 * RAD;
  const phi2 = 47 * RAD;
  const lon0 = 105 * RAD;
  const n = Math.log(Math.cos(phi1) / Math.cos(phi2)) /
    Math.log(Math.tan(Math.PI / 4 + phi2 / 2) / Math.tan(Math.PI / 4 + phi1 / 2));
  const f = Math.cos(phi1) * Math.pow(Math.tan(Math.PI / 4 + phi1 / 2), n) / n;
  const phi = lat * RAD;
  const rho = f / Math.pow(Math.tan(Math.PI / 4 + phi / 2), n);
  const theta = n * (lon * RAD - lon0);
  const px = rho * Math.sin(theta) * EARTH_RADIUS;
  const py = (f - rho * Math.cos(theta)) * EARTH_RADIUS;
  return [BRIDGE.a * px + BRIDGE.b * py + BRIDGE.tx, BRIDGE.c * px + BRIDGE.d * py + BRIDGE.ty];
}

function inside(point, ring) {
  let result = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    if ((yi > point[1]) !== (yj > point[1]) && point[0] < ((xj - xi) * (point[1] - yi)) / (yj - yi) + xi) result = !result;
  }
  return result;
}

const source = await fs.readFile(sourcePath);
const geojson = JSON.parse(source.toString('utf8'));
const feature = geojson.features.find((item) => item.properties?.ADMIN === 'Taiwan');
if (!feature) throw new Error('Natural Earth Taiwan feature not found');

const polygons = feature.geometry.coordinates.map((polygon) => polygon.map((ring) => ring.map(([lon, lat]) => toV(lon, lat))));
const png = new PNG({ width: WIDTH, height: HEIGHT });
const vertices = polygons.flat(2);
const minX = Math.max(0, Math.floor(Math.min(...vertices.map(([x]) => x)) - 2));
const maxX = Math.min(WIDTH - 1, Math.ceil(Math.max(...vertices.map(([x]) => x)) + 2));
const minY = Math.max(0, Math.floor(Math.min(...vertices.map(([, y]) => y)) - 2));
const maxY = Math.min(HEIGHT - 1, Math.ceil(Math.max(...vertices.map(([, y]) => y)) + 2));
for (let y = minY; y <= maxY; y += 1) {
  for (let x = minX; x <= maxX; x += 1) {
    const inLand = polygons.some((polygon) => inside([x + 0.5, y + 0.5], polygon[0]) && !polygon.slice(1).some((hole) => inside([x + 0.5, y + 0.5], hole)));
    if (!inLand) continue;
    const i = (y * WIDTH + x) * 4;
    png.data[i] = 255;
    png.data[i + 1] = 255;
    png.data[i + 2] = 255;
    png.data[i + 3] = 230;
  }
}
const output = PNG.sync.write(png, { colorType: 6, inputColorType: 6 });
await fs.writeFile(outputPath, output);
const metadata = {
  schemaVersion: '1.0',
  status: 'APPROXIMATE_VISUAL_MASK',
  label: 'APPROXIMATE_VISUAL_MASK - NOT A GEOGRAPHIC SOURCE',
  purpose: 'Visual clipping for the Taiwan land-color layer only; never a replacement for official map geometry.',
  sourceFile: sourcePath,
  sourceSha256: sha256(source),
  sourceDataset: 'Natural Earth 10m Admin 0 Countries',
  sourceFeature: 'ADMIN=Taiwan',
  outputFile: outputPath,
  outputSha256: sha256(output),
  outputDimensions: { width: WIDTH, height: HEIGHT },
  viewBox: '0 0 3025.3333 2137.3333',
  projection: 'WGS84 geographic -> China LCC -> existing SpatialBridge affine -> V',
  southSeaInset: { included: false, reason: 'South Sea inset remains an independent official layer.' },
  knownLimitations: [
    'Natural Earth geometry is approximate and is not an official Chinese map source.',
    'This layer must not define borders, city positions, or map facts.',
    'Use only beneath the unchanged official SVG for visual color and texture clipping.',
  ],
  generatedAt: new Date().toISOString(),
};
await fs.writeFile(metadataPath, `${JSON.stringify(metadata, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({ outputPath, outputSha256: metadata.outputSha256, dimensions: metadata.outputDimensions }));
