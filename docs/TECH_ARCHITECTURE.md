# 技术架构

## 分层

```text
官方地图/DEM资产与 manifest
        ↓
地图数据层（几何、mask、投影、城市投影）
        ↓
地图渲染层（SVG静态几何 + Canvas动态纹理）
        ↓
天文计算层（UTC/北京时间、太阳状态、事件、节气）
        ↓
动态可视化层（光场、分界线、阶段、缓存）
        ↓
交互状态层（日期、时间、城市、播放）
        ↓
UI层（标题、面板、时间轴、图例）
```

## 推荐技术栈

- TypeScript + Vite，沿用旧项目的构建经验。
- `astronomy-engine` 作为主天文引擎，`suncalc` 做独立测试交叉核验。
- SVG 承载官方矢量几何、边界、标签和城市命中区域。
- Canvas 2D 负责 DEM hillshade、动态色场、昼夜分界和光晕；使用离屏 Canvas 与 requestAnimationFrame 节流。
- CSS 负责面板、渐变、暗角和响应式布局；图标使用开源图标库。
- WebGL/WebGPU 仅在性能基准证明 Canvas 不能满足目标帧率后再评估。

## 建议目录

```text
src/
  assets/            # 由 manifest 管理的派生地图、DEM纹理、字体
  map/
    geometry.ts      # 官方几何加载与图层类型
    projection.ts    # EPS控制点/投影到viewBox
    masks.ts         # land/coast/inset mask
    render-static.ts # SVG静态层
  astronomy/
    solar.ts         # 旧项目算法迁移后的纯函数
    seasons.ts
    events.ts
  visualization/
    dem.ts           # hillshade/纹理
    light-field.ts   # 太阳场与晨昏分界
    compositor.ts
  interaction/
    state.ts         # 单一时间/城市/播放状态
    playback.ts
  ui/
    shell.ts
    panels.ts
    timeline.ts
tools/map-pipeline/  # EPS转换、拆层、mask、manifest、预览
tests/
docs/
```

## Phase 1C-1 实现边界

当前首屏使用根目录 `index.html`、`src/css/style.css` 和 `src/js/main.js` 的
Vanilla 静态容器，以便直接双击检查构图。它只加载已冻结的 Audit SVG 和背景
图片；真实 SpatialBridge、DEM、太阳状态与时间轴状态继续由后续模块接入，不在
静态骨架中复制或猜测。

## 关键接口边界

- `MapGeometry` 只描述官方路径和 viewBox，不包含太阳颜色。
- `Projection` 只负责经纬度与地图坐标转换，所有城市/经纬网/光场共用。
- `SolarEngine` 输入 UTC 瞬时和 GeoPoint，输出 `SolarState`、`MorningEvents`、`SeasonInstants`。
- `LightFieldRenderer` 输入 `SolarState`、DEM 派生纹理、mask 和渲染尺寸，输出 Canvas 图层；不读取 UI DOM。
- `TimelineState` 是唯一时间源；UI 只派发意图，渲染器订阅状态快照。
- `AssetManifest` 是静态几何和数据许可的审计入口，运行时不得静默替换资产。

## 渲染顺序

1. 深色海域与星点背景。
2. 官方 land/coast/island/inset SVG 几何。
3. mask 内 DEM hillshade 与基础地形色。
4. Canvas 动态晨光色场和分界线。
5. 经纬网、城市点/标签和太阳辅助线。
6. 右侧面板、底部时间轴和四季卡片。

## 性能与稳定性

- 地图路径只初始化一次；时间变化不重新解析 EPS/SVG。
- 动态场按设备像素比和目标尺寸生成，必要时使用 1/2 或 1/4 分辨率再放大。
- 播放时只更新受影响的 Canvas、标记和读数；拖动结束后再做昂贵的事件计算。
- 统一处理 resize、设备像素比、`prefers-reduced-motion` 和无日出/日落 null 值。
- 目标：桌面首屏播放保持稳定 30–60 fps；以真实设备基准决定是否升级 WebGL。

## 工具链与验证

地图转换脚本必须可重复、无网络副作用，并输出预览、manifest 和几何校验报告。科学测试沿用旧项目测试思路；发布前增加官方几何 hash、mask 边界、控制点误差和视口截图回归。
