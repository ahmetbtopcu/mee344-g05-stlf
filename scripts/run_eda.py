#!/usr/bin/env python3
"""Generate all EDA figures."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mee344_g05.data_loader import load_merged
from mee344_g05.features import build_features, get_feature_columns
from mee344_g05.plotting import (
    plot_acf,
    plot_consumption_series,
    plot_correlation,
    plot_daily_profile,
    plot_missing,
    plot_production_mix,
    plot_renewable_vs_consumption,
    plot_weekly_heatmap,
)
from mee344_g05.preprocessing import preprocess_merged


def main():
    merged = preprocess_merged(load_merged())
    featured = build_features(merged)
    feat_cols = get_feature_columns(featured)
    plot_consumption_series(merged)
    plot_daily_profile(merged)
    plot_weekly_heatmap(merged)
    plot_production_mix(merged)
    plot_renewable_vs_consumption(featured)
    plot_correlation(featured, feat_cols)
    plot_acf(merged)
    plot_missing(merged)
    print("EDA figures saved to reports/figures/eda/")


if __name__ == "__main__":
    main()
