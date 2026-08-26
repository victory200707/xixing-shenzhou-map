# Phase 1C-8：海岸线层级优化与南海 inset 视觉清理

日期：2026-08-26

## 审计结果

- `presentation-map.svg`：859 个 path，无 `<text>`；其 metadata 将 650 条 primary、207 条 secondary 和 1 条 accent 线划全部标记为 `UNKNOWN` 语义，另有 1 条主体填充候选。
- `official-south-sea.svg`：594 个 path、1 个 presentation backdrop rect，无 `<text>`。文字、比例尺和说明在源文件中均已转曲，不能仅凭对象类型安全识别。
- 两个 SVG 共享 50 个来源 path ID。`path3` 是主体填充候选，保留在主图；其余 49 条是与 inset 重复的线划对象，已在新的主图表现派生层中隐藏。
- 因此当前页面不再重复绘制 inset 线划；完整官方南海 inset 仍由 `official-south-sea.svg` 单独显示。

## 海岸线候选与样式层级

当前无法从官方路径语义可靠区分国界、海岸线和省界，均记录为 `UNKNOWN`。本阶段采用保守候选分组：primary linework 作为 `coastline-candidate / national-line candidate`，secondary linework 作为 `province-line candidate`。

新的 `presentation-coastline.svg` 仅调整表现样式：

- primary：`#c8b98f`，1.16px，opacity 0.78；
- secondary：`#6e8595`，0.68px，opacity 0.34；
- accent 与主体填充保持原派生样式。

这使候选海岸线/国界比省界更清晰，但不宣称完成了语义级海岸线识别；没有修改任何 `path d`、transform、viewBox 或坐标。

## 南海 inset 清理与对齐

页面原先同时加载 `presentation-map.svg` 和 `official-south-sea.svg`，造成 50 个共享对象重复渲染，表现为 inset 线划发亮和重影。页面现改用 `presentation-coastline.svg`，其中仅隐藏 49 个重复线划；保留完整 `official-south-sea.svg`，其 viewBox、显示矩形和 `object-fit: contain` 与主图一致。未删除、重绘或重命名官方南海对象，短段语义继续为 `UNKNOWN`。

由于南海文字已经转曲且语义未确认，本阶段没有猜测隐藏任何文字、岛屿或线段。Inset 仍位于主图表现层上方、城市层下方；太阳光场位于其下方，因此不能独立改变 inset 内部填充，但不会遮挡官方线划。

## 图层顺序

```text
terrain canvas (z-index 0)
→ solar field canvas (z-index 1)
→ presentation-coastline.svg (z-index 2)
→ official-south-sea.svg (z-index 3)
→ city markers (z-index 4)
→ UI
```

## 浏览器验证

使用本地 HTTP 页面完成 1440 × 900 截图检查，并复核 1280 × 800、1920 × 1080 的地图矩形、比例和无溢出状态。主图海岸线候选与省界仍可区分；海南、台湾和南海 inset 保留，未见重复边框或明显重影。截图：

- `docs/screenshots/phase1c8-coastline-south-sea.png`
- SHA-256：`64FD729313AB37DFEB48FE73977B531AC34FE3C4CDFAF5C07D51418FAB856AE2`

## 派生层追踪

- 来源：`assets/map/svg/presentation-map.svg`
- 来源 SHA-256：`6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F`
- 派生：`assets/map/svg/presentation-coastline.svg`
- 派生 SHA-256：`AFDADE73B26560432D66015434C1B2F9A417D2562C0415554669CEA562D18A89`
- 元数据：`assets/map/metadata/presentation-coastline.json`
- 几何指纹：来源 `0E954D47738601EAA32B063DB765D72D712CF8DBBA0E454DCBFA980A3A9E8ACE`；派生保留路径 `882EDEB33610D1E849CEF5A3DF0F6AC0DDB73201ED314562E745857585A5BF64`。指纹不同仅因为隐藏 49 个重复 inset 路径，保留路径的 `d` 未变。

## 官方资产完整性

- `official-master.eps`: `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC`
- `official-audit.svg`: `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0`
- `clean-map.svg`: `51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72`
- `presentation-map.svg`: `6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F`
- `official-south-sea.svg`: `2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D`

## 未确认对象与风险

- 海岸线、国界、省界和南海短段仍未完成对象级语义确认。
- 南海转曲文字未删除，以避免误删地理事实；未来若需减密，应先取得可审计对象分类。
- 光场无法独立裁切到 inset 填充，当前仅保证其位于 inset 线划下方且不破坏可读性。
