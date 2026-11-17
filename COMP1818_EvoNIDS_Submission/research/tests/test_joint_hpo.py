import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import joblib
from research.src.evolution.budgeted import Budget, run
from research.src.run_experiments import (HPO_BITS, HPO_OPTIONS, decode_joint,
                                         evaluate_method, synthetic_data)
from tools.audit_historical_equivalence import audit


def test_joint_decode_and_feature_count():
    bits=np.zeros(3+HPO_BITS,dtype=int)
    bits[1]=1
    bits[3:]=[1,1, 0,1, 1,0, 0,0]
    mask,hyper=decode_joint(bits,3)
    assert mask.tolist()==[False,True,False]
    assert hyper=={'n_estimators':200,'max_depth':12,'min_samples_leaf':4,'max_features':'sqrt'}
    with pytest.raises(ValueError):decode_joint(np.r_[np.zeros(3,dtype=int),bits[3:]],3)


def test_joint_cache_distinguishes_rf_parameters():
    seen=[]
    def evaluate(candidate):
        seen.append(candidate.copy())
        return 0.8
    objective=Budget(evaluate,3+HPO_BITS,2,feature_count=3)
    a=np.zeros(3+HPO_BITS,dtype=int);a[0]=1
    b=a.copy();b[3]=1
    assert objective.assess(a) is objective.assess(a)
    assert objective.assess(b).n_features==1
    assert objective.used==len(seen)==2


@pytest.mark.parametrize('method',['GA','BPSO','PSO','NSGA-II'])
def test_joint_all_algorithms_equal_candidate_budget(method):
    objective=Budget(lambda genotype: .7,4+HPO_BITS,12,feature_count=4)
    best,front=run(method,objective,42,**({'population':4} if method in ('GA','NSGA-II') else {'particles':4}))
    assert objective.used==12
    assert all(r.n_features==sum(r.mask[:4]) for r in objective.cache.values())
    assert best.n_features>=1


def test_joint_real_pipeline_exports_selected_params(tmp_path):
    X,y,xt,yt=synthetic_data(120)
    out=tmp_path/'experiment';out.mkdir()
    result=evaluate_method('GA',42,X,y,xt,yt,12,65,18,5,9,out,4,'joint')
    assert result['fitness_evaluations']==12
    assert result['selected_features']>=1
    params=json.loads(result['rf_hyperparameters'])
    assert all(params[name] in options for name,options in HPO_OPTIONS.items())
    model=joblib.load(out/'models/ga_rf_joint_pipeline.joblib')
    rf=model.named_steps['classifier']
    assert all(getattr(rf,k)==v for k,v in params.items())
    assert (out/'models/ga_rf_joint_hyperparameters.json').is_file()
    assert len(model.predict(xt[model.feature_names_in_]))==len(xt)


def test_historical_audit_fails_closed():
    base={'dataset_sha256':{'train':'A','test':'B'},'source_sha256':{'x':'hash'},
          'dependencies':{'numpy':'2'},'configuration':{'optimisation':'features'},
          'per_seed_results_sha256':'123'}
    assert audit(base,base)==(True,[])
    modified={**base,'configuration':{'optimisation':'joint'}}
    assert not audit(base,modified)[0]
    assert not audit({'result_mean':.86},modified)[0]


def test_joint_cli_dispatch_records_actual_hyperparameters(tmp_path):
    """CLI integration test: --optimisation joint must reach evaluate_method."""
    from research.src.run_experiments import main
    out = tmp_path / "joint_cli"
    main(["--synthetic-smoke", "--mode", "quick", "--optimisation", "joint",
          "--methods", "GA", "--seeds", "42", "--budget", "2",
          "--population", "4", "--output-dir", str(out)])
    df = pd.read_csv(out / "runs.csv")
    assert len(df) == 1
    assert df.loc[0, "optimisation"] == "joint"
    assert df.loc[0, "unique_candidate_definition"] == "feature mask + RF hyperparameters"
    params = json.loads(df.loc[0, "rf_hyperparameters"])
    assert set(params) == set(HPO_OPTIONS)
    assert df.loc[0, "fitness_evaluations"] == 2
