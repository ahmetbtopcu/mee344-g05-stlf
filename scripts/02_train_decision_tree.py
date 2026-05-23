#!/usr/bin/env python3
"""Train tuned Decision Tree regressor."""

import json
import sys
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mee344_g05.config import MODELS_DIR, TARGET_COL, TRAIN_PARQUET
from mee344_g05.features import get_feature_columns
from mee344_g05.tuning import tune_decision_tree


def main():
    train = pd.read_parquet(TRAIN_PARQUET)
    feat_cols = get_feature_columns(train)
    X = train[feat_cols]
    y = train[TARGET_COL]

    print("Tuning Decision Tree...")
    search = tune_decision_tree(X, y)
    best = search.best_estimator_
    print(f"Best CV RMSE: {-search.best_score_:.2f}")
    print(f"Best params: {search.best_params_}")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model": best, "feature_columns": feat_cols},
        MODELS_DIR / "decision_tree.joblib",
    )

    params_path = MODELS_DIR / "best_params.json"
    existing = {}
    if params_path.exists():
        existing = json.loads(params_path.read_text(encoding="utf-8"))
    existing["decision_tree"] = {
        "params": search.best_params_,
        "cv_rmse": float(-search.best_score_),
    }
    params_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    print(f"Saved: {MODELS_DIR / 'decision_tree.joblib'}")


if __name__ == "__main__":
    main()
