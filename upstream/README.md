# Materials from the construction stages

These files document the construction stages described in Sections 3–5. Paths below are relative to this folder unless otherwise stated.

| Stage | File | Contents |
| --- | --- | --- |
| Topic organization | [data/topic_hierarchy.csv](data/topic_hierarchy.csv) | All 85 micro-topics, their 18 intermediate categories and seven macro-categories, and paper counts. The paper-to-topic assignments are in the repository's [paper-level table](../data/papers.csv.gz). The hierarchy lists T56, Research Analysis: Turkey and Iran, under Comparative Studies of Regional Research. T55, Comparison of Database Coverage, belongs to Organization and Discovery of Scholarly Resources. |
| Topic organization | [spectral_clustering.py](spectral_clustering.py) | The UMAP and nearest-neighbor spectral clustering settings from the archived spectral clustering script. Input is a local NumPy matrix with one row per document. The default fits 85 clusters. The `--search` option evaluates 80–130 clusters with silhouette scores. |
| Information extraction | [data/sentence_label_counts.csv](data/sentence_label_counts.csv) and [data/entity_span_counts.csv](data/entity_span_counts.csv) | Label and entity-span frequencies by split from the archived binary, six-class, and BIO annotation files. Label IDs and names retain their archive form. The span counter starts a span at each B tag and treats an I tag after a different type or a boundary as a new span. |
| Information extraction | [train_scibert.py](train_scibert.py) | An adapted copy of the archived SciBERT classifier. It accepts local split files and a local checkpoint or model identifier. It uses PyTorch's AdamW and accepts either `val.txt` or `dev.txt`. |
| Logical inference | [data/relation_rules.csv](data/relation_rules.csv) and [analyst_prompt.md](analyst_prompt.md) | Five relation definitions, evidence and direction criteria, and the analyst prompt in the archived Gemini script. The prompt shows the expected JSON fields. The inference archive retains the final decisions. Stage transcripts for review and adjudication are unavailable. |
| Logical inference | [data/retained_relation_counts.csv](data/retained_relation_counts.csv) and [data/retained_relation_examples.csv](data/retained_relation_examples.csv) | Counts from all 270,134 retained edges and 150 illustrative records with OpenAlex work IDs, candidate source, relation type, and archival subtype. The sample takes ten edges per candidate-source × relation-type cell, ordered by the SHA-256 hash of the source label, relation type, and ordered endpoint IDs. It represents the final archive and carries no independent judgment labels. |
| Network analysis | [data/topic_flows.csv](data/topic_flows.csv) and [plot_topic_flows.py](plot_topic_flows.py) | Directed edge counts by source micro-topic, target micro-topic, and relation type. The plotting script uses the original colors and the 95th percentile of nonzero counts in each matrix. Its legend describes the diagonal as within-topic logical edges. |
| Network analysis | [data/top_cross_topic_flows_by_year.csv](data/top_cross_topic_flows_by_year.csv) | Figure 3 counts by source and target issue year and relation type. The twelve directed topic pairs are selected by total edge count among cross-topic edges whose source issue year is no later than the target issue year. |

## Running the examples

```text
python upstream/plot_topic_flows.py
python upstream/spectral_clustering.py embeddings.npy cluster_labels.npy
python upstream/train_scibert.py --data_dir splits --model_name_or_path scibert_checkpoint --save_dir scibert_output
```

Run the commands from the repository root. The topic-flow plot uses the root requirements and an installed Times New Roman font. Spectral clustering requires scikit-learn and umap-learn. SciBERT training requires PyTorch, transformers, scikit-learn, and tqdm. The classifier expects tab-separated files with sentence text followed by a label, one example per line.

The archived annotation counts characterize the files available for this release. Benchmark scores require the corresponding training and test partitions and checkpoints. The public files contain topic and label counts, identifiers, rules, and selected code. They omit the source articles, training sentences, and pair-level evidence text.

The relation tables preserve the order of the two endpoints in the final archive. The archive contains 1,199 edges with a blank subtype and 69 edges with a subtype outside the three reported categories for their respective main relation after spelling variants are harmonized. Blank subtype cells in the CSV denote an empty archived label.
