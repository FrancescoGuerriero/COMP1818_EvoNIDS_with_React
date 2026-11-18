# COMP-1818 — Results and critical evaluation evidence (November 2026)

This is a **report-writing evidence sheet**, not a replacement for the submitted coursework report. All numbers come from the published UNSW-NB15 run CSVs; the comments below are interpretations to be critically evaluated.

## Experimental design and provenance

- Binary intrusion detection using the official UNSW-NB15 training and testing partitions. Exclude `id` and `attack_cat` from predictors; there are **42 raw candidate features**.
- Four evolutionary algorithms: GA, BPSO, PSO, NSGA-II, evaluated over matched seeds **42, 101, 202, 303, 404**.
- Equal budget of **300 unique candidate evaluations per method/seed**; search population/particles **8**; internal search sizes **20,000 training / 8,000 validation**.
- Compare (1) feature-mask-only Random Forest wrapper optimisation and (2) joint feature mask plus four discrete Random Forest hyperparameters.
- Joint RF hyperparameters: `n_estimators` (40, 80, 120, 200); `max_depth` (None, 12, 24, 36); `min_samples_leaf` (1, 2, 4, 8); `max_features` (sqrt, log2, 0.5, 1.0).
- Optimisation uses validation information obtained from the official *training* partition; the official *testing* partition is evaluated only after selection and refitting. Test results must **not** be used to select a final deployable configuration.
- Result sources:
  - `results/protocol_runs/20261115T183225Z_full/optimisers/{runs,summary}.csv`
  - `results/protocol_runs/20261116T151402Z_full_joint/optimisers/{runs,summary}.csv`
  - `results/protocol_runs/20261116T151402Z_full_joint/baselines/baseline_summary.csv`
  - `results/statistical_analysis/paired_joint_comparison.csv`
- The earlier `20261116T100750Z_full_joint` output is **invalid as a joint comparison**. A CLI-forwarding defect caused it to execute feature-only search despite the command line requesting joint optimisation. The corrected version and a CLI regression test are published.

## Held-out test results (five-seed means)

| Method | Feature-only Macro-F1 ± SD | Joint Macro-F1 ± SD | Joint selected features /42 | Joint reduction | Joint FPR |
|---|---:|---:|---:|---:|---:|
| GA | 0.861168 ± 0.008158 | 0.878881 ± 0.018512 | 9.8 | 76.67% | 0.224362 |
| BPSO | 0.859390 ± 0.010662 | 0.877153 ± 0.012766 | 12.6 | 70.00% | 0.230427 |
| PSO | **0.864282 ± 0.012864** | **0.881373 ± 0.008072** | 11.4 | 72.86% | **0.219708** |
| NSGA-II | 0.839713 ± 0.039023 | 0.843918 ± 0.024652 | **6.0** | **85.71%** | 0.267638 |

The joint PSO run had the highest *mean* test Macro-F1 and lowest mean FPR among the four optimisers. Joint NSGA-II retained the fewest features on average but sacrificed predictive performance. GA yielded a good accuracy/feature-count compromise, with 9.8 joint selected features on average.

### Full-feature baselines

| Classifier | Mean test Macro-F1 ± SD |
|---|---:|
| Dummy | 0.355088 ± 0 |
| Logistic Regression | 0.829171 ± 0 |
| Random Forest | 0.864103 ± 0.000393 |
| XGBoost | 0.866822 ± 0.000794 |

Joint PSO's mean Macro-F1 was **0.014551** above the full-feature XGBoost mean and **0.017270** above the full-feature Random Forest mean. These are descriptive, **not** paired inferential comparisons of model families.

## Paired feature-only versus joint differences

Each difference uses the *same method and seed* for both protocols.

| Method | Mean Δ Macro-F1 | 95% t CI | Paired t p | Exact Wilcoxon p | Seeds improved |
|---|---:|---:|---:|---:|---:|
| GA | +0.017713 | [−0.005207, +0.040633] | 0.098456 | 0.1250 | 4/5 |
| BPSO | +0.017762 | [−0.006911, +0.042435] | 0.116278 | 0.0625 | 5/5 |
| PSO | +0.017091 | [+0.006659, +0.027523] | 0.010427 | 0.0625 | 5/5 |
| NSGA-II | +0.004205 | [−0.056517, +0.064926] | 0.856910 | 0.8125 | 3/5 |

PSO improved for all five matched seeds and has a positive *paired-t* confidence interval. The exact two-sided Wilcoxon result for PSO is p=0.0625, however. With **n=5**, discrete exact p-values, a normality assumption for the t-interval and **four** algorithm comparisons, inferential claims must remain cautious. No universal significance claim is warranted. A Holm correction of the four paired t-test p-values yields approximately 0.0417 for PSO, but the nonparametric test still does not reject at 0.05.

## Critical evaluation: what the evidence does and does not show

1. **Predictive quality versus dimensionality:** Joint optimisation generally improves mean Macro-F1 at the same nominal *unique-candidate* budget. It does not imply identical training compute: candidate RF models can have 40–200 trees and varying depth.
2. **Variation across runs:** PSO's joint Macro-F1 sample SD (0.008072) is lower than GA (0.018512) and BPSO (0.012766). Five seeds give only limited confidence about distributional stability.
3. **False positives matter:** Joint PSO mean FPR (0.219708) is lower than its feature-only mean FPR (0.256319), a difference of **0.036611**, approximately **3.66 percentage points**. This does not prove an operational deployment FPR on a different traffic mix.
4. **Multiobjective compromise:** NSGA-II's mean 6 features (85.71% reduction) illustrates a sparsity/accuracy trade-off. The reported score reflects the implemented validation-only compromise selection, not automatic superiority of every Pareto-optimal solution.
5. **Overfitting/generalisation:** Held-out scores alone do not establish that tuning is immune to validation overfitting. Inspect validation and test gaps, additional data, confidence calibration and attack-category robustness before operational claims.
6. **Scope of the Windows prototype:** The Windows passive socket monitor does not generate every UNSW-NB15 engineered flow field; prototype operation is **not** proof of real-time inference on arbitrary live connections.
7. **Reproducibility:** GitHub-hosted Windows CI verifies installation, Python tests, synthetic CLI joint-mode wiring and exact recomputation of published paired statistics. It **does not** run all 20 × 300 full UNSW-NB15 fits from a clean checkout. The raw datasets are intentionally not committed; large model artefacts are retained locally.
8. **Source provenance:** Each run manifest includes file SHA-256 digests; inspect those alongside the Git revision, because locally modified source at execution time can differ from the recorded commit.
9. **Research integrity:** Avoid choosing the single highest individual *test* score (GA seed 404, Macro-F1 ≈ 0.900010) as the final deployed model solely from test outcomes. Use validation-defined selection and preserve the official test partition for final evaluation.

## Suggested report wording (revise into your own academic voice)

> Under an equal budget of 300 distinct fitness evaluations per algorithm and seed, joint optimisation of the raw-feature mask and Random Forest hyperparameters improved mean held-out Macro-F1 relative to feature-only search for all four evolutionary methods. PSO achieved the highest joint mean Macro-F1 (0.8814 ± 0.0081), selecting 11.4 of 42 features on average (72.9% reduction), compared with 0.8643 ± 0.0129 for feature-only PSO. The mean paired gain was 0.0171 (95% t interval 0.0067–0.0275); however, the exact two-sided Wilcoxon p-value was 0.0625 across only five seeds. Therefore, the gain is best interpreted as encouraging benchmark evidence rather than definitive cross-dataset or operational superiority.

## Reproduction

From `COMP1818_EvoNIDS_Submission`:

```bash
python -m pytest -q research/tests prototype/tests
python tools/compare_joint_statistics.py \
  results/protocol_runs/20261115T183225Z_full/optimisers/runs.csv \
  results/protocol_runs/20261116T151402Z_full_joint/optimisers/runs.csv
```

Also see `docs/REPRODUCTION.md` and the GitHub root `.github/workflows/evonids-windows-reproducibility.yml`.
