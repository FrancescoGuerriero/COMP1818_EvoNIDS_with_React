"""Reproduce 42-feature baselines independently, without using test data for tuning."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from research.src.run_experiments import SEEDS, load_official, make_pipeline, metrics


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--train',default='data/raw/UNSW_NB15_training-set.csv')
    parser.add_argument('--test',default='data/raw/UNSW_NB15_testing-set.csv')
    parser.add_argument('--seeds',nargs='+',type=int,default=list(SEEDS))
    parser.add_argument('--output-dir',default='results/reproduction_baselines')
    args=parser.parse_args()
    X,y,Xte,yte=load_official(args.train,args.test)
    num=list(X.select_dtypes(include='number').columns);cat=[c for c in X if c not in num]
    pre=ColumnTransformer([('num',Pipeline([('fill',SimpleImputer(strategy='median')),('scale',StandardScaler())]),num),
      ('cat',Pipeline([('fill',SimpleImputer(strategy='most_frequent')),('encode',OneHotEncoder(handle_unknown='ignore'))]),cat)])
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    data=[]
    for seed in args.seeds:
        classifiers={'Dummy':DummyClassifier(strategy='most_frequent'),
            'Logistic Regression':Pipeline([('pre',pre),('model',LogisticRegression(max_iter=2000,class_weight='balanced',random_state=seed))]),
            'Random Forest':make_pipeline(X,seed,200)}
        try:
            from xgboost import XGBClassifier
            classifiers['XGBoost']=Pipeline([('pre',pre),('model',XGBClassifier(n_estimators=200,max_depth=6,
              learning_rate=.05,subsample=.9,colsample_bytree=.9,random_state=seed,n_jobs=1,eval_metric='logloss'))])
        except ImportError:print('xgboost not installed: skipping XGBoost')
        for name,model in classifiers.items():
            model.fit(X,y);values=metrics(yte,model.predict(Xte))
            row={'model':name,'seed':seed,'features':len(X.columns),**values}
            data.append(row);print(name,seed,values['macro_f1'])
            pd.DataFrame(data).to_csv(out/'baseline_runs.csv',index=False)
    pd.DataFrame(data).groupby('model').agg(macro_f1_mean=('macro_f1','mean'),
        macro_f1_std=('macro_f1','std'),false_positive_rate_mean=('false_positive_rate','mean')).to_csv(out/'baseline_summary.csv')

if __name__=='__main__':main()