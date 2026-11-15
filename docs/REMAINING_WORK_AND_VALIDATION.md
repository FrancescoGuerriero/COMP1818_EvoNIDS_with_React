# Implementation gaps and verification status (14 November 2026)

## Implemented and verified in a Linux execution container
- Python research runner for distinct GA, BPSO, continuous PSO and NSGA-II, shared cached evaluation budget.
- Twelve Python tests passing against merged project.
- All four algorithms run with 12 expensive evaluations each on synthetic training data.
- Synthetic demonstration model export, CSV scoring, and log/manifest capture.
- Prototype can observe sockets in current container, but Windows-specific permissions/PID coverage remain untested.

## Requires execution on Windows and official dataset
- Five seeds × 300 evaluations on UNSW-NB15; no fresh official result is claimed yet.
- Confirm exactly 20 rows and 300 charged evaluations each, all cross-seed variance and FPR.
- Check actual train/test partition hashes, categorical encoders, feature alignment and exported model replay.
- Clean `python -m pip install -r requirements.txt` from a newly created Windows venv.
- `npm install`, `npm run build`, Vite launch and browser API wiring.
- Exported model replay on the *real* UNSW feature columns and live Windows passive socket collection.

## Unfinished engineering rather than silently completed
- **True live ML inference** is not implemented: `psutil` socket records cannot supply UNSW-NB15 engineered flow features; implementing a compatible feature extraction or retrained native-Windows model is a separate research task.
- React Results loads newly recorded completed full runs; it has not yet been built or verified in a Windows browser.
- The original canonical late-stage GA/BPSO/PSO/NSGA-II research source and run artefacts on the student's computer were not included in the initial GitHub submission. Reconstructions have **not** been proven configuration-identical to those source files.
- Hyperparameter optimisation is mentioned in the broader topic, but the reconstructed runner optimises feature subsets only; RF hyperparameters are fixed. Do not describe this runner as jointly optimising RF hyperparameters.
- A fresh 5-seed full run and re-analysis are required before rewriting reported figures.
- GitHub currently had only research placeholder files before merging this research patch; upload and confirm the implementation before claiming repository reproducibility.

## Academic limitations
- Five seeds have limited statistical power. Earlier Friedman p≈0.178 does not establish algorithm superiority.
- The original training-validation/test generalisation gaps may reflect distribution differences as well as model selection overfitting.
- Equal unique evaluation budget controls expensive fitness calls but not training-time equivalence or RF hyperparameter differences.
- A supervised benchmark can demonstrate classification performance but does not establish effectiveness for unconstrained real-world deployment.

## Recently completed in this release patch
- `/api/experiment-results` now exposes the latest completed official-data protocol run, if available.
- React Research Results displays that recorded run rather than always showing historical fixed values; fallback remains labelled historical.
- An additional integration test checks saved-model CSV replay; API health and research-result response tests are included.
- A 300-unique-evaluation synthetic stress check passed for GA, BPSO, PSO and NSGA-II individually. This validates budget accounting on a synthetic feature space, **not** official test accuracy.
- `tools/compare_reproduction.py` compares a future full rerun against the previously reported five-seed mean values without silently updating the report.

## Update 15 November 2026 — implemented joint optimisation

- New opt-in `--optimisation joint` searches raw predictors plus four encoded
  RF hyperparameters for all four optimisers; the legacy features mode is intact.
- Refit/export uses the selected hyperparameters and writes a new joint-specific
  GA model rather than overwriting the feature-only GA model.
- A separate `_full_joint` protocol run with its own manifest and hashes keeps
  the earlier official five-seed result untouched.
- Local unit/integration checks cover cache accounting, four algorithm budgets,
  legal hyperparameters, final model settings and fail-closed historical audit.
- No new official UNSW-NB15 joint HPO test metrics are claimed until the user
  executes and shares the recorded Windows run.
- Full historical settings are still **NOT VERIFIED**. The original source
  revision and full historical run provenance must be independently recovered.