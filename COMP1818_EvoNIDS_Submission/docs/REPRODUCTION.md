# EvoNIDS reproducibility and verification

**Run all commands below from `COMP1818_EvoNIDS_Submission/` unless a command explicitly changes directory.** See [root package README](../README.md), [experiment index](../results/README.md), [recorded protocol](EXPERIMENT_PROTOCOL.md) and [Git/submission checklist](GIT_AND_SUBMISSION.md).

## Clean Python and JavaScript environments

Python 3.12 (Windows Git Bash):

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

Windows PowerShell: `py -3.12 -m venv .venv`; `.\.venv\Scripts\Activate.ps1`; `python -m pip install -r requirements.txt`. For React use Node.js 22, then `cd frontend && npm ci && npm run build`.

## Dataset-free quality gates (fast)

```bash
python -m pytest -q research/tests prototype/tests
python tools/check_repository_evidence.py
python -m prototype.train_demo_model --output models/demo_pipeline.joblib --csv-output results/demo_rows.csv
python -m tools.check_saved_model_replay --model models/demo_pipeline.joblib --csv results/demo_rows.csv --rows 20
python -m research.src.run_experiments --synthetic-smoke --mode quick --optimisation joint --methods GA --seeds 42 --budget 2 --population 4 --output-dir results/ci_joint_smoke_local
```

The last three commands exercise **synthetic data and a demonstration model only**. They do not establish the numerical claims made for UNSW-NB15. The [GitHub Windows workflow](https://github.com/FrancescoGuerriero/COMP1818_EvoNIDS_with_React/actions/workflows/evonids-windows-reproducibility.yml) automates these gates, statistical consistency checks and the React production build.

Use `python tools/verify_submission.py` only in a **clean release checkout**, not a development working tree containing a virtual environment or `node_modules`: that verifier deliberately flags machine-specific directories.

## Independently verify published results without training

```bash
python tools/compare_joint_statistics.py \
  results/protocol_runs/20261115T183225Z_full/optimisers/runs.csv \
  results/protocol_runs/20261116T151402Z_full_joint/optimisers/runs.csv \
  --output results/paired_verification.csv
python tools/check_repository_evidence.py
```

`paired_verification.csv` is a verification copy. The canonical paired analysis is `results/statistical_analysis/paired_joint_comparison.csv`. This does **not** count as an independent refit of the trained classifier.

## Full official dataset-based replication (expensive, optional)

Download official training and testing partitions from https://research.unsw.edu.au/projects/unsw-nb15-dataset and place them in:

```text
data/raw/UNSW_NB15_training-set.csv
data/raw/UNSW_NB15_testing-set.csv
```

The recorded protocol with five seeds and a 300-evaluation budget per method is:

```bash
python tools/run_protocol.py --phase full --optimisation features \
  --train data/raw/UNSW_NB15_training-set.csv \
  --test data/raw/UNSW_NB15_testing-set.csv \
  --seeds 42 101 202 303 404 --budget 300 --population 8 \
  --search-train-size 20000 --search-valid-size 8000

python tools/run_protocol.py --phase full --optimisation joint \
  --train data/raw/UNSW_NB15_training-set.csv \
  --test data/raw/UNSW_NB15_testing-set.csv \
  --seeds 42 101 202 303 404 --budget 300 --population 8 \
  --search-train-size 20000 --search-valid-size 8000
```

Each call writes a new immutable timestamped `results/protocol_runs/` folder, recording SHA-256 input/source digests, Python version, fitted methods, per-seed results and command logs. Exact historical equivalence to an older unarchived study is **not verified**. The invalid run `results/protocol_runs/20261116T100750Z_full_joint` suffered a mode-forwarding bug and must be excluded from the joint analysis. Published full-result folders are `results/protocol_runs/20261115T183225Z_full` and `results/protocol_runs/20261116T151402Z_full_joint`.

## Recompile the current LaTeX report

```bash
cd report/latex/COMP1818_EvoNIDS_LaTeX
python -m pip install matplotlib
python figures/generate_figures.py
pdflatex -interaction=nonstopmode -halt-on-error main.tex
biber main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

This rebuilds the five-page report from the bundled CSV snapshots and `main.tex`. It is not a full refit of the official evolutionary optimisers. A complete LaTeX distribution is needed on Windows. The project has another **duplicate extracted report folder**; the path above is the canonical report source.

## Original full-data model boundary

The source version controls seed-42 GA joint feature/hyperparameter metadata but **not** the original large benchmark-trained `.joblib`. Use [real model replay acceptance](REAL_MODEL_REPLAY_ACCEPTANCE.md) only when the trusted local pipeline and official CSV are available. The Windows telemetry screen is passive and does not provide the engineered UNSW-NB15 flow features necessary for live benchmark inference.
