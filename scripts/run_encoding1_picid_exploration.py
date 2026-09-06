"""Run the held-out exploratory test for first-encoding picture identity.

This is intentionally separate from primary-v1.  It asks an exploratory
question: after choosing each unit's best picture on training trials, does
that picture still have a larger response-minus-baseline rate on unseen test
trials than the other four pictures?
"""

from __future__ import annotations

import hashlib
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from pynwb import NWBHDF5IO
from statsmodels.stats.multitest import multipletests


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "results" / "exploratory-v1" / "encoding1_picid_train_test"
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from data_paths import find_session  # noqa: E402
from sternberg_primary import (  # noqa: E402
    REQUIRED_TRIAL_COLUMNS,
    IncompatibleSessionError,
    build_trial_qc,
    build_unit_qc,
    build_unit_trial_features,
    file_identity,
    sha256,
    write_json,
)


PIC_ID_COLUMN = "loadsEnc1_PicIDs"
SPLIT_SEED = 20260906
PERMUTATION_SEED = 20260907
PERMUTATIONS = 10_000
FDR_Q_THRESHOLD = 0.05
SESSIONS = (
    "sub-1_ses-2_ecephys+image.nwb",
    "sub-11_ses-2_ecephys+image.nwb",
    "sub-20_ses-2_ecephys+image.nwb",
    "sub-21_ses-2_ecephys+image.nwb",
)


def pic_id_label(value: object) -> str:
    """Convert a scalar NWB picture ID into a stable text label."""
    values = np.asarray(value).reshape(-1)
    if values.size != 1:
        raise ValueError(f"Expected one picture ID per trial, found {values.tolist()}")
    return str(values[0])


def session_seed(master_seed: int, file_name: str) -> int:
    """Derive a stable per-session seed without relying on Python's hash()."""
    digest = hashlib.sha256(file_name.encode("utf-8")).digest()
    return master_seed + int.from_bytes(digest[:4], byteorder="little")


def read_exploration_inputs(
    input_path: Path,
) -> tuple[pd.DataFrame, pd.Series, dict[str, object]]:
    """Reuse frozen QC and rate features without re-running primary statistics."""
    with NWBHDF5IO(str(input_path), "r", load_namespaces=True) as io:
        nwbfile = io.read()
        trials = nwbfile.trials.to_dataframe()
        units = nwbfile.units.to_dataframe()
        electrodes = nwbfile.electrodes.to_dataframe()

        missing = [column for column in REQUIRED_TRIAL_COLUMNS if column not in trials.columns]
        if missing:
            raise IncompatibleSessionError("Missing required trial columns: " + ", ".join(missing))
        if PIC_ID_COLUMN not in trials.columns:
            raise IncompatibleSessionError(f"Missing required picture-ID column: {PIC_ID_COLUMN}")
        if "spike_times" not in units.columns or "location" not in electrodes.columns:
            raise IncompatibleSessionError("Missing spike_times or electrode location")

        trial_qc = build_trial_qc(trials)
        valid_trials = trial_qc.loc[trial_qc["keep"]].copy()
        unit_qc = build_unit_qc(units, electrodes, valid_trials)
        valid_units = unit_qc.loc[unit_qc["keep"]].copy()
        if valid_trials.empty or valid_units.empty:
            raise ValueError("No trial or unit passed the frozen QC rules")

        features = build_unit_trial_features(valid_units, valid_trials)
        picture_ids = trials.loc[valid_trials.index, PIC_ID_COLUMN].map(pic_id_label).rename("pic_id")
        metadata = {
            "source_file": input_path.name,
            "sha256": sha256(input_path),
            **file_identity(input_path),
            "nwb_identifier": nwbfile.identifier,
            "session_start_time": str(nwbfile.session_start_time),
            "n_trials_total": len(trials),
            "n_trials_kept": len(valid_trials),
            "n_units_total": len(units),
            "n_units_kept": len(valid_units),
        }

    return features, picture_ids, metadata


def make_stratified_split(pic_ids: pd.Series, file_name: str) -> pd.DataFrame:
    """Put about half of each picture ID's trials in train and the rest in test."""
    rng = np.random.default_rng(session_seed(SPLIT_SEED, file_name))
    rows: list[dict[str, object]] = []
    for pic_id in sorted(pic_ids.unique(), key=lambda value: (float(value), value)):
        trial_ids = pic_ids.index[pic_ids == pic_id].to_numpy()
        shuffled_ids = rng.permutation(trial_ids)
        n_train = len(shuffled_ids) // 2
        for trial_id in shuffled_ids[:n_train]:
            rows.append({"trial_id": trial_id, "pic_id": pic_id, "split": "train"})
        for trial_id in shuffled_ids[n_train:]:
            rows.append({"trial_id": trial_id, "pic_id": pic_id, "split": "test"})
    return pd.DataFrame(rows).sort_values("trial_id").reset_index(drop=True)


def one_sided_permutation_p(
    selected_values: np.ndarray, other_values: np.ndarray, rng: np.random.Generator
) -> tuple[float, float]:
    """Test whether selected-image values are larger than the other-image values."""
    observed_difference = float(selected_values.mean() - other_values.mean())
    values = np.concatenate([selected_values, other_values])
    n_selected = len(selected_values)
    null_differences = np.empty(PERMUTATIONS, dtype=float)
    for iteration in range(PERMUTATIONS):
        shuffled_values = rng.permutation(values)
        null_differences[iteration] = (
            shuffled_values[:n_selected].mean() - shuffled_values[n_selected:].mean()
        )
    p_value = float(((null_differences >= observed_difference).sum() + 1) / (PERMUTATIONS + 1))
    return observed_difference, p_value


def analyze_picture_identity_session(input_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    """Select a candidate picture on train trials and test it on held-out trials."""
    features, picture_ids, metadata = read_exploration_inputs(input_path)
    split = make_stratified_split(picture_ids, input_path.name)

    features = features.merge(
        split, on="trial_id", how="inner", validate="many_to_one"
    )
    expected_rows = len(picture_ids) * metadata["n_units_kept"]
    if len(features) != expected_rows:
        raise ValueError("The picture-ID split did not cover every QC-passing unit x trial row")

    rng = np.random.default_rng(session_seed(PERMUTATION_SEED, input_path.name))
    rows: list[dict[str, object]] = []
    for unit_id, unit_features in features.groupby("unit_id", sort=True):
        train = unit_features.loc[unit_features["split"] == "train"]
        test = unit_features.loc[unit_features["split"] == "test"]

        # The candidate is chosen without seeing any test-trial firing rates.
        train_means = train.groupby("pic_id")["rate_difference_hz"].mean()
        selected_pic_id = train_means.sort_values(ascending=False, kind="stable").index[0]
        selected_test = test.loc[test["pic_id"] == selected_pic_id, "rate_difference_hz"].to_numpy()
        other_test = test.loc[test["pic_id"] != selected_pic_id, "rate_difference_hz"].to_numpy()
        effect_hz, p_value = one_sided_permutation_p(selected_test, other_test, rng)

        rows.append(
            {
                "unit_id": unit_id,
                "selected_pic_id": selected_pic_id,
                "n_train_selected": int((train["pic_id"] == selected_pic_id).sum()),
                "train_selected_mean_delta_hz": float(train_means.loc[selected_pic_id]),
                "n_test_selected": len(selected_test),
                "n_test_other": len(other_test),
                "test_selected_mean_delta_hz": float(selected_test.mean()),
                "test_other_mean_delta_hz": float(other_test.mean()),
                "test_selected_minus_other_hz": effect_hz,
                "permutation_p_one_sided": p_value,
            }
        )

    statistics = pd.DataFrame(rows).set_index("unit_id")
    reject, q_values, _, _ = multipletests(
        statistics["permutation_p_one_sided"],
        alpha=FDR_Q_THRESHOLD,
        method="fdr_bh",
    )
    statistics["fdr_q"] = q_values
    statistics["significant_q05"] = reject
    return split, statistics, metadata


def write_readme() -> None:
    """Document the frozen exploratory design beside its outputs."""
    text = """# Encoding1 图片 ID 探索性分析（训练/测试分离）

这不是 `primary-v1` 的主检验，而是独立的探索性分析。

## 问题

对每个 unit：第一张编码图片中，哪一张图片的 `response - baseline` 平均放电率最高？这张图片在未参与选择的 trial 中，是否仍高于其他四张图片？

## 固定流程

1. 每个 session 的每个图片 ID 都按 `SPLIT_SEED=20260906` 随机、分层地切为近似 50% 训练和 50% 测试 trial。
2. 对每个 unit，只用训练 trial 计算每张图片的平均 `rate_difference_hz`，并选取最大者为 `selected_pic_id`。
3. 只用测试 trial 比较 `selected_pic_id` 与其他四张图片的平均 `rate_difference_hz`。正值表示候选图片较强。
4. 用 10,000 次单尾置换检验该测试集差异是否大于随机标签下的差异；随后只在同一 session 的 unit 之间做 BH-FDR（`q < 0.05`）。

训练集和测试集分开，因此不会发生“用同一批 trial 先挑最强图片、又用同一批 trial 宣称它最强”的数据泄漏。但这仍是探索性结果：需要在新的、独立的数据中重复，不能反过来改变 `primary-v1` 的窗口、QC 或主结论。
"""
    (OUTPUT_DIR / "README.md").write_text(text, encoding="utf-8")


def write_summary_report(session_summary: pd.DataFrame, all_units: pd.DataFrame) -> Path:
    """Write a human-readable report from the already computed CSV tables."""
    session_rows = "\n".join(
        "| {file_name} | {trials} | {units} | {significant} | {effect:.3f} |".format(
            file_name=row.file_name,
            trials=int(row.n_trials_kept),
            units=int(row.n_units_kept),
            significant=int(row.significant_units_q05),
            effect=float(row.mean_test_selected_minus_other_hz),
        )
        for row in session_summary.itertuples(index=False)
    )
    significant = all_units.loc[all_units["significant_q05"]].copy()
    if significant.empty:
        unit_details = "- 没有 unit 在独立测试集通过同一 session 内的 BH-FDR。"
    else:
        unit_details = "\n".join(
            "- `{file_name}`，unit {unit_id}：训练集选择图片 ID {pic_id}；"
            "测试集候选图片均值 {selected:.3f} Hz，其他图片均值 {other:.3f} Hz，"
            "差值 {effect:.3f} Hz，单尾置换 p={p:.6f}，session 内 FDR q={q:.6f}。".format(
                file_name=row.file_name,
                unit_id=int(row.unit_id),
                pic_id=row.selected_pic_id,
                selected=float(row.test_selected_mean_delta_hz),
                other=float(row.test_other_mean_delta_hz),
                effect=float(row.test_selected_minus_other_hz),
                p=float(row.permutation_p_one_sided),
                q=float(row.fdr_q),
            )
            for row in significant.itertuples(index=False)
        )

    report = f"""# Encoding1 图片 ID 探索性结果

生成时间：{datetime.now().astimezone().isoformat(timespec="seconds")}

## Session 汇总

| session | 保留 trial | QC unit | 测试集 q<0.05 unit | unit 测试集差值均值 (Hz) |
|---|---:|---:|---:|---:|
{session_rows}

`unit 测试集差值`是训练集选择的候选图片在测试集的平均 `response - baseline` 放电率，减去测试集中其余四张图片的对应平均值。它只用于描述该 session 的 unit 结果，不能作为跨 subject 的总体效应。

## 通过 Session 内 FDR 的 Unit

{unit_details}

## 解读边界

- 候选图片仅由训练 trial 选出，统计检验只使用独立测试 trial，因此本结果避免了同一 trial 同时用于选择和验证的泄漏。
- FDR 只在各自 session 的 unit 内校正；这里的显著 unit 不能合并为跨 subject 的总体 p 值。
- 这是探索性结果，不修改 `primary-v1` 的时间窗、QC、主检验或主结论。应在新的独立数据中重复后，才可支持更强的图片选择性结论。
"""
    report_path = OUTPUT_DIR / "exploratory_summary.md"
    report_path.write_text(report, encoding="utf-8")
    return report_path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_readme()
    summary_rows = []
    all_unit_tables = []

    for file_name in SESSIONS:
        input_path = find_session(file_name, PROJECT_DIR)
        session_dir = OUTPUT_DIR / input_path.stem.replace("_ecephys+image", "")
        session_dir.mkdir(parents=True, exist_ok=True)
        split, statistics, metadata = analyze_picture_identity_session(input_path)
        split.to_csv(session_dir / "trial_split.csv", index=False)
        statistics.to_csv(session_dir / "unit_picture_identity_statistics.csv", index_label="unit_id")
        write_json(
            session_dir / "analysis_parameters.json",
            {
                "analysis_type": "exploratory held-out Encoding1 picture-ID test",
                "source_picture_id_column": PIC_ID_COLUMN,
                "split_seed": SPLIT_SEED,
                "permutation_seed": PERMUTATION_SEED,
                "permutations": PERMUTATIONS,
                "fdr_q_threshold": FDR_Q_THRESHOLD,
                "candidate_selection": "largest train-trial mean response-minus-baseline rate",
                "held_out_test": "selected picture versus all other pictures, one-sided",
                "warning": "Exploratory result; it does not modify primary-v1.",
            },
        )
        write_json(session_dir / "session_metadata.json", metadata)

        summary_rows.append(
            {
                "file_name": file_name,
                "subject_id": metadata["subject_id"],
                "session_id": metadata["session_id"],
                "n_trials_kept": metadata["n_trials_kept"],
                "n_units_kept": metadata["n_units_kept"],
                "significant_units_q05": int(statistics["significant_q05"].sum()),
                "mean_test_selected_minus_other_hz": float(
                    statistics["test_selected_minus_other_hz"].mean()
                ),
            }
        )
        unit_table = statistics.reset_index()
        unit_table.insert(0, "session_id", metadata["session_id"])
        unit_table.insert(0, "subject_id", metadata["subject_id"])
        unit_table.insert(0, "file_name", file_name)
        all_unit_tables.append(unit_table)
        print(
            f"included: {file_name} | trials {metadata['n_trials_kept']} | "
            f"units {metadata['n_units_kept']} | "
            f"held-out q<0.05: {int(statistics['significant_q05'].sum())}"
        )

    session_summary = pd.DataFrame(summary_rows).sort_values(["subject_id", "session_id"])
    session_summary.to_csv(OUTPUT_DIR / "session_summary.csv", index=False)
    all_units = pd.concat(all_unit_tables, ignore_index=True)
    all_units.to_csv(
        OUTPUT_DIR / "unit_picture_identity_statistics_all_sessions.csv", index=False
    )
    report_path = write_summary_report(session_summary, all_units)
    print("\nExploratory session summary:")
    print(session_summary.to_string(index=False))
    print(f"Exploratory report: {report_path}")
    print(f"\nresults: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
