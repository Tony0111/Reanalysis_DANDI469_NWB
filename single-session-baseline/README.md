# single-session-baseline

`sub-20_ses-2` 的单 session 教学与回归基线。这里把完整分析流程放在一个 notebook 里逐步讲清楚，用来学习，也用来检查以后的改动有没有破坏原有结果。

## 三个文件分别是干什么的

| 文件 | 是什么 | 来源 |
|---|---|---|
| `read_data.ipynb` | 教学 notebook：从读 NWB 到统计画图的完整流程，每段配中文讲解 | 手工维护，推荐入口 |
| `data_dictionary.json` | 该 session 的字段映射与结构检查摘要（字段名、类型、缺失、示例值、unit→脑区） | notebook 第二段写出 |
| `unit_level_statistics.csv` | 5 个 QC unit 的统计结果，作为回归基线 | notebook 主检验第 3 步写出 |

## notebook 段落导航

| 段 | 内容 |
|---|---|
| 第一段 | NWB 文件结构检查（能否打开、三张核心表在哪） |
| 第二段 | 数据字典与字段映射（项目名 ↔ 实际列名），含 `fixation_event` 的含义 |
| 补充 | 单个 trial 的事件时间线图 |
| 第三段 | trial QC（事件顺序、窗口覆盖）+ **QC 原则笔记** |
| 第四段 | unit QC（spike 完整性、活动量）+ **本段在 QC 流程中的位置** |
| 第五段 | 按 unit × trial 计算窗口放电率（基线 / 响应 / 差值，675 行） |
| 补充 | unit × trial 关系热图 |
| 第六、七段 | 事件对齐 raster 与 PSTH + **待解决的疑问** |
| 最后一段 | 统计前 QC：ISI、零计数、极端计数 |
| 主检验第 1 步 | 配对置换检验、p 值 |
| 主检验第 2 步 | bootstrap 95% CI、common-language effect |
| 主检验第 3 步 | BH-FDR、q 值、最终结果表（写 CSV） |
| 主检验第 4 步 | 最终汇总图（配对效应图、森林图） |
| 文末附录 | **主检验四步涉及到的统计学方法清单**（待补基础） |

## notebook 里额外补充的笔记

除了流程代码，notebook 里还夹着几处学习笔记，读的时候不要漏掉：

- **关于 QC**（第三、四段）：QC 是原则而不是固定步骤；坏数据不报错、只会静默算错；排除型 vs 报告型 QC；**QC 要做三次**（导入之后 / 分析之前 / 分析之后）。
- **raster / PSTH 的待解决疑问**（第六、七段）：为什么需要这两张图、怎么读，先记下来待补。
- **统计学方法清单**（文末附录）：主检验四步涉及的方法，只列名字，之后专门补统计学基础。

## 想看什么，读哪个

| 你想了解 | 读这里 |
|---|---|
| 一个 NWB 文件长什么样、有哪些字段 | 第一、二段 + `data_dictionary.json` |
| trial / unit 怎么做质量控制（QC） | 第三、四段（含 QC 原则笔记） |
| 怎么把 spike 对齐到图片、算放电率 | 第五段 |
| raster / PSTH 怎么画、怎么读 | 第六、七段（含待解决疑问） |
| 置换检验 / bootstrap / FDR 怎么实现 | 主检验第 1–3 步 |
| 用到了哪些统计学概念 | 文末附录 |
| 这个 session 的最终数值 | `unit_level_statistics.csv` |
| 全量 21 个 session 的处理代码 | 仓库根的 `src/` 和 `scripts/`（本文件夹不参与全量生产） |

## 基线结论（sub-20_ses-2）

保留 135 个 trial、5 个通过 QC 的 unit。FDR 校正后没有 unit 显著（`q < 0.05` 的 unit 数为 0）；在当前固定窗口和单尾检验下，没有足够证据支持图片后放电率升高。此结论只适用于这个 session。

数值与 `results/primary-v2-all/sub-20_ses-2/unit_level_statistics.csv` 一致，只是显示精度不同。

## 运行

```powershell
uv run jupyter nbconvert --to notebook --execute --inplace .\single-session-baseline\read_data.ipynb
```

- 运行后 notebook 的输出会写回本文件夹的 `data_dictionary.json` 和 `unit_level_statistics.csv`。
- notebook 的 kernel 已指向 uv 环境（`reanalysis-dandi469-nwb`）。新机器上先注册：

```powershell
uv run python -m ipykernel install --user --name reanalysis-dandi469-nwb --display-name "Reanalysis DANDI469 (uv .venv)"
```

## 注意

本 notebook 为了教学，把分析逻辑**内联**实现，**不 import `src/`**，与 `src/sternberg_primary.py` 是两份平行实现。两者目前参数一致、`sub-20` 数值逐位相同；如果以后出现差异，以 `src/` 为准。
