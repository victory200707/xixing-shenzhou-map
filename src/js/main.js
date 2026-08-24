(() => {
  const playToggle = document.querySelector("#playToggle");
  if (playToggle) {
    // Static scaffold only: this toggles a placeholder control state and does
    // not calculate or animate any astronomical data.
    playToggle.addEventListener("click", () => {
      const paused = playToggle.getAttribute("aria-pressed") === "true";
      playToggle.setAttribute("aria-pressed", String(!paused));
      playToggle.textContent = paused ? "▶" : "Ⅱ";
      playToggle.title = paused ? "播放/暂停" : "暂停占位动画";
    });
  }

  const mapImage = document.querySelector(".map-image");
  const cityLayer = document.querySelector("#cityLayer");
  if (!mapImage || !cityLayer) return;

  const VIEWBOX = { width: 3025.3333, height: 2137.3333 };
  const FALLBACK_POINTS = [
    { name: "哈尔滨", role: "interior", x: 2293.3535, y: 478.5389 },
    { name: "乌鲁木齐", role: "interior", x: 789.5632, y: 547.7053 },
    { name: "拉萨", role: "interior", x: 771.3615, y: 1376.7095 },
    { name: "北京", role: "capital", x: 1958.1115, y: 860.7744 },
    { name: "西安", role: "interior", x: 1630.4811, y: 1202.9661 },
    { name: "成都", role: "interior", x: 1404.7802, y: 1397.5587 },
    { name: "武汉", role: "interior", x: 1870.7434, y: 1397.5587 },
    { name: "上海", role: "coast", x: 2231.1368, y: 1342.9536 },
    { name: "广州", role: "coast", x: 1856.1821, y: 1823.4782 },
    { name: "台北", role: "island", x: 2271.1805, y: 1683.4906 },
    { name: "海口", role: "island", x: 1699.6476, y: 2011.121 },
    { name: "三沙", role: "island", x: 2777.1875, y: 1672.5696, inset: true },
  ];

  const loadControlPoints = async () => {
    try {
      const response = await fetch("assets/map/metadata/control-points.json", { cache: "no-store" });
      if (!response.ok) throw new Error(`control points: ${response.status}`);
      const payload = await response.json();
      return payload.controlPoints;
    } catch {
      // Direct file:// opening blocks fetch in some browsers. The fallback is
      // the audited V-coordinate subset and keeps the static preview usable.
      return FALLBACK_POINTS;
    }
  };

  const displayPoints = (points) => points.filter((point) => {
    if (point.role === "border") return false;
    if (["曾母暗沙", "黄岩岛"].includes(point.name)) return false;
    return Number.isFinite(Number(point.x)) && Number.isFinite(Number(point.y));
  });

  const renderCityMarkers = (points) => {
    cityLayer.replaceChildren();
    displayPoints(points).forEach((point) => {
      const marker = document.createElement("span");
      marker.className = "city-marker";
      marker.dataset.role = point.role || "interior";
      if (point.inset || point.name === "三沙") marker.dataset.inset = "true";
      marker.dataset.name = point.name;
      marker.setAttribute("aria-label", point.name);
      marker.innerHTML = `<span class="city-marker-label">${point.name}</span>`;
      marker._visualPoint = { x: Number(point.x), y: Number(point.y) };
      cityLayer.append(marker);
    });
    syncCityMarkerPositions();
  };

  const syncCityMarkerPositions = () => {
    const layerRect = cityLayer.getBoundingClientRect();
    const imageRect = mapImage.getBoundingClientRect();
    if (!imageRect.width || !imageRect.height || !layerRect.width || !layerRect.height) return;

    const viewRatio = VIEWBOX.width / VIEWBOX.height;
    const boxRatio = imageRect.width / imageRect.height;
    const scale = boxRatio > viewRatio ? imageRect.height / VIEWBOX.height : imageRect.width / VIEWBOX.width;
    const renderedWidth = VIEWBOX.width * scale;
    const renderedHeight = VIEWBOX.height * scale;
    const offsetX = (imageRect.width - renderedWidth) / 2;
    const offsetY = (imageRect.height - renderedHeight) / 2;

    cityLayer.querySelectorAll(".city-marker").forEach((marker) => {
      const point = marker._visualPoint;
      const x = imageRect.left - layerRect.left + offsetX + point.x * scale;
      const y = imageRect.top - layerRect.top + offsetY + point.y * scale;
      marker.style.left = `${x}px`;
      marker.style.top = `${y}px`;
    });
  };

  loadControlPoints().then(renderCityMarkers);
  mapImage.addEventListener("load", syncCityMarkerPositions, { once: false });
  window.addEventListener("resize", syncCityMarkerPositions, { passive: true });
})();
