# Phase 1C-6F：双城日出标尺、时间轴事件标签与地点概览

日期：2026-08-26

## 完成内容

- 晨光推进模式保留窄幅竖向双城日出标尺，城市名、日出时刻、时间差和状态说明均绑定 `state.selected` 与现有 SPA 结果。
- 标尺说明根据当前时刻的真实太阳高度角判断两座城市是否已经日出，覆盖“两座均未日出 / 一座已日出 / 两座均已日出”三种状态。
- 时间轴城市事件标签改为相对轨道绝对定位，使用 `((eventMinutes - 180) / 420) * 100` 并限制在 0%–100%，标签中心与对应节点一致。事件过近时通过垂直错层避免文字重叠。
- 当前时刻概览从右侧栏独立区域迁入 `#comparePanel` 末尾，只在地点对比模式显示，包含四项：已见晨光区域、日出最长差异、日出最早、日出最晚。

## 数据范围

最早/最晚日出及“日出最长差异”统计使用当前已加载且非 `border` 角色的代表城市控制点，并排除三沙、曾母暗沙、黄岩岛等非城市点；最长差异为该集合内最晚与最早事件的分钟差。该统计不是完整全国统计。已见晨光区域为同一代表点集合中太阳高度角不低于 -6° 的比例估算。

## 动态联动

城市选择、时间轴拖动和季节切换均调用现有 `render()` 链路，更新标尺、事件节点、标签、太阳数据和概览；城市点击在两座城市选定后也会立即触发完整渲染，避免时间轴标签残留旧城市。未改写太阳计算公式、SpatialBridge 或城市 `pickedV` 坐标。

## 宽屏验证

- 1280 × 800：地图与右侧栏保持分区，时间轴事件标签跟随节点。
- 1440 × 900：完成晨光推进、地点对比和天文阶段截图；概览在地点对比面板内部且不被页脚遮挡。
- 1920 × 1080：保持同一比例关系，未发现布局溢出或地图裁切。

截图：

- `docs/screenshots/phase1c6f-dawn-progress.png`
- `docs/screenshots/phase1c6f-location-compare.png`
- `docs/screenshots/phase1c6f-astronomy-stage.png`

截图 SHA-256：

- dawn-progress: `82DD07E0BE90521FB24A64A456E5C2425835B6108D8CB9979CDDBCCCD7F1C2FD`
- location-compare: `2656E3F0683D3AB1C3729CCDC8002DA4108B7E74EB8BF3D203697480C3A40B30`
- astronomy-stage: `C875F295DC6554A6A8B370341E4245AE5832D96238C21450601C09C3DEFF3E7C`
- desktop-1280: `8609CF2E83D72B01AA2E1253F266A0938CFEFD5B0AA102C195F447F1278FB47A`
- desktop-1440: `53ECC33581A97C4E0ABB683E5C4C713717B28A89E5FE3BBBCC9C5457A035BEA9`
- desktop-1920: `CF2CF412FA2D67C4231DF66BB3B317D6CC6AA66FC0BC80CAF37A27ADBCF3ADB8`

## 资产完整性

本阶段未修改官方地图几何。完成后复核以下 SHA-256：

- `official-master.eps`: `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC`
- `official-audit.svg`: `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0`
- `clean-map.svg`: `51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72`
- `presentation-map.svg`: `6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F`
- `official-south-sea.svg`: `2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D`

## 已知限制

- 事件时间轴仍限定在 03:00–10:00；超出范围的事件会贴在轨道端点。
- 最早/最晚统计受当前代表城市控制点覆盖范围限制，不代表完整中国区域。
