"""Summarize independent session results without pooling trial observations."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_DIR / "results" / "primary-v1"


def write_descriptive_report(
    session_summary: pd.DataFrame,
    subject_summary: pd.DataFrame,
    all_units: pd.DataFrame,
) -> Path:
    session_rows = "\n".join(
        "| {file_name} | {trials} | {units} | {significant} | {positive} | "
        "{mean_delta:.3f} | {median_delta:.3f} |".format(
            file_name=row.file_name,
            trials=int(row.n_trials_kept),
            units=int(row.n_units_kept),
            significant=int(row.significant_units_q05),
            positive=int(row.positive_mean_delta_units),
            mean_delta=float(row.mean_of_unit_mean_delta_hz),
            median_delta=float(row.median_of_unit_mean_delta_hz),
        )
        for row in session_summary.itertuples(index=False)
    )
    subject_rows = "\n".join(
        "| {subject} | {sessions} | {trials} | {units} | {significant} | "
        "{mean_effect:.3f} |".format(
            subject=int(row.subject_id),
            sessions=int(row.sessions_analyzed),
            trials=int(row.trials_kept),
            units=int(row.units_kept),
            significant=int(row.significant_units_q05),
            mean_effect=float(row.mean_of_session_effects_hz),
        )
        for row in subject_summary.itertuples(index=False)
    )

    report = f"""# Primary-v1 跨 Session 描述性汇总

生成时间：{datetime.now().astimezone().isoformat(timespec="seconds")}

## 分析范围

本报告只包含 4 个具有当前固定事件定义的 `ses-2` Sternberg session。每个 session 的 baseline 为 `[-0.8, 0.0)` 秒，response 为 `[0.2, 1.0)` 秒；`mean_delta_hz` 是 unit 内每个 trial 的 response firing rate 减 baseline firing rate 后再取平均。

这些数据按 session 独立分析，未把不同 session 的 trial 合并，也没有计算跨 subject 的总体 p 值。当前每位 subject 只纳入了 1 个兼容 session，因此本报告只能描述结果，不能作为总体人群结论。

## Session 结果

| session | 保留 trial | QC unit | q<0.05 unit | 正向 mean delta unit | unit mean delta 均值 (Hz) | unit mean delta 中位数 (Hz) |
|---|---:|---:|---:|---:|---:|---:|
{session_rows}

总计：{len(session_summary)} 个 session，{int(session_summary['n_trials_kept'].sum())} 个保留 trial，{len(all_units)} 个 QC unit。这里的总计只用于清点数据规模，不构成把所有 trial 或 unit 当作独立受试者的统计检验。

## Subject 并列结果

| subject | 已分析 session | 保留 trial | QC unit | q<0.05 unit | session-level unit mean delta (Hz) |
|---:|---:|---:|---:|---:|---:|
{subject_rows}

## 当前可作的描述

- 结果在不同 session 之间存在明显异质性：sub-11_ses-2 有 {int(session_summary['significant_units_q05'].max())} 个 session 内 FDR 显著 unit，而其余 3 个 session 均为 0 个。
- 4 个 session 的 unit-level 平均效应方向并不一致，因此不能写成“所有 session 在图片后都增强”或“所有 session 都不响应”。
- raster/PSTH 已作为时间对齐 QC 通过；它们帮助确认事件对齐没有系统性错误，但不替代预先定义的置换检验和 FDR 结果。

## 后续推断计划（未执行）

1. 不把 540 个 trial 合并后进行一次总体 t 检验，也不把 139 个 unit 当作 139 位独立受试者。
2. 若后续为每位 subject 建立了可比的额外 session 事件映射，先在 subject 内汇总 session-level 效应，再以 subject 为分析单位预先定义跨 subject 描述或推断。
3. 在样本量仍只有 4 位 subject 时，优先报告每位 subject 的效应和不确定性；任何总体 p 值都应明确标注探索性、统计功效有限。
4. 图片 ID、记忆负荷、正确率和脑区问题留到阶段 F，并单独预注册/记录分析单位、训练测试划分和多重比较范围。
"""
    report_path = RESULTS_DIR / "descriptive_summary.md"
    report_path.write_text(report, encoding="utf-8")
    return report_path


def main() -> None:
    session_rows = []
    unit_tables = []
    for metadata_path in sorted(RESULTS_DIR.glob("sub-*_ses-*/session_metadata.json")):
        session_dir = metadata_path.parent
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        statistics = pd.read_csv(
            session_dir / "unit_level_statistics.csv", index_col="unit_id"
        )
        session_rows.append(
            {
                "file_name": metadata["source_file"],
                "subject_id": metadata["subject_id"],
                "session_id": metadata["session_id"],
                "n_trials_total": metadata["n_trials_total"],
                "n_trials_kept": metadata["n_trials_kept"],
                "n_units_total": metadata["n_units_total"],
                "n_units_kept": metadata["n_units_kept"],
                "significant_units_q05": int(statistics["significant_q05"].sum()),
                "positive_mean_delta_units": int((statistics["mean_delta_hz"] > 0).sum()),
                "mean_of_unit_mean_delta_hz": float(statistics["mean_delta_hz"].mean()),
                "median_of_unit_mean_delta_hz": float(statistics["mean_delta_hz"].median()),
            }
        )
        unit_table = statistics.reset_index()
        unit_table.insert(0, "session_id", metadata["session_id"])
        unit_table.insert(0, "subject_id", metadata["subject_id"])
        unit_table.insert(0, "file_name", metadata["source_file"])
        unit_tables.append(unit_table)

    if not session_rows:
        raise FileNotFoundError("No primary-v1 session results were found.")

    session_summary = pd.DataFrame(session_rows).sort_values(["subject_id", "session_id"])
    session_summary.to_csv(RESULTS_DIR / "session_summary.csv", index=False)
    all_units = pd.concat(unit_tables, ignore_index=True)
    all_units.to_csv(RESULTS_DIR / "unit_statistics_all_sessions.csv", index=False)

    subject_summary = (
        session_summary.groupby("subject_id", as_index=False)
        .agg(
            sessions_analyzed=("session_id", "nunique"),
            trials_kept=("n_trials_kept", "sum"),
            units_kept=("n_units_kept", "sum"),
            significant_units_q05=("significant_units_q05", "sum"),
            mean_of_session_effects_hz=("mean_of_unit_mean_delta_hz", "mean"),
        )
        .sort_values("subject_id")
    )
    subject_summary.to_csv(RESULTS_DIR / "subject_level_descriptive_summary.csv", index=False)
    report_path = write_descriptive_report(session_summary, subject_summary, all_units)

    print(session_summary.to_string(index=False))
    print("\nSubject-level descriptive summary:")
    print(subject_summary.to_string(index=False))
    print(f"\nUnit rows summarized: {len(all_units)}")
    print(f"Descriptive report: {report_path}")


if __name__ == "__main__":
    main()
