"""Create small, independent raster/PSTH QC figures for one NWB session."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pynwb import NWBHDF5IO

PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from sternberg_primary import (  # noqa: E402
    BASELINE_WINDOW,
    RESPONSE_WINDOW,
    build_trial_qc,
)


PLOT_WINDOW = (-0.8, 1.0)
PSTH_BIN_SECONDS = 0.05


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--unit-id", nargs="*", type=int)
    return parser.parse_args()


def selected_units(unit_ids: list[int], requested: list[int] | None) -> list[int]:
    if requested:
        missing = sorted(set(requested) - set(unit_ids))
        if missing:
            raise ValueError(f"Requested unit IDs are not present: {missing}")
        return requested
    positions = sorted(set([0, len(unit_ids) // 2, len(unit_ids) - 1]))
    return [unit_ids[position] for position in positions]


def plot_unit(unit_id: int, spike_times: np.ndarray, onsets: np.ndarray, output_path: Path) -> None:
    edges = np.arange(
        PLOT_WINDOW[0], PLOT_WINDOW[1] + PSTH_BIN_SECONDS, PSTH_BIN_SECONDS
    )
    aligned = []
    counts = np.zeros(len(edges) - 1, dtype=int)
    for onset in onsets:
        left = np.searchsorted(spike_times, onset + PLOT_WINDOW[0])
        right = np.searchsorted(spike_times, onset + PLOT_WINDOW[1])
        relative = spike_times[left:right] - onset
        aligned.append(relative)
        counts += np.histogram(relative, bins=edges)[0]

    fig, axes = plt.subplots(2, 1, figsize=(9, 5), sharex=True, constrained_layout=True)
    raster_ax, psth_ax = axes
    raster_ax.axvline(0, color="black", lw=1)
    raster_ax.axvspan(*BASELINE_WINDOW, color="0.9", zorder=-1)
    raster_ax.axvspan(*RESPONSE_WINDOW, color="#dbeaf5", zorder=-1)
    raster_x = np.concatenate(aligned) if any(len(value) for value in aligned) else np.array([])
    raster_y = np.concatenate(
        [np.full(len(value), trial_number) for trial_number, value in enumerate(aligned)]
    ) if raster_x.size else np.array([])
    raster_ax.scatter(raster_x, raster_y, marker="|", s=7, linewidths=0.4, color="black")
    raster_ax.set_ylabel("Trial")
    raster_ax.set_title(f"Unit {unit_id}: raster")

    rate = counts / (len(onsets) * PSTH_BIN_SECONDS)
    psth_ax.step(edges[:-1], rate, where="post", color="#0072B2", lw=1.5)
    psth_ax.axvline(0, color="black", lw=1)
    psth_ax.axvspan(*BASELINE_WINDOW, color="0.9", zorder=-1)
    psth_ax.axvspan(*RESPONSE_WINDOW, color="#dbeaf5", zorder=-1)
    psth_ax.set_xlabel("Time from first encoding onset (s)")
    psth_ax.set_ylabel("Rate (Hz)")
    psth_ax.set_title(f"Unit {unit_id}: PSTH")
    psth_ax.set_xlim(PLOT_WINDOW)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    input_path = args.input if args.input.is_absolute() else PROJECT_DIR / args.input
    output_dir = args.output if args.output.is_absolute() else PROJECT_DIR / args.output
    output_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    with NWBHDF5IO(str(input_path.resolve()), "r", load_namespaces=True) as io:
        nwbfile = io.read()
        trials = nwbfile.trials.to_dataframe()
        units = nwbfile.units.to_dataframe()
        trial_qc = build_trial_qc(trials)
        valid_trials = trial_qc.loc[trial_qc["keep"]]
        unit_ids = units.index.to_list()
        ids = selected_units(unit_ids, args.unit_id)
        onsets = valid_trials["encoding_onset"].to_numpy()
        for unit_id in ids:
            spike_times = np.asarray(units.loc[unit_id, "spike_times"])
            output_path = output_dir / f"unit_{unit_id}_raster_psth.png"
            plot_unit(unit_id, spike_times, onsets, output_path)
            print(f"saved: {output_path.resolve()}")


if __name__ == "__main__":
    main()
