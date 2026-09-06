# Encoding1 图片 ID 探索性结果

分析执行时间：2026-09-06 14:59:39 +08:00

## Session 汇总

| session | 保留 trial | QC unit | 测试集 q<0.05 unit | unit 测试集差值均值 (Hz) |
|---|---:|---:|---:|---:|
| sub-1_ses-2_ecephys+image.nwb | 135 | 40 | 0 | 0.181 |
| sub-11_ses-2_ecephys+image.nwb | 135 | 74 | 1 | 0.145 |
| sub-20_ses-2_ecephys+image.nwb | 135 | 5 | 0 | -0.089 |
| sub-21_ses-2_ecephys+image.nwb | 135 | 20 | 1 | 0.379 |

`unit 测试集差值`是训练集选择的候选图片在测试集的平均 `response - baseline` 放电率，减去测试集中其余四张图片的对应平均值。它只描述该 session 的 unit 结果，不能作为跨 subject 的总体效应。

## 通过 Session 内 FDR 的 Unit

- `sub-11_ses-2_ecephys+image.nwb`，unit 36：训练集选择图片 ID 5；测试集候选图片均值 3.393 Hz，其他图片均值 -0.250 Hz，差值 3.643 Hz，单尾置换 p=0.000100，session 内 FDR q=0.007399。
- `sub-21_ses-2_ecephys+image.nwb`，unit 1：训练集选择图片 ID 1；测试集候选图片均值 3.304 Hz，其他图片均值 -0.341 Hz，差值 3.644 Hz，单尾置换 p=0.000100，session 内 FDR q=0.002000。

## 解读边界

- 候选图片仅由训练 trial 选出，统计检验只使用独立测试 trial，因此本结果避免了同一 trial 同时用于选择和验证的泄漏。
- FDR 只在各自 session 的 unit 内校正；这两个 unit 不能合并为跨 subject 的总体 p 值。
- 这是探索性结果，不修改 `primary-v1` 的时间窗、QC、主检验或主结论。应在新的独立数据中重复后，才可支持更强的图片选择性结论。
