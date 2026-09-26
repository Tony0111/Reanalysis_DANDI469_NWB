"""生成全量（21 个兼容 session）主检验结果图（供 learning-record 使用）。

左侧：每个 session 的 unit 效应分布（红点 = q < 0.05，黑竖线 = session 中位数）。
右侧：每个 session 的显著 unit 数。
超出显示范围的极端效应值用三角形标在边界；数值全部来自 results/primary-v2-all/。
运行：uv run python learning-report/scripts/make_all_sessions_results.py
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
UNIT_CSV = PROJECT / "results" / "primary-v2-all" / "unit_statistics_all_sessions.csv"
OUT = REPORT / "figures" / "all_sessions_results.png"

LIM = 1.6  # 显示范围 ±1.6 Hz，超出者标在边界
GREY = "#9AA5B1"
RED = "#C0392B"


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

units = pd.read_csv(UNIT_CSV)
units["subject_num"] = units["subject_id"].astype(int)
session_order = [
    key for key, _ in sorted(
        units.groupby("session_key")["subject_num"].first().items(),
        key=lambda item: item[1],
    )
]

rng = np.random.default_rng(20260926)


def plot_points(ax, x, y, *, color, size, edge=None):
    x = np.asarray(x, float)
    inside = np.abs(x) <= LIM
    ax.scatter(np.clip(x[inside], -LIM, LIM), y[inside], s=size, color=color,
               edgecolors=edge, linewidths=0.5 if edge else 0, zorder=3)
    for mask, marker, side in ((x < -LIM, "<", -LIM), (x > LIM, ">", LIM)):
        if mask.any():
            ax.scatter(np.full(mask.sum(), side), y[mask], s=size, marker=marker,
                       color=color, zorder=3)


fig, (ax, ax2) = plt.subplots(
    1, 2, figsize=(12.5, 9.0), gridspec_kw={"width_ratios": [3.1, 1.0]},
    sharey=True, constrained_layout=True,
)

for y, key in enumerate(session_order):
    sub = units[units["session_key"] == key]
    x = sub["mean_delta_hz"].to_numpy()
    sig = sub["significant_q05"].to_numpy().astype(bool)
    y_jit = y + rng.uniform(-0.24, 0.24, size=len(sub))

    plot_points(ax, x[~sig], y_jit[~sig], color=GREY, size=12)
    plot_points(ax, x[sig], y_jit[sig], color=RED, size=30, edge="white")

    median = float(np.median(x))
    ax.plot([np.clip(median, -LIM, LIM)] * 2, [y - 0.3, y + 0.3],
            color="black", lw=1.6, zorder=4)

    k, n = int(sig.sum()), len(sub)
    ax2.barh(y, k, height=0.55, color=RED if k else GREY, alpha=0.85, zorder=2)
    ax2.text(k + 0.15, y, f"{k}/{n}", va="center", fontsize=8.5, color="#495057")

ax.axvline(0, color="black", ls="--", lw=1)
ax.set_xlim(-LIM - 0.1, LIM + 0.1)
ax.set_xticks([-1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5])
ax.set_xlabel("unit 平均差值 response − baseline (Hz)")
ax.set_yticks(range(len(session_order)),
              [f"sub-{units.loc[units.session_key == k, 'subject_num'].iloc[0]}" for k in session_order])
ax.invert_yaxis()
ax.set_ylim(len(session_order) - 0.4, -0.6)
ax.grid(axis="y", color="0.9", lw=0.6, zorder=0)
ax.set_title("A. 每个 session 的 unit 效应分布（红 = q<0.05，黑线 = 中位数）", loc="left", fontsize=11)

max_k = int(units.groupby("session_key")["significant_q05"].sum().max())
ax2.set_xlim(0, max_k + 3)
ax2.set_xlabel("显著 unit 数（标注为 显著 / 总数）")
ax2.set_title("B. 显著 unit 数", loc="left", fontsize=11)
ax2.grid(axis="y", color="0.9", lw=0.6, zorder=0)

fig.suptitle(
    "全量主分析：21 个兼容 session / 901 个 QC unit / 101 个 q<0.05\n"
    "各 session 效应方向不一致；超出 ±1.6 Hz 的极端值用三角标在边界",
    fontsize=12.5,
)
fig.savefig(OUT, dpi=200, facecolor="white")
plt.close(fig)
print(f"saved: {OUT}")
