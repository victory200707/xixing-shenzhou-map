# Phase 1A 分析产物

此目录只保存官方候选 EPS 的只读分析副本和审查输出，不是网站运行时资产。

## 来源

- `4o28b0625501ad13015501ad2bfc0240b/`：1:2200 万 Illustrator EPS。
- `4o28b0625501ad13015501ad2bfc0696b/`：1:740 万 CorelDRAW EPS。
- `4o28b0625501ad13015501ad2bfc2190b/`：1:1000 万 CorelDRAW X8 EPS。

每个目录中的 EPS 都从 Downloads 压缩包解出，没有改写源字节。PNG 是 Ghostscript `-dEPSCrop -r96` 生成的人工核验预览；PDF/normalized PostScript 是转换能力测试产物，不能作为最终地图来源。

## 解释限制

- `%Note: Object`、bbox、PostScript 命令和颜色操作是词法/结构指标，不等于行政区、河流或岛屿的权威 feature 数量。
- 三份 EPS 的 CRS/投影控制点尚未从源资料确认，当前不生成 GeoJSON。
- 图层没有被假设为语义正确；对象分类必须在用户确认 Master 后逐层叠加原图核验。

首次技术比较见 `docs/MAP_MASTER_SELECTION.md`，但其唯一 Master 建议已由 Phase 1A.5 撤回。参考图一致性和南海对象复核见 `docs/PHASE1A5_REFERENCE_FIT.md`；当前不冻结 Master、不生成最终地图资产。
