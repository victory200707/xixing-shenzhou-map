# Phase 1C-16：当前网站地图同源 Mask 对齐

## 目的

解决太阳光场与页面地图边界不一致的问题。页面显示层是
`assets/map/svg/presentation-coastline.svg`，此前太阳层同时使用了 Natural Earth
近似边界，导致西藏南缘、沿海和岛屿出现错位或暗缝。

## 实现

- 从当前网站同源的 `assets/map/svg/presentation-map.svg#path3` 提取主体填充路径；
- 保留原始 `d`、`transform`、`fill-rule=evenodd` 和 `viewBox`，不修改官方 SVG；
- 浏览器运行时将该路径栅格化为透明白色 Mask；
- 太阳颜色层、地势层和晨昏线优先使用此同源 Mask；
- Natural Earth 不再参与本轮页面光场裁切，台湾仍作为单独视觉 Mask；
- 官方主图、南海 inset、城市和交互逻辑保持原有层级。

## 坐标一致性

同源 Mask 与页面主图均使用：

```text
viewBox: 0 0 3025.3333 2137.3333
V 坐标空间
同一 presentation scale 与 object-fit: contain 显示矩形
```

太阳计算链未改变：

```text
UTC -> WGS84 -> 太阳高度角 -> LCC -> SpatialBridge -> SVG V
```

## 验收状态

- 页面入口：`http://127.0.0.1:4173/index.html`
- `presentation-map.svg#path3` 实际渲染复核为开放轮廓带，不能作为陆地填充；
- 已回退到既有 `ne-china-visual-mask.png` 视觉层，避免太阳光场消失；
- 同源路径保留为审计候选，不进入页面裁切链；
- 太阳层与官方主图仍共享同一显示矩形；
- 未修改官方 EPS/SVG 几何；
- 近似视觉层仍不属于正式地理数据。

验收截图：

- `docs/screenshots/phase1c16-same-map-0500.png`
- `docs/screenshots/phase1c16-same-map-0600.png`
- `docs/screenshots/phase1c16-same-map-0800.png`

这三张截图记录了同源路径误判为填充后的失败状态，仅用于回归对照。

浏览器验收：控制台 error/warn 为 0；城市标记和时间轴仍可交互。

标识：

`SAME_SOURCE_VISUAL_MASK — FOR DISPLAY CLIPPING ONLY`

`TECHNICAL SOLAR FIELD PREVIEW — NOT FORMAL LAND MASK`
