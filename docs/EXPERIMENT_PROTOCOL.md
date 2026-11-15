# Experiment protocol

## Dataset and target

- Dataset: UNSW-NB15.
- Binary target: `label`.
- Drop `id` and `attack_cat` for binary classification.
- 42 raw predictors remain.
- Preserve the official test partition from all search and tuning decisions.

## Split protocol

For each seed (`42, 101, 202, 303, 404`):

1. Split the official training partition into training and validation data with stratification.
2. Fit preprocessing after raw-column selection.
3. Perform feature search only on training-derived data.
4. Select the candidate subset using validation information only.
5. Recombine the official train/validation rows, retrain the selected model, and evaluate once on the official test partition.

## Baselines

- Dummy Classifier (most frequent class)
- Logistic Regression
- Random Forest
- XGBoost

## Feature-selection methods

- GA
- BPSO
- PSO
- NSGA-II

GA/BPSO/PSO optimise the scalar objective:

`Macro-F1 - 0.05 * (selected_count / 42)`

NSGA-II optimises two separate objectives:

- maximise validation Macro-F1;
- minimise selected-feature ratio.

## Fairness control

The main search comparison uses exactly **300 unique expensive classifier evaluations per method per seed**. Cached duplicate masks consume no additional evaluation budget.

## Metrics

Primary:

- Macro-F1

Secondary:

- balanced accuracy;
- false-positive rate;
- selected feature count;
- feature reduction;
- optimisation runtime;
- inference latency;
- Jaccard feature-selection stability.

## Statistical interpretation

Five matched stochastic seeds are used. Friedman and pairwise Wilcoxon analyses are interpreted conservatively because `n=5` provides limited statistical power. Descriptive differences, seed wins, variance, and effect sizes should be reported alongside p-values.

## Current reproduction implementation / scope boundary

`research/src/run_experiments.py` implements **feature-subset optimisation only**. The Random Forest search and final classifiers use fixed tree counts and other fixed hyperparameters. Thus this reconstructed runner must not be described as joint hyperparameter optimisation. It does not establish that these defaults match the historical canonical local experiments.

A recorded run uses `python tools/run_protocol.py --phase full`. Logs, environment versions, official dataset input hashes, baseline scores and evolutionary scores are stored in a timestamped folder. The historical summary files in `results/` and the coursework PDF are not overwritten. Use `python tools/compare_reproduction.py` to compare a successful rerun descriptively with the historical five-seed means. The React interface reads the most recent **complete, recorded** full run and marks older values as historical when no new full-run result exists.

## Additional, separate experiment: joint feature selection + Random Forest tuning (15 November 2026)

The original five-seed feature-selection experiment remains **feature-only** and is not
retroactively relabelled. A new opt-in `--optimisation joint` mode performs simultaneous
optimisation of the binary raw-feature mask and four Random Forest hyperparameters.
It is a new experiment with a larger search space, not an exact rerun of the historical one.

Each chromosome has **F + 8 binary bits**, with `F=42` for UNSW-NB15. The first 42
bits are the raw-feature mask; the following 8 bits form four two-bit categorical codes:

| Tuned RF hyperparameter | Four allowed values |
|---|---|
| `n_estimators` | 40, 80, 120, 200 |
| `max_depth` | None, 12, 24, 36 |
| `min_samples_leaf` | 1, 2, 4, 8 |
| `max_features` | sqrt, log2, 0.5, 1.0 |

`class_weight=balanced_subsample`, `random_state=seed`, `n_jobs=1`, preprocessing
and the 0.05 feature penalty stay fixed. All chromosome candidates must select at
least one *feature*, not merely one hyperparameter bit. A fitness evaluation
fits the RF *with the candidate hyperparameters* on training-derived data,
then computes Macro-F1 using only its internal validation sample.

GA/BPSO/PSO maximise `Macro-F1_validation - 0.05 × (raw_selected_features / 42)`.
NSGA-II maximises validation Macro-F1 and minimises the *raw feature count*;
its validation-only compromise is the documented ideal-point distance.
A cached candidate is exactly the pair `(feature mask, RF parameters)`; two
identical masks with different RF settings require **two** classifier fits and
consume **two** units of the 300-evaluation budget. The joint search space is
`(2^42-1) × 4^4`. At final refit the selected RF hyperparameters are used again
on the complete official training partition. Test data are used only after
candidate selection.

Run using the recorded protocol:

```bash
python tools/run_protocol.py --phase smoke --optimisation joint
python tools/run_protocol.py --phase full --optimisation joint \
  --train data/raw/UNSW_NB15_training-set.csv \
  --test data/raw/UNSW_NB15_testing-set.csv \
  --seeds 42 101 202 303 404 \
  --budget 300 --population 8 \
  --search-train-size 20000 --search-valid-size 8000
```

Joint-run directories end `_full_joint`; feature-only directories end `_full`.
The baseline run remains fixed-feature and recorded separately. Exported seed-42
joint GA model: `optimisers/models/ga_rf_joint_pipeline.joblib`, with
`ga_rf_joint_hyperparameters.json`. `optimisers/runs.csv` includes the selected
hyperparameter JSON for every method and seed. Avoid describing equal budgets
as equal wall-clock cost: candidate models have different tree counts and
hence different execution times.

## Historical equivalence: required evidence and audit

The historical *summary numbers* are available, but original per-seed configuration
files, authoritative source revisions, dataset hashes and package snapshots are
not all present in the reconstructed release. Exact historical reproduction is
therefore **NOT VERIFIED**, and cannot be manufactured from aggregate metrics.

`tools/audit_historical_equivalence.py` performs a strict comparison when the
original, **independently archived** provenance JSON is supplied: dataset file
hashes, original code hashes, dependency versions, full configuration and
per-seed CSV hash must match. Without that evidence the audit reports
`NOT_VERIFIED` and exits with code 2. This is intentional.

```bash
python tools/audit_historical_equivalence.py \
  --current-run results/protocol_runs/REPLACE_WITH_EXISTING_FULL_RUN
```

Once genuine historical evidence has been recovered from the earlier canonical
project, add `--historical-evidence path/to/original_provenance.json`.
The old five-seed study and new joint HPO study must be reported as separate
experimental protocols; **joint HPO can never be called configuration-identical
to a feature-only historical run**.