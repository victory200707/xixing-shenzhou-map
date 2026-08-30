# Phase 1C-10 官方边界视觉 Mask 尝试

日期：2026-08-26

## 目标

从官方 1∶740 万 SVG 的已渲染外轮廓生成独立视觉 Mask，使太阳高度角颜色只作用于中国大陆主体。

## 输入

- 输入渲染：`tools/current-mask-black.png`
- 对应官方 SVG viewBox：`0 0 3025.3333 2137.3333`
- 官方 SVG SHA-256：`D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0`

## 方法

1. 提取官方渲染中的浅色/蓝灰外轮廓；
2. 对栅格断缝执行有限形态学闭合；
3. 从画布边缘进行外部洪水填充；
4. 从北京、海南、台湾 V 坐标进行内部连通性检查；
5. 排除右下角南海 inset 区域；
6. 输出独立黑白诊断图和 RGBA 视觉 Mask。

工具：`tools/generate_official_boundary_mask.py`

## 结果

状态：`BLOCKED_BOUNDARY_RASTER_HAS_OPEN_SEAMS`

当前渲染外轮廓存在无法由有限栅格闭合安全修复的断缝。外部洪水填充会进入大陆内部，因此：

- 北京内部未得到白色陆地区域；
- 海南内部未得到白色陆地区域；
- 台湾内部未得到白色陆地区域；
- 输出 Mask 覆盖率为 0；
- 该 Mask 未接入页面；
- 官方 SVG/EPS 未修改。

## 保护结论

不能通过继续扩大膨胀半径、手工连接断点或按截图描绘轮廓来修复。那会把视觉近似层变成未经审计的新地理几何。

## 下一步阻塞解除条件

需要以下任一项：

1. 与当前 SVG viewBox 对齐的官方中国大陆闭合陆地面（SVG/GeoJSON/矢量图层）；或
2. 官方 EPS 中可确认的大陆填充图层及其图层说明；或
3. 经授权的官方地图数据导出，并记录来源、版本、许可、SHA-256 和控制点。

取得闭合陆地面后，重新生成：

```text
陆地面 → 黑白 Mask 验收 → 太阳高度角颜色层 → 官方 SVG
```

当前页面继续保持无矩形色场的回退状态：

`CURRENT_MASK_RENDERING_DISABLED_DUE_TO_OUTLINE_LEAK`

`APPROXIMATE_VISUAL_MASK — NOT A GEOGRAPHIC SOURCE`
