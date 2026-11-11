"""Reproduce the Section 6 summaries from the released paper-level counts."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import statsmodels.formula.api as smf
from threadpoolctl import threadpool_limits


HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "papers.csv.gz"
RESULTS = HERE / "results"
SOURCES = ("all", "citation_only", "both", "semantic_archived", "semantic_no_direct_citation")


def correlation_table(papers, window):
    output = []
    for label, frame, suffix, citation_col in (
        ("full_period", papers, "all", "citations_all"),
        ("five_year_window", window, "five_year", "citations_five_year"),
    ):
        for source in SOURCES:
            x = frame[f"{source}_{suffix}"]
            y = frame[citation_col]
            output.append({
                "window_or_count_basis": label, "candidate_source": source,
                "papers": len(frame), "pearson_r": pearsonr(x, y).statistic,
                "spearman_rho": spearmanr(x, y).statistic,
            })
    return pd.DataFrame(output)


def topic_year_correlations(window):
    grouped = window.groupby(["issue_year", "micro_topic"])
    eligible = window[grouped["paper_id"].transform("size").ge(10)].copy()
    columns = ["citations_five_year", *[f"{source}_five_year" for source in SOURCES]]
    logged = np.log1p(eligible[columns])
    groups = [eligible["issue_year"], eligible["micro_topic"]]
    centered = logged - logged.groupby(groups).transform("mean")
    assert len(eligible) == 13_416 and eligible.groupby(["issue_year", "micro_topic"]).ngroups == 495
    return pd.DataFrame([
        {
            "candidate_source": source, "papers": len(eligible), "issue_year_topic_cells": 495,
            "pearson_r_log_counts_centered_within_issue_year_topic": pearsonr(
                centered[f"{source}_five_year"], centered["citations_five_year"]
            ).statistic,
        }
        for source in SOURCES
    ])


def count_models(window):
    data = window.assign(
        log2_semantic=np.log2(1 + window["semantic_no_direct_citation_five_year"]),
        cohort=np.maximum(window["issue_year"] // 10 * 10, 1970),
    )
    raw_predictor = "semantic_no_direct_citation_five_year"
    outcome = "citations_five_year"
    thresholds = data[[raw_predictor, outcome]].quantile(0.99, interpolation="lower")
    trimmed = data[data[raw_predictor].le(thresholds[raw_predictor]) & data[outcome].le(thresholds[outcome])]
    formula = f"{outcome} ~ log2_semantic + C(cohort) + C(micro_topic)"

    def fit(frame, model, sample):
        if model == "NB2":
            result = smf.negativebinomial(formula, data=frame).fit(
                disp=False, method="bfgs", maxiter=350, cov_type="cluster",
                cov_kwds={"groups": frame["micro_topic"]},
            )
            if not result.mle_retvals["converged"]:
                raise RuntimeError(f"NB2 did not converge for {sample}")
            dispersion = result.params["alpha"]
        else:
            result = smf.poisson(formula, data=frame).fit(
                disp=False, cov_type="cluster", cov_kwds={"groups": frame["micro_topic"]},
            )
            if not result.mle_retvals["converged"]:
                raise RuntimeError(f"Poisson did not converge for {sample}")
            dispersion = np.sum(result.resid_pearson**2) / result.df_resid
        coefficient = result.params["log2_semantic"]
        lower, upper = result.conf_int().loc["log2_semantic"]
        assert np.isfinite([coefficient, lower, upper, dispersion]).all()
        return {
            "model": model, "sample": sample, "papers": int(result.nobs),
            "topic_clusters": frame["micro_topic"].nunique(),
            "coefficient": coefficient, "cluster_se": result.bse["log2_semantic"],
            "incidence_rate_ratio": np.exp(coefficient), "ci_95_low": np.exp(lower), "ci_95_high": np.exp(upper),
            "dispersion": dispersion, "dispersion_measure": "NB2 alpha" if model == "NB2" else "Pearson chi-square / residual df",
        }

    with threadpool_limits(limits=2):
        models = [
            fit(data, "NB2", "five_year"),
            fit(trimmed, "NB2", "five_year_trimmed"),
            fit(data, "Poisson", "five_year"),
        ]
    return pd.DataFrame(models), {key: int(value) for key, value in thresholds.items()}


def illustrative_cases(papers):
    fields = [
        "paper_id", "issue_year", "citations_all", "all_all",
        "semantic_no_direct_citation_all",
    ]
    records = papers.loc[:, fields].copy()
    records["outdegree_minus_within_corpus_citations"] = records["all_all"] - records["citations_all"]
    records["outdegree_percentile"] = records["all_all"].rank(pct=True) * 100
    records["within_corpus_citation_percentile"] = records["citations_all"].rank(pct=True) * 100
    records = records[papers["stable_id_for_case_selection"].eq(1)]
    gap = "outdegree_minus_within_corpus_citations"
    sides = []
    for sign, ascending, label in ((-1, True, "more_within_corpus_citations"), (1, False, "more_inferred_edges")):
        side = records[records[gap] * sign > 0].sort_values([gap, "paper_id"], ascending=[ascending, True]).head(3).copy()
        side.insert(0, "profile", label)
        side.insert(1, "rank_within_profile", range(1, 4))
        sides.append(side)
    return pd.concat(sides, ignore_index=True)


def main():
    papers = pd.read_csv(DATA)
    window = papers[papers["in_five_year_sample"].eq(1)].copy()
    assert len(papers) == papers["paper_id"].nunique() == 24_767 and len(window) == 18_170
    assert papers["citations_all"].sum() == 251_714 and papers["all_all"].sum() == 270_134
    assert papers["semantic_no_direct_citation_all"].sum() == 147_728
    assert papers["stable_id_for_case_selection"].sum() == 24_764
    assert window["issue_year"].max() == 2019
    correlations = correlation_table(papers, window)
    models, thresholds = count_models(window)
    correlations.to_csv(RESULTS / "correlations.csv", index=False, float_format="%.12g")
    topic_year_correlations(window).to_csv(RESULTS / "within_issue_year_topic.csv", index=False, float_format="%.12g")
    models.to_csv(RESULTS / "count_models.csv", index=False, float_format="%.12g")
    (RESULTS / "trimming_thresholds.json").write_text(json.dumps(thresholds, indent=2) + "\n", encoding="utf-8")
    illustrative_cases(papers).to_csv(RESULTS / "illustrative_cases.csv", index=False, float_format="%.6g")
    print(models.to_string(index=False))
    print(f"Trimming thresholds: {thresholds}")


if __name__ == "__main__":
    main()
