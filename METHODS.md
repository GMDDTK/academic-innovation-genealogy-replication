# Section 6 data and methods

## Corpus and relation archive

The analysis uses 24,767 unique OpenAlex work IDs from the archived metadata table. The inferred logical layer contains 23,297 paper nodes and 270,134 directed edges. The citation outcome counts distinct citing papers among the 24,767 works. A citation link with the same citing and cited ID is excluded, and repeated directed links are counted once. These rules give 251,714 within-corpus citation links.

Candidate-source groups reproduce the labels in the inference archive. The archive contains 468,873 inference records. Treating endpoint orders as equivalent and deduplicating across sources yields 468,019 distinct unordered pairs. Of the 148,565 retained edges from archived semantic-only records, 837 have a direct citation in either direction in the reference data used for the citation outcome. Removing those edges yields the 147,728-edge semantic subset.

## Paper-level data

| Field | Definition |
| --- | --- |
| `paper_id` | OpenAlex work ID used in the relation archive. |
| `issue_year` | Publication year in the consolidated issue metadata. |
| `micro_topic` | Numeric identifier for the paper’s assigned micro-topic. |
| `in_five_year_sample` | 1 for issue years through 2019, and 0 otherwise. |
| `stable_id_for_case_selection` | 1 for IDs present in both archived metadata workbooks, and 0 for the three IDs with suffix differences. This field is used for illustrative case selection. |
| `citations_all`, `citations_five_year` | Counts of distinct within-corpus citing papers for the full period and the five-year window. |
| `all_*`, `citation_only_*`, `both_*` | Out-degree over all retained edges, over citation-only edges, or over edges selected by both signals. |
| `semantic_archived_*` | Out-degree over the archived semantic-only edges. |
| `semantic_no_direct_citation_*` | Out-degree over semantic-only edges after excluding pairs with a direct citation in either direction in the reference data. |

The `*_five_year` fields count citations or outward edges to papers issued one to five years after the focal paper through 2024. The fields are blank for papers outside the 18,170-paper five-year sample. All counts retain zeros for included papers.

## Statistical summaries

- **Correlations.** Pearson and Spearman correlations use the same focal-paper set for each candidate source within a period. The additional within-cell analysis uses Pearson correlations of `log(1 + count)` values after centering within issue-year × micro-topic cells with at least ten papers. It includes 13,416 papers across 495 cells.
- **Count models.** Within the common five-year window, the outcome is the within-corpus citation count and the predictor is `log2(1 + semantic out-degree)` after the direct-citation exclusion. Negative binomial (NB2) and Poisson models use publication-decade and micro-topic fixed effects. The earliest cohort pools all issue years through 1979. Standard errors are clustered by micro-topic. The incidence rate ratio is per doubling of one plus semantic out-degree. The trimmed NB2 fit removes papers above either marginal 99th-percentile cutoff, computed with lower interpolation (35 semantic edges or 41 citations).
- **Archival citation-field comparison.** The archived `Citation` metadata field and the within-corpus reference-derived counts are separate measures. The archival field sums to 995,174 across the analysis papers. The release includes the resulting correlations in aggregate because the exact provenance of the archival field could not be recovered from its column label.
- **Illustrative cases.** The difference is full-period out-degree from all retained edges minus within-corpus citations. The three largest positive and three largest negative gaps are shown, with ties resolved by work ID. Selection uses IDs shared across both archived metadata workbooks. Percentile ranks use average ranks over all 24,767 papers. The cases illustrate count profiles on the scale used in the analysis.

The derived tables include identifiers, publication years, topic numbers, and counts. The inference outputs are summarized at aggregate level. The original full-text files, extracted passages, API credentials, review records, and intermediate inference logs are outside this release.
