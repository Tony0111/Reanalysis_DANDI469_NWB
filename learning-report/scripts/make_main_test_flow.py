"""生成单 session 主检验流程图（供 learning-record 使用）。

只画分析部分：窗口特征 → 置换检验 → 效应量/CI → FDR → 汇总图。
数据导入与 QC 属于前置步骤，图中不展开，只在正文说明。
运行：uv run python learning-report/scripts/make_main_test_flow.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent          # learning-report/scripts
REPORT = HERE.parent                            # learning-report
OUT = REPORT / "figures" / "main_test_flow.png"


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

fig, ax = plt.subplots(figsize=(11.5, 8.8))
ax.set_xlim(-0.3, 11.2)
ax.set_ylim(0.0, 11.8)
ax.axis("off")

BOX_X = 4.2
BOX_W = 7.0
OUT_X = 8.2


def draw_box(y, h, title, body, color, *, output=None, muted=False):
    ax.add_patch(
        FancyBboxPatch(
            (BOX_X - BOX_W / 2, y - h / 2), BOX_W, h,
            boxstyle="round,pad=0.06,rounding_size=0.14",
            linewidth=1.6, edgecolor=color,
            facecolor=color if not muted else "#F1F3F5",
            alpha=0.16 if not muted else 1.0,
        )
    )
    ax.text(BOX_X, y + h / 2 - 0.24, title, ha="center", va="top",
            fontsize=11.5, fontweight="bold", color=color if not muted else "#495057")
    ax.text(BOX_X, y + h / 2 - 0.72, body, ha="center", va="top",
            fontsize=9.2, color="#212529")
    if output:
        ax.text(OUT_X, y, output, ha="left", va="center", fontsize=8.6,
                color="#495057",
                bbox=dict(boxstyle="round,pad=0.35", facecolor="#F8F9FA",
                          edgecolor="#CED4DA", linewidth=0.8))


def arrow(y_from, y_to):
    ax.add_patch(
        FancyArrowPatch(
            (BOX_X, y_from), (BOX_X, y_to),
            arrowstyle="-|>", mutation_scale=16, linewidth=1.6, color="#495057",
            shrinkA=0, shrinkB=0,
        )
    )


# 输入
draw_box(
    10.15, 1.0,
    "输入：valid_trials（135）+ valid_units（5）",
    "数据导入、trial QC、unit QC 已完成（前置步骤，图中不展开）",
    "#6C757D", muted=True,
)

steps = [
    (8.35, 1.3, "① 窗口特征（unit × trial）",
     "基线率 [-0.8, 0) Hz，响应率 [0.2, 1.0) Hz\n差值 d = response_rate − baseline_rate",
     "#4C72B0", "unit_trial_features：675 行"),
    (6.55, 1.3, "② 主检验第 1 步：置换检验",
     "每个 unit 内对 135 个 d 做符号翻转\n10,000 次 → 单尾 p（备择：图片后更高）",
     "#DD8452", "permutation_p"),
    (4.75, 1.3, "③ 主检验第 2 步：效应量与不确定性",
     "bootstrap 5,000 次 → 95% CI\ncommon-language effect（概率优势）",
     "#55A868", "ci95_lower/upper\ncommon_language_prob"),
    (2.95, 1.3, "④ 主检验第 3 步：多重比较",
     "5 个 unit 的 p 一起做 BH-FDR\nq < 0.05 判定显著",
     "#C44E52", "fdr_q\nsignificant_q05"),
    (1.15, 1.3, "⑤ 主检验第 4 步：汇总图",
     "配对效应图（baseline → response）\n森林图（effect size ± 95% CI）",
     "#8172B3", "figures"),
]

for y, h, title, body, color, output in steps:
    draw_box(y, h, title, body, color, output=output)

# 箭头
arrow(10.15 - 1.0 / 2, 8.35 + 1.3 / 2)
for (y1, h1, *_), (y2, h2, *_) in zip(steps[:-1], steps[1:]):
    arrow(y1 - h1 / 2, y2 + h2 / 2)

ax.text(BOX_X, 11.7, "单 session 主检验流程", ha="center", va="top",
        fontsize=15, fontweight="bold")
ax.text(0.0, 11.2,
        "说明：图中只画分析部分；数据导入、trial QC、unit QC 是前置步骤，见正文。",
        ha="left", va="top", fontsize=9.5, color="#495057")

fig.savefig(OUT, dpi=200, facecolor="white")
plt.close(fig)
print(f"saved: {OUT}")
