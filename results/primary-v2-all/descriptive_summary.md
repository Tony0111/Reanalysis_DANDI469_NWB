# Primary-v2-all 描述性汇总

生成时间：2026-09-06T23:00:14+08:00

本报告汇总各个 session 的独立分析结果。不同 session 的 trial 没有合并，
也没有把 unit 或 trial 当作独立受试者进行总体推断检验。

## 分析范围

- Inventory 文件记录数：41
- 成功完成的兼容 session：21
- 排除或失败的 session：20
- 完成 session 的保留 trial 总数（仅作数据量描述）：2672
- 完成 session 的 QC unit 总数（仅作数据量描述）：901

当前纳入的是具有固定 Encoding1 事件定义的 21 个 `ses-2` session。20 个
`ses-1` session 因缺少 `timestamps_FixationCross`、`timestamps_Encoding1` 和
`timestamps_Encoding1_end`，没有套用本 primary 分析。

## Session 结果

| session | 保留 trial | QC unit | q<0.05 unit | 正向平均差值 unit | unit 平均差值均值 (Hz) | unit 平均差值中位数 (Hz) |
|---|---:|---:|---:|---:|---:|---:|
| sub-1_ses-2_ecephys+image.nwb | 135 | 40 | 0 | 15 | -0.196 | -0.056 |
| sub-10_ses-2_ecephys+image.nwb | 135 | 28 | 6 | 15 | 0.008 | 0.028 |
| sub-11_ses-2_ecephys+image.nwb | 135 | 74 | 14 | 51 | 0.110 | 0.171 |
| sub-12_ses-2_ecephys+image.nwb | 135 | 22 | 2 | 10 | 0.102 | -0.023 |
| sub-13_ses-2_ecephys+image.nwb | 135 | 58 | 13 | 41 | 0.180 | 0.148 |
| sub-14_ses-2_ecephys+image.nwb | 135 | 65 | 9 | 40 | 0.192 | 0.111 |
| sub-15_ses-2_ecephys+image.nwb | 135 | 55 | 1 | 24 | -0.039 | -0.019 |
| sub-16_ses-2_ecephys+image.nwb | 108 | 33 | 4 | 20 | -0.047 | 0.058 |
| sub-17_ses-2_ecephys+image.nwb | 135 | 13 | 0 | 5 | -0.442 | -0.019 |
| sub-18_ses-2_ecephys+image.nwb | 135 | 118 | 10 | 71 | -0.083 | 0.042 |
| sub-19_ses-2_ecephys+image.nwb | 108 | 11 | 1 | 9 | 0.281 | 0.104 |
| sub-2_ses-2_ecephys+image.nwb | 135 | 31 | 2 | 15 | -0.198 | -0.046 |
| sub-20_ses-2_ecephys+image.nwb | 135 | 5 | 0 | 4 | 0.065 | 0.102 |
| sub-21_ses-2_ecephys+image.nwb | 135 | 20 | 0 | 11 | -0.085 | 0.042 |
| sub-3_ses-2_ecephys+image.nwb | 135 | 28 | 7 | 14 | -0.117 | 0.009 |
| sub-4_ses-2_ecephys+image.nwb | 135 | 76 | 5 | 34 | 0.024 | -0.051 |
| sub-5_ses-2_ecephys+image.nwb | 135 | 50 | 2 | 26 | -0.172 | 0.032 |
| sub-6_ses-2_ecephys+image.nwb | 108 | 35 | 4 | 15 | -0.074 | -0.035 |
| sub-7_ses-2_ecephys+image.nwb | 108 | 22 | 0 | 19 | 0.173 | 0.191 |
| sub-8_ses-2_ecephys+image.nwb | 108 | 74 | 17 | 46 | -0.064 | 0.127 |
| sub-9_ses-2_ecephys+image.nwb | 107 | 43 | 4 | 29 | 0.130 | 0.070 |

## 受试者并列结果

| 受试者 | 分析 session 数 | 保留 trial | QC unit | q<0.05 unit | session 平均效应 (Hz) |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 135 | 40 | 0 | -0.196 |
| 10 | 1 | 135 | 28 | 6 | 0.008 |
| 11 | 1 | 135 | 74 | 14 | 0.110 |
| 12 | 1 | 135 | 22 | 2 | 0.102 |
| 13 | 1 | 135 | 58 | 13 | 0.180 |
| 14 | 1 | 135 | 65 | 9 | 0.192 |
| 15 | 1 | 135 | 55 | 1 | -0.039 |
| 16 | 1 | 108 | 33 | 4 | -0.047 |
| 17 | 1 | 135 | 13 | 0 | -0.442 |
| 18 | 1 | 135 | 118 | 10 | -0.083 |
| 19 | 1 | 108 | 11 | 1 | 0.281 |
| 2 | 1 | 135 | 31 | 2 | -0.198 |
| 20 | 1 | 135 | 5 | 0 | 0.065 |
| 21 | 1 | 135 | 20 | 0 | -0.085 |
| 3 | 1 | 135 | 28 | 7 | -0.117 |
| 4 | 1 | 135 | 76 | 5 | 0.024 |
| 5 | 1 | 135 | 50 | 2 | -0.172 |
| 6 | 1 | 108 | 35 | 4 | -0.074 |
| 7 | 1 | 108 | 22 | 0 | 0.173 |
| 8 | 1 | 108 | 74 | 17 | -0.064 |
| 9 | 1 | 107 | 43 | 4 | 0.130 |

## 排除与失败记录

完整审计记录见 `session_run_log.csv` 和 `session_failures.csv`。这些 session
不是因为文件读取失败而排除，而是因为事件字段结构与预先固定的 Encoding1
对齐定义不一致。它们保留在 inventory 和排除日志中，没有被静默跳过。
