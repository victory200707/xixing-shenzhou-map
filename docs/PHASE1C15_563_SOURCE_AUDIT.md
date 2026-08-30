# Phase 1C-15：563.svg 候选陆地/地势源审计

日期：2026-08-28  
状态：`CANDIDATE_UNREGISTERED`

## 只读结论

桌面文件 `C:\Users\HUAWEI\Desktop\563.svg` 已归档为
`assets/map/source/563.svg`，它不是当前页面正在使用的
`presentation-coastline.svg`，也不是同一套 SVG viewBox。它具备进一步处理价值，
但本轮未接入页面。

| 项目 | 结果 |
| --- | --- |
| 文件 SHA-256 | `CDA24AC7DF6D2AC115D19DAD3CB5DECE949A7ECB0F77BCF014756D1F22FE8B0D` |
| viewBox | `0 0 210 297` |
| 路径数量 | 3088 |
| 闭合路径（含 Z/z） | 1544 |
| 填充 | 主要为 `#c8b7b7`，多种 opacity |
| stroke | 路径主体为 `none` |
| image/text 对象 | 0 |
| Inkscape 图层 | 2 层，内部包含 `translate(34.183962,-30.692278)` |

## 与当前问题的关系

当前光场使用的是 Natural Earth 近似 Mask，而官方底图使用
`0 0 3025.3333 2137.3333` 的 V 坐标。因此截图中的西藏南部缺口，确实可以由两套
边界不一致造成。`563.svg` 的闭合填充路径可能提供更贴近原始地势图的视觉面，
但它当前没有：

- 与项目 V 坐标的配准参数；
- 可核验的经纬度控制点；
- 中国大陆、台湾、海南和南海 inset 的对象语义；
- 来源版本、比例尺和公开发布许可说明。

所以不能直接把它当作官方陆地 Mask，也不能仅凭图形外观把它强行缩放到当前地图。

## 同源官方派生层的新发现

复核项目内的 `assets/map/svg/presentation-map.svg` 后，发现其中保留了一个
`presentation-body-fill-unknown`（`path3`）主体填充对象，而当前页面使用的
`presentation-coastline.svg` 不包含该对象。该对象与当前地图使用相同的
`0 0 3025.3333 2137.3333` viewBox，因此比 Natural Earth 更有希望消除边界错位。

已在 `solar-field.js` 中加入受覆盖率门控的运行时像素取色候选：仅当该填充对象
实际覆盖率达到 8% 以上时才使用；否则自动回退到既有近似 Mask。该候选不改变
官方 SVG，也不会定义国界、省界或城市坐标。

## 当前采取的决定

- 未修改任何官方 EPS/SVG；
- 未替换当前太阳计算或城市坐标；
- 未将 `563.svg` 接入 `solar-field.js`；
- 未把未配准路径生成页面可见的陆地颜色层；
- 保留现有近似 Mask 与页面基线，避免引入新的错位。

## 解除阻塞所需的最小工作

1. 在 Inkscape 或其他可审计工具中确认 563 中哪些路径属于中国地图主体；
2. 从 563 图层选取至少 4 个可识别控制点，与 `control-points.json` 建立 A4→V 仿射变换；
3. 生成黑白候选 Mask，并检查北京、拉萨、西藏南缘、广州、海南、台湾和海域像素；
4. 只有差异叠加通过后，才接入太阳颜色层；563 仍只能作为视觉候选源，不能替代官方地图事实。

当前标签：

`CANDIDATE_UNREGISTERED — DO NOT USE AS GEOGRAPHIC SOURCE`
