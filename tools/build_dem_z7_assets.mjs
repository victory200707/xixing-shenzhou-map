import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import { PNG } from 'pngjs';

const root = 'C:/Users/HUAWEI/Documents/ChatGPT/mask';
const dir = `${root}/assets/terrain/source/terrarium-z7`;
const tileSize = 256, zoom = 7, xMin = 88, xMax = 113, yMin = 41, yMax = 63;
const mosaicW = (xMax - xMin + 1) * tileSize, mosaicH = (yMax - yMin + 1) * tileSize;
const mosaic = new Float32Array(mosaicW * mosaicH);
for (let tx = xMin; tx <= xMax; tx += 1) for (let ty = yMin; ty <= yMax; ty += 1) {
  const bytes = await fs.readFile(`${dir}/z7-x${tx}-y${ty}.png`);
  const tile = PNG.sync.read(bytes);
  for (let y = 0; y < tileSize; y += 1) for (let x = 0; x < tileSize; x += 1) {
    const q = (y * tileSize + x) * 4;
    mosaic[((ty - yMin) * tileSize + y) * mosaicW + (tx - xMin) * tileSize + x] =
      tile.data[q] * 256 + tile.data[q + 1] + tile.data[q + 2] / 256 - 32768;
  }
}

const viewW = 3025.3333, viewH = 2137.3333, outW = 1513, outH = 1069;
const RAD = Math.PI / 180, DEG = 180 / Math.PI, earth = 6378137;
const bridge = { a: 0.0005049096535585887, b: 0.000022454384736449136, tx: 1361.601054864795, c: 0.000025236110567069284, d: -0.0005152163553260364, ty: 3246.205083005489 };
const phi1 = 25 * RAD, phi2 = 47 * RAD, lon0 = 105 * RAD;
const n = Math.log(Math.cos(phi1) / Math.cos(phi2)) / Math.log(Math.tan(Math.PI / 4 + phi2 / 2) / Math.tan(Math.PI / 4 + phi1 / 2));
const f = Math.cos(phi1) * Math.pow(Math.tan(Math.PI / 4 + phi1 / 2), n) / n, det = bridge.a * bridge.d - bridge.b * bridge.c;
const world = tileSize * (2 ** zoom), sample = (x, y) => mosaic[Math.max(0, Math.min(mosaicH - 1, y)) * mosaicW + Math.max(0, Math.min(mosaicW - 1, x))];
const hill = new PNG({ width: outW, height: outH }), normal = new PNG({ width: outW, height: outH });
const sunE = Math.sin(315 * RAD), sunN = Math.cos(315 * RAD), sunU = Math.sin(45 * RAD), exaggeration = 0.00135;

for (let row = 0; row < outH; row += 1) {
  const vy = (row + 0.5) * viewH / outH;
  for (let col = 0; col < outW; col += 1) {
    const vx = (col + 0.5) * viewW / outW, dx = vx - bridge.tx, dy = vy - bridge.ty;
    const px = (bridge.d * dx - bridge.b * dy) / det, py = (-bridge.c * dx + bridge.a * dy) / det;
    const rho = Math.hypot(px / earth, f - py / earth), theta = Math.atan2(px / earth, f - py / earth);
    const lon = (lon0 + theta / n) / RAD, lat = (2 * Math.atan(Math.pow(f / Math.max(rho, 1e-12), 1 / n)) - Math.PI / 2) / RAD;
    const gx = (lon + 180) / 360 * world, gy = (1 - Math.asinh(Math.tan(Math.max(-85.051, Math.min(85.051, lat)) * RAD)) / Math.PI) / 2 * world;
    const mx = Math.max(1, Math.min(mosaicW - 2, gx - xMin * tileSize)), my = Math.max(1, Math.min(mosaicH - 2, gy - yMin * tileSize));
    const ix = Math.floor(mx), iy = Math.floor(my), eL = sample(ix - 1, iy), eR = sample(ix + 1, iy), eU = sample(ix, iy - 1), eD = sample(ix, iy + 1);
    const east = -(eR - eL) * 0.5 * exaggeration, north = (eD - eU) * 0.5 * exaggeration, up = 1, len = Math.hypot(east, north, up);
    const nx = east / len, ny = north / len, nz = up / len, shade = Math.max(0, nx * sunE + ny * sunN + nz * sunU);
    const q = (row * outW + col) * 4, tone = Math.max(0, Math.min(255, Math.round((0.24 + 0.76 * shade) * 255)));
    hill.data[q] = tone; hill.data[q + 1] = tone; hill.data[q + 2] = tone; hill.data[q + 3] = 255;
    normal.data[q] = Math.round((nx * 0.5 + 0.5) * 255); normal.data[q + 1] = Math.round((ny * 0.5 + 0.5) * 255); normal.data[q + 2] = Math.round(nz * 255); normal.data[q + 3] = 255;
  }
}

const hillPath = `${root}/assets/map/raster/dem-hillshade-z7-v.png`, normalPath = `${root}/assets/map/raster/dem-normal-z7-v.png`;
await fs.writeFile(hillPath, PNG.sync.write(hill)); await fs.writeFile(normalPath, PNG.sync.write(normal));
const sha = async (p) => crypto.createHash('sha256').update(await fs.readFile(p)).digest('hex').toUpperCase();
const metadata = { schemaVersion: '1.0', status: 'APPROXIMATE_DEM_MULTISCALE_VISUAL_ASSET', source: { provider: 'AWS elevation-tiles-prod Terrarium tiles', zoom, tileCount: (xMax - xMin + 1) * (yMax - yMin + 1), xRange: [xMin, xMax], yRange: [yMin, yMax], encoding: 'Mapzen Terrarium RGB elevation' }, outputViewBox: `0 0 ${viewW} ${viewH}`, hillshade: { file: 'assets/map/raster/dem-hillshade-z7-v.png', sha256: await sha(hillPath), dimensions: { width: outW, height: outH } }, normal: { file: 'assets/map/raster/dem-normal-z7-v.png', sha256: await sha(normalPath), dimensions: { width: outW, height: outH }, encoding: 'RGB ENU normal from raw elevation', verticalExaggeration: exaggeration }, projectionChain: ['WGS84', 'inverse LCC', 'inverse SpatialBridge', 'SVG V sampling'], limitation: 'Visual terrain asset only; not a geographic boundary or quantitative elevation source.' };
await fs.writeFile(`${root}/assets/map/metadata/dem-z7-v.json`, JSON.stringify(metadata, null, 2) + '\n');
console.log(JSON.stringify({ hillshade: metadata.hillshade, normal: metadata.normal }));
