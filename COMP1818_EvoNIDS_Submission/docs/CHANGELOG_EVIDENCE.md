# EvoNIDS documentation and research evidence changelog

## 2026-11-23 — Repository audit and canonical documentation refresh

- Re-centred the main research README on **corrected joint PSO** results (mean test Macro-F1 0.881373) while retaining the **earlier historical GA** study as distinct evidence.
- Indexed feature-only, corrected joint, invalid joint-labelled, historical, synthetic smoke and duplicated paired-verification files in [results/README.md](../results/README.md). **No experiment results were recalculated, edited or deleted.**
- Documented the nested canonical LaTeX source `report/latex/COMP1818_EvoNIDS_LaTeX/` and duplicate legacy copy; kept existing binary report artifacts intact.
- Corrected frontend demo model paths and clarified the separate historical research dashboard versus local replay classifier.
- Added a standard-library evidence check to Windows CI, verifying 40 per-seed records, 300-evaluation budgets, correct experiment modes, summary means, paired comparison consistency and presence of report sources.
- Clarified limitations: Pages publication requires owner setup, synthetic CI does not rerun official UNSW-NB15 benchmark, and the original trained full-data classifier is not hosted.

Primary provenance: [corrected joint experiment manifest](../results/protocol_runs/20261116T151402Z_full_joint/manifest.json). The run's historical executable/input SHA-256 values remain unchanged.
