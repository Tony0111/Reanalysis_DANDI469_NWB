"""Run the numerical primary analysis for one compatible NWB session."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from sternberg_primary import (  # noqa: E402
    IncompatibleSessionError,
    analyze_session,
    parameters,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input if args.input.is_absolute() else PROJECT_DIR / args.input
    output_dir = args.output if args.output.is_absolute() else PROJECT_DIR / args.output
    input_path = input_path.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = analyze_session(input_path)
    except IncompatibleSessionError as error:
        print(f"INCOMPATIBLE: {error}")
        raise SystemExit(2)

    result["trial_qc"].to_csv(output_dir / "trial_qc.csv", index_label="trial_id")
    result["unit_qc"].drop(columns="spike_times").to_csv(
        output_dir / "unit_qc.csv", index_label="unit_id"
    )
    result["unit_trial_features"].to_csv(
        output_dir / "unit_trial_features.csv", index=False
    )
    result["final_count_qc"].to_csv(
        output_dir / "final_count_qc.csv", index_label="unit_id"
    )
    result["unit_level_statistics"].to_csv(
        output_dir / "unit_level_statistics.csv", index_label="unit_id"
    )
    write_json(output_dir / "session_metadata.json", result["metadata"])
    write_json(output_dir / "analysis_parameters.json", parameters())

    statistics = result["unit_level_statistics"]
    metadata = result["metadata"]
    print(
        f"included: {metadata['source_file']} | "
        f"trials {metadata['n_trials_kept']}/{metadata['n_trials_total']} | "
        f"units {metadata['n_units_kept']}/{metadata['n_units_total']} | "
        f"significant q<0.05: {int(statistics['significant_q05'].sum())}"
    )
    print(f"results: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
