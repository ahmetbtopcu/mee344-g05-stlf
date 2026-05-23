"""Visualization helpers."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .config import FIGURES_DIR, TARGET_COL

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")


def _save(fig, name: str, subdir: str = "") -> Path:
    out_dir = FIGURES_DIR / subdir if subdir else FIGURES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_consumption_series(df: pd.DataFrame, name: str = "eda_01_consumption_series.png") -> Path:
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(df.index, df[TARGET_COL], linewidth=0.8)
    ax.set_title("Hourly Electricity Consumption (MWh)")
    ax.set_xlabel("Date")
    ax.set_ylabel("MWh")
    return _save(fig, name, "eda")


def plot_daily_profile(df: pd.DataFrame, name: str = "eda_02_daily_profile.png") -> Path:
    hourly = df.groupby(df.index.hour)[TARGET_COL].agg(["mean", "std"])
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(hourly.index, hourly["mean"], marker="o", label="Mean")
    ax.fill_between(
        hourly.index,
        hourly["mean"] - hourly["std"],
        hourly["mean"] + hourly["std"],
        alpha=0.3,
        label="±1 std",
    )
    ax.set_title("Average Daily Load Profile")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("MWh")
    ax.legend()
    return _save(fig, name, "eda")


def plot_weekly_heatmap(df: pd.DataFrame, name: str = "eda_03_weekly_heatmap.png") -> Path:
    tmp = df.copy()
    tmp["hour"] = tmp.index.hour
    tmp["dow"] = tmp.index.dayofweek
    pivot = tmp.pivot_table(values=TARGET_COL, index="dow", columns="hour", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(14, 5))
    sns.heatmap(pivot, cmap="YlOrRd", ax=ax)
    ax.set_title("Weekly Load Heatmap (Day × Hour)")
    ax.set_ylabel("Day of Week (0=Mon)")
    ax.set_xlabel("Hour")
    return _save(fig, name, "eda")


def plot_production_mix(df: pd.DataFrame, name: str = "eda_04_production_mix.png") -> Path:
    sources = [
        c
        for c in [
            "dogal_gaz",
            "barajli",
            "linyit",
            "ruzgar",
            "gunes",
            "ithal_komur",
        ]
        if c in df.columns
    ]
    if not sources:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No production columns", ha="center")
        return _save(fig, name, "eda")
    means = df[sources].mean().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    means.plot(kind="barh", ax=ax)
    ax.set_title("Average Production Mix by Source (MWh)")
    ax.set_xlabel("MWh")
    return _save(fig, name, "eda")


def plot_renewable_vs_consumption(df: pd.DataFrame, name: str = "eda_05_renewable_vs_consumption.png") -> Path:
    fig, ax1 = plt.subplots(figsize=(14, 4))
    ax1.plot(df.index, df[TARGET_COL], color="tab:blue", label="Consumption", alpha=0.8)
    ax1.set_ylabel("Consumption (MWh)", color="tab:blue")
    if "prod_renewable_share" in df.columns:
        ax2 = ax1.twinx()
        ax2.plot(df.index, df["prod_renewable_share"], color="tab:green", alpha=0.6, label="Renewable share")
        ax2.set_ylabel("Renewable Share", color="tab:green")
    ax1.set_title("Consumption vs Renewable Share")
    return _save(fig, name, "eda")


def plot_correlation(df: pd.DataFrame, feature_cols: list[str], name: str = "eda_06_correlation.png") -> Path:
    cols = [TARGET_COL] + feature_cols[:20]
    cols = [c for c in cols if c in df.columns]
    corr = df[cols].corr()
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr, cmap="coolwarm", center=0, ax=ax, annot=False)
    ax.set_title("Feature Correlation Matrix")
    return _save(fig, name, "eda")


def plot_acf(df: pd.DataFrame, name: str = "eda_07_acf.png") -> Path:
    from statsmodels.graphics.tsaplots import plot_acf

    fig, ax = plt.subplots(figsize=(10, 4))
    plot_acf(df[TARGET_COL].dropna(), lags=48, ax=ax)
    ax.set_title("ACF — Consumption (48 lags)")
    return _save(fig, name, "eda")


def plot_missing(df: pd.DataFrame, name: str = "eda_08_missing.png") -> Path:
    try:
        import missingno as msno

        fig = plt.figure(figsize=(12, 4))
        msno.matrix(df.iloc[:500], figsize=(12, 4))
        path = FIGURES_DIR / "eda" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        return path
    except Exception:
        fig, ax = plt.subplots(figsize=(8, 3))
        miss = df.isna().sum()
        miss[miss > 0].plot(kind="bar", ax=ax)
        ax.set_title("Missing Values per Column")
        return _save(fig, name, "eda")


def plot_actual_vs_pred(
    y_true,
    y_pred,
    index,
    title: str,
    name: str,
) -> Path:
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(index, y_true, label="Actual", linewidth=1.2)
    ax.plot(index, y_pred, label="Predicted", linewidth=1.0, alpha=0.85)
    ax.set_title(title)
    ax.set_ylabel("MWh")
    ax.legend()
    return _save(fig, name, "model")


def plot_residuals(y_true, y_pred, title: str, name: str) -> Path:
    resid = np.asarray(y_true) - np.asarray(y_pred)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].scatter(y_pred, resid, alpha=0.5, s=8)
    axes[0].axhline(0, color="red", linestyle="--")
    axes[0].set_xlabel("Predicted")
    axes[0].set_ylabel("Residual")
    axes[0].set_title(f"{title} — Residuals")
    axes[1].hist(resid, bins=40, edgecolor="white")
    axes[1].set_title("Residual Distribution")
    return _save(fig, name, "model")


def plot_feature_importance(importances: dict, title: str, name: str, top_n: int = 15) -> Path:
    items = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:top_n]
    names, vals = zip(*items) if items else ([], [])
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(range(len(names)), vals)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_title(title)
    ax.set_xlabel("Importance")
    return _save(fig, name, "model")


def plot_metrics_comparison(metrics: dict, name: str = "model_metrics_comparison.png") -> Path:
    models = list(metrics.get("test", {}).keys())
    rmse_vals = [metrics["test"][m]["rmse"] for m in models]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(models, rmse_vals, color=sns.color_palette("husl", len(models)))
    ax.set_title("Test RMSE by Model")
    ax.set_ylabel("RMSE (MWh)")
    plt.xticks(rotation=15)
    return _save(fig, name, "model")
