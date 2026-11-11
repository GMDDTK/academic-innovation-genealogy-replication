"""Draw the five topic-flow matrices from the released archive aggregates."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.font_manager import findfont
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
COLORS = {
    "Supplement": "#9467BD",
    "Analogy": "#F28E2B",
    "Comparison": "#E15759",
    "Implication": "#76B7B2",
    "Usage": "#59A14F",
}


def main():
    flows = pd.read_csv(HERE / "data" / "topic_flows.csv")
    topics = pd.read_csv(HERE / "data" / "topic_hierarchy.csv")["micro_topic"].tolist()
    ticks = np.arange(0, len(topics), max(1, len(topics) // 15))
    tick_labels = [f"T{topics[i]}" for i in ticks]
    findfont("Times New Roman", fallback_to_default=False)
    plt.rcParams.update({"font.family": "Times New Roman", "pdf.fonttype": 42})
    fig, axes = plt.subplots(2, 3, figsize=(13.6, 6.9), layout="constrained")
    for ax, (relation, color) in zip(axes.flat[:5], COLORS.items(), strict=True):
        table = flows.loc[flows["relation"].eq(relation)].pivot(
            index="source_topic", columns="target_topic", values="edges"
        )
        counts = table.reindex(index=topics, columns=topics).fillna(0).to_numpy()
        cap = max(int(np.percentile(counts[counts > 0], 95)), 1)
        palette = LinearSegmentedColormap.from_list(relation, ["white", color])
        hm = ax.imshow(counts, cmap=palette, interpolation="nearest", vmin=0, vmax=cap)
        ax.set_title(relation, fontweight="bold")
        ax.set_xticks(ticks, tick_labels, rotation=45, fontsize=8)
        ax.set_yticks(ticks, tick_labels, fontsize=8)
        ax.set(xlabel="Target topic", ylabel="Source topic")
        bar = fig.colorbar(hm, ax=ax, fraction=0.047, pad=0.04, extend="max")
        bar.set_label(f"Logical edges (cap: {cap})", fontsize=9)
        bar.ax.tick_params(labelsize=8)
        print(f"{relation}: {counts.sum():.0f} logical edges, color cap {cap}")
    guide = axes.flat[-1]
    guide.axis("off")
    guide.text(0.5, 0.52,
               "Rows show source topics and columns show target topics.\n"
               "The diagonal counts within-topic logical edges.\n"
               "Colors are capped at the 95th percentile\n"
               "of nonzero counts in each matrix.",
               ha="center", va="center", fontsize=11, linespacing=1.6)
    target = HERE.parent / "figures" / "Figure_2.pdf"
    fig.savefig(target, metadata={"Title": "Figure 2. Topic-flow matrices for five logical relation types"})
    plt.close(fig)


if __name__ == "__main__":
    main()
