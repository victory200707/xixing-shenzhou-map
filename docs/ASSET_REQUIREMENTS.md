# 素材需求与来源管理

## 素材清单

| 素材 | 处理方式 | 是否必须下载/提供 | 版权与验收 |
| --- | --- | --- | --- |
| 官方中国地图 EPS | 原件归档；可重复转换为 SVG/PDF；拆分 land/boundary/coast/island/inset | 用户提供/已发现候选 | 保留原始压缩包、哈希、来源、版本、审图号和署名要求 |
| 官方地图派生 SVG/GeoJSON/mask | 程序生成并版本化 | 需要生成 | 不改几何；manifest 记录转换器版本、控制点、容差 |
| DEM（30–90 m） | 下载 GeoTIFF，裁切/重采样，派生 hillshade/坡度纹理 | 可自行获取，需用户确认许可 | 原始数据不一定随站点发布；记录许可和派生图发布范围 |
| 城市点与名称 | 权威坐标表，必要时人工审核 | 可自行获取，首批名单建议用户确认 | 记录来源、查询日期、坐标基准；不要从地图图片 OCR 猜坐标 |
| 南海插图/岛屿层 | 从官方地图独立拆出 | 随官方地图 | 保留官方比例和位置关系，不用第三方 inset 替代 |
| 星空/背景纹理 | 固定种子程序生成低密度星点与噪声 | 不需要下载 | 不使用与地图事实混淆的 AI 生成底图；生成参数入 manifest |
| 云层/大气纹理 | MVP 不需要；若使用，程序生成极低对比度纹理 | 不需要下载 | 不能暗示实时天气或观测数据 |
| 图标 | 使用已选开源图标库 | 依赖安装 | 记录库版本与许可证；按钮提供无障碍名称 |
| 中文字体 | 使用系统字体或已获许可字体 | 需确认品牌要求 | 商业字体不得打包；标题字稿如需一致，应由用户提供或确认许可 |
| 参考图 | 仅作视觉规格与验收参照 | 用户已提供 | 不把参考图裁切成最终地图底图 |

## 当前发现的压缩包

- `C:\Users\HUAWEI\Downloads\4o28b0625501ad13015501ad2bfc0240b.zip`：1:2200 万 EPS。
- `C:\Users\HUAWEI\Downloads\4o28b0625501ad13015501ad2bfc0696b.zip`：1:740 万分省设色 EPS。
- `C:\Users\HUAWEI\Downloads\4o28b0625501ad13015501ad2bfc2190b.zip`：1:1000 万 EPS。
- `C:\Users\HUAWEI\Downloads\morning-china-0.2.1.zip`：旧项目源码快照，不是最终地图资产。

已计算的文件哈希如下（当前仅用于识别，不代表审图或授权证明）：

- 1:2200 万压缩包 SHA-256：`DE2854D1601D9658902BA11F0002F9DACEDF029C9EE630A72EA73900708B31AC`
- 1:740 万压缩包 SHA-256：`3BFC7D2BB5E141495FDC03BE1BA67232ADA99E79BCA9563BA42B0BDE041B9731`
- 1:1000 万压缩包 SHA-256：`DD787FD7F24A58A9811D9D47EE5D579F315F3B140C5859F9DB9B475E4F2641B9`
- 旧项目压缩包 SHA-256：`73597C784B740064999F45F04846EA1B0ABEAFF173A594DB7C15D906F7A05010`

## 资产 manifest 最低字段

`id`, `sourcePath`, `sourceSha256`, `sourcePublisher`, `editionOrScale`, `createdAt`, `reviewNumber`, `license`, `attribution`, `crsOrControlPoints`, `conversionTool`, `conversionVersion`, `derivedFiles`, `notes`。

## 不应加入的素材依赖

不下载一张“已经带地形和中国边界的成品图片”作为最终底图，不使用未经授权的商业字体，不使用 AI 生成的中国轮廓、行政区或岛屿，不为 MVP 引入没有数据叙事价值的云图和复杂 3D 资产。
