"""Fail-closed audit of claimed equivalence with original, pre-reconstruction runs.

The historical five-seed *summary* is not configuration provenance. This tool
requires original source, dataset, dependency and run-config fingerprints before
claiming an exact match. It never labels an unverified run as reproduced.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ['research/src/run_experiments.py', 'research/src/evolution/budgeted.py',
          'research/src/run_baselines.py']


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as inp:
        for chunk in iter(lambda: inp.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def source_fingerprints():
    return {key: digest(ROOT / key) for key in SOURCE}


def audit(historical, current):
    """Return pass only when all independently recorded provenance agrees."""
    required = ['dataset_sha256', 'source_sha256', 'dependencies', 'configuration',
                'per_seed_results_sha256']
    missing = [key for key in required if key not in historical or key not in current]
    if missing:
        return False, [f'Missing independent provenance field: {name}' for name in missing]
    differing = [name for name in required if historical[name] != current[name]]
    return not differing, [f'Historical and new {name} differ' for name in differing]


def build_current(run_dir):
    manifest = json.loads((run_dir / 'manifest.json').read_text(encoding='utf-8'))
    config = json.loads((run_dir / 'optimisers' / 'run_config.json').read_text(encoding='utf-8'))
    runs_file = run_dir / 'optimisers' / 'runs.csv'
    return {
        'dataset_sha256': {k: v.get('sha256') for k, v in manifest.get('inputs', {}).items()},
        'source_sha256': manifest.get('source_sha256') or source_fingerprints(),
        'dependencies': manifest.get('dependencies', {}),
        'configuration': config,
        'per_seed_results_sha256': digest(runs_file),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current-run', required=True, type=Path)
    parser.add_argument('--historical-evidence', type=Path,
                        help='Independently archived original-run provenance JSON, not reconstructed from new code')
    args = parser.parse_args()
    if not (args.current_run / 'manifest.json').is_file():
        parser.error('Current run manifest missing')
    current = build_current(args.current_run)
    output = args.current_run / 'historical_equivalence_audit.json'
    if not args.historical_evidence:
        passed, reasons = False, ['Original historical source/configuration, environment and per-seed evidence not supplied. Historical result means alone cannot establish equivalence.']
    else:
        original = json.loads(args.historical_evidence.read_text(encoding='utf-8'))
        passed, reasons = audit(original, current)
        if not passed and not reasons:
            reasons = ['Unexplained mismatch']
    result = {'historical_equivalence': 'VERIFIED' if passed else 'NOT_VERIFIED',
              'reason': reasons, 'current_run': str(args.current_run),
              'historical_evidence': str(args.historical_evidence) if args.historical_evidence else None,
              'warning': 'Matching hashes prove identity of supplied artefacts, not correctness of the experimental design.'}
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    # A failed check is an expected nonzero status for CI/reviewers.
    return 0 if passed else 2


if __name__ == '__main__':
    raise SystemExit(main())