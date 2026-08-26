# Phase 1C-9B：官方陆地裁切昼夜光场审计

日期：2026-08-26  
状态：`BLOCKED_UNKNOWN_LAND_GEOMETRY`

## 只读审计结论

本阶段检查了：

- `assets/map/svg/official-audit.svg`
- `assets/map/svg/clean-map.svg`
- `assets/map/svg/presentation-map.svg`
- `assets/map/svg/presentation-coastline.svg`
- `assets/map/metadata/spatial_bridge.json`
- `src/astronomy/solar-field.js`
- `assets/map/metadata/map-mask.json`

`official-audit.svg` 和 `clean-map.svg` 没有可由对象 ID、图层语义或官方元数据确认的中国主体陆地填充路径。`presentation-map.svg` 中唯一的填充候选是 `path3`，其表现样式为填充色、`fill-rule:evenodd`，但已有 `map-mask.json` 审计记录确认：

- `path3` 的 V 空间包围盒约为 `[125.92, 58.10, 2631.34, 1941.15]`；
- 采样覆盖率约 `0.02124`；
- 结构上是细窄的印刷轮廓带，不是可确认的实心中国陆地轮廓；
- 其余 858 条可见对象是无语义标识的 stroke-only 路径；
- 南海 inset 为独立线划对象，语义仍为 `UNKNOWN`。

因此不能安全使用 `path3` 生成陆地 Mask，也不能根据截图、路径长度或视觉形状猜测中国轮廓。

## 执行决策

按照阶段规则，本轮已停止：

- 未生成 `assets/map/raster/official-land-mask.png`；
- 未创建或修改任何 Mask 生成脚本；
- 未修改 `src/astronomy/solar-field.js`；
- 未修改任何官方 SVG/EPS；
- 未生成新的抽象地形层；
- 未把矩形技术光场宣称为正式中国陆地光场；
- 未继续进行陆地裁切视觉优化。

当前仍可使用 Phase 1C-9A 的连续昼夜光场作为**技术范围预览**：它通过 SpatialBridge 反解到 WGS84 并按太阳高度角计算，但覆盖的是地图显示矩形，不是中国陆地 Mask。

## 已有太阳场状态

`src/astronomy/solar-field.js` 当前保留：

- UTC `Date` 输入；
- WGS84 经纬度反解；
- LCC 与 SpatialBridge `P → V` 链；
- `-6°` 天文晨光、`-0.833°` 民用日出和 `0°` 几何昼夜阈值；
- 连续三段 alpha 光场和平滑插值；
- 矩形边缘渐隐 fallback。

其明确限制是：没有可靠陆地 Mask，因此不能称为正式陆地裁切光场。

## 官方资产完整性

| 文件 | SHA-256 |
| --- | --- |
| `official-audit.svg` | `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0` |
| `clean-map.svg` | `51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72` |
| `presentation-map.svg` | `6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F` |
| `presentation-coastline.svg` | `AFDADE73B26560432D66015434C1B2F9A417D2562C0415554669CEA562D18A89` |
| `official-south-sea.svg` | `2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D` |
| `south-sea-presentation.svg` | `D5086F7C6A6C8EA5424F95558F1794712CD33565C0C8C41D9697B2B2ECA493A6` |

以上资产在本阶段未修改。下一步必须提供或正式确认一个带明确陆地语义、可追溯来源且与 `0 0 3025.3333 2137.3333` 对齐的官方陆地面；在此之前，正式陆地裁切验收保持阻塞。
