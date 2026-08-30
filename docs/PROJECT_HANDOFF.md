# 《曦行神州·万里晨光》项目转交文档

版本：2026-08-26  
工作区：`C:\Users\HUAWEI\Documents\ChatGPT\mask`

## 1. 项目定位

本项目是以官方中国地图为地理事实底图、以统一北京时间播放太阳状态的科学可视化作品。核心叙事是：在同一北京时间下，晨光如何沿中国经度和纬度推进，以及节气和城市位置如何改变日出节律。

首屏优先级为：

1. 中国官方地图及南海附图；
2. 连续的昼夜/晨光视觉变化；
3. 城市标记和日出时间对比；
4. 右侧分析面板、季节入口和底部时间轴。

参考图只用于视觉风格参考，不是中国地图几何或南海内容的来源。

## 2. 当前运行方式

不能双击 `index.html` 进行验收。`file://` 会导致 ES Module 或 `fetch()` 被浏览器同源策略阻止，表现为地图、城市或交互缺失。

有效入口：

```text
http://127.0.0.1:4173/index.html
```

必须从项目根目录启动静态 HTTP 服务。部署到 GitHub Pages 或其他静态托管时，保持 `assets/`、`src/`、`vendor/` 的相对目录结构。

## 3. 当前完成内容

### 已完成并可继续使用

- Vanilla HTML/CSS/JS 首屏和响应式布局；
- 官方主图和独立南海 inset 图层；
- 经纬度刻度、城市标记和城市名称；
- 14 个城市数据及四个极端方向城市：漠河、抚远、喀什、乌鲁木齐；
- 晨光推进、地点对比、天文阶段三种模式；
- 北京时间 03:00–10:00 时间轴、播放/暂停和城市日出标记；
- 春分、夏至、秋分、冬至切换；
- 城市日出、民用晨光、太阳高度角等读数；
- UTC + WGS84 + 太阳高度角 + LCC + SpatialBridge + SVG V 坐标链；
- 右侧窄栏、双城日出标尺、当前时刻概览和宋体视觉系统的既有调整；
- 南海重复渲染抑制和展示层样式降噪；
- 多个桌面尺寸的 HTTP 浏览器回归检查，既有记录显示控制台 error/warn 为 0。

### 当前明确未完成

- 可审计、连续的中国大陆陆地 Mask；
- 正式陆地裁切后的昼夜颜色层；
- 真实 DEM 或地形遮挡模型；
- 南海 inset 中转曲文字、比例尺、短线和其他对象的权威语义确认；
- 正式地图审图号、公开发布许可和最终来源核验；
- 基于独立 `suncalc` 的自动化交叉测试（当前环境可能未安装该包）。

## 4. 目录与关键文件

### 页面入口

- `index.html`：页面结构、图层顺序、模式和季节按钮、时间轴。
- `src/css/style.css`：布局、面板、地图尺寸、图层定位、字体和视觉样式。
- `src/js/main.js`：页面状态、城市选择、时间/季节联动、面板和标记更新。

### 天文计算

- `src/astronomy/solar.js`：太阳状态和阶段相关纯函数。
- `src/astronomy/solar-spa.js`：现有高精度事件适配层。
- `src/astronomy/solar-field.js`：太阳高度角驱动的动态 Canvas 预览层。
- `test/solar.test.mjs`：天文计算回归测试。

当前计算原则：所有城市和场采样点都必须使用 WGS84 经纬度；北京时间必须先转换为真实 UTC 瞬时；太阳高度角用于阶段和冷暖变化；不得用屏幕左右位置代替经纬度计算。

### 地图和空间配置

- `assets/map/source/official-master.eps`：官方原始源，只读归档。
- `assets/map/svg/official-audit.svg`：人工视觉核验通过的不可变 Audit SVG。
- `assets/map/svg/clean-map.svg`：官方清洗派生图，不得直接修改。
- `assets/map/svg/presentation-map.svg`、`presentation-coastline.svg`：表现层派生图。
- `assets/map/svg/official-south-sea.svg`：官方南海 inset source-faithful 派生。
- `assets/map/svg/south-sea-presentation.svg`：南海展示样式派生层。
- `assets/map/metadata/spatial_bridge.json`：G（WGS84）→ P（LCC）→ V（SVG viewBox）桥接。
- `assets/map/metadata/control-points.json`：城市/地理控制点。
- `assets/map/metadata/*.json`：来源、哈希、对象审计和派生记录。

当前 SVG viewBox：`0 0 3025.3333 2137.3333`。主图和南海 inset 必须在同一 V 坐标和同一显示矩形中对齐。

## 5. 官方资产保护规则

以下资产不得重绘、简化、压缩、重新配准或写回：

- `official-master.eps`
- `official-audit.svg`
- `clean-map.svg`
- `presentation-map.svg`
- `presentation-coastline.svg`
- `official-south-sea.svg`

任何派生文件都必须保留来源路径、源 SHA-256、viewBox、尺寸、处理脚本、生成日期和用途限制。视觉层可以改变颜色、透明度和层级，但不能创造、删除或猜测具有地理意义的几何。

## 6. 光场与 Mask 的当前真实状态

当前页面采用同源线划推导的技术性太阳光场预览，不是正式中国陆地光场：

```text
TECHNICAL SOLAR FIELD PREVIEW — NOT FORMAL LAND MASK
```

历史尝试中，`path3` 被误认为陆地填充，强制 `fill: white` 后仍只得到轮廓带，已确认不可用。基于地势 JPG 的近似 Mask 也出现矩形覆盖、硬垂直分界、海域染亮或轮廓外溢等问题，不能直接接入页面。

当前页面已接入同源视觉裁切（仅用于显示），同时仍保持正式地理数据禁用：

- `terrain-registered.png` 页面接入；
- `approx-land-mask.png` 页面接入；
- 任何 Mask stroke/outline/glow；
- 任何矩形或梯形暖色覆盖。

当前视觉裁切来源为 `presentation-coastline.svg` 的 V 坐标扫描线包络，运行时生成并缓存；
`1123-land-mask-v.svg` 仅作为开放外轮廓审计候选，未直接填充。实现和验收记录见
`docs/PHASE1C19_SAME_SOURCE_LAND_COLOR.md`。

相关记录：

- `docs/PHASE1C9F_SOLAR_FIELD_ROLLBACK.md`
- `docs/PHASE1C9E_MASK_FILL_VALIDATION.md`
- `docs/PHASE1C9F_TERRAIN_JPG_MASK.md`

如果继续实现陆地颜色层，必须先通过黑白像素验收：大陆主体内部连续为白色、海域为黑色、海南和台湾按设计保留、南海 inset 独立排除、边缘不外溢。不能通过膨胀轮廓、洪泛填充、手绘轮廓或屏幕左右裁切来制造 Mask。

## 7. 南海 inset 状态

南海附图已与主图分层，且重复线划已抑制。当前 `south-sea-presentation.svg` 保留 594 个官方 path，只调整非几何表现属性；没有确认哪些转曲对象是文字、比例尺、岛群符号或南海断续线，因此这些对象统一标记为 `UNKNOWN`。

禁止：

- 根据截图猜测或补画九段线；
- 仅凭视觉删除南海 path；
- 将南海 inset 当作中国大陆 Mask；
- 把展示样式派生图宣称为正式地图合规成果。

如需清理文字或说明，必须先取得带对象标识的官方图例、源文件图层说明或审图资料。

## 8. 已知风险与接手时优先检查

1. 不要从 `file://` 入口判断项目损坏；先确认 HTTP 入口。
2. 检查是否有旧的 JPG/Mask/CSS 矩形层被重新挂回 DOM。
3. 检查 `.map-visual`、Canvas、主图 SVG、南海 inset 的 `position`、`z-index` 和显示矩形是否一致。
4. 检查城市标记是否仍使用 `projectLonLat()`，不要在组件中加入临时线性经纬度映射。
5. 修改太阳场时，确认海域、背景、文字和 UI 不被同一强度暖色染亮。
6. 任何视觉修复都要同时验证 05:00、06:00、08:00，至少覆盖夏至；再检查春分和冬至。
7. 不要把“无 console error”当成地图科学性或视觉正确性的证明。

## 9. 推荐后续顺序

### A. 先稳定当前基线

- 使用 HTTP 入口恢复并保存一份无矩形色块的基线截图；
- 运行 `npm run test:solar`；
- 检查 1280×800、1440×900、1920×1080（或实际可用宽度）；
- 确认 14 个城市、季节按钮、三模式、时间轴和南海 inset 正常。

### B. 再决定陆地颜色实现路线

优先路线是取得与当前 SVG V 坐标严格对齐、来源可审计的陆地面。若项目时间紧且接受视觉近似，可以建立独立的 `APPROXIMATE_VISUAL_MASK`，但必须经过黑白 Mask、边缘叠加和三时刻截图验收，并明确其不是地理数据。

如果无法在短时间内获得合格 Mask，建议暂时保持技术预览，不再尝试 JPG 直接覆盖。作品仍可通过城市读数、时间轴和阶段信息表达日出节律，避免明显矩形或错误轮廓损害整体可信度。

### C. 最后做视觉增强

只有在 Mask 通过后，才加入低饱和暖金白昼、蓝紫晨昏过渡和深蓝夜面。官方 SVG、边界、省界、城市文字和南海 inset 始终位于动态颜色层之上。

## 10. 最终验收清单

- [ ] 通过 HTTP 入口加载，非 `file://`。
- [ ] 官方地图几何和受保护文件 SHA-256 未变化。
- [ ] 主图与南海 inset 无重复、错位、镜像或二次缩放。
- [ ] 中国主体、海南、台湾和四个极端城市可见。
- [ ] 国界、省界、海岸线、城市名称清晰。
- [ ] 太阳高度角链路使用 UTC/WGS84/SpatialBridge/LCC/V。
- [ ] 05:00、06:00、08:00 的昼夜状态连续且无矩形/梯形边界。
- [ ] 海域和页面背景没有与陆地同强度的暖色覆盖。
- [ ] 时间轴、季节切换、城市对比和天文阶段保持可交互。
- [ ] 控制台 error/warn 为 0。
- [ ] 报告明确区分“视觉近似层”和“正式地理数据”。
- [ ] 发布前完成地图来源、审图号、许可和署名核验。

## 11. 重要文档索引

- 项目定义：`docs/PROJECT.md`
- 地图规格：`docs/MAP_SPEC.md`
- 技术架构：`docs/TECH_ARCHITECTURE.md`
- 本地运行：`docs/LOCAL_RUN.md`
- 旧项目研究：`docs/PHASE1C4B_MORNING_CHINA_RESEARCH.md`
- 布局验收：`docs/PHASE1C6D_DESKTOP_ACCEPTANCE.md`
- 南海审计：`docs/PHASE1C8A_MAP_ENTRY_AND_SOUTH_SEA_AUDIT.md`、`docs/PHASE1C8B_SOUTH_SEA_PRESENTATION.md`
- 光场回退：`docs/PHASE1C9F_SOLAR_FIELD_ROLLBACK.md`
- Mask 验证：`docs/PHASE1C9E_MASK_FILL_VALIDATION.md`、`docs/PHASE1C9F_TERRAIN_JPG_MASK.md`

## 12. 交接结论

当前项目可以作为“官方地图 + 城市日出节律 + 时间轴交互”的可运行基线继续开发。不能把当前状态描述为已完成正式中国陆地光场、真实 DEM 或正式地图合规发布版本。

接手者的第一任务应是确认基线和保护资产，再选择是否投入时间制作可审计的视觉 Mask。任何不能通过陆地内部/海域黑白验证的 Mask 都必须停留在离线诊断目录，不得接入页面。
