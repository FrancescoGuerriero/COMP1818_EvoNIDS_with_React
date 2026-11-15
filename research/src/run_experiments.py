"""Leakage-safe feature selection with GA/BPSO/PSO/NSGA-II on official UNSW-NB15.

To prevent accidental replacement of published results, writes only to the
explicit --output-dir (default results/reproduction_runs).
"""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (balanced_accuracy_score, confusion_matrix,
                             f1_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from research.src.evolution.budgeted import Budget, run

SEEDS=(42,101,202,303,404)
METHODS=('GA','BPSO','PSO','NSGA-II')

# Two encoded bits per hyperparameter; all combinations are feasible.
# Changing these options changes the experimental protocol and must be recorded.
HPO_OPTIONS = {
    'n_estimators': (40, 80, 120, 200),
    'max_depth': (None, 12, 24, 36),
    'min_samples_leaf': (1, 2, 4, 8),
    'max_features': ('sqrt', 'log2', 0.5, 1.0),
}
HPO_BITS = 2 * len(HPO_OPTIONS)


def decode_joint(chromosome, feature_count):
    """Decode a nonempty raw-column mask and four RF hyperparameters."""
    chromosome = np.asarray(chromosome, dtype=np.int8)
    if len(chromosome) != feature_count + HPO_BITS:
        raise ValueError('Joint chromosome length mismatch')
    if not chromosome[:feature_count].any():
        raise ValueError('At least one raw predictor is required')
    params = {}
    for i, (key, options) in enumerate(HPO_OPTIONS.items()):
        b0, b1 = chromosome[feature_count + 2*i:feature_count + 2*i + 2]
        params[key] = options[int(b0)*2 + int(b1)]
    return chromosome[:feature_count].astype(bool), params



def load_official(train_path,test_path):
    training=pd.read_csv(train_path); testing=pd.read_csv(test_path)
    required={'label'}
    if not required.issubset(training) or not required.issubset(testing):
        raise ValueError('Both partitions must contain the binary label column')
    exclude={'id','attack_cat','label'}
    cols=[c for c in training.columns if c not in exclude]
    if not cols or set(cols)-set(testing.columns):
        raise ValueError('Official training and testing predictors do not align')
    if training['label'].nunique()!=2 or testing['label'].nunique()!=2:
        raise ValueError('Expected binary labels in both partitions')
    return training[cols], training.label.astype(int), testing[cols], testing.label.astype(int)


def make_pipeline(X, seed, trees=80, rf_params=None):
    num=list(X.select_dtypes(include='number').columns)
    cat=[c for c in X.columns if c not in num]
    steps=[]
    if num:
        steps.append(('numeric',Pipeline([('fill',SimpleImputer(strategy='median',keep_empty_features=True))]),num))
    if cat:
        steps.append(('categorical',Pipeline([
            ('fill',SimpleImputer(strategy='most_frequent',keep_empty_features=True)),
            ('encode',OneHotEncoder(handle_unknown='ignore'))]),cat))
    pre=ColumnTransformer(steps,sparse_threshold=0.3)
    rf_args={'n_estimators':trees,'random_state':seed,'class_weight':'balanced_subsample','n_jobs':1}
    if rf_params:
        if set(rf_params) - set(HPO_OPTIONS):
            raise ValueError('Unexpected RF tuning parameter')
        rf_args.update(rf_params)
    rf=RandomForestClassifier(**rf_args)
    return Pipeline([('preprocessor',pre),('classifier',rf)])


def sample_split(X,y,seed,train_size,valid_size):
    indices=np.arange(len(X))
    tr,va=train_test_split(indices,test_size=.2,stratify=y,random_state=seed)
    rng=np.random.default_rng(seed)
    def subsample(idx,limit):
        if limit is None or limit>=len(idx):return idx
        # Stratified downsample, with fixed seed and no overlap.
        selected,_=train_test_split(idx,train_size=limit,stratify=y.iloc[idx],random_state=seed)
        return selected
    tr=subsample(tr,train_size);va=subsample(va,valid_size)
    return X.iloc[tr],y.iloc[tr],X.iloc[va],y.iloc[va]


def metrics(y, pred):
    matrix=confusion_matrix(y,pred,labels=[0,1])
    tn,fp,fn,tp=matrix.ravel()
    return dict(macro_f1=float(f1_score(y,pred,average='macro',zero_division=0)),
                balanced_accuracy=float(balanced_accuracy_score(y,pred)),
                false_positive_rate=float(fp/(fp+tn)) if fp+tn else None,
                confusion_matrix=matrix.tolist())


def evaluate_method(method,seed,X,y,X_test,y_test,budget_count,search_train_size,
                    search_valid_size,search_trees,final_trees,output,algorithm_population,optimisation="features"):
    tr,yt,va,yv=sample_split(X,y,seed,search_train_size,search_valid_size)
    columns=list(X.columns)
    if optimisation not in ('features', 'joint'):
        raise ValueError('Unknown optimisation mode')
    n_features=len(columns)
    chromosome_length=n_features + (HPO_BITS if optimisation=='joint' else 0)
    def split_candidate(chromosome):
        if optimisation=='joint':
            return decode_joint(chromosome,n_features)
        return np.asarray(chromosome,dtype=bool), {}
    def evaluator(chromosome):
        feature_mask,params=split_candidate(chromosome)
        selected=[columns[i] for i in np.flatnonzero(feature_mask)]
        model=make_pipeline(tr[selected],seed,search_trees,params)
        model.fit(tr[selected],yt)
        return f1_score(yv,model.predict(va[selected]),average='macro',zero_division=0)
    objective=Budget(evaluator,chromosome_length,budget_count,0.05,feature_count=n_features)
    started=time.perf_counter()
    kw={'population':algorithm_population} if method in ('GA','NSGA-II') else {'particles':algorithm_population}
    selected,pareto=run(method,objective,seed,**kw)
    optimisation_seconds=time.perf_counter()-started
    final_mask,final_params=split_candidate(selected.mask)
    names=[columns[i] for i in np.flatnonzero(final_mask)]
    # Fixed-feature mode preserves the previous final-tree default. In joint
    # mode, the selected classifier settings are used for final refitting.
    final=make_pipeline(X[names],seed,final_trees,final_params)
    final.fit(X[names],y)
    pred=final.predict(X_test[names])
    stats=metrics(y_test,pred)
    if method=='NSGA-II':
        pd.DataFrame([{'macro_f1_validation':p.macro_f1,'n_features':p.n_features,
                       'features':json.dumps([columns[i] for i in np.flatnonzero(split_candidate(p.mask)[0])]),
                       'rf_hyperparameters':json.dumps(split_candidate(p.mask)[1])}
                      for p in pareto]).to_csv(output/f'pareto_seed_{seed}.csv',index=False)
    if method=='GA' and seed==42:
        path=output/'models'/('ga_rf_joint_pipeline.joblib' if optimisation=='joint' else 'ga_rf_pipeline.joblib')
        path.parent.mkdir(parents=True,exist_ok=True)
        joblib.dump(final,path)
        (path.parent/('ga_rf_joint_features.json' if optimisation=='joint' else 'ga_rf_features.json')).write_text(json.dumps(names,indent=2))
        if optimisation=='joint':
            (path.parent/'ga_rf_joint_hyperparameters.json').write_text(json.dumps(final_params,indent=2))
    return dict(method=method,seed=seed,optimisation=optimisation,
                rf_hyperparameters=json.dumps(final_params,sort_keys=True),
                unique_candidate_definition=('feature mask + RF hyperparameters' if optimisation=='joint' else 'feature mask'),
                fitness_evaluations=objective.used,
                validation_macro_f1=selected.macro_f1,selected_features=len(names),
                feature_reduction_pct=100*(1-len(names)/len(columns)),
                selected_feature_names=json.dumps(names),optimisation_seconds=optimisation_seconds,
                **stats)


def synthetic_data(rows=250, seed=123):
    """Only for smoke testing; never mix with official test measurements."""
    rng=np.random.default_rng(seed)
    X=pd.DataFrame({f'feature_{i}':rng.normal(size=rows) for i in range(8)})
    X['proto']=rng.choice(['tcp','udp'],rows)
    y=pd.Series(((X.feature_0+X.feature_1-X.feature_2+(X.proto=='tcp')*.4)>0).astype(int),name='label')
    split=int(rows*.7)
    return X.iloc[:split],y.iloc[:split],X.iloc[split:],y.iloc[split:]


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode',choices=['quick','full'],default='quick')
    ap.add_argument('--optimisation',choices=['features','joint'],default='features',
                    help='Legacy feature-only or joint feature+RF hyperparameter search')
    ap.add_argument('--train',default='data/raw/UNSW_NB15_training-set.csv')
    ap.add_argument('--test',default='data/raw/UNSW_NB15_testing-set.csv')
    ap.add_argument('--synthetic-smoke',action='store_true',help='Test wiring on synthetic data; not a real IDS result')
    ap.add_argument('--methods',nargs='+',choices=METHODS,default=list(METHODS))
    ap.add_argument('--seeds',nargs='+',type=int)
    ap.add_argument('--budget',type=int)
    ap.add_argument('--population',type=int)
    ap.add_argument('--search-train-size',type=int)
    ap.add_argument('--search-valid-size',type=int)
    ap.add_argument('--search-trees',type=int)
    ap.add_argument('--final-trees',type=int)
    ap.add_argument('--output-dir',default='results/reproduction_runs')
    args=ap.parse_args(argv)
    if args.synthetic_smoke:
        X,y,Xte,yte=synthetic_data()
    else:
        if not Path(args.train).is_file() or not Path(args.test).is_file():
            ap.error('UNSW-NB15 CSV files missing; supply --train and --test, or --synthetic-smoke for wiring test')
        X,y,Xte,yte=load_official(args.train,args.test)
    seeds=args.seeds or ([42] if args.mode=='quick' else list(SEEDS))
    budget=args.budget or (12 if args.mode=='quick' else 300)
    population=args.population or (4 if args.mode=='quick' else 8)
    total_bits=len(X.columns)+(HPO_BITS if args.optimisation=='joint' else 0)
    if total_bits<=20 and budget>((1<<len(X.columns))-1)*(2**(total_bits-len(X.columns))):
        ap.error('Unique candidate budget exceeds finite nonempty search space')
    search_train_size=args.search_train_size or (min(80,len(X)//2) if args.mode=='quick' else 20000)
    search_valid_size=args.search_valid_size or (min(40,len(X)//10) if args.mode=='quick' else 8000)
    search_trees=args.search_trees or (8 if args.mode=='quick' else 80)
    final_trees=args.final_trees or (12 if args.mode=='quick' else 200)
    out=Path(args.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for method in args.methods:
        for seed in seeds:
            print(f'Running {method}, seed={seed}, budget={budget}',flush=True)
            row=evaluate_method(method,seed,X,y,Xte,yte,budget,search_train_size,
                  search_valid_size,search_trees,final_trees,out,population)
            rows.append(row)
            pd.DataFrame(rows).to_csv(out/'runs.csv',index=False)
            print(f'  test Macro-F1={row["macro_f1"]:.5f}; features={row["selected_features"]}; evaluations={row["fitness_evaluations"]}',flush=True)
    frame=pd.DataFrame(rows)
    frame.groupby('method').agg(macro_f1_mean=('macro_f1','mean'),macro_f1_std=('macro_f1','std'),
         mean_features=('selected_features','mean'),mean_reduction_pct=('feature_reduction_pct','mean'),
         mean_fpr=('false_positive_rate','mean')).to_csv(out/'summary.csv')
    (out/'run_config.json').write_text(json.dumps({**vars(args),'seed_list':seeds,'budget_used':budget,
        'source':'SYNTHETIC SMOKE ONLY' if args.synthetic_smoke else 'UNSW-NB15 official partitions',
        'hpo_options':HPO_OPTIONS if args.optimisation=='joint' else None,
        'fitness_charge_unit':'distinct (mask, RF parameters)' if args.optimisation=='joint' else 'distinct mask',
        'historical_equivalence':'NOT_VERIFIED'},indent=2))
    print(f'Saved to {out}')

if __name__=='__main__':main()