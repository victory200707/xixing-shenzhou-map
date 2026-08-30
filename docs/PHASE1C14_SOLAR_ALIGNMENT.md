# Phase 1C-14：太阳光场坐标统一与宽屏验收

## 目标

修正太阳光场、地势纹理、官方 SVG 和城市标记之间因独立 CSS 缩放产生的相对偏移。保持 UTC、WGS84、太阳高度角、LCC 与 SpatialBridge 计算链不变。

## 实现

- `.map-visual` 成为唯一的 `scale(1.04)` 变换拥有者，变换原点保持 `48% 48%`。
- `presentation-coastline.svg`、南海 inset、两个 Canvas 和城市层均使用同一未变换布局坐标。
- Canvas 和城市点位依据 `offsetWidth/offsetHeight` 计算 V 坐标，不再使用变换后 SVG 的外接矩形反推内部投影。
- 晨昏线在独立 1 倍 CSS 像素线层中应用大陆/台湾 Mask，再合成到光场，避免线条和昼面使用不同坐标基准。
- 光场先在低分辨率计算，再放大到最终 CSS 像素后裁切；最终 Mask 仅做约 1.4 CSS 像素的显示层边缘闭合，抵消近似 Natural Earth 与官方轮廓之间的细小内缩，不改变任何地理几何。
- 入口 CSS 与太阳模块增加版本查询参数，避免本地验收复用旧缓存。

## 验收

入口：`http://127.0.0.1:4173/index.html`

宽屏截图：

- `docs/screenshots/phase1c14-aligned-1280.png`
- `docs/screenshots/phase1c14-aligned-0500.png`
- `docs/screenshots/phase1c14-aligned-0600.png`
- `docs/screenshots/phase1c14-aligned-0800.png`

已检查：

- 05:00、06:00、08:00 昼面连续推进；
- 西藏南部、东部沿海边缘与官方轮廓保持同一显示框架；
- 台湾随太阳高度角参与颜色变化；
- 城市文字和点位未发生相对漂移；
- 南海 inset 保持独立，不进入大陆 Mask；
- 播放测试从 05:00 推进至 05:09；
- 浏览器控制台 error/warn：0。

## 数据边界

当前大陆与台湾裁切仍采用 Natural Earth 派生的近似视觉 Mask，仅用于低对比度颜色/纹理裁切，不能替代官方地理边界，也不能用于正式地图审查或发布：

`APPROXIMATE_VISUAL_MASK - NOT A GEOGRAPHIC SOURCE`

官方 EPS、Audit SVG、Clean SVG、Presentation SVG 和南海 SVG 未修改。

## 追加修正

由于近似视觉 Mask 与官方西藏南缘存在少量边缘差异，最终光场与晨昏线裁切均增加了 1.4 CSS 像素的十字方向边缘闭合，并保留 0.35px 羽化。该操作只用于降低肉眼可见的暗缝，仍属于：

`APPROXIMATE_VISUAL_MASK - NOT A GEOGRAPHIC SOURCE`
