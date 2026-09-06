"""Numerical-only primary analysis for one Sternberg NWB session.

This module deliberately has no plotting dependency. It preserves the frozen
single-session definitions used in read_data.ipynb.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from pynwb import NWBHDF5IO
from statsmodels.stats.multitest import multipletests


BASELINE_WINDOW = (-0.8, 0.0)
RESPONSE_WINDOW = (0.2, 1.0)
WINDOW_SECONDS = 0.8
MIN_ACTIVE_TRIALS = 10
PERMUTATIONS = 10_000
BOOTSTRAPS = 5_000
FDR_Q_THRESHOLD = 0.05
RANDOM_SEED = 20260901

REQUIRED_TRIAL_COLUMNS = [
    "start_time",
    "stop_time",
    "timestamps_FixationCross",
    "timestamps_Encoding1",
    "timestamps_Encoding1_end",
]

FILE_PATTERN = re.compile(
    r"sub-(?P<subject>[^_]+)_ses-(?P<session>[^_]+)_ecephys\+image\.nwb$"
)


class IncompatibleSessionError(ValueError):
    """The file does not expose the frozen primary-analysis event schema."""


def file_identity(path: Path) -> dict[str, str]:
    match = FILE_PATTERN.match(path.name)
    if match is None:
        return {"subject_id": "unknown", "session_id": "unknown"}
    return {
        "subject_id": match.group("subject"),
        "session_id": match.group("session"),
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parameters() -> dict[str, object]:
    return {
        "baseline_window_seconds": BASELINE_WINDOW,
        "response_window_seconds": RESPONSE_WINDOW,
        "minimum_active_trials": MIN_ACTIVE_TRIALS,
        "permutations": PERMUTATIONS,
        "bootstraps": BOOTSTRAPS,
        "fdr_q_threshold": FDR_Q_THRESHOLD,
        "random_seed": RANDOM_SEED,
        "analysis_scope": "Each compatible session is analyzed independently; trial rows are not pooled.",
    }


def build_trial_qc(trials: pd.DataFrame) -> pd.DataFrame:
    trial_qc = trials[REQUIRED_TRIAL_COLUMNS].copy().rename(
        columns={
            "start_time": "trial_start",
            "stop_time": "trial_stop",
            "timestamps_FixationCross": "fixation",
            "timestamps_Encoding1": "encoding_onset",
            "timestamps_Encoding1_end": "encoding_end",
        }
    )
    time_columns = [
        "trial_start",
        "trial_stop",
        "fixation",
        "encoding_onset",
        "encoding_end",
    ]
    trial_qc["finite_times"] = np.isfinite(trial_qc[time_columns]).all(axis=1)
    trial_qc["event_order"] = (
        (trial_qc["trial_start"] <= trial_qc["fixation"])
        & (trial_qc["fixation"] < trial_qc["encoding_onset"])
        & (trial_qc["encoding_onset"] < trial_qc["encoding_end"])
        & (trial_qc["encoding_end"] <= trial_qc["trial_stop"])
    )
    trial_qc["baseline_covered"] = (
        trial_qc["encoding_onset"] + BASELINE_WINDOW[0] >= trial_qc["fixation"]
    )
    trial_qc["response_covered"] = (
        trial_qc["encoding_onset"] + RESPONSE_WINDOW[1] <= trial_qc["trial_stop"]
    )
    checks = ["finite_times", "event_order", "baseline_covered", "response_covered"]
    trial_qc["keep"] = trial_qc[checks].all(axis=1)
    return trial_qc


def _single_index(value: object) -> float:
    values = np.asarray(value).reshape(-1)
    if values.size != 1:
        return np.nan
    try:
        return float(values[0])
    except (TypeError, ValueError):
        return np.nan


def build_unit_qc(
    units: pd.DataFrame, electrodes: pd.DataFrame, valid_trials: pd.DataFrame
) -> pd.DataFrame:
    columns = [
        name
        for name in [
            "spike_times",
            "electrodes",
            "clusterID_orig",
            "waveforms_mean_snr",
            "waveforms_peak_snr",
            "waveforms_isolation_distance",
        ]
        if name in units.columns
    ]
    unit_qc = units[columns].copy()
    spikes = [np.asarray(value) for value in unit_qc["spike_times"]]
    unit_qc["spike_count"] = [len(value) for value in spikes]
    unit_qc["finite_spikes"] = [np.isfinite(value).all() for value in spikes]
    unit_qc["increasing_spikes"] = [
        finite and np.all(np.diff(value) >= 0)
        for value, finite in zip(spikes, unit_qc["finite_spikes"])
    ]

    starts = valid_trials["trial_start"].to_numpy()
    stops = valid_trials["trial_stop"].to_numpy()
    unit_qc["active_trials"] = [
        int((np.searchsorted(value, stops) > np.searchsorted(value, starts)).sum())
        if increasing
        else 0
        for value, increasing in zip(spikes, unit_qc["increasing_spikes"])
    ]
    unit_qc["enough_activity"] = unit_qc["active_trials"] >= MIN_ACTIVE_TRIALS
    unit_qc["keep"] = unit_qc[
        ["finite_spikes", "increasing_spikes", "enough_activity"]
    ].all(axis=1)

    if "electrodes" in unit_qc.columns:
        unit_qc["electrode_index"] = unit_qc["electrodes"].map(_single_index)
        location_map = electrodes["location"].to_dict() if "location" in electrodes else {}
        unit_qc["region"] = unit_qc["electrode_index"].map(location_map)
    else:
        unit_qc["electrode_index"] = np.nan
        unit_qc["region"] = "unknown"
    return unit_qc


def build_unit_trial_features(
    valid_units: pd.DataFrame, valid_trials: pd.DataFrame
) -> pd.DataFrame:
    records: list[dict[str, int]] = []
    for unit_id, unit in valid_units.iterrows():
        spike_times = np.asarray(unit["spike_times"])
        for trial_id, onset in valid_trials["encoding_onset"].items():
            baseline_count = np.searchsorted(
                spike_times, onset + BASELINE_WINDOW[1]
            ) - np.searchsorted(spike_times, onset + BASELINE_WINDOW[0])
            response_count = np.searchsorted(
                spike_times, onset + RESPONSE_WINDOW[1]
            ) - np.searchsorted(spike_times, onset + RESPONSE_WINDOW[0])
            records.append(
                {
                    "unit_id": unit_id,
                    "trial_id": trial_id,
                    "baseline_count": int(baseline_count),
                    "response_count": int(response_count),
                }
            )
    features = pd.DataFrame(records)
    features["baseline_rate_hz"] = features["baseline_count"] / WINDOW_SECONDS
    features["response_rate_hz"] = features["response_count"] / WINDOW_SECONDS
    features["rate_difference_hz"] = (
        features["response_rate_hz"] - features["baseline_rate_hz"]
    )
    return features


def build_final_count_qc(
    valid_units: pd.DataFrame, features: pd.DataFrame
) -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []
    for unit_id, unit in valid_units.iterrows():
        spike_times = np.asarray(unit["spike_times"])
        isi = np.diff(spike_times)
        unit_features = features.loc[features["unit_id"] == unit_id]
        rows.append(
            {
                "unit_id": unit_id,
                "min_isi_ms": float(isi.min() * 1000) if isi.size else np.nan,
                "short_isi_count": int((isi < 0.002).sum()),
                "short_isi_fraction": float((isi < 0.002).mean()) if isi.size else np.nan,
                "baseline_zero_fraction": float(
                    (unit_features["baseline_count"] == 0).mean()
                ),
                "response_zero_fraction": float(
                    (unit_features["response_count"] == 0).mean()
                ),
                "max_baseline_count": int(unit_features["baseline_count"].max()),
                "max_response_count": int(unit_features["response_count"].max()),
            }
        )
    return pd.DataFrame(rows).set_index("unit_id")


def compute_unit_statistics(features: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)
    unit_ids = sorted(features["unit_id"].unique())
    differences_by_unit = {
        unit_id: features.loc[
            features["unit_id"] == unit_id, "rate_difference_hz"
        ].to_numpy()
        for unit_id in unit_ids
    }

    # Keep the original notebook's random-number order: all permutation tests
    # run first, then all bootstrap tests. This makes the baseline reproducible.
    permutation_rows: dict[object, dict[str, float | int]] = {}
    for unit_id in unit_ids:
        differences = differences_by_unit[unit_id]
        n_trials = differences.size
        observed_mean = float(differences.mean())
        signs = rng.choice([-1.0, 1.0], size=(PERMUTATIONS, n_trials))
        null_means = (signs * differences).mean(axis=1)
        permutation_p = float(
            ((null_means >= observed_mean).sum() + 1) / (PERMUTATIONS + 1)
        )
        permutation_rows[unit_id] = {
            "n_trials": n_trials,
            "mean_delta_hz": observed_mean,
            "permutation_p": permutation_p,
        }

    rows: list[dict[str, float | int]] = []
    for unit_id in unit_ids:
        differences = differences_by_unit[unit_id]
        n_trials = differences.size
        observed_mean = float(differences.mean())
        draws = rng.choice(n_trials, size=(BOOTSTRAPS, n_trials), replace=True)
        bootstrap_means = differences[draws].mean(axis=1)
        ci_lower, ci_upper = np.percentile(bootstrap_means, [2.5, 97.5])
        trials_above = int((differences > 0).sum())
        trials_tie = int((differences == 0).sum())
        rows.append({
            "unit_id": unit_id,
            **permutation_rows[unit_id],
            "median_delta_hz": float(np.median(differences)),
            "ci95_lower_hz": float(ci_lower),
            "ci95_upper_hz": float(ci_upper),
            "trials_above": trials_above,
            "trials_tie": trials_tie,
            "common_language_prob": float(
                (trials_above + 0.5 * trials_tie) / n_trials
            ),
        })

    result = pd.DataFrame(rows).set_index("unit_id")
    reject, qvalues, _, _ = multipletests(
        result["permutation_p"], alpha=FDR_Q_THRESHOLD, method="fdr_bh"
    )
    result["fdr_q"] = qvalues
    result["significant_q05"] = reject
    return result


def analyze_session(path: Path) -> dict[str, object]:
    path = path.resolve()
    identity = file_identity(path)
    with NWBHDF5IO(str(path), "r", load_namespaces=True) as io:
        nwbfile = io.read()
        trials = nwbfile.trials.to_dataframe()
        units = nwbfile.units.to_dataframe()
        electrodes = nwbfile.electrodes.to_dataframe()
        missing = [column for column in REQUIRED_TRIAL_COLUMNS if column not in trials.columns]
        if missing:
            raise IncompatibleSessionError(
                "Missing required trial columns: " + ", ".join(missing)
            )
        if "spike_times" not in units.columns or "location" not in electrodes.columns:
            raise IncompatibleSessionError("Missing spike_times or electrode location")

        trial_qc = build_trial_qc(trials)
        valid_trials = trial_qc.loc[trial_qc["keep"]].copy()
        unit_qc = build_unit_qc(units, electrodes, valid_trials)
        valid_units = unit_qc.loc[unit_qc["keep"]].copy()
        if valid_trials.empty or valid_units.empty:
            raise ValueError("No trial or unit passed the frozen QC rules")

        features = build_unit_trial_features(valid_units, valid_trials)
        final_count_qc = build_final_count_qc(valid_units, features)
        unit_statistics = compute_unit_statistics(features)

        metadata = {
            "source_file": path.name,
            "sha256": sha256(path),
            "subject_id": identity["subject_id"],
            "session_id": identity["session_id"],
            "nwb_identifier": nwbfile.identifier,
            "session_start_time": str(nwbfile.session_start_time),
            "n_trials_total": len(trials),
            "n_trials_kept": len(valid_trials),
            "n_units_total": len(units),
            "n_units_kept": len(valid_units),
            "n_electrodes_total": len(electrodes),
            "trial_columns": trials.columns.to_list(),
            "unit_columns": units.columns.to_list(),
            "electrode_columns": electrodes.columns.to_list(),
        }
    return {
        "metadata": metadata,
        "trial_qc": trial_qc,
        "unit_qc": unit_qc,
        "unit_trial_features": features,
        "final_count_qc": final_count_qc,
        "unit_level_statistics": unit_statistics,
    }


def json_default(value: object) -> str:
    return str(value)


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, default=json_default),
        encoding="utf-8",
    )
