from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md", "requirements.txt", "pyproject.toml", ".gitignore",
    "docs/EXPERIMENT_PROTOCOL.md", "docs/REPRODUCTION.md",
    "research/src/run_experiments.py", "research/src/evolution/budgeted.py",
    "research/src/run_baselines.py", "research/tests/test_joint_hpo.py",
    "prototype/windows_ids.py", "prototype/replay.py", "prototype/api.py",
    "frontend/package.json", "frontend/src/vite-env.d.ts",
    "results/final_summary.csv", "report/COMP1818_EvoNIDS_Report.pdf",
]
FORBIDDEN_PARTS = {".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", ".idea", ".vscode"}

def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).is_file()]
    for path in missing:
        print("Missing required file:", path)
    tracked_forbidden = []
    try:
        completed = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
        )
        tracked = [x.decode("utf-8", errors="replace") for x in completed.stdout.split(b"\0") if x]
        tracked_forbidden = [p for p in tracked if any(part in FORBIDDEN_PARTS for part in Path(p).parts)]
    except (OSError, subprocess.CalledProcessError):
        print("Note: Git not available; tracked-file hygiene check skipped")
    for path in tracked_forbidden:
        print("Machine-generated file tracked in Git:", path)
    if missing or tracked_forbidden:
        return 1
    print("GitHub release structure verification: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
