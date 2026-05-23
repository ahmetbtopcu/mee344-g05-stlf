#!/usr/bin/env python3
"""Feature importance, PDP, tree plot, error analysis."""

import json
import sys
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.inspection import PartialDependenceDisplay, permutation_importance

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mee344_g05.config import FIGURES_DIR, MODELS_DIR, REPORTS_DIR, TARGET_COL, TEST_PARQUET, TRAIN_PARQUET
from mee344_g05.features import get_feature_columns
from mee344_g05.plotting import plot_feature_importance

INTERP_DIR = FIGURES_DIR / "interpretation"


def save_fig(fig, name: str) -> Path:
    INTERP_DIR.mkdir(parents=True, exist_ok=True)
    path = INTERP_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def main():
    INTERP_DIR.mkdir(parents=True, exist_ok=True)
    train = pd.read_parquet(TRAIN_PARQUET)
    test = pd.read_parquet(TEST_PARQUET)
    feat_cols = get_feature_columns(train)
    X_test = test[feat_cols]
    y_test = test[TARGET_COL]

    for model_name in ["decision_tree", "adaboost"]:
        bundle = joblib.load(MODELS_DIR / f"{model_name}.joblib")
        model = bundle["model"]
        pred = model.predict(X_test)
        resid = y_test - pred

        # Permutation importance
        perm = permutation_importance(
            model, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1
        )
        perm_imp = dict(zip(feat_cols, perm.importances_mean.tolist()))
        fig, ax = plt.subplots(figsize=(10, 6))
        items = sorted(perm_imp.items(), key=lambda x: x[1], reverse=True)[:15]
        names, vals = zip(*items)
        ax.barh(range(len(names)), vals)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names)
        ax.invert_yaxis()
        ax.set_title(f"{model_name} — Permutation Importance")
        save_fig(fig, f"{model_name}_permutation_importance.png")
        with open(INTERP_DIR / f"{model_name}_permutation.json", "w", encoding="utf-8") as f:
            json.dump(perm_imp, f, indent=2)

        # Partial dependence
        pdp_features = [c for c in ["lag_24h", "hour_sin", "prod_solar", "prod_wind"] if c in feat_cols]
        if pdp_features:
            fig, ax = plt.subplots(figsize=(12, 8))
            PartialDependenceDisplay.from_estimator(
                model, X_test, pdp_features[:4], ax=ax, n_jobs=-1
            )
            fig.suptitle(f"{model_name} — Partial Dependence")
            save_fig(fig, f"{model_name}_pdp.png")

        # Residual by hour
        tmp = test.copy()
        tmp["residual"] = resid
        tmp["hour"] = tmp.index.hour
        hourly_err = tmp.groupby("hour")["residual"].mean()
        fig, ax = plt.subplots(figsize=(10, 4))
        hourly_err.plot(kind="bar", ax=ax, color="steelblue")
        ax.axhline(0, color="red", linestyle="--")
        ax.set_title(f"{model_name} — Mean Residual by Hour")
        ax.set_xlabel("Hour")
        save_fig(fig, f"{model_name}_residual_by_hour.png")

        # Worst 10 predictions
        tmp["abs_err"] = np.abs(resid)
        worst = tmp.nlargest(10, "abs_err")[["abs_err", TARGET_COL]]
        worst["predicted"] = pred[worst.index.get_indexer(worst.index)]
        worst.to_csv(INTERP_DIR / f"{model_name}_worst_10.csv")

    # Decision tree structure (first 3 levels)
    dt_bundle = joblib.load(MODELS_DIR / "decision_tree.joblib")
    from sklearn.tree import plot_tree

    fig, ax = plt.subplots(figsize=(20, 10))
    plot_tree(
        dt_bundle["model"],
        feature_names=feat_cols,
        filled=True,
        max_depth=3,
        ax=ax,
        fontsize=8,
    )
    ax.set_title("Decision Tree (depth=3)")
    save_fig(fig, "decision_tree_structure.png")

    print(f"Interpretation outputs saved to {INTERP_DIR}")


if __name__ == "__main__":
    main()
