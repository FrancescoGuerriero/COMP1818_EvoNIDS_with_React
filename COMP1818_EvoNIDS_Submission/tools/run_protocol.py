"""Recorded EvoNIDS reproduction: immutable per-run output folders, no benchmark overwrite.

Usage: python tools/run_protocol.py --phase smoke
       python tools/run_protocol.py --phase full --train data/raw/... --test data/raw/...
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ['numpy', 'pandas', 'scikit-learn', 'scipy', 'xgboost', 'pytest', 'fastapi', 'uvicorn', 'psutil', 'joblib']


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as src:
        for data in iter(lambda: src.read(1024 * 1024), b''):
            digest.update(data)
    return digest.hexdigest()


def execute(cmd: list[str], logdir: Path, name: str, extra_env: dict[str,str] | None = None) -> dict:
    logpath = logdir / (name + '.log')
    print(f'\n[{name}] ' + ' '.join(cmd), flush=True)
    t0 = time.perf_counter()
    env = os.environ.copy()
    env.update(extra_env or {})
    with logpath.open('w', encoding='utf-8') as logfile:
        process = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, errors='replace', bufsize=1)
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end='', flush=True)
            logfile.write(line)
        code = process.wait()
    result = {'step': name, 'command': cmd, 'exit_code': code, 'elapsed_seconds': round(time.perf_counter()-t0, 2), 'log': str(logpath.relative_to(ROOT))}
    if code:
        raise RuntimeError(f'Step {name} failed (exit={code}). See {logpath}')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['smoke', 'full', 'all'], default='smoke')
    parser.add_argument('--optimisation', choices=['features','joint'], default='features')
    parser.add_argument('--train', default='data/raw/UNSW_NB15_training-set.csv')
    parser.add_argument('--test', default='data/raw/UNSW_NB15_testing-set.csv')
    parser.add_argument('--seeds', type=int, nargs='+', default=[42, 101, 202, 303, 404])
    parser.add_argument('--budget', type=int, default=300)
    parser.add_argument('--population', type=int, default=8)
    parser.add_argument('--search-train-size', type=int, default=20000)
    parser.add_argument('--search-valid-size', type=int, default=8000)
    parser.add_argument('--monitor', action='store_true', help='Also take one passive connection snapshot')
    args = parser.parse_args()
    now = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    target = ROOT / 'results' / 'protocol_runs' / (f'{now}_{args.phase}' + ('_joint' if args.optimisation=='joint' else ''))
    target.mkdir(parents=True, exist_ok=False)
    logs = target / 'logs'; logs.mkdir()
    run = {'started_utc': now, 'phase': args.phase, 'configuration': vars(args),
           'python': sys.version, 'python_executable': sys.executable,
           'platform': platform.platform(), 'working_root': str(ROOT),
           'git_commit': subprocess.run(['git','rev-parse','HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip() or 'UNAVAILABLE',
           'dependencies': {}, 'inputs': {}, 'steps': [], 'status': 'RUNNING',
           'source_sha256': {name: sha256(ROOT / name) for name in (
               'research/src/run_experiments.py',
               'research/src/evolution/budgeted.py',
               'research/src/run_baselines.py')}}
    for package in PACKAGES:
        try: run['dependencies'][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError: run['dependencies'][package] = 'NOT INSTALLED'
    manifest = target / 'manifest.json'
    def save(): manifest.write_text(json.dumps(run, indent=2), encoding='utf-8')
    save()
    py = sys.executable
    def step(name, *cmd):
        try:
            value = execute(list(cmd), logs, name)
            run['steps'].append(value)
            save()
        except Exception as exc:
            run['status'] = 'FAILED'; run['error'] = str(exc); save()
            raise
    try:
        step('unit_tests', py, '-m', 'pytest', '-q', 'research/tests', 'prototype/tests')
        if args.phase in ('smoke','all'):
            step('synthetic_evolutionary_smoke', py, '-m', 'research.src.run_experiments', '--synthetic-smoke', '--mode', 'quick', '--optimisation', args.optimisation, '--output-dir', str(target/'synthetic_search'))
            step('demo_model', py, '-m', 'prototype.train_demo_model', '--output', str(target/'demo_pipeline.joblib'), '--csv-output', str(target/'demo_rows.csv'))
            step('demo_replay', py, '-m', 'prototype.windows_ids', 'replay', '--csv', str(target/'demo_rows.csv'), '--model', str(target/'demo_pipeline.joblib'), '--output', str(target/'demo_scored.csv'))
        if args.phase in ('full','all'):
            for kind, filename in [('train', args.train), ('test',args.test)]:
                path = (ROOT / filename).resolve()
                if not path.is_file():
                    raise FileNotFoundError(f'{kind} CSV not found: {path}')
                run['inputs'][kind] = {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha256(path)}
                save()
            common = ('--train', args.train, '--test',args.test, '--seeds',*[str(v) for v in args.seeds])
            step('official_baselines', py, '-m','research.src.run_baselines',*common,'--output-dir',str(target/'baselines'))
            step('official_evolutionary_search',py,'-m','research.src.run_experiments','--mode','full','--optimisation',args.optimisation,*common,
                 '--methods','GA','BPSO','PSO','NSGA-II','--budget',str(args.budget),
                 '--population',str(args.population),'--search-train-size',str(args.search_train_size),
                 '--search-valid-size',str(args.search_valid_size),'--output-dir',str(target/'optimisers'))
        if args.monitor:
            step('passive_socket_snapshot',py,'-m','prototype.windows_ids','monitor','--iterations','1')
        run['status']='PASS'
        print(f'\nRUN PASSED. Results and logs: {target}')
        return 0
    except Exception as exc:
        run['status']='FAILED';run['error']=str(exc)
        print(f'\nRUN FAILED: {exc}', file=sys.stderr)
        return 1
    finally:
        run['finished_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
        save()

if __name__ == '__main__':
    raise SystemExit(main())