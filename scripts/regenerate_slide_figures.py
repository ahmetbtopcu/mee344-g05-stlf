#!/usr/bin/env python3
"""Regenerate presentation-quality figures."""

import json
import shutil
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import joblib

from mee344_g05.config import FIGURES_DIR, MODELS_DIR, REPORTS_DIR, TARGET_COL, TEST_PARQUET, TRAIN_PARQUET
from mee344_g05.data_loader import load_merged
from mee344_g05.features import build_features, get_feature_columns
from mee344_g05.preprocessing import preprocess_merged
from mee344_g05.ppt_theme import MPL_RC, NAVY, SKY, TEAL, AMBER, OFF_WHITE

OUT = FIGURES_DIR / "presentation"


def apply_style():
    plt.rcParams.update(MPL_RC)


def savefig(name: str):
    path = OUT / name
    plt.savefig(path, dpi=200, bbox_inches="tight", facecolor=OFF_WHITE)
    plt.close()
    return path


def main():
    apply_style()
    OUT.mkdir(parents=True, exist_ok=True)

    merged = preprocess_merged(load_merged())
    featured = build_features(merged)
    test = pd.read_parquet(TEST_PARQUET)
    y = test[TARGET_COL]

    # 1 Consumption series
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(merged.index, merged[TARGET_COL], color=NAVY, lw=1.2)
    ax.fill_between(merged.index, merged[TARGET_COL], alpha=0.08, color=TEAL)
    ax.set_title("Hourly Electricity Consumption — EPİAŞ", fontweight="bold")
    ax.set_ylabel("MWh")
    savefig("consumption_series.png")

    # 2 Daily profile
    hourly = merged.groupby(merged.index.hour)[TARGET_COL].agg(["mean", "std"])
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(hourly.index, hourly["mean"], color=TEAL, marker="o", lw=2)
    ax.fill_between(hourly.index, hourly["mean"] - hourly["std"], hourly["mean"] + hourly["std"], alpha=0.25, color=SKY)
    ax.set_title("Daily Load Profile", fontweight="bold")
    ax.set_xlabel("Hour")
    savefig("daily_profile.png")

    # 3 Heatmap
    tmp = merged.copy()
    tmp["h"] = tmp.index.hour
    tmp["d"] = tmp.index.dayofweek
    pivot = tmp.pivot_table(values=TARGET_COL, index="d", columns="h", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(11, 4))
    im = ax.imshow(pivot, aspect="auto", cmap="YlOrRd")
    plt.colorbar(im, ax=ax, label="MWh")
    ax.set_title("Weekly Pattern (Day × Hour)", fontweight="bold")
    savefig("weekly_heatmap.png")

    # 4 Production mix
    sources = [c for c in ["dogal_gaz", "barajli", "linyit", "ruzgar", "gunes", "ithal_komur"] if c in merged.columns]
    means = merged[sources].mean().sort_values()
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = plt.cm.Blues(np.linspace(0.35, 0.9, len(means)))
    means.plot(kind="barh", ax=ax, color=colors)
    ax.set_title("Average Generation Mix", fontweight="bold")
    savefig("production_mix.png")

    # 5 Metrics bar
    metrics = json.loads((REPORTS_DIR / "metrics.json").read_text(encoding="utf-8"))
    test_m = metrics["test"]
    labels = ["Naive 1h", "Seasonal 168h", "Decision Tree", "AdaBoost"]
    keys = ["baseline_last_hour", "baseline_seasonal_168h", "decision_tree", "adaboost"]
    rmse = [test_m[k]["rmse"] for k in keys]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, rmse, color=[NAVY, "#94A3B8", SKY, TEAL], edgecolor="white", lw=1.5)
    ax.set_title("Test RMSE Comparison", fontweight="bold")
    ax.set_ylabel("MWh")
    for i, (b, v) in enumerate(zip(bars, rmse)):
        ax.text(b.get_x() + b.get_width() / 2, v + 25, f"{v:.0f}", ha="center", fontweight="bold")
        if i == len(bars) - 1:
            b.set_edgecolor(TEAL)
            b.set_linewidth(3)
    ax.set_ylim(0, max(rmse) * 1.15)
    savefig("metrics_rmse_comparison.png")

    # Renewable overlay
    if "prod_renewable_share" in featured.columns:
        fig, ax1 = plt.subplots(figsize=(11, 4))
        ax1.plot(featured.index, featured[TARGET_COL], color=NAVY, lw=1.2, label="Consumption")
        ax2 = ax1.twinx()
        ax2.plot(featured.index, featured["prod_renewable_share"], color=TEAL, alpha=0.7, label="Renewable share")
        ax1.set_title("Consumption vs Renewable Share", fontweight="bold")
        savefig("renewable_overlay.png")

    # 6 Actual vs pred
    fig, axes = plt.subplots(2, 1, figsize=(11, 6.5), sharex=True)
    for ax, key, title, color in [
        (axes[0], "decision_tree", "Decision Tree", SKY),
        (axes[1], "adaboost", "AdaBoost", TEAL),
    ]:
        b = joblib.load(MODELS_DIR / f"{key}.joblib")
        pred = b["model"].predict(test[b["feature_columns"]])
        ax.plot(test.index, y, color=NAVY, label="Actual", lw=1.4)
        ax.plot(test.index, pred, color=color, label="Predicted", lw=1.1, alpha=0.9)
        ax.set_title(title, fontweight="bold")
        ax.legend()
    fig.suptitle("Test Set — Actual vs Predicted", fontweight="bold")
    savefig("actual_vs_pred_both.png")

    # 7 Importance
    for key, out in [("decision_tree", "dt_importance.png"), ("adaboost", "ada_importance.png")]:
        b = joblib.load(MODELS_DIR / f"{key}.joblib")
        m = b["model"]
        cols = b["feature_columns"]
        if hasattr(m, "feature_importances_"):
            imp = pd.Series(m.feature_importances_, index=cols).sort_values().tail(12)
            fig, ax = plt.subplots(figsize=(9, 5))
            imp.plot(kind="barh", ax=ax, color=TEAL if "ada" in out else SKY)
            ax.set_title(f"{key.replace('_', ' ').title()} — Feature Importance", fontweight="bold")
            savefig(out)

    # Copy interpretation if exists
    for src, dst in [
        ("interpretation/adaboost_pdp.png", "ada_pdp.png"),
        ("interpretation/adaboost_residual_by_hour.png", "residual_hour.png"),
    ]:
        s = FIGURES_DIR / src
        if s.exists():
            shutil.copy(s, OUT / dst)

    print(f"Saved figures to {OUT}")


if __name__ == "__main__":
    main()
