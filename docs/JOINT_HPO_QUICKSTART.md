# EvoNIDS joint feature selection + RF tuning: Windows Git Bash quickstart

Run commands from the root of a fresh GitHub clone (`COMP1818_EvoNIDS_with_React`). For existing local installations, use the current `COMP1818_EvoNIDS_Submission` project folder.

1. Back up/commit existing changes (`git status --short`) and extract the
   `EvoNIDS_Joint_RF_HPO_Implementation_Patch.zip` **into this folder**, keeping paths.
   This updates the existing research runner and does not create a second repo.
2. Activate local Python 3.12 venv:

   ```bash
   source .venv/Scripts/activate
   python -m pytest -q research/tests prototype/tests
   ```

3. Verify the joint experiment on synthetic inputs:

   ```bash
   python tools/run_protocol.py --phase smoke --optimisation joint
   ```

4. Run the **new** official-data experiment, separately from the November 14
   feature-only run (potentially CPU-intensive):

   ```bash
   python tools/run_protocol.py --phase full --optimisation joint \
     --train data/raw/UNSW_NB15_training-set.csv \
     --test data/raw/UNSW_NB15_testing-set.csv \
     --seeds 42 101 202 303 404 \
     --budget 300 --population 8 \
     --search-train-size 20000 --search-valid-size 8000
   ```

5. Find the new export and metrics:

   ```bash
   find results/protocol_runs -path '*_full_joint/optimisers/models/ga_rf_joint_pipeline.joblib' -print
   find results/protocol_runs -path '*_full_joint/optimisers/summary.csv' -print
   ```

6. Replay using the latest completed joint GA pipeline:

   ```bash
   MODEL=$(find results/protocol_runs -path '*_full_joint/optimisers/models/ga_rf_joint_pipeline.joblib' -print | sort | tail -1)
   test -f "$MODEL" || { echo 'Joint model missing'; exit 1; }
   python -m prototype.windows_ids replay \
     --csv data/raw/UNSW_NB15_testing-set.csv \
     --model "$MODEL" \
     --output results/windows_ga_joint_predictions.csv
   ```

7. Inspect the selected model settings:

   ```bash
   python - <<'PY'
   import joblib
   from pathlib import Path
   models=sorted(Path('results/protocol_runs').glob('*_full_joint/optimisers/models/ga_rf_joint_pipeline.joblib'))
   if not models: raise SystemExit('Joint GA model not found')
   model=joblib.load(models[-1])
   print('Model:',models[-1]);print('Features:',list(model.feature_names_in_))
   print('RF parameters:',model.named_steps['classifier'].get_params())
   PY
   ```

8. Historical equivalence checking (requires independently archived original
   run provenance):

   ```bash
   RUN=$(find results/protocol_runs -maxdepth 1 -type d -name '*_full' | sort | tail -1)
   python tools/audit_historical_equivalence.py --current-run "$RUN"
   ```

   Output will say `NOT_VERIFIED` until authentic original settings, source,
   package versions and result hashes are supplied. This is not a failure to
   execute the new algorithm; it is correct scientific uncertainty.

## Interpreting outcomes

- `--optimisation features` is the historical-style feature-only baseline;
  `--optimisation joint` adds RF hyperparameter tuning. Do **not** compare as
  configuration-identical replications.
- `300` counts **distinct (feature-mask, hyperparameter-vector)** combinations
  in joint mode, not 300 unique masks alone.
- Joint GA/BPSO/PSO maximise Macro-F1 minus 0.05 times selected raw-feature
  fraction. NSGA-II optimises Macro-F1 and feature count separately.
- The previous official test results are **not** altered. After the Windows
  full run finishes, report the new results with a distinct protocol label.
- Windows `monitor` remains passive socket monitoring, **not** live inference
  with UNSW-NB15 features.