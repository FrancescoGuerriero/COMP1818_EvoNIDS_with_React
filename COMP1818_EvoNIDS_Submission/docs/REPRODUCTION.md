# Reproduction guide

## 1. Clean clone / unzip

Work from a new directory that does not contain an existing virtual environment.

## 2. Create Python 3.12 environment

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. Smoke verification without the research dataset

```bash
python tools/verify_submission.py
python -m pytest
python -m prototype.train_demo_model --output models/demo_pipeline.joblib --csv-output results/demo_rows.csv
python -m prototype.windows_ids replay --csv results/demo_rows.csv --model models/demo_pipeline.joblib --output results/demo_scored.csv
python -m prototype.windows_ids monitor --iterations 1
```

The synthetic model verifies prototype wiring only and must not be reported as an experiment.

## 4. Obtain UNSW-NB15

Download the dataset from the official UNSW source:

https://research.unsw.edu.au/projects/unsw-nb15-dataset

Place:

```text
data/raw/UNSW_NB15_training-set.csv
data/raw/UNSW_NB15_testing-set.csv
```

## 5. Full reproduction

Run the experiment commands documented in this directory's `README.md`. The `research/` source and `tools/` runner are already included in this GitHub repository. The full UNSW-NB15 experiments require the two separately obtained official CSV files. A dataset-free clean Windows test is automated under `.github/workflows/evonids-windows-reproducibility.yml` in the GitHub repository root.

## Clean-room release test status

The generated submission-support package is tested in a fresh virtual environment for:

- package structure verification;
- pytest prototype tests;
- synthetic model creation;
- CSV replay scoring;
- passive connection-monitor execution.

The full 5-seed, 300-evaluation UNSW-NB15 searches are recorded in `results/protocol_runs/20261115T183225Z_full/` (feature-only) and `results/protocol_runs/20261116T151402Z_full_joint/` (corrected joint). The invalid 16 November 10:07 UTC joint-labelled run accidentally selected feature-only mode and must not support joint-HPO claims. The dataset-free Windows CI checks code/tests, synthetic joint-mode wiring and recomputation of paired statistics from the published CSVs; it does **not** independently rerun all UNSW-NB15 optimisations. Large trained-model files are excluded from Git.
