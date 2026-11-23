"""Fail fast if published EvoNIDS research evidence is missing or internally inconsistent.

Standard-library only; no training, dataset access or model unpickling.
Run from anywhere: python tools/check_repository_evidence.py
"""
from __future__ import annotations
import csv
import json
from pathlib import Path
from statistics import mean

ROOT=Path(__file__).resolve().parents[1]
FEATURE="results/protocol_runs/20261115T183225Z_full/"
JOINT="results/protocol_runs/20261116T151402Z_full_joint/"
INVALID="results/protocol_runs/20261116T100750Z_full_joint/"
EXPECTED_METHODS={"GA","BPSO","PSO","NSGA-II"}
EXPECTED_SEEDS={42,101,202,303,404}
NEEDED=[
"README.md","requirements.txt","docs/EXPERIMENT_PROTOCOL.md",
"docs/REPRODUCTION.md","docs/ONLINE_EXPERIMENTS.md","docs/GIT_AND_SUBMISSION.md",
"results/README.md","report/latex/COMP1818_EvoNIDS_LaTeX/main.tex",
"report/latex/COMP1818_EvoNIDS_LaTeX/ref.bib",
"report/latex/COMP1818_EvoNIDS_LaTeX/figures/generate_figures.py",
"results/statistical_analysis/paired_joint_comparison.csv",
"results/paired_verification.csv",
"results/protocol_runs/20261116T100750Z_full_joint/optimisers/runs.csv",
]
for family in (FEATURE, JOINT):
    NEEDED += [family + name for name in (
        "optimisers/runs.csv","optimisers/summary.csv","optimisers/run_config.json",
        "manifest.json","baselines/baseline_summary.csv")]
NEEDED += [INVALID+"optimisers/run_config.json", "results/final_summary.csv"]


def read_csv(path: str) -> list[dict[str,str]]:
    with (ROOT/path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def verify(family: str, mode: str) -> dict[str,float]:
    runs=read_csv(family+"optimisers/runs.csv")
    if len(runs)!=20:
        raise AssertionError(f"{mode}: expected 20 records, got {len(runs)}")
    pairs={(row["method"],int(row["seed"])) for row in runs}
    if len(pairs)!=20 or pairs != {(m,s) for m in EXPECTED_METHODS for s in EXPECTED_SEEDS}:
        raise AssertionError(f"{mode}: duplicated or missing method/seed combination")
    for row in runs:
        if row["optimisation"]!=mode or int(row["fitness_evaluations"])!=300:
            raise AssertionError(f"{mode}: incorrect optimisation mode/evaluation budget")
        hp=json.loads(row["rf_hyperparameters"])
        if mode=="joint" and not all(k in hp for k in ("max_depth","max_features","min_samples_leaf","n_estimators")):
            raise AssertionError("Joint row missing RF hyperparameters")
        if mode=="features" and hp:
            raise AssertionError("Feature-only row unexpectedly contains RF hyperparameters")
    summaries={r["method"]:r for r in read_csv(family+"optimisers/summary.csv")}
    if set(summaries)!=EXPECTED_METHODS:
        raise AssertionError(f"{mode}: missing summary methods")
    for method in EXPECTED_METHODS:
        records=[r for r in runs if r["method"]==method]
        expected=mean(float(r["macro_f1"]) for r in records)
        actual=float(summaries[method]["macro_f1_mean"])
        if abs(expected-actual)>1e-10:
            raise AssertionError(f"{mode} {method}: mean differs from raw seed-level records")
    config=json.loads((ROOT/family/"optimisers/run_config.json").read_text(encoding="utf-8"))
    if config["optimisation"]!=mode or set(config["seed_list"])!=EXPECTED_SEEDS:
        raise AssertionError(f"{mode}: configuration is inconsistent")
    manifest=json.loads((ROOT/family/"manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status")!="PASS":
        raise AssertionError(f"{mode}: run manifest is not PASS")
    return {m:float(summaries[m]["macro_f1_mean"]) for m in EXPECTED_METHODS}


def main() -> None:
    missing=[p for p in NEEDED if not (ROOT/p).is_file()]
    if missing:
        raise SystemExit("FAIL: missing evidence files:\n" + "\n".join(missing))
    original=verify(FEATURE,"features")
    corrected=verify(JOINT,"joint")
    invalid=json.loads((ROOT/INVALID/"optimisers/run_config.json").read_text(encoding="utf-8"))
    invalid_rows=read_csv(INVALID+"optimisers/runs.csv")
    if invalid["optimisation"]!="joint" or not invalid_rows:
        raise AssertionError("Invalid historical run must retain joint request metadata and recorded rows")
    if not all(row["optimisation"]=="features" and not json.loads(row["rf_hyperparameters"]) for row in invalid_rows):
        raise AssertionError("Mislabelled joint run must contain actual feature-only observations")
    paired={row["method"]:row for row in read_csv("results/statistical_analysis/paired_joint_comparison.csv")}
    duplicate={row["method"]:row for row in read_csv("results/paired_verification.csv")}
    if set(paired)!=EXPECTED_METHODS or set(duplicate)!=EXPECTED_METHODS:
        raise AssertionError("Paired results have missing methods")
    for m in EXPECTED_METHODS:
        row=paired[m]
        if int(row["seeds"])!=5 or abs(float(row["feature_only_mean"])-original[m])>1e-10 or abs(float(row["joint_mean"])-corrected[m])>1e-10:
            raise AssertionError(f"{m}: paired results do not agree with experiment summaries")
        for field in row:
            if field=="method":
                continue
            if abs(float(row[field])-float(duplicate[m][field]))>1e-10:
                raise AssertionError(f"{m}: independent paired verification differs: {field}")
    if max(corrected, key=corrected.get)!="PSO":
        raise AssertionError("Primary reporting claim that PSO leads no longer holds")
    print("PASS: 40 official optimiser records, budgets, modes, means, original/invalid provenance and paired comparisons")
    print("PASS: canonical LaTeX source, docs and report evidence paths exist")


if __name__=="__main__":
    main()
