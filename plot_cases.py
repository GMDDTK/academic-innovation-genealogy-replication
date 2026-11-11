"""Draw the six illustrative gaps using the released selection and title tables."""

from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import findfont
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent


def main():
    cases = pd.read_csv(HERE / "results" / "illustrative_cases.csv")
    titles = pd.read_csv(HERE / "data" / "case_titles.csv")
    cases = cases.merge(titles, on="paper_id", validate="one_to_one")
    assert list(cases.groupby("profile", sort=False).size()) == [3, 3]
    findfont("Times New Roman", fallback_to_default=False)
    plt.rcParams.update({
        "font.family": "Times New Roman",
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "pdf.fonttype": 42,
    })
    citation_color = "#174C72"
    logic_color = "#AD4E13"
    positions = np.array([6.5, 5.35, 4.2, 2.55, 1.4, 0.25])
    fig = plt.figure(figsize=(9.8, 5.2))
    ax = fig.add_axes([0.375, 0.17, 0.43, 0.74])
    annotations = fig.add_axes([0.825, 0.17, 0.155, 0.74], sharey=ax)
    annotations.axis("off")
    citations = cases["citations_all"].to_numpy()
    outdegrees = cases["all_all"].to_numpy()
    cx, dx = np.log1p(citations), np.log1p(outdegrees)
    ax.hlines(positions, np.minimum(cx, dx), np.maximum(cx, dx), color="#B5C0C9", linewidth=1.6, zorder=1)
    ax.scatter(cx, positions, color=citation_color, s=34, zorder=3)
    ax.scatter(dx, positions, marker="D", facecolor="white", edgecolor=logic_color, linewidth=1.25, s=37, zorder=4)

    labels = []
    for row in cases.itertuples():
        title = row.title.capitalize() if row.title.isupper() else row.title
        short = textwrap.shorten(title, width=72, placeholder="…")
        labels.append(textwrap.fill(f"{short} ({row.issue_year})", width=45))
    ax.set_yticks(positions, labels)
    ax.tick_params(axis="y", length=0, labelsize=9.4, pad=8)
    ticks = [0, 1, 3, 10, 30, 100, 300, 1000, 3000]
    ax.set_xticks(np.log1p(ticks), [f"{x:,}" for x in ticks])
    ax.set_xlim(-.10, np.log1p(3250))
    ax.set_ylim(-.3, 7.47)
    ax.grid(axis="x", color="#DFE5EA", linewidth=.7)
    ax.set_axisbelow(True)
    ax.set_xlabel("Count over the full period")
    for x, title, color in ((.25, "Citations", citation_color), (.76, "Out-degree", logic_color)):
        annotations.text(x, 7.20, title, color=color, fontweight="bold", ha="center", fontsize=10)
    for y, c, d in zip(positions, citations, outdegrees, strict=True):
        annotations.text(.25, y, f"{c:,}", color=citation_color, ha="center", va="center")
        annotations.text(.76, y, f"{d:,}", color=logic_color, ha="center", va="center")
    ax.axhline(3.43, color="#CAD3DC", linewidth=.8)
    ax.text(.015, 7.18, "Citation count exceeds out-degree", transform=ax.get_yaxis_transform(), fontweight="bold")
    ax.text(.015, 3.11, "Out-degree exceeds citation count", transform=ax.get_yaxis_transform(), fontweight="bold")
    fig.legend(
        handles=[
            Line2D([], [], marker="o", linestyle="", color=citation_color, label="Within-corpus citations"),
            Line2D([], [], marker="D", linestyle="", markerfacecolor="white", markeredgecolor=logic_color,
                   label="Inferred out-degree (all sources)"),
        ],
        loc="lower center", bbox_to_anchor=(.59, .013), ncol=2, frameon=False,
    )
    fig.savefig(HERE / "figures" / "Figure_9.pdf", metadata={"Title": "Figure 9. Illustrative citation and out-degree profiles"})
    plt.close(fig)


if __name__ == "__main__":
    main()
