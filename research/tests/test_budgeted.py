import numpy as np
import pytest
from research.src.evolution.budgeted import Budget, run, fronts, Assessment, BudgetExhausted
from research.src.run_experiments import make_pipeline, synthetic_data

@pytest.mark.parametrize('method', ['GA','BPSO','PSO','NSGA-II'])
def test_equal_unique_evaluations(method):
    seen=[]
    def f(mask):
        seen.append(tuple(mask))
        return .5+ .02*float(mask[0])
    budget=Budget(f,9,18)
    best,pareto=run(method,budget,42,**({'population':4} if method in ('GA','NSGA-II') else {'particles':4}))
    assert budget.used==18
    assert len(set(seen))==18
    assert 0<best.n_features<=9
    assert 0<=best.macro_f1<=1
    assert bool(pareto)==(method=='NSGA-II')

def test_cache_uncharged_and_budget_limit():
    count=[0]
    def evaluate(mask):count[0]+=1;return .8
    budget=Budget(evaluate,4,1)
    assert budget.assess([1,0,0,0])==budget.assess([1,0,0,0])
    assert count[0]==1
    with pytest.raises(BudgetExhausted):budget.assess([0,1,0,0])

def test_pareto_non_dominated():
    a=Assessment((1,0,0),.8,1,.8)
    b=Assessment((1,1,0),.9,2,.9)
    c=Assessment((1,1,1),.5,3,.5)
    layers=fronts([a,b,c]);assert set(layers[0])=={a,b};assert layers[1]==[c]

def test_pipeline_raw_input_columns():
    X,y,_,_=synthetic_data(100)
    model=make_pipeline(X,42,5).fit(X,y)
    assert list(model.feature_names_in_)==list(X.columns)
    assert len(model.predict(X.iloc[:2]))==2