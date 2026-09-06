"""Generate representative raster/PSTH figures for all compatible sessions.

Run this only from an activated ``bci-plot`` Conda environment. Each session
is launched sequentially in a fresh child process. The script stops at the
first failure and preserves a complete run log for diagnosis.
"""

from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
PLOT_SCRIPT = PROJECT_DIR / "scripts" / "plot_session_qc.py"
RESULTS_DIR = PROJECT_DIR / "results" / "primary-v1"

SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))
from data_paths import find_session  # noqa: E402

# Only these sessions have the fixation and Encoding1 event fields required by
# the frozen primary analysis. The ses-1 files are deliberately excluded.
SESSIONS = (
    "sub-1_ses-2_ecephys+image.nwb",
    "sub-11_ses-2_ecephys+image.nwb",
    "sub-20_ses-2_ecephys+image.nwb",
    "sub-21_ses-2_ecephys+image.nwb",
)


def write_line(log_file, message: str) -> None:
    print(message, flush=True)
    log_file.write(message + "\n")
    log_file.flush()


def output_name(input_name: str) -> str:
    return input_name.removesuffix("_ecephys+image.nwb")


def main() -> None:
    conda_prefix = Path(os.environ.get("CONDA_PREFIX", ""))
    if conda_prefix.name != "bci-plot":
        raise SystemExit(
            "Activate the plotting environment first: conda activate bci-plot"
        )

    run_dir = RESULTS_DIR / "plot_runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S%z")
    log_path = run_dir / f"representative_plots_{timestamp}.log"

    with log_path.open("w", encoding="utf-8") as log_file:
        write_line(log_file, f"Python: {sys.executable}")
        write_line(log_file, f"Conda environment: {conda_prefix}")
        write_line(log_file, f"Log: {log_path.resolve()}")

        for input_name in SESSIONS:
            input_path = find_session(input_name, PROJECT_DIR)
            output_dir = RESULTS_DIR / output_name(input_name)
            command = [
                sys.executable,
                str(PLOT_SCRIPT),
                "--input",
                str(input_path),
                "--output",
                str(output_dir),
            ]

            write_line(log_file, "")
            write_line(log_file, f"START: {input_name}")
            result = subprocess.run(
                command,
                cwd=PROJECT_DIR,
                text=True,
                encoding="utf-8",
                errors="replace",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if result.stdout:
                log_file.write(result.stdout)
                log_file.flush()
                print(result.stdout, end="", flush=True)

            if result.returncode != 0:
                write_line(log_file, f"FAILED: {input_name} (exit code {result.returncode})")
                raise SystemExit(result.returncode)

            write_line(log_file, f"PASS: {input_name}")

        write_line(log_file, "")
        write_line(log_file, "ALL COMPATIBLE SESSIONS PASSED")


if __name__ == "__main__":
    main()
