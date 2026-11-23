# Clean-room smoke test record

Date: 2026-11-01

A clean copy of the generated release-support package was tested from a newly created virtual environment outside the package directory.

Functional checks completed successfully:

1. `python tools/verify_submission.py` - PASS
2. `python -m pytest` - 2/2 prototype tests PASS
3. Synthetic smoke-test model creation - PASS
4. CSV replay scoring through the IDS pipeline - PASS
5. One passive socket-monitor iteration - PASS

Final functional status: `CLEAN_ROOM_PASS`.

## Dependency-install limitation of this verification environment

A direct `pip install -r requirements.txt` was attempted from the fresh environment but the execution container could not resolve PyPI (`Temporary failure in name resolution`). For that reason, the functional fresh-venv run used the container's already installed Python package path. This verifies project wiring and execution but does **not** independently certify network-based dependency installation.

The final Windows release should therefore repeat the documented PowerShell/Git Bash clean-room procedure on the student's machine before submission, where PyPI access is available.

## Scope

This smoke test covers the generated submission structure and Windows IDS prototype. It does not re-run the full five-seed 300-evaluation UNSW-NB15 experiment because the canonical local research source and raw dataset are not present in this execution container.

## Later automated verification (different scope)

The 1 November two-test clean-room record above is historical and must **not** be represented as the current full test count. Current [Windows GitHub Actions](https://github.com/FrancescoGuerriero/COMP1818_EvoNIDS_with_React/actions/workflows/evonids-windows-reproducibility.yml) validates the expanded Python suite, synthetic joint optimisation, synthetic FastAPI model replay, saved CSV paired comparison, repository evidence links, and React build on fresh hosted runners. See [REPRODUCTION.md](REPRODUCTION.md) and [results index](../results/README.md). These hosted tests do not download the official training data or refit the full five-seed benchmark.
