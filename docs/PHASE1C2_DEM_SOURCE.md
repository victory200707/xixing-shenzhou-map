# Phase 1C-2 DEM 来源核验

状态：`AUTHORIZED / INPUT_PENDING`

用户已授权优先使用 Copernicus DEM GLO-30。Copernicus Data Space 官方入口已核验可访问：<https://dataspace.copernicus.eu/>。实际文件下载需要在官方数据空间中选择准确产品/瓦片并完成相应账户授权；项目不会猜测或伪造下载直链。

截至 2026-08-23，项目没有提供或归档真实 DEM GeoTIFF：

- 预期路径 `assets/map/source/dem.tif` 不存在。
- 项目内没有其他 `.tif`、`.tiff` 或 DEM 栅格输入。
- 因此无法核验发布机构、版本、下载地址、空间分辨率、水平 CRS、垂直基准、NoData、许可、覆盖范围或源文件 SHA-256。

## 当前可确认内容

现有 Mock 管线只使用确定性合成数组，不是地理数据，也不能作为发布地形资产：

- 脚本：`tools/render_dem.py`
- 输出：`assets/map/raster/mock_base.png`
- 输出尺寸：3025 × 2137
- 用途：验证 V → P → G 逆采样和输出尺寸，不代表真实高程。

现有候选来源仅作为待核验选项，当前没有纳入项目资产：

| 候选 | 发布机构/产品 | 当前状态 |
| --- | --- | --- |
| GEBCO Grid | British Oceanographic Data Centre / GEBCO | 待确认具体版本、下载文件、许可和陆海覆盖 |
| Copernicus DEM GLO-30 | European Space Agency / Copernicus | 待确认版本、许可、覆盖和派生纹理再分发条件 |
| NASA SRTM/NASADEM | NASA/USGS | 主要为陆地高程，不能单独覆盖南海海域；待确认版本和许可 |

## 解除输入阻塞所需步骤

请从官方数据空间下载覆盖项目范围的 GeoTIFF，并放置为：

```text
assets/map/source/dem.tif
```

同时补全 `assets/terrain/metadata/terrain-manifest.json`：数据名称、发布机构、版本/日期、实际文件 URL、分辨率、覆盖范围、水平 CRS/WKT 或 EPSG、垂直基准、高程单位、NoData、许可证和下载日期。收到后才能继续元数据读取、重投影、hillshade、V 对齐纹理和配准误差报告。
