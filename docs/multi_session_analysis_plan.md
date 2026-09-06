# 多 Session 数据处理计划与执行记录

更新日期：2026-09-06；归档日期：2026-09-06

> 本文保留为多 session 分析的设计与执行记录。项目初步冻结的范围、目录和后续维护规则见 `project_freeze_plan.md`。

## 当前执行状态

- [x] 阶段 A（pilot）：8 个旧 raw 文件的只读 inventory、SHA-256 和事件 schema 清单。
- [x] 阶段 A-v2（全量）：对 `raw/all/000469/` 下的完整 DANDI 000469 数据生成清单，并输出到 `results/primary-v2-all/`。
- [x] 阶段 B：建立不含 Matplotlib 的纯数值分析核心，并通过 `sub-20_ses-2` 基线复现。
- [x] 阶段 C：顺序完成 21 个兼容 `ses-2` 的数值主分析和独立结果保存。
- [x] 阶段 D：恢复小规模 raster/PSTH 可视化并完成人工时间对齐检查。
- [x] 阶段 E：跨 session/subject 的正式描述性汇总与后续推断计划。
- [~] 阶段 F：第一张编码图片 ID 的探索性分析已在 4 个 session 完成；负荷、正确率和脑区问题尚未开展。

阶段 A-C 的结果位于 `results/primary-v1/`。早期失败尝试的 `results/multi_session/` 已于 2026-09-06 清理，不属于正式结果。

阶段 D 的环境处理结果：数值分析继续使用 `bci`；绘图使用已激活的 `bci-plot`。在 `bci-plot` 中固定 NumPy 1.26.4、Matplotlib 3.10.9 后，增强版 smoke test 和 4 个兼容 session 的代表性图均已成功生成并通过人工检查。绘图命令必须在 `conda activate bci-plot` 后使用 `python` 执行，不能只用环境 Python 的绝对路径，以确保 Conda DLL 路径正确加载。

## 1. 当前状态

### 已完成且可保留的基线分析

- `read_data.ipynb` 已完成 `sub-20_ses-2_ecephys+image.nwb` 的结构检查、字段映射、trial/unit QC、raster/PSTH、window firing rate、置换检验、bootstrap CI 和 session 内 BH-FDR。
- 该 session 的正式结论是：135 个 trial、5 个 QC 合格 unit；在预先定义的 baseline `[-0.8, 0.0)` s 与 response `[0.2, 1.0)` s 中，0/5 个 unit 通过 session 内 FDR (`q < 0.05`)。
- notebook 曾从干净 kernel 全量执行成功。它是后续批处理代码必须复现的“基线答案”。

### 新增原始数据

早期 pilot 文件现归档于 `raw/pilot-legacy/`；完整数据位于 `raw/all/000469/`，共 41 个 NWB 文件，覆盖 Subject 1-21。新的全量分析优先读取完整目录，不把两处文件混在一起：

| 文件组 | trial 数 | 当前主分析所需事件字段 | 当前处理决定 |
|---|---:|---|---|
| `sub-1_ses-2`、`sub-11_ses-2`、`sub-20_ses-2`、`sub-21_ses-2` | 135 | 有 `timestamps_FixationCross`、`timestamps_Encoding1`、`timestamps_Encoding1_end` | 纳入第一轮多 session 验证分析 |
| `sub-1_ses-1`、`sub-11_ses-1`、`sub-20_ses-1`、`sub-21_ses-1` | 378 | 缺少当前主分析所需事件字段 | 暂不纳入；先单独建立字段地图，再决定是否能回答另一个预先定义的问题 |

这里的“不纳入”不是说 `ses-1` 数据错误，而是说不能把为 135-trial Sternberg session 定义的事件规则硬套到它们身上。

### 中间产物与已知问题

- 早期的整合式批处理原型及其 `results/multi_session/` 中间产物已于 2026-09-06 删除，不是正式分析入口或正式结果。
- 该原型曾在 `sub-11_ses-2` 的批量 raster/PSTH 绘图阶段触发 Windows/Matplotlib 底层异常；故障原因与环境修复方案仍记录在 `experiment_log.md`。
- 当前正式入口是 `src/sternberg_primary.py` 和 `scripts/` 下的独立数值/绘图脚本；正式结果只从 `results/primary-v1/` 和 `results/exploratory-v1/` 读取。
- `raw/` 中的 NWB 文件未被修改；不删除、不移动、不覆盖原始文件。

## 2. 总原则

1. **一套数值分析代码，多份独立 session 结果。**不复制四份 notebook，也不把所有 session 混成一张 trial 表。
2. **先计算，后绘图。**数值分析核心不导入 Matplotlib；绘图是独立、可选、可单独失败的步骤。
3. **每个 session 独立 QC 和独立主检验。**trial 嵌套在 unit，unit 嵌套在 session，session 嵌套在 subject；不能把全部 trial 当成独立患者样本。
4. **先复现旧结果，再扩展新数据。**任何重构后的核心代码都要先复现 `sub-20_ses-2` 的正式结果。
5. **不因不显著而改变主窗口或统计方向。**新增 session 使用与基线完全相同的预先冻结参数。
6. **所有失败可追溯。**保留日志、文件哈希、环境版本、错误原因和排除原因；不把中间文件伪装成最终结果。

## 3. 目标目录与代码组织

后续在不改动 `raw/` 的前提下，逐步形成以下结构：

```text
Reanalysis_DANDI469_NWB/
├── raw/                         # 只放原始 NWB，不写入、不覆盖
├── src/
│   └── sternberg_primary.py      # 纯数值函数：读取、QC、特征、统计
├── scripts/
│   ├── inventory_sessions.py     # 只读清单与字段兼容性检查
│   └── run_one_session.py        # 指定一个 NWB，生成一个 session 的结果
├── results/
│   └── primary-v1/
│       ├── session_inventory.csv
│       ├── session_summary.csv
│       ├── unit_statistics_all_sessions.csv
│       └── sub-XX_ses-Y/
│           ├── session_metadata.json
│           ├── trial_qc.csv
│           ├── unit_qc.csv
│           ├── unit_trial_features.csv
│           ├── final_count_qc.csv
│           └── unit_level_statistics.csv
├── notebooks/
│   ├── 01_single_session_tutorial.ipynb
│   └── 02_multi_session_summary.ipynb
└── plan.md
```

在重构完成前，不移动现有 `read_data.ipynb`；它继续作为可教学、可人工检查的单 session notebook。

## 4. 冻结的主分析参数

所有纳入的 `ses-2` session 保持以下参数不变：

| 项目 | 固定值 |
|---|---|
| 事件对齐点 | `trials.timestamps_Encoding1` |
| baseline | `[-0.8, 0.0)` s |
| response | `[0.2, 1.0)` s |
| PSTH bin | 50 ms，仅用于可视化 |
| 最低 unit 活动要求 | 至少 10 个保留 trial 有 spike |
| 置换检验 | unit 内、配对、单尾上侧、10,000 次 |
| bootstrap | unit 内 trial 配对重采样、5,000 次 |
| 多重比较 | 每个 session 内 BH-FDR，`q < 0.05` |
| 随机种子 | `20260901` |

任何改变窗口、统计方向、纳入阈值或 FDR 家族定义的尝试，都必须作为新的分析版本记录，不能覆盖 `primary-v1`。

## 5. 分阶段执行计划

### 阶段 A：冻结与清理状态

**目标：**区分正式基线、原始数据和失败中间产物。

操作：

1. 不删除 `raw/` 中的任何文件。
2. 不从已清理的早期批处理尝试恢复或读取任何结果；所有结论仅来自 `results/primary-v1/` 与 `results/exploratory-v1/`。
3. 记录 Python、PyNWB、NumPy、pandas、statsmodels、Matplotlib 和操作系统版本。
4. 为完整数据目录中的 41 个 NWB 生成只读清单：文件名、大小、SHA-256、subject/session、trial/unit/electrode 数、关键字段是否存在。

验收：清单明确列出全部 41 个文件，并按关键事件字段区分可进入当前主分析的 session 与待单独解释的 session。

### 阶段 B：建立无绘图的数值核心

**目标：**把单 session notebook 中已验证的计算逻辑提取为纯函数。

函数职责：

1. 读取一个 NWB 文件并检查必需字段。
2. 生成 `trial_qc`，保留通过事件顺序与两个时间窗覆盖检查的 trial。
3. 生成 `unit_qc`，检查 spike 时间有效、递增、活动 trial 数和可报告的质量字段。
4. 生成 `unit_trial_features`：每个 `unit × trial` 的 baseline/response spike count、Hz 和差值。
5. 生成 unit 内置换 p、bootstrap CI、common-language effect 与 session 内 FDR q。
6. 将结果写入指定的 session 输出目录。

限制：这一阶段不导入或调用 Matplotlib，不画任何图。

验收：用同一随机种子处理 `sub-20_ses-2` 后，得到与现有正式结果一致的 trial 数、unit 数、mean delta、p、CI 和 q（允许 CSV 显示精度差异，但不允许实质结果差异）。

### 阶段 C：逐 session 运行并验收

**目标：**在每个 session 独立运行冻结的主分析。

顺序：

1. `sub-20_ses-2`：复现基线答案。
2. `sub-1_ses-2`：单独运行，检查字段、QC 和数值输出。
3. `sub-11_ses-2`：单独运行，确认先前崩溃没有影响数值流程。
4. `sub-21_ses-2`：单独运行。

每完成一个 session，检查：

- 文件哈希和参数文件已保存；
- `trial_qc.csv`、`unit_qc.csv`、`unit_trial_features.csv`、`final_count_qc.csv`、`unit_level_statistics.csv` 都存在；
- 纳入/排除数量可解释；
- 每个 unit 的 `n_trials` 等于该 session 保留 trial 数；
- p、CI、q 和 `significant_q05` 均可读且无缺失；
- 输出目录只属于该 session，不覆盖其他 session。

验收：4 个 `ses-2` 各有可重复的独立数值结果；任何失败 session 被明确记录为失败而非静默跳过。

### 阶段 D：独立的可视化稳定性测试

**目标：**恢复可控的 raster/PSTH 人工检查，而不让绘图阻断统计分析。

操作：

1. 先在 Jupyter inline 环境中，用 `sub-20_ses-2` 重画已成功过的单 unit raster/PSTH，作为绘图 smoke test。
2. 每次只画 1 个 unit；通过后再画最多 4 个 unit，不创建几十个 panel 的巨型 Figure。
3. 每个新 session 选择固定、可追溯的少量代表性 unit，例如最小 ID、居中 ID、最大 ID，或预先固定随机种子抽取的 3 个 unit。
4. 人工检查 `0 s`、baseline 阴影、response 阴影、PSTH Hz 换算和有无系统性时间错位。
5. 最终论文图另存 PDF/SVG（矢量）和 PNG（审阅方便）；图中只展示代表性 unit 与汇总统计，不展示所有 unit 的超长 raster 网格。

若单 unit smoke test 仍失败：停止批量作图，建立最小复现脚本，再在隔离环境中测试固定 Matplotlib 版本、升级或回退版本、以及不同 backend。不得在正式数值分析流程中边运行边改图形依赖。

验收：至少每个纳入 session 有经人工检查的代表性 raster/PSTH；图形失败不会损坏或阻止数值结果。

### 阶段 E：跨 session 汇总，先描述后推断

**目标：**回答“不同 session 是否呈现相近结果”，但避免伪重复。

先生成描述性汇总：

- 每个 session 的总/保留 trial 数、总/保留 unit 数、FDR 显著 unit 数；
- 每个 session 中 unit `mean_delta_hz` 的分布、中位数和方向比例；
- 每个 subject 的两个 session 并列结果；
- unit 所属脑区的描述性计数，不把单一患者脑区差异解释为总体结论。

禁止做法：

- 不把所有 session 的 trial 行拼接后进行一次普通 t 检验；
- 不把同一 subject 的多个 unit 或多个 session 当作独立患者；
- 不用新数据反过来改变已冻结的 baseline、response 或统计方向。

在描述性汇总完成后，另写一份跨 session 推断计划，预先定义分析单位（session 或 subject）、效应汇总方式、缺失 session 处理和多重比较范围，再决定是否做层级模型或 meta-analytic 汇总。

验收：汇总表清楚区分 trial、unit、session、subject 四个层级，且不作超出当前样本层级的泛化声明。

### 阶段 F：探索性分析

**目标：**在主分析扩展稳定后，才研究图片 ID、记忆负荷、正确率、trial order 或脑区等问题。

第一优先候选是第一张编码图片 ID 与 unit 响应的关系，但开始前必须：

1. 检查 `loadsEnc1_PicIDs` 的重复次数与每种图片的样本量；
2. 预先定义训练/测试划分；
3. 在训练集选择图片或条件，在测试集评估；
4. 将探索性结果与主分析结果分开标记和报告。

前置计数已完成：4 个兼容 `ses-2` session 均有图片 ID 1-5，每张图片各出现 26-28 次，无单次出现图片。该结果支持进行分层训练/测试切分，但尚未进行图片选择性检验。

探索性图片 ID 规则已冻结为 `exploratory-v1/encoding1_picid_train_test`：每个 session 内，每个图片 ID 按 `SPLIT_SEED=20260906` 随机、分层切为近似各半的训练和测试 trial；每个 unit 仅在训练 trial 中以最大平均 `response - baseline` 放电率选择候选图片；仅在测试 trial 中比较该候选图片与其余四张图片；使用 10,000 次单尾置换检验，并只在同一 session 的 unit 之间做 BH-FDR（`q < 0.05`）。训练/测试分离避免选择与验证使用同一 trial，但全部结果仍须标注为探索性。

验收：无数据泄漏；不在全体 trial 上选择最强响应后又用同一批 trial 宣称验证成功。

## 6. 绘图与工具决策

- Matplotlib 保留为主静态作图工具；当前错误不足以证明它不适合本项目。
- 这次失败发生在批量多 panel 图形渲染，不是数据规模、NWB 文件或统计计算本身的失败。
- raster/PSTH 是视觉 QC 与代表性展示图，不是数值主检验的输入；因此必须与数值分析解耦。
- 不为当前已排序的 NWB unit 引入 SpikeInterface 重新 sorting；它适合原始连续电压与 sorting/curation 工作流，不是本项目的必要依赖。
- MNE-Python 留给未来 LFP、连续 sEEG/ECoG 或脑区电极可视化，不作为当前单神经元 raster/PSTH 的替代品。

## 7. 每次运行的操作纪律

1. 一次只运行一个 session，确认输出后再运行下一个。
2. 不在后台同时启动多个 Python 分析进程。
3. 每个运行命令都等待正常退出码，并把标准输出/错误写入该运行目录。
4. 先跑数值核心；图形步骤即使失败，也不得使数值结果看起来像“完成”。
5. 不删除旧结果；新参数或代码版本写入新的 `results/primary-vN/` 目录。
6. 每一阶段完成后，在 `experiment_log.md` 记录输入、操作、输出和验收结果。

## 8. 当前下一步

阶段 A-E 已完成。阶段 F 的第一张编码图片 ID 分析已完成：训练/测试切分完整，sub-11 与 sub-21 各有 1 个 unit 在独立测试集通过各自 session 内的 FDR；详见 `results/exploratory-v1/encoding1_picid_train_test/exploratory_summary.md`。这两个候选发现仍是探索性的，不构成跨 subject 结论。下一步如继续阶段 F，应对负荷、正确率或脑区中的一个问题另行进行数据可用性检查并预先固定比较规则。
