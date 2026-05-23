"""Hyperparameter search."""

from __future__ import annotations

from sklearn.model_selection import GridSearchCV

from .config import RANDOM_STATE
from .evaluation import time_series_cv
from .models import build_adaboost, build_decision_tree


def tune_decision_tree(X, y, n_jobs: int = -1):
    model = build_decision_tree()
    param_grid = {
        "max_depth": [3, 5, 8, 12, 16, None],
        "min_samples_split": [2, 5, 10, 20],
        "min_samples_leaf": [1, 2, 5, 10],
        "max_features": [None, "sqrt", 0.7],
    }
    search = GridSearchCV(
        model,
        param_grid,
        cv=time_series_cv(),
        scoring="neg_root_mean_squared_error",
        n_jobs=n_jobs,
        refit=True,
    )
    search.fit(X, y)
    return search


def tune_adaboost(X, y, n_jobs: int = -1):
    model = build_adaboost()
    param_grid = {
        "estimator__max_depth": [3, 5, 8],
        "n_estimators": [50, 100, 200],
        "learning_rate": [0.05, 0.1, 0.5, 1.0],
        "loss": ["linear", "square"],
    }
    search = GridSearchCV(
        model,
        param_grid,
        cv=time_series_cv(),
        scoring="neg_root_mean_squared_error",
        n_jobs=n_jobs,
        refit=True,
    )
    search.fit(X, y)
    return search
