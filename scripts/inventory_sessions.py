"""Create a read-only inventory of the selected NWB data root."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from pynwb import NWBHDF5IO

PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from data_paths import data_root, nwb_files  # noqa: E402
from sternberg_primary import REQUIRED_TRIAL_COLUMNS, file_identity, sha256  # noqa: E402


def main() -> None:
    output_dir = PROJECT_DIR / "results" / "primary-v2-all"
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []

    for path in nwb_files(PROJECT_DIR):
        with NWBHDF5IO(str(path), "r", load_namespaces=True) as io:
            nwbfile = io.read()
            trials = nwbfile.trials.to_dataframe()
            units = nwbfile.units.to_dataframe()
            electrodes = nwbfile.electrodes.to_dataframe()
            missing = [column for column in REQUIRED_TRIAL_COLUMNS if column not in trials.columns]
            has_units_spike_times = "spike_times" in units.columns
            has_units_electrodes = "electrodes" in units.columns
            has_electrodes_location = "location" in electrodes.columns
            compatible = (
                not missing
                and has_units_spike_times
                and has_units_electrodes
                and has_electrodes_location
            )
            rows.append(
                {
                    "file_name": path.name,
                    "relative_path": str(path.relative_to(PROJECT_DIR)),
                    "subject_id": file_identity(path)["subject_id"],
                    "session_id": file_identity(path)["session_id"],
                    "file_size_bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "nwb_identifier": nwbfile.identifier,
                    "session_start_time": str(nwbfile.session_start_time),
                    "n_trials": len(trials),
                    "n_units": len(units),
                    "n_electrodes": len(electrodes),
                    "has_timestamps_FixationCross": "timestamps_FixationCross" in trials.columns,
                    "has_timestamps_Encoding1": "timestamps_Encoding1" in trials.columns,
                    "has_timestamps_Encoding1_end": "timestamps_Encoding1_end" in trials.columns,
                    "has_units_spike_times": has_units_spike_times,
                    "has_units_electrodes": has_units_electrodes,
                    "has_electrodes_location": has_electrodes_location,
                    "missing_primary_columns": ";".join(missing),
                    "primary_schema_compatible": compatible,
                }
            )

    inventory = pd.DataFrame(rows).sort_values(["subject_id", "session_id", "file_name"])
    output_path = output_dir / "session_inventory.csv"
    inventory.to_csv(output_path, index=False)
    print(inventory.to_string(index=False))
    print(f"\nInventory saved: {output_path.resolve()}")


if __name__ == "__main__":
    main()
