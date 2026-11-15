# Verification run: 14 November 2026 — container-only synthetic smoke test

Execution platform: Linux Python 3.13.5 (not the user's Windows PC).

- `python -m pytest -q research/tests prototype/tests`: **12 passed**.
- `python tools/run_protocol.py --phase smoke`: **PASS**. Each algorithm used exactly 12 distinct expensive evaluations on *synthetic data*.
- GA synthetic hold-out Macro-F1: 0.78632, 5 selected features.
- BPSO synthetic hold-out Macro-F1: 0.81250, 5 selected features.
- PSO synthetic hold-out Macro-F1: 0.87923, 6 selected features.
- NSGA-II synthetic hold-out Macro-F1: 0.44344, 3 selected features.
- Demo model train/save: **PASS**.
- Demo CSV scoring and `ids_prediction` / `attack_probability` export: **PASS**.
- One passive socket snapshot in container: **PASS**.

**Do not cite any of the above synthetic metrics as UNSW-NB15 experimental evidence.**

Not exercised: official UNSW-NB15 five-seed training, Windows networking, fresh Windows dependency installation, React/Vite production build. Those require the user's local machine and the official files. Historical report metrics were not changed.

Additional checks in the same environment:
- Expanded suite after React results-API integration: **14 Python tests passed**.
- Synthetic stress run using a 300-evaluation budget for seed 42: **GA=300, BPSO=300, PSO=300, NSGA-II=300** unique evaluations (PASS).
- Official 5-seed benchmark, native Windows telemetry and React production build still not executed.