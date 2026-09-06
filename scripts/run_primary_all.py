"""Run the numerical primary analysis sequentially for all inventoried sessions."""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import pandas as pd

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
    parser.add_argument(
        "--inventory",
        type=Path,
        default=PROJECT_DIR / "results" / "primary-v2-all" / "session_inventory.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_DIR / "results" / "primary-v2-all",
    )
    return parser.parse_args()


def timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def session_key(row: pd.Series) -> str:
    return f"sub-{row['subject_id']}_ses-{row['session_id']}"


def save_result(output_dir: Path, result: dict[str, object]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
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


def write_run_log(output_dir: Path, records: list[dict[str, object]]) -> None:
    columns = [
        "session_key",
        "file_name",
        "relative_path",
        "subject_id",
        "session_id",
        "status",
        "reason_code",
        "message",
        "started_at",
        "finished_at",
        "duration_seconds",
        "n_trials_total",
        "n_trials_kept",
        "n_units_total",
        "n_units_kept",
        "significant_units_q05",
    ]
    pd.DataFrame(records, columns=columns).to_csv(
        output_dir / "session_run_log.csv", index=False
    )


def main() -> None:
    args = parse_args()
    inventory_path = (
        args.inventory if args.inventory.is_absolute() else PROJECT_DIR / args.inventory
    ).resolve()
    output_dir = (
        args.output if args.output.is_absolute() else PROJECT_DIR / args.output
    ).resolve()
    if not inventory_path.exists():
        raise FileNotFoundError(f"Inventory not found: {inventory_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    inventory = pd.read_csv(inventory_path).sort_values(
        ["subject_id", "session_id", "file_name"]
    )
    records: list[dict[str, object]] = []

    for _, row in inventory.iterrows():
        key = session_key(row)
        started = time.monotonic()
        started_at = timestamp()
        record: dict[str, object] = {
            "session_key": key,
            "file_name": row["file_name"],
            "relative_path": row["relative_path"],
            "subject_id": row["subject_id"],
            "session_id": row["session_id"],
            "status": "",
            "reason_code": "",
            "message": "",
            "started_at": started_at,
            "finished_at": "",
            "duration_seconds": 0.0,
            "n_trials_total": "",
            "n_trials_kept": "",
            "n_units_total": "",
            "n_units_kept": "",
            "significant_units_q05": "",
        }
        input_path = (PROJECT_DIR / Path(str(row["relative_path"]))).resolve()

        if str(row["primary_schema_compatible"]).lower() != "true":
            missing = str(row.get("missing_primary_columns", ""))
            record["status"] = "excluded_incompatible_schema"
            record["reason_code"] = "missing_primary_event_schema"
            record["message"] = (
                "Excluded before numerical analysis; missing required fields: "
                + (missing or "unknown")
            )
            failure_dir = output_dir / "session_failures" / key
            failure_dir.mkdir(parents=True, exist_ok=True)
            write_json(failure_dir / "failure.json", record)
            print(f"EXCLUDED: {key} | {record['message']}")
        else:
            try:
                if not input_path.exists():
                    raise FileNotFoundError(f"Input not found: {input_path}")
                result = analyze_session(input_path)
                metadata = result["metadata"]
                statistics = result["unit_level_statistics"]
                save_result(output_dir / key, result)
                record["status"] = "completed"
                record["reason_code"] = ""
                record["message"] = "Numerical analysis completed"
                record["n_trials_total"] = metadata["n_trials_total"]
                record["n_trials_kept"] = metadata["n_trials_kept"]
                record["n_units_total"] = metadata["n_units_total"]
                record["n_units_kept"] = metadata["n_units_kept"]
                record["significant_units_q05"] = int(
                    statistics["significant_q05"].sum()
                )
                print(
                    f"COMPLETED: {key} | trials "
                    f"{metadata['n_trials_kept']}/{metadata['n_trials_total']} | "
                    f"units {metadata['n_units_kept']}/{metadata['n_units_total']} | "
                    f"significant q<0.05: {record['significant_units_q05']}"
                )
            except IncompatibleSessionError as error:
                record["status"] = "failed_incompatible_schema"
                record["reason_code"] = "analyze_session_schema_check"
                record["message"] = str(error)
                print(f"FAILED: {key} | {record['message']}")
            except Exception as error:  # keep the batch auditable and continue
                record["status"] = "failed"
                record["reason_code"] = type(error).__name__
                record["message"] = str(error)
                failure_dir = output_dir / "session_failures" / key
                failure_dir.mkdir(parents=True, exist_ok=True)
                failure_record = {
                    **record,
                    "traceback": traceback.format_exc(),
                }
                write_json(failure_dir / "failure.json", failure_record)
                print(f"FAILED: {key} | {type(error).__name__}: {error}")

        record["finished_at"] = timestamp()
        record["duration_seconds"] = round(time.monotonic() - started, 3)
        records.append(record)
        write_run_log(output_dir, records)

    failures = pd.DataFrame(records)
    failures = failures[failures["status"] != "completed"]
    failures.to_csv(output_dir / "session_failures.csv", index=False)
    write_json(
        output_dir / "batch_manifest.json",
        {
            "inventory": str(inventory_path),
            "output": str(output_dir),
            "analysis_parameters": parameters(),
            "n_inventory_rows": len(inventory),
            "n_completed": int((pd.DataFrame(records)["status"] == "completed").sum()),
            "n_excluded_or_failed": len(failures),
            "completed_without_trial_pooling": True,
        },
    )
    print(
        f"\nBatch finished: {len(records)} sessions, "
        f"{len(records) - len(failures)} completed, {len(failures)} excluded/failed."
    )
    print(f"Run log: {output_dir / 'session_run_log.csv'}")
    print(f"Failure/exclusion log: {output_dir / 'session_failures.csv'}")


if __name__ == "__main__":
    main()
