# 实验记录

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
