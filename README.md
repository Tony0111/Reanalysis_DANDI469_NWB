# Reanalysis_DANDI469_NWB

基于公开 NWB 数据（DANDI 000469）的人体侵入式视觉工作记忆单神经元数据的可复现二次分析项目。

> 这是**二次分析**项目，不是新的数据采集实验。目标是把"下载公开 NWB → 结构检查 → 数据字典 → trial/unit QC → 事件对齐 → 窗口放电率 → 单元级统计（置换 / bootstrap / FDR）→ 出图"整条分析链条做成可复现、可核查的流程。

## 主要研究问题

在一个 Sternberg 工作记忆 session 中，**QC 合格的单个神经元在第一张编码图片呈现后的放电率，是否高于同一 trial 内的 fixation 基线？**

- 基线窗：`[encoding_onset − 0.8, encoding_onset)`（fixation，0.8 s）
- 响应窗：`[encoding_onset + 0.2, encoding_onset + 1.0)`（0.8 s）
- 主要推断单位：unit；trial 是 unit 内的重复观测。
- 统计：unit 内配对置换检验（10,000 次）、bootstrap 95% CI（5,000 次）、Benjamini–Hochberg FDR（q<0.05）。
- 随机种子：`20260901`。

## 数据来源（不在本仓库内）

原始 NWB 文件**不提交到 git**（体积约 25 MB，且为 DANDI 公开数据）。运行 notebook 前，请从 DANDI 下载并放到本目录根：

- DANDI 数据集：`000469`（发布版本 `0.240123.1806`，许可证 CC BY 4.0）
- 数据论文：Human single-neuron recordings during a working memory task（PMC10796636）
- 资产路径/文件名：`sub-20_ses-2_ecephys+image.nwb`（约 25,582,000 bytes）
- 下载后放置：`Reanalysis_DANDI469_NWB/sub-20_ses-2_ecephys+image.nwb`

作者公开代码：https://github.com/rutishauserlab/workingmem-release-NWB

## 本 session 的关键结果（milestone 6）

对 5 个 QC 合格 unit、135 个 trial：

- unit 0–4 的 `mean response − baseline` 差值：0.213 / 0.241 / 0.028 / −0.259 / 0.102 Hz。
- 5 个 unit 的置换方向性 p：0.195 / 0.117 / 0.464 / 0.892 / 0.293。
- 5 个 unit 的 bootstrap 95% CI 全部跨越 0。
- BH-FDR（q<0.05）：**0/5 个 unit 显著**。

诚实读图结论：本 session、预先定义的窗口与 QC 规则下，**没有足够证据表明第一张编码图片后的放电率显著高于同一 trial 的 fixation 基线**。此结论只适用于这一个 subject/session，不推广到其他被试。

## 目录内容

| 文件 | 说明 |
|---|---|
| `read_data.ipynb` | 主 notebook：结构检查 → 数据字典 → trial/unit QC → 对齐/raster/PSTH → 窗口放电率 → 置换检验/bootstrap/FDR → 最终图 |
| `project_top_design.md` | 顶层设计与可复现规范（研究问题、参数、里程碑、QC、统计方法、局限） |
| `experiment_log.md` | 实验记录（含一次数据恢复事故与后续改进工作流） |
| `data_dictionary.json` | 字段名到分析名的映射与检查摘要（notebook 自动生成/更新） |
| `unit_level_statistics.csv` | unit 级统计结果表（notebook 自动生成） |
| `requirements.txt` | Python 依赖与版本 |
| `*.nwb`（未提交） | 原始数据，见上方数据来源 |

## 环境与复现

本项目在 conda 环境 `bci`（Python 3.12.13）中运行。依赖见 `requirements.txt`。

```bash
# 创建并激活环境（示例）
conda create -n bci python=3.12
conda activate bci
pip install -r requirements.txt

# 先把 NWB 数据放到本目录（见“数据来源”），再运行 notebook
jupyter nbconvert --to notebook --execute --inplace read_data.ipynb
```

可复现要点：随机种子固定为 `20260901`；时间窗、PSTH bin、置换/bootstrap 次数与 FDR 阈值都记录在 `project_top_design.md` 第 20 节，并在改动结果前冻结。

## 注意事项

- 单元级 FDR 只控制本 session 内跨 unit 的错误发现率，不等于跨患者的确证证据。
- Sternberg 图片来自前期 screening 选择，不能据此无偏估计人群中的"概念细胞"比例。
- 本项目使用作者已提供的 sorted units，不重新做 spike sorting。
