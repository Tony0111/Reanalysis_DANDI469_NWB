# DANDI 000469 Sternberg 单神经元再分析

本项目对 DANDI 000469 的 Sternberg 工作记忆任务人类单神经元 NWB 数据进行可复现再分析。主问题是：**在每个可兼容 session 内，第一张编码图片出现后，单元的放电率是否高于图片出现前的基线。** 结论必须以 session 为分析边界解释，不能把所有 session 的 trial 或 unit 拼接成一个总体检验。

这份 README 分两大部分：

- **第一部分 · 代码仓库导读**：仓库怎么组织，哪些文件是用来学习的，哪些文件是真正跑数据的。
- **第二部分 · 实验说明**：数据集是什么、实验怎么做、分析口径是什么、结果如何。

---

# 第一部分 · 代码仓库导读

## 1.1 仓库分两块：学习部分与运行部分

| 类别 | 目录 | 说明 |
|---|---|---|
| **学习部分** | `single-session-baseline/`、`learning-report/` | 单 session 的逐步教学 notebook，以及它的学习汇报副本。用来阅读代码、理解完整流程。**不参与全量结果生产。** |
| **运行部分** | `raw/`、`src/`、`scripts/`、`results/`、`docs/` | 真实 NWB 数据、分析核心实现、可执行脚本、正式结果与设计文档。**正式结果全部由这里的 Python 脚本产出。** |

一句话：**想学流程看 `single-session-baseline/` 和 `learning-report/`；想跑真实数据看 `src/` + `scripts/`。**

## 1.2 仓库结构总览

```text
Reanalysis_DANDI469_NWB/
│
├── single-session-baseline/            学习部分：单 session 教学 notebook
│   ├── README.md                       本文件夹导读：三个文件的用途与阅读顺序
│   ├── read_data.ipynb                 推荐入口：逐步讲解从读 NWB 到统计画图的完整流程
│   ├── data_dictionary.json            该 session 的字段映射与结构检查摘要
│   └── unit_level_statistics.csv       5 个基线 unit 的统计结果（回归基线）
│
├── learning-report/                    学习部分：学习汇报
│   ├── learning_record.md              复盘：项目、数据、实验、流程、疑问、统计基础
│   ├── read_data.ipynb                 完整流程 notebook（上面的副本）
│   ├── figures/                        报告用图
│   │   ├── trial_timeline.png          单 trial 时间线图
│   │   ├── main_test_flow.png          主检验流程图
│   │   ├── single_session_results.png  单 session 主检验结果图
│   │   └── all_sessions_results.png    全量 21 session 结果图
│   └── scripts/                        生成图的脚本
│       ├── make_trial_timeline.py
│       ├── make_main_test_flow.py
│       ├── make_single_session_results.py
│       └── make_all_sessions_results.py
│
├── raw/                                运行部分：原始 NWB 输入，不提交 Git
│   ├── all/000469/                     正式全量输入：41 个 NWB 文件
│   │   └── sub-*/sub-*_ses-*_ecephys+image.nwb
│   └── pilot-legacy/                   历史 pilot 副本：8 个文件，仅供复现旧工作
│
├── src/                                运行部分：可复用、无命令行副作用的分析核心
│   ├── data_paths.py                   统一选择输入根目录并定位 NWB 文件
│   ├── sternberg_primary.py            主分析的规范实现：读取、QC、特征、统计
│   └── __init__.py                     Python 包标识
│
├── scripts/                            运行部分：可直接执行的工作流入口
│   ├── inventory_sessions.py           扫描 NWB 结构，写出 session inventory
│   ├── run_primary_all.py              按 session 顺序完成全量数值主分析
│   ├── run_one_session.py              运行一个指定兼容 session 的主分析
│   ├── summarize_primary_v2_all.py     汇总 primary-v2-all 的 session/subject/unit 结果
│   ├── plot_session_qc.py              为单个 session 绘制少量 raster/PSTH
│   ├── run_representative_plots_v2.py  顺序生成 v2 的代表性图
│   ├── summarize_primary_results.py    primary-v1 的历史汇总入口
│   ├── run_representative_plots.py     primary-v1 的历史绘图入口
│   ├── inventory_encoding1_picids.py   图片 ID 探索性分析的结构盘点
│   └── run_encoding1_picid_exploration.py  图片 ID 探索性分析入口
│
├── results/                            运行部分：版本化分析产物；已有版本不覆盖
│   ├── primary-v2-all/                 当前正式全量主分析结果
│   ├── primary-v1/                     历史 4-session pilot 主分析结果
│   └── exploratory-v1/                 与主分析分开的图片 ID 探索结果
│
├── docs/                               运行部分：设计、计划、审计和冻结文档
│   ├── project_top_design.md           研究问题、QC、统计和可复现性设计
│   ├── multi_session_analysis_plan.md  多 session 工作计划及实际执行记录
│   ├── experiment_log.md               输入、命令、环境、排除和验证的时间序列日志
│   └── project_freeze_plan.md          冻结范围、验收条件和后续变更规则
│
├── pyproject.toml                      uv 项目定义与顶层依赖
├── uv.lock                             完整锁定依赖版本（uv sync 使用）
├── .python-version                     指定 Python 3.12
├── requirements.txt                    等价的人类可读依赖清单
├── .gitignore                          排除 raw 数据、NWB、缓存和本地临时文件
└── README.md                           本说明
```

## 1.3 学习部分：`single-session-baseline/`

这是整个仓库的**学习入口**，只针对一个 session（`sub-20_ses-2`），目的是把分析流程一步一步讲清楚。

| 文件 | 说明 |
|---|---|
| `README.md` | 本文件夹导读：三个文件各自干什么、想了解什么该读哪个 |
| `read_data.ipynb` | 逐步讲解：打开 NWB → 结构检查 → trial QC → unit QC → 窗口特征 → 置换检验/Bootstrap/FDR → raster 与 PSTH。每个 cell 都有中文说明，代码**完整内联**在 notebook 里，可以直接看到每一步怎么算。 |
| `data_dictionary.json` | 该 session 的字段映射、字段类型、缺失情况和示例值。 |
| `unit_level_statistics.csv` | 该 session 5 个 QC unit 的统计结果，用作回归基线。 |

**注意**：`read_data.ipynb` 为了教学，把逻辑内联实现，**不 import `src/`**。它与 `src/sternberg_primary.py` 是两份平行实现，目前参数一致、`sub-20` 数值逐位相同（notebook 写出的 `unit_level_statistics.csv` 与 `results/primary-v2-all/sub-20_ses-2/` 中的同名文件一致，只是显示精度不同）。如果以后两者出现差异，**以 `src/` 为准**。

### 学习汇报：`learning-report/`

把完整流程 notebook 和学习复盘放在一起，可单独作为汇报材料：

| 文件 | 说明 |
|---|---|
| `learning_record.md` | 复盘记录：项目、数据、数据结构、实验与 trial、单 session 与全量处理流程、遗留问题、待补的统计学基础 |
| `read_data.ipynb` | `single-session-baseline/read_data.ipynb` 的副本（完整流程） |
| `figures/` | 报告用图：`trial_timeline.png`（单 trial 时间线）、`main_test_flow.png`（主检验流程）、`single_session_results.png`（单 session 结果）、`all_sessions_results.png`（全量 21 session 结果） |
| `scripts/` | 生成上面这些图的脚本（`make_*.py`） |

## 1.4 运行部分

### `raw/` —— 原始数据输入

- `raw/all/000469/` 是正式分析**唯一应使用**的输入根目录；`src/data_paths.py` 会优先选择它，只有在完整数据不存在时才回退到 `raw/pilot-legacy/`。
- `raw/pilot-legacy/` 里的 8 个 NWB 是早期 pilot 副本，已用 SHA-256 确认与全量目录中的对应文件逐字节相同，**不能与全量目录一起扫描或混合分析**。
- `raw/`、`*.nwb` 和缓存目录由 `.gitignore` 排除，仓库只保存代码、文档和分析产物。

### `src/` —— 分析核心

`src/` 负责“**如何分析**”：提供可导入的函数与常量，不决定批处理范围、命令行参数或绘图数量。

- `data_paths.py`：统一定位输入根目录和 NWB 文件。
- `sternberg_primary.py`：主分析的规范实现 —— trial QC、unit QC、窗口特征、置换检验、bootstrap、BH-FDR。

### `scripts/` —— 可执行入口

`scripts/` 负责“**何时、对哪些文件分析**”：调用 `src/`，处理命令行入口、按 session 顺序执行、写结果目录并记录日志。

| 脚本 | 作用 |
|---|---|
| `inventory_sessions.py` | 扫描全部 NWB，记录行数、哈希、关键字段存在性，判定 `primary_schema_compatible`，写出 `session_inventory.csv` |
| `run_primary_all.py` | 按 inventory 顺序批量完成全量数值主分析，写 `results/primary-v2-all/` |
| `run_one_session.py` | 用 `--input/--output` 跑单个 session |
| `summarize_primary_v2_all.py` | 汇总 primary-v2-all，生成 session/subject/unit 汇总表与可读报告 |
| `plot_session_qc.py` | 为单个 session 的少量代表性 unit 画 raster/PSTH |
| `run_representative_plots_v2.py` | 顺序调用绘图，处理 primary-v2-all 中选定的 session |
| `inventory_encoding1_picids.py` | 图片 ID 探索分析的结构盘点 |
| `run_encoding1_picid_exploration.py` | 图片 ID 训练/测试探索分析 |
| `summarize_primary_results.py`、`run_representative_plots.py` | primary-v1 的历史入口，保留用于复现旧结果 |

这个分层让同一套分析核心既能被全量脚本、单 session 脚本复用，也能与教学 notebook 对应，同时避免把 I/O 和批处理混进统计实现。

全量主流程：

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

（分析方法本身见「第二部分 2.2 实验流程」。）

### `results/` —— 结果产物

结果按版本保留，新问题应建新版本目录，不覆盖旧结果。

| 目录 | 范围 | 角色 |
|---|---|---|
| `results/primary-v2-all/` | 21 个兼容 `ses-2` session | 当前正式全量主分析 |
| `results/primary-v1/` | 4 个历史 pilot session | 回归基线与旧结果复现 |
| `results/exploratory-v1/encoding1_picid_train_test/` | 图片 ID 训练/测试探索 | 探索性结果，不作为主结论 |

`primary-v2-all/` 顶层文件：

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

每个完成 session 的目录（如 `results/primary-v2-all/sub-20_ses-2/`）：

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

`exploratory-v1/encoding1_picid_train_test/` 保存独立于主分析的图片身份探索：每个 session 的 `trial_split.csv` 记录训练/测试切分，`unit_picture_identity_statistics.csv` 记录图片 ID 统计；顶层 `session_summary.csv`、`unit_picture_identity_statistics_all_sessions.csv` 和 `exploratory_summary.md` 提供汇总。该目录中的发现**不得替代** `primary-v2-all/` 的主分析结论。

### `docs/` —— 设计与审计文档

| 文档 | 作用 |
|---|---|
| `project_top_design.md` | 研究问题、变量、QC、统计和可复现性设计 |
| `multi_session_analysis_plan.md` | 多 session 分析计划与实际执行记录 |
| `experiment_log.md` | 每个阶段的输入、命令、输出、排除原因和验证结论 |
| `project_freeze_plan.md` | 冻结边界、验收条件与后续分析的版本规则 |

## 1.5 环境与复现（uv）

项目使用 [uv](https://docs.astral.sh/uv/) 管理 Python 环境。依赖的顶层约束见 `pyproject.toml`，完整锁定版本见 `uv.lock`；`requirements.txt` 保留为等价的人类可读清单。首次克隆或换机后，在项目根目录执行：

```powershell
cd E:\BCI-workstation\NWB\Reanalysis_DANDI469_NWB
uv sync
```

之后可用 `uv run python scripts\<script>.py` 运行脚本，无需手动激活虚拟环境；也可以 `source .venv/Scripts/activate` 后再用普通 `python`。

### 复现全量主分析

数值处理在项目 uv 环境中完成。一次只运行一个 Python 分析进程；不要同时启动多个批处理脚本。

```powershell
cd E:\BCI-workstation\NWB\Reanalysis_DANDI469_NWB
uv run python scripts\inventory_sessions.py
uv run python scripts\run_primary_all.py
uv run python scripts\summarize_primary_v2_all.py
```

运行前应先检查 `results/primary-v2-all/session_inventory.csv`；只有具有固定 Encoding1 事件定义的 session 才能进入主流程。某个 session 若失败，`run_primary_all.py` 会在 `session_run_log.csv`、`session_failures.csv` 和对应 `failure.json` 中记录原因，不会静默跳过。

数值结果确认无误后，才运行少量代表性绘图（与数值分析使用同一个 uv 环境）：

```powershell
uv run python scripts\run_representative_plots_v2.py
```

该绘图入口顺序处理选定 session 中的少量 unit；不要改造成一次生成所有 unit 的大型 raster/PSTH 图。

### 复现单 session 基线

`single-session-baseline/read_data.ipynb` 优先使用全量目录中的 canonical 文件 `sub-20_ses-2_ecephys+image.nwb`，仅在完整数据目录不存在时回退至 `raw/pilot-legacy/`。在项目根目录执行：

```powershell
uv run jupyter nbconvert --to notebook --execute --inplace .\single-session-baseline\read_data.ipynb
```

notebook 的新输出会写回 `single-session-baseline/`（`data_dictionary.json` 和 `unit_level_statistics.csv`），因此运行前应确认自己需要更新该教学/回归基线。

notebook 的 kernel 元数据已指向 uv 环境（kernel 名 `reanalysis-dandi469-nwb`）。如果在新机器上该 kernel 尚未注册，先执行：

```powershell
uv run python -m ipykernel install --user --name reanalysis-dandi469-nwb --display-name "Reanalysis DANDI469 (uv .venv)"
```

## 1.6 冻结与变更规则

后续若要处理 `ses-1` 的不同事件结构、比较图片 ID、记忆负荷、正确率或脑区效应，应创建新的结果版本和对应分析计划。**不得修改当前 `primary-v2-all/` 中已冻结的主分析文件**来承载新的假设或参数。

---

# 第二部分 · 实验说明

## 2.1 数据集

### 数据从哪来

- **数据集**：DANDI 000469 *Human Single Neuron Recordings During a Working Memory Task*，由 Rutishauser 实验室公开发布（DANDI 上的 ID 为 `000469`）。
- **发布版本**：`0.240123.1806`；访问级别 OpenAccess；许可 **CC BY 4.0**。
- **数据论文**：<https://pmc.ncbi.nlm.nih.gov/articles/PMC10796636/>；**官方发布代码**：<https://github.com/rutishauserlab/workingmem-release-NWB>。
- **规模**：21 名受试者、41 个 NWB session 文件、约 1,809 个 units，总量约 9.8 GB。本项目使用的副本位于 `raw/all/000469/`，每个文件约 25–616 MB。
- **受试者与记录**：受试者为因临床需要而植入颅内微丝电极的患者，记录的是**人类单神经元 spike**（不是动物数据，也不是头皮 EEG/fMRI）。记录脑区以 `electrodes.location` / `electrode_groups[].location` 为准，涵盖内侧颞叶（MTL，如海马、杏仁核）及部分运动/前运动、扣带等区域。
- **本项目是二次分析**：不采集数据、不重新做 spike sorting，只使用发布版 NWB 中已经整理好的 trials 和 units。

### 收集到的数据是什么样（已预处理）

本数据集是**已经预处理过的发布版本**，而不是原始宽带电压：

- 项目直接使用 `units.spike_times`（已完成 spike sorting），**不重新 sorting、不做滤波、不做 LFP/相位分析**。
- 文件中没有需要本项目处理的连续电压信号；`processing` 组为空。有用信息集中在 `acquisition.events`、`trials`、`units`、`electrodes`、`electrode_groups` 和 `devices`。
- 因此这里的“原始数据”指的是发布版 NWB 文件本身，不是电极记录到的原始信号。

### NWB 数据结构

每个 `*_ecephys+image.nwb` 是一份 NWB 2.x 文件，结构如下：

| 组 / 表 | 内容 |
|---|---|
| `session_description` / `identifier` / `session_start_time` | 受试者编号、全局标识（`SBID_*` 为 Sternberg，`SCID_*` 为 screening）、session 起始时间 |
| `subject` | 受试者信息 |
| `devices` / `electrode_groups` | 记录设备与电极组；`electrode_groups[].location` 记录脑区 |
| `electrodes` | 电极表：`x, y, z, location, filtering, group, group_name, origChannel` |
| `acquisition.events` | TTL 事件时间序列（TimeSeries） |
| `trials` | 每行一个 trial，含事件时间戳、记忆负荷、图片 ID 和行为字段（本数据集共 19 列） |
| `units` | 每行一个已排序 unit：`spike_times`、`electrodes`、`clusterID_orig`，以及波形质量指标 `waveforms_mean_snr`、`waveforms_peak_snr`、`waveforms_isolation_distance`、`waveforms_mean_proj_dist` |
| `processing` | 本数据集为空 |

关键字段映射：主分析的对齐事件是 `trials.timestamps_Encoding1`（第一张编码图片 onset）；`units.electrodes` 通过 `electrodes.location` 关联到脑区。完整的实际字段清单见 `single-session-baseline/data_dictionary.json`。

### 数据集层级与 session 兼容性

- `raw/all/000469/` 下共 41 个文件：**20 个 `ses-1`（screening）+ 21 个 `ses-2`（Sternberg）**。
- 只有 21 个 `ses-2` 文件同时具备 `timestamps_FixationCross`、`timestamps_Encoding1`、`timestamps_Encoding1_end` 三个字段，它们是当前主分析的输入。
- 20 个 `ses-1` 文件缺少这三个字段，不能在不改变事件定义的前提下套用本主分析，因此在数值分析前被**明确排除并留下审计记录**，而不是静默跳过。
- 文件命名规则为 `sub-<subject>_ses-<session>_ecephys+image.nwb`，一个文件对应一次 session。

## 2.2 实验流程

### 任务范式与刺激

范式是 **Sternberg 工作记忆任务**：先记住一组图片，随后判断 probe 图片是否属于刚才记住的那组。

- 每个受试者有两个 session：
  - `ses-1`（screening，标识前缀 `SCID`）：筛查任务，用来挑选对该受试者神经反应较强的图片。
  - `ses-2`（Sternberg，标识前缀 `SBID`）：正式工作记忆任务，图片来自 screening 的结果。
- **刺激是图片**。`loads` 字段表示本 trial 的记忆负荷（本数据集中取 1/2/3，即呈现 1–3 张编码图片）；每张图片的 ID 保存在 `loadsEnc1_PicIDs`、`loadsEnc2_PicIDs`、`loadsEnc3_PicIDs`、`loadsProbe_PicIDs`。
- 单个 trial 的时间线（以 `sub-20_ses-2` 第一个 trial 为例，单位秒）：

| 阶段 | trial 字段 | 示例时间 |
|---|---|---:|
| 注视 fixation | `timestamps_FixationCross` | 19.34 |
| 第一张编码图片出现 | `timestamps_Encoding1` | 20.38 |
| 第一张编码图片结束 | `timestamps_Encoding1_end` | 21.40 |
| 第二张编码图片 | `timestamps_Encoding2` / `_end` | 21.60 |
| 第三张编码图片 | `timestamps_Encoding3` / `_end` | 22.75 |
| 保持期开始 | `timestamps_Maintenance` | 23.77 |
| probe 出现 | `timestamps_Probe` | 26.40 |
| 受试者反应 | `timestamps_Response` | 27.12 |

- 行为结果存在 `response_accuracy`（0/1）和 `probe_in_out`（probe 是否在记忆集合内）。
- 原始 TTL marker 另外保存在 acquisition 的 `events` TimeSeries 中（例如 11=注视、1/2/3=第 1/2/3 张图、6=保持期开始、7=probe、8=反应）；本项目主要使用 trials 表中已整理好的事件列。
- **重要限制**：Sternberg 用的图片本身是 screening 阶段按神经反应挑出来的，因此结果带有选择偏差，不能直接解释成普通人群中的视觉选择性或“概念细胞”比例。

### 主分析问题与固定口径

在**每个可兼容 session 内**独立回答：

> QC 合格的单神经元，在第一张编码图片呈现后的放电率，是否高于同一 trial 内的 fixation 基线？

| 项目 | 固定定义 |
|---|---|
| 对齐事件 | `timestamps_Encoding1`，即第一张编码图片开始出现 |
| 基线窗 | `[-0.8, 0.0)` 秒 |
| 反应窗 | `[0.2, 1.0)` 秒 |
| 单位内特征 | 每个保留 `unit × trial` 的反应窗放电率减基线窗放电率，单位为 Hz |
| 单元检验 | session 内 10,000 次单尾配对置换检验，备择为图片后放电率更高 |
| 不确定性 | 5,000 次 bootstrap 置信区间 |
| 多重比较 | 仅在同一 session 内做 BH-FDR，阈值 `q < 0.05` |
| 随机种子 | `20260901`（只用于置换与 bootstrap 的可复现性，输入数据全部真实） |
| 数据汇总限制 | 不跨 session 合并 trial；不把 unit 当作独立受试者做总体推断 |

### 分析步骤（从 spike 到结论）

1. **读取与映射**：打开 NWB，取 `trials`、`units`、`electrodes`；把 `timestamps_Encoding1` 作为对齐零点，`units.spike_times` 作为 spike 时间，`units.electrodes` 关联到脑区。
2. **trial QC**：事件时间须为有限实数、顺序合理，基线窗和反应窗都落在可用记录范围内。
3. **unit QC**：`spike_times` 须有限且单调递增，检查活跃 trial 数与 ISI 边界。
4. **窗口特征**：对每个保留的 `unit × trial`，分别统计基线窗和反应窗的 spike count，换算为放电率 Hz（窗长 0.8 s），并计算差值。
5. **单元内统计**：对每个 unit 的 trial 配对差值做 10,000 次单尾置换检验和 5,000 次 bootstrap 置信区间。
6. **多重比较**：只在同一 session 内做 BH-FDR，标记 `q < 0.05`。
7. **汇总与绘图**：按 session/subject 汇总描述结果；另用少量代表性 unit 的 raster/PSTH 做时间对齐 QC，图不参与统计。

主分析不导入 Matplotlib。数值结果确认后，才在 uv 环境里生成少量代表性图。

## 2.3 实验结果

### 单 session 基线（`sub-20_ses-2`）

`single-session-baseline/` 固定保存 `sub-20_ses-2` 的教学和回归基线。该 session 在当前主分析口径下保留 135 个 trial、5 个通过 QC 的 unit。

- 5 个 unit 在 session 内 FDR 校正后均未显著（`q < 0.05` 的 unit 数为 0）。
- 5 个 unit 的平均放电率差均值为 `0.065 Hz`，中位数为 `0.102 Hz`；这不是显著的 session 内总体检验，也不能推广到其他受试者。
- 该结果说明：对于 `sub-20_ses-2`，在当前固定时间窗和单尾检验下，没有足够证据支持图片出现后存在一致的放电率升高。

完整的单元统计见 `single-session-baseline/unit_level_statistics.csv`；其数值与全量版本中 `results/primary-v2-all/sub-20_ses-2/` 的同名结果一致。

### 全量主分析（21 个兼容 session）

41 个 NWB 文件中，21 个 `ses-2` 文件具有当前定义所需的 `timestamps_FixationCross`、`timestamps_Encoding1` 和 `timestamps_Encoding1_end` 字段，因此进入主分析。20 个 `ses-1` 文件缺少这三项字段，不能在不改变事件定义的前提下套用本主分析，已标记为 `excluded_incompatible_schema`。

21 个完成 session 合计保留 2,672 个 trial、901 个 QC unit。这些总数仅描述数据规模，并不构成跨 session 的合并检验。

- 16 个 session 含有至少一个 session 内 FDR 显著的 unit。
- 共有 101 个 unit 满足 `q < 0.05`；由于检验的备择是图片后升高，这 101 个 unit 的平均放电率差均为正。
- 不同 session 的整体单位效应方向并不一致：有的 session 的 unit 平均差为正，有的为负，也有多个 session 没有 FDR 显著 unit。
- 因此，当前证据支持“部分 session 中存在图片后放电率升高的 unit”，但不支持写成“所有 session 在图片后均增强”，也不能从本项目得出跨受试者的总体显著性结论。

各 session 的 trial 数、QC unit 数、显著 unit 数和效应描述见 `results/primary-v2-all/descriptive_summary.md` 与 `results/primary-v2-all/session_summary.csv`。

### 探索性图片 ID 结果

`results/exploratory-v1/encoding1_picid_train_test/` 保存了独立于主分析的图片身份探索。该目录中的发现属于探索性结果，**不得替代** `primary-v2-all/` 的主分析结论。
