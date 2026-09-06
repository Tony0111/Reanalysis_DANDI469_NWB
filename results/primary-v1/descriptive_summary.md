# Primary-v1 跨 Session 描述性汇总

生成时间：2026-09-06T14:43:13+08:00

## 分析范围

本报告只包含 4 个具有当前固定事件定义的 `ses-2` Sternberg session。每个 session 的 baseline 为 `[-0.8, 0.0)` 秒，response 为 `[0.2, 1.0)` 秒；`mean_delta_hz` 是 unit 内每个 trial 的 response firing rate 减 baseline firing rate 后再取平均。

这些数据按 session 独立分析，未把不同 session 的 trial 合并，也没有计算跨 subject 的总体 p 值。当前每位 subject 只纳入了 1 个兼容 session，因此本报告只能描述结果，不能作为总体人群结论。

## Session 结果

| session | 保留 trial | QC unit | q<0.05 unit | 正向 mean delta unit | unit mean delta 均值 (Hz) | unit mean delta 中位数 (Hz) |
|---|---:|---:|---:|---:|---:|---:|
| sub-1_ses-2_ecephys+image.nwb | 135 | 40 | 0 | 15 | -0.196 | -0.056 |
| sub-11_ses-2_ecephys+image.nwb | 135 | 74 | 14 | 51 | 0.110 | 0.171 |
| sub-20_ses-2_ecephys+image.nwb | 135 | 5 | 0 | 4 | 0.065 | 0.102 |
| sub-21_ses-2_ecephys+image.nwb | 135 | 20 | 0 | 11 | -0.085 | 0.042 |

总计：4 个 session，540 个保留 trial，139 个 QC unit。这里的总计只用于清点数据规模，不构成把所有 trial 或 unit 当作独立受试者的统计检验。

## Subject 并列结果

| subject | 已分析 session | 保留 trial | QC unit | q<0.05 unit | session-level unit mean delta (Hz) |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 135 | 40 | 0 | -0.196 |
| 11 | 1 | 135 | 74 | 14 | 0.110 |
| 20 | 1 | 135 | 5 | 0 | 0.065 |
| 21 | 1 | 135 | 20 | 0 | -0.085 |

## 当前可作的描述

- 结果在不同 session 之间存在明显异质性：sub-11_ses-2 有 14 个 session 内 FDR 显著 unit，而其余 3 个 session 均为 0 个。
- 4 个 session 的 unit-level 平均效应方向并不一致，因此不能写成“所有 session 在图片后都增强”或“所有 session 都不响应”。
- raster/PSTH 已作为时间对齐 QC 通过；它们帮助确认事件对齐没有系统性错误，但不替代预先定义的置换检验和 FDR 结果。

## 后续推断计划（未执行）

1. 不把 540 个 trial 合并后进行一次总体 t 检验，也不把 139 个 unit 当作 139 位独立受试者。
2. 若后续为每位 subject 建立了可比的额外 session 事件映射，先在 subject 内汇总 session-level 效应，再以 subject 为分析单位预先定义跨 subject 描述或推断。
3. 在样本量仍只有 4 位 subject 时，优先报告每位 subject 的效应和不确定性；任何总体 p 值都应明确标注探索性、统计功效有限。
4. 图片 ID、记忆负荷、正确率和脑区问题留到阶段 F，并单独预注册/记录分析单位、训练测试划分和多重比较范围。
