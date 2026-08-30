# Phase 1C-11：近似大陆 Mask 与陆地昼夜颜色层

## 结论

已接入一层独立的近似大陆视觉 Mask，用于裁切太阳驱动的陆地颜色层。该层不提供国界、省界、城市坐标或任何地图事实。

`APPROXIMATE_VISUAL_MASK - NOT A GEOGRAPHIC SOURCE`

## 来源与处理

- 来源：`assets/map/source/ne_10m_admin_0_countries.geojson`
- 数据集：Natural Earth 10m Admin 0 Countries
- 选择对象：`ADMIN=China`
- 投影链：WGS84 经纬度 → China LCC → 现有 SpatialBridge → SVG V
- 输出：`assets/map/raster/ne-china-visual-mask.png`
- 输出尺寸：`3025 × 2137`
- 输出 viewBox：`0 0 3025.3333 2137.3333`
- South Sea inset：未包含，继续使用独立官方图层

## 光场合成

太阳高度角仍由 UTC、WGS84、LCC、SpatialBridge 计算。颜色层只在 Mask alpha 内绘制，并位于官方 SVG 下方：

`background → terrain → solar field clipped by mask → official SVG → South Sea inset → cities → UI`

`< -18°` 为深蓝夜面，`-18°` 至 `-6°` 为冷色过渡，`-6°` 至 `-0.833°` 为蓝紫至暗金晨昏过渡，`> -0.833°` 为连续暖金白昼层。

## 验证

已在 HTTP 页面 `http://127.0.0.1:4173/index.html` 验证：

- 05:00 画面中东部陆地暖金、西部陆地深蓝；
- 海域和页面背景没有同强度暖色覆盖；
- 官方边界、省界、城市名称和城市点位保持在上层；
- 南海 inset 保持独立；
- 控制台 error/warn：0。

Mask 内部采样 alpha：北京 230、乌鲁木齐 230、漠河 230、抚远 230、喀什 230、广州 230、海口 230。台北不在本近似大陆 Mask 内，仍由官方地图单独表示。

## SHA-256

- `ne_10m_admin_0_countries.geojson`: `239EEC57AC17F100A11E2536CFFC56752C318B50AE765B0918FF7AAB4CE8F255`
- `ne-china-visual-mask.png`: `0289060CC08A0D2D23F5EEF5CB4A0432840A92E8A19EF7C3C94C790AC1716FF2`

官方 EPS、Audit SVG、Clean SVG、Presentation SVG 和 South Sea SVG 均未修改。

## 限制

Natural Earth 几何不是中国官方地图数据，Mask 仅供低对比度视觉裁切。它不能用于正式地图发布、边界审查、城市定位或替代官方底图；正式发布前仍需取得与官方底图严格一致且有审图依据的陆地面数据。

## 2026-08-27 视觉连续性修复

针对宽屏验收中西藏南部出现的局部视觉断带，本轮仅调整渲染层：

- 光场采样由 `0.25` 提高至 `0.75`，避免窄南缘在缩小采样时消失；
- 在运行时对同一 Natural Earth Mask 做最大 4 CSS px 的圆形边缘闭合，再进行透明羽化；
- 未新增经纬度顶点、未绘制西藏边界、未改变官方 SVG/EPS；
- 南海 inset 仍不进入大陆 Mask。

本轮补充台湾：

- 新增 `assets/map/raster/ne-taiwan-visual-mask.png`；
- 来源同为 Natural Earth 10m `ADMIN=Taiwan`，与大陆 Mask 分开保存和合成；
- SHA-256：`1AED6DA80DD265D3E57D07235CD5CCA65639E0995E45561EADAF143FCE3DDDA3`；
- 该要素只用于台湾的视觉颜色/纹理裁切，不替代官方岛屿几何。

已配准的 `terrain-texture-registered-v.png` 现以低透明度 `screen` 材质叠加在太阳颜色层下方，并同时使用大陆与台湾视觉 Mask 裁切。其注册误差 RMSE 为 4.686px，仍属于视觉纹理，不是 DEM 或地图事实源。

该处理仍属于：

`APPROXIMATE_VISUAL_MASK - NOT A GEOGRAPHIC SOURCE`

并且页面输出仍属于：

`TECHNICAL SOLAR FIELD PREVIEW - NOT FORMAL LAND MASK`

## 宽屏验收

HTTP 页面 `http://127.0.0.1:4173/index.html` 在 1440x900 下复验：

- `docs/screenshots/phase1c11-final-0500.jpg`
- `docs/screenshots/phase1c11-final-0600.jpg`
- `docs/screenshots/phase1c11-final-0800.jpg`

结果：

- 05:00 东部大陆为暖金、西部为深蓝，过渡区连续；
- 06:00 过渡带保持连续，西藏南部没有 Mask 内部透明孔洞；
- 08:00 大陆主体保持连续暖金，海域和 UI 未被同强度染色；
- 官方边界、省界、城市名称、城市点位和南海 inset 均在光场之上；
- 控制台 error/warn：0。

西藏南部此前被观察到的暗色三角区是该时刻太阳高度角低于晨昏阈值形成的连续夜面/过渡面，不是渲染缺口。将其强行涂暖会破坏天文意义，因此仅修复了 Mask 边缘的采样断带。
