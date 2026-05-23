"""Model builders."""

from __future__ import annotations

from sklearn.ensemble import AdaBoostRegressor
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor


def build_decision_tree(**kwargs) -> DecisionTreeRegressor:
    defaults = dict(random_state=42)
    defaults.update(kwargs)
    return DecisionTreeRegressor(**defaults)


def build_adaboost(**kwargs) -> AdaBoostRegressor:
    defaults = dict(
        estimator=DecisionTreeRegressor(max_depth=5, random_state=42),
        n_estimators=100,
        learning_rate=0.1,
        random_state=42,
    )
    defaults.update(kwargs)
    return AdaBoostRegressor(**defaults)


def build_dt_pipeline(dt_params: dict | None = None) -> Pipeline:
    params = dt_params or {}
    return Pipeline([("model", build_decision_tree(**params))])


def build_ada_pipeline(ada_params: dict | None = None) -> Pipeline:
    params = ada_params or {}
    base = params.pop("base_max_depth", 5)
    estimator = DecisionTreeRegressor(max_depth=base, random_state=42)
    ada = AdaBoostRegressor(estimator=estimator, random_state=42, **params)
    return Pipeline([("model", ada)])
