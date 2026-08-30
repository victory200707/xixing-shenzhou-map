const RAD = Math.PI / 180;
const EARTH_RADIUS = 6378137;
const VIEWBOX = { width: 3025.3333, height: 2137.3333 };
const BRIDGE = {
  a: 0.0005049096535585887, b: 0.000022454384736449136, tx: 1361.601054864795,
  c: 0.000025236110567069284, d: -0.0005152163553260364, ty: 3246.205083005489,
};
function toV(lon, lat) {
  const phi1 = 25 * RAD, phi2 = 47 * RAD, lon0 = 105 * RAD;
  const n = Math.log(Math.cos(phi1) / Math.cos(phi2)) /
    Math.log(Math.tan(Math.PI / 4 + phi2 / 2) / Math.tan(Math.PI / 4 + phi1 / 2));
  const f = Math.cos(phi1) * Math.pow(Math.tan(Math.PI / 4 + phi1 / 2), n) / n;
  const phi = lat * RAD, rho = f / Math.pow(Math.tan(Math.PI / 4 + phi / 2), n);
  const theta = n * (lon * RAD - lon0);
  const px = rho * Math.sin(theta) * EARTH_RADIUS;
  const py = (f - rho * Math.cos(theta)) * EARTH_RADIUS;
  return { x: BRIDGE.a * px + BRIDGE.b * py + BRIDGE.tx, y: BRIDGE.c * px + BRIDGE.d * py + BRIDGE.ty };
}
function renderMapGrid(root, frame) {
  if (!root || !frame?.width || !frame?.height) return;
  const ratio = VIEWBOX.width / VIEWBOX.height;
  const scale = frame.width / frame.height > ratio ? frame.height / VIEWBOX.height : frame.width / VIEWBOX.width;
  const ox = (frame.width - VIEWBOX.width * scale) / 2;
  const oy = (frame.height - VIEWBOX.height * scale) / 2;
  root.querySelectorAll('.map-axis-top span').forEach((label) => {
    const longitude = Number(label.dataset.longitude || label.textContent.replace(/[^0-9.-]/g, ''));
    const v = toV(longitude, 50);
    label.style.left = `${ox + v.x * scale}px`;
  });
  root.querySelectorAll('.map-axis-left span').forEach((label) => {
    const latitude = Number(label.dataset.latitude || label.textContent.replace(/[^0-9.-]/g, ''));
    const v = toV(72, latitude);
    label.style.top = `${oy + v.y * scale}px`;
  });
}
export { renderMapGrid };
