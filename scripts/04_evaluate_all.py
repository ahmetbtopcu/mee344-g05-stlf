#!/usr/bin/env python3
"""Evaluate baselines, DT, AdaBoost on hold-out test set."""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mee344_g05.config import FIGURES_DIR, MODELS_DIR, REPORTS_DIR, TARGET_COL, TEST_PARQUET, TRAIN_PARQUET
from mee344_g05.evaluation import compute_metrics, save_metrics
from mee344_g05.features import get_feature_columns
from mee344_g05.plotting import (
    plot_actual_vs_pred,
    plot_feature_importance,
    plot_metrics_comparison,
    plot_residuals,
)


def baseline_last_hour(test: pd.DataFrame, train: pd.DataFrame) -> np.ndarray:
    full = pd.concat([train[[TARGET_COL]], test[[TARGET_COL]]])
    return full[TARGET_COL].shift(1).loc[test.index].values


def baseline_seasonal(test: pd.DataFrame, train: pd.DataFrame) -> np.ndarray:
    full = pd.concat([train[[TARGET_COL]], test[[TARGET_COL]]])
    return full[TARGET_COL].shift(168).loc[test.index].values


def get_importance(model, feature_cols: list[str]) -> dict:
    if hasattr(model, "feature_importances_"):
        imp = model.feature_importances_
    elif hasattr(model, "estimators_"):
        imp = np.mean(
            [getattr(e, "feature_importances_", np.zeros(len(feature_cols))) for e in model.estimators_],
            axis=0,
        )
    else:
        return {}
    return dict(zip(feature_cols, imp.tolist()))


def main():
    train = pd.read_parquet(TRAIN_PARQUET)
    test = pd.read_parquet(TEST_PARQUET)
    feat_cols = get_feature_columns(train)
    y_true = test[TARGET_COL].values
    index = test.index

    results = {"test": {}, "cv": {}}
    params = json.loads((MODELS_DIR / "best_params.json").read_text(encoding="utf-8"))
    results["cv"] = {
        "decision_tree": params.get("decision_tree", {}).get("cv_rmse"),
        "adaboost": params.get("adaboost", {}).get("cv_rmse"),
    }

    preds = {
        "baseline_last_hour": baseline_last_hour(test, train),
        "baseline_seasonal_168h": baseline_seasonal(test, train),
    }

    for name, pred in preds.items():
        mask = ~np.isnan(pred)
        results["test"][name] = compute_metrics(y_true[mask], pred[mask])

    for model_name in ["decision_tree", "adaboost"]:
        bundle = joblib.load(MODELS_DIR / f"{model_name}.joblib")
        model = bundle["model"]
        cols = bundle["feature_columns"]
        pred = model.predict(test[cols])
        preds[model_name] = pred
        results["test"][model_name] = compute_metrics(y_true, pred)

        plot_actual_vs_pred(
            y_true,
            pred,
            index,
            f"{model_name.replace('_', ' ').title()} — Test Set",
            f"{model_name}_actual_vs_pred.png",
        )
        plot_residuals(y_true, pred, model_name, f"{model_name}_residuals.png")
        imp = get_importance(model, cols)
        if imp:
            plot_feature_importance(
                imp,
                f"{model_name.replace('_', ' ').title()} Feature Importance",
                f"{model_name}_importance.png",
            )

    for bname, pred in list(preds.items())[:2]:
        mask = ~np.isnan(pred)
        plot_actual_vs_pred(
            y_true[mask],
            pred[mask],
            index[mask],
            bname,
            f"{bname}_actual_vs_pred.png",
        )

    save_metrics(results, REPORTS_DIR / "metrics.json")
    plot_metrics_comparison(results)

    print("Test metrics:")
    for m, v in results["test"].items():
        print(f"  {m}: RMSE={v['rmse']:.2f} MAE={v['mae']:.2f} R2={v['r2']:.4f} MAPE={v['mape']:.2f}%")
    print(f"Saved: {REPORTS_DIR / 'metrics.json'}")


if __name__ == "__main__":
    main()
