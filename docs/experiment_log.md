# 实验记录

## 2026-09-06 23:20:24 +08:00

- 事项：项目初步冻结前的目录整理与文档更新。
- 原始数据：完整输入固定为 `raw/all/000469/`。`raw/` 顶层的 8 个历史 pilot NWB 经 SHA-256 核验后确认均与完整集同名文件逐字节相同，已移动到 `raw/pilot-legacy/`；未删除任何 NWB，也未改写完整数据。
- 文档：`plan.md` 归档并重命名为 `docs/multi_session_analysis_plan.md`；`experiment_log.md` 与 `project_top_design.md` 移入 `docs/`；新增 `docs/project_freeze_plan.md`。
- 单 session 基线：`read_data.ipynb`、`data_dictionary.json` 与 `unit_level_statistics.csv` 移入 `single-session-baseline/`。notebook 已改为固定读取完整集中的 canonical `sub-20_ses-2`，并将其两个结构化输出写回该目录。
- 路径规则：`src/data_paths.py` 继续优先选择 `raw/all/000469/`；仅在完整集不可用时才明确回退到 `raw/pilot-legacy/`，不再把 `raw/` 顶层作为默认 pilot 输入。
- 结果：`results/` 的版本目录和产物未移动、未改写。README 已记录 `src/` 与 `scripts/` 的分工、结果 JSON/CSV 的内容和冻结维护规则。
- 验证：移动后确认完整目录有 41 个 NWB，pilot 归档目录有 8 个 NWB，`raw/` 顶层无 NWB；`data_paths.py` 仍选择 41 个全量文件，核心脚本通过语法检查，notebook JSON 有效。上述布局现作为初步冻结基线。

## 2026-09-06 18:11:01 +08:00

- Stage: representative plotting completed after numerical analysis and summaries.
- Activation/command: activated `bci-plot` in a temporary PowerShell process with `ExecutionPolicy Bypass`, then ran `python .\Reanalysis_DANDI469_NWB\scripts\run_representative_plots_v2.py`.
- Output: `results/primary-v2-all/plot_runs/representative_plots_v2_20260906_180922+0800.log` and 9 PNG files under `sub-1_ses-2/figures`, `sub-9_ses-2/figures`, and `sub-11_ses-2/figures`.
- Scope: exactly three representative sessions, three default unit IDs per session; no all-unit batch plotting was attempted. All three sessions passed sequentially. A representative PNG was visually checked and showed the expected raster/PSTH alignment windows.
- Conclusion: primary-v2-all numerical outputs, descriptive summaries, exclusion logs, and limited representative plots are complete. The 20 event-schema-incompatible `ses-1` sessions remain excluded from the frozen primary analysis and are not silently mixed with `ses-2`.

## 2026-09-06 18:08:19 +08:00

- Stage: session and subject descriptive summaries generated after numerical validation.
- Command: `D:\AI\miniconda_envs\bci\python.exe .\Reanalysis_DANDI469_NWB\scripts\summarize_primary_v2_all.py`.
- Output: `results/primary-v2-all/session_summary.csv`, `subject_level_descriptive_summary.csv`, `unit_statistics_all_sessions.csv`, and `descriptive_summary.md`.
- Result: 21 session rows, 21 subject rows, 901 QC unit rows, and 2,672 retained trial rows. These are descriptive counts and session-stratified summaries only; no trial pooling and no subject-level inferential p-value were computed. Each subject currently contributes one compatible `ses-2` session.
- Plotting preparation: added `scripts/run_representative_plots_v2.py` for three selected sessions (`sub-1_ses-2`, `sub-9_ses-2`, `sub-11_ses-2`), with the plotting environment check and sequential execution enforced. No plots have been generated yet in this log entry.

## 2026-09-06 18:06:18 +08:00

- Stage: full-data numerical primary analysis completed in the `bci` environment.
- Command: `D:\AI\miniconda_envs\bci\python.exe .\Reanalysis_DANDI469_NWB\scripts\run_primary_all.py`.
- Output: `results/primary-v2-all/`. The batch processed one NWB at a time with `src/sternberg_primary.py`, without importing Matplotlib. It completed 21 compatible sessions and wrote `session_metadata.json`, `trial_qc.csv`, `unit_qc.csv`, `unit_trial_features.csv`, `final_count_qc.csv`, `unit_level_statistics.csv`, and `analysis_parameters.json` for every completed session.
- QC result: 20 `ses-1` sessions were recorded in `session_failures.csv` as `excluded_incompatible_schema` because the three frozen event fields are absent. No compatible session had a runtime failure. The run log contains 41 rows: 21 completed and 20 excluded.
- Numerical validation: every completed session has all required output files; all permutation p-values and FDR q-values are within `[0, 1]`. `sub-20_ses-2/unit_level_statistics.csv` is an exact CSV match to the existing `primary-v1` baseline. No trial rows were pooled across sessions.
- Conclusion: the full numerical primary stage is complete for the 21 schema-compatible `ses-2` sessions. Summary generation can proceed; plotting remains deferred.

## 2026-09-06 18:03:41 +08:00

- Stage: full-data inventory for `primary-v2-all`.
- Input: `raw/all/000469`, selected by `src/data_paths.py`; the legacy pilot files under `raw/` were not included. The inventory contains 41 non-empty NWB files.
- Command: `D:\AI\miniconda_envs\bci\python.exe .\Reanalysis_DANDI469_NWB\scripts\inventory_sessions.py` (the equivalent `conda run -n bci` invocation was blocked by Conda's unwritable envs-directory configuration).
- Output: `results/primary-v2-all/session_inventory.csv`. The inventory now records all six requested schema flags: `timestamps_FixationCross`, `timestamps_Encoding1`, `timestamps_Encoding1_end`, `units.spike_times`, `units.electrodes`, and `electrodes.location`.
- Inventory result: all 41 sessions have `units.spike_times`, `units.electrodes`, and `electrodes.location`. All 21 `ses-2` sessions also have the three required event columns and are eligible for the frozen primary analysis. The 20 `ses-1` sessions all lack the three event columns; they are excluded from the current primary analysis because their event schema does not define the frozen Encoding1 alignment. `ses-1` has 378 trials for 15 sessions and 324 trials for 5 sessions; `ses-2` has 135 trials for 15 sessions and 108 trials for 6 sessions.
- Decision: do not combine `ses-1` and `ses-2`, and do not pool trial rows across sessions. The new `scripts/run_primary_all.py` processes one compatible NWB at a time, writes per-session outputs under `results/primary-v2-all/sub-*_ses-*`, and records exclusions or failures in `session_run_log.csv` and `session_failures.csv`. The new `scripts/summarize_primary_v2_all.py` is reserved for the post-analysis descriptive summaries.
- Verification: `run_primary_all.py`, `summarize_primary_v2_all.py`, and `src/sternberg_primary.py` passed `python -m py_compile` in `bci`. No numerical analysis or plotting was started in this stage.

## 2026-09-06 15:15:16 +08:00

- 事项：清理 Matplotlib 排错临时文件和早期失败的批处理尝试，恢复清晰的项目结构。
- 已删除：工作区根目录的 `test_matplotlib.py` 与 `matplotlib_smoke_test.png`；项目根目录的 `mpl_smoke.png` 与 `analyze_sternberg_sessions.py`；以及该原型崩溃前写出的 `results/multi_session/` 目录。
- 保留：所有 `raw/` 原始 NWB 文件、`read_data.ipynb`、`src/`、`scripts/`、`results/primary-v1/`、`results/exploratory-v1/`、设计文件和已有实验记录。
- 验证：已逐一确认上述 5 个删除目标均不存在；`results/` 当前只保留 `primary-v1/` 和 `exploratory-v1/` 两类正式结果目录。
- 额外清理：删除了路径误用留下的空嵌套目录 `Reanalysis_DANDI469_NWB/Reanalysis_DANDI469_NWB/`，以及仅含已删除原型编译缓存的 `__pycache__/`。
- 历史边界：删除的是不可作为结论依据的临时/失败产物，不影响已验证的数值结果。Matplotlib 故障原因和正确环境使用方式仍保留在本日志中，以便将来排错。

## 2026-09-06 14:48:27 +08:00

- 事项：阶段 F（探索性分析）的图片 ID 样本量前置检查。
- 执行：在 `bci` 环境运行 `scripts/inventory_encoding1_picids.py`，只读取第一张编码图片的 `trials.loadsEnc1_PicIDs`；输出保存在 `results/primary-v1/exploratory_precheck/`。
- 结果：4 个兼容的 `ses-2` session（sub-1、sub-11、sub-20、sub-21）均有 135 个 trial 和相同的 5 个图片 ID。每个图片 ID 在每个 session 中分别出现 26、27 或 28 次（具体为 ID 1: 28 次，ID 2: 26 次，ID 3-5: 各 27 次）；没有只出现一次的图片。
- 结论：每种图片都有足够且近似平衡的重复 trial，可进行按图片 ID 分层的训练/测试切分。此结果仅说明数据结构适合做探索性图片选择性分析，不说明任何图片已经引起更强或更弱的神经反应。
- 下一步：预先固定 50/50 的分层训练/测试切分和随机种子；仅在训练 trial 中为每个 unit 选择候选图片，再只在独立测试 trial 中比较该图片与其余图片的反应差异。探索性结果将与 `primary-v1` 主分析分开保存和报告。

## 2026-09-06 14:59:39 +08:00

- 事项：完成阶段 F 的第一张编码图片 ID 探索性训练/测试分析。
- 执行：在 `bci` 环境运行 `scripts/run_encoding1_picid_exploration.py`。每个 session 的每个图片 ID 按固定种子 `20260906` 分层切为近似各半的训练/测试 trial；每个 unit 仅在训练集选择平均 `response - baseline` 放电率最高的候选图片，再仅在测试集比较候选图片与其余四张图片。测试使用 10,000 次单尾置换，并在各自 session 的 unit 内做 BH-FDR。
- 数据完整性：4 个 session 均保留 135 个 trial；QC unit 数与主分析一致，依次为 40、74、5、20。每个图片 ID 均有 13 或 14 个训练 trial 和 13 或 14 个测试 trial，分层切分完整。
- 结果：sub-1 为 0/40、sub-11 为 1/74、sub-20 为 0/5、sub-21 为 1/20 个 unit 在独立测试集通过 session 内 `q < 0.05`。sub-11 的 unit 36 在训练集选择图片 ID 5；测试集候选图片均值为 3.393 Hz，其他图片均值为 -0.250 Hz，差值 3.643 Hz，p=0.000100，q=0.007399。sub-21 的 unit 1 在训练集选择图片 ID 1；测试集候选图片均值为 3.304 Hz，其他图片均值为 -0.341 Hz，差值 3.644 Hz，p=0.000100，q=0.002000。
- 与主分析的关系：sub-11 unit 36 同时在主分析中显著；sub-21 unit 1 的主分析总体图片后增强未通过 FDR，但其对图片 ID 1 的选择性通过独立测试。这不矛盾：主分析检验的是平均所有图片后是否高于基线，当前检验的是某张图片是否相对其他图片更强；平均会掩盖图片特异性的反应。
- 结论边界：这是探索性、训练/测试分离的候选发现。FDR 校正范围仅为各自 session 的 unit，不可把这 2 个 unit 合并成跨 subject 的总体显著性结论，也不可据此改变 `primary-v1` 的主结论。需在独立数据或预先定义的重复分析中确认。

## 2026-09-02 15:05:25 +08:00

- 事项：手动下载 DANDI 000469 数据集固定版本 `0.240123.1806` 的推荐 NWB 文件。
- 文件：`sub-20_ses-2_ecephys+image.nwb`
- 保存位置：`Reanalysis_DANDI469_NWB` 项目根目录。

## 2026-09-02 15:05:25 +08:00

- 事项：初步检查 NWB 数据结构。
- 检查结果：当前目录发现 1 个 NWB 文件；PyNWB 打开成功；`trials` 有 135 行，`units` 有 5 行，`electrodes` 有 5 行；`units` 表中存在 `spike_times` 和 `electrodes` 字段；文件的 `acquisition` 中存在 `events`，没有 `processing` 模块。
- 关键字段及其当前含义：
  - `trials.timestamps_Encoding1`：第一张编码图片开始的事件时间，暂作为后续事件对齐的候选 onset 字段。
  - `units.spike_times`：每个神经元的 spike 时间数组。
  - `units.electrodes`：unit 与电极表之间的关联字段，通常保存指向 `electrodes` 表行的索引或引用，不是另一套独立的电极数据。
  - `electrodes.location`：电极所在的解剖脑区或位置描述。
- 问题：`electrodes` 在多个地方出现时分别是什么意思？
- 回答：
  1. `nwbfile.electrodes` 是 NWB 文件顶层的电极表。每一行描述一个实际电极或电极接触点，当前表中包含 `location`、`x`、`y`、`z`、`group` 等字段。
  2. `units.electrodes` 是 `units` 表中的关联列。它把某个 unit 连接到 `nwbfile.electrodes` 中对应的电极行，用来回答“这个神经元由哪条电极记录”。它不是新的电极表。
  3. `nwbfile.electrode_groups` 是电极组对象，用来把属于同一记录设备、探针或记录区域的一组电极组织在一起。`electrodes.group` 或 `group_name` 表示电极所属的组，不等于脑区本身。
  4. `electrodes.location` 是电极表中的位置字段，通常用于描述脑区。它是文字属性，不是对另一个电极对象的引用。
- 当前结论：核心 NWB 结构和项目所需的关键入口已经找到，可以进入数据字典阶段。下一步仍需查看实际数值，确认 `units.electrodes` 的具体索引形式、`timestamps_Encoding1` 的时间格式，以及事件时间和 spike 时间是否使用同一时间基准。

## 2026-09-02 15:20:28 +08:00

- 事项：进入数据字典阶段，在 `read_data.ipynb` 中新增第二个代码单元。
- 操作：重新只读打开 NWB 文件，建立项目内部字段名与真实 NWB 字段名的映射，并检查关键字段的实际类型、示例值、缺失数量和数值范围。
- 输出：生成字段元数据报告 `data_dictionary.json`；该报告只保存字段说明和检查摘要，不转换或复制原始 trial 和 spike 数据。
- 当前字段映射：`first_encoding_onset <- trials.timestamps_Encoding1`，`spike_times <- units.spike_times`，`unit_electrode <- units.electrodes`，`region <- electrodes.location`。这些映射中的事件语义、时间单位和电极索引形式仍需根据第二个代码单元的实际输出确认。

## 2026-09-02 15:38:12 +08:00

- 事项：重新审查并精简数据字典代码。
- 操作：删除重复的数据目录查找、重复表结构读取和过度封装；保留固定字段映射、字段存在性、类型、缺失数量、数值范围，以及 `units.electrodes` 到 `electrodes.location` 的关联检查。
- 既有检查结果：上一版 `data_dictionary.json` 中 8 个字段全部 `FOUND`，`trials` 相关字段均为 135 行且缺失数为 0，`spike_times` 为 5 个 ndarray 且缺失数为 0，`electrodes.location` 为 5 个字符串且缺失数为 0。
- 注意：第二个代码单元已修改并清除了旧输出，需要重新运行后更新 `data_dictionary.json`；新版结果应以重新运行后的报告为准。

## 2026-09-02 16:06:38 +08:00

- 事项：记录 Python 字典在本项目中的名称映射方法。
- 说明：`FIELD_MAP` 是一个小型 Python 字典变量，保存“项目内部名称 -> NWB 实际字段位置”的查找规则；它不复制或改名 NWB 原始数据。`data_dictionary.json` 则保存本次字段映射和检查结果的可阅读、可复核摘要。
- 关键映射：
  - `first_encoding_onset = trials.timestamps_Encoding1`
  - `fixation_event = trials.timestamps_FixationCross`
  - `spike_times = units.spike_times`
  - `unit_electrode = units.electrodes`
  - `region = electrodes.location`

## 2026-09-02 16:12:55 +08:00

- 事项：在 `read_data.ipynb` 新增第三个代码单元，进行 trial 时间完整性检查。
- 判定规则：检查必需时间戳是否有限；检查 `trial_start <= fixation < encoding_onset < encoding_end <= trial_stop`；确认编码前至少有 0.8 s fixation 基线，且编码后至少有 1.0 s 可用记录时间。
- 输出：建立 `trial_qc` 表，逐条保存检查结果；建立 `valid_trials` 表，供下一步 spike-event 对齐使用。该单元只读 NWB 文件，不修改原始数据。
- 验证结果：135 个 trial 的四项检查均通过，0 个 trial 因时间戳、事件顺序、基线覆盖或响应窗口覆盖而被排除；`valid_trials` 共 135 行。

## 2026-09-02 16:22:36 +08:00

- 事项：完成 trial 时间结构完整性检查，进入 unit 质量控制阶段。
- 结论：所有 135 个 trial 的时间结构均完整，且均有可用的 fixation 基线与第一张编码图片后的响应窗口。因此，可以在同一 trial 内公平比较 fixation 基线放电与第一张编码图片后的放电。
- 后续分析：对每个 unit 检查 spike 时间是否非空、有限且递增，并统计其在保留 trial 中的活动情况；质量字段只在缺失模式和实际数值确认后才用于排除。
- unit QC 结果：新增第四个代码单元后，5 个 unit 的 spike 时间均非空、有限且递增；它们分别在 133、128、131、134、89 个保留 trial 中有 spike，均超过至少 10 个活动 trial 的最低规则。因此 `valid_units` 共 5 行。`waveforms_isolation_distance` 仅 1 个 unit 有值，当前只报告、不作为排除阈值。

## 2026-09-02 16:32:28 +08:00

- 事项：trial QC 与最低 unit QC 均完成，进入事件对齐后的窗口特征计算。
- QC 结论：`valid_trials` 为 135/135，`valid_units` 为 5/5；所有纳入 trial 具有完整的 fixation 基线和响应窗口，所有纳入 unit 具有可用且足够活跃的 spike 时间序列。
- 下一步：以 `encoding_onset` 为零点，按每个 `unit × trial` 计算 baseline `[-0.8, 0)` 与 response `[0.2, 1.0)` 的 spike count、放电率（Hz）和 response-baseline 差值。
- 特征计算结果：成功生成 675 行 `unit_trial_features`（5 个 unit × 135 个 trial）。unit 0-4 的平均 response-baseline 放电率差分别为 0.213、0.241、0.028、-0.259、0.102 Hz；这些只是描述性均值，尚未进行 unit 内的统计检验。

## 2026-09-02 16:45:52 +08:00

- 事项：解释 unit 内跨 135 个 trial 的平均放电率与窗口 spike 计数方法。
- 平均值含义：对同一个 unit 的 135 个 trial 分别计算 baseline_rate、response_rate 和二者配对差值，再取平均。该均值描述该 unit 在本 session、当前时间窗和当前试次集合中的典型放电水平；它不代表人群效应、图片选择性或统计显著性。由于所有 135 个 trial 均被纳入且两个窗口均为 0.8 s，平均差值等于平均 response_rate 减平均 baseline_rate。
- `np.searchsorted`：对递增 spike 时间数组返回某个时间值应插入的位置。令 `start_index = np.searchsorted(spike_times, left)`、`end_index = np.searchsorted(spike_times, right)`，则 `end_index - start_index` 是左闭右开时间窗 `[left, right)` 内的 spike 数；因此不需要复制完整的相对 spike 时间数组。

## 2026-09-02 17:00:05 +08:00

- 事项：在 `read_data.ipynb` 新增第六和第七个代码单元，分别绘制单个 unit 与全部合格 unit 的事件对齐 raster 和 PSTH。
- 图形定义：raster 中每行对应一个 trial、每条短线对应一个 spike；PSTH 按 50 ms bin 汇总所有 trial 的 spike 并换算为 Hz。横轴均为相对 `encoding_onset` 的时间，范围 `[-0.8, 1.0)` s；图中标记基线窗、响应窗和 0 s 图片 onset。
- 目的：在统计检验前，直观核对 spike-event 对齐、时间方向和放电率变化是否合理。

## 2026-09-04 19:53:15 +08:00

- 事项：开始在每个代码块后补充 Markdown 解说；本次完成第一个代码块的解说。
- 内容：说明其在顶层设计中对应只读 NWB 文件检查与第一份结构报告；列出当前文件发现、PyNWB 打开状态、session 元数据、`trials`/`units`/`electrodes` 的行数与关键字段，以及本阶段能够确认和仍需后续确认的边界。

## 2026-09-04 19:56:02 +08:00

- 事项：完成第二个代码块后的 Markdown 解说。
- 内容：说明其在顶层设计中对应数据字典与结构报告；区分 `FIELD_MAP` 名称映射和 `data_dictionary.json` 检查摘要；列出 8 个关键映射的实际类型、缺失数、时间范围，以及 5 个 unit 到电极/脑区的关联和当前分析边界。

## 2026-09-04 20:03:37 +08:00

- 事项：在第二段数据字典与第三段 trial QC 之间新增单个 trial 的任务事件时间线及 Markdown 解说。
- 内容：以第 0 个 trial 的 `timestamps_FixationCross` 为 0 s，绘制 fixation、三次编码图片、maintenance、probe 和 response 的实际顺序与持续时间，直观说明时间字段的任务含义；明确该图仅为单个 trial 示例，全部 135 个 trial 的时间关系由随后 trial QC 验证。
- 图形标注更新：在每个关键时间点下方直接标注任务含义和 NWB 变量名；图中明确 `start_time = timestamps_FixationCross`、`timestamps_Encoding3_end = timestamps_Maintenance`、`timestamps_Response = stop_time`。

## 2026-09-04 20:16:26 +08:00

- 事项：完成第三个代码块（trial QC）后的 Markdown 解说。
- 内容：说明其在顶层设计中对应 trial 纳入和时间完整性 QC；列出有限时间戳、事件顺序、0.8 s 基线覆盖、1.0 s 响应窗覆盖四项规则；记录当前 135 个 trial 全部通过、`valid_trials` 为 135 行，以及 `Empty DataFrame` 表示没有被排除 trial。

## 2026-09-04 20:27:01 +08:00

- 事项：完成第四个代码块（unit QC）后的 Markdown 解说。
- 内容：说明其在顶层设计中对应 unit 纳入；列出 spike 总数、有限性、递增性、活动 trial 数和至少 10 个活动 trial 的最低规则；记录当前 5 个 unit 均通过、`valid_units` 为 5/5，并说明 isolation distance 的缺失仅报告、不作为临时排除标准及当前最低 QC 的边界。

## 2026-09-04 20:30:41 +08:00

- 事项：完成第五个代码块的 Markdown 解说，并新增 unit-trial 关系热图及其解说。
- 内容：说明 `unit_trial_features` 的 675 行是 5 个 unit × 135 个 trial 的配对观察；热图用行表示 unit、列表示 trial、小格颜色表示 response-baseline 放电率差，实际矩阵形状为 5 × 135；强调 trial 是 unit 内重复观测，675 个小格不能当作独立受试者样本，颜色不表示显著性。

## 2026-09-04 20:36:52 +08:00

- 事项：将第六和第七个代码块的 raster/PSTH 绘图逻辑合并写成一段 Markdown 解说。
- 内容：说明第六段定义并测试 `plot_unit()` 函数，第七段复用该函数遍历全部 5 个 unit；解释 raster、PSTH、50 ms bin、图片 onset、基线窗和响应窗的含义；明确它们用于统计前的对齐核查与描述，不构成显著性结论，且当前图输出需要在 notebook 中重新运行生成。

## 2026-09-04 20:46:36 +08:00

- 事项：新增并运行统计前最终 QC。
- 结果：生成 `final_qc` 表。unit 0-4 的最短 ISI 为 1.8750-2.0000 ms，短于 2 ms 的 ISI 比例均低于 0.1%；基线/响应零计数比例和最大单 trial spike count 均已记录，未出现当前阶段需要自动排除的明显异常。5 个 unit 保持纳入。
- 统计前门槛：数值 QC 已通过；仍需在 Jupyter 中运行并人工检查第七个代码块的全 unit raster/PSTH，确认不存在明显系统性时间错位后再进行主要统计。

## 2026-09-04 20:57:54 +08:00

- 事项：在最终 QC Markdown 中补充 ISI、零计数和极端计数的简单定义。
- 说明：ISI 检查相邻 spike 间隔是否出现大量异常短值；零计数说明窗口内无 spike、影响统计方法选择但不等于缺失数据；极端计数用于识别可能由少数异常 trial 主导的均值。
- spike sorting 边界：spike sorting 是原始电极电压到已排序 unit/spike_times 的上游数据生成步骤。本项目使用公开 NWB 中作者已经提供的 sorted units，不重新进行 sorting；当前流程通过 spike 时间、SNR、isolation distance、ISI 和活动量等 QC 审计既有 sorting 结果，并在结果中报告其局限。

## 2026-09-05 15:00 +08:00

- 事项（数据恢复）：因操作失误，`read_data.ipynb` 曾被清空为 0 字节，现已完成恢复并重新执行验证。
- 原因：用 bash heredoc 把含中文的代码单元经 Windows 管道喂给 Python 追加脚本，管道把中文转成孤立 surrogate；`nbformat.write` 报 UnicodeEncodeError，而其写文件方式是“先清空再写”，因此报错前文件已被截断。
- 恢复方法：本对话早前已用 `nbconvert --to script` 完整 dump 过该 notebook 全部源码（代码单元 + markdown 解说）。据此把 19 个单元格内容逐条重建为 UTF-8 文本文件（用文件写入工具，不经 shell 管道），再由纯 ASCII 组装脚本 `nbformat` 生成 `read_data.ipynb`。
- 验证：在 `bci` 环境 `nbconvert --execute` 全量重跑成功（exit 0，约 335 KB）。核对关键输出与历史记录一致：trials 135/135、units 5/5（spike 数 2255/2318/2647/2585/1454，活动 trial 133/128/131/134/89）、`unit_trial_features` 675 行、矩阵 (5,135)、最短 ISI 1.8750–2.0000 ms、零计数比例等均与实验记录一致；`data_dictionary.json` 已重新生成。
- 教训：后续所有向 notebook 追加含中文单元格的操作，一律先把内容写成 UTF-8 文本文件（不经 shell 管道），再由 Python 读取组装。

## 2026-09-05 15:20 +08:00

- 事项：进入里程碑 6（统计检验），开始一小步一小步实现。
- 本步目标：单元级（unit 内）配对置换检验，回答主问题“每个 unit 的图片后放电率是否高于同一 trial 的 fixation 基线”。
- 冻结参数：随机种子 20260901、unit 内置换次数 10,000（来自顶层设计第 20 节）；方向性（单尾上）检验平均差值 > 0。
- 方法说明：对每个 unit 收集其在全部保留 trial 的配对差值 `d_i = response_rate_hz - baseline_rate_hz`；因两个窗口等长，在同一 trial 内交换 baseline/response 标签等价于把 `d_i` 随机取负号。置换零分布 = 大量随机翻符号后的均值；`p = (count(null >= observed) + 1) / (10,000 + 1)`，作连续性校正避免出现 0。
- 结果（135 trial/unit，单尾方向性）：unit 0 mean_delta=0.213 Hz p=0.195；unit 1 =0.241 p=0.117；unit 2 =0.028 p=0.464；unit 3 =-0.259 p=0.892；unit 4 =0.102 p=0.293。
- 当前结论：没有 unit 在原显著水平通过单尾置换检验。这是诚实结果（单 session、平均差值相对 trial 间基线变异较小），不因不显著而放宽窗口或调参。p 值取决于固定种子 20260901，可复现。
- 下一步：补充 unit 内 bootstrap 95% CI、配对 common-language effect 和描述性效应量，再做跨 unit 的 BH-FDR。
- 事项：第 6.2 步 bootstrap CI 与 common-language effect。
- 方法修正：common-language 效应量初版误写成“两个不同 trial 相互比较”，因放电率由整数计数/0.8 得到、取值粗、平局多，全部返回无信息的 0.5000。已改为设计的原意“随机抽一个 trial 时 response 高于该 trial 内 baseline 的概率，平局计 0.5”，即 (trials_above + 0.5×trials_tie)/135。
- 结果：unit 0–4 的 mean_delta 0.213/0.241/0.028/-0.259/0.102 Hz；bootstrap 95% CI 依次 [-0.232,0.685]/[-0.139,0.611]/[-0.361,0.435]/[-0.685,0.167]/[-0.222,0.407]，全部跨 0；trials_above 61/46/36/45/30、tie 25/51/55/27/82，common_language 0.544/0.530/0.470/0.433/0.526。
- 下一步：合并 p、CI、效应量到一张结果表，做跨 5 个 unit 的 Benjamini–Hochberg FDR（q<0.05），并把结果表落盘为 CSV。
- 事项：第 6.3 步合并结果表 + BH-FDR + 落盘。
- 结果表：unit 0–4 的 mean_delta 0.213/0.241/0.028/-0.259/0.102 Hz，median_delta 全部 0.0（平局多），bootstrap 95% CI 全部跨 0，permutation_p 0.195/0.117/0.464/0.892/0.293，BH-FDR q 0.488/0.488/0.579/0.892/0.488。
- FDR 结论：在 q<0.05 下 0/5 个 unit 显著。表已保存 `unit_level_statistics.csv`。解释：在本 session、预先定义的窗口与 QC 规则下，这 5 个 unit 没有一个达到 FDR 显著的“图片后高于基线”效应；这是诚实结果，不因不显著而放宽窗口或换更宽窗。
- 下一步（里程碑 6 第 4 步）：用结果表画最终图：unit 级配对效应图 + 效应量/CI（森林）汇总图，并把图保存为 PNG。
- 事项：第 6.4 步最终汇总图完成。
- 图 A（unit 级配对效应）：每个 unit 一条从 baseline 均值连到 response 均值的线，横轴为两个时间条件、纵轴为平均放电率 Hz；本 session 无 unit 通过 FDR，故全部灰线。
- 图 B（效应量森林图）：每个 unit 一个 mean_delta ± bootstrap 95% CI 误差棒，竖直虚线 0 为无差异；右侧标 q 与 trial 数。全部 CI 跨 0。
- 输出：图已保存 `fig_3_unit_paired_effect.png`、`fig_4_unit_effect_ci.png`，并在 notebook 内显示；结果表 `unit_level_statistics.csv`。
- 结论（仅描述该 session）：多个 unit 平均响应方向为正，但 95% CI 均跨 0、FDR(q<0.05) 后 0/5 unit 显著；因此在此 session、预先定义的窗口与 QC 规则下，没有足够证据表明第一张编码图片后的放电率显著高于同一 trial 的 fixation 基线。此结论不推广到其他被试。
- notebook 现共 27 个单元格，`nbconvert --execute` 在 `bci` 环境全量跑通（exit 0）。里程碑 6 的“检验-效应量-FDR-落盘-出图”链路已走通。

## 2026-09-05 16:00 +08:00

- 事项：因担心数据再次丢失，决定把本项目做成独立 git 仓库并准备同步 GitHub。
- 范围决策：仓库根 = `Reanalysis_DANDI469_NWB` 子目录（而非整个 `NWB` 父目录，后者含约 800MB 其他/上游克隆内容）。
- 决定：notebook 提交前不清空输出；结果图不另存 PNG 文件夹，只留在 notebook 内。
- 操作：①新建 `README.md`（项目简介/复现/数据来源/结果摘要）；②新建 `requirements.txt`（bci 环境依赖版本，Python 3.12.13）；③新建 `.gitignore`（排除 `*.nwb` 及 notebook/python 杂项）；④修改 notebook cell 25 去掉两张图的 `savefig` 并移除多余 `import pathlib`，同步修改 cell 26 解说（图仅显示、不存 PNG）；⑤删除已生成的 `fig_3_*.png`、`fig_4_*.png`。
- 验证：删除 savefig 后 `nbconvert --execute` 全量重跑成功（exit 0），两张图以内嵌输出保留在 cell 25，目录内不再生成 PNG。
- 安全：改动前已做一次本地备份快照到 `E:/BCI-workstation/tmp/backup_Reanalysis_20260905_152320`。

## 2026-09-05 16:20 +08:00

- 事项：把原始 NWB 数据移入 `raw/` 子目录并使其不入 git。
- 操作：①新建 `raw/`，把 `sub-20_ses-2_ecephys+image.nwb` 移入；②`.gitignore` 增加 `raw/`；③修改 notebook cell 0 的文件发现逻辑（在项目根目录与 `raw/` 下同时查找 `*.nwb`，DATA_DIR 仍为项目根以正常落盘输出）；④README 更新数据放置路径与文件表。
- 验证：改后 `nbconvert --execute` 全量重跑成功（exit 0），能从 `raw/` 读到数据，输出仍在项目根。

## 2026-09-06 11:18:32 +08:00

- 事项：新增多 session 数据后的处理方案重新规划，详细计划见 `plan.md`。
- 数据清单：`raw/` 有 8 个 NWB 文件；4 个 `ses-2` 文件各有 135 trial，具备当前主分析所需 fixation/Encoding1 事件字段，拟纳入第一轮多 session 验证；4 个 `ses-1` 文件各有 378 trial，但缺少当前主分析字段，暂不强行纳入。
- 问题记录：实验性批处理脚本在 `sub-11_ses-2` 的批量 raster/PSTH 绘图阶段触发 Windows/Matplotlib 底层异常；错误发生在图形渲染，不是 NWB 读取、spike 计数或统计计算。原始 NWB 未修改；崩溃前生成的 `results/multi_session/` CSV 视为中间产物，不用于结论。
- 决策：后续采用“一套无绘图数值核心 + 每个 session 独立结果目录 + 独立的小规模可视化 + 单独的跨 session 汇总”结构。第一步必须用 `sub-20_ses-2` 复现已有正式结果，再依次分析其余兼容 session。

## 2026-09-06 11:27:00 +08:00

- 事项：执行 `plan.md` 阶段 A-C，完成多 session 的无绘图数值主分析。
- 阶段 A：生成 `results/primary-v1/session_inventory.csv`，记录 8 个 NWB 的文件大小、SHA-256、subject/session、trial/unit/electrode 数和 schema 兼容性。4 个 `ses-2` 兼容当前主分析；4 个 `ses-1` 缺少 `timestamps_FixationCross`、`timestamps_Encoding1`、`timestamps_Encoding1_end`，暂不纳入。
- 阶段 B：新增 `src/sternberg_primary.py`、`scripts/inventory_sessions.py` 和 `scripts/run_one_session.py`。数值核心不导入 Matplotlib，仍使用冻结窗口、QC、10,000 次置换、5,000 次 bootstrap、session 内 BH-FDR 和随机种子 `20260901`。
- 基线验收：`sub-20_ses-2` 新核心与已有 `unit_level_statistics.csv` 的数值最大绝对差小于 `1e-6`，`n_trials` 和显著性结果完全一致。中途修正了随机数调用顺序，使其与原 notebook 的“先完成所有 permutation，再完成所有 bootstrap”一致。
- 阶段 C：4 个 `ses-2` 均为 135/135 trial、通过 QC 的 unit 数分别为 sub-1=40、sub-11=74、sub-20=5、sub-21=20，共 139 个 unit；结果分别保存于 `results/primary-v1/sub-*_ses-2/`。
- session 级描述性结果：sub-1 为 0 个、sub-11 为 14 个、sub-20 为 0 个、sub-21 为 0 个 unit 通过 `q<0.05`。这只是各 session 内结果，尚未构成跨 subject 总体结论。
- 当前阶段：阶段 A-C 完成；阶段 D 的小规模 Matplotlib/Jupyter raster-PSTH smoke test 和人工时间对齐检查待执行。旧的 `results/multi_session/` 仍视为失败尝试中间产物，不纳入汇总。

## 2026-09-06 11:31:16 +08:00

- 事项：执行阶段 D 的最小绘图 smoke test。
- 结果：单 unit raster/PSTH 脚本和最简单的 Matplotlib 折线在 `fig.canvas.draw()` 时均触发 Windows fatal exception `0xc06d007f`，错误位于 Matplotlib transforms；即使使用 `Agg` backend 仍失败。
- 环境：Python 3.12.13、Matplotlib 3.11.0、NumPy 2.5.1；默认 backend 为 `qtagg`。
- 判断：这是当前 Matplotlib 二进制/依赖/渲染环境问题，不是 NWB 文件、spike 数据量或 raster/PSTH 逻辑问题。阶段 D 暂停，未生成正式 figure，也不影响 `results/primary-v1/` 的数值结果。
- 决策：先建立隔离绘图环境并通过最小折线 smoke test，再恢复代表性 unit 的人工时间对齐检查；阶段 E/F 暂不推进。

## 2026-09-06 14:19:20 +08:00

- 事项：按 `plan.md` 恢复阶段 D 的独立绘图流程。
- 环境分工：`bci` 继续负责 NWB 数值处理；已激活的 `bci-plot` 负责 raster/PSTH。绘图环境固定为 NumPy 1.26.4、Matplotlib 3.10.9，并通过增强版 smoke test（折线、垂直参考线和阴影区域）验证。
- 验证：使用已激活环境中的 `python` 成功生成 `sub-20_ses-2` 和 `sub-1_ses-2` 的 unit 0 raster/PSTH PNG。绘图结果仍需每个兼容 session 选取代表性 unit 并完成人工时间对齐检查，因此阶段 D 尚未完成。
- 纪律：不得使用未激活环境的 Python 绝对路径替代 `conda activate bci-plot` 后的 `python`，以免 Conda 原生 DLL 路径未进入 `PATH`。

## 2026-09-06 14:23:11 +08:00

- 故障主题：Windows 下 Matplotlib 绘图进程直接退出，错误码为 `0xc06d007f`。
- 典型表现：最初的 `bci` 环境中，即使使用 `matplotlib.use("Agg")`，程序也可能在 `fig.canvas.draw()`、`fig.savefig()` 或 `axvline()` 期间直接退出；Python 的 `try/except` 无法捕获。故障回溯通常停在 `matplotlib.transforms.get_affine()`、`backend_agg` 或 NumPy/BLAS 原生层。
- 排查结论：这不是 NWB 文件损坏、spike 点数量过多、trial 数量过多或统计代码错误。数值核心不导入 Matplotlib，`results/primary-v1/` 的数值结果不受影响。真实数据中 unit 0 的对齐点数只有 107 个，仍可触发故障，排除了“大数据量”解释。
- 重要原因：Conda 环境的原生 DLL 依赖必须通过环境激活后的 `PATH` 正确加载。仅使用 `D:\AI\miniconda_envs\bci-plot\python.exe` 的绝对路径，不能等同于先执行 `conda activate bci-plot`；这种运行方式可能缺少环境的 `Library\bin`、`Library\usr\bin` 和 `Scripts` 路径。此前由工具直接调用绝对路径得到的部分崩溃结果，不能代替用户在已激活 PowerShell 中的测试。
- 处理方法：保留 `bci` 作为数值分析环境；单独使用 `bci-plot` 绘图。当前稳定组合为 Python 3.12、Matplotlib 3.10.9、NumPy 1.26.4，并通过 conda-forge 安装。不要在原 `bci` 环境中安装或降级绘图库。
- 正确验证：
  1. 关闭旧的 Jupyter/Python kernel。
  2. 执行 `conda activate bci-plot`。
  3. 用 `where python` 确认第一项是 `D:\AI\miniconda_envs\bci-plot\python.exe`。
  4. 执行根目录的 `python .\test_matplotlib.py`，必须看到 `PASS: figure saved ...`。
  5. 再一次只运行一个 session 的 `plot_session_qc.py`，成功保存 PNG 后才继续下一个 session。
- 当前验证结果：增强版 smoke test 已成功；`sub-20_ses-2` 和 `sub-1_ses-2` 的 unit 0 raster/PSTH 已成功保存。阶段 D 仍需完成其余代表性 unit 的人工时间对齐检查。
- 复发时的诊断命令：在已激活的环境中使用 `python -u -X faulthandler .\test_matplotlib.py`，保存完整输出和退出码；不要并行启动多个绘图进程，也不要先修改数值分析代码。

## 2026-09-06 14:25:59 +08:00

- 事项：完成 `sub-1_ses-2` 的 3 个代表性 unit（0、20、39）raster/PSTH 可视化检查。
- 输出：`results/primary-v1/sub-1_ses-2/figures/unit_0_raster_psth.png`、`unit_20_raster_psth.png`、`unit_39_raster_psth.png`。
- 人工 QC：0 秒黑色参考线、baseline `[-0.8, 0)` 灰色区域、0 到 0.2 秒间隔和 response `[0.2, 1.0)` 蓝色区域均位置正确；未观察到系统性的整体时间错位。该 session 的代表性绘图检查暂记为通过。
- 下一步：在同一已激活的 `bci-plot` 环境中处理 `sub-11_ses-2`，完成后再处理 `sub-20_ses-2` 和 `sub-21_ses-2`。

## 2026-09-06 14:32:46 +08:00

- 事项：完成阶段 D 的代表性 raster/PSTH 批量绘图与人工时间对齐检查。
- 执行：在已激活的 `bci-plot` 中运行 `scripts/run_representative_plots.py`。脚本按顺序处理 4 个兼容 `ses-2`，每个 session 绘制最小、中间、最大 ID 的 3 个 unit；运行日志为 `results/primary-v1/plot_runs/representative_plots_20260906_143110+0800.log`。
- 结果：4 个 session 全部 PASS，共生成 12 张 PNG。代表性 unit 分别为 sub-1: 0/20/39，sub-11: 0/37/73，sub-20: 0/2/4，sub-21: 0/10/19。
- 人工 QC：全部图的 0 秒黑线、baseline `[-0.8, 0)` 灰色区、0 到 0.2 秒间隔、response `[0.2, 1.0)` 蓝色区和 PSTH 横轴一致；未观察到任何 session 的系统性时间错位。
- 验收：阶段 D 完成。raster/PSTH 仅作为对齐和展示 QC，不参与或改变数值主检验。下一步进入阶段 E 的跨 session 描述性汇总；不合并 trial，不进行跨 subject 总体显著性推断。

## 2026-09-06 14:44:05 +08:00

- 事项：完成阶段 E 的跨 session/subject 描述性汇总。
- 执行：在 `bci` 环境运行 `scripts/summarize_primary_results.py`，生成/更新 `session_summary.csv`、`unit_statistics_all_sessions.csv`、`subject_level_descriptive_summary.csv` 和 `results/primary-v1/descriptive_summary.md`。
- 结果：4 个兼容 session 各保留 135 个 trial，共 540 个 trial 和 139 个 QC unit；sub-11_ses-2 有 14/74 个 session 内 FDR 显著 unit，其余 3 个 session 均为 0 个。session-level unit mean delta 的方向不一致。
- 解释边界：540 个 trial 和 139 个 unit 仅用于数据规模清点，不能当作独立受试者进行总体检验；每位 subject 目前只有 1 个兼容 session，因此未计算跨 subject 总体 p 值。
- 验收：阶段 E 完成。下一步仅进行阶段 F 的前置数据检查：统计 `loadsEnc1_PicIDs` 的重复次数与样本量，不提前进行图片选择性检验。
