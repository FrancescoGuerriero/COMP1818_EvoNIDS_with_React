# Clean-room and reproduction verification record — EvoNIDS

**Updated:** 2026-11-15  
**Project:** COMP-1818 — Multi-Objective Evolutionary Feature Selection for Efficient Network Intrusion Detection  
**Purpose:** Preserve a chronological, evidence-based account of checks performed on the Python research implementation, Windows IDS prototype, and React frontend.

> **Verification convention:** **PASS (reported)** refers to an explicitly reported test result; **RECORDED (outputs inspected)** means the supplied output files or console output were reviewed; **PENDING** means completion has not been demonstrated. These terms do not imply that a historical test was rerun today. A research experiment on a working Windows installation is not, by itself, a clean-room reproduction from a fresh checkout.

## 1. Original clean-room smoke test — 2026-11-01

A release-support copy was tested with a newly created virtual environment outside the package directory.

| Check | Recorded outcome |
|---|---|
| `python tools/verify_submission.py` | PASS (reported) |
| `python -m pytest` | PASS — 2 prototype tests (reported) |
| Synthetic demonstration-model creation | PASS (reported) |
| CSV replay scoring | PASS (reported) |
| One passive socket-monitor iteration | PASS (reported) |

**Historical scope:** `CLEAN_ROOM_PASS` applied **only** to this limited prototype smoke test. It did not certify React, a fresh internet-based Python package installation, or full UNSW-NB15 research reproducibility.

**Dependency-install limitation:** At that time, `pip install -r requirements.txt` could not reach PyPI (`Temporary failure in name resolution`). The functional test used already installed packages. Thus, installation of all dependencies in an isolated, network-enabled Windows environment was not demonstrated.

**Research limitation:** The official five-seed, 300-evaluation experiments were not executed in the November 1 clean-room test; the original research implementation and raw UNSW-NB15 dataset were unavailable there.

## 2. Subsequent Python research development and automated checks — November 2026

Subsequent work extended the repository beyond the November 1 release-support package:

- A reconstructed feature-selection runner with GA, BPSO, PSO and NSGA-II, equal unique-fitness-evaluation accounting, official-split evaluation and separate result directories was added.
- A later **opt-in joint feature-selection + Random Forest hyperparameter optimisation** implementation was prepared. The previous feature-only experiment mode was retained.
- In the assistant's development environment, the updated merged implementation was reported to pass **22 Python tests**, including joint search, budget/cache accounting, model export, and prototype tests. Joint-mode synthetic smoke and lightweight 300-candidate accounting checks were also reported as passed.

**Status:** **PASS (development-environment checks reported); Windows verification of the latest joint-HPO revision remains PENDING.** These development checks must not be presented as an independent Windows clean-room installation test. They also do not establish that the old and reconstructed research implementations are identical.

For the **current local revision**, rerun from the project root (not from `frontend/`):

```bash
cd ~/CourseWorks/Comp1818/COMP1818_EvoNIDS_with_React/COMP1818_EvoNIDS_Submission  # existing local checkout
source .venv/Scripts/activate
python -m pytest -q research/tests prototype/tests
python tools/run_protocol.py --phase smoke --optimisation joint
```

Record the command output and exit codes before assigning a new Windows PASS status. Earlier test counts (2, 14, 22) refer to **different code revisions and verification scopes**, not conflicting results for the same revision.

## 3. Official UNSW-NB15 research reproduction — 2026-11-14

The user supplied console output from a recorded full run at:

```text
results/protocol_runs/20261114T165654Z_full/
```

The recorded files include:

- `optimisers/runs.csv` — **20 rows:** four optimisation methods × five seeds (`42`, `101`, `202`, `303`, `404`).
- `optimisers/summary.csv` — mean/standard deviation of held-out test Macro-F1, average feature count/reduction, and average false-positive rate.
- `baselines/baseline_runs.csv` — **20 rows:** four full-feature baselines × five seeds.
- `baselines/baseline_summary.csv` — aggregated baseline metrics.

All **20 optimiser rows report exactly 300 unique fitness evaluations**, for **6,000 recorded unique evaluations** in total. These are recorded program outputs, not independent verification of every classifier fit or source-level implementation detail.

### 3.1 Recorded official test results

| Method | Mean Macro-F1 | SD | Mean selected raw features | Feature reduction | Mean FPR |
|---|---:|---:|---:|---:|---:|
| PSO + RF | **0.864282** | 0.012864 | 11.2 | 73.33% | 0.256319 |
| GA + RF | 0.861168 | 0.008158 | 10.2 | 75.71% | 0.266508 |
| BPSO + RF | 0.859390 | 0.010662 | 12.0 | 71.43% | 0.268416 |
| NSGA-II + RF | 0.839713 | 0.039023 | 5.4 | 87.14% | 0.273589 |
| Full-feature RF | 0.864103 | 0.000393 | 42 | 0% | 0.272308 |
| Full-feature XGBoost | **0.866822** | 0.000794 | 42 | 0% | 0.267211 |
| Logistic Regression | 0.829171 | 0.000000 | 42 | 0% | 0.281405 |
| Dummy | 0.355088 | 0.000000 | 42 | 0% | 1.000000 |

**Interpretation:** XGBoost achieved the highest absolute mean test Macro-F1; PSO was highest among the four feature-selection methods in this recorded run. NSGA-II showed large seed-to-seed variation (SD approximately 0.039), requiring critical discussion. These values relate to the **feature-only** run, not the subsequent joint-HPO extension.

### 3.2 GA seed-42 model and Windows replay

A separate user-reported replay processed **82,332 records** from `data/raw/UNSW_NB15_testing-set.csv`, using an exported GA + Random Forest scikit-learn pipeline:

```text
results/protocol_runs/20261114T165654Z_full/optimisers/models/ga_rf_pipeline.joblib
```

| Measure | Recorded value |
|---|---:|
| Selected raw predictors | 11 / 42 |
| Feature reduction | 73.81% |
| Accuracy | 0.8617 |
| Macro-F1 | 0.855574 (approximately 0.8556) |
| Balanced accuracy | 0.849570 |
| False-positive rate | 0.270108 |
| True negatives / false positives | 27,006 / 9,994 |
| False negatives / true positives | 1,394 / 43,938 |

The exported pipeline used a 200-tree `RandomForestClassifier`, `max_depth=None`, `min_samples_leaf=1`, `class_weight=balanced_subsample`, `random_state=42`, `n_jobs=1`, and preprocessing for ten numeric features plus categorical `service`. These settings were inspected from the saved pipeline, **not inferred from the five-seed historical means**.

**Limitations:** Replay of the same official test dataset checks the exported model's inference integration; it is not an additional independent hold-out evaluation. Live Windows socket monitoring also does not yet provide the engineered UNSW-NB15 flow features needed for real-time model inference.

### 3.3 Reproducibility classification

**Status: RECORDED (full official-data experiment outputs inspected), NOT a certified exact historical reproduction.** Prior five-seed summaries differ from these new results. Historical source revision, preprocessing and complete experiment configurations have not been verified as identical. A numerical match alone would not establish equivalence.

The original `EXPERIMENT_PROTOCOL.md` includes a boundary note that the reconstructed feature-only runner uses **fixed RF hyperparameters**. The later joint-HPO extension is a distinct experiment mode: its **official-data full run has not been documented as complete** and must not be conflated with the November 14 feature-only results.

## 4. Windows React frontend verification — 2026-11-15

### 4.1 Initial path error and dependency recovery

A Windows terminal previously reported `The system cannot find the path specified` while positioned inside:

```text
frontend/node_modules/@babel/code-frame/lib
```

A later user-reported recovery from `frontend/` executed `rm -rf node_modules` followed by `npm install` successfully:

- 69 packages added; 70 packages audited.
- 0 vulnerabilities reported.
- `npm` warned that `esbuild@0.28.2` has an installation script not yet approved by the installed script-policy mechanism. This warning is not, by itself, evidence of a failed installation.

**Status:** **Frontend dependency installation PASS (reported).** The original path-error symptom did not recur during that installation; the exact underlying cause was not independently established.

### 4.2 TypeScript/Vite build issue

A subsequent `npm run build` failed with:

```text
src/api.ts:14:30 - error TS2339:
Property 'env' does not exist on type 'ImportMeta'.
```

The documented remedy was to create `frontend/src/vite-env.d.ts` containing:

```ts
/// <reference types="vite/client" />
```

**Status:** Remedy provided; **successful rebuild has not been demonstrated in the supplied outputs**.

### 4.3 Mislocated commands and build log

The user executed Python commands from `frontend/`, producing:

```text
ERROR: file or directory not found: research/tests
ModuleNotFoundError: No module named 'prototype'
```

These errors arise because `research/` and `prototype/` are siblings of `frontend/`. Both commands must be executed from the project root. They do not establish missing Python packages or broken model files.

A later logged build command was launched from **the project root** instead of `frontend/` and returned:

```text
Build exit code: 127
```

In Git Bash, exit code 127 generally indicates a command was not found. The specific failing command must be confirmed from the captured log; `127` alone does not prove that Vite or npm is broken. The original log was written to `../results/verification/` relative to the project root, not to the intended project's `results/verification/` directory.

**Frontend production build status: PENDING.** No successful `npm run build` or browser/API integration check has yet been supplied.

### 4.4 Correct rerun from the frontend directory

Open a fresh **Git Bash** terminal:

```bash
cd ~/CourseWorks/Comp1818/COMP1818_EvoNIDS_with_React/COMP1818_EvoNIDS_Submission  # existing local checkout/frontend  # existing local checkout; fresh GitHub clones use repository-root/frontend
pwd
ls package.json
node --version
npm --version
ls src/vite-env.d.ts
```

If `src/vite-env.d.ts` is missing, create it:

```bash
printf '/// <reference types="vite/client" />\n' > src/vite-env.d.ts
```

Run and record the frontend build. **Preserve the exit code immediately after the grouped command**:

```bash
mkdir -p ../results/verification
{
  date -u
  pwd
  node --version
  npm --version
  npm run build
} > ../results/verification/frontend_build_2026-11-15.log 2>&1
BUILD_STATUS=$?
echo "Build exit code: $BUILD_STATUS"
cat ../results/verification/frontend_build_2026-11-15.log
```

Only if `BUILD_STATUS=0` and a `dist/` bundle exists may this check be marked **PASS**:

```bash
ls -lh dist/
```

### 4.5 Python API and React browser integration

From a **separate terminal at the project root**:

```bash
cd ~/CourseWorks/Comp1818/COMP1818_EvoNIDS_with_React/COMP1818_EvoNIDS_Submission  # existing local checkout
source .venv/Scripts/activate
python -m pytest -q research/tests prototype/tests
python -m uvicorn prototype.api:app --host 127.0.0.1 --port 8000
```

Check `http://127.0.0.1:8000/api/health`. Then start React from `frontend/` in another terminal with `npm run dev` and open `http://127.0.0.1:5173`. Verify the Overview, Live Connections, Model Replay and Research Results views. A passing production build does not, on its own, verify these live integrations.

## 5. Outstanding release checks

- [x] Historical November 1 prototype-only smoke test recorded, with its limitations.
- [x] November 14 official UNSW-NB15 feature-only run recorded for four methods × five seeds.
- [x] Each of the 20 recorded optimiser rows reports 300 unique evaluations.
- [x] GA seed-42 exported pipeline inspected and official test CSV replay recorded.
- [x] Frontend `npm install` recovered successfully on Windows (reported).
- [ ] Verify `python -m pytest -q research/tests prototype/tests` against the **latest joint-HPO revision** on the user's Windows installation; attach actual terminal log.
- [ ] Verify a full **joint feature-selection + RF hyperparameter** experiment on official UNSW-NB15 and preserve separate results.
- [ ] Demonstrate a clean, network-enabled Windows Python dependency installation from PyPI.
- [ ] Confirm successful TypeScript/Vite production build (`npm run build`, exit code 0, `dist/` present).
- [ ] Verify React pages and API integration in a running Windows environment.
- [ ] Capture dataset SHA-256 hashes, exact Git commit, dependency versions, config and execution logs for each official experiment.
- [ ] Audit original historical algorithm implementations and hyperparameters using authoritative source/configuration evidence; report `NOT_VERIFIED` until available.
- [ ] Reconcile new results and coursework report text without overwriting historical data.

## 6. Current verification conclusion

**Historical prototype:** **PASS** within the documented limited scope (2026-11-01).  
**Feature-only official-data experiment:** **RECORDED**, 20 optimiser runs and 20 baseline rows inspected (2026-11-14).  
**Windows GA CSV replay:** **PASS (reported)** for 82,332 official test records.  
**Joint RF-HPO implementation:** development checks reported as passed; **latest Windows full-run validation PENDING**.  
**Windows React dependency installation:** **PASS (reported)**.  
**Windows React production build and browser integration:** **PENDING**.  
**Exact reproduction of original historical source/settings:** **NOT_VERIFIED**.

Do not use the blanket label `CLEAN_ROOM_PASS` for the entire current project until the remaining clean-room and integration checks are completed and their logs preserved.