# EvoNIDS React / TypeScript dashboard

The React + Vite frontend presents **published research summaries** and separately exposes a local FastAPI demonstration with passive Windows socket telemetry and compatible CSV inference. These are not the same evidence streams.

Architecture:

```text
React :5173 ── GET /api/health ─┐
             GET /api/connections ├── local Python FastAPI :8000
             POST /api/replay ────┘    (trusted saved sklearn pipeline)
```

**Research Results:** corrected feature-only and joint GA/BPSO/PSO/NSGA-II five-seed means, XGBoost/RF/logistic/Dummy baselines, selected features and false-positive rates. Source-of-truth: [results index](../results/README.md), [official joint summary](../results/protocol_runs/20261116T151402Z_full_joint/optimisers/summary.csv) and [paired analysis](../results/statistical_analysis/paired_joint_comparison.csv). The leading research score is **joint PSO mean Macro-F1 0.881373**, not the identity or accuracy of the locally loaded replay model.

**Live Connections:** Windows `psutil` process/socket snapshots; offline fallback rows are labelled synthetic/demonstration.

**Model Replay:** CSV input goes to the Python API; its model is selected via `EVONIDS_MODEL`. Direct Windows socket telemetry is **not** a valid UNSW-NB15 feature vector.

## Start an isolated demo on Windows / VS Code

From `COMP1818_EvoNIDS_Submission/`, in terminal 1:

```bash
python -m prototype.train_demo_model --output models/demo_pipeline.joblib --csv-output results/demo_rows.csv
export EVONIDS_MODEL="models/demo_pipeline.joblib"  # Git Bash
python -m uvicorn prototype.api:app --host 127.0.0.1 --port 8000
```

PowerShell equivalent for environment variable: `$env:EVONIDS_MODEL="models/demo_pipeline.joblib"`. API health check: http://127.0.0.1:8000/api/health.

Terminal 2 (start from `COMP1818_EvoNIDS_Submission/`):

```bash
cd frontend
npm ci
npm run build
npm run dev
```

Open http://127.0.0.1:5173. Synthetic demo data may be used for the Model Replay tab. The demonstration-model score is **not** a research benchmark; do not relabel it GA or PSO test performance.

For a trusted local benchmark model, read [REAL_MODEL_REPLAY_ACCEPTANCE.md](../docs/REAL_MODEL_REPLAY_ACCEPTANCE.md). The historical trained joint GA `.joblib` was not committed; the trained model's source feature list and RF settings JSON are versioned. An external publicly hosted inference API is **not** provided.

GitHub CI builds the frontend with Node.js 22 and `npm ci && npm run build`. Vite writes the static bundle to `frontend/dist/`. For version control and submission instructions see [GIT_AND_SUBMISSION.md](../docs/GIT_AND_SUBMISSION.md).
