"""Create session- and subject-level descriptive summaries for primary-v2-all."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_DIR / "results" / "primary-v2-all"


def write_descriptive_report(
    session_summary: pd.DataFrame,
    subject_summary: pd.DataFrame,
    run_log: pd.DataFrame,
) -> Path:
    session_rows = "\n".join(
        "| {file_name} | {trials} | {units} | {significant} | "
        "{positive} | {mean_delta:.3f} | {median_delta:.3f} |".format(
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
            subject=row.subject_id,
            sessions=int(row.sessions_analyzed),
            trials=int(row.trials_kept),
            units=int(row.units_kept),
            significant=int(row.significant_units_q05),
            mean_effect=float(row.mean_of_session_effects_hz),
        )
        for row in subject_summary.itertuples(index=False)
    )
    excluded = run_log[run_log["status"] != "completed"]
    report = f"""# Primary-v2-all 描述性汇总

生成时间：{datetime.now().astimezone().isoformat(timespec="seconds")}

本报告汇总各个 session 的独立分析结果。不同 session 的 trial 没有合并，
也没有把 unit 或 trial 当作独立受试者进行总体推断检验。

## 分析范围

- Inventory 文件记录数：{len(run_log)}
- 成功完成的兼容 session：{int((run_log['status'] == 'completed').sum())}
- 排除或失败的 session：{len(excluded)}
- 完成 session 的保留 trial 总数（仅作数据量描述）：{int(session_summary['n_trials_kept'].sum())}
- 完成 session 的 QC unit 总数（仅作数据量描述）：{int(session_summary['n_units_kept'].sum())}

当前纳入的是具有固定 Encoding1 事件定义的 21 个 `ses-2` session。20 个
`ses-1` session 因缺少 `timestamps_FixationCross`、`timestamps_Encoding1` 和
`timestamps_Encoding1_end`，没有套用本 primary 分析。

## Session 结果

| session | 保留 trial | QC unit | q<0.05 unit | 正向平均差值 unit | unit 平均差值均值 (Hz) | unit 平均差值中位数 (Hz) |
|---|---:|---:|---:|---:|---:|---:|
{session_rows}

## 受试者并列结果

| 受试者 | 分析 session 数 | 保留 trial | QC unit | q<0.05 unit | session 平均效应 (Hz) |
|---:|---:|---:|---:|---:|---:|
{subject_rows}

## 排除与失败记录

完整审计记录见 `session_run_log.csv` 和 `session_failures.csv`。这些 session
不是因为文件读取失败而排除，而是因为事件字段结构与预先固定的 Encoding1
对齐定义不一致。它们保留在 inventory 和排除日志中，没有被静默跳过。
"""
    report_path = RESULTS_DIR / "descriptive_summary.md"
    report_path.write_text(report, encoding="utf-8")
    return report_path


def main() -> None:
    run_log_path = RESULTS_DIR / "session_run_log.csv"
    if not run_log_path.exists():
        raise FileNotFoundError(f"Run log not found: {run_log_path}")
    run_log = pd.read_csv(run_log_path)
    completed = run_log[run_log["status"] == "completed"]
    if completed.empty:
        raise RuntimeError("No completed primary-v2-all sessions were found.")

    session_rows: list[dict[str, object]] = []
    unit_tables: list[pd.DataFrame] = []
    for row in completed.itertuples(index=False):
        session_dir = RESULTS_DIR / row.session_key
        metadata = json.loads(
            (session_dir / "session_metadata.json").read_text(encoding="utf-8")
        )
        statistics = pd.read_csv(
            session_dir / "unit_level_statistics.csv", index_col="unit_id"
        )
        session_rows.append(
            {
                "session_key": row.session_key,
                "file_name": metadata["source_file"],
                "subject_id": metadata["subject_id"],
                "session_id": metadata["session_id"],
                "n_trials_total": metadata["n_trials_total"],
                "n_trials_kept": metadata["n_trials_kept"],
                "n_units_total": metadata["n_units_total"],
                "n_units_kept": metadata["n_units_kept"],
                "significant_units_q05": int(statistics["significant_q05"].sum()),
                "positive_mean_delta_units": int(
                    (statistics["mean_delta_hz"] > 0).sum()
                ),
                "mean_of_unit_mean_delta_hz": float(
                    statistics["mean_delta_hz"].mean()
                ),
                "median_of_unit_mean_delta_hz": float(
                    statistics["mean_delta_hz"].median()
                ),
            }
        )
        unit_table = statistics.reset_index()
        unit_table.insert(0, "session_key", row.session_key)
        unit_table.insert(1, "session_id", metadata["session_id"])
        unit_table.insert(1, "subject_id", metadata["subject_id"])
        unit_table.insert(1, "file_name", metadata["source_file"])
        unit_tables.append(unit_table)

    session_summary = pd.DataFrame(session_rows).sort_values(
        ["subject_id", "session_id"]
    )
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
    subject_summary.to_csv(
        RESULTS_DIR / "subject_level_descriptive_summary.csv", index=False
    )
    report_path = write_descriptive_report(session_summary, subject_summary, run_log)

    print(session_summary.to_string(index=False))
    print("\nSubject-level descriptive summary:")
    print(subject_summary.to_string(index=False))
    print(f"\nUnit rows summarized: {len(all_units)}")
    print(f"Descriptive report: {report_path}")


if __name__ == "__main__":
    main()
