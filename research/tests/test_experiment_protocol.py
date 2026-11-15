from pathlib import Path
import numpy as np
import pytest
from research.src.evolution.budgeted import Budget
from research.src.run_experiments import load_official, make_pipeline, synthetic_data
from prototype.replay import score_csv
import joblib


def test_budget_deduplicates_and_exhausts():
    budget=Budget(lambda mask: 0.8, 3, 1)
    first=budget.assess([1,0,0]); second=budget.assess([1,0,0])
    assert first is second and budget.used==1
    with pytest.raises(Exception): budget.assess([0,1,0])


def test_official_partition_excludes_label_and_attack_category(tmp_path):
    import pandas as pd
    frame=pd.DataFrame({'id':[1,2,3,4],'attack_cat':['Normal','Attack']*2,
                        'sbytes':[1,2,3,4],'service':['http','dns']*2,'label':[0,1,0,1]})
    tr=tmp_path/'train.csv';te=tmp_path/'test.csv'
    frame.to_csv(tr,index=False);frame.to_csv(te,index=False)
    x,y,xt,yt=load_official(tr,te)
    assert list(x.columns)==['sbytes','service']
    assert len(x)==4 and y.nunique()==2 and len(xt)==4


def test_exported_pipeline_replays(tmp_path):
    X,y,xt,yt=synthetic_data(90)
    model=make_pipeline(X,42,trees=4)
    model.fit(X,y)
    path=tmp_path/'model.joblib'; rows=tmp_path/'rows.csv'
    joblib.dump(model,path);xt.head(3).to_csv(rows,index=False)
    scored=score_csv(rows,path)
    assert len(scored)==3
    assert set(scored['ids_prediction'].unique()).issubset({0,1})
    assert 'attack_probability' in scored