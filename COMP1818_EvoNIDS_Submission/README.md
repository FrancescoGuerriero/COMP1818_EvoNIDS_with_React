Multi-Objective Evolutionary Feature Selection for Efficient Network Intrusion Detection

COMP1818 Artificial Intelligence Applications coursework implementation and reproducibility package.

Project objective

This project evaluates Genetic Algorithm (GA), Binary Particle Swarm Optimisation (BPSO), Particle Swarm Optimisation (PSO), and NSGA-II feature selection for binary network intrusion detection on UNSW-NB15. The primary objective is to reduce raw network-traffic dimensionality while maintaining predictive performance.

The final controlled comparison uses five seeds (`42, 101, 202, 303, 404`) and an equal budget of 300 unique expensive fitness evaluations per optimiser per seed. Random Forest is used as the wrapper classifier. Full-feature Dummy, Logistic Regression, Random Forest, and XGBoost baselines are also evaluated.

Historical study summary (earlier local implementation; not the corrected November 2026 joint experiment)

GA + Random Forest was reported to achieve the strongest feature-selection trade-off in the earlier study:

- Macro-F1: **0.865394 +/- 0.003952**
- Mean selected raw predictors: **10.2 / 42**
- Mean feature reduction: **75.71%**
- False-positive rate: **0.254795**
- Full-feature RF Macro-F1: **0.864225 +/- 0.000689**
- Full-feature XGBoost Macro-F1: **0.870417 +/- 0.000866** (highest absolute predictive result)

These values belong to the earlier study and must not be conflated with the November 2026 reproduced feature-only or corrected joint runs. The later equal-budget comparison and results are listed below.

Repository layout

```text
.
|-- README.md
|-- requirements.txt
|-- pyproject.toml
|-- .gitignore
|-- report/
|   |-- COMP1818_EvoNIDS_Report.docx
|   `-- COMP1818_EvoNIDS_Report.pdf
|-- docs/
|   |-- EXPERIMENT_PROTOCOL.md
|   `-- REPRODUCTION.md
|-- research/
|   `-- README.md
|-- frontend/
|   |-- src/
|   |-- package.json
|   `-- README.md
|-- prototype/
|   |-- windows_ids.py
|   |-- model_io.py
|   |-- telemetry.py
|   |-- replay.py
|   |-- train_demo_model.py
|   |-- config/selected_features.json
|   `-- tests/
|-- results/
|   |-- final_summary.csv
|   |-- budget_effect.csv
|   |-- generalisation_gap.csv
|   `-- feature_consensus.csv
`-- tools/
    |-- package_existing_project.py
    `-- verify_submission.py
```

Dataset

Dataset: UNSW-NB15

Official source: https://research.unsw.edu.au/projects/unsw-nb15-dataset

Expected local files for the full coursework experiments:

```text
data/raw/UNSW_NB15_training-set.csv
data/raw/UNSW_NB15_testing-set.csv
```

Binary target: `label`.

The identifier `id` and multiclass attack category `attack_cat` are excluded from the binary predictor set, leaving 42 raw predictors.

The raw dataset is intentionally not bundled in this repository package. Download it from the official source and place the two CSV files under `data/raw/`.

Python environment

The coursework experiments were developed with Python 3.12.

Windows / Git Bash

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Tests

```bash
python -m pytest
```

For the curated submission package, verify the expected release structure with:

```bash
python tools/verify_submission.py
```

Full experiment commands

Run from this nested `COMP1818_EvoNIDS_Submission` directory. The research implementation is now checked into the repository. Both commands use the same five seeds and equal 300-unique-candidate budget per method/seed; they write new timestamped result directories and do not overwrite published results.

Feature-only optimisation and full-feature baselines:

```bash
python tools/run_protocol.py --phase full --optimisation features \\
  --train data/raw/UNSW_NB15_training-set.csv \\
  --test data/raw/UNSW_NB15_testing-set.csv \\
  --seeds 42 101 202 303 404 --budget 300 --population 8 \\
  --search-train-size 20000 --search-valid-size 8000
```

Joint feature selection and Random Forest hyperparameter optimisation:

```bash
python tools/run_protocol.py --phase full --optimisation joint \\
  --train data/raw/UNSW_NB15_training-set.csv \\
  --test data/raw/UNSW_NB15_testing-set.csv \\
  --seeds 42 101 202 303 404 --budget 300 --population 8 \\
  --search-train-size 20000 --search-valid-size 8000
```

Synthetic-only verification without UNSW-NB15:

```bash
python -m pytest -q research/tests prototype/tests
python tools/run_protocol.py --phase smoke --optimisation joint
```

Reproduce the published five-seed paired statistics without re-training classifiers:

```bash
python tools/compare_joint_statistics.py \\
  results/protocol_runs/20261115T183225Z_full/optimisers/runs.csv \\
  results/protocol_runs/20261116T151402Z_full_joint/optimisers/runs.csv
```

The corrected joint experiment is recorded under `results/protocol_runs/20261116T151402Z_full_joint/`. The earlier `20261116T100750Z_full_joint/` mistakenly ran feature-only optimisation despite being requested as joint; **do not use it as evidence of RF hyperparameter optimisation**.

### Corrected experiment means (test Macro-F1)

| Method | Feature-only | Joint RF-HPO | Joint mean features |
|---|---:|---:|---:|
| GA | 0.861168 | 0.878881 | 9.8 |
| BPSO | 0.859390 | 0.877153 | 12.6 |
| PSO | 0.864282 | **0.881373** | 11.4 |
| NSGA-II | 0.839713 | 0.843918 | 6.0 |

PSO joint mode has the highest *mean* Macro-F1 across the five matched seeds. With n=5, paired t/Wilcoxon statistics are exploratory, not definitive. See `results/statistical_analysis/paired_joint_comparison.csv` and `docs/EXPERIMENT_PROTOCOL.md`.

React frontend

The `frontend/` directory contains a React + TypeScript + Vite control-centre UI for the Windows IDS prototype. It includes:

- research overview and final model metrics;
- passive Windows connection-monitor view;
- CSV/model replay workflow;
- GA/BPSO/PSO/NSGA-II results view.

Start the local Python API first:

```bash
python -m uvicorn prototype.api:app --host 127.0.0.1 --port 8000 --reload
```

Then in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. The Live Connections page polls the passive Windows telemetry API and Model Replay sends CSV content to the saved Python classifier. If the API is unavailable, the connection table falls back to rows that are explicitly labelled as demonstration data. Build the production bundle with `npm run build`.

Windows IDS prototype

The `prototype/` directory provides a passive, defensive Windows IDS prototype with two roles:

1. `replay`: run a trained scikit-learn pipeline against UNSW-NB15-compatible CSV rows.
2. `monitor`: display passive local TCP/UDP connection telemetry obtained through `psutil` without blocking traffic or changing firewall rules.

The live Windows telemetry is deliberately separated from the coursework benchmark model because Windows socket telemetry does not natively provide all UNSW-NB15 engineered features. It is therefore a prototype integration layer, not a claim that the benchmark model can classify arbitrary live sockets without a compatible flow-feature extractor.

Run:

```bash
python -m prototype.windows_ids --help
python -m prototype.windows_ids monitor --interval 2
python -m prototype.windows_ids replay --csv path/to/unsw_compatible.csv --model models/ga_rf_pipeline.joblib
```

A synthetic demonstration model can be created only for smoke-testing the prototype wiring:

```bash
python -m prototype.train_demo_model --output models/demo_pipeline.joblib
```

Synthetic demo results are not coursework benchmark results.

Reproducible submission build

From the canonical local project root, use:

```bash
python tools/package_existing_project.py --source . --destination ../COMP1818_EvoNIDS_Submission
```

The packager excludes machine-specific and unnecessary material such as `.venv`, caches, IDE metadata, Node modules, temporary logs, build output, and Python bytecode while preserving research source, tests, results, report material, prototype code, and reproducibility documentation.

See `docs/REPRODUCTION.md` for a clean-room verification procedure.

Coursework delivery

The formal Moodle submission is the report PDF. The report should contain:

- a clearly labelled GitHub implementation link;
- the official UNSW-NB15 dataset link;
- enough detail for the teaching team to map the report claims to code and result files.

Do not upload the code archive to Moodle unless the teaching team explicitly requests it; keep the implementation available through the GitHub link used in the report.

Academic integrity and AI use

The report includes the required 60-100 word reflection on generative-AI use. Experimental outputs are generated by the implemented Python pipeline; AI assistance is described as development, explanation, review, and writing support rather than as a source of experimental measurements.
