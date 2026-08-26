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
  nightOpacity: 0.105,
  twilightOpacity: 0.105,
  daylightOpacity: 0.105,
  warmBandOpacity: 0.115,
  terminatorGlow: 0.34,
  boundaryPreservation: 0.86,
};

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

function smoothstep(edge0, edge1, value) {
  const t = Math.max(0, Math.min(1, (value - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
}

function canvasEdgeFade(x, y, width, height) {
  // PREVIEW_MAP_EXTENT_ONLY: fade the actual displayed rectangle, never a
  // projected longitude/latitude bounding box that could look trapezoidal.
  const edgeDistance = Math.min(x, y, width - x, height - y);
  return smoothstep(0, Math.min(width, height) * 0.12, edgeDistance);
}

function sampleColor(altitude) {
  if (altitude < -18) return { r: 6, g: 25, b: 55, a: LIGHT.nightOpacity };
  if (altitude < -12) {
    const t = (altitude + 18) / 6;
    return { r: 11 + 12 * t, g: 36 + 30 * t, b: 71 + 35 * t, a: LIGHT.twilightOpacity * (0.54 + 0.46 * t) };
  }
  if (altitude < -6) {
    const t = (altitude + 12) / 6;
    return { r: 23 + 47 * t, g: 65 + 43 * t, b: 105 + 28 * t, a: LIGHT.twilightOpacity * (0.72 + 0.28 * t) };
  }
  if (altitude < -0.833) {
    const t = (altitude + 6) / 5.167;
    return { r: 70 + 130 * t, g: 108 + 55 * t, b: 132 - 22 * t, a: LIGHT.warmBandOpacity * (0.45 + 0.55 * t) };
  }
  const t = Math.min(1, Math.max(0, (altitude + 0.833) / 45));
  return { r: 202 + 32 * t, g: 161 + 43 * t, b: 91 + 47 * t, a: LIGHT.daylightOpacity * (0.36 + 0.64 * t) };
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

function drawTerminator(ctx, mapper, date, threshold, style) {
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
    if (!started) { ctx.moveTo(point[0], point[1]); started = true; }
    else ctx.lineTo(point[0], point[1]);
  }
  ctx.save();
  ctx.strokeStyle = style.color;
  ctx.globalAlpha = style.alpha;
  ctx.lineWidth = style.width;
  if (style.dash) ctx.setLineDash(style.dash);
  ctx.stroke();
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
  // Dense offscreen sampling removes visible cell edges. This is a technical
  // geographic extent, not a claimed land polygon or a real DEM.
  const sampleWidth = Math.max(180, Math.min(320, Math.round(imageRect.width / 3)));
  const sampleHeight = Math.max(120, Math.min(220, Math.round(imageRect.height / 3)));
  const field = document.createElement('canvas');
  field.width = sampleWidth;
  field.height = sampleHeight;
  const fieldCtx = field.getContext('2d', { alpha: true });
  const pixels = fieldCtx.createImageData(sampleWidth, sampleHeight);
  for (let y = 0; y < sampleHeight; y += 1) {
    for (let x = 0; x < sampleWidth; x += 1) {
      const geo = mapper.toGeo((x + 0.5) * imageRect.width / sampleWidth, (y + 0.5) * imageRect.height / sampleHeight);
      if (!geo) continue;
      const fade = canvasEdgeFade((x + 0.5) * imageRect.width / sampleWidth, (y + 0.5) * imageRect.height / sampleHeight, imageRect.width, imageRect.height);
      const color = sampleColor(solarAltitude(date, geo.longitude, geo.latitude));
      const index = (y * sampleWidth + x) * 4;
      pixels.data[index] = color.r;
      pixels.data[index + 1] = color.g;
      pixels.data[index + 2] = color.b;
      pixels.data[index + 3] = Math.round(color.a * fade * 255);
    }
  }
  fieldCtx.putImageData(pixels, 0, 0);
  ctx.imageSmoothingEnabled = true;
  ctx.globalCompositeOperation = 'source-over';
  ctx.drawImage(field, 0, 0, imageRect.width, imageRect.height);

  const edge = ctx.createRadialGradient(imageRect.width * .5, imageRect.height * .5, Math.min(imageRect.width, imageRect.height) * .18, imageRect.width * .5, imageRect.height * .5, Math.max(imageRect.width, imageRect.height) * .75);
  edge.addColorStop(0, 'rgba(0, 14, 34, 0)');
  edge.addColorStop(1, 'rgba(0, 11, 28, .12)');
  ctx.fillStyle = edge;
  ctx.fillRect(0, 0, imageRect.width, imageRect.height);

  // 0° is the geometric day/night boundary; -0.833° is the sunrise boundary.
  drawTerminator(ctx, mapper, date, 0, { color: 'rgba(181, 210, 231, 1)', alpha: LIGHT.terminatorGlow * .55, width: 1.05, dash: [2, 5] });
  drawTerminator(ctx, mapper, date, -0.833, { color: 'rgba(233, 188, 102, 1)', alpha: LIGHT.terminatorGlow, width: 1.25, dash: [6, 4] });
}

export { solarAltitude, toV, fromV, LIGHT };
