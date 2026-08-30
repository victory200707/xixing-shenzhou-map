// Browser solar light field. This is a visual layer only: it does not encode
// elevation and it never changes the official SVG geometry.
const RAD = Math.PI / 180;
const DEG = 180 / Math.PI;
const EARTH_RADIUS = 6378137;
const VIEWBOX = { width: 3025.3333, height: 2137.3333 };
const BRIDGE = {
  a: 0.0005049096535585887, b: 0.000022454384736449136, tx: 1361.601054864795,
  c: 0.000025236110567069284, d: -0.0005152163553260364, ty: 3246.205083005489,
};
const LIGHT = {
  // TECHNICAL SOLAR FIELD PREVIEW — NOT FORMAL LAND MASK.
  nightOpacity: 0.16,
  twilightOpacity: 0.14,
  daylightOpacity: 0.12,
  warmBandOpacity: 0.16,
  terminatorOpacity: 0.22,
};

let landMaskImage = null;
let landMaskLoading = false;
const landMaskReadyCallbacks = [];
let terrainTextureImage = null;
let terrainTextureLoading = false;
let terrainTextureCache = null;
const terrainTextureReadyCallbacks = [];
let terrainElevationImage = null;
let terrainElevationLoading = false;
const terrainElevationReadyCallbacks = [];
let terrainNormalImage = null;
let terrainNormalLoading = false;
const terrainNormalReadyCallbacks = [];
let officialBodyImage = null;
let officialBodyLoading = false;
let officialBodyMaskCache = null;
let lineworkFillMaskCache = null;

function loadLandMask(canvas, imageRect, date, onReady = () => renderSolarField(canvas, imageRect, date)) {
  if (landMaskImage) return;
  landMaskReadyCallbacks.push(onReady);
  if (landMaskLoading) return;
  landMaskLoading = true;
  const image = new Image();
  image.onload = () => {
    landMaskImage = image;
    landMaskLoading = false;
    const callbacks = landMaskReadyCallbacks.splice(0);
    callbacks.forEach((callback) => requestAnimationFrame(callback));
  };
  image.onerror = () => { landMaskLoading = false; landMaskReadyCallbacks.length = 0; };
  // Use the exact linework currently displayed by the page. The derived
  // raster mask is visual-only and is generated in the same SVG V frame.
  image.src = 'assets/map/svg/presentation-coastline.svg?v=phase1c51-rollback';
}

// Build a display-only fill from the exact linework used by the page. The
// source is rasterized in SVG V coordinates, tiny antialiasing gaps are closed,
// then all sufficiently large enclosed regions are unioned. No boundary is
// redrawn and no second geographic dataset participates in this mask.
function createLineworkFillMask(image) {
  if (!image) return null;
  const w = Math.round(VIEWBOX.width * 0.125);
  const h = Math.round(VIEWBOX.height * 0.125);
  const key = `${w}:${h}`;
  if (lineworkFillMaskCache?.key === key) return lineworkFillMaskCache.canvas;

  const source = document.createElement('canvas');
  source.width = w; source.height = h;
  const sourceCtx = source.getContext('2d', { willReadFrequently: true });
  sourceCtx.drawImage(image, 0, 0, w, h);
  const rgba = sourceCtx.getImageData(0, 0, w, h).data;
  const binary = new Uint8Array(w * h);
  for (let i = 0; i < binary.length; i += 1) binary[i] = rgba[i * 4 + 3] > 34 ? 1 : 0;

  // Two 3x3 close passes bridge only sub-pixel raster breaks. The operation is
  // intentionally small so province/coastline geometry is not materially
  // thickened.
  const dilate = (input) => {
    const out = new Uint8Array(input.length);
    for (let y = 0; y < h; y += 1) for (let x = 0; x < w; x += 1) {
      let hit = 0;
      for (let dy = -1; dy <= 1 && !hit; dy += 1) for (let dx = -1; dx <= 1; dx += 1) {
        const nx = x + dx, ny = y + dy;
        if (nx >= 0 && nx < w && ny >= 0 && ny < h && input[ny * w + nx]) { hit = 1; break; }
      }
      out[y * w + x] = hit;
    }
    return out;
  };
  const erode = (input) => {
    const out = new Uint8Array(input.length);
    for (let y = 0; y < h; y += 1) for (let x = 0; x < w; x += 1) {
      let solid = 1;
      for (let dy = -1; dy <= 1 && solid; dy += 1) for (let dx = -1; dx <= 1; dx += 1) {
        const nx = x + dx, ny = y + dy;
        if (nx < 0 || nx >= w || ny < 0 || ny >= h || !input[ny * w + nx]) { solid = 0; break; }
      }
      out[y * w + x] = solid;
    }
    return out;
  };
  const closed = erode(dilate(dilate(binary)));

  // Flood-fill the outside of the linework barrier. The lower-right South Sea
  // inset is explicitly excluded from the mainland visual mask.
  const outside = new Uint8Array(w * h);
  const queueX = new Int32Array(w * h);
  const queueY = new Int32Array(w * h);
  let head = 0, tail = 0;
  const enqueue = (x, y) => {
    if (x < 0 || x >= w || y < 0 || y >= h) return;
    const index = y * w + x;
    if (outside[index] || closed[index]) return;
    outside[index] = 1; queueX[tail] = x; queueY[tail] = y; tail += 1;
  };
  for (let x = 0; x < w; x += 1) { enqueue(x, 0); enqueue(x, h - 1); }
  for (let y = 0; y < h; y += 1) { enqueue(0, y); enqueue(w - 1, y); }
  while (head < tail) {
    const x = queueX[head], y = queueY[head]; head += 1;
    enqueue(x - 1, y); enqueue(x + 1, y); enqueue(x, y - 1); enqueue(x, y + 1);
  }

  const excludedInset = (x, y) => x > w * 0.78 && y > h * 0.60;
  const seen = new Uint8Array(w * h);
  const componentX = new Int32Array(w * h);
  const componentY = new Int32Array(w * h);
  const land = new Uint8Array(w * h);
  const minComponent = Math.max(18, Math.round(w * h * 0.000006));
  for (let y = 0; y < h; y += 1) for (let x = 0; x < w; x += 1) {
    const start = y * w + x;
    if (seen[start] || closed[start] || outside[start] || excludedInset(x, y)) continue;
    let cHead = 0, cTail = 0;
    componentX[cTail] = x; componentY[cTail] = y; cTail += 1; seen[start] = 1;
    while (cHead < cTail) {
      const cx = componentX[cHead], cy = componentY[cHead]; cHead += 1;
      const visit = (nx, ny) => {
        if (nx < 0 || nx >= w || ny < 0 || ny >= h || excludedInset(nx, ny)) return;
        const index = ny * w + nx;
        if (seen[index] || closed[index] || outside[index]) return;
        seen[index] = 1; componentX[cTail] = nx; componentY[cTail] = ny; cTail += 1;
      };
      visit(cx - 1, cy); visit(cx + 1, cy); visit(cx, cy - 1); visit(cx, cy + 1);
    }
    if (cTail >= minComponent) for (let i = 0; i < cTail; i += 1) land[componentY[i] * w + componentX[i]] = 1;
  }

  // Province/coast strokes are barriers for the outside flood only. They are
  // still inside the mainland and must remain covered so the official SVG can
  // redraw those lines above the color layer without dark gaps between regions.
  for (let y = 0; y < h; y += 1) for (let x = 0; x < w; x += 1) {
    if (!outside[y * w + x] && !excludedInset(x, y)) land[y * w + x] = 1;
  }

  // Keep the dominant connected mainland and explicit Hainan/Taiwan anchors.
  // A second pass prevents an earlier, smaller annotation loop from surviving
  // merely because a larger component was discovered later.
  const seenLand = new Uint8Array(land.length);
  const componentId = new Int32Array(land.length); componentId.fill(-1);
  const sizes = [], boxes = [];
  const qx = new Int32Array(land.length), qy = new Int32Array(land.length);
  let componentCount = 0;
  for (let y = 0; y < h; y += 1) for (let x = 0; x < w; x += 1) {
    const start = y * w + x;
    if (!land[start] || seenLand[start]) continue;
    const id = componentCount++;
    let head2 = 0, tail2 = 0, minX = x, maxX = x, minY = y, maxY = y;
    qx[tail2] = x; qy[tail2] = y; tail2 += 1; seenLand[start] = 1; componentId[start] = id;
    while (head2 < tail2) {
      const cx = qx[head2], cy = qy[head2]; head2 += 1;
      minX = Math.min(minX, cx); maxX = Math.max(maxX, cx); minY = Math.min(minY, cy); maxY = Math.max(maxY, cy);
      const visit = (nx, ny) => {
        if (nx < 0 || nx >= w || ny < 0 || ny >= h) return;
        const index = ny * w + nx;
        if (!land[index] || seenLand[index]) return;
        seenLand[index] = 1; componentId[index] = id; qx[tail2] = nx; qy[tail2] = ny; tail2 += 1;
      };
      visit(cx - 1, cy); visit(cx + 1, cy); visit(cx, cy - 1); visit(cx, cy + 1);
    }
    sizes[id] = tail2; boxes[id] = [minX, maxX, minY, maxY];
  }
  let largestId = -1;
  for (let id = 0; id < sizes.length; id += 1) if (largestId < 0 || sizes[id] > sizes[largestId]) largestId = id;
  const islandSeeds = [[1699.6476 * 0.125, 2011.121 * 0.125], [2271.1805 * 0.125, 1683.4906 * 0.125]];
  const keepIds = new Set([largestId]);
  for (let id = 0; id < boxes.length; id += 1) {
    const [minX, maxX, minY, maxY] = boxes[id];
    if (islandSeeds.some(([sx, sy]) => sx >= minX - 8 && sx <= maxX + 8 && sy >= minY - 8 && sy <= maxY + 8)) keepIds.add(id);
  }
  for (let i = 0; i < land.length; i += 1) land[i] = keepIds.has(componentId[i]) ? 1 : 0;

  // Keep the explicitly visible island interiors when their loops are small,
  // while never importing South Sea inset pixels into the mainland mask.
  const mask = document.createElement('canvas'); mask.width = w; mask.height = h;
  const maskCtx = mask.getContext('2d');
  const alpha = maskCtx.createImageData(w, h);
  for (let i = 0; i < land.length; i += 1) alpha.data[i * 4 + 3] = land[i] ? 232 : 0;
  maskCtx.putImageData(alpha, 0, 0);
  lineworkFillMaskCache = { key, canvas: mask };
  return mask;
}

function loadTerrainTexture(canvas, imageRect, date, onReady = () => renderSolarField(canvas, imageRect, date)) {
  if (terrainTextureImage) return;
  terrainTextureReadyCallbacks.push(onReady);
  if (terrainTextureLoading) return;
  terrainTextureLoading = true;
  const image = new Image();
  image.onload = () => {
    terrainTextureImage = image;
    terrainTextureLoading = false;
    const callbacks = terrainTextureReadyCallbacks.splice(0);
    callbacks.forEach((callback) => requestAnimationFrame(callback));
  };
  image.onerror = () => { terrainTextureLoading = false; terrainTextureReadyCallbacks.length = 0; };
  image.src = 'assets/map/raster/dem-hillshade-z7-art-v.png?v=phase1c51-rollback';
}

function loadTerrainElevation(canvas, imageRect, date, onReady = () => renderSolarField(canvas, imageRect, date)) {
  if (terrainElevationImage) return;
  terrainElevationReadyCallbacks.push(onReady);
  if (terrainElevationLoading) return;
  terrainElevationLoading = true;
  const image = new Image();
  image.onload = () => {
    terrainElevationImage = image;
    terrainElevationLoading = false;
    const callbacks = terrainElevationReadyCallbacks.splice(0);
    callbacks.forEach((callback) => requestAnimationFrame(callback));
  };
  image.onerror = () => { terrainElevationLoading = false; terrainElevationReadyCallbacks.length = 0; };
  image.src = 'assets/map/raster/dem-elevation-v.png?v=phase1c51-rollback';
}

function loadTerrainNormal(canvas, imageRect, date, onReady = () => renderSolarField(canvas, imageRect, date)) {
  if (terrainNormalImage) return;
  terrainNormalReadyCallbacks.push(onReady);
  if (terrainNormalLoading) return;
  terrainNormalLoading = true;
  const image = new Image();
  image.onload = () => {
    terrainNormalImage = image;
    terrainNormalLoading = false;
    const callbacks = terrainNormalReadyCallbacks.splice(0);
    callbacks.forEach((callback) => requestAnimationFrame(callback));
  };
  image.onerror = () => { terrainNormalLoading = false; terrainNormalReadyCallbacks.length = 0; };
  image.src = 'assets/map/raster/dem-normal-z7-v.png?v=phase1c51-rollback';
}

function loadOfficialBodyImage(canvas, imageRect, date) {
  if (officialBodyImage || officialBodyLoading) return;
  officialBodyLoading = true;
  // Build the mask from the exact body-fill path used by the current website
  // map. This keeps the visual clipping in the same V coordinate space as the
  // displayed coastline SVG, instead of aligning a second geographic dataset.
  fetch('assets/map/svg/presentation-map.svg?v=phase1c16', { cache: 'no-store' })
    .then((response) => response.text())
    .then((source) => {
      const doc = new DOMParser().parseFromString(source, 'image/svg+xml');
      const root = doc.documentElement;
      const path = root.querySelector('#path3');
      if (!path) throw new Error('presentation-map.svg does not contain #path3');
      const maskSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="${VIEWBOX.width}" height="${VIEWBOX.height}" viewBox="0 0 ${VIEWBOX.width} ${VIEWBOX.height}"><path d="${path.getAttribute('d')}" transform="${path.getAttribute('transform') || ''}" fill="#fff" fill-rule="evenodd"/></svg>`;
      const blobUrl = URL.createObjectURL(new Blob([maskSvg], { type: 'image/svg+xml' }));
      const image = new Image();
      image.onload = () => {
        URL.revokeObjectURL(blobUrl);
        officialBodyImage = image;
        officialBodyLoading = false;
        officialBodyMaskCache = null;
        requestAnimationFrame(() => renderSolarField(canvas, imageRect, date));
      };
      image.onerror = () => { URL.revokeObjectURL(blobUrl); officialBodyLoading = false; };
      image.src = blobUrl;
    })
    .catch(() => { officialBodyLoading = false; });
}

function createOfficialBodyMask(imageRect, scale, ox, oy) {
  if (!officialBodyImage) return null;
  const width = Math.max(1, Math.ceil(imageRect.width));
  const height = Math.max(1, Math.ceil(imageRect.height));
  const key = `${width}:${height}:${ox.toFixed(2)}:${oy.toFixed(2)}:${scale.toFixed(6)}`;
  if (officialBodyMaskCache?.key === key) return officialBodyMaskCache.canvas;
  const source = document.createElement('canvas');
  source.width = width;
  source.height = height;
  const sourceCtx = source.getContext('2d', { willReadFrequently: true });
  sourceCtx.clearRect(0, 0, width, height);
  sourceCtx.drawImage(officialBodyImage, ox, oy, VIEWBOX.width * scale, VIEWBOX.height * scale);
  const image = sourceCtx.getImageData(0, 0, width, height);
  let covered = 0;
  for (let i = 3; i < image.data.length; i += 4) if (image.data[i] > 12) covered += 1;
  // A valid body fill should occupy a substantial area of the displayed map.
  // If the source changes and becomes an outline-only path, fail closed and
  // let the explicit visual fallback remain in charge.
  const coverage = covered / (width * height);
  if (coverage < 0.08) return null;
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  canvas.getContext('2d').putImageData(image, 0, 0);
  officialBodyMaskCache = { key, canvas, coverage };
  return canvas;
}

function lccConstants() {
  const phi1 = 25 * RAD;
  const phi2 = 47 * RAD;
  const lon0 = 105 * RAD;
  const n = Math.log(Math.cos(phi1) / Math.cos(phi2)) /
    Math.log(Math.tan(Math.PI / 4 + phi2 / 2) / Math.tan(Math.PI / 4 + phi1 / 2));
  const f = Math.cos(phi1) * Math.pow(Math.tan(Math.PI / 4 + phi1 / 2), n) / n;
  return { n, f, rho0: f, lon0 };
}

function lcc(lon, lat) {
  const { n, f, rho0, lon0 } = lccConstants();
  const phi = lat * RAD;
  const rho = f / Math.pow(Math.tan(Math.PI / 4 + phi / 2), n);
  const theta = n * (lon * RAD - lon0);
  return { x: rho * Math.sin(theta) * EARTH_RADIUS, y: (rho0 - rho * Math.cos(theta)) * EARTH_RADIUS };
}

function toV(lon, lat) {
  const p = lcc(lon, lat);
  return { x: BRIDGE.a * p.x + BRIDGE.b * p.y + BRIDGE.tx, y: BRIDGE.c * p.x + BRIDGE.d * p.y + BRIDGE.ty };
}

function fromV(x, y) {
  const dx = x - BRIDGE.tx;
  const dy = y - BRIDGE.ty;
  const det = BRIDGE.a * BRIDGE.d - BRIDGE.b * BRIDGE.c;
  const px = (BRIDGE.d * dx - BRIDGE.b * dy) / det;
  const py = (-BRIDGE.c * dx + BRIDGE.a * dy) / det;
  const { n, f, rho0, lon0 } = lccConstants();
  const rho = Math.hypot(px / EARTH_RADIUS, rho0 - py / EARTH_RADIUS);
  if (!Number.isFinite(rho) || rho === 0) return null;
  const theta = Math.atan2(px / EARTH_RADIUS, rho0 - py / EARTH_RADIUS);
  const lon = lon0 + theta / n;
  const phi = 2 * Math.atan(Math.pow(f / rho, 1 / n)) - Math.PI / 2;
  return { longitude: lon * DEG, latitude: phi * DEG };
}

// NOAA low-order position, used for the dense visual field. Event readouts
// continue to use the audited SPA adapter in solar-spa.js.
function solarAltitude(date, lon, lat) {
  const day = (date.getTime() - Date.UTC(date.getUTCFullYear(), 0, 0)) / 86400000;
  const hour = date.getUTCHours() + date.getUTCMinutes() / 60 + date.getUTCSeconds() / 3600;
  const gamma = 2 * Math.PI / 365 * (day - 1 + (hour - 12) / 24);
  const decl = 0.006918 - 0.399912 * Math.cos(gamma) + 0.070257 * Math.sin(gamma) - 0.006758 * Math.cos(2 * gamma) + 0.000907 * Math.sin(2 * gamma) - 0.002697 * Math.cos(3 * gamma) + 0.00148 * Math.sin(3 * gamma);
  const eqTime = 229.18 * (0.000075 + 0.001868 * Math.cos(gamma) - 0.032077 * Math.sin(gamma) - 0.014615 * Math.cos(2 * gamma) - 0.040849 * Math.sin(2 * gamma));
  const minutes = date.getUTCHours() * 60 + date.getUTCMinutes() + date.getUTCSeconds() / 60;
  const hourAngle = ((minutes + eqTime + 4 * lon) / 4 - 180) * RAD;
  return Math.asin(Math.sin(lat * RAD) * Math.sin(decl) + Math.cos(lat * RAD) * Math.cos(decl) * Math.cos(hourAngle)) / RAD;
}

function solarPosition(date, lon, lat) {
  const day = (date.getTime() - Date.UTC(date.getUTCFullYear(), 0, 0)) / 86400000;
  const hour = date.getUTCHours() + date.getUTCMinutes() / 60 + date.getUTCSeconds() / 3600;
  const gamma = 2 * Math.PI / 365 * (day - 1 + (hour - 12) / 24);
  const decl = 0.006918 - 0.399912 * Math.cos(gamma) + 0.070257 * Math.sin(gamma) - 0.006758 * Math.cos(2 * gamma) + 0.000907 * Math.sin(2 * gamma) - 0.002697 * Math.cos(3 * gamma) + 0.00148 * Math.sin(3 * gamma);
  const eqTime = 229.18 * (0.000075 + 0.001868 * Math.cos(gamma) - 0.032077 * Math.sin(gamma) - 0.014615 * Math.cos(2 * gamma) - 0.040849 * Math.sin(2 * gamma));
  const minutes = date.getUTCHours() * 60 + date.getUTCMinutes() + date.getUTCSeconds() / 60;
  const hourAngle = ((minutes + eqTime + 4 * lon) / 4 - 180) * RAD;
  const phi = lat * RAD;
  const sinAlt = Math.sin(phi) * Math.sin(decl) + Math.cos(phi) * Math.cos(decl) * Math.cos(hourAngle);
  const altitude = Math.asin(Math.max(-1, Math.min(1, sinAlt)));
  const azimuth = Math.atan2(Math.sin(hourAngle), Math.cos(hourAngle) * Math.sin(phi) - Math.tan(decl) * Math.cos(phi)) + Math.PI;
  return { altitude: altitude / RAD, azimuth };
}

function smoothstep(edge0, edge1, value) {
  const t = Math.max(0, Math.min(1, (value - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
}

function mixColor(a, b, t, alpha) {
  return {
    r: Math.round(a[0] + (b[0] - a[0]) * t),
    g: Math.round(a[1] + (b[1] - a[1]) * t),
    b: Math.round(a[2] + (b[2] - a[2]) * t),
    a: alpha,
  };
}

// A continuous six-stop ramp keeps DEM luminance readable beneath the solar
// tint. The altitude thresholds remain the scientific stage boundaries.
function sampleColor(altitude) {
  // Deep night is intentionally close to the page navy while remaining
  // slightly lighter inside the mainland. Keeping a visible alpha avoids a
  // black cutout and lets the official linework stay readable above it.
  if (altitude < -18) return { r: 4, g: 15, b: 39, a: 0.56 };
  if (altitude < -12) {
    const t = smoothstep(-18, -12, altitude);
    return mixColor([4, 15, 39], [20, 40, 76], t, 0.52 - 0.20 * t);
  }
  if (altitude < -6) {
    const t = smoothstep(-12, -6, altitude);
    return mixColor([20, 40, 76], [52, 68, 101], t, 0.29 + 0.07 * t);
  }
  if (altitude < -2) {
    const t = smoothstep(-6, -2, altitude);
    return mixColor([52, 68, 101], [91, 81, 89], t, 0.34 + 0.08 * t);
  }
  if (altitude < -0.833) {
    const t = smoothstep(-2, -0.833, altitude);
    return mixColor([91, 81, 89], [181, 129, 76], t, 0.41 + 0.08 * t);
  }
  const t = smoothstep(-0.833, 35, Math.min(35, altitude));
  return mixColor([181, 129, 76], [224, 184, 108], t, 0.49 + 0.08 * t);
}

function screenMapper(imageRect) {
  const sourceRatio = VIEWBOX.width / VIEWBOX.height;
  const boxRatio = imageRect.width / imageRect.height;
  const scale = boxRatio > sourceRatio ? imageRect.height / VIEWBOX.height : imageRect.width / VIEWBOX.width;
  const ox = (imageRect.width - VIEWBOX.width * scale) / 2;
  const oy = (imageRect.height - VIEWBOX.height * scale) / 2;
  return {
    toScreen(lon, lat) { const v = toV(lon, lat); return [ox + v.x * scale, oy + v.y * scale]; },
    toGeo(x, y) { return fromV((x - ox) / scale, (y - oy) / scale); },
  };
}

function drawTerminator(ctx, mapper, date, threshold, style, contains = null) {
  const lonMin = 70;
  const lonMax = 140;
  const latMin = 3;
  const latMax = 55;
  let started = false;
  ctx.beginPath();
  for (let lat = latMin; lat <= latMax; lat += 0.5) {
    let previousLon = lonMin;
    let previousValue = solarAltitude(date, previousLon, lat) - threshold;
    let crossing = null;
    for (let lon = lonMin + 1; lon <= lonMax; lon += 1) {
      const value = solarAltitude(date, lon, lat) - threshold;
      if ((previousValue < 0 && value >= 0) || (previousValue >= 0 && value < 0)) {
        let lo = previousLon;
        let hi = lon;
        for (let iteration = 0; iteration < 14; iteration += 1) {
          const mid = (lo + hi) / 2;
          const midValue = solarAltitude(date, mid, lat) - threshold;
          if ((previousValue < 0 && midValue >= 0) || (previousValue >= 0 && midValue < 0)) hi = mid;
          else lo = mid;
        }
        crossing = (lo + hi) / 2;
        break;
      }
      previousLon = lon;
      previousValue = value;
    }
    if (crossing == null) { started = false; continue; }
    const point = mapper.toScreen(crossing, lat);
    if (contains && !contains(point[0], point[1])) { started = false; continue; }
    if (!started) { ctx.moveTo(point[0], point[1]); started = true; }
    else ctx.lineTo(point[0], point[1]);
  }
  ctx.save();
  ctx.strokeStyle = style.color;
  ctx.globalAlpha = style.alpha;
  ctx.lineWidth = style.width;
  if (style.shadow) ctx.shadowColor = style.shadow;
  if (style.blur) ctx.shadowBlur = style.blur;
  if (style.dash) ctx.setLineDash(style.dash);
  ctx.stroke();
  ctx.restore();
}

function drawMaskedTerminators(ctx, mapper, date, imageRect, landMask, taiwanMask, dpr, scale, ox, oy, displayMask = null) {
  const lineLayer = document.createElement('canvas');
  lineLayer.width = Math.max(1, Math.ceil(imageRect.width));
  lineLayer.height = Math.max(1, Math.ceil(imageRect.height));
  const lineCtx = lineLayer.getContext('2d');

  // Use the same V-space contain rectangle as the solar field. The line layer
  // is clipped independently so no terminator stroke can leak into ocean or
  // the separate South Sea inset.
  const clip = document.createElement('canvas');
  // Keep mask sampling in CSS pixels. getImageData coordinates are backing
  // store coordinates, so using a separate 1x canvas avoids DPR ambiguity.
  clip.width = Math.max(1, Math.ceil(imageRect.width));
  clip.height = Math.max(1, Math.ceil(imageRect.height));
  const clipCtx = clip.getContext('2d');
  const drawMask = (image) => {
    if (image === displayMask) {
      clipCtx.drawImage(image, 0, 0, imageRect.width, imageRect.height);
      return;
    }
    const w = VIEWBOX.width * scale;
    const h = VIEWBOX.height * scale;
    // Sub-pixel visual closure compensates for the approximate mask's small
    // coastline mismatch without changing the official map or inventing data.
    const r = 1.4;
    for (const [dx, dy] of [[0, 0], [r, 0], [-r, 0], [0, r], [0, -r]]) {
      clipCtx.drawImage(image, ox + dx, oy + dy, w, h);
    }
  };
  drawMask(displayMask || landMask);
  if (taiwanMask) drawMask(taiwanMask);
  const contains = (x, y) => {
    const px = Math.round(x);
    const py = Math.round(y);
    if (px < 0 || py < 0 || px >= clip.width || py >= clip.height) return false;
    return clipCtx.getImageData(px, py, 1, 1).data[3] > 24;
  };
  // Check each sampled terminator point against the mask and break the path
  // outside land, then apply the same mask as a final raster guard.
  drawTerminator(lineCtx, mapper, date, -0.833, { color: 'rgba(238, 191, 111, 1)', alpha: 0.13, width: 10, shadow: 'rgba(231, 177, 91, .24)', blur: 13 }, contains);
  drawTerminator(lineCtx, mapper, date, 0, { color: 'rgba(174, 205, 229, 1)', alpha: 0.18, width: 0.8, dash: [3, 6] }, contains);
  drawTerminator(lineCtx, mapper, date, -0.833, { color: 'rgba(244, 203, 128, 1)', alpha: 0.54, width: 1.35, shadow: 'rgba(241, 181, 85, .48)', blur: 7 }, contains);
  lineCtx.globalCompositeOperation = 'destination-in';
  lineCtx.drawImage(clip, 0, 0, imageRect.width, imageRect.height);
  lineCtx.globalCompositeOperation = 'source-over';
  ctx.drawImage(lineLayer, 0, 0, imageRect.width, imageRect.height);
}

// Render the registered terrain texture as an independent visual layer. The
// texture and the solar field intentionally share the same V-space frame and
// visual-only land mask, while the unchanged official SVG remains above both.
export function renderTerrainRelief(canvas, imageRect) {
  if (!canvas || !imageRect.width || !imageRect.height) return;
  const parent = canvas.parentElement.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 1.25);
  canvas.style.left = `${imageRect.left - parent.left}px`;
  canvas.style.top = `${imageRect.top - parent.top}px`;
  canvas.style.width = `${imageRect.width}px`;
  canvas.style.height = `${imageRect.height}px`;
  canvas.width = Math.max(1, Math.round(imageRect.width * dpr));
  canvas.height = Math.max(1, Math.round(imageRect.height * dpr));
  const ctx = canvas.getContext('2d', { alpha: true });
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, imageRect.width, imageRect.height);

  loadLandMask(canvas, imageRect, null, () => { renderTerrainRelief(canvas, imageRect); renderSolarField(document.querySelector('#solarFieldLayer'), imageRect); });
  loadTerrainTexture(canvas, imageRect, null, () => { renderTerrainRelief(canvas, imageRect); renderSolarField(document.querySelector('#solarFieldLayer'), imageRect); });
  if (!landMaskImage || !terrainTextureImage) return;
  const bodyMaskImage = createLineworkFillMask(landMaskImage);
  if (!bodyMaskImage) return;

  const sourceRatio = VIEWBOX.width / VIEWBOX.height;
  const boxRatio = imageRect.width / imageRect.height;
  const scale = boxRatio > sourceRatio ? imageRect.height / VIEWBOX.height : imageRect.width / VIEWBOX.width;
  const ox = (imageRect.width - VIEWBOX.width * scale) / 2;
  const oy = (imageRect.height - VIEWBOX.height * scale) / 2;
  const width = Math.max(1, Math.ceil(imageRect.width));
  const height = Math.max(1, Math.ceil(imageRect.height));
  const cacheKey = `${width}:${height}:${ox.toFixed(2)}:${oy.toFixed(2)}:${scale.toFixed(6)}`;
  if (!terrainTextureCache || terrainTextureCache.key !== cacheKey) {
    const texture = document.createElement('canvas');
    texture.width = width;
    texture.height = height;
    const textureCtx = texture.getContext('2d');
    textureCtx.imageSmoothingEnabled = true;
    // Keep ridge detail visible while removing tile noise.
    textureCtx.filter = 'grayscale(1) blur(0.16px)';
    textureCtx.drawImage(terrainTextureImage, ox, oy, VIEWBOX.width * scale, VIEWBOX.height * scale);
    textureCtx.filter = 'none';

    // Build a low-frequency companion before normalization. Mixing it with
    // the source hillshade keeps broad plateaus and mountain systems readable
    // while suppressing the uniformly noisy embossed look.
    const coarseW = Math.max(1, Math.ceil(width / 16));
    const coarseH = Math.max(1, Math.ceil(height / 16));
    const coarse = document.createElement('canvas');
    coarse.width = coarseW; coarse.height = coarseH;
    const coarseCtx = coarse.getContext('2d');
    coarseCtx.imageSmoothingEnabled = true;
    coarseCtx.filter = 'blur(0.8px)';
    coarseCtx.drawImage(texture, 0, 0, width, height, 0, 0, coarseW, coarseH);
    coarseCtx.filter = 'none';
    const broad = document.createElement('canvas');
    broad.width = width; broad.height = height;
    const broadCtx = broad.getContext('2d');
    broadCtx.imageSmoothingEnabled = true;
    broadCtx.drawImage(coarse, 0, 0, coarseW, coarseH, 0, 0, width, height);
    const broadPixels = broadCtx.getImageData(0, 0, width, height).data;

    // Normalize the registered texture locally into a restrained cool
    // hillshade. This amplifies terrain relief without preserving source
    // colors, labels, or map furniture as geographic content.
    const terrainPixels = textureCtx.getImageData(0, 0, width, height);
    const luminance = new Uint8Array(width * height);
    const samples = [];
    for (let i = 0; i < luminance.length; i += 1) {
      const p = i * 4;
      const value = terrainPixels.data[p];
      luminance[i] = value;
      if ((i & 7) === 0) samples.push(value);
    }
    samples.sort((a, b) => a - b);
    const lo = samples[Math.floor(samples.length * 0.05)] ?? 0;
    const hi = samples[Math.floor(samples.length * 0.95)] ?? 255;
    const span = Math.max(1, hi - lo);
    for (let i = 0; i < luminance.length; i += 1) {
      const raw = luminance[i];
      const broadValue = broadPixels[i * 4];
      const blended = raw * 0.58 + broadValue * 0.42;
      const normalized = Math.max(0, Math.min(1, (blended - lo) / span));
      // Preserve broad mountain systems while steepening local ridges. The
      // high-pass term is derived from the same registered hillshade, so it
      // cannot introduce a second or misaligned geographic geometry.
      const highPass = Math.max(-1, Math.min(1, (raw - broadValue) / 42));
      const t = Math.max(0, Math.min(1, Math.pow(normalized, 0.88) + highPass * 0.10));
      const p = i * 4;
      terrainPixels.data[p] = Math.round(8 + 94 * t);
      terrainPixels.data[p + 1] = Math.round(20 + 122 * t);
      terrainPixels.data[p + 2] = Math.round(43 + 164 * t);
      // Keep a translucent terrain material rather than an opaque blue wash;
      // this lets the underlying night backdrop remain visible in valleys.
      terrainPixels.data[p + 3] = Math.round(78 + 92 * Math.min(1, Math.abs(highPass) * 0.7 + normalized * 0.48));
    }
    textureCtx.putImageData(terrainPixels, 0, 0);

    const mask = document.createElement('canvas');
    mask.width = width;
    mask.height = height;
    const maskCtx = mask.getContext('2d');
    maskCtx.imageSmoothingEnabled = true;
    maskCtx.filter = 'blur(0.55px)';
    maskCtx.drawImage(bodyMaskImage, ox, oy, VIEWBOX.width * scale, VIEWBOX.height * scale);
    maskCtx.filter = 'none';
    textureCtx.globalCompositeOperation = 'destination-in';
    textureCtx.drawImage(mask, 0, 0);
    textureCtx.globalCompositeOperation = 'source-over';
    terrainTextureCache = { key: cacheKey, canvas: texture };
  }

  ctx.save();
  ctx.globalAlpha = 0.78;
  ctx.globalCompositeOperation = 'normal';
  ctx.drawImage(terrainTextureCache.canvas, 0, 0, imageRect.width, imageRect.height);
  ctx.restore();
}

export function renderSolarField(canvas, imageRect, date = new Date('2026-06-20T21:00:00Z')) {
  if (!canvas || !imageRect.width || !imageRect.height) return;
  const parent = canvas.parentElement.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 1.25);
  canvas.style.left = `${imageRect.left - parent.left}px`;
  canvas.style.top = `${imageRect.top - parent.top}px`;
  canvas.style.width = `${imageRect.width}px`;
  canvas.style.height = `${imageRect.height}px`;
  canvas.width = Math.max(1, Math.round(imageRect.width * dpr));
  canvas.height = Math.max(1, Math.round(imageRect.height * dpr));
  const ctx = canvas.getContext('2d', { alpha: true });
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, imageRect.width, imageRect.height);

  const mapper = screenMapper(imageRect);
  loadLandMask(canvas, imageRect, date);
  loadTerrainElevation(canvas, imageRect, date);
  loadTerrainNormal(canvas, imageRect, date);
  // The mask is derived once from the same presentation linework currently
  // visible in the page. No Natural Earth or second-map guard participates.
  if (!landMaskImage) return;
  const bodyMaskImage = createLineworkFillMask(landMaskImage);
  if (!bodyMaskImage) return;

  // Render a low-resolution solar color field for playback performance. Every
  // sample still uses WGS84 and the inverse SpatialBridge chain; the mask
  // supplies no geographic facts. The field is clipped only after it has been
  // upscaled to the final CSS-pixel canvas, avoiding inward erosion at the
  // Tibet/coast edge caused by clipping a low-resolution raster.
  // The color field is intentionally lower resolution than the official map:
  // bilinear upscaling keeps the transition soft while preserving interactive
  // playback performance. The mask itself remains source-resolution imagery.
  const sampleScale = 0.38;
  const sw = Math.max(1, Math.ceil(imageRect.width * sampleScale));
  const sh = Math.max(1, Math.ceil(imageRect.height * sampleScale));
  const field = document.createElement('canvas');
  field.width = sw; field.height = sh;
  const fctx = field.getContext('2d');
  const pixels = fctx.createImageData(sw, sh);
  const warmPixels = fctx.createImageData(sw, sh);
  const sr = VIEWBOX.width / VIEWBOX.height;
  const br = imageRect.width / imageRect.height;
  const scale = br > sr ? imageRect.height / VIEWBOX.height : imageRect.width / VIEWBOX.width;
  const ox = (imageRect.width - VIEWBOX.width * scale) / 2;
  const oy = (imageRect.height - VIEWBOX.height * scale) / 2;
  let terrainPixels = null;
  // The official body fill is opaque, so the dynamic field must carry the
  // visible relief itself. Prefer the registered hillshade for local ridge
  // contrast; elevation remains available as a fallback for loading races.
  const terrainGradientImage = terrainTextureImage || terrainElevationImage;
  const terrainNormalSample = terrainNormalImage;
  if (terrainGradientImage) {
    const terrainSample = document.createElement('canvas');
    terrainSample.width = sw; terrainSample.height = sh;
    const terrainSampleCtx = terrainSample.getContext('2d', { willReadFrequently: true });
    terrainSampleCtx.filter = 'grayscale(1)';
    terrainSampleCtx.drawImage(terrainGradientImage, ox * sampleScale, oy * sampleScale, VIEWBOX.width * scale * sampleScale, VIEWBOX.height * scale * sampleScale);
    terrainSampleCtx.filter = 'none';
    terrainPixels = terrainSampleCtx.getImageData(0, 0, sw, sh).data;
  }
  let hillContrast = null;
  if (terrainPixels) {
    hillContrast = new Float32Array(sw * sh);
    const hillAt = (xx, yy) => terrainPixels[(yy * sw + xx) * 4] / 255;
    for (let y = 1; y < sh - 1; y += 1) for (let x = 1; x < sw - 1; x += 1) {
      const center = hillAt(x, y);
      const around = (hillAt(x - 1, y) + hillAt(x + 1, y) + hillAt(x, y - 1) + hillAt(x, y + 1)) * 0.25;
      // High-pass ridge signal, intentionally bounded to avoid embossing tile
      // seams or turning the map into a noisy relief chart.
      hillContrast[y * sw + x] = Math.max(-1, Math.min(1, (center - around) * 8.5));
    }
  }
  let normalPixels = null;
  if (terrainNormalSample) {
    const normalSample = document.createElement('canvas');
    normalSample.width = sw; normalSample.height = sh;
    const normalSampleCtx = normalSample.getContext('2d', { willReadFrequently: true });
    normalSampleCtx.drawImage(terrainNormalSample, ox * sampleScale, oy * sampleScale, VIEWBOX.width * scale * sampleScale, VIEWBOX.height * scale * sampleScale);
    normalPixels = normalSampleCtx.getImageData(0, 0, sw, sh).data;
  }
  for (let y = 0; y < sh; y += 1) {
    for (let x = 0; x < sw; x += 1) {
      const vx = (x / sampleScale - ox) / scale;
      const vy = (y / sampleScale - oy) / scale;
      const geo = fromV(vx, vy);
      const i = (y * sw + x) * 4;
      if (!geo || !Number.isFinite(geo.longitude) || !Number.isFinite(geo.latitude)) continue;
      const position = solarPosition(date, geo.longitude, geo.latitude);
      const color = sampleColor(position.altitude);
      const warmness = smoothstep(-4.5, 1.5, position.altitude);
      let relief = 1;
      if (normalPixels) {
        const nr = normalPixels[i] / 255 * 2 - 1;
        const nn = normalPixels[i + 1] / 255 * 2 - 1;
        const nz = normalPixels[i + 2] / 255;
        const altRad = position.altitude * RAD;
        const sunEast = Math.sin(position.azimuth) * Math.cos(altRad);
        const sunNorth = Math.cos(position.azimuth) * Math.cos(altRad);
        const sunUp = Math.sin(altRad);
        const direct = Math.max(0, nr * sunEast + nn * sunNorth + nz * sunUp);
        // Boost mid-tone directional response so mountain faces remain legible
        // beneath the warm solar tint. This is a display exaggeration only;
        // the underlying normal still comes from the registered DEM asset.
        const shapedDirect = Math.pow(direct, 0.68);
        relief = Math.max(0.48, Math.min(1.48, 0.42 + 0.98 * shapedDirect + 0.34 * (1 - nz)));
        if (hillContrast) {
          const h = terrainPixels[i] / 255;
          const ridge = hillContrast[y * sw + x] || 0;
          // Hillshade supplies broad form and the high-pass term sharpens
          // mountain crests without changing the solar geometry.
          relief *= 0.72 + 0.48 * h + ridge * 0.30;
        }
      } else if (terrainPixels && x > 0 && x < sw - 1 && y > 0 && y < sh - 1) {
        const at = (xx, yy) => terrainPixels[(yy * sw + xx) * 4];
        const gx = (at(x + 1, y) - at(x - 1, y)) / 255;
        const gy = (at(x, y + 1) - at(x, y - 1)) / 255;
        const slope = Math.min(1, Math.hypot(gx, gy) * 5.4);
        const aspect = Math.atan2(-gx, gy);
        const face = Math.max(0, Math.cos(position.azimuth - aspect));
        // The elevation analysis raster is low-resolution, so use a wider
        // visual range to make ridges readable without creating hard bands.
        relief = 0.70 + 0.34 * face + 0.24 * slope;
      }
      pixels.data[i] = Math.min(255, Math.round(color.r * relief));
      pixels.data[i + 1] = Math.min(255, Math.round(color.g * relief));
      pixels.data[i + 2] = Math.min(255, Math.round(color.b * relief));
      pixels.data[i + 3] = Math.round(color.a * (0.92 + 0.08 * relief) * 255);
      warmPixels.data[i] = 246;
      warmPixels.data[i + 1] = 181;
      warmPixels.data[i + 2] = 89;
      warmPixels.data[i + 3] = Math.round(warmness * (0.025 + 0.085 * Math.min(1, relief)) * 255);
    }
  }
  fctx.putImageData(pixels, 0, 0);
  const warmField = document.createElement('canvas');
  warmField.width = sw; warmField.height = sh;
  warmField.getContext('2d').putImageData(warmPixels, 0, 0);

  const mask = document.createElement('canvas');
  mask.width = sw; mask.height = sh;
  const mctx = mask.getContext('2d');
  mctx.clearRect(0, 0, sw, sh);
  const maskX = ox * sampleScale;
  const maskY = oy * sampleScale;
  const maskW = VIEWBOX.width * scale * sampleScale;
  const maskH = VIEWBOX.height * scale * sampleScale;
  const drawMask = (image) => {
    mctx.drawImage(image, maskX, maskY, maskW, maskH);
  };
  drawMask(bodyMaskImage);
  const solarLayer = document.createElement('canvas');
  solarLayer.width = Math.max(1, Math.ceil(imageRect.width));
  solarLayer.height = Math.max(1, Math.ceil(imageRect.height));
  const solarCtx = solarLayer.getContext('2d');
  solarCtx.imageSmoothingEnabled = true;
  solarCtx.drawImage(field, 0, 0, imageRect.width, imageRect.height);
  if (terrainGradientImage) {
    // A restrained multiply pass restores the crisp valley/ridge separation
    // that is lost when the low-resolution solar field is upscaled. It is
    // clipped by the same visual land mask below, so it cannot tint ocean or
    // the South Sea inset.
    solarCtx.save();
    solarCtx.globalAlpha = 0.27;
    solarCtx.globalCompositeOperation = 'multiply';
    solarCtx.drawImage(terrainGradientImage, ox, oy, VIEWBOX.width * scale, VIEWBOX.height * scale);
    solarCtx.restore();
  }

  // Apply the source-resolution visual mask in the final display frame. A
  // very small blur only feathers anti-aliased pixels; it is intentionally
  // below one CSS pixel and is not a geographic dilation.
  const finalMask = document.createElement('canvas');
  finalMask.width = solarLayer.width;
  finalMask.height = solarLayer.height;
  const finalMaskCtx = finalMask.getContext('2d');
  finalMaskCtx.imageSmoothingEnabled = true;
  finalMaskCtx.filter = 'blur(0.35px)';
  const drawFinalMask = (image) => {
    const w = VIEWBOX.width * scale;
    const h = VIEWBOX.height * scale;
    // Keep this closure deliberately tiny: it is a display-layer tolerance,
    // not a replacement for official coastline geometry.
    const r = 1.4;
    for (const [dx, dy] of [[0, 0], [r, 0], [-r, 0], [0, r], [0, -r]]) {
      finalMaskCtx.drawImage(image, ox + dx, oy + dy, w, h);
    }
  };
  // Do not use the open-contour path3 candidate here. It is retained only for
  // audit documentation; the working visual mask is the validated raster
  // fallback in the exact same V-space display frame.
  drawFinalMask(bodyMaskImage);
  finalMaskCtx.filter = 'none';
  solarCtx.globalCompositeOperation = 'destination-in';
  solarCtx.drawImage(finalMask, 0, 0);
  solarCtx.globalCompositeOperation = 'source-over';

  // Soft warm bloom follows the computed solar altitude and is clipped to the
  // same land mask. It provides the reference image's atmospheric glow without
  // turning the terminator into a hard painted stripe.
  const bloomLayer = document.createElement('canvas');
  bloomLayer.width = solarLayer.width; bloomLayer.height = solarLayer.height;
  const bloomCtx = bloomLayer.getContext('2d');
  bloomCtx.imageSmoothingEnabled = true;
  bloomCtx.drawImage(warmField, 0, 0, imageRect.width, imageRect.height);
  bloomCtx.globalCompositeOperation = 'destination-in';
  bloomCtx.drawImage(finalMask, 0, 0);
  bloomCtx.globalCompositeOperation = 'source-over';
  const bloomBlur = document.createElement('canvas');
  bloomBlur.width = bloomLayer.width; bloomBlur.height = bloomLayer.height;
  const blurCtx = bloomBlur.getContext('2d');
  blurCtx.filter = 'blur(14px)';
  blurCtx.globalAlpha = 0.72;
  blurCtx.drawImage(bloomLayer, 0, 0);
  blurCtx.filter = 'none';

  ctx.imageSmoothingEnabled = true;
  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  ctx.globalAlpha = 0.72;
  ctx.drawImage(bloomBlur, 0, 0, imageRect.width, imageRect.height);
  ctx.restore();
  ctx.drawImage(solarLayer, 0, 0, imageRect.width, imageRect.height);
  drawMaskedTerminators(ctx, mapper, date, imageRect, bodyMaskImage, null, dpr, scale, ox, oy, null);

}

export { solarAltitude, solarPosition, toV, fromV, LIGHT };
