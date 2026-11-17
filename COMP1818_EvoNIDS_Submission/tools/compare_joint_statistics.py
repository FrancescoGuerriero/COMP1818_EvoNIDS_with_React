"""Paired feature-only versus joint optimisation statistics for five matched seeds.

Usage from COMP1818_EvoNIDS_Submission:
 python tools/compare_joint_statistics.py results/protocol_runs/20261115T183225Z_full/optimisers/runs.csv results/protocol_runs/20261116T151402Z_full_joint/optimisers/runs.csv
Outputs a CSV with paired differences, 95% t confidence intervals, two-sided paired t tests, and exact Wilcoxon signed-rank p-values.
Small-n and multiple-comparison caution: treat findings as exploratory.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats


def compare(features_csv, joint_csv):
    a = pd.read_csv(features_csv)
    b = pd.read_csv(joint_csv)
    if not (a["optimisation"] == "features").all():
        raise ValueError("Feature-only CSV contains rows with unexpected optimisation mode")
    if not (b["optimisation"] == "joint").all():
        raise ValueError("Joint CSV contains rows with unexpected optimisation mode")
    if b["rf_hyperparameters"].map(lambda x: pd.notna(x) and x.strip() not in ("", "{}")).eq(False).any():
        raise ValueError("Joint CSV has missing hyperparameters")
    key = ["method", "seed"]
    if a.duplicated(key).any() or b.duplicated(key).any():
        raise ValueError("Duplicate method/seed pair")
    if set(map(tuple, a[key].to_numpy())) != set(map(tuple, b[key].to_numpy())):
        raise ValueError("Method/seed pairs differ between runs")
    merged = a.merge(b, on=key, suffixes=("_features", "_joint"), validate="one_to_one")
    summary = []
    for method, group in merged.groupby("method", sort=True):
        diff = group["macro_f1_joint"].to_numpy(dtype=float) - group["macro_f1_features"].to_numpy(dtype=float)
        n = len(diff)
        sd = float(np.std(diff, ddof=1)) if n > 1 else np.nan
        mean = float(np.mean(diff))
        half_width = float(stats.t.ppf(0.975, df=n-1) * sd / np.sqrt(n)) if n > 1 else np.nan
        t_p = float(stats.ttest_rel(group["macro_f1_joint"], group["macro_f1_features"]).pvalue) if n > 1 else np.nan
        # zero_method=wilcox drops zeros, with scipy exact p-values for n=5 and no ties
        w_p = float(stats.wilcoxon(diff, alternative="two-sided", method="exact").pvalue) if np.any(diff) else 1.0
        summary.append(dict(method=method, seeds=n,
            feature_only_mean=float(group["macro_f1_features"].mean()),
            joint_mean=float(group["macro_f1_joint"].mean()),
            mean_paired_gain=mean, paired_sd=sd,
            ci95_lower=mean-half_width, ci95_upper=mean+half_width,
            paired_t_p=t_p, wilcoxon_p=w_p,
            improved_seeds=int((diff>0).sum()), declined_seeds=int((diff<0).sum())))
    return pd.DataFrame(summary), merged


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("features_csv", type=Path)
    p.add_argument("joint_csv", type=Path)
    p.add_argument("--output", type=Path, default=Path("results/statistical_analysis/paired_joint_comparison.csv"))
    args = p.parse_args()
    summary, _ = compare(args.features_csv, args.joint_csv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output, index=False)
    print(summary.to_string(index=False, float_format=lambda v: f"{v:.6f}"))
    print("Saved:", args.output)


if __name__ == "__main__":
    main()
