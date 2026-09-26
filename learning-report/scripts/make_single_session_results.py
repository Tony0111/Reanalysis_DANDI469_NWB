"""生成单 session（sub-20_ses-2）的主检验结果图（供 learning-record 使用）。

数据来源：results/primary-v2-all/sub-20_ses-2/
运行：uv run python learning-report/scripts/make_single_session_results.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent          # learning-report/scripts
REPORT = HERE.parent                            # learning-report
PROJECT = REPORT.parent                         # 仓库根目录
SESSION_DIR = PROJECT / "results" / "primary-v2-all" / "sub-20_ses-2"
OUT = REPORT / "figures" / "single_session_results.png"


def cjk_font() -> str | None:
    available = {f.name for f in fm.fontManager.ttflist}
    for candidate in [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "PingFang SC",
        "STHeiti",
        "Arial Unicode MS",
    ]:
        if candidate in available:
            return candidate
    return None


font = cjk_font()
if font:
    plt.rcParams["font.sans-serif"] = [font]
plt.rcParams["axes.unicode_minus"] = False

stats = pd.read_csv(SESSION_DIR / "unit_level_statistics.csv").set_index("unit_id")
features = pd.read_csv(SESSION_DIR / "unit_trial_features.csv")
means = features.groupby("unit_id")[["baseline_rate_hz", "response_rate_hz"]].mean()
units = list(stats.index)
colors = plt.get_cmap("tab10")(np.linspace(0, 1, len(units)))

fig, (ax_a, ax_b) = plt.subplots(
    1, 2, figsize=(12.5, 5.0), gridspec_kw={"width_ratios": [1.0, 1.2]},
    constrained_layout=True,
)

# ---------- Panel A: paired baseline -> response mean rate ----------
handles = []
for color, unit in zip(colors, units):
    b = means.loc[unit, "baseline_rate_hz"]
    r = means.loc[unit, "response_rate_hz"]
    line, = ax_a.plot([0, 1], [b, r], marker="o", color=color, lw=1.8, markersize=6)
    handles.append((line, f"unit {unit}"))
ax_a.set_xticks([0, 1], ["Baseline\n(fixation)", "Response\n(after encoding)"])
ax_a.set_xlim(-0.2, 1.2)
ax_a.set_ylim(0.7, 3.1)
ax_a.set_ylabel("平均放电率 (Hz)")
ax_a.set_title("A. 每个 unit 的 baseline → response 平均放电率", loc="left", fontsize=11.5)
ax_a.legend([h for h, _ in handles], [label for _, label in handles],
            loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=5,
            fontsize=8.5, frameon=False)

# ---------- Panel B: effect size with bootstrap 95% CI ----------
ax_b.axvline(0, color="black", ls="--", lw=1)
for i, (color, unit) in enumerate(zip(colors, units)):
    row = stats.loc[unit]
    mean = float(row["mean_delta_hz"])
    lo = float(row["ci95_lower_hz"])
    hi = float(row["ci95_upper_hz"])
    ax_b.errorbar(mean, i, xerr=[[mean - lo], [hi - mean]],
                  fmt="o", color=color, capsize=4, markersize=6, lw=1.6)
    ax_b.text(hi + 0.05, i, f"q={row['fdr_q']:.2f}   n={int(row['n_trials'])}",
              va="center", fontsize=8.5, color="#495057")
ax_b.set_yticks(range(len(units)), [f"unit {u}" for u in units])
ax_b.invert_yaxis()
ax_b.set_xlim(-0.95, 1.25)
ax_b.set_xlabel("平均差值 response − baseline (Hz)   [bootstrap 95% CI]")
ax_b.set_title("B. 效应量与 95% CI（虚线 = 0）", loc="left", fontsize=11.5)

fig.suptitle(
    "sub-20_ses-2 主检验结果：135 trials / 5 units；0/5 通过 FDR（q < 0.05）",
    fontsize=12.5,
)
fig.savefig(OUT, dpi=200, facecolor="white")
plt.close(fig)
print(f"saved: {OUT}")
