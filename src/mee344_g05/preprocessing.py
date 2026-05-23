"""Data cleaning and outlier handling."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import TARGET_COL


def fill_missing_hours(df: pd.DataFrame, max_gap: int = 2) -> pd.DataFrame:
    """Reindex to hourly grid and forward-fill short gaps."""
    full_idx = pd.date_range(df.index.min(), df.index.max(), freq="h")
    out = df.reindex(full_idx)
    gap_flag = out[TARGET_COL].isna().astype(int).groupby(
        (out[TARGET_COL].notna() != out[TARGET_COL].notna().shift()).cumsum()
    ).transform("sum")
    out["gap_hours"] = gap_flag.where(out[TARGET_COL].isna(), 0)
    out = out.ffill(limit=max_gap)
    return out.dropna(subset=[TARGET_COL])


def clip_consumption_outliers(
    df: pd.DataFrame,
    column: str = TARGET_COL,
    iqr_mult: float = 3.0,
) -> pd.DataFrame:
    """IQR fence on target only."""
    out = df.copy()
    q1 = out[column].quantile(0.25)
    q3 = out[column].quantile(0.75)
    iqr = q3 - q1
    low = q1 - iqr_mult * iqr
    high = q3 + iqr_mult * iqr
    out[column] = out[column].clip(lower=low, upper=high)
    return out


def preprocess_merged(df: pd.DataFrame) -> pd.DataFrame:
    """Full preprocessing pipeline on merged raw data."""
    out = fill_missing_hours(df)
    out = clip_consumption_outliers(out)
    # Drop near-zero variance columns
    for col in ["nafta", "lng"]:
        if col in out.columns and out[col].max() == 0:
            out = out.drop(columns=[col])
    return out
