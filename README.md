# EvoNIDS — COMP-1818 Artificial Intelligence Applications

Evolutionary feature selection and optional joint Random Forest hyperparameter
optimisation for **binary network intrusion detection** using UNSW-NB15.

**GitHub:** https://github.com/FrancescoGuerriero/COMP1818_EvoNIDS_with_React

## Repository layout

```text
.
├── .github/workflows/windows.yml  Windows CI and optional full experiment jobs
├── data/README.md                Dataset acquisition instructions
├── docs/                         Experimental protocol and verification records
├── frontend/                     React + TypeScript + Vite dashboard
├── prototype/                    Passive Windows monitor, API and CSV replay
├── research/                     GA, BPSO, PSO, NSGA-II, baselines and tests
├── report/                       Coursework report
├── results/                      Historical published results (not overwritten)
├── tools/                        Recorded runner and historical audit
├── requirements.txt
└── README.md
```

## Quick start from a clean GitHub clone

Requires **Python 3.12** and **Node.js 22** on Windows.

```bash
git clone https://github.com/FrancescoGuerriero/COMP1818_EvoNIDS_with_React.git
cd COMP1818_EvoNIDS_with_React
py -3.12 -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
python -m pytest -q research/tests prototype/tests
python tools/run_protocol.py --phase smoke --optimisation joint
cd frontend
npm install
npm run build
```

Use separate terminals for the backend and UI, both started from their correct directories:

```bash
# Terminal 1: repository root
python -m uvicorn prototype.api:app --host 127.0.0.1 --port 8000
# Terminal 2: repository root
cd frontend && npm run dev
```

Open http://127.0.0.1:5173 and http://127.0.0.1:8000/api/health.

## Official UNSW-NB15 experiment

Download the two CSV files as described in [data/README.md](data/README.md).

```bash
# Feature-only study (reproduces the current experimental mode, not necessarily historical weights/settings)
python tools/run_protocol.py --phase full --optimisation features \
  --train data/raw/UNSW_NB15_training-set.csv \
  --test data/raw/UNSW_NB15_testing-set.csv \
  --seeds 42 101 202 303 404 --budget 300

# Joint feature + Random Forest hyperparameter optimisation (new experiment)
python tools/run_protocol.py --phase full --optimisation joint \
  --train data/raw/UNSW_NB15_training-set.csv \
  --test data/raw/UNSW_NB15_testing-set.csv \
  --seeds 42 101 202 303 404 --budget 300
```

Each invocation creates a timestamped directory in `results/protocol_runs/`
containing a manifest, dataset SHA-256 hashes, environment details, logs,
baselines, algorithm results and exported models. Do not overwrite historical files.

## Windows GitHub Actions

[Windows verification workflow](.github/workflows/windows.yml) runs Python tests,
a synthetic evolutionary smoke test and the React production build on pushes.
For a full official experiment, open **Actions → Windows verification and full
experiments → Run workflow**, set `run_full=true`, and choose `features` or `joint`.
Five independent Windows jobs run the five seeds, and upload per-seed evidence.
A workflow that has not passed is not evidence of successful reproduction.
Check compute quotas and the dataset source/hashes before triggering full runs.

## Research integrity and limitations

- Binary target `label`; exclude `id` and `attack_cat` (42 raw predictors).
- Five matched seeds: 42, 101, 202, 303, 404.
- Equal budgets: 300 distinct expensive candidate evaluations per method and seed.
- Leakage-safe feature selection using training-derived validation data; held-out
  official test data is used only after selecting each final model.
- Macro-F1 is primary; report balanced accuracy, FPR, number of features,
  runtime and variation across runs.
- The passive Windows socket monitor is **not** an end-to-end live classifier:
  UNSW-NB15-compatible feature extraction is required for real-time inference.
- Previous feature-only results must not be represented as outcomes of joint
  hyperparameter optimisation. Exact equivalence with original historical
  implementations has **not** been established.
- The coursework PDF contains the required declaration about AI-assisted work;
  it is part of the academic submission record.

Dataset: https://research.unsw.edu.au/projects/unsw-nb15-dataset

See [docs/EXPERIMENT_PROTOCOL.md](docs/EXPERIMENT_PROTOCOL.md),
[docs/CLEAN_ROOM_TEST.md](docs/CLEAN_ROOM_TEST.md) and
[docs/JOINT_HPO_QUICKSTART.md](docs/JOINT_HPO_QUICKSTART.md).