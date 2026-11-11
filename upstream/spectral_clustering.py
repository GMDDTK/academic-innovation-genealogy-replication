"""Run the archived UMAP and spectral clustering steps on a local embedding matrix."""

import argparse
from pathlib import Path

import numpy as np
from sklearn.cluster import SpectralClustering
from sklearn.metrics import silhouette_score


def fit_spectral(embedding, clusters):
    return SpectralClustering(
        n_clusters=clusters, assign_labels="kmeans", random_state=0,
        n_jobs=-1, affinity="nearest_neighbors",
    ).fit_predict(embedding)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("embeddings", type=Path, help="2-D NumPy .npy array in document order")
    parser.add_argument("labels", type=Path, help="Output .npy file in the same document order")
    parser.add_argument("--search", action="store_true", help="Score candidate K values from 80 to 130")
    parser.add_argument("--clusters", type=int, default=85)
    args = parser.parse_args()
    from umap import UMAP

    vectors = np.load(args.embeddings, allow_pickle=False)
    if vectors.ndim != 2 or not np.isfinite(vectors).all():
        parser.error("embeddings must be a finite 2-D matrix")
    if not 2 <= args.clusters < len(vectors) or len(vectors) < (132 if args.search else 52):
        parser.error("the input must support the cluster count and 50-dimensional UMAP")
    reduced = UMAP(
        n_components=50, random_state=0, n_neighbors=15, min_dist=0.1, metric="cosine",
    ).fit_transform(vectors)
    if args.search:
        best_score, best_labels = -np.inf, None
        for k in range(80, 131):
            labels = fit_spectral(reduced, k)
            if not 2 <= np.unique(labels).size < len(vectors):
                continue
            score = silhouette_score(reduced, labels)
            print(f"K={k}  silhouette={score:.6f}")
            if score > best_score:
                best_score, best_labels = score, labels
        if best_labels is None:
            raise RuntimeError("No valid spectral clustering partition")
        labels = best_labels
    else:
        labels = fit_spectral(reduced, args.clusters)
    np.save(args.labels, labels, allow_pickle=False)


if __name__ == "__main__":
    main()
