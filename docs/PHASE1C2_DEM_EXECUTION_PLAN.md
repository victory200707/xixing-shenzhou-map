# Phase 1C-2 DEM 执行计划

状态：`AUTHORIZED / INPUT_PENDING`

用户已授权优先核验 Copernicus DEM GLO-30。AI 可以负责下载后的元数据检查、哈希记录、重投影、纹理渲染和验证；不会猜测 CRS、许可证或地图几何。

## 执行顺序

1. 将准确版本的 Copernicus DEM GeoTIFF 放入 `assets/map/source/dem.tif`。
2. 补全 `assets/terrain/metadata/terrain-manifest.json` 的版本、URL、许可证和下载日期。
3. 运行 `tools/prepare_dem.py`，确认 CRS、bounds、分辨率、NoData 和 SHA-256。
4. 检查覆盖中国主体、海南和台湾；海域覆盖不足时单独标记，不自动补高程。
5. 重投影到现有 LCC 工作坐标 P，并通过 SpatialBridge 反向采样到 SVG V。
6. 生成 hillshade 和低对比度 terrain-v 纹理，使用官方 Mask 限制显示范围。
7. 独立检查主图和南海 inset，输出偏差、泄漏、镜像、裁切报告。
8. 人工验收后才接入前端；本阶段不修改 `official-audit.svg`。

## 当前阻塞

仓库尚无真实 GeoTIFF，且当前运行时没有 `rasterio`。在这两项到位前不生成正式 terrain 资产。
