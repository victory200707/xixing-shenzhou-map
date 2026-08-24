# Phase 1C-1 静态首屏骨架验收记录

## 状态

`COMPLETED`（2026-08-23）；静态参考图对齐复核见 `docs/PHASE1C1_REFERENCE_DIFF.md`。

本阶段完成首屏视觉容器初始化，暂不接入真实天文计算、DEM、晨光场或动态地图状态。

## 实现文件

- `index.html`：可直接双击打开的静态入口。
- `src/css/style.css`：全屏背景、地图舞台、玻璃面板、时间轴和响应式布局。
- `src/js/main.js`：仅处理播放按钮的占位状态切换。
- `tools/clean_map_svg.py`：从 Audit SVG 派生展示层清洗图，保留官方路径数据并移除明确的文字/图例装饰。
- `assets/map/svg/clean-map.svg`：当前静态视觉展示所用的地图派生文件。
- `assets/images/bg-canvas.jpg`：用户提供的背景幕布，未修改。
- `assets/map/svg/official-audit.svg`：人工验收通过的官方 Audit SVG，只读引用，未修改。

## 视觉结构

- 深色星空背景覆盖整个视口且不重复。
- 中国官方地图占据首屏主舞台，位于左侧/中央，并保留南海 inset。
- 右侧为地点对比、城市快捷选择和天文阶段三个半透明毛玻璃面板。
- 底部为播放按钮、时间轨道、摘要指标和四季预设占位。
- 桌面端使用地图主导的双栏构图；窄屏端将信息轨道和时间控制转为纵向流。

## 静态边界

- 面板读数使用 `XX:XX`、`00.0%` 等占位值，不代表科学结果。
- 未加载真实 DEM，不生成 hillshade、晨光或昼夜分界。
- 未修改、压缩、简化或重绘官方 SVG 路径。
- 未引入 React/Vue 等大型前端框架。

## 资源校验

| 资源 | 结果 |
| --- | --- |
| `bg-canvas.jpg` | 2528×1688；SHA-256 `F9A316BDB9800695359724897061D6B3D8B62CF0EE9EAE8E5E21CD204A5E7B44` |
| `official-audit.svg` | 继续使用已冻结文件；未发生内容修改 |

## 浏览器验证

- 桌面：1536×1024，背景、地图主体、右侧面板、底部时间轴均已加载。
- 移动：390×844，地图主舞台、信息轨道和时间控制按响应式规则纵向排列。

截图：

- `analysis/phase1c/desktop-1536x1024-final.png`
- `analysis/phase1c/mobile-390x844-viewport.png`

本轮参考图对齐验收：

- `analysis/phase1c1/before.png`
- `analysis/phase1c1/after.png`
- `analysis/phase1c1/overlay.png`
- `analysis/phase1c1/desktop-1920x1080.png`
- `analysis/phase1c1/mobile-390x844.png`

## 下一阶段边界

进入真实数据接入前，仍需确认公开发布所需的官方地图来源/许可，并在独立模块中接入 SpatialBridge、真实 DEM 与既有天文算法。任何动态层必须继续与官方几何解耦。
