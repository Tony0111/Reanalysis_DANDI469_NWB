"""生成 Sternberg 单 trial 的时间线图（供 learning-record 使用）。

数据来源：sub-20_ses-2 的第 0 个 trial。
运行：uv run python learning-report/scripts/make_trial_timeline.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from pynwb import NWBHDF5IO

HERE = Path(__file__).resolve().parent          # learning-report/scripts
REPORT = HERE.parent                            # learning-report
PROJECT = REPORT.parent                         # 仓库根目录
NWB = PROJECT / "raw" / "all" / "000469" / "sub-20" / "sub-20_ses-2_ecephys+image.nwb"
OUT = REPORT / "figures" / "trial_timeline.png"


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

with NWBHDF5IO(str(NWB), "r", load_namespaces=True) as io:
    trial = io.read().trials.to_dataframe().iloc[0]

fix = float(trial["timestamps_FixationCross"])


def rel(column: str) -> float:
    return float(trial[column]) - fix


enc1, enc1e = rel("timestamps_Encoding1"), rel("timestamps_Encoding1_end")
enc2, enc2e = rel("timestamps_Encoding2"), rel("timestamps_Encoding2_end")
enc3, enc3e = rel("timestamps_Encoding3"), rel("timestamps_Encoding3_end")
maint = rel("timestamps_Maintenance")
probe = rel("timestamps_Probe")
resp = rel("timestamps_Response")

BASELINE = (-0.8, 0.0)
RESPONSE = (0.2, 1.0)

fig, (ax_a, ax_b) = plt.subplots(
    2, 1, figsize=(11.5, 6.6), gridspec_kw={"height_ratios": [1.15, 1.0]},
    constrained_layout=True,
)

# ---------------- Panel A: 完整 trial（以 fixation 为 0） ----------------
bar_y, bar_h = 0.0, 0.62
phases = [
    ("Fixation", 0.0, enc1, "#BDBDBD"),
    ("Encoding 1", enc1, enc1e, "#4C72B0"),
    ("Encoding 2", enc2, enc2e, "#4C72B0"),
    ("Encoding 3", enc3, enc3e, "#4C72B0"),
    ("Maintenance", maint, probe, "#55A868"),
]
for name, start, end, color in phases:
    width = end - start
    ax_a.broken_barh([(start, width)], (bar_y - bar_h / 2, bar_h),
                     facecolors=color, edgecolor="white", linewidth=0.8)
    ax_a.text((start + end) / 2, bar_y, name, ha="center", va="center",
              fontsize=9, color="white" if name.startswith("Encoding") else "#222222")

# Probe / Response 用标记点，避免和 Maintenance 条重叠
ax_a.scatter([probe], [bar_y], marker="D", s=42, color="#C44E52", zorder=5)
ax_a.scatter([resp], [bar_y], marker="*", s=150, color="#8172B3", zorder=5)
ax_a.text(probe, bar_y + bar_h / 2 + 0.28, "Probe", ha="center", va="bottom",
          fontsize=9, color="#C44E52")
ax_a.text(resp, bar_y + bar_h / 2 + 0.28, "Response", ha="center", va="bottom",
          fontsize=9, color="#8172B3")

event_ticks = [
    ("FixationCross", 0.0),
    ("Encoding1", enc1),
    ("Encoding2", enc2),
    ("Encoding3", enc3),
    ("Maintenance", maint),
    ("Probe", probe),
    ("Response", resp),
]
positions = [p for _, p in event_ticks]
labels = [f"{name}\n{p:.2f}s" for name, p in event_ticks]
for _, p in event_ticks:
    ax_a.plot([p, p], [bar_y - bar_h / 2 - 0.05, -0.62], color="0.75",
              linewidth=0.7, linestyle=":", zorder=0)
ax_a.set_xticks(positions)
ax_a.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
ax_a.set_xlim(-0.25, resp + 0.35)
ax_a.set_ylim(-0.72, 1.3)
ax_a.set_yticks([])
ax_a.set_xlabel("相对于 fixation 的时间（秒）", fontsize=9)
ax_a.set_title("A. 一个完整 trial 的事件时间线（sub-20_ses-2 第 0 个 trial）", fontsize=11, loc="left")
for spine in ["left", "right", "top"]:
    ax_a.spines[spine].set_visible(False)

# ---------------- Panel B: 主分析的两个时间窗（以 Encoding1 onset 为 0） ----------------
ax_b.axvspan(*BASELINE, color="#BDBDBD", alpha=0.55, zorder=0)
ax_b.axvspan(*RESPONSE, color="#4C72B0", alpha=0.30, zorder=0)
ax_b.axvspan(0.0, RESPONSE[0], color="#F2C14E", alpha=0.35, zorder=0)

ax_b.axvline(0.0, color="black", linewidth=1.4, zorder=3)
enc2_rel = enc2 - enc1
ax_b.axvline(enc2_rel, color="#4C72B0", linewidth=1.0, linestyle=":", zorder=3)

ylim = (0, 1)
ax_b.set_ylim(*ylim)
ax_b.text(np.mean(BASELINE), 0.72, "基线窗\n[-0.8, 0) s", ha="center", va="center",
          fontsize=9, color="#333333")
ax_b.text(np.mean(RESPONSE), 0.72, "响应窗\n[0.2, 1.0) s", ha="center", va="center",
          fontsize=9, color="#1F3B57")
ax_b.text(RESPONSE[0] / 2, 0.22, "缓冲\n0–0.2 s", ha="center", va="center",
          fontsize=8, color="#8A6D1B")
ax_b.text(0.0, 1.0, "Encoding1 onset = 0", ha="center", va="bottom", fontsize=9.5)
ax_b.text(enc2_rel, 1.0, "Encoding2 onset", ha="center", va="bottom", fontsize=9,
          color="#4C72B0")
ax_b.annotate("", xy=(RESPONSE[1], 0.5), xytext=(BASELINE[0], 0.5),
              arrowprops=dict(arrowstyle="<->", color="black", linewidth=1.0))
ax_b.text((BASELINE[0] + RESPONSE[1]) / 2, 0.42,
          "两个窗都是 0.8 s，可直接做配对差值", ha="center", va="top", fontsize=8.5)

ax_b.set_xlim(BASELINE[0] - 0.1, enc2_rel + 0.15)
ax_b.set_yticks([])
ax_b.set_xlabel("相对于第一张编码图片 onset 的时间（秒）", fontsize=9)
ax_b.set_title("B. 主分析用的两个时间窗", fontsize=11, loc="left")
for spine in ["left", "right", "top"]:
    ax_b.spines[spine].set_visible(False)

fig.savefig(OUT, dpi=200, facecolor="white")
plt.close(fig)
print(f"saved: {OUT}")
