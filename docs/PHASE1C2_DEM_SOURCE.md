# Phase 1C-2 DEM 来源核验

状态：`AUTHORIZED / INPUT_PENDING`

用户已授权优先使用 Copernicus DEM GLO-30。Copernicus Data Space 官方入口已核验可访问：<https://dataspace.copernicus.eu/>。实际文件下载需要在官方数据空间中选择准确产品/瓦片并完成相应账户授权；项目不会猜测或伪造下载直链。

2026-08-25 已接收 9 个唯一的 ASTER GDEM V3 原始压缩包并归档到 `assets/terrain/source/`。经瓦片名称核验，它们仅覆盖约 `80–82°E, 5–14°N`，不覆盖中国主体、海南或台湾，不能参与本项目 DEM 拼接。详情与哈希见 `assets/terrain/metadata/received-astgtmv003.json`。

随后又收到 37 个唯一 ASTER 瓦片（含前一批），已归档到 `assets/terrain/source/`。当前中国相关覆盖主要为 `80–89°E、19–22°N`，仍不完整；缺口汇总见 `assets/terrain/metadata/tile-coverage-report.json`。当前不得解压拼接为正式 DEM。

2026-08-25 已接收并归档 82 个唯一 `SRTMDEM 90M` 压缩包到 `assets/terrain/source/srtm-90m/`。所有压缩包通过结构性 ZIP 检查。经平台编号语义复核，`srtm_XX_YY` 的第一字段是纬向条带、第二字段是经向列，例如门户显示 `srtm_51_02` 中心为 `72.5°E、52.5°N`。保守中国陆地区域需条带 `51–58` 和列 `02–15`；当前缺 66 个候选网格，主要为东部列 `10–15`。完整清单见 `assets/terrain/metadata/srtm-90m-coverage-report.json`；禁止在覆盖完整前拼接正式 DEM。

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
