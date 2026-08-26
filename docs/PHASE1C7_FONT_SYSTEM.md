# Phase 1C-7：全站中文字体系统与品牌标题

日期：2026-08-26

## 字体审计

修改前正文使用 `Segoe UI`, `Microsoft YaHei`, `sans-serif`，品牌主标题使用 `STKaiti/KaiTi`，不同区域的中文、数字和辅助说明没有统一的字体回退策略。字号分布从 8px 阶段摘要到 43px 品牌标题，部分数字使用 300/350 的过细字重。

## 字体方案

建立三组 CSS 变量，均采用同一组可回退宋体：

```css
"Noto Serif SC", "Source Han Serif SC", "STSong", "SimSun", serif
```

- `--font-display`：品牌标题“曦行神州”和“万里晨光”。主标题 SemiBold，副标题 Regular。
- `--font-ui`：项目说明、面板标题、城市名、标签、按钮和辅助说明。
- `--font-number`：当前时间、日出时间、时间差、角度、经纬度、日期和时间轴读数。

未新增字体文件、未下载外部字体，也未引入新的许可证依赖；实际字体由浏览器按回退栈选择。

## 天文阶段摘要

横向阶段摘要由六项调整为四项，仅保留：民用晨光、日出、正午、日落；移除“天文晨光”和“航海晨光”。上部竖向阶段列表仍保留全部阶段和既有数据逻辑。

## 可读性调整

品牌标题保持原位置和暖金色，仅替换为展示型宋体。关键数字使用宋体常规字重，城市标签和面板标题提升到 Regular/Medium，保留原有颜色层级和布局尺寸。没有使用负字距或大面积发光补偿。

## 验收

使用本地 HTTP 页面检查 1280 × 800、1440 × 900、1920 × 1080：品牌区、右侧栏、地图城市标签、经纬度刻度、时间轴和季节按钮均保持在容器内，无新增控制台错误。阶段摘要横向显示四项且不溢出。

截图：

- `docs/screenshots/phase1c7-fonts-1440.png`
- `docs/screenshots/phase1c7-fonts-1920.png`

截图 SHA-256：

- 1440: `7B692C81DC6A2E92D877898A56A8EECEC2E15BE8DB6678FD3630000A79478A96`
- 1920: `869132140FB3C97DD48A6F72C19E651A7B7A35DECFE82CB436CA1339E3BEA66B`

## 官方资产完整性

本阶段未修改地图几何或官方 SVG。复核哈希：

- `official-master.eps`: `8709AA9590ACAEF2926FAB9AD6979665C7CAF8469EC7186EA33EDEB9838368CC`
- `official-audit.svg`: `D661148E382F91D3972D0825F70EBF2FC45DE995CD99D489F865229FDC5514E0`
- `clean-map.svg`: `51D3EB706ECAB3E0C07878ECC203BDD81DF52A4A9474766BF3B05515043C9D72`
- `presentation-map.svg`: `6B3D0A8DD100D809D5682B945C9553432A6BB289A4AF6B4A7FB35C0F003F420F`
- `official-south-sea.svg`: `2D7EA15DD23DBBB65DD696AF4342D375E5F8A8CC88E9B7C21FB5C1F67194328D`

## 已知问题

如果操作系统未安装首选宋体，浏览器会回退到 `STSong`、`SimSun` 或通用 serif，字形细节可能略有差异；不影响布局、数据或地图坐标。1920px 截图受浏览器自动化画布物理宽度限制，已以 DOM 视口和布局矩形完成 1920 × 1080 验收。
