# Phase 1C-2 DEM 配准验证

状态：`BLOCKED`

本阶段尚未生成真实 DEM 派生资产，也未修改前端接入真实地形层。阻塞原因是没有可核验的真实 DEM 输入。

## 已核验的空间桥接

- G：WGS84 / EPSG:4326，单位 degrees。
- P：现有 manifest 中的 Lambert Conformal Conic：`+lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +datum=WGS84 +units=m +no_defs`。
- V：官方 SVG viewBox `0 0 3025.3333 2137.3333`。
- 现有主图仿射矩阵来自 `assets/map/metadata/spatial_bridge.json`，未重新拟合、未修改官方 SVG。

## 当前指标（仅桥接控制点，不是 DEM 配准结果）

| 指标 | 结果 |
| --- | ---: |
| 主图控制点 RMSE | 12.1946 px |
| 主图控制点平均误差 | 10.2852 px |
| 主图控制点最大误差 | 27.6791 px |
| 主图控制点 P95 | 20.3315 px |
| 真实 DEM 控制点误差 | `PENDING` |
| 海南/台湾 DEM 边缘误差 | `PENDING` |
| 官方 Mask 外 DEM 泄漏 | `PENDING` |

这些指标说明现有 G→P→V 桥接可以作为当前工程输入，但不能证明真实 DEM 已满足“中位误差 ≤1.5 px、95% ≤3 px”的配准目标。禁止将 Mock PNG 或 SVG 轮廓当作该验证的替代证据。

## 尚未执行的检查

- GeoTIFF CRS/WKT、bounds、像元大小、NoData 和高程单位。
- DEM 重投影到 P 的重采样参数。
- P→V 纹理边缘与官方主体边界的偏差。
- 西部、东部、北部、南部控制点和独立验证点误差。
- 海南、台湾以及南海 inset 的独立处理。
- Mask 外泄漏、镜像、旋转、垂直翻转和裁切检查。

## 结论

在真实 DEM、许可和元数据到位前，Phase 1C-2 不能标记为通过，不能生成 `assets/terrain/derived/` 正式纹理，不能修改前端加入真实 DEM 图层，也不能进入晨光或太阳动态阶段。

