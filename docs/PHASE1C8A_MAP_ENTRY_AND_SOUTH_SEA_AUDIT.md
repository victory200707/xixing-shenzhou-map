# Phase 1C-8A：官方地图入口修复与南海 inset 规范审计

日期：2026-08-26

## 1. 页面入口

正式验收入口为：

```text
http://127.0.0.1:4173/index.html
```

`file:///C:/Users/HUAWEI/Documents/ChatGPT/mask/index.html` 不是有效功能验收入口。其 origin 通常为 `null`，浏览器会按同源策略限制 ES Module 和 `fetch(control-points.json)`，从而可能导致 `main.js` 不执行、控制点数据加载失败以及城市/面板/季节交互失效。本次浏览器工具对 `file://` 直达被安全 URL 策略拦截，未绕过该限制；失效原因同时由页面的模块导入和 fetch 依赖确认。

运行步骤见 `README.md` 和 `docs/LOCAL_RUN.md`。

## 2. 官方地图派生链

| 文件 | 大小 | SHA-256 | 关系与使用结论 |
| --- | ---: | --- | --- |
| `official-master.eps` | 20,165,997 bytes | `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC` | 官方原始源，保留本地，不改动 |
| `official-audit.svg` | 5,624,733 bytes | `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0` | EPS 的人工核验派生，冻结 |
| `clean-map.svg` | 734,169 bytes | `51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72` | 清洗派生，几何冻结 |
| `presentation-map.svg` | 769,385 bytes | `6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F` | 样式派生来源，几何冻结 |
| `presentation-coastline.svg` | 742,942 bytes | `AFDADE73B26560432D66015434C1B2F9A417D2562C0415554669CEA562D18A89` | 本阶段主图表现层，样式调整并抑制重复 inset 线划 |
| `official-south-sea.svg` | 897,328 bytes | `2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D` | 官方 Audit SVG 的 source-faithful 南海派生，保留完整显示 |

## 3. `presentation-coastline.svg` 几何审计

元数据：`assets/map/metadata/presentation-coastline.json`。

- 来源文件和 SHA-256 与 `presentation-map.svg` 一致；
- 源路径 859，派生保留路径 810；
- `changedGeometry=0`：逐路径比较 `d` 和 transform 无变化；
- `geometryFingerprint.equal=false` 仅因为隐藏了 49 个与官方 inset overlay 重复的 path，隐藏 ID 已完整记录在 metadata；
- viewBox 仍为 `0 0 3025.3333 2137.3333`；
- `pathDataChanged=false`、`transformChanged=false`、`viewBoxChanged=false`、`pathOrderChanged=false`。

因此该差异可解释且可追溯，不构成 `BLOCKED_GEOMETRY_UNVERIFIED`。派生层允许继续作为表现层使用，不作为新的地理事实来源。

## 4. 南海 inset 重复与内容

`presentation-map.svg` 与 `official-south-sea.svg` 原先共享 50 个来源 path ID，其中 `path3` 为主体填充候选，其余 49 条为重复线划。当前页面使用 `presentation-coastline.svg` 加完整 `official-south-sea.svg`，因此只保留一套南海线划，避免重复边框、岛屿、短段和亮度叠加。

南海派生文件包含 594 个 path 和 1 个 presentation backdrop rect；没有 `<text>`。源对象样式分为填充、线划和小型符号等多组，但语义均未完成对象级确认。东沙、西沙、中沙、南沙、曾母暗沙等对象是否对应具体地理名称不能仅凭转曲路径安全判断，统一标记为 `UNKNOWN`。不得将短段称为“九段线”，本阶段未补画或删除任何南海短段。

转曲文字、比例尺和说明无法可靠区分，未隐藏任何对象；仅通过去重和整体层级降低视觉干扰。

## 5. 对齐与图层

主图和 inset 均使用同一 V viewBox、`object-fit: contain` 和显示矩形，浏览器检查未发现第二次缩放、镜像、裁切或 transform origin 不一致。实际图层为：

```text
背景
→ terrain canvas
→ solar field canvas
→ presentation-coastline.svg
→ official-south-sea.svg
→ 城市与地理标记
→ UI
```

南海 overlay 位于主图表现层上方、城市层下方；太阳光场不会独立裁切 inset 底色，但不会覆盖或抹除官方线划。

## 6. HTTP 验收

在 `http://127.0.0.1:4173/index.html` 下检查 1280 × 800、1440 × 900、1920 × 1080：

- 14 个城市标记存在；
- 季节按钮、地点对比、天文阶段和时间轴可用；
- 日出时间显示为真实数值，不是全量 `--:--`；
- 南海 inset 可见且无明显重影；
- 三个尺寸均无页面溢出；
- 控制台错误和警告为 0。

截图：`docs/screenshots/phase1c8a-http-1440.png`  
SHA-256：`2DC4623BF2AFB88EA7EAD858BB3DA25320DE0A3FFA422B25858DAC0A4CEC42B4`

## 7. 结论与风险

本阶段地图入口和重复渲染问题已修复，官方资产哈希保持不变，可以进入后续人工地图规范复核。海岸线、国界、省界、南海文字和短段的对象语义仍为 `UNKNOWN`；若需删除或重分类对象，必须先取得可审计的官方对象说明。
