# Phase 1C-8B：南海 inset 对象级复核

日期：2026-08-26  
状态：`MAP_AUDIT_BLOCKED`（语义确认与正式地图合规仍阻塞；技术核验通过）

## 1. 核验范围与保护边界

本轮只读审计 `presentation-coastline.svg` 中由 Phase 1C-8A 标记为隐藏 inset 重复对象的 49 个 `path`，并核对 `official-south-sea.svg` 的可观察对象结构。未修改、重绘、删除或重命名任何官方地图路径。

机器可读逐对象结果：

- `assets/map/metadata/south-sea-object-audit.json`
- 每条记录包含 source-id、两侧 `d` SHA-256/长度、自身 transform、父级 transform、主图和 inset 的 V 空间 bounding box、Canvas 像素差异和分类。

## 2. 49 个隐藏对象核验结果

| 项目 | 结果 |
| --- | --- |
| 对象总数 | 49 |
| `EXACT_DUPLICATE`（几何/变换） | 49 |
| `DIFFERENT_GEOMETRY` | 0 |
| 对应对象缺失 | 0 |
| 自身 transform 不同 | 0 |
| 父级 transform 不同 | 0 |
| V 空间 bounding box 不同 | 0 |
| 浏览器 Canvas 栅格比较 | 49/49 `OK` |

所有对象的主图与 inset `d` 字符串相等，且常见变换为 `matrix(0.13333333,0,0,-0.13333333,0,2137.3333)`；父级 transform 均为空。包围盒由浏览器 SVG `getBBox()` 与 `getCTM()` 计算，坐标空间为 `0 0 3025.3333 2137.3333`。

像素比较采用同一页面 origin 下的浏览器 `Image` + 256×181 Canvas 栅格化。报告同时记录 `rgbaDiffPixels`、`rgbaDiffRate`、`alphaDiffPixels` 和并集非透明像素数。部分对象存在非零像素差异，这是主图表现层和官方 inset 使用不同线色/透明度造成的表现差异，不构成几何差异；几何分类不以颜色相等为条件。

## 3. official-south-sea.svg 对象分类

文件包含 594 个 `path`、1 个 `rect`、0 个 `<text>`。文字、比例尺或说明若存在，均已转曲为路径。基于当前文件、Phase 1C-8A 元数据和可追溯信息，无法对下列语义作官方确认：

| 可观察类别 | 可观察对象 | 语义分类 | 处理 |
| --- | --- | --- | --- |
| 外框候选 | `path3622`（闭合矩形几何） | `UNKNOWN` | 保留 |
| 内框候选 | `path3621`（长框状路径几何） | `UNKNOWN` | 保留 |
| 比例尺候选 | `path3504`, `path3505`（短矩形/线段几何） | `UNKNOWN` | 保留 |
| 转曲文字 | 无 `<text>`；可能与其他 path 混合 | `UNKNOWN` | 不删除 |
| 岛群符号 | path artwork，无法从当前元数据分离 | `UNKNOWN` | 不删除 |
| 短线对象 | 以短 `d` 长度筛出的候选列表见 JSON | `UNKNOWN` | 不删除、不命名 |
| 背景矩形 | 1 个 presentation backdrop `rect` | `UNKNOWN` | 保留 |

没有官方图例、来源说明或审图资料支持时，短线对象不得命名为“九段线”，任何路径也不得被猜测为岛屿、行政边界或其他地理语义。语义 UNKNOWN 是审计结论，不代表对象不存在。

## 4. 视觉整合与图层

页面继续使用以下顺序：

```text
terrain canvas
→ solar field canvas
→ presentation-coastline.svg
→ official-south-sea.svg
→ city markers
→ UI
```

主图与 inset 继续使用同一 viewBox、显示矩形和 `object-fit: contain` 对齐关系。未增加视觉删除或新的地图绘制；保留的 inset 由官方 `official-south-sea.svg` 单独提供，避免与主图重复叠加。

## 5. 对比截图

- 处理前（Phase 1C-8 页面）：`docs/screenshots/phase1c8-coastline-south-sea.png`，1440×900，SHA-256 `64FD729313AB37DFEB48FE73977B531AC34FE3C4CDFAF5C07D51418FAB856AE2`
- 处理后 HTTP 渲染：`docs/screenshots/phase1c8b-south-sea-after.png`，1280×720，SHA-256 `61D3F5D84D6FD4316BC845ED390DC662DD6FF3AF40A286D387F327C378B38CFF`
- 前后对比合成：`docs/screenshots/phase1c8b-south-sea-before-after.jpg`，1440×478，SHA-256 `4B95A30DEE890A574FFDF24E2B9E8758D645D67FAC94F849956387B875976537`

## 6. 结论分层

- **技术渲染通过：是。** 49/49 对象均完成浏览器栅格化和差异记录；HTTP 页面可加载。
- **几何来源可追溯：是。** 49 条隐藏对象均可追溯到 `presentation-map.svg` 与 `official-south-sea.svg` 同源 path，`d`/transform 未改写。
- **南海语义已确认：否。** 外框、内框、比例尺、转曲文字、岛群符号和短线对象缺乏官方图例/审图资料，全部按 `UNKNOWN` 保留。
- **正式地图合规已认证：否。** 本项目没有审图号、发布许可或语义级对象证明，不能宣称正式地图合规认证。

由于存在未确认语义，本阶段停止任何对象删除、重命名或补画操作，并标记 `MAP_AUDIT_BLOCKED`。进入后续视觉优化前，需要提供可核验的官方来源说明、图例或审图资料。

## 7. 官方资产完整性

| 文件 | 大小（bytes） | SHA-256 |
| --- | ---: | --- |
| `assets/map/source/official-master.eps` | 20,165,997 | `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC` |
| `assets/map/svg/official-audit.svg` | 5,624,733 | `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0` |
| `assets/map/svg/clean-map.svg` | 734,169 | `51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72` |
| `assets/map/svg/presentation-map.svg` | 769,385 | `6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F` |
| `assets/map/svg/presentation-coastline.svg` | 742,942 | `AFDADE73B26560432D66015434C1B2F9A417D2562C0415554669CEA562D18A89` |
| `assets/map/svg/official-south-sea.svg` | 897,328 | `2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D` |

以上哈希与 8A 记录一致；本阶段未修改这些地图资产。
