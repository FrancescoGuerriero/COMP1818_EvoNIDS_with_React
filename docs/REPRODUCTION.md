# Reproduction from GitHub (Windows 11)

Clone https://github.com/FrancescoGuerriero/COMP1818_EvoNIDS_with_React .
The repository root directly contains `research`, `prototype`, `frontend`, and `tools`; do not `cd` into a nested submission directory after cloning.

1. Install Python 3.12 and Node.js 22.
2. In Git Bash run `py -3.12 -m venv .venv` then `source .venv/Scripts/activate`.
3. Run `python -m pip install -r requirements.txt` and `python -m pytest -q research/tests prototype/tests`.
4. Run `python tools/run_protocol.py --phase smoke --optimisation joint`.
5. Run `cd frontend && npm install && npm run build`.
6. Download the official training/testing CSV files described in `data/README.md` and place in `data/raw`.
7. From repository root, run `python tools/run_protocol.py --phase full --optimisation features` and, separately, `python tools/run_protocol.py --phase full --optimisation joint`.

The full experiment takes substantial compute resources and outputs a new immutable run directory under `results/protocol_runs`.
The CI Windows smoke workflow runs on pushes. To run full experiments on GitHub-hosted Windows machines, use Actions → Windows verification and full experiments → Run workflow, with `run_full=true`.
The CI full mode retrieves a **public mirror**, not an authenticated copy of the source dataset; check the recorded file hashes against official copies.

Historical November 2026 experiment results were recorded locally; they are not proof that CI completed official-data training.
Never claim a clean-room pass before reviewing the new workflow logs and successful artifacts.

The passive Windows IDS monitor captures socket telemetry but does not convert it into full UNSW-NB15 features. For ML predictions, use replay of compatible CSV records.