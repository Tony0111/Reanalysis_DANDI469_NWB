# DANDI 000469 Sternberg 单神经元再分析

本项目对 DANDI 000469 的 Sternberg 工作记忆任务人类单神经元 NWB 数据进行可复现再分析。当前版本已完成全量数据的主分析，并按初步冻结规则保留了代码、原始数据布局、结果和审计记录。

项目的主问题是：在每个可兼容 session 内，第一张编码图片出现后，单元放电率是否高于图片出现前的基线。结论必须以 session 为分析边界解释，不能将所有 session 的 trial 或 unit 直接拼接为一个总体检验。

## 当前状态

- 原始全量数据：41 个 NWB 文件，位于 `raw/all/000469/`。
- 当前主结果：`results/primary-v2-all/`，已完成 21 个兼容 `ses-2` session 的独立数值分析。
- 不兼容 session：20 个 `ses-1` 文件完整可读，但缺少当前主问题要求的三项 Encoding1 事件字段，已在数值分析前明确排除并留下审计记录。
- 历史结果：`results/primary-v1/` 和 `results/exploratory-v1/` 均保留，不会被全量分析改写。
- 冻结边界：当前主分析的时间窗、统计方案、结果文件和代表性图已固定。新的研究问题应建立新版本结果目录。

## 研究问题与主分析口径

每个兼容 session 独立完成下列比较：

| 项目 | 固定定义 |
|---|---|
| 对齐事件 | `timestamps_Encoding1`，即第一张编码图片开始出现 |
| 基线窗 | `[-0.8, 0.0)` 秒 |
| 反应窗 | `[0.2, 1.0)` 秒 |
| 单位内特征 | 每个保留 `unit x trial` 的反应窗放电率减基线窗放电率，单位为 Hz |
| 单元检验 | session 内 10,000 次单尾配对置换检验，备择为图片后放电率更高 |
| 不确定性 | 5,000 次 bootstrap 置信区间 |
| 多重比较 | 仅在同一 session 内做 BH-FDR，阈值 `q < 0.05` |
| 随机种子 | `20260901` |
| 数据汇总限制 | 不跨 session 合并 trial；不将 unit 当作独立受试者做总体推断 |

主分析不导入 Matplotlib。数值结果确认后，才在单独的 `bci-plot` 环境中为少量代表性 unit 生成 raster/PSTH，图只用于时间对齐 QC 和结果展示，不代替预先定义的统计检验。

## 结论

### 单 session 基线结论

`single-session-baseline/` 固定保存 `sub-20_ses-2` 的教学和回归基线。该 session 在当前主分析口径下保留 135 个 trial、5 个通过 QC 的 unit。

- 5 个 unit 在 session 内 FDR 校正后均未显著（`q < 0.05` 的 unit 数为 0）。
- 5 个 unit 的平均放电率差均值为 `0.065 Hz`，中位数为 `0.102 Hz`；这不是显著的 session 内总体检验，也不能推广到其他受试者。
- 该结果说明：对于 `sub-20_ses-2`，在当前固定时间窗和单尾检验下，没有足够证据支持图片出现后存在一致的放电率升高。

完整的单元统计见 `single-session-baseline/unit_level_statistics.csv`；其数值与全量版本中 `results/primary-v2-all/sub-20_ses-2/` 的同名结果一致。

### 全量主分析结论

41 个 NWB 文件中，21 个 `ses-2` 文件具有当前定义所需的 `timestamps_FixationCross`、`timestamps_Encoding1` 和 `timestamps_Encoding1_end` 字段，因此进入主分析。20 个 `ses-1` 文件缺少这三项字段，不能在不改变事件定义的前提下套用本主分析，已标记为 `excluded_incompatible_schema`。

21 个完成 session 合计保留 2,672 个 trial、901 个 QC unit。这些总数仅描述数据规模，并不构成跨 session 的合并检验。

- 16 个 session 含有至少一个 session 内 FDR 显著的 unit。
- 共有 101 个 unit 满足 `q < 0.05`；由于检验的备择是图片后升高，这 101 个 unit 的平均放电率差均为正。
- 不同 session 的整体单位效应方向并不一致：有的 session 的 unit 平均差为正，有的为负，也有多个 session 没有 FDR 显著 unit。
- 因此，当前证据支持“部分 session 中存在图片后放电率升高的 unit”，但不支持写成“所有 session 在图片后均增强”，也不能从本项目得出跨受试者的总体显著性结论。

各 session 的 trial 数、QC unit 数、显著 unit 数和效应描述见 `results/primary-v2-all/descriptive_summary.md` 与 `results/primary-v2-all/session_summary.csv`。

## 项目结构

```text
Reanalysis_DANDI469_NWB/
|-- raw/                                  原始 NWB 数据，不提交到 Git
|   |-- all/000469/                       正式全量输入：41 个 NWB 文件
|   |   `-- sub-*/sub-*_ses-*_ecephys+image.nwb
|   `-- pilot-legacy/                     历史 pilot 副本：8 个文件
|                                            与全量集对应文件逐字节相同，仅供复现旧工作
|
|-- src/                                  可复用、无命令行副作用的分析核心
|   |-- data_paths.py                     统一选择全量数据根目录并定位 NWB 文件
|   |-- sternberg_primary.py              主分析的读取、QC、特征和统计实现
|   `-- __init__.py                       Python 包标识
|
|-- scripts/                              可直接运行的工作流入口
|   |-- inventory_sessions.py             扫描 NWB 结构，写出 session inventory
|   |-- run_primary_all.py                按 session 顺序完成全量数值主分析
|   |-- run_one_session.py                运行一个指定兼容 session 的主分析
|   |-- summarize_primary_v2_all.py       汇总 primary-v2-all 的 session/subject/unit 描述结果
|   |-- plot_session_qc.py                为单个 session 绘制少量 raster/PSTH
|   |-- run_representative_plots_v2.py    顺序生成 v2 的代表性图，不批量绘制全部 unit
|   |-- summarize_primary_results.py      primary-v1 的历史汇总入口
|   |-- run_representative_plots.py       primary-v1 的历史绘图入口
|   |-- inventory_encoding1_picids.py     图片 ID 探索性分析的结构盘点
|   `-- run_encoding1_picid_exploration.py 图片 ID 探索性分析入口
|
|-- results/                              版本化分析产物；已有版本不覆盖
|   |-- primary-v2-all/                   当前正式全量主分析结果
|   |-- primary-v1/                       历史 4-session pilot 主分析结果
|   `-- exploratory-v1/                   与主分析分开的图片 ID 探索结果
|
|-- single-session-baseline/              sub-20_ses-2 的单 session 教学/回归基线
|   |-- read_data.ipynb                   结构检查、QC、可视化和统计 notebook
|   |-- data_dictionary.json              notebook 的字段映射与结构检查摘要
|   `-- unit_level_statistics.csv         5 个基线 unit 的统计结果
|
|-- docs/                                 设计、计划、审计和冻结文档
|   |-- project_top_design.md             研究问题、QC、统计和可复现性设计
|   |-- multi_session_analysis_plan.md    多 session 工作计划及实际执行记录
|   |-- experiment_log.md                 输入、命令、环境、排除和验证的时间序列日志
|   `-- project_freeze_plan.md            冻结范围、验收条件和后续变更规则
|
|-- requirements.txt                      运行所需 Python 依赖
|-- .gitignore                            排除 raw 数据、NWB、缓存和本地临时文件
`-- README.md                             本说明
```

### 原始数据目录

`raw/all/000469/` 是后续正式分析唯一应使用的输入根目录。`src/data_paths.py` 会优先选择该路径，只有完整数据不存在时才回退到 `raw/pilot-legacy/`，以支持历史单 session 材料的可读性。

`raw/pilot-legacy/` 中的 8 个 NWB 是此前 pilot 工作留下的副本，已通过 SHA-256 确认与 `raw/all/000469/` 中对应文件完全相同。它们不能与全量目录一起扫描或混合分析。`raw/`、`*.nwb` 和缓存目录由 `.gitignore` 排除，GitHub 仓库只保存代码、文档和分析产物。

### `src/` 与 `scripts/` 的关系

`src/` 负责“如何分析”：包含可在 Python 中导入的函数与数据结构，不决定批处理范围、命令行参数或绘图数量。

`scripts/` 负责“何时、对哪些文件分析”：它们调用 `src/`，处理命令行入口、按 session 顺序执行、写入结果目录和记录日志。这个分层让相同的分析核心可以被全量脚本、单 session 脚本和 notebook 复用，同时避免把 I/O 和批处理逻辑混入统计实现。

全量主流程如下：

```text
raw/all/000469/
        |
        v
scripts/inventory_sessions.py
        |
        v
results/primary-v2-all/session_inventory.csv
        |
        v
scripts/run_primary_all.py  -->  src/sternberg_primary.py
        |
        +--> 每个兼容 session 的 QC、features、statistics
        +--> 不兼容或失败 session 的明确审计记录
        |
        v
scripts/summarize_primary_v2_all.py
        |
        +--> session_summary.csv
        +--> subject_level_descriptive_summary.csv
        +--> unit_statistics_all_sessions.csv
        `--> descriptive_summary.md
```

## 结果目录说明

### 版本目录

| 目录 | 范围 | 角色 |
|---|---|---|
| `results/primary-v2-all/` | 21 个兼容 `ses-2` session | 当前正式全量主分析 |
| `results/primary-v1/` | 4 个历史 pilot session | 回归基线与旧结果复现 |
| `results/exploratory-v1/encoding1_picid_train_test/` | 图片 ID 的训练/测试探索 | 探索性结果，不作为主结论 |

### `primary-v2-all/` 顶层文件

| 文件 | 内容与用途 |
|---|---|
| `session_inventory.csv` | 41 个 NWB 的相对路径、SHA-256、subject/session 标识、trial/unit/electrode 数量和关键字段存在性 |
| `session_run_log.csv` | 每个 inventory session 的状态、时长、QC 数量和显著 unit 数 |
| `session_failures.csv` | 排除或失败 session 的原因；当前 20 行均为事件字段结构不兼容，不是文件读写错误 |
| `session_failures/sub-*_ses-1/failure.json` | 每个被排除 session 的机器可读审计记录 |
| `batch_manifest.json` | 本批次输入、输出、固定参数、完成数与排除数 |
| `session_summary.csv` | 每个完成 session 的保留 trial、QC unit、显著 unit 和 unit 效应描述 |
| `subject_level_descriptive_summary.csv` | 按 subject 并列的描述性汇总；不是跨 subject 推断统计 |
| `unit_statistics_all_sessions.csv` | 21 个 session 的 unit 统计纵向表，仅用于描述和二次检查 |
| `descriptive_summary.md` | 当前全量分析的中文可读汇总 |
| `plot_runs/*.log` | 代表性绘图的运行日志 |

### 每个完成 session 的文件

每个 `results/primary-v2-all/sub-*_ses-2/` 目录均对应一个独立完成的 session：

| 文件 | 内容与用途 |
|---|---|
| `session_metadata.json` | 输入文件、SHA-256、subject/session、NWB 标识、原始字段名与保留 trial/unit 数 |
| `analysis_parameters.json` | 本 session 使用的时间窗、随机种子、置换/Bootstrap 次数和 FDR 阈值 |
| `trial_qc.csv` | 每个 trial 的事件时间顺序、窗口覆盖和保留/排除判断 |
| `unit_qc.csv` | 每个 unit 的 spike 完整性、活跃 trial 数、脑区映射和保留判断 |
| `unit_trial_features.csv` | 每个保留 `unit x trial` 的基线/反应 spike count、Hz 与差值 |
| `final_count_qc.csv` | 保留 unit 的 ISI 与 spike count 边界检查 |
| `unit_level_statistics.csv` | unit 内置换 p、bootstrap CI、效应描述、FDR q 与显著性标记 |
| `figures/*.png` | 仅少量代表性 unit 的 raster/PSTH；不存在则表示该 session 未被选作展示图 |

### 探索性图片 ID 结果

`results/exploratory-v1/encoding1_picid_train_test/` 保存独立于主分析的图片身份探索。每个 session 的 `trial_split.csv` 记录训练/测试切分，`unit_picture_identity_statistics.csv` 记录图片 ID 统计；顶层 `session_summary.csv`、`unit_picture_identity_statistics_all_sessions.csv` 和 `exploratory_summary.md` 提供汇总。该目录中的发现不得替代 `primary-v2-all/` 的主分析结论。

## 复现全量主分析

数值处理在 `bci` 环境完成。一次只运行一个 Python 分析进程；不要同时启动多个批处理脚本。

```powershell
conda activate bci
cd E:\BCI-workstation\NWB
python .\Reanalysis_DANDI469_NWB\scripts\inventory_sessions.py
python .\Reanalysis_DANDI469_NWB\scripts\run_primary_all.py
python .\Reanalysis_DANDI469_NWB\scripts\summarize_primary_v2_all.py
```

运行前应先检查 `results/primary-v2-all/session_inventory.csv`；只有具有固定 Encoding1 事件定义的 session 才能进入当前主流程。某个 session 若失败，`run_primary_all.py` 会在 `session_run_log.csv`、`session_failures.csv` 和对应 `failure.json` 中记录原因，不会静默跳过。

数值结果确认无误后，才在 `bci-plot` 环境中运行少量代表性绘图：

```powershell
conda activate bci-plot
cd E:\BCI-workstation\NWB
python .\Reanalysis_DANDI469_NWB\scripts\run_representative_plots_v2.py
```

该绘图入口顺序处理选定 session 中的少量 unit；不要改造成一次生成所有 unit 的大型 raster/PSTH 图。

## 复现单 session 基线

`single-session-baseline/read_data.ipynb` 优先使用全量目录中的 canonical 文件 `sub-20_ses-2_ecephys+image.nwb`，仅在完整数据目录不存在时回退至 `raw/pilot-legacy/`。在项目根目录执行：

```powershell
conda activate bci
jupyter nbconvert --to notebook --execute --inplace .\single-session-baseline\read_data.ipynb
```

notebook 的新输出会写回 `single-session-baseline/`，因此运行前应确认自己需要更新该教学/回归基线。

## 文档与变更规则

| 文档 | 作用 |
|---|---|
| `docs/project_top_design.md` | 研究问题、QC、统计和可复现性设计 |
| `docs/multi_session_analysis_plan.md` | 多 session 分析计划与实际执行记录 |
| `docs/experiment_log.md` | 每个阶段的输入、命令、输出、排除原因和验证结论 |
| `docs/project_freeze_plan.md` | 冻结边界、验收条件与后续分析的版本规则 |

后续若要处理 `ses-1` 的不同事件结构、比较图片 ID、记忆负荷、正确率或脑区效应，应创建新的结果版本和对应分析计划。不得修改当前 `primary-v2-all/` 中已冻结的主分析文件来承载新的假设或参数。

## 数据来源与范围

原始数据来自 DANDI 000469 发布版本 `0.240123.1806`，许可为 CC BY 4.0。本项目使用发布 NWB 中已经整理好的 `units` 数据，不重新进行 spike sorting。
