# EvoNIDS research implementation

The implemented official-data study compares GA, BPSO, PSO and NSGA-II with a Random Forest wrapper under a common budget of 300 unique candidate evaluations for each seed (`42,101,202,303,404`). **Two different protocols** are recorded: feature-only optimisation and joint selection of a binary feature mask plus four RF hyperparameters. The earlier GA-leading historical aggregate output is a separate study and must not be confused with these official recorded runs.

- [Feature-only 20-run evidence](../results/protocol_runs/20261115T183225Z_full/optimisers/runs.csv)
- [Corrected joint 20-run evidence](../results/protocol_runs/20261116T151402Z_full_joint/optimisers/runs.csv)
- [Paired five-seed analysis](../results/statistical_analysis/paired_joint_comparison.csv)
- [Full indexed results, including invalid/historical/synthetic data](../results/README.md)
- [Experiment protocol, budget semantics and scientific limitations](../docs/EXPERIMENT_PROTOCOL.md)

## Code map

- `src/run_experiments.py`: runs scalar GA/BPSO/PSO, Pareto NSGA-II and optional joint RF tuning
- `src/evolution/budgeted.py`: candidate evaluation/caching and evolutionary search operators
- `src/run_baselines.py`: most-frequent Dummy, logistic regression, RF and XGBoost
- `tests/`: fitness accounting, modes, experiment protocol and joint-option forwarding regression

From the package root:

```bash
python -m pytest -q research/tests prototype/tests
python tools/check_repository_evidence.py
python -m research.src.run_experiments --synthetic-smoke --mode quick --optimisation joint --methods GA --seeds 42 --budget 2 --population 4 --output-dir results/ci_joint_smoke_local
```

**Important:** that last command runs only a *synthetic software smoke test*. A full independent UNSW-NB15 rerun requires the official dataset and substantial CPU time; see [REPRODUCTION.md](../docs/REPRODUCTION.md). An exact reproduction claim for an earlier non-archived source configuration requires independent historical evidence, not merely similar summary statistics.
