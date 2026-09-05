# 基于公开 NWB 数据的人体侵入式视觉记忆神经电生理二次分析项目

> 这是一个基于已有公开数据的二次分析项目，不是重新进行数据采集实验。  
> 本轮只完成顶层设计，不下载数据、不修改分析代码。正式实施前，先确认数据集和主要研究问题。

## 1. 项目名称

**从 NWB 到 PSTH：人体单神经元对视觉工作记忆图片的事件锁定分析**

副标题：以 DANDI 000469 的一个 Sternberg 工作记忆 session 为例。

## 2. 项目摘要

本项目使用公开 NWB 数据，对一名受试者一个工作记忆 session 中的单神经元放电进行二次分析。我们将读取 trial、图片呈现事件、unit 和电极信息，把 spike time 对齐到第一张编码图片，比较图片呈现后的放电率与同一 trial 内的注视基线，并用 raster、PSTH、效应量和多重比较校正评估单元响应。项目重点是建立可复现、可核查的完整分析链条，而不是估计患者群体效应或重新声称发现“概念细胞”。

## 3. 候选数据集比较与最终推荐

以下信息按公开 DANDI 页面、数据论文、作者代码仓库和 PyNWB 示例核对，核对时间为 2026-09-01。若 DANDI 页面在后续发布新版本，应在项目配置中记录实际下载的版本并重新检查文件清单。

| 数据集 | 版本、许可证与访问 | 模态与范式 | 规模 | 关键 NWB 内容 | 公开代码 | 单文件下载 | 初学者评价 |
|---|---|---|---|---|---|---|---|
| DANDI 000004：Recognition Memory in the Human Medial Temporal Lobe | 当前核对版本 0.220126.1852；OpenAccess；CC BY 4.0 | 人体内侧颞叶单神经元，图片识别/熟悉度任务 | 59 名受试者、87 个 NWB 文件、1,863 units；总约 6.2 GB；典型文件约 54–74 MB | acquisition 中的事件/脉冲接口，stimulus，electrodes，trials，units；官方 PyNWB 教程直接使用其中一个约 72.6 MB 文件 | [Rutishauser lab release](https://github.com/rutishauserlab/recogmem-release-NWB)；[数据论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC7055261/) | 可以 | 文件小、教程成熟、图片识别直观；但部分任务的试次间隔和前一张图片响应可能使简单基线受污染 |
| DANDI 000469：Human Single Neuron Recordings During a Working Memory Task | 当前核对版本 0.240123.1806；OpenAccess；CC BY 4.0 | 人体内侧颞叶/相关区域单神经元；screening 后的 Sternberg 工作记忆任务 | 21 名受试者；41 个文件/session（20 screening、21 Sternberg）；1,809 units（约 907 screening、902 Sternberg）；总约 9.8 GB；单文件约 25.6–615.6 MB，中位数约 228.7 MB | trials 含事件时间戳和行为字段；units 含 spike times、质量相关字段，部分文件含原始/平均波形；electrodes、electrode_groups、devices 等 | [Rutishauser lab release](https://github.com/rutishauserlab/workingmem-release-NWB)；[数据论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC10796636/) | 可以；建议先取最小的 Sternberg 文件 | 有清晰的 0.9–1.0 s fixation 基线和第一张编码图片事件，最适合做配对基线比较；任务字段较多，需要先做结构报告 |
| DANDI 000623：Human intracranial electrophysiology during movie viewing | 当前核对版本 0.240227.2023；OpenAccess；CC BY 4.0 | 颅内电生理、眼动、行为与连续电影观看 | 完整多模态研究 20 人；DANDI ephys NWB 约 16 人、29 文件/session、1,450 units；总约 27.7 GB；单文件约 492 MB–1.26 GB，中位数约 929 MB | continuous ephys、units、electrodes、事件/行为及电影相关时间轴；具体字段需逐文件核对 | [项目代码](https://github.com/rutishauserlab/bmovie-release-NWB-BIDS)；[数据论文](https://www.nature.com/articles/s41597-024-03029-1) | 可以，但入门文件大 | 真实、丰富且有趣；连续信号和电影时间轴带来较高存储、预处理和事件解析负担，不适合作为第一阶段 |

### 最终推荐：DANDI 000469

推荐理由：

1. 主要问题可以在一个 Sternberg session 内定义清楚：第一张编码图片之后的放电率是否高于同一 trial 的 fixation 基线。
2. 数据说明中有明确的约 0.9–1.0 s fixation 区间，基线不必依赖前一个 trial 的空档。
3. 第一张编码图片有明确事件时间，可以直接做 spike-event alignment。
4. trial、unit、electrode 和质量相关信息足以训练完整的 PyNWB 分析流程。
5. 可以只下载一个文件；目前建议从 DANDI 000469 中选一个较小的 Sternberg 文件，例如 sub-20/sub-20_ses-2_ecephys+image.nwb，其公开清单大小约为 25,582,000 bytes。这个选择只依据入门成本，不代表该被试神经响应最好。

重要限制：Sternberg 任务中的工作记忆图片来自前面的 screening 选择。因此，主分析可以回答“所选图片呈现期间哪些 QC 合格单元有响应”，但不能不加限定地估计一般人群中的“概念细胞”比例，也不能把所有图片选择性都解释成纯粹的视觉选择性。

## 4. 必要的神经科学背景

- **神经元（unit）**：这里指由电极记录并经过 spike sorting 得到的一个放电单元。一次快速的动作电位在数据中表现为一个 spike time。
- **单神经元电生理**：用植入脑内的微电极记录神经元何时放电。最基础的问题是，在某个实验事件附近，spike 出现得是否更多。
- **颅内脑电/iEEG**：由脑内电极记录的局部电活动，可以包含连续电压信号、LFP，也可以经过 spike sorting 得到离散 spike times。这个项目的主结果使用 spike times，不把连续电压分析和 spike 分析混为一谈。
- **内侧颞叶（MTL）**：包括海马、杏仁核及邻近皮层，和记忆编码、熟悉度、视觉概念以及情境记忆有关。记录位置由 electrode/electrode_group 和数据论文共同解释。
- **工作记忆**：短时间内保持并操作少量信息。Sternberg 范式通常先呈现一组项目，再要求受试者判断探测项目是否在刚才记住的项目中。
- **基线**：事件前的一段时间，作为同一 trial 内放电水平的参照。基线不是“没有神经活动”，而是假设它与事件后时间窗在任务意义上可比较。
- **响应时间窗**：事件发生后用于汇总放电的区间。窗口需要在分析前定义，不能看完结果后再挑最漂亮的区间。
- **概念细胞**：对一个人、物体或抽象概念表现出选择性反应的神经元。一个单元在一项图片任务中显著，不足以自动证明它是概念细胞。

## 5. 实验范式的逐步解释

推荐从一个 Sternberg session 开始，按以下逻辑理解 trial：

1. 受试者进入 fixation（注视）阶段。这个阶段提供 trial 内的基线。
2. 屏幕依次呈现若干图片，形成一个需要短时记忆的项目集合。
3. 每张图片都有事件时间戳。主分析只锁定第一张编码图片，避免多张图片叠加造成事件归因困难。
4. 编码阶段结束后，受试者等待或执行保持任务。
5. 出现 probe/测试项目，受试者判断它是否属于刚才的集合。
6. NWB 的 trials 表应把上述事件和行为信息以列的形式组织起来；实际列名和事件定义以目标文件中的内容为准。

本项目先不把行为正确率、延迟或所有图片位置都纳入主假设。这样可以先验证最核心的“事件时间—spike—放电率”链路，再逐步增加复杂度。

## 6. 推荐数据集的 NWB 结构地图

目标文件读取后，预期先核对下列结构；其中字段名不是先验保证，必须由实际文件报告确认。

    NWBFile
    ├── session_description / identifier / session_start_time
    ├── subject
    ├── devices
    ├── electrode_groups
    │   └── group metadata（脑区、设备、描述）
    ├── electrodes
    │   └── electrode table（group、location、坐标、参考方式等）
    ├── acquisition
    │   └── event/continuous interfaces（如存在，先记录名称和时间基准）
    ├── processing
    │   └── ecephys 相关处理结果（如存在）
    ├── trials
    │   └── start/stop、fixation、encoding、probe、行为和图片字段
    └── units
        └── spike_times、unit id、electrode/region、quality、波形/ISI 等字段

第一份结构报告必须回答：

- trials 的起止时间和事件列分别叫什么；
- 第一张编码图片的时间是单独列、嵌套列，还是需要由多个事件字段重建；
- units 的 spike_times 是每个 unit 的独立数组还是 DynamicTableRegion 引用；
- unit 与 electrode/region 的连接字段叫什么；
- 数据时间单位、session 起点和事件时间是否使用同一个时钟；
- 是否存在 NaN、缺失 trial、重复 unit id 或异常时间戳。

## 7. 主要研究问题和假设

### 预注册式主要问题

在 DANDI 000469 的一个 Sternberg session 中，**QC 合格的单神经元在第一张编码图片呈现后的放电率，是否高于同一 trial 内的 fixation 基线？**

- 研究对象：一个 session 内的 QC 合格单神经元。
- 自变量：时间条件，基线 vs. 第一张编码图片后的响应。
- 因变量：每个 trial、每个 unit 在时间窗内的 spike count 转换得到的放电率（Hz）。
- 基线时间窗：相对于第一张编码图片 onset 的 [-0.8, 0.0) 秒，若实际 fixation 短于 0.8 秒则按预先规则缩短或排除该 trial。
- 响应时间窗：[0.2, 1.0) 秒。前 200 ms 作为视觉输入、显示器延迟和早期对齐误差的缓冲；窗口长度与基线相同，便于直接比较。
- 分析单位：主要推断单位是 unit；每个 unit 内的 trial 是重复观测。spike 不是独立观测。
- 主要比较：对每个 unit 计算 trial-wise response rate - baseline rate，并检验该差值是否倾向于高于 0。

### 主要假设

- H0：单位内配对差值的中心位置不高于 0。
- H1：单位内配对差值高于 0。
- 报告方向性效应量、95% 不确定性区间和 FDR 校正后的 unit-level 结果。

### 可以支持的结论

- 在这个 session、这些预先定义的窗口和 QC 规则下，某些单元的第一张编码图片后放电率高于其 trial 内基线。
- 响应大小、方向和估计不确定性如何分布。
- 事件对齐、trial 完整性和 unit QC 是否支持这个结论。

### 不能支持的结论

- 不能据此推断所有癫痫患者、健康人或整个人类的群体效应。
- 不能把单个显著 unit 自动称为“概念细胞”。
- 不能确定该响应是纯粹视觉输入、记忆编码、注意、眼动、运动或任务策略中的哪一种机制。
- 不能把离线 spike 分析描述成实时脑机接口性能。

## 8. 探索性问题

在主要分析通过结构和质量检查后，才考虑：

1. 图片 ID 或图片类别是否与单元响应有关。使用训练/测试 trial 划分，避免先用全部数据选出最佳图片再在同一数据上验证。
2. 工作记忆负荷或图片位置是否调制放电率。
3. 正确与错误 trial 的响应是否存在差异，但只在错误 trial 数量足够时分析。
4. 单元响应是否随 trial 顺序漂移。
5. 按脑区做描述性比较；一个患者内的脑区差异不能当作跨患者推断。
6. 在完成单元级分析后，进行简单群体描述或严格交叉验证的解码。深度学习不属于本项目边界。

## 9. 自变量、因变量、协变量和分析单位

| 类型 | 变量 | 说明 |
|---|---|---|
| 主要自变量 | 时间条件 | baseline 或 response |
| 探索性自变量 | 图片 ID、图片类别、位置、记忆负荷、行为正确性、trial order | 只有在字段和样本量确认后使用 |
| 主要因变量 | window firing rate | spike count / window duration，单位 Hz |
| 辅助因变量 | spike count、PSTH bin rate、response-baseline difference | 用于图和质量核对 |
| 可能协变量 | trial duration、反应时、眼动/运动指标、脑区、session 内时间 | 不在第一版主模型中自动调整 |
| 主要分析单位 | unit | unit 内 trial 是重复观测 |
| 观察层级 | trial、unit、session、subject | 报告每层的数量；不要把 trial 直接当作独立患者样本 |

## 10. 纳入与排除标准

### Trial 纳入

- trial 有明确的第一张编码图片 onset；
- 时间戳为有限实数，且事件顺序合理；
- 基线窗和响应窗都落在可用记录范围内；
- 没有明显重复或负持续时间；
- 若分析行为条件，行为标签不缺失。

### Unit 纳入

- 有非空、有限、单调递增的 spike_times；
- unit 与可解释的电极或脑区信息能够关联，或明确标为未知；
- 通过数据集已有的质量字段；若质量字段缺失，执行项目内最小 QC；
- 在纳入 trial 期间有足够的活动，例如至少 10 个 trial 出现 spike，具体阈值在看到实际样本量后冻结。

### 排除

- 重复 unit、明显越界时间或 spike_times 无法与 session 对齐；
- trial 事件字段缺失或窗长度不足；
- 明显断电、记录中断或该 trial 的同步信息不可信；
- 质量检查显示严重异常，如极端 ISI violation、波形缺失且无法解释。

所有排除都要记录原因和数量，不能只在最终图中隐式删除。

## 11. 从读取 NWB 到结果图的完整分析流程

1. **固定数据版本**：记录 DANDI ID、发布版本、asset path、文件哈希、下载日期和许可证。
2. **只读检查文件**：打开 NWB，列出 acquisition、processing、electrodes、trials、units 和字段。
3. **建立数据字典**：将实际字段名映射到项目内部的标准名称，例如 first_encoding_onset、spike_times、region。
4. **生成结构报告**：输出对象类型、表格行数、时间范围、缺失比例和示例值。
5. **提取 trials**：构造一张 tidy trial 表，每行一个 trial。
6. **提取 units**：构造 unit 元数据表，每行一个 unit；spike_times 保持为数组或可追溯的对象。
7. **执行事件对齐**：用 onset 作为零点，将 spike time 转为相对时间。
8. **计算窗口特征**：按 unit × trial 计算 baseline 和 response spike count/rate。
9. **质量控制**：检查 trial 数、窗边界、spike 范围、unit 活跃度、ISI 和事件顺序。
10. **画单元级图**：先画少量 unit 的 raster 和 PSTH，核对时间方向和单位。
11. **进行主要统计**：unit 内配对差值、置换检验、效应量、bootstrap 区间和 BH-FDR。
12. **生成汇总图**：响应分布、显著 unit 比例（只作 session 描述）、代表性 unit、QC 图。
13. **写出分析表**：保存 trial-level、unit-level 和 QC summary，附参数文件。
14. **可重复运行检查**：从干净 kernel/环境重新运行 Notebook，确认结果和随机种子一致。

## 12. spike time 与刺激事件对齐方法

设第一张编码图片 onset 为 t_event，某个 unit 的 spike time 为 t_spike。相对时间为：

    t_relative = t_spike - t_event

对每一个 trial 和 unit：

1. 先确认 spike 和事件使用相同时间基准；若存在 acquisition 起点或 offset，必须显式转换。
2. 在 [-0.8, 1.0) 秒的大范围内提取 spike，画 raster 前先检查是否有明显错位。
3. 统计 baseline 窗 [-0.8, 0.0) 和 response 窗 [0.2, 1.0) 的 spike。
4. 窗口采用左闭右开，避免边界 spike 被重复计数。
5. 对缺少 onset 或窗越界的 trial，按预先规则排除并记录。
6. 第一版不使用动态时间扭曲、复杂同步校正或连续 LFP 相位锁定；先保证事件和 spike 的时钟关系正确。

最小伪代码逻辑：

    for each unit:
        for each valid trial:
            relative_spikes = spike_times - first_encoding_onset
            baseline_count = count(-0.8 <= relative_spikes < 0.0)
            response_count = count(0.2 <= relative_spikes < 1.0)
            baseline_rate = baseline_count / 0.8
            response_rate = response_count / 0.8

## 13. raster、PSTH、放电率和选择性分析的定义

- **Raster plot**：横轴是相对事件时间，纵轴是 trial；每个短线代表一个 spike。它回答“放电是否在事件附近成批出现”。
- **PSTH**：把相对时间划分为固定 bin，例如 50 ms，统计每个 bin 的 spike 数并除以 trial 数和 bin 宽度，得到 Hz。它回答“群体平均时间进程如何变化”。PSTH 的平滑只用于可视化，不改变主统计窗口。
- **放电率**：给定窗内 spike count 除以窗长度。等长窗口可以直接做配对差值。
- **响应差值**：delta_rate = response_rate - baseline_rate。主效应量可报告均值、中位数、配对差值分布和 bootstrap 95% CI。
- **响应选择性**：图片/类别条件之间的放电率差异。第一版把它定义为探索性，并使用独立的训练/测试划分或预先定义的图片类别；不根据全数据的显著性选择 unit 后再验证。

## 14. 单元质量控制项目

最小 QC 清单：

1. spike_times 是否有限、递增、在 session 时间范围内。
2. 每个 unit 的总 spike 数、平均 firing rate 和有效 trial 数。
3. trial 间是否有极少数异常高放电的 outlier。
4. ISI violation：不应出现大量不可能的极短间隔；阈值优先采用数据集论文/代码中既有定义。
5. 波形字段是否存在，波形幅度、持续时间和缺失比例是否合理。
6. unit 与电极、脑区和记录时段是否能够对应。
7. baseline 期间是否完全无放电；若大量为零，考虑使用计数模型/置换而不是默认正态检验。
8. event alignment sanity check：随机抽取 trial，确认 raster 的零点和第一张图片事件一致。
9. trial 数是否足以支持 unit-level 统计；稀疏 unit 的结果标为低精度或排除。
10. 数据完整性：NWB 文件能否重复打开，文件哈希是否稳定，关键表格行数是否一致。

每个主要结果至少配一项质量检查：例如主响应图旁边报告有效 trial 数、基线/响应窗覆盖率和 unit QC 状态。

## 15. 统计方法、效应量和不确定性

### 主要检验

对每个 unit，得到一组 trial-wise 配对差值：

    d_i = response_rate_i - baseline_rate_i

使用 unit 内标签交换的 paired permutation test：在每个 trial 内随机交换 response 和 baseline 标签，重复 10,000 次，检验平均差值是否大于 0。该方法不要求 rate 差值服从正态分布，并保持 trial 配对结构。

### 报告内容

- 估计效应：mean delta Hz 和 median delta Hz；
- 95% bootstrap CI：对 trial 配对差值重采样 5,000 次；
- 方向性 p 值和 BH-FDR q 值；
- 可选的配对 common-language effect：随机抽取一对 trial 时 response 高于 baseline 的概率；
- unit 数、每个 unit 的有效 trial 数和排除数；
- 统计检验的独立观测单位明确写为 unit 内的 trial 配对，而不是 spike。

### 零膨胀和低计数

如果大量窗口为零，优先保留计数和置换结果，避免把带大量零值的数据强行套用普通 t 检验。Poisson/负二项混合模型可以作为后续扩展，但不是第一版的必要条件。

### 跨层级解释

当前只有一个 subject/session，因此“显著 unit 比例”只能作为该 session 的描述。若要做患者层面的推断，必须增加受试者并以 subject 为更高层级的独立单位，不能将所有 trial 或 unit 直接池化。

## 16. 循环分析、数据泄漏、伪重复和多重比较

- **循环分析**：不能先用全部 trial 找出最显著的 unit，再用同一 trial 声称该 unit 显著。主问题使用预先定义的所有 QC 合格 unit；图片选择性使用 train/test split。
- **数据泄漏**：任何标准化、特征选择、阈值选择和模型调参都只能在训练数据完成，再在测试数据评估。
- **伪重复**：同一 unit 的 trial 是重复观测；同一 subject 的多个 unit 不是多个独立患者。图中同时标明 trial、unit、session 和 subject 层级。
- **多重比较**：unit-level 主要检验使用 Benjamini–Hochberg FDR，预先设定 q < 0.05。探索性结果单独标注，不与主要结果混在同一个显著性结论中。
- **窗口选择**：baseline、response、bin 宽度和平滑参数在查看结果前写入配置。PSTH 中的平滑曲线只用于展示。
- **结果核查**：随机抽取未参与选择的 unit/trial 做复现图；对原始 spike count 和 rate 两种表示交叉核对。

## 17. 计划生成的图

计划生成五张图，实际可根据信息量合并为三至五张：

1. **数据与实验范式图**：一个 trial 的事件时间线、NWB 结构简图和 trial 数量。回答“分析使用的事件到底是什么”。
2. **代表性 unit raster + PSTH**：显示 baseline、response 窗和零点。回答“事件附近的放电时间结构是否可信”。
3. **unit-level paired effect 图**：每个 unit 的 baseline 与 response 配对点/线，按 q 值或脑区着色。回答“哪些 unit 的放电率提高，效应有多大”。
4. **效应量和不确定性汇总图**：delta Hz 的分布、bootstrap CI 或 forest-like 点图，并附有效 trial 数。回答“结果是否由少数极端 unit 驱动”。
5. **QC 图**：unit firing rate、ISI violation、波形可用性、trial 覆盖率和排除流程。回答“神经结果是否可能由记录质量或数据缺失造成”。

## 18. Python 技术栈及职责

- **PyNWB**：读取 NWBFile、DynamicTable、trials、units、electrodes 和时间序列。
- **DANDI client 或 DANDI CLI**：查询版本、文件清单和下载单个 asset；不在 Notebook 中隐藏数据来源。
- **NumPy**：数组、spike 时间筛选、计数和随机置换。
- **pandas**：trial/unit tidy 表、质量摘要和结果导出。
- **SciPy**：基础统计分布、bootstrap 辅助函数和数值工具。
- **statsmodels**：Benjamini–Hochberg FDR 和必要的多重比较工具。
- **Matplotlib**：raster、PSTH、效应量和 QC 图；优先保持图形可读、可复现。
- **Jupyter**：按“读取—检查—提取—对齐—统计—作图”组织 Notebook。
- **JSON/YAML、pathlib、hashlib、platform**：保存参数、路径、文件哈希和环境信息。

第一版暂不引入 Neo、Elephant、MNE、SpikeInterface 或 ALPACA：

- Neo/Elephant 适合更复杂的神经数据对象和点过程分析，但本项目的 spike window count、PSTH 和置换检验可由 NumPy 完成。
- MNE 更适合连续 EEG/MEG/iEEG 预处理；当前主问题不需要 LFP 滤波。
- SpikeInterface 更适合从原始连续电压到 spike sorting 的流程；本项目使用已经整理好的 NWB units。
- ALPACA 和深度学习会显著扩大工程和解释范围，等基础分析验证后再决定是否需要。

## 19. 建议的项目目录结构

    project/
    ├── README.md
    ├── environment.yml 或 requirements.txt
    ├── data/
    │   ├── raw/              # 原始 NWB；通常不提交版本库
    │   ├── interim/          # 结构报告和标准化中间表
    │   └── processed/        # trial-level、unit-level、QC 结果
    ├── notebooks/
    │   ├── 01_nwb_structure_report.ipynb
    │   ├── 02_extract_trials_units.ipynb
    │   ├── 03_alignment_raster_psth.ipynb
    │   ├── 04_qc_and_primary_test.ipynb
    │   └── 05_final_figures.ipynb
    ├── src/
    │   ├── io_nwb.py
    │   ├── trial_events.py
    │   ├── alignment.py
    │   ├── quality_control.py
    │   ├── statistics.py
    │   └── plotting.py
    ├── configs/
    │   └── analysis_parameters.yaml
    ├── reports/
    │   ├── figures/
    │   └── tables/
    └── blog/
        └── technical_blog.md

第一阶段只处理一个 subject、一个 session 和少量 unit；原始数据不要复制到博客或公开仓库。

## 20. 数据版本、参数、随机种子和环境记录

在配置文件和 Notebook 输出中记录：

- DANDI ID、发布版本、asset path、文件哈希、下载日期和许可证；
- subject、session、NWB 文件名；
- 实际字段映射和时间基准；
- baseline [-0.8, 0.0)、response [0.2, 1.0)；
- PSTH bin = 50 ms；
- 平滑只用于显示，初始 Gaussian sigma = 75 ms；
- unit 内置换次数 = 10,000；
- bootstrap 次数 = 5,000；
- FDR q 阈值 = 0.05；
- trial/unit 纳入和排除阈值；
- 随机种子 = 20260901；
- Python 版本、PyNWB、numpy、pandas、scipy、statsmodels、matplotlib、jupyter 版本；
- 操作系统和 Notebook 执行时间。

每次参数变化都生成新的结果目录或配置版本，不覆盖旧结果。

## 21. 按天/里程碑划分的实施计划

### 里程碑 0：确认范围（半天）

目标：确认 DANDI 000469 和主要问题。  
输入：本设计文档。  
输出：固定的数据集版本、session 和参数草案。  
验收：能够用一句话写出研究对象、自变量、因变量和两个时间窗。

### 里程碑 1：下载并检查一个 NWB 文件（第 1 天）

目标：确保文件可读并知道实际结构。  
输入：一个 Sternberg NWB asset。  
输出：文件哈希、对象清单、表格行数和字段摘要。  
验收：PyNWB 可重复打开；trials、units、electrodes 的关键字段已列出。

### 里程碑 2：数据字典和 NWB 结构报告（第 2 天）

目标：将真实字段映射到分析字段。  
输入：结构报告。  
输出：data dictionary、缺失值摘要、时间基准说明。  
验收：能够定位第一张编码图片 onset、spike_times 和 unit-electrode 关系。

### 里程碑 3：提取 trial、unit、electrode 和事件（第 3 天）

目标：生成稳定的 tidy 表。  
输入：NWB 文件和数据字典。  
输出：trial 表、unit 元数据表、electrode 表。  
验收：每个表都有行数、唯一 ID、时间范围和排除原因。

### 里程碑 4：事件对齐、raster 和 PSTH（第 4–5 天）

目标：验证 spike 与事件的时间关系。  
输入：trial/event/unit 表。  
输出：相对 spike、代表性 unit raster、PSTH。  
验收：零点正确、窗口边界正确、PSTH 单位为 Hz，随机抽查无明显错位。

### 里程碑 5：QC 和条件比较（第 6–7 天）

目标：冻结纳入标准并计算 trial-wise rate。  
输入：对齐后的 spike。  
输出：QC summary、baseline/response 表和排除流程。  
验收：至少少量 unit 通过 QC；所有排除可追溯。

### 里程碑 6：统计检验和最终图（第 8–9 天）

目标：完成主要问题和探索性结果。  
输入：冻结的 unit/trial 数据。  
输出：置换 p、FDR q、效应量、CI 和三至五张图。  
验收：独立观测单位、参数、随机种子和多重比较方法都写入结果表。

### 里程碑 7：可重复 Notebook（第 10 天）

目标：从干净环境重跑。  
输入：固定版本和配置文件。  
输出：可顺序执行的 Notebook 和运行说明。  
验收：重跑结果在允许的浮点误差内一致。

### 里程碑 8：技术博客（第 11–12 天）

目标：解释从实验范式到结果图的完整逻辑。  
输入：最终 Notebook、图和 QC 表。  
输出：技术博客初稿和限制说明。  
验收：读者能区分数据事实、分析选择、统计推断和不能支持的结论。

## 22. 各阶段完成标准

每个阶段都必须有四类记录：

1. 输入：具体文件、版本和字段；
2. 操作：参数和代码入口；
3. 输出：表、图或报告；
4. 验收：一个可以独立检查的条件。

任何阶段若出现字段不一致，先停止下游分析，更新结构报告和数据字典；不能用猜测的列名继续跑。

## 23. 可能遇到的问题及排查顺序

1. **文件打不开**：检查下载是否完整、哈希、PyNWB/HDF5 版本和文件路径。
2. **找不到 trials 或 units**：先打印 NWB 顶层对象和实际接口名称；不要假设对象一定位于 acquisition。
3. **字段名不同**：读取 DynamicTable 的列名和前几行，更新数据字典。
4. **事件时间和 spike 时间错位**：检查 session 起点、timestamps、rate/starting_time、单位和可能的 offset。
5. **trial 数为零或大量缺失**：检查筛选条件、NaN、事件类型和 trial 边界。
6. **raster 全部挤在零点或完全空白**：检查时间单位、事件列是否为 onset、spike_times 是否为绝对时间。
7. **PSTH 数值异常**：核对 bin 宽度、trial 数、窗口长度和 Hz 换算。
8. **所有 unit 都不显著**：先检查对齐、基线覆盖和统计方向，不要立刻放宽 p 值或扩大搜索窗口。
9. **所有 unit 都显著**：检查重复 trial、事件复制、单位换算和是否把同一 spike 重复计数。
10. **unit 与脑区无法连接**：保留未知区域标签，查看 electrode_groups 和数据论文，不强行推断解剖位置。
11. **内存不足**：只读取一个 asset、少量 unit 或 trial，避免把连续 acquisition 全部载入内存。
12. **结果不可复现**：固定配置、随机种子、软件版本和文件哈希，重新启动 kernel 验证。

## 24. 最终技术博客标题和详细提纲

### 标题

**《从公开 NWB 文件到单神经元 PSTH：一次人体视觉工作记忆数据的可复现二次分析》**

### 提纲

1. 为什么选择公开 NWB 数据，以及“二次分析”意味着什么；
2. DANDI 000469、Sternberg 范式和人体内侧颞叶记录背景；
3. NWB 文件中 trials、units、electrodes 和事件如何关联；
4. 研究问题、预先定义的基线窗和响应窗；
5. 从绝对 spike time 到事件相对时间；
6. raster、PSTH 和放电率计算；
7. unit QC、trial 排除和每一步的质量检查；
8. 配对置换检验、bootstrap CI、效应量和 FDR；
9. 主要图逐张解释：每张图回答什么问题；
10. 探索性图片选择性及其 train/test 防泄漏方案；
11. 哪些结论可以说，哪些结论不能说；
12. 数据版本、环境、随机种子和项目目录；
13. 遇到的数据结构问题和排查过程；
14. 局限性、停止扩展边界和下一步学习路线；
15. 附录：关键字段表、参数表和可重复运行说明。

## 25. 局限性和停止扩展的边界

### 主要局限性

- 单个 subject/session 不能支持人群层面的统计推断。
- 临床植入位置由治疗需要决定，存在选择偏差和脑区覆盖不均。
- spike sorting、unit 稳定性和电极定位依赖原始数据集处理流程。
- 视觉图片响应可能混合视觉输入、记忆编码、注意、眼动和任务策略。
- Sternberg 图片由前期 screening 选择，不能直接估计无偏的概念细胞比例。
- baseline 假设可能受到 trial 结构、注意和前序事件的影响。
- 事件时间戳、显示延迟和行为标记的精度可能限制早期响应解释。
- unit-level FDR 控制的是本 session 内的发现率，不等于跨患者的确认性证据。

### 停止扩展的边界

在以下条件满足前，不扩展到复杂分析：

- 结构报告、字段映射和时钟对齐未通过；
- raster/PSTH 仍显示系统性错位；
- QC 和排除流程不能复现；
- 主要问题的窗口、统计单位和多重比较规则尚未冻结；
- Notebook 不能从固定版本重跑。

完成这些基础目标后，才可以考虑多 session、跨患者层级模型、LFP/时频分析或严格交叉验证的群体解码。深度学习、复杂连接分析和实时脑机接口不属于本项目第一阶段。

## 参考资料

- [DANDI 000004 数据集页面](https://dandiarchive.org/dandiset/000004/0.220126.1852)
- [DANDI 000469 数据集页面](https://dandiarchive.org/dandiset/000469/0.240123.1806)
- [DANDI 000623 数据集页面](https://dandiarchive.org/dandiset/000623/0.240227.2023)
- [000004 数据论文：Human single-neuron responses during visual recognition memory](https://pmc.ncbi.nlm.nih.gov/articles/PMC7055261/)
- [000469 数据论文：Human single-neuron recordings during a working memory task](https://pmc.ncbi.nlm.nih.gov/articles/PMC10796636/)
- [000623 数据论文：Intracranial electrophysiology during movie viewing](https://www.nature.com/articles/s41597-024-03029-1)
- [000004 作者公开代码](https://github.com/rutishauserlab/recogmem-release-NWB)
- [000469 作者公开代码](https://github.com/rutishauserlab/workingmem-release-NWB)
- [000623 作者公开代码](https://github.com/rutishauserlab/bmovie-release-NWB-BIDS)
- [PyNWB 读取基础教程](https://pynwb.readthedocs.io/en/stable/tutorials/general/plot_read_basics.html)

## 下一步

请先确认以下两点：

1. 是否采用 DANDI 000469 的一个 Sternberg session 作为第一阶段数据；
2. 是否采用“第一张编码图片后放电率是否高于同一 trial fixation 基线”作为主要研究问题。

确认后再进入阶段 1：只下载并检查一个 NWB 文件。
