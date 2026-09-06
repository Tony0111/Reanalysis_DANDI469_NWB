# 项目初步冻结计划

更新时间：2026-09-06

## 目的

将已经完成的 DANDI 000469 Sternberg 单神经元主分析整理为可复现、可审计且不再被日常修改的基线。冻结不代表研究问题已经全部完成；它表示当前的输入、代码、参数、结果和解释边界已经明确，新的分析必须以新版本开展。

## 当前冻结范围

1. 原始数据：`raw/all/000469/` 下的 41 个 NWB 是正式全量输入。`raw/pilot-legacy/` 的 8 个历史文件与完整集对应文件 SHA-256 完全相同，仅为复现 `primary-v1` 留存，不参与全量分析。
2. 主分析代码：`src/data_paths.py` 与 `src/sternberg_primary.py`，以及调用它们的 `scripts/inventory_sessions.py`、`run_primary_all.py`、`summarize_primary_v2_all.py`。
3. 冻结参数：Encoding1 对齐；baseline `[-0.8, 0.0)` s；response `[0.2, 1.0)` s；最少 10 个活动 trial；10,000 次单尾配对置换；5,000 次 bootstrap；session 内 BH-FDR `q < 0.05`；随机种子 `20260901`。
4. 正式全量结果：`results/primary-v2-all/`。其中 21 个兼容 `ses-2` session 已完成数值分析；20 个 `ses-1` session 因缺少固定事件字段而明确排除。
5. 历史可复现结果：`results/primary-v1/`、`results/exploratory-v1/` 与 `single-session-baseline/`。它们保留原始产物，不被 v2 覆盖。
6. 绘图：仅保留少量代表性 raster/PSTH 作为事件对齐 QC；不批量生成所有 unit 的大型图。

## 冻结验收

- [x] 完整输入清单有 41 行，并保存文件哈希与字段兼容性。
- [x] 8 个 pilot 副本已核验为精确重复文件，并从 `raw/` 顶层归档至 `raw/pilot-legacy/`。
- [x] 21 个兼容 session 的每个结果目录均包含 metadata、parameters、trial/unit QC、unit-trial features、最终 count QC 与 unit 统计。
- [x] 20 个不兼容 session 均在运行日志和排除日志中有明确原因。
- [x] `sub-20_ses-2` 的 v2 unit 统计 CSV 与 `primary-v1` 基线完全一致。
- [x] session、subject 和 unit 描述性汇总已生成；未进行 trial 池化或跨 subject 总体显著性检验。
- [x] 3 个代表性 session 的 9 张 raster/PSTH 已在 `bci-plot` 中顺序生成并检查。
- [x] README 已记录目录、代码边界和所有正式 JSON/CSV 的含义。

## 冻结后的维护规则

1. 不修改 `raw/` 内的 NWB 内容，不删除 `pilot-legacy/`，也不将其与完整集混合输入。
2. 不改写 `results/primary-v1/`、`results/primary-v2-all/` 或 `results/exploratory-v1/` 内的结果文件。修正代码或改变参数时，创建新的结果版本目录。
3. 新增主分析问题必须先写入一个独立计划，明确事件定义、分析层级、排除规则、统计方向和多重比较范围，再运行数据。
4. `ses-1` 只能在建立并验证独立事件映射后纳入新的分析版本，不能强行沿用当前 Encoding1 窗口。
5. `scripts/` 可以增加新的编排入口；影响主分析结果的可复用逻辑应放在 `src/`，并保留无 Matplotlib 的数值路径。
6. 每次新增正式运行都在 `docs/experiment_log.md` 记录输入、命令、输出、失败或排除原因和验收结论。

## 冻结后的候选工作

1. 为 `ses-1` 建立字段映射并提出独立、可比较的问题。
2. 在预先定义规则后研究负荷、正确率或脑区，而不是从当前结果反向挑选窗口。
3. 将图片 ID 的训练/测试探索结果扩展到更多兼容 session，并保持它与主分析的明确区分。
4. 如需要跨 subject 推断，先确定可比较的 subject 层效应、缺失 session 处理和模型假设；当前数据不支持把 unit 或 trial 当作独立受试者。
