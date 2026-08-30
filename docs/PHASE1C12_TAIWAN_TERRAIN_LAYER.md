# Phase 1C-12：台湾光影补全与地势材质试接

## 完成内容

- 新增台湾独立近似视觉 Mask：`assets/map/raster/ne-taiwan-visual-mask.png`；
- 太阳颜色层同时使用大陆与台湾 Mask，台湾不再被遗漏；
- 台湾 Mask 来源为 Natural Earth 10m `ADMIN=Taiwan`，仅用于视觉裁切；
- 接入由已配准地势图低频化生成的 `terrain-relief-lowfreq-v.png`，以低透明度 `screen` 材质叠加在太阳颜色层下方；
- 地势纹理与太阳场均位于官方 SVG 下方，南海 inset 继续独立；
- 官方 EPS、Audit SVG、Clean SVG、Presentation SVG、South Sea SVG 未修改。

## 明确边界

`APPROXIMATE_VISUAL_MASK - NOT A GEOGRAPHIC SOURCE`

台湾 Mask 和大陆 Mask 都不能用于边界、城市坐标、南海内容或正式地图发布。地势纹理不是 DEM，也不提供海拔值；只承担参考图所需的低对比度材质效果。

`terrain-relief-lowfreq-v.png` 来源于已配准地势图，经过 15px 块平均与二次低通，仅保留大尺度蓝灰明暗变化，再同时使用大陆与台湾视觉 Mask 裁切。低频材质 SHA-256：`70084D3D456C88E53012CCC9AC6670AF375021F036408CB9B3A4CE05E4C015D1`。

## 宽屏验收

页面：`http://127.0.0.1:4173/index.html`

截图：`docs/screenshots/phase1c12-taiwan-terrain-1440.jpg`（1440x900）
截图 SHA-256：`619BA3AC23E1089F9FE31AFDD00271130B5C468E7760B4350E288498C51B4BD2`

验收结论：

- 05:00 台湾出现与太阳高度角一致的暖色过渡；
- 大陆东暖西冷分区保持连续，西藏南部没有新的透明断带；
- 地势纹理只在大陆与台湾视觉 Mask 内出现，海域、右侧 UI、时间轴未被纹理覆盖；
- 官方边界、省界、城市名称和点位仍在最上层；
- 控制台 error/warn：0。

## 当前限制

Natural Earth 与已配准地势 JPG 都不是官方地图事实源。当前效果可用于视觉演示和交互验收，不能据此宣称完成正式陆地 Mask 或地图审查。
