# Academic Innovation Genealogy — replication materials

Analysis data, code, and results accompanying *From Citation Counts to Academic Innovation Genealogies: A Rule-Constrained Multi-Agent Reasoning Framework for Revealing the Evolution of Academic Innovation*.

The release supports reproduction of the paper-level analyses in Section 6. It contains derived counts for 24,767 scientometrics papers, aggregate network counts, results for the citation comparisons and count models, and the data and plotting scripts for Figures 8 and 9. The full-text extraction and inference stages are represented by aggregate counts of their archived outputs.

## Reproduce the analysis

From the repository directory, run the following with Python 3.12.

```text
python -m pip install -r requirements.txt
python analyze.py
python plot_associations.py
python plot_cases.py
```

The plotting scripts use an installed Times New Roman font. The supplied PDF figures retain vector graphics and text, and their PNG versions were rendered from those PDFs.

## Files

| Path | Contents |
| --- | --- |
| [data/papers.csv.gz](data/papers.csv.gz) | One row per paper, with an OpenAlex work identifier, issue year, micro-topic, and derived citation and out-degree counts. Python reads the compressed CSV directly. |
| [data/case_titles.csv](data/case_titles.csv) | Published titles of the six papers in Figure 9. |
| [results/network_overview.json](results/network_overview.json) | Corpus and network totals, candidate records by source, and retained edges by source and relation type. |
| [results/correlations.csv](results/correlations.csv) | Full-period and five-year Pearson and Spearman correlations. |
| [results/within_issue_year_topic.csv](results/within_issue_year_topic.csv) | Correlations after centering logged five-year counts within issue-year and micro-topic cells. |
| [results/count_models.csv](results/count_models.csv) | Negative binomial and Poisson estimates, clustered standard errors, and 95% confidence intervals. |
| [results/archive_count_sensitivity.csv](results/archive_count_sensitivity.csv) | Aggregate comparison using the archival metadata citation field. |
| [results/illustrative_cases.csv](results/illustrative_cases.csv) | Deterministically selected cases and their counts and percentile ranks. |
| [figures/](figures/) | Figures 8 and 9 as vector PDFs and PNGs. |

See [METHODS.md](METHODS.md) for field definitions, units of analysis, and the relation between candidate sources and the citation comparison.
