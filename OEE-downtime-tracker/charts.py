"""
charts.py
---------
Generates and saves all OEE visualisation charts.

Charts produced:
  1. OEE trend line by date (all lines + world-class benchmark)
  2. Pareto chart — downtime by reason
  3. OEE component breakdown by line (stacked bar: A x P x Q)
  4. Availability heatmap by line and date
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np
import os

WORLD_CLASS_OEE = 85          # % benchmark line
CHART_DIR = "charts"
COLORS = {
    "availability": "#1D9E75",
    "performance":  "#378ADD",
    "quality":      "#BA7517",
    "oee":          "#534AB7",
    "benchmark":    "#E24B4A",
    "bars":         ["#1D9E75", "#378ADD", "#BA7517", "#534AB7"],
}
FONT = {"family": "DejaVu Sans", "size": 11}
plt.rc("font", **FONT)


def _save(fig, filename: str):
    os.makedirs(CHART_DIR, exist_ok=True)
    path = os.path.join(CHART_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ── Chart 1: OEE trend over time ──────────────────────────────────────────────
def plot_oee_trend(df_by_date: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        df_by_date["date"], df_by_date["avg_oee"],
        color=COLORS["oee"], linewidth=2.5, marker="o",
        markersize=6, label="Daily OEE (%)"
    )
    ax.axhline(
        WORLD_CLASS_OEE, color=COLORS["benchmark"],
        linewidth=1.5, linestyle="--", label=f"World-class benchmark ({WORLD_CLASS_OEE}%)"
    )

    # Shade area below benchmark
    ax.fill_between(
        df_by_date["date"], df_by_date["avg_oee"], WORLD_CLASS_OEE,
        where=(df_by_date["avg_oee"] < WORLD_CLASS_OEE),
        alpha=0.12, color=COLORS["benchmark"], label="Gap to benchmark"
    )

    ax.set_title("OEE trend — all lines (daily average)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("OEE (%)")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.set_ylim(50, 100)
    ax.legend(fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.autofmt_xdate()

    _save(fig, "1_oee_trend.png")


# ── Chart 2: Pareto — downtime by reason ──────────────────────────────────────
def plot_pareto(pareto_series: pd.Series):
    labels = pareto_series.index.tolist()
    values = pareto_series.values
    cumulative = np.cumsum(values) / values.sum() * 100

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()

    bars = ax1.bar(labels, values, color=COLORS["bars"][:len(labels)], alpha=0.85, zorder=2)
    ax2.plot(labels, cumulative, color="#2C2C2A", linewidth=2, marker="D",
             markersize=6, label="Cumulative %", zorder=3)
    ax2.axhline(80, color=COLORS["benchmark"], linewidth=1, linestyle="--", alpha=0.7)
    ax2.text(len(labels) - 0.5, 81, "80%", color=COLORS["benchmark"], fontsize=9)

    # Value labels on bars
    for bar in bars:
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2,
            f"{int(bar.get_height())} min",
            ha="center", va="bottom", fontsize=10
        )

    ax1.set_title("Pareto chart — downtime by reason", fontsize=13, fontweight="bold", pad=12)
    ax1.set_xlabel("Downtime reason")
    ax1.set_ylabel("Total downtime (minutes)")
    ax2.set_ylabel("Cumulative (%)")
    ax2.set_ylim(0, 110)
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax1.grid(axis="y", linestyle="--", alpha=0.3, zorder=0)

    _save(fig, "2_pareto_downtime.png")


# ── Chart 3: OEE component breakdown by line ──────────────────────────────────
def plot_component_breakdown(df_by_line: pd.DataFrame):
    lines = df_by_line["line"].tolist()
    x = np.arange(len(lines))
    width = 0.22

    fig, ax = plt.subplots(figsize=(10, 5))

    b1 = ax.bar(x - width, df_by_line["avg_availability"], width,
                label="Availability", color=COLORS["availability"], alpha=0.85)
    b2 = ax.bar(x,           df_by_line["avg_performance"],  width,
                label="Performance",  color=COLORS["performance"],  alpha=0.85)
    b3 = ax.bar(x + width,   df_by_line["avg_quality"],      width,
                label="Quality",      color=COLORS["quality"],      alpha=0.85)

    # OEE as a line overlay
    ax.plot(x, df_by_line["avg_oee"], color=COLORS["oee"],
            linewidth=2.5, marker="o", markersize=7, label="OEE (%)", zorder=5)
    ax.axhline(WORLD_CLASS_OEE, color=COLORS["benchmark"],
               linewidth=1.5, linestyle="--", label=f"World-class ({WORLD_CLASS_OEE}%)")

    ax.set_title("OEE component breakdown by production line", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(lines)
    ax.set_ylabel("(%)")
    ax.set_ylim(50, 105)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.legend(fontsize=10, ncol=3)
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    _save(fig, "3_component_breakdown.png")


# ── Chart 4: Availability heatmap ─────────────────────────────────────────────
def plot_availability_heatmap(df: pd.DataFrame):
    pivot = df.pivot_table(
        index="line", columns="date", values="availability", aggfunc="mean"
    )
    pivot.columns = [d.strftime("%d-%b") for d in pivot.columns]

    fig, ax = plt.subplots(figsize=(11, 4))
    im = ax.imshow(pivot.values, cmap="RdYlGn", aspect="auto", vmin=70, vmax=100)

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=10)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=10)

    # Annotate each cell
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            ax.text(j, i, f"{val:.1f}%", ha="center", va="center",
                    fontsize=9, color="black", fontweight="bold")

    plt.colorbar(im, ax=ax, label="Availability (%)", fraction=0.03, pad=0.02)
    ax.set_title("Availability heatmap — line × date", fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()

    _save(fig, "4_availability_heatmap.png")
