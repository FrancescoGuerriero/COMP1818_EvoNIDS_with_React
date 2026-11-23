# EvoNIDS experiment results — authoritative index

This directory contains multiple experimental generations. **Do not combine incompatible results in the same comparison, overwrite recorded run files, or describe synthetic smoke results as official UNSW-NB15 scores.**

## Corrected official experiment (primary evidence for joint HPO)

| Method | Feature-only mean test Macro-F1 | Corrected joint mean test Macro-F1 | Joint mean features / 42 | Joint reduction |
|---|---:|---:|---:|---:|
| GA | 0.861168 | 0.878881 | 9.8 | 76.67% |
| BPSO | 0.859390 | 0.877153 | 12.6 | 70.00% |
| PSO | 0.864282 | 0.881373 | 11.4 | 72.86% |
| NSGA-II | 0.839713 | 0.843918 | 6.0 | 85.71% |

The numbers are five-seed **held-out test** means rounded from the committed `summary.csv` values. The feature-only and joint runs use exactly the same seeds (`42, 101, 202, 303, 404`) and a 300-unique-candidate budget per method per seed. The joint RF hyperparameters vary by candidate, so equal evaluation count does not guarantee equal wall-clock cost.

| Experiment family | Exact folder | Role |
|---|---|---|
| Feature-only official run | [`results/protocol_runs/20261115T183225Z_full`](results/protocol_runs/20261115T183225Z_full/optimisers/runs.csv) | Valid, 20 algorithm/seed records; feature masks only |
| Corrected joint official run | [`results/protocol_runs/20261116T151402Z_full_joint`](results/protocol_runs/20261116T151402Z_full_joint/optimisers/runs.csv) | Valid, 20 records; mask plus four RF hyperparameters |
| Incorrectly labelled 'joint' | [`results/protocol_runs/20261116T100750Z_full_joint`](results/protocol_runs/20261116T100750Z_full_joint/optimisers/run_config.json) | **Excluded** from joint-HPO analysis; underlying mode was `features` |
| Earlier historical study | [`final_summary.csv`](final_summary.csv) | Distinct older GA-leading experiment, not corrected 2026 joint study |
| Synthetic smoke runs | [`smoke/`](smoke/run_config.json), [`joint_fix_smoke/`](joint_fix_smoke/run_config.json), [`protocol_runs/20261115T183159Z_smoke_joint/`](protocol_runs/20261115T183159Z_smoke_joint/manifest.json) | Software integration only, not benchmark performance |

## Primary experiment files

| Evidence | Source |
|---|---|
| Corrected joint **all per-seed observations** | [joint `optimisers/runs.csv`](results/protocol_runs/20261116T151402Z_full_joint/optimisers/runs.csv) |
| Joint five-seed means, SD, FPR and feature reduction | [joint `optimisers/summary.csv`](results/protocol_runs/20261116T151402Z_full_joint/optimisers/summary.csv) |
| Joint RF hyperparameter options, seeds and budget | [joint `optimisers/run_config.json`](results/protocol_runs/20261116T151402Z_full_joint/optimisers/run_config.json) |
| Joint provenance, dataset SHA-256, dependency versions, source hashes, status | [joint `manifest.json`](results/protocol_runs/20261116T151402Z_full_joint/manifest.json) |
| Joint full-feature baseline observations | [joint `baselines/baseline_runs.csv`](results/protocol_runs/20261116T151402Z_full_joint/baselines/baseline_runs.csv) |
| Joint full-feature baseline summary | [joint `baselines/baseline_summary.csv`](results/protocol_runs/20261116T151402Z_full_joint/baselines/baseline_summary.csv) |
| Feature-only per-seed observations | [feature-only `optimisers/runs.csv`](results/protocol_runs/20261115T183225Z_full/optimisers/runs.csv) |
| Feature-only five-seed summary | [feature-only `optimisers/summary.csv`](results/protocol_runs/20261115T183225Z_full/optimisers/summary.csv) |
| Feature-only provenance and settings | [feature-only `manifest.json`](results/protocol_runs/20261115T183225Z_full/manifest.json), [run config](results/protocol_runs/20261115T183225Z_full/optimisers/run_config.json) |
| Paired tests and confidence intervals | [`statistical_analysis/paired_joint_comparison.csv`](statistical_analysis/paired_joint_comparison.csv) |
| Independently produced paired verification | [`paired_verification.csv`](paired_verification.csv) |

Each official optimiser run also contains five [NSGA-II Pareto archive CSVs](results/protocol_runs/20261116T151402Z_full_joint/optimisers/pareto_seed_42.csv) (one for each seed) and seed-42 GA feature and RF hyperparameter JSON in `optimisers/models/`. The **original trained GA joint `.joblib` is not committed**. Synthetic smoke folders may contain small `.joblib` files, which must never be presented as the official trained benchmark.

## Historical summaries retained separately

The following files document the earlier local study; they **must not be relabelled as corrected joint results**:

- [`final_summary.csv`](final_summary.csv): earlier full-feature baselines and GA/BPSO/PSO/NSGA-II aggregate scores; GA 0.865394, XGBoost 0.870417.
- [`budget_effect.csv`](budget_effect.csv): earlier 24-to-300-evaluation sensitivity.
- [`generalisation_gap.csv`](generalisation_gap.csv): earlier internal-validation/test differences.
- [`feature_consensus.csv`](feature_consensus.csv): earlier feature-selection frequency analysis.

The earlier study lacks the independently archived provenance needed to declare exact reproduction of those historical scores. The new corrected experiment has its own provenance and should be cited on its own terms.

## Statistics and scientific limitations

Joint PSO has the highest five-seed mean held-out Macro-F1 (0.881373; SD 0.008072) with 11.4/42 mean features and 72.86% reduction. Feature-only PSO mean is 0.864282. The matched gain is +0.017091; paired-t p = 0.010427 but exact two-sided Wilcoxon p = 0.062500. Four methods and n=5 require conservative inference; **do not equate the lowest mean with statistical certainty**.

No external deployment, live NIDS accuracy, lower latency or memory saving is established solely by fewer raw columns or reduced FPR in benchmark evaluation. The published HTML/SVG viewer is a presentation of recorded evidence.

## Verify without expensive retraining

From `COMP1818_EvoNIDS_Submission/`:

```bash
python tools/check_repository_evidence.py
python tools/compare_joint_statistics.py \
  results/protocol_runs/20261115T183225Z_full/optimisers/runs.csv \
  results/protocol_runs/20261116T151402Z_full_joint/optimisers/runs.csv \
  --output results/paired_verification.csv
```

The first command audits expected files, modes, 40 seed/method records and CSV summary integrity using standard-library Python. The second independently reproduces the published paired statistics (SciPy required). [Full reproduction and environment instructions](../docs/REPRODUCTION.md).
