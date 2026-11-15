"""Compare a fresh completed protocol run to the historical report summary.

This is a descriptive comparison, not a statistical significance test.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

HISTORICAL = {'GA': (0.865394, 10.2), 'BPSO': (0.861518, 12.2),
              'PSO': (0.859817, 11.4), 'NSGA-II': (0.856150, 10.6)}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',help='Full protocol run directory (default latest)')
    args=parser.parse_args()
    if args.run:
        folder=Path(args.run)
    else:
        base=Path('results/protocol_runs')
        candidates=sorted(base.glob('*_full*'))
        if not candidates:
            parser.error('No full protocol runs available')
        folder=candidates[-1]
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('status')!='PASS' or manifest.get('phase')!='full':
        parser.error('Selected run was not a completed official full run')
    if manifest.get('configuration', {}).get('optimisation') == 'joint':
        print('WARNING: Joint HPO changes the search space; historical feature-only values are not directly protocol-equivalent.')
    runs=pd.read_csv(folder/'optimisers/runs.csv')
    if not (len(runs)==20 and runs['fitness_evaluations'].eq(300).all()):
        parser.error('Expected 20 rows and exactly 300 evaluations per method/seed')
    summary=pd.read_csv(folder/'optimisers/summary.csv')
    summary.columns=[c if not c.startswith('Unnamed:') else 'method' for c in summary.columns]
    rows=[]
    for method,(f1,features) in HISTORICAL.items():
        subset=summary.loc[summary['method']==method]
        if len(subset)!=1:
            parser.error(f'Missing method {method}')
        new_f1=float(subset.iloc[0]['macro_f1_mean'])
        new_feat=float(subset.iloc[0]['mean_features'])
        rows.append({'method':method,'historical_macro_f1':f1,'new_macro_f1':new_f1,
                     'delta_macro_f1':new_f1-f1,'historical_mean_features':features,
                     'new_mean_features':new_feat,'delta_features':new_feat-features})
    result=pd.DataFrame(rows)
    result.to_csv(folder/'historical_vs_new.csv',index=False)
    print(result.to_string(index=False, float_format=lambda x:f'{x:.6f}'))
    print('Descriptive comparison only. Configuration identity is not verified.')

if __name__=='__main__':main()