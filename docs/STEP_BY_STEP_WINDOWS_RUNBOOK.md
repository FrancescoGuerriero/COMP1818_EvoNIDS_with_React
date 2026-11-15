# EvoNIDS: step-by-step execution and evidence recording (Windows 11 / Git Bash)

**Scope:** This runbook is based on `docs/EXPERIMENT_PROTOCOL.md` and the current runnable research implementation. The new runner is a reproduction attempt, **not** evidence that the original published five-seed results have been replicated. Run from the **project directory containing `requirements.txt`, `frontend/` and `prototype/`**.

## Stage 0 — Confirm you are in the correct repository

```bash
cd COMP1818_EvoNIDS_with_React  # after a fresh GitHub clone
pwd
ls README.md requirements.txt research/src/run_experiments.py prototype/windows_ids.py frontend/package.json
git status --short
```

If `research/src/run_experiments.py` does not exist, the research completion patch has not been merged into this folder. Extract the patch with `unzip -o` from the repository *submission subfolder* (not its parent). Do not delete existing original experiment scripts.

## Stage 1 — Python installation

```bash
py -3.12 --version
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
which python
python -c "import numpy,pandas,sklearn,xgboost,fastapi,psutil;print('Python requirements OK')"
```

Use `python -m venv .venv` if `py -3.12` is unavailable and `python --version` is compatible. `.venv/` is untracked and must never be committed. Reuse it for subsequent terminals; do not recreate it each run.

## Stage 2 — Validate official UNSW-NB15 files

Both input files must exist before running the full experiment:

```bash
ls -lh data/raw/UNSW_NB15_training-set.csv data/raw/UNSW_NB15_testing-set.csv
python - <<'PY'
import pandas as pd
for name in ('training','testing'):
    p=f'data/raw/UNSW_NB15_{name}-set.csv'
    df=pd.read_csv(p)
    print(name, 'rows=',len(df),'columns=',len(df.columns),'target_counts=',df['label'].value_counts().to_dict())
    assert {'label','id','attack_cat'}.issubset(df.columns)
    assert len([c for c in df if c not in ('label','id','attack_cat')])==42
PY
```

Expected rows: 175,341 train, 82,332 test. The official split is never re-randomised across training and testing; only official training rows are internally split for optimisation.

## Stage 3 — Test every Python component before expensive training

```bash
python -m pytest -q research/tests prototype/tests
python tools/run_protocol.py --phase smoke --monitor
```

This runs algorithm unit tests, all 4 optimisers with a **synthetic-only** short budget, trains a synthetic demonstration classifier, replays the demo CSV and takes one passive Windows connection snapshot. It records log files and a `manifest.json` in a new timestamped `results/protocol_runs/` directory. **Do not quote smoke-test classification metrics as UNSW-NB15 results.**

## Stage 4 — Execute the official research protocol and record fresh results

```bash
python tools/run_protocol.py --phase full \
  --train data/raw/UNSW_NB15_training-set.csv \
  --test data/raw/UNSW_NB15_testing-set.csv \
  --seeds 42 101 202 303 404 \
  --budget 300 \
  --population 8 \
  --search-train-size 20000 \
  --search-valid-size 8000
```

The driver executes the full-feature Dummy / Logistic Regression / RF / XGBoost baselines, then GA / BPSO / PSO / NSGA-II at the prescribed unique-evaluation budget. It records input dataset SHA-256 hashes, Python/package versions, a command log, exit statuses and elapsed time. Outputs are written **only** inside the fresh timestamped run folder: `baselines/baseline_runs.csv`, `baselines/baseline_summary.csv`, `optimisers/runs.csv`, `optimisers/summary.csv`, `optimisers/pareto_seed_*.csv`, `optimisers/models/ga_rf_pipeline.joblib`, `optimisers/models/ga_rf_features.json`, and `logs/`.

Do not close VS Code while this run executes. This involves up to 6,000 expensive feature-mask assessments (4 algorithms × 5 seeds × 300) plus full-feature baseline training. Do not assume results will equal historical results: the reconstructed runner has not been shown to have identical hyperparameters to the original Windows scripts.

**Check success:** the terminal must end with `RUN PASSED`, the manifest's `status` must be `PASS`, and *each* of the 20 optimiser rows must have `fitness_evaluations == 300`. Do not replace historical report figures until comparing the new results carefully.

Inspect the latest full run:

```bash
python - <<'PY'
from pathlib import Path
import json,pandas as pd
folders=sorted(Path('results/protocol_runs').glob('*_full'))
assert folders, 'No full run found yet'
p=folders[-1]
manifest=json.loads((p/'manifest.json').read_text())
print('Run:',p,'Status:',manifest['status'])
assert manifest['status']=='PASS'
runs=pd.read_csv(p/'optimisers/runs.csv')
assert len(runs)==20
assert runs['fitness_evaluations'].eq(300).all()
print(pd.read_csv(p/'optimisers/summary.csv').to_string(index=False))
print(pd.read_csv(p/'baselines/baseline_summary.csv').to_string(index=False))
print('Official dataset SHA-256:',manifest['inputs'])
PY
```

## Stage 5 — Use the trained model with terminal-based IDS replay

To score new compatible CSV flow rows with the *actual exported GA seed-42 model*:

```bash
python - <<'PY'
from pathlib import Path
p=sorted(Path('results/protocol_runs').glob('*_full'))[-1]
print('MODEL:',p/'optimisers/models/ga_rf_pipeline.joblib')
PY
```

Copy the printed model path into this command:

```bash
python -m prototype.windows_ids replay \
  --csv data/raw/UNSW_NB15_testing-set.csv \
  --model 'REPLACE_WITH_PRINTED_MODEL_PATH' \
  --output results/windows_replay_ga_seed42.csv
```

The CSV predictions are **not** a new independent evaluation if you score the already-used official test data; this step verifies model export/replay integration. Keep the original official test split separate from any later tuning decisions.

## Stage 6 — View passive local Windows connection telemetry (Bash)

```bash
python -m prototype.windows_ids monitor --interval 2 --iterations 5
```

This lists TCP/UDP socket metadata with available process names and PIDs. This is *not* direct UNSW-feature extraction and does not generate intrusion predictions from raw Windows connections. It neither blocks traffic nor changes Windows Firewall. Administrator privilege is not normally required but may reveal more process metadata.

## Stage 7 — Start Python API + React (two VS Code Git Bash terminals)

**Terminal A** (project root, environment activated):

```bash
python -m uvicorn prototype.api:app --host 127.0.0.1 --port 8000 --reload
```

Open http://127.0.0.1:8000/api/health. The default replay model is `models/demo_pipeline.joblib`. To select the actual GA model, first stop the API with Ctrl+C, then:

```bash
export EVONIDS_MODEL='REPLACE_WITH_PRINTED_MODEL_PATH'
python -m uvicorn prototype.api:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal B** (project root):

```bash
cd frontend
node --version
npm --version
npm install
npm run build
npm run dev
```

Open http://127.0.0.1:5173. React pages include Overview, Live Connections, Model Replay and Research Results. The Research Results panel is currently populated with **historical fixed summary data**, and does not automatically update from freshly generated `runs.csv`. Do not show it as evidence of the most recent experiment without updating the data source and verifying it.

## Stage 8 — Evidence and publication

Keep the timestamped full-run `manifest.json`, `logs/`, `baseline_runs.csv`, `runs.csv`, `summary.csv`, Pareto CSVs, selected feature JSON and Python/Windows test output. Record any failure, configuration change, rerun reason and git commit SHA in the reproducibility notes. Confirm `git status --short`, inspect `git diff --stat`, exclude raw dataset and machine-generated files from Git, then commit implementation changes. The submitted PDF must link to the accessible repository and UNSW-NB15 official dataset. The Moodle deliverable is the PDF, not a source ZIP.

## Stage 9 — Compare fresh experiment results against the earlier report

```bash
python tools/compare_reproduction.py
```

This produces `historical_vs_new.csv` inside the latest successful run directory. If any differences appear, inspect dataset hashes, selected feature columns, search/final RF hyperparameters, validation split, and algorithm settings **before** altering the submitted PDF. Do not report new values as a direct reproduction unless configuration identity has been demonstrated.