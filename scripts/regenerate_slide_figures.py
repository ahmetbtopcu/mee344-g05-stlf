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

# Sunum için okunabilir Türkçe etiketler
FEATURE_LABELS = {
    "lag_168h": "1 hafta önce (168h)",
    "lag_1h": "1 saat önce",
    "lag_2h": "2 saat önce",
    "lag_3h": "3 saat önce",
    "lag_24h": "24 saat önce",
    "hour_cos": "Saat (cos)",
    "hour_sin": "Saat (sin)",
    "dow_sin": "Gün (sin)",
    "dow_cos": "Gün (cos)",
    "doy_sin": "Yıl günü (sin)",
    "prod_solar": "Güneş üretimi",
    "prod_thermal": "Termik üretim",
    "prod_wind": "Rüzgar üretimi",
    "roll_min_24h": "24h min (kayan)",
    "roll_mean_24h": "24h ort. (kayan)",
    "roll_mean_168h": "168h ort. (kayan)",
    "ithal_komur": "İthal kömür",
    "net_balance": "Net denge",
    "is_weekend": "Hafta sonu",
    "is_holiday": "Resmi tatil",
}


def _label_feature(name: str) -> str:
    return FEATURE_LABELS.get(name, name.replace("_", " "))


def _annotate_importance(ax, imp: pd.Series, color: str) -> None:
    """Üst çubuklara değer ve kısa açıklama yaz."""
    top = imp.sort_values(ascending=False).head(2)
    for feat, val in top.items():
        y_idx = list(imp.index).index(feat)
        pct = val / imp.sum() * 100
        ax.text(
            val + imp.max() * 0.02,
            y_idx,
            f" %{pct:.0f}",
            va="center",
            fontsize=9,
            fontweight="bold",
            color=NAVY,
        )
    # En baskın özellik için ok + kutu
    top_feat = top.index[0]
    y0 = list(imp.index).index(top_feat)
    note = "Geçen hafta\naynı saat" if top_feat == "lag_168h" else _label_feature(top_feat)
    ax.annotate(
        note,
        xy=(top.iloc[0], y0),
        xytext=(top.iloc[0] * 0.55, y0 + 1.8),
        fontsize=9,
        color=NAVY,
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=color, lw=1.5, alpha=0.95),
        arrowprops=dict(arrowstyle="->", color=color, lw=1.2),
    )


def plot_importance(key: str, out: str, title_tr: str, bar_color: str) -> None:
    b = joblib.load(MODELS_DIR / f"{key}.joblib")
    m = b["model"]
    cols = b["feature_columns"]
    if not hasattr(m, "feature_importances_"):
        return
    imp_raw = pd.Series(m.feature_importances_, index=cols).sort_values().tail(12)
    imp = imp_raw.rename(index=_label_feature)
    fig, ax = plt.subplots(figsize=(9, 5))
    imp.plot(kind="barh", ax=ax, color=bar_color)
    ax.set_title(title_tr, fontweight="bold", fontsize=13)
    ax.set_xlabel("Önem skoru (MDI — ne kadar bölünürse o kadar etkili)", fontsize=10)
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.25, linestyle="--")
    _annotate_importance(ax, imp_raw, bar_color)
    fig.text(
        0.5,
        0.01,
        "Yüksek çubuk = tahminde daha fazla kullanılan özellik · Lag = geçmiş tüketim (sızıntı yok)",
        ha="center",
        fontsize=8.5,
        color="#475569",
        style="italic",
    )
    savefig(out)


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

    # 7 Importance (Türkçe etiket + açıklama)
    metrics = json.loads((REPORTS_DIR / "metrics.json").read_text(encoding="utf-8"))
    dt_rmse = metrics["test"]["decision_tree"]["rmse"]
    ada_rmse = metrics["test"]["adaboost"]["rmse"]
    plot_importance(
        "decision_tree",
        "dt_importance.png",
        f"Decision Tree — Özellik önemi  ·  Test RMSE {dt_rmse:.0f} MWh",
        SKY,
    )
    plot_importance(
        "adaboost",
        "ada_importance.png",
        f"AdaBoost — Özellik önemi  ·  Test RMSE {ada_rmse:.0f} MWh (en iyi)",
        TEAL,
    )

    # İki grafik tek panel (slayt sağ yarı)
    fig, axes = plt.subplots(2, 1, figsize=(10, 9))
    for ax, key, title_tr, bar_color in [
        (axes[0], "decision_tree", f"Decision Tree — RMSE {dt_rmse:.0f} MWh", SKY),
        (axes[1], "adaboost", f"AdaBoost — RMSE {ada_rmse:.0f} MWh", TEAL),
    ]:
        b = joblib.load(MODELS_DIR / f"{key}.joblib")
        imp_raw = pd.Series(b["model"].feature_importances_, index=b["feature_columns"]).sort_values().tail(10)
        imp = imp_raw.rename(index=_label_feature)
        imp.plot(kind="barh", ax=ax, color=bar_color)
        ax.set_title(title_tr, fontweight="bold", fontsize=11)
        ax.set_xlabel("Önem (MDI)", fontsize=9)
        ax.grid(axis="x", alpha=0.2, linestyle="--")
        top = imp_raw.sort_values(ascending=False).head(1)
        ax.text(
            0.98,
            0.08,
            f"En güçlü: {_label_feature(top.index[0])}\n(%{top.iloc[0] / imp_raw.sum() * 100:.0f} katkı)",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=8.5,
            bbox=dict(boxstyle="round", fc="white", ec=bar_color, alpha=0.9),
        )
    fig.suptitle("Hangi özellikler tüketimi taşıyor?", fontweight="bold", fontsize=13, y=0.98)
    fig.text(
        0.5,
        0.01,
        "Her iki modelde lag_168h (1 hafta) baskın; AdaBoost lag_1h’i de aktif kullanır → daha düşük hata",
        ha="center",
        fontsize=9,
        color="#475569",
    )
    savefig("dt_ada_importance_panel.png")

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
