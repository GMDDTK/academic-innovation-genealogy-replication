"""Build Figure 8 from the released paper-level count table."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.font_manager import findfont
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr


HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "data" / "papers.csv.gz"
PDF_FILE = HERE / "figures" / "Figure_8.pdf"
GROUPS = {
    "all": "All sources",
    "citation_only": "Citation only",
    "both": "Both signals",
    "semantic_archived": "Semantic only (archive)",
    "semantic_no_direct_citation": "Semantic only\n(excluding direct citations)",
}


def load_counts():
    papers = pd.read_csv(DATA_FILE)
    window = papers[papers["in_five_year_sample"].eq(1)]
    return {
        period: {key: frame[f"{key}_{period}"].to_numpy() for key in ("citations", *GROUPS)}
        for period, frame in (("all", papers), ("five_year", window))
    }


def correlations(data):
    return {
        period: {
            key: (pearsonr(values[key], values["citations"]).statistic,
                  spearmanr(values[key], values["citations"]).statistic)
            for key in GROUPS
        }
        for period, values in data.items()
    }


def density_panels(fig, axes, color_axis, data):
    keys = ("citation_only", "semantic_no_direct_citation")
    y = np.log1p(data["citations"])
    x_values = [np.log1p(data[key]) for key in keys]
    x_max = max(x.max() for x in x_values)
    y_max = y.max()
    x_edges = np.linspace(-0.04, x_max + 0.04, 43)
    y_edges = np.linspace(-0.04, y_max + 0.04, 43)
    histograms = [np.histogram2d(x, y, bins=(x_edges, y_edges))[0] for x in x_values]
    assert all(h.sum() == len(y) for h in histograms)
    normalizer = LogNorm(vmin=1, vmax=max(h.max() for h in histograms))
    ticks = np.array([0, 1, 3, 10, 30, 100, 300, 1000, 3000])
    titles = ("A  Citation only", "B  Semantic only, excluding direct citations")
    for ax, title, density in zip(axes, titles, histograms, strict=True):
        image = ax.pcolormesh(x_edges, y_edges, np.ma.masked_equal(density.T, 0), cmap="viridis", norm=normalizer)
        ax.set(xlim=(x_edges[0], x_edges[-1]), ylim=(y_edges[0], y_edges[-1]))
        x_ticks = ticks[np.log1p(ticks) <= x_max]
        y_ticks = ticks[np.log1p(ticks) <= y_max]
        ax.set_xticks(np.log1p(x_ticks), [f"{v:,}" for v in x_ticks])
        ax.set_yticks(np.log1p(y_ticks), [f"{v:,}" for v in y_ticks])
        ax.set_xlabel("Inferred out-degree")
        ax.set_title(title, loc="left", fontweight="semibold", pad=9)
    axes[0].set_ylabel("Within-corpus citations")
    axes[1].tick_params(axis="y", labelleft=False)
    colorbar = fig.colorbar(image, cax=color_axis, label="Papers per bin")
    color_ticks = [10**power for power in range(int(np.log10(normalizer.vmax)) + 1)]
    colorbar.set_ticks(color_ticks, labels=[f"{tick:,}" for tick in color_ticks])


def coefficient_panels(fig, axes, values):
    colors = {"all": "#174C72", "five_year": "#AD4E13"}
    y = np.arange(len(GROUPS))[::-1]
    for i, (ax, title) in enumerate(zip(axes, ("C  Pearson correlation", "D  Spearman correlation"), strict=True)):
        overall = [values["all"][key][i] for key in GROUPS]
        five = [values["five_year"][key][i] for key in GROUPS]
        ax.hlines(y, np.minimum(overall, five), np.maximum(overall, five), color="#AEBCC7", linewidth=1.4, zorder=1)
        ax.scatter(overall, y, color=colors["all"], marker="o", s=30, linewidths=0, zorder=3)
        ax.scatter(five, y, facecolors="white", edgecolors=colors["five_year"], marker="D", s=30, linewidths=1.2, zorder=4)
        ax.set_yticks(y, list(GROUPS.values()) if i == 0 else [""] * len(GROUPS))
        ax.set(xlim=(0, 1), ylim=(-0.55, len(GROUPS) - 0.45))
        ax.set_xticks(np.arange(0, 1.01, .2), ["0", "0.2", "0.4", "0.6", "0.8", "1.0"])
        ax.grid(axis="x", color="#DCE3E8", linewidth=0.7, zorder=0)
        ax.tick_params(axis="y", length=0)
        ax.set_title(title, loc="left", fontweight="semibold", pad=8)
    fig.legend(
        handles=[
            Line2D([], [], linestyle="", marker="o", color=colors["all"], label="Full period"),
            Line2D([], [], linestyle="", marker="D", markerfacecolor="white",
                   markeredgecolor=colors["five_year"], label="Five-year window"),
        ],
        loc="lower center", bbox_to_anchor=(0.55, 0.02), frameon=False, ncol=2,
    )


def draw():
    data = load_counts()
    values = correlations(data)
    findfont("Times New Roman", fallback_to_default=False)
    plt.rcParams.update({
        "font.family": "Times New Roman",
        "font.size": 10,
        "axes.titlesize": 10.5,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#586774",
        "pdf.fonttype": 42,
    })
    fig = plt.figure(figsize=(9.8, 6.55))
    grid = fig.add_gridspec(
        2, 3, width_ratios=(1, 1, 0.047), height_ratios=(1.22, 1),
        left=0.225, right=0.927, top=0.93, bottom=0.116, hspace=0.47, wspace=0.22,
    )
    density_panels(fig, (fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1])), fig.add_subplot(grid[0, 2]), data["all"])
    coefficient_panels(fig, (fig.add_subplot(grid[1, 0]), fig.add_subplot(grid[1, 1])), values)
    fig.savefig(PDF_FILE, metadata={"Title": "Figure 8. Inferred out-degree and within-corpus citations"})
    plt.close(fig)
    print(f"Wrote {PDF_FILE}")


if __name__ == "__main__":
    draw()
