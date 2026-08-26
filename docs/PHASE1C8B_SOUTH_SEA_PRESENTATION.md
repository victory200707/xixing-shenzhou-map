# Phase 1C-8B：南海 inset 展示层科学化与视觉融合

日期：2026-08-26

## 审计结论

指定源文件均已只读核对。`official-south-sea.svg` 包含 594 个 `path`、1 个背景 `rect`，没有 `<text>` 元素；文字、比例尺和说明若存在，均已转曲为 path。当前 `south-sea-inset.json` 明确要求短段语义保持 `UNKNOWN`，且官方图例与使用条款仍待外部核验。

由于缺少官方图例、来源说明或审图资料，无法可靠区分地名文字、说明文字、比例尺、版权注记与地理线划。本轮没有删除任何 path，避免误删海岸线、岛屿、岛群符号、南海短线或附图边界。

## 独立展示派生文件

- 展示 SVG：`assets/map/svg/south-sea-presentation.svg`
- 对象审计元数据：`assets/map/metadata/south-sea-presentation.json`
- 源文件：`assets/map/svg/official-south-sea.svg`
- 源 SHA-256：`2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D`
- 派生 SHA-256：`D5086F7C6A6C8EA5424F95558F1794712CD33565C0C8C41D9697B2B2ECA493A6`
- viewBox：`0 0 3025.3333 2137.3333`
- 源/派生 path 数：594 / 594
- 移除 path 数：0
- 几何变化：无（path `d`、ID、transform、顺序和 viewBox 保持）

元数据逐条记录 594 个原始 path ID、保留动作、保留原因、`d` SHA-256、transform 和 `geometryChanged=false`。所有对象语义继续标记为 `UNKNOWN`。

## 仅表现层调整

派生层仅调整非几何属性：

| 对象 | 调整 |
| --- | --- |
| inset 背景 rect | `#06172a`，opacity `0.72` |
| 蓝灰线划 | `#70879a`，stroke-opacity `0.52` |
| 暗金线划 | `#b6a37a`，stroke-opacity `0.60` |
| 页面展示层 | CSS opacity `0.88`，弱化 drop-shadow |

没有加入暖色光场、太阳方向光或任何新地理几何。南海层仍位于太阳场上方、城市层下方，不遮挡主图城市和右侧面板。

## 前端与对齐

页面运行时将 `.south-sea-layer` 切换到 `south-sea-presentation.svg`；主图坐标系统、SpatialBridge、显示矩形和 `object-fit: contain` 未改动。HTTP 页面实测主图和 inset 渲染矩形一致：`967.20 × 557.44`（1440 宽屏下的当前布局）。

## 浏览器验证

正式入口：`http://127.0.0.1:4173/index.html`。三种请求视口均加载成功，控制台 error/warn 为 0，城市标记和右侧交互面板正常。

| 请求尺寸 | 实际截图尺寸 | 截图 | SHA-256 |
| --- | --- | --- | --- |
| 1280×800 | 1280×800 | `docs/screenshots/phase1c8b-south-sea-1280.png` | `7233AFDFA9C4125E76AC08905A72C1D34031E825BCB485D71014052905899051` |
| 1440×900 | 1440×900 | `docs/screenshots/phase1c8b-south-sea-1440.png` | `A232F1FF86B8D7B3A3F6405C06040B24CE6A5C58489BA0211E33DDB5681BDC6A` |
| 1920×1080 | 1742×1080（运行环境宽度上限） | `docs/screenshots/phase1c8b-south-sea-1920.png` | `40F0C30EE8980579FC210F2240C79A67E87E5E0A893DB6DC78B847581C452A84` |

处理前后对比：`docs/screenshots/phase1c8b-south-sea-before-after.jpg`。

## 语义与合规分层

- 官方源文件未修改：是。
- 展示派生图移除已确认文字：无；当前没有可确认的文字对象。
- 仍为 `UNKNOWN`：转曲文字、外框/内框、比例尺、岛群符号、短线对象及其他未标注 path。
- 视觉样式调整：仅背景透明度、线色/透明度、CSS opacity 和弱阴影。
- 技术渲染通过：是。
- 几何来源可追溯：是。
- 南海语义已确认：否。
- 正式地图合规已认证：否。

因此当前不具备直接进入正式地图规范复核的条件；需要补充带对象标识的官方图例、来源说明或审图资料后，才能安全执行文字/说明对象移除。此前后续删除操作保持停止状态，不使用截图猜测，也不补画或修正九段线。

## 官方资产完整性

以下文件均未修改：

- `official-master.eps`：`8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC`
- `official-audit.svg`：`D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0`
- `clean-map.svg`：`51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72`
- `presentation-map.svg`：`6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F`
- `official-south-sea.svg`：`2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D`
