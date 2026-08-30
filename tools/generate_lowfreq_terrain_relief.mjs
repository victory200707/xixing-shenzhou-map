import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import { PNG } from 'pngjs';

const inputPath = 'assets/map/raster/terrain-registered.png';
const outputPath = 'assets/map/raster/terrain-relief-lowfreq-v.png';
const metadataPath = 'assets/map/metadata/terrain-relief-lowfreq-v.json';
// Strong reduction removes labels, rivers and linework while retaining only
// broad terrain-light variations suitable for a restrained visual layer.
const factor = 15;

const sha256 = (buffer) => crypto.createHash('sha256').update(buffer).digest('hex').toUpperCase();
const source = await fs.readFile(inputPath);
const input = PNG.sync.read(source);
const width = Math.ceil(input.width / factor);
const height = Math.ceil(input.height / factor);
const values = new Float32Array(width * height);

for (let y = 0; y < height; y += 1) {
  for (let x = 0; x < width; x += 1) {
    let sum = 0;
    let count = 0;
    for (let sy = y * factor; sy < Math.min(input.height, (y + 1) * factor); sy += 1) {
      for (let sx = x * factor; sx < Math.min(input.width, (x + 1) * factor); sx += 1) {
        const i = (sy * input.width + sx) * 4;
        sum += input.data[i] * 0.2126 + input.data[i + 1] * 0.7152 + input.data[i + 2] * 0.0722;
        count += 1;
      }
    }
    values[y * width + x] = sum / count;
  }
}

// A second low-pass pass removes the original map's labels and thin linework.
const smoothed = new Float32Array(values.length);
for (let y = 0; y < height; y += 1) {
  for (let x = 0; x < width; x += 1) {
    let sum = 0;
    let count = 0;
    for (let dy = -5; dy <= 5; dy += 1) {
      for (let dx = -5; dx <= 5; dx += 1) {
        const sx = x + dx;
        const sy = y + dy;
        if (sx < 0 || sy < 0 || sx >= width || sy >= height) continue;
        sum += values[sy * width + sx];
        count += 1;
      }
    }
    smoothed[y * width + x] = sum / count;
  }
}

const sorted = [...smoothed].sort((a, b) => a - b);
const lo = sorted[Math.floor(sorted.length * 0.14)];
const hi = sorted[Math.floor(sorted.length * 0.86)];
const output = new PNG({ width, height });
for (let i = 0; i < smoothed.length; i += 1) {
  const t = Math.max(0, Math.min(1, (smoothed[i] - lo) / Math.max(1, hi - lo)));
  // Blue-gray luminance only: no source colors, text or topographic symbols.
  output.data[i * 4] = Math.round(17 + 54 * t);
  output.data[i * 4 + 1] = Math.round(42 + 78 * t);
  output.data[i * 4 + 2] = Math.round(74 + 106 * t);
  output.data[i * 4 + 3] = 255;
}
const encoded = PNG.sync.write(output, { colorType: 6, inputColorType: 6 });
await fs.writeFile(outputPath, encoded);
const metadata = {
  schemaVersion: '1.0',
  status: 'APPROXIMATE_MASKED_VISUAL_TEXTURE',
  label: 'VISUAL LOW-FREQUENCY RELIEF - NOT DEM OR GEOGRAPHIC FACT',
  sourceFile: inputPath,
  sourceSha256: sha256(source),
  outputFile: outputPath,
  outputSha256: sha256(encoded),
  sourceDimensions: { width: input.width, height: input.height },
  outputDimensions: { width, height },
  outputViewBox: '0 0 3025.3333 2137.3333',
  processing: [
    'five-pixel block average',
    'five-by-five low-pass smoothing on the reduced image',
    'percentile normalization and blue-gray luminance remap',
    'no boundary, river, contour, label, or elevation value is retained as map data',
    'must be clipped by approximate visual masks before rendering',
  ],
  knownLimitations: [
    'Derived from a registered visual terrain map, not a DEM.',
    'Does not encode reliable height, slope, river, or boundary information.',
    'Not valid for geography, analysis, or formal map publication.',
  ],
  generatedAt: new Date().toISOString(),
};
await fs.writeFile(metadataPath, `${JSON.stringify(metadata, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({ outputPath, sha256: metadata.outputSha256, dimensions: metadata.outputDimensions }));
