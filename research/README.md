# Research implementation

- `src/run_experiments.py`: four feature-selection methods, optionally joint with Random Forest hyperparameters.
- `src/evolution/budgeted.py`: evaluation-budget accounting, candidate encoding and search operators.
- `src/run_baselines.py`: Dummy, Logistic Regression, full-feature Random Forest and XGBoost.
- `tests/`: unit, budget, joint optimisation and protocol checks.

Start at the repository root:

```bash
python -m pytest -q research/tests prototype/tests
python tools/run_protocol.py --phase smoke --optimisation joint
```

Run official UNSW-NB15 experiments only after downloading the two CSVs per `data/README.md`.

An exact historical-source-equivalence claim requires the original implementation and configuration; similarity of summary metrics is not proof of equivalence.