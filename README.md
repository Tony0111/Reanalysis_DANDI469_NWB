# Reanalysis_DANDI469_NWB

基于 DANDI 000469 Sternberg 工作记忆 NWB 数据的人体单神经元二次分析项目。当前版本已完成全量主分析并初步冻结：分析代码、结果、原始数据布局和审计记录均已保留，后续新问题必须写入新的分析版本，不能改写现有结果。

## 当前结论与边界

冻结的主分析比较第一张编码图片出现前的 baseline `[-0.8, 0.0)` s 与出现后的 response `[0.2, 1.0)` s。以 unit 为推断单位，在 session 内进行 10,000 次单尾配对置换检验、5,000 次 bootstrap，并以 BH-FDR 控制该 session 内的多重比较（`q < 0.05`；随机种子 `20260901`）。

完整集有 41 个 NWB 文件。21 个 `ses-2` session 具备当前 Encoding1 事件定义并完成主分析；20 个 `ses-1` session 缺少三个必需事件字段，明确排除在该主问题之外。21 个完成 session 的结果方向存在异质性：16 个 session 内有 FDR 显著的刺激后增强 unit（共 101 个），但没有一致的跨 session 整体效应。不得将全部 trial 或全部 unit 合并为一个总体检验。

## 目录结构

```text
Reanalysis_DANDI469_NWB/
├── raw/
│   ├── all/000469/                 # 全量 41 个 NWB；正式分析的唯一输入
│   └── pilot-legacy/               # 8 个历史 pilot 副本；与全量集逐字节相同
├── src/                            # 可复用、无命令行副作用的分析核心
├── scripts/                        # 可直接运行的工作流入口
├── results/                        # 版本化且不可改写的分析产物
├── single-session-baseline/        # sub-20_ses-2 的教学/复现基线
├── docs/                           # 设计、计划、审计记录与冻结方案
├── requirements.txt
└── README.md
```

`raw/all/000469/` 是后续运行的唯一输入根目录。`raw/pilot-legacy/` 中的 8 个文件仅为历史复现而保留；其 SHA-256 与完整集对应文件完全相同，不能与完整集一起分析。

## `src/` 与 `scripts/` 的关系

`src/` 放可组合的实现，不负责决定批次、输出目录或绘图规模：

| 文件 | 职责 |
|---|---|
| `src/data_paths.py` | 统一选择全量输入根目录、列举 NWB、定位单个 session。 |
| `src/sternberg_primary.py` | 纯数值核心：读取、trial/unit QC、特征构建、置换、bootstrap、FDR 和结构化结果。该模块不导入 Matplotlib。 |

`scripts/` 是调用 `src/` 的可执行入口，负责工作流编排、文件读写和运行日志：

| 脚本 | 用途 |
|---|---|
| `inventory_sessions.py` | 扫描全量数据并生成字段兼容性清单。 |
| `run_primary_all.py` | 按 session 顺序运行全量数值主分析，并记录排除或失败。 |
| `summarize_primary_v2_all.py` | 生成 v2 的 session、subject 和 unit 描述性汇总。 |
| `run_one_session.py` | 对一个指定兼容 session 运行主分析。 |
| `plot_session_qc.py` | 为一个 session 绘制少数 raster/PSTH QC 图；只能在 `bci-plot` 使用。 |
| `run_representative_plots_v2.py` | 顺序调用绘图脚本，为 3 个 v2 代表 session 生成 9 张图。 |
| `inventory_encoding1_picids.py`、`run_encoding1_picid_exploration.py` | 图片 ID 的探索性分析工具。 |
| `summarize_primary_results.py`、`run_representative_plots.py` | `primary-v1` 的历史入口，保留以便复现旧结果。 |

数值处理在 `bci` 环境运行；绘图仅在已激活的 `bci-plot` 环境运行。一次只启动一个 Python 分析进程。

## 结果目录与文件说明

`results/primary-v2-all/` 是当前全量主分析的正式结果；`primary-v1/` 是 4 个 pilot session 的历史基线；`exploratory-v1/` 是与主分析分开的图片 ID 探索结果。各版本结果保留，不相互覆盖。

### 全量运行记录

| 文件 | 内容 |
|---|---|
| `session_inventory.csv` | 41 个 NWB 的相对路径、SHA-256、subject/session、trial/unit/electrode 数和关键字段是否存在。 |
| `session_run_log.csv` | 每个 inventory session 的状态、运行时间、QC 数量和显著 unit 数。 |
| `session_failures.csv` | 排除或失败 session 的原因；当前 20 行均为事件结构不兼容的 `ses-1`。 |
| `session_failures/*/failure.json` | 单个排除或失败 session 的机器可读审计记录。 |
| `batch_manifest.json` | 批处理输入、输出、冻结参数和完成数量。 |
| `session_summary.csv` | 每个完成 session 的 trial/unit 数、显著 unit 数和 unit 效应描述。 |
| `subject_level_descriptive_summary.csv` | 每位 subject 的描述性汇总；不是跨 subject 推断。 |
| `unit_statistics_all_sessions.csv` | 21 个完成 session 的 unit 级统计表纵向合并，仅供描述和二次检查。 |
| `descriptive_summary.md` | 上述结果的中文可读摘要。 |
| `plot_runs/*.log` | 代表性绘图的运行日志。 |

### 每个完成 session 的目录

每个 `results/primary-v2-all/sub-*_ses-2/` 目录都含有：

| 文件 | 内容 |
|---|---|
| `session_metadata.json` | 输入文件、SHA-256、subject/session、NWB 标识符、总/保留 trial 和 unit 数、原始字段名。 |
| `analysis_parameters.json` | 冻结的时间窗、随机种子、置换/bootstrap 次数、FDR 阈值和分析范围。 |
| `trial_qc.csv` | 每个 trial 的时间顺序、窗口覆盖和保留判定。 |
| `unit_qc.csv` | 每个 unit 的 spike 完整性、活动 trial 数、脑区映射和保留判定。 |
| `unit_trial_features.csv` | 每个保留 `unit × trial` 的 baseline/response spike count、Hz 和差值。 |
| `final_count_qc.csv` | 保留 unit 的 ISI 与 spike count 边界检查。 |
| `unit_level_statistics.csv` | unit 内置换 p、bootstrap CI、效应量、FDR q 和显著性。 |
| `figures/*.png` | 少量代表性 raster/PSTH，只用于对齐 QC 和展示。 |

`results/exploratory-v1/encoding1_picid_train_test/` 的 `trial_split.csv` 记录训练/测试切分，`unit_picture_identity_statistics.csv` 记录图片 ID 探索统计；`analysis_parameters.json` 和 `session_metadata.json` 分别记录规则与输入身份。

## 单 session 基线

`single-session-baseline/` 保留 `sub-20_ses-2` 的教学和回归基线：

| 文件 | 内容 |
|---|---|
| `read_data.ipynb` | 单 session 的结构检查、QC、raster/PSTH 和主统计 notebook。它固定读取完整集中的 canonical `sub-20_ses-2`。 |
| `data_dictionary.json` | notebook 输出的字段映射与结构检查摘要。 |
| `unit_level_statistics.csv` | notebook 输出的 5 个基线 unit 统计表。 |

从项目根目录运行该 notebook 时，其新输出会写回该目录：

```powershell
conda activate bci
jupyter nbconvert --to notebook --execute --inplace .\single-session-baseline\read_data.ipynb
```

## 文档与冻结

| 文件 | 用途 |
|---|---|
| `docs/project_top_design.md` | 研究问题、QC、统计和可复现性设计。 |
| `docs/multi_session_analysis_plan.md` | 多 session 分析的原始计划与实际执行记录。 |
| `docs/experiment_log.md` | 包含命令、环境问题、验证和排除原因的时间序列审计日志。 |
| `docs/project_freeze_plan.md` | 当前初步冻结边界、验收条件及后续工作规则。 |

原始 NWB 不提交到 Git；数据来源为 DANDI 000469（发布版本 `0.240123.1806`，CC BY 4.0）。本项目使用发布数据内已整理好的 units，不重新进行 spike sorting。
