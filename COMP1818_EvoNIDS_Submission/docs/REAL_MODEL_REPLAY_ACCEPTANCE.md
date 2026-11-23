# Real-model API replay acceptance (local Windows)

The GitHub Actions workflow tests the **synthetic demonstration model**. For real-model acceptance, use the locally saved GA seed-42 joint Random Forest pipeline, exported by `research/src/run_experiments.py` during the corrected 16 November full joint run. The algorithm with the highest *mean* test Macro-F1 is joint **PSO**, but the code currently exports the **GA seed-42** pipeline only. Do **not** label the GA export as the PSO model, and do not select a model solely because it attained a high held-out test score.

The canonical nested project root is `COMP1818_EvoNIDS_Submission`. The public research index is [results/README.md](../results/README.md); results browsing and real-model online execution are separate capabilities.

## Local checklist

1. Pull latest GitHub `main` without discarding local untracked model or result files.
2. Activate Python 3.12 and run `python -m pytest -q research/tests prototype/tests`.
3. Ensure the original UNSW-NB15 testing CSV is available under `data/raw/UNSW_NB15_testing-set.csv`.
4. Verify that the **trusted local** model file exists at:

   `results/protocol_runs/20261116T151402Z_full_joint/optimisers/models/ga_rf_joint_pipeline.joblib`

   Large binary model artefacts are not committed to GitHub; do not run full optimisation again simply to satisfy a missing file. Recover the locally exported file if available.

5. Run:

```bash
python -m tools.check_saved_model_replay \
  --model results/protocol_runs/20261116T151402Z_full_joint/optimisers/models/ga_rf_joint_pipeline.joblib \
  --csv data/raw/UNSW_NB15_testing-set.csv \
  --features-json results/protocol_runs/20261116T151402Z_full_joint/optimisers/models/ga_rf_joint_features.json \
  --rows 20
```

Expected: the script reports `PASS` and states that predictions made through FastAPI match direct sklearn predictions. It does not modify data or recompute the coursework performance metrics. It verifies the loaded pipeline and input schema on the supplied rows; it does not prove model quality on new networks.

6. For a visual check, start the API from this directory with the environment variable set *before* Uvicorn:

```bash
export EVONIDS_MODEL="results/protocol_runs/20261116T151402Z_full_joint/optimisers/models/ga_rf_joint_pipeline.joblib"
python -m uvicorn prototype.api:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:5173` and submit a CSV with the model's feature columns in the Model Replay view. The dashboard's summary metrics describe the *five-seed joint PSO research result*, not the identity of the locally configured GA replay model.

**Scope:** Windows connection-monitor telemetry cannot be directly passed to this UNSW-NB15-trained pipeline without a compatible engineered-feature extraction layer. The UI must not be described as a validated real-time network IDS. Only load joblib model files from trusted sources, since they can execute Python code on deserialisation.
