# EvoNIDS — COMP-1818 Artificial Intelligence Applications

**Multi-Objective Evolutionary Feature Selection for Efficient Network Intrusion Detection**

This is the reproducible research and React prototype package. Start with the [lecturer's online evidence guide](docs/ONLINE_EXPERIMENTS.md), [experiment index](results/README.md), [protocol](docs/EXPERIMENT_PROTOCOL.md) and [latest editable LaTeX report](report/latex/COMP1818_EvoNIDS_LaTeX/README.md).

## Corrected UNSW-NB15 experimental results

Five matched seeds (`42, 101, 202, 303, 404`), four evolutionary methods, **300 unique expensive candidate fits per method per seed**, 42 eligible raw predictors, and official UNSW-NB15 train/test partitions. Random Forest (RF) is the wrapper classifier. GA, BPSO, PSO and NSGA-II were compared in feature-only and joint feature-selection/RF-hyperparameter modes.

| Method | Feature-only mean test Macro-F1 | Corrected joint mean test Macro-F1 | Joint mean features / 42 | Joint reduction |
|---|---:|---:|---:|---:|
| GA | 0.861168 | 0.878881 | 9.8 | 76.67% |
| BPSO | 0.859390 | 0.877153 | 12.6 | 70.00% |
| PSO | 0.864282 | 0.881373 | 11.4 | 72.86% |
| NSGA-II | 0.839713 | 0.843918 | 6.0 | 85.71% |

The **corrected joint PSO** experiment has the highest mean test Macro-F1, 0.881373 (SD 0.008072), with 72.86% average feature reduction and mean false-positive rate 0.219708. Full-feature corrected-run baselines: XGBoost 0.866822; RF 0.864103; logistic regression 0.829171; Dummy 0.355088. These comparisons are descriptive; different computational search costs and the small sample of five seeds constrain conclusions.

The matched PSO mean gain over feature-only is +0.017091 (95% paired-t CI [0.006659, 0.027523]); paired t p=0.010427 but exact two-sided Wilcoxon p=0.0625. **Do not claim robust or multiple-testing-adjusted significance.** See [paired statistics](results/statistical_analysis/paired_joint_comparison.csv).

**Crucial provenance:** The earlier run `results/protocol_runs/20261116T100750Z_full_joint` was labelled joint but actually ran **feature-only** due to a CLI argument-forwarding defect. It is retained for transparency and must not be cited as joint HPO evidence. The valid feature-only run is `results/protocol_runs/20261115T183225Z_full`, and the valid corrected joint run is `results/protocol_runs/20261116T151402Z_full_joint`. Older aggregate CSVs such as `results/final_summary.csv` and the initial Word/PDF paper relate to an **earlier historical study**; their GA-leading values are not interchangeable with the corrected joint study.

## Browse evidence online

- [All corrected joint seed-level results](results/protocol_runs/20261116T151402Z_full_joint/optimisers/runs.csv) · [joint summary](results/protocol_runs/20261116T151402Z_full_joint/optimisers/summary.csv) · [configuration](results/protocol_runs/20261116T151402Z_full_joint/optimisers/run_config.json)
- [All feature-only seed-level results](results/protocol_runs/20261115T183225Z_full/optimisers/runs.csv) · [feature-only summary](results/protocol_runs/20261115T183225Z_full/optimisers/summary.csv)
- [Official-run baseline scores](results/protocol_runs/20261116T151402Z_full_joint/baselines/baseline_summary.csv) · [paired statistical output](results/statistical_analysis/paired_joint_comparison.csv)
- [Execution provenance, input SHA-256 digests and dependency versions](results/protocol_runs/20261116T151402Z_full_joint/manifest.json)
- [Published charts](../online-experiments/index.html) · [public GitHub graphs](../README.md)
- [Latest LaTeX report source](report/latex/COMP1818_EvoNIDS_LaTeX/main.tex) · [compiled LaTeX PDF](report/latex/COMP1818_EvoNIDS_LaTeX/main.pdf)

The repository includes the full source code and result tables; **the original trained full-dataset GA joint `.joblib` is not uploaded**. Synthetic smoke-model binaries under `results/smoke/` and `results/joint_fix_smoke/` are not official benchmark models. The independent online CI does not repeat the expensive full dataset search.

## Layout and environment

```text
COMP1818_EvoNIDS_Submission/
├── research/          # GA, BPSO, PSO, NSGA-II, baselines and tests
├── prototype/         # passive Windows connection monitoring and CSV replay API
├── frontend/          # React + TypeScript + Vite research console
├── results/           # earlier study, feature-only, corrected joint, provenance and smoke evidence
├── report/latex/COMP1818_EvoNIDS_LaTeX/  # editable 5-page LaTeX report and figure generator
├── docs/              # protocol, reproduction and lecturer guides
└── tools/             # recorded experiment runner, statistical checks, verification
```

From a VS Code terminal at **this directory**, use Python 3.12:

```bash
python -m venv .venv
source .venv/Scripts/activate  # Git Bash; for PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q research/tests prototype/tests
python tools/check_repository_evidence.py
```

To verify the **published** five-seed paired comparison without retraining:

```bash
python tools/compare_joint_statistics.py \
  results/protocol_runs/20261115T183225Z_full/optimisers/runs.csv \
  results/protocol_runs/20261116T151402Z_full_joint/optimisers/runs.csv \
  --output results/paired_verification.csv
```

This writes a verification copy, not new experiment evidence. Compare with [the canonical comparison](results/statistical_analysis/paired_joint_comparison.csv).

Full experimental reruns require the official [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset) CSV partitions in `data/raw/`. **Do not rerun expensive searches simply to check the existing results**. The exact full-run commands, search options and constraints are in [REPRODUCTION.md](docs/REPRODUCTION.md) and [EXPERIMENT_PROTOCOL.md](docs/EXPERIMENT_PROTOCOL.md).

## Running the React/FastAPI demonstration

From the package root, terminal 1:

```bash
python -m prototype.train_demo_model --output models/demo_pipeline.joblib --csv-output results/demo_rows.csv
export EVONIDS_MODEL="models/demo_pipeline.joblib"  # Git Bash
python -m uvicorn prototype.api:app --host 127.0.0.1 --port 8000
```

In terminal 2, still inside the package root:

```bash
cd frontend
npm ci
npm run build
npm run dev
```

Visit http://127.0.0.1:5173. This model is **synthetic**: it checks wiring only. Passive Windows socket fields are **not** an UNSW-NB15 engineered feature vector. For real saved-model replay use [the separate local acceptance guide](docs/REAL_MODEL_REPLAY_ACCEPTANCE.md); online live benchmark scoring is not claimed.

## Report, Git and submission

The [latest LaTeX report](report/latex/COMP1818_EvoNIDS_LaTeX/README.md) includes reproducible Matplotlib figure source and native LaTeX tables/equations. An older copy remains in `report/COMP1818_EvoNIDS_LaTeX_Full_Four_Page_Project/` and a ZIP is archived; **use `report/latex/COMP1818_EvoNIDS_LaTeX/` as the working location**. A five-page PDF is included there. The prior separately produced Word/PDF may be absent from the latest repository; prefer the LaTeX PDF when the module allows its format. This recreates the provided example style, not a verified exact Moodle style package.

See [Git and submission checklist](docs/GIT_AND_SUBMISSION.md) for safe staging, LaTeX builds, clean-clone verification and online publication. Check Moodle for the authoritative report format and upload instructions. Do not commit raw benchmark data, virtual environments, `node_modules`, secrets or untrusted `.joblib` models.

**Academic integrity:** the report's AI-use disclosure distinguishes assistance with explanation, code review and editing from independently executed Python experimental measurements.
