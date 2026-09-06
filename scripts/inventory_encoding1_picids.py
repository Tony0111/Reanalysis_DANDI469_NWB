"""Count first-encoding picture IDs before any exploratory picture analysis."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from pynwb import NWBHDF5IO


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from data_paths import find_session  # noqa: E402


OUTPUT_DIR = PROJECT_DIR / "results" / "primary-v1" / "exploratory_precheck"
PIC_ID_COLUMN = "loadsEnc1_PicIDs"

SESSIONS = (
    "sub-1_ses-2_ecephys+image.nwb",
    "sub-11_ses-2_ecephys+image.nwb",
    "sub-20_ses-2_ecephys+image.nwb",
    "sub-21_ses-2_ecephys+image.nwb",
)


def pic_id_label(value: object) -> str:
    """Return a stable label for scalar or array-like NWB table values."""
    values = np.asarray(value).reshape(-1)
    if values.size == 0:
        return "<empty>"
    return "|".join(map(str, values.tolist()))


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    count_tables = []
    summary_rows = []

    for file_name in SESSIONS:
        input_path = find_session(file_name, PROJECT_DIR)
        with NWBHDF5IO(str(input_path), "r", load_namespaces=True) as io:
            nwbfile = io.read()
            trials = nwbfile.trials.to_dataframe()
            metadata = {
                "file_name": file_name,
                "subject_id": str(nwbfile.subject.subject_id),
                "session_id": str(nwbfile.session_id),
            }

        if PIC_ID_COLUMN not in trials.columns:
            raise KeyError(f"{file_name} is missing {PIC_ID_COLUMN}")

        labels = trials[PIC_ID_COLUMN].map(pic_id_label)
        counts = labels.value_counts().sort_index()
        count_table = counts.rename_axis("pic_id").reset_index(name="n_trials")
        for key, value in reversed(list(metadata.items())):
            count_table.insert(0, key, value)
        count_tables.append(count_table)

        repeat_counts = counts.to_numpy()
        summary_rows.append(
            {
                **metadata,
                "n_trials": int(len(trials)),
                "n_unique_pic_ids": int(len(counts)),
                "min_trials_per_pic_id": int(repeat_counts.min()),
                "median_trials_per_pic_id": float(np.median(repeat_counts)),
                "max_trials_per_pic_id": int(repeat_counts.max()),
                "pic_ids_seen_once": int((repeat_counts == 1).sum()),
                "pic_ids_seen_multiple_times": int((repeat_counts >= 2).sum()),
            }
        )

    counts_output = pd.concat(count_tables, ignore_index=True)
    summary_output = pd.DataFrame(summary_rows).sort_values(["subject_id", "session_id"])
    counts_path = OUTPUT_DIR / "encoding1_picid_counts.csv"
    summary_path = OUTPUT_DIR / "encoding1_picid_summary.csv"
    counts_output.to_csv(counts_path, index=False)
    summary_output.to_csv(summary_path, index=False)

    manifest = {
        "purpose": "Exploratory precheck only; no picture-selectivity test was run.",
        "source_field": PIC_ID_COLUMN,
        "sessions": list(SESSIONS),
        "counts_file": counts_path.name,
        "summary_file": summary_path.name,
    }
    (OUTPUT_DIR / "encoding1_picid_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(summary_output.to_string(index=False))
    print(f"\nPicture-ID counts: {counts_path}")
    print(f"Picture-ID summary: {summary_path}")


if __name__ == "__main__":
    main()
