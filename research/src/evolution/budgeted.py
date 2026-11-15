"""Four independent evolutionary feature-subset searches with equal *unique* budgets.

All masks represent raw UNSW-NB15 columns, not one-hot transformed columns.
The cache charges exactly once per distinct nonempty mask. No test records are
used by these search routines. NSGA-II uses independent objectives and a
validation-only compromise rule, not the scalar fitness function.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


class BudgetExhausted(RuntimeError):
    pass


@dataclass(frozen=True)
class Assessment:
    mask: tuple[int, ...]
    macro_f1: float
    n_features: int
    scalar: float


class Budget:
    def __init__(self, evaluator, n_features: int, maximum: int, penalty: float = 0.05, feature_count: int | None = None):
        if maximum < 1 or n_features < 1:
            raise ValueError('Budget and number of features must be positive')
        self.evaluator = evaluator
        self.n_features = n_features
        self.feature_count = n_features if feature_count is None else feature_count
        if not 1 <= self.feature_count <= n_features:
            raise ValueError("Invalid feature-bit count")
        self.maximum = maximum
        self.penalty = float(penalty)
        self.cache: dict[tuple[int, ...], Assessment] = {}

    @property
    def used(self) -> int:
        return len(self.cache)

    def assess(self, mask) -> Assessment:
        a = np.asarray(mask, dtype=np.int8)
        if a.shape != (self.n_features,):
            raise ValueError('Wrong mask dimensions')
        if not np.all((a == 0) | (a == 1)) or not a[:self.feature_count].any():
            raise ValueError('Mask must be binary and nonempty')
        key = tuple(int(z) for z in a)
        if key not in self.cache:
            if self.used >= self.maximum:
                raise BudgetExhausted(f'Budget reached: {self.maximum}')
            f1 = float(self.evaluator(a.astype(bool)))
            if not np.isfinite(f1) or not (0 <= f1 <= 1):
                raise ValueError(f'Invalid validation Macro-F1: {f1}')
            n = int(a[:self.feature_count].sum())
            self.cache[key] = Assessment(key, f1, n, f1 - self.penalty*n/self.feature_count)
        return self.cache[key]


def _nonempty(bits, rng, feature_count=None):
    bits = np.asarray(bits, dtype=np.int8).copy()
    if feature_count is None: feature_count = len(bits)
    if not bits[:feature_count].any():
        bits[int(rng.integers(feature_count))] = 1
    return bits


def _random_new(budget, rng, tries=1000):
    """Generate a cache miss where possible; terminate gracefully on tiny spaces."""
    n = budget.n_features
    if n <= 20 and budget.used >= (1 << n) - 1:
        return None
    for _ in range(tries):
        bits = _nonempty(rng.integers(0,2,size=n,dtype=np.int8),rng,budget.feature_count)
        if tuple(bits) not in budget.cache:
            return bits
    return None


def _record(budget, candidate):
    try:
        return budget.assess(candidate)
    except BudgetExhausted:
        return None


def _pad_budget(budget, rng):
    while budget.used < budget.maximum:
        candidate = _random_new(budget,rng)
        if candidate is None:
            break
        budget.assess(candidate)


def _tournament(pop, budget, rng, size=3):
    idx=rng.integers(0,len(pop),size=size)
    return max((pop[int(i)] for i in idx),key=lambda m:budget.cache[tuple(m)].scalar).copy()


def ga(budget, rng, population=8, mutation=0.05, crossover=0.8):
    n=budget.n_features
    pop=[]
    while len(pop)<population and budget.used<budget.maximum:
        m=_random_new(budget,rng)
        if m is None: break
        budget.assess(m);pop.append(m)
    if not pop: raise RuntimeError('No valid feature subsets')
    while budget.used<budget.maximum:
        offspring=[]; before=budget.used
        while len(offspring)<population and budget.used<budget.maximum:
            a=_tournament(pop,budget,rng);b=_tournament(pop,budget,rng)
            if n>1 and rng.random()<crossover:
                k=int(rng.integers(1,n));a[k:],b[k:]=b[k:].copy(),a[k:].copy()
            for child in (a,b):
                child=_nonempty(child ^ (rng.random(n)<mutation).astype(np.int8),rng,budget.feature_count)
                _record(budget,child)
                if tuple(child) in budget.cache: offspring.append(child)
                if len(offspring)>=population or budget.used>=budget.maximum:break
        pop=sorted(pop+offspring,key=lambda m:budget.cache[tuple(m)].scalar,reverse=True)[:population]
        if budget.used==before:
            m=_random_new(budget,rng)
            if m is None:break
            budget.assess(m)
            pop[-1]=m
    _pad_budget(budget,rng)


def bpso(budget, rng, particles=8, inertia=0.7, cognitive=1.5, social=1.5):
    n=budget.n_features
    x=np.array([_nonempty(rng.integers(0,2,size=n),rng,budget.feature_count) for _ in range(particles)])
    v=rng.normal(size=(particles,n))
    pb=x.copy(); pf=np.full(particles,-np.inf)
    gb=x[0].copy(); gf=-np.inf; stagnant=0
    while budget.used<budget.maximum:
        before=budget.used
        for i in range(particles):
            val=_record(budget,x[i])
            if val is None:break
            if val.scalar>pf[i]:pf[i]=val.scalar;pb[i]=x[i].copy()
            if val.scalar>gf:gf=val.scalar;gb=x[i].copy()
        r1=rng.random((particles,n));r2=rng.random((particles,n))
        v=inertia*v+cognitive*r1*(pb-x)+social*r2*(gb-x)
        sigmoid=1/(1+np.exp(-np.clip(v,-30,30)))
        x=np.array([_nonempty(z,rng,budget.feature_count) for z in (rng.random((particles,n))<sigmoid).astype(np.int8)])
        stagnant=stagnant+1 if budget.used==before else 0
        if stagnant>=5:
            extra=_random_new(budget,rng)
            if extra is None:break
            budget.assess(extra);stagnant=0
    _pad_budget(budget,rng)


def pso(budget,rng,particles=8,inertia=0.7,cognitive=1.5,social=1.5,threshold=0.5):
    """Continuous-position PSO, thresholded to binary at evaluation time."""
    n=budget.n_features
    x=rng.random((particles,n)); v=rng.normal(0,0.1,(particles,n))
    pb=x.copy();pf=np.full(particles,-np.inf);gb=x[0].copy();gf=-np.inf
    stagnant=0
    while budget.used<budget.maximum:
        before=budget.used
        for i in range(particles):
            mask=_nonempty((x[i]>=threshold).astype(np.int8),rng,budget.feature_count)
            val=_record(budget,mask)
            if val is None:break
            if val.scalar>pf[i]:pf[i]=val.scalar;pb[i]=x[i].copy()
            if val.scalar>gf:gf=val.scalar;gb=x[i].copy()
        v=inertia*v+cognitive*rng.random((particles,n))*(pb-x)+social*rng.random((particles,n))*(gb-x)
        x=np.clip(x+v,0,1)
        stagnant=stagnant+1 if before==budget.used else 0
        if stagnant>=5:
            x[int(rng.integers(particles))]=rng.random(n)
            extra=_random_new(budget,rng)
            if extra is None:break
            budget.assess(extra);stagnant=0
    _pad_budget(budget,rng)


def _dominates(a,b):
    return a.macro_f1>=b.macro_f1 and a.n_features<=b.n_features and (a.macro_f1>b.macro_f1 or a.n_features<b.n_features)


def fronts(records):
    """NSGA-II non-dominated sorting; objective ordering is F1↑, features↓."""
    items=list(records)
    dominates=[[] for _ in items]; count=[0]*len(items);layers=[]
    for i,a in enumerate(items):
        for j,b in enumerate(items):
            if i==j:continue
            if _dominates(a,b):dominates[i].append(j)
            elif _dominates(b,a):count[i]+=1
    current=[i for i,c in enumerate(count) if c==0]
    while current:
        layers.append([items[i] for i in current]);nxt=[]
        for i in current:
            for j in dominates[i]:
                count[j]-=1
                if count[j]==0:nxt.append(j)
        current=nxt
    return layers


def crowding(items):
    if len(items)<3:return {x.mask:float('inf') for x in items}
    dist={x.mask:0. for x in items}
    for accessor in (lambda a:a.macro_f1,lambda a:a.n_features):
        ordered=sorted(items,key=accessor)
        dist[ordered[0].mask]=dist[ordered[-1].mask]=float('inf')
        scale=accessor(ordered[-1])-accessor(ordered[0])
        if scale:
            for i in range(1,len(ordered)-1):
                if np.isfinite(dist[ordered[i].mask]):
                    dist[ordered[i].mask]+=(accessor(ordered[i+1])-accessor(ordered[i-1]))/scale
    return dist


def _nsga_select(items,size):
    chosen=[]
    for layer in fronts(items):
        if len(chosen)+len(layer)<=size:chosen.extend(layer)
        else:
            d=crowding(layer)
            chosen.extend(sorted(layer,key=lambda a:d[a.mask],reverse=True)[:size-len(chosen)])
            break
    return chosen


def nsga2(budget,rng,population=20,mutation=0.05,crossover=0.8):
    n=budget.n_features
    pop=[]
    while len(pop)<population and budget.used<budget.maximum:
        x=_random_new(budget,rng)
        if x is None:break
        pop.append(budget.assess(x))
    while budget.used<budget.maximum:
        before=budget.used;children=[]
        ranks={r.mask:i for i,layer in enumerate(fronts(pop)) for r in layer}
        distance={k:v for layer in fronts(pop) for k,v in crowding(layer).items()}
        def choice():
            a,b=rng.choice(len(pop),size=2,replace=True)
            p,q=pop[int(a)],pop[int(b)]
            return p if (ranks[p.mask],-distance[p.mask]) < (ranks[q.mask],-distance[q.mask]) else q
        while len(children)<population and budget.used<budget.maximum:
            a=np.array(choice().mask,dtype=np.int8);b=np.array(choice().mask,dtype=np.int8)
            if n>1 and rng.random()<crossover:
                point=int(rng.integers(1,n));a[point:],b[point:]=b[point:].copy(),a[point:].copy()
            for c in (a,b):
                c=_nonempty(c ^ (rng.random(n)<mutation).astype(np.int8),rng,budget.feature_count)
                val=_record(budget,c)
                if val is not None:children.append(val)
                if len(children)>=population or budget.used>=budget.maximum:break
        pop=_nsga_select(list({r.mask:r for r in pop+children}.values()),population)
        if budget.used==before:
            extra=_random_new(budget,rng)
            if extra is None:break
            pop=_nsga_select(pop+[budget.assess(extra)],population)
    _pad_budget(budget,rng)
    # Final Pareto candidates from ALL evaluated masks, not just survivor population.
    return fronts(budget.cache.values())[0]


def compromise(pareto,n_features):
    """Fixed validation-only ideal-point distance, objectives [1-F1, fraction]."""
    if not pareto: raise ValueError('No Pareto candidates')
    return min(pareto,key=lambda a:((1-a.macro_f1)**2+(a.n_features/n_features)**2,a.n_features,a.mask))


def run(method,budget,seed,**kwargs):
    rng=np.random.default_rng(seed)
    methods={'GA':ga,'BPSO':bpso,'PSO':pso,'NSGA-II':nsga2}
    if method not in methods:raise ValueError(f'Unknown method: {method}')
    pareto=methods[method](budget,rng,**kwargs)
    if method=='NSGA-II':
        best=compromise(pareto,budget.feature_count)
    else:
        best=max(budget.cache.values(),key=lambda a:(a.scalar,-a.n_features))
    return best,pareto