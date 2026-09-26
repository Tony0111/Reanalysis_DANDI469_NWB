"""Generate a small sequential set of raster/PSTH QC figures for primary-v2-all."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import subprocess
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
PLOT_SCRIPT = PROJECT_DIR / "scripts" / "plot_session_qc.py"
RESULTS_DIR = PROJECT_DIR / "results" / "primary-v2-all"
SESSION_NAMES = (
    "sub-1_ses-2_ecephys+image.nwb",
    "sub-9_ses-2_ecephys+image.nwb",
    "sub-11_ses-2_ecephys+image.nwb",
)


def write_line(log_file, message: str) -> None:
    print(message, flush=True)
    log_file.write(message + "\n")
    log_file.flush()


def session_key(input_name: str) -> str:
    return input_name.removesuffix("_ecephys+image.nwb")


def find_input(input_name: str) -> Path:
    matches = list(
        (PROJECT_DIR / "raw" / "all" / "000469").rglob(input_name)
    )
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected exactly one input for {input_name}, found {len(matches)}"
        )
    return matches[0]


def main() -> None:
    run_dir = RESULTS_DIR / "plot_runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S%z")
    log_path = run_dir / f"representative_plots_v2_{timestamp}.log"

    with log_path.open("w", encoding="utf-8") as log_file:
        write_line(log_file, f"Python: {sys.executable}")
        write_line(log_file, f"Environment prefix: {sys.prefix}")
        write_line(log_file, f"Log: {log_path.resolve()}")
        write_line(log_file, "Sessions: " + ", ".join(session_key(name) for name in SESSION_NAMES))

        for input_name in SESSION_NAMES:
            input_path = find_input(input_name)
            key = session_key(input_name)
            output_dir = RESULTS_DIR / key
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
        write_line(log_file, "ALL SELECTED V2 SESSIONS PASSED")


if __name__ == "__main__":
    main()
